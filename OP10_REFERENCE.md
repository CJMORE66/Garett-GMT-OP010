# OP10 Deep Reference

This document is meant to spare future engineers/AI agents from re-reading the entire
TIA export. It captures how the OP010 station is wired, how stations exchange data,
where errors/safety/manual controls sit, and where barcode/MES hooks live.

---

## 1. Control Architecture
- **Master station DB** – `Program blocks/OP010/00_Main/Station_Sys.db:1-120` defines
  `Status`, `Cmd`, `Auto`, `Manual`, `Safety`, `Signal`, `Flag.IndexTable`, and the edge
  detectors (`P`/`N`). All higher-level blocks (robots, scanners, presses) watch the
  `Station_Sys.*` bits for mode, run, reset, and safety gating.
- **OB1 orchestration** – `Program blocks/01_OB/01_OB1.xml:1345-1356` calls
  `AutoProcessDataPopUp` each scan so the HMI data manipulator stays synced with PLC data.
- **Main logic container** – `Program blocks/OP010/00_Main/ST10_Main.xml:362-3150`
  sequences Auto/Manual requests, links i/o modules to `Station_Sys`, and instantiates
  the Auto process Graphs under `Program blocks/OP010/03_Auto/*`.

## 2. Cycle Flow (see `flowchart.svg`)
- Generated from `flowchart.mmd`; covers every wait condition from pallet arrival →
  table clamp/scan → Robots/Presses/Glue → routing → Flow21–28 handling → unload.
- Keep this diagram with the export; it is the quickest troubleshooting aid.

## 3. Station-to-Station Data Map
`Program blocks/OP010/03_Auto/AutoProcessData.db:9-24` defines the 16 process slots:

| AutoProcessData field | Producer flow (Graph) | Consumer |
| --- | --- | --- |
| `A_ScanRotate` | Flow1/11 (table scan) | Robot #1 (`F_Robot1Grip1/2`) |
| `F_Robot1Grip1/2` | Flow5 robot steps | Press 1 / Glue buffers |
| `B_Press1` | Flow4 press Graph | Robot #2 + Glue |
| `C_Glue` | Flow7 glue Graph | Robot #2 |
| `F_Robot2Grip1/2` | Flow8 robot Graph | Press 2 / NG buffer |
| `C_GlueNGBuffer` | Glue NG logic | Robot #3 routing |
| `C_MagnScanNGBuffer` | Magnet scan NG | Robot #3 routing |
| `B_Press2` | Flow14 press Graph | Robot #3 |
| `F_Robot3Grip1/2` | Flow15 robot Graph | Shaft/Magnet/Reserve flows |
| `H/J/K/L_ShafeLine` | Flow21/22/23/24 & Flow25/26/27/28 | Final unload + pallet clear |

Supporting arrays include `A_Table_1/2` tooling codes and `GripperCode_R1..R3`
(`AutoProcessData.db:26-92`), plus `GlobalData.*CodeStatus` and `DataIndex`
(`AutoProcessData.db:30-84,93`). `AutoProcessData_Buffer` is used in robot graphs
(`ST10_Flow15_FRobot_3.xml:25164-27235`) to push ProcessData snapshots between stations.

`Program blocks/OP010/03_Auto/HMI/AutoProcessDataPopUp.scl:67-346` and
`AutoProcess_HMI.db:10-27` expose the same 16 slots on HMI, provide double-confirm edits,
and populate `StationHasProduct[1..16]` bits for visualization. Pro paralelní přechod lze
využít `Program blocks/OP010/03_Auto/FB_ProcessSlotManager.scl:1-78`, který cyklicky
zrcadlí hodnoty mezi `AutoProcessData` a novým `DB_ProcessSlots`.
- **Připravovaný model receptů/slotů** – `PLC data types/500 User/UDT_RecipeHeader.udt`,
  `UDT_SubProcessRecipe.udt` a `UDT_ProcessSlot.udt` společně s bloky
  `DB_RecipeMaster.db`, `DB_RecipeActiveNew.db`, `DB_ProcessSlots.db` a
  `DB_ProcessSlots_Global.db` sjednocují receptové, fixture a NG údaje.
  `FC_MigrateProcessData.scl` a `FC_ProcessSlot_Read/Write.scl` poskytují most mezi
  historickým `AutoProcessData` a novým uložením – díky tomu lze nové struktury
  naplnit už dnes a zítra pouze přepnout čtení v grafech.

