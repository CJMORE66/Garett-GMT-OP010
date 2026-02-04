# OP10 PLC Project Structure Overview

> **Generated:** 2026-02-01  
> **Project:** OP10 Station PLC Code  
> **Purpose:** Siemens TIA Portal PLC Project for Manufacturing Station

---

## 📁 ROOT DIRECTORY STRUCTURE

```
📂 OP10/
├── 📁 DB_ALL_PROCESS_PARAMETERS.db          # Process parameters database
├── 📁 GlueningRotaryTable.db                # Gluing rotary table database
├── 📁 DOKUMENTACE/                          # Documentation folder
├── 📁 PLC data types/                       # UDTs (User Data Types)
├── 📁 PLC tags/                             # PLC tag tables
└── 📁 Program blocks/                       # Main program logic (FC, FB, DB, OB)
```

---

## 📊 PLC DATA TYPES (`PLC data types/`)

User-Defined Types (UDTs) organized by category:

### System Types (`00 Sys/`)
| File | Purpose |
|------|---------|
| `RCS_CountCycleTime_V1.xml` | Cycle time counting structure |
| `RCS_PMInterface_V1.xml` | PM Interface structure |
| `RCS_SysAlarmWarning_V1.xml` | System alarm/warning structure |
| `RCS_SysAuto_V1.xml` | Auto mode structure |
| `RCS_SysCmd_V1.xml` | System commands structure |
| `RCS_SysComInterface_V1.xml` | Communication interface |
| `RCS_SysCount_V1.xml` | System counter structure |
| `RCS_SysCycleTime_V1.xml` | System cycle time |
| `RCS_SysManual_V1.xml` | Manual mode structure |
| `RCS_SysSafety_V1.xml` | Safety system structure |
| `RCS_SysStatus_V1.xml` | System status structure |

### Function Block Types (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `101 Cylinder/` | Cylinder control UDT (`Cyl.xml`) |
| `102 SafetyGate/` | Safety gate UDT (`SafetyGateUDT.xml`) |
| `105 MaterialGate/` | Material gate UDT |
| `201 Stopper/` | Stopper UDT (`ST_Stopper.xml`, `UDT_Stopper_FB.xml`) |
| `202 Conveyer_Line/` | Motor control UDT (`Motor_Control.xml`) |
| `211 ATEQ LeakTest/` | ATEQ leak test visual type |
| `212 Analog/` | General analog UDT (`ST_GeneralAnalog.xml`) |

### User Types (`500 User/`)
| File | Purpose |
|------|---------|
| `ATEQRecipe.xml` | ATEQ recipe structure |
| `Check.xml` | Check data structure |
| `PresserRecipe.xml` | Presser recipe structure |
| `StaProcessData.xml` | Station process data |
| `UDT_LabelFeeder.xml` | Label feeder UDT |
| `UDT_Marking CharToASCII.xml` | Marking char conversion |
| `UDT_Marking StringToChar.xml` | Marking string conversion |
| `UDT_StaProcessData.xml` | Station process data UDT |
| `100 FixtureCheck/` | Fixture check UDT |
| `104 PartDataManage/` | Part data management UDTs |
| `210 Recipe/` | Recipe axis UDT |

### External Device Types
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner (HMI, Input, Output types) |
| `LXL/` | IAI Servo, Kistler, Kuka Robot types |
| `MES/` | MES monitoring types |
| `ProcessData/` | Process data types |
| `RCS-PPK/` | Stopper interface types |

### Recipe Parameters (`_PARAMETERS_RECIPES/`)
| File | Purpose |
|------|---------|
| `UDT_Gripper_Fixture_Codes.xml` | Gripper/fixture codes |
| `UDT_IAI_Axis_Positions.xml` | IAI axis positions |
| `UDT_Motion_Point_IAI.xml` | IAI motion points |
| `UDT_Motion_Point_V90.xml` | V90 motion points |
| `UDT_OP10_Recipe_type.xml` | OP10 recipe type |
| `UDT_RECIPE.xml` | Main recipe structure |
| `UDT_Recipe_ATEQ.xml` | ATEQ recipe |
| `UDT_Recipe_PressCurve.xml` | Press curve recipe |
| `UDT_V90_Axis_Positions.xml` | V90 axis positions |

### Enums
| File | Purpose |
|------|---------|
| `NGDoorState_Enum.xml` | NG Door state enumeration |
| `PartStatus_Enum.xml` | Part status enumeration |
| `UDT_OP10_Recipe_diff.xml` | Recipe difference structure |

---

## 🏷️ PLC TAGS (`PLC tags/`)

### Tag Tables
| File/Folder | Content |
|-------------|---------|
| `Default variable table.xml` | Default PLC tags |
| `NGSensor.xml` | NG sensor tags |
| `STEP7 classic symbols.xml` | STEP7 classic symbols |
| `constant/` | Constants (Flow, IV3, Lifting, Marking, MES codes, PartType, ProcessResult, RFID, TestResult, partstatus) |
| `IO/` | I/O tags (PLC DI/DQ, Remote IO DI/DO) |

---

## 🔧 PROGRAM BLOCKS (`Program blocks/`)

### Organization Blocks (`01_OB/`)
| File | Purpose |
|------|---------|
| `01_OB1.xml` | Main cyclic OB |
| `02_Warm Restart.xml` | Warm restart OB |
| `03_CYC_INT2.xml` | Cyclic interrupt 2 |
| `04_CYC_INT5.xml` | Cyclic interrupt 5 |
| `05_MOD_ERR.xml` | Module error OB |
| `07_CYCL_FLT.xml` | Cycle fault OB |
| `08_HW_INT0.xml` | Hardware interrupt 0 |
| `09_IO_FLT1.xml` | I/O fault OB |
| `11_PROG_ERR.xml` | Program error OB |
| `12_RACK_FLT.xml` | Rack fault OB |

### System Functions (`00 Sys/`)
| File | Purpose |
|------|---------|
| `CheckData.xml` | Data checking |
| `Count_CycleTime.xml` | Cycle time counting |
| `Count_CycleTime_V3.xml` | Cycle time counting v3 |
| `SysFlowCtrlGraph.xml` | Flow control graph |
| `SystemMode.xml` | System mode management |

### Communication (`02_Comm/`)
| Folder | Content |
|--------|---------|
| `03-Diagnosis/` | Diagnostic FBs |
| `04-ChangeOver/` | Changeover logic |
| `06_SysDataBlock&Function/` | System data/functions |

### Reusable Function Blocks (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `003 Tower_Lamp/` | Tower lamp control (`FB_Tower_4Lamp.xml`) |
| `101 Cylinder/` | Cylinder control (`CylinderCtrl_V2.xml`, `CylinderModule_V2.xml`) |
| `102 SafetyGate/` | Safety gate (`SafetyGate.xml`) |
| `201 Stopper/` | Stopper control (`FB_Stopper.xml`) |
| `202 Conveyer_Line/` | Motor control (`MotorContro.xml`) |
| `999 Base/` | Base functions (`FB_Next.xml`) |

### Device-Specific (`03_Device/`)
| Folder | Content |
|--------|---------|
| `102 SafetyGate/` | Material gate |
| `211 ATEQ LeakTest/` | ATEQ F620 leak test |
| `212 Analog/` | Analog processing |

### User Functions (`500 User/`)
| Folder | Content |
|--------|---------|
| `100 FixtureCheck/` | Fixture checking |
| `104 PartDataManage/` | Part data management |

### External Device Libraries
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner control |
| `RCS-PPK/` | Stopper control library |

### Special Folders
| Folder | Purpose |
|--------|---------|
| `__MES MONITORING/` | MES monitoring FBs |
| `__PARAMETERS/` | Recipe/parameter handling |
| `Z_Reserve/` | Reserved/commissioning blocks |

---

## 🏭 STATION OP010 (`Program blocks/OP010/`)

Main station logic organized by function:

### Main (`00_Main/`)
| File | Purpose |
|------|---------|
| `ST10_Main.xml` | Main station FB |
| `ST10_GeneralData.xml` | General data DB |
| `Station_Sys.xml` | Station system FB |
| `iDB/ST10_SystemModeFB_iDB.xml` | System mode instance DB |

### Input Processing (`01_Input/`)
| File | Purpose |
|------|---------|
| `ST10_Input.xml` | Input processing |
| `ST10_SysInput.xml` | System input processing |

### Output Processing (`02_Output/`)
| File | Purpose |
|------|---------|
| `ST10_Output.xml` | Output processing |
| `ST10_SysOutput.xml` | System output processing |
| `ST10_FB_Tower_4Lamp_DB.xml` | Tower lamp instance DB |

### Automatic Mode (`03_Auto/`)
| Folder/File | Purpose |
|-------------|---------|
| `AutoProcessControl.xml` | Auto process control |
| `AutoProcessData.xml` | Auto process data |
| `AutoProcessData_Buffer.xml` | Process data buffer |
| `PalletRelease.xml` | Pallet release logic |
| `ST10_PM.xml` | PM interface |
| `TON.xml` | Timer functions |
| `01ChangeOver/` | Changeover flows |
| `A1_TableLoad&Scan/` | Table A1 loading & scanning |
| `A2_TableLoad&Scan/` | Table A2 loading & scanning |
| `B_Press/` | Press operations (B1, B2) |
| `C_Glue/` | Gluing operation |
| `F_Robot/` | Robot operations (1, 2, 3) |
| `H_ShaftLifting&Load&Unload/` | Shaft lifting operations |
| `J_MagnetLifting&Load&Unload/` | Magnet lifting operations |
| `L_Unload/` | Unloading operations |
| `M_iDB/` | Instance DBs for all flows |
| `HMI/` | HMI interface blocks |

**Flow Sequence:**
1. `ST10_Flow1_A1TableScan` - A1 Table Scan
2. `ST10_Flow2_A1TableUnloading` - A1 Table Unload
3. `ST10_Flow3_A1RotaryShaftScan` - Rotary Shaft Scan
4. `ST10_Flow4_B1Press` - B1 Press
5. `ST10_Flow5_FRobot_1` - Robot 1 Operation
6. `ST10_Flow6_ToolCodeScan` - Tool Code Scan
7. `ST10_Flow7_CGlueing` - Gluing
8. `ST10_Flow8_FRobot_2` - Robot 2 Operation
11. `ST10_Flow11_A2TableScan` - A2 Table Scan
12. `ST10_Flow12_A2TableUnloading` - A2 Table Unload
14. `ST10_Flow14_B2Press` - B2 Press
15. `ST10_Flow15_FRobot_3` - Robot 3 Operation
21. `ST10_Flow21_HShaftLifting` - H Shaft Lifting
22. `ST10_Flow22_JMagnetLifting` - J Magnet Lifting
23. `ST10_Flow23_KReserveLifting` - K Reserve Lifting
24. `ST10_Flow24_LUnloadingTrans` - L Unloading Transfer
25. `ST10_Flow25_HShaftLoad&Unload` - H Shaft Load/Unload
26. `ST10_Flow26_JMagnetLoad&Unload` - J Magnet Load/Unload
27. `ST10_Flow27_KReserveLoad&Unload` - K Reserve Load/Unload
28. `ST10_Flow28_LUnloadingLoad&Unload` - L Unloading Load/Unload

### Manual Mode (`04_Manual/`)
| File | Purpose |
|------|---------|
| `ST10_Manual.xml` | Manual operation logic |

### Alarm Handling (`05_Alarm/`)
| File | Purpose |
|------|---------|
| `ST10_Alarm.xml` | Alarm management |
| `ST10_DeviceError.xml` | Device error handling |
| `ST10_GlobalError.xml` | Global error handling |

### Warning Handling (`06_Warning/`)
| File | Purpose |
|------|---------|
| `ST10_Warning.xml` | Warning management |
| `ST10_WarningDB.xml` | Warning data block |

### Tips (`07_Tip/`)
| File | Purpose |
|------|---------|
| `ST10_Tip.xml` | Tip management |
| `ST10_TipDB.xml` | Tip data block |

### Changeover (`08_ChangeOver/`)
| File | Purpose |
|------|---------|
| `ST10_ChangeOver.xml` | Changeover logic |
| `Parameter.xml` | Parameters |
| `ST10_RecipeDB.xml` | Recipe database |
| `ST10_RecipeDB_HMI.xml` | HMI recipe interface |
| `ST10_RecipeActiveDB.xml` | Active recipe DB |
| `MES/OP010_MES_RecipeDB.xml` | MES recipe DB |

### Cycle Time (`09_Count_CycleTime/`)
| File | Purpose |
|------|---------|
| `ST10_CountCycleTimeMain.xml` | Main cycle time counter |
| `ST10_CountCycleTimeMain_DB.xml` | Cycle time data block |
| `ST10_PMCountCycleTime.xml` | PM cycle time |

### Device Control (`10_Device/`)
| Folder | Device/Function |
|--------|-----------------|
| `01_Cylinder/` | Cylinders 1-100 (ST10Cylinder.xml + interfaces) |
| `03_SafetyGate/` | Safety gates 1-9 + Material gates 1-7 |
| `06_Stopper/` | Stopper control |
| `08_PressureAanlog/` | Pressure analog processing |
| `09_CuringOven/` | Curing oven control |
| `18_SR1000 Scan/` | Keyence SR1000 scanners (8 instances) |
| `21_IV3/` | Keyence IV3 vision sensors |
| `22_IAI/` | IAI servo axes (A1, A2, A3) |
| `23_Kistler/` | Kistler press systems (1 & 2) |
| `24_Robot/` | Kuka robots (1, 2, 3) |
| `25_V90/` | **V90 servo drives + TO_BasicPos technology** |
| `26_Stopper/` | Additional stopper control |
| `27_Pilz/` | Pilz safety system |
| `28_Gluing/` | Gluing system control |
| `29_NG/` | NG (Not Good) box control |
| `31_Motor_1/` | Motor controls 1-17 |

#### V90 Servo Technology Objects (`25_V90/`)
The V90 folder contains **2 different servo control technologies**:

**1. Standard V90 Position Control (fbV90Ctrl)**
| File | Purpose |
|------|---------|
| `V90_Servo.xml` | Main FB calling 4 servo instances (Servo_380A1..383A1) |
| `Servo.xml` | FC wrapper calling V90_Servo FB |
| `ServoV90_A1.xml` - `ServoV90_A4.xml` | Global DBs for servo data (In/Out structs) |
| `V90Servo_DB.xml` | Instance DB for V90_Servo FB |
| `V90_Standard/fbV90Ctrl.xml` | **Standard V90 control FB** - handles jog, auto, homing, position lists |
| `V90_Standard/SINA_POS.xml` | Siemens SINA_POS block for V90 |
| `V90_Standard/SINA_PARA_S.xml` | Siemens parameter access block |
| `V90_Standard/ServoCheck/` | Servo startup & position check |

**2. TO_BasicPos Technology Object (Motion Control) - NOT USED**
| File | Purpose |
|------|---------|
| `Z_NOT_USED/FB_GlueRotation_BasicPos.scl` | **TO_BasicPos-based FB** using `BasicPosControl` technology object for rotary table gluing - **NOT USED** |
| `FB_GlueRotationJob.scl` | Job controller for glue rotation using standard V90 interface |
| `Z_NOT_USED/FB_RotaryJobController.scl` | **TO-based rotary control** using `MC_Power` + `MC_MoveRelative` motion control blocks - **NOT USED** |
| `ServoV90_DeviceCtl.xml` | Device control logic |
| `Patch/` | Positioning order check patches |

**Key Difference:**
- `fbV90Ctrl` = Standard V90 telegram 111 positioning (ACTIVE/USED)
- `FB_GlueRotation_BasicPos` = Technology Object Basic Positioning (NOT USED - moved to Z_NOT_USED)
- `FB_RotaryJobController` = Full TO-based motion control (NOT USED - moved to Z_NOT_USED)

### MES Integration (`11_MES/`)
| File | Purpose |
|------|---------|
| `MES.xml` | Main MES FB |
| `MES_CheckControl.xml` | MES check control |
| `MES_CHeck.xml` / `MES Check_fb.xml` | MES check functions |
| `MES_CHeck_DB.xml` | MES check DB |
| `MEStoPLC.xml` | MES to PLC data |
| `PLCtoMES.xml` | PLC to MES data |
| `DT-Chars.xml` / `DT-Chars_DB.xml` | Data type char conversion |
| `Station1LoadData.xml` - `Station8UnLoadData.xml` | Station load/unload data |
| `Scanner1LoadData.xml` | Scanner load data |

### Part Data (`12_PartData/`)
| File | Purpose |
|------|---------|
| `ST10_PartData.xml` | Part data management |
| `PartData_Interface_DB.xml` | Part data interface |
| `PartDataManage_Part1_DB.xml` - `PartDataManage_Part4_DB.xml` | Part data for parts 1-4 |

---

## 📋 STANDARDS & GUIDELINES

### Naming Conventions
| Prefix | Meaning | Example |
|--------|---------|---------|
| `ST10_` | Station 10 blocks | `ST10_Main.xml` |
| `ST10_FlowX_` | Process flow step X | `ST10_Flow1_A1TableScan.xml` |
| `FB_` | Function Block | `FB_Stopper.xml` |
| `FC_` | Function Call | `FC_Save_Values_Final.xml` |
| `DB_` | Data Block | `DB_MES_Monitoring.xml` |
| `UDT_` | User Data Type | `UDT_RECIPE.xml` |
| `iDB/` | Instance Data Blocks folder | - |

### File Extensions
| Extension | Type |
|-----------|------|
| `.xml` | TIA Portal exported block (standard) |
| `.scl` | Structured Control Language (Siemens) |
| `.db` | Database file |

### Folder Numbering Convention
| Range | Category |
|-------|----------|
| `00-09` | System/Organization |
| `01-09` | Organization Blocks |
| `10-99` | Function Blocks |
| `100-199` | User Functions |
| `200-299` | Devices |
| `500+` | Custom/User |

---

## 🔍 WHERE TO ADD NEW COMPONENTS

### New Device Type (UDT)
📂 `PLC data types/03 FunctionBlocks/`  
Create folder: `[NNN] [DeviceName]/`  
Add UDT in: `[NNN].1 UDT/[Name].xml`

### New Device Instance
📂 `Program blocks/OP010/10_Device/`  
Create folder: `[NN]_[DeviceName]/`  
Add control FB and instance DBs

