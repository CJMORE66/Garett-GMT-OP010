#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BlockRow:
    kind: str
    name: str
    original_language: str
    source_path: str
    out_path: str
    structured_text_networks: int
    flgnet_networks: int
    statementlist_networks: int


def _int(v: Any) -> int:
    try:
        return int(v)
    except Exception:
        return 0


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Analyze xml_to_scl_export coverage across all blocks and write a CZ report."
    )
    ap.add_argument("--scl-root", default="deep_reader/scl_export", help="SCL export folder")
    ap.add_argument("--reports", default="deep_reader/reports", help="Report output folder")
    ap.add_argument("--top", type=int, default=40, help="Top N blocks to list by warnings/size")
    args = ap.parse_args()

    scl_root = Path(args.scl_root)
    reports_dir = Path(args.reports)
    reports_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = scl_root / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Missing: {manifest_path.as_posix()} (run xml_to_scl_export.py first)")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    outputs = manifest.get("outputs") or []

    blocks: list[BlockRow] = []
    for r in outputs:
        kind = str(r.get("kind") or "")
        if kind not in {"SW.Blocks.OB", "SW.Blocks.FB", "SW.Blocks.FC"}:
            continue
        if str(r.get("status") or "") != "block_interface_exported":
            continue
        blocks.append(
            BlockRow(
                kind=kind,
                name=str(r.get("name") or ""),
                original_language=str(r.get("original_language") or ""),
                source_path=str(r.get("source_path") or ""),
                out_path=str(r.get("out_path") or ""),
                structured_text_networks=_int(r.get("structured_text_networks")),
                flgnet_networks=_int(r.get("flgnet_networks")),
                statementlist_networks=_int(r.get("statementlist_networks")),
            )
        )

    # Parse generated SCL text for markers (what actually got written)
    per_lang: dict[str, Counter[str]] = defaultdict(Counter)
    missing_files: list[BlockRow] = []
    blocks_no_logic: list[BlockRow] = []
    blocks_with_warnings: list[tuple[int, int, BlockRow]] = []
    blocks_with_unsupported: list[tuple[int, BlockRow]] = []

    for b in blocks:
        per_lang[b.original_language]["blocks_total"] += 1
        out_path = Path(b.out_path)
        if not out_path.exists():
            missing_files.append(b)
            per_lang[b.original_language]["missing_out_file"] += 1
            continue

        txt = read_text(out_path)
        has_st = "Rekonstruovaný StructuredText" in txt
        has_lad = "LAD/FBD → SCL" in txt
        has_stl = "STL (StatementList)" in txt
        warn_sections = txt.count("Poznámky / omezení převodu")
        unsupported_lines = txt.count("Síť obsahuje nepodporované prvky")

        if has_st:
            per_lang[b.original_language]["has_structured_text_section"] += 1
        if has_lad:
            per_lang[b.original_language]["has_lad_section"] += 1
        if has_stl:
            per_lang[b.original_language]["has_stl_section"] += 1
        if warn_sections:
            per_lang[b.original_language]["blocks_with_warnings"] += 1
            blocks_with_warnings.append((warn_sections, unsupported_lines, b))
        if unsupported_lines:
            per_lang[b.original_language]["blocks_with_unsupported_parts"] += 1
            blocks_with_unsupported.append((unsupported_lines, b))

        any_logic = bool(b.structured_text_networks or b.flgnet_networks or b.statementlist_networks or has_st or has_lad or has_stl)
        if not any_logic:
            blocks_no_logic.append(b)
            per_lang[b.original_language]["no_logic_extracted"] += 1

        # Source-driven counters (from manifest)
        if b.structured_text_networks:
            per_lang[b.original_language]["structured_text_networks_total"] += b.structured_text_networks
            per_lang[b.original_language]["blocks_with_structured_text_networks"] += 1
        if b.flgnet_networks:
            per_lang[b.original_language]["flgnet_networks_total"] += b.flgnet_networks
            per_lang[b.original_language]["blocks_with_flgnet_networks"] += 1
        if b.statementlist_networks:
            per_lang[b.original_language]["statementlist_networks_total"] += b.statementlist_networks
            per_lang[b.original_language]["blocks_with_statementlist_networks"] += 1

    # Sort and keep top lists
    blocks_with_warnings.sort(key=lambda t: (-t[0], -t[1], t[2].kind, t[2].name))
    blocks_with_unsupported.sort(key=lambda t: (-t[0], t[1].kind, t[1].name))
    blocks_no_logic.sort(key=lambda b: (b.original_language, b.kind, b.name))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md: list[str] = []
    md.append("# Pokrytí převodu XML → SCL (všechny bloky)\n")
    md.append(f"- Čas generování: `{now}`")
    md.append(f"- Zdroj manifestu: `{manifest_path.as_posix()}`")
    md.append(f"- Počet bloků (OB/FB/FC) v exportu SCL: `{len(blocks)}`\n")

    md.append("## Souhrn podle původního jazyka\n")
    md.append("| Jazyk | Bloky | ST sekce | LAD/FBD sekce | STL sekce | Varování | Nepodporované prvky | Bez logiky |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for lang, c in sorted(per_lang.items(), key=lambda kv: (-kv[1]["blocks_total"], kv[0])):
        md.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                lang or "unknown",
                c["blocks_total"],
                c["has_structured_text_section"],
                c["has_lad_section"],
                c["has_stl_section"],
                c["blocks_with_warnings"],
                c["blocks_with_unsupported_parts"],
                c["no_logic_extracted"],
            )
        )
    md.append("")

    md.append("## Top bloky podle počtu varování (omezení převodu)\n")
    md.append("Pozn.: Varování znamená, že síť obsahovala nepodporované prvky nebo nebylo možné určit operand/target/podmínku. Překlad je orientační pro revizi.\n")
    md.append("| Varování | Nepodporované | Blok | Jazyk | Zdroj |")
    md.append("|---:|---:|---|---|---|")
    for warn_cnt, unsup_cnt, b in blocks_with_warnings[: max(1, int(args.top))]:
        md.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                warn_cnt,
                unsup_cnt,
                f"{b.kind} `{b.name}`",
                b.original_language or "unknown",
                b.source_path,
            )
        )
    md.append("")

    md.append("## Bloky bez extrahované logiky (podezření na GRAPH / nepodporovanou reprezentaci)\n")
    md.append("Tyto bloky nemají StructuredText/FlgNet/StatementList sítě v exportu, takže SCL obsahuje jen rozhraní + odkazy na zdroj XML.\n")
    for b in blocks_no_logic[: max(1, int(args.top))]:
        md.append(f"- `{b.name}` ({b.kind}, `{b.original_language or 'unknown'}`) `{b.source_path}`")
    if len(blocks_no_logic) > int(args.top):
        md.append(f"- (zobrazeno {int(args.top)} z {len(blocks_no_logic)})")
    md.append("")

    if missing_files:
        md.append("## Chybějící výstupní soubory\n")
        for b in missing_files[: max(1, int(args.top))]:
            md.append(f"- `{b.name}` ({b.kind}, `{b.original_language or 'unknown'}`) expected `{b.out_path}`")
        md.append("")

    report_path = reports_dir / "07_pokryti_prevodu_xml_do_scl.md"
    report_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote: {report_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

