import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path
from PIL import Image, ImageTk
import io
import requests
from urllib.parse import urljoin


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


class BrowseTab:
    """Tab for browsing and adding new novels"""
    def __init__(self, notebook, data_file):
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Browse")
        
        self.data_file = data_file
        self.novels = []
        self.browse_results = []
        
        self._setup_ui()
        self._load_novels()
    
    def _setup_ui(self):
        """Setup the browse tab UI"""
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Browse Novels", font=("Arial", 14, "bold")).pack(anchor=tk.W)
        
        # Search frame
        search_frame = ttk.LabelFrame(header_frame, text="Search", padding="10")
        search_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(search_frame, text="Search by title or author:").pack(anchor=tk.W)
        
        input_frame = ttk.Frame(search_frame)
        input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.search_entry = ttk.Entry(input_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.search_entry.bind("<Return>", lambda e: self._search_novels())
        
        ttk.Button(
            input_frame,
            text="Search",
            command=self._search_novels
        ).pack(side=tk.LEFT)
        
        # Add by URL section
        url_frame = ttk.LabelFrame(self.frame, text="Add Novel by URL", padding="10")
        url_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        ttk.Label(url_frame, text="Novel URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.url_entry.bind("<Return>", lambda e: self._add_novel_from_url())
        url_frame.columnconfigure(1, weight=1)
        
        ttk.Label(url_frame, text="Novel Name (optional):").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.name_entry = ttk.Entry(url_frame)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.name_entry.bind("<Return>", lambda e: self._add_novel_from_url())
        
        button_frame = ttk.Frame(url_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Add Novel",
            command=self._add_novel_from_url
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Clear Fields",
            command=self._clear_fields
        ).pack(side=tk.LEFT)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.frame, text="Search Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.results_listbox = tk.Listbox(
            results_frame,
            yscrollcommand=scrollbar.set,
            height=12,
            font=("Arial", 10)
        )
        self.results_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.results_listbox.yview)
        
        # Info label
        self.info_label = ttk.Label(self.frame, text="")
        self.info_label.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    def _load_novels(self):
        """Load existing novels from JSON file"""
        self.novels = []
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.novels = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.novels = []
    
    def _search_novels(self):
        """Search for novels (placeholder - can integrate with actual API)"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            messagebox.showwarning("Input Error", "Please enter a search term")
            return
        
        # Clear results
        self.results_listbox.delete(0, tk.END)
        
        # Placeholder search results
        self.browse_results = [
            {"name": f"Sample Novel {i}", "url": f"https://example.com/novel{i}"}
            for i in range(1, 6)
        ]
        
        self.results_listbox.insert(tk.END, "Search feature - ready to integrate with API")
        for result in self.browse_results:
            self.results_listbox.insert(tk.END, f"  {result['name']}")
        
        self.info_label.config(text=f"Found {len(self.browse_results)} results")
    
    def _add_novel_from_url(self):
        """Add a novel using URL and name"""
        url = self.url_entry.get().strip()
        name = self.name_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Input Error", "Please enter a novel URL")
            return
        
        # Validate URL format
        if not url.startswith(("http://", "https://", "www.")):
            messagebox.showwarning("URL Error", "Please enter a valid URL")
            return
        
        # Check for duplicates
        if any(novel["url"] == url for novel in self.novels):
            messagebox.showwarning("Duplicate", "This URL has already been added")
            return
        
        # Add novel
        novel_entry = {"url": url, "name": name if name else "Unnamed"}
        self.novels.append(novel_entry)
        self._save_novels()
        
        # Clear inputs
        self._clear_fields()
        messagebox.showinfo("Success", f"Novel '{novel_entry['name']}' added successfully!")
    
    def _clear_fields(self):
        """Clear input fields"""
        self.url_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.url_entry.focus()
    
    def _save_novels(self):
        """Save novels to JSON file"""
        import os
        os.makedirs(self.data_file.parent, exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.novels, f, indent=2, ensure_ascii=False)


class MainWindow:
    """Main application window with tabs"""
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Novel Tracker")
        self.window.geometry("900x600")
        self.window.minsize(600, 400)
        
        # Data file path
        self.data_file = Path(__file__).parent.parent / "novels_data.json"
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the main window UI"""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.library_tab = LibraryTab(self.notebook, self.data_file)
        self.browse_tab = BrowseTab(self.notebook, self.data_file)
        
        # Bind tab change to refresh library
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _on_tab_changed(self, event):
        """Handle tab change event"""
        selected_tab = self.notebook.select()
        if selected_tab == self.notebook.tabs()[0]:  # Library tab
            self.library_tab.refresh()
    
    def run(self):
        """Run the application"""
        self.window.mainloop()


def launch_gui(root=None):
    """Launch the GUI window"""
    if root:
        # If root is provided, create window as toplevel
        window = tk.Toplevel(root)
        window.title("Novel Tracker")
        window.geometry("900x600")
        
        notebook = ttk.Notebook(window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        data_file = Path(__file__).parent.parent / "novels_data.json"
        
        library_tab = LibraryTab(notebook, data_file)
        browse_tab = BrowseTab(notebook, data_file)
        
        notebook.bind("<<NotebookTabChanged>>", lambda e: library_tab.refresh() if notebook.select() == notebook.tabs()[0] else None)
        
        return type('GUI', (), {'window': window})()
    else:
        app = MainWindow()
        return app


if __name__ == "__main__":
    app = MainWindow()
    app.run()