### New Process Flow Step
📂 `Program blocks/OP010/03_Auto/`  
Add to appropriate subfolder (A1, A2, B_Press, etc.)  
Create: `ST10_Flow[X]_[Description].xml`  
Create iDB: `M_iDB/ST10_Flow[X]_[Description]_iDB.xml`

### New Recipe Parameter
📂 `PLC data types/_PARAMETERS_RECIPES/`  
Add UDT definition  
Update: `UDT_RECIPE.xml`

### New MES Data Exchange
📂 `Program blocks/OP010/11_MES/`  
Create: `Station[X]LoadData.xml` / `Station[X]UnLoadData.xml`

### New Constant/Enum
📂 `PLC tags/constant/`  
Create or modify appropriate XML file

---

## ⚠️ NOTES

- **OLD SHIT folders** contain deprecated/legacy code - do not use for new development
- **Z_Reserve folder** is for temporary/commissioning blocks
- **iDB folders** contain instance data blocks (automatically generated instances of FBs)
- Flow numbers are NOT sequential (gaps exist: 9, 10, 13, 16-20, etc.)
- Multiple file formats exist: `.xml` (TIA exports), `.scl` (source code)

> **Generated:** 2026-02-01  
> **Project:** OP10 Station PLC Code  
> **Purpose:** Siemens TIA Portal PLC Project for Manufacturing Station

---

## 📁 ROOT DIRECTORY STRUCTURE

```
📂 OP10/
├── 📁 DB_ALL_PROCESS_PARAMETERS.db          # Process parameters database
├── 📁 GlueningRotaryTable.db                # Gluing rotary table database
├── 📁 DOKUMENTACE/                          # Documentation folder
├── 📁 PLC data types/                       # UDTs (User Data Types)
├── 📁 PLC tags/                             # PLC tag tables
└── 📁 Program blocks/                       # Main program logic (FC, FB, DB, OB)
```

---

## 📊 PLC DATA TYPES (`PLC data types/`)

User-Defined Types (UDTs) organized by category:

### System Types (`00 Sys/`)
| File | Purpose |
|------|---------|
| `RCS_CountCycleTime_V1.xml` | Cycle time counting structure |
| `RCS_PMInterface_V1.xml` | PM Interface structure |
| `RCS_SysAlarmWarning_V1.xml` | System alarm/warning structure |
| `RCS_SysAuto_V1.xml` | Auto mode structure |
| `RCS_SysCmd_V1.xml` | System commands structure |
| `RCS_SysComInterface_V1.xml` | Communication interface |
| `RCS_SysCount_V1.xml` | System counter structure |
| `RCS_SysCycleTime_V1.xml` | System cycle time |
| `RCS_SysManual_V1.xml` | Manual mode structure |
| `RCS_SysSafety_V1.xml` | Safety system structure |
| `RCS_SysStatus_V1.xml` | System status structure |

### Function Block Types (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `101 Cylinder/` | Cylinder control UDT (`Cyl.xml`) |
| `102 SafetyGate/` | Safety gate UDT (`SafetyGateUDT.xml`) |
| `105 MaterialGate/` | Material gate UDT |
| `201 Stopper/` | Stopper UDT (`ST_Stopper.xml`, `UDT_Stopper_FB.xml`) |
| `202 Conveyer_Line/` | Motor control UDT (`Motor_Control.xml`) |
| `211 ATEQ LeakTest/` | ATEQ leak test visual type |
| `212 Analog/` | General analog UDT (`ST_GeneralAnalog.xml`) |

### User Types (`500 User/`)
| File | Purpose |
|------|---------|
| `ATEQRecipe.xml` | ATEQ recipe structure |
| `Check.xml` | Check data structure |
| `PresserRecipe.xml` | Presser recipe structure |
| `StaProcessData.xml` | Station process data |
| `UDT_LabelFeeder.xml` | Label feeder UDT |
| `UDT_Marking CharToASCII.xml` | Marking char conversion |
| `UDT_Marking StringToChar.xml` | Marking string conversion |
| `UDT_StaProcessData.xml` | Station process data UDT |
| `100 FixtureCheck/` | Fixture check UDT |
| `104 PartDataManage/` | Part data management UDTs |
| `210 Recipe/` | Recipe axis UDT |

### External Device Types
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner (HMI, Input, Output types) |
| `LXL/` | IAI Servo, Kistler, Kuka Robot types |
| `MES/` | MES monitoring types |
| `ProcessData/` | Process data types |
| `RCS-PPK/` | Stopper interface types |

### Recipe Parameters (`_PARAMETERS_RECIPES/`)
| File | Purpose |
|------|---------|
| `UDT_Gripper_Fixture_Codes.xml` | Gripper/fixture codes |
| `UDT_IAI_Axis_Positions.xml` | IAI axis positions |
| `UDT_Motion_Point_IAI.xml` | IAI motion points |
| `UDT_Motion_Point_V90.xml` | V90 motion points |
| `UDT_OP10_Recipe_type.xml` | OP10 recipe type |
| `UDT_RECIPE.xml` | Main recipe structure |
| `UDT_Recipe_ATEQ.xml` | ATEQ recipe |
| `UDT_Recipe_PressCurve.xml` | Press curve recipe |
| `UDT_V90_Axis_Positions.xml` | V90 axis positions |

### Enums
| File | Purpose |
|------|---------|
| `NGDoorState_Enum.xml` | NG Door state enumeration |
| `PartStatus_Enum.xml` | Part status enumeration |
| `UDT_OP10_Recipe_diff.xml` | Recipe difference structure |

---

## 🏷️ PLC TAGS (`PLC tags/`)

### Tag Tables
| File/Folder | Content |
|-------------|---------|
| `Default variable table.xml` | Default PLC tags |
| `NGSensor.xml` | NG sensor tags |
| `STEP7 classic symbols.xml` | STEP7 classic symbols |
| `constant/` | Constants (Flow, IV3, Lifting, Marking, MES codes, PartType, ProcessResult, RFID, TestResult, partstatus) |
| `IO/` | I/O tags (PLC DI/DQ, Remote IO DI/DO) |

---

## 🔧 PROGRAM BLOCKS (`Program blocks/`)

### Organization Blocks (`01_OB/`)
| File | Purpose |
|------|---------|
| `01_OB1.xml` | Main cyclic OB |
| `02_Warm Restart.xml` | Warm restart OB |
| `03_CYC_INT2.xml` | Cyclic interrupt 2 |
| `04_CYC_INT5.xml` | Cyclic interrupt 5 |
| `05_MOD_ERR.xml` | Module error OB |
| `07_CYCL_FLT.xml` | Cycle fault OB |
| `08_HW_INT0.xml` | Hardware interrupt 0 |
| `09_IO_FLT1.xml` | I/O fault OB |
| `11_PROG_ERR.xml` | Program error OB |
| `12_RACK_FLT.xml` | Rack fault OB |

### System Functions (`00 Sys/`)
| File | Purpose |
|------|---------|
| `CheckData.xml` | Data checking |
| `Count_CycleTime.xml` | Cycle time counting |
| `Count_CycleTime_V3.xml` | Cycle time counting v3 |
| `SysFlowCtrlGraph.xml` | Flow control graph |
| `SystemMode.xml` | System mode management |

### Communication (`02_Comm/`)
| Folder | Content |
|--------|---------|
| `03-Diagnosis/` | Diagnostic FBs |
| `04-ChangeOver/` | Changeover logic |
| `06_SysDataBlock&Function/` | System data/functions |

### Reusable Function Blocks (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `003 Tower_Lamp/` | Tower lamp control (`FB_Tower_4Lamp.xml`) |
| `101 Cylinder/` | Cylinder control (`CylinderCtrl_V2.xml`, `CylinderModule_V2.xml`) |
| `102 SafetyGate/` | Safety gate (`SafetyGate.xml`) |
| `201 Stopper/` | Stopper control (`FB_Stopper.xml`) |
| `202 Conveyer_Line/` | Motor control (`MotorContro.xml`) |
| `999 Base/` | Base functions (`FB_Next.xml`) |

### Device-Specific (`03_Device/`)
| Folder | Content |
|--------|---------|
| `102 SafetyGate/` | Material gate |
| `211 ATEQ LeakTest/` | ATEQ F620 leak test |
| `212 Analog/` | Analog processing |

### User Functions (`500 User/`)
| Folder | Content |
|--------|---------|
| `100 FixtureCheck/` | Fixture checking |
| `104 PartDataManage/` | Part data management |

### External Device Libraries
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner control |
| `RCS-PPK/` | Stopper control library |

### Special Folders
| Folder | Purpose |
|--------|---------|
| `__MES MONITORING/` | MES monitoring FBs |
| `__PARAMETERS/` | Recipe/parameter handling |
| `Z_Reserve/` | Reserved/commissioning blocks |

---

## 🏭 STATION OP010 (`Program blocks/OP010/`)

Main station logic organized by function:

### Main (`00_Main/`)
| File | Purpose |
|------|---------|
| `ST10_Main.xml` | Main station FB |
| `ST10_GeneralData.xml` | General data DB |
| `Station_Sys.xml` | Station system FB |
| `iDB/ST10_SystemModeFB_iDB.xml` | System mode instance DB |

### Input Processing (`01_Input/`)
| File | Purpose |
|------|---------|
| `ST10_Input.xml` | Input processing |
| `ST10_SysInput.xml` | System input processing |

### Output Processing (`02_Output/`)
| File | Purpose |
|------|---------|
| `ST10_Output.xml` | Output processing |
| `ST10_SysOutput.xml` | System output processing |
| `ST10_FB_Tower_4Lamp_DB.xml` | Tower lamp instance DB |

### Automatic Mode (`03_Auto/`)
| Folder/File | Purpose |
|-------------|---------|
| `AutoProcessControl.xml` | Auto process control |
| `AutoProcessData.xml` | Auto process data |
| `AutoProcessData_Buffer.xml` | Process data buffer |
| `PalletRelease.xml` | Pallet release logic |
| `ST10_PM.xml` | PM interface |
| `TON.xml` | Timer functions |
| `01ChangeOver/` | Changeover flows |
| `A1_TableLoad&Scan/` | Table A1 loading & scanning |
| `A2_TableLoad&Scan/` | Table A2 loading & scanning |
| `B_Press/` | Press operations (B1, B2) |
| `C_Glue/` | Gluing operation |
| `F_Robot/` | Robot operations (1, 2, 3) |
| `H_ShaftLifting&Load&Unload/` | Shaft lifting operations |
| `J_MagnetLifting&Load&Unload/` | Magnet lifting operations |
| `L_Unload/` | Unloading operations |
| `M_iDB/` | Instance DBs for all flows |
| `HMI/` | HMI interface blocks |

**Flow Sequence:**
1. `ST10_Flow1_A1TableScan` - A1 Table Scan
2. `ST10_Flow2_A1TableUnloading` - A1 Table Unload
3. `ST10_Flow3_A1RotaryShaftScan` - Rotary Shaft Scan
4. `ST10_Flow4_B1Press` - B1 Press
5. `ST10_Flow5_FRobot_1` - Robot 1 Operation
6. `ST10_Flow6_ToolCodeScan` - Tool Code Scan
7. `ST10_Flow7_CGlueing` - Gluing
8. `ST10_Flow8_FRobot_2` - Robot 2 Operation
11. `ST10_Flow11_A2TableScan` - A2 Table Scan
12. `ST10_Flow12_A2TableUnloading` - A2 Table Unload
14. `ST10_Flow14_B2Press` - B2 Press
15. `ST10_Flow15_FRobot_3` - Robot 3 Operation
21. `ST10_Flow21_HShaftLifting` - H Shaft Lifting
22. `ST10_Flow22_JMagnetLifting` - J Magnet Lifting
23. `ST10_Flow23_KReserveLifting` - K Reserve Lifting
24. `ST10_Flow24_LUnloadingTrans` - L Unloading Transfer
25. `ST10_Flow25_HShaftLoad&Unload` - H Shaft Load/Unload
26. `ST10_Flow26_JMagnetLoad&Unload` - J Magnet Load/Unload
27. `ST10_Flow27_KReserveLoad&Unload` - K Reserve Load/Unload
28. `ST10_Flow28_LUnloadingLoad&Unload` - L Unloading Load/Unload

### Manual Mode (`04_Manual/`)
| File | Purpose |
|------|---------|
| `ST10_Manual.xml` | Manual operation logic |

### Alarm Handling (`05_Alarm/`)
| File | Purpose |
|------|---------|
| `ST10_Alarm.xml` | Alarm management |
| `ST10_DeviceError.xml` | Device error handling |
| `ST10_GlobalError.xml` | Global error handling |

### Warning Handling (`06_Warning/`)
| File | Purpose |
|------|---------|
| `ST10_Warning.xml` | Warning management |
| `ST10_WarningDB.xml` | Warning data block |

### Tips (`07_Tip/`)
| File | Purpose |
|------|---------|
| `ST10_Tip.xml` | Tip management |
| `ST10_TipDB.xml` | Tip data block |

### Changeover (`08_ChangeOver/`)
| File | Purpose |
|------|---------|
| `ST10_ChangeOver.xml` | Changeover logic |
| `Parameter.xml` | Parameters |
| `ST10_RecipeDB.xml` | Recipe database |
| `ST10_RecipeDB_HMI.xml` | HMI recipe interface |
| `ST10_RecipeActiveDB.xml` | Active recipe DB |
| `MES/OP010_MES_RecipeDB.xml` | MES recipe DB |

### Cycle Time (`09_Count_CycleTime/`)
| File | Purpose |
|------|---------|
| `ST10_CountCycleTimeMain.xml` | Main cycle time counter |
| `ST10_CountCycleTimeMain_DB.xml` | Cycle time data block |
| `ST10_PMCountCycleTime.xml` | PM cycle time |

### Device Control (`10_Device/`)
| Folder | Device/Function |
|--------|-----------------|
| `01_Cylinder/` | Cylinders 1-100 (ST10Cylinder.xml + interfaces) |
| `03_SafetyGate/` | Safety gates 1-9 + Material gates 1-7 |
| `06_Stopper/` | Stopper control |
| `08_PressureAanlog/` | Pressure analog processing |
| `09_CuringOven/` | Curing oven control |
| `18_SR1000 Scan/` | Keyence SR1000 scanners (8 instances) |
| `21_IV3/` | Keyence IV3 vision sensors |
| `22_IAI/` | IAI servo axes (A1, A2, A3) |
| `23_Kistler/` | Kistler press systems (1 & 2) |
| `24_Robot/` | Kuka robots (1, 2, 3) |
| `25_V90/` | V90 servo drives (A1-A4) |
| `26_Stopper/` | Additional stopper control |
| `27_Pilz/` | Pilz safety system |
| `28_Gluing/` | Gluing system control |
| `29_NG/` | NG (Not Good) box control |
| `31_Motor_1/` | Motor controls 1-17 |

### MES Integration (`11_MES/`)
| File | Purpose |
|------|---------|
| `MES.xml` | Main MES FB |
| `MES_CheckControl.xml` | MES check control |
| `MES_CHeck.xml` / `MES Check_fb.xml` | MES check functions |
| `MES_CHeck_DB.xml` | MES check DB |
| `MEStoPLC.xml` | MES to PLC data |
| `PLCtoMES.xml` | PLC to MES data |
| `DT-Chars.xml` / `DT-Chars_DB.xml` | Data type char conversion |
| `Station1LoadData.xml` - `Station8UnLoadData.xml` | Station load/unload data |
| `Scanner1LoadData.xml` | Scanner load data |

### Part Data (`12_PartData/`)
| File | Purpose |
|------|---------|
| `ST10_PartData.xml` | Part data management |
| `PartData_Interface_DB.xml` | Part data interface |
| `PartDataManage_Part1_DB.xml` - `PartDataManage_Part4_DB.xml` | Part data for parts 1-4 |

---

## 📋 STANDARDS & GUIDELINES

### Naming Conventions
| Prefix | Meaning | Example |
|--------|---------|---------|
| `ST10_` | Station 10 blocks | `ST10_Main.xml` |
| `ST10_FlowX_` | Process flow step X | `ST10_Flow1_A1TableScan.xml` |
| `FB_` | Function Block | `FB_Stopper.xml` |
| `FC_` | Function Call | `FC_Save_Values_Final.xml` |
| `DB_` | Data Block | `DB_MES_Monitoring.xml` |
| `UDT_` | User Data Type | `UDT_RECIPE.xml` |
| `iDB/` | Instance Data Blocks folder | - |

### File Extensions
| Extension | Type |
|-----------|------|
| `.xml` | TIA Portal exported block (standard) |
| `.scl` | Structured Control Language (Siemens) |
| `.db` | Database file |

### Folder Numbering Convention
| Range | Category |
|-------|----------|
| `00-09` | System/Organization |
| `01-09` | Organization Blocks |
| `10-99` | Function Blocks |
| `100-199` | User Functions |
| `200-299` | Devices |
| `500+` | Custom/User |

---

## 🔍 WHERE TO ADD NEW COMPONENTS

### New Device Type (UDT)
📂 `PLC data types/03 FunctionBlocks/`  
Create folder: `[NNN] [DeviceName]/`  
Add UDT in: `[NNN].1 UDT/[Name].xml`

### New Device Instance
📂 `Program blocks/OP010/10_Device/`  
Create folder: `[NN]_[DeviceName]/`  
Add control FB and instance DBs

### New Process Flow Step
📂 `Program blocks/OP010/03_Auto/`  
Add to appropriate subfolder (A1, A2, B_Press, etc.)  
Create: `ST10_Flow[X]_[Description].xml`  
Create iDB: `M_iDB/ST10_Flow[X]_[Description]_iDB.xml`

### New Recipe Parameter
📂 `PLC data types/_PARAMETERS_RECIPES/`  
Add UDT definition  
Update: `UDT_RECIPE.xml`

### New MES Data Exchange
📂 `Program blocks/OP010/11_MES/`  
Create: `Station[X]LoadData.xml` / `Station[X]UnLoadData.xml`

### New Constant/Enum
📂 `PLC tags/constant/`  
Create or modify appropriate XML file

---

## ⚠️ NOTES

- **OLD SHIT folders** contain deprecated/legacy code - do not use for new development
- **Z_Reserve folder** is for temporary/commissioning blocks
- **iDB folders** contain instance data blocks (automatically generated instances of FBs)
- Flow numbers are NOT sequential (gaps exist: 9, 10, 13, 16-20, etc.)
- Multiple file formats exist: `.xml` (TIA exports), `.scl` (source code)


