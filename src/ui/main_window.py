import tkinter as tk
from tkinter import ttk
from src.utils.constants import APP_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, COLORS, COLLAPSED_RAIL_WIDTH
from src.ui.theme import setup_theme
from src.ui.menu_bar import MenuBar
from src.ui.left_toolbar import LeftToolbar
from src.ui.image_viewer import ImageViewer
from src.ui.status_panel import StatusPanel
from src.ui.file_explorer import FileExplorer
from src.ui.right_panel import RightPanel
from src.ui.gallery_viewer import GalleryViewer


class MainWindow(tk.Tk):
    def __init__(self, callbacks=None):
        super().__init__()
        self.callbacks = callbacks or {}

        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        setup_theme(self)
        self._setup_ui()

    # ── Layout ──────────────────────────────────────────────────
    #  col 0  : left toolbar  (or rail)
    #  col 1  : separator
    #  col 2  : file explorer (or rail)
    #  col 3  : separator
    #  col 4  : image viewer  (weight=1, expands)
    #  col 5  : separator
    #  col 6  : right panel   (or rail)
    # ────────────────────────────────────────────────────────────
    def _setup_ui(self):
        self.menu_bar = MenuBar(self, self.callbacks)
        self.config(menu=self.menu_bar)

        # Container for grid layout
        self.container = ttk.Frame(self, style="TFrame")
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container.columnconfigure(4, weight=1)
        self.container.rowconfigure(0, weight=1)

        # -- Left Toolbar (col 0) --
        self.left_toolbar = LeftToolbar(self.container, self.callbacks)
        self.left_toolbar.grid(row=0, column=0, sticky="ns")
        self.is_left_visible = True

        self._left_rail = self._make_rail(
            self.container, "\U0001F6E0", "Outils",
            lambda: self.toggle_left_toolbar())

        # -- Separator (col 1) --
        ttk.Frame(self.container, style="Border.TFrame",
                  width=1).grid(row=0, column=1, sticky="ns")

        # -- File Explorer (col 2) --
        self.file_explorer = FileExplorer(self.container, self.callbacks)
        self.file_explorer.grid(row=0, column=2, sticky="ns")
        self.is_explorer_visible = True

        self._explorer_rail = self._make_rail(
            self.container, "\U0001F4C2", "Fichiers",
            lambda: self.toggle_file_explorer())

        # -- Separator (col 3) --
        ttk.Frame(self.container, style="Border.TFrame",
                  width=1).grid(row=0, column=3, sticky="ns")

        # -- Image Viewer (col 4) --
        self.image_viewer = ImageViewer(self.container, self.callbacks)
        self.image_viewer.grid(row=0, column=4, sticky="nsew")

        # -- Gallery Viewer (col 4) --
        self.gallery_viewer = GalleryViewer(self.container, self.callbacks)

        # -- Separator (col 5) --
        ttk.Frame(self.container, style="Border.TFrame",
                  width=1).grid(row=0, column=5, sticky="ns")

        # -- Right Panel (col 6) --
        self.right_panel = RightPanel(self.container, self.callbacks)
        self.right_panel.grid(row=0, column=6, sticky="ns")
        self.is_right_panel_visible = True

        self._right_rail = self._make_rail(
            self.container, "\u2699", "Param.",
            lambda: self.toggle_right_panel())

        # -- Status Panel --
        self.status_panel = StatusPanel(self)
        self.status_panel.pack(fill=tk.X, side=tk.BOTTOM)

    # ── Rail factory ────────────────────────────────────────────
    def _make_rail(self, parent, icon, tooltip, command):
        rail = ttk.Frame(parent, style="Rail.TFrame",
                         width=COLLAPSED_RAIL_WIDTH)
        rail.pack_propagate(False)
        rail.grid_propagate(False)

        btn = tk.Button(rail, text=icon, font=("Segoe UI", 14),
                        bg=COLORS["bg_panel"], fg=COLORS["text_secondary"],
                        activebackground=COLORS["bg_hover"],
                        activeforeground=COLORS["accent"],
                        bd=0, relief="flat", cursor="hand2",
                        command=command)
        btn.pack(fill=tk.X, pady=(12, 2))

        lbl = tk.Label(rail, text=tooltip, font=("Segoe UI", 7),
                       bg=COLORS["bg_panel"], fg=COLORS["text_muted"])
        lbl.pack()
        lbl.bind("<Button-1>", lambda e: command())

        return rail

    # ── Toggle methods ──────────────────────────────────────────
    def toggle_left_toolbar(self):
        if self.is_left_visible:
            self.left_toolbar.grid_remove()
            self._left_rail.grid(row=0, column=0, sticky="ns")
            self.is_left_visible = False
        else:
            self._left_rail.grid_remove()
            self.left_toolbar.grid(row=0, column=0, sticky="ns")
            self.is_left_visible = True

    def toggle_file_explorer(self):
        if self.is_explorer_visible:
            self.file_explorer.grid_remove()
            self._explorer_rail.grid(row=0, column=2, sticky="ns")
            self.is_explorer_visible = False
        else:
            self._explorer_rail.grid_remove()
            self.file_explorer.grid(row=0, column=2, sticky="ns")
            self.is_explorer_visible = True

    def toggle_right_panel(self):
        if self.is_right_panel_visible:
            self.right_panel.grid_remove()
            self._right_rail.grid(row=0, column=6, sticky="ns")
            self.is_right_panel_visible = False
        else:
            self._right_rail.grid_remove()
            self.right_panel.grid(row=0, column=6, sticky="ns")
            self.is_right_panel_visible = True

    def toggle_view_mode(self, is_gallery):
        if is_gallery:
            self.image_viewer.grid_remove()
            self.gallery_viewer.grid(row=0, column=4, sticky="nsew")
        else:
            self.gallery_viewer.grid_remove()
            self.image_viewer.grid(row=0, column=4, sticky="nsew")

    # ── Dialogs ─────────────────────────────────────────────────
    def show_error(self, message):
        from tkinter import messagebox
        messagebox.showerror("Erreur", message)

    def show_info(self, title, message):
        from tkinter import messagebox
        messagebox.showinfo(title, message)
