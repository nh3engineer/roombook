import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

from .. import config, storage, excel_io, pdf_io

from . import widgets
from .dialogs import (FuellmengeDialog, ProjectDialog, RaumtypenDialog,
                      RoomDialog, ZentraleDialog)


def export_excel(app):
    if not app.project:
        messagebox.showinfo("Hinweis", "Bitte öffnen Sie zuerst ein Projekt.")
        return
    default = f"{app.project.name or 'Projekt'}_{app.project.version or 'Auslegung'}.xlsx"
    path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                        initialfile=default,
                                        filetypes=[("Excel-Datei", "*.xlsx")])
    if not path:
        return
    try:
        excel_io.export_project(app.project, Path(path))
    except Exception as exc:
        messagebox.showerror("Fehler", f"Der Excel-Export ist fehlgeschlagen:\n{exc}")
        return
    messagebox.showinfo("Export", f"Die Excel-Datei wurde gespeichert unter:\n{path}")


def export_pdf(app):
    if not app.project:
        messagebox.showinfo("Hinweis", "Bitte öffnen Sie zuerst ein Projekt.")
        return
    default = f"{app.project.name or 'Projekt'}_{app.project.version or 'Auslegung'}.pdf"
    path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                        initialfile=default,
                                        filetypes=[("PDF-Datei", "*.pdf")])
    if not path:
        return
    try:
        pdf_io.export_project_pdf(app.project, Path(path))
    except Exception as exc:
        messagebox.showerror("Fehler", f"Der PDF-Export ist fehlgeschlagen:\n{exc}")
        return
    messagebox.showinfo("Export", f"Das PDF wurde gespeichert unter:\n{path}")


class NoProjectView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        inner = ctk.CTkFrame(self, fg_color=config.COLORS["card"], corner_radius=16,
                             border_width=1, border_color="#E7D5DC")
        inner.place(relx=0.5, rely=0.4, anchor="center")
        ctk.CTkLabel(inner, text="Kein Projekt geöffnet",
                     font=("Segoe UI", 20, "bold"),
                     text_color=config.COLORS["primary"]).pack(pady=(24, 6))
        ctk.CTkLabel(inner,
                     text="Bitte erstellen Sie ein neues Projekt oder öffnen Sie "
                          "eine bestehende Auslegung über die Projektübersicht.",
                     font=("Segoe UI", 13),
                     text_color=config.COLORS["muted"]).pack(pady=(0, 18), padx=30)
        widgets.primary_button(inner, "Zur Projektübersicht",
                               app.show_uebersicht, width=220).pack(pady=(0, 24))


