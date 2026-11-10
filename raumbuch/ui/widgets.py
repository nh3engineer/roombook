import customtkinter as ctk
from tkinter import ttk
from pathlib import Path

from .. import config

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def logo_path() -> Path:
    return ASSETS_DIR / config.LOGO_FILE


def make_treeview(parent, columns: dict, height: int = 14) -> ttk.Treeview:
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Raumbuch.Treeview",
                    background="#FFFFFF",
                    foreground=config.COLORS["text_dark"],
                    rowheight=30,
                    fieldbackground="#FFFFFF",
                    bordercolor=config.COLORS["accent_soft"],
                    font=("Segoe UI", 11))
    style.configure("Raumbuch.Treeview.Heading",
                    background=config.COLORS["primary"],
                    foreground="#FFFFFF",
                    font=("Segoe UI", 11, "bold"),
                    relief="flat")
    style.map("Raumbuch.Treeview",
              background=[("selected", config.COLORS["accent_soft"])],
              foreground=[("selected", config.COLORS["text_dark"])])
    style.map("Raumbuch.Treeview.Heading", background=[("active", config.COLORS["primary_dark"])])

    tree = ttk.Treeview(parent, columns=list(columns.keys()), show="headings", height=height,
                        style="Raumbuch.Treeview")
    for col_id, title in columns.items():
        tree.heading(col_id, text=title)
        tree.column(col_id, width=120, anchor="w")
    return tree


def hero_card(parent, title: str, value: str) -> ctk.CTkFrame:
    card = ctk.CTkFrame(parent, fg_color=config.COLORS["card"],
                        corner_radius=14, border_width=1,
                        border_color=config.COLORS["accent_soft"])
    ctk.CTkLabel(card, text=title, text_color=config.COLORS["muted"],
                 font=("Segoe UI", 12)).pack(pady=(14, 2), padx=24)
    ctk.CTkLabel(card, text=value, text_color=config.COLORS["primary"],
                 font=("Segoe UI", 24, "bold")).pack(pady=(0, 14), padx=24)
    return card


def section_title(parent, text: str) -> ctk.CTkLabel:
    return ctk.CTkLabel(parent, text=text, text_color=config.COLORS["primary"],
                        font=("Segoe UI", 18, "bold"))


def primary_button(parent, text: str, command, width: int = 180) -> ctk.CTkButton:
    return ctk.CTkButton(parent, text=text, command=command, width=width, height=38,
                          fg_color=config.COLORS["primary"],
                          hover_color=config.COLORS["primary_dark"],
                          font=("Segoe UI", 13, "bold"), corner_radius=10)


def accent_button(parent, text: str, command, width: int = 180) -> ctk.CTkButton:
    return ctk.CTkButton(parent, text=text, command=command, width=width, height=38,
                         fg_color=config.COLORS["accent"],
                         hover_color="#D98BA0",
                         text_color=config.COLORS["primary"],
                         font=("Segoe UI", 13, "bold"), corner_radius=10)


def ghost_button(parent, text: str, command, width: int = 180) -> ctk.CTkButton:
    return ctk.CTkButton(parent, text=text, command=command, width=width, height=38,
                         fg_color=config.COLORS["card"],
                         hover_color=config.COLORS["accent_soft"],
                         text_color=config.COLORS["primary"],
                         border_width=1, border_color=config.COLORS["accent"],
                         font=("Segoe UI", 13), corner_radius=10)


def danger_button(parent, text: str, command, width: int = 180) -> ctk.CTkButton:
    return ctk.CTkButton(parent, text=text, command=command, width=width, height=38,
                         fg_color=config.COLORS["danger"],
                         hover_color="#8E2E24",
                         font=("Segoe UI", 13, "bold"), corner_radius=10)
