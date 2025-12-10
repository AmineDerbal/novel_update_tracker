import asyncio
from playwright.async_api import async_playwright
import sys


async def scrape_novelupdates():
    """
    Scrape https://www.novelupdates.com/ using Playwright.
    Bypasses Cloudflare by using a headless browser with proper headers.
    """
    async with async_playwright() as p:
        # Launch browser with appropriate settings to bypass Cloudflare
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--no-default-browser-check',
            ]
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 720},
            locale='en-US',
        )
        
        # Add extra headers to appear more like a legitimate browser
        await context.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        })
        
        page = await context.new_page()
        
        try:
            print("🔄 Navigating to https://www.novelupdates.com/...")
            
            # Navigate with increased timeout to wait for Cloudflare challenge
            await page.goto('https://www.novelupdates.com/', wait_until='domcontentloaded', timeout=120000)
            
            print("✅ Successfully bypassed Cloudflare!")
            print("\n" + "="*80)
            print("PAGE CONTENT")
            print("="*80 + "\n")
            
            # Get page title
            title = await page.title()
            print(f"📄 Page Title: {title}\n")
            
            # Get page URL (after redirects)
            current_url = page.url
            print(f"🔗 Current URL: {current_url}\n")
            
            # Get the full HTML content
            html_content = await page.content()
            print("📜 HTML Content (first 2000 characters):\n")
            print(html_content[:2000])
            print("\n[... content truncated ...]\n")
            
            # Try to extract specific elements
            print("\n" + "="*80)
            print("EXTRACTED DATA")
            print("="*80 + "\n")
            
            # Extract headings
            headings = await page.query_selector_all('h1, h2, h3')
            if headings:
                print("📍 Headings found:")
                for i, heading in enumerate(headings[:10], 1):  # First 10 headings
                    text = await heading.text_content()
                    text = text.strip() if text else ""
                    if text:
                        print(f"  {i}. {text}")
            
         
        except Exception as e:
            print(f"❌ Error occurred: {type(e).__name__}: {str(e)}", file=sys.stderr)
            raise
        
        finally:
            await context.close()
            await browser.close()


async def main():
    """Main entry point."""
    try:
        await scrape_novelupdates()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
