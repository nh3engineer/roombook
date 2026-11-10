# ❄️ Raumbuch

**Raumbuch – powered by Eckert & Partner**

Das digitale Raumbuch für die Kälteplanung – im Original-Branding von Eckert & Partner.
Version 2.0 – Neuaufbau mit Benutzerverwaltung, vier Bereichen und mehreren Auslegungen pro Projekt.

---

## Was kann Version 2.0?

### 👤 Benutzerebene
- Mitarbeiter **registrieren sich mit Name, E-Mail-Adresse und Passwort** (einmalig)
- **Anmeldung** beim Start der Software – jeder sieht, wer angemeldet ist
- Abmelden jederzeit möglich

### 🗂️ Vier Bereiche (per Seitenleiste)
1. **Projekt** – alle wichtigen Projektdaten (Name, Nummer, Kunde, Adresse, Bauvorhaben, Ansprechpartner, Bearbeiter, Datum, Planungsstand, Notizen)
2. **Raum** – die Raumgeometrie als Liste: **Länge, Breite, Höhe → Volumen automatisch**; **Raumtyp als Dropdown** (Lager, Klimatisierung, Technische Klimatisierung, Tiefkühlung u. a.) – die Typenliste ist **beliebig erweiterbar** (Einstellungen → „Raumtypen verwalten")
3. **Zentrale** – Auslegung der Kälteerzeugung (Bezeichnung, Medium wie NH3/CO2, Leistung, Temperatur)
4. **Füllmenge** – Füllmengen erfassen (Medium, Menge in kg, Ort/Raum)

### 📁 Projektübersicht, Auslegungen & Speichersystem
- **Projektübersicht** als Startseite: alle gespeicherten Projekte und Auslegungen als Liste
- **Mehrere Auslegungen/Versionen pro Projekt**: über „Speichern unter ..." wird jede Auslegung als eigene Projektdatei gespeichert (z. B. „Projekt_Auslegung 1", „Projekt_Auslegung 2")
- **Öffnen** holt eine bestehende Auslegung zurück ins Programm
- **Beim Schließen der Software wird an ungespeicherte Änderungen erinnert** (Speichern / Verwerfen / Abbrechen)
- Ungespeicherte Änderungen sind durch „•" neben dem Projektnamen sichtbar

### 📤 Export überall
- **Excel-Export** (Projekt, Räume, Zentrale, Füllmenge, Summen – je ein Blatt)
- **PDF-Export** mit E&P-Logo und Firmenfarben
- Auch die Projektübersicht aller Projekte ist als Excel exportierbar

### 💾 Zentraler Datenspeicher
- Alle Projekte, Auslegungen, Benutzer und Raumtypen liegen in **einem zentralen Datenordner** (Standard: `Dokumente\Raumbuch`)
- Ordner frei konfigurierbar unter „Einstellungen" – ideal für Netzlaufwerke und Backups

---

## 🚀 Installation (Windows 10/11)

1. **Python installieren** (nur einmal): https://www.python.org/downloads/ – im Installer den Haken **„Add python.exe to PATH"** setzen
2. Dieses Repository als **ZIP herunterladen** (grüner „Code"-Button) und entpacken
3. **Doppelklick auf `start.bat`** – beim ersten Start richtet sich alles selbst ein (ca. 1–2 Minuten)

---

## ✅ In 5 Minuten testen

1. **Registrieren**: Beim ersten Start Namen, E-Mail und Passwort eingeben → „Konto erstellen"
2. **Neues Projekt**: „+ Neues Projekt" → Projektdaten eintragen → „Übernehmen"
3. **Räume**: Seitenleiste „2 · Raum" → „+ Neuer Raum" → Raumtyp aus dem Dropdown wählen, L/B/H eintragen → Volumen erscheint automatisch
4. **Speichern unter**: Oben rechts „Speichern unter ..." → z. B. „Auslegung 2" – so legen Sie Varianten an
5. **Export**: „Als PDF exportieren" in jedem Bereich

---

## 🎨 Branding

Das Programm nutzt die Original-Farbwelt von Eckert & Partner (kaelteplaner.de):
weicher Rosa-Lavendel-Hintergrund, schwarzer Text, weiße Karten, Altrosa-Akzente.
Das **Original-Logo** (`EP_Bildmarke`) liegt unter `raumbuch/assets/logo.png` –
ein Logo-Update einfach durch die neue Datei ersetzen.
Farben zentral anpassbar in `raumbuch/config.py` (Abschnitt `COLORS`).

Vorschau: `docs/screenshot-projektliste.png` und `docs/screenshot-raumansicht.png`.

---

## 🗺️ Ausblick

Das Raumbuch ist als ständig erweiterbares System gebaut. Nächste Schritte nach Absprache:
- Berechnungen auf Basis der Raumliste (welche Daten zusammengefasst/berechnet werden sollen)
- Weitere Felder in Zentrale und Füllmenge
- Druckansichten im Firmenlayout

---

**Eckert & Partner Kälteplanung** · https://www.kaelteplaner.de/
