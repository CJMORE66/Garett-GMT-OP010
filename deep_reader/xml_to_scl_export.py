#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[1] if tag.startswith("{") else tag


def safe_filename(name: str) -> str:
    name = name.strip()
    name = name.replace("\\", "_").replace("/", "_")
    name = re.sub(r"[^0-9A-Za-z._ -]+", "_", name)
    name = re.sub(r"\s+", " ", name)
    name = name.replace(" ", "_")
    if not name:
        return "_"
    return name[:180]


def scl_quote_name(name: str) -> str:
    # TIA allows quoted names for blocks/DB/TYPE identifiers.
    return '"' + name.replace('"', '""') + '"'

def scl_member_name(name: str) -> str:
    """
    Quote member identifiers when needed for valid SCL.
    TIA supports quoted member names (e.g., "PLC IP Addr").
    """
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name or ""):
        return name
    return scl_quote_name(name)


def unescape_datatype(dt: str) -> str:
    # XML encodes quotes as &quot; for UDT references
    return html.unescape(dt).strip()


@dataclasses.dataclass
class Member:
    name: str
    datatype: str
    children: list["Member"]


def find_first(elem: ET.Element, local: str) -> ET.Element | None:
    for c in list(elem):
        if strip_ns(c.tag) == local:
            return c
    return None


def iter_children(elem: ET.Element, local: str) -> list[ET.Element]:
    return [c for c in list(elem) if strip_ns(c.tag) == local]


def parse_members_from_section(section_elem: ET.Element) -> list[Member]:
    members: list[Member] = []
    for m in iter_children(section_elem, "Member"):
        name = m.attrib.get("Name", "")
        dt = unescape_datatype(m.attrib.get("Datatype", ""))
        children: list[Member] = []

        # In many DB exports, nested struct members are direct <Member> children
        direct_nested = iter_children(m, "Member")
        if direct_nested:
            nested_members: list[Member] = []
            for child in direct_nested:
                # Wrap into a pseudo-section so we can reuse the same parsing logic recursively
                pseudo_section = ET.Element("Section")
                pseudo_section.append(child)
                nested_members.extend(parse_members_from_section(pseudo_section))
            if dt.lower() == "struct":
                children = nested_members

        # In many UDT/interface exports, nested members are inside <Sections><Section ...>
        if not children:
            sections = find_first(m, "Sections")
            if sections is not None:
                nested_sections = iter_children(sections, "Section")
                nested_members: list[Member] = []
                for s in nested_sections:
                    nested_members.extend(parse_members_from_section(s))
                if dt.lower() == "struct" or (dt == "" and nested_members):
                    children = nested_members

        members.append(Member(name=name, datatype=dt, children=children))
    return members


def parse_interface_sections(path: Path) -> dict[str, list[Member]]:
    """
    Returns dict of section name -> list of Members.
    Section names: Input/Output/InOut/Static/Temp/Constant/None.
    """
    tree = ET.parse(path)
    root = tree.getroot()

    # Find Interface/Sections regardless of namespace
    interface = None
    for elem in root.iter():
        if strip_ns(elem.tag) == "Interface":
            interface = elem
            break
    if interface is None:
        return {}
    sections_root = None
    for elem in interface.iter():
        if strip_ns(elem.tag) == "Sections":
            sections_root = elem
            break
    if sections_root is None:
        return {}

    out: dict[str, list[Member]] = {}
    for sec in iter_children(sections_root, "Section"):
        sec_name = sec.attrib.get("Name", "None")
        out[sec_name] = parse_members_from_section(sec)
    return out


