#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Iterable, Iterator
from xml.etree import ElementTree as ET


def strip_ns(tag: str) -> str:
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


@dataclasses.dataclass(frozen=True)
class ObjectRef:
    kind: str
    name: str
    number: str | None
    language: str | None
    source_path: str


@dataclasses.dataclass
class SymbolUse:
    symbol: str
    root: str
    read: int = 0
    write: int = 0
    unknown: int = 0
    blocks: set[str] = dataclasses.field(default_factory=set)
    evidence: list[str] = dataclasses.field(default_factory=list)  # capped
    hmi_tags: set[str] = dataclasses.field(default_factory=set)

    def add(self, block: str, rw: str, evidence: str) -> None:
        self.blocks.add(block)
        if rw == "read":
            self.read += 1
        elif rw == "write":
            self.write += 1
        else:
            self.unknown += 1
        if len(self.evidence) < 5 and evidence not in self.evidence:
            self.evidence.append(evidence)


CONTACT_PARTS = {
    "Contact",
    "PContact",
    "NContact",
    "RContact",
}

COIL_PARTS = {
    "Coil",
    "SCoil",
    "RCoil",
}


def iter_xml_paths(root: Path) -> Iterator[Path]:
    for path in root.rglob("*.xml"):
        if path.is_file():
            yield path


def safe_text(elem: ET.Element | None) -> str | None:
    if elem is None or elem.text is None:
        return None
    return elem.text.strip()


