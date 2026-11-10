import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path

from .. import config, storage, excel_io, calculation
from . import widgets


class ProjectListView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 12))
        widgets.section_title(header, "Meine Projekte").pack(side="left")
        widgets.primary_button(header, "+ Neues Projekt",
                               lambda: app.edit_project(None)).pack(side="right")

        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=28, pady=(70, 0))
        self.search = ctk.CTkEntry(search_frame, placeholder_text="🔍  Projekt suchen ...",
                                   height=38, font=("Segoe UI", 13))
        self.search.pack(side="left", fill="x", expand=True)
        self.search.bind("<KeyRelease>", lambda e: self.refresh_list())

        self.show_archived = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(search_frame, text="Archivierte anzeigen",
                        variable=self.show_archived,
                        command=self.refresh_list).pack(side="right", padx=(16, 0))

        table_wrap = ctk.CTkFrame(self, fg_color="transparent")
        table_wrap.grid(row=1, column=0, sticky="nsew", padx=28, pady=12)
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)

        self.tree = widgets.make_treeview(table_wrap, {
            "name": "Projekt", "nummer": "Nr.", "kunde": "Kunde",
            "bauvorhaben": "Bauvorhaben", "planungsstand": "Status",
            "raeume": "Räume", "leistung": "Kälteleistung",
        }, height=16)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", lambda e: self.open_selected())

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=2, column=0, sticky="ew", padx=28, pady=(4, 24))
        widgets.ghost_button(btns, "Öffnen", self.open_selected).pack(side="left", padx=(0, 10))
        widgets.ghost_button(btns, "Bearbeiten", self.edit_selected).pack(side="left", padx=10)
        widgets.accent_button(btns, "Archivieren / Aktivieren", self.toggle_archive).pack(side="left", padx=10)
        widgets.ghost_button(btns, "Exportieren", self.export_selected).pack(side="left", padx=10)
        widgets.ghost_button(btns, "Importieren", self.import_project).pack(side="left", padx=10)
        widgets.danger_button(btns, "Löschen", self.delete_selected).pack(side="right")

        self.refresh_list()

    def selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        term = self.search.get().strip().lower()
        for p in storage.list_projects(include_archived=self.show_archived.get()):
            text = " ".join([p.name, p.nummer, p.kunde, p.bauvorhaben]).lower()
            if term and term not in text:
                continue
            status = "Archiviert" if p.archiviert else p.planungsstand
            self.tree.insert("", "end", iid=p.id, values=(
                p.name or "(ohne Namen)", p.nummer, p.kunde, p.bauvorhaben,
                status, len(p.raeume),
                f"{p.gesamtleistung()/1000:.2f} kW",
            ))

    def open_selected(self):
        pid = self.selected_id()
        if not pid:
            messagebox.showinfo("Hinweis", "Bitte wählen Sie zuerst ein Projekt aus.")
            return
        project = storage.load_project(pid)
        self.app.current_project = project
        self.app.show_rooms(project)

    def edit_selected(self):
        pid = self.selected_id()
        if not pid:
            messagebox.showinfo("Hinweis", "Bitte wählen Sie zuerst ein Projekt aus.")
            return
        self.app.edit_project(storage.load_project(pid))
        self.refresh_list()

    def toggle_archive(self):
        pid = self.selected_id()
        if not pid:
            messagebox.showinfo("Hinweis", "Bitte wählen Sie zuerst ein Projekt aus.")
            return
        project = storage.load_project(pid)
        project.archiviert = not project.archiviert
        storage.save_project(project)
        self.refresh_list()

    def export_selected(self):
        pid = self.selected_id()
        if not pid:
            messagebox.showinfo("Hinweis", "Bitte wählen Sie zuerst ein Projekt aus.")
            return
        project = storage.load_project(pid)
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"{project.name or 'projekt'}.raumbuch.json",
            filetypes=[("Raumbuch-Projekt", "*.json")])
        if path:
            storage.export_project(project, Path(path))
            messagebox.showinfo("Export", f"Das Projekt wurde gespeichert unter:\n{path}")

    def import_project(self):
        path = filedialog.askopenfilename(filetypes=[("Raumbuch-Projekt", "*.json")])
        if not path:
            return
        try:
            project = storage.import_project(Path(path))
        except Exception:
            messagebox.showerror("Fehler", "Die Datei konnte nicht gelesen werden. "
                                           "Handelt es sich um eine Raumbuch-Exportdatei?")
            return
        storage.save_project(project)
        self.refresh_list()
        messagebox.showinfo("Import", f"Das Projekt '{project.name}' wurde importiert.")

    def delete_selected(self):
        pid = self.selected_id()
        if not pid:
            messagebox.showinfo("Hinweis", "Bitte wählen Sie zuerst ein Projekt aus.")
            return
        project = storage.load_project(pid)
        if messagebox.askyesno("Projekt löschen",
                               f"Möchten Sie das Projekt '{project.name}' wirklich endgültig löschen?\n"
                               "Diese Aktion kann nicht rückgängig gemacht werden."):
            storage.delete_project(pid)
            self.refresh_list()


