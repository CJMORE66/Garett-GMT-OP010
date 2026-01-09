# Pokrytí převodu XML → SCL (všechny bloky)

- Čas generování: `2026-01-09 17:42:53`
- Zdroj manifestu: `deep_reader/scl_export/manifest.json`
- Počet bloků (OB/FB/FC) v exportu SCL: `118`

## Souhrn podle původního jazyka

| Jazyk | Bloky | ST sekce | LAD/FBD sekce | STL sekce | Varování | Nepodporované prvky | Bez logiky |
|---|---:|---:|---:|---:|---:|---:|---:|
| `LAD` | `65` | `25` | `57` | `0` | `37` | `36` | `4` |
| `SCL` | `26` | `25` | `0` | `0` | `0` | `0` | `1` |
| `GRAPH` | `22` | `0` | `0` | `0` | `0` | `0` | `22` |
| `STL` | `5` | `0` | `0` | `0` | `0` | `0` | `5` |

## Top bloky podle počtu varování (omezení převodu)

Pozn.: Varování znamená, že síť obsahovala nepodporované prvky nebo nebylo možné určit operand/target/podmínku. Překlad je orientační pro revizi.

| Varování | Nepodporované | Blok | Jazyk | Zdroj |
|---:|---:|---|---|---|
| `77` | `77` | `SW.Blocks.FC `ST10_Alarm`` | `LAD` | `EXPORT/Program blocks/OP010/05_Alarm/ST10_Alarm.xml` |
| `28` | `28` | `SW.Blocks.FC `ST10_Output`` | `LAD` | `EXPORT/Program blocks/OP010/02_Output/ST10_Output.xml` |
| `25` | `25` | `SW.Blocks.FC `ChangeOverProcess`` | `LAD` | `EXPORT/Program blocks/OP010/03_Auto/01ChangeOver/ChangeOverProcess.xml` |
| `20` | `18` | `SW.Blocks.FC `Robot`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/24_Robot/Robot.xml` |
| `17` | `0` | `SW.Blocks.FB `ST10_StopperCtrl`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/26_Stopper/ST10_StopperCtrl.xml` |
| `16` | `16` | `SW.Blocks.FB `fbV90Ctrl`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/25_V90/V90_Standard/fbV90Ctrl.xml` |
| `16` | `15` | `SW.Blocks.FC `MES`` | `LAD` | `EXPORT/Program blocks/OP010/11_MES/MES.xml` |
| `13` | `13` | `SW.Blocks.FB `V90_Servo`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/25_V90/V90_Servo.xml` |
| `10` | `10` | `SW.Blocks.FB `NGStatus`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/29_NG/NGStatus.xml` |
| `10` | `8` | `SW.Blocks.FC `KistlerPresser_Main`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/23_Kistler/KistlerPresser_Main.xml` |
| `9` | `9` | `SW.Blocks.FB `FB_Tower_4Lamp`` | `LAD` | `EXPORT/Program blocks/03_Device/04 Lamp/FB_Tower_4Lamp.xml` |
| `9` | `7` | `SW.Blocks.FB `FB_Stopper`` | `LAD` | `EXPORT/Program blocks/03_Device/201 Stopper/FB_Stopper.xml` |
| `8` | `8` | `SW.Blocks.FB `MotorContro`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/31_Motor_1/MotorContro.xml` |
| `7` | `7` | `SW.Blocks.FB `StopperCtrl`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/26_Stopper/01_FuncationBlock/StopperCtrl.xml` |
| `7` | `7` | `SW.Blocks.FC `CylinderModule_V2`` | `LAD` | `EXPORT/Program blocks/03_Device/101_Cylinder/CylinderModule_V2.xml` |
| `7` | `7` | `SW.Blocks.FC `ST10_Auto`` | `LAD` | `EXPORT/Program blocks/OP010/03_Auto/ST10_Auto.xml` |
| `6` | `6` | `SW.Blocks.FB `MaterialGate`` | `LAD` | `EXPORT/Program blocks/03_Device/102 SafetyGate/MaterialGate.xml` |
| `6` | `6` | `SW.Blocks.FB `SafetyGate`` | `LAD` | `EXPORT/Program blocks/03_Device/102 SafetyGate/SafetyGate.xml` |
| `5` | `4` | `SW.Blocks.FB `MES Check_fb`` | `LAD` | `EXPORT/Program blocks/OP010/11_MES/MES Check_fb.xml` |
| `4` | `4` | `SW.Blocks.FB `FB_Analog`` | `LAD` | `EXPORT/Program blocks/03_Device/212 Analog/FB_Analog.xml` |
| `4` | `4` | `SW.Blocks.FB `MES_CHeck`` | `LAD` | `EXPORT/Program blocks/OP010/11_MES/MES_CHeck.xml` |
| `4` | `4` | `SW.Blocks.FB `SystemMode`` | `LAD` | `EXPORT/Program blocks/02_Comm/02_SysMode/SystemMode.xml` |
| `4` | `4` | `SW.Blocks.FC `Motorr`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/31_Motor_1/Motorr.xml` |
| `4` | `2` | `SW.Blocks.FB `NG`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/29_NG/NG.xml` |
| `3` | `3` | `SW.Blocks.FB `FB_Step`` | `LAD` | `EXPORT/Program blocks/03_Device/999 Base/FB_Step.xml` |
| `3` | `3` | `SW.Blocks.FB `ST10_Stopper_FB`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/06_Stopper/ST10_Stopper_FB.xml` |
| `3` | `3` | `SW.Blocks.FC `Gluing`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/28_Gluing/Gluing.xml` |
| `3` | `3` | `SW.Blocks.FC `ST10_ChangeOver`` | `LAD` | `EXPORT/Program blocks/OP010/08_ChangeOver/ST10_ChangeOver.xml` |
| `3` | `3` | `SW.Blocks.FC `ST10_Tip`` | `LAD` | `EXPORT/Program blocks/OP010/07_Tip/ST10_Tip.xml` |
| `2` | `2` | `SW.Blocks.FB `ST10_FB_S7connect`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/09_CuringOven/ST10_FB_S7connect.xml` |
| `2` | `2` | `SW.Blocks.FB `SevroStart&PosCheck`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/25_V90/V90_Standard/ServoCheck/SevroStart&PosCheck.xml` |
| `2` | `2` | `SW.Blocks.FB `SevroStart&PosCheck_IAI`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/22_IAI/ServoCheck/SevroStart&PosCheck_IAI.xml` |
| `2` | `2` | `SW.Blocks.FC `fcFixtureCheck`` | `LAD` | `EXPORT/Program blocks/03_Device/100 FixtureCheck/fcFixtureCheck.xml` |
| `2` | `2` | `SW.Blocks.OB `01_OB1`` | `LAD` | `EXPORT/Program blocks/01_OB/01_OB1.xml` |
| `1` | `1` | `SW.Blocks.FC `Pilz`` | `LAD` | `EXPORT/Program blocks/OP010/10_Device/27_Pilz/Pilz.xml` |
| `1` | `1` | `SW.Blocks.FC `ST10_Main`` | `LAD` | `EXPORT/Program blocks/OP010/00_Main/ST10_Main.xml` |
| `1` | `1` | `SW.Blocks.OB `03_CYC_INT2`` | `LAD` | `EXPORT/Program blocks/01_OB/03_CYC_INT2.xml` |