> **Generated:** 2026-02-01  
> **Project:** OP10 Station PLC Code  
> **Purpose:** Siemens TIA Portal PLC Project for Manufacturing Station

---

## 📁 ROOT DIRECTORY STRUCTURE

```
📂 OP10/
├── 📁 DB_ALL_PROCESS_PARAMETERS.db          # Process parameters database
├── 📁 GlueningRotaryTable.db                # Gluing rotary table database
├── 📁 DOKUMENTACE/                          # Documentation folder
├── 📁 PLC data types/                       # UDTs (User Data Types)
├── 📁 PLC tags/                             # PLC tag tables
└── 📁 Program blocks/                       # Main program logic (FC, FB, DB, OB)
```

---

## 📊 PLC DATA TYPES (`PLC data types/`)

User-Defined Types (UDTs) organized by category:

### System Types (`00 Sys/`)
| File | Purpose |
|------|---------|
| `RCS_CountCycleTime_V1.xml` | Cycle time counting structure |
| `RCS_PMInterface_V1.xml` | PM Interface structure |
| `RCS_SysAlarmWarning_V1.xml` | System alarm/warning structure |
| `RCS_SysAuto_V1.xml` | Auto mode structure |
| `RCS_SysCmd_V1.xml` | System commands structure |
| `RCS_SysComInterface_V1.xml` | Communication interface |
| `RCS_SysCount_V1.xml` | System counter structure |
| `RCS_SysCycleTime_V1.xml` | System cycle time |
| `RCS_SysManual_V1.xml` | Manual mode structure |
| `RCS_SysSafety_V1.xml` | Safety system structure |
| `RCS_SysStatus_V1.xml` | System status structure |

### Function Block Types (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `101 Cylinder/` | Cylinder control UDT (`Cyl.xml`) |
| `102 SafetyGate/` | Safety gate UDT (`SafetyGateUDT.xml`) |
| `105 MaterialGate/` | Material gate UDT |
| `201 Stopper/` | Stopper UDT (`ST_Stopper.xml`, `UDT_Stopper_FB.xml`) |
| `202 Conveyer_Line/` | Motor control UDT (`Motor_Control.xml`) |
| `211 ATEQ LeakTest/` | ATEQ leak test visual type |
| `212 Analog/` | General analog UDT (`ST_GeneralAnalog.xml`) |

### User Types (`500 User/`)
| File | Purpose |
|------|---------|
| `ATEQRecipe.xml` | ATEQ recipe structure |
| `Check.xml` | Check data structure |
| `PresserRecipe.xml` | Presser recipe structure |
| `StaProcessData.xml` | Station process data |
| `UDT_LabelFeeder.xml` | Label feeder UDT |
| `UDT_Marking CharToASCII.xml` | Marking char conversion |
| `UDT_Marking StringToChar.xml` | Marking string conversion |
| `UDT_StaProcessData.xml` | Station process data UDT |
| `100 FixtureCheck/` | Fixture check UDT |
| `104 PartDataManage/` | Part data management UDTs |
| `210 Recipe/` | Recipe axis UDT |

### External Device Types
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner (HMI, Input, Output types) |
| `LXL/` | IAI Servo, Kistler, Kuka Robot types |
| `MES/` | MES monitoring types |
| `ProcessData/` | Process data types |
| `RCS-PPK/` | Stopper interface types |

### Recipe Parameters (`_PARAMETERS_RECIPES/`)
| File | Purpose |
|------|---------|
| `UDT_Gripper_Fixture_Codes.xml` | Gripper/fixture codes |
| `UDT_IAI_Axis_Positions.xml` | IAI axis positions |
| `UDT_Motion_Point_IAI.xml` | IAI motion points |
| `UDT_Motion_Point_V90.xml` | V90 motion points |
| `UDT_OP10_Recipe_type.xml` | OP10 recipe type |
| `UDT_RECIPE.xml` | Main recipe structure |
| `UDT_Recipe_ATEQ.xml` | ATEQ recipe |
| `UDT_Recipe_PressCurve.xml` | Press curve recipe |
| `UDT_V90_Axis_Positions.xml` | V90 axis positions |

### Enums
| File | Purpose |
|------|---------|
| `NGDoorState_Enum.xml` | NG Door state enumeration |
| `PartStatus_Enum.xml` | Part status enumeration |
| `UDT_OP10_Recipe_diff.xml` | Recipe difference structure |

---

## 🏷️ PLC TAGS (`PLC tags/`)

### Tag Tables
| File/Folder | Content |
|-------------|---------|
| `Default variable table.xml` | Default PLC tags |
| `NGSensor.xml` | NG sensor tags |
| `STEP7 classic symbols.xml` | STEP7 classic symbols |
| `constant/` | Constants (Flow, IV3, Lifting, Marking, MES codes, PartType, ProcessResult, RFID, TestResult, partstatus) |
| `IO/` | I/O tags (PLC DI/DQ, Remote IO DI/DO) |

---

## 🔧 PROGRAM BLOCKS (`Program blocks/`)

### Organization Blocks (`01_OB/`)
| File | Purpose |
|------|---------|
| `01_OB1.xml` | Main cyclic OB |
| `02_Warm Restart.xml` | Warm restart OB |
| `03_CYC_INT2.xml` | Cyclic interrupt 2 |
| `04_CYC_INT5.xml` | Cyclic interrupt 5 |
| `05_MOD_ERR.xml` | Module error OB |
| `07_CYCL_FLT.xml` | Cycle fault OB |
| `08_HW_INT0.xml` | Hardware interrupt 0 |
| `09_IO_FLT1.xml` | I/O fault OB |
| `11_PROG_ERR.xml` | Program error OB |
| `12_RACK_FLT.xml` | Rack fault OB |

### System Functions (`00 Sys/`)
| File | Purpose |
|------|---------|
| `CheckData.xml` | Data checking |
| `Count_CycleTime.xml` | Cycle time counting |
| `Count_CycleTime_V3.xml` | Cycle time counting v3 |
| `SysFlowCtrlGraph.xml` | Flow control graph |
| `SystemMode.xml` | System mode management |

### Communication (`02_Comm/`)
| Folder | Content |
|--------|---------|
| `03-Diagnosis/` | Diagnostic FBs |
| `04-ChangeOver/` | Changeover logic |
| `06_SysDataBlock&Function/` | System data/functions |

### Reusable Function Blocks (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `003 Tower_Lamp/` | Tower lamp control (`FB_Tower_4Lamp.xml`) |
| `101 Cylinder/` | Cylinder control (`CylinderCtrl_V2.xml`, `CylinderModule_V2.xml`) |
| `102 SafetyGate/` | Safety gate (`SafetyGate.xml`) |
| `201 Stopper/` | Stopper control (`FB_Stopper.xml`) |
| `202 Conveyer_Line/` | Motor control (`MotorContro.xml`) |
| `999 Base/` | Base functions (`FB_Next.xml`) |

### Device-Specific (`03_Device/`)
| Folder | Content |
|--------|---------|
| `102 SafetyGate/` | Material gate |
| `211 ATEQ LeakTest/` | ATEQ F620 leak test |
| `212 Analog/` | Analog processing |

### User Functions (`500 User/`)
| Folder | Content |
|--------|---------|
| `100 FixtureCheck/` | Fixture checking |
| `104 PartDataManage/` | Part data management |

### External Device Libraries
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner control |
| `RCS-PPK/` | Stopper control library |

### Special Folders
| Folder | Purpose |
|--------|---------|
| `__MES MONITORING/` | MES monitoring FBs |
| `__PARAMETERS/` | Recipe/parameter handling |
| `Z_Reserve/` | Reserved/commissioning blocks |

---

## 🏭 STATION OP010 (`Program blocks/OP010/`)

Main station logic organized by function:

### Main (`00_Main/`)
| File | Purpose |
|------|---------|
| `ST10_Main.xml` | Main station FB |
| `ST10_GeneralData.xml` | General data DB |
| `Station_Sys.xml` | Station system FB |
| `iDB/ST10_SystemModeFB_iDB.xml` | System mode instance DB |

### Input Processing (`01_Input/`)
| File | Purpose |
|------|---------|
| `ST10_Input.xml` | Input processing |
| `ST10_SysInput.xml` | System input processing |

### Output Processing (`02_Output/`)
| File | Purpose |
|------|---------|
| `ST10_Output.xml` | Output processing |
| `ST10_SysOutput.xml` | System output processing |
| `ST10_FB_Tower_4Lamp_DB.xml` | Tower lamp instance DB |

### Automatic Mode (`03_Auto/`)
| Folder/File | Purpose |
|-------------|---------|
| `AutoProcessControl.xml` | Auto process control |
| `AutoProcessData.xml` | Auto process data |
| `AutoProcessData_Buffer.xml` | Process data buffer |
| `PalletRelease.xml` | Pallet release logic |
| `ST10_PM.xml` | PM interface |
| `TON.xml` | Timer functions |
| `01ChangeOver/` | Changeover flows |
| `A1_TableLoad&Scan/` | Table A1 loading & scanning |
| `A2_TableLoad&Scan/` | Table A2 loading & scanning |
| `B_Press/` | Press operations (B1, B2) |
| `C_Glue/` | Gluing operation |
| `F_Robot/` | Robot operations (1, 2, 3) |
| `H_ShaftLifting&Load&Unload/` | Shaft lifting operations |
| `J_MagnetLifting&Load&Unload/` | Magnet lifting operations |
| `L_Unload/` | Unloading operations |
| `M_iDB/` | Instance DBs for all flows |
| `HMI/` | HMI interface blocks |

**Flow Sequence:**
1. `ST10_Flow1_A1TableScan` - A1 Table Scan
2. `ST10_Flow2_A1TableUnloading` - A1 Table Unload
3. `ST10_Flow3_A1RotaryShaftScan` - Rotary Shaft Scan
4. `ST10_Flow4_B1Press` - B1 Press
5. `ST10_Flow5_FRobot_1` - Robot 1 Operation
6. `ST10_Flow6_ToolCodeScan` - Tool Code Scan
7. `ST10_Flow7_CGlueing` - Gluing
8. `ST10_Flow8_FRobot_2` - Robot 2 Operation
11. `ST10_Flow11_A2TableScan` - A2 Table Scan
12. `ST10_Flow12_A2TableUnloading` - A2 Table Unload
14. `ST10_Flow14_B2Press` - B2 Press
15. `ST10_Flow15_FRobot_3` - Robot 3 Operation
21. `ST10_Flow21_HShaftLifting` - H Shaft Lifting
22. `ST10_Flow22_JMagnetLifting` - J Magnet Lifting
23. `ST10_Flow23_KReserveLifting` - K Reserve Lifting
24. `ST10_Flow24_LUnloadingTrans` - L Unloading Transfer
25. `ST10_Flow25_HShaftLoad&Unload` - H Shaft Load/Unload
26. `ST10_Flow26_JMagnetLoad&Unload` - J Magnet Load/Unload
27. `ST10_Flow27_KReserveLoad&Unload` - K Reserve Load/Unload
28. `ST10_Flow28_LUnloadingLoad&Unload` - L Unloading Load/Unload

### Manual Mode (`04_Manual/`)
| File | Purpose |
|------|---------|
| `ST10_Manual.xml` | Manual operation logic |

### Alarm Handling (`05_Alarm/`)
| File | Purpose |
|------|---------|
| `ST10_Alarm.xml` | Alarm management |
| `ST10_DeviceError.xml` | Device error handling |
| `ST10_GlobalError.xml` | Global error handling |

### Warning Handling (`06_Warning/`)
| File | Purpose |
|------|---------|
| `ST10_Warning.xml` | Warning management |
| `ST10_WarningDB.xml` | Warning data block |

### Tips (`07_Tip/`)
| File | Purpose |
|------|---------|
| `ST10_Tip.xml` | Tip management |
| `ST10_TipDB.xml` | Tip data block |

### Changeover (`08_ChangeOver/`)
| File | Purpose |
|------|---------|
| `ST10_ChangeOver.xml` | Changeover logic |
| `Parameter.xml` | Parameters |
| `ST10_RecipeDB.xml` | Recipe database |
| `ST10_RecipeDB_HMI.xml` | HMI recipe interface |
| `ST10_RecipeActiveDB.xml` | Active recipe DB |
| `MES/OP010_MES_RecipeDB.xml` | MES recipe DB |

### Cycle Time (`09_Count_CycleTime/`)
| File | Purpose |
|------|---------|
| `ST10_CountCycleTimeMain.xml` | Main cycle time counter |
| `ST10_CountCycleTimeMain_DB.xml` | Cycle time data block |
| `ST10_PMCountCycleTime.xml` | PM cycle time |

### Device Control (`10_Device/`)
| Folder | Device/Function |
|--------|-----------------|
| `01_Cylinder/` | Cylinders 1-100 (ST10Cylinder.xml + interfaces) |
| `03_SafetyGate/` | Safety gates 1-9 + Material gates 1-7 |
| `06_Stopper/` | Stopper control |
| `08_PressureAanlog/` | Pressure analog processing |
| `09_CuringOven/` | Curing oven control |
| `18_SR1000 Scan/` | Keyence SR1000 scanners (8 instances) |
| `21_IV3/` | Keyence IV3 vision sensors |
| `22_IAI/` | IAI servo axes (A1, A2, A3) |
| `23_Kistler/` | Kistler press systems (1 & 2) |
| `24_Robot/` | Kuka robots (1, 2, 3) |
| `25_V90/` | **V90 servo drives + TO_BasicPos technology** |
| `26_Stopper/` | Additional stopper control |
| `27_Pilz/` | Pilz safety system |
| `28_Gluing/` | Gluing system control |
| `29_NG/` | NG (Not Good) box control |
| `31_Motor_1/` | Motor controls 1-17 |

#### V90 Servo Technology Objects (`25_V90/`)
The V90 folder contains **2 different servo control technologies**:

**1. Standard V90 Position Control (fbV90Ctrl)**
| File | Purpose |
|------|---------|
| `V90_Servo.xml` | Main FB calling 4 servo instances (Servo_380A1..383A1) |
| `Servo.xml` | FC wrapper calling V90_Servo FB |
| `ServoV90_A1.xml` - `ServoV90_A4.xml` | Global DBs for servo data (In/Out structs) |
| `V90Servo_DB.xml` | Instance DB for V90_Servo FB |
| `V90_Standard/fbV90Ctrl.xml` | **Standard V90 control FB** - handles jog, auto, homing, position lists |
| `V90_Standard/SINA_POS.xml` | Siemens SINA_POS block for V90 |
| `V90_Standard/SINA_PARA_S.xml` | Siemens parameter access block |
| `V90_Standard/ServoCheck/` | Servo startup & position check |

**2. TO_BasicPos Technology Object (Motion Control)**
| File | Purpose |
|------|---------|
| `FB_GlueRotation_BasicPos.scl` | **TO_BasicPos-based FB** using `BasicPosControl` technology object for rotary table gluing |
| `FB_GlueRotationJob.scl` | Job controller for glue rotation using standard V90 interface |
| `FB_RotaryJobController.scl` | **TO-based rotary control** using `MC_Power` + `MC_MoveRelative` motion control blocks |
| `ServoV90_DeviceCtl.xml` | Device control logic |
| `Patch/` | Positioning order check patches |

**Key Difference:**
- `fbV90Ctrl` = Standard V90 telegram 111 positioning (legacy)
- `FB_GlueRotation_BasicPos` = Technology Object Basic Positioning (modern, uses `BasicPosControl`)
- `FB_RotaryJobController` = Full TO-based motion control (`MC_Power`, `MC_MoveRelative`)

### MES Integration (`11_MES/`)
| File | Purpose |
|------|---------|
| `MES.xml` | Main MES FB |
| `MES_CheckControl.xml` | MES check control |
| `MES_CHeck.xml` / `MES Check_fb.xml` | MES check functions |
| `MES_CHeck_DB.xml` | MES check DB |
| `MEStoPLC.xml` | MES to PLC data |
| `PLCtoMES.xml` | PLC to MES data |
| `DT-Chars.xml` / `DT-Chars_DB.xml` | Data type char conversion |
| `Station1LoadData.xml` - `Station8UnLoadData.xml` | Station load/unload data |
| `Scanner1LoadData.xml` | Scanner load data |

### Part Data (`12_PartData/`)
| File | Purpose |
|------|---------|
| `ST10_PartData.xml` | Part data management |
| `PartData_Interface_DB.xml` | Part data interface |
| `PartDataManage_Part1_DB.xml` - `PartDataManage_Part4_DB.xml` | Part data for parts 1-4 |

---

## 📋 STANDARDS & GUIDELINES

### Naming Conventions
| Prefix | Meaning | Example |
|--------|---------|---------|
| `ST10_` | Station 10 blocks | `ST10_Main.xml` |
| `ST10_FlowX_` | Process flow step X | `ST10_Flow1_A1TableScan.xml` |
| `FB_` | Function Block | `FB_Stopper.xml` |
| `FC_` | Function Call | `FC_Save_Values_Final.xml` |
| `DB_` | Data Block | `DB_MES_Monitoring.xml` |
| `UDT_` | User Data Type | `UDT_RECIPE.xml` |
| `iDB/` | Instance Data Blocks folder | - |

### File Extensions
| Extension | Type |
|-----------|------|
| `.xml` | TIA Portal exported block (standard) |
| `.scl` | Structured Control Language (Siemens) |
| `.db` | Database file |

### Folder Numbering Convention
| Range | Category |
|-------|----------|
| `00-09` | System/Organization |
| `01-09` | Organization Blocks |
| `10-99` | Function Blocks |
| `100-199` | User Functions |
| `200-299` | Devices |
| `500+` | Custom/User |

---

## 🔍 WHERE TO ADD NEW COMPONENTS

### New Device Type (UDT)
📂 `PLC data types/03 FunctionBlocks/`  
Create folder: `[NNN] [DeviceName]/`  
Add UDT in: `[NNN].1 UDT/[Name].xml`

### New Device Instance
📂 `Program blocks/OP010/10_Device/`  
Create folder: `[NN]_[DeviceName]/`  
Add control FB and instance DBs

### New Process Flow Step
📂 `Program blocks/OP010/03_Auto/`  
Add to appropriate subfolder (A1, A2, B_Press, etc.)  
Create: `ST10_Flow[X]_[Description].xml`  
Create iDB: `M_iDB/ST10_Flow[X]_[Description]_iDB.xml`

