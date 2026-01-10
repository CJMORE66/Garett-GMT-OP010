# Nevolané bloky – hledání „dvojčat“
Cíl: pro každý blok označený jako nevolaný najít pravděpodobné kopie/varianty, které jsou volané.
Pozn.: „volané“ zde znamená, že se blok objevil jako `callee` v `deep_reader/out/call_edges.csv`.

## `MaterialGate`
- Typ: SW.Blocks.FB, jazyk: LAD, číslo: 5210
- Zdroj: EXPORT/Program blocks/03_Device/102 SafetyGate/MaterialGate.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

## `ST10_SafetyGate`
- Typ: SW.Blocks.FC, jazyk: SCL, číslo: 1140
- Zdroj: EXPORT/Program blocks/OP010/10_Device/03_SafetyGate/ST10_SafetyGate.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
**Silná shoda názvu (pravděpodobná varianta/kopie):**
- `SafetyGate` (match=no_ctrl, in-degree=0, reachable=NE/NEJISTÉ)

## `ST10_StopperCtrl`
- Typ: SW.Blocks.FB, jazyk: LAD, číslo: 2601
- Zdroj: EXPORT/Program blocks/OP010/10_Device/26_Stopper/ST10_StopperCtrl.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
**Silná shoda názvu (pravděpodobná varianta/kopie):**
- `ST10_Stopper_FB` (match=no_ctrl, in-degree=0, reachable=NE/NEJISTÉ)
- `Stopper` (match=no_ctrl, in-degree=1, reachable=ANO)
- `StopperCtrl` (match=no_ctrl, in-degree=1, reachable=NE/NEJISTÉ)

## `ST10_Stopper_FB`
- Typ: SW.Blocks.FB, jazyk: LAD, číslo: 1160
- Zdroj: EXPORT/Program blocks/OP010/10_Device/06_Stopper/ST10_Stopper_FB.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
**Silná shoda názvu (pravděpodobná varianta/kopie):**
- `ST10_StopperCtrl` (match=no_ctrl, in-degree=0, reachable=NE/NEJISTÉ)
- `Stopper` (match=no_ctrl, in-degree=1, reachable=ANO)
- `StopperCtrl` (match=no_ctrl, in-degree=1, reachable=NE/NEJISTÉ)

## `SafetyGate`
- Typ: SW.Blocks.FB, jazyk: LAD, číslo: 5200
- Zdroj: EXPORT/Program blocks/03_Device/102 SafetyGate/SafetyGate.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
**Silná shoda názvu (pravděpodobná varianta/kopie):**
- `ST10_SafetyGate` (match=no_ctrl, in-degree=0, reachable=NE/NEJISTÉ)

## `ChangeOver`
- Typ: SW.Blocks.FC, jazyk: SCL, číslo: 3002
- Zdroj: EXPORT/Program blocks/02_Comm/04-ChangeOver/ChangeOver.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
**Silná shoda názvu (pravděpodobná varianta/kopie):**
- `ST10_ChangeOver` (match=no_ctrl, in-degree=1, reachable=ANO)

## `CheckPositioningOrder`
- Typ: SW.Blocks.FB, jazyk: LAD, číslo: 1
- Zdroj: EXPORT/Program blocks/OP010/10_Device/25_V90/Patch/CheckPositioningOrder.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

## `CylinderModule_V2`
- Typ: SW.Blocks.FC, jazyk: LAD, číslo: 3010
- Zdroj: EXPORT/Program blocks/03_Device/101_Cylinder/CylinderModule_V2.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
**Silná shoda názvu (pravděpodobná varianta/kopie):**
- `CylinderCtrl_V2` (match=no_ctrl, in-degree=1, reachable=ANO)
- `ST10Cylinder` (match=no_ctrl, in-degree=0, reachable=NE/NEJISTÉ)

**Shoda názvu + podobnost tokenů (heuristika):**
- `CylinderCtrl_V2` score=0.53 (in-degree=1, reachable=ANO)

## `DT-Chars`
- Typ: SW.Blocks.FB, jazyk: SCL, číslo: 2360
- Zdroj: EXPORT/Program blocks/OP010/11_MES/DT-Chars.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