## 4. Device Subsystems
- **Robots** – `Program blocks/OP010/10_Device/24_Robot/KukaRobot?_Ctrl.scl:1-210` use
  DPRD/DPWR to exchange `KukaRobot_*` UDTs with KRCs. `Robot.xml:59-200` shows how the FBs
  hook into `Station_Sys.Status.Run`, Auto/Manual bits, E-stop, task mode, and PGNO.
  Each GRAPH flow (`ST10_Flow5/8/15`) includes a `RobotManuallyMoved?` step
  (`Flow5`: lines 6783-9985; `Flow8`: 5689-12841; `Flow15`: 7248-14964) and writes
  `ManualMoved` flags consumed by the alarm DBs.
- **Presses** – `Program blocks/OP010/10_Device/23_Kistler/KistlerPresser _FB.scl:1-1135`
  drive individual maXYmos heads using hardware IDs (`iHW_ID_Input/Output`). Process data
  is stored in `ProcessData_1.db` etc. Both press Graphs share `KISTLER_HMI_DATA.udt`
  which also carries manual jog limits (`ServoManualMaxForce`).
- **Glue** – `Program blocks/OP010/10_Device/28_Gluing/Gluing.xml:407-2292` exposes manual
  jog/test nodes (`Manual_X/Y/Z`, `ManualTestStartGlue`), calibration flags, and reset
  interlocks for glue heads.
- **IAI/V90 axes** – `Program blocks/OP010/10_Device/22_IAI/*.scl/xml` and
  `10_Device/25_V90/V90_Servo.xml:1905-12013` define axis control (with numerous
  `Manual` components and `iManual` parameters).
- **Stopper/Conveyors** – `10_Device/06_Stopper/ST10_Stopper_FB.xml:510` shows stoppers
  checking both servo status and `Station_Sys.Manual.Mode`.
- **NG Handling** – `10_Device/29_NG/NG.xml:1738-4329` manages NG buffers with manual
  go-home/work commands (`ManualGoHome`, `ManualGoWork`).

## 5. Safety & Interlocks
- **Pilz PSS interface** – `Program blocks/OP010/10_Device/27_Pilz/PilzData.db:1-60` maps
  Pilz inputs (`E-Stop`, `SafetyGate`, `Light Curtain`) and outputs. Manual confirmation
  bits `ManualOKBox`, `HMIManualOKBox` live at lines 140-141.
- **Material/Safety Gates** – `10_Device/03_SafetyGate/ST10_SafetyGate.scl:1-304` calls
  individual gate DBs (`ST10_SafetyGate?_DB`) and the interface DB that drives lamp bits.
  TIMERS such as `iMaterialGate ManualLock Timer` (`MaterialGate.xml:31,981`) ensure gates
  stay locked before releasing Auto.
- **Station_Sys.Safety** – defined in `Station_Sys.db:70-120`; combine with
  `PilzData` to interlock `Station_Sys.Status.Run`.
- **Manual override detection** – Robot GRAPH steps emit `ManualMoved` bits which are tied
  to device alarms (`Program blocks/OP010/05_Alarm/ST10_DeviceError.db:1275-1311` and
  `ST10_Alarm.xml:6816-6950`). Alarms called “Robot Manual Moved” (line 6950) latch until
  reset.

## 6. Manual Operation Strategy
- `Station_Sys.db:75-105` contains both the `Manual` struct (device-level manual buttons)
  and `M."Device# Manual control"` overrides.
- `Program blocks/OP010/04_Manual/ST10_Manual.xml` centralizes manual routines; it is
  instantiated via `ST10_Main.xml:362-3150`.
- Changeover flows embed `ManualModeFlag` gating (`ChangeOverProcess.xml:2432-5223`,
  `ChangeOver_DB.db:185`) so recipes cannot be swapped in Auto.
- Device FBs (SR1000, IV3, Kistler, IAI, V90, gluing, NG) all expose `iManual` or
  `Manual` fields for maintenance and set HMI screen states based on
  `"Station_Sys".Manual.Mode` (e.g. `Call_KeyenceCheckerIV.scl:56-178`).

