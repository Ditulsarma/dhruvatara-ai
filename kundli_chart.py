"""
Vedic Astrology Kundli Chart Visualizer using PIL/Pillow.
Supports three styles: Bengali (East Indian), North Indian, and South Indian.
"""

import io
import os
from PIL import Image, ImageDraw, ImageFont

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

_FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

PLANET_NAMES = {
    "ৰ": "ৰবি", "চ": "চন্দ্ৰ", "ম": "মংগল", "বু": "বুধ",
    "বৃ": "বৃহস্পতি", "শু": "শুক্ৰ", "শ": "শনি",
    "ৰা": "ৰাহু", "কে": "কেতু", "লং": "লগ্ন",
}

# Planet short codes for chart display
PLANET_SHORT_DISPLAY = {
    "ৰ": "ৰ", "চ": "চ", "ম": "ম", "বু": "বু",
    "বৃ": "বৃ", "শু": "শু", "শ": "শ",
    "ৰা": "ৰা", "কে": "কে", "লং": "লং",
}

RASI_NAMES = [
    "মেষ", "বৃষ", "মিথুন", "কৰ্কট",
    "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক",
    "ধনু", "মকৰ", "কুম্ভ", "মীন",
]

# Zodiac symbols are left blank as per request
RASI_SYMBOLS = ["", "", "", "", "", "", "", "", "", "", "", ""]

# Assamese/Bengali Numerals for North Indian Chart
RASI_NUMBERS = ["১", "২", "৩", "৪", "৫", "৬", "৭", "৮", "৯", "১০", "১১", "১২"]

# Colors
BG_COLOR = "#FFF8F0"
LINE_COLOR = "#2c3e50"
RASI_COLOR = "#c62828"
PLANET_COLOR = "#1a237e"
ASC_HIGHLIGHT = "#FF6600"


# ═══════════════════════════════════════════════════════════════════════════════
# FONT LOADING
# ═══════════════════════════════════════════════════════════════════════════════

