# ❄️ Raumbuch

**Raumbuch – powered by Eckert & Partner**

Ein modernes, leicht verständliches digitales Raumbuch für die Kälteplanung.
Version 1.0 – Projektverwaltung & Raumgeometrie mit Kälteleistungsberechnung.

---

## Was kann Version 1.0?

### 📁 Projekte anlegen & verwalten
- Neues Projekt mit allen wichtigen Projektdaten (Projektname, -nummer, Kunde, Adresse, Bauvorhaben, Ansprechpartner, Datum, Planungsstand, Notizen)
- Projektliste mit **Suche**, Sortierung, Bearbeiten, **Archivieren** und Löschen (mit Rückfrage)
- Projekte **exportieren/importieren** (JSON-Datei) – ideal für Backup oder Übergabe an Kollegen

### 🧊 Raumgeometrie & Kälteleistung
- Räume pro Projekt anlegen: Länge, Breite, Höhe → **Fläche & Volumen automatisch**
- **Kälteleistung wird live berechnet** (Transmissionslast, Lüftungslast, interne Lasten, Sicherheitsfaktor)
- **Zwei Eingabevarianten:**
  1. **Direkteingabe** im Programm mit Live-Berechnung
  2. **Excel-Import** – Vorlage erstellen, ausfüllen, importieren (inkl. Validierung und verständlichen Fehlermeldungen)
- Raumliste als Tabelle mit **Gesamtübersicht** (Gesamtfläche, Gesamtvolumen, Summe Kälteleistung)
- „**Wie berechnet?**"-Button zeigt die Rechenwege transparent an
- Raumliste **als Excel exportieren**

### 💾 Zentraler Datenspeicher
- Alle Projekte liegen an **einem zentralen Datenordner** (Standard: `Dokumente\Raumbuch`)
- Ordner ist in den **Einstellungen** frei konfigurierbar – ideal für Netzlaufwerke, Backups oder mehrere Rechner
- Keine Daten im Programmordner

---

## 🚀 Installation (Windows 10/11)

### Schritt 1: Python installieren (nur einmal nötig)
1. Python herunterladen: https://www.python.org/downloads/ (Button „Download Python 3.x")
2. Installer starten und **wichtig**: Haken bei **„Add python.exe to PATH"** setzen
3. „Install Now" klicken – fertig

### Schritt 2: Raumbuch starten
1. Dieses Repository herunterladen (grüner „Code"-Button → „Download ZIP") und entpacken
2. **Doppelklick auf `start.bat`**
3. Beim ersten Start richtet sich das Programm selbst ein (virtuelle Umgebung + Bibliotheken) – das dauert ca. 1–2 Minuten, danach startet das Raumbuch

> Alternative ohne `start.bat`:
> ```bat
> python -m venv .venv
> .venv\Scripts\activate
> pip install -r requirements.txt
> python -m raumbuch.main
> ```

---

## ✅ In 5 Minuten testen

1. **Projekt anlegen**: „+ Neues Projekt" → Name z. B. „Molkerei Muster" → speichern
2. **Raum anlegen**: „+ Neuer Raum" → z. B. R-001, „Kühlraum 1", 5 × 4 × 3 m → die Kälteleistung wird sofort live angezeigt
3. **Excel testen**: „Excel-Vorlage erstellen" → Datei öffnen, eine Zeile ergänzen → „Excel-Import" → Raum erscheint in der Liste
4. **Zentraler Speicher**: „Einstellungen" → Ihren Wunschordner eintragen → „Ordner öffnen" zeigt alle Projektdateien
5. Fertig! 🎉

---

## 🎨 Logo & Farben

Das Programm nutzt die Original-Farbgebung von Eckert & Partner (kaelteplaner.de):
weicher Rosa-Lavendel-Ton als Hintergrund, schwarzer Text, weiße Karten und
Altrosa-Akzente (`#E8A0B4`).

**Offizielles Eckert-&-Partner-Logo einbinden:**
Einfach das Original-Logo als `logo.png` in den Ordner `raumbuch/assets/` speichern (altes überschreiben) – das Programm nutzt es automatisch beim nächsten Start.
Die Farben können zentral in `raumbuch/config.py` (Abschnitt `COLORS`) angepasst werden.

Vorschau der Oberfläche: `docs/screenshot-projektliste.png` und `docs/screenshot-raumansicht.png`.

---

## 🧮 Berechnungsgrundlagen

- **Transmissionslast:** Q_T = (U_Wand × A_Wand + U_Decke × A_Decke + U_Boden × A_Boden) × ΔT
  - A_Wand = 2 × (Länge + Breite) × Höhe, A_Decke = A_Boden = Länge × Breite
- **Lüftungslast:** Q_L = (Volumen × Luftwechsel / 3600) × 1,2 kg/m³ × 1006 J/(kg·K) × ΔT
- **Gesamt:** (Q_T + Q_L + interne Lasten) × (1 + Sicherheitsfaktor / 100)

Alle Werte sind transparent im Programm unter „Wie berechnet?" einsehbar.

---

## 🗺️ Ausblick (nächste Versionen)

Das Raumbuch ist als ständig erweiterbares System gebaut. Geplant für Folgeversionen:
- Druck-/PDF-Export des Raumbuchs im Firmenlayout
- Detaillierte Bauteile (Fenster, Türen, Trennwände)
- Geräte-/Komponentenauswahl
- Raumgrafik & Schemaansicht

---

**Eckert & Partner Kälteplanung** · https://www.kaelteplaner.de/
