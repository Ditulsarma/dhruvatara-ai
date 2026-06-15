"""
ধ্ৰুৱতৰা AI - সন্নাড়ী চক্ৰ ইঞ্জিন (Sannari Chakra Engine)
============================================================
নক্ষত্ৰ সংখ্যাৰ ওপৰত ভিত্তি কৰি সন্নাড়ী চক্ৰ গণনা আৰু SVG নিৰ্মাণ।
৬টা ভাগ: জন্ম, কৰ্ম, সমুদয়, মানস, সাংঘাতিক, বিনাশ।
প্ৰতিটো নক্ষত্ৰৰ বাবে ১-২৭ লৈ চক্ৰীয় ক্ৰমত গণনা।
"""

# ═══════════════════════════════════════════════════════════════
# সন্নাড়ী চক্ৰ গণনা
# ═══════════════════════════════════════════════════════════════

def get_sannari_data(nakshatra_number: int, lang: str = 'as') -> dict:
    """
    নক্ষত্ৰ সংখ্যা (১-২৭) ৰ পৰা সন্নাড়ী চক্ৰৰ ৬টা ভাগ গণনা কৰে।
    Args:
        nakshatra_number: 1-27
        lang: language code (as/bn/hi/en)
    Returns dict with labels and their corresponding nakshatra numbers.
    """
    if nakshatra_number < 1 or nakshatra_number > 27:
        return None

    # Get i18n labels
    try:
        from prediction_i18n import get_sannari_label_i18n
        L = lambda k: get_sannari_label_i18n(k, lang)
    except ImportError:
        L = lambda k: k

    n = nakshatra_number
    janma = n
    karma = ((n - 1) + 9) % 27 + 1
    samudaya = ((n - 1) + 17) % 27 + 1
    manasa = ((n - 1) + 24) % 27 + 1
    sanghatika = ((n - 1) + 15) % 27 + 1
    binasha = ((n - 1) + 22) % 27 + 1

    return {
        "nakshatra_number": n,
        "positions": [
            {"label": L('janma'), "number": janma, "x": 70, "y": 150},
            {"label": L('karma'), "number": karma, "x": 160, "y": 70},
            {"label": L('samudaya'), "number": samudaya, "x": 360, "y": 70},
            {"label": L('manasa'), "number": manasa, "x": 480, "y": 150},
            {"label": L('sanghatika'), "number": sanghatika, "x": 160, "y": 230},
            {"label": L('binasha'), "number": binasha, "x": 360, "y": 230},
        ]
    }


# ═══════════════════════════════════════════════════════════════
# সন্নাড়ী চক্ৰ SVG নিৰ্মাণ
# ═══════════════════════════════════════════════════════════════

def generate_sannari_svg(nakshatra_number: int, nakshatra_name: str = "",
                          width: int = 600, height: int = 300, lang: str = 'as') -> str:
    """
    সন্নাড়ী চক্ৰৰ SVG চিত্ৰ নিৰ্মাণ কৰে।
    """
    data = get_sannari_data(nakshatra_number, lang)
    try:
        from prediction_i18n import get_sannari_label_i18n
        title_label = get_sannari_label_i18n('title', lang)
        nak_no_label = get_sannari_label_i18n('nak_no', lang)
        invalid_label = get_sannari_label_i18n('invalid', lang)
    except ImportError:
        title_label = 'সন্নাড়ী চক্ৰ'
        nak_no_label = 'নক্ষত্ৰ নং'
        invalid_label = 'অবৈধ নক্ষত্ৰ সংখ্যা'

    if data is None:
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 300"><text x="300" y="150" text-anchor="middle" font-size="14" fill="#c62828">{invalid_label}</text></svg>'

    # Ellipse parameters (matching VB.Net: ellipseRect = 30, 30, 560, 255)
    cx = 310   # center x: 30 + 560/2
    cy = 157   # center y: 30 + 255/2
    rx = 280   # radius x: 560/2
    ry = 127   # radius y: 255/2

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">'
    svg += f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>'

    # Draw ellipse
    svg += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#C62828" stroke-width="2"/>'

    # Title
    title = f"{title_label} — {nakshatra_name} ({nak_no_label} {nakshatra_number})"
    svg += f'<text x="{width//2}" y="22" text-anchor="middle" font-size="13" fill="#1a237e" font-weight="bold" font-family="Noto Sans Bengali, Nirmala UI, sans-serif">{title}</text>'

    # Draw each position
    for pos in data["positions"]:
        label = pos["label"]
        number = pos["number"]
        x = pos["x"]
        y = pos["y"]

        # Draw text: "জন্ম(১)" format
        text = f"{label}({number})"
        svg += f'<text x="{x}" y="{y}" text-anchor="start" font-size="11" fill="#1565C0" font-weight="bold" font-family="Noto Sans Bengali, Nirmala UI, sans-serif">{text}</text>'

    svg += '</svg>'
    return svg


# ═══════════════════════════════════════════════════════════════
# সন্নাড়ী চক্ৰ HTML Table (PDF ৰ বাবে)
# ═══════════════════════════════════════════════════════════════

def generate_sannari_html_table(nakshatra_number: int, nakshatra_name: str = "", lang: str = 'as') -> str:
    """
    PDF ৰ বাবে সন্নাড়ী চক্ৰৰ HTML টেবুল আৰু SVG নিৰ্মাণ কৰে।
    """
    data = get_sannari_data(nakshatra_number, lang)
    try:
        from prediction_i18n import get_sannari_label_i18n
        section_label = get_sannari_label_i18n('section', lang)
        nak_no_label = get_sannari_label_i18n('nak_no', lang)
        invalid_label = get_sannari_label_i18n('invalid', lang)
    except ImportError:
        section_label = 'বিভাগ'
        nak_no_label = 'নক্ষত্ৰ নং'
        invalid_label = 'অবৈধ নক্ষত্ৰ সংখ্যা'

    if data is None:
        return f'<p>{invalid_label}</p>'

    svg = generate_sannari_svg(nakshatra_number, nakshatra_name, width=600, height=300, lang=lang)

    # Build table rows
    rows_html = ""
    for pos in data["positions"]:
        rows_html += f"""
        <tr>
            <td><b>{pos['label']}</b></td>
            <td>{pos['number']}</td>
        </tr>"""

    html = f"""
    <div class="sannari-section">
        <div class="sannari-svg" style="text-align:center;margin-bottom:10px;">
            {svg}
        </div>
        <table class="small-table sannari-table">
            <thead><tr><th>{section_label}</th><th>{nak_no_label}</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>"""

    return html