def parse_block_header(path: Path) -> dict[str, str]:
    kind = ""
    name = ""
    number = ""
    lang = ""

    block_attr_seen = False
    block_attr_open = False
    block_attr_depth = 0
    block_kind = None

    for event, elem in ET.iterparse(path, events=("start", "end")):
        tag = strip_ns(elem.tag)
        if event == "start" and tag.startswith("SW.Blocks.") and not kind:
            block_kind = tag.split(".", 2)[-1]
            kind = block_kind
        elif event == "start" and tag == "AttributeList":
            if block_kind is not None and not block_attr_seen:
                block_attr_seen = True
                block_attr_open = True
                block_attr_depth = 1
            elif block_attr_open:
                block_attr_depth += 1
        elif event == "end":
            if block_attr_open and tag in {"Name", "Number", "ProgrammingLanguage"}:
                txt = (elem.text or "").strip()
                if tag == "Name" and not name and txt:
                    name = txt
                elif tag == "Number" and not number and txt:
                    number = txt
                elif tag == "ProgrammingLanguage" and not lang and txt:
                    lang = txt
            if tag == "AttributeList" and block_attr_open:
                block_attr_depth -= 1
                if block_attr_depth <= 0:
                    block_attr_open = False
            elem.clear()
        if kind and name and lang:
            # Number can be missing for some exports; do not block on it.
            pass
    return {"kind": kind, "name": name, "number": number, "language": lang}


def extract_structured_text_code(path: Path) -> list[str]:
    """
    Extract tokenized StructuredText networks into readable pseudo-SCL.
    This is best-effort and intended for review (not guaranteed to compile).
    """
    outputs: list[str] = []
    in_st = False
    buf: list[str] = []

    in_access = False
    access_scope: str | None = None
    in_symbol = False
    components: list[str] = []

    def flush_access() -> None:
        nonlocal in_access, access_scope, in_symbol, components
        if not components:
            in_access = False
            access_scope = None
            in_symbol = False
            components = []
            return
        sym = ".".join(components)
        if access_scope == "LocalVariable":
            sym = "#" + sym
        buf.append(sym)
        in_access = False
        access_scope = None
        in_symbol = False
        components = []

    for event, elem in ET.iterparse(path, events=("start", "end")):
        tag = strip_ns(elem.tag)
        if event == "start" and tag == "StructuredText":
            in_st = True
            buf = []
        elif in_st and event == "start":
            if tag == "Access":
                in_access = True
                access_scope = elem.attrib.get("Scope")
                in_symbol = False
                components = []
            elif in_access and tag == "Symbol":
                in_symbol = True
            elif in_access and in_symbol and tag == "Component":
                name = elem.attrib.get("Name")
                if name:
                    components.append(name)
            elif tag == "Token":
                text = elem.attrib.get("Text", "")
                if text:
                    buf.append(text)
            elif tag == "Blank":
                num = elem.attrib.get("Num", "1")
                try:
                    n = max(1, int(num))
                except ValueError:
                    n = 1
                buf.append(" " * n)
            elif tag == "NewLine":
                buf.append("\n")
        elif in_st and event == "end":
            if tag == "Access" and in_access:
                flush_access()
            elif tag == "StructuredText":
                in_st = False
                text = "".join(buf).strip()
                if text:
                    outputs.append(text)
            elem.clear()
        else:
            if event == "end":
                elem.clear()

    return outputs


@dataclasses.dataclass
class FlgNetPart:
    name: str
    uid: str
    negated: set[str]


@dataclasses.dataclass
class FlgNetNetwork:
    title: str
    comment: str
    scl_lines: list[str]
    warnings: list[str]


class _DSU:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        p = self.parent.get(x)
        if p is None:
            self.parent[x] = x
            return x
        if p != x:
            self.parent[x] = self.find(p)
        return self.parent[x]

    def union(self, a: str, b: str) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def _fmt_or(exprs: list[str]) -> str:
    exprs = [e for e in exprs if e and e != "FALSE"]
    if not exprs:
        return "FALSE"
    if "TRUE" in exprs:
        return "TRUE"
    uniq: list[str] = []
    seen = set()
    for e in exprs:
        if e not in seen:
            seen.add(e)
            uniq.append(e)
    if len(uniq) == 1:
        return uniq[0]
    return "(" + " OR ".join(uniq) + ")"


def _fmt_and(a: str, b: str) -> str:
    if a == "FALSE" or b == "FALSE":
        return "FALSE"
    if a == "TRUE":
        return b
    if b == "TRUE":
        return a
    if a == b:
        return a
    return "(" + a + " AND " + b + ")"


def _pin(kind: str, uid: str, name: str | None = None) -> str:
    if name is None:
        return f"{kind}:{uid}"
    return f"{kind}:{uid}:{name}"


