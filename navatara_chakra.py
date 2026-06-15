"""
ধ্ৰুৱতৰা AI - নৱতাৰা চক্ৰ ইঞ্জিন (Navatara Chakra Engine)
============================================================
নক্ষত্ৰ সংখ্যাৰ ওপৰত ভিত্তি কৰি নৱতাৰা চক্ৰ গণনা আৰু SVG/HTML নিৰ্মাণ।
৯ তাৰা: জন্ম, সম্পদ, বিপদ, ক্ষেম, প্ৰত্যাৰি, সাধক, বধ, মিত্ৰ, পৰমমিত্ৰ।
৩ শাৰী x ৯ স্তম্ভ = ২৭ নক্ষত্ৰ।
ৰঙা ৰং: বিপদ (২), প্ৰত্যাৰি (৪), বধ (৬) — এই নক্ষত্ৰত শুভকৰ্ম বৰ্জন কৰিব।
"""

# ═══════════════════════════════════════════════════════════════
# ধ্ৰুৱক
# ═══════════════════════════════════════════════════════════════

TARA_NAMES = ["জন্ম", "সম্পদ", "বিপদ", "ক্ষেম", "প্ৰত্যাৰি", "সাধক", "বধ", "মিত্ৰ", "পৰমমিত্ৰ"]

# ৰঙা ৰংৰ স্তম্ভ (0-indexed): বিপদ=2, প্ৰত্যাৰি=4, বধ=6
RED_COLUMNS = {2, 4, 6}

NAKSHATRA_NAMES = [
    "অশ্বিনী", "ভৰণী", "কৃত্তিকা", "ৰোহিণী", "মৃগশিৰা", "আৰ্দ্ৰা", "পুনৰ্বসু",
    "পুষ্যা", "অশ্লেষা", "মঘা", "পূৰ্বফাল্গুনী", "উত্তৰফাল্গুনী", "হস্তা",
    "চিত্ৰা", "স্বাতী", "বিশাখা", "অনুৰাধা", "জ্যেষ্ঠা", "মূল", "পূৰ্বাষাঢ়া",
    "উত্তৰাষাঢ়া", "শ্ৰৱণা", "ধনিষ্ঠা", "শতভিষা", "পূৰ্বভাদ্ৰপদ", "উত্তৰভাদ্ৰপদ", "ৰেৱতী"
]


# ═══════════════════════════════════════════════════════════════
# নৱতাৰা চক্ৰ গণনা
# ═══════════════════════════════════════════════════════════════

def get_navatara_data(nakshatra_number: int, lang: str = 'as') -> dict:
    """
    নক্ষত্ৰ সংখ্যা (১-২৭) ৰ পৰা নৱতাৰা চক্ৰৰ ৩x৯ গ্ৰীড গণনা কৰে।
    Args:
        nakshatra_number: 1-27
        lang: language code (as/bn/hi/en)
    Returns dict with rows of (nakshatra_number, tara_name, is_red) tuples.
    """
    if nakshatra_number < 1 or nakshatra_number > 27:
        return None

    # Get i18n tara names and nakshatra names
    try:
        from prediction_i18n import get_navatara_tara_names_i18n, get_nakshatra_names_list_i18n
        tara_names = get_navatara_tara_names_i18n(lang)
        nak_names = get_nakshatra_names_list_i18n(lang)
    except ImportError:
        tara_names = TARA_NAMES
        nak_names = NAKSHATRA_NAMES

    n = nakshatra_number
    rows = []

    for row in range(3):
        row_data = []
        for col in range(9):
            nak_num = ((n - 1) + row * 9 + col) % 27 + 1
            tara_name = tara_names[col]
            is_red = col in RED_COLUMNS
            nak_name = nak_names[nak_num - 1]
            row_data.append({
                "nakshatra_number": nak_num,
                "nakshatra_name": nak_name,
                "tara_name": tara_name,
                "is_red": is_red,
            })
        rows.append(row_data)

    return {
        "nakshatra_number": n,
        "nakshatra_name": nak_names[n - 1],
        "headers": tara_names,
        "rows": rows,
        "red_columns": list(RED_COLUMNS),
    }


# ═══════════════════════════════════════════════════════════════
# নৱতাৰা চক্ৰ HTML Table (ৱেব আৰু PDF দুয়োৰে বাবে)
# ═══════════════════════════════════════════════════════════════

