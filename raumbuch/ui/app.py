import traceback
import customtkinter as ctk
from tkinter import messagebox

from .. import config, storage
from . import widgets
from .dialogs import LoginFrame, ProjectDialog
from .views import (EinstellungenView, FuellmengenView, NoProjectView,
                    ProjektdatenView, RaeumeView, UebersichtView, ZentraleView)

NAV = [
    ("uebersicht", "Projektübersicht"),
    ("projektdaten", "1 · Projekt"),
    ("raeume", "2 · Raum"),
    ("zentrale", "3 · Zentrale"),
    ("fuellmengen", "4 · Füllmenge"),
    ("einstellungen", "Einstellungen"),
]

PROJECT_VIEWS = {"projektdaten", "raeume", "zentrale", "fuellmengen"}


class RaumbuchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        self.title("Raumbuch – powered by Eckert & Partner")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.current_user = None
        self.project = None
        self.project_file = None
        self.dirty = False
        self.nav_buttons = {}

        try:
            config.ensure_data_dirs()
        except PermissionError as exc:
            msg = str(exc)
            self.after(300, lambda: messagebox.showerror("Speicherproblem", msg))

        self._safe_show(self._show_login)

    def report_callback_exception(self, exc, val, tb):
        text = "".join(traceback.format_exception(exc, val, tb))
        self._show_error_in_window(text)

    def _show_error_in_window(self, text: str) -> None:
        try:
            log_path = config.ensure_data_dirs() / "raumbuch_fehler.log"
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(text + "\n\n")
        except Exception:
            log_path = None
        win = ctk.CTkToplevel(self)
        win.title("Fehler")
        win.geometry("760x480")
        win.grab_set()
        ctk.CTkLabel(win, text="⚠️ Es ist ein Fehler aufgetreten",
                     font=("Segoe UI", 18, "bold"),
                     text_color=config.COLORS["danger"]).pack(pady=(16, 4))
        ctk.CTkLabel(win, text="Bitte kopieren Sie den folgenden Text komplett "
                               "und schicken Sie ihn weiter.",
                     font=("Segoe UI", 12),
                     text_color=config.COLORS["muted"]).pack()
        box = ctk.CTkTextbox(win, font=("Consolas", 12), wrap="word")
        box.pack(fill="both", expand=True, padx=20, pady=12)
        box.insert("1.0", text)
        if log_path:
            box.insert("end", f"\n\n(Gespeichert auch unter: {log_path})")

    def _safe_show(self, builder):
        try:
            builder()
        except Exception:
            self._show_error_in_window(traceback.format_exc())

    def _clear(self):
        for child in self.winfo_children():
            child.destroy()

    def _show_login(self):
        self._clear()
        LoginFrame(self, on_success=self._on_login).pack(fill="both", expand=True)

    def _on_login(self, user):
        self.current_user = user
        self._safe_show(self._build_main)

    def _build_main(self):
        self._clear()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, fg_color=config.COLORS["sidebar"],
                                    corner_radius=0, width=240)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        self.content = ctk.CTkFrame(self, fg_color=config.COLORS["bg_light"],
                                    corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self._build_sidebar()
        self._build_topbar()
        self.view_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.view_frame.grid(row=1, column=0, sticky="nsew")
        self.show_uebersicht()

    def _build_sidebar(self):
        logo_file = widgets.logo_path()
        top = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        top.pack(pady=(24, 4), padx=16, fill="x")
        if logo_file.exists():
            try:
                from PIL import Image
                pil_logo = Image.open(logo_file)
                height = 88
                width = int(pil_logo.width / pil_logo.height * height)
                logo = ctk.CTkImage(light_image=pil_logo, size=(width, height))
                ctk.CTkLabel(top, image=logo, text="").pack()
            except Exception:
                pass
        ctk.CTkLabel(self.sidebar, text="Raumbuch", font=("Segoe UI", 24, "bold"),
                     text_color=config.COLORS["primary"]).pack(pady=(4, 0))
        ctk.CTkLabel(self.sidebar, text="powered by Eckert & Partner",
                     font=("Segoe UI", 12),
                     text_color=config.COLORS["muted"]).pack(pady=(2, 20))

        for key, label in NAV:
            btn = ctk.CTkButton(self.sidebar, text=label, anchor="w", height=42,
                                fg_color="transparent",
                                hover_color=config.COLORS["sidebar_hover"],
                                text_color=config.COLORS["primary"],
                                corner_radius=10, font=("Segoe UI", 14),
                                command=lambda k=key: self.show_view(k))
            btn.pack(padx=16, pady=5, fill="x")
            self.nav_buttons[key] = btn

        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.pack(side="bottom", pady=16, fill="x")
        if self.current_user:
            ctk.CTkLabel(bottom, text=f"Angemeldet:\n{self.current_user['name']}",
                         font=("Segoe UI", 11), justify="left",
                         text_color=config.COLORS["muted"]).pack(padx=20, anchor="w")
            ctk.CTkButton(bottom, text="Abmelden", height=32,
                          fg_color="transparent",
                          hover_color=config.COLORS["sidebar_hover"],
                          text_color=config.COLORS["danger"],
                          font=("Segoe UI", 12),
                          command=self._logout).pack(padx=16, pady=(6, 0), fill="x")

    def _build_topbar(self):
        self.topbar = ctk.CTkFrame(self.content, fg_color=config.COLORS["card"],
                                   corner_radius=0, height=64)
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.project_label = ctk.CTkLabel(self.topbar, text="",
                                          font=("Segoe UI", 14, "bold"),
                                          text_color=config.COLORS["primary"])
        self.project_label.pack(side="left", padx=24)
        widgets.ghost_button(self.topbar, "Speichern", self.speichern, width=130).pack(
            side="right", padx=(6, 16), pady=14)
        widgets.primary_button(self.topbar, "Speichern unter ...",
                               self.speichern_unter, width=170).pack(
            side="right", pady=14)

    def update_topbar(self):
        if not hasattr(self, "project_label"):
            return
        if self.project:
            text = f"{self.project.name or '(ohne Namen)'}  ·  {self.project.version or '-'}"
            if self.dirty:
                text += "  •"
            self.project_label.configure(text=text)
        else:
            self.project_label.configure(text="Kein Projekt geöffnet")

    def show_view(self, key):
        self._highlight_nav(key)
        for child in self.view_frame.winfo_children():
            child.destroy()
        if key in PROJECT_VIEWS and not self.project:
            NoProjectView(self.view_frame, self).pack(fill="both", expand=True)
            return
        builder = {
            "uebersicht": lambda: UebersichtView(self.view_frame, self),
            "projektdaten": lambda: ProjektdatenView(self.view_frame, self),
            "raeume": lambda: RaeumeView(self.view_frame, self),
            "zentrale": lambda: ZentraleView(self.view_frame, self),
            "fuellmengen": lambda: FuellmengenView(self.view_frame, self),
            "einstellungen": lambda: EinstellungenView(self.view_frame, self),
        }[key]
        self._safe_show(lambda: builder().pack(fill="both", expand=True))

    def show_uebersicht(self):
        self.show_view("uebersicht")

    def _highlight_nav(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=config.COLORS["card"])
            else:
                btn.configure(fg_color="transparent")

    def open_project(self, project, file_path=None):
        self.project = project
        self.project_file = file_path
        self.dirty = file_path is None
        self.update_topbar()
        self.show_view("projektdaten")

    def mark_dirty(self):
        self.dirty = True
        self.update_topbar()

    def speichern(self):
        if not self.project:
            messagebox.showinfo("Hinweis", "Es ist kein Projekt geöffnet.")
            return
        try:
            self.project_file = storage.save_project(self.project, self.project_file)
        except (PermissionError, OSError) as exc:
            messagebox.showerror("Fehler", f"Das Projekt konnte nicht gespeichert "
                                           f"werden:\n{exc}")
            return
        self.dirty = False
        self.update_topbar()
        messagebox.showinfo("Gespeichert",
                            f"Das Projekt wurde gespeichert unter:\n"
                            f"{self.project_file}")

    def speichern_unter(self):
        if not self.project:
            messagebox.showinfo("Hinweis", "Es ist kein Projekt geöffnet.")
            return
        dialog = ProjectDialog(self, project=self.project)
        self.wait_window(dialog)
        if dialog.result is None:
            return
        self.project = dialog.result
        self.project_file = None
        self.speichern()
        self.show_view("projektdaten")

    def _on_close(self):
        if self.dirty and self.project:
            answer = messagebox.askyesnocancel(
                "Änderungen speichern?",
                "Sie haben ungespeicherte Änderungen.\n\n"
                "Möchten Sie das Projekt vor dem Beenden speichern?")
            if answer is None:
                return
            if answer:
                try:
                    self.project_file = storage.save_project(self.project,
                                                             self.project_file)
                except (PermissionError, OSError):
                    messagebox.showerror("Fehler", "Speichern fehlgeschlagen – "
                                                   "das Programm bleibt geöffnet.")
                    return
        self.destroy()

    def _logout(self):
        if self.dirty and self.project:
            if not messagebox.askyesno("Abmelden",
                                        "Sie haben ungespeicherte Änderungen. "
                                        "Trotzdem abmelden?"):
                return
        self.project = None
        self.project_file = None
        self.dirty = False
        self._safe_show(self._show_login)
