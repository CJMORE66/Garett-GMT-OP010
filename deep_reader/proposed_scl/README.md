# Návrh (pouze additivní) – Monitoring DB + mirror blok

Tento adresář obsahuje **návrhové** SCL bloky pro fázi A (read‑only zrcadlení).

## Bezpečnost / rozsah

- Neprovádí žádné změny existujících bloků.
- Blok `FC_MON_Mirror` je navržen jako **read-only** kopírování do nového DB.
- Integrace (volání z `OB1`/`ST10_Main`) není součástí tohoto balíčku – je to samostatný krok během odstávky.

## Soubory

- `UDT_MON_Header.scl`
- `UDT_MON_Sys.scl`
- `UDT_MON_Station.scl`
- `DB_OP010_Monitoring.scl`
- `FC_MON_Mirror.scl`

## Jak použít (doporučený postup)

1) Importujte UDT + DB + FC do projektu (offline).
2) Zkompilujte bez změn stávajícího programu.
3) Teprve potom (během odstávky) přidejte **jedno** volání `FC_MON_Mirror` s `Enable := TRUE`.
4) Ověřte ve watch table, že se hodnoty kopírují a cyklový čas se nezhoršil.

