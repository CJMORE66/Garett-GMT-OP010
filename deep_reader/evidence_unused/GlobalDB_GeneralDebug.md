# Důkazní balíček: `GeneralDebug`

## FAKTA

- Objekt: `GeneralDebug`
- Druh: `SW.Blocks.GlobalDB`
- Číslo: `1`
- Jazyk: `DB`
- Deklarace (export): `EXPORT/Program blocks/GeneralDebug.xml`
- Riziko: `RIZIKOVÉ`
- Jistota (bez cross-reference): `NÍZKÁ`

## DŮKAZY (reference / použití)

### Přímé nálezy v exportu (hledání v textu v `EXPORT/Program blocks/**/*.xml`)

- Nálezy `CallInfo Name="GeneralDebug"`: `0`
- Nálezy `Text="GeneralDebug"` (tokenizovaný StructuredText): `0`
- Nálezy `Component Name="GeneralDebug"`: `0`

### Volání bloků (z `deep_reader/out/call_edges.csv`)

- Příchozí volání (kdo volá `GeneralDebug`): `0`
- Odchozí volání (co `GeneralDebug` volá): `0`

- Nejkratší cesta z `01_OB1`: (nenalezeno v extrahovaných datech)
- Dosažitelné z některého OB: `False` (orientačně)

### Použití DB přes symboly (z `deep_reader/out/symbol_usage.csv`)

- Root `GeneralDebug` nebyl nalezen v symbolickém použití (0 záznamů).

### Absolutní adresování DB (orientační scan)

- Pro DB číslo `1` nebyl nalezen výskyt `DB1` / `DB 1` v exportovaných OB/FB/FC (není to důkaz nepoužití).

### Vazby HMI (z `deep_reader/out/hmi_tags.csv`)

- HMI tagy s kořenem `ControllerTag` = `GeneralDebug`: `0`

## RIZIKA / GATE

- V projektu je nalezeno `21` bloků s indikátory nepřímého přístupu (ANY/BLKMOV/PEEK/POKE/AR/AT/VARIANT). To snižuje jistotu 'mrtvé' i při 0 symbolech/0 voláních.
- Vzorek bloků s indikátory:
  - `CheckData`: `PEEK`
  - `CylinderCtrl_V2`: `ANY;AT_view;BLKMOV`
  - `DB_maXYmosNC1`: `ANY`
  - `DB_maXYmosNC2`: `ANY`
  - `Diagnostic`: `ANY;AT_view`
  - `FB_AteqF620`: `AT_view`
  - `KeyenceSR1000Ctrl`: `ANY;AT_view;BLKMOV`
  - `KistlerPresser _FB`: `ANY;AT_view;BLKMOV`
  - `KistlerPresser_Main`: `ANY`
  - `MotorContro`: `Variant`
  - `SINA_PARA_S`: `Variant`
  - `ST10_Alarm`: `ANY;AT_view;P#_pointer;Variant`

## DOPORUČENÍ (bez mazání)

### Jak ověřit v TIA (bez exportu cross-reference)

- Pro bloky: globální vyhledání názvu bloku v projektu (všechny bloky, LAD/STL/GRAPH) a kontrola, zda existuje volání.
- Pro DB: vyhledat kořen DB v symbolickém vyhledávání a zkontrolovat HMI vazby (ControllerTag) + alarmy/trendy.
- Pokud je objekt podezřelý, ale nejistý: během odstávky přidejte dočasné watch/trace a ověřte, zda se hodnoty mění (pozorování bez zásahu / bez zápisu).

### Jak validovat (offline + krátká odstávka)

- Offline kompilace bez změn chování.
- Krátká odstávka: online download pouze additivních objektů (pokud se přidává diagnostika).

### Rollback (pokud by se někdy dělala změna)

- Okamžitý rollback = návrat na poslední zálohu projektu / online compare + download.
- Preferovat nejdříve deaktivaci (podmínka/enable), ne fyzické smazání.