def generate_navatara_html(nakshatra_number: int, lang: str = 'as') -> str:
    """
    নৱতাৰা চক্ৰৰ সম্পূৰ্ণ HTML (টেবুল + ব্যাখ্যা) নিৰ্মাণ কৰে।
    """
    data = get_navatara_data(nakshatra_number, lang)
    try:
        from prediction_i18n import get_navatara_label_i18n
        title_label = get_navatara_label_i18n('title', lang)
        note_label = get_navatara_label_i18n('note', lang)
        invalid_label = get_navatara_label_i18n('invalid', lang)
    except ImportError:
        title_label = 'নৱতাৰা চক্ৰ'
        note_label = 'নৱতাৰা চক্ৰত উল্লেখিত নক্ষত্ৰত গ্ৰহ সঞ্চাৰ হলে...'
        invalid_label = 'অবৈধ নক্ষত্ৰ সংখ্যা'

    if data is None:
        return f'<p style="color:#c62828;">{invalid_label}</p>'

    # Build table
    html = '<div class="navatara-section">'
    html += f'<h4 style="text-align:center;color:#1a237e;margin-bottom:8px;">🌀 {title_label} — {data["nakshatra_name"]} (নং {data["nakshatra_number"]})</h4>'

    html += '<div style="overflow-x:auto;">'
    html += '<table class="navatara-table">'

    # Header row - use column index to check RED_COLUMNS instead of searching in TARA_NAMES
    html += '<thead><tr>'
    for col_idx, h in enumerate(data["headers"]):
        is_red = col_idx in RED_COLUMNS
        style = 'style="color:#C62828;"' if is_red else ''
        html += f'<th {style}>{h}</th>'
    html += '</tr></thead>'

    # Data rows
    html += '<tbody>'
    for row in data["rows"]:
        html += '<tr>'
        for col_idx, cell in enumerate(row):
            is_red = col_idx in RED_COLUMNS
            if is_red:
                html += f'<td class="navatara-red">{cell["nakshatra_number"]}<br><span class="navatara-name">{cell["nakshatra_name"]}</span></td>'
            else:
                html += f'<td class="navatara-blue">{cell["nakshatra_number"]}<br><span class="navatara-name">{cell["nakshatra_name"]}</span></td>'
        html += '</tr>'
    html += '</tbody>'

    html += '</table>'
    html += '</div>'

    # Explanation text (i18n)
    html += f'''
    <div class="navatara-note">
        <p>{note_label}</p>
    </div>
    '''

    html += '</div>'
    return html


# ═══════════════════════════════════════════════════════════════
# নৱতাৰা চক্ৰ SVG (ৱেবৰ বাবে)
# ═══════════════════════════════════════════════════════════════

def generate_navatara_svg(nakshatra_number: int, width: int = 700, height: int = 200, lang: str = 'as') -> str:
    """
    নৱতাৰা চক্ৰৰ SVG চিত্ৰ নিৰ্মাণ কৰে।
    """
    data = get_navatara_data(nakshatra_number, lang)
    try:
        from prediction_i18n import get_navatara_label_i18n
        title_label = get_navatara_label_i18n('title', lang)
        invalid_label = get_navatara_label_i18n('invalid', lang)
    except ImportError:
        title_label = 'নৱতাৰা চক্ৰ'
        invalid_label = 'অবৈধ নক্ষত্ৰ সংখ্যা'

    if data is None:
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 200"><text x="350" y="100" text-anchor="middle" font-size="14" fill="#c62828">{invalid_label}</text></svg>'

    cell_w = 72
    cell_h = 36
    start_x = 26
    start_y = 40
    header_y = 28

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">'
    svg += f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>'

    # Title
    svg += f'<text x="{width//2}" y="18" text-anchor="middle" font-size="13" fill="#1a237e" font-weight="bold" font-family="Noto Sans Bengali, Nirmala UI, sans-serif">{title_label} — {data["nakshatra_name"]} (নং {data["nakshatra_number"]})</text>'

    # Headers
    for col, h in enumerate(data["headers"]):
        x = start_x + col * cell_w + cell_w // 2
        is_red = col in RED_COLUMNS
        color = "#C62828" if is_red else "#1565C0"
        svg += f'<text x="{x}" y="{header_y}" text-anchor="middle" font-size="10" fill="{color}" font-weight="bold" font-family="Noto Sans Bengali, Nirmala UI, sans-serif">{h}</text>'

    # Data rows
    for row_idx, row in enumerate(data["rows"]):
        for col, cell in enumerate(row):
            x = start_x + col * cell_w
            y = start_y + row_idx * cell_h
            color = "#C62828" if cell["is_red"] else "#1565C0"

            # Cell rectangle
            svg += f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" fill="none" stroke="#333" stroke-width="1"/>'

            # Number
            svg += f'<text x="{x + cell_w//2}" y="{y + 14}" text-anchor="middle" font-size="11" fill="{color}" font-weight="bold" font-family="Noto Sans Bengali, Nirmala UI, sans-serif">{cell["nakshatra_number"]}</text>'

            # Name (smaller)
            svg += f'<text x="{x + cell_w//2}" y="{y + 28}" text-anchor="middle" font-size="7" fill="{color}" font-family="Noto Sans Bengali, Nirmala UI, sans-serif">{cell["nakshatra_name"]}</text>'

    svg += '</svg>'
    return svg