## Bloky bez extrahované logiky (podezření na GRAPH / nepodporovanou reprezentaci)

Tyto bloky nemají StructuredText/FlgNet/StatementList sítě v exportu, takže SCL obsahuje jen rozhraní + odkazy na zdroj XML.

- `ST10_Flow11_A2TableScan` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/A2_TableLoad&Scan/ST10_Flow11_A2TableScan.xml`
- `ST10_Flow12_A2TableUnloading` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/A2_TableLoad&Scan/ST10_Flow12_A2TableUnloading.xml`
- `ST10_Flow14_B2Press` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/B_Press/ST10_Flow14_B2Press.xml`
- `ST10_Flow15_FRobot_3` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/F_Robot/ST10_Flow15_FRobot_3.xml`
- `ST10_Flow1_A1TableScan` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/A1_TableLoad&Scan/ST10_Flow1_A1TableScan.xml`
- `ST10_Flow21_HShaftLifting` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/H_ShaftLifting&Load&Unload/ST10_Flow21_HShaftLifting.xml`
- `ST10_Flow22_JMagnetLifting` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/J_MagnetLifting&Load&Unload/ST10_Flow22_JMagnetLifting.xml`
- `ST10_Flow23_KReserveLifting` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/L_Unload/K_ReserveLifting&Load&Unload/ST10_Flow23_KReserveLifting.xml`
- `ST10_Flow24_LUnloadingTrans` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/L_Unload/ST10_Flow24_LUnloadingTrans.xml`
- `ST10_Flow25_HShaftLoad&Unload` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/H_ShaftLifting&Load&Unload/ST10_Flow25_HShaftLoad&Unload.xml`
- `ST10_Flow26_JMagnetLoad&Unload` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/J_MagnetLifting&Load&Unload/ST10_Flow26_JMagnetLoad&Unload.xml`
- `ST10_Flow27_KReserveLoad&Unload` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/L_Unload/K_ReserveLifting&Load&Unload/ST10_Flow27_KReserveLoad&Unload.xml`
- `ST10_Flow28_LUnloadingLoad&Unload` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/L_Unload/ST10_Flow28_LUnloadingLoad&Unload.xml`
- `ST10_Flow2_A1TableUnloading` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/A1_TableLoad&Scan/ST10_Flow2_A1TableUnloading.xml`
- `ST10_Flow3_A1RotaryShaftScan` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/A1_TableLoad&Scan/ST10_Flow3_A1RotaryShaftScan.xml`
- `ST10_Flow4_B1Press` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/B_Press/ST10_Flow4_B1Press.xml`
- `ST10_Flow5_FRobot_1` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/F_Robot/ST10_Flow5_FRobot_1.xml`
- `ST10_Flow5_FRobot_1` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/F_Robot/ST10_Flow5_FRobot_1_01092026_152002.xml`
- `ST10_Flow5_FRobot_1` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/F_Robot/ST10_Flow5_FRobot_1_01092026_152004.xml`
- `ST10_Flow6_ToolCodeScan` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/01ChangeOver/ST10_Flow6_ToolCodeScan.xml`
- `ST10_Flow7_CGlueing` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/C_Glue/ST10_Flow7_CGlueing.xml`
- `ST10_Flow8_FRobot_2` (SW.Blocks.FB, `GRAPH`) `EXPORT/Program blocks/OP010/03_Auto/F_Robot/ST10_Flow8_FRobot_2.xml`
- `ST10_Manual` (SW.Blocks.FC, `LAD`) `EXPORT/Program blocks/OP010/04_Manual/ST10_Manual.xml`
- `Stopper` (SW.Blocks.FC, `LAD`) `EXPORT/Program blocks/OP010/10_Device/26_Stopper/Stopper.xml`
- `04_CYC_INT5` (SW.Blocks.OB, `LAD`) `EXPORT/Program blocks/01_OB/04_CYC_INT5.xml`
- `08_HW_INT0` (SW.Blocks.OB, `LAD`) `EXPORT/Program blocks/01_OB/08_HW_INT0.xml`
- `ST10_PartData` (SW.Blocks.FC, `SCL`) `EXPORT/Program blocks/OP010/12_PartData/ST10_PartData.xml`
- `05_MOD_ERR` (SW.Blocks.OB, `STL`) `EXPORT/Program blocks/01_OB/05_MOD_ERR.xml`
- `07_CYCL_FLT` (SW.Blocks.OB, `STL`) `EXPORT/Program blocks/01_OB/07_CYCL_FLT.xml`
- `09_I/O_FLT1` (SW.Blocks.OB, `STL`) `EXPORT/Program blocks/01_OB/09_IO_FLT1.xml`
- `11_PROG_ERR` (SW.Blocks.OB, `STL`) `EXPORT/Program blocks/01_OB/11_PROG_ERR.xml`
- `12_RACK_FLT` (SW.Blocks.OB, `STL`) `EXPORT/Program blocks/01_OB/12_RACK_FLT.xml`

