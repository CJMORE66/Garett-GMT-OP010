# PILZ PNOZmulti – mapování projektu (read-only)

## FAKTA

- Zdroj: `EXPORT/SAFETY RELAY PILZ/OP10/GarretPilz_Op10_20250814`
- BuildInfo: `v11.3.0 build 7719`
- Connection: Name=`GarretPilz_Op10_20250814`, Address=`192.168.10.63`, Port=`9000`
- Čas zpracování: `2026-01-09 18:04:02`
- Soubor: `EXPORT/SAFETY RELAY PILZ/OP10/GarretPilz_Op10_20250814/bin/pmimicro/visu/visuModel.json`

## Moduly a I/O

- Počet modulů ve visuModel: `6`
- Počet I/O proměnných ve visuModel: `76`
- Export mapy I/O: `deep_reader/reports/pilz_io_map.csv`

## Safety funkce (podle `blockType`)

| Typ | Počet |
|---|---:|
| `SEMICONDUCTOR` | `11` |
| `COPY_MODULE_INPUT_BLOCK` | `10` |
| `SAFETY_GATE` | `10` |
| `E_STOP` | `5` |
| `LIGHT_CURTAIN` | `2` |
| `TIP_SWITCH` | `2` |
| `RS_FLIP_FLOP` | `1` |

- Kompletní seznam instancí: `deep_reader/reports/pilz_safety_devices.csv`

## DŮLEŽITÉ OMEZENÍ (pro migraci)

- `visuModel.json` typicky obsahuje **seznam bloků a jejich I/O kanály**, ale neobsahuje plné **propojení logiky** (jak jsou bloky navzájem svázané, reset priority, muting, EDM/feedback vazby mezi výstupy a vstupy atd.).
- Proto z těchto dat nelze prokázat 1:1 chování celé safety logiky – slouží jako **inventář** pro vytvoření specifikace a následnou ruční implementaci/validaci v Safety programu.

## Výstupy

- `deep_reader/reports/pilz_io_map.csv` – mapování VarRef→OPC+název
- `deep_reader/reports/pilz_safety_devices.csv` – seznam bezpečnostních bloků/funkcí + připojené signály
- Tento report: `deep_reader/reports/08_pilz_pnoz_project_map.md`