def parse_program_block_xml(path: Path) -> dict[str, Any]:
    """
    Parse Siemens Openness XML export for OB/FB/FC/DB and extract:
    - block metadata (kind/name/number/language)
    - call edges (caller -> callee)
    - symbol uses (GlobalVariable accesses with best-effort read/write)
    - per-block referenced roots (top component of symbol path)
    """
    result: dict[str, Any] = {
        "kind": None,
        "name": None,
        "number": None,
        "language": None,
        "calls": [],  # list of (callee_name, block_type)
        "uses": [],  # list of (symbol_path, rw_kind, evidence)
    }

    access_uid_to_symbol: dict[str, str] = {}
    part_uid_to_name: dict[str, str] = {}
    call_uid_to_info: dict[str, dict[str, Any]] = {}

    in_flgnet = False
    in_structured_text = False
    block_attr_seen = False
    block_attr_open = False
    block_attr_depth = 0
    block_kind = None
    block_name = None

    # StructuredText token stream state (best-effort)
    st_mode: str = "unknown"  # "unknown" | "rhs"
    st_pending_globals: list[tuple[str, str]] = []  # (symbol, evidence)
    st_next_rw_override: str | None = None  # e.g. after '=>'
    st_in_access = False
    st_access_scope: str | None = None
    st_in_symbol = False
    st_components: list[str] = []

    # iterparse keeps memory bounded for large LAD exports
    for event, elem in ET.iterparse(path, events=("start", "end")):
        tag = strip_ns(elem.tag)

        if event == "start":
            if tag.startswith("SW.Blocks.") and result["kind"] is None:
                block_kind = tag.split(".", 2)[-1]
                result["kind"] = block_kind
            elif tag == "AttributeList":
                if block_kind is not None and not block_attr_seen:
                    block_attr_seen = True
                    block_attr_open = True
                    block_attr_depth = 1
                elif block_attr_open:
                    block_attr_depth += 1
            elif tag == "FlgNet":
                in_flgnet = True
                access_uid_to_symbol.clear()
                part_uid_to_name.clear()
                call_uid_to_info.clear()
            elif tag == "StructuredText":
                in_structured_text = True
                st_mode = "unknown"
                st_pending_globals.clear()
                st_next_rw_override = None
                st_in_access = False
                st_access_scope = None
                st_in_symbol = False
                st_components.clear()
            elif in_structured_text and tag == "Token":
                tok = elem.attrib.get("Text")
                if tok == ":=":
                    # Assignment: pending globals before ':=' are reads except the last one (write).
                    if st_pending_globals:
                        for sym, ev in st_pending_globals[:-1]:
                            result["uses"].append((sym, "read", ev))
                        sym, ev = st_pending_globals[-1]
                        result["uses"].append((sym, "write", ev))
                        st_pending_globals.clear()
                    st_mode = "rhs"
                    st_next_rw_override = None
                elif tok == "=>":
                    # Output parameter binding for call: next variable is written by callee.
                    st_next_rw_override = "write"
                elif tok == ";":
                    # End statement: any pending globals are reads.
                    for sym, ev in st_pending_globals:
                        result["uses"].append((sym, "read", ev))
                    st_pending_globals.clear()
                    st_mode = "unknown"
                    st_next_rw_override = None
                else:
                    # Other tokens do not affect the simple rw heuristic.
                    pass
            elif in_structured_text and tag == "Access":
                st_in_access = True
                st_access_scope = elem.attrib.get("Scope")
                st_in_symbol = False
                st_components = []
            elif in_structured_text and st_in_access and tag == "Symbol":
                st_in_symbol = True
            elif in_structured_text and st_in_access and st_in_symbol and tag == "Component":
                name = elem.attrib.get("Name")
                if name:
                    st_components.append(name)

        if event == "end":
            if block_attr_open and tag in {"Name", "Number", "ProgrammingLanguage"} and result.get(tag.lower()) is None:
                text = safe_text(elem)
                if text:
                    if tag == "Name":
                        block_name = text
                        result["name"] = text
                    elif tag == "Number":
                        result["number"] = text
                    elif tag == "ProgrammingLanguage":
                        result["language"] = text

            # FlgNet parsing (LAD/FBD compile unit source)
            if in_flgnet:
                if tag == "Access":
                    uid = elem.attrib.get("UId")
                    scope = elem.attrib.get("Scope", "")
                    if uid and scope in {"GlobalVariable", "GlobalConstant"}:
                        symbol = None
                        if scope == "GlobalVariable":
                            sym = next((c for c in list(elem) if strip_ns(c.tag) == "Symbol"), None)
                            if sym is not None:
                                comps = [c.attrib.get("Name", "") for c in list(sym) if strip_ns(c.tag) == "Component"]
                                comps = [c for c in comps if c]
                                if comps:
                                    symbol = ".".join(comps)
                        elif scope == "GlobalConstant":
                            const = next((c for c in list(elem) if strip_ns(c.tag) == "Constant"), None)
                            if const is not None:
                                name = const.attrib.get("Name")
                                if name:
                                    symbol = f"CONST:{name}"
                        if symbol:
                            access_uid_to_symbol[uid] = symbol

                elif tag == "Part":
                    uid = elem.attrib.get("UId")
                    name = elem.attrib.get("Name")
                    if uid and name:
                        part_uid_to_name[uid] = name

                elif tag == "Call":
                    uid = elem.attrib.get("UId")
                    call_info = next((c for c in list(elem) if strip_ns(c.tag) == "CallInfo"), None)
                    if uid and call_info is not None:
                        callee = call_info.attrib.get("Name")
                        block_type = call_info.attrib.get("BlockType")
                        if callee and block_type:
                            params: dict[str, str] = {}
                            for p in list(call_info):
                                if strip_ns(p.tag) != "Parameter":
                                    continue
                                pname = p.attrib.get("Name")
                                section = p.attrib.get("Section")
                                if pname and section:
                                    params[pname] = section
                            call_uid_to_info[uid] = {"callee": callee, "block_type": block_type, "params": params}
                            result["calls"].append((callee, block_type))

                elif tag == "Wire":
                    # Best-effort read/write inference:
                    # - Call parameters: section Input/Output/InOut
                    # - Contacts: read, Coils: write
                    # Anything else: unknown
                    access_uids = [c.attrib.get("UId") for c in list(elem) if strip_ns(c.tag) == "IdentCon" and c.attrib.get("UId")]
                    name_cons = [
                        (c.attrib.get("UId"), c.attrib.get("Name")) for c in list(elem) if strip_ns(c.tag) == "NameCon"
                    ]
                    for access_uid in access_uids:
                        symbol = access_uid_to_symbol.get(access_uid or "")
                        if not symbol:
                            continue
                        for target_uid, connector_name in name_cons:
                            if not target_uid or not connector_name:
                                continue
                            rw = "unknown"
                            if target_uid in call_uid_to_info:
                                section = call_uid_to_info[target_uid]["params"].get(connector_name)
                                if section == "Input":
                                    rw = "read"
                                elif section == "Output":
                                    rw = "write"
                                elif section == "InOut":
                                    rw = "unknown"
                            elif target_uid in part_uid_to_name:
                                part = part_uid_to_name[target_uid]
                                if part in CONTACT_PARTS and connector_name == "operand":
                                    rw = "read"
                                elif part in COIL_PARTS and connector_name == "operand":
                                    rw = "write"
                            evidence = f"{path.as_posix()}:{block_name or ''}:FlgNet"
                            result["uses"].append((symbol, rw, evidence))

                elif tag == "FlgNet":
                    in_flgnet = False
                    access_uid_to_symbol.clear()
                    part_uid_to_name.clear()
                    call_uid_to_info.clear()

            # StructuredText parsing (tokenized SCL)
            if in_structured_text:
                if tag == "Access" and st_in_access:
                    if st_access_scope == "GlobalVariable" and st_components:
                        sym = ".".join(st_components)
                        evidence = f"{path.as_posix()}:{block_name or ''}:StructuredText"
                        if st_next_rw_override:
                            result["uses"].append((sym, st_next_rw_override, evidence))
                            st_next_rw_override = None
                        elif st_mode == "rhs":
                            result["uses"].append((sym, "read", evidence))
                        else:
                            st_pending_globals.append((sym, evidence))
                    st_in_access = False
                    st_access_scope = None
                    st_in_symbol = False
                    st_components = []
                elif tag == "StructuredText":
                    # Flush any dangling pending globals at end of structured text block
                    for sym, ev in st_pending_globals:
                        result["uses"].append((sym, "read", ev))
                    st_pending_globals.clear()
                    st_mode = "unknown"
                    st_next_rw_override = None
                    in_structured_text = False

            if tag == "AttributeList" and block_attr_open:
                block_attr_depth -= 1
                if block_attr_depth <= 0:
                    block_attr_open = False
                    block_attr_depth = 0

            # IMPORTANT: while inside a FlgNet, we must not clear child elements
            # (e.g., IdentCon/NameCon/Component) before their parent (Wire/Access)
            # is processed, otherwise attributes needed for evidence extraction are lost.
            if (not in_flgnet or tag == "FlgNet") and (not in_structured_text or tag == "StructuredText"):
                elem.clear()

    return result


