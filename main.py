import asyncio
import sys
from gui.add_novel_window import launch_gui


async def scrape_with_gui():
    """Run scraper with GUI for managing novels"""
    from scraper.novelupdates import scrape_novelupdates
    try:
        await scrape_novelupdates()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)


def main():
    """Main entry point - launches the GUI"""
    app = launch_gui()
    app.window.mainloop()
    ##asyncio.run(scrape_with_gui())


if __name__ == "__main__":
    main()
