from pathlib import Path
from typing import List, Sequence

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


from .models import Project

HEADER_FILL = PatternFill(start_color="FF1A1A1A", end_color="FF1A1A1A", fill_type="solid")
HEADER_FONT = Font(color="FFFFFFFF", bold=True, size=11)


def _new_sheet(wb: Workbook, title: str, headers: Sequence[str],
               rows: Sequence[Sequence[object]]) -> None:
    ws = wb.active if wb.active.title == "Sheet" else wb.create_sheet()
    ws.title = title
    ws.append(list(headers))
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(col)].width = max(
            14, len(str(headers[col - 1])) + 4)
    for row in rows:
        ws.append(list(row))


def export_project(project: Project, path: Path) -> None:
    wb = Workbook()
    _new_sheet(wb, "Projekt", ["Feld", "Wert"],
               [(k, v) for k, v in _projekt_zeilen(project)])
    _new_sheet(wb, "Räume",
               ["Raumnummer", "Raumname", "Raumtyp", "Länge (m)", "Breite (m)",
                "Höhe (m)", "Fläche (m²)", "Volumen (m³)", "Notizen"],
               [[r.nummer, r.name, r.raumtyp, r.laenge, r.breite, r.hoehe,
                 round(r.flaeche(), 2), round(r.volumen(), 2), r.notizen]
                for r in project.raeume])
    _new_sheet(wb, "Zentrale",
               ["Bezeichnung", "Medium", "Leistung (kW)", "Temperatur (°C)", "Notizen"],
               [[z.bezeichnung, z.medium, z.leistung_kw, z.temperatur_c, z.notizen]
                for z in project.zentrale])
    _new_sheet(wb, "Füllmenge",
               ["Medium", "Menge (kg)", "Ort", "Notizen"],
               [[f.medium, f.menge_kg, f.ort, f.notizen] for f in project.fuellmengen])
    _new_sheet(wb, "Summen", ["Bezeichnung", "Wert"], [
        ("Gesamtfläche (m²)", round(project.gesamtflaeche(), 2)),
        ("Gesamtvolumen (m³)", round(project.gesamtvolumen(), 2)),
        ("Gesamtleistung Zentrale (kW)", round(project.gesamtleistung_kw(), 2)),
        ("Gesamte Füllmenge (kg)", round(project.gesamtmenge_kg(), 2)),
    ])
    wb.save(path)


def _projekt_zeilen(project: Project) -> List[tuple]:
    return [
        ("Projektname", project.name),
        ("Projektnummer", project.nummer),
        ("Auslegung/Version", project.version),
        ("Kunde", project.kunde),
        ("Adresse", project.adresse),
        ("Bauvorhaben", project.bauvorhaben),
        ("Ansprechpartner", project.ansprechpartner),
        ("Bearbeiter", project.bearbeiter),
        ("Datum", project.datum),
        ("Planungsstand", project.planungsstand),
        ("Notizen", project.notizen),
        ("Anzahl Räume", len(project.raeume)),
    ]
