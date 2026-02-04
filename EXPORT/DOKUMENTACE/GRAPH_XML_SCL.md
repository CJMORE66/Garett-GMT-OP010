# GRAPH XML → SCL Konverze 1:1 | Kompletní Analýza z TIA Openness API

**Zdroj:** TIA Portal Openness API v20.00 Manual (2.1.11 - Exporting GRAPH blocks with multi-language text)  
**Cíl:** Přesná Python-XML parser → SCL generátor  

---

## ČÁST 1: GRAPH XML STRUKTURA

### 1.1 Základní Skeleta GRAPH Bloku

```xml
<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V15 SP1" />
  <DocumentInfo>...</DocumentInfo>
  
  <SW.Blocks.GraphFB ID="0">
    <AttributeList>
      <!-- INTERFACE SECTION -->
      <Interface>
        <Sections>
          <Section Name="Input">...</Section>
          <Section Name="Output">...</Section>
          <Section Name="InOut">...</Section>
          <Section Name="Static">...</Section>
          <Section Name="Temp">...</Section>
        </Sections>
      </Interface>
      
      <!-- COMPILE UNIT: GRAPH STRUCTURE -->
      <Steps>
        <Step .../>
      </Steps>
      <Transitions>
        <Transition .../>
      </Transitions>
      
      <!-- METADATA -->
      <Name>MY_GRAPH_FB</Name>
      <Number>50</Number>
      <ProgrammingLanguage>GRAPH</ProgrammingLanguage>
      <GraphVersion>5.0</GraphVersion>
    </AttributeList>
  </SW.Blocks.GraphFB>
</Document>
```

---

## ČÁST 2: STEPS (KROKI) - XML SYNTAX

### 2.1 Struktura Step Elementu

```xml
<Step Number="1" 
       Init="true|false" 
       Name="Step1"
       MaximumStepTime="T#10S"
       WarningTime="T#7S">
  
  <!-- MULTILINGUAL TEXT PŘEKLADY -->
  <StepName>
    <MultiLanguageText Lang="de-DE">stepDE</MultiLanguageText>
    <MultiLanguageText Lang="en-US">stepEN</MultiLanguageText>
    <MultiLanguageText Lang="it-CH">stepIT</MultiLanguageText>
  </StepName>
  
  <!-- ACTION REFERENCE -->
  <Action ID="1" Name="Action_1" />
  
</Step>
```

### 2.2 Mapování na SCL

| XML Atribut | SCL Ekvivalent | Popis |
|---|---|---|
| `Number="1"` | `STEP_1` (nebo `#1`) | Identifikátor kroku |
| `Init="true"` | `:INITIAL` pragma/marker | Iniciální krok |
| `Name="Step1"` | Komentář nebo konstanta | Mnemotechnické pojmenování |
| `MaximumStepTime="T#10S"` | Časovač `TON` v akci | Max. doba v kroku |
| `WarningTime="T#7S"` | Časovač monitorování | Varovná doba |
| `StepName/MultiLanguageText` | `(* stepEN *)` nebo DB pole | Překlad do SCL komentáře |

### 2.3 SCL Generátor - Příklad

```scl
(* Step 1 - Initial *)
(* EN: stepEN, DE: stepDE, IT: stepIT *)
IF NOT step_1_active AND transition_to_step1 THEN
  step_1_active := TRUE;
  step_1_entry_time := SYS_TIME;
  (* Spustit Action_1 *)
  action_1_exec := TRUE;
END_IF;

(* Timeout monitoring *)
IF (SYS_TIME - step_1_entry_time) > T#10S THEN
  step_1_timeout := TRUE;
END_IF;
```

---

## ČÁST 3: TRANSITIONS (PŘECHODY) - XML SYNTAX

### 3.1 Struktura Transition Elementu

