#!/usr/bin/env python3
"""Convert all markdown files under evi-prep/markdown to PDF in evi-prep/pdf."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
MD_DIR = ROOT / "markdown"
PDF_DIR = ROOT / "pdf"
FONT_DIR = Path(__file__).resolve().parent / "fonts"

FONT_REGULAR = FONT_DIR / "DejaVuSans.ttf"
FONT_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"

PAGE_WIDTH = 210
MARGIN = 15
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN


class MarkdownPdf(FPDF):
    def __init__(self) -> None:
        super().__init__()
        self.add_font("DejaVu", "", str(FONT_REGULAR))
        self.add_font("DejaVu", "B", str(FONT_BOLD))
        self.set_auto_page_break(auto=True, margin=15)

    def header(self) -> None:
        pass

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"{self.page_no()}", align="C")


def strip_md_inline(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.strip()


def md_to_pdf(md_path: Path, pdf_path: Path) -> None:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    pdf = MarkdownPdf()
    pdf.add_page()
    pdf.set_left_margin(MARGIN)
    pdf.set_right_margin(MARGIN)

    in_code = False
    code_lines: list[str] = []
    in_table = False
    table_rows: list[list[str]] = []

    def flush_code() -> None:
        nonlocal code_lines
        if not code_lines:
            return
        pdf.set_font("DejaVu", "", 8)
        pdf.set_fill_color(245, 245, 245)
        block = "\n".join(code_lines)
        pdf.multi_cell(CONTENT_WIDTH, 4.5, block, fill=True)
        pdf.ln(2)
        code_lines = []

    def flush_table() -> None:
        nonlocal table_rows, in_table
        if not table_rows:
            in_table = False
            return
        col_count = max(len(r) for r in table_rows)
        col_width = CONTENT_WIDTH / col_count
        pdf.set_font("DejaVu", "", 8)
        for i, row in enumerate(table_rows):
            if i == 0:
                pdf.set_font("DejaVu", "B", 8)
            else:
                pdf.set_font("DejaVu", "", 8)
            row = row + [""] * (col_count - len(row))
            for cell in row:
                pdf.cell(col_width, 6, strip_md_inline(cell)[:80], border=1)
            pdf.ln(6)
        pdf.ln(2)
        table_rows = []
        in_table = False

    for raw in lines:
        line = raw.rstrip()

        if line.strip().startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                flush_table()
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if "|" in line and line.strip().startswith("|"):
            if re.match(r"^\|\s*[-:]+", line.strip()):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            in_table = True
            table_rows.append(cells)
            continue
        elif in_table:
            flush_table()

        if not line.strip():
            pdf.ln(3)
            continue

        if line.startswith("# "):
            pdf.ln(2)
            pdf.set_font("DejaVu", "B", 16)
            pdf.multi_cell(CONTENT_WIDTH, 8, strip_md_inline(line[2:]))
            pdf.ln(2)
        elif line.startswith("## "):
            pdf.ln(2)
            pdf.set_font("DejaVu", "B", 13)
            pdf.multi_cell(CONTENT_WIDTH, 7, strip_md_inline(line[3:]))
            pdf.ln(1)
        elif line.startswith("### "):
            pdf.ln(1)
            pdf.set_font("DejaVu", "B", 11)
            pdf.multi_cell(CONTENT_WIDTH, 6, strip_md_inline(line[4:]))
            pdf.ln(1)
        elif line.startswith("- [ ] ") or line.startswith("- [x] ") or line.startswith("- [X] "):
            mark = "☑" if line[3] in "xX" else "☐"
            pdf.set_font("DejaVu", "", 10)
            pdf.multi_cell(CONTENT_WIDTH, 5, f"{mark} {strip_md_inline(line[6:])}")
        elif line.startswith("- ") or line.startswith("* "):
            pdf.set_font("DejaVu", "", 10)
            pdf.multi_cell(CONTENT_WIDTH, 5, f"• {strip_md_inline(line[2:])}")
        elif re.match(r"^\d+\.\s", line):
            pdf.set_font("DejaVu", "", 10)
            pdf.multi_cell(CONTENT_WIDTH, 5, strip_md_inline(line))
        elif line.strip() == "---":
            pdf.ln(2)
            y = pdf.get_y()
            pdf.set_draw_color(200, 200, 200)
            pdf.line(MARGIN, y, PAGE_WIDTH - MARGIN, y)
            pdf.ln(3)
        elif line.startswith(">"):
            pdf.set_font("DejaVu", "", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(CONTENT_WIDTH, 5, strip_md_inline(line.lstrip("> ").strip()))
            pdf.set_text_color(0, 0, 0)
        else:
            pdf.set_font("DejaVu", "", 10)
            pdf.multi_cell(CONTENT_WIDTH, 5, strip_md_inline(line))

    if in_code:
        flush_code()
    if in_table:
        flush_table()

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(pdf_path))


def main() -> int:
    if not FONT_REGULAR.exists():
        print(f"Missing font: {FONT_REGULAR}", file=sys.stderr)
        return 1
    if not MD_DIR.is_dir():
        print(f"Missing markdown directory: {MD_DIR}", file=sys.stderr)
        return 1

    md_files = sorted(MD_DIR.rglob("*.md"))
    if not md_files:
        print(f"No .md files in {MD_DIR}", file=sys.stderr)
        return 1

    ok, failed = 0, 0
    for md_path in md_files:
        rel = md_path.relative_to(MD_DIR)
        pdf_path = PDF_DIR / rel.with_suffix(".pdf")
        try:
            md_to_pdf(md_path, pdf_path)
            print(f"OK  {rel}")
            ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {rel}: {exc}", file=sys.stderr)
            failed += 1

    print(f"\nConverted {ok}/{len(md_files)} files" + (f", {failed} failed" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
