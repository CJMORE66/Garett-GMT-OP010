#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import re
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Block:
    kind: str
    name: str
    number: str
    language: str
    source_path: Path


def read_text(path: Path) -> str:
    data = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "cp1250", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def parse_unused_from_report(report_path: Path) -> list[str]:
    text = read_text(report_path)
    # Limit to the "Nevolané bloky (FC/FB)" section.
    m = re.search(r"### Nevolané bloky.*?\n(.*?)(?:\n###|\n## |\Z)", text, flags=re.S)
    if not m:
        return []
    section = m.group(1)
    names = re.findall(r"-\s+`([^`]+)`\s+\(", section)
    # Preserve order, unique.
    seen: set[str] = set()
    out: list[str] = []
    for name in names:
        if name not in seen:
            out.append(name)
            seen.add(name)
    return out


def parse_objects(objects_csv: Path) -> list[Block]:
    blocks: list[Block] = []
    with objects_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            blocks.append(
                Block(
                    kind=row["kind"].strip(),
                    name=row["name"].strip(),
                    number=row["number"].strip(),
                    language=row["language"].strip(),
                    source_path=(ROOT / row["source_path"].strip()).resolve(),
                )
            )
    return blocks


def parse_call_edges(call_edges_csv: Path) -> tuple[dict[str, int], dict[str, set[str]], dict[str, set[str]]]:
    in_degree: dict[str, int] = defaultdict(int)
    out_graph: dict[str, set[str]] = defaultdict(set)
    in_graph: dict[str, set[str]] = defaultdict(set)
    with call_edges_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            caller = row["caller"].strip()
            callee = row["callee"].strip()
            if not caller or not callee:
                continue
            out_graph[caller].add(callee)
            in_graph[callee].add(caller)
            in_degree[callee] += 1
            # Ensure caller exists in maps too
            in_degree.setdefault(caller, in_degree.get(caller, 0))
    return in_degree, out_graph, in_graph


def find_roots(blocks: Iterable[Block], out_graph: dict[str, set[str]]) -> set[str]:
    roots: set[str] = set()
    for b in blocks:
        if b.kind.endswith(".OB"):
            roots.add(b.name)
    # Fallback: any node that looks like an OB in the extracted graph.
    for caller in out_graph.keys():
        if re.match(r"^\d+_OB", caller, flags=re.I) or re.match(r"^OB\d+", caller, flags=re.I):
            roots.add(caller)
    return roots


def reachable_from_roots(roots: set[str], out_graph: dict[str, set[str]]) -> set[str]:
    seen: set[str] = set()
    q: deque[str] = deque()
    for r in roots:
        q.append(r)
        seen.add(r)
    while q:
        node = q.popleft()
        for nxt in out_graph.get(node, set()):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return seen


_GUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
_HEX_LONG_RE = re.compile(r"\b[0-9a-f]{16,}\b", re.I)
_NUM_RE = re.compile(r"\b\d{2,}\b")
_TAG_RE = re.compile(r"<[^>]+>")
_CDATA_RE = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.S)


def extract_code_text(xml_text: str) -> str:
    cdata_parts = _CDATA_RE.findall(xml_text)
    if cdata_parts:
        # Choose the largest CDATA section; typically contains ST source.
        return max(cdata_parts, key=len)
    # Fallback: strip tags to get a text-ish representation.
    return _TAG_RE.sub(" ", xml_text)


