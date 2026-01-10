# Migrace safety: PILZ PNOZmulti → Siemens SIMATIC F-CPU (specifikace)

## FAKTA

- Čas generování: `2026-01-09 18:06:23`
- Zdrojový inventář: `deep_reader/reports/pilz_safety_devices.csv` + `deep_reader/reports/pilz_io_map.csv`
- Safety funkce v Pilz exportu: `41` instancí
- I/O proměnné v Pilz exportu: `76` (`vstupy≈44`, `výstupy≈20`, ostatní `12`)

## ZÁSADNÍ BEZPEČNOSTNÍ UPOZORNĚNÍ

- Převod safety relé/PNOZ logiky na F-CPU je **bezpečnostně kritická změna**: vyžaduje znovu provést analýzu rizik (PL/SIL), validaci, dokumentaci a řízenou odstávku.
- Tento dokument je **specifikace a mapování** pro implementaci; není to hotový safety program.

## Co umíme prokázat z dodaných souborů (evidence)

- Seznam safety funkčních bloků/instancí a jejich připojené I/O kanály (např. E-STOP má 2 kanály).
- Názvy signálů (překlady) + jejich OPC cesty (diagnostika/visu).
- Neumíme prokázat: **vnitřní propojení** mezi bloky (muting, reset priority, EDM vazby, logické OR/AND mezi zónami) – v exportu chybí síťová logika.

## Inventář bezpečnostních funkcí (souhrn)

| Typ (Pilz) | Počet | Poznámka |
|---|---:|---|
| `SEMICONDUCTOR` | `11` | Bezpečný výstup / odpojování (pravděpodobně přes stykač/SSR + EDM). |
| `COPY_MODULE_INPUT_BLOCK` | `10` | Zpětná vazba (feedback) / přenesení vstupu do diagnostiky. |
| `SAFETY_GATE` | `10` | Bezpečnostní dveře/vrata (2-kanálové vstupy). |
| `E_STOP` | `5` | Nouzové zastavení (2-kanálové vstupy). |
| `LIGHT_CURTAIN` | `2` | Světelná závora (2-kanálové vstupy). |
| `TIP_SWITCH` | `2` |  |
| `RS_FLIP_FLOP` | `1` |  |

## Mapování I/O (moduly)

### Modul `85A1`
| VarRef | Název | OPC |
|---|---|---|
| `85A1.IM0` | `HMI_Control On` | `GarretPilz_Op10_20250814/Generic/IM/0.0` |
| `85A1.IM1` | `HMI_Control Off` | `GarretPilz_Op10_20250814/Generic/IM/0.1` |
| `85A1.IM16` | `Feedback Loop3(Light Current1)` | `GarretPilz_Op10_20250814/Generic/IM/0.16` |
| `85A1.IM17` | `Feedback Loop3(Light Current2)` | `GarretPilz_Op10_20250814/Generic/IM/0.17` |
| `85A1.IM18` | `Feedback Loop4(StoveE-Stop)` | `GarretPilz_Op10_20250814/Generic/IM/0.18` |
| `85A1.IM19` | `` | `GarretPilz_Op10_20250814/Generic/IM/0.19` |
| `85A1.IM2` | `HMI_Reset` | `GarretPilz_Op10_20250814/Generic/IM/0.2` |
| `85A1.IM3` | `PLC signal` | `GarretPilz_Op10_20250814/Generic/IM/0.3` |
| `85A1.T0M20` | `` | `GarretPilz_Op10_20250814/Generic/TM/0.20` |
| `85A1.T1M21` | `` | `GarretPilz_Op10_20250814/Generic/TM/0.21` |
| `85A1.T2M22` | `` | `GarretPilz_Op10_20250814/Generic/TM/0.22` |
| `85A1.T3M23` | `` | `GarretPilz_Op10_20250814/Generic/TM/0.23` |
| `85A1.i10` | `Light Current2.1` | `GarretPilz_Op10_20250814/Generic/I/0.10` |
| `85A1.i11` | `Light Current2.2` | `GarretPilz_Op10_20250814/Generic/I/0.11` |
| `85A1.i12` | `StoveE-Stop2.1` | `GarretPilz_Op10_20250814/Generic/I/0.12` |
| `85A1.i13` | `StoveE-Stop2.2` | `GarretPilz_Op10_20250814/Generic/I/0.13` |
| `85A1.i14` | `Feedback Loop1(E-stop)` | `GarretPilz_Op10_20250814/Generic/I/0.14` |
| `85A1.i15` | `Feedback Loop2(Safety Gate)` | `GarretPilz_Op10_20250814/Generic/I/0.15` |
| `85A1.i4` | `E-Stop 1.1` | `GarretPilz_Op10_20250814/Generic/I/0.4` |
| `85A1.i5` | `E-Stop 1.2` | `GarretPilz_Op10_20250814/Generic/I/0.5` |
| `85A1.i6` | `SafetyGate 1.1` | `GarretPilz_Op10_20250814/Generic/I/0.6` |
| `85A1.i7` | `SafetyGate 1.2` | `GarretPilz_Op10_20250814/Generic/I/0.7` |
| `85A1.i8` | `Light Current1.1` | `GarretPilz_Op10_20250814/Generic/I/0.8` |
| `85A1.i9` | `Light Current1.2` | `GarretPilz_Op10_20250814/Generic/I/0.9` |
| `85A1.o0` | `Emergency Cut off` | `GarretPilz_Op10_20250814/Generic/O/0.0` |
| `85A1.o1` | `Safety Door Cut off` | `GarretPilz_Op10_20250814/Generic/O/0.1` |
| `85A1.o2` | `Light Current1 Cut Off` | `GarretPilz_Op10_20250814/Generic/O/0.2` |
| `85A1.o3` | `Light Current2 Cut Off` | `GarretPilz_Op10_20250814/Generic/O/0.3` |

