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
import unicodedata
from datetime import datetime, timedelta
import base64

# ─── Colors ─────────────────────────────────────────────────────
ORANGE = '#FF6600'
DEEP_BLUE = '#1a237e'
DARK_GREY = '#333333'
LIGHT_BG = '#FFF8F0'
WHITE = '#FFFFFF'
RED = '#C62828'
GREEN = '#2E7D32'

# ─── Ganesh Image Helper ────────────────────────────────────────
_GANESH_BASE64 = None

def _get_ganesh_base64():
    """Load Ganesh image from static/images and return base64 data URI."""
    global _GANESH_BASE64
    if _GANESH_BASE64 is not None:
        return _GANESH_BASE64
    # Try multiple possible paths
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'Ganesh_Image_Dhrubatara.png'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Image', 'Ganesh_Image_Dhrubatara.png'),
    ]
    for img_path in possible_paths:
        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                data = f.read()
            ext = os.path.splitext(img_path)[1].lower()
            mime = 'image/png' if ext == '.png' else 'image/jpeg'
            _GANESH_BASE64 = f'data:{mime};base64,{base64.b64encode(data).decode()}'
            return _GANESH_BASE64
    return None

# ─── SVG Kundli Chart Generator (Bengali Style) ─────────────────

def _svg_chart(chart_data: dict, size: int = 400, title: str = "", show_rasi_names: bool = True, lang: str = "as") -> str:
    """Generate an SVG kundli chart in Bengali (fixed rasi) style.
    Uses a 4x4 grid layout with proper cell-based positioning to prevent
    planet overlap. Each house gets its own rectangular cell with centered content.
    chart_data: dict mapping rasi_index (0-11) -> list of planet short codes
    lang: language code for rasi names
    """
    from prediction_i18n import get_panchanga_names_i18n
    pnames = get_panchanga_names_i18n(lang)
    rasi_names = pnames['RASHI_NAMES']

    # Pick a font-family list appropriate to the language so that the
    # browser / PDF rasterizer uses a font that has the required glyphs.
    # Devanagari (Hindi) and Bengali live in different Unicode blocks, so
    # the same primary font cannot render both.
    if lang == 'hi':
        font_family = "Nirmala UI, Mangal, Noto Sans Devanagari, Lohit Devanagari, sans-serif"
    elif lang == 'bn':
        font_family = "Noto Sans Bengali, SiyamRupali, Kalpurush, sans-serif"
    elif lang == 'en':
        font_family = "Noto Sans, Arial, Helvetica, sans-serif"
    else:  # 'as' and any other default
        font_family = "Noto Sans Bengali, Kalpurush, Nirmala UI, sans-serif"

    S = size
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
            svg += f'<text x="{cx + C/2}" y="{rasi_y}" text-anchor="middle" font-size="{rasi_fs}" fill="#7f8c8d" font-family="{font_family}">{rasi_names[ri]}</text>'

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
                svg += f'<text x="{cx + C/2}" y="{py}" text-anchor="middle" font-size="{p_fs}" fill="#1a237e" font-weight="800" font-family="{font_family}">{p}</text>'

    if title:
        svg += f'<text x="{S/2}" y="{S - 4}" text-anchor="middle" font-size="{S*0.03}" fill="#FF6600" font-weight="bold" font-family="{font_family}">{title}</text>'
    svg += '</svg>'
    return svg

# ─── HTML Template ──────────────────────────────────────────────

def get_shani_sare_sati_data(moon_rasi: str, planets_data: list, user_dob: str = "", max_age: float = 100.0, lang: str = "as") -> list:
    """
    Compute Saturn Sare Sati / Dhaiya periods from birth to max_age.
    Returns a list of dicts with keys: age_start, age_end, year_start, year_end, rasi, phase
    
    Uses the full birth date for accurate year calculations.
    Saturn takes approximately 2.5 years per rashi transit.
    lang: language code for phase names
    """
    from prediction_i18n import get_panchanga_names_i18n
    from translations import get_text
    pnames = get_panchanga_names_i18n(lang)
    rasi_names = pnames['RASHI_NAMES']
    # Normalize to NFC for consistent matching
    rasi_names_n = [unicodedata.normalize('NFC', r) for r in rasi_names]
    moon_rasi_n = unicodedata.normalize('NFC', moon_rasi) if moon_rasi else ''

    if not moon_rasi_n or moon_rasi_n not in rasi_names_n:
        return []

    moon_idx = rasi_names_n.index(moon_rasi_n)
    shani_planet = next((p for p in planets_data if p.get('name_asm') == 'শনি'), None)
    if not shani_planet:
        return []

    shani_rasi = shani_planet.get('rasi', '')
    shani_rasi_n = unicodedata.normalize('NFC', shani_rasi) if shani_rasi else ''
    if shani_rasi_n not in rasi_names_n:
        return []

    # Parse full birth date from user_dob (format: YYYY-MM-DD)
    birth_date = None
    if user_dob:
        try:
            birth_date = datetime.strptime(user_dob.strip(), "%Y-%m-%d")
        except (ValueError, IndexError):
            pass

    sat_idx = rasi_names_n.index(shani_rasi_n)
    step_years = 2.5  # Saturn takes ~2.5 years per rashi
    step_days = step_years * 365.25  # approximate days per step
    events = []
    total_steps = int(max_age / step_years)

    for step in range(total_steps):
        age_start = step * step_years
        age_end = age_start + step_years
        rasi_idx = (sat_idx + step) % 12
        relation = (rasi_idx - moon_idx) % 12

        if relation == 11:
            phase = get_text('pdf_sare_sati_phase1', lang)
        elif relation == 0:
            phase = get_text('pdf_sare_sati_phase2', lang)
        elif relation == 1:
            phase = get_text('pdf_sare_sati_phase3', lang)
        elif relation == 3:
            phase = get_text('pdf_dhaiya_4', lang)
        elif relation == 7:
            phase = get_text('pdf_dhaiya_8', lang)
        else:
            continue

        # Accurate year calculation using full birth date
        year_start = None
        year_end = None
        if birth_date is not None:
            # Calculate exact start and end dates
            start_date = birth_date + timedelta(days=int(step * step_days))
            end_date = birth_date + timedelta(days=int((step + 1) * step_days))
            
            year_start = start_date.year
            year_end = end_date.year

        events.append({
            "age_start": round(age_start, 1),
            "age_end": round(age_end, 1),
            "year_start": year_start,
            "year_end": year_end,
            "rasi": rasi_names[rasi_idx],
            "phase": phase
        })

    return events


