#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import re
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SAFETY_KEYWORDS = [
    "safety",
    "safe",
    "estop",
    "e-stop",
    "e stop",
    "guard",
    "door",
    "lightcurtain",
    "light curtain",
    "sto",
    "ss1",
    "sls",
    "profisafe",
    "failsafe",
]


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def has_any_keyword(text: str, keywords: list[str]) -> list[str]:
    n = norm(text)
    hits = []
    for kw in keywords:
        if norm(kw) in n:
            hits.append(kw)
    return sorted(set(hits))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@dataclass(frozen=True)
class Obj:
    kind: str
    name: str
    number: str
    language: str
    source_path: str


def build_graph(call_edges: list[dict[str, str]]) -> tuple[dict[str, set[str]], dict[str, set[str]], Counter[tuple[str, str]]]:
    g: dict[str, set[str]] = defaultdict(set)
    g_rev: dict[str, set[str]] = defaultdict(set)
    counts: Counter[tuple[str, str]] = Counter()
    for r in call_edges:
        caller = (r.get("caller") or "").strip()
        callee = (r.get("callee") or "").strip()
        if not caller or not callee:
            continue
        g[caller].add(callee)
        g_rev[callee].add(caller)
        try:
            c = int((r.get("count") or "1").strip())
        except ValueError:
            c = 1
        counts[(caller, callee)] += c
    return g, g_rev, counts


