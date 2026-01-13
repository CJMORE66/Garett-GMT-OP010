# Analýza přístupu k datovým blokům (DB) v projektu TIA Portal

Tento dokument shrnuje výsledky analýzy datových bloků (DB) v exportovaném projektu TIA Portal s ohledem na použití "Optimalizovaného přístupu k bloku" vs. "Standardního přístupu" (absolutní adresování).

## Souhrn
*   **Celkem nalezeno DB:** 81
*   **DB s optimalizovaným přístupem:** 15
*   **DB se standardním (neoptimalizovaným) přístupem:** 66

---

## 1. Seznam DB s optimalizovaným přístupem (Optimized)
Následující datové bloky již používají optimalizovaný přístup. Toto je moderní a doporučený způsob práce s datovými bloky v TIA Portal, který zlepšuje výkon a efektivitu paměti.

*   `GeneralDebug`
*   `ST10_SysInput`
*   `ST10_SysOutput`
*   `TON`
*   `AutoProcess_HMI`
*   `Parameter`
*   `ST10_SafetyGate_InterfaceDB`
*   `ST10_Stopper_InterfaceDB`
*   `OP10_GeneralAnalogDB`
*   `DB_KeyenceCheckerIV3`
*   `Debug`
*   `DATA`
*   `MotorControl`
*   `PartData_Interface_DB`
*   `DB_Commissioning`

---

## 2. Seznam DB se standardním (neoptimalizovaným) přístupem
Tyto datové bloky používají standardní přístup (absolutní adresování) a jsou potenciálními kandidáty na přepnutí na optimalizovaný přístup. Přepnutí by mělo být provedeno s rozvahou a po důkladné kontrole, zejména u bloků, které komunikují s externími systémy (HMI, MES, SCADA atd.).

### Kategorie rizika přepnutí:

#### 🟢 Nízké riziko (Doporučeno přepnout po ověření)
Tyto bloky pravděpodobně slouží pro interní logiku PLC a neměly by být vázány na externí systémy vyžadující absolutní adresování. Přepnutí na optimalizovaný přístup je zde nejpravděpodobnější a přínosné.

*   `AutoProcessControl` (Cesta: `Program blocks\OP010\03_Auto\AutoProcessControl.xml`)
*   `AutoProcessData` (Cesta: `Program blocks\OP010\03_Auto\AutoProcessData.xml`)
*   `AutoProcessData_Buffer` (Cesta: `Program blocks\OP010\03_Auto\AutoProcessData_Buffer.xml`)
*   `AutoProcessData_Buffer_Clear` (Cesta: `Program blocks\OP010\03_Auto\AutoProcessData_Buffer_Clear.xml`)
*   `PalletRelease` (Cesta: `Program blocks\OP010\03_Auto\PalletRelease.xml`)
*   `ST10_PM` (Cesta: `Program blocks\OP010\03_Auto\ST10_PM.xml`)
*   `ChangeOver_DB` (Cesta: `Program blocks\OP010\03_Auto\01ChangeOver\ChangeOver_DB.xml`)
*   `ST10_GeneralData` (Cesta: `Program blocks\OP010\00_Main\ST10_GeneralData.xml`)
*   `Station_Sys` (Cesta: `Program blocks\OP010\00_Main\Station_Sys.xml`)
*   `ST10_PMCountCycleTime` (Cesta: `Program blocks\OP010\09_Count_CycleTime\ST10_PMCountCycleTime.xml`)
*   `ST10Cylinder` (Cesta: `Program blocks\OP010\10_Device\01_Cylinder\ST10Cylinder.xml`)
*   `ST10_DBInterface_Stopper` (Cesta: `Program blocks\OP010\10_Device\26_Stopper\ST10_DBInterface_Stopper.xml`)
*   `GluingControl` (Cesta: `Program blocks\OP010\10_Device\28_Gluing\GluingControl.xml`)
*   `PalletNGData` (Cesta: `Program blocks\OP010\10_Device\29_NG\PalletNGData.xml`)
*   `MotorData` (Cesta: `Program blocks\OP010\10_Device\31_Motor_1\MotorData.xml`)

#### 🟡 Střední riziko (Nutná kontrola HMI/externího přístupu)
Tyto bloky jsou často přístupné z HMI panelů nebo jiných externích systémů. Před přepnutím je nezbytné ověřit, zda všechny externí přístupy (např. HMI proměnné, SCADA propojení, externí skripty) používají symbolický přístup k proměnným v těchto DB. Pokud používají absolutní adresy, přepnutí způsobí chyby.

