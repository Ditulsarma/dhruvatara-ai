"""Helper script: runs Playwright in its own process to generate PDF from HTML.
This avoids threading conflicts with Flask's debug mode.
Usage: python pdf_worker.py <html_file_path> <output_pdf_path>
"""
import sys
import asyncio
from playwright.async_api import async_playwright

async def html_to_pdf(html_path: str, pdf_path: str):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.new_page()
        await page.set_content(html, wait_until='networkidle', timeout=30000)
        await page.pdf(
            path=pdf_path, format='A4',
            margin={'top': '15mm', 'bottom': '15mm', 'left': '18mm', 'right': '18mm'},
            print_background=True
        )
        await browser.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python pdf_worker.py <html_file> <pdf_file>", file=sys.stderr)
        sys.exit(1)
    asyncio.run(html_to_pdf(sys.argv[1], sys.argv[2]))
