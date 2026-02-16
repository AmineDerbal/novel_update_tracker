import asyncio
import sys
from gui.main_window import MainWindow
from database.setup import setup_database


def main():
    """Main entry point - launches the GUI"""
    setup_database()
    app = MainWindow()
    app.run()
    

if __name__ == "__main__":
    main()