def extract_statement_list_networks(path: Path) -> list[tuple[str, str, list[str]]]:
    """
    Extract tokenized STL (StatementList) networks into readable pseudo text.
    Output is for review only (not SCL).
    Returns list of (title, comment, lines).
    """
    nets: list[tuple[str, str, list[str]]] = []

    in_compile = False
    compile_title = ""
    compile_comment = ""
    in_title = False
    in_comment = False
    in_text = False

    in_stmtlist = False
    in_stmt = False
    stmt_tokens: list[str] = []
    stmt_lines: list[str] = []

    def flush_network() -> None:
        nonlocal stmt_lines, compile_title, compile_comment
        if stmt_lines:
            nets.append((compile_title, compile_comment, stmt_lines))
        stmt_lines = []

    for event, elem in ET.iterparse(path, events=("start", "end")):
        tag = strip_ns(elem.tag)
        if event == "start":
            if tag == "SW.Blocks.CompileUnit":
                in_compile = True
                compile_title = ""
                compile_comment = ""
            elif in_compile and tag == "MultilingualText":
                comp = elem.attrib.get("CompositionName")
                if comp == "Title":
                    in_title = True
                elif comp == "Comment":
                    in_comment = True
            elif (in_title or in_comment) and tag == "Text":
                in_text = True
            elif tag == "StatementList":
                in_stmtlist = True
                stmt_lines = []
            elif in_stmtlist and tag == "StlStatement":
                in_stmt = True
                stmt_tokens = []
            elif in_stmt and tag == "StlToken":
                t = elem.attrib.get("Text", "")
                if t and t != "EMPTY_LINE":
                    stmt_tokens.append(t)
        elif event == "end":
            if tag == "Text" and in_text:
                txt = (elem.text or "").strip()
                if txt:
                    if in_title and not compile_title:
                        compile_title = txt
                    if in_comment and not compile_comment:
                        compile_comment = txt
                in_text = False
            elif tag == "MultilingualText":
                in_title = False
                in_comment = False
            elif tag == "StlStatement" and in_stmt:
                line = " ".join(stmt_tokens).strip()
                if line:
                    stmt_lines.append(line)
                in_stmt = False
                stmt_tokens = []
            elif tag == "StatementList" and in_stmtlist:
                in_stmtlist = False
                flush_network()
            elif tag == "SW.Blocks.CompileUnit" and in_compile:
                in_compile = False
            elem.clear()

    return nets


