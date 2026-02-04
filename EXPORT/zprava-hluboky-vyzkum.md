```
A) [INVENTORY]
| Blok               | Typ | Jazyk | Memory Layout | Volá       |
|--------------------|-----|-------|---------------|------------|
| OB1                | OB  | LAD   | n/a           | -          |
| OB100 (Start-up)   | OB  | LAD   | n/a           | -          |
| ST10_Main          | FB  | LAD   | n/a           | OB1        |
| ST10_Input         | FC  | LAD   | n/a           | ST10_Main  |
| ST10_Output        | FC  | LAD   | n/a           | ST10_Main  |
| ST10_Manual        | FC  | LAD   | n/a           | ST10_Main  |
| ST10_ChangeOver    | FC  | LAD   | n/a           | ST10_Main  |
| ST10_Alarm        | FC  | LAD   | n/a           | ST10_Main  |
| ST10_Warning      | FC  | LAD   | n/a           | ST10_Main  |
| ST10_Tip          | FC  | LAD   | n/a           | ST10_Main  |
| DB_ST10_Global    | DB  |       | Standard      | ST10_Main / HMI |
| DB_ST10_Inputs    | DB  |       | Standard      | ST10_Input |
| DB_ST10_Outputs   | DB  |       | Standard      | ST10_Output |
*PŘEDPOKLAD:* Název a jazyk bloků je odvozen z kontextu (např. ST10_Main v LAD) – ověřit v XML exportu projektu. MemoryLayout pro původní DB je „Standard“ (legacy) – ověřit vlastnosti DB v TIA Openness exportu.

B) [LEGACY INTERFACE MAP]
- **Globální DB / tagy používané ve ST10_Main:** např. datablocky `DB_ST10_Global` (obsahuje EStopOK, GateOK, ServoReady apod.), `DB_ST10_Inputs` (příkazy z HMI: CmdNext, CmdPrev, CmdGoto), `DB_ST10_Outputs` (stavové signály do HMI: CurrentStep, Busy, Done).
- Příklad signálů:
  - `DB_ST10_Global.EStopOK` – vstup nouzového zastavení,
  - `DB_ST10_Global.GateClosed` – kontakty ochranných dveří,
  - `DB_ST10_Inputs.CmdNext`, `CmdPrev`, `CmdGoto` – ovládací příkazy od OIT/MES,
  - `DB_ST10_Outputs.CurrentStep`, `Done`, `Busy` – sdělení stavu zpět do OIT/MES.
*PŘEDPOKLAD:* Jména tagů jsou typická, verifikovat skutečná jména v `Symbols.xml` nebo datablocku.

C) [PROCESS STEPS]
1. **Krok 10 (Inicializace/Start):**  
   - *Entry:* spuštění sekvence (přepnutí do AutoRun, aktivace výstupů na safe pozici).  
   - *Podmínky:* všechny měniče mimo pohyb (ServoNotMoving=TRUE), E-STOP OK, dveře zavřené.  
   - *Done:* výstupy v základní poloze (všechny válce zasunuté, stojan otevřen).  
   - *Timeout:* pokud po ~5 s nedojde k inicializaci, vyhlásit chybu.  
   - *Fault:* jakákoliv nouzová situace (E-STOP apod.), nebo servo chybovost.  
2. **Krok 20 (Robot – pick up part):**  
   - *Entry:* požadavek posunout robot (např. CmdRobotPick=TRUE).  
   - *Podmínky:* servo dráha volná, robot připraven.  
   - *Done:* robot v požadované poloze (feedback RobotPosReached).  
   - *Timeout:* např. 10 s pro přemístění (jinak chybná akce).  
   - *Fault:* robot/servo selhání, přerušení bezpečnosti.  
3. **Krok 30 (Proces/Výstupní operace):**  
   - *Entry:* aktivace válce (ActivateCylinder=TRUE), uzavření vstupních dveří.  
   - *Podmínky:* senzor potvrdí dokončení (InputPartProcessed=TRUE).  
   - *Done:* proces dokončen (OutputPartReady=TRUE).  
   - *Timeout:* např. 5–10 s (záleží na průběhu operace).  
   - *Fault:* mechanická závada (válce se nezajel), porucha detekce.  
4. **Krok 40 (Robot – return/home):**  
   - *Entry:* příkaz vrátit robot (CmdRobotHome=TRUE).  
   - *Podmínky:* servo dráha volná, robot mohl dokončit práci.  
   - *Done:* robot na home pozici (RobotHomeReached=TRUE).  
   - *Timeout:* např. 10 s.  
   - *Fault:* robot uvízl, bezpečnostní přerušení.  
5. **Krok 50 (Konec cyklu):**  
   - *Entry:* signál CycleDone=TRUE (HMI/MES).  
   - *Podmínky:* všechny akce dokončeny.  
   - *Done:* sequencer nastaví výstupy do idle (CurrStep=0).  
   - *Timeout:* krátký (úklid signálů), příp. 5 s.  
   - *Fault:* -  

D) [NEW DESIGN]
- **Driver Layer:** samostatné FB pro každé zařízení (FB_Cylinder, FB_Stopper, FB_V90, FB_RobotIf apod.) s metodami (Move/Stop/Init). Modulární kód dle praxe【27†L158-L167】.  
- **Station Controller (Sequencer):** nový FB_OP010_Sequencer v SCL s `CASE Step OF...` strukturou (výstupy ovládány uvnitř každého kroku, ne externím porovnáváním kroku【23†L133-L142】). Každému kroku odpovídá sekvence ON_ENTRY, DO_EVERY_SCAN, ON_TIMEOUT, ON_EXIT pro jasnou logiku【35†L359-L368】【35†L370-L377】. Pro každý krok je implementován vlastní časovač pro timeout【23†L111-L119】.  
- **Handshaking:** signály do zařízení (valce, servo, robot) se předávají jako požadavky/Ack tokeny: při vstupu do kroku se inkrementuje `ReqID` a čeká se na `AckID`【14†L182-L190】【12†L53-L57】. Díky tomu není žádný jednorázový bit a minimalizují se závody.  
- **Robot Coordinator + RobotCtx:** pokud je více robotů nebo sdílené zóny, použije se FB_RobotCoordinator. Každý robot má vlastní `RobotCtx` UDT s poli `ReqID/AckID, Busy, InPosition` apod.  
- **Bridge (Legacy Interface):** zachováme původní DB/tagy pro HMI/MES, např. přemapujeme `ST10_Input/Output` do nových UDT (StationCtx) přes pomocný FB_IO_OP10. Legacy DB necháváme Standard (aby HMI/MES fungovalo beze změny).  

E) [CODE]
// UDT pro kontext stanice (stav, příkazy, časovače): včetně handshake polí ReqID/AckID.
```scl
TYPE UDT_StationCtx :
 STRUCT
  Step: INT;           // aktuální krok
  AutoRun: BOOL;       // AUTO/HOLD mód
  StepMode: BOOL;
  // Bezpečnostní vlajky:
  EStopOK: BOOL; 
  InterlockOK: BOOL; 
  ServoNotMoving: BOOL;
  RobotSafe: BOOL;
  // Handshake:
  ReqID: INT;
  AckID: INT;
  // Historie kroků (posledních N kroků)
  //History: ARRAY[0..9] OF INT;
  // Časovač pro timeout kroku:
  StepTimer: TIME;
  StepTimeout: TIME;
 END_STRUCT;
