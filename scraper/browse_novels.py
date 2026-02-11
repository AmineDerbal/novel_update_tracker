import sys
from browser.playwright_client import create_browser

async def browse_novels(pg=1):
  playwright, browser, context = await create_browser()
  page = await context.new_page()
  novels_url = "https://www.novelupdates.com/series-finder/?sf=1&org=495,496,497&nt=2444&ge=168,851,1692,560,922&sort=sdate&order=desc"
  url = novels_url if pg <= 1 else f"{novels_url}&pg={pg}"
 
  try:
    print(f"🔄 Navigating to {novels_url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=120_000)
    print("✅ Successfully loaded page")

    page_novels = await page.query_selector_all(".search_main_box_nu")
    novels = []

    for novel in page_novels:
      title = await novel.query_selector(".search_title a")
      title_text = (await title.text_content() or "").strip() if title else "No Title"
      title_url = await title.get_attribute("href") if title else "No URL"
      title_image = await novel.query_selector(".search_img_nu img")
      title_image_url = await title_image.get_attribute("src") if title_image else "No Image"
      novels.append({
        "title": title_text,
        "url": title_url,
        "image_url": title_image_url
      })
      

  except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}", file=sys.stderr)
    raise 
  
  finally:    
    await context.close()
    await browser.close()
    await playwright.stop()

  return novels

  

    