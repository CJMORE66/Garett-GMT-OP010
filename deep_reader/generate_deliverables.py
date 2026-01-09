#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
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
    "pilz",
]

COMMS_KEYWORDS = [
    "opc",
    "opcu",
    "opcuA",
    "mes",
    "shopworx",
    "modbus",
    "tcp",
    "profinet",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def normalize_keyword(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def classify_keywords(name_or_path: str, keywords: list[str]) -> list[str]:
    n = normalize_keyword(name_or_path)
    hits = []
    for kw in keywords:
        if normalize_keyword(kw) in n:
            hits.append(kw)
    return hits


@dataclass(frozen=True)
class Obj:
    kind: str
    name: str
    number: str
    language: str
    source_path: str


def build_call_graph(call_edges: list[dict[str, str]]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    callers_to_callees: dict[str, set[str]] = defaultdict(set)
    callee_to_callers: dict[str, set[str]] = defaultdict(set)
    for row in call_edges:
        caller = row.get("caller", "").strip()
        callee = row.get("callee", "").strip()
        if not caller or not callee:
            continue
        callers_to_callees[caller].add(callee)
        callee_to_callers[callee].add(caller)
    return callers_to_callees, callee_to_callers


def bfs_call_tree(roots: list[str], callers_to_callees: dict[str, set[str]], max_depth: int = 4) -> dict[str, list[tuple[int, str]]]:
    out: dict[str, list[tuple[int, str]]] = {}
    for root in roots:
        seen: set[str] = set([root])
        q: deque[tuple[str, int]] = deque([(root, 0)])
        lines: list[tuple[int, str]] = [(0, root)]
        while q:
            node, depth = q.popleft()
            if depth >= max_depth:
                continue
            for callee in sorted(callers_to_callees.get(node, set())):
                if callee in seen:
                    continue
                seen.add(callee)
                lines.append((depth + 1, callee))
                q.append((callee, depth + 1))
        out[root] = lines
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate Deep Reader deliverables from deep_reader/out/*.")
    ap.add_argument("--out", default="deep_reader/out", help="Input folder from tia_deep_reader.py")
    ap.add_argument("--reports", default="deep_reader/reports", help="Output folder for deliverables")
    args = ap.parse_args()

    out_dir = Path(args.out)
    reports_dir = Path(args.reports)
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
    hw = None
    hw_path = out_dir / "hardware_aml_summary.json"
    if hw_path.exists():
        hw = json.loads(hw_path.read_text(encoding="utf-8"))
    objects_rows = read_csv(out_dir / "objects.csv")
    call_edges_rows = read_csv(out_dir / "call_edges.csv")
    symbol_usage_rows = read_csv(out_dir / "symbol_usage.csv")
    hmi_rows = read_csv(out_dir / "hmi_tags.csv")
    plc_tag_rows = read_csv(out_dir / "plc_tags.csv")
    edge_rows = read_csv(out_dir / "edge_case_scan.csv")
    hmi_dupes: dict[str, list[str]] = json.loads((out_dir / "hmi_controller_tag_duplicates.json").read_text(encoding="utf-8"))

    objects = [
        Obj(
            kind=r.get("kind", ""),
            name=r.get("name", ""),
            number=r.get("number", "") or "",
            language=r.get("language", "") or "",
            source_path=r.get("source_path", "") or "",
        )
        for r in objects_rows
        if r.get("kind") and r.get("name")
    ]

    kind_counts = Counter(o.kind for o in objects)
    ob_list = sorted([o for o in objects if o.kind == "SW.Blocks.OB"], key=lambda o: int(o.number) if o.number.isdigit() else 9999)

    callers_to_callees, callee_to_callers = build_call_graph(call_edges_rows)
    root_obs = [o.name for o in ob_list if o.number in {"1", "100", "101", "102", "80", "82", "83", "86", "121", "122", "32", "35", "40"}]
    if "01_OB1" in {o.name for o in ob_list}:
        root_obs = ["01_OB1"] + [r for r in root_obs if r != "01_OB1"]
    call_trees = bfs_call_tree(root_obs[:3], callers_to_callees, max_depth=4)  # keep readable

    # HMI monitoring map (controller tag roots)
    controller_tags = [r.get("ControllerTag", "") for r in hmi_rows if r.get("ControllerTag")]
    controller_root_counts = Counter((ct.split(".", 1)[0] if "." in ct else ct) for ct in controller_tags)
    top_hmi_roots = controller_root_counts.most_common(15)

    # PLC tag tables (IO mapping evidence)
    plc_tables = Counter(r.get("Table", "") for r in plc_tag_rows if r.get("Table"))

    # Edge cases
    edge_case_blocks = [(r.get("block", ""), r.get("hits", "")) for r in edge_rows if r.get("hits")]

    # Registr NEŠAHAT (evidence by name/path match + critical OBs)
    no_touch: list[dict[str, Any]] = []
    for o in objects:
        hits = classify_keywords(o.name, SAFETY_KEYWORDS) + classify_keywords(o.source_path, SAFETY_KEYWORDS)
        comms_hits = classify_keywords(o.name, COMMS_KEYWORDS) + classify_keywords(o.source_path, COMMS_KEYWORDS)
        reasons: list[str] = []
        if o.kind == "SW.Blocks.OB":
            if o.number in {"1", "100", "101", "102", "80", "82", "83", "86", "121", "122", "32", "35", "40"}:
                reasons.append("Komisionačně kritický OB")
        if hits:
            reasons.append(f"Bezpečnostně-adjacentní klíčová slova: {', '.join(sorted(set(hits)))}")
        if comms_hits and ("mes" in [normalize_keyword(x) for x in comms_hits] or "opcu" in normalize_keyword("".join(comms_hits))):
            reasons.append(f"Externí rozhraní (klíčová slova): {', '.join(sorted(set(comms_hits)))}")
        if reasons:
            no_touch.append(
                {
                    "Objekt": o.name,
                    "Druh": o.kind,
                    "Číslo": o.number,
                    "Jazyk": o.language,
                    "Cesta": o.source_path,
                    "Důvody": " | ".join(reasons),
                    "Jistota": "STŘEDNÍ",
                }
            )

    # Unused candidates (evidence-driven but conservative)
    blocks_fc_fb = [o for o in objects if o.kind in {"SW.Blocks.FC", "SW.Blocks.FB"}]
    unused_blocks = []
    for o in blocks_fc_fb:
        callers = callee_to_callers.get(o.name, set())
        if not callers:
            confidence = "STŘEDNÍ"
            risk = "RIZIKOVÉ"
            # Graph/STL call visibility can be incomplete
            if o.language in {"GRAPH", "STL"}:
                confidence = "NÍZKÁ"
            # Bezpečnostně-adjacentní pojmenování => NEŠAHAT
            if classify_keywords(o.name, SAFETY_KEYWORDS) or classify_keywords(o.source_path, SAFETY_KEYWORDS):
                risk = "KRITICKÉ"
                confidence = "NÍZKÁ"
            unused_blocks.append(
                {
                    "name": o.name,
                    "kind": o.kind,
                    "language": o.language,
                    "source_path": o.source_path,
                    "evidence": "Žádná příchozí volání v `deep_reader/out/call_edges.csv`",
                    "confidence": confidence,
                    "risk": risk,
                }
            )

    # Unused DB candidates
    symbol_roots_used = {r.get("root", "") for r in symbol_usage_rows if r.get("root")}
    dbs = [o for o in objects if o.kind == "SW.Blocks.GlobalDB"]
    unused_dbs = []
    for db in dbs:
        if db.name not in symbol_roots_used:
            confidence = "NÍZKÁ" if edge_case_blocks else "STŘEDNÍ"
            risk = "RIZIKOVÉ"
            if classify_keywords(db.name, SAFETY_KEYWORDS) or classify_keywords(db.source_path, SAFETY_KEYWORDS):
                risk = "KRITICKÉ"
                confidence = "NÍZKÁ"
            unused_dbs.append(
                {
                    "name": db.name,
                    "number": db.number,
                    "source_path": db.source_path,
                    "evidence": "Název DB nebyl nalezen jako kořen symbolů v `deep_reader/out/symbol_usage.csv` (jsou sloučené PLC symboly i HMI `ControllerTag`)",
                    "confidence": confidence,
                    "risk": risk,
                }
            )

    # Reports
    facts_lines = []
    facts_lines.append(f"- Kořen exportu: `{summary['export_root']}`")
    facts_lines.append(
        f"- Počet zpracovaných XML: `{summary['counts']['program_blocks_files'] + summary['counts']['plc_types_files'] + summary['counts']['plc_tags_files'] + summary['counts']['hmi_tags_files']}`"
    )
    facts_lines.append(f"- Nalezené objekty (bloky+typy+tagy): `{summary['counts']['objects']}`")
    facts_lines.append(f"- Programové bloky (XML): `{summary['counts']['program_blocks_files']}`")
    facts_lines.append(f"- PLC datové typy (XML): `{summary['counts']['plc_types_files']}`")
    facts_lines.append(f"- PLC tagy (XML): `{summary['counts']['plc_tags_files']}`")
    facts_lines.append(f"- HMI tagy (XML): `{summary['counts']['hmi_tags_files']}`")
    facts_lines.append(f"- Extrahované hrany volání: `{summary['counts']['call_edges']}`")
    facts_lines.append(f"- Záznamy použití symbolů: `{summary['counts']['symbol_usage_entries']}`")

    ob_lines = "\n".join([f"- `{o.name}` (OB{o.number}, `{o.language}`) `{o.source_path}`" for o in ob_list])
    kind_lines = "\n".join([f"- `{k}`: `{v}`" for k, v in sorted(kind_counts.items())])
    call_tree_lines = []
    for root, lines in call_trees.items():
        call_tree_lines.append(f"- Kořen `{root}`:")
        for depth, node in lines[1:]:
            call_tree_lines.append(f"  - {'  ' * (depth - 1)}`{node}`")
        if len(lines) == 1:
            call_tree_lines.append("  - (žádná extrahovaná volání v dané hloubce)")
    call_tree_text = "\n".join(call_tree_lines) if call_tree_lines else "- (no roots found)"

    monitoring_lines = []
    monitoring_lines.append(
        f"- HMI tagy exportované: `{len(hmi_rows)}` (tabulky: `{len(set(r.get('Table','') for r in hmi_rows if r.get('Table')) )}`)"
    )
    monitoring_lines.append(f"- Unikátní HMI `ControllerTag`: `{len(set(controller_tags))}`")
    monitoring_lines.append(
        f"- `ControllerTag` s duplicitní HMI vazbou: `{len(hmi_dupes)}` (`deep_reader/out/hmi_controller_tag_duplicates.json`)"
    )
    monitoring_lines.append("- Nejčastější PLC kořeny používané v HMI `ControllerTag`:")
    for root, c in top_hmi_roots:
        monitoring_lines.append(f"  - `{root}`: `{c}`")
    monitoring_text = "\n".join(monitoring_lines)

    edge_lines = []
    if edge_case_blocks:
        edge_lines.append("- Nalezené indikátory nepřímého/okrajového přístupu (hledání v textu):")
        for blk, hits in edge_case_blocks[:25]:
            edge_lines.append(f"  - `{blk}`: `{hits}`")
    else:
        edge_lines.append("- String scan nenašel indikátory (`ANY`, `BLKMOV`, `PEEK/POKE`, `AR1/AR2`, `AT`, `VARIANT`).")

    abs_db_unique = int(summary.get("counts", {}).get("absolute_db_numbers_referenced_hint", 0) or 0)
    abs_db_hits = int(summary.get("counts", {}).get("absolute_db_total_hits_hint", 0) or 0)
    if abs_db_unique:
        edge_lines.append(
            f"- Nálezy absolutního adresování DB (hledání v textu): `{abs_db_unique}` různých DB, `{abs_db_hits}` výskytů (viz `deep_reader/out/absolute_db_refs.csv`)."
        )
    else:
        edge_lines.append("- Absolutní adresování DB nebylo detekováno (orientačně, viz `deep_reader/out/absolute_db_refs.csv`).")
    edge_text = "\n".join(edge_lines)

    hw_lines = []
    if isinstance(hw, dict) and hw.get("cpus"):
        hw_lines.append("- Zdroj (AutomationML): `{}`".format(hw.get("source_path", "")))
        for cpu in hw.get("cpus", []):
            hw_lines.append(
                "- CPU: `{}` / `{}` / `{}` / FW `{}`".format(
                    cpu.get("Name", ""),
                    cpu.get("TypeName", ""),
                    cpu.get("TypeIdentifier", ""),
                    cpu.get("FirmwareVersion", ""),
                )
            )
        nets = hw.get("networks") or []
        if nets:
            hw_lines.append("- PN sítě (z AML): " + ", ".join([f"`{n}`" for n in nets]))
        hw_lines.append(f"- Moduly (vzorek): `{hw.get('modules_count', '')}` celkem, vzorek v `deep_reader/out/hardware_aml_summary.json`")
    else:
        hw_lines.append("- Hardware export (AutomationML) nebyl nalezen nebo se nepodařilo načíst.")

    comp_report = f"""# Zpráva o porozumění projektu

## FAKTA (z exportů)
{chr(10).join(facts_lines)}

### Inventář objektů
{kind_lines}

### Komisionačně kritické OB (NEŠAHAT)
{ob_lines}

### Hierarchie volání (extrahováno, omezená hloubka)
{call_tree_text}

### Monitoring mapa (z HMI tagů)
{monitoring_text}

### Nepřímé adresování / okrajové případy
{edge_text}

### Hardware / IO (z AutomationML)
{chr(10).join(hw_lines)}

## PŘEDPOKLADY / OMEZENÍ
- Cross-reference export není k dispozici; proto jsou výstupy “nepoužité/mrtvé” pouze kandidáti k ověření (bez doporučení mazání).
- Explicitní bezpečnostní program (F-CPU/F-Blocks/F-OBs) nebyl nalezen v `EXPORT/Program blocks`; položky se “Safety/EStop/Door/Guard/…” jsou označeny jako NEŠAHAT konzervativně.
- Inferování read/write je orientační: `CallInfo Parameter Section`, LAD `Contact`=read a `Coil/SCoil/RCoil`=write; StructuredText používá jednoduchou heuristiku (přiřazení `:=`, výstupní vazba `=>`).

## DOPORUČENÍ (bezpečné další kroky)
- Pokud chcete zvýšit jistotu “nepoužité”: postupujte přes TIA vyhledávání symbolu v projektu a HMI (bez mazání), případně dočasné watch/trace (pozorování bez zásahu / bez zápisu).
- Pro konsolidaci monitoringu začněte vždy fází A (zrcadlení pouze pro monitoring do nového DB), bez přepojení HMI tagů v prvním kroku.
"""
    write_text(reports_dir / "01_project_comprehension_report.md", comp_report)

    unused_report_lines = []
    unused_report_lines.append("# Analýza nevyužitých prvků (evidence-driven)\n")
    unused_report_lines.append("## FAKTA\n")
    unused_report_lines.append(f"- Kandidáti na nevolané FC/FB (bez příchozích volání): `{len(unused_blocks)}`")
    unused_report_lines.append(f"- Kandidáti na neodkazované GlobalDB (DB root neviděn): `{len(unused_dbs)}`\n")
    unused_report_lines.append("## PŘEDPOKLADY / OMEZENÍ\n")
    unused_report_lines.append("- Tato zpráva NEdoporučuje mazání; pouze vypisuje kandidáty k ověření.\n")
    unused_report_lines.append("- Důkaz volání je z `deep_reader/out/call_edges.csv` (extrakce z FlgNet `CallInfo`); část logiky může být skrytá v STL/GRAPH nebo přes nepřímé volání.\n")
    unused_report_lines.append("- Důkaz DB/root je z `deep_reader/out/symbol_usage.csv` (kořeny symbolů z PLC + HMI ControllerTag); absolutní adresování (viz `deep_reader/out/absolute_db_refs.csv`) nebo nepřímý přístup může obejít symbolické kořeny.\n")
    unused_report_lines.append("\n## KANDIDÁTI (ověřit před jakoukoliv změnou)\n")
    unused_report_lines.append("### Nevolané bloky (FC/FB)\n")
    for row in sorted(unused_blocks, key=lambda r: (r["risk"], r["confidence"], r["name"]))[:80]:
        unused_report_lines.append(
            f"- `{row['name']}` ({row['kind']}, `{row['language']}`) [Riziko={row['risk']}, Jistota={row['confidence']}] {row['source_path']} | Důkaz: {row['evidence']}"
        )
    if len(unused_blocks) > 80:
        unused_report_lines.append(f"- (truncated) Full list derivable from `deep_reader/out/objects.csv` + `deep_reader/out/call_edges.csv`.")
    unused_report_lines.append("\n### Neodkazované GlobalDB\n")
    for row in sorted(unused_dbs, key=lambda r: (r["risk"], r["confidence"], r["name"]))[:80]:
        unused_report_lines.append(
            f"- `{row['name']}` (DB{row['number']}) [Riziko={row['risk']}, Jistota={row['confidence']}] {row['source_path']} | Důkaz: {row['evidence']}"
        )
    if len(unused_dbs) > 80:
        unused_report_lines.append(f"- (truncated) Full list derivable from `deep_reader/out/objects.csv` + `deep_reader/out/symbol_usage.csv`.")

    unused_report_lines.append("\n## DOPORUČENÍ (bezpečné ověření)\n")
    unused_report_lines.append("- V TIA: pro každý kandidát vyhledejte reference (PLC i HMI) a potvrďte 0 výskytů.\n")
    unused_report_lines.append("- Pokud je to stále nejasné: použijte dočasné watch/trace (bez změny chování) nebo existující diagnostické počitadla.\n")
    unused_report_lines.append("- Teprve po delším ověření v provozu: uvažujte o odstranění během odstávky s triviálním rollbackem.\n")
    write_text(reports_dir / "02_unused_elements_analysis.md", "\n".join(unused_report_lines))

    # Monitoring consolidation blueprint
    blueprint = f"""# Návrh konsolidace monitoringu (strategie bez rozbití)

## FAKTA (z HMI exportů)
- HMI tag tabulky: `{len(set(r.get('Table','') for r in hmi_rows if r.get('Table')) )}`
- HMI tagy: `{len(hmi_rows)}`
- Nejčastější PLC kořeny (z HMI ControllerTag):
{chr(10).join([f"- `{root}`: `{c}`" for root, c in top_hmi_roots])}

## PŘEDPOKLADY / OMEZENÍ
- `ControllerTag` beru jako autoritativní vazbu HMI → PLC symbol (z `EXPORT/HMI tags/**/*.xml`).
- “Pouze monitoring” na PLC straně nelze bez cross-reference + alarm/trend exportů prokázat; návrh je proto konzervativní: nejdřív zrcadlení pouze pro monitoring.

## DOPORUČENÍ (varianta A: nejdřív zrcadlení, nejbezpečnější)
### Navržené nové objekty (pouze přidat)
- Nový GlobalDB: `DB_OP010_Monitoring` (optimalizovaný přístup; pouze pro čtení)
- Volitelné UDT: `UDT_MON_Header`, `UDT_MON_Sys`, `UDT_MON_Area_*`

### Návrh struktury DB (dle oblastí)
- `Header` (metadata kvalita/čas)
- `Sys` (shrnutí CPU/Com/Mode, cyklový čas, stavy)
- `Area` skupiny dle existujících HMI tabulek / oblastí stanice:
  - `Cyl`, `IOVisual`, `IAI`, `IV3`, `Kistler`, `Motor`, `Robot`, `Servo`, `ChangeOver`, `MES`, `Alarm`

### Strategie kompatibility s legacy
- Ponechat všechny existující PLC symboly a HMI tagy beze změny.
- Přidat jednu “mirror” rutinu (např. `FC_MON_Mirror`), která kopíruje vybrané hodnoty do `DB_OP010_Monitoring` každý cyklus.
- Mirror je vůči řízení striktně pouze pro čtení: nesmí být použit v řídicí logice; HMI lze přepojit až později (volitelně).

### Validace (neočekává se změna chování)
- Online compare: ověřit, že jsou pouze přidané bloky/DB (žádné změny stávajících).
- Runtime: ověřit dopad na cyklový čas a že nevznikají diagnostiky.
- HMI: potvrdit beze změny (Fáze A), poté volitelně přepojovat obrazovky po jedné (Fáze B).

### Výstupy pro implementaci (už připraveno v tomto workspace)
- Registr HMI→PLC: `deep_reader/reports/monitoring_registry.csv` + souhrn `deep_reader/reports/monitoring_roots_summary.csv`
- Duplicitní vazby: `deep_reader/reports/monitoring_duplicates.csv`
- Návrh SCL (additivní DB+FC pro zrcadlení): `deep_reader/proposed_scl/README.md`
"""
    write_text(reports_dir / "03_monitoring_consolidation_blueprint.md", blueprint)

    # Migration roadmap + rollback
    roadmap = """# Migrační roadmapa + test plán + rollback plán

## Fáze A — Read-only zrcadlení (NEPORUŠIT)
### PROČ
- Centralizace monitoringu bez zásahu do řízení nebo HMI vazeb.

### CO (dotčené objekty)
- Přidat `DB_OP010_Monitoring` (+ volitelné UDT)
- Přidat `FC_MON_Mirror` (nebo ekvivalent) volaný z existujícího cyklického místa (typicky `OB1`/`ST10_Main`) jedním novým voláním.

### JAK (kroky)
1) Vytvořit nový DB + UDT.
2) Implementovat mirror s explicitními přiřazeními (bez nepřímého adresování).
3) Zavolat mirror z jednoho známého cyklického bodu.

### JAK OVĚŘIT
- Offline kompilace.
- Online download během odstávky.
- Watch table: porovnat vzorek signálů (legacy vs nový DB).
- Změřit dopad na cyklový čas.

### JAK VRÁTIT ZPĚT (ROLLBACK)
- Odebrat volání mirroru (nebo vypnout jedním enable bitem) a znovu nahrát.
- DB lze ponechat pro forenzní porovnání.

## Fáze B — Přepojení HMI (volitelné, po krocích)
### PROČ
- Zmenšení tag “sprawlu”, standardizace názvosloví.

### CO
- Mění se pouze HMI tag vazby (`ControllerTag`), PLC řízení zůstává beze změny.

### JAK
- Vytvořit nové (duplicitní) tagy na `DB_OP010_Monitoring`.
- Přepojovat obrazovky jednu po druhé.

### JAK OVĚŘIT
- Akceptační test obrazovka po obrazovce.
- Ověření alarmů/trendů (pokud se používají).

### JAK VRÁTIT ZPĚT
- Vrátit HMI `ControllerTag` na původní symboly.

## Fáze C — Úklid (POUZE po dlouhodobém ověření)
### PROČ
- Odstranění prokázaných duplikátů/mrtvých prvků.

### BRÁNA (GATE)
- 0 referencí v PLC + HMI + alarm/trend.
- Žádné riziko nepřímého přístupu.
"""
    write_text(reports_dir / "04_migration_roadmap.md", roadmap)

    # Risk matrix (CSV)
    risk_rows = [
        {
            "Změna": "Přidat DB_OP010_Monitoring (nový GlobalDB)",
            "Dopad": "Nízký (additivní)",
            "Pravděpodobnost": "Nízká",
            "Detekovatelnost": "Vysoká",
            "Mitigace": "Pouze přidat; bez změny existujících tagů; sledovat diagnostiku",
            "Validace": "Kompilace + online download + watch porovnání + kontrola cyklu",
        },
        {
            "Změna": "Přidat FC_MON_Mirror a volat z OB1/ST10_Main",
            "Dopad": "Střední (přidává cyklický čas)",
            "Pravděpodobnost": "Nízká/Střední",
            "Detekovatelnost": "Vysoká",
            "Mitigace": "Pouze čtení (bez zápisu); podmínit enable; minimalizovat běhový čas",
            "Validace": "Monitoring cyklu/diagnostiky; funkční pozorování",
        },
        {
            "Změna": "Přepojit HMI tagy na nový DB (Fáze B)",
            "Dopad": "Střední (změna zdroje vizualizace)",
            "Pravděpodobnost": "Střední",
            "Detekovatelnost": "Vysoká",
            "Mitigace": "Po obrazovkách; zachovat legacy tagy; okamžitý revert",
            "Validace": "Akceptační test po obrazovkách; kontrola trendů/alarmů",
        },
        {
            "Změna": "Odstranit legacy tagy/DB (Fáze C)",
            "Dopad": "Vysoký (riziko skrytých referencí)",
            "Pravděpodobnost": "Střední",
            "Detekovatelnost": "Střední",
            "Mitigace": "Vyžadovat důkaz referencí + dlouhodobé ověření; pouze v odstávce",
            "Validace": "Kontrolované testy v odstávce + rollback plán",
        },
    ]
    with (reports_dir / "05_risk_assessment_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(risk_rows[0].keys()))
        w.writeheader()
        w.writerows(risk_rows)

    # Registr NEŠAHAT (CSV)
    if no_touch:
        with (reports_dir / "no_touch_register.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(no_touch[0].keys()))
            w.writeheader()
            w.writerows(sorted(no_touch, key=lambda r: (r["Druh"], r["Objekt"])))

    index_md = """# OP10 – index výstupů (Deep Reader)

## Co je hotové (FINAL GATE)
- [x] Struktura projektu namapovaná (inventář objektů)
- [x] Call tree / závislosti (omezeno na extrahovatelná volání)
- [x] Mapa použití proměnných (orientační čtení/zápis, bez cross-reference)
- [x] Monitoring body identifikované (HMI tag export → ControllerTag)
- [x] Registr NEŠAHAT vytvořen (konzervativně podle názvů + kritických OB)
- [x] Okrajové případy zkontrolované (ANY/BLKMOV/PEEK/POKE/AR/AT/VARIANT + absolutní DB scan)

## Hlavní reporty (čeština)
- `deep_reader/reports/01_project_comprehension_report.md`
- `deep_reader/reports/02_unused_elements_analysis.md`
- `deep_reader/reports/03_monitoring_consolidation_blueprint.md`
- `deep_reader/reports/04_migration_roadmap.md`
- `deep_reader/reports/05_risk_assessment_matrix.csv`
- `deep_reader/reports/06_zavislosti_a_ostrovy.md`
- `deep_reader/reports/no_touch_register.csv`

## Důkazní balíčky (režim 2)
- `deep_reader/evidence_unused/INDEX.md`
- `deep_reader/evidence_unused/souhrn_kandidatu.csv`

## Surová data / evidence
- `deep_reader/out/summary.json`
- `deep_reader/out/objects.csv`, `deep_reader/out/call_edges.csv`, `deep_reader/out/symbol_usage.csv`
- `deep_reader/out/hmi_tags.csv`, `deep_reader/out/plc_tags.csv`
- `deep_reader/out/edge_case_scan.csv`, `deep_reader/out/absolute_db_refs.csv`

## Offline SCL export (pro čtení/porovnání)
- `deep_reader/scl_export/` (XML → SCL, orientační převod)
- `deep_reader/scl_export/graph_generated/` (GRAPH → SCL, orientační převod)
"""
    write_text(reports_dir / "00_index.md", index_md)

    print(f"Wrote deliverables to: {reports_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
