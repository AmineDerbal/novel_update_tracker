import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path

class NovelCard:
    """A card widget displaying a novel with image and title"""
    def __init__(self, parent, novel_data, on_click=None):
        self.novel_data = novel_data
        self.on_click = on_click
        
        self.frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=2)
        self.frame.pack_propagate(False)
        self.frame.configure(width=160, height=220)
        
        # Bind click events
        self.frame.bind("<Button-1>", self._on_click)
        
        # Image label
        self.image_label = tk.Label(self.frame, bg="lightgray", width=20, height=10)
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 3))
        self.image_label.bind("<Button-1>", self._on_click)
        
        # Load and display image
        self._load_image()
        
        # Title label
        title = novel_data.get("name", "Unnamed")
        self.title_label = tk.Label(
            self.frame,
            text=title,
            bg="white",
            wraplength=150,
            justify=tk.CENTER,
            font=("Arial", 9, "bold")
        )
        self.title_label.pack(fill=tk.X, padx=5, pady=(3, 5))
        self.title_label.bind("<Button-1>", self._on_click)
        
    def _load_image(self):
        """Load and display the novel's image"""
        image_path = self.novel_data.get("image_path")
        
        if image_path and Path(image_path).exists():
            try:
                img = Image.open(image_path)
                img.thumbnail((150, 180), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=photo)
                self.image_label.image = photo  # Keep a reference
            except Exception as e:
                self.image_label.config(text=f"Error loading image\n{str(e)}")
        else:
            self.image_label.config(text="No Image")
    
    def _on_click(self, event=None):
        """Handle card click"""
        if self.on_click:
            self.on_click(self.novel_data)