import customtkinter as ctk
from tkinter import messagebox

from .. import config, storage
from ..models import Project, Room, Zentrale, Fuellmenge
from . import widgets


def field_label(parent, text):
    return ctk.CTkLabel(parent, text=text, font=("Segoe UI", 12),
                        text_color=config.COLORS["text_dark"], anchor="w")


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, on_success):
        super().__init__(parent, fg_color="transparent")
        self.on_success = on_success
        self.register_mode = False

        logo_file = widgets.logo_path()
        try:
            from PIL import Image
            pil = Image.open(logo_file)
            logo = ctk.CTkImage(light_image=pil, size=(130, 84))
            ctk.CTkLabel(self, image=logo, text="").pack(pady=(60, 8))
        except Exception:
            pass

        ctk.CTkLabel(self, text="Raumbuch", font=("Segoe UI", 30, "bold"),
                     text_color=config.COLORS["primary"]).pack()
        ctk.CTkLabel(self, text="powered by Eckert & Partner",
                     font=("Segoe UI", 13),
                     text_color=config.COLORS["muted"]).pack(pady=(0, 28))

        self.card = ctk.CTkFrame(self, fg_color=config.COLORS["card"], corner_radius=16,
                                 border_width=1, border_color="#E7D5DC")
        self.card.pack(padx=30, fill="x", expand=False)

        self.error = ctk.CTkLabel(self, text="", font=("Segoe UI", 12),
                                  text_color=config.COLORS["danger"])
        self.error.pack(pady=(6, 0))

        self._build_fields()

    def _build_fields(self):
        for child in self.card.winfo_children():
            child.destroy()
        mode_register = self.register_mode
        ctk.CTkLabel(self.card, text="Registrieren" if mode_register else "Anmelden",
                     font=("Segoe UI", 18, "bold"),
                     text_color=config.COLORS["primary"]).pack(pady=(18, 4))
        ctk.CTkLabel(self.card,
                     text="Neuer Mitarbeiter? Dann einmalig registrieren."
                     if not mode_register else
                     "Bitte registrieren Sie sich mit Ihrer E-Mail-Adresse.",
                     font=("Segoe UI", 12),
                     text_color=config.COLORS["muted"]).pack(pady=(0, 10))

        entries = {}
        if mode_register:
            field_label(self.card, "Ihr Name").pack(fill="x", padx=24)
            entries["name"] = ctk.CTkEntry(self.card, height=38, font=("Segoe UI", 13))
            entries["name"].pack(fill="x", padx=24)
        field_label(self.card, "E-Mail-Adresse").pack(fill="x", padx=24, pady=(8, 0))
        entries["email"] = ctk.CTkEntry(self.card, height=38, font=("Segoe UI", 13))
        entries["email"].pack(fill="x", padx=24)
        field_label(self.card, "Passwort").pack(fill="x", padx=24, pady=(8, 0))
        entries["passwort"] = ctk.CTkEntry(self.card, height=38, show="•",
                                          font=("Segoe UI", 13))
        entries["passwort"].pack(fill="x", padx=24)
        self.entries = entries

        widgets.primary_button(self.card,
                               "Konto erstellen" if mode_register else "Anmelden",
                               self._submit, width=220).pack(pady=(18, 4))
        link = ctk.CTkButton(self.card,
                             text="Noch kein Konto? Jetzt registrieren"
                             if not mode_register else
                             "Zurück zur Anmeldung",
                             fg_color="transparent", height=30,
                             text_color=config.COLORS["accent"],
                             hover_color=config.COLORS["accent_soft"],
                             font=("Segoe UI", 12, "underline"),
                             command=self._toggle_mode)
        link.pack(pady=(0, 18))
        if mode_register:
            entries["name"].focus()
        else:
            entries["email"].focus()
        self.entries["passwort"].bind("<Return>", lambda e: self._submit())

    def _toggle_mode(self):
        self.register_mode = not self.register_mode
        self.error.configure(text="")
        self._build_fields()

    def _submit(self):
        email = self.entries["email"].get()
        passwort = self.entries["passwort"].get()
        if self.register_mode:
            name = self.entries["name"].get()
            ok, msg = storage.register_user(email, name, passwort)
            if not ok:
                self.error.configure(text=msg)
                return
            user = storage.login_user(email, passwort)
        else:
            user = storage.login_user(email, passwort)
            if user is None:
                self.error.configure(
                    text="Anmeldung fehlgeschlagen. Bitte E-Mail und Passwort prüfen.")
                return
        self.on_success(user)


