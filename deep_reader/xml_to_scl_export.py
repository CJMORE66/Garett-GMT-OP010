#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import html
import json
import re
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
            "These SCL files are generated for review. LAD/FBD/STL/GRAPH logic is not automatically translated.",
            "StructuredText networks are reconstructed best-effort from tokenized XML and may not compile as-is.",
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
        if st_networks:
            scl_lines.append("  // --- Rekonstruovaný StructuredText (best-effort) ---")
            for i, code in enumerate(st_networks, start=1):
                scl_lines.append(f"  // Network {i}")
                for line in code.splitlines():
                    scl_lines.append("  " + line)
        else:
            scl_lines.append("  // (Žádný StructuredText network nebyl nalezen; LAD/STL/GRAPH není automaticky překládán.)")
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
            }
        )

    (out_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote SCL exports to: {out_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
