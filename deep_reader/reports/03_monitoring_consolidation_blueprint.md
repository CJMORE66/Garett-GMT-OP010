# Návrh konsolidace monitoringu (strategie bez rozbití)

## FAKTA (z HMI exportů)
- HMI tag tabulky: `65`
- HMI tagy: `2161`
- Nejčastější PLC kořeny (z HMI ControllerTag):
- `AutoProcessData`: `126`
- `PilzData`: `113`
- `ST10_GeneralData`: `105`
- `MEStoPLC`: `97`
- `PalletNGData`: `50`
- `PLCtoMES`: `42`
- `ST10_RecipeDB`: `34`
- `Sys`: `32`
- `ChangeOver_DB`: `29`
- `AutoProcessControl`: `24`
- `MotorControl`: `20`
- `ST10_SafetyGate_InterfaceDB`: `20`
- `ST10_RecipeDB_HMI`: `16`
- `Parameter`: `15`
- `GluingControl`: `14`

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