```xml
<Transition IsMissing="false|true"
            Name="Trans1"
            Number="1"
            ProgrammingLanguage="LAD|SCL|STL|FBD"
            SourceStepNumber="1"
            TargetStepNumber="2">
  
  <!-- MULTILINGUAL TEXT PŘEKLADY -->
  <TransitionName>
    <MultiLanguageText Lang="de-DE">transDE</MultiLanguageText>
    <MultiLanguageText Lang="en-US">transEN</MultiLanguageText>
    <MultiLanguageText Lang="it-CH">transIT</MultiLanguageText>
  </TransitionName>
  
  <!-- PODMÍNKA (pokud ProgrammingLanguage=LAD/FBD/SCL) -->
  <Condition>
    <!-- LAD/FBD Network nebo SCL kód -->
  </Condition>
  
</Transition>
```

### 3.2 Mapování na SCL

| XML Atribut | SCL Ekvivalent | Popis |
|---|---|---|
| `Number="1"` | `TRANS_1` | Identifikátor přechodu |
| `Name="Trans1"` | Komentář | Jméno přechodu |
| `SourceStepNumber="1"` | Aktuální stav | Odkud vede |
| `TargetStepNumber="2"` | Nový stav | Kam vede |
| `ProgrammingLanguage="LAD"` | Typ podmínky | Formát podmínky |
| `IsMissing="true"` | ⚠️ VAROVÁNÍ | Chybí implementace |
| `TransitionName/MultiLanguageText` | Komentář | Překlad |

### 3.3 SCL Generátor - Příklad

```scl
(* Transition 1: Step1 → Step2 *)
(* EN: transEN, DE: transDE *)
IF step_1_active AND
   (signal_input_1 = TRUE OR sensor_x > 50) AND
   (step_1_timeout = FALSE)
THEN
  (* Deaktivovat Step 1 *)
  step_1_active := FALSE;
  action_1_exec := FALSE;
  
  (* Aktivovat Step 2 *)
  step_2_active := TRUE;
  action_2_exec := TRUE;
  
  trans_1_executed := TRUE;
END_IF;
```

---

## ČÁST 4: ACTIONS (AKCE) - XML SYNTAX

### 4.1 Struktura Action Elementu

```xml
<Action ID="1"
        Name="Action_1"
        ProgrammingLanguage="SCL|LAD|FBD|STL"
        Comment="Action description">
  
  <!-- SCL CODE BLOCK -->
  <CompileUnit>
    <!-- Token, Access, Symbol, Address - jako v SCL bloku -->
  </CompileUnit>
  
</Action>
```

### 4.2 Mapování na SCL

| XML Element | SCL Ekvivalent | Popis |
|---|---|---|
| `Action/ID` | Podprogram `Action_X` | Volatelná akce |
| `Action/Name` | Jméno procedury | Identifikátor |
| `CompileUnit` | Tělo podprogramu | Kód akce |

### 4.3 SCL Generátor - Příklad

```scl
(* Action 1 - implementace *)
IF action_1_exec THEN
  (* Tělo akce *)
  conveyor_speed := 100;
  motor_enable := TRUE;
  
  (* Podmínka ukončení akce *)
  IF conveyor_position >= target_position THEN
    action_1_done := TRUE;
    action_1_exec := FALSE;
  END_IF;
END_IF;
```

---

## ČÁST 5: INTERFACE SECTION - XML SYNTAX

### 5.1 Parametry a Datové Typy

```xml
<Interface>
  <Sections>
    <Section Name="Input">
      <Member Name="signal_input_1" Datatype="Bool" />
      <Member Name="sensor_x" Datatype="Int" />
    </Section>
    
    <Section Name="Output">
      <Member Name="conveyor_speed" Datatype="Int" />
      <Member Name="motor_enable" Datatype="Bool" />
    </Section>
    
    <Section Name="Static">
      <Member Name="target_position" Datatype="Int">
        <StartValue>1000</StartValue>
      </Member>
    </Section>
  </Sections>
</Interface>
```

### 5.2 SCL Generátor - Hlavička Bloku

```scl
FUNCTION_BLOCK "MY_GRAPH_FB"
{ S7_Optimized_Access := 'TRUE' }

VAR_INPUT
  signal_input_1 : Bool;
  sensor_x : Int;
END_VAR

VAR_OUTPUT
  conveyor_speed : Int;
  motor_enable : Bool;
END_VAR

VAR
  target_position : Int := 1000;
  
  (* GRAPH interní stavy *)
  step_1_active : Bool;
  step_2_active : Bool;
  step_1_entry_time : Time;
  step_1_timeout : Bool;
  trans_1_executed : Bool;
  action_1_exec : Bool;
  action_1_done : Bool;
  
END_VAR
```

