import tkinter as tk
from tkinter import ttk, messagebox
import json

from gui.novel_card import NovelCard

class LibraryTab:
    """Tab for displaying the user's novel library as cards"""
    def __init__(self, notebook, data_file):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Library")
        
        self.data_file = data_file
        self.novels = []
        
        self._setup_ui()
        self._load_novels()
    
    def _setup_ui(self):
        """Setup the library tab UI"""
        # Header frame
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="My Novels", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        
        # Search frame
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._filter_novels())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Canvas with scrollbar for cards
        canvas_frame = ttk.Frame(self.frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(canvas_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            bg="white",
            yscrollcommand=scrollbar.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        # Frame inside canvas to hold cards
        self.cards_frame = tk.Frame(self.canvas, bg="white")
        self.canvas_window = self.canvas.create_window(
            0, 0, window=self.cards_frame, anchor=tk.NW
        )
        
        # Bind mousewheel to canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Update scroll region
        self.cards_frame.bind(
            "<Configure>",
            lambda e: self.canvas.config(scrollregion=self.canvas.bbox("all"))
        )
        
        # Info label
        self.info_label = ttk.Label(self.frame, text="")
        self.info_label.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _load_novels(self):
        """Load novels from JSON file"""
        self.novels = []
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.novels = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.novels = []
        
        self._display_novels()
    
    def _filter_novels(self):
        """Filter novels based on search term"""
        self._display_novels()
    
    def _display_novels(self):
        """Display novels as cards"""
        # Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        search_term = self.search_var.get().lower()
        filtered_novels = [
            n for n in self.novels
            if search_term in n.get("name", "").lower() or
               search_term in n.get("url", "").lower()
        ]
        
        if not filtered_novels:
            no_novels_label = tk.Label(
                self.cards_frame,
                text="No novels found" if search_term else "No novels in library",
                font=("Arial", 12),
                fg="gray",
                bg="white"
            )
            no_novels_label.pack(pady=50)
        else:
            # Create a grid of cards
            grid_frame = tk.Frame(self.cards_frame, bg="white")
            grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            cards_per_row = 4
            for i, novel in enumerate(filtered_novels):
                row = i // cards_per_row
                col = i % cards_per_row
                
                card = NovelCard(
                    grid_frame,
                    novel,
                    on_click=self._on_novel_click
                )
                card.frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Configure grid weights
            for i in range(cards_per_row):
                grid_frame.columnconfigure(i, weight=1)
        
        # Update info label
        total = len(self.novels)
        displayed = len(filtered_novels)
        if search_term:
            self.info_label.config(
                text=f"Showing {displayed} of {total} novels"
            )
        else:
            self.info_label.config(text=f"Total novels: {total}")
    
    def _on_novel_click(self, novel_data):
        """Handle novel card click"""
        messagebox.showinfo(
            "Novel Info",
            f"Title: {novel_data.get('name', 'Unnamed')}\n\n"
            f"URL: {novel_data.get('url', 'N/A')}"
        )
    
    def refresh(self):
        """Refresh the library display"""
        self._load_novels()