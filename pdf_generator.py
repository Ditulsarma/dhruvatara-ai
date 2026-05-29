"""
ধ্ৰুৱতৰা AI - পিডিএফ ৰিপৰ্ট জেনেৰেটৰ
PDF Report Generator: Generates professional Assamese astrology PDF reports
using Playwright (Chromium) for perfect Assamese/Bengali text rendering.
Uses subprocess isolation to avoid threading conflicts with Flask.
"""

import io
import os
import json
import subprocess
import tempfile
import sys
from datetime import datetime
import base64

# ─── Colors ─────────────────────────────────────────────────────
ORANGE = '#FF6600'
DEEP_BLUE = '#1a237e'
DARK_GREY = '#333333'
LIGHT_BG = '#FFF8F0'
WHITE = '#FFFFFF'
RED = '#C62828'
GREEN = '#2E7D32'

# ─── SVG Kundli Chart Generator (Bengali Style) ─────────────────

def _svg_chart(chart_data: dict, size: int = 400, title: str = "", show_rasi_names: bool = True) -> str:
    """Generate an SVG kundli chart in Bengali (fixed rasi) style.
    Uses a 4x4 grid layout with proper cell-based positioning to prevent
    planet overlap. Each house gets its own rectangular cell with centered content.
    chart_data: dict mapping rasi_index (0-11) -> list of planet short codes
    """
    S = size
    # Grid: 4 columns x 4 rows, center 4 cells are empty (diamond shape)
    # Bengali fixed rasi layout mapped to grid positions:
    # Row 0: [1-বৃষ] [0-মেষ] [11-মীন]
    # Row 1: [2-মিথুন] [empty] [10-কুম্ভ]
    # Row 2: [3-কৰ্কট] [empty] [9-মকৰ]
    # Row 3: [4-সিংহ] [5-কন্যা] [6-তুলা] ... wait, standard is:
    # Actually Bengali layout:
    # Row 0: col0=1(বৃষ) col1=0(মেষ) col2=11(মীন)
    # Row 1: col0=2(মিথুন) col1=empty col2=10(কুম্ভ)
    # Row 2: col0=3(কৰ্কট) col1=empty col2=9(মকৰ)
    # Row 3: col0=4(সিংহ) col1=5(কন্যা) col2=6(তুলা) col3=7(বৃশ্চিক) ... 
    # Actually the standard Bengali diamond has 12 houses around a center:
    # Top row: 1, 0, 11
    # Left col: 2, 3, 4
    # Bottom row: 5, 6, 7
    # Right col: 10, 9, 8
    
    rasi_names = ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"]

    # Use a 4x4 grid. Each cell is S/4 x S/4.
    # Grid positions (row, col) for each rasi:
    grid_pos = {
        0:  (0, 1),   # মেষ - top center
        1:  (0, 0),   # বৃষ - top left
        2:  (1, 0),   # মিথুন - left row 1
        3:  (2, 0),   # কৰ্কট - left row 2
        4:  (3, 0),   # সিংহ - bottom left
        5:  (3, 1),   # কন্যা - bottom center-left
        6:  (3, 2),   # তুলা - bottom center-right
        7:  (3, 3),   # বৃশ্চিক - bottom right
        8:  (2, 3),   # ধনু - right row 2
        9:  (1, 3),   # মকৰ - right row 1
        10: (0, 3),   # কুম্ভ - top right
        11: (0, 2),   # মীন - top center-right
    }

    C = S / 4  # cell size

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">'
    # Background
    svg += f'<rect x="0" y="0" width="{S}" height="{S}" fill="#fafafa" stroke="#2c3e50" stroke-width="2"/>'

    # Draw the diamond lines (Bengali kundli style)
    # Outer square border already drawn above
    # Diagonal lines from corners to midpoints
    svg += f'<line x1="0" y1="0" x2="{S}" y2="{S}" stroke="#2c3e50" stroke-width="1.5"/>'
    svg += f'<line x1="{S}" y1="0" x2="0" y2="{S}" stroke="#2c3e50" stroke-width="1.5"/>'
    # Diamond midlines
    svg += f'<line x1="{S/2}" y1="0" x2="{S}" y2="{S/2}" stroke="#2c3e50" stroke-width="1.5"/>'
    svg += f'<line x1="{S}" y1="{S/2}" x2="{S/2}" y2="{S}" stroke="#2c3e50" stroke-width="1.5"/>'
    svg += f'<line x1="{S/2}" y1="{S}" x2="0" y2="{S/2}" stroke="#2c3e50" stroke-width="1.5"/>'
    svg += f'<line x1="0" y1="{S/2}" x2="{S/2}" y2="0" stroke="#2c3e50" stroke-width="1.5"/>'

    # Draw rasi names and planets using foreignObject for proper text wrapping
    for ri in range(12):
        row, col = grid_pos[ri]
        planets = chart_data.get(ri, [])
        # Cell position
        cx = col * C
        cy = row * C
        
        # Rasi name at top of cell
        rasi_fs = S * 0.028
        rasi_y = cy + rasi_fs + 2
        if show_rasi_names:
            svg += f'<text x="{cx + C/2}" y="{rasi_y}" text-anchor="middle" font-size="{rasi_fs}" fill="#7f8c8d" font-family="Noto Sans Bengali, Nirmala UI, sans-serif">{rasi_names[ri]}</text>'

        # Planets - use foreignObject for proper multi-line centering
        if planets:
            n = len(planets)
            p_fs = S * 0.055  # planet font size
            p_line_h = p_fs * 1.4  # line height
            total_h = n * p_line_h
            # Available space: from below rasi name to bottom of cell
            avail_top = rasi_y + 2
            avail_bottom = cy + C - 4
            avail_h = avail_bottom - avail_top
            
            # Center the planet block in available space
            block_start_y = avail_top + (avail_h - total_h) / 2
            if block_start_y < avail_top:
                block_start_y = avail_top
            
            for pi, p in enumerate(planets):
                py = block_start_y + pi * p_line_h + p_fs * 0.75
                svg += f'<text x="{cx + C/2}" y="{py}" text-anchor="middle" font-size="{p_fs}" fill="#1a237e" font-weight="800" font-family="Noto Sans Bengali, Nirmala UI, sans-serif">{p}</text>'

    if title:
        svg += f'<text x="{S/2}" y="{S - 4}" text-anchor="middle" font-size="{S*0.03}" fill="#FF6600" font-weight="bold" font-family="Noto Sans Bengali, Nirmala UI, sans-serif">{title}</text>'
    svg += '</svg>'
    return svg

