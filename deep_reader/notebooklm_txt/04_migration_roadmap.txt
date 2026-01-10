# Migrační roadmapa + test plán + rollback plán

## Fáze A — Read-only zrcadlení (NEPORUŠIT)
### PROČ
- Centralizace monitoringu bez zásahu do řízení nebo HMI vazeb.

### CO (dotčené objekty)
- Přidat `DB_OP010_Monitoring` (+ volitelné UDT)
- Přidat `FC_MON_Mirror` (nebo ekvivalent) volaný z existujícího cyklického místa (typicky `OB1`/`ST10_Main`) jedním novým voláním.

### JAK (kroky)
1) Vytvořit nový DB + UDT.
2) Implementovat mirror s explicitními přiřazeními (bez nepřímého adresování).
3) Zavolat mirror z jednoho známého cyklického bodu.

### JAK OVĚŘIT
- Offline kompilace.
- Online download během odstávky.
- Watch table: porovnat vzorek signálů (legacy vs nový DB).
- Změřit dopad na cyklový čas.

### JAK VRÁTIT ZPĚT (ROLLBACK)
- Odebrat volání mirroru (nebo vypnout jedním enable bitem) a znovu nahrát.
- DB lze ponechat pro forenzní porovnání.

## Fáze B — Přepojení HMI (volitelné, po krocích)
### PROČ
- Zmenšení tag “sprawlu”, standardizace názvosloví.

### CO
- Mění se pouze HMI tag vazby (`ControllerTag`), PLC řízení zůstává beze změny.

### JAK
- Vytvořit nové (duplicitní) tagy na `DB_OP010_Monitoring`.
- Přepojovat obrazovky jednu po druhé.

### JAK OVĚŘIT
- Akceptační test obrazovka po obrazovce.
- Ověření alarmů/trendů (pokud se používají).

### JAK VRÁTIT ZPĚT
- Vrátit HMI `ControllerTag` na původní symboly.

## Fáze C — Úklid (POUZE po dlouhodobém ověření)
### PROČ
- Odstranění prokázaných duplikátů/mrtvých prvků.

### BRÁNA (GATE)
- 0 referencí v PLC + HMI + alarm/trend.
- Žádné riziko nepřímého přístupu.