def parse_automationml_hardware(path: Path) -> dict[str, Any]:
    """
    Very lightweight AutomationML (TIA HW export) parser.
    Extracts CPU(s) and rack modules with OrderNumber/TypeName/PositionNumber.
    """
    cpu_list: list[dict[str, str]] = []
    modules: list[dict[str, str]] = []
    networks: list[str] = []

    # AML typically has no default namespace in the root CAEXFile (as seen in this export)
    current_internal: list[dict[str, Any]] = []

    for event, elem in ET.iterparse(path, events=("start", "end")):
        tag = strip_ns(elem.tag)

        if event == "start" and tag == "InternalElement":
            current_internal.append(
                {
                    "Name": elem.attrib.get("Name", ""),
                    "ID": elem.attrib.get("ID", ""),
                    "attrs": {},
                }
            )
        elif event == "end" and tag == "Attribute":
            if not current_internal:
                elem.clear()
                continue
            attr_name = elem.attrib.get("Name")
            if attr_name:
                value_elem = next((c for c in list(elem) if strip_ns(c.tag) == "Value"), None)
                value = safe_text(value_elem) or ""
                current_internal[-1]["attrs"][attr_name] = value
            elem.clear()
        elif event == "end" and tag == "InternalElement":
            if current_internal:
                node = current_internal.pop()
                name = node.get("Name", "")
                attrs: dict[str, str] = node.get("attrs", {})

                type_name = attrs.get("TypeName", "")
                device_item_type = attrs.get("DeviceItemType", "")
                type_identifier = attrs.get("TypeIdentifier", "")
                pos = attrs.get("PositionNumber", "")
                fw = attrs.get("FirmwareVersion", "")

                # Network nodes (PN/IE_*)
                if name.startswith("PN/IE_") or attrs.get("Type") == "Ethernet":
                    if name:
                        networks.append(name)

                if device_item_type.upper() == "CPU" or type_name.upper().startswith("CPU"):
                    cpu_list.append(
                        {
                            "Name": name,
                            "TypeName": type_name,
                            "TypeIdentifier": type_identifier,
                            "FirmwareVersion": fw,
                            "PositionNumber": pos,
                        }
                    )
                elif type_identifier.startswith("OrderNumber:") or type_name:
                    # Keep rack/module entries (best-effort)
                    if pos or type_identifier.startswith("OrderNumber:"):
                        modules.append(
                            {
                                "Name": name,
                                "TypeName": type_name,
                                "TypeIdentifier": type_identifier,
                                "FirmwareVersion": fw,
                                "PositionNumber": pos,
                                "DeviceItemType": device_item_type,
                            }
                        )
            elem.clear()

    return {
        "source_path": path.as_posix(),
        "networks": sorted(set(networks)),
        "cpus": cpu_list,
        "modules_count": len(modules),
        "modules_sample": modules[:50],
        "notes": [
            "AutomationML parsing is best-effort; it extracts CPU/module identity and position but does not build full PROFINET topology.",
        ],
    }