END_TYPE;

TYPE UDT_RobotCtx :
 STRUCT
  ReqID: INT;       // požadavek z sequenceru
  AckID: INT;       // potvrzení od robotu
  Busy: BOOL;       // robot v pohybu
  InPosition: BOOL; // robot dojel
 END_STRUCT;
END_TYPE;
```
(* Příklad SCL FB sekvenceru: použití `CASE Step OF`【30†L216-L224】, struktury ON_ENTRY/ON_EXIT【35†L370-L377】 a handshake pomocí ReqID/AckID【14†L182-L190】. *)

```scl
FUNCTION_BLOCK FB_OP010_Sequencer
 VAR_INPUT
  CmdNext : BOOL;    // ruční/příkaz další krok
  CmdPrev : BOOL;    // ruční/předchozí krok
  CmdGoto : INT;     // přímý výběr kroku
  AutoRun : BOOL;
  StepMode: BOOL;
 END_VAR
 VAR_IN_OUT
  StationCtx: UDT_StationCtx;  // stav sekvenceru
  RobotCtx  : UDT_RobotCtx;
 END_VAR
 VAR
  prevStep: INT := -1;
 END_VAR

// Struktura stavu: ON_ENTRY, DO_EVERY_SCAN, ON_TIMEOUT, ON_EXIT dle doporučení【35†L359-L368】【35†L370-L377】 
BEGIN
 CASE StationCtx.Step OF
  10: // Krok 10 – inicializace
     IF StationCtx.Step <> prevStep THEN
       // ON_ENTRY:
       StationCtx.ReqID := StationCtx.ReqID + 1;    // požadavek na reset zařízení
       prevStep := StationCtx.Step;
       StationCtx.StepTimer := T#0S;                // reset timeout
     END_IF;
     // DO_EVERY_SCAN: čekáme na potvrzení
     IF StationCtx.AckID = StationCtx.ReqID THEN
       StationCtx.Step := 20;  // přechod do dalšího kroku
     END_IF;
     // ON_TIMEOUT:
     IF StationCtx.StepTimer > StationCtx.StepTimeout THEN
       // nastavit chybu (např. -> StationCtx.Fault)
     END_IF;
  20: // Krok 20 – pohyb robota pro vyjmutí dílu
     IF StationCtx.Step <> prevStep THEN
       // ON_ENTRY:
       StationCtx.ReqID := StationCtx.ReqID + 1;    // požadavek na posun robota
       prevStep := StationCtx.Step;
       StationCtx.StepTimer := T#0S;
     END_IF;
     IF StationCtx.AckID = StationCtx.ReqID THEN
       StationCtx.Step := 30;
     END_IF;
     IF StationCtx.StepTimer > StationCtx.StepTimeout THEN
       // Timeout chyby
     END_IF;
  // ... další kroky 30, 40, 50 analogicky ...
 END_CASE;