### New Recipe Parameter
📂 `PLC data types/_PARAMETERS_RECIPES/`  
Add UDT definition  
Update: `UDT_RECIPE.xml`

### New MES Data Exchange
📂 `Program blocks/OP010/11_MES/`  
Create: `Station[X]LoadData.xml` / `Station[X]UnLoadData.xml`

### New Constant/Enum
📂 `PLC tags/constant/`  
Create or modify appropriate XML file

---

## ⚠️ NOTES

- **OLD SHIT folders** contain deprecated/legacy code - do not use for new development
- **Z_Reserve folder** is for temporary/commissioning blocks
- **iDB folders** contain instance data blocks (automatically generated instances of FBs)
- Flow numbers are NOT sequential (gaps exist: 9, 10, 13, 16-20, etc.)
- Multiple file formats exist: `.xml` (TIA exports), `.scl` (source code)

> **Generated:** 2026-02-01  
> **Project:** OP10 Station PLC Code  
> **Purpose:** Siemens TIA Portal PLC Project for Manufacturing Station

---

## 📁 ROOT DIRECTORY STRUCTURE

```
📂 OP10/
├── 📁 DB_ALL_PROCESS_PARAMETERS.db          # Process parameters database
├── 📁 GlueningRotaryTable.db                # Gluing rotary table database
├── 📁 DOKUMENTACE/                          # Documentation folder
├── 📁 PLC data types/                       # UDTs (User Data Types)
├── 📁 PLC tags/                             # PLC tag tables
└── 📁 Program blocks/                       # Main program logic (FC, FB, DB, OB)
```

---

## 📊 PLC DATA TYPES (`PLC data types/`)

User-Defined Types (UDTs) organized by category:

### System Types (`00 Sys/`)
| File | Purpose |
|------|---------|
| `RCS_CountCycleTime_V1.xml` | Cycle time counting structure |
| `RCS_PMInterface_V1.xml` | PM Interface structure |
| `RCS_SysAlarmWarning_V1.xml` | System alarm/warning structure |
| `RCS_SysAuto_V1.xml` | Auto mode structure |
| `RCS_SysCmd_V1.xml` | System commands structure |
| `RCS_SysComInterface_V1.xml` | Communication interface |
| `RCS_SysCount_V1.xml` | System counter structure |
| `RCS_SysCycleTime_V1.xml` | System cycle time |
| `RCS_SysManual_V1.xml` | Manual mode structure |
| `RCS_SysSafety_V1.xml` | Safety system structure |
| `RCS_SysStatus_V1.xml` | System status structure |

### Function Block Types (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `101 Cylinder/` | Cylinder control UDT (`Cyl.xml`) |
| `102 SafetyGate/` | Safety gate UDT (`SafetyGateUDT.xml`) |
| `105 MaterialGate/` | Material gate UDT |
| `201 Stopper/` | Stopper UDT (`ST_Stopper.xml`, `UDT_Stopper_FB.xml`) |
| `202 Conveyer_Line/` | Motor control UDT (`Motor_Control.xml`) |
| `211 ATEQ LeakTest/` | ATEQ leak test visual type |
| `212 Analog/` | General analog UDT (`ST_GeneralAnalog.xml`) |

### User Types (`500 User/`)
| File | Purpose |
|------|---------|
| `ATEQRecipe.xml` | ATEQ recipe structure |
| `Check.xml` | Check data structure |
| `PresserRecipe.xml` | Presser recipe structure |
| `StaProcessData.xml` | Station process data |
| `UDT_LabelFeeder.xml` | Label feeder UDT |
| `UDT_Marking CharToASCII.xml` | Marking char conversion |
| `UDT_Marking StringToChar.xml` | Marking string conversion |
| `UDT_StaProcessData.xml` | Station process data UDT |
| `100 FixtureCheck/` | Fixture check UDT |
| `104 PartDataManage/` | Part data management UDTs |
| `210 Recipe/` | Recipe axis UDT |

### External Device Types
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner (HMI, Input, Output types) |
| `LXL/` | IAI Servo, Kistler, Kuka Robot types |
| `MES/` | MES monitoring types |
| `ProcessData/` | Process data types |
| `RCS-PPK/` | Stopper interface types |

### Recipe Parameters (`_PARAMETERS_RECIPES/`)
| File | Purpose |
|------|---------|
| `UDT_Gripper_Fixture_Codes.xml` | Gripper/fixture codes |
| `UDT_IAI_Axis_Positions.xml` | IAI axis positions |
| `UDT_Motion_Point_IAI.xml` | IAI motion points |
| `UDT_Motion_Point_V90.xml` | V90 motion points |
| `UDT_OP10_Recipe_type.xml` | OP10 recipe type |
| `UDT_RECIPE.xml` | Main recipe structure |
| `UDT_Recipe_ATEQ.xml` | ATEQ recipe |
| `UDT_Recipe_PressCurve.xml` | Press curve recipe |
| `UDT_V90_Axis_Positions.xml` | V90 axis positions |

### Enums
| File | Purpose |
|------|---------|
| `NGDoorState_Enum.xml` | NG Door state enumeration |
| `PartStatus_Enum.xml` | Part status enumeration |
| `UDT_OP10_Recipe_diff.xml` | Recipe difference structure |

---

## 🏷️ PLC TAGS (`PLC tags/`)

### Tag Tables
| File/Folder | Content |
|-------------|---------|
| `Default variable table.xml` | Default PLC tags |
| `NGSensor.xml` | NG sensor tags |
| `STEP7 classic symbols.xml` | STEP7 classic symbols |
| `constant/` | Constants (Flow, IV3, Lifting, Marking, MES codes, PartType, ProcessResult, RFID, TestResult, partstatus) |
| `IO/` | I/O tags (PLC DI/DQ, Remote IO DI/DO) |

---

## 🔧 PROGRAM BLOCKS (`Program blocks/`)

### Organization Blocks (`01_OB/`)
| File | Purpose |
|------|---------|
| `01_OB1.xml` | Main cyclic OB |
| `02_Warm Restart.xml` | Warm restart OB |
| `03_CYC_INT2.xml` | Cyclic interrupt 2 |
| `04_CYC_INT5.xml` | Cyclic interrupt 5 |
| `05_MOD_ERR.xml` | Module error OB |
| `07_CYCL_FLT.xml` | Cycle fault OB |
| `08_HW_INT0.xml` | Hardware interrupt 0 |
| `09_IO_FLT1.xml` | I/O fault OB |
| `11_PROG_ERR.xml` | Program error OB |
| `12_RACK_FLT.xml` | Rack fault OB |

### System Functions (`00 Sys/`)
| File | Purpose |
|------|---------|
| `CheckData.xml` | Data checking |
| `Count_CycleTime.xml` | Cycle time counting |
| `Count_CycleTime_V3.xml` | Cycle time counting v3 |
| `SysFlowCtrlGraph.xml` | Flow control graph |
| `SystemMode.xml` | System mode management |

### Communication (`02_Comm/`)
| Folder | Content |
|--------|---------|
| `03-Diagnosis/` | Diagnostic FBs |
| `04-ChangeOver/` | Changeover logic |
| `06_SysDataBlock&Function/` | System data/functions |

### Reusable Function Blocks (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `003 Tower_Lamp/` | Tower lamp control (`FB_Tower_4Lamp.xml`) |
| `101 Cylinder/` | Cylinder control (`CylinderCtrl_V2.xml`, `CylinderModule_V2.xml`) |
| `102 SafetyGate/` | Safety gate (`SafetyGate.xml`) |
| `201 Stopper/` | Stopper control (`FB_Stopper.xml`) |
| `202 Conveyer_Line/` | Motor control (`MotorContro.xml`) |
| `999 Base/` | Base functions (`FB_Next.xml`) |

### Device-Specific (`03_Device/`)
| Folder | Content |
|--------|---------|
| `102 SafetyGate/` | Material gate |
| `211 ATEQ LeakTest/` | ATEQ F620 leak test |
| `212 Analog/` | Analog processing |

### User Functions (`500 User/`)
| Folder | Content |
|--------|---------|
| `100 FixtureCheck/` | Fixture checking |
| `104 PartDataManage/` | Part data management |

### External Device Libraries
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner control |
| `RCS-PPK/` | Stopper control library |

### Special Folders
| Folder | Purpose |
|--------|---------|
| `__MES MONITORING/` | MES monitoring FBs |
| `__PARAMETERS/` | Recipe/parameter handling |
| `Z_Reserve/` | Reserved/commissioning blocks |

---

## 🏭 STATION OP010 (`Program blocks/OP010/`)

Main station logic organized by function:

### Main (`00_Main/`)
| File | Purpose |
|------|---------|
| `ST10_Main.xml` | Main station FB |
| `ST10_GeneralData.xml` | General data DB |
| `Station_Sys.xml` | Station system FB |
| `iDB/ST10_SystemModeFB_iDB.xml` | System mode instance DB |

### Input Processing (`01_Input/`)
| File | Purpose |
|------|---------|
| `ST10_Input.xml` | Input processing |
| `ST10_SysInput.xml` | System input processing |

### Output Processing (`02_Output/`)
| File | Purpose |
|------|---------|
| `ST10_Output.xml` | Output processing |
| `ST10_SysOutput.xml` | System output processing |
| `ST10_FB_Tower_4Lamp_DB.xml` | Tower lamp instance DB |

### Automatic Mode (`03_Auto/`)
| Folder/File | Purpose |
|-------------|---------|
| `AutoProcessControl.xml` | Auto process control |
| `AutoProcessData.xml` | Auto process data |
| `AutoProcessData_Buffer.xml` | Process data buffer |
| `PalletRelease.xml` | Pallet release logic |
| `ST10_PM.xml` | PM interface |
| `TON.xml` | Timer functions |
| `01ChangeOver/` | Changeover flows |
| `A1_TableLoad&Scan/` | Table A1 loading & scanning |
| `A2_TableLoad&Scan/` | Table A2 loading & scanning |
| `B_Press/` | Press operations (B1, B2) |
| `C_Glue/` | Gluing operation |
| `F_Robot/` | Robot operations (1, 2, 3) |
| `H_ShaftLifting&Load&Unload/` | Shaft lifting operations |
| `J_MagnetLifting&Load&Unload/` | Magnet lifting operations |
| `L_Unload/` | Unloading operations |
| `M_iDB/` | Instance DBs for all flows |
| `HMI/` | HMI interface blocks |

**Flow Sequence:**
1. `ST10_Flow1_A1TableScan` - A1 Table Scan
2. `ST10_Flow2_A1TableUnloading` - A1 Table Unload
3. `ST10_Flow3_A1RotaryShaftScan` - Rotary Shaft Scan
4. `ST10_Flow4_B1Press` - B1 Press
5. `ST10_Flow5_FRobot_1` - Robot 1 Operation
6. `ST10_Flow6_ToolCodeScan` - Tool Code Scan
7. `ST10_Flow7_CGlueing` - Gluing
8. `ST10_Flow8_FRobot_2` - Robot 2 Operation
11. `ST10_Flow11_A2TableScan` - A2 Table Scan
12. `ST10_Flow12_A2TableUnloading` - A2 Table Unload
14. `ST10_Flow14_B2Press` - B2 Press
15. `ST10_Flow15_FRobot_3` - Robot 3 Operation
21. `ST10_Flow21_HShaftLifting` - H Shaft Lifting
22. `ST10_Flow22_JMagnetLifting` - J Magnet Lifting
23. `ST10_Flow23_KReserveLifting` - K Reserve Lifting
24. `ST10_Flow24_LUnloadingTrans` - L Unloading Transfer
25. `ST10_Flow25_HShaftLoad&Unload` - H Shaft Load/Unload
26. `ST10_Flow26_JMagnetLoad&Unload` - J Magnet Load/Unload
27. `ST10_Flow27_KReserveLoad&Unload` - K Reserve Load/Unload
28. `ST10_Flow28_LUnloadingLoad&Unload` - L Unloading Load/Unload

### Manual Mode (`04_Manual/`)
| File | Purpose |
|------|---------|
| `ST10_Manual.xml` | Manual operation logic |

### Alarm Handling (`05_Alarm/`)
| File | Purpose |
|------|---------|
| `ST10_Alarm.xml` | Alarm management |
| `ST10_DeviceError.xml` | Device error handling |
| `ST10_GlobalError.xml` | Global error handling |

### Warning Handling (`06_Warning/`)
| File | Purpose |
|------|---------|
| `ST10_Warning.xml` | Warning management |
| `ST10_WarningDB.xml` | Warning data block |

### Tips (`07_Tip/`)
| File | Purpose |
|------|---------|
| `ST10_Tip.xml` | Tip management |
| `ST10_TipDB.xml` | Tip data block |

### Changeover (`08_ChangeOver/`)
| File | Purpose |
|------|---------|
| `ST10_ChangeOver.xml` | Changeover logic |
| `Parameter.xml` | Parameters |
| `ST10_RecipeDB.xml` | Recipe database |
| `ST10_RecipeDB_HMI.xml` | HMI recipe interface |
| `ST10_RecipeActiveDB.xml` | Active recipe DB |
| `MES/OP010_MES_RecipeDB.xml` | MES recipe DB |

### Cycle Time (`09_Count_CycleTime/`)
| File | Purpose |
|------|---------|
| `ST10_CountCycleTimeMain.xml` | Main cycle time counter |
| `ST10_CountCycleTimeMain_DB.xml` | Cycle time data block |
| `ST10_PMCountCycleTime.xml` | PM cycle time |

### Device Control (`10_Device/`)
| Folder | Device/Function |
|--------|-----------------|
| `01_Cylinder/` | Cylinders 1-100 (ST10Cylinder.xml + interfaces) |
| `03_SafetyGate/` | Safety gates 1-9 + Material gates 1-7 |
| `06_Stopper/` | Stopper control |
| `08_PressureAanlog/` | Pressure analog processing |
| `09_CuringOven/` | Curing oven control |
| `18_SR1000 Scan/` | Keyence SR1000 scanners (8 instances) |
| `21_IV3/` | Keyence IV3 vision sensors |
| `22_IAI/` | IAI servo axes (A1, A2, A3) |
| `23_Kistler/` | Kistler press systems (1 & 2) |
| `24_Robot/` | Kuka robots (1, 2, 3) |
| `25_V90/` | V90 servo drives (A1-A4) |
| `26_Stopper/` | Additional stopper control |
| `27_Pilz/` | Pilz safety system |
| `28_Gluing/` | Gluing system control |
| `29_NG/` | NG (Not Good) box control |
| `31_Motor_1/` | Motor controls 1-17 |

### MES Integration (`11_MES/`)
| File | Purpose |
|------|---------|
| `MES.xml` | Main MES FB |
| `MES_CheckControl.xml` | MES check control |
| `MES_CHeck.xml` / `MES Check_fb.xml` | MES check functions |
| `MES_CHeck_DB.xml` | MES check DB |
| `MEStoPLC.xml` | MES to PLC data |
| `PLCtoMES.xml` | PLC to MES data |
| `DT-Chars.xml` / `DT-Chars_DB.xml` | Data type char conversion |
| `Station1LoadData.xml` - `Station8UnLoadData.xml` | Station load/unload data |
| `Scanner1LoadData.xml` | Scanner load data |

### Part Data (`12_PartData/`)
| File | Purpose |
|------|---------|
| `ST10_PartData.xml` | Part data management |
| `PartData_Interface_DB.xml` | Part data interface |
| `PartDataManage_Part1_DB.xml` - `PartDataManage_Part4_DB.xml` | Part data for parts 1-4 |

---

## 📋 STANDARDS & GUIDELINES

### Naming Conventions
| Prefix | Meaning | Example |
|--------|---------|---------|
| `ST10_` | Station 10 blocks | `ST10_Main.xml` |
| `ST10_FlowX_` | Process flow step X | `ST10_Flow1_A1TableScan.xml` |
| `FB_` | Function Block | `FB_Stopper.xml` |
| `FC_` | Function Call | `FC_Save_Values_Final.xml` |
| `DB_` | Data Block | `DB_MES_Monitoring.xml` |
| `UDT_` | User Data Type | `UDT_RECIPE.xml` |
| `iDB/` | Instance Data Blocks folder | - |

### File Extensions
| Extension | Type |
|-----------|------|
| `.xml` | TIA Portal exported block (standard) |
| `.scl` | Structured Control Language (Siemens) |
| `.db` | Database file |

### Folder Numbering Convention
| Range | Category |
|-------|----------|
| `00-09` | System/Organization |
| `01-09` | Organization Blocks |
| `10-99` | Function Blocks |
| `100-199` | User Functions |
| `200-299` | Devices |
| `500+` | Custom/User |

---

## 🔍 WHERE TO ADD NEW COMPONENTS

### New Device Type (UDT)
📂 `PLC data types/03 FunctionBlocks/`  
Create folder: `[NNN] [DeviceName]/`  
Add UDT in: `[NNN].1 UDT/[Name].xml`

### New Device Instance
📂 `Program blocks/OP010/10_Device/`  
Create folder: `[NN]_[DeviceName]/`  
Add control FB and instance DBs

### New Process Flow Step
📂 `Program blocks/OP010/03_Auto/`  
Add to appropriate subfolder (A1, A2, B_Press, etc.)  
Create: `ST10_Flow[X]_[Description].xml`  
Create iDB: `M_iDB/ST10_Flow[X]_[Description]_iDB.xml`

### New Recipe Parameter
📂 `PLC data types/_PARAMETERS_RECIPES/`  
Add UDT definition  
Update: `UDT_RECIPE.xml`

### New MES Data Exchange
📂 `Program blocks/OP010/11_MES/`  
Create: `Station[X]LoadData.xml` / `Station[X]UnLoadData.xml`

### New Constant/Enum
📂 `PLC tags/constant/`  
Create or modify appropriate XML file

---

## ⚠️ NOTES

- **OLD SHIT folders** contain deprecated/legacy code - do not use for new development
- **Z_Reserve folder** is for temporary/commissioning blocks
- **iDB folders** contain instance data blocks (automatically generated instances of FBs)
- Flow numbers are NOT sequential (gaps exist: 9, 10, 13, 16-20, etc.)
- Multiple file formats exist: `.xml` (TIA exports), `.scl` (source code)



