import asyncio
import sys
from gui.main_window import MainWindow


def main():
    """Main entry point - launches the GUI"""
    app = MainWindow()
    app.run()
    

if __name__ == "__main__":
    main()
