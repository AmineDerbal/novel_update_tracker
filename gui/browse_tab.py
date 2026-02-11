import tkinter as tk
from tkinter import ttk, messagebox
import json
import asyncio
from scraper.browse_novels import browse_novels

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
        
        ttk.Button(
            input_frame,
            text="Check Browse Novels",
            command=self._check_browse_novels
        ).pack(side=tk.LEFT, padx=(5, 0))
        
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
    
    def _check_browse_novels(self):
        """Run the browse novels scraper"""
        self.info_label.config(text="🔄 Fetching novels from NovelUpdates...")
        self.frame.update()
        
        try:
            novels =asyncio.run(browse_novels())
            self.info_label.config(text="✅ Browse novels check completed!")
            messagebox.showinfo("Success", "Browse novels scraper completed successfully!")
        except Exception as e:
            self.info_label.config(text="❌ Error fetching novels")
            messagebox.showerror("Error", f"Failed to fetch novels: {str(e)}")
    
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