class ProjectDialog(ctk.CTkToplevel):
    def __init__(self, parent, project=None):
        super().__init__(parent)
        self.title("Neues Projekt" if project is None else "Projektdaten")
        self.geometry("560x700")
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        self.source = project

        ctk.CTkLabel(self, text="Neues Projekt" if project is None else "Projektdaten",
                     font=("Segoe UI", 20, "bold"),
                     text_color=config.COLORS["primary"]).pack(pady=(18, 4))
        ctk.CTkLabel(self, text="Alle wichtigsten Daten zum Projekt.",
                     font=("Segoe UI", 12),
                     text_color=config.COLORS["muted"]).pack(pady=(0, 10))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=32)

        self.entries = {}
        fields = [
            ("Projektname *", "name"),
            ("Projektnummer", "nummer"),
            ("Auslegung / Version", "version"),
            ("Kunde", "kunde"),
            ("Adresse", "adresse"),
            ("Bauvorhaben / Standort", "bauvorhaben"),
            ("Ansprechpartner", "ansprechpartner"),
            ("Bearbeiter", "bearbeiter"),
            ("Datum", "datum"),
        ]
        for label, key in fields:
            field_label(form, label).pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(form, height=36, font=("Segoe UI", 13))
            entry.pack(fill="x")
            if project is not None:
                entry.insert(0, getattr(project, key))
            self.entries[key] = entry

        field_label(form, "Planungsstand").pack(fill="x", pady=(8, 2))
        self.planungsstand = ctk.CTkComboBox(
            form, values=["In Planung", "In Bearbeitung", "Fertig geplant",
                          "Abgeschlossen"], height=36, font=("Segoe UI", 13))
        self.planungsstand.pack(fill="x")
        self.planungsstand.set(project.planungsstand if project else "In Planung")

        field_label(form, "Notizen").pack(fill="x", pady=(8, 2))
        self.notizen = ctk.CTkTextbox(form, height=70, font=("Segoe UI", 13))
        self.notizen.pack(fill="x")
        if project is not None:
            self.notizen.insert("1.0", project.notizen)

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=32, pady=(16, 20))
        widgets.ghost_button(btns, "Abbrechen", self.destroy, width=140).pack(side="left")
        widgets.primary_button(btns, "Übernehmen", self._save, width=180).pack(side="right")

    def _save(self):
        name = self.entries["name"].get().strip()
        if not name:
            messagebox.showwarning("Pflichtfeld", "Bitte geben Sie einen Projektnamen ein.",
                                   parent=self)
            return
        project = self.source or Project()
        for key, entry in self.entries.items():
            setattr(project, key, entry.get().strip())
        project.planungsstand = self.planungsstand.get()
        project.notizen = self.notizen.get("1.0", "end").strip()
        self.result = project
        self.destroy()


