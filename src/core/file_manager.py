import os

class FileManager:
    def __init__(self):
        self.current_folder = None
        self.image_files = []
        self.current_index = -1
        self.supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tif', '.tiff')

    def load_folder(self, folder_path):
        if not folder_path or not os.path.isdir(folder_path):
            return False
            
        self.current_folder = folder_path
        self.image_files = []
        
        for file in sorted(os.listdir(folder_path)):
            if file.lower().endswith(self.supported_extensions):
                self.image_files.append(os.path.join(folder_path, file))
                
        if self.image_files:
            self.current_index = 0
            return True
            
        return False

    def get_current_image_path(self):
        if 0 <= self.current_index < len(self.image_files):
            return self.image_files[self.current_index]
        return None

    def set_current_image(self, path):
        # Si c'est une image seule (hors dossier)
        if path in self.image_files:
            self.current_index = self.image_files.index(path)
        else:
            self.image_files = [path]
            self.current_index = 0
            self.current_folder = os.path.dirname(path)

    def next_image(self):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            return self.get_current_image_path()
        return None

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            return self.get_current_image_path()
        return None

    def has_next(self):
        return self.current_index < len(self.image_files) - 1

    def has_prev(self):
        return self.current_index > 0
        
    def get_stats(self):
        return {
            "current_idx": self.current_index + 1,
            "total": len(self.image_files)
        }
