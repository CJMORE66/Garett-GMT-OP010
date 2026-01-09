# Zpráva o porozumění projektu

## FAKTA (z exportů)
- Kořen exportu: `EXPORT`
- Počet zpracovaných XML: `521`
- Nalezené objekty (bloky+typy+tagy): `427`
- Programové bloky (XML): `279`
- PLC datové typy (XML): `148`
- PLC tagy (XML): `19`
- HMI tagy (XML): `75`
- Extrahované hrany volání: `187`
- Záznamy použití symbolů: `2543`

### Inventář objektů
- `SW.Blocks.FB`: `64`
- `SW.Blocks.FC`: `44`
- `SW.Blocks.GlobalDB`: `80`
- `SW.Blocks.InstanceDB`: `81`
- `SW.Blocks.OB`: `10`
- `SW.Types.PlcStruct`: `148`

### Komisionačně kritické OB (NEŠAHAT)
- `01_OB1` (OB1, `LAD`) `EXPORT/Program blocks/01_OB/01_OB1.xml`
- `03_CYC_INT2` (OB32, `LAD`) `EXPORT/Program blocks/01_OB/03_CYC_INT2.xml`
- `04_CYC_INT5` (OB35, `LAD`) `EXPORT/Program blocks/01_OB/04_CYC_INT5.xml`
- `08_HW_INT0` (OB40, `LAD`) `EXPORT/Program blocks/01_OB/08_HW_INT0.xml`
- `07_CYCL_FLT` (OB80, `STL`) `EXPORT/Program blocks/01_OB/07_CYCL_FLT.xml`
- `09_I/O_FLT1` (OB82, `STL`) `EXPORT/Program blocks/01_OB/09_IO_FLT1.xml`
- `12_RACK_FLT` (OB86, `STL`) `EXPORT/Program blocks/01_OB/12_RACK_FLT.xml`
- `02_Warm Restart` (OB100, `LAD`) `EXPORT/Program blocks/01_OB/02_Warm Restart.xml`
- `11_PROG_ERR` (OB121, `STL`) `EXPORT/Program blocks/01_OB/11_PROG_ERR.xml`
- `05_MOD_ERR` (OB122, `STL`) `EXPORT/Program blocks/01_OB/05_MOD_ERR.xml`

### Hierarchie volání (extrahováno, omezená hloubka)
- Kořen `01_OB1`:
  - `AutoProcessDataPopUp`
  - `Diagnostic`
  - `ST10_Main`
  -   `CylinderCtrl_V2`
  -   `MES`
  -   `ST10Cyl_interface1-10`
  -   `ST10Cyl_interface11-20`
  -   `ST10Cyl_interface21-30`
  -   `ST10Cyl_interface31-40`
  -   `ST10Cyl_interface41-50`
  -   `ST10Cyl_interface51-60`
  -   `ST10Cyl_interface61-70`
  -   `ST10Cyl_interface71-80`
  -   `ST10Cyl_interface81-90`
  -   `ST10_Alarm`
  -   `ST10_Auto`
  -   `ST10_ChangeOver`
  -   `ST10_CountCycleTimeMain`
  -   `ST10_Device`
  -   `ST10_Input`
  -   `ST10_Manual`
  -   `ST10_Output`
  -   `ST10_Tip`
  -   `ST10_Warning`
  -   `SystemMode`
  -     `MES_CHeck`
  -     `CheckData`
  -     `ChangeOverProcess`
  -     `ST10_Flow11_A2TableScan`
  -     `ST10_Flow12_A2TableUnloading`
  -     `ST10_Flow14_B2Press`
  -     `ST10_Flow15_FRobot_3`
  -     `ST10_Flow1_A1TableScan`
  -     `ST10_Flow21_HShaftLifting`
  -     `ST10_Flow22_JMagnetLifting`
  -     `ST10_Flow23_KReserveLifting`
  -     `ST10_Flow24_LUnloadingTrans`
  -     `ST10_Flow25_HShaftLoad&Unload`
  -     `ST10_Flow26_JMagnetLoad&Unload`
  -     `ST10_Flow27_KReserveLoad&Unload`
  -     `ST10_Flow28_LUnloadingLoad&Unload`
  -     `ST10_Flow2_A1TableUnloading`
  -     `ST10_Flow3_A1RotaryShaftScan`
  -     `ST10_Flow4_B1Press`
  -     `ST10_Flow5_FRobot_1`
  -     `ST10_Flow6_ToolCodeScan`
  -     `ST10_Flow7_CGlueing`
  -     `ST10_Flow8_FRobot_2`
  -     `Count_CycleTime`
  -     `Count_CycleTime_V3`
  -     `CuringOven`
  -     `Gluing`
  -     `IAI`
  -     `IV3`
  -     `KistlerPresser_Main`
  -     `Motorr`
  -     `Pallet_NG`
  -     `Pilz`
  -     `Robot`
  -     `SR1000`
  -     `Servo`
  -     `Stopper`
  -     `FB_Tower_4Lamp`
  -       `MES Check_fb`
  -       `SysFlowCtrlGraph`
  -       `ST10_FB_S7connect`
  -       `Axis_FB`
  -       `IAI_Position`
  -       `Call_KeyenceCheckerIV`
  -       `KistlerPresser _FB`
  -       `MotorContro`
  -       `NG`
  -       `PilzData_fb`
  -       `KukaRobot1_Ctrl`
  -       `KukaRobot2_Ctrl`
  -       `KukaRobot3_Ctrl`
  -       `KeyenceSR1000Ctrl`
  -       `V90_Servo`