class RoomDialog(ctk.CTkToplevel):
    def __init__(self, parent, room=None):
        super().__init__(parent)
        self.title("Neuer Raum" if room is None else "Raum bearbeiten")
        self.geometry("640x560")
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        self.source = room

        ctk.CTkLabel(self, text="Neuer Raum" if room is None else "Raum bearbeiten",
                     font=("Segoe UI", 20, "bold"),
                     text_color=config.COLORS["primary"]).pack(pady=(16, 2))
        ctk.CTkLabel(self, text="Raumgeometrie: Länge, Breite, Höhe – Volumen automatisch.",
                     font=("Segoe UI", 12),
                     text_color=config.COLORS["muted"]).pack(pady=(0, 10))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=32)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        self.entries = {}

        field_label(form, "Raumnummer *").grid(row=0, column=0, sticky="ew",
                                                padx=(0, 10), pady=(8, 2))
        field_label(form, "Raumname *").grid(row=0, column=1, sticky="ew", pady=(8, 2))
        self.entries["nummer"] = ctk.CTkEntry(form, height=36, font=("Segoe UI", 13))
        self.entries["nummer"].grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.entries["name"] = ctk.CTkEntry(form, height=36, font=("Segoe UI", 13))
        self.entries["name"].grid(row=1, column=1, sticky="ew")

        field_label(form, "Raumtyp").grid(row=2, column=0, columnspan=2,
                                          sticky="ew", pady=(10, 2))
        self.raumtyp = ctk.CTkComboBox(form, values=storage.list_raumtypen(),
                                       height=36, font=("Segoe UI", 13))
        self.raumtyp.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.raumtyp.set(room.raumtyp if room else storage.list_raumtypen()[0])

        field_label(form, "Länge (m) *").grid(row=4, column=0, sticky="ew",
                                              padx=(0, 10), pady=(8, 2))
        field_label(form, "Breite (m) *").grid(row=4, column=1, sticky="ew", pady=(8, 2))
        self.entries["laenge"] = ctk.CTkEntry(form, height=36, font=("Segoe UI", 13))
        self.entries["laenge"].grid(row=5, column=0, sticky="ew", padx=(0, 10))
        field_label(form, "Höhe (m) *").grid(row=6, column=0, sticky="ew",
                                             padx=(0, 10), pady=(8, 2))
        self.entries["breite"] = ctk.CTkEntry(form, height=36, font=("Segoe UI", 13))
        self.entries["breite"].grid(row=5, column=1, sticky="ew")
        self.entries["hoehe"] = ctk.CTkEntry(form, height=36, font=("Segoe UI", 13))
        self.entries["hoehe"].grid(row=7, column=0, sticky="ew", padx=(0, 10))

        for key in ("laenge", "breite", "hoehe"):
            self.entries[key].bind("<KeyRelease>", lambda e: self._update_live())

        field_label(form, "Notizen").grid(row=8, column=0, columnspan=2,
                                          sticky="ew", pady=(8, 2))
        self.notizen = ctk.CTkTextbox(form, height=60, font=("Segoe UI", 13))
        self.notizen.grid(row=9, column=0, columnspan=2, sticky="ew")

        if room is not None:
            self.entries["nummer"].insert(0, room.nummer)
            self.entries["name"].insert(0, room.name)
            for key in ("laenge", "breite", "hoehe"):
                self.entries[key].insert(0, f"{getattr(room, key):g}")
            self.notizen.insert("1.0", room.notizen)

        self.live = ctk.CTkLabel(self, text="", font=("Segoe UI", 14, "bold"),
                                 text_color=config.COLORS["primary"])
        self.live.grid(row=10, column=0, columnspan=2, sticky="w", pady=(10, 0))

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(14, 8))
        widgets.ghost_button(btns, "Abbrechen", self.destroy, width=140).pack(side="left")
        widgets.primary_button(btns, "Übernehmen", self._save, width=170).pack(side="right")

        self._update_live()

    def _room_from_form(self) -> Room:
        room = self.source or Room()
        room.nummer = self.entries["nummer"].get().strip()
        room.name = self.entries["name"].get().strip()
        room.raumtyp = self.raumtyp.get()
        room.notizen = self.notizen.get("1.0", "end").strip()
        for key in ("laenge", "breite", "hoehe"):
            raw = self.entries[key].get().strip().replace(",", ".")
            try:
                setattr(room, key, float(raw))
            except ValueError:
                setattr(room, key, 0.0)
        return room

    def _update_live(self):
        room = self._room_from_form()
        if room.laenge > 0 and room.breite > 0 and room.hoehe > 0:
            self.live.configure(
                text=f"Fläche: {room.flaeche():.2f} m²   ·   "
                     f"Volumen: {room.volumen():.2f} m³")
        else:
            self.live.configure(text="Bitte Länge, Breite und Höhe eingeben ...")

    def _save(self):
        room = self._room_from_form()
        if not room.nummer or not room.name:
            messagebox.showwarning("Pflichtfelder",
                                   "Bitte Raumnummer und Raumname eingeben.", parent=self)
            return
        if room.laenge <= 0 or room.breite <= 0 or room.hoehe <= 0:
            messagebox.showwarning("Geometrie",
                                   "Länge, Breite und Höhe müssen größer als 0 sein.",
                                   parent=self)
            return
        self.result = room
        self.destroy()