# ─── HTML Template ──────────────────────────────────────────────

def get_shani_sare_sati_data(moon_rasi: str, planets_data: list, user_dob: str = "", max_age: float = 100.0) -> list:
    """
    Compute Saturn Sare Sati / Dhaiya periods from birth to max_age.
    Returns a list of dicts with keys: age_start, age_end, year_start, year_end, rasi, phase
    """
    rasi_names = ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"]

    if not moon_rasi or moon_rasi not in rasi_names:
        return []

    moon_idx = rasi_names.index(moon_rasi)
    shani_planet = next((p for p in planets_data if p.get('name') == 'শনি'), None)
    if not shani_planet:
        return []

    shani_rasi = shani_planet.get('rasi')
    if shani_rasi not in rasi_names:
        return []

    # Parse birth year from user_dob (format: YYYY-MM-DD)
    birth_year = None
    if user_dob:
        try:
            birth_year = int(user_dob.split('-')[0])
        except (ValueError, IndexError):
            pass

    sat_idx = rasi_names.index(shani_rasi)
    step_years = 2.5
    events = []
    total_steps = int(max_age / step_years)

    for step in range(total_steps):
        age_start = step * step_years
        age_end = age_start + step_years
        rasi_idx = (sat_idx + step) % 12
        relation = (rasi_idx - moon_idx) % 12

        if relation == 11:
            phase = "সাড়ে সাতীৰ প্ৰথম চৰণ (১২ষ্ঠ ভাৱ)"
        elif relation == 0:
            phase = "সাড়ে সাতীৰ মধ্য চৰণ (১ম ভাৱ)"
        elif relation == 1:
            phase = "সাড়ে সাতীৰ শেষ চৰণ (২য় ভাৱ)"
        elif relation == 3:
            phase = "ঢৈয়া (৪র্থ ভাৱ)"
        elif relation == 7:
            phase = "ঢৈয়া (৮ম ভাৱ)"
        else:
            continue

        year_start = None
        year_end = None
        if birth_year is not None:
            year_start = birth_year + int(age_start)
            year_end = birth_year + int(age_end) - 1  # exclusive end, so -1

        events.append({
            "age_start": age_start,
            "age_end": age_end,
            "year_start": year_start,
            "year_end": year_end,
            "rasi": rasi_names[rasi_idx],
            "phase": phase
        })

    return events


def _render_shani_sare_sati_html(moon_rasi: str, planets_data: list, user_dob: str = "", max_age: float = 100.0) -> str:
    events = get_shani_sare_sati_data(moon_rasi, planets_data, user_dob, max_age)

    if not events:
        return '<div class="empty-msg">এই জন্ম কুণ্ডলীৰ বাবে ১০০ বছৰত কোনো শনি সাড়ে সাতী বা ঢৈয়া ঘটনাৰ পূৰ্ণ তালিকা নাথাকে।</div>'

    rows = ""
    for e in events:
        year_col = ""
        if e["year_start"] is not None and e["year_end"] is not None:
            year_col = f"<td>{e['year_start']} - {e['year_end']}</td>"
        else:
            year_col = "<td>—</td>"
        rows += f"""
            <tr>
                <td>{e['age_start']:.1f} - {e['age_end']:.1f}</td>
                {year_col}
                <td>{e['rasi']}</td>
                <td>{e['phase']}</td>
            </tr>"""

    return f"""
        <div class=\"sare-sati-box\">
            <p class=\"sare-sati-note\">এই তালিকাখন শনিৰ প্ৰতি ৰাশীত প্ৰায় ২.৫ বছৰৰ চলাচলৰ ভিত্তিত অনুমান কৰা হৈছে। আসল সময়কাল বর্তমান গ্ৰহ গতিবিধি আৰু জন্মে থকা শনিৰ অবস্থানৰ ওপৰত নিৰ্ভৰ কৰে।</p>
            <table class=\"sare-sati-table\">
                <thead><tr><th>আনুমানিক বয়স</th><th>আনুমানিক চন</th><th>শনি ৰাশি</th><th>দশা</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>"""



