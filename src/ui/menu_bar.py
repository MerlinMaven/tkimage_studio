import tkinter as tk
from src.utils.constants import COLORS, FONTS


def _safe(callbacks, key, *args):
    fn = callbacks.get(key)
    if fn:
        fn(*args)


class MenuBar(tk.Menu):
    def __init__(self, parent, callbacks=None):

        theme_config = {
            "bg": COLORS["bg_panel"],
            "fg": COLORS["text_primary"],
            "activebackground": COLORS["accent"],
            "activeforeground": "#ffffff",
            "activeborderwidth": 0,
            "borderwidth": 0,
            "font": FONTS["main"],
            "relief": "flat"
        }

        super().__init__(parent, **theme_config)
        self.callbacks = callbacks or {}
        cb = self.callbacks

        # --- Menu Fichier ---
        self.file_menu = tk.Menu(self, tearoff=0, **theme_config)
        self.file_menu.add_command(label="  Ouvrir image\u2026", accelerator="Ctrl+O",
                                   command=cb.get("open_image"))
        self.file_menu.add_command(label="  Ouvrir dossier\u2026",
                                   command=cb.get("open_folder"))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="  Enregistrer", accelerator="Ctrl+S",
                                   command=cb.get("save_image"))
        self.file_menu.add_command(label="  Enregistrer sous\u2026", accelerator="Ctrl+Shift+S",
                                   command=cb.get("save_image_as"))
        self.file_menu.add_command(label="  Exporter annotations\u2026",
                                   command=cb.get("export_annotations"))
        self.file_menu.add_command(label="\U0001F4E6  Exporter dataset ML\u2026",
                                   command=cb.get("export_dataset"))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="\U0001F4CB  Rapport de session",
                                   command=cb.get("generate_report"))
        self.file_menu.add_command(label="\U0001F4BE  Exporter le rapport (.txt)",
                                   command=cb.get("export_report"))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="  Quitter", command=parent.quit)
        self.add_cascade(label="Fichier", menu=self.file_menu)

        # --- Menu \u00c9dition ---
        self.edit_menu = tk.Menu(self, tearoff=0, **theme_config)
        self.edit_menu.add_command(label="  Annuler", accelerator="Ctrl+Z",
                                   command=cb.get("undo"))
        self.edit_menu.add_command(label="  R\u00e9tablir", accelerator="Ctrl+Y",
                                   command=cb.get("redo"))
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="  Supprimer de la session",
                                   command=cb.get("remove_from_session"))
        self.edit_menu.add_command(label="  R\u00e9initialiser l\u2019image", accelerator="Ctrl+R",
                                   command=cb.get("reset_image"))
        self.add_cascade(label="\u00c9dition", menu=self.edit_menu)

        # --- Menu Vue ---
        self.view_menu = tk.Menu(self, tearoff=0, **theme_config)
        self.view_menu.add_command(label="  Panneau Outils",
                                   command=cb.get("toggle_left_toolbar"))
        self.view_menu.add_command(label="  Explorateur de fichiers",
                                   command=cb.get("toggle_file_explorer"))
        self.view_menu.add_command(label="  Panneau Propri\u00e9t\u00e9s / IA",
                                   command=cb.get("toggle_right_panel"))
        self.add_cascade(label="Vue", menu=self.view_menu)

        # --- Menu Filtres ---
        self.filter_menu = tk.Menu(self, tearoff=0, **theme_config)
        self.filter_menu.add_command(label="  Niveaux de gris",
                                     command=lambda: _safe(cb, "apply_filter", "grayscale"))
        self.filter_menu.add_command(label="  Flou",
                                     command=lambda: _safe(cb, "apply_filter", "blur"))
        self.filter_menu.add_command(label="  Nettet\u00e9",
                                     command=lambda: _safe(cb, "apply_filter", "sharpen"))
        self.filter_menu.add_command(label="  Contraste",
                                     command=lambda: _safe(cb, "apply_filter", "contrast"))
        self.filter_menu.add_command(label="  Luminosit\u00e9",
                                     command=lambda: _safe(cb, "apply_filter", "brightness"))
        self.filter_menu.add_command(label="  Inversion",
                                     command=lambda: _safe(cb, "apply_filter", "invert"))
        self.filter_menu.add_command(label="  Autocontraste",
                                     command=lambda: _safe(cb, "apply_filter", "autocontrast"))
        self.filter_menu.add_separator()
        self.filter_menu.add_command(label="  D\u00e9tection de contours",
                                     command=lambda: _safe(cb, "apply_filter", "edge_detect"))
        self.filter_menu.add_command(label="  Relief (Emboss)",
                                     command=lambda: _safe(cb, "apply_filter", "emboss"))
        self.add_cascade(label="Filtres", menu=self.filter_menu)

        # --- Menu Segmentation ---
        self.seg_menu = tk.Menu(self, tearoff=0, **theme_config)
        self.seg_menu.add_command(label="  Seuillage simple",
                                  command=lambda: _safe(cb, "apply_segmentation", "threshold"))
        self.seg_menu.add_command(label="  Masque binaire",
                                  command=lambda: _safe(cb, "apply_segmentation", "binary_mask"))
        self.seg_menu.add_command(label="  Extraction d\u2019une zone",
                                  command=lambda: _safe(cb, "apply_segmentation", "extract_zone"))
        self.add_cascade(label="Segmentation", menu=self.seg_menu)

        # --- Menu Visualisation 3D ---
        self.vis3d_menu = tk.Menu(self, tearoff=0, **theme_config)
        self.vis3d_menu.add_command(label="  Pseudo-visualisation 3D",
                                    command=lambda: _safe(cb, "apply_vis3d", "pseudo_3d"))
        self.vis3d_menu.add_command(label="  Empilement de coupes",
                                    command=lambda: _safe(cb, "apply_vis3d", "stack"))
        self.add_cascade(label="Visualisation 3D", menu=self.vis3d_menu)

        # --- Menu \u00c0 propos ---
        self.help_menu = tk.Menu(self, tearoff=0, **theme_config)
        self.help_menu.add_command(label="  Pr\u00e9sentation du projet",
                                   command=cb.get("show_presentation"))
        self.help_menu.add_command(label="  Version",
                                   command=cb.get("show_version"))
        self.help_menu.add_command(label="  Auteur",
                                   command=cb.get("show_author"))
        self.help_menu.add_separator()
        self.help_menu.add_command(label="  Aide",
                                   command=cb.get("show_help"))
        self.add_cascade(label="\u00c0 propos", menu=self.help_menu)

