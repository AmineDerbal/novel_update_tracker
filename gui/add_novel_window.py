import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from pathlib import Path


class AddNovelWindow:
    def __init__(self, root=None):
        if root:
            self.window = tk.Toplevel(root)
        else:
            self.window = tk.Tk()

        self.window.title("Add NovelUpdates Novel Links")
        self.window.geometry("700x600")
        self.window.resizable(True, True)

        # Data file path
        self.data_file = Path(__file__).parent.parent / "novels_data.json"

        self.setup_ui()
        self.load_novels()

    def setup_ui(self):
        """Create the UI elements"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Add Novel Link", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)

        # URL label and input
        ttk.Label(input_frame, text="Novel URL:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.url_entry = ttk.Entry(input_frame)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.url_entry.bind("<Return>", lambda e: self.add_novel())
        input_frame.columnconfigure(1, weight=1)

        # Name label and input
        ttk.Label(input_frame, text="Novel Name (optional):").grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.name_entry = ttk.Entry(input_frame)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        self.name_entry.bind("<Return>", lambda e: self.add_novel())

        # Button frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Button(button_frame, text="Add Novel", command=self.add_novel).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields).pack(
            side=tk.LEFT
        )

        # Novels list section
        list_frame = ttk.LabelFrame(main_frame, text="Added Novels", padding="10")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.novels_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            height=12,
            font=("Arial", 10),
            activestyle="none",
        )
        self.novels_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.novels_listbox.yview)

        # Delete button
        delete_frame = ttk.Frame(main_frame)
        delete_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(
            delete_frame, text="Delete Selected Novel", command=self.delete_novel
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            delete_frame, text="Clear All Novels", command=self.clear_all_novels
        ).pack(side=tk.LEFT)

        # Info label
        self.info_label = ttk.Label(main_frame, text="", foreground="blue")
        self.info_label.grid(row=4, column=0, sticky=(tk.W, tk.E))

    def load_novels(self):
        """Load novels from JSON file"""
        self.novels = []
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.novels = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.novels = []

        self.update_listbox()

    def save_novels(self):
        """Save novels to JSON file"""
        os.makedirs(self.data_file.parent, exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.novels, f, indent=2, ensure_ascii=False)

    def update_listbox(self):
        """Update the novels listbox display"""
        self.novels_listbox.delete(0, tk.END)
        for i, novel in enumerate(self.novels):
            name = novel.get("name", "Unnamed")
            url = novel.get("url", "No URL")
            display_text = f"[{i + 1}] {name}" if name != "Unnamed" else f"[{i + 1}] {url}"
            self.novels_listbox.insert(tk.END, display_text)

        self.info_label.config(
            text=f"Total novels: {len(self.novels)}", foreground="blue"
        )

    def add_novel(self):
        """Add a new novel"""
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
        self.save_novels()
        self.update_listbox()

        # Clear inputs
        self.clear_fields()
        messagebox.showinfo("Success", f"Novel '{novel_entry['name']}' added successfully!")

    def delete_novel(self):
        """Delete selected novel"""
        selection = self.novels_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a novel to delete")
            return

        index = selection[0]
        deleted_novel = self.novels.pop(index)
        self.save_novels()
        self.update_listbox()
        messagebox.showinfo(
            "Deleted", f"Novel '{deleted_novel.get('name')}' has been removed"
        )

    def clear_fields(self):
        """Clear input fields"""
        self.url_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.url_entry.focus()

    def clear_all_novels(self):
        """Clear all novels with confirmation"""
        if not self.novels:
            messagebox.showinfo("Empty", "No novels to clear")
            return

        if messagebox.askyesno(
            "Confirm", f"Delete all {len(self.novels)} novels? This cannot be undone."
        ):
            self.novels.clear()
            self.save_novels()
            self.update_listbox()
            messagebox.showinfo("Cleared", "All novels have been removed")


def launch_gui(root=None):
    """Launch the GUI window"""
    return AddNovelWindow(root)


if __name__ == "__main__":
    app = AddNovelWindow()
    app.window.mainloop()
