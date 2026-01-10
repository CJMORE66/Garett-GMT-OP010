#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def esc(s: Any) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def linkify(path: str) -> str:
    # Use relative links when possible (HTML opened from reports folder)
    return f'<a href="{esc(path)}">{esc(path)}</a>'


def md_to_html_paragraphs(md: str) -> str:
    """
    Minimal, safe-ish markdown rendering:
    - Headers (#, ##, ###) -> h2/h3/h4
    - Bullets (- ) -> ul/li
    - Inline code `x` -> <code>
    - Backtick paths remain as code
    Keeps everything else as escaped text.
    """
    lines = md.splitlines()
    out: list[str] = []
    in_ul = False

    def close_ul() -> None:
        nonlocal in_ul
        if in_ul:
            out.append("</ul>")
            in_ul = False

    def inline(s: str) -> str:
        # Replace inline `code` segments
        parts: list[str] = []
        buf = ""
        in_code = False
        for ch in s:
            if ch == "`":
                if in_code:
                    parts.append(f"<code>{esc(buf)}</code>")
                    buf = ""
                    in_code = False
                else:
                    parts.append(esc(buf))
                    buf = ""
                    in_code = True
            else:
                buf += ch
        if buf:
            parts.append(esc(buf) if not in_code else f"<code>{esc(buf)}</code>")
        return "".join(parts)

    for raw in lines:
        line = raw.rstrip("\n")
        if not line.strip():
            close_ul()
            continue
        if line.startswith("### "):
            close_ul()
            out.append(f"<h4>{inline(line[4:])}</h4>")
            continue
        if line.startswith("## "):
            close_ul()
            out.append(f"<h3>{inline(line[3:])}</h3>")
            continue
        if line.startswith("# "):
            close_ul()
            out.append(f"<h2>{inline(line[2:])}</h2>")
            continue
        if line.lstrip().startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline(line.lstrip()[2:])}</li>")
            continue
        close_ul()
        out.append(f"<p>{inline(line)}</p>")
    close_ul()
    return "\n".join(out)


def render_table(
    *,
    title: str,
    rows: list[dict[str, Any]],
    columns: list[str] | None = None,
    limit: int | None = None,
    table_id: str | None = None,
) -> str:
    if not rows:
        return f"<h4>{esc(title)}</h4><p><em>Žádná data.</em></p>"
    cols = columns or list(rows[0].keys())
    show = rows[:limit] if limit else rows
    tid = table_id or ("tbl_" + str(abs(hash(title)))[:10])
    header = "".join([f"<th>{esc(c)}</th>" for c in cols])
    body_rows: list[str] = []
    for r in show:
        tds = "".join([f"<td>{esc(r.get(c,''))}</td>" for c in cols])
        body_rows.append(f"<tr>{tds}</tr>")
    suffix = ""
    if limit and len(rows) > limit:
        suffix = f"<p class='note'>Zobrazeno {limit} z {len(rows)} řádků.</p>"
    return f"""
    <div class="card">
      <div class="card-h">
        <h4>{esc(title)}</h4>
        <div class="tools">
          <input class="filter" type="search" placeholder="Filtrovat tabulku…" data-table="{esc(tid)}" />
        </div>
      </div>
      <div class="table-wrap">
        <table id="{esc(tid)}">
          <thead><tr>{header}</tr></thead>
          <tbody>
            {''.join(body_rows)}
          </tbody>
        </table>
      </div>
      {suffix}
    </div>
    """


