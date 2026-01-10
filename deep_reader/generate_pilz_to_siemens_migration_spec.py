#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate CZ migration/spec document: Pilz PNOZmulti -> Siemens F-CPU (spec only, no safety code).")
    ap.add_argument("--reports", default="deep_reader/reports", help="Reports folder")
    args = ap.parse_args()

    reports = Path(args.reports)
    devices_csv = reports / "pilz_safety_devices.csv"
    io_csv = reports / "pilz_io_map.csv"
    if not devices_csv.exists() or not io_csv.exists():
        raise SystemExit("Missing pilz_safety_devices.csv or pilz_io_map.csv; run pilz_pnoz_project_reader.py first.")

    dev = read_csv(devices_csv)
    io = read_csv(io_csv)

    by_type: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in dev:
        by_type[(r.get("Typ") or "").strip()].append(r)

    io_by_module: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in io:
        io_by_module[(r.get("ModuleId") or "").strip()].append(r)

    # Minimal counts
    c_types = Counter([r.get("Typ") or "" for r in dev])
    c_io = Counter()
    for r in io:
        varref = (r.get("VarRef") or "")
        if "/I/" in (r.get("OPC") or "") or ".i" in varref:
            c_io["inputs"] += 1
        elif "/O/" in (r.get("OPC") or "") or ".o" in varref:
            c_io["outputs"] += 1
        else:
            c_io["other"] += 1

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md: list[str] = []
    md.append("# Migrace safety: PILZ PNOZmulti → Siemens SIMATIC F-CPU (specifikace)\n")
    md.append("## FAKTA\n")
    md.append(f"- Čas generování: `{now}`")
    md.append(f"- Zdrojový inventář: `{devices_csv.as_posix()}` + `{io_csv.as_posix()}`")
    md.append(f"- Safety funkce v Pilz exportu: `{len(dev)}` instancí")
    md.append(f"- I/O proměnné v Pilz exportu: `{len(io)}` (`vstupy≈{c_io['inputs']}`, `výstupy≈{c_io['outputs']}`, ostatní `{c_io['other']}`)\n")

    md.append("## ZÁSADNÍ BEZPEČNOSTNÍ UPOZORNĚNÍ\n")
    md.append("- Převod safety relé/PNOZ logiky na F-CPU je **bezpečnostně kritická změna**: vyžaduje znovu provést analýzu rizik (PL/SIL), validaci, dokumentaci a řízenou odstávku.")
    md.append("- Tento dokument je **specifikace a mapování** pro implementaci; není to hotový safety program.\n")

    md.append("## Co umíme prokázat z dodaných souborů (evidence)\n")
    md.append("- Seznam safety funkčních bloků/instancí a jejich připojené I/O kanály (např. E-STOP má 2 kanály).")
    md.append("- Názvy signálů (překlady) + jejich OPC cesty (diagnostika/visu).")
    md.append("- Neumíme prokázat: **vnitřní propojení** mezi bloky (muting, reset priority, EDM vazby, logické OR/AND mezi zónami) – v exportu chybí síťová logika.\n")

    md.append("## Inventář bezpečnostních funkcí (souhrn)\n")
    md.append("| Typ (Pilz) | Počet | Poznámka |")
    md.append("|---|---:|---|")
    for k, v in sorted(c_types.items(), key=lambda kv: (-kv[1], kv[0])):
        note = ""
        if k == "E_STOP":
            note = "Nouzové zastavení (2-kanálové vstupy)."
        elif k == "SAFETY_GATE":
            note = "Bezpečnostní dveře/vrata (2-kanálové vstupy)."
        elif k == "LIGHT_CURTAIN":
            note = "Světelná závora (2-kanálové vstupy)."
        elif k == "SEMICONDUCTOR":
            note = "Bezpečný výstup / odpojování (pravděpodobně přes stykač/SSR + EDM)."
        elif k == "COPY_MODULE_INPUT_BLOCK":
            note = "Zpětná vazba (feedback) / přenesení vstupu do diagnostiky."
        md.append(f"| `{k}` | `{v}` | {note} |")
    md.append("")

    md.append("## Mapování I/O (moduly)\n")
    for module_id, rows in sorted(io_by_module.items(), key=lambda kv: kv[0]):
        md.append(f"### Modul `{module_id}`")
        md.append("| VarRef | Název | OPC |")
        md.append("|---|---|---|")
        for r in rows:
            md.append(f"| `{r.get('VarRef','')}` | `{r.get('Název(překlad)','')}` | `{r.get('OPC','')}` |")
        md.append("")

    md.append("## Doporučené konceptuální mapování na Siemens Safety (bez kódu)\n")
    md.append("Níže je doporučené mapování typů (koncept). Konkrétní parametry/časování musí potvrdit safety dokumentace stroje a komisionační testy.\n")
    md.append("| Typ (Pilz) | Typický ekvivalent v Siemens Safety | Poznámka |")
    md.append("|---|---|---|")
    md.append("| `E_STOP` | `F_ESTOP` / `F_EmergencyStop` (knihovna Safety Advanced) | 2-kanál, test zkratu/rozporu, reset logika dle požadavků. |")
    md.append("| `SAFETY_GATE` | `F_DOOR` / `F_Gate` | 2-kanál, může být s/bez blokování, reset/ack dle zóny. |")
    md.append("| `LIGHT_CURTAIN` | `F_LightCurtain` / `F_SafetySensor` | 2-kanál OSSD, případně muting (pokud existuje – zde neprokázáno). |")
    md.append("| `SEMICONDUCTOR` | `F_Q` + `F_FDBK` (EDM) / bezpečný výstup | Vyžaduje definovat, co se odpojuje (stykače, STO, ventily) a jak se kontroluje zpětná vazba. |")
    md.append("| `COPY_MODULE_INPUT_BLOCK` | Diagnostika/EDM vstupy, mapování do standard PLC | V Siemens často zvlášť: bezpečný vstup pro EDM + standardní diagnostické bity. |")
    md.append("")

    md.append("## Minimální validační plán (musí být splněno před nasazením)\n")
    md.append("1) Offline: porovnat všechny bezpečnostní funkce s aktuální bezpečnostní dokumentací stroje (risk assessment, safety matrix).")
    md.append("2) Offline: simulace / Safety Acceptance Test (SAT) pro každý bezpečnostní okruh (E-stop, dveře, světelná závora, robot dveře, materiálové dveře).")
    md.append("3) Online v odstávce: test každého kanálu zvlášť (CH1/CH2), test rozporu kanálů, test resetu, test EDM (zaseknutý stykač).")
    md.append("4) Důkaz: protokol testů + sign-off kompetentní osoby.\n")

    md.append("## Open questions (blokující pro vytvoření 1:1 chování)\n")
    md.append("- Kde je v Pilz projektu export **logického propojení** mezi bloky (graf/schéma)? Bez toho nelze prokázat přesné vazby (např. které dveře vypínají které výstupy).")
    md.append("- Jaké jsou požadované úrovně bezpečnosti (PL/SIL) pro jednotlivé okruhy a jaké jsou požadované reakční časy?")
    md.append("- Jaké výstupy PNOZ skutečně odpojují energii (stykače, STO na servu, ventily) a jaké jsou jejich EDM zpětné vazby?")

    out_path = reports / "09_pilz_to_siemens_safety_spec.md"
    write_text(out_path, "\n".join(md) + "\n")
    print(f"Wrote: {out_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

