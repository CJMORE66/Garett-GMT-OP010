# Revize logiky řízení V90 Servo a procesu Lepení (Gluing)

Tento dokument obsahuje detailní analýzu a "přísnou revizi" aktuálního řešení řízení serva Siemens V90 a procesu lepení v projektu. Cílem je identifikovat slabá místa a navrhnout modernější, efektivnější a bezpečnější řešení.

## 🛑 Hlavní verdikt
Současná implementace je **funkční, ale zastaralá, rigidní a obtížně udržovatelná**. Spoléhá na tzv. "Super Bloky" (funkční bloky, které dělají příliš mnoho věcí najednou), nevhodný styl programování pro sekvence (LAD - kontaktní schéma) a rizikové metody adresování (tzv. "magická čísla"). Pro kritický proces, jako je nanášení lepidla, je toto řešení suboptimální a může vést k problémům s kvalitou.

---

## 🔍 Detailní analýza problémů

### 1. Architektura a "Wrapper" (V90_Servo)
*   **Anti-vzor "Super Wrapper":** Blok `fbV90Ctrl` se snaží obsloužit *všechno* najednou – manuální režim, automatiku, referencování (homing), čtení/zápis parametrů, polohování podle tabulky a bezpečnost.
    *   **Proč je to špatně:** Vytváří to "God Object" (božský objekt), který je noční můrou pro debugování. Pokud změníte logiku referencování, riskujete, že rozbijete automatickou sekvenci. Rozhraní bloku je zahlceno desítkami pinů, které v daném okamžiku nejsou vůbec potřeba.
    *   **Pozorování:** V podstatě "obalujete" standardní Siemens blok `SINA_POS` do vlastního `fbV90Ctrl`, a ten je pak znovu obalen v `V90_Servo`. Toto trojité zanoření skrývá standardní funkcionalitu a nepřidává žádnou hodnotu, jen složitost.
*   **Zbytečné kopírování dat:** Systém spoléhá na masivní datový blok se standardním přístupem (`ServoV90_A1`) pro mapování dat do bloku. To zbytečně zatěžuje CPU a v moderním TIA Portalu je to neefektivní.

### 2. Proces Lepení (Gluing.xml)
*   **LAD pro sekvence je chyba:** Používáte kontaktní schéma (LAD) pro řízení krokové sekvence lepení.
    *   **Proč je to špatně:** LAD je skvělý pro jednoduchou logiku (např. bezpečnostní blokování), ale nevhodný pro sekvencery. Vede to ke "špagetovému kódu" s cívkami Set/Reset rozesetými všude možně. Je téměř nemožné vizuálně sledovat tok programu nebo zjistit, ve kterém kroku se proces zasekl.
    *   **Riziko:** Lepení vyžaduje přesné časování. Hledání chyb v časování v síti plné LAD kontaktů a `TON` časovačů je extrémně neefektivní.
*   **Magická čísla a hardcoding:**
    *   **Kód:** `V90Servo[3].Point[2].Start`, `V90Servo[3].Point[6].Start`.
    *   **Problém:** Co je Servo 3? Co je Bod 6? Pokud se změní mechanický design a pozice "Čištění" se přesune na bod 7, musíte v kódu ručně dohledat a přepsat všechna tato čísla. To je velmi náchylné k chybám.
*   **Nejasná správa stavů:** Logika lepení spoléhá na příznaky (flagy) jako `GluingDeviceReady`, `GluingFault`. Chybí zde jasný "Stavový automat" (např. stavy: IDLE -> PŘÍJEZD -> LEPENÍ -> ODJEZD).

### 3. Technologie a Výkon
*   **EPOS vs. Technologický objekt (TO):** Používáte `SINA_POS` (EPOS - Basic Positioner).
    *   **Kritické pro lepení:** EPOS je "Point-to-Point" polohovač. To znamená, že akceleruje, přesune se a zpomalí do zastavení (nebo téměř do zastavení) v každém cílovém bodě.
    *   **Důsledek:** Pokud nanášíte souvislou housenku lepidla po dráze složené z více bodů, EPOS způsobí **nerovnoměrné nanesení** (tlusté "bloby" v bodech, kde osa zpomaluje, a tenké čáry během zrychleného přesunu).