def parse_plc_tags_xml(path: Path) -> tuple[str | None, list[dict[str, str]]]:
    table_name: str | None = None
    tags: list[dict[str, str]] = []

    current_tag: dict[str, str] | None = None
    in_tag = False
    in_attribute_list = False

    for event, elem in ET.iterparse(path, events=("start", "end")):
        tag = strip_ns(elem.tag)

        if event == "start":
            if tag == "SW.Tags.PlcTagTable":
                in_tag = False
            elif tag == "SW.Tags.PlcTag":
                in_tag = True
                current_tag = {}
            elif tag == "AttributeList":
                in_attribute_list = True

        if event == "end":
            if in_attribute_list and tag == "Name":
                text = safe_text(elem)
                if text:
                    if in_tag and current_tag is not None and "Name" not in current_tag:
                        current_tag["Name"] = text
                    elif table_name is None:
                        table_name = text
            if in_tag and current_tag is not None and in_attribute_list and tag in {
                "DataTypeName",
                "LogicalAddress",
                "ExternalAccessible",
                "ExternalVisible",
                "ExternalWritable",
            }:
                text = safe_text(elem)
                if text is not None:
                    current_tag[tag] = text

            if tag == "SW.Tags.PlcTag":
                if current_tag and current_tag.get("Name"):
                    tags.append(current_tag)
                in_tag = False
                current_tag = None

            if tag == "AttributeList":
                in_attribute_list = False

            elem.clear()

    return table_name, tags


def parse_hmi_tags_xml(path: Path) -> tuple[str | None, list[dict[str, str]]]:
    table_name: str | None = None
    tags: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    in_tag = False
    in_attribute_list = False
    in_link_list = False
    current_link: str | None = None

    for event, elem in ET.iterparse(path, events=("start", "end")):
        tag = strip_ns(elem.tag)

        if event == "start":
            if tag == "Hmi.Tag.Tag":
                in_tag = True
                current = {}
            elif tag == "AttributeList":
                in_attribute_list = True
            elif tag == "LinkList":
                in_link_list = True
            elif in_link_list and tag in {"ControllerTag", "Connection", "DataType", "HmiDataType", "AcquisitionCycle"}:
                current_link = tag

        if event == "end":
            if in_attribute_list and tag == "Name":
                text = safe_text(elem)
                if text:
                    if in_tag and current is not None and "Name" not in current:
                        current["Name"] = text
                    elif table_name is None:
                        table_name = text

            if in_link_list and current is not None and current_link and tag == "Name":
                # The HMI export places link target values in nested <Name> nodes
                text = safe_text(elem)
                if text:
                    current[current_link] = text
                current_link = None

            if tag == "Hmi.Tag.Tag":
                if current and current.get("Name"):
                    tags.append(current)
                in_tag = False
                current = None

            if tag == "LinkList":
                in_link_list = False
                current_link = None
            if tag == "AttributeList":
                in_attribute_list = False

            elem.clear()

    return table_name, tags


