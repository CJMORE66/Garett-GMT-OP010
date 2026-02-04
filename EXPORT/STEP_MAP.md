# STEP MAP (GRAPH blocks)

| Flow FB | Steps | Transitions | Relpath |
|---|---:|---:|---|
| ST10_Flow11_A2TableScan | 120 | 145 | Program blocks/OP010/03_Auto/A2_TableLoad&Scan/ST10_Flow11_A2TableScan.xml |
| ST10_Flow12_A2TableUnloading | 47 | 56 | Program blocks/OP010/03_Auto/A2_TableLoad&Scan/ST10_Flow12_A2TableUnloading.xml |
| ST10_Flow14_B2Press | 94 | 116 | Program blocks/OP010/03_Auto/B_Press/ST10_Flow14_B2Press.xml |
| ST10_Flow15_FRobot_3 | 159 | 182 | Program blocks/OP010/03_Auto/F_Robot/ST10_Flow15_FRobot_3.xml |
| ST10_Flow1_A1TableScan | 100 | 116 | Program blocks/OP010/03_Auto/A1_TableLoad&Scan/ST10_Flow1_A1TableScan.xml |
| ST10_Flow21_HShaftLifting | 33 | 38 | Program blocks/OP010/03_Auto/H_ShaftLifting&Load&Unload/ST10_Flow21_HShaftLifting.xml |
| ST10_Flow22_JMagnetLifting | 33 | 38 | Program blocks/OP010/03_Auto/J_MagnetLifting&Load&Unload/ST10_Flow22_JMagnetLifting.xml |
| ST10_Flow23_KReserveLifting | 32 | 37 | Program blocks/OP010/03_Auto/L_Unload/K_ReserveLifting&Load&Unload/ST10_Flow23_KReserveLifting.xml |
| ST10_Flow24_LUnloadingTrans | 43 | 49 | Program blocks/OP010/03_Auto/L_Unload/ST10_Flow24_LUnloadingTrans.xml |
| ST10_Flow25_HShaftLoad&Unload | 149 | 164 | Program blocks/OP010/03_Auto/H_ShaftLifting&Load&Unload/ST10_Flow25_HShaftLoad&Unload.xml |
| ST10_Flow26_JMagnetLoad&Unload | 149 | 164 | Program blocks/OP010/03_Auto/J_MagnetLifting&Load&Unload/ST10_Flow26_JMagnetLoad&Unload.xml |
| ST10_Flow27_KReserveLoad&Unload | 149 | 164 | Program blocks/OP010/03_Auto/L_Unload/K_ReserveLifting&Load&Unload/ST10_Flow27_KReserveLoad&Unload.xml |
| ST10_Flow28_LUnloadingLoad&Unload | 104 | 114 | Program blocks/OP010/03_Auto/L_Unload/ST10_Flow28_LUnloadingLoad&Unload.xml |
| ST10_Flow2_A1TableUnloading | 49 | 59 | Program blocks/OP010/03_Auto/A1_TableLoad&Scan/ST10_Flow2_A1TableUnloading.xml |
| ST10_Flow3_A1RotaryShaftScan | 84 | 104 | Program blocks/OP010/03_Auto/A1_TableLoad&Scan/ST10_Flow3_A1RotaryShaftScan.xml |
| ST10_Flow4_B1Press | 94 | 116 | Program blocks/OP010/03_Auto/B_Press/ST10_Flow4_B1Press.xml |
| ST10_Flow5_FRobot_1 | 154 | 178 | Program blocks/OP010/03_Auto/F_Robot/ST10_Flow5_FRobot_1.xml |
| ST10_Flow6_ToolCodeScan | 191 | 203 | Program blocks/OP010/03_Auto/01ChangeOver/ST10_Flow6_ToolCodeScan.xml |
| ST10_Flow7_CGlueing | 189 | 203 | Program blocks/OP010/03_Auto/C_Glue/ST10_Flow7_CGlueing.xml |
| ST10_Flow8_FRobot_2 | 132 | 152 | Program blocks/OP010/03_Auto/F_Robot/ST10_Flow8_FRobot_2.xml |

## Key step-name samples (first 25 per flow)

### ST10_Flow11_A2TableScan
S5_MESInitial, ServoReady?, S10_InitialFinish, Servo returns to2st Pos, Servo returns to1st Pos, Servo returns to3st Pos, Servo returns to4st Pos, Servo returns to3st Pos_1, Servo returns to3st Pos_2, Servo returns to3st Pos_3, Servo returns to3st Pos_4, Determine TableFixtureStatus, A-Loading-01HorizontalCylinderToHP, A-Loading-02UpDownTakeCylinderToHP, FixtureOK, Step128, FixtureNG, Tablecode reading, ReadyReading, process, Start 2st reading, ReadNG1, ReadNG2, Wait reading complete_, DataMove_4