## `FB_Analog`
- Typ: SW.Blocks.FB, jazyk: LAD, číslo: 4090
- Zdroj: EXPORT/Program blocks/03_Device/212 Analog/FB_Analog.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
**Silná shoda názvu (pravděpodobná varianta/kopie):**
- `ST10_Analog` (match=no_ctrl, in-degree=0, reachable=NE/NEJISTÉ)

## `FB_AteqF620`
- Typ: SW.Blocks.FB, jazyk: SCL, číslo: 4080
- Zdroj: EXPORT/Program blocks/03_Device/211 ATEQ LeakTest/FB_AteqF620.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

## `FB_Keyence_SR1000`
- Typ: SW.Blocks.FB, jazyk: SCL, číslo: 1230
- Zdroj: EXPORT/Program blocks/03_Device/214_KeyenceSR X80/FB_Keyence_SR1000.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
**Silná shoda názvu (pravděpodobná varianta/kopie):**
- `KeyenceSR1000Ctrl` (match=no_ctrl, in-degree=1, reachable=ANO)
- `ST_KeyenceSR1000` (match=no_ctrl, in-degree=0, reachable=NE/NEJISTÉ)

## `FB_Next`
- Typ: SW.Blocks.FB, jazyk: SCL, číslo: 42
- Zdroj: EXPORT/Program blocks/03_Device/999 Base/999.0 General/999.0.3 FB/FB_Next.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

## `FB_Step`
- Typ: SW.Blocks.FB, jazyk: LAD, číslo: 5002
- Zdroj: EXPORT/Program blocks/03_Device/999 Base/FB_Step.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

## `IAI_BASE_FB`
- Typ: SW.Blocks.FB, jazyk: SCL, číslo: 2201
- Zdroj: EXPORT/Program blocks/OP010/10_Device/22_IAI/IAI_BASE_FB.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

## `PartDataManage`
- Typ: SW.Blocks.FB, jazyk: SCL, číslo: 2
- Zdroj: EXPORT/Program blocks/03_Device/104 PartDataManage/PartDataManage.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

## `ST10Cyl_interface91-100`
- Typ: SW.Blocks.FC, jazyk: LAD, číslo: 1029
- Zdroj: EXPORT/Program blocks/OP010/10_Device/01_Cylinder/ST10Cyl_interface91-100.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

## `ST10_Analog`
- Typ: SW.Blocks.FC, jazyk: SCL, číslo: 1080
- Zdroj: EXPORT/Program blocks/OP010/10_Device/08_PressureAanlog/ST10_Analog.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
**Silná shoda názvu (pravděpodobná varianta/kopie):**
- `FB_Analog` (match=no_ctrl, in-degree=0, reachable=NE/NEJISTÉ)

## `ST10_PartData`
- Typ: SW.Blocks.FC, jazyk: SCL, číslo: 1500
- Zdroj: EXPORT/Program blocks/OP010/12_PartData/ST10_PartData.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

## `SevroStart&PosCheck`
- Typ: SW.Blocks.FB, jazyk: LAD, číslo: 4073
- Zdroj: EXPORT/Program blocks/OP010/10_Device/25_V90/V90_Standard/ServoCheck/SevroStart&PosCheck.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

## `SevroStart&PosCheck_IAI`
- Typ: SW.Blocks.FB, jazyk: LAD, číslo: 2209
- Zdroj: EXPORT/Program blocks/OP010/10_Device/22_IAI/ServoCheck/SevroStart&PosCheck_IAI.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

## `fcFixtureCheck`
- Typ: SW.Blocks.FC, jazyk: LAD, číslo: 2
- Zdroj: EXPORT/Program blocks/03_Device/100 FixtureCheck/fcFixtureCheck.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

## `块_1`
- Typ: SW.Blocks.FC, jazyk: LAD, číslo: 1
- Zdroj: EXPORT/Program blocks/OP010/10_Device/25_V90/Patch/块_1.xml
- In-degree (důkaz příchozích volání): 0
- Reachable z OB (z extrahovaného grafu): NE/NEJISTÉ

### Podezření na dvojčata
- Nenašel jsem žádné jasné dvojče podle názvu ani obsahu.