def _find_font_path() -> str:
    """Find best Assamese/Bengali font. kalpurush first."""
    candidates = [
        os.path.join(_FONTS_DIR, "kalpurush.ttf"),
        os.path.join(_FONTS_DIR, "NotoSansBengali-Regular.ttf"),
        os.path.join(_FONTS_DIR, "NotoSansBengali-Bold.ttf"),
        "C:/Windows/Fonts/kalpurush.ttf",
        "C:/Windows/Fonts/Nirmala.ttf",
        "C:/Windows/Fonts/Siyamrupali.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf",
        "/usr/share/fonts/noto/NotoSansBengali-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def _find_bold_font_path() -> str:
    """Find best bold Assamese/Bengali font for planet text."""
    candidates = [
        os.path.join(_FONTS_DIR, "NotoSansBengali-Bold.ttf"),
        os.path.join(_FONTS_DIR, "NirmalaB.ttf"),
        os.path.join(_FONTS_DIR, "kalpurush.ttf"),  # fallback
        "C:/Windows/Fonts/NirmalaB.ttf",
        "C:/Windows/Fonts/NotoSansBengali-Bold.ttf",
        "C:/Windows/Fonts/kalpurush.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf",
        "/usr/share/fonts/noto/NotoSansBengali-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return _find_font_path()  # ultimate fallback

def _load_fonts(scale=1.0):
    """Load all needed font sizes, scaled by chart size factor.
    Planet fonts use bold variant for better readability in small charts."""
    font_path = _find_font_path()
    if font_path is None:
        font_path = "arial.ttf" if os.name == "nt" else "DejaVuSans.ttf"
    bold_path = _find_bold_font_path()

    def _fs(base):
        return max(8, int(base * scale))

    return {
        "rasi": ImageFont.truetype(font_path, _fs(25)),
        "rasi_sm": ImageFont.truetype(font_path, _fs(20)),
        "planet": ImageFont.truetype(bold_path, _fs(28)),
        "planet_sm": ImageFont.truetype(bold_path, _fs(23)),
        "title": ImageFont.truetype(bold_path, _fs(30)),
        "title_sm": ImageFont.truetype(bold_path, _fs(25)),
        "number": ImageFont.truetype(bold_path, _fs(28)),
        "number_sm": ImageFont.truetype(bold_path, _fs(20)),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DRAWING HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_text_centered(draw, xy, text, font, fill):
    """Draw text perfectly centered at (x, y) avoiding clipping bounds."""
    if not text: return
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = xy
    draw.text((x - tw // 2, y - th // 2), text, font=font, fill=fill)

def _draw_text_centered_multi(draw, cx, cy, lines, font, fill, line_spacing=2):
    """Draw multiple lines of planets perfectly centered block at (cx, cy).
    For >3 planets, uses 2-column grid layout to prevent overflow."""
    if not lines:
        return
    n = len(lines)
    if n <= 3:
        # Single column, centered
        total_h = sum([draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines])
        total_h += line_spacing * (n - 1)
        y = cy - total_h // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((cx - tw // 2, y), line, font=font, fill=fill)
            y += th + line_spacing
    else:
        # 2-column grid: split into left and right columns
        mid = (n + 1) // 2  # left column gets the extra if odd
        left_col = lines[:mid]
        right_col = lines[mid:]
        # Measure line heights
        def _line_h(line):
            b = draw.textbbox((0, 0), line, font=font)
            return b[3] - b[1], b[2] - b[0]
        left_heights = [_line_h(l) for l in left_col]
        right_heights = [_line_h(l) for l in right_col]
        left_total = sum(h for h, _ in left_heights) + line_spacing * (len(left_col) - 1)
        right_total = sum(h for h, _ in right_heights) + line_spacing * (len(right_col) - 1)
        total_h = max(left_total, right_total)
        # Column spacing: ~1.5x average char width
        avg_w = sum(w for _, w in left_heights + right_heights) / max(1, len(left_heights) + len(right_heights))
        col_gap = int(avg_w * 0.8)
        # Draw left column
        ly = cy - total_h // 2
        for line, (th, tw) in zip(left_col, left_heights):
            draw.text((cx - col_gap // 2 - tw, ly), line, font=font, fill=fill)
            ly += th + line_spacing
        # Draw right column
        ry = cy - total_h // 2
        for line, (th, tw) in zip(right_col, right_heights):
            draw.text((cx + col_gap // 2, ry), line, font=font, fill=fill)
            ry += th + line_spacing


# ═══════════════════════════════════════════════════════════════════════════════
# BENGALI (EAST INDIAN) CHART — 3x3 grid + split corners
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_bengali_chart(draw, W, H, ascendant_index, planet_data, fonts, scale=1.0, rasi_names=None, planet_short=None):
    if rasi_names is None: rasi_names = RASI_NAMES
    if planet_short is None: planet_short = PLANET_SHORT_DISPLAY
    M = int(40 * scale)
    cell = (min(W, H) - 2 * M) / 3
    X0, Y0 = M, M + (H - min(W, H)) // 2
    lw = max(1, int(3 * scale))

    # Base grid
    draw.rectangle([X0, Y0, X0 + cell * 3, Y0 + cell * 3], outline=LINE_COLOR, width=lw)
    draw.line([(X0 + cell, Y0), (X0 + cell, Y0 + cell * 3)], fill=LINE_COLOR, width=lw)
    draw.line([(X0 + cell * 2, Y0), (X0 + cell * 2, Y0 + cell * 3)], fill=LINE_COLOR, width=lw)
    draw.line([(X0, Y0 + cell), (X0 + cell * 3, Y0 + cell)], fill=LINE_COLOR, width=lw)
    draw.line([(X0, Y0 + cell * 2), (X0 + cell * 3, Y0 + cell * 2)], fill=LINE_COLOR, width=lw)
    
    # Corner Diagonals
    draw.line([(X0, Y0 + cell * 3), (X0 + cell, Y0 + cell * 2)], fill=LINE_COLOR, width=lw)
    draw.line([(X0 + cell * 3, Y0 + cell * 3), (X0 + cell * 2, Y0 + cell * 2)], fill=LINE_COLOR, width=lw)
    draw.line([(X0, Y0), (X0 + cell, Y0 + cell)], fill=LINE_COLOR, width=lw)
    draw.line([(X0 + cell * 3, Y0), (X0 + cell * 2, Y0 + cell)], fill=LINE_COLOR, width=lw)

    # 12 Rasi mapping (0 is always Top-Middle, Counter-Clockwise)
    houses = [
        (X0 + 1.5 * cell, Y0 + 0.5 * cell),    # 0: Aries (মেষ)
        (X0 + 0.65 * cell, Y0 + 0.25 * cell),  # 1: Taurus (বৃষ)
        (X0 + 0.25 * cell, Y0 + 0.65 * cell),  # 2: Gemini (মিথুন)
        (X0 + 0.5 * cell, Y0 + 1.5 * cell),    # 3: Cancer (কর্কট)
        (X0 + 0.25 * cell, Y0 + 2.35 * cell),  # 4: Leo (সিংহ)
        (X0 + 0.65 * cell, Y0 + 2.75 * cell),  # 5: Virgo (কন্যা)
        (X0 + 1.5 * cell, Y0 + 2.5 * cell),    # 6: Libra (তুলা)
        (X0 + 2.35 * cell, Y0 + 2.75 * cell),  # 7: Scorpio (বৃশ্চিক)
        (X0 + 2.75 * cell, Y0 + 2.35 * cell),  # 8: Sagittarius (ধনু)
        (X0 + 2.5 * cell, Y0 + 1.5 * cell),    # 9: Capricorn (মকর)
        (X0 + 2.75 * cell, Y0 + 0.65 * cell),  # 10: Aquarius (কুম্ভ)
        (X0 + 2.35 * cell, Y0 + 0.25 * cell),  # 11: Pisces (মীন)
    ]

    for rasi_idx, (cx, cy) in enumerate(houses):
        if rasi_idx == ascendant_index:
            _draw_text_centered(draw, (cx, cy - 14), "", fonts["planet_sm"], ASC_HIGHLIGHT)
        
        if rasi_idx in planet_data and planet_data[rasi_idx]:
            planet_names = [planet_short.get(p, p) for p in planet_data[rasi_idx]]
            py = cy + 10 if rasi_idx == ascendant_index else cy
            _draw_text_centered_multi(draw, cx, py, planet_names, fonts["planet"], PLANET_COLOR, line_spacing=3)


# ═══════════════════════════════════════════════════════════════════════════════
# NORTH INDIAN CHART — Fixed Geometry & Bengali Numerals Fixed
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_north_indian_chart(draw, W, H, ascendant_index, planet_data, fonts, scale=1.0, rasi_numbers=None, planet_short=None):
    if rasi_numbers is None: rasi_numbers = RASI_NUMBERS
    if planet_short is None: planet_short = PLANET_SHORT_DISPLAY
    M = int(30 * scale)
    S = min(W, H) - 2 * M
    X0, Y0 = M + (W - min(W, H)) // 2, M
    lw = max(1, int(3 * scale))

    # Main Grid (Outer + Corners + Inner Diamond)
    draw.rectangle([X0, Y0, X0 + S, Y0 + S], outline=LINE_COLOR, width=lw)
    draw.line([(X0, Y0 + S), (X0 + S, Y0)], fill=LINE_COLOR, width=lw)
    draw.line([(X0, Y0), (X0 + S, Y0 + S)], fill=LINE_COLOR, width=lw)
    draw.line([(X0 + S // 2, Y0), (X0 + S, Y0 + S // 2)], fill=LINE_COLOR, width=lw)
    draw.line([(X0 + S, Y0 + S // 2), (X0 + S // 2, Y0 + S)], fill=LINE_COLOR, width=lw)
    draw.line([(X0 + S // 2, Y0 + S), (X0, Y0 + S // 2)], fill=LINE_COLOR, width=lw)
    draw.line([(X0, Y0 + S // 2), (X0 + S // 2, Y0)], fill=LINE_COLOR, width=lw)

    # 12 Houses Mapping (H1 is always Top-Middle. Progresses Counter-Clockwise!)
    houses = [
        (X0 + S * 0.50, Y0 + S * 0.25), # H1
        (X0 + S * 0.25, Y0 + S * 0.12), # H2
        (X0 + S * 0.12, Y0 + S * 0.25), # H3
        (X0 + S * 0.25, Y0 + S * 0.50), # H4
        (X0 + S * 0.12, Y0 + S * 0.75), # H5
        (X0 + S * 0.25, Y0 + S * 0.88), # H6
        (X0 + S * 0.50, Y0 + S * 0.75), # H7
        (X0 + S * 0.75, Y0 + S * 0.88), # H8
        (X0 + S * 0.88, Y0 + S * 0.75), # H9
        (X0 + S * 0.75, Y0 + S * 0.50), # H10
        (X0 + S * 0.88, Y0 + S * 0.25), # H11
        (X0 + S * 0.75, Y0 + S * 0.12), # H12
    ]

    for i, (cx, cy) in enumerate(houses):
        rasi_idx = (ascendant_index + i) % 12
        rasi_num_str = rasi_numbers[rasi_idx]
        
        # Adjust Y so text doesn't overlap lines in tight corner spaces
        _draw_text_centered(draw, (cx, cy - 10), rasi_num_str, fonts["number"], RASI_COLOR)
        
        # Draw "লং" (Lagna) specifically in the 1st House box
        if i == 0:
            _draw_text_centered(draw, (cx, cy + 12), "", fonts["planet_sm"], ASC_HIGHLIGHT)

        # Draw Planets
        if rasi_idx in planet_data and planet_data[rasi_idx]:
            planet_names = [planet_short.get(p, p) for p in planet_data[rasi_idx]]
            py = cy + 30 if i == 0 else cy + 12
            _draw_text_centered_multi(draw, cx, py, planet_names, fonts["planet_sm"], PLANET_COLOR, line_spacing=2)


# ═══════════════════════════════════════════════════════════════════════════════
# SOUTH INDIAN CHART — 4x4 grid, empty center
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_south_indian_chart(draw, W, H, ascendant_index, planet_data, fonts, scale=1.0, rasi_names=None, planet_short=None):
    if rasi_names is None: rasi_names = RASI_NAMES
    if planet_short is None: planet_short = PLANET_SHORT_DISPLAY
    M = int(30 * scale)
    S = min(W, H) - 2 * M
    cell = S / 4
    X0, Y0 = M + (W - min(W, H)) // 2, M
    lw = max(1, int(3 * scale))

    # Base Grid
    draw.rectangle([X0, Y0, X0 + S, Y0 + S], outline=LINE_COLOR, width=lw)
    for x in [1, 2, 3]:
        draw.line([(X0 + x * cell, Y0), (X0 + x * cell, Y0 + cell)], fill=LINE_COLOR, width=lw)
        draw.line([(X0 + x * cell, Y0 + 3 * cell), (X0 + x * cell, Y0 + S)], fill=LINE_COLOR, width=lw)
    for y in [1, 2, 3]:
        draw.line([(X0, Y0 + y * cell), (X0 + cell, Y0 + y * cell)], fill=LINE_COLOR, width=lw)
        draw.line([(X0 + 3 * cell, Y0 + y * cell), (X0 + S, Y0 + y * cell)], fill=LINE_COLOR, width=lw)
    draw.rectangle([X0 + cell, Y0 + cell, X0 + 3 * cell, Y0 + 3 * cell], outline=LINE_COLOR, width=lw)

    # 12 Rasi Mapping (Aries is top row, 2nd box. Progresses Clockwise)
    houses = [
        (X0 + 1.5 * cell, Y0 + 0.5 * cell),  # 0: Aries
        (X0 + 2.5 * cell, Y0 + 0.5 * cell),  # 1: Taurus
        (X0 + 3.5 * cell, Y0 + 0.5 * cell),  # 2: Gemini
        (X0 + 3.5 * cell, Y0 + 1.5 * cell),  # 3: Cancer 
        (X0 + 3.5 * cell, Y0 + 2.5 * cell),  # 4: Leo 
        (X0 + 3.5 * cell, Y0 + 3.5 * cell),  # 5: Virgo 
        (X0 + 2.5 * cell, Y0 + 3.5 * cell),  # 6: Libra 
        (X0 + 1.5 * cell, Y0 + 3.5 * cell),  # 7: Scorpio 
        (X0 + 0.5 * cell, Y0 + 3.5 * cell),  # 8: Sagittarius 
        (X0 + 0.5 * cell, Y0 + 2.5 * cell),  # 9: Capricorn 
        (X0 + 0.5 * cell, Y0 + 1.5 * cell),  # 10: Aquarius 
        (X0 + 0.5 * cell, Y0 + 0.5 * cell),  # 11: Pisces 
    ]

    for rasi_idx, (cx, cy) in enumerate(houses):
        if rasi_idx == ascendant_index:
            # Subtle highlight box for Lagna sign
            pad = 5
            draw.rectangle(
                [cx - cell / 2 + pad, cy - cell / 2 + pad, cx + cell / 2 - pad, cy + cell / 2 - pad],
                outline=ASC_HIGHLIGHT, width=2
            )
            _draw_text_centered(draw, (cx, cy - 22), "", fonts["planet_sm"], ASC_HIGHLIGHT)

        # Print Text Name of Rasi (মেষ, বৃষ, etc)
        _draw_text_centered(draw, (cx, cy - 8), RASI_NAMES[rasi_idx], fonts["rasi_sm"], RASI_COLOR)
        
        # Planets
        if rasi_idx in planet_data and planet_data[rasi_idx]:
            planet_names = [PLANET_SHORT_DISPLAY.get(p, p) for p in planet_data[rasi_idx]]
            _draw_text_centered_multi(draw, cx, cy + 16, planet_names, fonts["planet_sm"], PLANET_COLOR, line_spacing=2)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXPORT LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

def draw_kundli_chart(
    style: str = "bengali",
    ascendant_index: int = 0,
    planet_data: dict = None,
    title: str = "",
    width: int = 700,
    height: int = 700,
    lang: str = "as",
) -> io.BytesIO:
    if planet_data is None: planet_data = {}

    # Get i18n names
    try:
        from prediction_i18n import (
            get_kundli_planet_name_i18n, get_kundli_planet_short_i18n,
            get_kundli_rashi_name_i18n, get_kundli_rashi_number_i18n
        )
        _planet_names = {k: get_kundli_planet_name_i18n(k, lang) for k in PLANET_NAMES}
        _planet_short = {k: get_kundli_planet_short_i18n(k, lang) for k in PLANET_SHORT_DISPLAY}
        _rasi_names = [get_kundli_rashi_name_i18n(i, lang) for i in range(12)]
        _rasi_numbers = [get_kundli_rashi_number_i18n(i, lang) for i in range(12)]
    except ImportError:
        _planet_names = PLANET_NAMES
        _planet_short = PLANET_SHORT_DISPLAY
        _rasi_names = RASI_NAMES
        _rasi_numbers = RASI_NUMBERS

    # Scale fonts and geometry proportionally to chart size (reference: 700px)
    ref = 700.0
    scale = min(width, height) / ref
    fonts = _load_fonts(scale)
    title_h = int(50 * scale) if title else 0
    img = Image.new("RGB", (width, height + title_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    if title:
        _draw_text_centered(draw, (width // 2, title_h // 2), title, fonts["title"], "#1a237e")

    chart_img = Image.new("RGB", (width, height), BG_COLOR)
    chart_draw = ImageDraw.Draw(chart_img)

    if style == "bengali":
        _draw_bengali_chart(chart_draw, width, height, ascendant_index, planet_data, fonts, scale, _rasi_names, _planet_short)
    elif style == "north":
        _draw_north_indian_chart(chart_draw, width, height, ascendant_index, planet_data, fonts, scale, _rasi_numbers, _planet_short)
    elif style == "south":
        _draw_south_indian_chart(chart_draw, width, height, ascendant_index, planet_data, fonts, scale, _rasi_names, _planet_short)

    img.paste(chart_img, (0, title_h))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def draw_all_styles(
    ascendant_index: int = 0,
    planet_data: dict = None,
    width: int = 2100,
    height: int = 700,
    lang: str = "as",
) -> io.BytesIO:
    if planet_data is None: 
        planet_data = {}

    # Get i18n names
    try:
        from prediction_i18n import (
            get_kundli_planet_short_i18n, get_kundli_rashi_name_i18n, get_kundli_rashi_number_i18n
        )
        _planet_short = {k: get_kundli_planet_short_i18n(k, lang) for k in PLANET_SHORT_DISPLAY}
        _rasi_names = [get_kundli_rashi_name_i18n(i, lang) for i in range(12)]
        _rasi_numbers = [get_kundli_rashi_number_i18n(i, lang) for i in range(12)]
    except ImportError:
        _planet_short = PLANET_SHORT_DISPLAY
        _rasi_names = RASI_NAMES
        _rasi_numbers = RASI_NUMBERS

    chart_w = width // 3
    chart_h = height - 50

    ref = 700.0
    scale = min(chart_w, chart_h) / ref
    fonts = _load_fonts(scale)

    # Create the main wide canvas
    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # i18n style labels
    style_labels = {
        'as': [("bengali", "বঙালী আৰ্হি (East Indian)"), ("north", "উত্তৰ ভাৰতীয় (North Indian)"), ("south", "দক্ষিণ ভাৰতীয় (South Indian)")],
        'bn': [("bengali", "বাংলা আর্হি (East Indian)"), ("north", "উত্তর ভারতীয় (North Indian)"), ("south", "দক্ষিণ ভারতীয় (South Indian)")],
        'hi': [("bengali", "बंगाली शैली (East Indian)"), ("north", "उत्तर भारतीय (North Indian)"), ("south", "दक्षिण भारतीय (South Indian)")],
        'en': [("bengali", "Bengali Style (East Indian)"), ("north", "North Indian Style"), ("south", "South Indian Style")],
    }
    styles = style_labels.get(lang, style_labels['as'])

    for idx, (style, label) in enumerate(styles):
        x_offset = idx * chart_w
        
        # Draw the title for each section
        _draw_text_centered(draw, (x_offset + chart_w // 2, 25), label, fonts["title_sm"], "#1a237e")

        # Create a sub-image for the specific chart
        chart_img = Image.new("RGB", (chart_w, chart_h), BG_COLOR)
        chart_draw = ImageDraw.Draw(chart_img)

        # Draw the respective chart on the sub-image
        if style == "bengali":
            _draw_bengali_chart(chart_draw, chart_w, chart_h, ascendant_index, planet_data, fonts, scale, _rasi_names, _planet_short)
        elif style == "north":
            _draw_north_indian_chart(chart_draw, chart_w, chart_h, ascendant_index, planet_data, fonts, scale, _rasi_numbers, _planet_short)
        elif style == "south":
            _draw_south_indian_chart(chart_draw, chart_w, chart_h, ascendant_index, planet_data, fonts, scale, _rasi_names, _planet_short)

        # Paste the finished chart sub-image onto the main wide canvas
        img.paste(chart_img, (x_offset, 50))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    sample_data = {
        0: ["ৰ", "চ"],
        3: ["ম"],
        5: ["বৃ"],
        7: ["শু", "শ"],
        10: ["ৰা"],
        11: ["কে"],
    }

    for style in ["bengali", "north", "south"]:
        buf = draw_kundli_chart(
            style=style,
            ascendant_index=3,
            planet_data=sample_data,
            title=f"কুণ্ডলী চক্ৰ — {style.title()} Style",
        )
        with open(f"test_chart_{style}.png", "wb") as f:
            f.write(buf.read())
        print(f"Saved test_chart_{style}.png successfully.")

    buf = draw_all_styles(ascendant_index=3, planet_data=sample_data)
    with open("test_chart_all_styles.png", "wb") as f:
        f.write(buf.read())
    print("Saved test_chart_all_styles.png successfully.")
    print("\nDone!")