### Modul `85A2`
| VarRef | Název | OPC |
|---|---|---|
| `85A2.i0` | `Material door 1.1` | `GarretPilz_Op10_20250814/Generic/I/1.0` |
| `85A2.i1` | `Material door 1.2` | `GarretPilz_Op10_20250814/Generic/I/1.1` |
| `85A2.i2` | `Material door 2.1` | `GarretPilz_Op10_20250814/Generic/I/1.2` |
| `85A2.i3` | `Material door 2.2` | `GarretPilz_Op10_20250814/Generic/I/1.3` |
| `85A2.i4` | `Material door 3.1` | `GarretPilz_Op10_20250814/Generic/I/1.4` |
| `85A2.i5` | `Material door 3.2` | `GarretPilz_Op10_20250814/Generic/I/1.5` |
| `85A2.i6` | `Material door 4.1` | `GarretPilz_Op10_20250814/Generic/I/1.6` |
| `85A2.i7` | `Material door 4.2` | `GarretPilz_Op10_20250814/Generic/I/1.7` |
| `85A2.o0` | `Material door 1Cut off` | `GarretPilz_Op10_20250814/Generic/O/1.0` |
| `85A2.o1` | `Material door 2Cut off` | `GarretPilz_Op10_20250814/Generic/O/1.1` |
| `85A2.o2` | `Material door 3Cut off` | `GarretPilz_Op10_20250814/Generic/O/1.2` |
| `85A2.o3` | `Material door 4Cut off` | `GarretPilz_Op10_20250814/Generic/O/1.3` |

### Modul `85A3`
| VarRef | Název | OPC |
|---|---|---|
| `85A3.i0` | `Material door1 Feedback` | `GarretPilz_Op10_20250814/Generic/I/2.0` |
| `85A3.i1` | `Material door2 Feedback` | `GarretPilz_Op10_20250814/Generic/I/2.1` |
| `85A3.i2` | `Material door3 Feedback` | `GarretPilz_Op10_20250814/Generic/I/2.2` |
| `85A3.i3` | `Material door4 Feedback` | `GarretPilz_Op10_20250814/Generic/I/2.3` |
| `85A3.i4` | `Stove door Feedback1` | `GarretPilz_Op10_20250814/Generic/I/2.4` |
| `85A3.i5` | `Stove door Feedback2` | `GarretPilz_Op10_20250814/Generic/I/2.5` |
| `85A3.i6` | `RobotFeedback` | `GarretPilz_Op10_20250814/Generic/I/2.6` |
| `85A3.i7` | `RobotDoorFeedback` | `GarretPilz_Op10_20250814/Generic/I/2.7` |
| `85A3.o0` | `Stove Cut off` | `GarretPilz_Op10_20250814/Generic/O/2.0` |
| `85A3.o1` | `RobotEstop Cut off` | `GarretPilz_Op10_20250814/Generic/O/2.1` |
| `85A3.o2` | `RobotSafetyDoor Cut off` | `GarretPilz_Op10_20250814/Generic/O/2.2` |
| `85A3.o3` | `` | `GarretPilz_Op10_20250814/Generic/O/2.3` |