class ZentraleDialog(ctk.CTkToplevel):
    def __init__(self, parent, zentrale=None):
        super().__init__(parent)
        self.title("Zentrale anlegen" if zentrale is None else "Zentrale bearbeiten")
        self.geometry("560x480")
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        self.source = zentrale

        ctk.CTkLabel(self, text="Zentrale (Kälteerzeugung)",
                     font=("Segoe UI", 20, "bold"),
                     text_color=config.COLORS["primary"]).pack(pady=(16, 2))
        ctk.CTkLabel(self, text="Auslegung der Kälteerzeugung / Zentrale.",
                     font=("Segoe UI", 12),
                     text_color=config.COLORS["muted"]).pack(pady=(0, 10))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=32)
        self.entries = {}

        def add(label, key):
            field_label(form, label).pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(form, height=36, font=("Segoe UI", 13))
            entry.pack(fill="x")
            self.entries[key] = entry

        add("Bezeichnung *", "bezeichnung")
        field_label(form, "Medium").pack(fill="x", pady=(8, 2))
        self.medium = ctk.CTkComboBox(form, values=["NH3", "CO2", "R290", "R134a",
                                                    "Wasser/Glykol", "Sonstiges"],
                                       height=36, font=("Segoe UI", 13))
        self.medium.pack(fill="x")
        self.medium.set(zentrale.medium if zentrale else "NH3")
        add("Leistung (kW)", "leistung_kw")
        add("Temperatur (°C)", "temperatur_c")
        add("Notizen", "notizen")

        if zentrale is not None:
            self.entries["bezeichnung"].insert(0, zentrale.bezeichnung)
            self.entries["leistung_kw"].insert(0, f"{zentrale.leistung_kw:g}")
            self.entries["temperatur_c"].insert(0, f"{zentrale.temperatur_c:g}")
            self.entries["notizen"].insert(0, zentrale.notizen)

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=32, pady=(16, 20))
        widgets.ghost_button(btns, "Abbrechen", self.destroy, width=140).pack(side="left")
        widgets.primary_button(btns, "Übernehmen", self._save, width=170).pack(side="right")

    def _save(self):
        z = self.source or Zentrale()
        z.bezeichnung = self.entries["bezeichnung"].get().strip()
        if not z.bezeichnung:
            messagebox.showwarning("Pflichtfeld", "Bitte eine Bezeichnung eingeben.",
                                   parent=self)
            return
        z.medium = self.medium.get()
        z.notizen = self.entries["notizen"].get().strip()
        for key in ("leistung_kw", "temperatur_c"):
            raw = self.entries[key].get().strip().replace(",", ".")
            try:
                setattr(z, key, float(raw))
            except ValueError:
                setattr(z, key, 0.0)
        self.result = z
        self.destroy()


