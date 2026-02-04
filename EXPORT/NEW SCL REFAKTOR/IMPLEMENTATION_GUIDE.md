# Implementační manuál pro refaktoring OP10

Tento dokument popisuje, jak integrovat nové SCL bloky do projektu TIA Portal.

## 1. Import bloků do TIA Portalu

1.  Otevřete projekt v TIA Portalu.
2.  Ve stromu projektu přejděte na `External Source Files`.
3.  Klikněte pravým tlačítkem -> `Add new external file`.
4.  Vyberte soubory ze složky `NEW SCL REFAKTOR`:
    *   `FB_OP010_Sequencer.scl`
    *   `FB_NG_Box_Control.scl`
5.  Klikněte pravým tlačítkem na importované soubory -> `Generate blocks from source`.

## 2. Integrace sekvenceru (`FB_OP010_Sequencer`)

Tento blok nahrazuje staré krokování.

### Zapojení v hlavním programu (např. OB1 nebo Main FB):

```scl
"FB_OP010_Sequencer_DB"(
    iEStopOK := "iEStopPB",                // Bezpečnostní okruh
    iInterlockOK := "Global_Interlock",    // Všechny brány zavřené atd.
    iModeAuto := "Station_Sys".Auto.Mode,  // Auto režim
    iModeStep := "Station_Sys".Manual.Mode,// Krok režim (nebo StepMode signál)
    iCmdNext := "HMI_Btn_Next",            // Tlačítko Další krok
    iCmdPrev := "HMI_Btn_Prev",            // Tlačítko Zpět
    iCmdGoto := "HMI_Btn_Goto",            // Tlačítko Skok
    iGotoStepID := "HMI_Int_TargetStep",   // Cílový krok
    iSeqPausedByNG := "FB_NG_Boxes_Main_DB".out_Request_to_open // Propojení s NG boxy
);

// Výstup kroku pro ostatní části logiky
"ActualStep" := "FB_OP010_Sequencer_DB".oStep;
```

## 3. Integrace NG Boxů (`FB_NG_Boxes_Main`)

Tento blok spravuje NG boxy a žádá sekvencer o zastavení, pokud obsluha zmáčkne tlačítko.

### Zapojení:

```scl
"FB_NG_Boxes_Main_DB"(
    in_Permission_to_Open := "FB_OP010_Sequencer_DB".oInPosition_111
);

// Poznámka: Fyzické vstupy/výstupy (senzory, tlačítka) jsou mapovány uvnitř FB.
// Pokud se změní názvy tagů (např. "iE1-Unloading..."), je nutné je upravit přímo v SCL souboru.
```

## 4. Testování

### Test bezpečného návratu (Reverse Logic)
1.  Spusťte stroj v krokovém režimu.
2.  Dostaňte se např. do kroku 60 (Lisování).
3.  Stiskněte `Prev` (Zpět).
4.  Očekávané chování:
    *   `SafeBaselineActive` se nastaví na TRUE (Krok 0).
    *   Stroj zastaví všechny pohyby (nutno dopsat logiku do Kroku 0!).
    *   Po splnění podmínek (serva stojí) skočí do kroku 20 (nebo 10, dle mapy).

### Test NG Boxů
1.  Během auto cyklu stiskněte tlačítko na NG Boxu.
2.  Tlačítko začne blikat (požadavek přijat).
3.  Sekvence dojede do kroku 111 (po lepení) a zastaví se.
4.  Zámek boxu se otevře.
5.  Po zavření a potvrzení tlačítkem se sekvence opět rozjede.

## 5. Důležité upozornění
V bloku `FB_OP010_Sequencer` je v sekci `SafeBaseline` (Krok 0) komentář:
`// TODO: Write outputs to force safe state here`
**Zde musíte doplnit kód, který explicitně vypne/resetuje výstupy všech válců a zastaví serva!** Bez toho není funkce "Safe Goto" bezpečná.
