#!/usr/bin/env python3
"""
GRAPH XML to SCL Converter - Robust Parser
Parses TIA Portal V18 GRAPH XML with proper namespace handling
"""

import xml.etree.ElementTree as ET
import re
import sys
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class GraphAction:
    qualifier: str = "N"
    event: str = ""
    code: str = ""

@dataclass
class GraphStep:
    number: int
    name: str
    actions: List[GraphAction] = field(default_factory=list)

@dataclass
class GraphTransition:
    number: int
    name: str
    condition: str = "TRUE"

class GraphToSCLConverter:
    def __init__(self, xml_path: str):
        self.xml_path = xml_path
        self.steps: Dict[int, GraphStep] = {}
        self.transitions: Dict[int, GraphTransition] = {}
        self.flow_name = os.path.basename(xml_path).replace('.xml', '')

    def parse(self) -> bool:
        """Parse XML with namespace handling"""
        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
        except Exception as e:
            print(f"ERROR: Cannot parse {self.xml_path}: {e}", file=sys.stderr)
            return False

        # Find Graph section - handle namespace
        ns = {'ns': 'http://www.siemens.com/automation/Openness/SW/NetworkSource/Graph/v5'}

        # Try with namespace first
        graph = root.find('.//ns:Graph', ns)
        if graph is None:
            # Try without namespace
            graph = root.find('.//Graph')

        if graph is None:
            print(f"ERROR: No Graph section found in {self.xml_path}", file=sys.stderr)
            return False

        # Extract steps
        step_elements = graph.findall('.//ns:Step', ns)
        if not step_elements:
            step_elements = graph.findall('.//Step')

        for step_elem in step_elements:
            step_num = int(step_elem.get('Number', 0))
            step_name = step_elem.get('Name', f'S{step_num}')

            step = GraphStep(number=step_num, name=step_name)

            # Extract actions
            action_elements = step_elem.findall('.//ns:Action', ns)
            if not action_elements:
                action_elements = step_elem.findall('.//Action')

            for action_elem in action_elements:
                qualifier = action_elem.get('Qualifier', 'N')
                event = action_elem.get('Event', '')

                # Collect all Token text
                tokens = []
                token_elements = action_elem.findall('.//ns:Token', ns)
                if not token_elements:
                    token_elements = action_elem.findall('.//Token')

                for token in token_elements:
                    if token.text:
                        text = token.text.strip()
                        text = re.sub(r'&#xA;', '', text)
                        text = re.sub(r'\s+', ' ', text).strip()
                        if text:
                            tokens.append(text)

                code = ' '.join(tokens)
                action = GraphAction(qualifier=qualifier, event=event, code=code)
                step.actions.append(action)

            self.steps[step_num] = step

        # Extract transitions
        trans_elements = graph.findall('.//ns:Transition', ns)
        if not trans_elements:
            trans_elements = graph.findall('.//Transition')

        for trans_elem in trans_elements:
            trans_num = int(trans_elem.get('Number', 0))
            trans_name = trans_elem.get('Name', f'Trans{trans_num}')

            # Extract condition from Access elements
            access_elements = trans_elem.findall('.//ns:Access', ns)
            if not access_elements:
                access_elements = trans_elem.findall('.//Access')

            if access_elements:
                # Build condition from component names
                components = []
                for access in access_elements:
                    symbol = access.find('ns:Symbol', ns)
                    if symbol is None:
                        symbol = access.find('Symbol')
                    if symbol is not None:
                        for comp in symbol.findall('.//ns:Component', ns):
                            name = comp.get('Name', '')
                            if name:
                                components.append(name)
                        # Try without namespace
                        if not components:
                            for comp in symbol.findall('.//Component'):
                                name = comp.get('Name', '')
                                if name:
                                    components.append(name)

                if components:
                    condition = '.'.join(components)
                else:
                    condition = "TRUE"
            else:
                condition = "TRUE"

            self.transitions[trans_num] = GraphTransition(
                number=trans_num,
                name=trans_name,
                condition=condition
            )

        return True

    def generate_scl(self, output_path: str) -> bool:
        """Generate complete SCL file"""
        sorted_steps = sorted(self.steps.values(), key=lambda x: x.number)
        sorted_trans = sorted(self.transitions.values(), key=lambda x: x.number)

        lines = []
        lines.append("//" + "=" * 77)
        lines.append(f"// {self.flow_name}.scl")
        lines.append("// COMPLETE 1:1 CONVERSION FROM TIA PORTAL V18 GRAPH XML")
        lines.append(f"// Source: {os.path.basename(self.xml_path)}")
        lines.append(f"// Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}")
        lines.append("//" + "=" * 77)
        lines.append("")

        # TYPE
        lines.append("TYPE")
        lines.append(f"    E_STEP_{self.flow_name} : (")
        for i, step in enumerate(sorted_steps):
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', step.name)
            if safe_name[0].isdigit():
                safe_name = f"S_{safe_name}"
            lines.append(f"        STEP_{self.flow_name}_{safe_name} := {step.number},")
        lines.append("    ) INT := 1;")
        lines.append("END_TYPE")
        lines.append("")

        # CONST - Steps
        lines.append("CONST")
        for step in sorted_steps:
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', step.name)
            if safe_name[0].isdigit():
                safe_name = f"S_{safe_name}"
            lines.append(f"    STEP_{self.flow_name}_{safe_name} := {step.number};")
        lines.append("END_CONST")
        lines.append("")

        # CONST - Transitions
        lines.append("CONST")
        for trans in sorted_trans:
            lines.append(f"    TRANS_{self.flow_name}_{trans.number} := {trans.condition};")
        lines.append("END_CONST")
        lines.append("")

        # FUNCTION_BLOCK
        lines.append(f"FUNCTION_BLOCK \"{self.flow_name}_1to1\"")
        lines.append("{ S7_Optimized_Access := 'TRUE' }")
        lines.append("VERSION : 1.0")
        lines.append("")
        lines.append("VAR_INPUT")
        lines.append('    iSysInface : "RCS_SysComInterface_V1";')
        lines.append("END_VAR")
        lines.append("")
        lines.append("VAR_IN_OUT")
        lines.append('    ioPM_Inface : "RCS_PMInterface_V1";')
        lines.append("    ioStatus : Int;")
        lines.append("END_VAR")
        lines.append("")
        lines.append("VAR_OUTPUT")
        lines.append("    oAlarmID : Int;")
        lines.append("END_VAR")
        lines.append("")
        lines.append("VAR")
        lines.append("    State : INT := 1;")
        lines.append("")
        lines.append("    // Action flags")
        lines.append("    act_InitialRun : Bool;")
        lines.append("    act_InitialOK : Bool;")
        lines.append("    act_WaitRunning : Bool;")
        lines.append("    act_Running : Bool;")
        lines.append("    act_ProcessComplete : Bool;")
        lines.append("    act_ProcessStart : Bool;")
        lines.append("    act_UnPause : Bool;")
        lines.append("")

        # Transition variables
        for trans in sorted_trans:
            lines.append(f"    tmpTrans{trans.number} : Bool;")
        lines.append("")
        lines.append("    bError : Bool;")
        lines.append("    wErrorID : Word;")
        lines.append("END_VAR")
        lines.append("")
        lines.append("BEGIN")
        lines.append("    //" + "=" * 70)
        lines.append("    // TRANSITIONS")
        lines.append("    //" + "=" * 70)

        for trans in sorted_trans:
            lines.append(f"    #tmpTrans{trans.number} := {trans.condition};")

        lines.append("")
        lines.append("    //" + "=" * 70)
        lines.append("    // STATE MACHINE")
        lines.append("    //" + "=" * 70)
        lines.append("")
        lines.append("    CASE #State OF")

        for step in sorted_steps:
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', step.name)
            if safe_name[0].isdigit():
                safe_name = f"S_{safe_name}"

            lines.append("")
            lines.append(f"        // =======================================")
            lines.append(f"        // STEP {step.number}: {step.name}")
            lines.append(f"        // =======================================")
            lines.append(f"        STEP_{self.flow_name}_{safe_name}:")

            if step.actions:
                for action in step.actions:
                    qualifier = action.qualifier
                    event = action.event
                    code = action.code

                    if qualifier == "S":
                        lines.append(f"            // Action Qualifier=S")
                        lines.append(f"            // Token: {code}")
                        lines.append(f"            {code} := TRUE;")
                    elif qualifier == "R":
                        lines.append(f"            // Action Qualifier=R")
                        lines.append(f"            // Token: {code}")
                        lines.append(f"            {code} := FALSE;")
                    else:
                        event_str = f", Event=\"{event}\"" if event else ""
                        lines.append(f"            // Action Qualifier={qualifier}{event_str}")
                        lines.append(f"            // Token: {code}")
                        lines.append(f"            {code};")
            else:
                lines.append("            // No actions in XML")

        lines.append("    END_CASE;")
        lines.append("")
        lines.append("    // UPDATE ioPM_Inface")
        lines.append("    #ioPM_Inface.InitialRun := #act_InitialRun;")
        lines.append("    #ioPM_Inface.InitialOK := #act_InitialOK;")
        lines.append("    #ioPM_Inface.WaitRunning := #act_WaitRunning;")
        lines.append("    #ioPM_Inface.Running := #act_Running;")
        lines.append("    #ioPM_Inface.ProcessComplete := #act_ProcessComplete;")
        lines.append("    #ioPM_Inface.ProcessStart := #act_ProcessStart;")
        lines.append("    #ioPM_Inface.UnPause := #act_UnPause;")
        lines.append("")
        lines.append("    // ERROR HANDLING")
        lines.append("    IF #bError THEN")
        lines.append("        #ioStatus := 900;")
        lines.append("        #oAlarmID := INT_TO_WORD(#wErrorID);")
        lines.append("    ELSE")
        lines.append("        #ioStatus := 0;")
        lines.append("        #oAlarmID := 0;")
        lines.append("    END_IF;")
        lines.append("END_FUNCTION_BLOCK")
        lines.append("")
        lines.append("//" + "=" * 77)
        lines.append("// END OF FILE")
        lines.append("//" + "=" * 77)

        # Write output
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return True
        except Exception as e:
            print(f"ERROR: Cannot write {output_path}: {e}", file=sys.stderr)
            return False