class FuellmengeDialog(ctk.CTkToplevel):
    def __init__(self, parent, fuellmenge=None):
        super().__init__(parent)
        self.title("Füllmenge anlegen" if fuellmenge is None else "Füllmenge bearbeiten")
        self.geometry("560x440")
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        self.source = fuellmenge

        ctk.CTkLabel(self, text="Füllmenge", font=("Segoe UI", 20, "bold"),
                     text_color=config.COLORS["primary"]).pack(pady=(16, 2))
        ctk.CTkLabel(self, text="Füllmengen des Projekts erfassen.",
                     font=("Segoe UI", 12),
                     text_color=config.COLORS["muted"]).pack(pady=(0, 10))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=32)
        self.entries = {}

        def add(label, key):
            field_label(form, label).pack(fill="x", pady=(8, 2))
            entry = ctk.CTkEntry(form, height=36, font=("Segoe UI", 13))
            entry.pack(fill="x")
            self.entries[key] = entry

        add("Medium *", "medium")
        add("Menge (kg)", "menge_kg")
        add("Ort / Raum", "ort")
        add("Notizen", "notizen")

        if fuellmenge is not None:
            self.entries["medium"].insert(0, fuellmenge.medium)
            self.entries["menge_kg"].insert(0, f"{fuellmenge.menge_kg:g}")
            self.entries["ort"].insert(0, fuellmenge.ort)
            self.entries["notizen"].insert(0, fuellmenge.notizen)

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=32, pady=(16, 20))
        widgets.ghost_button(btns, "Abbrechen", self.destroy, width=140).pack(side="left")
        widgets.primary_button(btns, "Übernehmen", self._save, width=170).pack(side="right")

    def _save(self):
        f = self.source or Fuellmenge()
        f.medium = self.entries["medium"].get().strip()
        if not f.medium:
            messagebox.showwarning("Pflichtfeld", "Bitte ein Medium eingeben.",
                                   parent=self)
            return
        f.ort = self.entries["ort"].get().strip()
        f.notizen = self.entries["notizen"].get().strip()
        raw = self.entries["menge_kg"].get().strip().replace(",", ".")
        try:
            f.menge_kg = float(raw)
        except ValueError:
            f.menge_kg = 0.0
        self.result = f
        self.destroy()


class RaumtypenDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_change=None):
        super().__init__(parent)
        self.title("Raumtypen verwalten")
        self.geometry("440x480")
        self.resizable(False, False)
        self.grab_set()
        self.on_change = on_change

        ctk.CTkLabel(self, text="Raumtypen", font=("Segoe UI", 20, "bold"),
                     text_color=config.COLORS["primary"]).pack(pady=(16, 2))
        ctk.CTkLabel(self, text="Diese Typen stehen im Raumformular zur Auswahl.\n"
                                "Die Liste ist beliebig erweiterbar.",
                     font=("Segoe UI", 12), justify="left",
                     text_color=config.COLORS["muted"]).pack(pady=(0, 10))

        self.listbox = ctk.CTkTextbox(self, height=240, font=("Segoe UI", 13))
        self.listbox.pack(fill="both", expand=True, padx=32)
        self.listbox.configure(state="normal")
        self._refresh()

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=32, pady=(10, 0))
        self.new_type = ctk.CTkEntry(row, height=36, placeholder_text="Neuer Raumtyp ...",
                                     font=("Segoe UI", 13))
        self.new_type.pack(side="left", fill="x", expand=True)
        self.new_type.bind("<Return>", lambda e: self._add())

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=32, pady=(10, 16))
        widgets.accent_button(btns, "Hinzufügen", self._add, width=150).pack(side="left")
        widgets.danger_button(btns, "Markierten löschen", self._remove, width=180).pack(
            side="left", padx=10)
        widgets.primary_button(btns, "Fertig", self.destroy, width=120).pack(side="right")

    def _selected(self):
        try:
            return self.listbox.get("sel.first", "sel.last").strip()
        except Exception:
            return ""

    def _refresh(self):
        self.listbox.configure(state="normal")
        self.listbox.delete("1.0", "end")
        for typ in storage.list_raumtypen():
            self.listbox.insert("end", typ + "\n")
        self.listbox.configure(state="disabled")

    def _add(self):
        name = self.new_type.get().strip()
        if not name:
            return
        if storage.add_raumtyp(name):
            self.new_type.delete(0, "end")
            if self.on_change:
                self.on_change()
        self._refresh()

    def _remove(self):
        selected = self._selected()
        if selected:
            storage.remove_raumtyp(selected)
            if self.on_change:
                self.on_change()
        self._refresh()