### ST10_Flow12_A2TableUnloading
S5_MESInitial, ServoReady?, WaitRobotInitialFinish, S10_InitialFinish, Servo returns to1st Pos, ServoPosCount, ServoPosCountJudge, ServoPosCountClear, CountCompare, TableLackMaterial, WaitFixtureScanFinish, ResetPartMissingAlarm, WaitChangeOverFinish, WaitServoInPosition, Detect cartridge exist, Detect Ring exist, Detect UnloadingRing exist, Detect UnloadingRing exist_1, PartMissingAlarm, Step111, Request robot pick, SensorNoPart, CountClear, CountClear_1, A-Loading-02UpDownTakeCylinderToWP

### ST10_Flow14_B2Press
S5_MESInitial, PressProgram, PressHoming, S10_InitialFinish, PressReady?, PressHoming?, Step14, CheckPressGripStatus, ShaftAndRingOK, Press NG, MES, MESOK, PressProgram_1, PressHoming_1, PressReady?_1, PressHoming?_1, Step15, MES_1NG, Determine product status, CheckMachineStatus, Normal mode, ProcessStart,CTStart, Request robot putShaft, Request robot putRing, RobotLeavePress Area

### ST10_Flow15_FRobot_3
RobotSpeed, S5_MESInitial, S10_InitialFinish, ScanFixtureCode, Open NG BOX REQUESTED?, PickPallet, PickGlueNGReq, PickMagnetNGReqPick, PickTable, Maintenance, Masref_test, Brake_Test, ScanRing, PressShaftPut, PressRingPut, Tablecode ScanFinish, PressPick, OKPut, NG2Put_1Press/Glue, NG2Put_2/Magnet, NG2Put_3/Ring, Tablecode Scan, Grip1PartStatus, Grip2PartStatus, CheckScanReady

### ST10_Flow1_A1TableScan
S5_MESInitial, ServoReady?, S10_InitialFinish, Servo returns to2st Pos, Servo returns to1st Pos, Servo returns to3st Pos, Servo returns to4st Pos, Servo returns to3st Pos_1, Servo returns to3st Pos_2, Servo returns to3st Pos_3, Servo returns to3st Pos_4, Determine TableFixtureStatus, A-Loading-01HorizontalCylinderToHP, A-Loading-01UpDownTakeCylinderToHP, FixtureOK, Step128, FixtureNG, Tablecode reading, ReadyReading, process, Start 2st reading, ReadNG1, ReadNG2, Wait reading complete_, DataMove_4

### ST10_Flow21_HShaftLifting
S5_MESInitial, WaitRobotInitialFinish, S10_InitialFinish, StatusError, CheckStopPalletExist, TimeDelay, MotorCCWStart, MotorCWStart, H-shaftLiftingLiftingCylinderToWP, CheckShaftLiftingCylinderPos, H-shaftLiftingPalletLocationCylindertoHP, H-shaftLiftingPalletLocationCylindertoWP_1, Step131, MotorStop, CheckPalletExist, RequestRobotPickPalletShaft, WaitingPalletUnloading, PalletRequest, RobotCountClear0, H-shaftLiftingPalletLocationCylindertoHP_2, H-shaftLiftingPalletLocationCylindertoHP_3, MotorCCWRun, Motor Stop, H-shaftLiftingLiftingCylinderToWP2, H-shaftLiftingPalletLocationCylindertoHP_4

### ST10_Flow22_JMagnetLifting
S5_MESInitial, WaitRobotInitialFinish, S10_InitialFinish, StatusError, CheckStopPalletExist, TimeDelay, MotorCCWStart, MotorCWStart, H-shaftLiftingLiftingCylinderToWP, CheckShaftLiftingCylinderPos, J-magnetLiftingPalletLocationCylindertoHP, J-magnetLiftingPalletLocationCylindertoWP_1, Step131, MotorStop, CheckPalletExist, RequestRobotPickPallet, WaitingPalletUnloading, PalletRequest, RobotCountClear0, J-magnetLiftingPalletLocationCylindertoHP_2, J-magnetLiftingPalletLocationCylindertoHP_3, MotorCCWRun, Motor Stop, J-magnetLiftingCylinderToWP, J-magnetLiftingPalletLocationCylindertoHP_4