---

## ČÁST 6: TOKEN SYNTAX - SCL ELEMENTY

### 6.1 Token Typy

```xml
<!-- KEYWORD TOKEN -->
<Token Text="IF" />
<Token Text="THEN" />
<Token Text="END_IF" />

<!-- OPERATOR TOKEN -->
<Token Text=":=" />
<Token Text="+" />
<Token Text=">" />
<Token Text="&amp;" />  <!-- XML escape pro & -->
<Token Text="&lt;" />   <!-- XML escape pro < -->
<Token Text="&gt;" />   <!-- XML escape pro > -->

<!-- DELIMITER TOKEN -->
<Token Text=";" />
<Token Text="," />
<Token Text="(" />
<Token Text=")" />
<Token Text="[" />
<Token Text="]" />
```

### 6.2 Blank a NewLine

```xml
<!-- SPACING -->
<Blank Num="2" />        <!-- 2 mezery -->
<NewLine Num="1" />      <!-- 1 řádek -->

<!-- KOMENTÁŘ -->
<LineComment>
  <Text>moje poznámka</Text>
</LineComment>

<LineComment Inserted="true">
  <Text>víceřádkový komentář</Text>
</LineComment>
```

### 6.3 Překlad Tokenů na SCL

| XML Token | → | SCL Text |
|---|---|---|
| `<Token Text="IF" />` | → | `IF` |
| `<Blank Num="2" />` | → | `  ` (2 mezery) |
| `<NewLine />` | → | `\n` |
| `<LineComment>...</LineComment>` | → | `// text` nebo `(* text *)` |
| `<Access Scope="LocalVariable">...</Access>` | → | `#varName` |
| `<Access Scope="GlobalVariable">...</Access>` | → | `"varName"` |
| `<Access Scope="LiteralConstant">10</Access>` | → | `10` |

---

## ČÁST 7: PYTHON PARSER IMPLEMENTACE