class RoomListView(ctk.CTkFrame):
    def __init__(self, parent, app, project):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.project = project
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 8))
        widgets.ghost_button(header, "← Zurück", app.show_projects, width=110).pack(side="left")
        title = f"{project.name or '(ohne Namen)'}"
        if project.nummer:
            title += f"  ·  {project.nummer}"
        widgets.section_title(header, title).pack(side="left", padx=16)
        widgets.primary_button(header, "+ Neuer Raum",
                               lambda: app.open_room_dialog(project, None)).pack(side="right")

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="ew", padx=28, pady=(4, 8))
        for i in range(3):
            cards.grid_columnconfigure(i, weight=1)
        widgets.hero_card(cards, "Gesamtfläche", f"{project.gesamtflaeche():.1f} m²").grid(
            row=0, column=0, sticky="ew", padx=(0, 12))
        widgets.hero_card(cards, "Gesamtvolumen", f"{project.gesamtvolumen():.1f} m³").grid(
            row=0, column=1, sticky="ew", padx=6)
        widgets.hero_card(cards, "Kälteleistung gesamt",
                          f"{project.gesamtleistung()/1000:.2f} kW").grid(
            row=0, column=2, sticky="ew", padx=(12, 0))

        table_wrap = ctk.CTkFrame(self, fg_color="transparent")
        table_wrap.grid(row=2, column=0, sticky="nsew", padx=28, pady=8)
        table_wrap.grid_columnconfigure(0, weight=1)
        table_wrap.grid_rowconfigure(0, weight=1)

        self.tree = widgets.make_treeview(table_wrap, {
            "nummer": "Nr.", "name": "Raum", "typ": "Typ",
            "flaeche": "Fläche", "volumen": "Volumen",
            "soll": "Soll °C", "delta": "ΔT",
            "leistung": "Kälteleistung",
        }, height=12)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())
        self.tree.column("nummer", width=90)
        self.tree.column("name", width=180)
        self.tree.column("flaeche", width=100)
        self.tree.column("volumen", width=100)
        self.tree.column("leistung", width=140)

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=28, pady=(4, 24))
        widgets.ghost_button(btns, "Bearbeiten", self.edit_selected).pack(side="left", padx=(0, 10))
        widgets.ghost_button(btns, "Duplizieren", self.duplicate_selected).pack(side="left", padx=10)
        widgets.danger_button(btns, "Löschen", self.delete_selected).pack(side="left", padx=10)
        widgets.accent_button(btns, "Excel-Vorlage erstellen", self.create_template).pack(
            side="right", padx=(10, 0))
        widgets.accent_button(btns, "Excel-Import", self.import_excel).pack(
            side="right", padx=(10, 0))
        widgets.ghost_button(btns, "Als Excel exportieren", self.export_excel).pack(
            side="right", padx=10)

        self.refresh_list()

    def selected_index(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.index(sel[0])

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        for i, room in enumerate(self.project.raeume):
            res = calculation.berechne_kaelteleistung(room)
            self.tree.insert("", "end", iid=str(i), values=(
                room.nummer, room.name, room.raumtyp,
                f"{res['flaeche']:.2f} m²", f"{res['volumen']:.2f} m³",
                f"{room.solltemperatur:.1f}", f"{res['delta_t']:.1f} K",
                f"{res['gesamt']:.0f} W",
            ))

    def edit_selected(self):
        idx = self.selected_index()
        if idx is None:
            messagebox.showinfo("Hinweis", "Bitte wählen Sie zuerst einen Raum aus.")
            return
        self.app.open_room_dialog(self.project, self.project.raeume[idx])

    def duplicate_selected(self):
        idx = self.selected_index()
        if idx is None:
            messagebox.showinfo("Hinweis", "Bitte wählen Sie zuerst einen Raum aus.")
            return
        from ..models import Room
        copy = Room.from_dict(self.project.raeume[idx].to_dict())
        copy.nummer = (copy.nummer or "R") + "-KOPIE"
        copy.name = copy.name + " (Kopie)"
        self.project.raeume.append(copy)
        storage.save_project(self.project)
        self.app.refresh()

    def delete_selected(self):
        idx = self.selected_index()
        if idx is None:
            messagebox.showinfo("Hinweis", "Bitte wählen Sie zuerst einen Raum aus.")
            return
        room = self.project.raeume[idx]
        if messagebox.askyesno("Raum löschen",
                               f"Möchten Sie den Raum '{room.name}' wirklich löschen?"):
            self.project.raeume.pop(idx)
            storage.save_project(self.project)
            self.app.refresh()

    def create_template(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile="Raumbuch_Vorlage.xlsx",
            filetypes=[("Excel-Datei", "*.xlsx")])
        if not path:
            return
        try:
            excel_io.create_template(Path(path))
        except Exception as exc:
            messagebox.showerror("Fehler", f"Die Vorlage konnte nicht erstellt werden:\n{exc}")
            return
        messagebox.showinfo("Vorlage erstellt",
                            f"Die Excel-Vorlage wurde gespeichert unter:\n{path}\n\n"
                            "Füllen Sie sie aus und importieren Sie sie dann über 'Excel-Import'.")

    def import_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel-Datei", "*.xlsx")])
        if not path:
            return
        try:
            rooms, errors = excel_io.import_rooms(Path(path))
        except Exception as exc:
            messagebox.showerror("Fehler", f"Die Datei konnte nicht gelesen werden:\n{exc}")
            return
        if errors:
            messagebox.showwarning("Import mit Hinweisen",
                                   "Folgende Zeilen wurden übersprungen:\n\n" + "\n".join(errors))
        if rooms:
            self.project.raeume.extend(rooms)
            storage.save_project(self.project)
            self.app.refresh()
            messagebox.showinfo("Import abgeschlossen",
                                f"{len(rooms)} Raum/Räume wurden erfolgreich importiert.")

    def export_excel(self):
        if not self.project.raeume:
            messagebox.showinfo("Hinweis", "Dieses Projekt enthält noch keine Räume.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=f"{self.project.name or 'Raeume'}.xlsx",
            filetypes=[("Excel-Datei", "*.xlsx")])
        if not path:
            return
        try:
            excel_io.export_rooms(self.project.raeume, Path(path))
        except Exception as exc:
            messagebox.showerror("Fehler", f"Der Export ist fehlgeschlagen:\n{exc}")
            return
        messagebox.showinfo("Export", f"Die Raumliste wurde gespeichert unter:\n{path}")


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        widgets.section_title(self, "Einstellungen").grid(
            row=0, column=0, sticky="w", padx=28, pady=(24, 4))

        card = ctk.CTkFrame(self, fg_color=config.COLORS["card"], corner_radius=14,
                            border_width=1, border_color=config.COLORS["accent_soft"])
        card.grid(row=1, column=0, sticky="ew", padx=28, pady=12)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Zentraler Datenordner",
                     font=("Segoe UI", 15, "bold"),
                     text_color=config.COLORS["primary"]).grid(
            row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        ctk.CTkLabel(card,
                     text="Alle Projekte werden an diesem zentralen Ort gespeichert – ideal für Backups oder die Nutzung auf mehreren Rechnern.",
                     font=("Segoe UI", 12), text_color="#6B7B8A", wraplength=600,
                     justify="left").grid(row=1, column=0, sticky="w", padx=20)

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", padx=20, pady=(8, 16))
        row.grid_columnconfigure(0, weight=1)
        settings = config.load_settings()
        self.dir_entry = ctk.CTkEntry(row, height=38, font=("Segoe UI", 13))
        self.dir_entry.insert(0, settings["datenordner"])
        self.dir_entry.grid(row=0, column=0, sticky="ew")
        widgets.ghost_button(row, "Durchsuchen ...", self.browse, width=140).grid(
            row=0, column=1, padx=(10, 0))

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=2, column=0, sticky="w", padx=28, pady=12)
        widgets.primary_button(btns, "Speichern", self.save).pack(side="left")
        widgets.ghost_button(btns, "Ordner öffnen", self.open_folder).pack(
            side="left", padx=10)

        info = ctk.CTkLabel(self, text="Raumbuch 1.0 · Eckert & Partner Kälteplanung",
                            text_color="#8A9AA8", font=("Segoe UI", 12))
        info.grid(row=3, column=0, sticky="w", padx=28, pady=(20, 10))

    def browse(self):
        selected = filedialog.askdirectory(initialdir=self.dir_entry.get() or str(Path.home()))
        if selected:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, selected)

    def save(self):
        settings = config.load_settings()
        settings["datenordner"] = self.dir_entry.get().strip()
        try:
            config.save_settings(settings)
            config.ensure_data_dirs()
        except (PermissionError, OSError) as exc:
            messagebox.showerror("Fehler", str(exc))
            return
        messagebox.showinfo("Gespeichert", "Der Datenordner wurde gespeichert.\n"
                                          "Alle Projekte liegen ab jetzt zentral dort.")

    def open_folder(self):
        from .. import config as cfg
        path = Path(self.dir_entry.get().strip())
        if not path.exists():
            messagebox.showinfo("Hinweis", "Der Ordner existiert noch nicht. "
                                           "Speichern Sie zuerst die Einstellungen.")
            return
        cfg.open_in_explorer(path)