### ST10_Flow23_KReserveLifting
S5_MESInitial, WaitRobotInitialFinish, S10_InitialFinish, StatusError, CheckStopPalletExist, TimeDelay, MotorCCWStart, MotorCWStart, H-shaftLiftingLiftingCylinderToWP, CheckShaftLiftingCylinderPos, K-reserveLifting3PalletLocationCylindertoHP, K-reserveLifting3PalletLocationCylindertoWP_1, Step131, MotorStop, CheckPalletExist, RequestRobotPickPallet, WaitingPalletUnloading, PalletRequest, RobotCountClear0, K-reserveLifting3PalletLocationCylindertoHP_2, K-reserveLifting3PalletLocationCylindertoHP_3, MotorCCWRun, Motor Stop, K-reserveLiftingCylindertoWP_4, K-reserveLifting3PalletLocationCylindertoHP_4

### ST10_Flow24_LUnloadingTrans
S5_MESInitial, WaitRobotInitialFinish, S10_InitialFinish, StatusError, CheckStopPalletExist, TimeDelay, Motor CWStart, MotorCWStart, MotorCCWStart_1, MotorCWStart_2, MotorCCWStart_2, L-UnloadingTransCylinderToHP, CheckUnloadingTransCylinderPos, L-UnloadingTransPalletLocationCylinderHP_2, L-UnloadingTransCylindertoWP2, L-UnloadingTransPalletLocationCylinder ToWP, Time   Delay, MotorStop, CheckPalletExist, RequestRobotPickPallet, WaitingPalletUnloading, PalletRequest, RobotCountClear0, L-UnloadingTransPalletLocationCylinderTo HP, L-UnloadingTransCylindertoWP_3

### ST10_Flow25_HShaftLoad&Unload
S10_InitialFinish, MotorCWStart, MotorCWStart_1, MotorRunDelay, MotorRunDelay_1, StopProcess, LoadingStop_2, LoadingStop_3, LoadingStop_4, CheckPalletExist, CheckPalletExist_1, CheckMaterialDoorLock, MotorRun, WaitLineMotorReady, WaitPalletRequestRelease, WaitPalletArrveNextPos, WaitLineMotorReady_1, WaitPalletRequestRelease_1, WaitPalletArrveNextPos_1, CheckPalletExist_2, WaitLineMotorReady_2, WaitPalletRequestRelease_2, WaitPalletArrveNextPos_2, CheckPalletExist_3, WaitLineMotorReady_3

### ST10_Flow26_JMagnetLoad&Unload
S10_InitialFinish, MotorCWStart, MotorCWStart_1, MotorRunDelay, MotorRunDelay_1, StopProcess, LoadingStop_2, LoadingStop_3, LoadingStop_4, CheckPalletExist, CheckPalletExist_1, CheckMaterialDoorLock, MotorRun, WaitLineMotorReady, WaitPalletRequestRelease, WaitPalletArrveNextPos, WaitLineMotorReady_1, WaitPalletRequestRelease_1, WaitPalletArrveNextPos_1, CheckPalletExist_2, WaitLineMotorReady_2, WaitPalletRequestRelease_2, WaitPalletArrveNextPos_2, CheckPalletExist_3, WaitLineMotorReady_3

### ST10_Flow27_KReserveLoad&Unload
S10_InitialFinish, MotorCWStart, MotorCWStart_1, MotorRunDelay, MotorRunDelay_1, StopProcess, LoadingStop_2, LoadingStop_3, LoadingStop_4, CheckPalletExist, CheckPalletExist_1, CheckMaterialDoorLock, MotorRun, WaitLineMotorReady, WaitPalletRequestRelease, WaitPalletArrveNextPos, WaitLineMotorReady_1, WaitPalletRequestRelease_1, WaitPalletArrveNextPos_1, CheckPalletExist_2, WaitLineMotorReady_2, WaitPalletRequestRelease_2, WaitPalletArrveNextPos_2, CheckPalletExist_3, WaitLineMotorReady_3

### ST10_Flow28_LUnloadingLoad&Unload
S10_InitialFinish, MotorCWStart, MotorCWStart_1, MotorRunDelay, MotorRunDelay_1, StopProcess, LoadingStop_2, LoadingStop_3, CheckPalletExist, CheckPalletExist_1, CheckMaterialDoorLock, MotorRun, WaitLineMotorReady, WaitPalletRequestRelease, WaitPalletArrveNextPos, WaitLineMotorReady_1, WaitPalletRequestRelease_1, WaitPalletArrveNextPos_1, CheckPalletExist_2, WaitLineMotorReady_2, WaitPalletRequestRelease_2, WaitPalletArrveNextPos_2, LoadStop_14, LoadStop_12, LoadStop_13