> **Generated:** 2026-02-01  
> **Project:** OP10 Station PLC Code  
> **Purpose:** Siemens TIA Portal PLC Project for Manufacturing Station

---

## 📁 ROOT DIRECTORY STRUCTURE

```
📂 OP10/
├── 📁 DB_ALL_PROCESS_PARAMETERS.db          # Process parameters database
├── 📁 GlueningRotaryTable.db                # Gluing rotary table database
├── 📁 DOKUMENTACE/                          # Documentation folder
├── 📁 PLC data types/                       # UDTs (User Data Types)
├── 📁 PLC tags/                             # PLC tag tables
└── 📁 Program blocks/                       # Main program logic (FC, FB, DB, OB)
```

---

## 📊 PLC DATA TYPES (`PLC data types/`)

User-Defined Types (UDTs) organized by category:

### System Types (`00 Sys/`)
| File | Purpose |
|------|---------|
| `RCS_CountCycleTime_V1.xml` | Cycle time counting structure |
| `RCS_PMInterface_V1.xml` | PM Interface structure |
| `RCS_SysAlarmWarning_V1.xml` | System alarm/warning structure |
| `RCS_SysAuto_V1.xml` | Auto mode structure |
| `RCS_SysCmd_V1.xml` | System commands structure |
| `RCS_SysComInterface_V1.xml` | Communication interface |
| `RCS_SysCount_V1.xml` | System counter structure |
| `RCS_SysCycleTime_V1.xml` | System cycle time |
| `RCS_SysManual_V1.xml` | Manual mode structure |
| `RCS_SysSafety_V1.xml` | Safety system structure |
| `RCS_SysStatus_V1.xml` | System status structure |

### Function Block Types (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `101 Cylinder/` | Cylinder control UDT (`Cyl.xml`) |
| `102 SafetyGate/` | Safety gate UDT (`SafetyGateUDT.xml`) |
| `105 MaterialGate/` | Material gate UDT |
| `201 Stopper/` | Stopper UDT (`ST_Stopper.xml`, `UDT_Stopper_FB.xml`) |
| `202 Conveyer_Line/` | Motor control UDT (`Motor_Control.xml`) |
| `211 ATEQ LeakTest/` | ATEQ leak test visual type |
| `212 Analog/` | General analog UDT (`ST_GeneralAnalog.xml`) |

### User Types (`500 User/`)
| File | Purpose |
|------|---------|
| `ATEQRecipe.xml` | ATEQ recipe structure |
| `Check.xml` | Check data structure |
| `PresserRecipe.xml` | Presser recipe structure |
| `StaProcessData.xml` | Station process data |
| `UDT_LabelFeeder.xml` | Label feeder UDT |
| `UDT_Marking CharToASCII.xml` | Marking char conversion |
| `UDT_Marking StringToChar.xml` | Marking string conversion |
| `UDT_StaProcessData.xml` | Station process data UDT |
| `100 FixtureCheck/` | Fixture check UDT |
| `104 PartDataManage/` | Part data management UDTs |
| `210 Recipe/` | Recipe axis UDT |

### External Device Types
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner (HMI, Input, Output types) |
| `LXL/` | IAI Servo, Kistler, Kuka Robot types |
| `MES/` | MES monitoring types |
| `ProcessData/` | Process data types |
| `RCS-PPK/` | Stopper interface types |

### Recipe Parameters (`_PARAMETERS_RECIPES/`)
| File | Purpose |
|------|---------|
| `UDT_Gripper_Fixture_Codes.xml` | Gripper/fixture codes |
| `UDT_IAI_Axis_Positions.xml` | IAI axis positions |
| `UDT_Motion_Point_IAI.xml` | IAI motion points |
| `UDT_Motion_Point_V90.xml` | V90 motion points |
| `UDT_OP10_Recipe_type.xml` | OP10 recipe type |
| `UDT_RECIPE.xml` | Main recipe structure |
| `UDT_Recipe_ATEQ.xml` | ATEQ recipe |
| `UDT_Recipe_PressCurve.xml` | Press curve recipe |
| `UDT_V90_Axis_Positions.xml` | V90 axis positions |

### Enums
| File | Purpose |
|------|---------|
| `NGDoorState_Enum.xml` | NG Door state enumeration |
| `PartStatus_Enum.xml` | Part status enumeration |
| `UDT_OP10_Recipe_diff.xml` | Recipe difference structure |

---

## 🏷️ PLC TAGS (`PLC tags/`)

### Tag Tables
| File/Folder | Content |
|-------------|---------|
| `Default variable table.xml` | Default PLC tags |
| `NGSensor.xml` | NG sensor tags |
| `STEP7 classic symbols.xml` | STEP7 classic symbols |
| `constant/` | Constants (Flow, IV3, Lifting, Marking, MES codes, PartType, ProcessResult, RFID, TestResult, partstatus) |
| `IO/` | I/O tags (PLC DI/DQ, Remote IO DI/DO) |

---

## 🔧 PROGRAM BLOCKS (`Program blocks/`)

### Organization Blocks (`01_OB/`)
| File | Purpose |
|------|---------|
| `01_OB1.xml` | Main cyclic OB |
| `02_Warm Restart.xml` | Warm restart OB |
| `03_CYC_INT2.xml` | Cyclic interrupt 2 |
| `04_CYC_INT5.xml` | Cyclic interrupt 5 |
| `05_MOD_ERR.xml` | Module error OB |
| `07_CYCL_FLT.xml` | Cycle fault OB |
| `08_HW_INT0.xml` | Hardware interrupt 0 |
| `09_IO_FLT1.xml` | I/O fault OB |
| `11_PROG_ERR.xml` | Program error OB |
| `12_RACK_FLT.xml` | Rack fault OB |

### System Functions (`00 Sys/`)
| File | Purpose |
|------|---------|
| `CheckData.xml` | Data checking |
| `Count_CycleTime.xml` | Cycle time counting |
| `Count_CycleTime_V3.xml` | Cycle time counting v3 |
| `SysFlowCtrlGraph.xml` | Flow control graph |
| `SystemMode.xml` | System mode management |

### Communication (`02_Comm/`)
| Folder | Content |
|--------|---------|
| `03-Diagnosis/` | Diagnostic FBs |
| `04-ChangeOver/` | Changeover logic |
| `06_SysDataBlock&Function/` | System data/functions |

### Reusable Function Blocks (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `003 Tower_Lamp/` | Tower lamp control (`FB_Tower_4Lamp.xml`) |
| `101 Cylinder/` | Cylinder control (`CylinderCtrl_V2.xml`, `CylinderModule_V2.xml`) |
| `102 SafetyGate/` | Safety gate (`SafetyGate.xml`) |
| `201 Stopper/` | Stopper control (`FB_Stopper.xml`) |
| `202 Conveyer_Line/` | Motor control (`MotorContro.xml`) |
| `999 Base/` | Base functions (`FB_Next.xml`) |

### Device-Specific (`03_Device/`)
| Folder | Content |
|--------|---------|
| `102 SafetyGate/` | Material gate |
| `211 ATEQ LeakTest/` | ATEQ F620 leak test |
| `212 Analog/` | Analog processing |

### User Functions (`500 User/`)
| Folder | Content |
|--------|---------|
| `100 FixtureCheck/` | Fixture checking |
| `104 PartDataManage/` | Part data management |

### External Device Libraries
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner control |
| `RCS-PPK/` | Stopper control library |

### Special Folders
| Folder | Purpose |
|--------|---------|
| `__MES MONITORING/` | MES monitoring FBs |
| `__PARAMETERS/` | Recipe/parameter handling |
| `Z_Reserve/` | Reserved/commissioning blocks |

---

## 🏭 STATION OP010 (`Program blocks/OP010/`)

Main station logic organized by function:

### Main (`00_Main/`)
| File | Purpose |
|------|---------|
| `ST10_Main.xml` | Main station FB |
| `ST10_GeneralData.xml` | General data DB |
| `Station_Sys.xml` | Station system FB |
| `iDB/ST10_SystemModeFB_iDB.xml` | System mode instance DB |

### Input Processing (`01_Input/`)
| File | Purpose |
|------|---------|
| `ST10_Input.xml` | Input processing |
| `ST10_SysInput.xml` | System input processing |

### Output Processing (`02_Output/`)
| File | Purpose |
|------|---------|
| `ST10_Output.xml` | Output processing |
| `ST10_SysOutput.xml` | System output processing |
| `ST10_FB_Tower_4Lamp_DB.xml` | Tower lamp instance DB |

### Automatic Mode (`03_Auto/`)
| Folder/File | Purpose |
|-------------|---------|
| `AutoProcessControl.xml` | Auto process control |
| `AutoProcessData.xml` | Auto process data |
| `AutoProcessData_Buffer.xml` | Process data buffer |
| `PalletRelease.xml` | Pallet release logic |
| `ST10_PM.xml` | PM interface |
| `TON.xml` | Timer functions |
| `01ChangeOver/` | Changeover flows |
| `A1_TableLoad&Scan/` | Table A1 loading & scanning |
| `A2_TableLoad&Scan/` | Table A2 loading & scanning |
| `B_Press/` | Press operations (B1, B2) |
| `C_Glue/` | Gluing operation |
| `F_Robot/` | Robot operations (1, 2, 3) |
| `H_ShaftLifting&Load&Unload/` | Shaft lifting operations |
| `J_MagnetLifting&Load&Unload/` | Magnet lifting operations |
| `L_Unload/` | Unloading operations |
| `M_iDB/` | Instance DBs for all flows |
| `HMI/` | HMI interface blocks |

**Flow Sequence:**
1. `ST10_Flow1_A1TableScan` - A1 Table Scan
2. `ST10_Flow2_A1TableUnloading` - A1 Table Unload
3. `ST10_Flow3_A1RotaryShaftScan` - Rotary Shaft Scan
4. `ST10_Flow4_B1Press` - B1 Press
5. `ST10_Flow5_FRobot_1` - Robot 1 Operation
6. `ST10_Flow6_ToolCodeScan` - Tool Code Scan
7. `ST10_Flow7_CGlueing` - Gluing
8. `ST10_Flow8_FRobot_2` - Robot 2 Operation
11. `ST10_Flow11_A2TableScan` - A2 Table Scan
12. `ST10_Flow12_A2TableUnloading` - A2 Table Unload
14. `ST10_Flow14_B2Press` - B2 Press
15. `ST10_Flow15_FRobot_3` - Robot 3 Operation
21. `ST10_Flow21_HShaftLifting` - H Shaft Lifting
22. `ST10_Flow22_JMagnetLifting` - J Magnet Lifting
23. `ST10_Flow23_KReserveLifting` - K Reserve Lifting
24. `ST10_Flow24_LUnloadingTrans` - L Unloading Transfer
25. `ST10_Flow25_HShaftLoad&Unload` - H Shaft Load/Unload
26. `ST10_Flow26_JMagnetLoad&Unload` - J Magnet Load/Unload
27. `ST10_Flow27_KReserveLoad&Unload` - K Reserve Load/Unload
28. `ST10_Flow28_LUnloadingLoad&Unload` - L Unloading Load/Unload

### Manual Mode (`04_Manual/`)
| File | Purpose |
|------|---------|
| `ST10_Manual.xml` | Manual operation logic |

### Alarm Handling (`05_Alarm/`)
| File | Purpose |
|------|---------|
| `ST10_Alarm.xml` | Alarm management |
| `ST10_DeviceError.xml` | Device error handling |
| `ST10_GlobalError.xml` | Global error handling |

### Warning Handling (`06_Warning/`)
| File | Purpose |
|------|---------|
| `ST10_Warning.xml` | Warning management |
| `ST10_WarningDB.xml` | Warning data block |

### Tips (`07_Tip/`)
| File | Purpose |
|------|---------|
| `ST10_Tip.xml` | Tip management |
| `ST10_TipDB.xml` | Tip data block |

### Changeover (`08_ChangeOver/`)
| File | Purpose |
|------|---------|
| `ST10_ChangeOver.xml` | Changeover logic |
| `Parameter.xml` | Parameters |
| `ST10_RecipeDB.xml` | Recipe database |
| `ST10_RecipeDB_HMI.xml` | HMI recipe interface |
| `ST10_RecipeActiveDB.xml` | Active recipe DB |
| `MES/OP010_MES_RecipeDB.xml` | MES recipe DB |

### Cycle Time (`09_Count_CycleTime/`)
| File | Purpose |
|------|---------|
| `ST10_CountCycleTimeMain.xml` | Main cycle time counter |
| `ST10_CountCycleTimeMain_DB.xml` | Cycle time data block |
| `ST10_PMCountCycleTime.xml` | PM cycle time |

### Device Control (`10_Device/`)
| Folder | Device/Function |
|--------|-----------------|
| `01_Cylinder/` | Cylinders 1-100 (ST10Cylinder.xml + interfaces) |
| `03_SafetyGate/` | Safety gates 1-9 + Material gates 1-7 |
| `06_Stopper/` | Stopper control |
| `08_PressureAanlog/` | Pressure analog processing |
| `09_CuringOven/` | Curing oven control |
| `18_SR1000 Scan/` | Keyence SR1000 scanners (8 instances) |
| `21_IV3/` | Keyence IV3 vision sensors |
| `22_IAI/` | IAI servo axes (A1, A2, A3) |
| `23_Kistler/` | Kistler press systems (1 & 2) |
| `24_Robot/` | Kuka robots (1, 2, 3) |
| `25_V90/` | **V90 servo drives + TO_BasicPos technology** |
| `26_Stopper/` | Additional stopper control |
| `27_Pilz/` | Pilz safety system |
| `28_Gluing/` | Gluing system control |
| `29_NG/` | NG (Not Good) box control |
| `31_Motor_1/` | Motor controls 1-17 |

#### V90 Servo Technology Objects (`25_V90/`)
The V90 folder contains **2 different servo control technologies**:

**1. Standard V90 Position Control (fbV90Ctrl)**
| File | Purpose |
|------|---------|
| `V90_Servo.xml` | Main FB calling 4 servo instances (Servo_380A1..383A1) |
| `Servo.xml` | FC wrapper calling V90_Servo FB |
| `ServoV90_A1.xml` - `ServoV90_A4.xml` | Global DBs for servo data (In/Out structs) |
| `V90Servo_DB.xml` | Instance DB for V90_Servo FB |
| `V90_Standard/fbV90Ctrl.xml` | **Standard V90 control FB** - handles jog, auto, homing, position lists |
| `V90_Standard/SINA_POS.xml` | Siemens SINA_POS block for V90 |
| `V90_Standard/SINA_PARA_S.xml` | Siemens parameter access block |
| `V90_Standard/ServoCheck/` | Servo startup & position check |

**2. TO_BasicPos Technology Object (Motion Control) - NOT USED**
| File | Purpose |
|------|---------|
| `Z_NOT_USED/FB_GlueRotation_BasicPos.scl` | **TO_BasicPos-based FB** using `BasicPosControl` technology object for rotary table gluing - **NOT USED** |
| `FB_GlueRotationJob.scl` | Job controller for glue rotation using standard V90 interface |
| `Z_NOT_USED/FB_RotaryJobController.scl` | **TO-based rotary control** using `MC_Power` + `MC_MoveRelative` motion control blocks - **NOT USED** |
| `ServoV90_DeviceCtl.xml` | Device control logic |
| `Patch/` | Positioning order check patches |

**Key Difference:**
- `fbV90Ctrl` = Standard V90 telegram 111 positioning (ACTIVE/USED)
- `FB_GlueRotation_BasicPos` = Technology Object Basic Positioning (NOT USED - moved to Z_NOT_USED)
- `FB_RotaryJobController` = Full TO-based motion control (NOT USED - moved to Z_NOT_USED)

### MES Integration (`11_MES/`)
| File | Purpose |
|------|---------|
| `MES.xml` | Main MES FB |
| `MES_CheckControl.xml` | MES check control |
| `MES_CHeck.xml` / `MES Check_fb.xml` | MES check functions |
| `MES_CHeck_DB.xml` | MES check DB |
| `MEStoPLC.xml` | MES to PLC data |
| `PLCtoMES.xml` | PLC to MES data |
| `DT-Chars.xml` / `DT-Chars_DB.xml` | Data type char conversion |
| `Station1LoadData.xml` - `Station8UnLoadData.xml` | Station load/unload data |
| `Scanner1LoadData.xml` | Scanner load data |

### Part Data (`12_PartData/`)
| File | Purpose |
|------|---------|
| `ST10_PartData.xml` | Part data management |
| `PartData_Interface_DB.xml` | Part data interface |
| `PartDataManage_Part1_DB.xml` - `PartDataManage_Part4_DB.xml` | Part data for parts 1-4 |

---

## 📋 STANDARDS & GUIDELINES

### Naming Conventions
| Prefix | Meaning | Example |
|--------|---------|---------|
| `ST10_` | Station 10 blocks | `ST10_Main.xml` |
| `ST10_FlowX_` | Process flow step X | `ST10_Flow1_A1TableScan.xml` |
| `FB_` | Function Block | `FB_Stopper.xml` |
| `FC_` | Function Call | `FC_Save_Values_Final.xml` |
| `DB_` | Data Block | `DB_MES_Monitoring.xml` |
| `UDT_` | User Data Type | `UDT_RECIPE.xml` |
| `iDB/` | Instance Data Blocks folder | - |

### File Extensions
| Extension | Type |
|-----------|------|
| `.xml` | TIA Portal exported block (standard) |
| `.scl` | Structured Control Language (Siemens) |
| `.db` | Database file |

### Folder Numbering Convention
| Range | Category |
|-------|----------|
| `00-09` | System/Organization |
| `01-09` | Organization Blocks |
| `10-99` | Function Blocks |
| `100-199` | User Functions |
| `200-299` | Devices |
| `500+` | Custom/User |

---

## 🔍 WHERE TO ADD NEW COMPONENTS

### New Device Type (UDT)
📂 `PLC data types/03 FunctionBlocks/`  
Create folder: `[NNN] [DeviceName]/`  
Add UDT in: `[NNN].1 UDT/[Name].xml`

### New Device Instance
📂 `Program blocks/OP010/10_Device/`  
Create folder: `[NN]_[DeviceName]/`  
Add control FB and instance DBs

### New Process Flow Step
📂 `Program blocks/OP010/03_Auto/`  
Add to appropriate subfolder (A1, A2, B_Press, etc.)  
Create: `ST10_Flow[X]_[Description].xml`  
Create iDB: `M_iDB/ST10_Flow[X]_[Description]_iDB.xml`

