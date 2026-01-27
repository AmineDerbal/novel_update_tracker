import sys
from browser.playwright_client import create_browser


async def scrape_novelupdates():
    playwright, browser, context = await create_browser()
    page = await context.new_page()

    try:
        print("🔄 Navigating to https://www.novelupdates.com/ ...")

        await page.goto(
            "https://www.novelupdates.com/",
            wait_until="domcontentloaded",
            timeout=120_000,
        )

        print("✅ Successfully loaded page")

        title = await page.title()
        print(f"📄 Page title: {title}")

        print(f"🔗 Final URL: {page.url}")

        html = await page.content()
        print("\n📜 HTML (first 2000 chars):\n")
        print(html[:2000])

        headings = await page.query_selector_all("h1, h2, h3")
        print("\n📍 Headings:")
        for i, h in enumerate(headings[:10], 1):
            text = (await h.text_content() or "").strip()
            if text:
                print(f"{i}. {text}")

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}", file=sys.stderr)
        raise

    finally:
        await context.close()
        await browser.close()
        await playwright.stop()
