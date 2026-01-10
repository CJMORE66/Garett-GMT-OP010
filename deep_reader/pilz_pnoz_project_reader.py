#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VarRef:
    module_id: str
    var_name: str
    equipment_id: str
    opc_name: str
    writable: bool


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_translation_map(visu_model: dict[str, Any]) -> dict[str, str]:
    """
    visuModel.json contains a translations array with entries like:
    { locale: "...", translationentry: [{key:"C123", value:"..."}] }
    """
    out: dict[str, str] = {}
    translations = visu_model.get("translations") or []
    for t in translations:
        entries = t.get("translationentry") or []
        for e in entries:
            k = str(e.get("key") or "").strip()
            v = str(e.get("value") or "").strip()
            if k and v and k not in out:
                out[k] = v
    return out


def flatten_vars(visu_model: dict[str, Any]) -> dict[str, VarRef]:
    """
    Returns mapping from variable reference token (e.g. '85A1.i4') to VarRef with opcName.
    """
    vars_by_ref: dict[str, VarRef] = {}
    for m in visu_model.get("modules") or []:
        module_id = str(m.get("equipmentId") or "").strip()
        for v in m.get("variables") or []:
            name = str(v.get("name") or "").strip()
            if not name:
                continue
            vars_by_ref[name] = VarRef(
                module_id=module_id,
                var_name=name,
                equipment_id=str(v.get("equipmentId") or "").strip(),
                opc_name=str(v.get("opcName") or "").strip(),
                writable=bool(v.get("writable")),
            )
    return vars_by_ref


def read_buildinfo(project_root: Path) -> str:
    p = project_root / "BuildInfo.txt"
    return read_text(p).strip() if p.exists() else ""


def read_connection(project_root: Path) -> dict[str, str]:
    p = project_root / "connection.xml"
    if not p.exists():
        return {}
    # tiny XML, avoid full parser dependency
    txt = read_text(p)
    out: dict[str, str] = {}
    for key in ["Name", "Address", "Port"]:
        needle = f'{key}="'
        idx = txt.find(needle)
        if idx >= 0:
            j = txt.find('"', idx + len(needle))
            if j > idx:
                out[key] = txt[idx + len(needle) : j]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Read Pilz PNOZmulti (PASmulti) project exports and generate CZ mapping reports.")
    ap.add_argument(
        "--project-root",
        default="EXPORT/SAFETY RELAY PILZ/OP10/GarretPilz_Op10_20250814",
        help="Root folder of Pilz project export",
    )
    ap.add_argument("--out-dir", default="deep_reader/reports", help="Output folder for reports/CSVs")
    args = ap.parse_args()

    project_root = Path(args.project_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    visu_path = project_root / "bin/pmimicro/visu/visuModel.json"
    if not visu_path.exists():
        raise SystemExit(f"Missing: {visu_path.as_posix()}")

    visu = json.loads(read_text(visu_path))
    translations = build_translation_map(visu)
    vars_by_ref = flatten_vars(visu)

    buildinfo = read_buildinfo(project_root)
    conn = read_connection(project_root)

    safety_devices = visu.get("safetyDevices") or []
    blocktype_counts = Counter([str(d.get("blockType") or "") for d in safety_devices])

    # Build IO rows from modules
    io_rows: list[dict[str, Any]] = []
    for ref, v in sorted(vars_by_ref.items(), key=lambda kv: (kv[1].module_id, kv[0])):
        human = translations.get(v.equipment_id, "")
        io_rows.append(
            {
                "VarRef": ref,
                "ModuleId": v.module_id,
                "EquipmentId": v.equipment_id,
                "Název(překlad)": human,
                "OPC": v.opc_name,
                "Zapisovatelné": "ANO" if v.writable else "NE",
            }
        )
    write_csv(out_dir / "pilz_io_map.csv", io_rows)

    # Safety devices table
    dev_rows: list[dict[str, Any]] = []
    for idx, d in enumerate(safety_devices, start=1):
        block_type = str(d.get("blockType") or "").strip()
        equipment_id = str(d.get("equipmentId") or "").strip()
        name_raw = str(d.get("name") or "").strip()
        name = name_raw or translations.get(equipment_id, "") or ""
        reset = d.get("resetInput")
        module_refs = d.get("moduleReferences") or []
        var_refs = d.get("variableReferences") or []
        mapped = []
        for r in var_refs:
            vr = vars_by_ref.get(r)
            if vr:
                mapped.append(f"{r} ({translations.get(vr.equipment_id,'') or vr.equipment_id})")
            else:
                mapped.append(str(r))

        dev_rows.append(
            {
                "Idx": idx,
                "Typ": block_type,
                "Název": name,
                "EquipmentId": equipment_id,
                "Moduly": ";".join([str(x) for x in module_refs]),
                "Signály(VarRef)": ";".join([str(x) for x in var_refs]),
                "Signály(popis)": ";".join(mapped),
                "ResetInput": "" if reset is None else str(reset),
            }
        )
    write_csv(out_dir / "pilz_safety_devices.csv", dev_rows)

    # CZ report
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md: list[str] = []
    md.append("# PILZ PNOZmulti – mapování projektu (read-only)\n")
    md.append("## FAKTA\n")
    md.append(f"- Zdroj: `{project_root.as_posix()}`")
    if buildinfo:
        md.append(f"- BuildInfo: `{buildinfo}`")
    if conn:
        md.append(f"- Connection: Name=`{conn.get('Name','')}`, Address=`{conn.get('Address','')}`, Port=`{conn.get('Port','')}`")
    md.append(f"- Čas zpracování: `{now}`")
    md.append(f"- Soubor: `{visu_path.as_posix()}`\n")

    md.append("## Moduly a I/O\n")
    md.append(f"- Počet modulů ve visuModel: `{len(visu.get('modules') or [])}`")
    md.append(f"- Počet I/O proměnných ve visuModel: `{len(vars_by_ref)}`")
    md.append(f"- Export mapy I/O: `deep_reader/reports/pilz_io_map.csv`\n")

    md.append("## Safety funkce (podle `blockType`)\n")
    md.append("| Typ | Počet |")
    md.append("|---|---:|")
    for k, v in sorted(blocktype_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        md.append(f"| `{k or 'unknown'}` | `{v}` |")
    md.append("")
    md.append("- Kompletní seznam instancí: `deep_reader/reports/pilz_safety_devices.csv`\n")

    md.append("## DŮLEŽITÉ OMEZENÍ (pro migraci)\n")
    md.append("- `visuModel.json` typicky obsahuje **seznam bloků a jejich I/O kanály**, ale neobsahuje plné **propojení logiky** (jak jsou bloky navzájem svázané, reset priority, muting, EDM/feedback vazby mezi výstupy a vstupy atd.).")
    md.append("- Proto z těchto dat nelze prokázat 1:1 chování celé safety logiky – slouží jako **inventář** pro vytvoření specifikace a následnou ruční implementaci/validaci v Safety programu.\n")

    md.append("## Výstupy\n")
    md.append("- `deep_reader/reports/pilz_io_map.csv` – mapování VarRef→OPC+název")
    md.append("- `deep_reader/reports/pilz_safety_devices.csv` – seznam bezpečnostních bloků/funkcí + připojené signály")
    md.append("- Tento report: `deep_reader/reports/08_pilz_pnoz_project_map.md`\n")

    write_md(out_dir / "08_pilz_pnoz_project_map.md", "\n".join(md) + "\n")
    print(f"Wrote: {(out_dir / '08_pilz_pnoz_project_map.md').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

