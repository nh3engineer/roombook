import customtkinter as ctk
from tkinter import messagebox

from .. import config, calculation, models


class ProjectDialog(ctk.CTkToplevel):
    def __init__(self, parent, project=None):
        super().__init__(parent)
        self.title("Neues Projekt" if project is None else "Projekt bearbeiten")
        self.geometry("560x640")
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        ctk.CTkLabel(self, text="Neues Projekt" if project is None else "Projekt bearbeiten",
                     font=("Segoe UI", 20, "bold"),
                     text_color=config.COLORS["primary"]).pack(pady=(20, 4))
        ctk.CTkLabel(self, text="Hier tragen Sie die wichtigsten Projektdaten ein.",
                     font=("Segoe UI", 12), text_color="#6B7B8A").pack(pady=(0, 12))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=32)

        fields = [
            ("Projektname *", "name"),
            ("Projektnummer", "nummer"),
            ("Kunde", "kunde"),
            ("Adresse", "adresse"),
            ("Bauvorhaben / Standort", "bauvorhaben"),
            ("Ansprechpartner", "ansprechpartner"),
            ("Datum", "datum"),
        ]
        self.entries = {}
        for label, key in fields:
            ctk.CTkLabel(form, text=label, font=("Segoe UI", 12),
                         text_color=config.COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(form, height=36, font=("Segoe UI", 13))
            entry.pack(fill="x")
            if project is not None:
                entry.insert(0, getattr(project, key))
            self.entries[key] = entry

        ctk.CTkLabel(form, text="Planungsstand", font=("Segoe UI", 12),
                     text_color=config.COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
        self.planungsstand = ctk.CTkComboBox(
            form, values=["In Planung", "In Bearbeitung", "Fertig geplant", "Abgeschlossen"],
            height=36, font=("Segoe UI", 13))
        self.planungsstand.pack(fill="x")
        if project is not None:
            self.planungsstand.set(project.planungsstand or "In Planung")

        ctk.CTkLabel(form, text="Notizen", font=("Segoe UI", 12),
                     text_color=config.COLORS["text_dark"], anchor="w").pack(fill="x", pady=(8, 2))
        self.notizen = ctk.CTkTextbox(form, height=70, font=("Segoe UI", 13))
        self.notizen.pack(fill="x")
        if project is not None:
            self.notizen.insert("1.0", project.notizen)

        if project is not None:
            self.project_id = project.id
            self.raeume = list(project.raeume)
            self.archiviert = project.archiviert
        else:
            self.project_id = None
            self.raeume = []
            self.archiviert = False

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=32, pady=(16, 20))
        from . import widgets
        widgets.ghost_button(btns, "Abbrechen", self.destroy, width=140).pack(side="left")
        widgets.primary_button(btns, "Projekt speichern", self.save, width=180).pack(side="right")

    def save(self):
        name = self.entries["name"].get().strip()
        if not name:
            messagebox.showwarning("Pflichtfeld", "Bitte geben Sie einen Projektnamen ein.",
                                   parent=self)
            return
        project = models.Project(
            name=name,
            nummer=self.entries["nummer"].get().strip(),
            kunde=self.entries["kunde"].get().strip(),
            adresse=self.entries["adresse"].get().strip(),
            bauvorhaben=self.entries["bauvorhaben"].get().strip(),
            ansprechpartner=self.entries["ansprechpartner"].get().strip(),
            datum=self.entries["datum"].get().strip(),
            planungsstand=self.planungsstand.get(),
            notizen=self.notizen.get("1.0", "end").strip(),
            archiviert=self.archiviert,
            raeume=self.raeume,
        )
        if self.project_id:
            project.id = self.project_id
        self.result = project
        self.destroy()


class RoomDialog(ctk.CTkToplevel):
    def __init__(self, parent, room=None):
        super().__init__(parent)
        self.title("Neuer Raum" if room is None else "Raum bearbeiten")
        self.geometry("760x780")
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        self.room_source = room

        ctk.CTkLabel(self, text="Neuer Raum" if room is None else "Raum bearbeiten",
                     font=("Segoe UI", 20, "bold"),
                     text_color=config.COLORS["primary"]).pack(pady=(16, 2))
        ctk.CTkLabel(self, text="Raumgeometrie eintragen – die Kälteleistung wird live berechnet.",
                     font=("Segoe UI", 12), text_color="#6B7B8A").pack(pady=(0, 8))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=32)

        self.entries = {}
        ctk.CTkLabel(form, text="Raumnummer *", font=("Segoe UI", 12), anchor="w").grid(
            row=0, column=0, sticky="ew", padx=(0, 10))
        e = ctk.CTkEntry(form, height=36, font=("Segoe UI", 13))
        e.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.entries["nummer"] = e
        ctk.CTkLabel(form, text="Raumname *", font=("Segoe UI", 12), anchor="w").grid(
            row=0, column=1, sticky="ew")
        e = ctk.CTkEntry(form, height=36, font=("Segoe UI", 13))
        e.grid(row=1, column=1, sticky="ew")
        e.bind("<KeyRelease>", lambda ev: self.update_live())
        self.entries["name"] = e

        ctk.CTkLabel(form, text="Raumtyp", font=("Segoe UI", 12), anchor="w").grid(
            row=2, column=0, sticky="ew", pady=(10, 2))
        self.raumtyp = ctk.CTkComboBox(
            form, values=["Kühlraum", "Tiefkühlraum", "Lagerraum", "Produktionsraum",
                          "Verkaufsraum", "Reiferaum", "Sonstiger Raum"],
            height=36, font=("Segoe UI", 13))
        self.raumtyp.grid(row=3, column=0, sticky="ew")
        ctk.CTkLabel(form, text="Sicherheitsfaktor (%)", font=("Segoe UI", 12), anchor="w").grid(
            row=2, column=1, sticky="ew", pady=(10, 2))
        e = ctk.CTkEntry(form, height=36, font=("Segoe UI", 13))
        e.grid(row=3, column=1, sticky="ew")
        e.bind("<KeyRelease>", lambda ev: self.update_live())
        self.entries["sicherheitsfaktor"] = e

        geo_fields = [
            ("Länge (m) *", "laenge"), ("Breite (m) *", "breite"), ("Höhe (m) *", "hoehe"),
            ("Solltemperatur (°C)", "solltemperatur"),
            ("Umgebungstemperatur (°C)", "umgebungstemperatur"),
            ("Luftwechsel (1/h)", "luftwechsel"),
            ("U-Wert Wand (W/m²K)", "u_wand"),
            ("U-Wert Decke (W/m²K)", "u_decke"),
            ("U-Wert Boden (W/m²K)", "u_boden"),
            ("Innere Lasten (W)", "innere_laste"),
        ]
        for i, (label, key) in enumerate(geo_fields):
            row = 4 + i // 2
            col = i % 2
            ctk.CTkLabel(form, text=label, font=("Segoe UI", 12), anchor="w").grid(
                row=row, column=col, sticky="ew", padx=(0, 10), pady=(8, 2))
            entry = ctk.CTkEntry(form, height=36, font=("Segoe UI", 13))
            entry.grid(row=row + 1, column=col, sticky="ew", padx=(0, 10))
            entry.bind("<KeyRelease>", lambda ev: self.update_live())
            self.entries[key] = entry

        ctk.CTkLabel(form, text="Notizen", font=("Segoe UI", 12), anchor="w").grid(
            row=15, column=0, columnspan=2, sticky="ew", pady=(8, 2))
        self.notizen = ctk.CTkTextbox(form, height=60, font=("Segoe UI", 13))
        self.notizen.grid(row=16, column=0, columnspan=2, sticky="ew")

        defaults = models.Room()
        if room is not None:
            self.entries["nummer"].insert(0, room.nummer)
            self.entries["name"].insert(0, room.name)
            self.raumtyp.set(room.raumtyp or "Kühlraum")
            for key in ("laenge", "breite", "hoehe", "solltemperatur", "umgebungstemperatur",
                        "luftwechsel", "u_wand", "u_decke", "u_boden", "innere_laste",
                        "sicherheitsfaktor"):
                self.entries[key].insert(0, f"{getattr(room, key):g}")
            self.notizen.insert("1.0", room.notizen)
        else:
            for key in ("solltemperatur", "umgebungstemperatur", "luftwechsel",
                        "u_wand", "u_decke", "u_boden", "sicherheitsfaktor"):
                self.entries[key].insert(0, f"{getattr(defaults, key):g}")

        self.live = ctk.CTkLabel(self, text="", font=("Segoe UI", 14, "bold"),
                                 text_color=config.COLORS["primary"])
        self.live.pack(pady=(6, 0))
        ctk.CTkLabel(self, text="Fläche, Volumen und Leistung werden automatisch berechnet.",
                     font=("Segoe UI", 11), text_color="#6B7B8A").pack()

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=32, pady=(10, 20))
        from . import widgets
        widgets.ghost_button(btns, "Wie berechnet?", self.explain, width=140).pack(side="left")
        widgets.ghost_button(btns, "Abbrechen", self.destroy, width=120).pack(side="right")
        widgets.primary_button(btns, "Raum speichern", self.save, width=170).pack(
            side="right", padx=(0, 10))

        self.update_live()

    def _room_from_form(self) -> models.Room:
        room = models.Room()
        room.nummer = self.entries["nummer"].get().strip()
        room.name = self.entries["name"].get().strip()
        room.raumtyp = self.raumtyp.get()
        room.notizen = self.notizen.get("1.0", "end").strip()
        for key in ("laenge", "breite", "hoehe", "solltemperatur", "umgebungstemperatur",
                    "luftwechsel", "u_wand", "u_decke", "u_boden", "innere_laste",
                    "sicherheitsfaktor"):
            raw = self.entries[key].get().strip().replace(",", ".")
            try:
                setattr(room, key, float(raw))
            except ValueError:
                setattr(room, key, 0.0)
        return room

    def update_live(self):
        room = self._room_from_form()
        if room.laenge > 0 and room.breite > 0 and room.hoehe > 0:
            res = calculation.berechne_kaelteleistung(room)
            self.live.configure(
                text=f"Fläche: {res['flaeche']:.2f} m²   ·   "
                     f"Volumen: {res['volumen']:.2f} m³   ·   "
                     f"Kälteleistung: {res['gesamt']:.0f} W ({res['gesamt']/1000:.2f} kW)")
        else:
            self.live.configure(text="Bitte Länge, Breite und Höhe eingeben ...")

    def explain(self):
        room = self._room_from_form()
        messagebox.showinfo("So rechnet das Raumbuch",
                            calculation.formel_erklaerung(room), parent=self)

    def save(self):
        room = self._room_from_form()
        if not room.nummer or not room.name:
            messagebox.showwarning("Pflichtfelder",
                                   "Bitte geben Sie Raumnummer und Raumname ein.", parent=self)
            return
        if room.laenge <= 0 or room.breite <= 0 or room.hoehe <= 0:
            messagebox.showwarning("Geometrie",
                                   "Länge, Breite und Höhe müssen größer als 0 sein.", parent=self)
            return
        self.result = room
        self.destroy()