*   `DiagnosticDataBlock` (Cesta: `Program blocks\02_Comm\03-Diagnosis\DiagnosticDataBlock.xml`)
*   `Sys` (Cesta: `Program blocks\02_Comm\06_SysDataBlock&Function\Sys.xml`)
*   `ST10_DeviceError` (Cesta: `Program blocks\OP010\05_Alarm\ST10_DeviceError.xml`)
*   `ST10_GlobalError` (Cesta: `Program blocks\OP010\05_Alarm\ST10_GlobalError.xml`)
*   `ST10_WarningDB` (Cesta: `Program blocks\OP010\06_Warning\ST10_WarningDB.xml`)
*   `ST10_TipDB` (Cesta: `Program blocks\OP010\07_Tip\ST10_TipDB.xml`)
*   `ST10_RecipeActiveDB` (Cesta: `Program blocks\OP010\08_ChangeOver\ST10_RecipeActiveDB.xml`)
*   `ST10_RecipeDB` (Cesta: `Program blocks\OP010\08_ChangeOver\ST10_RecipeDB.xml`)
*   `ST10_RecipeDB_HMI` (Cesta: `Program blocks\OP010\08_ChangeOver\ST10_RecipeDB_HMI.xml`)
*   `OP010_MES_RecipeDB` (Cesta: `Program blocks\OP010\08_ChangeOver\MES\OP010_MES_RecipeDB.xml`)
*   `HMISystemDB` (Cesta: `Program blocks\OP010\10_Device\22_IAI\HMISystemDB.xml`)

#### 🔴 Vysoké riziko (Doporučeno ponechat Standardní nebo provést hloubkovou analýzu)
Tyto bloky jsou s vysokou pravděpodobností používány pro komunikaci s externími zařízeními, jako jsou MES systémy, roboty, servo měniče, nebo speciální senzory. Často vyžadují absolutní adresování kvůli komunikačním protokolům nebo starším ovladačům/systémům. **Přepnutí na optimalizovaný přístup bez důkladné analýzy kódu (hledání instrukcí PEEK, POKE, BLKMOV, AT, nebo knihoven pro externí komunikaci) je vysoce rizikové a může vést k nefunkčnosti.**

*   **MES Rozhraní:**
    *   `MEStoPLC` (Cesta: `Program blocks\OP010\11_MES\MEStoPLC.xml`)
    *   `MES_CheckControl` (Cesta: `Program blocks\OP010\11_MES\MES_CheckControl.xml`)
    *   `MES_Log_DB` (Cesta: `Program blocks\OP010\11_MES\MES_Log_DB.xml`)
    *   `PLCtoMES` (Cesta: `Program blocks\OP010\11_MES\PLCtoMES.xml`)
    *   `Scanner1LoadData` (Cesta: `Program blocks\OP010\11_MES\Scanner1LoadData.xml`)
    *   `Station1LoadData` až `Station8UnLoadData` (celá sada):
        *   `Station1LoadData` (Cesta: `Program blocks\OP010\11_MES\Station1LoadData.xml`)
        *   `Station1UnLoadData` (Cesta: `Program blocks\OP010\11_MES\Station1UnLoadData.xml`)
        *   `Station2LoadData` (Cesta: `Program blocks\OP010\11_MES\Station2LoadData.xml`)
        *   `Station2UnLoadData` (Cesta: `Program blocks\OP010\11_MES\Station2UnLoadData.xml`)
        *   `Station3LoadData` (Cesta: `Program blocks\OP010\11_MES\Station3LoadData.xml`)
        *   `Station3UnLoadData` (Cesta: `Program blocks\OP010\11_MES\Station3UnLoadData.xml`)
        *   `Station4LoadData` (Cesta: `Program blocks\OP010\11_MES\Station4LoadData.xml`)
        *   `Station4UnLoadData` (Cesta: `Program blocks\OP010\11_MES\Station4UnLoadData.xml`)
        *   `Station5LoadData` (Cesta: `Program blocks\OP010\11_MES\Station5LoadData.xml`)
        *   `Station5UnLoadData` (Cesta: `Program blocks\OP010\11_MES\Station5UnLoadData.xml`)
        *   `Station6LoadData` (Cesta: `Program blocks\OP010\11_MES\Station6LoadData.xml`)
        *   `Station6UnLoadData` (Cesta: `Program blocks\OP010\11_MES\Station6UnLoadData.xml`)
        *   `Station7LoadData` (Cesta: `Program blocks\OP010\11_MES\Station7LoadData.xml`)
        *   `Station7UnLoadData` (Cesta: `Program blocks\OP010\11_MES\Station7UnLoadData.xml`)
        *   `Station8LoadData` (Cesta: `Program blocks\OP010\11_MES\Station8LoadData.xml`)
        *   `Station8UnLoadData` (Cesta: `Program blocks\OP010\11_MES\Station8UnLoadData.xml`)