### New Recipe Parameter
📂 `PLC data types/_PARAMETERS_RECIPES/`  
Add UDT definition  
Update: `UDT_RECIPE.xml`

### New MES Data Exchange
📂 `Program blocks/OP010/11_MES/`  
Create: `Station[X]LoadData.xml` / `Station[X]UnLoadData.xml`

### New Constant/Enum
📂 `PLC tags/constant/`  
Create or modify appropriate XML file

---

## ⚠️ NOTES

- **OLD SHIT folders** contain deprecated/legacy code - do not use for new development
- **Z_Reserve folder** is for temporary/commissioning blocks
- **iDB folders** contain instance data blocks (automatically generated instances of FBs)
- Flow numbers are NOT sequential (gaps exist: 9, 10, 13, 16-20, etc.)
- Multiple file formats exist: `.xml` (TIA exports), `.scl` (source code)

> **Generated:** 2026-02-01  
> **Project:** OP10 Station PLC Code  
> **Purpose:** Siemens TIA Portal PLC Project for Manufacturing Station

---

## 📁 ROOT DIRECTORY STRUCTURE

```
📂 OP10/
├── 📁 DB_ALL_PROCESS_PARAMETERS.db          # Process parameters database
├── 📁 GlueningRotaryTable.db                # Gluing rotary table database
├── 📁 DOKUMENTACE/                          # Documentation folder
├── 📁 PLC data types/                       # UDTs (User Data Types)
├── 📁 PLC tags/                             # PLC tag tables
└── 📁 Program blocks/                       # Main program logic (FC, FB, DB, OB)
```

---

## 📊 PLC DATA TYPES (`PLC data types/`)

User-Defined Types (UDTs) organized by category:

### System Types (`00 Sys/`)
| File | Purpose |
|------|---------|
| `RCS_CountCycleTime_V1.xml` | Cycle time counting structure |
| `RCS_PMInterface_V1.xml` | PM Interface structure |
| `RCS_SysAlarmWarning_V1.xml` | System alarm/warning structure |
| `RCS_SysAuto_V1.xml` | Auto mode structure |
| `RCS_SysCmd_V1.xml` | System commands structure |
| `RCS_SysComInterface_V1.xml` | Communication interface |
| `RCS_SysCount_V1.xml` | System counter structure |
| `RCS_SysCycleTime_V1.xml` | System cycle time |
| `RCS_SysManual_V1.xml` | Manual mode structure |
| `RCS_SysSafety_V1.xml` | Safety system structure |
| `RCS_SysStatus_V1.xml` | System status structure |

### Function Block Types (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `101 Cylinder/` | Cylinder control UDT (`Cyl.xml`) |
| `102 SafetyGate/` | Safety gate UDT (`SafetyGateUDT.xml`) |
| `105 MaterialGate/` | Material gate UDT |
| `201 Stopper/` | Stopper UDT (`ST_Stopper.xml`, `UDT_Stopper_FB.xml`) |
| `202 Conveyer_Line/` | Motor control UDT (`Motor_Control.xml`) |
| `211 ATEQ LeakTest/` | ATEQ leak test visual type |
| `212 Analog/` | General analog UDT (`ST_GeneralAnalog.xml`) |

### User Types (`500 User/`)
| File | Purpose |
|------|---------|
| `ATEQRecipe.xml` | ATEQ recipe structure |
| `Check.xml` | Check data structure |
| `PresserRecipe.xml` | Presser recipe structure |
| `StaProcessData.xml` | Station process data |
| `UDT_LabelFeeder.xml` | Label feeder UDT |
| `UDT_Marking CharToASCII.xml` | Marking char conversion |
| `UDT_Marking StringToChar.xml` | Marking string conversion |
| `UDT_StaProcessData.xml` | Station process data UDT |
| `100 FixtureCheck/` | Fixture check UDT |
| `104 PartDataManage/` | Part data management UDTs |
| `210 Recipe/` | Recipe axis UDT |

### External Device Types
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner (HMI, Input, Output types) |
| `LXL/` | IAI Servo, Kistler, Kuka Robot types |
| `MES/` | MES monitoring types |
| `ProcessData/` | Process data types |
| `RCS-PPK/` | Stopper interface types |

### Recipe Parameters (`_PARAMETERS_RECIPES/`)
| File | Purpose |
|------|---------|
| `UDT_Gripper_Fixture_Codes.xml` | Gripper/fixture codes |
| `UDT_IAI_Axis_Positions.xml` | IAI axis positions |
| `UDT_Motion_Point_IAI.xml` | IAI motion points |
| `UDT_Motion_Point_V90.xml` | V90 motion points |
| `UDT_OP10_Recipe_type.xml` | OP10 recipe type |
| `UDT_RECIPE.xml` | Main recipe structure |
| `UDT_Recipe_ATEQ.xml` | ATEQ recipe |
| `UDT_Recipe_PressCurve.xml` | Press curve recipe |
| `UDT_V90_Axis_Positions.xml` | V90 axis positions |

### Enums
| File | Purpose |
|------|---------|
| `NGDoorState_Enum.xml` | NG Door state enumeration |
| `PartStatus_Enum.xml` | Part status enumeration |
| `UDT_OP10_Recipe_diff.xml` | Recipe difference structure |

---

## 🏷️ PLC TAGS (`PLC tags/`)

### Tag Tables
| File/Folder | Content |
|-------------|---------|
| `Default variable table.xml` | Default PLC tags |
| `NGSensor.xml` | NG sensor tags |
| `STEP7 classic symbols.xml` | STEP7 classic symbols |
| `constant/` | Constants (Flow, IV3, Lifting, Marking, MES codes, PartType, ProcessResult, RFID, TestResult, partstatus) |
| `IO/` | I/O tags (PLC DI/DQ, Remote IO DI/DO) |

---

## 🔧 PROGRAM BLOCKS (`Program blocks/`)

### Organization Blocks (`01_OB/`)
| File | Purpose |
|------|---------|
| `01_OB1.xml` | Main cyclic OB |
| `02_Warm Restart.xml` | Warm restart OB |
| `03_CYC_INT2.xml` | Cyclic interrupt 2 |
| `04_CYC_INT5.xml` | Cyclic interrupt 5 |
| `05_MOD_ERR.xml` | Module error OB |
| `07_CYCL_FLT.xml` | Cycle fault OB |
| `08_HW_INT0.xml` | Hardware interrupt 0 |
| `09_IO_FLT1.xml` | I/O fault OB |
| `11_PROG_ERR.xml` | Program error OB |
| `12_RACK_FLT.xml` | Rack fault OB |

### System Functions (`00 Sys/`)
| File | Purpose |
|------|---------|
| `CheckData.xml` | Data checking |
| `Count_CycleTime.xml` | Cycle time counting |
| `Count_CycleTime_V3.xml` | Cycle time counting v3 |
| `SysFlowCtrlGraph.xml` | Flow control graph |
| `SystemMode.xml` | System mode management |

### Communication (`02_Comm/`)
| Folder | Content |
|--------|---------|
| `03-Diagnosis/` | Diagnostic FBs |
| `04-ChangeOver/` | Changeover logic |
| `06_SysDataBlock&Function/` | System data/functions |

### Reusable Function Blocks (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `003 Tower_Lamp/` | Tower lamp control (`FB_Tower_4Lamp.xml`) |
| `101 Cylinder/` | Cylinder control (`CylinderCtrl_V2.xml`, `CylinderModule_V2.xml`) |
| `102 SafetyGate/` | Safety gate (`SafetyGate.xml`) |
| `201 Stopper/` | Stopper control (`FB_Stopper.xml`) |
| `202 Conveyer_Line/` | Motor control (`MotorContro.xml`) |
| `999 Base/` | Base functions (`FB_Next.xml`) |

### Device-Specific (`03_Device/`)
| Folder | Content |
|--------|---------|
| `102 SafetyGate/` | Material gate |
| `211 ATEQ LeakTest/` | ATEQ F620 leak test |
| `212 Analog/` | Analog processing |

### User Functions (`500 User/`)
| Folder | Content |
|--------|---------|
| `100 FixtureCheck/` | Fixture checking |
| `104 PartDataManage/` | Part data management |

### External Device Libraries
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner control |
| `RCS-PPK/` | Stopper control library |

### Special Folders
| Folder | Purpose |
|--------|---------|
| `__MES MONITORING/` | MES monitoring FBs |
| `__PARAMETERS/` | Recipe/parameter handling |
| `Z_Reserve/` | Reserved/commissioning blocks |

---

## 🏭 STATION OP010 (`Program blocks/OP010/`)

Main station logic organized by function:

### Main (`00_Main/`)
| File | Purpose |
|------|---------|
| `ST10_Main.xml` | Main station FB |
| `ST10_GeneralData.xml` | General data DB |
| `Station_Sys.xml` | Station system FB |
| `iDB/ST10_SystemModeFB_iDB.xml` | System mode instance DB |

### Input Processing (`01_Input/`)
| File | Purpose |
|------|---------|
| `ST10_Input.xml` | Input processing |
| `ST10_SysInput.xml` | System input processing |

### Output Processing (`02_Output/`)
| File | Purpose |
|------|---------|
| `ST10_Output.xml` | Output processing |
| `ST10_SysOutput.xml` | System output processing |
| `ST10_FB_Tower_4Lamp_DB.xml` | Tower lamp instance DB |

### Automatic Mode (`03_Auto/`)
| Folder/File | Purpose |
|-------------|---------|
| `AutoProcessControl.xml` | Auto process control |
| `AutoProcessData.xml` | Auto process data |
| `AutoProcessData_Buffer.xml` | Process data buffer |
| `PalletRelease.xml` | Pallet release logic |
| `ST10_PM.xml` | PM interface |
| `TON.xml` | Timer functions |
| `01ChangeOver/` | Changeover flows |
| `A1_TableLoad&Scan/` | Table A1 loading & scanning |
| `A2_TableLoad&Scan/` | Table A2 loading & scanning |
| `B_Press/` | Press operations (B1, B2) |
| `C_Glue/` | Gluing operation |
| `F_Robot/` | Robot operations (1, 2, 3) |
| `H_ShaftLifting&Load&Unload/` | Shaft lifting operations |
| `J_MagnetLifting&Load&Unload/` | Magnet lifting operations |
| `L_Unload/` | Unloading operations |
| `M_iDB/` | Instance DBs for all flows |
| `HMI/` | HMI interface blocks |

**Flow Sequence:**
1. `ST10_Flow1_A1TableScan` - A1 Table Scan
2. `ST10_Flow2_A1TableUnloading` - A1 Table Unload
3. `ST10_Flow3_A1RotaryShaftScan` - Rotary Shaft Scan
4. `ST10_Flow4_B1Press` - B1 Press
5. `ST10_Flow5_FRobot_1` - Robot 1 Operation
6. `ST10_Flow6_ToolCodeScan` - Tool Code Scan
7. `ST10_Flow7_CGlueing` - Gluing
8. `ST10_Flow8_FRobot_2` - Robot 2 Operation
11. `ST10_Flow11_A2TableScan` - A2 Table Scan
12. `ST10_Flow12_A2TableUnloading` - A2 Table Unload
14. `ST10_Flow14_B2Press` - B2 Press
15. `ST10_Flow15_FRobot_3` - Robot 3 Operation
21. `ST10_Flow21_HShaftLifting` - H Shaft Lifting
22. `ST10_Flow22_JMagnetLifting` - J Magnet Lifting
23. `ST10_Flow23_KReserveLifting` - K Reserve Lifting
24. `ST10_Flow24_LUnloadingTrans` - L Unloading Transfer
25. `ST10_Flow25_HShaftLoad&Unload` - H Shaft Load/Unload
26. `ST10_Flow26_JMagnetLoad&Unload` - J Magnet Load/Unload
27. `ST10_Flow27_KReserveLoad&Unload` - K Reserve Load/Unload
28. `ST10_Flow28_LUnloadingLoad&Unload` - L Unloading Load/Unload

### Manual Mode (`04_Manual/`)
| File | Purpose |
|------|---------|
| `ST10_Manual.xml` | Manual operation logic |

### Alarm Handling (`05_Alarm/`)
| File | Purpose |
|------|---------|
| `ST10_Alarm.xml` | Alarm management |
| `ST10_DeviceError.xml` | Device error handling |
| `ST10_GlobalError.xml` | Global error handling |

### Warning Handling (`06_Warning/`)
| File | Purpose |
|------|---------|
| `ST10_Warning.xml` | Warning management |
| `ST10_WarningDB.xml` | Warning data block |

### Tips (`07_Tip/`)
| File | Purpose |
|------|---------|
| `ST10_Tip.xml` | Tip management |
| `ST10_TipDB.xml` | Tip data block |

### Changeover (`08_ChangeOver/`)
| File | Purpose |
|------|---------|
| `ST10_ChangeOver.xml` | Changeover logic |
| `Parameter.xml` | Parameters |
| `ST10_RecipeDB.xml` | Recipe database |
| `ST10_RecipeDB_HMI.xml` | HMI recipe interface |
| `ST10_RecipeActiveDB.xml` | Active recipe DB |
| `MES/OP010_MES_RecipeDB.xml` | MES recipe DB |

### Cycle Time (`09_Count_CycleTime/`)
| File | Purpose |
|------|---------|
| `ST10_CountCycleTimeMain.xml` | Main cycle time counter |
| `ST10_CountCycleTimeMain_DB.xml` | Cycle time data block |
| `ST10_PMCountCycleTime.xml` | PM cycle time |

### Device Control (`10_Device/`)
| Folder | Device/Function |
|--------|-----------------|
| `01_Cylinder/` | Cylinders 1-100 (ST10Cylinder.xml + interfaces) |
| `03_SafetyGate/` | Safety gates 1-9 + Material gates 1-7 |
| `06_Stopper/` | Stopper control |
| `08_PressureAanlog/` | Pressure analog processing |
| `09_CuringOven/` | Curing oven control |
| `18_SR1000 Scan/` | Keyence SR1000 scanners (8 instances) |
| `21_IV3/` | Keyence IV3 vision sensors |
| `22_IAI/` | IAI servo axes (A1, A2, A3) |
| `23_Kistler/` | Kistler press systems (1 & 2) |
| `24_Robot/` | Kuka robots (1, 2, 3) |
| `25_V90/` | V90 servo drives (A1-A4) |
| `26_Stopper/` | Additional stopper control |
| `27_Pilz/` | Pilz safety system |
| `28_Gluing/` | Gluing system control |
| `29_NG/` | NG (Not Good) box control |
| `31_Motor_1/` | Motor controls 1-17 |

### MES Integration (`11_MES/`)
| File | Purpose |
|------|---------|
| `MES.xml` | Main MES FB |
| `MES_CheckControl.xml` | MES check control |
| `MES_CHeck.xml` / `MES Check_fb.xml` | MES check functions |
| `MES_CHeck_DB.xml` | MES check DB |
| `MEStoPLC.xml` | MES to PLC data |
| `PLCtoMES.xml` | PLC to MES data |
| `DT-Chars.xml` / `DT-Chars_DB.xml` | Data type char conversion |
| `Station1LoadData.xml` - `Station8UnLoadData.xml` | Station load/unload data |
| `Scanner1LoadData.xml` | Scanner load data |

### Part Data (`12_PartData/`)
| File | Purpose |
|------|---------|
| `ST10_PartData.xml` | Part data management |
| `PartData_Interface_DB.xml` | Part data interface |
| `PartDataManage_Part1_DB.xml` - `PartDataManage_Part4_DB.xml` | Part data for parts 1-4 |

---

## 📋 STANDARDS & GUIDELINES

### Naming Conventions
| Prefix | Meaning | Example |
|--------|---------|---------|
| `ST10_` | Station 10 blocks | `ST10_Main.xml` |
| `ST10_FlowX_` | Process flow step X | `ST10_Flow1_A1TableScan.xml` |
| `FB_` | Function Block | `FB_Stopper.xml` |
| `FC_` | Function Call | `FC_Save_Values_Final.xml` |
| `DB_` | Data Block | `DB_MES_Monitoring.xml` |
| `UDT_` | User Data Type | `UDT_RECIPE.xml` |
| `iDB/` | Instance Data Blocks folder | - |

### File Extensions
| Extension | Type |
|-----------|------|
| `.xml` | TIA Portal exported block (standard) |
| `.scl` | Structured Control Language (Siemens) |
| `.db` | Database file |

### Folder Numbering Convention
| Range | Category |
|-------|----------|
| `00-09` | System/Organization |
| `01-09` | Organization Blocks |
| `10-99` | Function Blocks |
| `100-199` | User Functions |
| `200-299` | Devices |
| `500+` | Custom/User |

---

## 🔍 WHERE TO ADD NEW COMPONENTS

### New Device Type (UDT)
📂 `PLC data types/03 FunctionBlocks/`  
Create folder: `[NNN] [DeviceName]/`  
Add UDT in: `[NNN].1 UDT/[Name].xml`

### New Device Instance
📂 `Program blocks/OP010/10_Device/`  
Create folder: `[NN]_[DeviceName]/`  
Add control FB and instance DBs

### New Process Flow Step
📂 `Program blocks/OP010/03_Auto/`  
Add to appropriate subfolder (A1, A2, B_Press, etc.)  
Create: `ST10_Flow[X]_[Description].xml`  
Create iDB: `M_iDB/ST10_Flow[X]_[Description]_iDB.xml`

### New Recipe Parameter
📂 `PLC data types/_PARAMETERS_RECIPES/`  
Add UDT definition  
Update: `UDT_RECIPE.xml`

### New MES Data Exchange
📂 `Program blocks/OP010/11_MES/`  
Create: `Station[X]LoadData.xml` / `Station[X]UnLoadData.xml`

### New Constant/Enum
📂 `PLC tags/constant/`  
Create or modify appropriate XML file

---

## ⚠️ NOTES

- **OLD SHIT folders** contain deprecated/legacy code - do not use for new development
- **Z_Reserve folder** is for temporary/commissioning blocks
- **iDB folders** contain instance data blocks (automatically generated instances of FBs)
- Flow numbers are NOT sequential (gaps exist: 9, 10, 13, 16-20, etc.)
- Multiple file formats exist: `.xml` (TIA exports), `.scl` (source code)


