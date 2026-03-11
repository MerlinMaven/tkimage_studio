from PIL import Image, ImageOps, ImageEnhance, ImageFilter

class ImageProcessor:
    def __init__(self):
        self.original_image = None
        self.current_image = None
        self.image_path = None
        self.history = []
        self.redo_stack = []

    def load_image(self, file_path):
        try:
            self.image_path = file_path
            self.original_image = Image.open(file_path).convert("RGB")
            self.current_image = self.original_image.copy()
            self._save_state()
            return True
        except Exception as e:
            print(f"Erreur de chargement: {e}")
            return False

    def get_display_image(self):
        return self.current_image

    def _save_state(self):
        if self.current_image:
            self.history.append(self.current_image.copy())
            self.redo_stack.clear() # Nouvelle action invalide le redo
            if len(self.history) > 15:
                self.history.pop(0)

    # --- Édition ---
    def undo(self):
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.current_image = self.history[-1].copy()
            return True
        return False

    def redo(self):
        if self.redo_stack:
            img = self.redo_stack.pop()
            self.current_image = img.copy()
            self.history.append(img)
            return True
        return False
        
    def reset(self):
        if self.original_image:
            self.current_image = self.original_image.copy()
            self._save_state()
            return True
        return False

    # --- Outils de Base ---
    def rotate(self, angle=90):
        if self.current_image:
            self.current_image = self.current_image.rotate(-angle, expand=True)
            self._save_state()
            return True
        return False

    def resize(self, scale_percent=50):
        if self.current_image:
            w, h = self.current_image.size
            new_w = int(w * scale_percent / 100)
            new_h = int(h * scale_percent / 100)
            self.current_image = self.current_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
            self._save_state()
            return True
        return False

    def crop(self, box=None):
        # Pour l'instant, crop simulé de 10% des bords si pas de box
        if self.current_image:
            w, h = self.current_image.size
            if not box:
                box = (int(w*0.1), int(h*0.1), int(w*0.9), int(h*0.9))
            self.current_image = self.current_image.crop(box)
            self._save_state()
            return True
        return False

    # --- Filtres ---
    def apply_filter(self, f_type):
        if not self.current_image: return False
        
        try:
            if f_type == "grayscale":
                self.current_image = ImageOps.grayscale(self.current_image).convert("RGB")
            elif f_type == "blur":
                self.current_image = self.current_image.filter(ImageFilter.BLUR)
            elif f_type == "sharpen":
                self.current_image = self.current_image.filter(ImageFilter.SHARPEN)
            elif f_type == "contrast":
                enhancer = ImageEnhance.Contrast(self.current_image)
                self.current_image = enhancer.enhance(1.5)
            elif f_type == "brightness":
                enhancer = ImageEnhance.Brightness(self.current_image)
                self.current_image = enhancer.enhance(1.2)
            elif f_type == "invert":
                self.current_image = ImageOps.invert(self.current_image)
            elif f_type == "autocontrast":
                self.current_image = ImageOps.autocontrast(self.current_image)
            elif f_type == "edge_detect":
                self.current_image = self.current_image.filter(ImageFilter.FIND_EDGES)
            elif f_type == "emboss":
                self.current_image = self.current_image.filter(ImageFilter.EMBOSS)
            else:
                return False
                
            self._save_state()
            return True
        except Exception as e:
            print(f"Erreur filtre: {e}")
            return False

    def get_info(self):
        if self.current_image:
            width, height = self.current_image.size
            return {
                "width": width,
                "height": height,
                "mode": self.current_image.mode, 
                "path": self.image_path
            }
        return None
