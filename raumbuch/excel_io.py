from pathlib import Path
from typing import List, Tuple

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from . import config
from .models import Room

HEADERS = [
    "Raumnummer", "Raumname", "Raumtyp", "Länge (m)", "Breite (m)",
    "Höhe (m)", "Solltemperatur (°C)", "Umgebungstemperatur (°C)",
    "U-Wert Wand (W/m²K)", "U-Wert Decke (W/m²K)", "U-Wert Boden (W/m²K)",
    "Luftwechsel (1/h)", "Innere Lasten (W)", "Sicherheitsfaktor (%)", "Notizen",
]

NUMERIC_FIELDS = [
    "laenge", "breite", "hoehe", "solltemperatur", "umgebungstemperatur",
    "u_wand", "u_decke", "u_boden", "luftwechsel", "innere_laste",
    "sicherheitsfaktor",
]

HEADER_FILL = PatternFill(start_color="FF" + config.COLORS["primary"].lstrip("#"),
                          end_color="FF" + config.COLORS["primary"].lstrip("#"),
                          fill_type="solid")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)


def create_template(path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Räume"
    ws.append(HEADERS)
    for col in range(1, len(HEADERS) + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[get_column_letter(col)].width = max(14, len(HEADERS[col - 1]) + 4)
    example = Room(
        nummer="R-001", name="Kühlraum 1", raumtyp="Kühlraum",
        laenge=5, breite=4, hoehe=3, solltemperatur=4, umgebungstemperatur=25,
        u_wand=0.4, u_decke=0.4, u_boden=0.4, luftwechsel=0.5,
        innere_laste=0, sicherheitsfaktor=10,
    )
    ws.append(_room_to_row(example))
    ws.cell(row=2, column=1).value = "R-002 (Beispielzeile – bitte ersetzen)"
    info = wb.create_sheet("Anleitung")
    info_lines = [
        "Raumbuch – Excel-Import",
        "",
        "So funktioniert es:",
        "1. Füllen Sie das Blatt 'Räume' aus (eine Zeile = ein Raum).",
        "2. Die Beispielzeile können Sie überschreiben.",
        "3. Zahlen bitte ohne Einheiten eingeben (z. B. 5 statt 5 m).",
        "4. Leere Zeilen werden automatisch übersprungen.",
        "5. Speichern Sie die Datei und importieren Sie sie im Raumbuch.",
        "",
        "Pflichtfelder: Raumnummer, Raumname, Länge, Breite, Höhe.",
        "Alle übrigen Spalten sind optional – es gelten die Standardwerte.",
    ]
    for line in info_lines:
        info.append([line])
    info.column_dimensions["A"].width = 80
    info["A1"].font = Font(bold=True, size=14)
    wb.save(path)


def _room_to_row(room: Room) -> list:
    return [
        room.nummer, room.name, room.raumtyp,
        room.laenge, room.breite, room.hoehe,
        room.solltemperatur, room.umgebungstemperatur,
        room.u_wand, room.u_decke, room.u_boden,
        room.luftwechsel, room.innere_laste, room.sicherheitsfaktor,
        room.notizen,
    ]


def export_rooms(rooms: List[Room], path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Räume"
    ws.append(HEADERS + ["Fläche (m²)", "Volumen (m³)", "Kälteleistung (W)"])
    for col in range(1, len(HEADERS) + 4):
        cell = ws.cell(row=1, column=col)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        ws.column_dimensions[get_column_letter(col)].width = 16
    from .calculation import berechne_kaelteleistung
    for room in rooms:
        result = berechne_kaelteleistung(room)
        ws.append(_room_to_row(room) + [result["flaeche"], result["volumen"], round(result["gesamt"], 1)])
    wb.save(path)


def import_rooms(path: Path) -> Tuple[List[Room], List[str]]:
    wb = load_workbook(path, data_only=True)
    if "Räume" not in wb.sheetnames:
        return [], ["Die Datei enthält kein Blatt mit dem Namen 'Räume'. "
                    "Bitte verwenden Sie die Vorlage aus dem Raumbuch."]
    ws = wb["Räume"]
    header = [str(c.value or "").strip() for c in ws[1]]
    try:
        col_map = {name: header.index(name) for name in HEADERS}
    except ValueError as exc:
        return [], [f"Die Spalten entsprechen nicht der Vorlage ({exc}). "
                    "Bitte verwenden Sie die Vorlage aus dem Raumbuch."]

    rooms: List[Room] = []
    errors: List[str] = []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if all(v is None or str(v).strip() == "" for v in row):
            continue
        room = Room()
        try:
            room.nummer = str(row[col_map["Raumnummer"]] or "").strip()
            room.name = str(row[col_map["Raumname"]] or "").strip()
            room.raumtyp = str(row[col_map["Raumtyp"]] or "Kühlraum").strip() or "Kühlraum"
            for label, field in zip(HEADERS[3:14], NUMERIC_FIELDS):
                value = row[col_map[label]]
                if value is not None and str(value).strip() != "":
                    setattr(room, field, float(str(value).replace(",", ".")))
            room.notizen = str(row[col_map["Notizen"]] or "").strip()
        except (ValueError, TypeError):
            errors.append(f"Zeile {row_idx}: Ungültiger Zahlenwert – Raum wurde übersprungen.")
            continue
        if not room.nummer or not room.name:
            errors.append(f"Zeile {row_idx}: Raumnummer oder Raumname fehlt – Raum wurde übersprungen.")
            continue
        if room.laenge <= 0 or room.breite <= 0 or room.hoehe <= 0:
            errors.append(f"Zeile {row_idx} ({room.name}): Länge, Breite und Höhe müssen größer als 0 sein – Raum wurde übersprungen.")
            continue
        rooms.append(room)
    if not rooms and not errors:
        errors.append("In der Datei wurden keine Räume gefunden.")
    return rooms, errors
