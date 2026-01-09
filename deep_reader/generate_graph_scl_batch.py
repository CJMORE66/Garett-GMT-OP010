#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path


def safe_name(name: str) -> str:
    out = []
    for ch in name:
        if ch.isalnum() or ch in {"_", "."}:
            out.append(ch)
        else:
            out.append("_")
    s = "".join(out).strip("_")
    return s[:150] if s else "GraphBlock"


def main() -> int:
    ap = argparse.ArgumentParser(description="Batch-generate SCL from GRAPH XML using tia-xml-to-scl skill script.")
    ap.add_argument("--objects-csv", default="deep_reader/out/objects.csv", help="Objects CSV from tia_deep_reader.py")
    ap.add_argument("--out-dir", default="deep_reader/scl_export/graph_generated", help="Output folder for generated SCL")
    ap.add_argument(
        "--script",
        default="C:/Users/caisik/.codex/skills/tia-xml-to-scl/scripts/graph_xml_to_scl.py",
        help="Path to graph_xml_to_scl.py",
    )
    ap.add_argument("--flow-field", default="Flow", help="DB flow field name passed to generator")
    args = ap.parse_args()

    objects_csv = Path(args.objects_csv)
    out_dir = Path(args.out_dir)
    script = Path(args.script)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "unmapped_symbols.log"

    if not objects_csv.exists():
        raise SystemExit(f"Missing: {objects_csv}")
    if not script.exists():
        raise SystemExit(f"Missing: {script}")

    rows = list(csv.DictReader(objects_csv.read_text(encoding="utf-8").splitlines()))
    graph_rows = [r for r in rows if r.get("kind") == "SW.Blocks.FB" and r.get("language") == "GRAPH" and r.get("source_path")]

    with log_path.open("w", encoding="utf-8") as log:
        for r in graph_rows:
            name = r["name"]
            src = Path(r["source_path"])
            if not src.exists():
                # source_path is workspace-relative; try relative to cwd
                src = Path.cwd() / r["source_path"]
            if not src.exists():
                log.write(f"[SKIP] Missing source: {r['source_path']}\n")
                continue

            out_path = out_dir / f"{safe_name(name)}.scl"
            db_name = f"DB_{safe_name(name)}_State"
            cmd = [
                "python",
                str(script),
                str(src),
                "--output",
                str(out_path),
                "--function-name",
                name,
                "--db-name",
                db_name,
                "--flow-field",
                args.flow_field,
            ]
            p = subprocess.run(cmd, capture_output=True, text=True)
            if p.stdout:
                log.write(p.stdout.rstrip() + "\n")
            if p.stderr:
                log.write(p.stderr.rstrip() + "\n")
            if p.returncode != 0:
                log.write(f"[ERROR] {name} rc={p.returncode}\n")

    print(f"Generated {len(graph_rows)} GRAPH SCL files into: {out_dir}")
    print(f"Unmapped symbols log: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

