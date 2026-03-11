import tkinter as tk
from tkinter import ttk
from src.utils.constants import (
    COLORS, FONTS,
    ANNOTATION_STATUS, ANNOTATION_QUALITY,
)


class RightPanel(ttk.Frame):
    """Panneau droit — Métadonnées, Classification, Workflow, Notes, Rapport."""

    WIDTH = 300

    def __init__(self, parent, callbacks=None):
        super().__init__(parent, style="Panel.TFrame", width=self.WIDTH)
        self.pack_propagate(False)
        self.callbacks = callbacks or {}
        self._custom_labels: list[str] = []

        # ── Header ──
        header = ttk.Frame(self, style="Panel.TFrame")
        header.pack(fill=tk.X, padx=16, pady=(14, 0))
        ttk.Label(header, text="PROPRIÉTÉS & IA",
                  style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(header, text="\u2715", style="Ghost.TButton", width=3,
                   command=self.callbacks.get("toggle_right_panel"),
                   ).pack(side=tk.RIGHT)
        ttk.Button(header, text="\u2699", style="Ghost.TButton", width=3,
                   command=self._open_settings).pack(side=tk.RIGHT, padx=(0, 2))

        ttk.Frame(self, style="Accent.TFrame", height=2).pack(
            fill=tk.X, padx=16, pady=(8, 0))

        # ── Scrollable area ──
        scroll_wrap = ttk.Frame(self, style="Panel.TFrame")
        scroll_wrap.pack(fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(
            scroll_wrap, bg=COLORS["bg_panel"],
            highlightthickness=0, bd=0)
        self._scrollbar = ttk.Scrollbar(
            scroll_wrap, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=4)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                          padx=(4, 0), pady=4)

        self.scrollable = ttk.Frame(self._canvas, style="Panel.TFrame")
        self._canvas_win = self._canvas.create_window(
            (0, 0), window=self.scrollable, anchor="nw")

        self.scrollable.bind("<Configure>", self._on_frame_cfg)
        self._canvas.bind("<Configure>", self._on_canvas_cfg)

        self._build_sections()
        self.after(100, self._bind_scroll_recursive)

    # ── Scroll helpers ──────────────────────────────────────────
    def _on_frame_cfg(self, _=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_cfg(self, event):
        self._canvas.itemconfig(self._canvas_win, width=event.width)

    def _bind_scroll_recursive(self):
        self._bind_wheel(self)

    def _bind_wheel(self, widget):
        widget.bind("<MouseWheel>", self._on_wheel, add="+")
        widget.bind("<Button-4>", self._on_wheel, add="+")
        widget.bind("<Button-5>", self._on_wheel, add="+")
        for child in widget.winfo_children():
            self._bind_wheel(child)

    def _on_wheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    # ════════════════════════════════════════════════════════════
    #  SECTIONS
    # ════════════════════════════════════════════════════════════
    def _build_sections(self):
        s = self.scrollable

        # ─── 1. IMAGE ──────────────────────────────────────────
        self._section(s, "📷  IMAGE")
        card = self._card(s)
        self.lbl_size   = self._row(card, "Dimensions", "—")
        self.lbl_mode   = self._row(card, "Mode", "—")
        self.lbl_weight = self._row(card, "Taille", "—")
        self.lbl_format = self._row(card, "Format", "—")
        ttk.Frame(card, style="Card.TFrame", height=6).pack()

        # ─── 2. CLASSIFICATION ─────────────────────────────────
        self._section(s, "🏷  CLASSIFICATION")
        card_cls = self._card(s)

        # Label — editable combobox
        ttk.Label(card_cls, text="Classe :",
                  style="CardMuted.TLabel").pack(
            anchor=tk.W, padx=14, pady=(10, 2))

        lbl_row = ttk.Frame(card_cls, style="Card.TFrame")
        lbl_row.pack(fill=tk.X, padx=14, pady=(0, 2))
        self.combo_label = ttk.Combobox(lbl_row, values=self._custom_labels)
        self.combo_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(lbl_row, text="+", style="Tool.TButton", width=3,
                   command=self._add_label).pack(side=tk.RIGHT, padx=(4, 0))

        ttk.Label(card_cls,
                  text="Saisissez un nom puis  +  pour l\u2019ajouter",
                  style="CardMuted.TLabel", font=FONTS["tiny"]).pack(
            anchor=tk.W, padx=14, pady=(0, 8))

        # IA confidence (compact sub-card inside classification)
        ia_row = ttk.Frame(card_cls, style="Elevated.TFrame")
        ia_row.pack(fill=tk.X, padx=12, pady=(0, 6))

        ia_top = ttk.Frame(ia_row, style="Elevated.TFrame")
        ia_top.pack(fill=tk.X, padx=10, pady=(8, 0))
        ttk.Label(ia_top, text="🤖 Suggestion IA", font=FONTS["tiny"],
                  background=COLORS["bg_elevated"],
                  foreground=COLORS["accent"]).pack(side=tk.LEFT)
        self.lbl_confidence = ttk.Label(
            ia_top, text="—", style="Card.TLabel",
            font=FONTS["section"],
            background=COLORS["bg_elevated"])
        self.lbl_confidence.pack(side=tk.RIGHT)

        self.progress_confidence = ttk.Progressbar(
            ia_row, orient="horizontal", length=200, mode="determinate",
            style="Accent.Horizontal.TProgressbar")
        self.progress_confidence.pack(fill=tk.X, padx=10, pady=(4, 2))

        self.lbl_sugg = ttk.Label(
            ia_row,
            text="Configurez l'IA via ⚙",
            background=COLORS["bg_elevated"],
            foreground=COLORS["text_secondary"],
            font=FONTS["tiny"])
        self.lbl_sugg.pack(anchor=tk.W, padx=10, pady=(0, 8))
        ttk.Frame(card_cls, style="Card.TFrame", height=6).pack()

        # ─── 2b. ASSISTANT IA ──────────────────────────────────
        self._section(s, "🤖  ASSISTANT IA")
        card_ia = self._card(s)

        # Task selector
        ttk.Label(card_ia, text="Tâche :",
                  style="CardMuted.TLabel").pack(
            anchor=tk.W, padx=14, pady=(10, 2))
        self._ia_tasks = [
            "Classifier l'image",
            "Décrire l'image",
            "Détecter les objets",
            "Évaluer la qualité",
            "Générer des tags",
            "Question libre",
        ]
        self.combo_task = ttk.Combobox(
            card_ia, values=self._ia_tasks, state="readonly")
        self.combo_task.set(self._ia_tasks[0])
        self.combo_task.pack(fill=tk.X, padx=14, pady=(0, 6))

        # Prompt
        ttk.Label(card_ia, text="Prompt :",
                  style="CardMuted.TLabel").pack(
            anchor=tk.W, padx=14, pady=(4, 2))
        self.txt_prompt = tk.Text(
            card_ia, height=3, width=28,
            bg="#ffffff", fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            font=FONTS["small"], bd=0, relief="flat",
            highlightthickness=1,
            highlightcolor=COLORS["accent"],
            highlightbackground=COLORS["border"])
        self.txt_prompt.pack(fill=tk.X, padx=12, pady=(0, 6))

        # Generate button
        self.btn_generate = ttk.Button(
            card_ia, text="▶  Générer",
            style="Accent.TButton",
            command=self.callbacks.get("run_ia_analysis"))
        self.btn_generate.pack(fill=tk.X, padx=12, pady=(0, 6))

        # Response area
        ttk.Label(card_ia, text="Réponse :",
                  style="CardMuted.TLabel").pack(
            anchor=tk.W, padx=14, pady=(6, 2))
        self.txt_response = tk.Text(
            card_ia, height=5, width=28,
            bg=COLORS["bg_elevated"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            font=FONTS["small"], bd=0, relief="flat",
            highlightthickness=1,
            highlightcolor=COLORS["accent"],
            highlightbackground=COLORS["border"],
            state=tk.DISABLED)
        self.txt_response.pack(fill=tk.X, padx=12, pady=(0, 6))

        # Copy button
        ttk.Button(
            card_ia, text="📋  Copier la réponse",
            style="Tool.TButton",
            command=self._copy_response,
        ).pack(fill=tk.X, padx=12, pady=(0, 10))

        # ─── 3. WORKFLOW ───────────────────────────────────────
        self._section(s, "⚙  WORKFLOW")
        card_wf = self._card(s)

        # Status
        row_st = ttk.Frame(card_wf, style="Card.TFrame")
        row_st.pack(fill=tk.X, padx=14, pady=(10, 4))
        ttk.Label(row_st, text="Statut", style="CardMuted.TLabel").pack(side=tk.LEFT)
        self.combo_status = ttk.Combobox(
            row_st, values=ANNOTATION_STATUS, state="readonly", width=14)
        self.combo_status.set("Non annoté")
        self.combo_status.pack(side=tk.RIGHT)

        # Quality
        row_q = ttk.Frame(card_wf, style="Card.TFrame")
        row_q.pack(fill=tk.X, padx=14, pady=(4, 4))
        ttk.Label(row_q, text="Qualité", style="CardMuted.TLabel").pack(side=tk.LEFT)
        self.combo_quality = ttk.Combobox(
            row_q, values=ANNOTATION_QUALITY, state="readonly", width=14)
        self.combo_quality.set("—")
        self.combo_quality.pack(side=tk.RIGHT)

        # Exclude checkbox
        excl_row = ttk.Frame(card_wf, style="Card.TFrame")
        excl_row.pack(fill=tk.X, padx=14, pady=(6, 10))
        self.var_exclude = tk.BooleanVar(value=False)
        self._chk_exclude = tk.Checkbutton(
            excl_row, text="  Exclure du dataset",
            variable=self.var_exclude,
            bg=COLORS["bg_panel_light"], fg=COLORS["danger"],
            activebackground=COLORS["bg_panel_light"],
            selectcolor=COLORS["bg_panel_light"],
            font=FONTS["small"])
        self._chk_exclude.pack(side=tk.LEFT)

        # Batch button
        self.btn_apply_batch = ttk.Button(
            card_wf, text="Appliquer à la sélection",
            style="Accent.TButton",
            command=self.callbacks.get("apply_annotation_batch"),
            state=tk.DISABLED)
        self.btn_apply_batch.pack(fill=tk.X, padx=12, pady=(0, 10))

        # ─── 4. NOTES ─────────────────────────────────────────
        self._section(s, "📝  NOTES")
        card_notes = self._card(s)
        self.txt_desc = tk.Text(
            card_notes, height=3, width=28,
            bg="#ffffff", fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            font=FONTS["small"], bd=0, relief="flat",
            highlightthickness=1,
            highlightcolor=COLORS["accent"],
            highlightbackground=COLORS["border"])
        self.txt_desc.pack(fill=tk.X, padx=12, pady=(10, 6))
        ttk.Button(
            card_notes, text="Générer description (IA)",
            style="Tool.TButton",
            command=self.callbacks.get("generate_description"),
        ).pack(fill=tk.X, padx=12, pady=(0, 10))

        # ─── 5. RAPPORT ───────────────────────────────────────
        self._section(s, "📋  RAPPORT")
        card_rpt = self._card(s)
        ttk.Button(card_rpt, text="Voir le rapport", style="Tool.TButton",
                   command=self.callbacks.get("generate_report"),
                   ).pack(fill=tk.X, padx=12, pady=(10, 4))
        ttk.Button(card_rpt, text="Exporter (.txt)", style="Tool.TButton",
                   command=self.callbacks.get("export_report"),
                   ).pack(fill=tk.X, padx=12, pady=(0, 10))

        # Bottom spacer
        ttk.Frame(s, style="Panel.TFrame", height=30).pack()

    # ════════════════════════════════════════════════════════════
    #  LABEL SYSTEM
    # ════════════════════════════════════════════════════════════
    def _add_label(self):
        text = self.combo_label.get().strip()
        if text and text not in self._custom_labels:
            self._custom_labels.append(text)
            self.combo_label["values"] = self._custom_labels

    # ════════════════════════════════════════════════════════════
    #  IA SETTINGS DIALOG
    # ════════════════════════════════════════════════════════════
    def _open_settings(self):
        """Open a modal dialog to configure API key, URL, provider."""
        dlg = tk.Toplevel(self)
        dlg.title("Paramètres IA")
        dlg.geometry("420x340")
        dlg.resizable(False, False)
        dlg.configure(bg=COLORS["bg_panel"])
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        pad = dict(padx=16, pady=(8, 2))

        ttk.Label(dlg, text="⚙  Configuration du modèle IA",
                  font=FONTS["header"],
                  background=COLORS["bg_panel"]).pack(anchor=tk.W, padx=16, pady=(16, 10))

        # Provider
        ttk.Label(dlg, text="Fournisseur :",
                  background=COLORS["bg_panel"],
                  font=FONTS["small"]).pack(anchor=tk.W, **pad)
        providers = ["OpenAI", "Google Gemini", "Anthropic Claude",
                     "Hugging Face", "Ollama (local)", "Autre"]
        self._dlg_provider = ttk.Combobox(dlg, values=providers, state="readonly")
        self._dlg_provider.set(getattr(self, '_cfg_provider', 'OpenAI'))
        self._dlg_provider.pack(fill=tk.X, padx=16, pady=(0, 4))

        # URL
        ttk.Label(dlg, text="URL de l'API :",
                  background=COLORS["bg_panel"],
                  font=FONTS["small"]).pack(anchor=tk.W, **pad)
        self._dlg_url = ttk.Entry(dlg)
        self._dlg_url.insert(0, getattr(self, '_cfg_url', 'https://api.openai.com/v1'))
        self._dlg_url.pack(fill=tk.X, padx=16, pady=(0, 4))

        # API Key
        ttk.Label(dlg, text="Clé API :",
                  background=COLORS["bg_panel"],
                  font=FONTS["small"]).pack(anchor=tk.W, **pad)
        self._dlg_key = ttk.Entry(dlg, show="•")
        self._dlg_key.insert(0, getattr(self, '_cfg_api_key', ''))
        self._dlg_key.pack(fill=tk.X, padx=16, pady=(0, 4))

        # Model name
        ttk.Label(dlg, text="Modèle :",
                  background=COLORS["bg_panel"],
                  font=FONTS["small"]).pack(anchor=tk.W, **pad)
        self._dlg_model = ttk.Entry(dlg)
        self._dlg_model.insert(0, getattr(self, '_cfg_model', 'gpt-4o-mini'))
        self._dlg_model.pack(fill=tk.X, padx=16, pady=(0, 12))

        # Buttons
        btn_row = ttk.Frame(dlg)
        btn_row.pack(fill=tk.X, padx=16, pady=(4, 16))
        ttk.Button(btn_row, text="Enregistrer",
                   style="Accent.TButton",
                   command=lambda: self._save_settings(dlg)).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))
        ttk.Button(btn_row, text="Annuler",
                   style="Tool.TButton",
                   command=dlg.destroy).pack(
            side=tk.RIGHT, expand=True, fill=tk.X, padx=(4, 0))

    def _save_settings(self, dlg):
        self._cfg_provider = self._dlg_provider.get()
        self._cfg_url = self._dlg_url.get().strip()
        self._cfg_api_key = self._dlg_key.get().strip()
        self._cfg_model = self._dlg_model.get().strip()
        dlg.destroy()

    def get_ia_config(self):
        """Return current IA configuration dict."""
        return {
            "provider": getattr(self, '_cfg_provider', 'OpenAI'),
            "url": getattr(self, '_cfg_url', 'https://api.openai.com/v1'),
            "api_key": getattr(self, '_cfg_api_key', ''),
            "model": getattr(self, '_cfg_model', 'gpt-4o-mini'),
        }

    def get_ia_prompt(self):
        """Return the current prompt text."""
        return self.txt_prompt.get("1.0", tk.END).strip()

    def get_ia_task(self):
        """Return the selected IA task."""
        return self.combo_task.get()

    def set_ia_response(self, text):
        """Write text into the response area."""
        self.txt_response.config(state=tk.NORMAL)
        self.txt_response.delete("1.0", tk.END)
        self.txt_response.insert("1.0", text)
        self.txt_response.config(state=tk.DISABLED)

    def _copy_response(self):
        """Copy response text to clipboard."""
        text = self.txt_response.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)

    # ════════════════════════════════════════════════════════════
    #  WIDGET HELPERS
    # ════════════════════════════════════════════════════════════
    def _section(self, parent, text):
        ttk.Label(parent, text=text, style="Header.TLabel").pack(
            anchor=tk.W, padx=12, pady=(16, 4))

    def _card(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame")
        card.pack(fill=tk.X, padx=8, pady=2)
        return card

    def _row(self, parent, label, value):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill=tk.X, padx=14, pady=(6, 0))
        ttk.Label(row, text=label, style="CardMuted.TLabel").pack(
            side=tk.LEFT)
        lbl = ttk.Label(row, text=value, style="Card.TLabel")
        lbl.pack(side=tk.RIGHT)
        return lbl

    # ════════════════════════════════════════════════════════════
    #  PUBLIC API
    # ════════════════════════════════════════════════════════════
    def update_metadata(self, width, height, mode, file_size_kb, fmt=""):
        self.lbl_size.config(text=f"{width} \u00d7 {height} px")
        self.lbl_mode.config(text=mode)
        if file_size_kb >= 1024:
            self.lbl_weight.config(text=f"{file_size_kb / 1024:.2f} MB")
        else:
            self.lbl_weight.config(text=f"{file_size_kb:.1f} KB")
        if fmt:
            self.lbl_format.config(text=fmt)

    def set_ia_results(self, suggested_class, description, confidence=0):
        """Update the panel with IA analysis results."""
        self.lbl_sugg.config(text=suggested_class)

        text = suggested_class.strip()
        if text and text not in self._custom_labels:
            self._custom_labels.append(text)
            self.combo_label["values"] = self._custom_labels
        self.combo_label.set(text)

        self.combo_status.set("À vérifier")

        self.txt_desc.delete("1.0", tk.END)
        self.txt_desc.insert("1.0", description)

        pct = max(0, min(100, int(confidence)))
        self.lbl_confidence.config(text=f"{pct} %")
        self.progress_confidence["value"] = pct

        if pct >= 80:
            self.progress_confidence.configure(
                style="Success.Horizontal.TProgressbar")
        elif pct >= 50:
            self.progress_confidence.configure(
                style="Accent.Horizontal.TProgressbar")
        elif pct >= 30:
            self.progress_confidence.configure(
                style="Warning.Horizontal.TProgressbar")
        else:
            self.progress_confidence.configure(
                style="Danger.Horizontal.TProgressbar")

    def reset_annotation(self):
        self.combo_label.set("")
        self.combo_status.set("Non annoté")
        self.combo_quality.set("—")
        self.var_exclude.set(False)
        self.txt_desc.delete("1.0", tk.END)
        self.lbl_sugg.config(text="Configurez l'IA via ⚙")
        self.lbl_confidence.config(text="—")
        self.progress_confidence["value"] = 0
        self.progress_confidence.configure(
            style="Accent.Horizontal.TProgressbar")
        self.txt_prompt.delete("1.0", tk.END)
        self.set_ia_response("")

    def load_annotation(self, data):
        self.combo_label.set(data.get("label", ""))
        self.combo_status.set(data.get("status", "Non annoté"))
        self.combo_quality.set(data.get("quality", "—"))
        self.var_exclude.set(data.get("exclude", False))
        self.txt_desc.delete("1.0", tk.END)
        self.txt_desc.insert("1.0", data.get("notes", ""))

    def get_annotation_data(self):
        return {
            "label": self.combo_label.get().strip(),
            "status": self.combo_status.get(),
            "quality": self.combo_quality.get(),
            "exclude": self.var_exclude.get(),
            "notes": self.txt_desc.get("1.0", tk.END).strip(),
        }

    def configure_batch_mode(self, count):
        if count > 0:
            self.btn_apply_batch.config(
                state=tk.NORMAL, text=f"Appliquer à {count} image(s)")
        else:
            self.btn_apply_batch.config(
                state=tk.DISABLED, text="Appliquer à la sélection")
