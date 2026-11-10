import traceback
import customtkinter as ctk
from tkinter import messagebox

from .. import config
from . import widgets
from .views import ProjectListView, RoomListView, SettingsView
from .dialogs import ProjectDialog, RoomDialog


class RaumbuchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        self.title("Raumbuch – powered by Eckert & Partner")
        self.geometry("1280x800")
        self.minsize(1100, 700)

        try:
            config.ensure_data_dirs()
        except PermissionError as exc:
            msg = str(exc)
            self.after(200, lambda: messagebox.showerror("Speicherproblem", msg))

        self.current_project = None
        self.active_nav = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, fg_color=config.COLORS["primary"],
                                    corner_radius=0, width=240)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        self.content = ctk.CTkFrame(self, fg_color=config.COLORS["bg_light"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._safe_show(self.show_projects)

    def report_callback_exception(self, exc, val, tb):
        text = "".join(traceback.format_exception(exc, val, tb))
        self._show_error(text)

    def _build_sidebar(self):
        logo_file = widgets.logo_path()
        top = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        top.pack(pady=(28, 8), padx=16, fill="x")
        if logo_file.exists():
            try:
                logo = ctk.CTkImage(light_image=ctk.Image.open(logo_file), size=(150, 75))
                ctk.CTkLabel(top, image=logo, text="").pack()
            except Exception:
                pass
        ctk.CTkLabel(self.sidebar, text="Raumbuch",
                     font=("Segoe UI", 24, "bold"),
                     text_color="#FFFFFF").pack(pady=(8, 0))
        ctk.CTkLabel(self.sidebar, text="powered by Eckert & Partner",
                     font=("Segoe UI", 12),
                     text_color=config.COLORS["accent"]).pack(pady=(2, 24))

        self.nav_buttons = {}
        for key, label in (("projects", "Meine Projekte"),
                            ("settings", "Einstellungen")):
            btn = ctk.CTkButton(self.sidebar, text=label, anchor="w", height=44,
                                fg_color="transparent",
                                hover_color=config.COLORS["primary_dark"],
                                corner_radius=10,
                                font=("Segoe UI", 14),
                                command=lambda k=key: self._on_nav(k))
            btn.pack(padx=16, pady=6, fill="x")
            self.nav_buttons[key] = btn

        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.pack(side="bottom", pady=16)
        ctk.CTkLabel(bottom, text="Version 1.0 – Projekt & Raum",
                     font=("Segoe UI", 11),
                     text_color="#8FB3C9").pack()

    def _on_nav(self, key: str):
        if key == "projects":
            if self.current_project:
                self._safe_show(lambda: self.show_rooms(self.current_project))
            else:
                self._safe_show(self.show_projects)
        elif key == "settings":
            self._safe_show(self.show_settings)

    def _highlight_nav(self, key: str):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=config.COLORS["primary_dark"])
            else:
                btn.configure(fg_color="transparent")

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _show_error(self, tb: str):
        try:
            log_path = config.ensure_data_dirs() / "raumbuch_fehler.log"
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(tb + "\n\n")
        except Exception:
            log_path = None
        self._clear_content()
        frame = ctk.CTkFrame(self.content, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(frame, text="⚠️ Diese Ansicht konnte nicht geladen werden",
                     font=("Segoe UI", 18, "bold"),
                     text_color=config.COLORS["danger"]).grid(
            row=0, column=0, sticky="w", padx=28, pady=(24, 4))
        ctk.CTkLabel(frame, text="Bitte kopieren Sie den folgenden Text komplett "
                                  "und schicken Sie ihn weiter – daraus ist die "
                                  "Ursache exakt erkennbar.",
                     font=("Segoe UI", 12), text_color="#6B7B8A", justify="left").grid(
            row=1, column=0, sticky="w", padx=28)
        box = ctk.CTkTextbox(frame, font=("Consolas", 12), wrap="word")
        box.grid(row=2, column=0, sticky="nsew", padx=28, pady=12)
        box.insert("1.0", tb)
        if log_path:
            box.insert("end", f"\n\n(Gespeichert auch unter: {log_path})")
        box.configure(state="disabled")

    def _safe_show(self, builder):
        try:
            builder()
        except Exception:
            self._show_error(traceback.format_exc())

    def show_projects(self):
        self.current_project = None
        self._highlight_nav("projects")
        self._clear_content()
        ProjectListView(self.content, app=self).grid(row=0, column=0, sticky="nsew")

    def show_rooms(self, project):
        self._highlight_nav("projects")
        self._clear_content()
        RoomListView(self.content, app=self, project=project).grid(row=0, column=0, sticky="nsew")

    def show_settings(self):
        self._highlight_nav("settings")
        self._clear_content()
        SettingsView(self.content, app=self).grid(row=0, column=0, sticky="nsew")

    def _safe_dialog(self, fn):
        try:
            fn()
        except Exception:
            messagebox.showerror("Unerwarteter Fehler",
                                  "Es ist ein Fehler aufgetreten. "
                                  "Bitte kopieren Sie diesen Text und schicken Sie ihn weiter:\n\n"
                                  + traceback.format_exc())

    def edit_project(self, project=None):
        def run():
            dialog = ProjectDialog(self, project=project)
            self.wait_window(dialog)
            if dialog.result is not None:
                from .. import storage
                storage.save_project(dialog.result)
                self.current_project = dialog.result
                self._safe_show(lambda: self.show_rooms(dialog.result))
        self._safe_dialog(run)

    def refresh(self):
        if self.current_project:
            from .. import storage
            try:
                self.current_project = storage.load_project(self.current_project.id)
            except FileNotFoundError:
                self.current_project = None
                self._safe_show(self.show_projects)
                return
            self._safe_show(lambda: self.show_rooms(self.current_project))
        else:
            self._safe_show(self.show_projects)

    def open_room_dialog(self, project, room=None):
        def run():
            dialog = RoomDialog(self, room=room)
            self.wait_window(dialog)
            if dialog.result is not None:
                if room is None:
                    project.raeume.append(dialog.result)
                else:
                    idx = project.raeume.index(room)
                    project.raeume[idx] = dialog.result
                from .. import storage
                storage.save_project(project)
                self.refresh()
        self._safe_dialog(run)