class UebersichtView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 8))
        widgets.section_title(header, "Projektübersicht").pack(side="left")
        widgets.primary_button(header, "+ Neues Projekt", self._neu).pack(side="right")

        ctk.CTkLabel(self, text="Alle gespeicherten Projekte und Auslegungen "
                                "(jede Auslegung ist eine eigene Datei).",
                     font=("Segoe UI", 12),
                     text_color=config.COLORS["muted"]).grid(
            row=1, column=0, sticky="w", padx=28)

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.grid(row=2, column=0, sticky="nsew", padx=28, pady=12)
        wrap.grid_columnconfigure(0, weight=1)
        wrap.grid_rowconfigure(0, weight=1)

        self.tree = widgets.make_treeview(wrap, {
            "name": "Projekt", "version": "Auslegung", "kunde": "Kunde",
            "status": "Status", "raeume": "Räume", "volumen": "Volumen gesamt",
        }, height=16)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", lambda e: self._oeffnen())

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=28, pady=(4, 24))
        widgets.ghost_button(btns, "Öffnen", self._oeffnen).pack(side="left", padx=(0, 10))
        widgets.ghost_button(btns, "Löschen", self._loeschen).pack(side="left", padx=10)
        widgets.accent_button(btns, "Excel-Export (alle Projekte)",
                             self._excel_alle).pack(side="right")
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        self.items = []
        for path, project in storage.list_project_files():
            iid = self.tree.insert("", "end", values=(
                project.name or "(ohne Namen)", project.version or "-",
                project.kunde, project.planungsstand, len(project.raeume),
                f"{project.gesamtvolumen():.1f} m³"))
            self.items.append((iid, path))

    def _selected_path(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Hinweis", "Bitte wählen Sie zuerst ein Projekt aus.")
            return None
        for iid, path in self.items:
            if iid == sel[0]:
                return path
        return None

    def _neu(self):
        dialog = ProjectDialog(self, project=None)
        self.wait_window(dialog)
        if dialog.result is not None:
            self.app.open_project(dialog.result, file_path=None)

    def _oeffnen(self):
        path = self._selected_path()
        if not path:
            return
        try:
            project = storage.load_project(path)
        except Exception:
            messagebox.showerror("Fehler", "Das Projekt konnte nicht geöffnet werden.")
            return
        self.app.open_project(project, file_path=path)

    def _loeschen(self):
        path = self._selected_path()
        if not path:
            return
        if messagebox.askyesno("Löschen",
                               "Möchten Sie diese Auslegung wirklich endgültig löschen?"):
            storage.delete_project_file(path)
            self.refresh()

    def _excel_alle(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", initialfile="Projektuebersicht.xlsx",
            filetypes=[("Excel-Datei", "*.xlsx")])
        if not path:
            return
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Projekte"
        ws.append(["Projekt", "Auslegung", "Kunde", "Status", "Räume",
                   "Volumen gesamt (m³)"])
        for _, project in storage.list_project_files():
            ws.append([project.name, project.version, project.kunde,
                       project.planungsstand, len(project.raeume),
                       round(project.gesamtvolumen(), 2)])
        wb.save(path)
        messagebox.showinfo("Export", f"Die Übersicht wurde gespeichert unter:\n{path}")


class ProjektdatenView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        project = app.project
        self.grid_columnconfigure(0, weight=1)

        widgets.section_title(self, "Projekt – Projektdaten").grid(
            row=0, column=0, sticky="w", padx=28, pady=(24, 4))
        ctk.CTkLabel(self, text="Alle wichtigsten Daten zum Projekt. "
                                "Änderungen mit „Übernehmen“ sichern.",
                     font=("Segoe UI", 12),
                     text_color=config.COLORS["muted"]).grid(
            row=1, column=0, sticky="w", padx=28)

        card = ctk.CTkFrame(self, fg_color=config.COLORS["card"], corner_radius=14,
                            border_width=1, border_color="#E7D5DC")
        card.grid(row=2, column=0, sticky="ew", padx=28, pady=12)
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        self.entries = {}
        fields = [
            ("Projektname", "name", 0, 0), ("Projektnummer", "nummer", 0, 1),
            ("Auslegung / Version", "version", 1, 0), ("Kunde", "kunde", 1, 1),
            ("Adresse", "adresse", 2, 0), ("Bauvorhaben / Standort", "bauvorhaben", 2, 1),
            ("Ansprechpartner", "ansprechpartner", 3, 0),
            ("Bearbeiter", "bearbeiter", 3, 1),
            ("Datum", "datum", 4, 0), ("Planungsstand", "planungsstand", 4, 1),
        ]
        for label, key, row, col in fields:
            ctk.CTkLabel(card, text=label, font=("Segoe UI", 12), anchor="w",
                         text_color=config.COLORS["text_dark"]).grid(
                row=row * 2, column=col, sticky="ew", padx=(20, 10), pady=(8, 2))
            entry = ctk.CTkEntry(card, height=36, font=("Segoe UI", 13))
            entry.grid(row=row * 2 + 1, column=col, sticky="ew", padx=(20, 10))
            entry.insert(0, getattr(project, key))
            self.entries[key] = entry

        ctk.CTkLabel(card, text="Notizen", font=("Segoe UI", 12), anchor="w",
                     text_color=config.COLORS["text_dark"]).grid(
            row=10, column=0, columnspan=2, sticky="ew", padx=20, pady=(8, 2))
        self.notizen = ctk.CTkTextbox(card, height=80, font=("Segoe UI", 13))
        self.notizen.grid(row=11, column=0, columnspan=2, sticky="ew", padx=20)
        self.notizen.insert("1.0", project.notizen)

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=28, pady=(4, 24))
        widgets.primary_button(btns, "Übernehmen", self._uebernehmen, width=180).pack(
            side="left")
        widgets.accent_button(btns, "Als Excel exportieren", lambda: export_excel(self.app)).pack(
            side="right", padx=10)
        widgets.accent_button(btns, "Als PDF exportieren", lambda: export_pdf(self.app)).pack(
            side="right")

    def _uebernehmen(self):
        project = self.app.project
        for key, entry in self.entries.items():
            setattr(project, key, entry.get().strip())
        project.notizen = self.notizen.get("1.0", "end").strip()
        self.app.mark_dirty()
        self.app.update_topbar()
        messagebox.showinfo("Gespeichert",
                            "Die Projektdaten wurden übernommen.\n"
                            "Denken Sie an „Speichern“, um die Projektdatei zu sichern.")


