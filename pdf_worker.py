"""Helper script: runs Playwright in its own process to generate PDF from HTML.
Usage: python pdf_worker.py <html_file> <pdf_file> [footer_html_file]
"""
import sys, asyncio
from playwright.async_api import async_playwright

async def html_to_pdf(html_path, pdf_path, footer_path=None):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    footer_html = None
    if footer_path:
        with open(footer_path, 'r', encoding='utf-8') as f:
            footer_content = f.read()
        # Playwright footer_template: must use inline styles, content is placed
        # inside a special container. We wrap it with proper centering.
        footer_html = f'''
        <div style="width:100%;font-size:8px;text-align:center;padding:0 18mm;font-family:'Noto Sans Bengali','Nirmala UI',sans-serif;">
            {footer_content}
        </div>
        '''
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.new_page()
        await page.set_content(html, wait_until='networkidle', timeout=30000)
        await page.wait_for_load_state('networkidle')
        await page.evaluate('document.fonts.ready')
        opts = {'path': pdf_path, 'format': 'A4',
                'margin': {'top': '15mm', 'bottom': '15mm', 'left': '18mm', 'right': '18mm'},
                'print_background': True}
        if footer_html:
            opts['display_header_footer'] = True
            opts['header_template'] = '<span></span>'
            opts['footer_template'] = footer_html
        await page.pdf(**opts)
        await browser.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python pdf_worker.py <html> <pdf> [footer_html]", file=sys.stderr)
        sys.exit(1)
    asyncio.run(html_to_pdf(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