def normalize_for_hash(text: str, self_name: str) -> str:
    t = text.lower()
    t = t.replace(self_name.lower(), "{name}")
    t = _GUID_RE.sub("{guid}", t)
    t = _HEX_LONG_RE.sub("{hex}", t)
    t = _NUM_RE.sub("{n}", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_STOP_TOKENS = {
    "and",
    "or",
    "not",
    "true",
    "false",
    "int",
    "dint",
    "real",
    "bool",
    "word",
    "dword",
    "byte",
    "string",
    "char",
    "if",
    "then",
    "else",
    "end_if",
    "for",
    "to",
    "do",
    "end_for",
    "while",
    "end_while",
    "case",
    "end_case",
    "var",
    "end_var",
    "st",
    "st10",
    "fb",
    "fc",
    "ob",
    "db",
}


def token_set(text: str) -> set[str]:
    tokens = {t.lower() for t in _TOKEN_RE.findall(text)}
    tokens = {t for t in tokens if len(t) >= 3 and t not in _STOP_TOKENS}
    return tokens


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def norm_name_keys(name: str) -> set[str]:
    # Generate multiple normalization keys to catch "dvojčata" by naming patterns.
    n = name.lower()
    n = n.replace("&", "and")
    alnum = re.sub(r"[^a-z0-9]+", "", n)

    def strip_prefix(s: str, prefix: str) -> str:
        return s[len(prefix) :] if s.startswith(prefix) else s

    def strip_affixes(s: str) -> str:
        # Handle both FB_* and *_FB style naming.
        for p in ("st10", "st", "fb", "fc"):
            s = strip_prefix(s, p)
        for suf in ("fb", "fc"):
            if s.endswith(suf):
                s = s[: -len(suf)]
        return s

    no_prefix = strip_affixes(alnum)

    no_version = re.sub(r"v\d+$", "", no_prefix)
    no_ctrl = re.sub(r"(ctrl|control|module)$", "", no_version)
    return {alnum, no_prefix, no_version, no_ctrl}


def name_key_variants(name: str) -> dict[str, str]:
    n = name.lower().replace("&", "and")
    alnum = re.sub(r"[^a-z0-9]+", "", n)

    def strip_prefix(s: str, prefix: str) -> str:
        return s[len(prefix) :] if s.startswith(prefix) else s

    def strip_affixes(s: str) -> str:
        for p in ("st10", "st", "fb", "fc"):
            s = strip_prefix(s, p)
        for suf in ("fb", "fc"):
            if s.endswith(suf):
                s = s[: -len(suf)]
        return s

    no_prefix = strip_affixes(alnum)
    no_version = re.sub(r"v\d+$", "", no_prefix)
    no_ctrl = re.sub(r"(ctrl|control|module)$", "", no_version)
    return {"alnum": alnum, "no_prefix": no_prefix, "no_version": no_version, "no_ctrl": no_ctrl}


def main() -> int:
    report_path = ROOT / "deep_reader" / "reports" / "02_unused_elements_analysis.md"
    objects_csv = ROOT / "deep_reader" / "out" / "objects.csv"
    call_edges_csv = ROOT / "deep_reader" / "out" / "call_edges.csv"

    unused = parse_unused_from_report(report_path)
    blocks = parse_objects(objects_csv)
    by_name = {b.name: b for b in blocks}

    in_degree, out_graph, _in_graph = parse_call_edges(call_edges_csv)
    roots = find_roots(blocks, out_graph)
    reachable = reachable_from_roots(roots, out_graph) if roots else set()

    # Precompute code fingerprints and token sets.
    fingerprints: dict[str, str] = {}
    tokens: dict[str, set[str]] = {}
    for b in blocks:
        try:
            xml_text = read_text(b.source_path)
            code = extract_code_text(xml_text)
            norm = normalize_for_hash(code, b.name)
            fingerprints[b.name] = hashlib.sha1(norm.encode("utf-8")).hexdigest()
            tokens[b.name] = token_set(code)
        except Exception:
            fingerprints[b.name] = ""
            tokens[b.name] = set()

    # Build name-key index.
    name_index: dict[str, set[str]] = defaultdict(set)
    for b in blocks:
        for k in norm_name_keys(b.name):
            if k:
                name_index[k].add(b.name)

    out_md = ROOT / "deep_reader" / "reports" / "10_unused_twins_analysis.md"
    out_csv = ROOT / "deep_reader" / "reports" / "10_unused_twins_analysis.csv"

    rows: list[dict[str, str]] = []
    md_lines: list[str] = []
    md_lines.append("# Nevolané bloky – hledání „dvojčat“\n")
    md_lines.append(
        "Cíl: pro každý blok označený jako nevolaný najít pravděpodobné kopie/varianty, které jsou volané.\n"
    )
    md_lines.append("Pozn.: „volané“ zde znamená, že se blok objevil jako `callee` v `deep_reader/out/call_edges.csv`.\n")
    md_lines.append("\n")

    for name in unused:
        b = by_name.get(name)
        if not b:
            continue
        md_lines.append(f"## `{name}`\n")
        md_lines.append(f"- Typ: {b.kind}, jazyk: {b.language}, číslo: {b.number}\n")
        md_lines.append(f"- Zdroj: {b.source_path.relative_to(ROOT).as_posix()}\n")
        md_lines.append(f"- In-degree (důkaz příchozích volání): {in_degree.get(name, 0)}\n")
        md_lines.append(f"- Reachable z OB (z extrahovaného grafu): {'ANO' if name in reachable else 'NE/NEJISTÉ'}\n")

        # 1) Exact fingerprint matches (strong duplicates)
        fp = fingerprints.get(name, "")
        exact_dups = [other for other, ofp in fingerprints.items() if other != name and fp and ofp == fp]

        # 2) Name-based candidates
        candidate_names: set[str] = set()
        for k in norm_name_keys(name):
            candidate_names |= name_index.get(k, set())
        candidate_names.discard(name)

        base_keys = name_key_variants(name)
        strong_name_matches: list[tuple[str, str]] = []  # (other, matched_key_type)
        for other in candidate_names:
            other_keys = name_key_variants(other)
            for key_type in ("no_ctrl", "no_version", "no_prefix"):
                if base_keys.get(key_type) and base_keys[key_type] == other_keys.get(key_type):
                    strong_name_matches.append((other, key_type))
                    break

        # Rank candidates: prefer evidence of being called + code token similarity.
        ranked: list[tuple[float, str]] = []
        base_tokens = tokens.get(name, set())
        for other in candidate_names:
            score = jaccard(base_tokens, tokens.get(other, set()))
            # Small bump if it's called (has in-degree) or reachable.
            if in_degree.get(other, 0) > 0:
                score += 0.05
            if other in reachable:
                score += 0.02
            ranked.append((score, other))
        ranked.sort(reverse=True)

        md_lines.append("\n### Podezření na dvojčata\n")
        found_any = False

        if exact_dups:
            found_any = True
            md_lines.append("**Shoda obsahu (silný důkaz):**\n")
            for other in sorted(exact_dups):
                md_lines.append(
                    f"- `{other}` (in-degree={in_degree.get(other,0)}, reachable={'ANO' if other in reachable else 'NE/NEJISTÉ'})\n"
                )
                rows.append(
                    {
                        "unused_block": name,
                        "candidate_twin": other,
                        "match_type": "content_hash_equal",
                        "token_jaccard": "",
                        "candidate_in_degree": str(in_degree.get(other, 0)),
                        "candidate_reachable": "yes" if other in reachable else "unknown",
                    }
                )
            md_lines.append("\n")

        if strong_name_matches:
            found_any = True
            md_lines.append("**Silná shoda názvu (pravděpodobná varianta/kopie):**\n")
            for other, key_type in sorted(set(strong_name_matches), key=lambda x: (x[1], x[0])):
                md_lines.append(
                    f"- `{other}` (match={key_type}, in-degree={in_degree.get(other,0)}, reachable={'ANO' if other in reachable else 'NE/NEJISTÉ'})\n"
                )
                rows.append(
                    {
                        "unused_block": name,
                        "candidate_twin": other,
                        "match_type": f"strong_name:{key_type}",
                        "token_jaccard": "",
                        "candidate_in_degree": str(in_degree.get(other, 0)),
                        "candidate_reachable": "yes" if other in reachable else "unknown",
                    }
                )
            md_lines.append("\n")

        # Take top N ranked candidates above a minimal threshold.
        top = [(s, o) for s, o in ranked[:10] if s >= 0.30]
        if top:
            found_any = True
            md_lines.append("**Shoda názvu + podobnost tokenů (heuristika):**\n")
            for score, other in top:
                md_lines.append(
                    f"- `{other}` score={score:.2f} (in-degree={in_degree.get(other,0)}, reachable={'ANO' if other in reachable else 'NE/NEJISTÉ'})\n"
                )
                rows.append(
                    {
                        "unused_block": name,
                        "candidate_twin": other,
                        "match_type": "name+tokens",
                        "token_jaccard": f"{max(0.0, score - (0.05 if in_degree.get(other,0)>0 else 0.0) - (0.02 if other in reachable else 0.0)):.3f}",
                        "candidate_in_degree": str(in_degree.get(other, 0)),
                        "candidate_reachable": "yes" if other in reachable else "unknown",
                    }
                )
            md_lines.append("\n")

        if not found_any:
            md_lines.append("- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.\n\n")

    out_md.write_text("".join(md_lines), encoding="utf-8", newline="\n")

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "unused_block",
            "candidate_twin",
            "match_type",
            "token_jaccard",
            "candidate_in_degree",
            "candidate_reachable",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {out_md.relative_to(ROOT)} and {out_csv.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