> **Generated:** 2026-02-01  
> **Project:** OP10 Station PLC Code  
> **Purpose:** Siemens TIA Portal PLC Project for Manufacturing Station

---

## 📁 ROOT DIRECTORY STRUCTURE

```
📂 OP10/
├── 📁 DB_ALL_PROCESS_PARAMETERS.db          # Process parameters database
├── 📁 GlueningRotaryTable.db                # Gluing rotary table database
├── 📁 DOKUMENTACE/                          # Documentation folder
├── 📁 PLC data types/                       # UDTs (User Data Types)
├── 📁 PLC tags/                             # PLC tag tables
└── 📁 Program blocks/                       # Main program logic (FC, FB, DB, OB)
```

---

## 📊 PLC DATA TYPES (`PLC data types/`)

User-Defined Types (UDTs) organized by category:

### System Types (`00 Sys/`)
| File | Purpose |
|------|---------|
| `RCS_CountCycleTime_V1.xml` | Cycle time counting structure |
| `RCS_PMInterface_V1.xml` | PM Interface structure |
| `RCS_SysAlarmWarning_V1.xml` | System alarm/warning structure |
| `RCS_SysAuto_V1.xml` | Auto mode structure |
| `RCS_SysCmd_V1.xml` | System commands structure |
| `RCS_SysComInterface_V1.xml` | Communication interface |
| `RCS_SysCount_V1.xml` | System counter structure |
| `RCS_SysCycleTime_V1.xml` | System cycle time |
| `RCS_SysManual_V1.xml` | Manual mode structure |
| `RCS_SysSafety_V1.xml` | Safety system structure |
| `RCS_SysStatus_V1.xml` | System status structure |

### Function Block Types (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `101 Cylinder/` | Cylinder control UDT (`Cyl.xml`) |
| `102 SafetyGate/` | Safety gate UDT (`SafetyGateUDT.xml`) |
| `105 MaterialGate/` | Material gate UDT |
| `201 Stopper/` | Stopper UDT (`ST_Stopper.xml`, `UDT_Stopper_FB.xml`) |
| `202 Conveyer_Line/` | Motor control UDT (`Motor_Control.xml`) |
| `211 ATEQ LeakTest/` | ATEQ leak test visual type |
| `212 Analog/` | General analog UDT (`ST_GeneralAnalog.xml`) |

### User Types (`500 User/`)
| File | Purpose |
|------|---------|
| `ATEQRecipe.xml` | ATEQ recipe structure |
| `Check.xml` | Check data structure |
| `PresserRecipe.xml` | Presser recipe structure |
| `StaProcessData.xml` | Station process data |
| `UDT_LabelFeeder.xml` | Label feeder UDT |
| `UDT_Marking CharToASCII.xml` | Marking char conversion |
| `UDT_Marking StringToChar.xml` | Marking string conversion |
| `UDT_StaProcessData.xml` | Station process data UDT |
| `100 FixtureCheck/` | Fixture check UDT |
| `104 PartDataManage/` | Part data management UDTs |
| `210 Recipe/` | Recipe axis UDT |

### External Device Types
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner (HMI, Input, Output types) |
| `LXL/` | IAI Servo, Kistler, Kuka Robot types |
| `MES/` | MES monitoring types |
| `ProcessData/` | Process data types |
| `RCS-PPK/` | Stopper interface types |

### Recipe Parameters (`_PARAMETERS_RECIPES/`)
| File | Purpose |
|------|---------|
| `UDT_Gripper_Fixture_Codes.xml` | Gripper/fixture codes |
| `UDT_IAI_Axis_Positions.xml` | IAI axis positions |
| `UDT_Motion_Point_IAI.xml` | IAI motion points |
| `UDT_Motion_Point_V90.xml` | V90 motion points |
| `UDT_OP10_Recipe_type.xml` | OP10 recipe type |
| `UDT_RECIPE.xml` | Main recipe structure |
| `UDT_Recipe_ATEQ.xml` | ATEQ recipe |
| `UDT_Recipe_PressCurve.xml` | Press curve recipe |
| `UDT_V90_Axis_Positions.xml` | V90 axis positions |

### Enums
| File | Purpose |
|------|---------|
| `NGDoorState_Enum.xml` | NG Door state enumeration |
| `PartStatus_Enum.xml` | Part status enumeration |
| `UDT_OP10_Recipe_diff.xml` | Recipe difference structure |

---

## 🏷️ PLC TAGS (`PLC tags/`)

### Tag Tables
| File/Folder | Content |
|-------------|---------|
| `Default variable table.xml` | Default PLC tags |
| `NGSensor.xml` | NG sensor tags |
| `STEP7 classic symbols.xml` | STEP7 classic symbols |
| `constant/` | Constants (Flow, IV3, Lifting, Marking, MES codes, PartType, ProcessResult, RFID, TestResult, partstatus) |
| `IO/` | I/O tags (PLC DI/DQ, Remote IO DI/DO) |

---

## 🔧 PROGRAM BLOCKS (`Program blocks/`)

### Organization Blocks (`01_OB/`)
| File | Purpose |
|------|---------|
| `01_OB1.xml` | Main cyclic OB |
| `02_Warm Restart.xml` | Warm restart OB |
| `03_CYC_INT2.xml` | Cyclic interrupt 2 |
| `04_CYC_INT5.xml` | Cyclic interrupt 5 |
| `05_MOD_ERR.xml` | Module error OB |
| `07_CYCL_FLT.xml` | Cycle fault OB |
| `08_HW_INT0.xml` | Hardware interrupt 0 |
| `09_IO_FLT1.xml` | I/O fault OB |
| `11_PROG_ERR.xml` | Program error OB |
| `12_RACK_FLT.xml` | Rack fault OB |

### System Functions (`00 Sys/`)
| File | Purpose |
|------|---------|
| `CheckData.xml` | Data checking |
| `Count_CycleTime.xml` | Cycle time counting |
| `Count_CycleTime_V3.xml` | Cycle time counting v3 |
| `SysFlowCtrlGraph.xml` | Flow control graph |
| `SystemMode.xml` | System mode management |

### Communication (`02_Comm/`)
| Folder | Content |
|--------|---------|
| `03-Diagnosis/` | Diagnostic FBs |
| `04-ChangeOver/` | Changeover logic |
| `06_SysDataBlock&Function/` | System data/functions |

### Reusable Function Blocks (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `003 Tower_Lamp/` | Tower lamp control (`FB_Tower_4Lamp.xml`) |
| `101 Cylinder/` | Cylinder control (`CylinderCtrl_V2.xml`, `CylinderModule_V2.xml`) |
| `102 SafetyGate/` | Safety gate (`SafetyGate.xml`) |
| `201 Stopper/` | Stopper control (`FB_Stopper.xml`) |
| `202 Conveyer_Line/` | Motor control (`MotorContro.xml`) |
| `999 Base/` | Base functions (`FB_Next.xml`) |

### Device-Specific (`03_Device/`)
| Folder | Content |
|--------|---------|
| `102 SafetyGate/` | Material gate |
| `211 ATEQ LeakTest/` | ATEQ F620 leak test |
| `212 Analog/` | Analog processing |

### User Functions (`500 User/`)
| Folder | Content |
|--------|---------|
| `100 FixtureCheck/` | Fixture checking |
| `104 PartDataManage/` | Part data management |

### External Device Libraries
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner control |
| `RCS-PPK/` | Stopper control library |

### Special Folders
| Folder | Purpose |
|--------|---------|
| `__MES MONITORING/` | MES monitoring FBs |
| `__PARAMETERS/` | Recipe/parameter handling |
| `Z_Reserve/` | Reserved/commissioning blocks |

---

## 🏭 STATION OP010 (`Program blocks/OP010/`)

Main station logic organized by function:

### Main (`00_Main/`)
| File | Purpose |
|------|---------|
| `ST10_Main.xml` | Main station FB |
| `ST10_GeneralData.xml` | General data DB |
| `Station_Sys.xml` | Station system FB |
| `iDB/ST10_SystemModeFB_iDB.xml` | System mode instance DB |

### Input Processing (`01_Input/`)
| File | Purpose |
|------|---------|
| `ST10_Input.xml` | Input processing |
| `ST10_SysInput.xml` | System input processing |

### Output Processing (`02_Output/`)
| File | Purpose |
|------|---------|
| `ST10_Output.xml` | Output processing |
| `ST10_SysOutput.xml` | System output processing |
| `ST10_FB_Tower_4Lamp_DB.xml` | Tower lamp instance DB |

### Automatic Mode (`03_Auto/`)
| Folder/File | Purpose |
|-------------|---------|
| `AutoProcessControl.xml` | Auto process control |
| `AutoProcessData.xml` | Auto process data |
| `AutoProcessData_Buffer.xml` | Process data buffer |
| `PalletRelease.xml` | Pallet release logic |
| `ST10_PM.xml` | PM interface |
| `TON.xml` | Timer functions |
| `01ChangeOver/` | Changeover flows |
| `A1_TableLoad&Scan/` | Table A1 loading & scanning |
| `A2_TableLoad&Scan/` | Table A2 loading & scanning |
| `B_Press/` | Press operations (B1, B2) |
| `C_Glue/` | Gluing operation |
| `F_Robot/` | Robot operations (1, 2, 3) |
| `H_ShaftLifting&Load&Unload/` | Shaft lifting operations |
| `J_MagnetLifting&Load&Unload/` | Magnet lifting operations |
| `L_Unload/` | Unloading operations |
| `M_iDB/` | Instance DBs for all flows |
| `HMI/` | HMI interface blocks |

**Flow Sequence:**
1. `ST10_Flow1_A1TableScan` - A1 Table Scan
2. `ST10_Flow2_A1TableUnloading` - A1 Table Unload
3. `ST10_Flow3_A1RotaryShaftScan` - Rotary Shaft Scan
4. `ST10_Flow4_B1Press` - B1 Press
5. `ST10_Flow5_FRobot_1` - Robot 1 Operation
6. `ST10_Flow6_ToolCodeScan` - Tool Code Scan
7. `ST10_Flow7_CGlueing` - Gluing
8. `ST10_Flow8_FRobot_2` - Robot 2 Operation
11. `ST10_Flow11_A2TableScan` - A2 Table Scan
12. `ST10_Flow12_A2TableUnloading` - A2 Table Unload
14. `ST10_Flow14_B2Press` - B2 Press
15. `ST10_Flow15_FRobot_3` - Robot 3 Operation
21. `ST10_Flow21_HShaftLifting` - H Shaft Lifting
22. `ST10_Flow22_JMagnetLifting` - J Magnet Lifting
23. `ST10_Flow23_KReserveLifting` - K Reserve Lifting
24. `ST10_Flow24_LUnloadingTrans` - L Unloading Transfer
25. `ST10_Flow25_HShaftLoad&Unload` - H Shaft Load/Unload
26. `ST10_Flow26_JMagnetLoad&Unload` - J Magnet Load/Unload
27. `ST10_Flow27_KReserveLoad&Unload` - K Reserve Load/Unload
28. `ST10_Flow28_LUnloadingLoad&Unload` - L Unloading Load/Unload

### Manual Mode (`04_Manual/`)
| File | Purpose |
|------|---------|
| `ST10_Manual.xml` | Manual operation logic |

### Alarm Handling (`05_Alarm/`)
| File | Purpose |
|------|---------|
| `ST10_Alarm.xml` | Alarm management |
| `ST10_DeviceError.xml` | Device error handling |
| `ST10_GlobalError.xml` | Global error handling |

### Warning Handling (`06_Warning/`)
| File | Purpose |
|------|---------|
| `ST10_Warning.xml` | Warning management |
| `ST10_WarningDB.xml` | Warning data block |

### Tips (`07_Tip/`)
| File | Purpose |
|------|---------|
| `ST10_Tip.xml` | Tip management |
| `ST10_TipDB.xml` | Tip data block |

### Changeover (`08_ChangeOver/`)
| File | Purpose |
|------|---------|
| `ST10_ChangeOver.xml` | Changeover logic |
| `Parameter.xml` | Parameters |
| `ST10_RecipeDB.xml` | Recipe database |
| `ST10_RecipeDB_HMI.xml` | HMI recipe interface |
| `ST10_RecipeActiveDB.xml` | Active recipe DB |
| `MES/OP010_MES_RecipeDB.xml` | MES recipe DB |

### Cycle Time (`09_Count_CycleTime/`)
| File | Purpose |
|------|---------|
| `ST10_CountCycleTimeMain.xml` | Main cycle time counter |
| `ST10_CountCycleTimeMain_DB.xml` | Cycle time data block |
| `ST10_PMCountCycleTime.xml` | PM cycle time |

### Device Control (`10_Device/`)
| Folder | Device/Function |
|--------|-----------------|
| `01_Cylinder/` | Cylinders 1-100 (ST10Cylinder.xml + interfaces) |
| `03_SafetyGate/` | Safety gates 1-9 + Material gates 1-7 |
| `06_Stopper/` | Stopper control |
| `08_PressureAanlog/` | Pressure analog processing |
| `09_CuringOven/` | Curing oven control |
| `18_SR1000 Scan/` | Keyence SR1000 scanners (8 instances) |
| `21_IV3/` | Keyence IV3 vision sensors |
| `22_IAI/` | IAI servo axes (A1, A2, A3) |
| `23_Kistler/` | Kistler press systems (1 & 2) |
| `24_Robot/` | Kuka robots (1, 2, 3) |
| `25_V90/` | **V90 servo drives + TO_BasicPos technology** |
| `26_Stopper/` | Additional stopper control |
| `27_Pilz/` | Pilz safety system |
| `28_Gluing/` | Gluing system control |
| `29_NG/` | NG (Not Good) box control |
| `31_Motor_1/` | Motor controls 1-17 |

#### V90 Servo Technology Objects (`25_V90/`)
The V90 folder contains **2 different servo control technologies**:

**1. Standard V90 Position Control (fbV90Ctrl)**
| File | Purpose |
|------|---------|
| `V90_Servo.xml` | Main FB calling 4 servo instances (Servo_380A1..383A1) |
| `Servo.xml` | FC wrapper calling V90_Servo FB |
| `ServoV90_A1.xml` - `ServoV90_A4.xml` | Global DBs for servo data (In/Out structs) |
| `V90Servo_DB.xml` | Instance DB for V90_Servo FB |
| `V90_Standard/fbV90Ctrl.xml` | **Standard V90 control FB** - handles jog, auto, homing, position lists |
| `V90_Standard/SINA_POS.xml` | Siemens SINA_POS block for V90 |
| `V90_Standard/SINA_PARA_S.xml` | Siemens parameter access block |
| `V90_Standard/ServoCheck/` | Servo startup & position check |

**2. TO_BasicPos Technology Object (Motion Control)**
| File | Purpose |
|------|---------|
| `FB_GlueRotation_BasicPos.scl` | **TO_BasicPos-based FB** using `BasicPosControl` technology object for rotary table gluing |
| `FB_GlueRotationJob.scl` | Job controller for glue rotation using standard V90 interface |
| `FB_RotaryJobController.scl` | **TO-based rotary control** using `MC_Power` + `MC_MoveRelative` motion control blocks |
| `ServoV90_DeviceCtl.xml` | Device control logic |
| `Patch/` | Positioning order check patches |

**Key Difference:**
- `fbV90Ctrl` = Standard V90 telegram 111 positioning (legacy)
- `FB_GlueRotation_BasicPos` = Technology Object Basic Positioning (modern, uses `BasicPosControl`)
- `FB_RotaryJobController` = Full TO-based motion control (`MC_Power`, `MC_MoveRelative`)

### MES Integration (`11_MES/`)
| File | Purpose |
|------|---------|
| `MES.xml` | Main MES FB |
| `MES_CheckControl.xml` | MES check control |
| `MES_CHeck.xml` / `MES Check_fb.xml` | MES check functions |
| `MES_CHeck_DB.xml` | MES check DB |
| `MEStoPLC.xml` | MES to PLC data |
| `PLCtoMES.xml` | PLC to MES data |
| `DT-Chars.xml` / `DT-Chars_DB.xml` | Data type char conversion |
| `Station1LoadData.xml` - `Station8UnLoadData.xml` | Station load/unload data |
| `Scanner1LoadData.xml` | Scanner load data |

### Part Data (`12_PartData/`)
| File | Purpose |
|------|---------|
| `ST10_PartData.xml` | Part data management |
| `PartData_Interface_DB.xml` | Part data interface |
| `PartDataManage_Part1_DB.xml` - `PartDataManage_Part4_DB.xml` | Part data for parts 1-4 |

---

## 📋 STANDARDS & GUIDELINES

### Naming Conventions
| Prefix | Meaning | Example |
|--------|---------|---------|
| `ST10_` | Station 10 blocks | `ST10_Main.xml` |
| `ST10_FlowX_` | Process flow step X | `ST10_Flow1_A1TableScan.xml` |
| `FB_` | Function Block | `FB_Stopper.xml` |
| `FC_` | Function Call | `FC_Save_Values_Final.xml` |
| `DB_` | Data Block | `DB_MES_Monitoring.xml` |
| `UDT_` | User Data Type | `UDT_RECIPE.xml` |
| `iDB/` | Instance Data Blocks folder | - |

### File Extensions
| Extension | Type |
|-----------|------|
| `.xml` | TIA Portal exported block (standard) |
| `.scl` | Structured Control Language (Siemens) |
| `.db` | Database file |

### Folder Numbering Convention
| Range | Category |
|-------|----------|
| `00-09` | System/Organization |
| `01-09` | Organization Blocks |
| `10-99` | Function Blocks |
| `100-199` | User Functions |
| `200-299` | Devices |
| `500+` | Custom/User |

---

## 🔍 WHERE TO ADD NEW COMPONENTS

### New Device Type (UDT)
📂 `PLC data types/03 FunctionBlocks/`  
Create folder: `[NNN] [DeviceName]/`  
Add UDT in: `[NNN].1 UDT/[Name].xml`

### New Device Instance
📂 `Program blocks/OP010/10_Device/`  
Create folder: `[NN]_[DeviceName]/`  
Add control FB and instance DBs

### New Process Flow Step
📂 `Program blocks/OP010/03_Auto/`  
Add to appropriate subfolder (A1, A2, B_Press, etc.)  
Create: `ST10_Flow[X]_[Description].xml`  
Create iDB: `M_iDB/ST10_Flow[X]_[Description]_iDB.xml`