def parse_plc_type_xml(path: Path) -> ObjectRef | None:
    kind = None
    name = None
    for event, elem in ET.iterparse(path, events=("start", "end")):
        tag = strip_ns(elem.tag)
        if event == "start" and kind is None and tag.startswith("SW.Types."):
            kind = tag
        if event == "end" and tag == "Name" and name is None:
            text = safe_text(elem)
            if text:
                name = text
        if event == "end":
            elem.clear()
        if kind and name:
            break
    if not kind or not name:
        return None
    return ObjectRef(kind=kind, name=name, number=None, language=None, source_path=path.as_posix())


def scan_edge_cases(text: str) -> set[str]:
    hits: set[str] = set()
    patterns = {
        "ANY": r"\bANY\b",
        "P#_pointer": r"\bP#\b",
        "AR1_AR2": r"\bAR[12]\b",
        "BLKMOV": r"\bBLKMOV\b",
        "PEEK": r"\bPEEK\b",
        "POKE": r"\bPOKE\b",
        "AT_view": r"\bAT\b",
        "Variant": r"\bVARIANT\b",
    }
    for label, pat in patterns.items():
        if re.search(pat, text, flags=re.IGNORECASE):
            hits.add(label)
    return hits


_ABS_DB_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("DB_space", re.compile(r"\bDB\s*([0-9]{1,5})\b", re.IGNORECASE)),
)


def scan_absolute_db_refs(
    *,
    text: str,
    source_path: str,
    db_counts: Counter[int],
    db_samples: DefaultDict[int, list[str]],
    max_samples_per_db: int = 12,
    max_snippet_len: int = 220,
) -> None:
    """
    Best-effort scan for absolute DB addressing hints (e.g., DB1066, DB 1066, P#DB1066...).

    This is NOT a formal cross-reference; it is a conservative risk signal used to
    downgrade confidence on "unused" DB candidates when absolute addressing exists.
    """
    if not text:
        return
    for line_no, line in enumerate(text.splitlines(), start=1):
        for _, pat in _ABS_DB_PATTERNS:
            for m in pat.finditer(line):
                try:
                    db_no = int(m.group(1))
                except Exception:
                    continue
                db_counts[db_no] += 1
                if len(db_samples[db_no]) < max_samples_per_db:
                    snippet = line.strip()
                    if len(snippet) > max_snippet_len:
                        snippet = snippet[:max_snippet_len] + "…"
                    db_samples[db_no].append(f"{source_path}:{line_no}: {snippet}")


