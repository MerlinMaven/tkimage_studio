import tkinter as tk
from tkinter import ttk
import os
from src.utils.constants import COLORS, FONTS


class StatusPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Card.TFrame", height=30)
        self.pack_propagate(False)

        # Thin top border
        ttk.Frame(self, style="Border.TFrame", height=1).pack(
            fill=tk.X, side=tk.TOP)

        inner = ttk.Frame(self, style="Card.TFrame")
        inner.pack(fill=tk.BOTH, expand=True, padx=18)

        self.lbl_path = ttk.Label(inner, text="Pr\u00eat",
                                  style="Card.TLabel")
        self.lbl_path.pack(side=tk.LEFT)

        self.lbl_index = ttk.Label(inner, text="",
                                   style="Card.TLabel")
        self.lbl_index.pack(side=tk.RIGHT, padx=(12, 0))

        self.lbl_info = ttk.Label(inner, text="",
                                  style="Card.TLabel")
        self.lbl_info.pack(side=tk.RIGHT)

    def update_status(self, file_path, width, height, mode,
                      current_idx=0, total_imgs=0):
        if file_path:
            filename = os.path.basename(file_path)
            self.lbl_path.config(text=filename)
            self.lbl_info.config(text=f"{width}\u00d7{height}  \u00b7  {mode}")
        else:
            self.lbl_path.config(text="Pr\u00eat")
            self.lbl_info.config(text="")

        if total_imgs > 0:
            self.lbl_index.config(text=f"{current_idx}/{total_imgs}")
        else:
            self.lbl_index.config(text="")
