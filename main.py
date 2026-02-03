import asyncio
import sys
from gui.main_window import MainWindow


async def scrape_with_gui():
    """Run scraper with GUI for managing novels"""
    from scraper.novelupdates import scrape_novelupdates
    try:
        await scrape_novelupdates()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)


def main():
    """Main entry point - launches the GUI"""
    app = MainWindow()
    app.run()
    ##asyncio.run(scrape_with_gui())


if __name__ == "__main__":
    main()