def _render_shani_sare_sati_html(moon_rasi: str, planets_data: list, user_dob: str = "", max_age: float = 100.0, lang: str = "as") -> str:
    """Render the Sade Sati section in the user's selected language.

    Uses language-specific templates from shani_sare_sati_pdf_templates.
    """
    from translations import get_text
    t = lambda k: get_text(k, lang)
    events = get_shani_sare_sati_data(moon_rasi, planets_data, user_dob, max_age, lang)

    if not events:
        return f'<div class="empty-msg">{t("pdf_sare_sati_empty")}</div>'

    rows = ""
    for e in events:
        year_col = ""
        if e["year_start"] is not None and e["year_end"] is not None:
            year_col = "<td>{}-{}</td>".format(e["year_start"], e["year_end"])
        else:
            year_col = "<td>\xe2\x80\x94</td>"
        rows += """
            <tr>
                <td>{:.1f} - {:.1f}</td>
                {year_col}
                <td>{rasi}</td>
                <td>{phase}</td>
            </tr>""".format(
                e["age_start"],
                e["age_end"],
                year_col=year_col,
                rasi=e["rasi"],
                phase=e["phase"],
            )

    # Use language-specific templates
    from shani_sare_sati_pdf_templates import get_sare_sati_template
    template = get_sare_sati_template(lang)

    # Build Sade Sati phase cards (3 phases)
    phase_cards_list = []
    for phase in template["phases"]:
        bullets_html = ""
        for bold, text in phase["main_effects"]:
            bullets_html += "<li><b>{}</b> {}</li>".format(bold, text)
        phase_card = (
            '<div class="ss-phase-card">'
            '<div class="ss-phase-title">{title}</div>'
            '<div class="ss-phase-body">'
            '<p>{intro}</p>'
            '<p class="ss-sub-heading">{main_label}</p>'
            '<ul>{bullets}</ul>'
            '<p class="ss-sub-heading">{precautions_label}</p>'
            '<p>{precautions}</p>'
            '</div>'
            '</div>'
        ).format(
            title=phase["title"],
            intro=phase["intro"],
            main_label=t("pdf_ss_main_effects"),
            bullets=bullets_html,
            precautions_label=t("pdf_ss_precautions"),
            precautions=phase["precautions_text"],
        )
        phase_cards_list.append(phase_card)
    phase_cards = "".join(phase_cards_list)

    # Build Dhaiya phase cards (2 phases)
    dhaiya_cards_list = []
    for dphase in template["dhaiya_phases"]:
        bullets_html = ""
        for bold, text in dphase["bullets"]:
            bullets_html += "<li><b>{}</b> {}</li>".format(bold, text)
        dhaiya_card = (
            '<div class="ss-phase-card">'
            '<div class="ss-phase-title">{title}</div>'
            '<div class="ss-phase-body">'
            '<p>{intro}</p>'
            '<ul>{bullets}</ul>'
            '</div>'
            '</div>'
        ).format(
            title=dphase["title"],
            intro=dphase["intro"],
            bullets=bullets_html,
        )
        dhaiya_cards_list.append(dhaiya_card)
    dhaiya_cards = "".join(dhaiya_cards_list)

    return (
        '<div class="sare-sati-box">'
        '<p class="sare-sati-note">{note}</p>'
        '<table class="sare-sati-table">'
        '<thead><tr><th>{age_col}</th><th>{year_col}</th><th>{rashi_col}</th><th>{phase_col}</th></tr></thead>'
        '<tbody>{tbody}</tbody>'
        '</table>'
        '</div>'
        '<div class="sare-sati-analysis">'
        '<h3 class="ss-analysis-heading">{analysis_heading}</h3>'
        '<p class="ss-analysis-intro">{analysis_intro}</p>'
        '{phase_cards}'
        '<div class="ss-note-box">'
        '<b>{special_note_label}:</b> {special_note}'
        '</div>'
        '<h3 class="ss-analysis-heading">{dhaiya_heading}</h3>'
        '{dhaiya_cards}'
        '</div>'
    ).format(
        note=t("pdf_sare_sati_note"),
        age_col=t("pdf_sare_sati_age_col"),
        year_col=t("pdf_sare_sati_year_col"),
        rashi_col=t("pdf_sare_sati_rashi_col"),
        phase_col=t("pdf_sare_sati_phase_col"),
        tbody=rows,
        analysis_heading=t("pdf_ss_analysis_heading"),
        analysis_intro=t("pdf_ss_analysis_intro"),
        phase_cards=phase_cards,
        special_note_label=t("pdf_ss_special_note"),
        special_note=template["special_note"],
        dhaiya_heading=t("pdf_ss_dhaiya_heading"),
        dhaiya_cards=dhaiya_cards,
    )






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
    antardasha_phala_html: str = "",
    dwadash_html: str = "",
    vimsottari_summary: str = "",
    selected_sections: list = None,
    lagna_lord: str = "",
    moon_rashi_lord: str = "",
    moon_rasi: str = "",
    gender: str = "male",
    astrologer_profile: dict = None,
    patrika_text: str = "",
    pratyantar_dasha_html: str = "",
    graha_maitri_html: str = "",
    kartari_html: str = "",
    ashtakavarga_html: str = "",
    prastara_ashtakavarga_html: str = "",
    ratna_html: str = "",
    lang: str = "as"
) -> str:
    """Build complete HTML for the PDF report.
    selected_sections: list of section keys to include. If None, include all.
    lang: language code ('as', 'bn', 'hi', 'en')
    """
    from prediction_i18n import get_panchanga_labels_i18n, get_panchanga_names_i18n
    from translations import get_text

    plabels = get_panchanga_labels_i18n(lang)
    pnames = get_panchanga_names_i18n(lang)
    t = lambda k: get_text(k, lang)  # shorthand for PDF i18n

    # Convert DOB from YYYY-MM-DD to DD-MM-YYYY format
    def _format_dob(dob_str):
        """Convert YYYY-MM-DD to DD-MM-YYYY"""
        if not dob_str or len(dob_str) < 10:
            return dob_str
        try:
            parts = dob_str.split('-')
            if len(parts) == 3:
                return f"{parts[2]}-{parts[1]}-{parts[0]}"
        except Exception:
            pass
        return dob_str
    
    # Format the DOB for use throughout the HTML
    user_dob_formatted = _format_dob(user_dob)
    
    # Helper: check if a section should be included
    def _include(key):
        if selected_sections is None:
            return True
        return key in selected_sections

    rasi_names = pnames['RASHI_NAMES']
    varga_names = {
        "D1": get_text('varga_d1', lang), "D2": get_text('varga_d2', lang),
        "D3": get_text('varga_d3', lang), "D4": get_text('varga_d4', lang),
        "D7": get_text('varga_d7', lang), "D9": get_text('varga_d9', lang),
        "D10": get_text('varga_d10', lang), "D12": get_text('varga_d12', lang),
        "D16": get_text('varga_d16', lang), "D20": get_text('varga_d20', lang),
        "D24": get_text('varga_d24', lang), "D27": get_text('varga_d27', lang),
        "D30": get_text('varga_d30', lang), "D40": get_text('varga_d40', lang),
        "D45": get_text('varga_d45', lang), "D60": get_text('varga_d60', lang)
    }

    # ── Planet Table Rows ──
    from prediction_i18n import (
        get_kundli_rashi_name_i18n, get_nakshatra_name_i18n, get_planet_name_i18n,
    )
    from app import get_eng_planet
    planet_rows = ""
    for p in planets_data:
        # Get planet name in target language
        # name_en (English) is the language-neutral key for get_planet_name_i18n
        p_eng = p.get('name_en', '')
        if p_eng:
            p_name = get_planet_name_i18n(p_eng, lang)
        else:
            # No English name (e.g., for Lagna); just use name_asm or name as-is
            p_name = p.get('name_asm', '') or p.get('name', '')

        # Get rashi name in target language
        # Prefer rasi_idx (numeric, language-agnostic); fall back to rashi (already in user's lang)
        if 'rasi_idx' in p:
            p_rasi = get_kundli_rashi_name_i18n(p['rasi_idx'], lang)
        else:
            p_rasi = p.get('rasi', '')

        # Get nakshatra name in target language
        if 'nak_idx' in p:
            p_nak = get_nakshatra_name_i18n(p['nak_idx'], lang)
        else:
            p_nak = p.get('nakshatra', '')

        # Get nakshatra lord in target language
        # lord field is in user's lang from get_nakshatra_details
        # If for some reason it's in another lang, convert via English
        lord_val = p.get('lord', '')
        if lord_val:
            lord_eng = get_eng_planet(lord_val)
            p_lord = get_planet_name_i18n(lord_eng, lang)
        else:
            p_lord = ''

        planet_rows += f"""
        <tr class="prow-{p_eng.lower()}">
            <td><b>{p_name}</b></td>
            <td>{p_rasi}</td>
            <td>{p['degree']}°</td>
            <td>{p_nak}</td>
            <td>{p_lord}</td>
            <td class="state-cell">{p.get('state', '—')}</td>
        </tr>"""

    # ── Panchanga Items ──
    pada_label = get_text('panchanga_pada', lang)
    panchanga_items = [
        (plabels['tithi'], panchanga.get('tithi', {}).get('name', '—'), panchanga.get('paksha', '')),
        (plabels['nakshatra'], panchanga.get('nakshatra', {}).get('name', '—'), f"{pada_label}: {panchanga.get('nakshatra', {}).get('pada', '—')}"),
        (plabels['yoga'], panchanga.get('yoga', {}).get('name', '—'), ''),
        (plabels['karana'], panchanga.get('karana', {}).get('name', '—'), ''),
        (plabels['vaar'], panchanga.get('vaar', {}).get('name', '—'), ''),
        (plabels['ritu'], panchanga.get('ritu', {}).get('name', '—'), ''),
        (plabels['masa'], panchanga.get('masa', {}).get('name', '—'), ''),
        (plabels['ayan'], f"{panchanga.get('ayanamsa', '—')}°", get_text('panchanga_lahiri', lang)),
        (plabels['sunrise'], panchanga.get('sunrise', '—'), ''),
        (plabels['sunset'], panchanga.get('sunset', '—'), ''),
        (get_text('panchanga_rahu_kalam', lang), panchanga.get('rahu_kalam', '—'), ''),
        (get_text('panchanga_yama_gandam', lang), panchanga.get('yama_gandam', '—'), ''),
        (get_text('panchanga_gulika', lang), panchanga.get('gulika_kalam', '—'), ''),
        (get_text('panchanga_abhijit', lang), panchanga.get('abhijit_muhurta', '—'), ''),
        (get_text('panchanga_yama_kaal', lang), panchanga.get('yama_kaal', '—'), ''),
        (get_text('panchanga_kaal_bela', lang), panchanga.get('kaal_bela', '—'), ''),
        (get_text('panchanga_bara_bela', lang), panchanga.get('bara_bela', '—'), ''),
        (get_text('panchanga_divaman', lang), panchanga.get('divaman', '—'), ''),
        (get_text('panchanga_ratriman', lang), panchanga.get('ratriman', '—'), ''),
        (get_text('panchanga_jata_danda', lang), panchanga.get('jata_danda', '—'), ''),
        (get_text('panchanga_varna', lang), panchanga.get('varna', '—'), ''),
        (get_text('panchanga_gana', lang), panchanga.get('gana', '—'), ''),
        (get_text('panchanga_yoni', lang), panchanga.get('yoni', '—'), ''),
        (get_text('panchanga_nadi', lang), panchanga.get('nadi', '—'), ''),
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
            sev = d.get('severity_text', t('pdf_dosha_present'))
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
                    <div><span class="d-name">{name}</span><span class="d-severity low">{t('pdf_dosha_absent')}</span></div>
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
                    <div class="y-effect"><b>{t('pdf_yoga_effect')}:</b> {y.get('effect', '')}</div>
                </div>
            </div>"""
    else:
        yoga_html = f'<div class="empty-msg">{t("pdf_yoga_none")}</div>'

    # ── Dasha Summary ──
    # Use localized *_display fields for planet names in the user's language
    dasha_rows = ""
    for md in dasa_data[:5]:
        maha_display = md.get('md_lord_display') or md.get('md_lord', '')
        ad_names_list = []
        for ad in md.get('sub_dasas', [])[:3]:
            ad_names_list.append(ad.get('ad_lord_display') or ad.get('ad_lord', ''))
        ad_names = ', '.join(ad_names_list)
        dasha_rows += f"""
        <tr>
            <td>{maha_display}</td>
            <td>{md['start']}</td>
            <td>{md['end']}</td>
            <td>{ad_names}</td>
        </tr>"""

    # ── Full Dasha (All Mahadasa + Antardasa with predictions) ──
    # Use localized *_display fields for planet names in the user's language
    full_dasha_html = ""
    for md in dasa_data:
        maha_display = md.get('md_lord_display') or md.get('md_lord', '')
        ad_rows = ""
        for ad in md.get('sub_dasas', []):
            ad_display = ad.get('ad_lord_display') or ad.get('ad_lord', '')
            ad_rows += f"""
            <tr>
                <td>{ad_display}</td>
                <td>{ad['start']}</td>
                <td>{ad['end']}</td>
            </tr>"""
        full_dasha_html += f"""
        <div class="md-block">
            <div class="md-title">★ {maha_display} ({md['start']} → {md['end']}) — {md.get('years', '')} {t('pdf_dasha_years')}</div>
            <table class="small-table">
                <thead><tr><th>{t('pdf_dasha_antardasha')}</th><th>{t('pdf_dasha_start')}</th><th>{t('pdf_dasha_end')}</th></tr></thead>
                <tbody>{ad_rows}</tbody>
            </table>
        </div>"""

    # ── All Dasha Predictions (81 combinations) ──
    # Get language-specific dasha terms
    from prediction_i18n import PLANET_NAMES_I18N
    # Use translation keys for Mahadasha and Antardasha labels
    maha_dasha_label = t('pdf_dasha_mahadasha')
    antar_dasha_label = t('pdf_dasha_antardasha')

    dasha_predictions_html = ""
    if all_dasha_predictions:
        for dp in all_dasha_predictions:
            pred_text = dp.get('prediction', '').replace('\n', '<br>')
            # Get language-specific planet names for the header
            maha_planet_name = PLANET_NAMES_I18N.get(lang, PLANET_NAMES_I18N['as']).get(dp.get('maha_eng', ''), dp.get('maha_asm', ''))
            antar_planet_name = PLANET_NAMES_I18N.get(lang, PLANET_NAMES_I18N['as']).get(dp.get('antar_eng', ''), dp.get('antar_asm', ''))
            dasha_predictions_html += f"""
            <div class="dasha-pred-block">
                <div class="dp-header">★ {maha_planet_name} {maha_dasha_label} → {antar_planet_name} {antar_dasha_label} <span class="dp-dates">({dp['start']} → {dp['end']})</span></div>
                <div class="dp-body">{pred_text}</div>
            </div>"""

    # ── Divisional Charts (prefer server-rendered PNGs to ensure font shaping)
    # Large D1 chart (embed PNG generated by kundli_chart.py if available)
    d1_svg = ""
    # Normalize rashi names and ascendant for NFC-consistent matching
    rasi_names_n = [unicodedata.normalize('NFC', r) for r in rasi_names]
    asc_rasi_n = unicodedata.normalize('NFC', asc_rasi) if asc_rasi else ''
    try:
        from kundli_chart import draw_kundli_chart

        def _embed_chart_png(chart_dict, asc_rasi_str=asc_rasi, w=450, h=450, style='bengali'):
            # determine ascendant index from string if possible
            try:
                asc_str_n = unicodedata.normalize('NFC', asc_rasi_str) if asc_rasi_str else ''
                asc_index = rasi_names_n.index(asc_str_n) if asc_str_n in rasi_names_n else 0
            except Exception:
                asc_index = 0
            buf = draw_kundli_chart(style=style, ascendant_index=asc_index, planet_data=chart_dict, width=w, height=h, lang=lang)
            img_bytes = buf.getvalue() if hasattr(buf, 'getvalue') else buf.read()
            b64 = base64.b64encode(img_bytes).decode('ascii')
            return f'<img src="data:image/png;base64,{b64}" alt="kundli" style="width:100%;height:auto;border-radius:8px;"/>'
        # embed D1 using the PIL renderer if available
        if all_vargas and "D1" in all_vargas:
            d1_svg = _embed_chart_png(all_vargas["D1"], w=420, h=420, style='bengali')
    except Exception:
        # Fallback to SVG generator if PIL/kundli_chart isn't available
        if all_vargas and "D1" in all_vargas:
            d1_svg = _svg_chart(all_vargas["D1"], size=450, title=t('pdf_d1_title'), show_rasi_names=True, lang=lang)

    # Small divisional charts (D2-D60)
    small_charts_html = ""
    if all_vargas:
        try:
            from kundli_chart import draw_kundli_chart
            for v_code in ["D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]:
                if v_code not in all_vargas:
                    continue
                vname = varga_names.get(v_code, v_code)
                # render small png for divisional chart (with lang parameter for i18n)
                try:
                    buf = draw_kundli_chart(style='bengali', ascendant_index=(rasi_names_n.index(asc_rasi_n) if asc_rasi_n in rasi_names_n else 0), planet_data=all_vargas[v_code], width=260, height=260, lang=lang)
                    img_bytes = buf.getvalue() if hasattr(buf, 'getvalue') else buf.read()
                    b64 = base64.b64encode(img_bytes).decode('ascii')
                    img_tag = f'<img src="data:image/png;base64,{b64}" alt="{v_code}" style="width:100%;height:auto;border:1px solid #e0e0e0;border-radius:4px;"/>'
                except Exception:
                    img_tag = _svg_chart(all_vargas[v_code], size=140, title=f"{v_code}", show_rasi_names=False, lang=lang)

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
                svg = _svg_chart(all_vargas[v_code], size=140, title=f"{v_code}", show_rasi_names=False, lang=lang)
                small_charts_html += f"""
                <div class="small-chart-card">
                    {svg}
                    <div class="small-chart-label">{v_code}<br>{vname}</div>
                </div>"""

    # ── Tripap Rista ──
    tripap_html = ""
    if tripap_data:
        # Use localized "No." prefix based on language
        no_prefix_map = {'as': 'নং', 'bn': 'নং', 'hi': 'क्र.', 'en': 'No.'}
        no_prefix = no_prefix_map.get(lang, 'নং')
        tripap_html += f"""
        <div class="tripap-header">
            <b>🌙 {t('pdf_tripap_moon_nak')}:</b> {tripap_data.get('nakshatra', '—')} ({no_prefix} {tripap_data.get('nakshatra_index', '—')})
        </div>
        <table class="small-table tripap-table">
            <thead><tr><th>{tripap_data.get('row_labels', {}).get('row_label', 'Row')}</th><th>{tripap_data.get('row_labels', {}).get('col_desc', 'Desc')}</th>"""
        for h in range(1, 13):
            tripap_html += f"<th>{tripap_data.get('row_labels', {}).get('col_house', 'House {}').format(h)}</th>"
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
                <b>⏳ {t('pdf_tripap_ages_note')} ({tripap_data.get('nakshatra', '')}):</b><br>
                {ages_str}
                <br><span class="small-note">{t('pdf_tripap_total_ages').format(n=len(tripap_ages))}</span>
            </div>"""

    # ── Graha Maitri (Planetary Friendship) ──
    if graha_maitri_html:
        # graha_maitri_html is already pre-built HTML from graha_maitri module
        pass  # Will be inserted in body assembly below

    # ââ AI Section ââ
    ai_html = ""
    if ai_interpretation:
        # Parse AI text - handles **Header:** markdown style
        import re as _re_ai
        raw_text = ai_interpretation.strip()
        lines = [l for l in raw_text.split(chr(10)) if l.strip() != ""]
        
        # Find intro greeting (e.g., "প্ৰিয় <name>,") at the start
        intro_greeting = ""
        intro_body_lines = []
        i = 0
        if lines and (lines[0].startswith("প্ৰিয়") or lines[0].startswith("প্রিয়") or "প্ৰিয়" in lines[0][:6]):
            intro_greeting = lines[0]
            i = 1
        
        def _is_md_header(ln):
            # Header from ai_engine.py is "**Title:**" - starts with ** and ends with **
            if not ln.startswith("**"):
                return False
            if ln.endswith(":**") or ln.endswith("ঃ**"):
                return True
            return False
        
        while i < len(lines):
            ln = lines[i].strip()
            if _is_md_header(ln):
                break
            intro_body_lines.append(ln)
            i += 1
        
        intro_body = " ".join(intro_body_lines).strip()
        
        ai_cards = ""
        
        # Add intro card
        if intro_greeting or intro_body:
            ai_cards += "<div class=\"ai-card ai-card-intro\">"
            if intro_greeting:
                ai_cards += "<div class=\"ai-card-greeting\">" + intro_greeting + "</div>"
            if intro_body:
                ai_cards += "<div class=\"ai-card-body\">" + intro_body + "</div>"
            ai_cards += "</div>"
        
        # Process remaining - split by **Header:** markers
        remaining = chr(10).join(lines[i:]) if i < len(lines) else ""
        
        section_pattern = _re_ai.compile(r"\*\*([^*]+?:)\*\*\s*(.*?)(?=\*\*[^*]+?:\*\*|\Z)", _re_ai.DOTALL)
        sections_found = section_pattern.findall(remaining) if remaining else []
        
        if sections_found:
            for header_text, body_text in sections_found:
                header_clean = header_text.strip()
                body_clean = body_text.strip()
                if not header_clean:
                    continue
                ai_cards += "<div class=\"ai-card\">"
                ai_cards += "<div class=\"ai-card-head\">" + header_clean + "</div>"
                if body_clean:
                    body_html = body_clean.replace(chr(10), "<br>")
                    ai_cards += "<div class=\"ai-card-body\">" + body_html + "</div>"
                ai_cards += "</div>"
        elif remaining:
            body_html = remaining.replace(chr(10), "<br>")
            ai_cards += "<div class=\"ai-card\"><div class=\"ai-card-body\">" + body_html + "</div></div>"
        
        # Closing signature card
        closing_text = t("pdf_ai_closing")
        ai_cards += "<div class=\"ai-card ai-card-closing\"><div class=\"ai-card-signature\">" + closing_text + "</div></div>"
        
        # Disclaimer footer
        ai_footer = "<div class=\"ai-footer-note\"><span class=\"ai-note-icon\">â ï¸</span><span>" + t("pdf_ai_disclaimer") + "</span></div>"
        
        ai_html = f"""
        <div class="ai-section-wrapper">
            <div class="ai-section-header">
                <div class="ai-header-icon">ð¤</div>
                <div class="ai-header-text">
                    <div class="ai-header-title">{t('pdf_ai_section_title')}</div>
                    <div class="ai-header-subtitle">{t('pdf_ai_section_subtitle')}</div>
                </div>
            </div>
            <div class="ai-divider"></div>
            <div class="ai-cards-container">{ai_cards}</div>
            {ai_footer}
        </div>"""
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

    ganesh_image_src = _get_ganesh_base64()
    ganesh_image_html = f'<img src="{ganesh_image_src}" alt="Ganesh" />' if ganesh_image_src else ''

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
        page-break-after: avoid;
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

    /* ── ৰঙীন গ্ৰহ ৰো (Colorful Planet Rows) ── */
    tr.prow-sun td {{ background: #FFF3E0; color: #E65100; font-weight: 700; }}
    tr.prow-moon td {{ background: #ECEFF1; color: #37474F; font-weight: 700; }}
    tr.prow-mars td {{ background: #FFEBEE; color: #C62828; font-weight: 700; }}
    tr.prow-mercury td {{ background: #E8F5E9; color: #1B5E20; font-weight: 700; }}
    tr.prow-jupiter td {{ background: #FFF8E1; color: #F57F17; font-weight: 700; }}
    tr.prow-venus td {{ background: #FCE4EC; color: #AD1457; font-weight: 700; }}
    tr.prow-saturn td {{ background: #ECEFF1; color: #263238; font-weight: 700; }}
    tr.prow-rahu td {{ background: #EDE7F6; color: #4527A0; font-weight: 700; }}
    tr.prow-ketu td {{ background: #EFEBE9; color: #4E342E; font-weight: 700; }}
    tr.prow-lagna td {{ background: #E3F2FD; color: #0D47A1; font-weight: 700; }}
    td.state-cell {{ font-size: 8pt; font-style: italic; letter-spacing: 0.2px; }}

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

    /* ─── AI Section New Design ─── */
    .ai-section-wrapper {{
        margin: 20px 0; page-break-inside: avoid;
    }}
    .ai-section-header {{
        display: flex; align-items: center; gap: 14px;
        background: linear-gradient(135deg, {DEEP_BLUE}, #283593);
        border-radius: 10px 10px 0 0; padding: 16px 20px;
    }}
    .ai-header-icon {{
        font-size: 28pt; flex-shrink: 0;
        width: 52px; height: 52px; display: flex;
        align-items: center; justify-content: center;
        background: rgba(255,255,255,0.15); border-radius: 50%;
    }}
    .ai-header-text {{ flex: 1; }}
    .ai-header-title {{
        font-size: 14pt; font-weight: 800; color: white;
        letter-spacing: 0.5px;
    }}
    .ai-header-subtitle {{
        font-size: 8pt; color: rgba(255,255,255,0.75);
        margin-top: 2px;
    }}
    .ai-divider {{
        height: 3px; background: linear-gradient(90deg, {ORANGE}, {DEEP_BLUE}, {ORANGE});
    }}
    .ai-cards-container {{
        background: white; border: 1px solid #e0e0e0;
        border-top: none; border-radius: 0 0 10px 10px;
        padding: 14px 18px;
    }}
    .ai-card {{
        margin-bottom: 10px; page-break-inside: avoid;
        border-radius: 8px; overflow: hidden;
        border: 1px solid #e8e0d5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .ai-card:last-child {{ margin-bottom: 0; }}
    .ai-card-head {{
        background: linear-gradient(135deg, #FFF8F0, #FFE0B2);
        padding: 10px 16px; font-weight: 700; font-size: 10pt;
        color: {DEEP_BLUE}; border-bottom: 1px solid #f0e0c8;
        letter-spacing: 0.2px;
    }}
    .ai-card-body {{
        padding: 12px 16px; font-size: 9pt; line-height: 1.9;
        color: #333; background: #fefefe;
        text-align: justify;
    }}
    .ai-card-intro {{
        background: linear-gradient(135deg, #E3F2FD, #F3E5F5);
        border: 1px solid #BBDEFB;
    }}
    .ai-card-intro .ai-card-greeting {{
        padding: 12px 16px 4px 16px;
        font-size: 12pt; font-weight: 700;
        color: {DEEP_BLUE};
        background: none;
    }}
    .ai-card-intro .ai-card-body {{
        padding: 4px 16px 12px 16px;
        background: transparent;
        font-style: italic;
        color: #444;
    }}
    .ai-card-closing {{
        background: linear-gradient(135deg, #F1F8E9, #DCEDC8);
        border: 1px solid #C5E1A5;
        text-align: center;
    }}
    .ai-card-signature {{
        padding: 12px 16px; font-size: 9.5pt;
        color: {DEEP_BLUE}; font-weight: 600;
        font-style: italic;
    }}
    .ai-footer-note {{
        margin-top: 12px; padding: 8px 14px;
        background: #FFF3E0; border-left: 3px solid {ORANGE};
        border-radius: 0 6px 6px 0; font-size: 7.5pt;
        color: #E65100; display: flex; align-items: center; gap: 6px;
        line-height: 1.6;
    }}
    .ai-note-icon {{ font-size: 10pt; flex-shrink: 0; }}
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
    .chart-large-page3 {{
        text-align: center; margin: 16px auto; padding: 20px;
        background: linear-gradient(135deg, #FFF8E1 0%, #FFF3E0 30%, #FCE4EC 70%, #F3E5F5 100%);
        border: 2px solid {ORANGE}; border-radius: 12px;
        box-shadow: 0 4px 20px rgba(255,102,0,0.12);
        max-width: 480px;
    }}
    .chart-large-page3 img {{
        max-width: 100%; height: auto;
        border-radius: 8px;
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

    /* Graha Maitri (Planetary Friendship) */
    .maitri-pdf-section {{
        margin-bottom: 10px; page-break-inside: avoid;
    }}
    .maitri-pdf-table {{
        width: 100%; border-collapse: collapse; font-size: 6.5pt;
        margin-bottom: 8px;
    }}
    .maitri-pdf-table th {{
        background: {DEEP_BLUE}; color: white; padding: 3px 4px;
        font-size: 6.5pt; font-weight: 700; text-align: center;
        border: 1px solid #ccc;
    }}
    .maitri-pdf-table td {{
        padding: 2px 4px; text-align: center; border: 1px solid #ccc;
        font-size: 6.5pt; font-weight: 500;
    }}
    .maitri-pdf-table .row-header {{
        background: #E8EAF6; font-weight: 700; color: {DEEP_BLUE};
        text-align: left; padding-left: 6px;
    }}
    .maitri-pdf-table .cell-self {{ background: #E0E0E0; color: #999; }}
    .maitri-pdf-table .cell-mitra {{ background: #C8E6C9; color: #1B5E20; font-weight: 600; }}
    .maitri-pdf-table .cell-shatru {{ background: #FFCDD2; color: #B71C1C; font-weight: 600; }}
    .maitri-pdf-table .cell-sam {{ background: #FFF9C4; color: #F57F17; font-weight: 600; }}
    .maitri-pdf-table .cell-adhimitra {{ background: #A5D6A7; color: #1B5E20; font-weight: 700; }}
    .maitri-pdf-table .cell-adhishatru {{ background: #EF9A9A; color: #B71C1C; font-weight: 700; }}
    .maitri-pdf-legend {{
        display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;
        margin-top: 6px; padding: 6px 10px; background: #fafafa;
        border-radius: 4px; font-size: 6.5pt;
    }}
    .maitri-pdf-legend-item {{
        display: flex; align-items: center; gap: 4px;
    }}
    .maitri-pdf-swatch {{
        width: 12px; height: 12px; border-radius: 2px; border: 1px solid #ccc;
    }}
    .maitri-pdf-house-row {{
        display: flex; flex-wrap: wrap; gap: 6px; justify-content: center;
        margin-bottom: 10px; font-size: 7pt;
    }}
    .maitri-pdf-house-badge {{
        background: #E8EAF6; padding: 3px 10px; border-radius: 12px;
        font-weight: 600; color: {DEEP_BLUE};
    }}

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
        margin: 6px 0 8px; page-break-inside: avoid; page-break-after: avoid;
    }}
    .shloka-outer-box {{
        background: linear-gradient(135deg, #FFF8E1 0%, #FFF3E0 30%, #FCE4EC 70%, #F3E5F5 100%);
        border: 2px solid {ORANGE};
        border-radius: 10px;
        padding: 10px 16px;
        position: relative;
        box-shadow: 0 2px 8px rgba(255,102,0,0.08);
        page-break-inside: avoid;
    }}
    .shloka-outer-box::before {{
        content: "🕉️";
        position: absolute;
        top: -14px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 18pt;
        background: white;
        padding: 0 10px;
        border-radius: 50%;
    }}
    .ganesh-image-container {{
        text-align: center; margin-bottom: 4px;
    }}
    .ganesh-image-container img {{
        display: inline-block;
        max-width: 120px;
        width: 100%;
        height: auto;
        margin: 0 auto;
    }}
    .shloka-title {{
        text-align: center;
        font-size: 9pt;
        font-weight: 800;
        color: {ORANGE};
        margin: 4px 0 8px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }}
    .shloka-block {{
        text-align: center;
        margin-bottom: 6px;
        padding: 6px 10px;
        background: rgba(255,255,255,0.55);
        border-radius: 6px;
        border: 1px dashed #e0c8a0;
    }}
    .shloka-text {{
        font-size: 7.5pt;
        font-weight: 600;
        color: {DEEP_BLUE};
        line-height: 1.8;
        letter-spacing: 0.2px;
        font-family: 'Noto Sans Bengali', 'Nirmala UI', 'Vrinda', sans-serif;
    }}
    .shloka-divider {{
        text-align: center;
        margin: 4px 0;
        font-size: 11pt;
        color: {ORANGE};
        letter-spacing: 4px;
    }}
    .shloka-footer-text {{
        text-align: center;
        font-size: 7pt;
        font-weight: 600;
        color: #888;
        margin-top: 4px;
        font-style: italic;
    }}

    /* ── জন্মপত্ৰিকা Title ── */
    .patrika-title-section {{
        text-align: center;
        margin: 22px 0 14px;
        page-break-inside: avoid;
        page-break-before: avoid;
    }}
    .patrika-main-title {{
        font-size: 24pt;
        font-weight: 900;
        color: {ORANGE};
        letter-spacing: 3px;
        text-shadow: 2px 2px 4px rgba(255,102,0,0.18);
        font-family: 'Noto Sans Bengali', 'Nirmala UI', 'Vrinda', sans-serif;
        line-height: 1.2;
    }}
    .patrika-ornament {{
        color: {ORANGE};
        font-size: 10pt;
        letter-spacing: 5px;
        margin: 4px 0;
    }}

    /* ── প্ৰকাশিত নাম ও ব্যক্তিগত তথ্য Card ── */
    .patrika-info-card {{
        display: inline-block;
        background: linear-gradient(135deg, #FFF8E1 0%, #FFF3E0 40%, #FCE4EC 100%);
        border: 2px solid {ORANGE};
        border-radius: 14px;
        padding: 16px 40px;
        margin: 10px auto 20px;
        box-shadow: 0 4px 18px rgba(255,102,0,0.14);
        text-align: center;
        min-width: 320px;
        page-break-inside: avoid;
        page-break-before: avoid;
    }}
    .patrika-published-label {{
        font-size: 9pt;
        font-weight: 600;
        color: #999;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 4px;
        font-family: 'Noto Sans Bengali', 'Nirmala UI', 'Vrinda', sans-serif;
    }}
    .patrika-name {{
        font-size: 16pt;
        font-weight: 800;
        color: {DEEP_BLUE};
        letter-spacing: 1.5px;
        font-family: 'Noto Sans Bengali', 'Nirmala UI', 'Vrinda', sans-serif;
        margin-bottom: 10px;
        padding-bottom: 10px;
        border-bottom: 1px dashed #e0c8a0;
    }}
    .patrika-details {{
        font-size: 10pt;
        color: #444;
        line-height: 2.2;
        font-family: 'Noto Sans Bengali', 'Nirmala UI', 'Vrinda', sans-serif;
    }}
    .patrika-details b {{
        color: {ORANGE};
        font-weight: 700;
    }}
    .patrika-details span {{
        color: {DEEP_BLUE};
        font-weight: 600;
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

    /* Sare Sati Detailed Analysis */
    .sare-sati-analysis {{
        margin-top: 0;
        page-break-inside: avoid;
    }}
    .ss-analysis-heading {{
        font-size: 11pt;
        font-weight: 800;
        color: {DEEP_BLUE};
        margin: 16px 0 10px;
        padding-bottom: 4px;
        border-bottom: 2px solid {ORANGE};
    }}
    .ss-analysis-intro {{
        font-size: 9pt;
        color: #444;
        line-height: 1.7;
        margin-bottom: 12px;
        text-align: justify;
    }}
    .ss-phase-card {{
        background: #FFFDF7;
        border: 1px solid #FFE0B2;
        border-left: 4px solid {ORANGE};
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 10px;
        page-break-inside: avoid;
    }}
    .ss-phase-title {{
        font-size: 10pt;
        font-weight: 800;
        color: {ORANGE};
        margin-bottom: 8px;
        padding-bottom: 4px;
        border-bottom: 1px dashed #e0c8a0;
    }}
    .ss-phase-body {{
        font-size: 8.5pt;
        color: #333;
        line-height: 1.8;
        text-align: justify;
    }}
    .ss-phase-body p {{
        margin-bottom: 6px;
    }}
    .ss-sub-heading {{
        font-size: 9pt;
        font-weight: 700;
        color: {DEEP_BLUE};
        margin: 8px 0 4px;
    }}
    .ss-phase-body ul {{
        margin: 4px 0 8px 16px;
        list-style-type: disc;
    }}
    .ss-phase-body ul li {{
        margin-bottom: 4px;
        line-height: 1.7;
    }}
    .ss-note-box {{
        background: #FFF3E0;
        border: 2px solid #FFCC80;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 12px 0;
        font-size: 8.5pt;
        color: #5D4037;
        line-height: 1.8;
        text-align: justify;
        page-break-inside: avoid;
    }}

    /* Dwadash Bhab Phala */
    .dwadash-phala-container {{
        margin-bottom: 0;
    }}
    .dwadash-house-section {{
        margin-bottom: 8px; padding: 10px 12px;
        background: #FFFDF7; border: 2px solid #FFE0B2;
        border-radius: 6px;
    }}
    .dwadash-house-title {{
        font-size: 10pt; font-weight: 800; color: {ORANGE};
        margin-bottom: 6px; border-bottom: 2px solid {ORANGE};
        padding-bottom: 4px;
    }}
    .dwadash-house-title h4 {{
        margin: 0; padding: 0; font-size: 10pt; font-weight: 800;
        display: inline; color: {ORANGE};
    }}
    .dwadash-house-title .dwadash-badge {{
        background: {ORANGE}; color: #fff;
        font-size: 7pt; font-weight: 700;
        padding: 2px 8px; border-radius: 10px;
        margin-left: 8px;
    }}
    .dwadash-positions {{
        font-size: 9pt; line-height: 1.8;
    }}
    .dwadash-position-item {{
        margin-bottom: 4px; padding: 6px 8px;
        background: white; border-left: 3px solid {DEEP_BLUE};
        border-radius: 3px;
    }}
    .position-label {{
        font-weight: 700; color: {ORANGE}; font-size: 9pt;
        margin-bottom: 4px;
    }}
    .position-phala {{
        font-size: 9pt; color: #333; text-align: justify;
        margin-top: 2px; line-height: 1.8;
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
    <h1>🌟 {t('pdf_title')}</h1>
    <div class="sub">{t('pdf_subtitle')}</div>
</div>
<hr class="divider">

<!-- ═══════════════ <!-- ═════════════ INVOCATORY SHLOKAS ═════════════ -->
<div class="shloka-section">
    <div class="shloka-outer-box">
        <div class="ganesh-image-container">
            {ganesh_image_html}
        </div>
        <div class="shloka-title">{t('pdf_shloka_title')}</div>

        <div class="shloka-block">
            <div class="shloka-text">
                {t('pdf_shloka_block1')}
            </div>
        </div>

        <div class="shloka-divider">{t('pdf_shloka_om')}</div>

        <div class="shloka-block">
            <div class="shloka-text">
                {t('pdf_shloka_block2')}
            </div>
        </div>

        <div class="shloka-footer-text">{t('pdf_shloka_footer')}</div>
    </div>
</div>
<!-- ═══════════════════════════════════════════ -->

<!-- ═══════════════ জন্মপত্ৰিকা TITLE ═══════════════ -->
<div class="patrika-title-section">
    <div class="patrika-ornament">❖  ॐ  ❖</div>
    <div class="patrika-main-title">{t('pdf_patrika_title')}</div>
</div>

<!-- ═══════════ প্ৰকাশিত নাম ও তথ্য ═══════════ -->
<div style="text-align:center;">
    <div class="patrika-info-card">
        <div class="patrika-published-label">{t('pdf_patrika_published')}</div>
        <div class="patrika-name">{user_name}</div>
        <div class="patrika-details">
            <b>{t('pdf_patrika_dob_label')}</b> <span>{user_dob_formatted}</span> &nbsp;&nbsp;|&nbsp;&nbsp; <b>{t('pdf_patrika_tob_label')}</b> <span>{user_tob}</span><br>
            <b>{t('pdf_patrika_place_label')}</b> <span>{user_place}</span>
        </div>
    </div>
</div>
<!-- ═══════════════════════════════════════════════════ -->

<!-- ═══════════════ PAGE BREAK → ২য় পৃষ্ঠা ═══════════════ -->
<div style="page-break-before: always;"></div>

<h2 class="section-heading">📋 {t('pdf_personal_info')}</h2>
<div class="info-grid">
    <div class="info-item"><b>{t('pdf_name')}:</b> {user_name}</div>
    <div class="info-item"><b>{t('pdf_gender')}:</b> {t('pdf_gender_female') if gender == "female" else t('pdf_gender_male')}</div>
    <div class="info-item"><b>{t('pdf_birth_place')}:</b> {user_place}</div>
    <div class="info-item"><b>{t('pdf_birth_date')}:</b> {user_dob_formatted}</div>
    <div class="info-item"><b>{t('pdf_birth_time')}:</b> {user_tob}</div>
    <div class="info-item"><b>{t('pdf_lagna')}:</b> {asc_rasi}</div>
    <div class="info-item"><b>{t('pdf_lagna_lord')}:</b> {lagna_lord}</div>
    <div class="info-item"><b>{t('pdf_moon_rashi')}:</b> {moon_rasi}</div>
    <div class="info-item"><b>{t('pdf_moon_rashi_lord')}:</b> {moon_rashi_lord}</div>
    <div class="info-item"><b>{t('panchanga_varna')}:</b> {panchanga.get('varna', '—')}</div>
    <div class="info-item"><b>{t('panchanga_gana')}:</b> {panchanga.get('gana', '—')}</div>
    <div class="info-item"><b>{t('panchanga_yoni')}:</b> {panchanga.get('yoni', '—')}</div>
    <div class="info-item"><b>{t('panchanga_nadi')}:</b> {panchanga.get('nadi', '—')}</div>
    <div class="info-item"><b>{t('panchanga_jata_danda')}:</b> {panchanga.get('jata_danda', '—')}</div>
    <div class="info-item"><b>{t('panchanga_divaman')}:</b> {panchanga.get('divaman', '—')}</div>
    <div class="info-item"><b>{t('panchanga_ratriman')}:</b> {panchanga.get('ratriman', '—')}</div>
</div>
"""

    # Build body sections using string concatenation (not f-string inline conditionals)
    if _include('panchanga'):
        html += '<h2 class="section-heading">🕉️ ' + t('pdf_panchanga_section') + '</h2><div class="p-grid">' + panchanga_html + '</div>'

    if _include('planets_table'):
        html += '<h2 class="section-heading">🪐 ' + t('pdf_planets_section') + '</h2><table><thead><tr><th>' + t('pdf_planet_col') + '</th><th>' + t('pdf_rashi_col') + '</th><th>' + t('pdf_degree_col') + '</th><th>' + t('pdf_nakshatra_col') + '</th><th>' + t('pdf_nak_lord_col') + '</th><th>' + t('pdf_state_col') + '</th></tr></thead><tbody>' + planet_rows + '</tbody></table>'

    # ═══════════════ PAGE BREAK → ৩য় পৃষ্ঠা (জন্ম কুণ্ডলী) ═══════════════
    if _include('kundli_chart'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">📊 ' + t('pdf_kundli_section') + '</h2>'
        html += '<div class="chart-large-page3">' + d1_svg + '</div>'
        # Patrika text below D1 chart
        if patrika_text:
            patrika_html = patrika_text.replace('\n', '<br>')
            html += '<div style="margin:12px 0;padding:14px 18px;background:linear-gradient(135deg,#FFF8E1,#FFF3E0);border:2px solid #FFCC80;border-radius:8px;font-size:9pt;line-height:2.2;text-align:justify;font-family:\'Noto Sans Bengali\',\'Nirmala UI\',sans-serif;">' + patrika_html + '</div>'

    # ═══════════════ PAGE BREAK → ৪ৰ্থ পৃষ্ঠা (বিভাগীয় কুণ্ডলী) ═══════════════
    if _include('varga_charts'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">📊 ' + t('pdf_varga_section') + '</h2><div class="charts-grid">' + small_charts_html + '</div>'

    shani_sare_sati_html = _render_shani_sare_sati_html(moon_rasi, planets_data, user_dob, lang=lang)
    if _include('shani_sare_sati'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">🌑 ' + t('pdf_shani_section') + '</h2>' + shani_sare_sati_html

    if _include('dosha'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">⚠️ ' + t('pdf_dosha_section') + '</h2>' + dosha_html

    if _include('yoga'):
        html += '<h2 class="section-heading">✨ ' + t('pdf_yoga_section') + '</h2>' + yoga_html

    if _include('sannari'):
        html += '<h2 class="section-heading">🌀 ' + t('pdf_sannari_section') + '</h2>' + sannari_html

    if _include('navatara'):
        html += '<h2 class="section-heading">🌀 ' + t('pdf_navatara_section') + '</h2>' + navatara_html

    if _include('tripap'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">☠️ ' + t('pdf_tripap_section') + '</h2>' + tripap_html

    if _include('graha_maitri'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">🤝 ' + t('pdf_graha_maitri_section') + '</h2>' + graha_maitri_html

    if _include('kartari'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">🔮 ' + t('pdf_kartari_section') + '</h2>' + kartari_html

    if _include('ashtakavarga'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">🔢 ' + t('pdf_ashtakavarga_section') + '</h2>' + ashtakavarga_html

    if _include('prastara_ashtakavarga'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">📋 ' + t('pdf_prastara_ashtakavarga_section') + '</h2>' + prastara_ashtakavarga_html

    if _include('nakshatra_phala'):
        html += '<h2 class="section-heading">🌟 ' + t('pdf_nakshatra_phala_section') + '</h2>' + nakshatra_phala_html

    if _include('lagna_phala'):
        html += '<h2 class="section-heading">🌅 ' + t('pdf_lagna_phala_section') + '</h2>' + lagna_phala_html

    if _include('rashi_phala'):
        html += '<h2 class="section-heading">🌙 ' + t('pdf_rashi_phala_section') + '</h2>' + rashi_phala_html

    if _include('graha_bichar'):
        html += '<h2 class="section-heading">🪐 ' + t('pdf_graha_bichar_section') + '</h2>' + graha_bichar_html

    if _include('dwadash_bhab_phala'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">🏠 ' + t('pdf_dwadash_section') + '</h2>' + dwadash_html

    if vimsottari_summary and _include('dasha_summary'):
        html += '<h2 class="section-heading">📊 ' + t('pdf_dasha_summary_section') + '</h2><div style="background:#FFF8F0;border-left:4px solid #FF6600;padding:12px 16px;font-size:9pt;line-height:1.8;border-radius:6px;margin-bottom:10px;text-align:justify;font-family:\'Noto Sans Bengali\',\'Nirmala UI\',sans-serif;">' + vimsottari_summary.replace('\n', '<br>') + '</div>'
        html += '<table class="dasha-table"><thead><tr><th>' + t('pdf_dasha_mahadasha') + '</th><th>' + t('pdf_dasha_start') + '</th><th>' + t('pdf_dasha_end') + '</th><th>' + t('pdf_dasha_first3') + '</th></tr></thead><tbody>' + dasha_rows + '</tbody></table>'
    elif _include('dasha_summary'):
        html += '<h2 class="section-heading">⏳ ' + t('pdf_dasha_summary_section') + '</h2><table class="dasha-table"><thead><tr><th>' + t('pdf_dasha_mahadasha') + '</th><th>' + t('pdf_dasha_start') + '</th><th>' + t('pdf_dasha_end') + '</th><th>' + t('pdf_dasha_first3') + '</th></tr></thead><tbody>' + dasha_rows + '</tbody></table>'

    if _include('dasha_full'):
        html += '<h2 class="section-heading">⏳ ' + t('pdf_dasha_full_section') + '</h2>' + full_dasha_html

    if _include('dasha_predictions'):
        html += '<h2 class="section-heading">📝 ' + t('pdf_dasha_predictions_section') + '</h2>' + dasha_predictions_html

    # Language-specific font for content text
    if lang == 'hi':
        content_font = "'Noto Sans Devanagari', 'Noto Sans Bengali', sans-serif"
    elif lang == 'bn':
        content_font = "'Noto Sans Bengali', 'Nirmala UI', sans-serif"
    else:
        content_font = "'Noto Sans Bengali', 'Nirmala UI', sans-serif"

    if _include('antardasha_phala'):
        html += '<h2 class="section-heading">📖 ' + t('pdf_antardasha_section') + '</h2>'
        html += f'<div style="font-family:{content_font};font-size:8.5pt;line-height:1.6;">' + antardasha_phala_html + '</div>'
    
    if _include('pratyantar_dasha'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">🔮 ' + t('pdf_pratyantar_section') + '</h2>'
        html += f'<div style="font-family:{content_font};font-size:8.5pt;line-height:1.6;">' + pratyantar_dasha_html + '</div>'

    if _include('ratna'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">💎 ' + t('pdf_ratna_section') + '</h2>' + ratna_html

    if _include('ai'):
        html += ai_html

    html += f"""
<div class="footer">
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
    antardasha_phala_html: str = "",
    dwadash_html: str = "",
    vimsottari_summary: str = "",
    selected_sections: list = None,
    lagna_lord: str = "",
    moon_rashi_lord: str = "",
    moon_rasi: str = "",
    gender: str = "male",
    astrologer_profile: dict = None,
    patrika_text: str = "",
    pratyantar_dasha_html: str = "",
    graha_maitri_html: str = "",
    kartari_html: str = "",
    ashtakavarga_html: str = "",
    prastara_ashtakavarga_html: str = "",
    ratna_html: str = "",
    lang: str = "as"
) -> bytes:
    """
    Generate a complete professional PDF astrology report.
    Uses Playwright (Chromium) via subprocess for perfect text rendering.
    Returns PDF as bytes.
    lang: language code ('as', 'bn', 'hi', 'en')
    """
    html_content, astro_footer_html = _build_html(
        user_name, user_dob, user_tob, user_place,
        planets_data, panchanga, dosha_results,
        yoga_results, dasa_data, ai_interpretation,
        all_vargas, tripap_data, tripap_ages, asc_rasi,
        all_dasha_predictions, sannari_html, navatara_html,
        nakshatra_phala_html, lagna_phala_html, rashi_phala_html,
        graha_bichar_html=graha_bichar_html,
        antardasha_phala_html=antardasha_phala_html,
        dwadash_html=dwadash_html,
        vimsottari_summary=vimsottari_summary,
        selected_sections=selected_sections,
        lagna_lord=lagna_lord,
        moon_rashi_lord=moon_rashi_lord,
        moon_rasi=moon_rasi,
        gender=gender,
        astrologer_profile=astrologer_profile,
        patrika_text=patrika_text,
        pratyantar_dasha_html=pratyantar_dasha_html,
        graha_maitri_html=graha_maitri_html,
        kartari_html=kartari_html,
        ashtakavarga_html=ashtakavarga_html,
        prastara_ashtakavarga_html=prastara_ashtakavarga_html,
        ratna_html=ratna_html,
        lang=lang
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
            capture_output=True, text=True, timeout=120
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