def main() -> int:
    parser = argparse.ArgumentParser(description="TIA Portal V18 Openness XML deep reader (evidence-first).")
    parser.add_argument("--export-root", default="EXPORT", help="Path to export folder (default: EXPORT)")
    parser.add_argument("--out", default="deep_reader/out", help="Output folder (default: deep_reader/out)")
    args = parser.parse_args()

    export_root = Path(args.export_root)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Inputs
    program_blocks_root = export_root / "Program blocks"
    plc_types_root = export_root / "PLC data types"
    plc_tags_root = export_root / "PLC tags"
    hmi_tags_root = export_root / "HMI tags"
    aml_paths = list(export_root.rglob("*.aml")) if export_root.exists() else []

    objects: list[ObjectRef] = []
    call_edges: Counter[tuple[str, str]] = Counter()
    inbound_calls: DefaultDict[str, set[str]] = defaultdict(set)
    symbol_uses: dict[str, SymbolUse] = {}
    object_decls: DefaultDict[str, list[ObjectRef]] = defaultdict(list)

    # PLC data types (UDTs)
    if plc_types_root.exists():
        for p in iter_xml_paths(plc_types_root):
            ref = parse_plc_type_xml(p)
            if ref:
                objects.append(ref)
                object_decls[ref.name].append(ref)

    # PLC tags (I/O, constants, etc.)
    plc_tag_rows: list[dict[str, str]] = []
    if plc_tags_root.exists():
        for p in iter_xml_paths(plc_tags_root):
            table, tags = parse_plc_tags_xml(p)
            for t in tags:
                row = {"Table": table or "", "SourcePath": p.as_posix(), **t}
                plc_tag_rows.append(row)
                name = t.get("Name")
                if name:
                    object_decls[name].append(ObjectRef(kind="SW.Tags.PlcTag", name=name, number=None, language=None, source_path=p.as_posix()))

    # HMI tags
    hmi_rows: list[dict[str, str]] = []
    controller_tag_to_hmi: DefaultDict[str, set[str]] = defaultdict(set)
    if hmi_tags_root.exists():
        for p in iter_xml_paths(hmi_tags_root):
            table, tags = parse_hmi_tags_xml(p)
            for t in tags:
                row = {"Table": table or "", "SourcePath": p.as_posix(), **t}
                hmi_rows.append(row)
                ctl = t.get("ControllerTag")
                if ctl and t.get("Name"):
                    controller_tag_to_hmi[ctl].add(t["Name"])

    # Program blocks: blocks, calls, symbol usage
    edge_case_hits: DefaultDict[str, set[str]] = defaultdict(set)
    absolute_db_counts: Counter[int] = Counter()
    absolute_db_samples: DefaultDict[int, list[str]] = defaultdict(list)
    if program_blocks_root.exists():
        for p in iter_xml_paths(program_blocks_root):
            info = parse_program_block_xml(p)
            kind = info.get("kind")
            name = info.get("name")
            if kind and name:
                ref = ObjectRef(
                    kind=f"SW.Blocks.{kind}",
                    name=name,
                    number=info.get("number"),
                    language=info.get("language"),
                    source_path=p.as_posix(),
                )
                objects.append(ref)
                object_decls[name].append(ref)

                # Best-effort edge-case scan (indirect addressing)
                try:
                    txt = p.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    txt = ""
                hits = scan_edge_cases(txt)
                if hits:
                    edge_case_hits[name].update(hits)

                # Best-effort: absolute DB addressing hints (skip DB exports themselves)
                if kind and kind not in {"GlobalDB", "InstanceDB"}:
                    scan_absolute_db_refs(
                        text=txt,
                        source_path=p.as_posix(),
                        db_counts=absolute_db_counts,
                        db_samples=absolute_db_samples,
                    )

                for callee, callee_type in info.get("calls", []):
                    call_edges[(name, callee)] += 1
                    inbound_calls[callee].add(name)

                for sym, rw, evidence in info.get("uses", []):
                    root = sym.split(".", 1)[0] if "." in sym else sym
                    su = symbol_uses.get(sym)
                    if su is None:
                        su = SymbolUse(symbol=sym, root=root)
                        symbol_uses[sym] = su
                    su.add(block=name, rw=rw, evidence=evidence)
                    if sym in controller_tag_to_hmi:
                        su.hmi_tags.update(controller_tag_to_hmi[sym])

    # Post-process: attach HMI tag bindings to symbols even if no PLC code use
    for ctl, tag_names in controller_tag_to_hmi.items():
        su = symbol_uses.get(ctl)
        if su is None:
            root = ctl.split(".", 1)[0] if "." in ctl else ctl
            su = SymbolUse(symbol=ctl, root=root)
            symbol_uses[ctl] = su
        su.hmi_tags.update(tag_names)

    # Write raw inventories
    objects_sorted = sorted(objects, key=lambda o: (o.kind, o.name))
    with (out_dir / "objects.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["kind", "name", "number", "language", "source_path"])
        w.writeheader()
        for o in objects_sorted:
            w.writerow(dataclasses.asdict(o))

    with (out_dir / "call_edges.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["caller", "callee", "count"])
        w.writeheader()
        for (caller, callee), count in call_edges.most_common():
            w.writerow({"caller": caller, "callee": callee, "count": count})

    with (out_dir / "plc_tags.csv").open("w", newline="", encoding="utf-8") as f:
        fieldnames = sorted({k for row in plc_tag_rows for k in row.keys()}) or ["Table", "Name"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in plc_tag_rows:
            w.writerow(row)

    with (out_dir / "hmi_tags.csv").open("w", newline="", encoding="utf-8") as f:
        fieldnames = sorted({k for row in hmi_rows for k in row.keys()}) or ["Table", "Name"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in hmi_rows:
            w.writerow(row)

    # Symbol usage register
    with (out_dir / "symbol_usage.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "symbol",
                "root",
                "read_count",
                "write_count",
                "unknown_count",
                "blocks_count",
                "blocks",
                "hmi_tags_count",
                "hmi_tags",
                "declared_in",
                "evidence_sample",
            ],
        )
        w.writeheader()
        for sym, su in sorted(symbol_uses.items(), key=lambda kv: (-len(kv[1].blocks), kv[0])):
            decls = object_decls.get(su.root, [])
            declared_in = ";".join(sorted({d.source_path for d in decls})) if decls else ""
            w.writerow(
                {
                    "symbol": su.symbol,
                    "root": su.root,
                    "read_count": su.read,
                    "write_count": su.write,
                    "unknown_count": su.unknown,
                    "blocks_count": len(su.blocks),
                    "blocks": ";".join(sorted(su.blocks)),
                    "hmi_tags_count": len(su.hmi_tags),
                    "hmi_tags": ";".join(sorted(su.hmi_tags)),
                    "declared_in": declared_in,
                    "evidence_sample": " | ".join(su.evidence),
                }
            )

    # Duplicated HMI bindings (same ControllerTag referenced by >1 HMI tag)
    duplicates = {ctl: sorted(tags) for ctl, tags in controller_tag_to_hmi.items() if len(tags) > 1}
    (out_dir / "hmi_controller_tag_duplicates.json").write_text(
        json.dumps(duplicates, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Hardware (AutomationML) summary, if provided
    aml_summary: dict[str, Any] | None = None
    if aml_paths:
        # Prefer the largest AML (typically the project export)
        aml_path = sorted(aml_paths, key=lambda p: p.stat().st_size if p.exists() else 0, reverse=True)[0]
        try:
            aml_summary = parse_automationml_hardware(aml_path)
            (out_dir / "hardware_aml_summary.json").write_text(
                json.dumps(aml_summary, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception as e:
            aml_summary = {"source_path": aml_path.as_posix(), "error": str(e)}
            (out_dir / "hardware_aml_summary.json").write_text(
                json.dumps(aml_summary, ensure_ascii=False, indent=2), encoding="utf-8"
            )

    # Edge cases scan
    with (out_dir / "edge_case_scan.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["block", "hits"])
        w.writeheader()
        for block, hits in sorted(edge_case_hits.items(), key=lambda kv: (kv[0])):
            w.writerow({"block": block, "hits": ";".join(sorted(hits))})

    # Absolute DB addressing hints (best-effort string scan)
    with (out_dir / "absolute_db_refs.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["db_number", "hit_count", "samples"])
        w.writeheader()
        for db_no, cnt in sorted(absolute_db_counts.items(), key=lambda kv: (-kv[1], kv[0])):
            w.writerow(
                {
                    "db_number": db_no,
                    "hit_count": int(cnt),
                    "samples": " | ".join(absolute_db_samples.get(db_no, [])),
                }
            )

    summary = {
        "export_root": export_root.as_posix(),
        "counts": {
            "objects": len(objects_sorted),
            "program_blocks_files": len(list(iter_xml_paths(program_blocks_root))) if program_blocks_root.exists() else 0,
            "plc_types_files": len(list(iter_xml_paths(plc_types_root))) if plc_types_root.exists() else 0,
            "plc_tags_files": len(list(iter_xml_paths(plc_tags_root))) if plc_tags_root.exists() else 0,
            "hmi_tags_files": len(list(iter_xml_paths(hmi_tags_root))) if hmi_tags_root.exists() else 0,
            "hardware_aml_files": len(aml_paths),
            "symbol_usage_entries": len(symbol_uses),
            "call_edges": sum(call_edges.values()),
            "absolute_db_numbers_referenced_hint": len(absolute_db_counts),
            "absolute_db_total_hits_hint": int(sum(absolute_db_counts.values())),
        },
        "hardware": aml_summary,
        "notes": [
            "Read/write inference is evidence-driven but best-effort: Calls use Parameter Section; Contacts=read, Coils=write; everything else=unknown.",
            "If safety program / hardware config exports are absent, safety classification is limited to naming and HMI/UDT context.",
        ],
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote outputs to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