### Modul `85A4`
| VarRef | Název | OPC |
|---|---|---|
| `85A4.i0` | `Material door 2.1` | `GarretPilz_Op10_20250814/Generic/I/3.0` |
| `85A4.i1` | `Material door 2.2` | `GarretPilz_Op10_20250814/Generic/I/3.1` |
| `85A4.i2` | `Material door 4.1` | `GarretPilz_Op10_20250814/Generic/I/3.2` |
| `85A4.i3` | `Material door 4.2` | `GarretPilz_Op10_20250814/Generic/I/3.3` |
| `85A4.i4` | `Material door 6.1` | `GarretPilz_Op10_20250814/Generic/I/3.4` |
| `85A4.i5` | `Material door 6.2` | `GarretPilz_Op10_20250814/Generic/I/3.5` |
| `85A4.i6` | `E-NG-02-Safety Gate` | `GarretPilz_Op10_20250814/Generic/I/3.6` |
| `85A4.i7` | `E-NG-02-Safety Gate` | `GarretPilz_Op10_20250814/Generic/I/3.7` |
| `85A4.o0` | `` | `GarretPilz_Op10_20250814/Generic/O/3.0` |
| `85A4.o1` | `` | `GarretPilz_Op10_20250814/Generic/O/3.1` |
| `85A4.o2` | `` | `GarretPilz_Op10_20250814/Generic/O/3.2` |
| `85A4.o3` | `` | `GarretPilz_Op10_20250814/Generic/O/3.3` |

### Modul `85A5`
| VarRef | Název | OPC |
|---|---|---|
| `85A5.i0` | `Estop Robot1.1` | `GarretPilz_Op10_20250814/Generic/I/4.0` |
| `85A5.i1` | `Estop Robot1.2` | `GarretPilz_Op10_20250814/Generic/I/4.1` |
| `85A5.i2` | `Estop Robot2.1` | `GarretPilz_Op10_20250814/Generic/I/4.2` |
| `85A5.i3` | `Estop Robot2.2` | `GarretPilz_Op10_20250814/Generic/I/4.3` |
| `85A5.i4` | `Estop Robot3.1` | `GarretPilz_Op10_20250814/Generic/I/4.4` |
| `85A5.i5` | `Estop Robot3.2` | `GarretPilz_Op10_20250814/Generic/I/4.5` |
| `85A5.i6` | `E-NG-01-Safety Gate` | `GarretPilz_Op10_20250814/Generic/I/4.6` |
| `85A5.i7` | `E-NG-01-Safety Gate` | `GarretPilz_Op10_20250814/Generic/I/4.7` |
| `85A5.o0` | `` | `GarretPilz_Op10_20250814/Generic/O/4.0` |
| `85A5.o1` | `` | `GarretPilz_Op10_20250814/Generic/O/4.1` |
| `85A5.o2` | `` | `GarretPilz_Op10_20250814/Generic/O/4.2` |
| `85A5.o3` | `` | `GarretPilz_Op10_20250814/Generic/O/4.3` |

## Doporučené konceptuální mapování na Siemens Safety (bez kódu)

Níže je doporučené mapování typů (koncept). Konkrétní parametry/časování musí potvrdit safety dokumentace stroje a komisionační testy.

| Typ (Pilz) | Typický ekvivalent v Siemens Safety | Poznámka |
|---|---|---|
| `E_STOP` | `F_ESTOP` / `F_EmergencyStop` (knihovna Safety Advanced) | 2-kanál, test zkratu/rozporu, reset logika dle požadavků. |
| `SAFETY_GATE` | `F_DOOR` / `F_Gate` | 2-kanál, může být s/bez blokování, reset/ack dle zóny. |
| `LIGHT_CURTAIN` | `F_LightCurtain` / `F_SafetySensor` | 2-kanál OSSD, případně muting (pokud existuje – zde neprokázáno). |
| `SEMICONDUCTOR` | `F_Q` + `F_FDBK` (EDM) / bezpečný výstup | Vyžaduje definovat, co se odpojuje (stykače, STO, ventily) a jak se kontroluje zpětná vazba. |
| `COPY_MODULE_INPUT_BLOCK` | Diagnostika/EDM vstupy, mapování do standard PLC | V Siemens často zvlášť: bezpečný vstup pro EDM + standardní diagnostické bity. |

## Minimální validační plán (musí být splněno před nasazením)

1) Offline: porovnat všechny bezpečnostní funkce s aktuální bezpečnostní dokumentací stroje (risk assessment, safety matrix).
2) Offline: simulace / Safety Acceptance Test (SAT) pro každý bezpečnostní okruh (E-stop, dveře, světelná závora, robot dveře, materiálové dveře).
3) Online v odstávce: test každého kanálu zvlášť (CH1/CH2), test rozporu kanálů, test resetu, test EDM (zaseknutý stykač).
4) Důkaz: protokol testů + sign-off kompetentní osoby.

## Open questions (blokující pro vytvoření 1:1 chování)

- Kde je v Pilz projektu export **logického propojení** mezi bloky (graf/schéma)? Bez toho nelze prokázat přesné vazby (např. které dveře vypínají které výstupy).
- Jaké jsou požadované úrovně bezpečnosti (PL/SIL) pro jednotlivé okruhy a jaké jsou požadované reakční časy?
- Jaké výstupy PNOZ skutečně odpojují energii (stykače, STO na servu, ventily) a jaké jsou jejich EDM zpětné vazby?
