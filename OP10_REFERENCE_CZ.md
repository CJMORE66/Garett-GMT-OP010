# OP10 Podrobná Referenční Příručka

Tento dokument má ušetřit budoucím inženýrům/AI agentům opakované čtení celého exportu
TIA. Popisuje strukturu stanice OP010, výměnu dat mezi stanicemi, umístění logiky chyb,
bezpečnostních funkcí, manuálního řízení i čteček čarových kódů/MES.

---

## 1. Řídicí architektura
- **Hlavní staniční DB** – `Program blocks/OP010/00_Main/Station_Sys.db:1-120` definuje
  `Status`, `Cmd`, `Auto`, `Manual`, `Safety`, `Signal`, `Flag.IndexTable` a hraniční
  detektory (`P`/`N`). Všechny nadřazené bloky (roboti, skenery, lisy) sledují bity
  `Station_Sys.*` pro módy, běh, reset a bezpečnostní stavy.
- **Orchestrace OB1** – `Program blocks/01_OB/01_OB1.xml:1345-1356` v každém cyklu volá
  `AutoProcessDataPopUp`, takže HMI editor dat zůstává synchronní s PLC DB.
- **Kontejner hlavní logiky** – `Program blocks/OP010/00_Main/ST10_Main.xml:362-3150` řídí
  požadavky Auto/Manual, mapuje I/O do `Station_Sys` a instancuje grafy v
  `Program blocks/OP010/03_Auto/*`.

## 2. Pracovní tok (viz `flowchart.svg`)
- Vznikl z `flowchart.mmd`; obsahuje všechny čekací podmínky od příjezdu palety přes
  upnutí/skener → roboty/lisy/lepení → směrování → fáze Flow21–28 → vykládku.
- Diagram přikládejte k exportu, je to nejrychlejší pomůcka při diagnostice.

## 3. Mapa výměny dat mezi stanicemi
`Program blocks/OP010/03_Auto/AutoProcessData.db:9-24` definuje 16 procesních slotů:

| pole AutoProcessData | Producent (Graph) | Konzument |
| --- | --- | --- |
| `A_ScanRotate` | Flow1/11 (skener stolu) | Robot #1 (`F_Robot1Grip1/2`) |
| `F_Robot1Grip1/2` | Robot Flow5 | Lis 1 / lepení |
| `B_Press1` | Flow4 (lis 1) | Robot #2 + lepení |
| `C_Glue` | Flow7 | Robot #2 |
| `F_Robot2Grip1/2` | Flow8 | Lis 2 / NG buffer |
| `C_GlueNGBuffer` | NG logika lepení | Směrování Robot #3 |
| `C_MagnScanNGBuffer` | NG magnetického skenu | Směrování Robot #3 |
| `B_Press2` | Flow14 | Robot #3 |
| `F_Robot3Grip1/2` | Flow15 | Flow21–27 (shaft/magnet/reserve) |
| `H/J/K/L_ShafeLine` | Flow21/22/23/24 & Flow25..28 | Finální vykládka + čištění palety |

Pole `A_Table_1/2` (kód přípravku) a `GripperCode_R1..R3`
(`AutoProcessData.db:26-92`), stejně jako `GlobalData.*CodeStatus` a `DataIndex`
(`AutoProcessData.db:30-84,93`), zajišťují sledování nástrojů. `AutoProcessData_Buffer`
se používá v grafech robotů (`ST10_Flow15_FRobot_3.xml:25164-27235`) pro kopírování dat
mezi stanicemi.

`Program blocks/OP010/03_Auto/HMI/AutoProcessDataPopUp.scl:67-346` a
`AutoProcess_HMI.db:10-27` zobrazují těchto 16 slotů na HMI, vyžadují dvojité potvrzení
editace/smazání a naplňují bity `StationHasProduct[1..16]`. Nový blok
`FB_ProcessSlotManager.scl:1-78` (Auto → DB a DB → Auto) drží data obou světů
identická během migrace.
- **Nový model receptů a slotů** – UDT `UDT_RecipeHeader`, `UDT_SubProcessRecipe`,
  `UDT_ProcessSlot` plus DB `DB_RecipeMaster.db`, `DB_RecipeActiveNew.db`,
  `DB_ProcessSlots.db` a `DB_ProcessSlots_Global.db` konsolidují recepty, fixture kódy a
  výsledky. `FC_MigrateProcessData`, `FC_ProcessSlot_Read` a
  `FC_ProcessSlot_Write` fungují jako most mezi starým `AutoProcessData` a novými
  strukturami.