### ST10_Flow2_A1TableUnloading
S5_MESInitial, ServoReady?, WaitRobotInitialFinish, S10_InitialFinish, Servo returns to1st Pos, ServoPosCount, ServoPosCountJudge, ServoPosCountClear, CountCompare, TableLackMaterial, WaitFixtureScanFinish, ResetPartMissingAlarm, WaitChangeOverFinish, WaitServoInPosition, Detect cartridge exist, Detect Ring exist, Detect UnloadingRing exist, Detect UnloadingRing exist_1, PartMissingAlarm, Step111, Request robot pick, SensorNoPart, CountClear, CountClear_1, A-Loading-01UpDownTakeCylinderToWP

### ST10_Flow3_A1RotaryShaftScan
ServoReady?, S5_MESInitial, WaitRobotInitialFinish, Servo returns to initial Pos, S10_InitialFinish, Servo returns to initial Pos_1, MES OK, Determine product status, CheckMachineStatus, Normal mode, ProcessStart,CTStart, Request robot put, RobotPutPartFinish, PartStatusOK, StatusAlarm, PartStatusError, NoPart, Wait  robot finish task, Wait robot finish task, Wait robot in safety area, Rotary code reading, Start 1st reading, Check reader Ready, Wait reading complete, Servo returns to Scan2 Pos

### ST10_Flow4_B1Press
S5_MESInitial, PressProgram, PressHoming, S10_InitialFinish, PressReady?, PressHoming?, Step14, CheckPressGripStatus, ShaftAndRingOK, Press NG, MES, MESOK, PressProgram_1, PressHoming_1, PressReady?_1, PressHoming?_1, Step15, MES_1, Determine product status, CheckMachineStatus, Normal mode, ProcessStart,CTStart, Request robot putShaft, Request robot putRing, RobotLeavePress Area

### ST10_Flow5_FRobot_1
RobotSpeed, S5_MESInitial, S10_InitialFinish, ScanFixtureCode, Open NG BOX REQUESTED?, PickPallet, PutBuffer, PickBuffer, PickTable, Maintenance, Masref_test, Brake_Test, ScanRing, PressShaftPut, PressRingPut, Tablecode ScanFinish, PressPick, GluePut, NG1Put_1/Press, NG1Put_2/ShaftScan, NG1Put_3/RingScan, Tablecode Scan, Wait ScanFinish, Grip1PartStatus, Grip2PartStatus

### ST10_Flow6_ToolCodeScan
S5_MESInitial, S10_InitialFinish, Determine TableFixtureStatus, RobotMaintenanceReq, WaitAllPartEmpty, ToolScanCondition, Robot2CheckScanResult, Fixturecode reading, CheckScanStatus, RB1_Process scan, DataMove_1, DataMove_2, Start 1st reading, Check reader Ready, Wait reading complete, Start 2st reading, Check reader Ready_1, Wait reading complete_1, DataMove_3, Start 3st reading, Check reader Ready_2, Wait reading complete_2, DataMove_4, Start 4st reading, Check reader Ready_3

### ST10_Flow7_CGlueing
S5_MESInitial, ServoReady?, WaitRobotInitialFinish, S10_InitialFinish, Axis_YToHomePos, Servo returns toHome Pos, CheckPartStatus, StatusAlarm, Axis_YToGlueePos_1, RequestRobot1PutShaft, WaitRobot1FinishTask, Axis_XToGluePos_1, CheckGlueSysOK, Servo returns toGluePos_1, Axis_XToGlueSafPos, Glue_1, Axis_ZToGlueePos_2, Axis_XToGluePos_2, CheckGlueSysOK_1, Servo returns toGluePos_2, Axis_XToGlueSafPos_2, Glue_2, Axis_YToGlueePos_5, TimeDelay_1, TimeDelay_2

### ST10_Flow8_FRobot_2
RobotSpeed, S5_MESInitial, S10_InitialFinish, ScanFixtureCode, Open NG BOX REQUESTED?, PickPallet, ScanNGPut, GlueNGPut, PickTable, Maintenance, Masref_test, Brake_Test, ScanMagane, GluePick, PutPress, Tablecode ScanFinish, PressPick, GluePut, Tablecode Scan, Grip1PartStatus, Grip2PartStatus, CheckScanReady, ScanStart, WaitScanCompletely, CodeMove
