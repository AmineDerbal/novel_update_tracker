import asyncio
import sys
from scraper.novelupdates import scrape_novelupdates


async def main():
    try:
        await scrape_novelupdates()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