- Kořen `03_CYC_INT2`:
  - (žádná extrahovaná volání v dané hloubce)
- Kořen `04_CYC_INT5`:
  - (žádná extrahovaná volání v dané hloubce)

### Monitoring mapa (z HMI tagů)
- HMI tagy exportované: `2161` (tabulky: `65`)
- Unikátní HMI `ControllerTag`: `805`
- `ControllerTag` s duplicitní HMI vazbou: `26` (`deep_reader/out/hmi_controller_tag_duplicates.json`)
- Nejčastější PLC kořeny používané v HMI `ControllerTag`:
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

### Nepřímé adresování / okrajové případy
- Nalezené indikátory nepřímého/okrajového přístupu (hledání v textu):
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
  - `ST10_Auto`: `BLKMOV;Variant`
  - `ST10_ChangeOver`: `BLKMOV;Variant`
  - `ST10_FB_S7connect`: `P#_pointer;Variant`
  - `ST10_FB_S7connect_IDB`: `Variant`
  - `ST10_WarningDB`: `AT_view`
  - `V90Servo_DB`: `Variant`
  - `V90_Servo`: `Variant`
  - `fbV90Ctrl`: `Variant`
  - `块_1`: `AT_view`
- Nálezy absolutního adresování DB (hledání v textu): `4` různých DB, `4` výskytů (viz `deep_reader/out/absolute_db_refs.csv`).

### Hardware / IO (z AutomationML)
- Zdroj (AutomationML): `EXPORT/SZ23055_Garret_OP010_V0.0_25.08.30.aml`
- CPU: `OP10_100A2` / `CPU 1515-2 PN` / `OrderNumber:6ES7 515-2AN03-0AB0` / FW `V3.0`
- PN sítě (z AML): `E1`, `IE1`, `PN/IE_1`, `PN/IE_2`
- Moduly (vzorek): `390` celkem, vzorek v `deep_reader/out/hardware_aml_summary.json`

## PŘEDPOKLADY / OMEZENÍ
- Cross-reference export není k dispozici; proto jsou výstupy “nepoužité/mrtvé” pouze kandidáti k ověření (bez doporučení mazání).
- Explicitní bezpečnostní program (F-CPU/F-Blocks/F-OBs) nebyl nalezen v `EXPORT/Program blocks`; položky se “Safety/EStop/Door/Guard/…” jsou označeny jako NEŠAHAT konzervativně.
- Inferování read/write je orientační: `CallInfo Parameter Section`, LAD `Contact`=read a `Coil/SCoil/RCoil`=write; StructuredText používá jednoduchou heuristiku (přiřazení `:=`, výstupní vazba `=>`).

## DOPORUČENÍ (bezpečné další kroky)
- Pokud chcete zvýšit jistotu “nepoužité”: postupujte přes TIA vyhledávání symbolu v projektu a HMI (bez mazání), případně dočasné watch/trace (pozorování bez zásahu / bez zápisu).
- Pro konsolidaci monitoringu začněte vždy fází A (zrcadlení pouze pro monitoring do nového DB), bez přepojení HMI tagů v prvním kroku.
