import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
from src.utils.constants import COLORS, FONTS

# ── Card dimensions ──
THUMB_SIZE = 140
CARD_PAD = 8          # inner padding around thumbnail
CARD_GAP = 12         # gap between cards
CARD_W = THUMB_SIZE + CARD_PAD * 2
CARD_H = THUMB_SIZE + CARD_PAD * 2 + 34   # extra 34 for filename bar

# Colours
_C = COLORS
_SEL_BORDER = _C["accent"]
_NORM_BORDER = _C["border_light"]
_CARD_BG = _C["bg_panel"]
_HOVER_BG = _C["accent_soft"]


class GalleryViewer(ttk.Frame):
    """Scrollable thumbnail gallery with selection."""

    def __init__(self, parent, callbacks):
        super().__init__(parent, style="TFrame")
        self.callbacks = callbacks
        self.image_files: list[str] = []
        self.selected_files: set[str] = set()
        self.thumbnails: dict[str, ImageTk.PhotoImage] = {}
        self.checkbox_vars: dict[str, tk.BooleanVar] = {}
        self._card_widgets: dict[str, tk.Frame] = {}
        self._last_width = 0

        self._build_ui()

    # ── UI construction ─────────────────────────────────────────
    def _build_ui(self):
        # ── Header bar ──
        hdr = tk.Frame(self, bg=_C["bg_panel"], padx=16, pady=10)
        hdr.pack(fill=tk.X)

        # Left: icon + counter
        left = tk.Frame(hdr, bg=_C["bg_panel"])
        left.pack(side=tk.LEFT)
        tk.Label(left, text="🖼", font=("Segoe UI", 14),
                 bg=_C["bg_panel"]).pack(side=tk.LEFT, padx=(0, 6))
        self.lbl_info = tk.Label(
            left, text="0 / 0 sélectionnée(s)",
            font=FONTS["main"], bg=_C["bg_panel"],
            fg=_C["text_secondary"])
        self.lbl_info.pack(side=tk.LEFT)

        # Right: action buttons
        btn_kw = dict(font=FONTS["small"], bd=0, padx=12, pady=4,
                      cursor="hand2", activeforeground="#fff")

        self.btn_none = tk.Button(
            hdr, text="✕ Aucune", bg=_C["bg_elevated"],
            fg=_C["text_secondary"], activebackground=_C["bg_hover"],
            command=self.select_none, **btn_kw)
        self.btn_none.pack(side=tk.RIGHT, padx=(6, 0))

        self.btn_all = tk.Button(
            hdr, text="☑ Tout", bg=_C["accent"],
            fg="#ffffff", activebackground=_C["accent_hover"],
            command=self.select_all, **btn_kw)
        self.btn_all.pack(side=tk.RIGHT)

        # Accent divider
        tk.Frame(self, bg=_C["accent"], height=2).pack(fill=tk.X)

        # ── Scrollable canvas ──
        wrap = tk.Frame(self, bg=_C["bg_base"])
        wrap.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(wrap, bg=_C["bg_base"],
                                highlightthickness=0, bd=0)
        self.vscroll = ttk.Scrollbar(wrap, orient=tk.VERTICAL,
                                     command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        self.vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.grid_container = tk.Frame(self.canvas, bg=_C["bg_base"])
        self.grid_window = self.canvas.create_window(
            (0, 0), window=self.grid_container, anchor="nw")

        self.grid_container.bind("<Configure>", self._on_frame_cfg)
        self.canvas.bind("<Configure>", self._on_canvas_cfg)

        # ── Wheel: bind recursively (not bind_all) ──
        self.after(120, lambda: self._bind_wheel(self))

    # ── Scroll helpers ──────────────────────────────────────────
    def _bind_wheel(self, widget):
        widget.bind("<MouseWheel>", self._on_wheel, add="+")
        for child in widget.winfo_children():
            self._bind_wheel(child)

    def _on_wheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def _on_frame_cfg(self, _=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_cfg(self, event):
        self.canvas.itemconfig(self.grid_window, width=event.width)
        # Only rebuild when column count actually changes
        new_cols = max(1, event.width // (CARD_W + CARD_GAP))
        old_cols = max(1, self._last_width // (CARD_W + CARD_GAP)) if self._last_width > 0 else 0
        if new_cols != old_cols:
            self._last_width = event.width
            self._rebuild_grid(event.width)

    # ── Public API ──────────────────────────────────────────────
    def load_images(self, image_files):
        self.image_files = image_files
        self.selected_files.clear()
        self.thumbnails.clear()
        self.checkbox_vars.clear()
        self._card_widgets.clear()
        for path in self.image_files:
            self.checkbox_vars[path] = tk.BooleanVar(value=False)
        self._update_info()
        self._last_width = self.canvas.winfo_width()
        self._rebuild_grid(self._last_width)

    # ── Grid layout ─────────────────────────────────────────────
    def _rebuild_grid(self, width):
        if width <= 10:
            return

        for w in self.grid_container.winfo_children():
            w.destroy()
        self._card_widgets.clear()

        if not self.image_files:
            tk.Label(self.grid_container,
                     text="Aucune image dans ce dossier.",
                     font=("Segoe UI", 12), bg=_C["bg_base"],
                     fg=_C["text_muted"]).pack(pady=60)
            return

        cols = max(1, width // (CARD_W + CARD_GAP))

        # Centre the grid with left padding
        total_grid_w = cols * (CARD_W + CARD_GAP)
        left_pad = max(0, (width - total_grid_w) // 2)

        for idx, path in enumerate(self.image_files):
            r = idx // cols
            c = idx % cols
            card = self._make_card(self.grid_container, path)
            card.grid(row=r, column=c,
                      padx=(left_pad if c == 0 else CARD_GAP // 2,
                            CARD_GAP // 2),
                      pady=CARD_GAP // 2)

        # Re-bind wheel on new widgets
        self.after(50, lambda: self._bind_wheel(self.grid_container))

    def _make_card(self, parent, path):
        """Build one thumbnail card."""
        is_sel = path in self.selected_files

        # Outer card frame
        border_col = _SEL_BORDER if is_sel else _NORM_BORDER
        card = tk.Frame(parent, bg=_CARD_BG, width=CARD_W, height=CARD_H,
                        highlightbackground=border_col,
                        highlightthickness=2, cursor="hand2")
        card.pack_propagate(False)
        card.grid_propagate(False)
        self._card_widgets[path] = card

        # ── Thumbnail area ──
        img_frame = tk.Frame(card, bg=_C["bg_surface"],
                             width=THUMB_SIZE, height=THUMB_SIZE)
        img_frame.pack(padx=CARD_PAD, pady=(CARD_PAD, 0))
        img_frame.pack_propagate(False)

        lbl_img = tk.Label(img_frame, bg=_C["bg_surface"])
        lbl_img.pack(expand=True)

        if path in self.thumbnails:
            lbl_img.config(image=self.thumbnails[path])
        else:
            self._load_thumbnail(path, lbl_img)

        # ── Bottom bar: checkbox + filename ──
        bot = tk.Frame(card, bg=_CARD_BG)
        bot.pack(fill=tk.X, padx=6, pady=(4, 4))

        var = self.checkbox_vars[path]
        chk = tk.Checkbutton(
            bot, variable=var,
            command=lambda p=path: self._on_check(p),
            bg=_CARD_BG, activebackground=_CARD_BG,
            highlightthickness=0, bd=0)
        chk.pack(side=tk.LEFT)

        fname = os.path.basename(path)
        if len(fname) > 18:
            fname = fname[:15] + "…"
        lbl_name = tk.Label(
            bot, text=fname, font=FONTS["tiny"],
            bg=_CARD_BG, fg=_C["text_secondary"],
            anchor="w")
        lbl_name.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ── Hover & click bindings ──
        widgets = [card, img_frame, lbl_img, bot, lbl_name]
        for w in widgets:
            w.bind("<Enter>", lambda e, c=card: self._hover_enter(c))
            w.bind("<Leave>", lambda e, c=card: self._hover_leave(c, path))
            w.bind("<Button-1>", lambda e, p=path: self._toggle_selection(p))

        return card

    # ── Thumbnail loading ───────────────────────────────────────
    def _load_thumbnail(self, path, lbl):
        try:
            img = Image.open(path)
            img.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.thumbnails[path] = photo
            lbl.config(image=photo)
        except Exception:
            lbl.config(text="⚠", font=("Segoe UI", 20),
                       fg=_C["text_muted"], width=6, height=4)

    # ── Hover effects ───────────────────────────────────────────
    def _hover_enter(self, card):
        card.configure(highlightbackground=_C["accent"])

    def _hover_leave(self, card, path):
        if path in self.selected_files:
            card.configure(highlightbackground=_SEL_BORDER)
        else:
            card.configure(highlightbackground=_NORM_BORDER)

    # ── Selection ───────────────────────────────────────────────
    def _toggle_selection(self, path):
        var = self.checkbox_vars[path]
        var.set(not var.get())
        self._on_check(path)

    def _on_check(self, path):
        if self.checkbox_vars[path].get():
            self.selected_files.add(path)
        else:
            self.selected_files.discard(path)
        # Visual update on card border
        card = self._card_widgets.get(path)
        if card:
            col = _SEL_BORDER if path in self.selected_files else _NORM_BORDER
            card.configure(highlightbackground=col)
        self._update_info()
        self._notify_mode_switch_if_needed()

    def select_all(self):
        for path, var in self.checkbox_vars.items():
            var.set(True)
            self.selected_files.add(path)
        for path, card in self._card_widgets.items():
            card.configure(highlightbackground=_SEL_BORDER)
        self._update_info()
        self._notify_mode_switch_if_needed()

    def select_none(self):
        for path, var in self.checkbox_vars.items():
            var.set(False)
        self.selected_files.clear()
        for card in self._card_widgets.values():
            card.configure(highlightbackground=_NORM_BORDER)
        self._update_info()
        self._notify_mode_switch_if_needed()
        
    def _update_info(self):
        sel = len(self.selected_files)
        total = len(self.image_files)
        self.lbl_info.config(text=f"{sel} / {total} sélectionnée(s)")
        
    def _notify_mode_switch_if_needed(self):
        if "on_gallery_selection_changed" in self.callbacks:
            self.callbacks["on_gallery_selection_changed"](list(self.selected_files))
