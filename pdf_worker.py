"""Helper script: runs Playwright in its own process to generate PDF from HTML.
Usage: python pdf_worker.py <html_file> <pdf_file> [footer_html_file]
"""
import sys, asyncio, os, traceback
from playwright.async_api import async_playwright

async def html_to_pdf(html_path, pdf_path, footer_path=None):
    if not os.path.exists(html_path):
        print(f"ERROR: HTML file not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    if not html or not html.strip():
        print("ERROR: HTML content is empty", file=sys.stderr)
        sys.exit(1)

    footer_html = None
    if footer_path and os.path.exists(footer_path):
        with open(footer_path, 'r', encoding='utf-8') as f:
            footer_content = f.read()
        if footer_content.strip():
            footer_html = f'''
        <div style="width:100%;font-size:8px;text-align:center;padding:0 18mm;font-family:'Noto Sans Bengali','Nirmala UI',sans-serif;">
            {footer_content}
        </div>
        '''

    # Retry logic: sometimes the browser fails to launch on first attempt
    max_retries = 3
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-software-rasterizer',
                        '--disable-extensions',
                        '--single-process'
                    ]
                )
                try:
                    page = await browser.new_page()
                    await page.set_content(html, wait_until='domcontentloaded', timeout=60000)
                    # Wait for fonts with a generous timeout
                    try:
                        await page.evaluate('document.fonts.ready')
                    except Exception:
                        pass  # font loading is best-effort

                    opts = {
                        'path': pdf_path,
                        'format': 'A4',
                        'margin': {'top': '15mm', 'bottom': '15mm', 'left': '18mm', 'right': '18mm'},
                        'print_background': True
                    }
                    if footer_html:
                        opts['display_header_footer'] = True
                        opts['header_template'] = '<span></span>'
                        opts['footer_template'] = footer_html

                    await page.pdf(**opts)
                    await browser.close()
                    return  # Success, exit the function
                except Exception as inner_err:
                    await browser.close()
                    raise inner_err

        except Exception as e:
            last_error = e
            if attempt < max_retries:
                print(f"PDF worker attempt {attempt} failed: {e}. Retrying...", file=sys.stderr)
                await asyncio.sleep(1)  # Wait before retry
            else:
                print(f"PDF worker failed after {max_retries} attempts: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                sys.exit(1)

    if last_error:
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python pdf_worker.py <html> <pdf> [footer_html]", file=sys.stderr)
        sys.exit(1)
    asyncio.run(html_to_pdf(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