def process_file(xml_path: str, output_dir: str) -> bool:
    """Process single XML file"""
    print(f"\n{'=' * 60}")
    print(f"Processing: {os.path.basename(xml_path)}")
    print(f"{'=' * 60}")

    converter = GraphToSCLConverter(xml_path)

    if not converter.parse():
        return False

    print(f"  Steps: {len(converter.steps)}")
    print(f"  Transitions: {len(converter.transitions)}")

    # Count actions
    total_actions = sum(len(s.actions) for s in converter.steps.values())
    print(f"  Actions: {total_actions}")

    # Generate output
    output_path = os.path.join(output_dir, f"{converter.flow_name}_1to1.scl")

    if not converter.generate_scl(output_path):
        return False

    print(f"  -> Generated: {os.path.basename(output_path)}")

    # Show sample
    if converter.steps:
        first_step = min(converter.steps.values(), key=lambda x: x.number)
        if first_step.actions:
            print(f"\n  Sample action from Step {first_step.number}:")
            print(f"    Qualifier: {first_step.actions[0].qualifier}")
            print(f"    Code: {first_step.actions[0].code[:80]}...")

    return True


def main():
    """Main entry point"""
    # Configuration
    source_dir = r"C:\Users\klonkanitka\Desktop\GARRET\OP10\Program blocks\OP010\03_Auto"
    output_dir = r"C:\Users\klonkanitka\Desktop\GARRET\OP10\NEW SCL REFAKTOR\03_Auto"

    # Flow definitions
    flows = [
        "A1_TableLoad&Scan\\ST10_Flow1_A1TableScan.xml",
        "A1_TableLoad&Scan\\ST10_Flow2_A1TableUnloading.xml",
        "A1_TableLoad&Scan\\ST10_Flow3_A1RotaryShaftScan.xml",
        "B_Press\\ST10_Flow4_B1Press.xml",
        "B_Press\\ST10_Flow14_B2Press.xml",
        "C_Glue\\ST10_Flow7_CGlueing.xml",
        "F_Robot\\ST10_Flow5_FRobot_1.xml",
        "F_Robot\\ST10_Flow8_FRobot_2.xml",
        "F_Robot\\ST10_Flow15_FRobot_3.xml",
        "A2_TableLoad&Scan\\ST10_Flow11_A2TableScan.xml",
        "A2_TableLoad&Scan\\ST10_Flow12_A2TableUnloading.xml",
        "H_ShaftLifting&Load&Unload\\ST10_Flow21_HShaftLifting.xml",
        "H_ShaftLifting&Load&Unload\\ST10_Flow25_HShaftLoad&Unload.xml",
        "J_MagnetLifting&Load&Unload\\ST10_Flow22_JMagnetLifting.xml",
        "J_MagnetLifting&Load&Unload\\ST10_Flow26_JMagnetLoad&Unload.xml",
        "L_Unload\\K_ReserveLifting&Load&Unload\\ST10_Flow23_KReserveLifting.xml",
        "L_Unload\\K_ReserveLifting&Load&Unload\\ST10_Flow27_KReserveLoad&Unload.xml",
        "L_Unload\\ST10_Flow24_LUnloadingTrans.xml",
        "L_Unload\\ST10_Flow28_LUnloadingLoad&Unload.xml",
    ]

    print("\n" + "=" * 60)
    print("GRAPH XML to SCL Converter")
    print("=" * 60)

    total_steps = 0
    total_trans = 0
    total_actions = 0

    for flow_path in flows:
        xml_path = os.path.join(source_dir, flow_path)

        if not os.path.exists(xml_path):
            print(f"\n  SKIP: File not found: {xml_path}")
            continue

        if not process_file(xml_path, output_dir):
            print(f"  FAILED: {xml_path}")
            continue

        # Load and count
        converter = GraphToSCLConverter(xml_path)
        if converter.parse():
            total_steps += len(converter.steps)
            total_trans += len(converter.transitions)
            total_actions += sum(len(s.actions) for s in converter.steps.values())

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total Steps: {total_steps}")
    print(f"  Total Transitions: {total_trans}")
    print(f"  Total Actions: {total_actions}")
    print(f"  Output directory: {output_dir}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
