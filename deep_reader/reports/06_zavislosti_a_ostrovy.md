# Závislosti programu (orientačně) + izolované ostrovy

## FAKTA

- Počet OB (kořeny): `10`
- Extrahované hrany volání: `103`
- Bloky dosažitelné z OB (dle extrahovaných volání): `92`
- FC/FB nedosažitelné z OB (kandidáti na izolované ostrovy): `25`

## OMEZENÍ

- Toto je graf pouze z `CallInfo`/FlgNet + částečně ze StructuredText tokenů; STL/GRAPH může obsahovat logiku, která se zde neprojeví.

- Nedosažitelnost v tomto reportu ≠ “mrtvé”; je to pouze kandidát k ověření.

## IZOLOVANÉ OSTROVY (seskupení nedosažitelných FC/FB)

### Ostrov 1 (počet bloků: 2)
- `FB_Stopper` | voláno z: `ST10_Stopper_FB`
- `ST10_Stopper_FB` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 2 (počet bloků: 2)
- `ST10_StopperCtrl` | voláno z: (nikdo v extrahovaných datech)
- `StopperCtrl` | voláno z: `ST10_StopperCtrl`

### Ostrov 3 (počet bloků: 1)
- `ChangeOver` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 4 (počet bloků: 1)
- `CheckPositioningOrder` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 5 (počet bloků: 1)
- `CylinderModule_V2` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 6 (počet bloků: 1)
- `DT-Chars` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 7 (počet bloků: 1)
- `FB_Analog` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 8 (počet bloků: 1)
- `FB_AteqF620` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 9 (počet bloků: 1)
- `FB_Keyence_SR1000` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 10 (počet bloků: 1)
- `FB_Next` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 11 (počet bloků: 1)
- `FB_Step` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 12 (počet bloků: 1)
- `IAI_BASE_FB` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 13 (počet bloků: 1)
- `MaterialGate` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 14 (počet bloků: 1)
- `PartDataManage` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 15 (počet bloků: 1)
- `ST10Cyl_interface91-100` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 16 (počet bloků: 1)
- `ST10_Analog` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 17 (počet bloků: 1)
- `ST10_PartData` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 18 (počet bloků: 1)
- `ST10_SafetyGate` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 19 (počet bloků: 1)
- `SafetyGate` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 20 (počet bloků: 1)
- `SevroStart&PosCheck` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 21 (počet bloků: 1)
- `SevroStart&PosCheck_IAI` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 22 (počet bloků: 1)
- `fcFixtureCheck` | voláno z: (nikdo v extrahovaných datech)

### Ostrov 23 (počet bloků: 1)
- `块_1` | voláno z: (nikdo v extrahovaných datech)