*   **Standardní přístup k DB:** Datový blok `ServoV90_A1` má nastaven "Standardní přístup". To znemožňuje optimalizace kompilátoru TIA Portal, zvyšuje využití paměti a zpomaluje přístup k datům ve srovnání s "Optimalizovaným přístupem".

---

## ✅ Doporučení pro zlepšení (Co udělat lépe)

### 1. Přejděte na Technologické objekty (Vysoce doporučeno)
Přepněte z `SINA_POS` na **Technology Objects (TO_PositioningAxis)**.
*   **Proč:** TO řeší komunikaci s drivem automaticky na pozadí. Získáte standardizované PLCopen rozhraní (`MC_Power`, `MC_MoveAbsolute`, `MC_MoveLinear`).
*   **Přínos pro Lepení:** Můžete využít funkci **`MC_MoveLinearAbsolute`** s režimem "Blending" (BufferMode). To umožní servu/robotu projíždět body **bez zastavení**, což zajistí perfektně konstantní rychlost a tím i rovnoměrnou housenku lepidla.

### 2. Implementujte pořádný Stavový automat (SCL nebo GRAPH)
Přepište blok `Gluing` pomocí jazyka **SCL (Case Statement)** nebo **S7-GRAPH**.
*   **Vzor (SCL):**
    ```scl
    CASE #Step OF
        10: // ČEKÁNÍ (IDLE)
            IF #Start THEN #Step := 20; END_IF;
        20: // PŘÍJEZD (APPROACH)
            #Axis.Position := #Pos_Purge; // Použití konstanty místo čísla!
            #Axis.Execute := TRUE;
            IF #Axis.Done THEN #Step := 30; END_IF;
        30: // LEPENÍ (GLUE ON)
            #GlueGun := TRUE;
            #Step := 40;
    END_CASE;
    ```
*   **Výhoda:** Kód je čitelný, snadno se ladí a upravuje.

### 3. Používejte Uživatelské konstanty a UDT
Nahraďte magická čísla pojmenovanými konstantami.
*   **Špatně:** `Point[6]`
*   **Dobře:** `Point[#CONST_POS_CISTENI]` nebo `Point[#CONST_POS_START_LEPENI]`
*   Vytvořte UDT (User Data Type) pro vaše data bodů namísto generických polí. UDT může obsahovat název bodu, rychlost, typ pohybu atd.

### 4. Optimalizujte Datové bloky
*   Převeďte `ServoV90_A1` a další související DB na **"Optimalizovaný přístup k bloku"**.
*   Odstraňte zbytečnou kopírovací logiku (Network 1 v `Gluing.xml`). Mapujte IO přímo na rozhraní bloku nebo použijte dedikovanou funkci pro mapování IO, pokud chcete abstrahovat hardware.

### Shrnutí akcí
| Oblast                | Současný stav                 | Cílový stav                           | Obtížnost | Hodnota   |
| :---                  | :---                          | :---                                  | :---      | :---      |
| **Motion Control**    | `SINA_POS` (EPOS) Wrapper     | **Technologický objekt (TO)**         | Vysoká    | ⭐⭐⭐⭐⭐ (Kritické pro kvalitu) |
| **Logika sekvence**   | Ladder (LAD)                  | **SCL Stavový automat**               | Střední   | ⭐⭐⭐⭐ (Udržitelnost) |
| **Datová struktura**  | Generická pole a čísla        | **UDT a Konstanty**                   | Nízká     | ⭐⭐⭐ |
| **Wrapper**           | "God Object" FB               | **Modulární FC** (Power, Home, Move)  | Střední        | ⭐⭐⭐   |

**Závěr:** Pokud z nějakého důvodu (např. hardware omezení staršího CPU) nemůžete přejít na Technologické objekty, pak jako minimum **přepište logiku `Gluing` do SCL** a odstraňte "magická čísla" (hardcoded indexy polí).
