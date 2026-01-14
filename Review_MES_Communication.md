# Revize rozhraní MES (Manufacturing Execution System)

Tento dokument shrnuje kritickou revizi komunikace mezi PLC a MES systémem.

## 🔍 Hlavní nálezy

### 1. Handshake mechanismus
*   **Stav:** Aktuálně řešeno pomocí izolovaných bitů v ploché struktuře (např. `Station1ChickInReq`).
*   **Problém:** Vysoké riziko "Race Condition" (souběhu signálů). PLC nemá jistotu, že odpověď z MES patří k aktuálnímu požadavku. Chybí unikátní identifikátor transakce.
*   **Důsledek:** Možnost záměny dat u po sobě jdoucích palet při výpadku sítě nebo restartu systému.

### 2. Jednosměrné `MES.Cycle_ID` (Klíčový nález o Race Condition)
*   **Stav:** `MES.Cycle_ID` (DInt) je nalezeno v datových blocích `StationXLoadData` (data posílaná do MES).
*   **Problém:** V odpovídajících datových blocích `StationXUnLoadData` (výsledky operací z MES) **chybí jakákoliv proměnná, která by toto `Cycle_ID` vracela zpět (tzv. "mirroring")**.
*   **Důsledek:** PLC nemá možnost ověřit, zda přijatá odpověď OK/NG z MES skutečně patří k poslednímu odeslanému požadavku. Systém se spoléhá na perfektní časovou synchronizaci a absenci zpoždění, což je v reálném provozu nereálné. V případě opožděné odezvy z MES (např. kvůli lagování sítě nebo přetížení serveru) může dojít k přiřazení výsledku (např. NG) k nesprávné paletě, která je právě zpracovávána.
*   **Příklad scénáře:** PLC pošle `Request` s `Cycle_ID=501`. MES se zpozdí. Mezitím přijede další paleta a PLC pošle `Request` s `Cycle_ID=502`. V tu chvíli přijde opožděná odpověď pro `Cycle_ID=501`. Bez vráceného ID si PLC myslí, že se jedná o odpověď pro `Cycle_ID=502`, což vede k chybnému vyhodnocení.
*   **Doporučení:** Rozšířit `StationXUnLoadData` o proměnnou (např. `MES.Mirror_Cycle_ID` typu DInt), do které bude MES kopírovat přijaté `Cycle_ID`. PLC pak musí před akceptací výsledku vždy porovnat `StationXLoadData.MES.Cycle_ID` s `StationXUnLoadData.MES.Mirror_Cycle_ID`.

### 3. Diagnostika a chyby
*   **Stav:** Rozhraní vrací pouze binární informaci OK/NG.
*   **Problém:** Pokud MES požadavek zamítne (např. paleta nebyla na předchozí operaci), operátor se nedozví důvod.
*   **Doporučení:** Rozšířit rozhraní o `ResultCode` (Int), kde MES předá kód specifické chyby.

### 3. Kvalita kódu a organizace
*   **Stav:** Názvosloví obsahuje překlepy (`ChickIn` místo `CheckIn`) a velké množství nevyužitých rezerv (`Spare_X`).
*   **Problém:** Ztížená údržba a vyhledávání v projektu.
*   **Doporučení:** Refaktorovat rozhraní do strukturovaných polí (Array of UDT).

## ✅ Navržená architektura (Best Practice)

Namísto stávajícího řešení doporučuji strukturu:
1. **Request (PLC):** Nastaví bit požadavku a unikátní ID.
2. **Busy (MES):** MES potvrdí přijetí požadavku.
3. **Done (MES):** MES dokončí operaci a nastaví OK/NG + ResultCode.
4. **Ack (PLC):** PLC přečte data a shodí Request.
5. **Clear (MES):** MES shodí Done/Busy a rozhraní je připraveno na další paletu.

Tento pětikrokový handshake je standardem pro robustní průmyslové systémy.