def extract_flgnet_lad_networks(path: Path) -> list[FlgNetNetwork]:
    """
    Best-effort conversion for LAD/FBD FlgNet networks to simple SCL statements.

    Supports a conservative subset:
    - Contact + Coil / SCoil / RCoil networks (series/parallel as boolean expressions)
    - Everything else is reported as warnings (kept as comments in output).

    Output is intended for review only and is NOT guaranteed to compile or preserve behavior.
    """
    networks: list[FlgNetNetwork] = []

    in_compile = False
    compile_title = ""
    compile_comment = ""
    in_title = False
    in_comment = False
    in_text = False

    in_flgnet = False
    access_scope: dict[str, str] = {}
    access_components: dict[str, list[str]] = {}
    parts: dict[str, FlgNetPart] = {}
    wires: list[list[str]] = []
    wire_nodes: list[str] = []
    in_access = False
    cur_access_uid: str | None = None
    in_symbol = False
    cur_part: FlgNetPart | None = None
    cur_wire_powerrail = False
    unsupported_part_counts: Counter[str] = Counter()

    def flush_network() -> None:
        nonlocal access_scope, access_components, parts, wires, wire_nodes, cur_wire_powerrail, unsupported_part_counts
        if not in_flgnet and not parts and not wires and not access_components:
            return

        dsu = _DSU()
        net_power: set[str] = set()
        net_ident_access: defaultdict[str, set[str]] = defaultdict(set)

        for nodes in wires:
            if not nodes:
                continue
            first = nodes[0]
            for n in nodes[1:]:
                dsu.union(first, n)
            if "Powerrail" in nodes:
                net_power.add(dsu.find(first))
            for n in nodes:
                if n.startswith("IdentCon:"):
                    _, auid = n.split(":", 1)
                    net_ident_access[dsu.find(first)].add(auid)

        access_symbol: dict[str, str] = {}
        for auid, comps in access_components.items():
            scope = access_scope.get(auid, "")
            sym = ".".join(comps)
            if scope == "LocalVariable":
                sym = "#" + sym
            access_symbol[auid] = sym

        net_symbol: dict[str, str] = {}
        for net, auids in net_ident_access.items():
            for auid in sorted(auids):
                sym = access_symbol.get(auid)
                if sym:
                    net_symbol[net] = sym
                    break

        def net_of(node: str) -> str:
            return dsu.find(node)

        contacts: list[FlgNetPart] = []
        coils: list[FlgNetPart] = []
        for p in parts.values():
            if p.name == "Contact":
                contacts.append(p)
            elif p.name in {"Coil", "SCoil", "RCoil"}:
                coils.append(p)

        contact_defs: list[tuple[str, str, str, bool]] = []
        warnings: list[str] = []
        for c in contacts:
            in_node = _pin("NameCon", c.uid, "in")
            out_node = _pin("NameCon", c.uid, "out")
            op_node = _pin("NameCon", c.uid, "operand")
            in_net = net_of(in_node)
            out_net = net_of(out_node)
            op_net = net_of(op_node)
            op_sym = net_symbol.get(op_net, "")
            if not op_sym:
                warnings.append(f"Contact UId={c.uid}: nelze určit operand symbol.")
                continue
            neg = "operand" in c.negated
            contact_defs.append((in_net, out_net, op_sym, neg))

        net_drivers: defaultdict[str, set[str]] = defaultdict(set)
        for n in net_power:
            net_drivers[n].add("TRUE")

        net_expr: dict[str, str] = {}

        def recompute() -> None:
            nonlocal net_expr
            net_expr = {}
            for n, drivers in net_drivers.items():
                net_expr[n] = _fmt_or(sorted(drivers))

        recompute()
        for _ in range(200):
            changed = False
            for in_net, out_net, op_sym, neg in contact_defs:
                in_expr = net_expr.get(in_net)
                if not in_expr:
                    continue
                op_expr = f"NOT {op_sym}" if neg else op_sym
                out_driver = _fmt_and(in_expr, op_expr)
                if out_driver and out_driver != "FALSE":
                    if out_driver not in net_drivers[out_net]:
                        net_drivers[out_net].add(out_driver)
                        changed = True
            if not changed:
                break
            recompute()

        scl_lines: list[str] = []
        if compile_title:
            scl_lines.append(f"// Síť: {compile_title}")
        if compile_comment:
            scl_lines.append(f"// Komentář: {compile_comment}")

        if unsupported_part_counts:
            top = ", ".join([f"{k}({v})" for k, v in unsupported_part_counts.most_common(8)])
            warnings.append(f"Síť obsahuje nepodporované prvky (ponecháno jen jako komentář): {top}")

        for coil in coils:
            in_node = _pin("NameCon", coil.uid, "in")
            op_node = _pin("NameCon", coil.uid, "operand")
            in_net = net_of(in_node)
            op_net = net_of(op_node)
            cond = net_expr.get(in_net, "")
            target = net_symbol.get(op_net, "")
            if not target:
                warnings.append(f"{coil.name} UId={coil.uid}: nelze určit cílový symbol.")
                continue
            if not cond:
                warnings.append(f"{coil.name} UId={coil.uid}: nelze určit podmínku (vstupní síť).")
                continue
            if coil.name == "Coil":
                scl_lines.append(f"{target} := {cond};")
            elif coil.name == "SCoil":
                scl_lines.append(f"IF {cond} THEN {target} := TRUE; END_IF;")
            elif coil.name == "RCoil":
                scl_lines.append(f"IF {cond} THEN {target} := FALSE; END_IF;")

        if warnings:
            scl_lines.append("// --- Poznámky / omezení převodu ---")
            for w in warnings[:40]:
                scl_lines.append("// " + w)

        networks.append(
            FlgNetNetwork(
                title=compile_title,
                comment=compile_comment,
                scl_lines=scl_lines,
                warnings=warnings,
            )
        )

        access_scope = {}
        access_components = {}
        parts = {}
        wires = []
        wire_nodes = []
        cur_wire_powerrail = False
        unsupported_part_counts = Counter()

    for event, elem in ET.iterparse(path, events=("start", "end")):
        tag = strip_ns(elem.tag)
        if event == "start":
            if tag == "SW.Blocks.CompileUnit":
                in_compile = True
                compile_title = ""
                compile_comment = ""
            elif in_compile and tag == "MultilingualText":
                comp = elem.attrib.get("CompositionName")
                if comp == "Title":
                    in_title = True
                elif comp == "Comment":
                    in_comment = True
            elif (in_title or in_comment) and tag == "Text":
                in_text = True
            elif tag == "FlgNet":
                in_flgnet = True
                access_scope = {}
                access_components = {}
                parts = {}
                wires = []
                unsupported_part_counts = Counter()
            elif in_flgnet and tag == "Access":
                in_access = True
                cur_access_uid = elem.attrib.get("UId")
                cur_access_scope = elem.attrib.get("Scope")
                if cur_access_uid:
                    access_scope[cur_access_uid] = cur_access_scope or ""
                    access_components[cur_access_uid] = []
            elif in_flgnet and in_access and tag == "Symbol":
                in_symbol = True
            elif in_flgnet and in_access and in_symbol and tag == "Component":
                nm = elem.attrib.get("Name")
                if nm and cur_access_uid:
                    access_components[cur_access_uid].append(nm)
            elif in_flgnet and tag == "Part":
                nm = elem.attrib.get("Name", "")
                uid = elem.attrib.get("UId", "")
                cur_part = FlgNetPart(name=nm, uid=uid, negated=set())
                if cur_part.uid:
                    parts[cur_part.uid] = cur_part
                    if nm not in {"Contact", "Coil", "SCoil", "RCoil"}:
                        unsupported_part_counts[nm] += 1
            elif in_flgnet and cur_part is not None and tag == "Negated":
                n = elem.attrib.get("Name")
                if n:
                    cur_part.negated.add(n)
            elif in_flgnet and tag == "Wire":
                wire_nodes = []
                cur_wire_powerrail = False
            elif in_flgnet and tag == "Powerrail":
                cur_wire_powerrail = True
            elif in_flgnet and tag == "NameCon":
                uid = elem.attrib.get("UId", "")
                nm = elem.attrib.get("Name", "")
                if uid and nm:
                    wire_nodes.append(_pin("NameCon", uid, nm))
            elif in_flgnet and tag == "IdentCon":
                uid = elem.attrib.get("UId", "")
                if uid:
                    wire_nodes.append(_pin("IdentCon", uid))
        elif event == "end":
            if tag == "Text" and in_text:
                txt = (elem.text or "").strip()
                if txt:
                    if in_title and not compile_title:
                        compile_title = txt
                    if in_comment and not compile_comment:
                        compile_comment = txt
                in_text = False
            elif tag == "MultilingualText":
                in_title = False
                in_comment = False
            elif tag == "Access":
                in_access = False
                cur_access_uid = None
                in_symbol = False
            elif tag == "Part":
                cur_part = None
            elif tag == "Wire":
                if cur_wire_powerrail:
                    wire_nodes.append("Powerrail")
                if wire_nodes:
                    wires.append(wire_nodes)
                wire_nodes = []
                cur_wire_powerrail = False
            elif tag == "FlgNet" and in_flgnet:
                in_flgnet = False
                flush_network()
            elif tag == "SW.Blocks.CompileUnit" and in_compile:
                in_compile = False
            elem.clear()

    return networks


