#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate CZ monitoring registry from deep_reader/out/hmi_tags.csv.")
    ap.add_argument("--hmi-tags", default="deep_reader/out/hmi_tags.csv", help="Input HMI tags CSV")
    ap.add_argument("--out-dir", default="deep_reader/reports", help="Output directory for reports")
    args = ap.parse_args()

    hmi_path = Path(args.hmi_tags)
    out_dir = Path(args.out_dir)

    rows = read_csv(hmi_path)

    out_rows: list[dict[str, str]] = []
    for r in rows:
        ctl = (r.get("ControllerTag") or "").strip()
        if not ctl:
            continue
        root = ctl.split(".", 1)[0] if "." in ctl else ctl
        out_rows.append(
            {
                "TabulkaHMI": r.get("Table", "") or "",
                "TagHMI": r.get("Name", "") or "",
                "ControllerTag": ctl,
                "KořenPLC": root,
                "DatovýTypPLC": r.get("DataType", "") or "",
                "DatovýTypHMI": r.get("HmiDataType", "") or "",
                "Cyklus": r.get("AcquisitionCycle", "") or "",
                "Spojení": r.get("Connection", "") or "",
                "ZdrojSoubor": r.get("SourcePath", "") or "",
            }
        )

    fieldnames = [
        "TabulkaHMI",
        "TagHMI",
        "ControllerTag",
        "KořenPLC",
        "DatovýTypPLC",
        "DatovýTypHMI",
        "Cyklus",
        "Spojení",
        "ZdrojSoubor",
    ]
    write_csv(out_dir / "monitoring_registry.csv", out_rows, fieldnames)

    # Root summary
    root_counts = Counter(r["KořenPLC"] for r in out_rows)
    summary_rows = [{"KořenPLC": k, "PočetTagů": str(v)} for k, v in root_counts.most_common()]
    write_csv(out_dir / "monitoring_roots_summary.csv", summary_rows, ["KořenPLC", "PočetTagů"])

    # Duplicates by ControllerTag
    ctl_to_tags: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in out_rows:
        ctl_to_tags[r["ControllerTag"]].append(r)
    dup_rows = []
    for ctl, rr in ctl_to_tags.items():
        if len(rr) <= 1:
            continue
        for item in rr:
            dup_rows.append({"ControllerTag": ctl, "TagHMI": item["TagHMI"], "TabulkaHMI": item["TabulkaHMI"], "ZdrojSoubor": item["ZdrojSoubor"]})
    write_csv(out_dir / "monitoring_duplicates.csv", dup_rows, ["ControllerTag", "TagHMI", "TabulkaHMI", "ZdrojSoubor"])

    print(f"Wrote: {out_dir / 'monitoring_registry.csv'}")
    print(f"Wrote: {out_dir / 'monitoring_roots_summary.csv'}")
    print(f"Wrote: {out_dir / 'monitoring_duplicates.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