def safe_key(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", s).strip("_") or "x"


def render_tasklist(title: str, items: list[tuple[str, str]]) -> str:
    """
    items: list of (task_key, html_label) where html_label is already escaped/HTML.
    """
    if not items:
        return f"<div class='card'><h4>{esc(title)}</h4><p><em>Žádné položky.</em></p></div>"
    rows = "\n".join(
        [
            f"<label class='task'><input type='checkbox' data-task='{esc(k)}' />"
            f"<span>{label}</span></label>"
            for k, label in items
        ]
    )
    return f"""
    <div class="card">
      <div class="card-h">
        <h4>{esc(title)}</h4>
        <div class="tools"><span class="note">Položek: {len(items)}</span></div>
      </div>
      <div class="tasklist">{rows}</div>
    </div>
    """


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate one nicely formatted HTML report for OP10 Deep Reader outputs (CZ).")
    ap.add_argument("--reports", default="deep_reader/reports", help="Reports directory")
    ap.add_argument("--out", default="deep_reader/reports/OP10_deep_reader_report.html", help="Output HTML path")
    ap.add_argument("--evidence", default="deep_reader/evidence_unused", help="Evidence packs directory")
    ap.add_argument("--out-dir", default="deep_reader/out", help="Analyzer out directory")
    ap.add_argument("--scl-manifest", default="deep_reader/scl_export/manifest.json", help="SCL export manifest.json")
    args = ap.parse_args()

    reports_dir = Path(args.reports)
    evidence_dir = Path(args.evidence)
    out_dir = Path(args.out_dir)
    out_path = Path(args.out)
    scl_manifest_path = Path(args.scl_manifest)
    root_dir = reports_dir.parent.parent

    summary_path = out_dir / "summary.json"
    summary = read_json(summary_path) if summary_path.exists() else {}

    # Optional: ad-hoc safety keyword scan output (legacy artifact in repo root)
    safety_report_path = root_dir / "safety_report.txt"
    safety_report_text = read_text(safety_report_path) if safety_report_path.exists() else ""

    # Load key CSVs (best-effort)
    no_touch_rows = read_csv(reports_dir / "no_touch_register.csv") if (reports_dir / "no_touch_register.csv").exists() else []
    unused_candidates = read_csv(evidence_dir / "souhrn_kandidatu.csv") if (evidence_dir / "souhrn_kandidatu.csv").exists() else []
    monitoring_roots = read_csv(reports_dir / "monitoring_roots_summary.csv") if (reports_dir / "monitoring_roots_summary.csv").exists() else []
    monitoring_dupes = read_csv(reports_dir / "monitoring_duplicates.csv") if (reports_dir / "monitoring_duplicates.csv").exists() else []
    abs_db_refs = read_csv(out_dir / "absolute_db_refs.csv") if (out_dir / "absolute_db_refs.csv").exists() else []
    edge_cases = read_csv(out_dir / "edge_case_scan.csv") if (out_dir / "edge_case_scan.csv").exists() else []
    pilz_devices = read_csv(reports_dir / "pilz_safety_devices.csv") if (reports_dir / "pilz_safety_devices.csv").exists() else []
    pilz_io = read_csv(reports_dir / "pilz_io_map.csv") if (reports_dir / "pilz_io_map.csv").exists() else []

    scl_manifest = read_json(scl_manifest_path) if scl_manifest_path.exists() else {}

    # Load markdown reports (best-effort)
    def md_file(name: str) -> str:
        p = reports_dir / name
        return read_text(p) if p.exists() else f"# {name}\n\n(chybí soubor `{p.as_posix()}`)\n"

    md_index = md_file("00_index.md")
    md_comprehension = md_file("01_project_comprehension_report.md")
    md_unused = md_file("02_unused_elements_analysis.md")
    md_monitoring = md_file("03_monitoring_consolidation_blueprint.md")
    md_migration = md_file("04_migration_roadmap.md")
    md_dep = md_file("06_zavislosti_a_ostrovy.md")
    md_scl_cov = md_file("07_pokryti_prevodu_xml_do_scl.md")
    md_pilz_map = md_file("08_pilz_pnoz_project_map.md")
    md_pilz_spec = md_file("09_pilz_to_siemens_safety_spec.md")

    # Small summary cards
    counts = (summary.get("counts") or {}) if isinstance(summary, dict) else {}
    facts_cards = [
        ("Kořen exportu", esc(summary.get("export_root", "EXPORT"))),
        ("Objekty (celkem)", esc(counts.get("objects", ""))),
        ("Program blocks XML", esc(counts.get("program_blocks_files", ""))),
        ("UDT XML", esc(counts.get("plc_types_files", ""))),
        ("PLC tags XML", esc(counts.get("plc_tags_files", ""))),
        ("HMI tags XML", esc(counts.get("hmi_tags_files", ""))),
        ("Hrany volání", esc(counts.get("call_edges", ""))),
        ("Symbol usage záznamy", esc(counts.get("symbol_usage_entries", ""))),
        ("Edge-case bloky", esc(len(edge_cases))),
        ("Absolutní DB narážky", esc(counts.get("absolute_db_numbers_referenced_hint", ""))),
    ]

    facts_html = "\n".join(
        [f"<div class='kpi'><div class='k'>{k}</div><div class='v'>{v}</div></div>" for k, v in facts_cards]
    )

    # Evidence packs list (from INDEX.md) – keep as link list
    index_md_path = evidence_dir / "INDEX.md"
    evidence_index_html = md_to_html_paragraphs(read_text(index_md_path) if index_md_path.exists() else "")

    # Risk matrix
    risk_csv = reports_dir / "05_risk_assessment_matrix.csv"
    risk_rows = read_csv(risk_csv) if risk_csv.exists() else []

    # Evidence file lookup for unused candidates (for checklist links)
    evidence_files: dict[tuple[str, str], str] = {}
    if evidence_dir.exists():
        for p in sorted(evidence_dir.glob("*.md")):
            stem = p.stem  # e.g., FB_FB_Analog, GlobalDB_GeneralDebug
            if "_" not in stem:
                continue
            prefix, obj = stem.split("_", 1)
            evidence_files[(prefix, obj)] = p.name

    def kind_prefix_from_druh(druh: str) -> str:
        if druh.endswith(".FB"):
            return "FB"
        if druh.endswith(".FC"):
            return "FC"
        if druh.endswith(".GlobalDB"):
            return "GlobalDB"
        return "OBJ"

    def evidence_link_for_candidate(druh: str, obj: str) -> str:
        prefix = kind_prefix_from_druh(druh)
        fname = evidence_files.get((prefix, obj))
        if not fname:
            return "<span class='note'>(evidence md nenalezeno)</span>"
        return linkify(f"../evidence_unused/{fname}")

    # Akční checklist (evidence-first, commissioning-safe)
    preflight_tasks: list[tuple[str, str]] = [
        (
            "gate_notouch",
            "Potvrdit <strong>NEŠAHAT</strong> registr: safety-adjacent signály, alarmy, comms, startup/shutdown, kritické OB.",
        ),
        (
            "gate_edgecases",
            "Projít <strong>edge cases</strong> (ANY/AT/AR/BLKMOV/PEEK/POKE/VARIANT + absolutní DB) a označit vše, kde není možné bezpečně tvrdit “dead”.",
        ),
        ("gate_hmi", "Ověřit HMI vazby: tagy/alarms/trendy pro monitorovací proměnné (zejm. u kandidátů “nevyužité”)."),
        ("gate_xref", "Pokud to půjde: získat cross-reference (export nebo alespoň kopie tabulky do Excelu/PDF) pro zvýšení jistoty."),
    ]

    unused_tasks: list[tuple[str, str]] = []
    for r in unused_candidates:
        obj = (r.get("Objekt") or "").strip()
        druh = (r.get("Druh") or "").strip()
        riziko = (r.get("Riziko") or "").strip()
        jistota = (r.get("Jistota") or "").strip()
        notouch = (r.get("NEŠAHAT") or "").strip()
        decl = (r.get("Deklarace") or "").strip()
        ev = evidence_link_for_candidate(druh, obj)
        badges: list[str] = []
        if notouch.upper() == "ANO" or "NEŠAHAT" in riziko.upper():
            badges.append("<span class='badge danger'>NEŠAHAT</span>")
        if jistota:
            badges.append(f"<span class='badge warn'>Jistota: {esc(jistota)}</span>")
        if riziko:
            badges.append(f"<span class='badge'>{esc(riziko)}</span>")
        label = (
            f"{''.join(badges)}"
            f"<div class='task-sub'>"
            f"<strong>{esc(obj)}</strong> <span class='note'>({esc(druh)})</span><br/>"
            f"<span class='note'>Deklarace:</span> <code>{esc(decl)}</code><br/>"
            f"<span class='note'>Evidence:</span> {ev}<br/>"
            f"<span class='note'>Akce:</span> ověřit v TIA (volání/čtení/zápis), HMI vazby, a nepřímé adresování; <em>nemazat bez HIGH jistoty</em>."
            f"</div>"
        )
        unused_tasks.append((safe_key(f"unused_{druh}_{obj}"), label))

    monitoring_tasks: list[tuple[str, str]] = []
    if monitoring_dupes:
        groups: dict[str, list[dict[str, str]]] = {}
        for r in monitoring_dupes:
            key = (r.get("ControllerTag") or "").strip()
            if not key:
                continue
            groups.setdefault(key, []).append(r)
        for tag, rows in sorted(groups.items(), key=lambda x: (-len(x[1]), x[0])):
            examples = ", ".join([esc(rr.get("TagHMI", "")) for rr in rows[:4] if rr.get("TagHMI")])
            more = "" if len(rows) <= 4 else f" (+{len(rows)-4} dalších)"
            label = (
                f"<strong>{esc(tag)}</strong> <span class='note'>(duplicitní HMI tagy: {len(rows)})</span><br/>"
                f"<span class='note'>Příklady:</span> {examples}{more}<br/>"
                f"<span class='note'>Akce:</span> ověřit, že tagy skutečně čtou stejný zdroj, a připravit staged retarget (nejdřív read-only audit)."
            )
            monitoring_tasks.append((safe_key(f"hmi_dupe_{tag}"), label))

    # Top edges/rows for tables
    safety_report_html = ""
    if safety_report_text.strip():
        safety_report_rel = "../../safety_report.txt"
        safety_report_html = f"""
        <details>
          <summary>Safety token scan (orientační) <span class="meta">zdroj: {linkify(safety_report_rel)}</span></summary>
          <div class="card">
            <p class="note">Toto není “safety program” ani důkaz bezpečnosti; jde jen o textový scan exportů pro vytvoření konzervativního registru <strong>NEŠAHAT</strong>.</p>
            <pre class="pre">{esc(safety_report_text)}</pre>
          </div>
        </details>
        """

    guide_js = """\
    // =============================
    // Průvodce (guided mode)
    // =============================
    const STEP_ORDER = ['tasks','map','notouch','unused','monitoring','scl','pilz','migration','files'];
    const STEP_DESC = {
      tasks: 'Ověřovací úkoly a brány rizika (co dělat jako první).',
      map: 'Rychlá orientace: struktura projektu, OB, volání, “ostrovy”.',
      notouch: 'Konzervativní registr NEŠAHAT + bezpečnostní poznámky.',
      unused: 'Kandidáti “nevyužité” + důkazy; nic nemaž bez HIGH jistoty.',
      monitoring: 'Monitoring konsolidace + duplicitní HMI vazby.',
      scl: 'Převod XML→SCL: pokrytí a upozornění (best-effort).',
      pilz: 'PILZ inventář + migrační specifikace (bez safety kódu).',
      migration: 'Roadmap, testy, riziková matice.',
      files: 'Klikací odkazy na všechny výstupy.'
    };
    const focusKey = 'op10_deep_reader_focus_mode_v1';
    let focusMode = (localStorage.getItem(focusKey) ?? '1') === '1'; // default: průvodce ON

    const btnFocus = document.getElementById('btnFocus');
    const btnPrev = document.getElementById('btnPrev');
    const btnNext = document.getElementById('btnNext');
    const stepsEl = document.getElementById('steps');
    const stepSearch = document.getElementById('stepSearch');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');

    const sections = STEP_ORDER.map((id) => document.getElementById(id)).filter(Boolean);
    const stepButtons = new Map();

    function setFocusMode(on) {
      focusMode = !!on;
      document.body.classList.toggle('focus', focusMode);
      localStorage.setItem(focusKey, focusMode ? '1' : '0');
      if (btnFocus) btnFocus.textContent = focusMode ? 'Zobrazit vše' : 'Režim: Průvodce';
    }

    function closeAllDetailsExcept(sec) {
      if (!focusMode) return;
      document.querySelectorAll('.section details').forEach((d) => (d.open = false));
      if (!sec) return;
      const first = sec.querySelector('details');
      if (first) first.open = true;
    }

    function updateProgress(activeIndex) {
      const n = sections.length || 1;
      const i = Math.max(0, Math.min(activeIndex, n - 1));
      const pct = Math.round(((i + 1) / n) * 100);
      if (progressBar) progressBar.style.width = pct + '%';
      if (progressText) progressText.textContent = `Krok ${i + 1} / ${n}`;
    }

    function setActive(stepId, opts = {}) {
      const { scroll = true, updateHash = true } = opts;
      const sec = document.getElementById(stepId);
      if (!sec) return;
      sections.forEach((s) => s.classList.remove('active'));
      sec.classList.add('active');
      stepButtons.forEach((btn) => btn.classList.remove('active'));
      const b = stepButtons.get(stepId);
      if (b) b.classList.add('active');

      const idx = sections.findIndex((s) => s.id === stepId);
      updateProgress(idx >= 0 ? idx : 0);
      closeAllDetailsExcept(sec);

      if (updateHash) history.replaceState(null, '', '#' + stepId);
      if (scroll) sec.scrollIntoView({ behavior: 'smooth', block: 'start' });

      if (btnPrev) btnPrev.disabled = idx <= 0;
      if (btnNext) btnNext.disabled = idx < 0 || idx >= sections.length - 1;
    }

    function currentStepId() {
      const h = (location.hash || '').replace('#', '');
      if (h && document.getElementById(h)) return h;
      return sections[0]?.id || 'tasks';
    }

    function go(delta) {
      const cur = currentStepId();
      const idx = sections.findIndex((s) => s.id === cur);
      const nextIdx = Math.max(0, Math.min(idx + delta, sections.length - 1));
      const id = sections[nextIdx]?.id;
      if (id) setActive(id);
    }

    // Build step list UI
    if (stepsEl) {
      stepsEl.innerHTML = '';
      sections.forEach((sec) => {
        const id = sec.id;
        const title = (sec.querySelector('h2')?.textContent || id).trim();
        const desc = STEP_DESC[id] || '';
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'step-btn';
        btn.setAttribute('data-step', id);
        btn.innerHTML = `<div class="t">${title}</div><div class="d">${desc}</div>`;
        btn.addEventListener('click', () => setActive(id));
        stepsEl.appendChild(btn);
        stepButtons.set(id, btn);
      });
    }

    if (btnFocus) btnFocus.addEventListener('click', () => setFocusMode(!focusMode));
    if (btnPrev) btnPrev.addEventListener('click', () => go(-1));
    if (btnNext) btnNext.addEventListener('click', () => go(+1));
    window.addEventListener('hashchange', () => setActive(currentStepId(), { scroll: true, updateHash: false }));

    if (stepSearch) {
      stepSearch.addEventListener('input', () => {
        const q = (stepSearch.value || '').toString().toLowerCase();
        stepButtons.forEach((btn) => {
          const text = (btn.textContent || '').toLowerCase();
          btn.style.display = q === '' || text.includes(q) ? '' : 'none';
        });
      });
    }

    // Init guided mode + active section
    setFocusMode(focusMode);
    setActive(currentStepId(), { scroll: false, updateHash: false });
    """

    html_doc = f"""<!doctype html>
<html lang="cs">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OP10 – TIA Deep Reader Report</title>
  <style>
    :root {{
      --bg: #0b1220;
      --card: rgba(255,255,255,.06);
      --card2: rgba(255,255,255,.08);
      --text: rgba(255,255,255,.92);
      --muted: rgba(255,255,255,.70);
      --border: rgba(255,255,255,.12);
      --accent: #6ee7ff;
      --accent2: #a78bfa;
      --danger: #fb7185;
      --ok: #34d399;
      --warn: #fbbf24;
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      --sans: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: var(--sans);
      color: var(--text);
      background:
        radial-gradient(1200px 700px at 15% 15%, rgba(110,231,255,.15), transparent 60%),
        radial-gradient(900px 600px at 85% 25%, rgba(167,139,250,.16), transparent 60%),
        linear-gradient(180deg, #070b14 0%, var(--bg) 100%);
    }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    code {{ font-family: var(--mono); font-size: .95em; padding: .08em .35em; background: rgba(255,255,255,.08); border: 1px solid var(--border); border-radius: .4em; }}
    .wrap {{ max-width: 1150px; margin: 0 auto; padding: 28px 18px 70px; }}
    .layout {{
      display: grid;
      grid-template-columns: 310px minmax(0, 1fr);
      gap: 14px;
      align-items: start;
    }}
    .side {{
      position: sticky;
      top: 14px;
      align-self: start;
    }}
    .side-card {{
      border: 1px solid var(--border);
      background: rgba(255,255,255,.04);
      border-radius: 18px;
      padding: 12px;
    }}
    .side-title {{ font-weight: 760; font-size: 14px; margin: 4px 0 10px; }}
    .side-tools {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }}
    .side-tools .btn {{ padding: 7px 10px; }}
    .side-search {{
      width: 100%;
      margin-top: 10px;
      padding: 8px 10px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: rgba(0,0,0,.25);
      color: var(--text);
      outline: none;
    }}
    .side-search:focus {{ border-color: rgba(110,231,255,.55); }}
    .progress {{
      margin-top: 10px;
      height: 8px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: rgba(0,0,0,.18);
      overflow: hidden;
    }}
    .progress > div {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, rgba(110,231,255,.9), rgba(167,139,250,.85));
    }}
    .steps {{ margin-top: 10px; display: grid; gap: 8px; }}
    .step-btn {{
      text-align: left;
      display: grid;
      gap: 2px;
      padding: 10px 10px;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: rgba(0,0,0,.16);
      color: var(--text);
      cursor: pointer;
    }}
    .step-btn:hover {{ border-color: rgba(110,231,255,.45); }}
    .step-btn.active {{
      border-color: rgba(110,231,255,.65);
      box-shadow: 0 0 0 2px rgba(110,231,255,.15);
    }}
    .step-btn .t {{ font-weight: 700; font-size: 13px; }}
    .step-btn .d {{ color: var(--muted); font-size: 12px; line-height: 1.25; }}
    .content {{
      min-width: 0;
    }}
    body.focus .content .section {{ display: none; }}
    body.focus .content .section.active {{ display: block; }}
    .section.active > h2 {{ scroll-margin-top: 14px; }}
    .hero {{
      padding: 18px 18px 16px;
      border: 1px solid var(--border);
      background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.04));
      border-radius: 18px;
    }}
    h1 {{ margin: 0 0 6px; font-size: 26px; letter-spacing: .2px; }}
    .sub {{ color: var(--muted); font-size: 13.5px; line-height: 1.4; }}
    .pill {{
      display: inline-flex; gap: 8px; align-items: center;
      border: 1px solid var(--border);
      background: rgba(255,255,255,.06);
      border-radius: 999px;
      padding: 6px 10px;
      margin-top: 10px;
      color: var(--muted);
      font-size: 12px;
    }}
    .grid {{
      margin-top: 14px;
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
    }}
    .kpi {{
      border: 1px solid var(--border);
      background: rgba(255,255,255,.05);
      border-radius: 14px;
      padding: 10px 10px 9px;
      min-height: 58px;
    }}
    .kpi .k {{ color: var(--muted); font-size: 12px; }}
    .kpi .v {{ font-family: var(--mono); font-size: 16px; margin-top: 6px; }}
    .nav {{
      margin-top: 14px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .nav a {{
      display: inline-flex; align-items: center; gap: 8px;
      padding: 7px 10px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,.05);
      border-radius: 10px;
      color: var(--text);
      font-size: 12.5px;
    }}
    .nav a:hover {{ border-color: rgba(110,231,255,.45); }}
    .section {{ margin-top: 18px; }}
    .section h2 {{ margin: 0 0 10px; font-size: 18px; }}
    details {{
      border: 1px solid var(--border);
      background: rgba(255,255,255,.04);
      border-radius: 14px;
      padding: 12px 12px;
      margin-top: 10px;
    }}
    details > summary {{
      cursor: pointer;
      list-style: none;
      font-weight: 650;
      display: flex;
      justify-content: space-between;
      gap: 10px;
    }}
    details > summary::-webkit-details-marker {{ display: none; }}
    .meta {{ color: var(--muted); font-size: 12px; font-weight: 500; }}
    .card {{
      border: 1px solid var(--border);
      background: rgba(255,255,255,.045);
      border-radius: 14px;
      padding: 12px;
      margin-top: 10px;
    }}
    .card-h {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
    }}
    .card h4 {{ margin: 0; font-size: 14px; }}
    .tools {{ display: flex; gap: 8px; align-items: center; }}
    .filter {{
      width: 260px;
      max-width: 52vw;
      padding: 8px 10px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: rgba(0,0,0,.25);
      color: var(--text);
      outline: none;
    }}
    .filter:focus {{ border-color: rgba(110,231,255,.55); }}
    .table-wrap {{
      overflow: auto;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: rgba(0,0,0,.18);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 640px;
    }}
    thead th {{
      position: sticky;
      top: 0;
      background: rgba(15,23,42,.92);
      color: rgba(255,255,255,.86);
      border-bottom: 1px solid var(--border);
      font-size: 12px;
      text-align: left;
      padding: 9px 10px;
      white-space: nowrap;
    }}
    tbody td {{
      border-top: 1px solid rgba(255,255,255,.08);
      font-size: 12.5px;
      padding: 8px 10px;
      vertical-align: top;
      white-space: nowrap;
    }}
    tbody tr:hover td {{ background: rgba(255,255,255,.04); }}
    .note {{ color: var(--muted); font-size: 12px; margin: 8px 2px 0; }}
    .badge {{
      display: inline-flex; align-items: center;
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 12px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,.05);
      color: var(--muted);
    }}
    .btn {{
      display: inline-flex; align-items: center; gap: 8px;
      padding: 8px 10px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,.06);
      color: var(--text);
      border-radius: 10px;
      cursor: pointer;
      font-size: 12.5px;
    }}
    .btn:hover {{ border-color: rgba(110,231,255,.45); }}
    .tasklist {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 8px;
    }}
    .task {{
      display: flex;
      gap: 10px;
      align-items: flex-start;
      padding: 10px 10px;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: rgba(0,0,0,.14);
    }}
    .task input[type="checkbox"] {{
      margin-top: 2px;
      width: 16px;
      height: 16px;
      accent-color: var(--accent);
      flex: 0 0 auto;
    }}
    .task-sub {{
      margin-top: 6px;
      color: var(--text);
      line-height: 1.35;
      font-size: 12.5px;
    }}
    .danger {{ border-color: rgba(251,113,133,.35); color: rgba(251,113,133,.95); }}
    .warn {{ border-color: rgba(251,191,36,.35); color: rgba(251,191,36,.95); }}
    .ok {{ border-color: rgba(52,211,153,.35); color: rgba(52,211,153,.95); }}
    .footer {{
      margin-top: 16px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }}
    pre.pre {{
      margin: 0;
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,.03);
      color: rgba(255,255,255,.86);
      white-space: pre-wrap;
      word-break: break-word;
      max-height: 520px;
      overflow: auto;
      font-size: 12px;
      line-height: 1.35;
    }}
    @media (max-width: 980px) {{
      .layout {{ grid-template-columns: 1fr; }}
      .side {{ position: relative; top: 0; }}
      .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      table {{ min-width: 520px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="layout">
      <aside class="side" aria-label="Průvodce" id="guide">
        <div class="side-card">
          <div class="side-title">Průvodce výsledky</div>
          <div class="side-tools">
            <button class="btn" type="button" id="btnFocus">Režim: Průvodce</button>
            <button class="btn" type="button" id="btnPrev">← Zpět</button>
            <button class="btn" type="button" id="btnNext">Další →</button>
          </div>
          <input class="side-search" id="stepSearch" type="search" placeholder="Hledat sekci…" />
          <div class="progress" aria-hidden="true"><div id="progressBar"></div></div>
          <div class="note" id="progressText" style="margin-top:8px;"></div>
          <div class="steps" id="steps"></div>
          <div class="note" style="margin-top:10px;">
            Tip: v režimu Průvodce se zobrazuje vždy jen 1 sekce. Přepni na “Zobrazit vše”, když chceš skenovat celý dokument.
          </div>
        </div>
      </aside>

      <div class="content">
        <div class="hero">
      <h1>OP10 – TIA Portal V18 Deep Reader (komplexní report)</h1>
      <div class="sub">
        Evidence-first audit z exportů TIA + HMI + hardware (AutomationML) + doplněná část PILZ PNOZmulti (inventář + specifikace migrace).
        Tento dokument je určen pro offline revizi; neprovádí žádné zásahy do PLC projektu.
      </div>
      <div class="pill">
        <span class="badge ok">Bez zásahu do PLC</span>
        <span class="badge warn">Bez cross-reference = omezená jistota</span>
        <span class="badge danger">Safety část: pouze mapování/specifikace</span>
        <span class="meta">Generováno: {esc(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}</span>
      </div>
      <div class="grid">{facts_html}</div>
      <div class="nav">
        <a href="#tasks">Úkoly</a>
        <a href="#map">Projektová mapa</a>
        <a href="#notouch">NEŠAHAT</a>
        <a href="#unused">Kandidáti nevyužité</a>
        <a href="#monitoring">Monitoring DB</a>
        <a href="#scl">Převod do SCL</a>
        <a href="#pilz">PILZ PNOZ</a>
        <a href="#migration">Migrace &amp; rizika</a>
        <a href="#files">Soubory</a>
      </div>
        </div>

    <div class="section" id="tasks">
      <h2>Akční checklist (k odškrtání)</h2>
      <div class="card">
        <p class="note">
          Tento seznam je určen pro bezpečné ověřování (commissioning-safe). Neimplikuje mazání ani zásahy do kritických částí.
          Stav se ukládá lokálně v prohlížeči (LocalStorage).
        </p>
        <button class="btn" type="button" data-reset-tasks="1">Reset všech checkboxů</button>
      </div>
      {render_tasklist("Brány rizika (gates) – udělej před jakýmkoli refaktorem", preflight_tasks)}
      <details open>
        <summary>Kandidáti “nevyužité” – ověřovací úkoly <span class="meta">z <code>souhrn_kandidatu.csv</code></span></summary>
        {render_tasklist("Ověřit kandidáty (bez mazání)", unused_tasks)}
      </details>
      <details>
        <summary>Monitoring – duplicitní HMI tagy (ověřit redundanci) <span class="meta">z <code>monitoring_duplicates.csv</code></span></summary>
        {render_tasklist("Ověřit duplikáty (read-only audit)", monitoring_tasks)}
      </details>
    </div>

    <div class="section" id="files">
      <h2>Rychlé odkazy na výstupy</h2>
      <div class="card">
        <ul>
          <li>{linkify("00_index.md")}</li>
          <li>{linkify("01_project_comprehension_report.md")}</li>
          <li>{linkify("02_unused_elements_analysis.md")}</li>
          <li>{linkify("03_monitoring_consolidation_blueprint.md")}</li>
          <li>{linkify("04_migration_roadmap.md")}</li>
          <li>{linkify("05_risk_assessment_matrix.csv")}</li>
          <li>{linkify("06_zavislosti_a_ostrovy.md")}</li>
          <li>{linkify("07_pokryti_prevodu_xml_do_scl.md")}</li>
          <li>{linkify("08_pilz_pnoz_project_map.md")}</li>
          <li>{linkify("09_pilz_to_siemens_safety_spec.md")}</li>
        </ul>
        <p class="note">Pozn.: HTML je uložen do stejné složky, takže odkazy míří na soubory v <code>deep_reader/reports</code>.</p>
      </div>
    </div>

    <div class="section" id="map">
      <h2>Projektová mapa</h2>
      <details open>
        <summary>Index &amp; FINAL GATE <span class="meta">z <code>00_index.md</code></span></summary>
        <div class="card">{md_to_html_paragraphs(md_index)}</div>
      </details>
      <details>
        <summary>Porozumění projektu (mapa, OB, call tree, HMI) <span class="meta">z <code>01_project_comprehension_report.md</code></span></summary>
        <div class="card">{md_to_html_paragraphs(md_comprehension)}</div>
      </details>
      <details>
        <summary>Závislosti a “ostrovy” <span class="meta">z <code>06_zavislosti_a_ostrovy.md</code></span></summary>
        <div class="card">{md_to_html_paragraphs(md_dep)}</div>
      </details>
    </div>

    <div class="section" id="notouch">
      <h2>Registr NEŠAHAT</h2>
      {render_table(title="NEŠAHAT register (výběr)", rows=no_touch_rows, limit=250, table_id="tbl_notouch")}
      <p class="note">Registr je konzervativní: zahrnuje kritické OB a vše se safety-adjacent/externím rozhraním podle názvu/cesty.</p>
      {safety_report_html}
    </div>

    <div class="section" id="unused">
      <h2>Kandidáti na “nevyužité” (jen k ověření)</h2>
      <details open>
        <summary>Souhrn (report) <span class="meta">z <code>02_unused_elements_analysis.md</code></span></summary>
        <div class="card">{md_to_html_paragraphs(md_unused)}</div>
      </details>
      {render_table(
        title="Souhrn kandidátů (evidence packs)",
        rows=unused_candidates,
        limit=400,
        table_id="tbl_unused_summary",
      )}
      <details>
        <summary>Důkazní balíčky – index <span class="meta">z <code>../evidence_unused/INDEX.md</code></span></summary>
        <div class="card">
          <p class="note">Tyto odkazy jsou relativní k <code>deep_reader/evidence_unused</code>. Pokud otevřeš HTML mimo reports složku, odkazy uprav.</p>
          {evidence_index_html}
        </div>
      </details>
      {render_table(
        title="Absolutní adresování DB (narážky)",
        rows=abs_db_refs,
        limit=200,
        table_id="tbl_absdb",
      )}
      {render_table(
        title="Indikátory nepřímého adresování (edge cases)",
        rows=edge_cases,
        limit=250,
        table_id="tbl_edge",
      )}
    </div>

    <div class="section" id="monitoring">
      <h2>Monitoring konsolidace (DB blueprint)</h2>
      <details open>
        <summary>Návrh konsolidace monitoringu <span class="meta">z <code>03_monitoring_consolidation_blueprint.md</code></span></summary>
        <div class="card">{md_to_html_paragraphs(md_monitoring)}</div>
      </details>
      {render_table(title="Top PLC kořeny z HMI (souhrn)", rows=monitoring_roots, limit=120, table_id="tbl_mon_roots")}
      {render_table(title="Duplicitní HMI vazby (vzorek)", rows=monitoring_dupes, limit=200, table_id="tbl_mon_dupes")}
      <div class="footer">
        Implementační SCL návrhy (additivní, bez zásahu do stávajících tagů) jsou v <code>deep_reader/proposed_scl/</code>.
      </div>
    </div>

    <div class="section" id="scl">
      <h2>Převod do SCL (offline pro revizi)</h2>
      <details open>
        <summary>Pokrytí převodu (všechny bloky) <span class="meta">z <code>07_pokryti_prevodu_xml_do_scl.md</code></span></summary>
        <div class="card">{md_to_html_paragraphs(md_scl_cov)}</div>
      </details>
      <div class="card">
        <p class="note">SCL exporty: <code>deep_reader/scl_export/</code>. GRAPH převody: <code>deep_reader/scl_export/graph_generated/</code>.</p>
        <p class="note">Manifest: <code>{esc(scl_manifest_path.as_posix())}</code> (obsahuje počty rekonstruovaných ST/FlgNet/StatementList sítí na blok).</p>
      </div>
    </div>

    <div class="section" id="pilz">
      <h2>PILZ PNOZmulti (safety relay) – inventář &amp; migrační specifikace</h2>
      <details open>
        <summary>Mapování Pilz projektu <span class="meta">z <code>08_pilz_pnoz_project_map.md</code></span></summary>
        <div class="card">{md_to_html_paragraphs(md_pilz_map)}</div>
      </details>
      {render_table(title="PILZ safety devices (výběr)", rows=pilz_devices, limit=120, table_id="tbl_pilz_dev")}
      {render_table(title="PILZ I/O mapa (výběr)", rows=pilz_io, limit=200, table_id="tbl_pilz_io")}
      <details>
        <summary>Specifikace migrace Pilz → Siemens (bez kódu) <span class="meta">z <code>09_pilz_to_siemens_safety_spec.md</code></span></summary>
        <div class="card">{md_to_html_paragraphs(md_pilz_spec)}</div>
      </details>
      <div class="footer">
        <strong>Bezpečnostní poznámka:</strong> Tento dokument úmyslně neobsahuje “hotový safety kód”.
        Migrace na F‑CPU vyžaduje safety dokumentaci, validaci a formální SAT/commissioning postup.
      </div>
    </div>

    <div class="section" id="migration">
      <h2>Migrační roadmap + rizika</h2>
      <details open>
        <summary>Roadmap <span class="meta">z <code>04_migration_roadmap.md</code></span></summary>
        <div class="card">{md_to_html_paragraphs(md_migration)}</div>
      </details>
      {render_table(title="Risk assessment matrix", rows=risk_rows, limit=80, table_id="tbl_risk")}
    </div>

    <div class="footer">
      <p>
        Všechny závěry “nevyužité” jsou evidence-first a bez cross-reference exportu mají omezenou jistotu.
        Pokud dodáš cross-reference export z TIA, reporty se dají zpřesnit a přepočítat.
      </p>
    </div>
      </div>
    </div>
  </div>

  <script>
{guide_js}

    // Simple table filter per input[data-table]
    function normalize(s) {{
      return (s || '').toString().toLowerCase();
    }}
    document.querySelectorAll('input.filter').forEach((inp) => {{
      const tableId = inp.getAttribute('data-table');
      const tbl = document.getElementById(tableId);
      if (!tbl) return;
      const tbody = tbl.querySelector('tbody');
      if (!tbody) return;
      const rows = Array.from(tbody.querySelectorAll('tr'));
      inp.addEventListener('input', () => {{
        const q = normalize(inp.value);
        rows.forEach((tr) => {{
          const txt = normalize(tr.textContent);
          tr.style.display = (q === '' || txt.includes(q)) ? '' : 'none';
        }});
      }});
    }});

    // Checklist persistence (localStorage)
    const TASK_PREFIX = 'op10_deep_reader_task__';
    function taskKey(el) {{
      return TASK_PREFIX + (el.getAttribute('data-task') || '');
    }}
    document.querySelectorAll('input[type="checkbox"][data-task]').forEach((cb) => {{
      const k = taskKey(cb);
      const v = localStorage.getItem(k);
      if (v === '1') cb.checked = true;
      cb.addEventListener('change', () => {{
        localStorage.setItem(k, cb.checked ? '1' : '0');
      }});
    }});
    document.querySelectorAll('button[data-reset-tasks]').forEach((btn) => {{
      btn.addEventListener('click', () => {{
        if (!confirm('Opravdu resetovat všechny checkboxy v tomto reportu?')) return;
        Object.keys(localStorage).forEach((k) => {{
          if (k.startsWith(TASK_PREFIX)) localStorage.removeItem(k);
        }});
        document.querySelectorAll('input[type="checkbox"][data-task]').forEach((cb) => (cb.checked = false));
      }});
    }});
  </script>
</body>
</html>
"""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_doc, encoding="utf-8")
    print(f"Wrote: {out_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