def emit_member_lines(members: list[Member], indent: str) -> list[str]:
    lines: list[str] = []
    for m in members:
        name = scl_member_name(m.name)
        if m.children:
            lines.append(f"{indent}{name} : STRUCT")
            lines.extend(emit_member_lines(m.children, indent + "  "))
            lines.append(f"{indent}END_STRUCT;")
            continue
        dt = m.datatype or "Struct"
        lines.append(f"{indent}{name} : {dt};")
    return lines


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Export TIA Openness XML interfaces/types into review SCL files.")
    ap.add_argument("--export-root", default="EXPORT", help="TIA export root (default: EXPORT)")
    ap.add_argument("--out", default="deep_reader/scl_export", help="Output folder (default: deep_reader/scl_export)")
    args = ap.parse_args()

    export_root = Path(args.export_root)
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "export_root": export_root.as_posix(),
        "outputs": [],
        "notes": [
            "These SCL files are generated for review only.",
            "StructuredText networks are reconstructed best-effort from tokenized XML and may not compile as-is.",
            "LAD/FBD FlgNet networks are converted best-effort for simple Contact/Coil patterns; complex networks are kept as comments with warnings.",
            "STL StatementList is reconstructed as comments (not executable SCL).",
        ],
    }

    # UDTs
    for xml_path in (export_root / "PLC data types").rglob("*.xml"):
        try:
            tree = ET.parse(xml_path)
        except Exception:
            continue
        root = tree.getroot()
        first = next(iter(root), None)
        # Determine type name from the XML, but prefer the <Name> in AttributeList
        type_name = None
        type_kind = None
        for elem in root.iter():
            t = strip_ns(elem.tag)
            if t.startswith("SW.Types.") and type_kind is None:
                type_kind = t
            if t == "Name" and type_name is None and (elem.text or "").strip():
                type_name = (elem.text or "").strip()
        if not type_kind or not type_name:
            continue

        sections = parse_interface_sections(xml_path)
        members = sections.get("None", [])
        scl_lines = []
        scl_lines.append(f"TYPE {scl_quote_name(type_name)}")
        scl_lines.append("STRUCT")
        scl_lines.extend(emit_member_lines(members, "  "))
        scl_lines.append("END_STRUCT;")
        scl_lines.append("END_TYPE")
        scl_text = "\n".join(scl_lines) + "\n"

        out_path = out_root / "types" / f"{safe_filename(type_name)}.scl"
        write_text(out_path, scl_text)
        manifest["outputs"].append(
            {
                "kind": type_kind,
                "name": type_name,
                "source_path": xml_path.as_posix(),
                "out_path": out_path.as_posix(),
                "status": "type_exported",
            }
        )

    # Blocks / DBs
    for xml_path in (export_root / "Program blocks").rglob("*.xml"):
        header = parse_block_header(xml_path)
        kind = header.get("kind", "")
        name = header.get("name", "")
        lang = header.get("language", "")
        if not kind or not name:
            continue

        sections = parse_interface_sections(xml_path)
        st_networks = extract_structured_text_code(xml_path)
        flgnet_networks = extract_flgnet_lad_networks(xml_path) if lang in {"LAD", "FBD"} else []
        stl_networks = extract_statement_list_networks(xml_path) if lang == "STL" else []

        out_subdir = out_root / "blocks" / kind
        out_path = out_subdir / f"{safe_filename(name)}.scl"

        # DBs
        if kind in {"GlobalDB", "InstanceDB"}:
            members = sections.get("Static", []) or sections.get("None", [])
            scl_lines = []
            scl_lines.append(f"DATA_BLOCK {scl_quote_name(name)}")
            scl_lines.append("VAR")
            scl_lines.extend(emit_member_lines(members, "  "))
            scl_lines.append("END_VAR")
            scl_lines.append("BEGIN")
            scl_lines.append("END_DATA_BLOCK")
            write_text(out_path, "\n".join(scl_lines) + "\n")
            manifest["outputs"].append(
                {
                    "kind": f"SW.Blocks.{kind}",
                    "name": name,
                    "source_path": xml_path.as_posix(),
                    "out_path": out_path.as_posix(),
                    "status": "db_interface_exported",
                    "original_language": lang,
                }
            )
            continue

        # OB/FC/FB skeletons
        scl_lines = []
        if kind == "OB":
            scl_lines.append(f"ORGANIZATION_BLOCK {scl_quote_name(name)}")
        elif kind == "FB":
            scl_lines.append(f"FUNCTION_BLOCK {scl_quote_name(name)}")
        elif kind == "FC":
            # Default to VOID return if unknown
            scl_lines.append(f"FUNCTION {scl_quote_name(name)} : Void")
        else:
            # Unknown block type: still emit a header for review
            scl_lines.append(f"// Unknown block kind: {kind}")
            scl_lines.append(f"// Source: {xml_path.as_posix()}")
            write_text(out_path, "\n".join(scl_lines) + "\n")
            manifest["outputs"].append(
                {
                    "kind": f"SW.Blocks.{kind}",
                    "name": name,
                    "source_path": xml_path.as_posix(),
                    "out_path": out_path.as_posix(),
                    "status": "skipped_unknown_kind",
                    "original_language": lang,
                }
            )
            continue

        # Interface sections
        in_members = sections.get("Input", [])
        out_members = sections.get("Output", [])
        inout_members = sections.get("InOut", [])
        static_members = sections.get("Static", [])
        temp_members = sections.get("Temp", [])
        const_members = sections.get("Constant", [])

        if in_members:
            scl_lines.append("VAR_INPUT")
            scl_lines.extend(emit_member_lines(in_members, "  "))
            scl_lines.append("END_VAR")
        if out_members:
            scl_lines.append("VAR_OUTPUT")
            scl_lines.extend(emit_member_lines(out_members, "  "))
            scl_lines.append("END_VAR")
        if inout_members:
            scl_lines.append("VAR_IN_OUT")
            scl_lines.extend(emit_member_lines(inout_members, "  "))
            scl_lines.append("END_VAR")
        if static_members and kind in {"FB"}:
            scl_lines.append("VAR")
            scl_lines.extend(emit_member_lines(static_members, "  "))
            scl_lines.append("END_VAR")
        if temp_members:
            scl_lines.append("VAR_TEMP")
            scl_lines.extend(emit_member_lines(temp_members, "  "))
            scl_lines.append("END_VAR")
        if const_members:
            scl_lines.append("VAR_CONSTANT")
            scl_lines.extend(emit_member_lines(const_members, "  "))
            scl_lines.append("END_VAR")

        scl_lines.append("BEGIN")
        scl_lines.append(f"  // Původní jazyk: {lang or 'unknown'}")
        scl_lines.append(f"  // Zdroj XML: {xml_path.as_posix()}")
        has_any_logic = False
        if st_networks:
            has_any_logic = True
            scl_lines.append("  // --- Rekonstruovaný StructuredText (best-effort) ---")
            for i, code in enumerate(st_networks, start=1):
                scl_lines.append(f"  // Network {i}")
                for line in code.splitlines():
                    scl_lines.append("  " + line)
        if flgnet_networks:
            has_any_logic = True
            scl_lines.append("  // --- LAD/FBD → SCL (orientační převod, jen pro revizi) ---")
            for i, net in enumerate(flgnet_networks, start=1):
                scl_lines.append(f"  // Network {i}")
                for line in net.scl_lines:
                    scl_lines.append("  " + line)
        if stl_networks:
            has_any_logic = True
            scl_lines.append("  // --- STL (StatementList) rekonstruováno jako komentář ---")
            for i, (title, comment, lines) in enumerate(stl_networks, start=1):
                scl_lines.append(f"  // Network {i}")
                if title:
                    scl_lines.append(f"  // Síť: {title}")
                if comment:
                    scl_lines.append(f"  // Komentář: {comment}")
                for ln in lines[:2000]:
                    scl_lines.append("  // " + ln)
        if not has_any_logic:
            scl_lines.append("  // (Nebylo nalezeno StructuredText/FlgNet/StatementList; logika může být v GRAPH nebo v nepodporované reprezentaci.)")
        scl_lines.append("END_" + ("ORGANIZATION_BLOCK" if kind == "OB" else ("FUNCTION_BLOCK" if kind == "FB" else "FUNCTION")))

        write_text(out_path, "\n".join(scl_lines) + "\n")
        manifest["outputs"].append(
            {
                "kind": f"SW.Blocks.{kind}",
                "name": name,
                "source_path": xml_path.as_posix(),
                "out_path": out_path.as_posix(),
                "status": "block_interface_exported",
                "original_language": lang,
                "structured_text_networks": len(st_networks),
                "flgnet_networks": len(flgnet_networks),
                "statementlist_networks": len(stl_networks),
            }
        )

    (out_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote SCL exports to: {out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
