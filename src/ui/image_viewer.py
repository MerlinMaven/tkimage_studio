import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from src.utils.constants import COLORS, FONTS


class ImageViewer(ttk.Frame):
    def __init__(self, parent, callbacks=None):
        super().__init__(parent, style="Surface.TFrame")
        self.callbacks = callbacks or {}

        self.pil_image = None
        self.image_tk = None
        self.image_id = None
        self.zoom_level = "fit"
        self.current_tool = "pointer"
        self.rect_id = None
        self.start_x = None
        self.start_y = None
        self._slider_after_id = None
        self._resize_after_id = None

        # ── Canvas ──
        self.canvas = tk.Canvas(self, bg=COLORS["bg_surface"],
                                highlightthickness=0, cursor="arrow")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Configure>", self._on_resize_event)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<ButtonPress-3>", self.on_pan_start)
        self.canvas.bind("<B3-Motion>", self.on_pan_drag)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        # ── Navigation bar ──
        nav = ttk.Frame(self, style="Surface.TFrame", padding=(16, 6))
        nav.pack(fill=tk.X, side=tk.BOTTOM)

        # Thin separator above nav
        ttk.Frame(self, style="Border.TFrame", height=1).pack(
            fill=tk.X, side=tk.BOTTOM)

        self.btn_prev = ttk.Button(nav, text="\u276e  Pr\u00e9c\u00e9dent",
                                   style="Nav.TButton",
                                   command=self.callbacks.get("prev_image"),
                                   state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT)

        self.btn_next = ttk.Button(nav, text="Suivant  \u276f",
                                   style="Nav.TButton",
                                   command=self.callbacks.get("next_image"),
                                   state=tk.DISABLED)
        self.btn_next.pack(side=tk.RIGHT)

        # Zoom indicator
        self.lbl_zoom = ttk.Label(nav, text="Fit", style="Surface.TLabel",
                                  font=FONTS["tiny"])
        self.lbl_zoom.pack(side=tk.RIGHT, padx=(0, 12))

        # Slider
        self.slider_var = tk.IntVar()
        self.slider = ttk.Scale(nav, from_=0, to=100,
                                variable=self.slider_var,
                                orient=tk.HORIZONTAL,
                                style="Horizontal.TScale",
                                state=tk.DISABLED,
                                command=self._on_slider_raw)
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12)

        # Show empty state on first render
        self.after(50, self._show_empty_state)

    # ── Empty state ──
    def _show_empty_state(self):
        self.canvas.delete("all")
        cw = max(self.canvas.winfo_width(), 400)
        ch = max(self.canvas.winfo_height(), 300)
        cx, cy = cw // 2, ch // 2

        # Subtle accent glow circle
        r = 55
        self.canvas.create_oval(
            cx - r, cy - 70 - r, cx + r, cy - 70 + r,
            fill=COLORS["accent_soft"], outline="",
            tags="empty")

        # App icon
        self.canvas.create_text(
            cx, cy - 70, text="\U0001F5BC",
            fill=COLORS["accent"], font=("Segoe UI", 38),
            anchor=tk.CENTER, tags="empty")

        self.canvas.create_text(
            cx, cy + 5, text="TkImage Studio",
            fill=COLORS["text_primary"], font=FONTS["title"],
            anchor=tk.CENTER, tags="empty")
        self.canvas.create_text(
            cx, cy + 34,
            text="Ouvrez une image ou un dossier pour commencer",
            fill=COLORS["text_secondary"], font=FONTS["main"],
            anchor=tk.CENTER, tags="empty")

        # Keyboard hints - styled as a subtle card
        hints_y = cy + 68
        pw, ph = 220, 22
        self.canvas.create_rectangle(
            cx - pw, hints_y - ph, cx + pw, hints_y + ph,
            fill=COLORS["bg_panel"], outline=COLORS["border"],
            tags="empty")
        self.canvas.create_text(
            cx, hints_y,
            text="Ctrl+O  \u00b7  \u2190 \u2192  Navigation  \u00b7  Molette = Zoom",
            fill=COLORS["text_muted"], font=FONTS["small"],
            anchor=tk.CENTER, tags="empty")

    # ── Resize debounce ──
    def _on_resize_event(self, event):
        if self._resize_after_id:
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(50, self._do_resize)

    def _do_resize(self):
        self._resize_after_id = None
        if self.pil_image is None:
            self._show_empty_state()
        elif self.zoom_level == "fit":
            self.display_image(self.pil_image)

    # ── Zoom ──
    def _update_zoom_label(self):
        if self.zoom_level == "fit":
            self.lbl_zoom.config(text="Fit")
        else:
            self.lbl_zoom.config(text=f"{int(self.zoom_level * 100)}%")

    def set_zoom(self, logic):
        if logic == "fit":
            self.zoom_level = "fit"
        elif logic == "in":
            if self.zoom_level == "fit":
                self.zoom_level = 1.0
            self.zoom_level = min(self.zoom_level * 1.2, 10.0)
        elif logic == "out":
            if self.zoom_level == "fit":
                self.zoom_level = 1.0
            self.zoom_level = max(self.zoom_level / 1.2, 0.1)

        self._update_zoom_label()
        if self.pil_image:
            self.display_image(self.pil_image)

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.set_zoom("in")
        else:
            self.set_zoom("out")

    # ── Tool ──
    def set_tool(self, tool_name):
        self.current_tool = tool_name
        self.canvas.config(
            cursor="crosshair" if tool_name == "mouse_crop" else "arrow")

    # ── Display ──
    def display_image(self, pil_image):
        self.pil_image = pil_image
        if pil_image is None:
            self._show_empty_state()
            self._update_zoom_label()
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 800, 600

        display_img = pil_image.copy()
        orig_w, orig_h = display_img.size

        if self.zoom_level == "fit":
            ratio = min(canvas_width / orig_w, canvas_height / orig_h)
            new_w, new_h = int(orig_w * ratio), int(orig_h * ratio)
        else:
            new_w = int(orig_w * self.zoom_level)
            new_h = int(orig_h * self.zoom_level)

        display_img = display_img.resize((max(new_w, 1), max(new_h, 1)),
                                          Image.Resampling.LANCZOS)
        self.image_tk = ImageTk.PhotoImage(display_img)

        self.canvas.delete("all")
        self.image_id = self.canvas.create_image(
            canvas_width // 2, canvas_height // 2,
            anchor=tk.CENTER, image=self.image_tk)

        if self.zoom_level != "fit":
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        else:
            self.canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))

    # ── Navigation slider ──
    def update_nav_slider(self, current_idx, total_count):
        if total_count > 1:
            self.slider.config(to=total_count - 1, state=tk.NORMAL)
            self.slider_var.set(current_idx)
        else:
            self.slider.config(state=tk.DISABLED)

    def _on_slider_raw(self, value):
        if self._slider_after_id:
            self.after_cancel(self._slider_after_id)
        self._slider_after_id = self.after(200, self._on_slider_commit)

    def _on_slider_commit(self):
        self._slider_after_id = None
        idx = self.slider_var.get()
        if "goto_image" in self.callbacks:
            self.callbacks["goto_image"](idx)

    def update_nav_buttons(self, has_prev, has_next):
        self.btn_prev.config(state=tk.NORMAL if has_prev else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if has_next else tk.DISABLED)



    # ── Mouse: crop selection ──
    def on_mouse_down(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.current_tool == "mouse_crop":
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline=COLORS["accent"], width=2, dash=(4, 4))

    def on_mouse_drag(self, event):
        if self.current_tool == "mouse_crop" and self.rect_id:
            cur_x = self.canvas.canvasx(event.x)
            cur_y = self.canvas.canvasy(event.y)
            self.canvas.coords(self.rect_id,
                               self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_up(self, event):
        if self.current_tool == "mouse_crop" and self.rect_id and self.pil_image:
            end_x = self.canvas.canvasx(event.x)
            end_y = self.canvas.canvasy(event.y)
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            orig_w, orig_h = self.pil_image.size
            if self.zoom_level == "fit":
                ratio = min(canvas_w / orig_w, canvas_h / orig_h)
            else:
                ratio = self.zoom_level
            img_w, img_h = int(orig_w * ratio), int(orig_h * ratio)
            offset_x = (canvas_w - img_w) / 2
            offset_y = (canvas_h - img_h) / 2
            x1 = max(0, int((min(self.start_x, end_x) - offset_x) / ratio))
            y1 = max(0, int((min(self.start_y, end_y) - offset_y) / ratio))
            x2 = min(orig_w, int((max(self.start_x, end_x) - offset_x) / ratio))
            y2 = min(orig_h, int((max(self.start_y, end_y) - offset_y) / ratio))
            if x2 - x1 > 10 and y2 - y1 > 10:
                if "crop_box" in self.callbacks:
                    self.callbacks["crop_box"]((x1, y1, x2, y2))
            self.canvas.delete(self.rect_id)
            self.rect_id = None

    # ── Pan (right-click drag) ──
    def on_pan_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def on_pan_drag(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