### New Recipe Parameter
📂 `PLC data types/_PARAMETERS_RECIPES/`  
Add UDT definition  
Update: `UDT_RECIPE.xml`

### New MES Data Exchange
📂 `Program blocks/OP010/11_MES/`  
Create: `Station[X]LoadData.xml` / `Station[X]UnLoadData.xml`

### New Constant/Enum
📂 `PLC tags/constant/`  
Create or modify appropriate XML file

---

## ⚠️ NOTES

- **OLD SHIT folders** contain deprecated/legacy code - do not use for new development
- **Z_Reserve folder** is for temporary/commissioning blocks
- **iDB folders** contain instance data blocks (automatically generated instances of FBs)
- Flow numbers are NOT sequential (gaps exist: 9, 10, 13, 16-20, etc.)
- Multiple file formats exist: `.xml` (TIA exports), `.scl` (source code)

> **Generated:** 2026-02-01  
> **Project:** OP10 Station PLC Code  
> **Purpose:** Siemens TIA Portal PLC Project for Manufacturing Station

---

## 📁 ROOT DIRECTORY STRUCTURE

```
📂 OP10/
├── 📁 DB_ALL_PROCESS_PARAMETERS.db          # Process parameters database
├── 📁 GlueningRotaryTable.db                # Gluing rotary table database
├── 📁 DOKUMENTACE/                          # Documentation folder
├── 📁 PLC data types/                       # UDTs (User Data Types)
├── 📁 PLC tags/                             # PLC tag tables
└── 📁 Program blocks/                       # Main program logic (FC, FB, DB, OB)
```

---

## 📊 PLC DATA TYPES (`PLC data types/`)

User-Defined Types (UDTs) organized by category:

### System Types (`00 Sys/`)
| File | Purpose |
|------|---------|
| `RCS_CountCycleTime_V1.xml` | Cycle time counting structure |
| `RCS_PMInterface_V1.xml` | PM Interface structure |
| `RCS_SysAlarmWarning_V1.xml` | System alarm/warning structure |
| `RCS_SysAuto_V1.xml` | Auto mode structure |
| `RCS_SysCmd_V1.xml` | System commands structure |
| `RCS_SysComInterface_V1.xml` | Communication interface |
| `RCS_SysCount_V1.xml` | System counter structure |
| `RCS_SysCycleTime_V1.xml` | System cycle time |
| `RCS_SysManual_V1.xml` | Manual mode structure |
| `RCS_SysSafety_V1.xml` | Safety system structure |
| `RCS_SysStatus_V1.xml` | System status structure |

### Function Block Types (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `101 Cylinder/` | Cylinder control UDT (`Cyl.xml`) |
| `102 SafetyGate/` | Safety gate UDT (`SafetyGateUDT.xml`) |
| `105 MaterialGate/` | Material gate UDT |
| `201 Stopper/` | Stopper UDT (`ST_Stopper.xml`, `UDT_Stopper_FB.xml`) |
| `202 Conveyer_Line/` | Motor control UDT (`Motor_Control.xml`) |
| `211 ATEQ LeakTest/` | ATEQ leak test visual type |
| `212 Analog/` | General analog UDT (`ST_GeneralAnalog.xml`) |

### User Types (`500 User/`)
| File | Purpose |
|------|---------|
| `ATEQRecipe.xml` | ATEQ recipe structure |
| `Check.xml` | Check data structure |
| `PresserRecipe.xml` | Presser recipe structure |
| `StaProcessData.xml` | Station process data |
| `UDT_LabelFeeder.xml` | Label feeder UDT |
| `UDT_Marking CharToASCII.xml` | Marking char conversion |
| `UDT_Marking StringToChar.xml` | Marking string conversion |
| `UDT_StaProcessData.xml` | Station process data UDT |
| `100 FixtureCheck/` | Fixture check UDT |
| `104 PartDataManage/` | Part data management UDTs |
| `210 Recipe/` | Recipe axis UDT |

### External Device Types
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner (HMI, Input, Output types) |
| `LXL/` | IAI Servo, Kistler, Kuka Robot types |
| `MES/` | MES monitoring types |
| `ProcessData/` | Process data types |
| `RCS-PPK/` | Stopper interface types |

### Recipe Parameters (`_PARAMETERS_RECIPES/`)
| File | Purpose |
|------|---------|
| `UDT_Gripper_Fixture_Codes.xml` | Gripper/fixture codes |
| `UDT_IAI_Axis_Positions.xml` | IAI axis positions |
| `UDT_Motion_Point_IAI.xml` | IAI motion points |
| `UDT_Motion_Point_V90.xml` | V90 motion points |
| `UDT_OP10_Recipe_type.xml` | OP10 recipe type |
| `UDT_RECIPE.xml` | Main recipe structure |
| `UDT_Recipe_ATEQ.xml` | ATEQ recipe |
| `UDT_Recipe_PressCurve.xml` | Press curve recipe |
| `UDT_V90_Axis_Positions.xml` | V90 axis positions |

### Enums
| File | Purpose |
|------|---------|
| `NGDoorState_Enum.xml` | NG Door state enumeration |
| `PartStatus_Enum.xml` | Part status enumeration |
| `UDT_OP10_Recipe_diff.xml` | Recipe difference structure |

---

## 🏷️ PLC TAGS (`PLC tags/`)

### Tag Tables
| File/Folder | Content |
|-------------|---------|
| `Default variable table.xml` | Default PLC tags |
| `NGSensor.xml` | NG sensor tags |
| `STEP7 classic symbols.xml` | STEP7 classic symbols |
| `constant/` | Constants (Flow, IV3, Lifting, Marking, MES codes, PartType, ProcessResult, RFID, TestResult, partstatus) |
| `IO/` | I/O tags (PLC DI/DQ, Remote IO DI/DO) |

---

## 🔧 PROGRAM BLOCKS (`Program blocks/`)

### Organization Blocks (`01_OB/`)
| File | Purpose |
|------|---------|
| `01_OB1.xml` | Main cyclic OB |
| `02_Warm Restart.xml` | Warm restart OB |
| `03_CYC_INT2.xml` | Cyclic interrupt 2 |
| `04_CYC_INT5.xml` | Cyclic interrupt 5 |
| `05_MOD_ERR.xml` | Module error OB |
| `07_CYCL_FLT.xml` | Cycle fault OB |
| `08_HW_INT0.xml` | Hardware interrupt 0 |
| `09_IO_FLT1.xml` | I/O fault OB |
| `11_PROG_ERR.xml` | Program error OB |
| `12_RACK_FLT.xml` | Rack fault OB |

### System Functions (`00 Sys/`)
| File | Purpose |
|------|---------|
| `CheckData.xml` | Data checking |
| `Count_CycleTime.xml` | Cycle time counting |
| `Count_CycleTime_V3.xml` | Cycle time counting v3 |
| `SysFlowCtrlGraph.xml` | Flow control graph |
| `SystemMode.xml` | System mode management |

### Communication (`02_Comm/`)
| Folder | Content |
|--------|---------|
| `03-Diagnosis/` | Diagnostic FBs |
| `04-ChangeOver/` | Changeover logic |
| `06_SysDataBlock&Function/` | System data/functions |

### Reusable Function Blocks (`03 FunctionBlocks/`)
| Folder | Content |
|--------|---------|
| `003 Tower_Lamp/` | Tower lamp control (`FB_Tower_4Lamp.xml`) |
| `101 Cylinder/` | Cylinder control (`CylinderCtrl_V2.xml`, `CylinderModule_V2.xml`) |
| `102 SafetyGate/` | Safety gate (`SafetyGate.xml`) |
| `201 Stopper/` | Stopper control (`FB_Stopper.xml`) |
| `202 Conveyer_Line/` | Motor control (`MotorContro.xml`) |
| `999 Base/` | Base functions (`FB_Next.xml`) |

### Device-Specific (`03_Device/`)
| Folder | Content |
|--------|---------|
| `102 SafetyGate/` | Material gate |
| `211 ATEQ LeakTest/` | ATEQ F620 leak test |
| `212 Analog/` | Analog processing |

### User Functions (`500 User/`)
| Folder | Content |
|--------|---------|
| `100 FixtureCheck/` | Fixture checking |
| `104 PartDataManage/` | Part data management |

### External Device Libraries
| Folder | Device |
|--------|--------|
| `KeyenceSR1000/` | Keyence SR1000 scanner control |
| `RCS-PPK/` | Stopper control library |

### Special Folders
| Folder | Purpose |
|--------|---------|
| `__MES MONITORING/` | MES monitoring FBs |
| `__PARAMETERS/` | Recipe/parameter handling |
| `Z_Reserve/` | Reserved/commissioning blocks |

---

## 🏭 STATION OP010 (`Program blocks/OP010/`)

Main station logic organized by function:

### Main (`00_Main/`)
| File | Purpose |
|------|---------|
| `ST10_Main.xml` | Main station FB |
| `ST10_GeneralData.xml` | General data DB |
| `Station_Sys.xml` | Station system FB |
| `iDB/ST10_SystemModeFB_iDB.xml` | System mode instance DB |

### Input Processing (`01_Input/`)
| File | Purpose |
|------|---------|
| `ST10_Input.xml` | Input processing |
| `ST10_SysInput.xml` | System input processing |

### Output Processing (`02_Output/`)
| File | Purpose |
|------|---------|
| `ST10_Output.xml` | Output processing |
| `ST10_SysOutput.xml` | System output processing |
| `ST10_FB_Tower_4Lamp_DB.xml` | Tower lamp instance DB |

### Automatic Mode (`03_Auto/`)
| Folder/File | Purpose |
|-------------|---------|
| `AutoProcessControl.xml` | Auto process control |
| `AutoProcessData.xml` | Auto process data |
| `AutoProcessData_Buffer.xml` | Process data buffer |
| `PalletRelease.xml` | Pallet release logic |
| `ST10_PM.xml` | PM interface |
| `TON.xml` | Timer functions |
| `01ChangeOver/` | Changeover flows |
| `A1_TableLoad&Scan/` | Table A1 loading & scanning |
| `A2_TableLoad&Scan/` | Table A2 loading & scanning |
| `B_Press/` | Press operations (B1, B2) |
| `C_Glue/` | Gluing operation |
| `F_Robot/` | Robot operations (1, 2, 3) |
| `H_ShaftLifting&Load&Unload/` | Shaft lifting operations |
| `J_MagnetLifting&Load&Unload/` | Magnet lifting operations |
| `L_Unload/` | Unloading operations |
| `M_iDB/` | Instance DBs for all flows |
| `HMI/` | HMI interface blocks |

**Flow Sequence:**
1. `ST10_Flow1_A1TableScan` - A1 Table Scan
2. `ST10_Flow2_A1TableUnloading` - A1 Table Unload
3. `ST10_Flow3_A1RotaryShaftScan` - Rotary Shaft Scan
4. `ST10_Flow4_B1Press` - B1 Press
5. `ST10_Flow5_FRobot_1` - Robot 1 Operation
6. `ST10_Flow6_ToolCodeScan` - Tool Code Scan
7. `ST10_Flow7_CGlueing` - Gluing
8. `ST10_Flow8_FRobot_2` - Robot 2 Operation
11. `ST10_Flow11_A2TableScan` - A2 Table Scan
12. `ST10_Flow12_A2TableUnloading` - A2 Table Unload
14. `ST10_Flow14_B2Press` - B2 Press
15. `ST10_Flow15_FRobot_3` - Robot 3 Operation
21. `ST10_Flow21_HShaftLifting` - H Shaft Lifting
22. `ST10_Flow22_JMagnetLifting` - J Magnet Lifting
23. `ST10_Flow23_KReserveLifting` - K Reserve Lifting
24. `ST10_Flow24_LUnloadingTrans` - L Unloading Transfer
25. `ST10_Flow25_HShaftLoad&Unload` - H Shaft Load/Unload
26. `ST10_Flow26_JMagnetLoad&Unload` - J Magnet Load/Unload
27. `ST10_Flow27_KReserveLoad&Unload` - K Reserve Load/Unload
28. `ST10_Flow28_LUnloadingLoad&Unload` - L Unloading Load/Unload

### Manual Mode (`04_Manual/`)
| File | Purpose |
|------|---------|
| `ST10_Manual.xml` | Manual operation logic |

### Alarm Handling (`05_Alarm/`)
| File | Purpose |
|------|---------|
| `ST10_Alarm.xml` | Alarm management |
| `ST10_DeviceError.xml` | Device error handling |
| `ST10_GlobalError.xml` | Global error handling |

### Warning Handling (`06_Warning/`)
| File | Purpose |
|------|---------|
| `ST10_Warning.xml` | Warning management |
| `ST10_WarningDB.xml` | Warning data block |

### Tips (`07_Tip/`)
| File | Purpose |
|------|---------|
| `ST10_Tip.xml` | Tip management |
| `ST10_TipDB.xml` | Tip data block |

### Changeover (`08_ChangeOver/`)
| File | Purpose |
|------|---------|
| `ST10_ChangeOver.xml` | Changeover logic |
| `Parameter.xml` | Parameters |
| `ST10_RecipeDB.xml` | Recipe database |
| `ST10_RecipeDB_HMI.xml` | HMI recipe interface |
| `ST10_RecipeActiveDB.xml` | Active recipe DB |
| `MES/OP010_MES_RecipeDB.xml` | MES recipe DB |

### Cycle Time (`09_Count_CycleTime/`)
| File | Purpose |
|------|---------|
| `ST10_CountCycleTimeMain.xml` | Main cycle time counter |
| `ST10_CountCycleTimeMain_DB.xml` | Cycle time data block |
| `ST10_PMCountCycleTime.xml` | PM cycle time |

### Device Control (`10_Device/`)
| Folder | Device/Function |
|--------|-----------------|
| `01_Cylinder/` | Cylinders 1-100 (ST10Cylinder.xml + interfaces) |
| `03_SafetyGate/` | Safety gates 1-9 + Material gates 1-7 |
| `06_Stopper/` | Stopper control |
| `08_PressureAanlog/` | Pressure analog processing |
| `09_CuringOven/` | Curing oven control |
| `18_SR1000 Scan/` | Keyence SR1000 scanners (8 instances) |
| `21_IV3/` | Keyence IV3 vision sensors |
| `22_IAI/` | IAI servo axes (A1, A2, A3) |
| `23_Kistler/` | Kistler press systems (1 & 2) |
| `24_Robot/` | Kuka robots (1, 2, 3) |
| `25_V90/` | V90 servo drives (A1-A4) |
| `26_Stopper/` | Additional stopper control |
| `27_Pilz/` | Pilz safety system |
| `28_Gluing/` | Gluing system control |
| `29_NG/` | NG (Not Good) box control |
| `31_Motor_1/` | Motor controls 1-17 |

### MES Integration (`11_MES/`)
| File | Purpose |
|------|---------|
| `MES.xml` | Main MES FB |
| `MES_CheckControl.xml` | MES check control |
| `MES_CHeck.xml` / `MES Check_fb.xml` | MES check functions |
| `MES_CHeck_DB.xml` | MES check DB |
| `MEStoPLC.xml` | MES to PLC data |
| `PLCtoMES.xml` | PLC to MES data |
| `DT-Chars.xml` / `DT-Chars_DB.xml` | Data type char conversion |
| `Station1LoadData.xml` - `Station8UnLoadData.xml` | Station load/unload data |
| `Scanner1LoadData.xml` | Scanner load data |

### Part Data (`12_PartData/`)
| File | Purpose |
|------|---------|
| `ST10_PartData.xml` | Part data management |
| `PartData_Interface_DB.xml` | Part data interface |
| `PartDataManage_Part1_DB.xml` - `PartDataManage_Part4_DB.xml` | Part data for parts 1-4 |

---

## 📋 STANDARDS & GUIDELINES

### Naming Conventions
| Prefix | Meaning | Example |
|--------|---------|---------|
| `ST10_` | Station 10 blocks | `ST10_Main.xml` |
| `ST10_FlowX_` | Process flow step X | `ST10_Flow1_A1TableScan.xml` |
| `FB_` | Function Block | `FB_Stopper.xml` |
| `FC_` | Function Call | `FC_Save_Values_Final.xml` |
| `DB_` | Data Block | `DB_MES_Monitoring.xml` |
| `UDT_` | User Data Type | `UDT_RECIPE.xml` |
| `iDB/` | Instance Data Blocks folder | - |

### File Extensions
| Extension | Type |
|-----------|------|
| `.xml` | TIA Portal exported block (standard) |
| `.scl` | Structured Control Language (Siemens) |
| `.db` | Database file |

### Folder Numbering Convention
| Range | Category |
|-------|----------|
| `00-09` | System/Organization |
| `01-09` | Organization Blocks |
| `10-99` | Function Blocks |
| `100-199` | User Functions |
| `200-299` | Devices |
| `500+` | Custom/User |

---

## 🔍 WHERE TO ADD NEW COMPONENTS

### New Device Type (UDT)
📂 `PLC data types/03 FunctionBlocks/`  
Create folder: `[NNN] [DeviceName]/`  
Add UDT in: `[NNN].1 UDT/[Name].xml`

### New Device Instance
📂 `Program blocks/OP010/10_Device/`  
Create folder: `[NN]_[DeviceName]/`  
Add control FB and instance DBs

### New Process Flow Step
📂 `Program blocks/OP010/03_Auto/`  
Add to appropriate subfolder (A1, A2, B_Press, etc.)  
Create: `ST10_Flow[X]_[Description].xml`  
Create iDB: `M_iDB/ST10_Flow[X]_[Description]_iDB.xml`

### New Recipe Parameter
📂 `PLC data types/_PARAMETERS_RECIPES/`  
Add UDT definition  
Update: `UDT_RECIPE.xml`

### New MES Data Exchange
📂 `Program blocks/OP010/11_MES/`  
Create: `Station[X]LoadData.xml` / `Station[X]UnLoadData.xml`

### New Constant/Enum
📂 `PLC tags/constant/`  
Create or modify appropriate XML file

---

## ⚠️ NOTES

- **OLD SHIT folders** contain deprecated/legacy code - do not use for new development
- **Z_Reserve folder** is for temporary/commissioning blocks
- **iDB folders** contain instance data blocks (automatically generated instances of FBs)
- Flow numbers are NOT sequential (gaps exist: 9, 10, 13, 16-20, etc.)
- Multiple file formats exist: `.xml` (TIA exports), `.scl` (source code)



