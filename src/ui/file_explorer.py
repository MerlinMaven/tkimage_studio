import tkinter as tk
from tkinter import ttk
import os
from src.utils.constants import COLORS, FONTS


class FileExplorer(ttk.Frame):
    def __init__(self, parent, callbacks=None):
        super().__init__(parent, style="Panel.TFrame", width=240)
        self.pack_propagate(False)
        self.callbacks = callbacks or {}

        # ── Header ──
        header = ttk.Frame(self, style="Panel.TFrame")
        header.pack(fill=tk.X, padx=14, pady=(14, 0))
        ttk.Label(header, text="\U0001F4C2  EXPLORATEUR",
                  style="Header.TLabel").pack(side=tk.LEFT)

        btn_box = ttk.Frame(header, style="Panel.TFrame")
        btn_box.pack(side=tk.RIGHT)
        ttk.Button(btn_box, text="\u21bb", style="Ghost.TButton", width=3,
                   command=self.refresh_tree).pack(side=tk.LEFT)
        ttk.Button(btn_box, text="\u2715", style="Ghost.TButton", width=3,
                   command=self.callbacks.get("toggle_file_explorer")).pack(
            side=tk.LEFT, padx=(2, 0))

        ttk.Frame(self, style="Accent.TFrame", height=2).pack(
            fill=tk.X, padx=14, pady=(8, 0))

        # ── Treeview ──
        tree_frame = ttk.Frame(self, style="Panel.TFrame")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.tree = ttk.Treeview(tree_frame, style="Explorer.Treeview", show="tree")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical",
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_node)

        self.current_root_path = os.getcwd()
        self.populate_tree(self.current_root_path)

    def set_root_path(self, path):
        if os.path.exists(path):
            self.current_root_path = path
            self.populate_tree(path)

    def refresh_tree(self):
        self.populate_tree(self.current_root_path)

    def populate_tree(self, path):
        for item in self.tree.get_children():
            self.tree.delete(item)
        display = os.path.basename(path) or path
        root_node = self.tree.insert("", "end", text=display, open=True,
                                     values=(path, "directory"))
        self._insert_children(root_node, path)

    def _insert_children(self, parent, path):
        try:
            entries = sorted(os.scandir(path),
                             key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                if entry.name.startswith('.'):
                    continue
                is_dir = entry.is_dir()
                node = self.tree.insert(
                    parent, "end", text=entry.name,
                    values=(entry.path, "directory" if is_dir else "file"))
                if is_dir:
                    self.tree.insert(node, "end", text="\u2026")
        except (PermissionError, OSError):
            pass

    def on_open_node(self, event):
        item = self.tree.focus()
        values = self.tree.item(item, "values")
        if values and values[1] == "directory":
            children = self.tree.get_children(item)
            if len(children) == 1 and self.tree.item(children[0], "text") == "\u2026":
                self.tree.delete(children[0])
                self._insert_children(item, values[0])

    def on_select_node(self, event):
        item = self.tree.focus()
        values = self.tree.item(item, "values")
        if values and values[1] == "file":
            file_path = values[0]
            if file_path.lower().endswith(
                    ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tif', '.tiff')):
                if "on_file_select" in self.callbacks:
                    self.callbacks["on_file_select"](file_path)