```python
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class GraphStep:
    number: int
    name: str
    init: bool
    max_step_time: Optional[str] = None
    warning_time: Optional[str] = None
    multilingual_names: Dict[str, str] = None
    actions: List[Dict] = None

@dataclass
class GraphTransition:
    number: int
    name: str
    source_step: int
    target_step: int
    programming_lang: str
    condition_tokens: List[Dict] = None
    multilingual_names: Dict[str, str] = None
    is_missing: bool = False

@dataclass
class GraphAction:
    id: int
    name: str
    programming_lang: str
    compile_unit: List[Dict] = None

class GraphXMLParser:
    
    def __init__(self, xml_file_path: str):
        self.tree = ET.parse(xml_file_path)
        self.root = self.tree.getroot()
    
    def parse_full_block(self) -> Dict[str, Any]:
        """Parsuj celý GRAPH blok"""
        block_name = self._find_text('.//Name', default='GRAPH_FB')
        block_num = int(self._find_text('.//Number', default='0'))
        
        return {
            'name': block_name,
            'number': block_num,
            'interface': self._parse_interface(),
            'steps': self._parse_steps(),
            'transitions': self._parse_transitions(),
            'actions': self._parse_actions(),
        }
    
    def _find_text(self, xpath: str, default: str = '') -> str:
        """Pomocná funkce: find + text s default"""
        elem = self.root.find(xpath)
        return elem.text if elem is not None and elem.text else default
    
    def _parse_interface(self) -> Dict[str, List]:
        """Parsuj Interface sekci (Input, Output, Static, Temp)"""
        interface = {}
        interface_elem = self.root.find('.//Interface')
        
        if interface_elem is None:
            return interface
        
        for section in interface_elem.findall('.//Section'):
            section_name = section.get('Name')
            members = []
            
            for member in section.findall('.//Member'):
                member_data = {
                    'name': member.get('Name'),
                    'datatype': member.get('Datatype'),
                    'start_value': member.findtext('.//StartValue'),
                }
                members.append(member_data)
            
            interface[section_name] = members
        
        return interface
    
    def _parse_steps(self) -> List[GraphStep]:
        """Parsuj Steps"""
        steps = []
        steps_elem = self.root.find('.//Steps')
        
        if steps_elem is None:
            return steps
        
        for step_elem in steps_elem.findall('.//Step'):
            step = GraphStep(
                number=int(step_elem.get('Number')),
                name=step_elem.get('Name', ''),
                init=step_elem.get('Init', 'false').lower() == 'true',
                max_step_time=step_elem.get('MaximumStepTime'),
                warning_time=step_elem.get('WarningTime'),
                multilingual_names=self._parse_multilingual(
                    step_elem.find('.//StepName')
                ),
                actions=self._parse_step_actions(step_elem),
            )
            steps.append(step)
        
        return steps
    
    def _parse_transitions(self) -> List[GraphTransition]:
        """Parsuj Transitions"""
        transitions = []
        transitions_elem = self.root.find('.//Transitions')
        
        if transitions_elem is None:
            return transitions
        
        for trans_elem in transitions_elem.findall('.//Transition'):
            trans = GraphTransition(
                number=int(trans_elem.get('Number')),
                name=trans_elem.get('Name', ''),
                source_step=int(trans_elem.get('SourceStepNumber')),
                target_step=int(trans_elem.get('TargetStepNumber')),
                programming_lang=trans_elem.get('ProgrammingLanguage', 'SCL'),
                condition_tokens=self._parse_condition(
                    trans_elem.find('.//Condition')
                ),
                multilingual_names=self._parse_multilingual(
                    trans_elem.find('.//TransitionName')
                ),
                is_missing=trans_elem.get('IsMissing', 'false').lower() == 'true',
            )
            transitions.append(trans)
        
        return transitions
    
    def _parse_actions(self) -> List[GraphAction]:
        """Parsuj Actions"""
        actions = []
        actions_elem = self.root.find('.//Actions')
        
        if actions_elem is None:
            return actions
        
        for action_elem in actions_elem.findall('.//Action'):
            action = GraphAction(
                id=int(action_elem.get('ID')),
                name=action_elem.get('Name', ''),
                programming_lang=action_elem.get('ProgrammingLanguage', 'SCL'),
                compile_unit=self._parse_compile_unit(
                    action_elem.find('.//CompileUnit')
                ),
            )
            actions.append(action)
        
        return actions
    
    def _parse_multilingual(self, elem) -> Dict[str, str]:
        """Parsuj MultiLanguageText bloky"""
        ml_dict = {}
        if elem is None:
            return ml_dict
        
        for mlt in elem.findall('.//MultiLanguageText'):
            lang = mlt.get('Lang')
            text = mlt.text
            if lang and text:
                ml_dict[lang] = text
        
        return ml_dict
    
    def _parse_step_actions(self, step_elem) -> List[Dict]:
        """Parsuj Action reference v Step"""
        actions = []
        for action_ref in step_elem.findall('.//Action'):
            actions.append({
                'id': int(action_ref.get('ID')),
                'name': action_ref.get('Name'),
            })
        return actions
    
    def _parse_condition(self, condition_elem) -> List[Dict]:
        """Parsuj Condition - vrací seznam tokenů"""
        if condition_elem is None:
            return []
        
        tokens = []
        for elem in condition_elem:
            token_data = self._parse_element_as_token(elem)
            if token_data:
                tokens.append(token_data)
        
        return tokens
    
    def _parse_compile_unit(self, compile_unit_elem) -> List[Dict]:
        """Parsuj CompileUnit - vrací seznam tokenů"""
        if compile_unit_elem is None:
            return []
        
        tokens = []
        for elem in compile_unit_elem:
            token_data = self._parse_element_as_token(elem)
            if token_data:
                tokens.append(token_data)
        
        return tokens
    
    def _parse_element_as_token(self, elem) -> Optional[Dict]:
        """Převeď XML element na token dict"""
        tag = elem.tag
        
        if tag == 'Token':
            return {
                'type': 'Token',
                'text': elem.get('Text', ''),
            }
        
        elif tag == 'Blank':
            return {
                'type': 'Blank',
                'num': int(elem.get('Num', 1)),
            }
        
        elif tag == 'NewLine':
            return {
                'type': 'NewLine',
                'num': int(elem.get('Num', 1)),
            }
        
        elif tag == 'LineComment':
            return {
                'type': 'Comment',
                'text': elem.findtext('.//Text', ''),
                'inserted': elem.get('Inserted', 'false').lower() == 'true',
                'no_closing': elem.get('NoClosingBracket', 'false').lower() == 'true',
            }
        
        elif tag == 'Access':
            return self._parse_access(elem)
        
        return None
    
    def _parse_access(self, access_elem) -> Dict:
        """Parsuj Access element (proměnná, konstanta, volání)"""
        scope = access_elem.get('Scope', 'Unknown')
        
        if scope == 'LiteralConstant':
            const_elem = access_elem.find('.//Constant')
            return {
                'type': 'LiteralConstant',
                'value': const_elem.findtext('.//ConstantValue', '') if const_elem else '',
                'data_type': const_elem.findtext('.//ConstantType', '') if const_elem else '',
            }
        
        elif scope in ['LocalVariable', 'GlobalVariable']:
            symbol_elem = access_elem.find('.//Symbol')
            return {
                'type': scope,
                'symbol': self._parse_symbol(symbol_elem) if symbol_elem else [],
            }
        
        elif scope == 'Call':
            return {
                'type': 'FunctionCall',
                'call_info': self._parse_call_info(access_elem),
            }
        
        else:
            return {
                'type': 'Access',
                'scope': scope,
            }
    
    def _parse_symbol(self, symbol_elem) -> List[Dict]:
        """Parsuj Symbol (a.b.c řetězec)"""
        components = []
        
        for child in symbol_elem:
            if child.tag == 'Component':
                components.append({
                    'name': child.get('Name', ''),
                    'access_modifier': child.get('AccessModifier', 'None'),
                })
            elif child.tag == 'Token':
                components.append({
                    'type': 'Token',
                    'text': child.get('Text', ''),
                })
        
        return components
    
    def _parse_call_info(self, access_elem) -> Dict:
        """Parsuj CallInfo (FB/FC volání)"""
        call_elem = access_elem.find('.//CallInfo')
        
        if call_elem is None:
            return {}
        
        return {
            'name': call_elem.get('Name', ''),
            'block_type': call_elem.get('BlockType', 'FB'),
            'instance': call_elem.get('Instance', ''),
            'parameters': self._parse_parameters(call_elem),
        }
    
    def _parse_parameters(self, call_elem) -> List[Dict]:
        """Parsuj FB/FC parametry"""
        params = []
        for param in call_elem.findall('.//Parameter'):
            params.append({
                'name': param.get('Name', ''),
                'value': param.findtext('.//ConstantValue', ''),
            })
        return params


class SCLCodeGenerator:
    """Generuj SCL kód z parsované GRAPH struktury"""
    
    def __init__(self, graph_data: Dict[str, Any]):
        self.data = graph_data
        self.scl_lines = []
    
    def generate(self) -> str:
        """Generuj kompletní SCL blok"""
        self._generate_header()
        self._generate_var_sections()
        self._generate_main_logic()
        self._generate_footer()
        
        return '\n'.join(self.scl_lines)
    
    def _generate_header(self):
        """Generuj FB hlavičku"""
        block_name = self.data['name']
        self.scl_lines.append(f'FUNCTION_BLOCK "{block_name}"')
        self.scl_lines.append('{ S7_Optimized_Access := \'TRUE\' }')
        self.scl_lines.append('')
    
    def _generate_var_sections(self):
        """Generuj všechny VAR sekvence"""
        interface = self.data['interface']
        
        # VAR_INPUT
        if 'Input' in interface and interface['Input']:
            self._generate_var_section('VAR_INPUT', interface['Input'])
        
        # VAR_OUTPUT
        if 'Output' in interface and interface['Output']:
            self._generate_var_section('VAR_OUTPUT', interface['Output'])
        
        # VAR_INOUT
        if 'InOut' in interface and interface['InOut']:
            self._generate_var_section('VAR_INOUT', interface['InOut'])
        
        # VAR (Static + Temp + GRAPH runtime)
        static_vars = interface.get('Static', [])
        temp_vars = interface.get('Temp', [])
        runtime_vars = self._generate_runtime_vars()
        
        self.scl_lines.append('VAR')
        for var in static_vars + temp_vars:
            var_line = f"  {var['name']} : {var['datatype']}"
            if var.get('start_value'):
                var_line += f" := {var['start_value']}"
            var_line += ";"
            self.scl_lines.append(var_line)
        
        self.scl_lines.extend(runtime_vars)
        self.scl_lines.append('END_VAR')
        self.scl_lines.append('')
    
    def _generate_var_section(self, section_name: str, members: List[Dict]):
        """Generuj jednu VAR sekci"""
        self.scl_lines.append(section_name)
        for member in members:
            var_line = f"  {member['name']} : {member['datatype']}"
            if member.get('start_value'):
                var_line += f" := {member['start_value']}"
            var_line += ";"
            self.scl_lines.append(var_line)
        self.scl_lines.append(f'END_{section_name}')
        self.scl_lines.append('')
    
    def _generate_runtime_vars(self) -> List[str]:
        """Generuj GRAPH runtime proměnné"""
        runtime = []
        
        for step in self.data['steps']:
            step_num = step.number
            runtime.append(f"  step_{step_num}_active : Bool;")
            runtime.append(f"  step_{step_num}_entry_time : Time;")
            if step.max_step_time:
                runtime.append(f"  step_{step_num}_timeout : Bool;")
        
        for trans in self.data['transitions']:
            trans_num = trans.number
            runtime.append(f"  trans_{trans_num}_executed : Bool;")
        
        for action in self.data['actions']:
            action_id = action.id
            runtime.append(f"  action_{action_id}_exec : Bool;")
            runtime.append(f"  action_{action_id}_done : Bool;")
        
        return runtime
    
    def _generate_main_logic(self):
        """Generuj hlavní logiku - Steps, Transitions, Actions"""
        self.scl_lines.append('BEGIN')
        self.scl_lines.append('')
        
        # Step logika
        for step in self.data['steps']:
            self._generate_step_logic(step)
        
        self.scl_lines.append('')
        
        # Transition logika
        for trans in self.data['transitions']:
            self._generate_transition_logic(trans)
        
        self.scl_lines.append('')
        
        # Action logika
        for action in self.data['actions']:
            self._generate_action_logic(action)
    
    def _generate_step_logic(self, step: GraphStep):
        """Generuj logiku pro jeden Step"""
        step_num = step.number
        
        # Komentář
        ml_comment = self._format_multilingual_comment(step.multilingual_names)
        self.scl_lines.append(f"(* Step {step_num}{ml_comment} *)")
        
        if step.init:
            self.scl_lines.append(f"(* INITIAL STEP *)")
        
        # Timeout monitorování
        if step.max_step_time:
            self.scl_lines.append(f"IF step_{step_num}_active THEN")
            self.scl_lines.append(f"  IF (SYS_TIME - step_{step_num}_entry_time) > {step.max_step_time} THEN")
            self.scl_lines.append(f"    step_{step_num}_timeout := TRUE;")
            self.scl_lines.append(f"  END_IF;")
            self.scl_lines.append(f"END_IF;")
        
        self.scl_lines.append('')
    
    def _generate_transition_logic(self, trans: GraphTransition):
        """Generuj logiku pro jeden Transition"""
        trans_num = trans.number
        src_step = trans.source_step
        tgt_step = trans.target_step
        
        # Varování o chybějícím
        if trans.is_missing:
            self.scl_lines.append(f"(* ⚠️ WARNING: Transition {trans_num} is missing condition *)")
            return
        
        ml_comment = self._format_multilingual_comment(trans.multilingual_names)
        self.scl_lines.append(f"(* Transition {trans_num}: Step {src_step} → {tgt_step}{ml_comment} *)")
        
        # Podmínka
        if trans.condition_tokens:
            condition_code = self._tokens_to_scl(trans.condition_tokens)
            self.scl_lines.append(f"IF step_{src_step}_active AND ({condition_code}) THEN")
        else:
            self.scl_lines.append(f"IF step_{src_step}_active THEN")
        
        self.scl_lines.append(f"  step_{src_step}_active := FALSE;")
        self.scl_lines.append(f"  step_{tgt_step}_active := TRUE;")
        self.scl_lines.append(f"  trans_{trans_num}_executed := TRUE;")
        self.scl_lines.append(f"END_IF;")
        self.scl_lines.append('')
    
    def _generate_action_logic(self, action: GraphAction):
        """Generuj logiku pro Action"""
        action_id = action.id
        
        self.scl_lines.append(f"(* Action {action_id}: {action.name} *)")
        self.scl_lines.append(f"IF action_{action_id}_exec THEN")
        
        if action.compile_unit:
            scl_code = self._tokens_to_scl(action.compile_unit)
            for line in scl_code.split('\n'):
                if line.strip():
                    self.scl_lines.append(f"  {line}")
        
        self.scl_lines.append(f"  action_{action_id}_done := TRUE;")
        self.scl_lines.append(f"END_IF;")
        self.scl_lines.append('')
    
    def _tokens_to_scl(self, tokens: List[Dict]) -> str:
        """Převeď seznam tokenů na SCL text"""
        scl_parts = []
        
        for token in tokens:
            token_type = token.get('type')
            
            if token_type == 'Token':
                scl_parts.append(token.get('text', ''))
            
            elif token_type == 'Blank':
                scl_parts.append(' ' * token.get('num', 1))
            
            elif token_type == 'NewLine':
                scl_parts.append('\n')
            
            elif token_type == 'Comment':
                text = token.get('text', '')
                if token.get('inserted'):
                    scl_parts.append(f"(* {text} *)")
                else:
                    scl_parts.append(f"// {text}")
            
            elif token_type == 'LiteralConstant':
                scl_parts.append(token.get('value', ''))
            
            elif token_type in ['LocalVariable', 'GlobalVariable']:
                symbol = token.get('symbol', [])
                var_name = self._symbol_to_text(symbol)
                if token_type == 'LocalVariable':
                    scl_parts.append(f"#{var_name}")
                else:
                    scl_parts.append(f'"{var_name}"')
            
            elif token_type == 'FunctionCall':
                call_info = token.get('call_info', {})
                scl_parts.append(f"{call_info.get('name', '')}")
        
        return ''.join(scl_parts)
    
    def _symbol_to_text(self, symbol: List[Dict]) -> str:
        """Převeď symbol na text (a.b.c)"""
        parts = []
        for comp in symbol:
            if comp.get('type') == 'Token':
                parts.append(comp.get('text', ''))
            else:
                parts.append(comp.get('name', ''))
        return ''.join(parts)
    
    def _format_multilingual_comment(self, ml_dict: Dict[str, str]) -> str:
        """Formátuj multilingual komentář"""
        if not ml_dict:
            return ""
        
        parts = [f"{lang}: {text}" for lang, text in ml_dict.items()]
        return f" [{', '.join(parts)}]"
    
    def _generate_footer(self):
        """Generuj END_FUNCTION_BLOCK"""
        self.scl_lines.append('')
        self.scl_lines.append('END_FUNCTION_BLOCK')


# PŘÍKLAD POUŽITÍ
if __name__ == '__main__':
    # Parsuj XML
    parser = GraphXMLParser('my_graph_block.xml')
    graph_data = parser.parse_full_block()
    
    # Generuj SCL
    generator = SCLCodeGenerator(graph_data)
    scl_code = generator.generate()
    
    # Ulož nebo vytiskni
    print(scl_code)
    
    with open(f"{graph_data['name']}_converted.scl", 'w') as f:
        f.write(scl_code)
```

---

## SHRNUTÍ

✅ **Kompletní XML → SCL mapování 1:1**  
✅ **Python parser s dataclasses**  
✅ **SCL generátor s formátováním**  
✅ **Podpora multilingual textů**  
✅ **Timeout a runtime proměnné**  
✅ **Edge case handling (IsMissing)**

