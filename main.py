import tkinter as tk
from tkinter import filedialog, ttk
import os
import json
import csv
import random
import threading
from PIL import Image, ImageOps, ImageEnhance
from src.ui.main_window import MainWindow
from src.core.image_processor import ImageProcessor
from src.core.file_manager import FileManager
from src.core.activity_logger import ActivityLogger
from src.utils.constants import APP_VERSION, APP_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, COLORS, FONTS

class Application:
    def __init__(self):
        # Initialisation Core
        self.processor = ImageProcessor()
        self.file_manager = FileManager()
        self.logger = ActivityLogger()
        self.annotations = {}  # {file_path: annotation_dict}
        self.is_gallery_mode = False

        
        # Dictionnaire des actions métier
        self.callbacks = {
            # --- Fichier ---
            "open_image": self.open_image,
            "open_folder": self.open_folder,
            "save_image": self.save_image,
            "save_image_as": self.save_image_as,
            "export_annotations": self.export_annotations,
            "export_dataset": self.export_dataset,
            # --- Édition ---
            "undo": self.undo,
            "redo": self.redo,
            "remove_from_session": self.remove_from_session,
            "reset_image": self.reset_image,
            # --- Navigation Image ---
            "prev_image": self.prev_image,
            "next_image": self.next_image,
            "goto_image": self.goto_image,
            # --- Outils ---
            "set_tool": self.set_tool,
            "tool_action": self.tool_action,
            "zoom": self.zoom,
            "crop_box": self.crop_box,
            # --- Filtres & IA Simulé ---
            "apply_filter": self.apply_filter,
            "apply_segmentation": self.apply_segmentation,
            "apply_vis3d": self.apply_vis3d,
            # --- Aide ---
            "show_presentation": self.show_presentation,
            "show_version": self.show_version,
            "show_author": self.show_author,
            "show_help": self.show_help,
            # --- UI ---
            "resize_window": self.refresh_display,
            "toggle_right_panel": self.toggle_right_panel,
            "toggle_left_toolbar": self.toggle_left_toolbar,
            "toggle_file_explorer": self.toggle_file_explorer,
            # --- Galerie ---
            "toggle_gallery_mode": self.toggle_gallery_mode,
            "on_gallery_selection_changed": self.on_gallery_selection_changed,
            "apply_annotation_batch": self.apply_annotation_batch,
            # --- File Explorer ---
            "on_file_select": self.on_file_select,
            # --- Right Panel (IA) ---
            "generate_description": self.generate_description,
            "run_ia_analysis": self.run_ia_analysis,
            # --- Rapport ---
            "generate_report": self.generate_report,
            "export_report": self.export_report,
        }
        
        self.root = MainWindow(callbacks=self.callbacks)
        self._bind_keyboard_shortcuts()

    def run(self):
        self.root.mainloop()

    # --- Raccourcis Clavier ---
    def _bind_keyboard_shortcuts(self):
        self.root.bind("<Control-o>", lambda e: self.open_image())
        self.root.bind("<Control-s>", lambda e: self.save_image())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_image_as())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-r>", lambda e: self.reset_image())
        self.root.bind("<Left>", self._nav_prev)
        self.root.bind("<Right>", self._nav_next)
        self.root.bind("<Control-plus>", lambda e: self.zoom("in"))
        self.root.bind("<Control-minus>", lambda e: self.zoom("out"))
        self.root.bind("<Control-0>", lambda e: self.zoom("fit"))

    def _nav_prev(self, event):
        if isinstance(event.widget, (tk.Text, tk.Entry)):
            return
        self.prev_image()

    def _nav_next(self, event):
        if isinstance(event.widget, (tk.Text, tk.Entry)):
            return
        self.next_image()

    # --- Fichiers & Dossiers ---
    def open_image(self):
        file_path = filedialog.askopenfilename(title="Ouvrir une image", filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff")])
        if file_path:
            self.file_manager.set_current_image(file_path)
            self._load_current_image()
            self.logger.log("file", "Ouverture d'image", os.path.basename(file_path))

    def open_folder(self):
        folder_path = filedialog.askdirectory(title="Ouvrir un dossier d'images")
        if folder_path:
            if self.file_manager.load_folder(folder_path):
                self.root.file_explorer.set_root_path(folder_path)
                self._load_current_image()
                self.logger.log("file", "Ouverture de dossier", folder_path)
            else:
                self.root.show_error("Dossier vide ou pas d'images supportées.")
                
    def on_file_select(self, file_path):
        self.file_manager.set_current_image(file_path)
        folder_path = os.path.dirname(file_path)
        if self.file_manager.current_folder != folder_path:
            self.file_manager.load_folder(folder_path)
            self.file_manager.set_current_image(file_path)
        self._load_current_image()
        self.logger.log("file", "Sélection de fichier", os.path.basename(file_path))

    def save_image(self):
        if self.processor.current_image and self.processor.image_path:
            try:
                self.processor.current_image.save(self.processor.image_path)
                self.root.show_info("Succès", "Image enregistrée.")
                self.logger.log("file", "Enregistrement", os.path.basename(self.processor.image_path))
            except Exception as e:
                self.root.show_error(f"Erreur d'enregistrement : {e}")

    def save_image_as(self):
        if not self.processor.current_image: return
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if file_path:
            try:
                self.processor.current_image.save(file_path)
                self.root.show_info("Succès", "Image enregistrée sous: " + file_path)
                self.logger.log("file", "Enregistrer sous", os.path.basename(file_path))
            except Exception as e:
                self.root.show_error(f"Erreur d'enregistrement : {e}")

    def export_annotations(self):
        """Exporte toutes les annotations en JSON."""
        self._save_current_annotation()
        if not self.annotations:
            self.root.show_error("Aucune annotation à exporter.")
            return
        file_path = filedialog.asksaveasfilename(
            title="Exporter les annotations",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("CSV", "*.csv")],
            initialfile="annotations.json")
        if not file_path:
            return
        export = {}
        for img_path, data in self.annotations.items():
            export[os.path.basename(img_path)] = {
                "path": img_path,
                **data,
            }
        if file_path.lower().endswith(".csv"):
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["fichier", "label", "statut", "qualite",
                                 "exclude", "notes"])
                for img_path, data in self.annotations.items():
                    writer.writerow([
                        os.path.basename(img_path),
                        data.get("label", ""),
                        data.get("status", ""),
                        data.get("quality", ""),
                        data.get("exclude", False),
                        data.get("notes", ""),
                    ])
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export, f, ensure_ascii=False, indent=2)
        self.root.show_info("Export", f"Annotations exportées vers :\n{file_path}")
        self.logger.log("file", "Export annotations", os.path.basename(file_path))

    def export_dataset(self):
        """Exporte un dataset ML-ready avec split train/val/test et augmentation."""
        self._save_current_annotation()

        # Collecter les images annotées avec un label, exclure les "exclues"
        labeled = {p: d for p, d in self.annotations.items()
                   if d.get("label", "").strip() and not d.get("exclude", False)}
        if not labeled:
            self.root.show_error(
                "Aucune image annotée avec un label.\n"
                "Attribuez un label (classe) à vos images avant d'exporter.")
            return

        # Compter les classes
        classes = {}
        for d in labeled.values():
            lbl = d["label"].strip()
            classes[lbl] = classes.get(lbl, 0) + 1

        # --- Dialogue de configuration ---
        dlg = tk.Toplevel(self.root)
        dlg.title("Exporter le dataset")
        dlg.geometry("460x520")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.configure(bg=COLORS["bg_base"])

        tk.Label(dlg, text="\U0001F4E6  Export Dataset ML",
                 font=("Segoe UI", 14, "bold"), bg=COLORS["bg_base"],
                 fg=COLORS["text_primary"]).pack(pady=(16, 2))
        summary = "  \u00b7  ".join(f"{l} ({n})" for l, n in sorted(classes.items()))
        tk.Label(dlg, text=f"{len(labeled)} images  \u2014  {summary}",
                 font=("Segoe UI", 8), bg=COLORS["bg_base"],
                 fg=COLORS["text_secondary"], wraplength=420).pack(pady=(0, 8))

        # ── Card 1: Image settings ──
        c1 = tk.LabelFrame(dlg, text=" Paramètres image ", font=("Segoe UI", 10, "bold"),
                           bg=COLORS["bg_panel"], fg=COLORS["text_primary"], padx=16, pady=10,
                           highlightbackground=COLORS["border"], highlightthickness=1, bd=0)
        c1.pack(fill="x", padx=18, pady=(0, 8))

        # Target size
        r0 = tk.Frame(c1, bg=COLORS["bg_panel"])
        r0.pack(fill="x", pady=2)
        tk.Label(r0, text="Taille cible :", font=("Segoe UI", 9),
                 bg=COLORS["bg_panel"], fg=COLORS["text_primary"]).pack(side="left")
        size_var = tk.StringVar(value="224 × 224")
        ttk.Combobox(r0, textvariable=size_var,
                     values=["Taille originale", "224 × 224", "256 × 256",
                             "299 × 299", "512 × 512"],
                     state="readonly", width=16).pack(side="right")

        # Format
        r1 = tk.Frame(c1, bg=COLORS["bg_panel"])
        r1.pack(fill="x", pady=2)
        tk.Label(r1, text="Format :", font=("Segoe UI", 9),
                 bg=COLORS["bg_panel"], fg=COLORS["text_primary"]).pack(side="left")
        fmt_var = tk.StringVar(value="JPEG")
        ttk.Combobox(r1, textvariable=fmt_var, values=["JPEG", "PNG"],
                     state="readonly", width=16).pack(side="right")

        # ── Card 2: Split ──
        c2 = tk.LabelFrame(dlg, text=" Split train / val / test ", font=("Segoe UI", 10, "bold"),
                           bg=COLORS["bg_panel"], fg=COLORS["text_primary"], padx=16, pady=10,
                           highlightbackground=COLORS["border"], highlightthickness=1, bd=0)
        c2.pack(fill="x", padx=18, pady=(0, 8))

        split_var = tk.BooleanVar(value=True)
        tk.Checkbutton(c2, text="Activer le split automatique",
                       variable=split_var, bg=COLORS["bg_panel"],
                       font=("Segoe UI", 9), fg=COLORS["text_primary"],
                       activebackground=COLORS["bg_panel"]).pack(anchor="w")

        split_frame = tk.Frame(c2, bg=COLORS["bg_panel"])
        split_frame.pack(fill="x", pady=(6, 0))
        tk.Label(split_frame, text="Train %", font=("Segoe UI", 9),
                 bg=COLORS["bg_panel"], fg=COLORS["text_secondary"]).pack(side="left")
        train_var = tk.StringVar(value="70")
        tk.Spinbox(split_frame, from_=50, to=90, increment=5,
                   textvariable=train_var, width=4,
                   font=("Segoe UI", 9)).pack(side="left", padx=(4, 12))
        tk.Label(split_frame, text="Val %", font=("Segoe UI", 9),
                 bg=COLORS["bg_panel"], fg=COLORS["text_secondary"]).pack(side="left")
        val_var = tk.StringVar(value="15")
        tk.Spinbox(split_frame, from_=5, to=30, increment=5,
                   textvariable=val_var, width=4,
                   font=("Segoe UI", 9)).pack(side="left", padx=(4, 12))
        tk.Label(split_frame, text="Test = reste", font=("Segoe UI", 8),
                 bg=COLORS["bg_panel"], fg=COLORS["text_muted"]).pack(side="left")

        # ── Card 3: Augmentation ──
        c3 = tk.LabelFrame(dlg, text=" Data Augmentation ", font=("Segoe UI", 10, "bold"),
                           bg=COLORS["bg_panel"], fg=COLORS["text_primary"], padx=16, pady=10,
                           highlightbackground=COLORS["border"], highlightthickness=1, bd=0)
        c3.pack(fill="x", padx=18, pady=(0, 8))

        aug_var = tk.BooleanVar(value=True)
        tk.Checkbutton(c3, text="Augmenter le set d'entra\u00eenement (\u00d73)",
                       variable=aug_var, bg=COLORS["bg_panel"],
                       font=("Segoe UI", 9), fg=COLORS["text_primary"],
                       activebackground=COLORS["bg_panel"]).pack(anchor="w")
        tk.Label(c3, text="Flip horizontal \u00b7 Rotation \u00b115\u00b0 \u00b7 Brightness/Contrast jitter",
                 font=("Segoe UI", 8), bg=COLORS["bg_panel"],
                 fg=COLORS["text_muted"]).pack(anchor="w", pady=(2, 0))

        # ── Card 4: Extras ──
        csv_var = tk.BooleanVar(value=True)
        tk.Checkbutton(dlg, text="Inclure annotations.csv",
                       variable=csv_var, bg=COLORS["bg_base"],
                       font=("Segoe UI", 9), fg=COLORS["text_primary"],
                       activebackground=COLORS["bg_base"]).pack(anchor="w", padx=22, pady=(4, 0))

        # ── Buttons ──
        result = {"go": False}
        def on_export():
            result["go"] = True
            dlg.destroy()

        bf = tk.Frame(dlg, bg=COLORS["bg_base"])
        bf.pack(fill="x", padx=18, pady=(12, 16))
        tk.Button(bf, text="Annuler", font=("Segoe UI", 10),
                  bg=COLORS["bg_panel"], fg=COLORS["text_secondary"], bd=0, padx=16, pady=6,
                  cursor="hand2", command=dlg.destroy).pack(side="left")
        tk.Button(bf, text="\U0001F4E5  Exporter le dataset",
                  font=("Segoe UI", 10, "bold"),
                  bg=COLORS["accent"], fg="#ffffff", bd=0, padx=20, pady=6,
                  cursor="hand2", command=on_export).pack(side="right")

        dlg.wait_window()
        if not result["go"]:
            return

        out_dir = filedialog.askdirectory(title="Choisir le dossier de destination")
        if not out_dir:
            return

        # ── Parse settings ──
        target_size = None
        s_str = size_var.get()
        if "×" in s_str:
            s = int(s_str.split("×")[0].strip())
            target_size = (s, s)

        ext = ".jpg" if fmt_var.get() == "JPEG" else ".png"
        save_fmt = fmt_var.get()
        do_split = split_var.get()
        do_augment = aug_var.get()
        train_pct = int(train_var.get()) / 100
        val_pct = int(val_var.get()) / 100

        dataset_dir = os.path.join(out_dir, "dataset")

        # ── Split images by class ──
        by_class = {}
        for p, d in labeled.items():
            lbl = d["label"].strip()
            by_class.setdefault(lbl, []).append(p)

        splits = {}  # {path: "train"/"val"/"test"}
        for lbl, paths in by_class.items():
            shuffled = paths[:]
            random.shuffle(shuffled)
            n = len(shuffled)
            if do_split and n >= 3:
                n_train = max(1, int(n * train_pct))
                n_val = max(1, int(n * val_pct))
                n_test = max(0, n - n_train - n_val)
                if n_test == 0:
                    n_val = n - n_train
                for p in shuffled[:n_train]:
                    splits[p] = "train"
                for p in shuffled[n_train:n_train + n_val]:
                    splits[p] = "val"
                for p in shuffled[n_train + n_val:]:
                    splits[p] = "test"
            else:
                for p in shuffled:
                    splits[p] = "train"

        # ── Augmentation helpers ──
        def augment_image(img):
            """Return list of augmented copies (flip, rotation, color jitter)."""
            augmented = []
            # 1: Horizontal flip
            augmented.append(ImageOps.mirror(img))
            # 2: Random-ish rotation + brightness jitter
            rotated = img.rotate(random.uniform(-15, 15), expand=False,
                                 fillcolor=(0, 0, 0))
            bright = ImageEnhance.Brightness(rotated).enhance(random.uniform(0.8, 1.2))
            contrast = ImageEnhance.Contrast(bright).enhance(random.uniform(0.8, 1.2))
            augmented.append(contrast)
            return augmented

        # ── Process & save ──
        count = 0
        aug_count = 0
        errors = []

        for img_path, split_name in splits.items():
            data = labeled[img_path]
            lbl = data["label"].strip()
            safe_label = "".join(
                c if c.isalnum() or c in (" ", "-", "_") else "_"
                for c in lbl).strip()

            if do_split:
                class_dir = os.path.join(dataset_dir, split_name, safe_label)
            else:
                class_dir = os.path.join(dataset_dir, safe_label)
            os.makedirs(class_dir, exist_ok=True)

            base_name = os.path.splitext(os.path.basename(img_path))[0].replace(" ", "_")
            out_path = os.path.join(class_dir, base_name + ext)
            save_kw = {"quality": 95} if save_fmt == "JPEG" else {}

            try:
                img = Image.open(img_path).convert("RGB")
                if target_size:
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                img.save(out_path, **save_kw)
                count += 1

                # Augmentation only on train split
                if do_augment and split_name == "train":
                    for i, aug_img in enumerate(augment_image(img)):
                        aug_path = os.path.join(class_dir, f"{base_name}_aug{i+1}{ext}")
                        aug_img.save(aug_path, **save_kw)
                        aug_count += 1

            except Exception as e:
                errors.append(f"{os.path.basename(img_path)}: {e}")

        # ── annotations.csv ──
        if csv_var.get():
            csv_path = os.path.join(dataset_dir, "annotations.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["fichier", "chemin_relatif", "label", "split",
                                 "qualite", "notes"])
                for img_path, split_name in splits.items():
                    data = labeled[img_path]
                    lbl = data["label"].strip()
                    safe_label = "".join(
                        c if c.isalnum() or c in (" ", "-", "_") else "_"
                        for c in lbl).strip()
                    base_name = os.path.splitext(
                        os.path.basename(img_path))[0].replace(" ", "_") + ext
                    if do_split:
                        rel = f"{split_name}/{safe_label}/{base_name}"
                    else:
                        rel = f"{safe_label}/{base_name}"
                    writer.writerow([
                        os.path.basename(img_path), rel, lbl, split_name,
                        data.get("quality", ""),
                        data.get("notes", ""),
                    ])

        # ── Summary message ──
        # Count per split
        split_counts = {}
        for s in splits.values():
            split_counts[s] = split_counts.get(s, 0) + 1

        msg = f"\u2705 Dataset exporté avec succès !\n\n"
        msg += f"\U0001F4C1 {dataset_dir}\n"
        msg += f"\U0001F5BC {count} images originales  ·  {len(classes)} classes\n"
        if do_split:
            msg += f"\U0001F4CA Split : train={split_counts.get('train',0)}"
            msg += f" · val={split_counts.get('val',0)}"
            msg += f" · test={split_counts.get('test',0)}\n"
        if do_augment:
            msg += f"\U0001F504 +{aug_count} images augmentées (train uniquement)\n"
        if target_size:
            msg += f"\U0001F4D0 Redimensionnées à {target_size[0]}×{target_size[1]}\n"
        msg += f"\U0001F4C4 Format : {save_fmt}\n"
        if errors:
            msg += f"\n\u26A0 {len(errors)} erreur(s) :\n" + "\n".join(errors[:5])

        if do_split:
            msg += "\n\n\U0001F4A1 Structure :\n"
            msg += "  dataset/train/<classe>/\n"
            msg += "  dataset/val/<classe>/\n"
            msg += "  dataset/test/<classe>/\n"
        msg += "\nCompatible : ImageFolder · image_dataset_from_directory · fastai"

        self.root.show_info("Export Dataset", msg)
        self.logger.log("file", "Export dataset",
                        f"{count}+{aug_count} imgs, {len(classes)} classes → {dataset_dir}")

    # --- Édition ---
    def undo(self):
        if self.processor.undo():
            self.refresh_display()
            self.logger.log("edit", "Annuler")

    def redo(self):
        if self.processor.redo():
            self.refresh_display()
            self.logger.log("edit", "Rétablir")

    def reset_image(self):
        if self.processor.reset():
            self.refresh_display()
            self.logger.log("edit", "Réinitialiser l'image")
            
    def remove_from_session(self):
        """Retire l'image courante de la session de travail."""
        path = self.file_manager.get_current_image_path()
        if not path:
            self.root.show_error("Aucune image à retirer.")
            return
        self.annotations.pop(path, None)
        files = self.file_manager.image_files
        idx = self.file_manager.current_index
        if path in files:
            files.remove(path)
        if not files:
            self.processor.current_image = None
            self.processor.image_path = None
            self.root.right_panel.reset_annotation()
            self.root.image_viewer.display_image(None)
            self.root.title(APP_TITLE)
            return
        self.file_manager.current_index = min(idx, len(files) - 1)
        self._load_current_image()
        self.logger.log("edit", "Image retirée", os.path.basename(path))

    # --- Navigation ---
    def next_image(self):
        if self.file_manager.next_image():
            self._load_current_image()
            self.logger.log("navigation", "Image suivante")

    def prev_image(self):
        if self.file_manager.prev_image():
            self._load_current_image()
            self.logger.log("navigation", "Image précédente")
            
    def goto_image(self, idx):
        if not (0 <= idx < len(self.file_manager.image_files)):
            return
        self._save_current_annotation()
        path = self.file_manager.image_files[idx]
        self.file_manager.current_index = idx
        if path and self.processor.load_image(path):
            self._update_title(path)
            if path in self.annotations:
                self.root.right_panel.load_annotation(self.annotations[path])
            else:
                self.root.right_panel.reset_annotation()
            self.refresh_display()

    def _save_current_annotation(self):
        """Persist annotation data for the current image."""
        path = self.processor.image_path
        if path:
            data = self.root.right_panel.get_annotation_data()
            has_data = any(v for k, v in data.items() if k != "status" and v and v != "—")
            has_status = data.get("status", "Non annoté") != "Non annoté"
            if has_data or has_status:
                self.annotations[path] = data

    def _load_current_image(self):
        self._save_current_annotation()
        path = self.file_manager.get_current_image_path()
        if path and self.processor.load_image(path):
            self.root.image_viewer.set_zoom("fit")
            self._update_title(path)
            if path in self.annotations:
                self.root.right_panel.load_annotation(self.annotations[path])
            else:
                self.root.right_panel.reset_annotation()
            self.refresh_display()

    def _update_title(self, path):
        if path == "Mode Galerie":
            self.root.title(f"{APP_TITLE} — Galerie d'images")
            return
        filename = os.path.basename(path) if path else ""
        self.root.title(f"{APP_TITLE} — {filename}" if filename else APP_TITLE)

    # --- Mode Galerie ---
    def toggle_gallery_mode(self):
        self._save_current_annotation()
        self.is_gallery_mode = not self.is_gallery_mode
        self.root.toggle_view_mode(self.is_gallery_mode)
        
        if self.is_gallery_mode:
            self.root.gallery_viewer.load_images(self.file_manager.image_files)
            self._update_title("Mode Galerie")
            self.root.right_panel.reset_annotation()
            self.root.right_panel.configure_batch_mode(len(self.root.gallery_viewer.selected_files))
        else:
            self.root.right_panel.configure_batch_mode(0)
            self._load_current_image()

    def on_gallery_selection_changed(self, selected_paths):
        self.root.right_panel.configure_batch_mode(len(selected_paths))

    def apply_annotation_batch(self):
        if not self.is_gallery_mode:
            return
        selected = self.root.gallery_viewer.selected_files
        if not selected:
            self.root.show_error("Aucune image sélectionnée.")
            return
            
        data = self.root.right_panel.get_annotation_data()
        count = 0
        for path in selected:
            self.annotations[path] = data.copy()
            count += 1
            
        self.root.show_info("Succès", f"Annotations appliquées à {count} image(s).")
        self.logger.log("annotation", "Batch apply", f"{count} images")

    # --- Rafraîchissement centralisé ---
    def refresh_display(self):
        display_img = self.processor.get_display_image()
        self.root.image_viewer.display_image(display_img)
        
        self.root.image_viewer.update_nav_buttons(self.file_manager.has_prev(), self.file_manager.has_next())
        
        info = self.processor.get_info()
        stats = self.file_manager.get_stats()
        if info:
            self.root.status_panel.update_status(info["path"], info["width"], info["height"], info["mode"], stats["current_idx"], stats["total"])
            self.root.image_viewer.update_nav_slider(stats["current_idx"] - 1, stats["total"])
            file_size = 0
            fmt = ""
            if info["path"] and os.path.exists(info["path"]):
                file_size = os.path.getsize(info["path"]) / 1024.0
                fmt = os.path.splitext(info["path"])[1].upper().lstrip(".")
            self.root.right_panel.update_metadata(
                info["width"], info["height"], info["mode"], file_size, fmt)

    # --- Actions UI ---
    def toggle_right_panel(self):
        self.root.toggle_right_panel()

    def toggle_left_toolbar(self):
        self.root.toggle_left_toolbar()

    def toggle_file_explorer(self):
        self.root.toggle_file_explorer()

    def generate_description(self):
        if not self.processor.current_image:
            self.root.show_error("Veuillez charger une image.")
            return
        # Set task to "Décrire l'image" and trigger analysis
        self.root.right_panel.combo_task.set("Décrire l'image")
        self.root.right_panel.txt_prompt.delete("1.0", "end")
        self.run_ia_analysis()

    def run_ia_analysis(self):
        if not self.processor.current_image:
            self.root.show_error("Veuillez charger une image pour analyser.")
            return

        rp = self.root.right_panel
        config = rp.get_ia_config()
        task = rp.get_ia_task()
        prompt = rp.get_ia_prompt()

        if not config.get("api_key"):
            self.root.show_error(
                "Clé API manquante.\n"
                "Cliquez sur ⚙ dans le panneau droit pour configurer.")
            return

        # Build the full prompt from task + user text
        task_prompts = {
            "Classifier l'image": "Classify this image into a single class label. Return only the class name.",
            "Décrire l'image": "Describe this image in detail.",
            "Détecter les objets": "List all objects detected in this image.",
            "Évaluer la qualité": "Rate the quality of this image (Excellent, Good, Acceptable, Poor, Unusable) and explain why.",
            "Générer des tags": "Generate a comma-separated list of relevant tags for this image.",
            "Question libre": "",
        }
        system_prompt = task_prompts.get(task, "")
        full_prompt = f"{system_prompt}\n{prompt}".strip() if prompt else system_prompt

        if not full_prompt:
            self.root.show_error("Veuillez saisir un prompt ou choisir une tâche.")
            return

        # Encode image to base64
        import base64, io
        buf = io.BytesIO()
        img = self.processor.current_image
        fmt = "PNG" if img.mode == "RGBA" else "JPEG"
        img.save(buf, format=fmt)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        mime = f"image/{fmt.lower()}"

        rp.set_ia_response("⏳ Analyse en cours...")
        rp.btn_generate.config(state="disabled")
        self.root.update_idletasks()

        def _do_request():
            try:
                import urllib.request, json as _json
                url = config["url"].rstrip("/")
                if not url.endswith("/chat/completions"):
                    url += "/chat/completions"

                payload = _json.dumps({
                    "model": config["model"],
                    "messages": [
                        {"role": "user", "content": [
                            {"type": "text", "text": full_prompt},
                            {"type": "image_url", "image_url": {
                                "url": f"data:{mime};base64,{b64}"}},
                        ]}
                    ],
                    "max_tokens": 1024,
                }).encode("utf-8")

                req = urllib.request.Request(
                    url, data=payload, method="POST",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {config['api_key']}",
                    })
                with urllib.request.urlopen(req, timeout=60) as resp:
                    body = _json.loads(resp.read().decode("utf-8"))

                answer = body["choices"][0]["message"]["content"].strip()
                self.root.after(0, lambda: _on_success(answer))
            except Exception as e:
                self.root.after(0, lambda err=e: _on_error(err))

        def _on_success(answer):
            rp.set_ia_response(answer)
            if task == "Classifier l'image":
                rp.set_ia_results(answer.split("\n")[0][:60], answer, confidence=90)
            else:
                rp.lbl_sugg.config(text=f"✅ {task}")
            rp.btn_generate.config(state="normal")
            self.logger.log("ia", f"Analyse IA ({task})", config["model"])

        def _on_error(err):
            rp.set_ia_response(f"❌ Erreur :\n{err}")
            rp.btn_generate.config(state="normal")

        threading.Thread(target=_do_request, daemon=True).start()

    # --- Outils Visuels ---
    def set_tool(self, tool_name):
        self.root.image_viewer.set_tool(tool_name)
        
    def tool_action(self, action):
        if self.is_gallery_mode:
            selected = self.root.gallery_viewer.selected_files
            if not selected:
                self.root.show_error("Aucune image sélectionnée.")
                return
            if action == "compress":
                self.root.show_info("Info", "La compression par lot sera active à l'exportation.")
                return
            if not filedialog.askyesno(
                    "Confirmation",
                    f"Appliquer '{action}' sur {len(selected)} image(s) ?\n"
                    "Les fichiers originaux seront modifiés."):
                return
            count = 0
            for path in selected:
                if self.processor.load_image(path):
                    changed = False
                    if action == "rotate":
                        changed = self.processor.rotate(90)
                    elif action == "resize":
                        changed = self.processor.resize(50)
                    elif action == "crop":
                        changed = self.processor.crop()
                    if changed:
                        self.processor.current_image.save(path)
                        count += 1
            if count > 0:
                self.root.show_info("Batch", f"Action '{action}' appliquée sur {count} images.")
                self.root.gallery_viewer.load_images(self.file_manager.image_files)
                self.logger.log("tool", f"Batch {action} ({count} images)")
        else:
            if not self.processor.current_image:
                self.root.show_error("Veuillez d'abord charger une image.")
                return
            changed = False
            if action == "rotate":
                changed = self.processor.rotate(90)
            elif action == "resize":
                changed = self.processor.resize(50)
            elif action == "crop":
                changed = self.processor.crop()
            elif action == "compress":
                self.root.show_info("Info", "L'outil de compression sera actif lors de la sauvegarde.")
                return
            if changed:
                self.refresh_display()
                self.logger.log("tool", f"Action outil : {action}")

    def crop_box(self, box):
        if self.processor.crop(box):
            self.refresh_display()
            self.logger.log("tool", "Recadrage", f"{box}")

    def zoom(self, logic):
        self.root.image_viewer.set_zoom(logic)

    def apply_filter(self, f_type):
        if self.is_gallery_mode:
            selected = self.root.gallery_viewer.selected_files
            if not selected:
                self.root.show_error("Aucune image sélectionnée.")
                return
            if not filedialog.askyesno(
                    "Confirmation",
                    f"Appliquer le filtre '{f_type}' sur {len(selected)} image(s) ?\n"
                    "Les fichiers originaux seront modifiés."):
                return
            count = 0
            for path in selected:
                if self.processor.load_image(path):
                    if self.processor.apply_filter(f_type):
                        self.processor.current_image.save(path)
                        count += 1
            if count > 0:
                self.root.show_info("Batch", f"Filtre '{f_type}' appliqué sur {count} images.")
                self.root.gallery_viewer.load_images(self.file_manager.image_files)
                self.logger.log("filter", f"Batch filter {f_type} ({count} images)")
        else:
            if not self.processor.current_image:
                self.root.show_error("Veuillez d'abord charger une image.")
                return
            if self.processor.apply_filter(f_type):
                self.refresh_display()
                self.logger.log("filter", f"Filtre appliqué : {f_type}")

    def apply_segmentation(self, s_type):
        self.root.show_info("Segmentation", f"L'outil de segmentation ({s_type}) fera l'objet d'un module spécifique.")

    def apply_vis3d(self, v_type):
        self.root.show_info("Visualisation 3D", f"Le module 3D ({v_type}) nécessite une série de coupes médicales (DICOM/NIfTI).")

    # --- Aide ---
    def show_presentation(self): self.root.show_info("À propos", f"{APP_TITLE}\nProjet de préparation au Machine Learning.")
    def show_version(self): self.root.show_info("Version", f"Version {APP_VERSION}")
    def show_author(self): self.root.show_info("Auteur", "Projet développé par l'élève, dirigé par Pr. Brahim BAKKAS.")
    def show_help(self): self.root.show_info("Aide", "Contactez l'assistance technique pour obtenir de l'aide.")

    # --- Rapport ---
    def generate_report(self):
        """Affiche un aperçu professionnel du rapport dans une fenêtre dédiée."""
        stats = self.logger.get_stats()
        report_text = self.logger.generate_report()

        C = {
            "base": COLORS["bg_base"], "surface": COLORS["bg_panel"],
            "panel": COLORS["bg_surface"], "card": COLORS["bg_panel"],
            "elevated": COLORS["bg_panel_light"], "hover": COLORS["bg_hover"],
            "accent": COLORS["accent"], "accent_hover": COLORS["accent_hover"],
            "text": COLORS["text_primary"], "text2": COLORS["text_secondary"],
            "muted": COLORS["text_muted"],
            "border": COLORS["border"], "border_light": COLORS["border_light"],
        }

        win = tk.Toplevel(self.root)
        win.title("Rapport de session \u2014 TkImage Studio")
        win.geometry("760x620")
        win.minsize(620, 420)
        win.configure(bg=C["base"])
        win.transient(self.root)

        # ── Header ──
        hdr = tk.Frame(win, bg=C["panel"], padx=22, pady=16)
        hdr.pack(fill="x")

        tk.Label(hdr, text="\U0001F4CB  Rapport de Session",
                 font=("Segoe UI", 15, "bold"),
                 bg=C["panel"], fg=C["text"]).pack(side="left")

        tk.Label(hdr, text=f"{stats['session_start']:%d/%m/%Y}   \u00b7   "
                           f"Dur\u00e9e : {stats['duration_str']}   \u00b7   "
                           f"{stats['total']} actions",
                 font=("Segoe UI", 9),
                 bg=C["panel"], fg=C["text2"]).pack(side="right")

        # ── Accent line ──
        tk.Frame(win, bg=C["accent"], height=2).pack(fill="x")

        # ── Stats cards row ──
        cards_frame = tk.Frame(win, bg=C["base"], padx=18, pady=14)
        cards_frame.pack(fill="x")

        category_labels = self.logger.CATEGORY_LABELS
        category_icons = self.logger.CATEGORY_ICONS
        counts = stats["counts"]

        for cat, count in sorted(counts.items(), key=lambda x: -x[1])[:5]:
            card = tk.Frame(cards_frame, bg=C["card"], padx=14, pady=10,
                            highlightbackground=C["border_light"],
                            highlightthickness=1)
            card.pack(side="left", padx=(0, 10), fill="x", expand=True)
            icon = category_icons.get(cat, "\u2022")
            label = category_labels.get(cat, cat)
            tk.Label(card, text=f"{icon} {label}",
                     font=("Segoe UI", 9), bg=C["card"],
                     fg=C["text2"]).pack(anchor="w")
            tk.Label(card, text=str(count),
                     font=("Segoe UI", 18, "bold"), bg=C["card"],
                     fg=C["accent"]).pack(anchor="w")

        # ── Report body ──
        body = tk.Frame(win, bg=C["base"])
        body.pack(fill="both", expand=True, padx=18, pady=(6, 0))

        txt = tk.Text(body, wrap="word", font=("Consolas", 9),
                      bg=C["surface"], fg=C["text"],
                      insertbackground=C["text"],
                      bd=0, relief="flat", padx=18, pady=14,
                      highlightthickness=1, highlightbackground=C["border"],
                      highlightcolor=C["accent"])
        txt.insert("1.0", report_text)
        txt.config(state="disabled")

        scrollbar_y = tk.Scrollbar(body, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_y.pack(side="right", fill="y")
        txt.pack(fill="both", expand=True)

        # ── Footer buttons ──
        footer = tk.Frame(win, bg=C["base"], padx=18, pady=12)
        footer.pack(fill="x")

        tk.Button(footer, text="Fermer", font=("Segoe UI", 10),
                  bg=C["card"], fg=C["text2"],
                  activebackground=C["hover"],
                  activeforeground=C["text"], bd=0, padx=18, pady=7,
                  cursor="hand2",
                  command=win.destroy).pack(side="left")

        tk.Button(footer, text="\U0001F4BE  Exporter le rapport (.txt)",
                  font=("Segoe UI", 10, "bold"),
                  bg=C["accent"], fg="#ffffff",
                  activebackground=C["accent_hover"],
                  activeforeground="#ffffff", bd=0, padx=20, pady=7,
                  cursor="hand2",
                  command=lambda: self.export_report()).pack(side="right")

        self.logger.log("file", "Rapport g\u00e9n\u00e9r\u00e9 (aper\u00e7u)")

    def export_report(self):
        """Exporte le rapport dans un fichier texte."""
        file_path = filedialog.asksaveasfilename(
            title="Exporter le rapport",
            defaultextension=".txt",
            filetypes=[("Fichier texte", "*.txt")],
            initialfile=f"rapport_session_{self.logger.session_start:%Y%m%d_%H%M%S}.txt")
        if file_path:
            self.logger.export_report(file_path)
            self.root.show_info("Export", f"Rapport exporté vers :\n{file_path}")
            self.logger.log("file", "Rapport exporté", os.path.basename(file_path))

if __name__ == "__main__":
    app = Application()
    app.run()