## 4. Pod-systémy zařízení
- **Roboti** – `Program blocks/OP010/10_Device/24_Robot/KukaRobot?_Ctrl.scl:1-210` používají
  DPRD/DPWR pro výměnu struktury `KukaRobot_*` s KRC. `Robot.xml:59-200` ukazuje, jak jsou
  FB napojeny na `Station_Sys.Status.Run`, Auto/Manual, E-stop, task mode a PGNO. Každý
  GRAPH (Flow5/8/15) obsahuje krok `RobotManuallyMoved?`
  (`Flow5`: 6783-9985; `Flow8`: 5689-12841; `Flow15`: 7248-14964) a zapisuje `ManualMoved`
  do alarmových DB.
- **Lisy** – `Program blocks/OP010/10_Device/23_Kistler/KistlerPresser _FB.scl:1-1135`
  ovládá maXYmos hlavy přes HW ID. Procesní data leží v `ProcessData_1.db` atd.
  `KISTLER_HMI_DATA.udt` zahrnuje i manuální limity.
- **Lepení** – `Program blocks/OP010/10_Device/28_Gluing/Gluing.xml:407-2292` nabízí
  manuální osy (`Manual_X/Y/Z`), testovací spouště a kalibrace.
- **IAI/V90** – `10_Device/22_IAI/*` a `10_Device/25_V90/V90_Servo.xml:1905-12013`
  pokrývají serva; každé má `Manual` vstupy.
- **Stoppery / dopravníky** – `10_Device/06_Stopper/ST10_Stopper_FB.xml:510` sdílí
  mezilock s `Station_Sys.Manual.Mode`.
- **NG buffer** – `10_Device/29_NG/NG.xml:1738-4329` řídí NG zásobníky včetně manuálních
  příkazů `ManualGoHome/ManualGoWork`.

## 5. Bezpečnost a mezizámky
- **Pilz rozhraní** – `Program blocks/OP010/10_Device/27_Pilz/PilzData.db:1-60` mapuje
  vstupy (E-stop, bezpečnostní vrata, světelné závory) a výstupy. Manuální potvrzení
  `ManualOKBox`/`HMIManualOKBox` jsou na řádcích 140-141.
- **Bezpečnostní vrata** – `10_Device/03_SafetyGate/ST10_SafetyGate.scl:1-304` volá
  gate DB a interface DB s lampami. Časovač `iMaterialGate ManualLock Timer`
  (`MaterialGate.xml:31,981`) hlídá zamčení v manuálu.
- **`Station_Sys.Safety`** – definován ve `Station_Sys.db:70-120`, kombinuje se s Pilz
  daty pro interlock `Station_Sys.Status.Run`.
- **Detekce manuálního pohybu** – kroky robotů vytváří `ManualMoved` bity a alarmy
  (`ST10_DeviceError.db:1275-1311`, `ST10_Alarm.xml:6816-6950`, text „Robot Manual Moved“
  na řádku 6950).

## 6. Strategie manuálního režimu
- `Station_Sys.db:75-105` obsahuje `Manual` strukturu i `M."Device# Manual control"`.
- `Program blocks/OP010/04_Manual/ST10_Manual.xml` sdružuje manuální sekvence, volané z
  `ST10_Main`.
- `ChangeOver` používá `ManualModeFlag` (`ChangeOverProcess.xml:2432-5223`,
  `ChangeOver_DB.db:185`), takže nelze měnit recept v AUTO.