def shortest_path(g: dict[str, set[str]], start: str, target: str, max_nodes: int = 5000) -> list[str] | None:
    if start == target:
        return [start]
    q: deque[str] = deque([start])
    prev: dict[str, str | None] = {start: None}
    visited = 0
    while q:
        n = q.popleft()
        visited += 1
        if visited > max_nodes:
            break
        for m in sorted(g.get(n, set())):
            if m in prev:
                continue
            prev[m] = n
            if m == target:
                # reconstruct
                path = [m]
                cur: str | None = n
                while cur is not None:
                    path.append(cur)
                    cur = prev.get(cur)
                return list(reversed(path))
            q.append(m)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate CZ evidence packs for unused candidates (no cross-reference).")
    ap.add_argument("--out", default="deep_reader/out", help="Input folder from tia_deep_reader.py")
    ap.add_argument("--reports", default="deep_reader/reports", help="Output folder")
    ap.add_argument("--evidence-dir", default="deep_reader/evidence_unused", help="Output evidence packs folder")
    args = ap.parse_args()

    out_dir = Path(args.out)
    reports_dir = Path(args.reports)
    evidence_dir = Path(args.evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    objects_rows = read_csv(out_dir / "objects.csv")
    call_edges_rows = read_csv(out_dir / "call_edges.csv")
    symbol_rows = read_csv(out_dir / "symbol_usage.csv")
    hmi_rows = read_csv(out_dir / "hmi_tags.csv")
    edge_rows = read_csv(out_dir / "edge_case_scan.csv")
    abs_db_rows: list[dict[str, str]] = []
    abs_db_path = out_dir / "absolute_db_refs.csv"
    if abs_db_path.exists():
        abs_db_rows = read_csv(abs_db_path)

    no_touch: dict[str, dict[str, str]] = {}
    nt_path = reports_dir / "no_touch_register.csv"
    if nt_path.exists():
        for r in read_csv(nt_path):
            name = (r.get("Objekt") or "").strip()
            if name:
                no_touch[name] = r

    objects: dict[str, Obj] = {}
    for r in objects_rows:
        name = (r.get("name") or "").strip()
        if not name:
            continue
        objects[name] = Obj(
            kind=r.get("kind", "").strip(),
            name=name,
            number=(r.get("number") or "").strip(),
            language=(r.get("language") or "").strip(),
            source_path=(r.get("source_path") or "").strip(),
        )

    # Pro „hledání v textu“ beru přímo všechny exportované program bloky
    program_block_paths = sorted((Path.cwd() / "EXPORT/Program blocks").rglob("*.xml"))

    g, g_rev, edge_counts = build_graph(call_edges_rows)

    # OB kořeny (orientační)
    ob_roots = sorted([o.name for o in objects.values() if o.kind == "SW.Blocks.OB"])
    start_root = "01_OB1" if "01_OB1" in objects else (ob_roots[0] if ob_roots else "")

    # Candidate selection (same logic as report)
    candidates_blocks: list[Obj] = []
    for o in objects.values():
        if o.kind in {"SW.Blocks.FC", "SW.Blocks.FB"}:
            if not g_rev.get(o.name):
                candidates_blocks.append(o)

    symbol_roots_seen = {r.get("root", "").strip() for r in symbol_rows if r.get("root")}
    candidates_dbs: list[Obj] = []
    for o in objects.values():
        if o.kind == "SW.Blocks.GlobalDB":
            if o.name not in symbol_roots_seen:
                candidates_dbs.append(o)

    # Build symbol summary per root
    sym_by_root: dict[str, dict[str, Any]] = defaultdict(lambda: {"read": 0, "write": 0, "unknown": 0, "blocks": set(), "hmi_tags": set(), "symbols": []})
    for r in symbol_rows:
        root = (r.get("root") or "").strip()
        sym = (r.get("symbol") or "").strip()
        if not root or not sym:
            continue
        def_int = lambda k: int((r.get(k) or "0").strip() or "0")
        try:
            read_c = def_int("read_count")
            write_c = def_int("write_count")
            unk_c = def_int("unknown_count")
        except ValueError:
            read_c, write_c, unk_c = 0, 0, 0
        sym_by_root[root]["read"] += read_c
        sym_by_root[root]["write"] += write_c
        sym_by_root[root]["unknown"] += unk_c
        blocks = (r.get("blocks") or "").split(";") if r.get("blocks") else []
        for b in blocks:
            if b:
                sym_by_root[root]["blocks"].add(b)
        tags = (r.get("hmi_tags") or "").split(";") if r.get("hmi_tags") else []
        for t in tags:
            if t:
                sym_by_root[root]["hmi_tags"].add(t)
        sym_by_root[root]["symbols"].append((sym, read_c + write_c + unk_c, r.get("evidence_sample") or ""))

    # HMI bindings per root (ControllerTag prefix)
    hmi_by_root: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in hmi_rows:
        ctl = (r.get("ControllerTag") or "").strip()
        if not ctl:
            continue
        root = ctl.split(".", 1)[0] if "." in ctl else ctl
        hmi_by_root[root].append(r)

    # Edge-case hits
    edge_case_blocks = {r.get("block", "").strip(): r.get("hits", "").strip() for r in edge_rows if r.get("hits")}
    edge_case_blocks_runtime = sorted([b for b in edge_case_blocks.keys() if b in objects and b in g or b in g_rev])  # loose heuristic
    edge_case_global_count = len(edge_case_blocks)

    abs_db_refs: dict[str, dict[str, Any]] = {}
    for r in abs_db_rows:
        db_number = (r.get("db_number") or "").strip()
        if not db_number:
            continue
        try:
            hit_count = int((r.get("hit_count") or "0").strip())
        except ValueError:
            hit_count = 0
        samples_raw = (r.get("samples") or "").strip()
        samples = [s for s in samples_raw.split(" | ") if s] if samples_raw else []
        abs_db_refs[db_number] = {"hit_count": hit_count, "samples": samples}

    # Index report
    idx_lines: list[str] = []
    idx_lines.append("# Důkazní balíčky – kandidáti na nevyužité prvky\n")
    idx_lines.append("## FAKTA\n")
    idx_lines.append(f"- Kandidáti bloků (FC/FB bez příchozích volání): `{len(candidates_blocks)}`")
    idx_lines.append(f"- Kandidáti DB (GlobalDB bez symbolického root použití): `{len(candidates_dbs)}`")
    idx_lines.append(f"- Indikátory nepřímého přístupu nalezeny v blocích: `{edge_case_global_count}` (snižuje jistotu)\n")
    idx_lines.append("## PRAVIDLO\n- Bez cross-reference exportu a při existenci nepřímého přístupu: **nedoporučuji mazat**; pouze ověřovat.\n")
    idx_lines.append("## Balíčky\n")

    def pack_name(o: Obj) -> str:
        return f"{o.kind.replace('SW.Blocks.', '')}_{o.name}".replace(" ", "_") + ".md"

    def make_name_variants(name: str) -> list[str]:
        esc = html.escape(name, quote=True)
        return [name] if esc == name else [name, esc]

    def scan_program_blocks_for(name: str, exclude_source: str) -> dict[str, Any]:
        """
        Scan all program block XML files for likely references to `name`.
        Excludes the declaration file of the candidate itself.
        """
        variants = make_name_variants(name)
        callinfo_re = re.compile(r'CallInfo\\s+Name="(' + "|".join(re.escape(v) for v in variants) + r')"', re.IGNORECASE)
        token_re = re.compile(r'Text="(' + "|".join(re.escape(v) for v in variants) + r')"', re.IGNORECASE)
        component_re = re.compile(r'Component\\s+Name="(' + "|".join(re.escape(v) for v in variants) + r')"', re.IGNORECASE)

        hits = {"callinfo": 0, "token": 0, "component": 0}
        samples: dict[str, list[str]] = {"callinfo": [], "token": [], "component": []}

        excl = (Path.cwd() / exclude_source).resolve() if exclude_source else None

        for path in program_block_paths:
            if excl and path.resolve() == excl:
                continue
            try:
                with path.open("r", encoding="utf-8", errors="ignore") as f:
                    for ln, line in enumerate(f, start=1):
                        if callinfo_re.search(line):
                            hits["callinfo"] += 1
                            if len(samples["callinfo"]) < 10:
                                samples["callinfo"].append(f"{path.as_posix()}:{ln}: {line.strip()[:220]}")
                        if token_re.search(line):
                            hits["token"] += 1
                            if len(samples["token"]) < 10:
                                samples["token"].append(f"{path.as_posix()}:{ln}: {line.strip()[:220]}")
                        if component_re.search(line):
                            hits["component"] += 1
                            if len(samples["component"]) < 10:
                                samples["component"].append(f"{path.as_posix()}:{ln}: {line.strip()[:220]}")
            except Exception:
                continue

        return {"hits": hits, "samples": samples}

    # Create packs
    all_candidates = sorted(candidates_blocks + candidates_dbs, key=lambda o: (o.kind, o.name))
    summary_rows: list[dict[str, str]] = []
    for o in all_candidates:
        nt = no_touch.get(o.name)
        safety_hits = has_any_keyword(o.name + " " + o.source_path, SAFETY_KEYWORDS)
        is_no_touch = bool(nt) or bool(safety_hits) or (o.kind == "SW.Blocks.OB")

        inbound = sorted(g_rev.get(o.name, set()))
        outbound = sorted(g.get(o.name, set()))

        # Call path evidence
        path_from_ob1 = shortest_path(g, start_root, o.name) if start_root else None
        reachable_from_any_ob = False
        for ob in ob_roots:
            if shortest_path(g, ob, o.name):
                reachable_from_any_ob = True
                break

        # DB usage / HMI binding (for DB roots)
        db_sym = sym_by_root.get(o.name)
        hmi_bindings = hmi_by_root.get(o.name, [])

        # Determine confidence
        confidence = "NÍZKÁ" if edge_case_global_count else "STŘEDNÍ"
        if is_no_touch:
            confidence = "NÍZKÁ"

        risk = "RIZIKOVÉ"
        if is_no_touch:
            risk = "KRITICKÉ (NEŠAHAT)"

        md: list[str] = []
        md.append(f"# Důkazní balíček: `{o.name}`\n")
        md.append("## FAKTA\n")
        md.append(f"- Objekt: `{o.name}`")
        md.append(f"- Druh: `{o.kind}`")
        if o.number:
            md.append(f"- Číslo: `{o.number}`")
        if o.language:
            md.append(f"- Jazyk: `{o.language}`")
        md.append(f"- Deklarace (export): `{o.source_path}`")
        md.append(f"- Riziko: `{risk}`")
        md.append(f"- Jistota (bez cross-reference): `{confidence}`\n")

        md.append("## DŮKAZY (reference / použití)\n")

        scan = scan_program_blocks_for(o.name, o.source_path)
        md.append("### Přímé nálezy v exportu (hledání v textu v `EXPORT/Program blocks/**/*.xml`)\n")
        md.append(f"- Nálezy `CallInfo Name=\"{o.name}\"`: `{scan['hits']['callinfo']}`")
        md.append(f"- Nálezy `Text=\"{o.name}\"` (tokenizovaný StructuredText): `{scan['hits']['token']}`")
        md.append(f"- Nálezy `Component Name=\"{o.name}\"`: `{scan['hits']['component']}`")
        md.append("")
        if scan["samples"]["callinfo"] or scan["samples"]["token"] or scan["samples"]["component"]:
            md.append("- Vzorky řádků (omezeno):")
            for s in scan["samples"]["callinfo"]:
                md.append(f"  - (CallInfo) {s}")
            for s in scan["samples"]["token"]:
                md.append(f"  - (Token) {s}")
            for s in scan["samples"]["component"]:
                md.append(f"  - (Component) {s}")
            md.append("")

        md.append("### Volání bloků (z `deep_reader/out/call_edges.csv`)\n")
        md.append(f"- Příchozí volání (kdo volá `{o.name}`): `{len(inbound)}`")
        if inbound:
            md.append("- Seznam volajících (vzorek):")
            for caller in inbound[:25]:
                caller_obj = objects.get(caller)
                if caller_obj:
                    md.append(f"  - `{caller}` ({caller_obj.kind}, `{caller_obj.language}`) `{caller_obj.source_path}`")
                else:
                    md.append(f"  - `{caller}`")
        md.append(f"- Odchozí volání (co `{o.name}` volá): `{len(outbound)}`")
        if outbound:
            md.append("- Seznam volaných (vzorek):")
            for callee in outbound[:25]:
                callee_obj = objects.get(callee)
                if callee_obj:
                    md.append(f"  - `{callee}` ({callee_obj.kind}, `{callee_obj.language}`) `{callee_obj.source_path}`")
                else:
                    md.append(f"  - `{callee}`")
        md.append("")
        if start_root:
            if path_from_ob1:
                md.append(f"- Nejkratší cesta z `{start_root}`: " + " → ".join([f"`{n}`" for n in path_from_ob1]))
            else:
                md.append(f"- Nejkratší cesta z `{start_root}`: (nenalezeno v extrahovaných datech)")
        md.append(f"- Dosažitelné z některého OB: `{reachable_from_any_ob}` (orientačně)\n")

        if o.kind == "SW.Blocks.GlobalDB":
            md.append("### Použití DB přes symboly (z `deep_reader/out/symbol_usage.csv`)\n")
            if db_sym:
                md.append(f"- Součet čtení: `{db_sym['read']}`, zápisů: `{db_sym['write']}`, neznámé: `{db_sym['unknown']}`")
                md.append(f"- Bloky, kde je root `{o.name}` použit: `{len(db_sym['blocks'])}`")
                md.append(f"- HMI tagy navázané na root `{o.name}` (z evidence): `{len(db_sym['hmi_tags'])}`")
                # show top symbols by activity
                top = sorted(db_sym["symbols"], key=lambda t: (-t[1], t[0]))[:15]
                if top:
                    md.append("- Nejaktivnější symboly (vzorek):")
                    for sym, cnt, ev in top:
                        ev_txt = f" | Důkaz: {ev}" if ev else ""
                        md.append(f"  - `{sym}` ({cnt}){ev_txt}")
            else:
                md.append(f"- Root `{o.name}` nebyl nalezen v symbolickém použití (0 záznamů).\n")

            md.append("### Absolutní adresování DB (orientační scan)\n")
            if o.number and o.number in abs_db_refs:
                hit_count = abs_db_refs[o.number]["hit_count"]
                md.append(
                    f"- Nálezy řetězců `DB{o.number}` / `DB {o.number}` v exportovaných OB/FB/FC (mimo DB exporty): `{hit_count}`"
                )
                samples = abs_db_refs[o.number]["samples"][:10]
                if samples:
                    md.append("- Vzorky řádků (omezeno):")
                    for s in samples:
                        md.append(f"  - {s}")
            else:
                if o.number:
                    md.append(
                        f"- Pro DB číslo `{o.number}` nebyl nalezen výskyt `DB{o.number}` / `DB {o.number}` v exportovaných OB/FB/FC (není to důkaz nepoužití)."
                    )
                else:
                    md.append("- Číslo DB není známé; absolutní scan nelze spárovat.")
            md.append("")

            md.append("### Vazby HMI (z `deep_reader/out/hmi_tags.csv`)\n")
            md.append(f"- HMI tagy s kořenem `ControllerTag` = `{o.name}`: `{len(hmi_bindings)}`")
            if hmi_bindings:
                md.append("- Vzorek HMI tagů:")
                for r in hmi_bindings[:25]:
                    md.append(f"  - `{r.get('Name','')}` (tabulka `{r.get('Table','')}`) → `{r.get('ControllerTag','')}`")
            md.append("")

        md.append("## RIZIKA / GATE\n")
        if is_no_touch:
            md.append("- Tento objekt je označen jako NEŠAHAT (bezpečnostně-adjacentní nebo kritický). Neprovádět změny bez samostatné analýzy rizik.")
            if nt:
                md.append(f"- Důvod (registr NEŠAHAT): {nt.get('Důvody','')}")
            if safety_hits:
                md.append(f"- Klíčová slova: {', '.join(safety_hits)}")
        md.append(
            f"- V projektu je nalezeno `{edge_case_global_count}` bloků s indikátory nepřímého přístupu (ANY/BLKMOV/PEEK/POKE/AR/AT/VARIANT). To snižuje jistotu 'mrtvé' i při 0 symbolech/0 voláních."
        )
        if edge_case_global_count:
            sample = list(sorted(edge_case_blocks.items(), key=lambda kv: kv[0]))[:12]
            md.append("- Vzorek bloků s indikátory:")
            for blk, hits in sample:
                md.append(f"  - `{blk}`: `{hits}`")
        md.append("")

        md.append("## DOPORUČENÍ (bez mazání)\n")
        md.append("### Jak ověřit v TIA (bez exportu cross-reference)\n")
        md.append("- Pro bloky: globální vyhledání názvu bloku v projektu (všechny bloky, LAD/STL/GRAPH) a kontrola, zda existuje volání.")
        md.append("- Pro DB: vyhledat kořen DB v symbolickém vyhledávání a zkontrolovat HMI vazby (ControllerTag) + alarmy/trendy.")
        md.append("- Pokud je objekt podezřelý, ale nejistý: během odstávky přidejte dočasné watch/trace a ověřte, zda se hodnoty mění (pozorování bez zásahu / bez zápisu).\n")
        md.append("### Jak validovat (offline + krátká odstávka)\n")
        md.append("- Offline kompilace bez změn chování.")
        md.append("- Krátká odstávka: online download pouze additivních objektů (pokud se přidává diagnostika).\n")
        md.append("### Rollback (pokud by se někdy dělala změna)\n")
        md.append("- Okamžitý rollback = návrat na poslední zálohu projektu / online compare + download.")
        md.append("- Preferovat nejdříve deaktivaci (podmínka/enable), ne fyzické smazání.")

        out_path = evidence_dir / pack_name(o)
        write_text(out_path, "\n".join(md) + "\n")
        idx_lines.append(f"- `{o.name}` → `{out_path.as_posix()}`")

        summary_rows.append(
            {
                "Objekt": o.name,
                "Druh": o.kind,
                "Jazyk": o.language,
                "Deklarace": o.source_path,
                "Riziko": risk,
                "Jistota": confidence,
                "PříchozíVolání(call_edges)": str(len(inbound)),
                "OdchozíVolání(call_edges)": str(len(outbound)),
                "CallInfoNálezy(scan)": str(scan["hits"]["callinfo"]),
                "TokenNálezy(scan)": str(scan["hits"]["token"]),
                "KomponentaNálezy(scan)": str(scan["hits"]["component"]),
                "HmiTagyKořen": str(len(hmi_bindings)) if o.kind == "SW.Blocks.GlobalDB" else "",
                "SymbolRootČtení": str(db_sym["read"]) if (o.kind == "SW.Blocks.GlobalDB" and db_sym) else "",
                "SymbolRootZápis": str(db_sym["write"]) if (o.kind == "SW.Blocks.GlobalDB" and db_sym) else "",
                "SymbolRootNeznámé": str(db_sym["unknown"]) if (o.kind == "SW.Blocks.GlobalDB" and db_sym) else "",
                "AbsolutníDBNálezy_hint": str(abs_db_refs.get(o.number, {}).get("hit_count", "")) if o.kind == "SW.Blocks.GlobalDB" else "",
                "NEŠAHAT": "ANO" if is_no_touch else "NE",
            }
        )

    write_text(evidence_dir / "INDEX.md", "\n".join(idx_lines) + "\n")
    if summary_rows:
        out_csv = evidence_dir / "souhrn_kandidatu.csv"
        with out_csv.open("w", encoding="utf-8", newline="") as f:
            fieldnames = list(summary_rows[0].keys())
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(summary_rows)
    print(f"Wrote evidence packs to: {evidence_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
