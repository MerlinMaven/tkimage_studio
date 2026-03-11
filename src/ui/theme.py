import tkinter as tk
from tkinter import ttk
from src.utils.constants import COLORS, FONTS


def setup_theme(root):
    style = ttk.Style(root)
    if 'clam' in style.theme_names():
        style.theme_use('clam')

    root.configure(bg=COLORS["bg_base"])
    C = COLORS

    # ═══════════════════════════════════════════════════════════
    # FRAMES
    # ═══════════════════════════════════════════════════════════
    style.configure("TFrame",          background=C["bg_base"])
    style.configure("Surface.TFrame",  background=C["bg_surface"])
    style.configure("Panel.TFrame",    background=C["bg_panel"])
    style.configure("Card.TFrame",     background=C["bg_panel_light"],
                    relief="flat")
    style.configure("Elevated.TFrame", background=C["bg_elevated"])
    style.configure("Border.TFrame",   background=C["border"])
    style.configure("Rail.TFrame",     background=C["bg_panel"])
    style.configure("Accent.TFrame",   background=C["accent"])

    # ═══════════════════════════════════════════════════════════
    # LABELS
    # ═══════════════════════════════════════════════════════════
    style.configure("TLabel",
                    background=C["bg_base"],
                    foreground=C["text_primary"],
                    font=FONTS["main"])

    style.configure("Panel.TLabel",
                    background=C["bg_panel"],
                    foreground=C["text_primary"],
                    font=FONTS["main"])

    style.configure("Card.TLabel",
                    background=C["bg_panel_light"],
                    foreground=C["text_primary"],
                    font=FONTS["main"])

    style.configure("CardMuted.TLabel",
                    background=C["bg_panel_light"],
                    foreground=C["text_secondary"],
                    font=FONTS["small"])

    style.configure("Header.TLabel",
                    background=C["bg_panel"],
                    foreground=C["text_secondary"],
                    font=FONTS["section"],
                    padding=(0, 8, 0, 2))

    style.configure("Status.TLabel",
                    background=C["bg_base"],
                    foreground=C["text_secondary"],
                    font=FONTS["small"])

    style.configure("StatusPanel.TLabel",
                    background=C["bg_panel_light"],
                    foreground=C["text_secondary"],
                    font=FONTS["small"])

    style.configure("Surface.TLabel",
                    background=C["bg_surface"],
                    foreground=C["text_secondary"],
                    font=FONTS["main"])

    # ═══════════════════════════════════════════════════════════
    # BUTTONS
    # ═══════════════════════════════════════════════════════════
    style.configure("TButton",
                    font=FONTS["main"],
                    background=C["bg_panel_light"],
                    foreground=C["text_primary"],
                    borderwidth=0, focusthickness=0,
                    padding=(14, 8))
    style.map("TButton",
              background=[("active",   C["bg_hover"]),
                          ("pressed",  C["accent"]),
                          ("disabled", C["bg_elevated"])],
              foreground=[("active",   C["text_primary"]),
                          ("pressed",  "#ffffff"),
                          ("disabled", C["text_muted"])])

    style.configure("Accent.TButton",
                    font=FONTS["header"],
                    background=C["accent"],
                    foreground="#ffffff",
                    borderwidth=0, focusthickness=0,
                    padding=(14, 8))
    style.map("Accent.TButton",
              background=[("active",   C["accent_hover"]),
                          ("disabled", C["bg_elevated"])],
              foreground=[("active",   "#ffffff"),
                          ("disabled", C["text_muted"])])

    style.configure("Ghost.TButton",
                    font=FONTS["main"],
                    background=C["bg_panel"],
                    foreground=C["text_muted"],
                    borderwidth=0, focusthickness=0,
                    padding=(6, 4))
    style.map("Ghost.TButton",
              background=[("active", C["bg_panel_light"])],
              foreground=[("active", C["text_primary"])])

    style.configure("Tool.TButton",
                    font=FONTS["main"],
                    background=C["bg_panel"],
                    foreground=C["text_secondary"],
                    borderwidth=0, focusthickness=0,
                    padding=(12, 7))
    style.map("Tool.TButton",
              background=[("active",  C["bg_panel_light"]),
                          ("pressed", C["accent_soft"])],
              foreground=[("active",  C["text_primary"]),
                          ("pressed", C["accent"])])

    style.configure("Nav.TButton",
                    font=FONTS["small"],
                    background=C["bg_surface"],
                    foreground=C["text_secondary"],
                    borderwidth=0, focusthickness=0,
                    padding=(12, 6))
    style.map("Nav.TButton",
              background=[("active",   C["bg_hover"]),
                          ("disabled", C["bg_surface"])],
              foreground=[("active",   C["text_primary"]),
                          ("disabled", C["text_muted"])])

    # ═══════════════════════════════════════════════════════════
    # SCROLLBAR
    # ═══════════════════════════════════════════════════════════
    style.configure("Vertical.TScrollbar",
                    background=C["bg_panel_light"],
                    troughcolor=C["bg_panel"],
                    bordercolor=C["bg_panel"],
                    arrowcolor=C["text_muted"],
                    width=7, relief="flat")
    style.map("Vertical.TScrollbar",
              background=[("active", C["bg_hover"])])

    # ═══════════════════════════════════════════════════════════
    # SCALE (slider)
    # ═══════════════════════════════════════════════════════════
    style.configure("Horizontal.TScale",
                    background=C["bg_surface"],
                    troughcolor=C["bg_elevated"],
                    slidercolor=C["accent"],
                    bordercolor=C["bg_surface"],
                    sliderlength=18,
                    sliderrelief="flat", troughrelief="flat")
    style.map("Horizontal.TScale",
              slidercolor=[("active", C["accent_hover"])])

    # ═══════════════════════════════════════════════════════════
    # COMBOBOX
    # ═══════════════════════════════════════════════════════════
    style.configure("TCombobox",
                    fieldbackground="#ffffff",
                    background="#ffffff",
                    foreground=C["text_primary"],
                    selectbackground=C["accent"],
                    selectforeground="#ffffff",
                    arrowcolor=C["text_secondary"],
                    font=FONTS["main"],
                    padding=5)
    style.map("TCombobox",
              fieldbackground=[("readonly", "#ffffff")],
              foreground=[("readonly", C["text_primary"])])
    root.option_add("*TCombobox*Listbox.background", "#ffffff")
    root.option_add("*TCombobox*Listbox.foreground", C["text_primary"])
    root.option_add("*TCombobox*Listbox.selectBackground", C["accent"])

    # ═══════════════════════════════════════════════════════════
    # TREEVIEW
    # ═══════════════════════════════════════════════════════════
    style.configure("Explorer.Treeview",
                    background=C["bg_panel"],
                    foreground=C["text_primary"],
                    fieldbackground=C["bg_panel"],
                    font=FONTS["small"],
                    borderwidth=0, relief="flat",
                    rowheight=26)
    style.map("Explorer.Treeview",
              background=[("selected", C["accent_soft"])],
              foreground=[("selected", C["accent"])])
    style.configure("Explorer.Treeview.Heading",
                    background=C["bg_panel_light"],
                    foreground=C["text_secondary"])

    # ═══════════════════════════════════════════════════════════
    # PROGRESSBAR (confidence scores)
    # ═══════════════════════════════════════════════════════════
    style.configure("Accent.Horizontal.TProgressbar",
                    troughcolor=C["bg_elevated"],
                    background=C["accent"],
                    borderwidth=0,
                    lightcolor=C["accent"],
                    darkcolor=C["accent"])

    style.configure("Success.Horizontal.TProgressbar",
                    troughcolor=C["bg_elevated"],
                    background=C["success"],
                    borderwidth=0,
                    lightcolor=C["success"],
                    darkcolor=C["success"])

    style.configure("Warning.Horizontal.TProgressbar",
                    troughcolor=C["bg_elevated"],
                    background=C["warning"],
                    borderwidth=0,
                    lightcolor=C["warning"],
                    darkcolor=C["warning"])

    style.configure("Danger.Horizontal.TProgressbar",
                    troughcolor=C["bg_elevated"],
                    background=C["danger"],
                    borderwidth=0,
                    lightcolor=C["danger"],
                    darkcolor=C["danger"])

    # ═══════════════════════════════════════════════════════════
    # SEPARATOR / PANEDWINDOW
    # ═══════════════════════════════════════════════════════════
    style.configure("TSeparator", background=C["border"])
    style.configure("TPanedwindow",
                    background=C["border"],
                    sashwidth=2, sashpad=0)