class _ListView(ctk.CTkFrame):
    columns = {}
    title = ""
    hint = ""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 4))
        widgets.section_title(header, self.title).pack(side="left")
        widgets.primary_button(header, self.add_label, self._add).pack(side="right")

        ctk.CTkLabel(self, text=self.hint, font=("Segoe UI", 12),
                     text_color=config.COLORS["muted"]).grid(
            row=1, column=0, sticky="w", padx=28)

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.grid(row=2, column=0, sticky="nsew", padx=28, pady=12)
        wrap.grid_columnconfigure(0, weight=1)
        wrap.grid_rowconfigure(0, weight=1)
        self.tree = widgets.make_treeview(wrap, self.columns, height=14)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", lambda e: self._edit())

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=28, pady=(4, 24))
        widgets.ghost_button(btns, "Bearbeiten", self._edit).pack(side="left", padx=(0, 10))
        widgets.danger_button(btns, "Löschen", self._delete).pack(side="left", padx=10)
        widgets.accent_button(btns, "Als Excel exportieren",
                              lambda: export_excel(self.app)).pack(side="right", padx=10)
        widgets.accent_button(btns, "Als PDF exportieren",
                              lambda: export_pdf(self.app)).pack(side="right")
        self.refresh()

    def _selected_index(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Hinweis", "Bitte wählen Sie zuerst einen Eintrag aus.")
            return None
        return self.tree.index(sel[0])


class RaeumeView(_ListView):
    columns = {"nummer": "Nr.", "name": "Raum", "typ": "Raumtyp", "laenge": "L (m)",
               "breite": "B (m)", "hoehe": "H (m)", "volumen": "Volumen (m³)"}
    title = "Raum – Raumgeometrie"
    hint = ("Basisliste für alle Berechnungen: Länge, Breite, Höhe – "
            "Volumen wird automatisch berechnet.")
    add_label = "+ Neuer Raum"

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for room in self.app.project.raeume:
            self.tree.insert("", "end", values=(
                room.nummer, room.name, room.raumtyp,
                f"{room.laenge:g}", f"{room.breite:g}", f"{room.hoehe:g}",
                f"{room.volumen():.2f}"))
        self.tree.column("nummer", width=80)
        self.tree.column("name", width=180)
        self.tree.column("volumen", width=120)

    def _add(self):
        dialog = RoomDialog(self)
        self.wait_window(dialog)
        if dialog.result is not None:
            self.app.project.raeume.append(dialog.result)
            self.app.mark_dirty()
            self.refresh()

    def _edit(self):
        idx = self._selected_index()
        if idx is None:
            return
        dialog = RoomDialog(self, room=self.app.project.raeume[idx])
        self.wait_window(dialog)
        if dialog.result is not None:
            self.app.project.raeume[idx] = dialog.result
            self.app.mark_dirty()
            self.refresh()

    def _delete(self):
        idx = self._selected_index()
        if idx is None:
            return
        room = self.app.project.raeume[idx]
        if messagebox.askyesno("Löschen",
                               f"Möchten Sie den Raum '{room.name}' wirklich löschen?"):
            self.app.project.raeume.pop(idx)
            self.app.mark_dirty()
            self.refresh()


class ZentraleView(_ListView):
    columns = {"bezeichnung": "Bezeichnung", "medium": "Medium",
               "leistung": "Leistung (kW)", "temperatur": "Temperatur (°C)",
               "notizen": "Notizen"}
    title = "Zentrale – Kälteerzeugung"
    hint = "Auslegung der Kälteerzeugung / Zentrale des Projekts."
    add_label = "+ Neue Zentrale"

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for z in self.app.project.zentrale:
            self.tree.insert("", "end", values=(
                z.bezeichnung, z.medium, f"{z.leistung_kw:g}",
                f"{z.temperatur_c:g}", z.notizen))
        self.tree.column("bezeichnung", width=200)

    def _add(self):
        dialog = ZentraleDialog(self)
        self.wait_window(dialog)
        if dialog.result is not None:
            self.app.project.zentrale.append(dialog.result)
            self.app.mark_dirty()
            self.refresh()

    def _edit(self):
        idx = self._selected_index()
        if idx is None:
            return
        dialog = ZentraleDialog(self, zentrale=self.app.project.zentrale[idx])
        self.wait_window(dialog)
        if dialog.result is not None:
            self.app.project.zentrale[idx] = dialog.result
            self.app.mark_dirty()
            self.refresh()

    def _delete(self):
        idx = self._selected_index()
        if idx is None:
            return
        z = self.app.project.zentrale[idx]
        if messagebox.askyesno("Löschen",
                               f"Möchten Sie '{z.bezeichnung}' wirklich löschen?"):
            self.app.project.zentrale.pop(idx)
            self.app.mark_dirty()
            self.refresh()


class FuellmengenView(_ListView):
    columns = {"medium": "Medium", "menge": "Menge (kg)", "ort": "Ort / Raum",
               "notizen": "Notizen"}
    title = "Füllmenge"
    hint = "Füllmengen des Projekts erfassen und zusammenfassen."
    add_label = "+ Neue Füllmenge"

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for f in self.app.project.fuellmengen:
            self.tree.insert("", "end", values=(
                f.medium, f"{f.menge_kg:g}", f.ort, f.notizen))
        self.tree.column("medium", width=160)

    def _add(self):
        dialog = FuellmengeDialog(self)
        self.wait_window(dialog)
        if dialog.result is not None:
            self.app.project.fuellmengen.append(dialog.result)
            self.app.mark_dirty()
            self.refresh()

    def _edit(self):
        idx = self._selected_index()
        if idx is None:
            return
        dialog = FuellmengeDialog(self, fuellmenge=self.app.project.fuellmengen[idx])
        self.wait_window(dialog)
        if dialog.result is not None:
            self.app.project.fuellmengen[idx] = dialog.result
            self.app.mark_dirty()
            self.refresh()

    def _delete(self):
        idx = self._selected_index()
        if idx is None:
            return
        f = self.app.project.fuellmengen[idx]
        if messagebox.askyesno("Löschen",
                               f"Möchten Sie '{f.medium}' wirklich löschen?"):
            self.app.project.fuellmengen.pop(idx)
            self.app.mark_dirty()
            self.refresh()


class EinstellungenView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        widgets.section_title(self, "Einstellungen").grid(
            row=0, column=0, sticky="w", padx=28, pady=(24, 4))

        card = ctk.CTkFrame(self, fg_color=config.COLORS["card"], corner_radius=14,
                            border_width=1, border_color="#E7D5DC")
        card.grid(row=1, column=0, sticky="ew", padx=28, pady=12)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Zentraler Datenordner",
                     font=("Segoe UI", 15, "bold"),
                     text_color=config.COLORS["primary"]).grid(
            row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        ctk.CTkLabel(card,
                     text="Alle Projekte, Auslegungen, Benutzer und Raumtypen werden "
                          "an diesem zentralen Ort gespeichert.",
                     font=("Segoe UI", 12),
                     text_color=config.COLORS["muted"], wraplength=600,
                     justify="left").grid(row=1, column=0, sticky="w", padx=20)

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", padx=20, pady=(8, 16))
        row.grid_columnconfigure(0, weight=1)
        settings = config.load_settings()
        self.dir_entry = ctk.CTkEntry(row, height=38, font=("Segoe UI", 13))
        self.dir_entry.insert(0, settings["datenordner"])
        self.dir_entry.grid(row=0, column=0, sticky="ew")
        widgets.ghost_button(row, "Durchsuchen ...", self._browse, width=140).grid(
            row=0, column=1, padx=(10, 0))

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=2, column=0, sticky="ew", padx=28, pady=12)
        widgets.primary_button(btns, "Speichern", self._save).pack(side="left")
        widgets.ghost_button(btns, "Ordner öffnen", self._open_folder).pack(
            side="left", padx=10)
        widgets.accent_button(btns, "Raumtypen verwalten", self._raumtypen).pack(
            side="left", padx=10)

    def _browse(self):
        selected = filedialog.askdirectory(
            initialdir=self.dir_entry.get() or str(Path.home()))
        if selected:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, selected)

    def _save(self):
        settings = config.load_settings()
        settings["datenordner"] = self.dir_entry.get().strip()
        try:
            config.save_settings(settings)
            config.ensure_data_dirs()
        except (PermissionError, OSError) as exc:
            messagebox.showerror("Fehler", str(exc))
            return
        messagebox.showinfo("Gespeichert", "Der Datenordner wurde gespeichert.")

    def _open_folder(self):
        path = Path(self.dir_entry.get().strip())
        if not path.exists():
            messagebox.showinfo("Hinweis", "Der Ordner existiert noch nicht.")
            return
        config.open_in_explorer(path)

    def _raumtypen(self):
        RaumtypenDialog(self)
