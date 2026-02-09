import tkinter as tk
from tkinter import ttk
from pathlib import Path

from gui.library_tab import LibraryTab
from gui.browse_tab import BrowseTab



class MainWindow:
    """Main application window with tabs"""
   
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Novel Tracker")
        self.window.geometry("900x600")

        self.data_file = Path("data/novels.json")

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.library_tab = LibraryTab(self.notebook, self.data_file)
        self.browse_tab = BrowseTab(self.notebook, self.data_file)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, e):
        self.library_tab.refresh()

    def run(self):
        self.window.mainloop()