END_FUNCTION_BLOCK;
```

F) [MIGRATION PLAN]
1. **Nové bloky:** vytvořit UDT_StationCtx, UDT_RobotCtx a FB_OP010_Sequencer (dle bodu E). Tyto moduly lze samostatně otestovat bez zásahu do legacy kódu【27†L158-L167】.  
2. **Legacy beze změny:** první fáze ponechat stávající ST10_Main/Input/Output sítě aktivní, nasadit nové FB paralelně. Mapování mezi starými DB a novým UDT uděláme skrze FB_IO_OP10 a kopii logiky v OB1 (zachovat stávající datablocky).  
3. **Přesměrování volání:** po ověření FB_OP010_Sequencer změnit OB1 tak, aby volal nový FB (např. místo ST10_Main zavolá FB_OP010_Sequencer). Staré sítě ST10_* během testů ponechat jako zálohu (Alarm/HMI).  
4. **Finální přechod:** kompletně deaktivovat původní sekvenční logiku (ST10_Main atd.) a potvrdit, že veškeré bity pro HMI/MES jsou namapovány na nové `StationCtx` a `RobotCtx` UDT. Ponechat staré DB v režimu read-only pro MES (MAP).  

Všechna stávající OB/FB/DB, které nezměníme, zůstanou v proceduře beze změny; nové bloky budou moduly obalené kolem nich nebo paralelně. Migraci nasadit ve třech krocích: nejprve testované rozšíření, pak přesměrování, nakonec úklid legacy kódu【27†L158-L167】.
```