- Všechny zařízení (SR1000, IV3, Kistler, IAI, V90, lepení, NG) mají vstupy `iManual` a
  přepínají HMI obrazovky podle `"Station_Sys".Manual.Mode`
  (`Call_KeyenceCheckerIV.scl:56-178`).

## 7. Chyby, alarmy a NG
- **Alarmy zařízení/globální** – `OP010/05_Alarm/ST10_DeviceError.db` +
  `ST10_Alarm.xml` drží chyby, latche `ManualMoved` a HMI texty (ř. 6950).
- **Varování / tipy** – `OP010/06_Warning/`, `OP010/07_Tip/` napojené na
  `Station_Sys.Warning`.
- **NG trasy** – lepení (`C_GlueNGBuffer`), magnetické NG a lis NG jsou oddělená pole.
  Flow15 kontroluje tyto bity před směrováním; viz komentované kopie dat v
  `ST10_Flow15_FRobot_3.xml:25164-27235`.
- **Debug** – `ST10_DeviceError.db` má `ManualMoved` pro každý robot, `ST10_GlobalError.db`
  shrnuje staniční chyby.

## 8. Čtečky kódů / RFID / kamera / MES
- **RFID** – `PLC tags/常量/RFID.xml:1-30` obsahuje konstanty (stanice, init kódy) pro
  Flow1/11 a MES load data.
- **Keyence SR1000** – `10_Device/18_SR1000 Scan/SR1000.xml:97-1319` řídí osm hlav přes
  instance `KeyenceSR1000Ctrl_xxxA1DB` a sleduje `Station_Sys` módy i `iManual`.
- **Keyence IV3** – `10_Device/21_IV3/FB_KeyenceCheckerIV3.scl:13-1083` využívá
  hraniční detektory `rtrigManualMode/ftrigManualMode` (ř. 989-992) a volání v
  `Call_KeyenceCheckerIV.scl` podle `Station_Sys.Manual.Mode`.
- **MES** – `Program blocks/OP010/11_MES/MES_CHeck.xml:12-32` instancuje MES FB pro
  stanice; DB `MEStoPLC.db`, `PLCtoMES.db`, `Station*_Load/UnloadData.db` řeší handshake.
- **Kistler traceability** – `PLC data types/LXL/Kistler/06_KISTLER/KISTLER_HMI_DATA.udt`
  + `WriteProcessData.udt` ukládají lisovací křivky pro MES.

## 9. Rychlý přehled bezpečnosti/manuálu/chyb
- `Station_Sys.Flag.IndexTable.*` (`Station_Sys.db:90-118`) – interlock pro indexovací
  stůl.
- `PilzData.db:1-200` – obraz vstupů/výstupů Pilz.
- `ST10_SafetyGate_InterfaceDB.db` – stav lamp a HMI pro vrata.
- `ST10_DeviceError.db:1275-1311` – `ManualMoved` pro Robot1/2/3.
- `ST10_CountCycleTimeMain.xml:11-310` – počítá cykly Auto/Manual.

## 10. Přehled souborů
- **Hlavní vstupy**
  - `flowchart.svg` – operační tok.
  - `Program blocks/OP010/03_Auto/` – všechny grafy (Flow1..Flow28, ChangeOver).
  - `Program blocks/OP010/10_Device/` – FB pro zařízení (roboti, lisy, lepení, SR1000,
    IV3, Pilz, V90, IAI, NG).
  - `Program blocks/OP010/11_MES/` – MES logika a DB.
  - `Program blocks/OP010/04_Manual/`, `/05_Alarm/`, `/06_Warning/`, `/07_Tip/`.
  - `PLC data types/` – UDT (Kuka, MES, IAI…).
  - `PLC tags/IO/*.xml` – obraz IO, `PLC tags/常量/*.xml` – konstanty (RFID, NG kódy).
- **Generované podklady**
  - `flowchart.mmd` + `flowchart.svg` – upravitelné přes `mmdc`.

Díky této příručce lze rychle skočit přímo k bezpečnostním funkcím, manuálním sekvencím,
záznamům chyb, FB zařízení nebo MES/traceability bez procházení celého projektu.
