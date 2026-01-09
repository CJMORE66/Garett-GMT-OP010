#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict, deque
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate dependency/island report (CZ) from call_edges.csv + objects.csv.")
    ap.add_argument("--out", default="deep_reader/out", help="Input folder from tia_deep_reader.py")
    ap.add_argument("--reports", default="deep_reader/reports", help="Output folder for reports")
    args = ap.parse_args()

    out_dir = Path(args.out)
    reports_dir = Path(args.reports)
    objects = read_csv(out_dir / "objects.csv")
    calls = read_csv(out_dir / "call_edges.csv")

    # Build call graph (caller -> callees)
    g: dict[str, set[str]] = defaultdict(set)
    g_rev: dict[str, set[str]] = defaultdict(set)
    for r in calls:
        caller = (r.get("caller") or "").strip()
        callee = (r.get("callee") or "").strip()
        if not caller or not callee:
            continue
        g[caller].add(callee)
        g_rev[callee].add(caller)

    # Roots: all OBs (commissioning-critical + other OBs)
    ob_names = [r["name"] for r in objects if r.get("kind") == "SW.Blocks.OB" and r.get("name")]
    roots = sorted(set(ob_names))

    # Reachable set from OB roots (best-effort, only from extracted calls)
    reachable: set[str] = set()
    q: deque[str] = deque()
    for root in roots:
        reachable.add(root)
        q.append(root)
    while q:
        n = q.popleft()
        for m in g.get(n, set()):
            if m not in reachable:
                reachable.add(m)
                q.append(m)

    # Identify blocks (FC/FB) not reachable
    blocks = [r for r in objects if r.get("kind") in {"SW.Blocks.FC", "SW.Blocks.FB"}]
    unreachable = [b for b in blocks if b.get("name") and b["name"] not in reachable]

    # Build islands among unreachable blocks using undirected edges within unreachable subgraph
    unreachable_set = {b["name"] for b in unreachable if b.get("name")}
    undirected: dict[str, set[str]] = defaultdict(set)
    for caller in unreachable_set:
        for callee in g.get(caller, set()):
            if callee in unreachable_set:
                undirected[caller].add(callee)
                undirected[callee].add(caller)
        for parent in g_rev.get(caller, set()):
            if parent in unreachable_set:
                undirected[caller].add(parent)
                undirected[parent].add(caller)

    components: list[list[str]] = []
    seen: set[str] = set()
    for n in sorted(unreachable_set):
        if n in seen:
            continue
        comp: list[str] = []
        dq: deque[str] = deque([n])
        seen.add(n)
        while dq:
            x = dq.popleft()
            comp.append(x)
            for y in sorted(undirected.get(x, set())):
                if y not in seen:
                    seen.add(y)
                    dq.append(y)
        components.append(sorted(comp))

    # Render report
    lines: list[str] = []
    lines.append("# Závislosti programu (orientačně) + izolované ostrovy\n")
    lines.append("## FAKTA\n")
    lines.append(f"- Počet OB (kořeny): `{len(roots)}`")
    lines.append(f"- Extrahované hrany volání: `{len(calls)}`")
    lines.append(f"- Bloky dosažitelné z OB (dle extrahovaných volání): `{len(reachable)}`")
    lines.append(f"- FC/FB nedosažitelné z OB (kandidáti na izolované ostrovy): `{len(unreachable)}`\n")
    lines.append("## OMEZENÍ\n")
    lines.append("- Toto je graf pouze z `CallInfo`/FlgNet + částečně ze StructuredText tokenů; STL/GRAPH může obsahovat logiku, která se zde neprojeví.\n")
    lines.append("- Nedosažitelnost v tomto reportu ≠ “mrtvé”; je to pouze kandidát k ověření.\n")
    lines.append("## IZOLOVANÉ OSTROVY (seskupení nedosažitelných FC/FB)\n")
    for i, comp in enumerate(sorted(components, key=lambda c: (-len(c), c[0]))[:25], start=1):
        lines.append(f"### Ostrov {i} (počet bloků: {len(comp)})")
        for name in comp[:60]:
            callers = sorted(g_rev.get(name, set()))
            callers_txt = ", ".join([f"`{c}`" for c in callers[:6]]) + (" …" if len(callers) > 6 else "")
            lines.append(f"- `{name}` | voláno z: {callers_txt if callers_txt else '(nikdo v extrahovaných datech)'}")
        if len(comp) > 60:
            lines.append("- (zkráceno)")
        lines.append("")

    write_text(reports_dir / "06_zavislosti_a_ostrovy.md", "\n".join(lines))
    print(f"Wrote: {reports_dir / '06_zavislosti_a_ostrovy.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
