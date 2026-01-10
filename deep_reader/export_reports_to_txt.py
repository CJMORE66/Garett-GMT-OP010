#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Literal


def decode_best_effort(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1250", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


class _HtmlToTextParser(HTMLParser):
    _SKIP_TAGS = {"script", "style", "noscript"}
    _BLOCK_TAGS = {
        "p",
        "div",
        "section",
        "article",
        "header",
        "footer",
        "main",
        "br",
        "hr",
        "pre",
        "blockquote",
        "ul",
        "ol",
        "li",
        "table",
        "thead",
        "tbody",
        "tr",
        "td",
        "th",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self._skip_depth = 0
        self._parts: list[str] = []
        self._list_item_start = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in {"br", "hr"}:
            self._parts.append("\n")
        elif tag == "li":
            self._parts.append("\n- ")
            self._list_item_start = True
        elif tag in {"tr"}:
            self._parts.append("\n")
        elif tag in {"td", "th"}:
            self._parts.append("\t")
        elif tag in self._BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self._SKIP_TAGS:
            if self._skip_depth:
                self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag in self._BLOCK_TAGS:
            self._parts.append("\n")
        if tag == "li":
            self._list_item_start = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if not data:
            return
        text = unescape(data)
        self._parts.append(text)

    def handle_entityref(self, name: str) -> None:
        if self._skip_depth:
            return
        self._parts.append(unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        if self._skip_depth:
            return
        self._parts.append(unescape(f"&#{name};"))

    def get_text(self) -> str:
        raw = "".join(self._parts)
        raw = raw.replace("\r\n", "\n").replace("\r", "\n")
        # collapse trailing spaces per-line
        raw = "\n".join(line.rstrip() for line in raw.split("\n"))
        # collapse too many blank lines
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip() + "\n"


def html_to_text(html: str) -> str:
    parser = _HtmlToTextParser()
    parser.feed(html)
    parser.close()
    return parser.get_text()


@dataclass(frozen=True)
class ConversionRecord:
    source: str
    output: str | None
    status: Literal["converted", "skipped", "error"]
    method: str
    message: str | None = None


def iter_report_files(source_dir: Path) -> Iterable[Path]:
    yield from sorted(p for p in source_dir.rglob("*") if p.is_file())


def convert_one(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    data = path.read_bytes()

    if suffix in {".md", ".csv", ".txt", ".json", ".xml", ".yml", ".yaml", ".log"}:
        return decode_best_effort(data), f"copy-as-text({suffix})"

    if suffix in {".html", ".htm"}:
        html = decode_best_effort(data)
        return html_to_text(html), "html-to-text(html.parser)"

    if suffix == ".pdf":
        # optional: only if pypdf is available
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"PDF conversion requires 'pypdf' (not installed): {exc}") from exc
        from io import BytesIO

        reader = PdfReader(BytesIO(data))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n\n".join(pages).strip() + "\n", "pdf-to-text(pypdf)"

    raise RuntimeError(f"Unsupported file type: {suffix}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export deep_reader reports to .txt for NotebookLM.")
    parser.add_argument(
        "--source",
        default=str(Path(__file__).resolve().parent / "reports"),
        help="Source reports directory (default: deep_reader/reports).",
    )
    parser.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parent / "notebooklm_txt"),
        help="Output directory for .txt exports (default: deep_reader/notebooklm_txt).",
    )
    args = parser.parse_args()

    source_dir = Path(args.source).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    records: list[ConversionRecord] = []
    combined_parts: list[str] = []
    converted_rel_paths: list[str] = []
    converted_out_paths: list[str] = []

    for src in iter_report_files(source_dir):
        rel = src.relative_to(source_dir)
        dst = (out_dir / rel).with_suffix(".txt")
        dst.parent.mkdir(parents=True, exist_ok=True)

        try:
            text, method = convert_one(src)
            dst.write_text(text, encoding="utf-8", newline="\n")

            records.append(
                ConversionRecord(
                    source=str(src),
                    output=str(dst),
                    status="converted",
                    method=method,
                )
            )
            converted_rel_paths.append(rel.as_posix())
            converted_out_paths.append(dst.name)

            combined_parts.append(f"{'=' * 80}\nFILE: {rel.as_posix()}\nMETHOD: {method}\n{'=' * 80}\n")
            combined_parts.append(text)
            if not text.endswith("\n"):
                combined_parts.append("\n")
        except Exception as exc:
            records.append(
                ConversionRecord(
                    source=str(src),
                    output=None,
                    status="error",
                    method="n/a",
                    message=str(exc),
                )
            )

    combined_path = out_dir / "ALL_REPORTS.txt"
    combined_path.write_text("".join(combined_parts), encoding="utf-8", newline="\n")

    manifest_path = out_dir / "MANIFEST.json"
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_dir": str(source_dir),
        "output_dir": str(out_dir),
        "records": [record.__dict__ for record in records],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

    podklady_path = out_dir / "NOTEBOOKLM_PODKLADY_CZ.txt"
    podklady_path.write_text(
        (
            "NOTEBOOKLM – podklady (CZ)\n"
            "\n"
            "Co nahrát do NotebookLM:\n"
            "- Doporučení: nahraj všechny .txt soubory z tohoto adresáře.\n"
            "- Alternativa: nahraj jen ALL_REPORTS.txt (vše v jednom souboru).\n"
            "\n"
            "Doporučené pořadí čtení (zdrojové názvy reportů):\n"
            + "".join(f"- {p}\n" for p in converted_rel_paths)
            + "\n"
            "Prompt pro AUDIO zprávu (zkopíruj do NotebookLM):\n"
            "1) Vytvoř audio shrnutí v češtině (cca 5–8 minut).\n"
            "2) Struktura: Kontext projektu → Klíčové nálezy → Rizika → Doporučené kroky (prioritizace) → Otevřené otázky.\n"
            "3) Vypiš konkrétní názvy souborů/artefaktů, pokud se v podkladech objevují (např. registry, mapy, reporty).\n"
            "4) Pokud podklady zmiňují safety/PROFIsafe/safety PLC, nevyvozuj závěry o funkční bezpečnosti; uveď jen, co je v textu, a označ body k ověření.\n"
        ),
        encoding="utf-8",
        newline="\n",
    )

    prompt_path = out_dir / "NOTEBOOKLM_PROMPT_AUDIO_CZ.txt"
    prompt_path.write_text(
        (
            "Vytvoř audio zprávu v češtině (cca 5–8 minut), která shrne nahrané podklady.\n"
            "Použij tuto strukturu:\n"
            "1) Kontext (co je to za projekt a jaké jsou cíle)\n"
            "2) Klíčové nálezy (3–7 bodů, konkrétní)\n"
            "3) Rizika a dopady (priorita + proč)\n"
            "4) Doporučené další kroky (krátkodobé vs. střednědobé)\n"
            "5) Otevřené otázky / chybějící informace\n"
            "\n"
            "Požadavky:\n"
            "- Mluv stručně, prakticky, bez marketingu.\n"
            "- Opři se jen o to, co je v podkladech; nic si nevymýšlej.\n"
            "- Pokud se objeví PROFIsafe/safety témata, nevyvozuj závěry o bezpečnosti; jen popiš a označ k ověření.\n"
        ),
        encoding="utf-8",
        newline="\n",
    )

    error_count = sum(1 for record in records if record.status == "error")
    print(f"Converted {len(records) - error_count}/{len(records)} files → {out_dir}")
    if error_count:
        print(f"Errors: {error_count} (see {manifest_path})")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
