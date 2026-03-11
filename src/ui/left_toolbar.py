import tkinter as tk
from tkinter import ttk
from src.utils.constants import COLORS, FONTS


def _safe(callbacks, key, *args):
    fn = callbacks.get(key)
    if fn:
        fn(*args)


class LeftToolbar(ttk.Frame):
    def __init__(self, parent, callbacks=None):
        super().__init__(parent, style="Panel.TFrame", width=235)
        self.pack_propagate(False)
        self.callbacks = callbacks or {}

        # ── Header ──
        header = ttk.Frame(self, style="Panel.TFrame")
        header.pack(fill=tk.X, padx=14, pady=(14, 0))
        ttk.Label(header, text="\U0001F6E0  OUTILS",
                  style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(header, text="\u2715", style="Ghost.TButton", width=3,
                   command=self.callbacks.get("toggle_left_toolbar")).pack(
            side=tk.RIGHT)

        ttk.Frame(self, style="Accent.TFrame", height=2).pack(
            fill=tk.X, padx=14, pady=(8, 0))

        # ── Scrollable area ──
        scroll_wrap = ttk.Frame(self, style="Panel.TFrame")
        scroll_wrap.pack(fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(scroll_wrap, bg=COLORS["bg_panel"],
                                 highlightthickness=0, bd=0)
        self._canvas.pack(fill=tk.BOTH, expand=True)

        sf = ttk.Frame(self._canvas, style="Panel.TFrame")
        self._canvas_win = self._canvas.create_window(
            (0, 0), window=sf, anchor="nw")

        sf.bind("<Configure>",
                lambda e: self._canvas.configure(
                    scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfig(
                              self._canvas_win, width=e.width))

        self._build_tools(sf)

        # Bind mousewheel on all descendants
        self.after(100, lambda: self._bind_wheel(self))

    def _bind_wheel(self, widget):
        widget.bind("<MouseWheel>", self._on_wheel, add="+")
        for child in widget.winfo_children():
            self._bind_wheel(child)

    def _on_wheel(self, e):
        self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        return "break"

    # ── Content ──
    def _build_tools(self, parent):
        cb = self.callbacks
        p = {"fill": tk.X, "padx": 14, "pady": 2}

        # FICHIER
        self._section(parent, "\U0001F4C1  FICHIER")
        ttk.Button(parent, text="  Ouvrir image", style="Tool.TButton",
                   command=cb.get("open_image")).pack(**p)
        ttk.Button(parent, text="  Ouvrir dossier", style="Tool.TButton",
                   command=cb.get("open_folder")).pack(**p)
        ttk.Button(parent, text="  Enregistrer", style="Tool.TButton",
                   command=cb.get("save_image")).pack(**p)
        ttk.Button(parent, text="\U0001F4E6  Export dataset ML", style="Accent.TButton",
                   command=cb.get("export_dataset")).pack(**p)

        # \u00c9DITION
        self._section(parent, "\u270F\uFE0F  \u00c9DITION")
        ttk.Button(parent, text="  Annuler", style="Tool.TButton",
                   command=cb.get("undo")).pack(**p)
        ttk.Button(parent, text="  R\u00e9tablir", style="Tool.TButton",
                   command=cb.get("redo")).pack(**p)
        ttk.Button(parent, text="  R\u00e9initialiser", style="Tool.TButton",
                   command=cb.get("reset_image")).pack(**p)

        # TRANSFORMATION
        self._section(parent, "\U0001F504  TRANSFORMATION")
        ttk.Button(parent, text="  Rotation 90\u00b0", style="Tool.TButton",
                   command=lambda: _safe(cb, "tool_action", "rotate")).pack(**p)
        ttk.Button(parent, text="  Redimensionner", style="Tool.TButton",
                   command=lambda: _safe(cb, "tool_action", "resize")).pack(**p)
        ttk.Button(parent, text="  Rogner (auto)", style="Tool.TButton",
                   command=lambda: _safe(cb, "tool_action", "crop")).pack(**p)
        ttk.Button(parent, text="  Recadrage souris", style="Tool.TButton",
                   command=lambda: _safe(cb, "set_tool", "mouse_crop")).pack(**p)
        ttk.Button(parent, text="  Compresser", style="Tool.TButton",
                   command=lambda: _safe(cb, "tool_action", "compress")).pack(**p)

        # VUE
        self._section(parent, "\U0001F50D  VUE")
        ttk.Button(parent, text="\U0001F5BC  Basculer Galerie", style="Accent.TButton",
                   command=lambda: _safe(cb, "toggle_gallery_mode")).pack(**p)
        ttk.Button(parent, text="  Pointeur", style="Tool.TButton",
                   command=lambda: _safe(cb, "set_tool", "pointer")).pack(**p)

        zoom_row = ttk.Frame(parent, style="Panel.TFrame")
        zoom_row.pack(fill=tk.X, padx=14, pady=2)
        ttk.Button(zoom_row, text=" + ", style="Tool.TButton", width=5,
                   command=lambda: _safe(cb, "zoom", "in")).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        ttk.Button(zoom_row, text=" \u2212 ", style="Tool.TButton", width=5,
                   command=lambda: _safe(cb, "zoom", "out")).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(zoom_row, text=" Fit ", style="Tool.TButton", width=5,
                   command=lambda: _safe(cb, "zoom", "fit")).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        # Bottom padding
        ttk.Frame(parent, style="Panel.TFrame", height=24).pack()

    def _section(self, parent, text):
        f = ttk.Frame(parent, style="Panel.TFrame")
        f.pack(fill=tk.X, padx=14, pady=(18, 6))
        ttk.Label(f, text=text, style="Header.TLabel").pack(side=tk.LEFT)