*   **Hardware drivery a speciální zařízení:**
    *   `IAI_A1` (Cesta: `Program blocks\OP010\10_Device\22_IAI\IAI_A1.xml`)
    *   `IAI_A2` (Cesta: `Program blocks\OP010\10_Device\22_IAI\IAI_A2.xml`)
    *   `IAI_A3` (Cesta: `Program blocks\OP010\10_Device\22_IAI\IAI_A3.xml`)
    *   `IAI_DeviceCtl` (Cesta: `Program blocks\OP010\10_Device\22_IAI\IAI_DeviceCtl.xml`)
    *   `ModeDB` (Cesta: `Program blocks\OP010\10_Device\22_IAI\ModeDB.xml`)
    *   `ProcessData_1` (Cesta: `Program blocks\OP010\10_Device\23_Kistler\ProcessData_1.xml`)
    *   `KistlerPressData1` (Cesta: `Program blocks\OP010\10_Device\23_Kistler\Kistler1\KistlerPressData1.xml`)
    *   `KistlerPresser1_DB` (Cesta: `Program blocks\OP010\10_Device\23_Kistler\Kistler1\KistlerPresser1_DB.xml`)
    *   `KistlerPressData2` (Cesta: `Program blocks\OP010\10_Device\23_Kistler\Kistler2\KistlerPressData2.xml`)
    *   `KistlerPresser2_DB` (Cesta: `Program blocks\OP010\10_Device\23_Kistler\Kistler2\KistlerPresser2_DB.xml`)
    *   `Robot_DB` (Cesta: `Program blocks\OP010\10_Device\24_Robot\Robot_DB.xml`)
    *   `ServoV90_A1` (Cesta: `Program blocks\OP010\10_Device\25_V90\ServoV90_A1.xml`)
    *   `ServoV90_A2` (Cesta: `Program blocks\OP010\10_Device\25_V90\ServoV90_A2.xml`)
    *   `ServoV90_A3` (Cesta: `Program blocks\OP010\10_Device\25_V90\ServoV90_A3.xml`)
    *   `ServoV90_A4` (Cesta: `Program blocks\OP010\10_Device\25_V90\ServoV90_A4.xml`)
    *   `ServoV90_DeviceCtl` (Cesta: `Program blocks\OP010\10_Device\25_V90\ServoV90_DeviceCtl.xml`)
    *   `PilzData` (Cesta: `Program blocks\OP010\10_Device\27_Pilz\PilzData.xml`)
    *   `ST10_PLC_GetDB` (Cesta: `Program blocks\OP010\10_Device\09_CuringOven\ST10_PLC_GetDB.xml`)
    *   `ST10_PLC_PutDB` (Cesta: `Program blocks\OP010\10_Device\09_CuringOven\ST10_PLC_PutDB.xml`)

---

## Doporučený postup pro přepínání na optimalizovaný přístup

1.  **Zálohování projektu:** Vždy začněte kompletní zálohou projektu TIA Portal.
2.  **Začněte s nízkým rizikem (🟢):** Postupně přepínejte na optimalizovaný přístup datové bloky označené jako "Nízké riziko".
3.  **Kompilace projektu:** Po každém přepnutí jednoho nebo skupiny DB proveďte "Kompilovat vše (Rebuild All)" v TIA Portal. Pokud kód programu používá absolutní přístup k proměnným v přepnutém DB (např. `DB1.DBX0.0`), kompilátor vygeneruje chybu, kterou je třeba opravit (přepsat na symbolický přístup).
4.  **HMI/Externí přístup (🟡):** U DB ze skupiny "Střední riziko" je nezbytné před přepnutím zkontrolovat HMI obrazovky a veškerý externí software, který k těmto DB přistupuje. Ujistěte se, že používají symbolický přístup. Pokud ne, buď aktualizujte externí systémy, nebo ponechte DB ve standardním režimu.
5.  **Vysoké riziko (🔴):** DB ze skupiny "Vysoké riziko" by měly být ponechány ve standardním režimu, pokud nemáte absolutní jistotu, že jejich přepnutí nebude mít negativní dopad na komunikaci s externími zařízeními. Přepínání těchto DB vyžaduje hlubokou znalost interní logiky a použitých komunikačních mechanismů. V případě, že se rozhodnete takový DB přepnout, je nutné provést velmi důkladné testování všech souvisejících funkcí.
6.  **Testování:** Po jakékoli změně typu přístupu k DB vždy proveďte důkladné funkční testování PLC programu a všech dotčených externích rozhraní.
