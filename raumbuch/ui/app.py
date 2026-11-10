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
        self.show_projects()

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
                self.show_rooms(self.current_project)
            else:
                self.show_projects()
        elif key == "settings":
            self.show_settings()

    def _highlight_nav(self, key: str):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=config.COLORS["primary_dark"])
            else:
                btn.configure(fg_color="transparent")

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

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

    def edit_project(self, project=None):
        dialog = ProjectDialog(self, project=project)
        self.wait_window(dialog)
        if dialog.result is not None:
            from .. import storage
            storage.save_project(dialog.result)
            self.current_project = dialog.result
            self.show_rooms(dialog.result)

    def refresh(self):
        if self.current_project:
            from .. import storage
            try:
                self.current_project = storage.load_project(self.current_project.id)
                self.show_rooms(self.current_project)
            except FileNotFoundError:
                self.current_project = None
                self.show_projects()
        else:
            self.show_projects()

    def open_room_dialog(self, project, room=None):
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
