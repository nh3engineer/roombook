from pathlib import Path
from typing import List, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

from . import config

PRIMARY = colors.HexColor("#1A1A1A")
ACCENT = colors.HexColor("#E8A0B4")
ACCENT_SOFT = colors.HexColor("#F6E3E8")
MUTED = colors.HexColor("#6E5F6B")


def _logo_path() -> Path:
    return Path(config.__file__).resolve().parent / "assets" / "logo.png"


def _header(story, title: str, subtitle: str) -> None:
    logo = _logo_path()
    if logo.exists():
        img = Image(str(logo), width=40 * mm, height=26 * mm)
        img.hAlign = "LEFT"
        story.append(img)
        story.append(Spacer(1, 6 * mm))
    styles = getSampleStyleSheet()
    story.append(Paragraph(title, ParagraphStyle(
        "TitleEP", parent=styles["Title"], fontSize=20, textColor=PRIMARY)))
    if subtitle:
        story.append(Paragraph(subtitle, ParagraphStyle(
            "SubEP", parent=styles["Normal"], fontSize=10, textColor=MUTED)))
    story.append(Spacer(1, 8 * mm))


def _table(story, headers: Sequence[str], rows: Sequence[Sequence[object]],
           widths: List[float]) -> None:
    data = [list(headers)] + [list(r) for r in rows]
    col_widths = [w * mm for w in widths]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ACCENT_SOFT]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9C3CE")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(table)
    story.append(Spacer(1, 6 * mm))


def _footer_text(project) -> str:
    return (f"Raumbuch · Eckert & Partner Kälteplanung · "
            f"Projekt {project.name or '-'} · {project.version or '-'}")


def export_project_pdf(project, path: Path) -> None:
    doc = SimpleDocTemplate(str(path), pagesize=A4,
                            topMargin=15 * mm, bottomMargin=15 * mm,
                            title="Raumbuch – " + (project.name or "Projekt"))
    story: List[object] = []
    _header(story, f"Raumbuch – {project.name or 'Projekt'}",
            f"Auslegung/Version: {project.version or '-'} · Kunde: {project.kunde or '-'}")
    styles = getSampleStyleSheet()

    story.append(Paragraph("Projektdaten", ParagraphStyle(
        "H1EP", parent=styles["Heading2"], textColor=PRIMARY)))
    _table(story, ["Feld", "Wert"], [
        ("Projektnummer", project.nummer),
        ("Bauvorhaben", project.bauvorhaben),
        ("Adresse", project.adresse),
        ("Ansprechpartner", project.ansprechpartner),
        ("Bearbeiter", project.bearbeiter),
        ("Datum", project.datum),
        ("Planungsstand", project.planungsstand),
        ("Notizen", project.notizen),
    ], [50, 120])

    story.append(Paragraph("Räume", ParagraphStyle(
        "H2EP", parent=styles["Heading2"], textColor=PRIMARY)))
    _table(story, ["Nr.", "Raum", "Raumtyp", "L (m)", "B (m)", "H (m)", "Volumen (m³)"],
           [[r.nummer, r.name, r.raumtyp, f"{r.laenge:g}", f"{r.breite:g}",
             f"{r.hoehe:g}", f"{r.volumen():.2f}"] for r in project.raeume],
           [18, 42, 40, 16, 16, 16, 24])

    story.append(Paragraph("Zentrale", ParagraphStyle(
        "H3EP", parent=styles["Heading2"], textColor=PRIMARY)))
    _table(story, ["Bezeichnung", "Medium", "Leistung (kW)", "Temperatur (°C)"],
           [[z.bezeichnung, z.medium, f"{z.leistung_kw:g}", f"{z.temperatur_c:g}"]
            for z in project.zentrale],
           [60, 30, 32, 32])

    story.append(Paragraph("Füllmenge", ParagraphStyle(
        "H4EP", parent=styles["Heading2"], textColor=PRIMARY)))
    _table(story, ["Medium", "Menge (kg)", "Ort"],
           [[f.medium, f"{f.menge_kg:g}", f.ort] for f in project.fuellmengen],
           [60, 30, 66])

    story.append(Paragraph("Summen", ParagraphStyle(
        "H5EP", parent=styles["Heading2"], textColor=PRIMARY)))
    _table(story, ["Bezeichnung", "Wert"], [
        ("Gesamtfläche", f"{project.gesamtflaeche():.2f} m²"),
        ("Gesamtvolumen", f"{project.gesamtvolumen():.2f} m³"),
        ("Gesamtleistung Zentrale", f"{project.gesamtleistung_kw():.2f} kW"),
        ("Gesamte Füllmenge", f"{project.gesamtmenge_kg():.2f} kg"),
    ], [80, 60])

    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(_footer_text(project), ParagraphStyle(
        "FootEP", parent=styles["Normal"], fontSize=8, textColor=MUTED)))
    doc.build(story)