def _build_html(
    user_name: str, user_dob: str, user_tob: str, user_place: str,
    planets_data: list, panchanga: dict, dosha_results: list,
    yoga_results: list, dasa_data: list, ai_interpretation: str = "",
    all_vargas: dict = None, tripap_data: dict = None,
    tripap_ages: list = None, asc_rasi: str = "",
    all_dasha_predictions: list = None,
    sannari_html: str = "",
    navatara_html: str = "",
    nakshatra_phala_html: str = "",
    lagna_phala_html: str = "",
    rashi_phala_html: str = "",
    graha_bichar_html: str = "",
    selected_sections: list = None,
    lagna_lord: str = "",
    moon_rashi_lord: str = "",
    moon_rasi: str = "",
    gender: str = "male",
    astrologer_profile: dict = None,
    patrika_text: str = ""
) -> str:
    """Build complete HTML for the PDF report.
    selected_sections: list of section keys to include. If None, include all.
    """
    # Helper: check if a section should be included
    def _include(key):
        if selected_sections is None:
            return True
        return key in selected_sections

    rasi_names = ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"]
    varga_names = {
        "D1": "ৰাশি", "D2": "হোৰা", "D3": "দ্ৰেক্কান", "D4": "চতুৰ্থাংশ",
        "D7": "সপ্তমাংশ", "D9": "নৱাংশ", "D10": "দশমাংশ", "D12": "দ্বাদশাংশ",
        "D16": "ষোড়শাংশ", "D20": "বিংশাংশ", "D24": "চতুৰ্বিংশাংশ",
        "D27": "সপ্তবিংশাংশ", "D30": "ত্ৰিংশাংশ", "D40": "খবেদাংশ",
        "D45": "অক্ষবেদাংশ", "D60": "ষষ্ট্যাংশ"
    }

    # ── Planet Table Rows ──
    planet_rows = ""
    for p in planets_data:
        planet_rows += f"""
        <tr>
            <td><b>{p['name']}</b></td>
            <td>{p['rasi']}</td>
            <td>{p['degree']}°</td>
            <td>{p['nakshatra']}</td>
            <td>{p['lord']}</td>
        </tr>"""

    # ── Panchanga Items ──
    panchanga_items = [
        ('তিথি', panchanga.get('tithi', {}).get('name', '—'), panchanga.get('paksha', '')),
        ('নক্ষত্ৰ', panchanga.get('nakshatra', {}).get('name', '—'), f"পাদ: {panchanga.get('nakshatra', {}).get('pada', '—')}"),
        ('যোগ', panchanga.get('yoga', {}).get('name', '—'), ''),
        ('কৰণ', panchanga.get('karana', {}).get('name', '—'), ''),
        ('বাৰ', panchanga.get('vaar', {}).get('name', '—'), ''),
        ('ঋতু', panchanga.get('ritu', {}).get('name', '—'), ''),
        ('অসমীয়া মাহ', panchanga.get('masa', {}).get('name', '—'), ''),
        ('অয়নাংশ', f"{panchanga.get('ayanamsa', '—')}°", 'লাহিড়ী'),
        ('সূৰ্য্যোদয়', panchanga.get('sunrise', '—'), ''),
        ('সূৰ্য্যাস্ত', panchanga.get('sunset', '—'), ''),
        ('ৰাহুকাল', panchanga.get('rahu_kalam', '—'), ''),
        ('যমগণ্ড', panchanga.get('yama_gandam', '—'), ''),
        ('গুলিক কাল', panchanga.get('gulika_kalam', '—'), ''),
        ('অভিজিৎ মুহূৰ্ত', panchanga.get('abhijit_muhurta', '—'), ''),
        ('যমকাল', panchanga.get('yama_kaal', '—'), ''),
        ('কালবেলা', panchanga.get('kaal_bela', '—'), ''),
        ('ৰাৰবেলা', panchanga.get('rar_bela', '—'), ''),
        ('দিবামান', panchanga.get('divaman', '—'), ''),
        ('ৰাত্ৰিমান', panchanga.get('ratriman', '—'), ''),
        ('জাতদণ্ড', panchanga.get('jata_danda', '—'), ''),
        ('বৰ্ণ', panchanga.get('varna', '—'), ''),
        ('গণ', panchanga.get('gana', '—'), ''),
        ('যোনি', panchanga.get('yoni', '—'), ''),
        ('নাড়ী', panchanga.get('nadi', '—'), ''),
    ]
    panchanga_html = ""
    for label, value, sub in panchanga_items:
        sub_html = f'<div class="p-sub">{sub}</div>' if sub else ''
        panchanga_html += f"""
        <div class="p-item">
            <div class="p-label">{label}</div>
            <div class="p-value">{value}</div>
            {sub_html}
        </div>"""

    # ── Dosha Cards ──
    dosha_html = ""
    for d in dosha_results:
        info = d.get('info', {})
        icon = info.get('icon', '•')
        name = info.get('name', d.get('key', ''))
        if d.get('present'):
            sev = d.get('severity_text', 'উপস্থিত')
            sev_class = 'high' if d.get('severity', 0) >= 3 else ('medium' if d.get('severity', 0) >= 2 else 'low')
            desc = info.get('description', '')[:200]
            remedies_html = ""
            if info.get('remedies'):
                remedies_html = '<ul>' + ''.join(f'<li>{r}</li>' for r in info['remedies'][:3]) + '</ul>'
            dosha_html += f"""
            <div class="dosha-card">
                <div class="d-icon">{icon}</div>
                <div class="d-content">
                    <div><span class="d-name">{name}</span><span class="d-severity {sev_class}">{sev}</span></div>
                    <div class="d-desc">{desc}...</div>
                    {remedies_html}
                </div>
            </div>"""
        else:
            dosha_html += f"""
            <div class="dosha-card safe">
                <div class="d-icon">{icon}</div>
                <div class="d-content">
                    <div><span class="d-name">{name}</span><span class="d-severity low">অনুপস্থিত ✅</span></div>
                </div>
            </div>"""

    # ── Yoga Cards ──
    yoga_html = ""
    if yoga_results:
        for y in yoga_results:
            yoga_html += f"""
            <div class="yoga-card">
                <div class="y-icon">{y.get('icon', '')}</div>
                <div class="y-content">
                    <div><span class="y-name">{y.get('name', '')}</span><span class="y-category">{y.get('category', '')}</span></div>
                    <div class="y-desc">{y.get('description', '')[:250]}...</div>
                    <div class="y-effect"><b>ফল:</b> {y.get('effect', '')}</div>
                </div>
            </div>"""
    else:
        yoga_html = '<div class="empty-msg">🔍 কোনো বিশেষ যোগ ধৰা পৰা নাই।</div>'

    # ── Dasha Summary ──
    dasha_rows = ""
    for md in dasa_data[:5]:
        ad_names = ', '.join(ad['ad_lord'] for ad in md.get('sub_dasas', [])[:3])
        dasha_rows += f"""
        <tr>
            <td>{md['md_lord']}</td>
            <td>{md['start']}</td>
            <td>{md['end']}</td>
            <td>{ad_names}</td>
        </tr>"""

    # ── Full Dasha (All Mahadasa + Antardasa with predictions) ──
    full_dasha_html = ""
    for md in dasa_data:
        ad_rows = ""
        for ad in md.get('sub_dasas', []):
            ad_rows += f"""
            <tr>
                <td>{ad['ad_lord']}</td>
                <td>{ad['start']}</td>
                <td>{ad['end']}</td>
            </tr>"""
        full_dasha_html += f"""
        <div class="md-block">
            <div class="md-title">★ {md['md_lord']} ({md['start']} → {md['end']}) — {md.get('years', '')} বছৰ</div>
            <table class="small-table">
                <thead><tr><th>অন্তৰ্দশা</th><th>আৰম্ভ</th><th>সমাপ্তি</th></tr></thead>
                <tbody>{ad_rows}</tbody>
            </table>
        </div>"""

    # ── All Dasha Predictions (81 combinations) ──
    dasha_predictions_html = ""
    if all_dasha_predictions:
        for dp in all_dasha_predictions:
            pred_text = dp.get('prediction', '').replace('\n', '<br>')
            dasha_predictions_html += f"""
            <div class="dasha-pred-block">
                <div class="dp-header">★ {dp['maha_asm']} মহাদশা → {dp['antar_asm']} অন্তৰ্দশা <span class="dp-dates">({dp['start']} → {dp['end']})</span></div>
                <div class="dp-body">{pred_text}</div>
            </div>"""

    # ── Divisional Charts (prefer server-rendered PNGs to ensure font shaping)
    # Large D1 chart (embed PNG generated by kundli_chart.py if available)
    d1_svg = ""
    try:
        from kundli_chart import draw_kundli_chart

        def _embed_chart_png(chart_dict, asc_rasi_str=asc_rasi, w=450, h=450, style='bengali'):
            # determine ascendant index from string if possible
            try:
                asc_index = rasi_names.index(asc_rasi_str) if asc_rasi_str in rasi_names else 0
            except Exception:
                asc_index = 0
            buf = draw_kundli_chart(style=style, ascendant_index=asc_index, planet_data=chart_dict, width=w, height=h)
            img_bytes = buf.getvalue() if hasattr(buf, 'getvalue') else buf.read()
            b64 = base64.b64encode(img_bytes).decode('ascii')
            return f'<img src="data:image/png;base64,{b64}" alt="kundli" style="max-width:100%;height:auto;border:1px solid #e0e0e0;border-radius:6px;"/>'
        # embed D1 using the PIL renderer if available
        if all_vargas and "D1" in all_vargas:
            d1_svg = _embed_chart_png(all_vargas["D1"], w=600, h=600, style='bengali')
    except Exception:
        # Fallback to SVG generator if PIL/kundli_chart isn't available
        if all_vargas and "D1" in all_vargas:
            d1_svg = _svg_chart(all_vargas["D1"], size=450, title="D1 - ৰাশি চক্ৰ (Rashi)", show_rasi_names=True)

    # Small divisional charts (D2-D60)
    small_charts_html = ""
    if all_vargas:
        try:
            from kundli_chart import draw_kundli_chart
            for v_code in ["D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]:
                if v_code not in all_vargas:
                    continue
                vname = varga_names.get(v_code, v_code)
                # render small png for divisional chart
                try:
                    buf = draw_kundli_chart(style='bengali', ascendant_index=(rasi_names.index(asc_rasi) if asc_rasi in rasi_names else 0), planet_data=all_vargas[v_code], width=260, height=260)
                    img_bytes = buf.getvalue() if hasattr(buf, 'getvalue') else buf.read()
                    b64 = base64.b64encode(img_bytes).decode('ascii')
                    img_tag = f'<img src="data:image/png;base64,{b64}" alt="{v_code}" style="width:100%;height:auto;border:1px solid #e0e0e0;border-radius:4px;"/>'
                except Exception:
                    img_tag = _svg_chart(all_vargas[v_code], size=140, title=f"{v_code}", show_rasi_names=False)

                small_charts_html += f"""
                <div class="small-chart-card">
                    {img_tag}
                    <div class="small-chart-label">{v_code}<br>{vname}</div>
                </div>"""
        except Exception:
            # Fallback to SVG generation
            for v_code in ["D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]:
                if v_code not in all_vargas:
                    continue
                vname = varga_names.get(v_code, v_code)
                svg = _svg_chart(all_vargas[v_code], size=140, title=f"{v_code}", show_rasi_names=False)
                small_charts_html += f"""
                <div class="small-chart-card">
                    {svg}
                    <div class="small-chart-label">{v_code}<br>{vname}</div>
                </div>"""

    # ── Tripap Rista ──
    tripap_html = ""
    if tripap_data:
        tripap_html += f"""
        <div class="tripap-header">
            <b>🌙 চন্দ্ৰৰ নক্ষত্ৰ:</b> {tripap_data.get('nakshatra', '—')} (নং {tripap_data.get('nakshatra_index', '—')})
        </div>
        <table class="small-table tripap-table">
            <thead><tr><th>শাৰী</th><th>বিৱৰণ</th>"""
        for h in range(1, 13):
            tripap_html += f"<th>ঘৰ {h}</th>"
        tripap_html += "</tr></thead><tbody>"
        for rk in ['r1','r2','r3','r4','r5','r6','r7','r8','r9','r10','r11','r12','r13','r14','r15']:
            tripap_html += f"<tr><td><b>{rk}</b></td><td>{tripap_data.get('row_labels', {}).get(rk, '')}</td>"
            for val in tripap_data.get('rows', {}).get(rk, []):
                cat = tripap_data.get('row_categories', {}).get(rk, '')
                if cat == 'planet' and val in tripap_data.get('planet_map', {}):
                    tripap_html += f"<td class='planet-cell'>{tripap_data['planet_map'][val]}</td>"
                else:
                    tripap_html += f"<td>{val}</td>"
            tripap_html += "</tr>"
        tripap_html += "</tbody></table>"

        if tripap_ages:
            ages_str = ', '.join(str(a) for a in tripap_ages)
            tripap_html += f"""
            <div class="tripap-ages">
                <b>⏳ ত্ৰিপাপ ৰিষ্ট হবলগীয়া বয়স ({tripap_data.get('nakshatra', '')}):</b><br>
                {ages_str}
                <br><span class="small-note">মুঠ {len(tripap_ages)}টা বয়স • এই বয়সসমূহত সাৱধানতা অৱলম্বন কৰক।</span>
            </div>"""

    # ── AI Section ──
    ai_html = ""
    if ai_interpretation:
        ai_lines = ''.join(f'<p>{line.strip()}</p>' for line in ai_interpretation.strip().split('\n') if line.strip())
        ai_html = f"""
        <h2 class="section-heading">🤖 AI বিশ্লেষণ আৰু পৰামৰ্শ</h2>
        <div class="ai-content">{ai_lines}</div>"""

    # ── Top-Right Astrologer Header (Full Details - First Page) ──
    top_right_html = ""
    if astrologer_profile:
        tr_lines = []
        tr_lines.append('<div class="trh-title">শ্ৰমেণ গণ্যতে কোষ্ঠিং</div>')
        inst = astrologer_profile.get('institution_name', '').strip()
        name = astrologer_profile.get('astrologer_name', '').strip()
        bio = astrologer_profile.get('astrologer_bio', '').strip()
        addr = astrologer_profile.get('address', '').strip()
        mob = astrologer_profile.get('mobile', '').strip()
        if inst:
            tr_lines.append(f'<div class="trh-line trh-inst">{inst}</div>')
        if name:
            tr_lines.append(f'<div class="trh-line trh-name">{name}</div>')
        if bio:
            tr_lines.append(f'<div class="trh-line trh-bio">{bio}</div>')
        if addr:
            tr_lines.append(f'<div class="trh-line trh-addr">{addr}</div>')
        if mob:
            tr_lines.append(f'<div class="trh-line trh-mob">📞 {mob}</div>')
        if len(tr_lines) > 1:  # more than just the title
            top_right_html = '<div class="top-right-header">' + ''.join(tr_lines) + '</div>'

    html = f"""<!DOCTYPE html>
<html lang="as">
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    @page {{ size: A4; margin: 15mm 18mm; }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: 'Noto Sans Bengali', 'Nirmala UI', 'Vrinda', sans-serif;
        color: {DARK_GREY}; font-size: 8pt; line-height: 1.4;
    }}
    .header {{ text-align: center; margin-bottom: 16px; position: relative; }}
    .header h1 {{ font-size: 22pt; color: {DEEP_BLUE}; font-weight: 800; }}
    .header .sub {{ font-size: 11pt; color: {DARK_GREY}; }}

    /* Top-Right Astrologer Header */
    .top-right-header {{
        position: absolute; top: 0; right: 0;
        text-align: right; max-width: 55%;
    }}
    .trh-title {{
        font-size: 10pt; font-weight: 800; color: {ORANGE};
        margin-bottom: 4px; letter-spacing: 0.5px;
    }}
    .trh-line {{ font-size: 7pt; line-height: 1.5; color: #555; }}
    .trh-inst {{ font-weight: 700; color: {DEEP_BLUE}; font-size: 7.5pt; }}
    .trh-name {{ font-weight: 600; color: {ORANGE}; font-size: 7pt; }}
    .trh-bio {{ color: #666; font-size: 6.5pt; font-style: italic; }}
    .trh-addr {{ color: #777; font-size: 6.5pt; }}
    .trh-mob {{ color: {DEEP_BLUE}; font-size: 6.5pt; font-weight: 500; }}
    .divider {{ border: none; border-top: 2px solid {ORANGE}; margin: 10px 0 16px; }}

    h2.section-heading {{
        font-size: 13pt; color: {ORANGE}; margin: 18px 0 8px;
        padding-bottom: 3px; border-bottom: 1px solid #e8e0d5;
    }}

    /* Info Grid */
    .info-grid {{
        display: grid; grid-template-columns: 1fr 1fr; gap: 6px;
        background: {LIGHT_BG}; border: 1px solid #e8e0d5;
        border-radius: 6px; padding: 10px 14px; margin-bottom: 10px;
    }}
    .info-item {{ font-size: 9pt; }}
    .info-item b {{ color: {DEEP_BLUE}; }}

    /* Tables */
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 9pt; }}
    th {{ background: {ORANGE}; color: white; padding: 6px 8px; font-weight: 700; text-align: center; }}
    td {{ padding: 5px 8px; border: 1px solid #e0e0e0; text-align: center; }}
    tr:nth-child(even) {{ background: {LIGHT_BG}; }}

    .dasha-table th {{ background: {DEEP_BLUE}; }}

    /* Panchanga Grid */
    .p-grid {{
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px;
        margin-bottom: 10px;
    }}
    .p-item {{
        background: {LIGHT_BG}; border: 1px solid #e8e0d5;
        border-radius: 4px; padding: 6px 8px; text-align: center;
    }}
    .p-label {{ font-size: 7pt; color: #888; text-transform: uppercase; }}
    .p-value {{ font-weight: 700; font-size: 9pt; }}
    .p-sub {{ font-size: 7pt; color: #999; }}

    /* Dosha Cards */
    .dosha-card {{
        border-left: 4px solid {RED}; background: #FFF5F5;
        border-radius: 4px; padding: 8px 12px; margin-bottom: 6px;
        display: flex; gap: 10px; align-items: flex-start;
    }}
    .dosha-card.safe {{ border-left-color: {GREEN}; background: #F1F8E9; }}
    .d-icon {{ font-size: 14pt; }}
    .d-name {{ font-weight: 700; font-size: 10pt; }}
    .d-severity {{
        display: inline-block; padding: 1px 8px; border-radius: 10px;
        font-size: 7pt; font-weight: 600; margin-left: 6px;
    }}
    .d-severity.high {{ background: #FFCDD2; color: {RED}; }}
    .d-severity.medium {{ background: #FFE0B2; color: #E65100; }}
    .d-severity.low {{ background: #C8E6C9; color: {GREEN}; }}
    .d-desc {{ font-size: 8pt; color: #666; margin-top: 3px; }}
    .d-content ul {{ margin: 4px 0 0 16px; font-size: 8pt; color: #666; }}

    /* Yoga Cards */
    .yoga-card {{
        border-left: 4px solid {GREEN}; background: #F1F8E9;
        border-radius: 4px; padding: 8px 12px; margin-bottom: 6px;
        display: flex; gap: 10px; align-items: flex-start;
    }}
    .y-icon {{ font-size: 14pt; }}
    .y-name {{ font-weight: 700; font-size: 10pt; }}
    .y-category {{
        display: inline-block; padding: 1px 8px; border-radius: 10px;
        font-size: 7pt; font-weight: 600; background: #C8E6C9;
        color: {GREEN}; margin-left: 6px;
    }}
    .y-desc {{ font-size: 8pt; color: #666; margin-top: 3px; }}
    .y-effect {{ font-size: 8pt; color: {GREEN}; margin-top: 3px; }}

    .ai-content {{
        background: linear-gradient(135deg, #f8f5ff, #fff8f0);
        border-radius: 6px; padding: 12px 16px; border: 1px solid #e8e0f0;
        font-size: 9pt; line-height: 1.8;
    }}
    .ai-content p {{ margin-bottom: 4px; }}

    .empty-msg {{ text-align: center; padding: 20px; color: #999; font-size: 10pt; }}

    /* Small tables for Dasha/Varga/Tripap */
    .small-table {{ font-size: 7pt; margin-bottom: 6px; }}
    .small-table th {{ padding: 3px 5px; font-size: 7pt; }}
    .small-table td {{ padding: 2px 5px; font-size: 7pt; }}

    /* Full Dasha */
    .md-block {{ margin-bottom: 8px; page-break-inside: avoid; }}
    .md-title {{
        font-weight: 700; font-size: 8pt; color: {DEEP_BLUE};
        background: #E8EAF6; padding: 3px 8px; border-radius: 3px;
        margin-bottom: 2px;
    }}

    /* Varga Charts */
    .varga-item {{
        font-size: 7pt; padding: 3px 6px; border-bottom: 1px dotted #e0e0e0;
        display: flex; gap: 8px; align-items: baseline;
    }}
    .varga-code {{
        font-weight: 800; color: {ORANGE}; min-width: 28px;
    }}
    .varga-name {{
        font-weight: 600; color: {DEEP_BLUE}; min-width: 80px;
    }}
    .varga-detail {{ color: #555; flex: 1; }}

    /* Kundli Charts */
    .chart-large {{
        text-align: center; margin: 12px 0; padding: 10px;
        background: #fafafa; border: 1px solid #e0e0e0; border-radius: 6px;
    }}
    .chart-large svg {{ max-width: 100%; height: auto; }}
    .charts-grid {{
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
        margin: 8px 0;
    }}
    .small-chart-card {{
        text-align: center; padding: 6px; background: #fafafa;
        border: 1px solid #e0e0e0; border-radius: 4px;
    }}
    .small-chart-card img {{ width: 100%; height: auto; }}
    .small-chart-label {{
        font-size: 7pt; font-weight: 700; color: {ORANGE}; margin-top: 3px;
        line-height: 1.2;
    }}

    /* Tripap Rista */
    .tripap-header {{
        font-size: 9pt; padding: 8px 12px; background: #FFF3E0;
        border-radius: 4px; margin-bottom: 8px; border: 1px solid #FFCC80;
    }}
    .tripap-table {{ font-size: 6pt; }}
    .tripap-table th {{ font-size: 6pt; padding: 2px 3px; }}
    .tripap-table td {{ font-size: 6pt; padding: 2px 3px; }}
    .planet-cell {{ color: {RED}; font-weight: 600; }}
    .tripap-ages {{
        margin-top: 10px; padding: 10px 14px;
        background: linear-gradient(135deg, #FCE4EC, #F3E5F5);
        border-radius: 6px; border: 2px solid #E91E63;
        font-size: 8pt; line-height: 1.6;
    }}
    .small-note {{ font-size: 6pt; color: #888; }}

    /* Sannari Chakra */
    .sannari-section {{
        margin-bottom: 10px; page-break-inside: avoid;
    }}
    .sannari-svg {{
        text-align: center; margin-bottom: 8px;
    }}
    .sannari-svg svg {{
        max-width: 100%; height: auto;
    }}
    .sannari-table {{
        font-size: 8pt; margin: 0 auto; max-width: 300px;
    }}
    .sannari-table th {{
        background: {DEEP_BLUE}; color: white; padding: 4px 8px;
        font-size: 8pt;
    }}
    .sannari-table td {{
        padding: 3px 8px; font-size: 8pt;
    }}

    /* Navatara Chakra */
    .navatara-section {{
        margin-bottom: 10px; page-break-inside: avoid;
    }}
    .navatara-table {{
        font-size: 7pt; border-collapse: collapse; margin: 0 auto;
        width: 100%;
    }}
    .navatara-table th {{
        background: {DEEP_BLUE}; color: white; padding: 4px 4px;
        font-size: 7pt; text-align: center; border: 1px solid #ccc;
    }}
    .navatara-table td {{
        padding: 3px 4px; text-align: center; border: 1px solid #ccc;
        font-size: 7pt; line-height: 1.3;
    }}
    .navatara-red {{
        color: {RED}; font-weight: 700;
    }}
    .navatara-blue {{
        color: {DEEP_BLUE}; font-weight: 600;
    }}
    .navatara-name {{
        font-size: 6pt; font-weight: 400;
    }}
    .navatara-note {{
        margin-top: 8px; padding: 8px 12px;
        background: #FFF3E0; border-left: 3px solid {ORANGE};
        border-radius: 4px; font-size: 7.5pt; color: #555;
        line-height: 1.6;
    }}

    /* Nakshatra Phala */
    .nakshatra-phala-section {{
        margin-bottom: 10px; page-break-inside: avoid;
    }}
    .nakshatra-para {{
        font-size: 9pt; line-height: 1.8; text-align: justify;
        margin-bottom: 8px; text-indent: 20px;
        color: {DARK_GREY};
    }}

    /* Lagna Phala */
    .lagna-phala-section {{
        margin-bottom: 10px; page-break-inside: avoid;
    }}
    .lagna-para {{
        font-size: 9pt; line-height: 1.8; text-align: justify;
        margin-bottom: 8px; text-indent: 20px;
        color: {DARK_GREY};
    }}

    /* Dasha Prediction Blocks */
    .dasha-pred-block {{
        margin-bottom: 4px; page-break-inside: avoid;
        border: 1px solid #e0e0e0; border-radius: 3px;
        overflow: hidden;
    }}
    .dp-header {{
        font-weight: 700; font-size: 8.5pt; color: {DEEP_BLUE};
        background: #E8EAF6; padding: 3px 6px;
    }}
    .dp-dates {{ font-size: 7pt; color: #888; font-weight: 400; }}
    .dp-body {{
        font-size: 8pt; padding: 4px 6px; line-height: 1.4;
        color: {DARK_GREY};
    }}

    /* ── Invocatory Shlokas ── */
    .shloka-section {{
        margin: 14px 0 16px; page-break-inside: avoid;
    }}
    .shloka-outer-box {{
        background: linear-gradient(135deg, #FFF8E1 0%, #FFF3E0 30%, #FCE4EC 70%, #F3E5F5 100%);
        border: 2px solid {ORANGE};
        border-radius: 12px;
        padding: 18px 22px;
        position: relative;
        box-shadow: 0 3px 12px rgba(255,102,0,0.12);
    }}
    .shloka-outer-box::before {{
        content: "🕉️";
        position: absolute;
        top: -14px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 22pt;
        background: white;
        padding: 0 10px;
        border-radius: 50%;
    }}
    .shloka-title {{
        text-align: center;
        font-size: 11pt;
        font-weight: 800;
        color: {ORANGE};
        margin: 6px 0 12px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }}
    .shloka-block {{
        text-align: center;
        margin-bottom: 14px;
        padding: 12px 16px;
        background: rgba(255,255,255,0.55);
        border-radius: 8px;
        border: 1px dashed #e0c8a0;
    }}
    .shloka-text {{
        font-size: 9.5pt;
        font-weight: 600;
        color: {DEEP_BLUE};
        line-height: 2.4;
        letter-spacing: 0.3px;
        font-family: 'Noto Sans Bengali', 'Nirmala UI', 'Vrinda', sans-serif;
    }}
    .shloka-divider {{
        text-align: center;
        margin: 8px 0;
        font-size: 14pt;
        color: {ORANGE};
        letter-spacing: 6px;
    }}
    .shloka-footer-text {{
        text-align: center;
        font-size: 8pt;
        font-weight: 600;
        color: #888;
        margin-top: 8px;
        font-style: italic;
    }}

    .sare-sati-box {{
        background: #fff8f0;
        border: 1px solid #ffd8b2;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }}
    .sare-sati-note {{
        font-size: 8pt;
        color: #5d4037;
        margin-bottom: 8px;
        line-height: 1.5;
    }}
    .sare-sati-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 8pt;
    }}
    .sare-sati-table th, .sare-sati-table td {{
        border: 1px solid #e9d8c7;
        padding: 6px 8px;
        text-align: left;
    }}
    .sare-sati-table th {{
        background: #ffe0b2;
        color: #5d4037;
        font-weight: 700;
    }}

    .footer {{
        margin-top: 24px; padding-top: 10px; border-top: 2px solid {ORANGE};
        text-align: center; font-size: 7pt; color: #999;
    }}
</style>
</head>
<body>

<div class="header">
    {top_right_html}
    <h1>🌟 জন্মকুণ্ডলী</h1>
    <div class="sub">বৈদিক জ্যোতিষ সম্পূৰ্ণ ৰিপৰ্ট</div>
</div>
<hr class="divider">

<!-- ═══════════════ INVOCATORY SHLOKAS ═══════════════ -->
<div class="shloka-section">
    <div class="shloka-outer-box">
        <div class="shloka-title">॥ আৰম্ভণি ॥</div>

        <div class="shloka-block">
            <div class="shloka-text">
                অপ্ৰত্যক্ষানি শাস্ত্ৰানি বিবাদস্তেষু কেৱলম্<br>
                প্ৰত্যক্ষং জ্যোতিষং শাস্ত্ৰং চন্দ্ৰাকৌ যত্ৰ সাক্ষিণৌ<br>
                অন্যান্য শাস্ত্ৰেষু বিনোদমাত্ৰং ন তেষু কিঞ্চিদ্ভুবি দৃষ্টমস্তি<br>
                চিকিৎসিতং জ্যোতিষতন্ত্ৰ বাদো পদে পদে ॥
            </div>
        </div>

        <div class="shloka-divider">॥ ॐ ॥</div>

        <div class="shloka-block">
            <div class="shloka-text">
                ওঁ সৰ্ববিঘ্ন বিনাশায় সৰ্বকল্যাণহেতবে<br>
                পাৰ্বতী প্ৰিয় পুত্ৰায় গণেশায় নমো নমঃ ॥<br><br>
                যস্য নাস্তি খলু জন্ম পত্ৰিকা যা শুভাশুভ ফলপ্ৰকাশিনী<br>
                অন্ধবদ্ভবতি তস্য জীৱনং দীপ হীনমিব মন্দিৰং নিশি<br><br>
                গৌৰ্য্যাদি মাতৰাঃ সৰ্বে আদিত্যাদি নৱগ্ৰহাঃ<br>
                ইন্দ্ৰাদি লোক পালাশ্চ কুৰ্বন্তু কুশলং সদা ॥<br><br>
                আদিত্যাদি গ্ৰহাঃ সৰ্বে নক্ষত্ৰাণি চৰাশয়ঃ<br>
                দীৰ্ঘমায়ুঃ প্ৰকুৰ্বন্তু যস্যেয়ং জন্ম পত্ৰিকা ॥
            </div>
        </div>

        <div class="shloka-footer-text">॥ শুভমস্তু ॥</div>
    </div>
</div>
<!-- ═══════════════════════════════════════════════════ -->

<h2 class="section-heading">📋 ব্যক্তিগত তথ্য</h2>
<div class="info-grid">
    <div class="info-item"><b>নাম:</b> {user_name}</div>
    <div class="info-item"><b>লিংগ:</b> {"মহিলা (জাতিকা)" if gender == "female" else "পুৰুষ (জাতক)"}</div>
    <div class="info-item"><b>জন্মৰ স্থান:</b> {user_place}</div>
    <div class="info-item"><b>জন্মৰ তাৰিখ:</b> {user_dob}</div>
    <div class="info-item"><b>জন্মৰ সময়:</b> {user_tob}</div>
    <div class="info-item"><b>লগ্ন:</b> {asc_rasi}</div>
    <div class="info-item"><b>লগ্নৰ অধিপতি:</b> {lagna_lord}</div>
    <div class="info-item"><b>জন্ম ৰাশি:</b> {moon_rasi}</div>
    <div class="info-item"><b>জন্ম ৰাশিৰ অধিপতি:</b> {moon_rashi_lord}</div>
    <div class="info-item"><b>বৰ্ণ:</b> {panchanga.get('varna', '—')}</div>
    <div class="info-item"><b>গণ:</b> {panchanga.get('gana', '—')}</div>
    <div class="info-item"><b>যোনি:</b> {panchanga.get('yoni', '—')}</div>
    <div class="info-item"><b>নাড়ী:</b> {panchanga.get('nadi', '—')}</div>
    <div class="info-item"><b>জাতদণ্ড:</b> {panchanga.get('jata_danda', '—')}</div>
    <div class="info-item"><b>দিবামান:</b> {panchanga.get('divaman', '—')}</div>
    <div class="info-item"><b>ৰাত্ৰিমান:</b> {panchanga.get('ratriman', '—')}</div>
</div>
"""

    # Build body sections using string concatenation (not f-string inline conditionals)
    if _include('panchanga'):
        html += '<h2 class="section-heading">🕉️ পঞ্চাঙ্গ</h2><div class="p-grid">' + panchanga_html + '</div>'

    if _include('planets_table'):
        html += '<h2 class="section-heading">🪐 গ্ৰহৰ অৱস্থান</h2><table><thead><tr><th>গ্ৰহ</th><th>ৰাশি</th><th>ডিগ্ৰী</th><th>নক্ষত্ৰ</th><th>নক্ষত্ৰ পতি</th></tr></thead><tbody>' + planet_rows + '</tbody></table>'

    if _include('kundli_chart'):
        html += '<h2 class="section-heading">📊 জন্ম কুণ্ডলী (D1 - ৰাশি চক্ৰ)</h2><div class="chart-large">' + d1_svg + '</div>'
        # Patrika text below D1 chart
        if patrika_text:
            patrika_html = patrika_text.replace('\n', '<br>')
            html += '<div style="margin:12px 0;padding:14px 18px;background:linear-gradient(135deg,#FFF8E1,#FFF3E0);border:2px solid #FFCC80;border-radius:8px;font-size:9pt;line-height:2.2;text-align:justify;font-family:\'Noto Sans Bengali\',\'Nirmala UI\',sans-serif;">' + patrika_html + '</div>'

    if _include('varga_charts'):
        html += '<h2 class="section-heading">📊 ষোড়শবৰ্গ বিভাগীয় কুণ্ডলী (D2 - D60)</h2><div class="charts-grid">' + small_charts_html + '</div>'

    shani_sare_sati_html = _render_shani_sare_sati_html(moon_rasi, planets_data, user_dob)
    if _include('shani_sare_sati'):
        html += '<h2 class="section-heading">🌑 শনি সাৰেসাতী আৰু ঢৈয়া (০-১০০ বছৰ)</h2>' + shani_sare_sati_html

    if _include('dosha'):
        html += '<h2 class="section-heading">⚠️ দোষ বিশ্লেষণ</h2>' + dosha_html

    if _include('yoga'):
        html += '<h2 class="section-heading">✨ যোগ বিশ্লেষণ</h2>' + yoga_html

    if _include('sannari'):
        html += '<h2 class="section-heading">🌀 সন্নাড়ী চক্ৰ</h2>' + sannari_html

    if _include('navatara'):
        html += '<h2 class="section-heading">🌀 নৱতাৰা চক্ৰ</h2>' + navatara_html

    if _include('tripap'):
        html += '<h2 class="section-heading">☠️ ত্ৰিপাপ ৰিষ্ট বিশ্লেষণ</h2>' + tripap_html

    if _include('nakshatra_phala'):
        html += '<h2 class="section-heading">🌟 নক্ষত্ৰ ফলাফল</h2>' + nakshatra_phala_html

    if _include('lagna_phala'):
        html += '<h2 class="section-heading">🌅 লগ্ন ফলাফল</h2>' + lagna_phala_html

    if _include('rashi_phala'):
        html += '<h2 class="section-heading">🌙 ৰাশিফল (চন্দ্ৰ ৰাশি)</h2>' + rashi_phala_html

    if _include('graha_bichar'):
        html += '<h2 class="section-heading">🪐 গ্ৰহ বিচাৰ (ভাব অনুসৰি)</h2>' + graha_bichar_html

    if _include('dasha_summary'):
        html += '<h2 class="section-heading">⏳ বিংশোত্তৰী দশা সাৰাংশ</h2><table class="dasha-table"><thead><tr><th>মহাদশা</th><th>আৰম্ভ</th><th>সমাপ্তি</th><th>অন্তৰ্দশা (প্ৰথম ৩)</th></tr></thead><tbody>' + dasha_rows + '</tbody></table>'

    if _include('dasha_full'):
        html += '<h2 class="section-heading">⏳ সম্পূৰ্ণ মহাদশা আৰু অন্তৰ্দশা</h2>' + full_dasha_html

    if _include('dasha_predictions'):
        html += '<h2 class="section-heading">📝 মহাদশা-অন্তৰ্দশাৰ সম্পূৰ্ণ ফলাফল</h2>' + dasha_predictions_html

    if _include('ai'):
        html += ai_html

    html += f"""
<div class="footer">
    <p>ধ্ৰুৱতৰা AI • বৈদিক জ্যোতিষ</p>
    <p>এই ৰিপৰ্ট কেৱল জ্যোতিষীয় তথ্যৰ বাবে। ই কোনো চিকিৎসা, আইনী, বা বিত্তীয় পৰামৰ্শ নহয়।</p>
</div>

</body>
</html>"""

    # ── Build Astrologer Footer HTML for Playwright footer_template ──
    astro_footer_html = ""
    if astrologer_profile:
        name = astrologer_profile.get('astrologer_name', '').strip()
        mob = astrologer_profile.get('mobile', '').strip()
        parts = []
        if name:
            parts.append(f'<span style="font-weight:600;color:#FF6600;font-size:8px;">{name}</span>')
        if mob:
            parts.append(f'<span style="color:#1a237e;font-size:8px;">📞 {mob}</span>')
        if parts:
            astro_footer_html = ' &nbsp;|&nbsp; '.join(parts)

    return html, astro_footer_html


def generate_pdf_report(
    user_name: str, user_dob: str, user_tob: str, user_place: str,
    planets_data: list, panchanga: dict, dosha_results: list,
    yoga_results: list, dasa_data: list, ai_interpretation: str = "",
    all_vargas: dict = None, tripap_data: dict = None,
    tripap_ages: list = None, asc_rasi: str = "",
    all_dasha_predictions: list = None,
    sannari_html: str = "",
    navatara_html: str = "",
    nakshatra_phala_html: str = "",
    lagna_phala_html: str = "",
    rashi_phala_html: str = "",
    graha_bichar_html: str = "",
    selected_sections: list = None,
    lagna_lord: str = "",
    moon_rashi_lord: str = "",
    moon_rasi: str = "",
    gender: str = "male",
    astrologer_profile: dict = None,
    patrika_text: str = ""
) -> bytes:
    """
    Generate a complete professional PDF astrology report in Assamese.
    Uses Playwright (Chromium) via subprocess for perfect Assamese text rendering.
    Returns PDF as bytes.
    """
    html_content, astro_footer_html = _build_html(
        user_name, user_dob, user_tob, user_place,
        planets_data, panchanga, dosha_results,
        yoga_results, dasa_data, ai_interpretation,
        all_vargas, tripap_data, tripap_ages, asc_rasi,
        all_dasha_predictions, sannari_html, navatara_html,
        nakshatra_phala_html, lagna_phala_html, rashi_phala_html,
        graha_bichar_html=graha_bichar_html,
        selected_sections=selected_sections,
        lagna_lord=lagna_lord,
        moon_rashi_lord=moon_rashi_lord,
        moon_rasi=moon_rasi,
        gender=gender,
        astrologer_profile=astrologer_profile,
        patrika_text=patrika_text
    )

    # Write HTML to temp file, call pdf_worker.py in subprocess, read PDF back
    worker_script = os.path.join(os.path.dirname(__file__), 'pdf_worker.py')
    python_exe = sys.executable

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', encoding='utf-8', delete=False) as html_file:
        html_file.write(html_content)
        html_path = html_file.name

    pdf_path = html_path + '.pdf'

    # Write astrologer footer to temp file if present
    footer_path = None
    if astro_footer_html:
        footer_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', encoding='utf-8', delete=False)
        footer_file.write(astro_footer_html)
        footer_file.close()
        footer_path = footer_file.name

    try:
        cmd = [python_exe, worker_script, html_path, pdf_path]
        if footer_path:
            cmd.append(footer_path)
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            raise RuntimeError(f"PDF worker failed: {result.stderr}")

        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        return pdf_bytes
    finally:
        # Clean up temp files
        for path in [html_path, pdf_path, footer_path]:
            if path:
                try:
                    os.unlink(path)
                except OSError:
                    pass
