# Analýza nevyužitých prvků (evidence-driven)

## FAKTA

- Kandidáti na nevolané FC/FB (bez příchozích volání): `23`
- Kandidáti na neodkazované GlobalDB (DB root neviděn): `5`

## PŘEDPOKLADY / OMEZENÍ

- Tato zpráva NEdoporučuje mazání; pouze vypisuje kandidáty k ověření.

- Důkaz volání je z `deep_reader/out/call_edges.csv` (extrakce z FlgNet `CallInfo`); část logiky může být skrytá v STL/GRAPH nebo přes nepřímé volání.

- Důkaz DB/root je z `deep_reader/out/symbol_usage.csv` (kořeny symbolů z PLC + HMI ControllerTag); absolutní adresování (viz `deep_reader/out/absolute_db_refs.csv`) nebo nepřímý přístup může obejít symbolické kořeny.


## KANDIDÁTI (ověřit před jakoukoliv změnou)

### Nevolané bloky (FC/FB)

- `MaterialGate` (SW.Blocks.FB, `LAD`) [Riziko=KRITICKÉ, Jistota=NÍZKÁ] EXPORT/Program blocks/03_Device/102 SafetyGate/MaterialGate.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `ST10_SafetyGate` (SW.Blocks.FC, `SCL`) [Riziko=KRITICKÉ, Jistota=NÍZKÁ] EXPORT/Program blocks/OP010/10_Device/03_SafetyGate/ST10_SafetyGate.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `ST10_StopperCtrl` (SW.Blocks.FB, `LAD`) [Riziko=KRITICKÉ, Jistota=NÍZKÁ] EXPORT/Program blocks/OP010/10_Device/26_Stopper/ST10_StopperCtrl.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `ST10_Stopper_FB` (SW.Blocks.FB, `LAD`) [Riziko=KRITICKÉ, Jistota=NÍZKÁ] EXPORT/Program blocks/OP010/10_Device/06_Stopper/ST10_Stopper_FB.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `SafetyGate` (SW.Blocks.FB, `LAD`) [Riziko=KRITICKÉ, Jistota=NÍZKÁ] EXPORT/Program blocks/03_Device/102 SafetyGate/SafetyGate.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `ChangeOver` (SW.Blocks.FC, `SCL`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/02_Comm/04-ChangeOver/ChangeOver.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `CheckPositioningOrder` (SW.Blocks.FB, `LAD`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/OP010/10_Device/25_V90/Patch/CheckPositioningOrder.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `CylinderModule_V2` (SW.Blocks.FC, `LAD`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/03_Device/101_Cylinder/CylinderModule_V2.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `DT-Chars` (SW.Blocks.FB, `SCL`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/OP010/11_MES/DT-Chars.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `FB_Analog` (SW.Blocks.FB, `LAD`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/03_Device/212 Analog/FB_Analog.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `FB_AteqF620` (SW.Blocks.FB, `SCL`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/03_Device/211 ATEQ LeakTest/FB_AteqF620.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `FB_Keyence_SR1000` (SW.Blocks.FB, `SCL`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/03_Device/214_KeyenceSR X80/FB_Keyence_SR1000.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `FB_Next` (SW.Blocks.FB, `SCL`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/03_Device/999 Base/999.0 General/999.0.3 FB/FB_Next.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `FB_Step` (SW.Blocks.FB, `LAD`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/03_Device/999 Base/FB_Step.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `IAI_BASE_FB` (SW.Blocks.FB, `SCL`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/OP010/10_Device/22_IAI/IAI_BASE_FB.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `PartDataManage` (SW.Blocks.FB, `SCL`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/03_Device/104 PartDataManage/PartDataManage.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `ST10Cyl_interface91-100` (SW.Blocks.FC, `LAD`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/OP010/10_Device/01_Cylinder/ST10Cyl_interface91-100.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `ST10_Analog` (SW.Blocks.FC, `SCL`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/OP010/10_Device/08_PressureAanlog/ST10_Analog.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `ST10_PartData` (SW.Blocks.FC, `SCL`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/OP010/12_PartData/ST10_PartData.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `SevroStart&PosCheck` (SW.Blocks.FB, `LAD`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/OP010/10_Device/25_V90/V90_Standard/ServoCheck/SevroStart&PosCheck.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `SevroStart&PosCheck_IAI` (SW.Blocks.FB, `LAD`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/OP010/10_Device/22_IAI/ServoCheck/SevroStart&PosCheck_IAI.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `fcFixtureCheck` (SW.Blocks.FC, `LAD`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/03_Device/100 FixtureCheck/fcFixtureCheck.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`
- `块_1` (SW.Blocks.FC, `LAD`) [Riziko=RIZIKOVÉ, Jistota=STŘEDNÍ] EXPORT/Program blocks/OP010/10_Device/25_V90/Patch/块_1.xml | Důkaz: Žádná příchozí volání v `deep_reader/out/call_edges.csv`

### Neodkazované GlobalDB

- `GeneralDebug` (DB1) [Riziko=RIZIKOVÉ, Jistota=NÍZKÁ] EXPORT/Program blocks/GeneralDebug.xml | Důkaz: Název DB nebyl nalezen jako kořen symbolů v `deep_reader/out/symbol_usage.csv` (jsou sloučené PLC symboly i HMI `ControllerTag`)
- `OP010_MES_RecipeDB` (DB9) [Riziko=RIZIKOVÉ, Jistota=NÍZKÁ] EXPORT/Program blocks/OP010/08_ChangeOver/MES/OP010_MES_RecipeDB.xml | Důkaz: Název DB nebyl nalezen jako kořen symbolů v `deep_reader/out/symbol_usage.csv` (jsou sloučené PLC symboly i HMI `ControllerTag`)
- `PalletRelease` (DB9001) [Riziko=RIZIKOVÉ, Jistota=NÍZKÁ] EXPORT/Program blocks/OP010/03_Auto/PalletRelease.xml | Důkaz: Název DB nebyl nalezen jako kořen symbolů v `deep_reader/out/symbol_usage.csv` (jsou sloučené PLC symboly i HMI `ControllerTag`)
- `Scanner1LoadData` (DB530) [Riziko=RIZIKOVÉ, Jistota=NÍZKÁ] EXPORT/Program blocks/OP010/11_MES/Scanner1LoadData.xml | Důkaz: Název DB nebyl nalezen jako kořen symbolů v `deep_reader/out/symbol_usage.csv` (jsou sloučené PLC symboly i HMI `ControllerTag`)
- `Station8UnLoadData` (DB525) [Riziko=RIZIKOVÉ, Jistota=NÍZKÁ] EXPORT/Program blocks/OP010/11_MES/Station8UnLoadData.xml | Důkaz: Název DB nebyl nalezen jako kořen symbolů v `deep_reader/out/symbol_usage.csv` (jsou sloučené PLC symboly i HMI `ControllerTag`)

## DOPORUČENÍ (bezpečné ověření)

- V TIA: pro každý kandidát vyhledejte reference (PLC i HMI) a potvrďte 0 výskytů.

- Pokud je to stále nejasné: použijte dočasné watch/trace (bez změny chování) nebo existující diagnostické počitadla.

- Teprve po delším ověření v provozu: uvažujte o odstranění během odstávky s triviálním rollbackem.
