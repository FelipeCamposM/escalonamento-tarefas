"""Gera o relatório acadêmico em PDF e incorpora os códigos-fonte.

O documento usa páginas A4 em retrato para o texto e em paisagem para os
apêndices de código. Execute depois de atualizar docs/RELATORIO.md.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    LongTable,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "RELATORIO.md"
OUTPUT = ROOT / "output" / "pdf" / "Relatorio_Escalonamento_Tarefas.pdf"
SOURCE_FILES = (
    ("Apêndice A - Núcleo dos algoritmos", ROOT / "src" / "scheduler.py"),
    ("Apêndice B - Automação dos experimentos", ROOT / "scripts" / "run_benchmarks.py"),
)

NAVY = colors.HexColor("#0B1F33")
BLUE = colors.HexColor("#0E7490")
CYAN = colors.HexColor("#22D3EE")
INK = colors.HexColor("#17202A")
MUTED = colors.HexColor("#536273")
LIGHT = colors.HexColor("#E8F1F5")
PALE = colors.HexColor("#F5F8FA")
LINE = colors.HexColor("#C9D6DE")


def register_fonts() -> tuple[str, str, str, str]:
    """Registra Arial quando disponível e mantém fontes PDF como fallback."""
    font_dir = Path("C:/Windows/Fonts")
    files = {
        "Body": font_dir / "arial.ttf",
        "Body-Bold": font_dir / "arialbd.ttf",
        "Body-Italic": font_dir / "ariali.ttf",
        "Body-BoldItalic": font_dir / "arialbi.ttf",
    }
    if all(path.exists() for path in files.values()):
        for name, path in files.items():
            pdfmetrics.registerFont(TTFont(name, str(path)))
        pdfmetrics.registerFontFamily(
            "Body",
            normal="Body",
            bold="Body-Bold",
            italic="Body-Italic",
            boldItalic="Body-BoldItalic",
        )
        return "Body", "Body-Bold", "Body-Italic", "Body-BoldItalic"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique"


BODY_FONT, BOLD_FONT, ITALIC_FONT, BOLD_ITALIC_FONT = register_fonts()


def inline_markdown(value: str) -> str:
    """Converte a pequena parte de Markdown usada pelo relatório em XML seguro."""
    code_tokens: dict[str, str] = {}

    def protect_code(match: re.Match[str]) -> str:
        token = f"@@CODE{len(code_tokens)}@@"
        code_tokens[token] = html.escape(match.group(1))
        return token

    value = re.sub(r"`([^`]+)`", protect_code, value)
    value = html.escape(value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", value)
    for token, code in code_tokens.items():
        value = value.replace(token, f'<font name="Courier">{code}</font>')
    return value


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    styles = {
        "Body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName=BODY_FONT,
            fontSize=10.2,
            leading=15.2,
            textColor=INK,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            allowWidows=0,
            allowOrphans=0,
        ),
        "Section": ParagraphStyle(
            "Section",
            parent=base["Heading1"],
            fontName=BOLD_FONT,
            fontSize=17,
            leading=21,
            textColor=NAVY,
            spaceBefore=16,
            spaceAfter=9,
            keepWithNext=True,
        ),
        "Subsection": ParagraphStyle(
            "Subsection",
            parent=base["Heading2"],
            fontName=BOLD_FONT,
            fontSize=12.4,
            leading=16,
            textColor=BLUE,
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "List": ParagraphStyle(
            "List",
            parent=base["BodyText"],
            fontName=BODY_FONT,
            fontSize=10,
            leading=14.5,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=3,
        ),
        "TableHeader": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName=BOLD_FONT,
            fontSize=8.1,
            leading=10,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "TableCell": ParagraphStyle(
            "TableCell",
            parent=base["BodyText"],
            fontName=BODY_FONT,
            fontSize=7.9,
            leading=10.1,
            textColor=INK,
            alignment=TA_LEFT,
        ),
        "Caption": ParagraphStyle(
            "Caption",
            parent=base["BodyText"],
            fontName=ITALIC_FONT,
            fontSize=8.5,
            leading=11,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceBefore=4,
            spaceAfter=10,
        ),
        "CoverKicker": ParagraphStyle(
            "CoverKicker",
            parent=base["BodyText"],
            fontName=BOLD_FONT,
            fontSize=11,
            leading=14,
            textColor=BLUE,
            alignment=TA_CENTER,
            spaceAfter=16,
        ),
        "CoverTitle": ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontName=BOLD_FONT,
            fontSize=27,
            leading=33,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=15,
        ),
        "CoverSubtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=base["BodyText"],
            fontName=BODY_FONT,
            fontSize=12.2,
            leading=17,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "CoverAuthor": ParagraphStyle(
            "CoverAuthor",
            parent=base["BodyText"],
            fontName=BOLD_FONT,
            fontSize=11.2,
            leading=17,
            textColor=INK,
            alignment=TA_CENTER,
        ),
        "Small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName=BODY_FONT,
            fontSize=8.5,
            leading=11,
            textColor=MUTED,
        ),
        "Code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.8,
            leading=9.1,
            textColor=INK,
            alignment=TA_LEFT,
            wordWrap="LTR",
        ),
        "CodeLine": ParagraphStyle(
            "CodeLine",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7,
            leading=9.2,
            textColor=MUTED,
            alignment=TA_RIGHT,
        ),
    }
    return styles


STYLES = build_styles()


class AccentRule(Flowable):
    """Pequena faixa visual usada na capa."""

    def __init__(self, width: float, height: float = 5):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self) -> None:
        self.canv.setFillColor(BLUE)
        self.canv.roundRect(0, 0, self.width * 0.72, self.height, 2, fill=1, stroke=0)
        self.canv.setFillColor(CYAN)
        self.canv.roundRect(self.width * 0.74, 0, self.width * 0.26, self.height, 2, fill=1, stroke=0)


class AcademicDocTemplate(BaseDocTemplate):
    """Documento com sumário automático, marcadores e metadados."""

    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=2.35 * cm,
            rightMargin=2.15 * cm,
            topMargin=2.3 * cm,
            bottomMargin=2.1 * cm,
            title="Implementação e Análise de Estratégias de Algoritmos para Escalonamento de Tarefas",
            author="Felipe Campos Macedo; Gabriel Guimarães Naves",
            subject="Trabalho de Análise e Projeto de Algoritmos - UFG",
            creator="ScheduleLab",
        )
        portrait_frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            A4[0] - self.leftMargin - self.rightMargin,
            A4[1] - self.topMargin - self.bottomMargin,
            id="portrait",
        )
        cover_frame = Frame(2.3 * cm, 1.8 * cm, A4[0] - 4.6 * cm, A4[1] - 3.6 * cm, id="cover")
        wide = landscape(A4)
        code_frame = Frame(1.45 * cm, 1.45 * cm, wide[0] - 2.9 * cm, wide[1] - 2.9 * cm, id="code")
        self.addPageTemplates(
            [
                PageTemplate(id="Cover", pagesize=A4, frames=[cover_frame], onPage=draw_cover_page),
                PageTemplate(id="Body", pagesize=A4, frames=[portrait_frame], onPage=draw_body_page),
                PageTemplate(id="Code", pagesize=wide, frames=[code_frame], onPage=draw_code_page),
            ]
        )
        self._bookmark_index = 0

    def afterFlowable(self, flowable: Flowable) -> None:
        if not isinstance(flowable, Paragraph):
            return
        if flowable.style.name not in {"Section", "Subsection"}:
            return
        level = 0 if flowable.style.name == "Section" else 1
        text = flowable.getPlainText()
        key = getattr(flowable, "_bookmark_key", None)
        if key is None:
            key = f"heading-{self._bookmark_index}"
            self._bookmark_index += 1
            flowable._bookmark_key = key
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=False)
        self.notify("TOCEntry", (level, text, self.page, key))


def draw_cover_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setPageSize(A4)
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 1.05 * cm, A4[0], 1.05 * cm, fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.circle(A4[0] - 2.1 * cm, A4[1] - 2.35 * cm, 0.38 * cm, fill=1, stroke=0)
    canvas.setFont(BOLD_FONT, 7.5)
    canvas.setFillColor(colors.white)
    canvas.drawCentredString(A4[0] - 2.1 * cm, A4[1] - 2.45 * cm, "UFG")
    canvas.setFillColor(LIGHT)
    canvas.rect(0, 0, A4[0], 0.35 * cm, fill=1, stroke=0)
    canvas.restoreState()


def draw_body_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setPageSize(A4)
    width, height = A4
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.45)
    canvas.line(doc.leftMargin, height - 1.45 * cm, width - doc.rightMargin, height - 1.45 * cm)
    canvas.setFont(BOLD_FONT, 7.2)
    canvas.setFillColor(BLUE)
    canvas.drawString(doc.leftMargin, height - 1.18 * cm, "UFG  |  ANÁLISE E PROJETO DE ALGORITMOS")
    canvas.setFont(BODY_FONT, 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(width - doc.rightMargin, height - 1.18 * cm, "Escalonamento de Tarefas")
    canvas.setStrokeColor(LINE)
    canvas.line(doc.leftMargin, 1.35 * cm, width - doc.rightMargin, 1.35 * cm)
    canvas.setFont(BODY_FONT, 8)
    canvas.drawString(doc.leftMargin, 0.92 * cm, "ScheduleLab  •  2026")
    canvas.drawRightString(width - doc.rightMargin, 0.92 * cm, str(doc.page))
    canvas.restoreState()


def draw_code_page(canvas, doc) -> None:
    canvas.saveState()
    wide = landscape(A4)
    canvas.setPageSize(wide)
    width, height = wide
    canvas.setStrokeColor(LINE)
    canvas.line(1.45 * cm, height - 1.0 * cm, width - 1.45 * cm, height - 1.0 * cm)
    canvas.setFont(BOLD_FONT, 7.2)
    canvas.setFillColor(BLUE)
    canvas.drawString(1.45 * cm, height - 0.73 * cm, "APÊNDICES DE CÓDIGO-FONTE")
    canvas.setFont(BODY_FONT, 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(width - 1.45 * cm, height - 0.73 * cm, "ScheduleLab")
    canvas.line(1.45 * cm, 0.92 * cm, width - 1.45 * cm, 0.92 * cm)
    canvas.setFont(BODY_FONT, 8)
    canvas.drawRightString(width - 1.45 * cm, 0.5 * cm, str(doc.page))
    canvas.restoreState()


def cover_story() -> list[Flowable]:
    content_width = A4[0] - 4.6 * cm
    return [
        Spacer(1, 1.05 * cm),
        Paragraph("UNIVERSIDADE FEDERAL DE GOIÁS", STYLES["CoverKicker"]),
        Paragraph("ANÁLISE E PROJETO DE ALGORITMOS", STYLES["CoverSubtitle"]),
        Spacer(1, 1.55 * cm),
        AccentRule(content_width),
        Spacer(1, 0.65 * cm),
        Paragraph(
            "Implementação e Análise de Estratégias de Algoritmos para Escalonamento de Tarefas",
            STYLES["CoverTitle"],
        ),
        Paragraph("Modelo P|prec|C<sub>max</sub>", STYLES["CoverSubtitle"]),
        Spacer(1, 1.55 * cm),
        Paragraph("Felipe Campos Macedo  •  202501133", STYLES["CoverAuthor"]),
        Paragraph("Gabriel Guimarães Naves  •  202503292", STYLES["CoverAuthor"]),
        Spacer(1, 1.5 * cm),
        HRFlowable(width="38%", thickness=0.8, color=LINE, hAlign="CENTER"),
        Spacer(1, 0.45 * cm),
        Paragraph("Professor: André Luiz Moura", STYLES["CoverSubtitle"]),
        Spacer(1, 2.0 * cm),
        Paragraph("Goiânia - GO<br/>2026", STYLES["CoverSubtitle"]),
    ]


def markdown_table(rows: list[str]) -> Table:
    parsed = [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in rows]
    if len(parsed) > 1 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in parsed[1]):
        parsed.pop(1)
    columns = len(parsed[0])
    available = A4[0] - 2.35 * cm - 2.15 * cm
    if columns == 4:
        widths = [available * 0.28, available * 0.39, available * 0.20, available * 0.13]
    elif columns == 6:
        widths = [available * 0.25] + [available * 0.15] * 5
    else:
        widths = [available / columns] * columns
    data = []
    for row_index, row in enumerate(parsed):
        style = STYLES["TableHeader"] if row_index == 0 else STYLES["TableCell"]
        data.append([Paragraph(inline_markdown(cell), style) for cell in row])
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
                ("GRID", (0, 0), (-1, -1), 0.35, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def parse_report() -> list[Flowable]:
    lines = REPORT.read_text(encoding="utf-8").splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("## "))
    lines = lines[start:]
    story: list[Flowable] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph:
            return
        text = " ".join(part.strip() for part in paragraph)
        style = STYLES["Body"]
        if text.startswith("**Palavras-chave:**"):
            box = Table([[Paragraph(inline_markdown(text), STYLES["Small"]) ]], colWidths=[A4[0] - 4.5 * cm])
            box.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                        ("LEFTPADDING", (0, 0), (-1, -1), 9),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                )
            )
            story.append(box)
            story.append(Spacer(1, 7))
        else:
            story.append(Paragraph(inline_markdown(text), style))
        paragraph.clear()

    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        if not line:
            flush_paragraph()
            index += 1
            continue
        if line.startswith("## "):
            flush_paragraph()
            title = line[3:].strip()
            if title.startswith("Apêndice A"):
                break
            story.append(Paragraph(inline_markdown(title), STYLES["Section"]))
            index += 1
            continue
        if line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markdown(line[4:].strip()), STYLES["Subsection"]))
            index += 1
            continue
        if line.startswith("|"):
            flush_paragraph()
            table_lines = []
            while index < len(lines) and lines[index].startswith("|"):
                table_lines.append(lines[index])
                index += 1
            story.extend([markdown_table(table_lines), Spacer(1, 9)])
            continue
        if re.match(r"^\d+\.\s+", line) or line.startswith("- "):
            flush_paragraph()
            ordered = bool(re.match(r"^\d+\.\s+", line))
            items = []
            while index < len(lines):
                current = lines[index].strip()
                match = re.match(r"^\d+\.\s+(.*)", current) if ordered else re.match(r"^-\s+(.*)", current)
                if not match:
                    break
                items.append(ListItem(Paragraph(inline_markdown(match.group(1)), STYLES["List"]), leftIndent=13))
                index += 1
            list_options = {
                "bulletType": "1" if ordered else "bullet",
                "start": "1" if ordered else "•",
                "leftIndent": 22,
                "bulletFontName": BOLD_FONT,
                "bulletFontSize": 8,
                "bulletColor": BLUE,
                "spaceAfter": 7,
            }
            story.append(ListFlowable(items, **list_options))
            continue
        paragraph.append(line)
        index += 1
    flush_paragraph()
    return story


def code_table(title: str, source: Path) -> list[Flowable]:
    lines = source.read_text(encoding="utf-8").splitlines()
    wide = landscape(A4)
    available = wide[0] - 2.9 * cm
    relative = source.relative_to(ROOT).as_posix()
    result: list[Flowable] = [
        Paragraph(title, STYLES["Section"]),
        Paragraph(
            f"Arquivo integral: <font name=\"Courier\">{relative}</font> "
            f"({len(lines)} linhas).",
            STYLES["Small"],
        ),
        Spacer(1, 7),
    ]
    position = 0
    first_page = True
    while position < len(lines):
        chunk_size = 44 if first_page else 51
        chunk = lines[position : position + chunk_size]
        numbered = "\n".join(
            f"{number:>4}  |  {line}"
            for number, line in enumerate(chunk, start=position + 1)
        )
        block = Preformatted(numbered, STYLES["Code"], maxLineLength=160)
        panel = Table([[block]], colWidths=[available], hAlign="LEFT")
        panel.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FBFCFD")),
                    ("BOX", (0, 0), (-1, -1), 0.55, LINE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        result.append(panel)
        position += len(chunk)
        first_page = False
        if position < len(lines):
            result.extend(
                [
                    PageBreak(),
                    Paragraph(
                        f"{relative} - continuação (linhas {position + 1} a "
                        f"{min(position + 51, len(lines))})",
                        STYLES["Small"],
                    ),
                    Spacer(1, 5),
                ]
            )
    return result


def build_pdf() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = AcademicDocTemplate(str(OUTPUT))
    story: list[Flowable] = []
    story.extend(cover_story())
    story.extend([NextPageTemplate("Body"), PageBreak()])

    story.append(Paragraph("Sumário", STYLES["Section"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            "TOC1",
            fontName=BOLD_FONT,
            fontSize=10.5,
            leading=16,
            leftIndent=0,
            firstLineIndent=0,
            textColor=NAVY,
            spaceBefore=4,
        ),
        ParagraphStyle(
            "TOC2",
            fontName=BODY_FONT,
            fontSize=9.2,
            leading=14,
            leftIndent=18,
            firstLineIndent=0,
            textColor=MUTED,
        ),
    ]
    story.extend([toc, PageBreak()])
    story.extend(parse_report())
    story.extend([NextPageTemplate("Code"), PageBreak()])
    for index, (title, source) in enumerate(SOURCE_FILES):
        if index:
            story.append(PageBreak())
        story.extend(code_table(title, source))
    doc.multiBuild(story)
    print(f"PDF gerado em {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