## 7. Error, Alarm, and NG Handling
- **Device & global alarms** – `Program blocks/OP010/05_Alarm/ST10_DeviceError.db` and
  `ST10_Alarm.xml` hold per-device errors, `ManualMoved` latches, and HMI text such as
  “Robot Manual Moved” (line 6950).
- **Warnings / tips** – `OP010/06_Warning/` and `07_Tip/` directories contain the warning
  DBs referenced from `Station_Sys.Warning`.
- **NG routes** – Glue (`C_GlueNGBuffer`), magnet scan NG, and press NGs are all separate
  AutoProcessData fields. Downstream flows check these bits before routing; `Robot #3`
  Graph (Flow15) contains fallback code (see commented buffer copy at
  `ST10_Flow15_FRobot_3.xml:25164-27235`).
- **Debug** – `Program blocks/OP010/05_Alarm/ST10_DeviceError.db` includes `ManualMoved`
  flags for each robot; `Program blocks/OP010/05_Alarm/ST10_GlobalError.db` covers station
  level faults.

## 8. Barcode / RFID / Vision / MES
- **RFID** – `PLC tags/常量/RFID.xml:1-30` defines RFID constants (init codes, station IDs)
  used by Flow1/11 table scans and MES load data.
- **Keyence SR1000 scanners** – `10_Device/18_SR1000 Scan/SR1000.xml:97-1320` controls
  eight SR1000 heads via `KeyenceSR1000Ctrl_xxxA1DB` instances; each call ties into
  `Station_Sys.Status.Run`, Reset, Auto/Manual, and uses `iManual` inputs.
- **Keyence IV3 vision** – `10_Device/21_IV3/FB_KeyenceCheckerIV3.scl:13-1083` manages the
  smart cameras. Rising/falling edge detectors (`rtrigManualMode`, `ftrigManualMode`)
  react to manual-mode transitions (`lines 989-992`), and `Call_KeyenceCheckerIV.scl`
  pushes screen activation according to `"Station_Sys".Manual.Mode`.
- **MES interface** – `Program blocks/OP010/11_MES/MES_CHeck.xml:12-32` instantiates MES
  check FBs for each station, while `MEStoPLC.db`, `PLCtoMES.db`, and
  `Station*_Load/UnloadData.db` handle results storage and handshake bits.
- **Kistler/Press traceability** – `PLC data types/LXL/Kistler/06_KISTLER/KISTLER_HMI_DATA.udt`
  and `WriteProcessData.udt` capture press curves for MES upload.

## 9. Safety / Manual / Error Quick Lookup
- `Station_Sys.Flag.IndexTable.*` (in `Station_Sys.db:90-118`) – gating for table
  interlocks (`Interlock`, `TableRunning`, `StopandPosition`, etc.).
- `PilzData.db:1-200` – raw Pilz input/output image.
- `ST10_SafetyGate_InterfaceDB.db` – per-gate lamp + HMI interface.
- `ST10_DeviceError.db:1275-1311` – `ManualMoved` flags for Robot1/2/3.
- `ST10_CountCycleTimeMain.xml:11-310` – counts auto/ manual cycles.

## 10. File Map for Future Work
- **Main access points**
  - `flowchart.svg` – operational flow reference.
  - `Program blocks/OP010/03_Auto/` – all GRAPH steps (Flow1..Flow28) plus `ChangeOver`.
  - `Program blocks/OP010/10_Device/` – per-device FBs (robots, presses, gluing, SR1000,
    IV3, Pilz, V90, IAI, NG).
  - `Program blocks/OP010/11_MES/` – MES handshake logic and DBs.
  - `Program blocks/OP010/04_Manual/` + `/05_Alarm/` + `/06_Warning/` + `/07_Tip/`.
  - `PLC data types/` – all UDT definitions (Kuka, MES, IAI, etc.).
  - `PLC tags/IO/*.xml` – raw IO image, `PLC tags/常量/*.xml` – constants (RFID, NG codes).
- **Generated artifacts**
  - `flowchart.mmd` + `flowchart.svg` – edit/regenerate as needed via `mmdc`.

With this map you should be able to jump directly to safety logic, manual handling, error
records, device FBs, or MES/tracking data without rescanning the entire project.
