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
    chart_data: dict mapping rasi_index (0-11) -> list of planet short codes
    """
    S = size
    M = S // 2  # center
    # Box positions for 12 rasis in Bengali fixed layout
    # Layout: top row 3, right col 2, bottom row 3, left col 2, bottom-center 2
    boxes = [
        (M, int(S*0.28), 0),           # 0  মেষ - top center
        (int(S*0.25), int(S*0.13), 1), # 1  বৃষ - top left
        (int(S*0.13), int(S*0.25), 2), # 2  মিথুন - left top
        (int(S*0.28), M, 3),           # 3  কৰ্কট - left center
        (int(S*0.13), int(S*0.75), 4), # 4  সিংহ - left bottom
        (int(S*0.25), int(S*0.87), 5), # 5  কন্যা - bottom left
        (M, int(S*0.72), 6),           # 6  তুলা - bottom center
        (int(S*0.75), int(S*0.87), 7), # 7  বৃশ্চিক - bottom right
        (int(S*0.87), int(S*0.75), 8), # 8  ধনু - right bottom
        (int(S*0.72), M, 9),           # 9  মকৰ - right center
        (int(S*0.87), int(S*0.25), 10),# 10 কুম্ভ - right top
        (int(S*0.75), int(S*0.13), 11),# 11 মীন - top right
    ]
    rasi_names = ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"]

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">'
    svg += f'<rect x="0" y="0" width="{S}" height="{S}" fill="#fafafa" stroke="#2c3e50" stroke-width="2"/>'
    # Diagonal lines
    svg += f'<line x1="0" y1="0" x2="{S}" y2="{S}" stroke="#2c3e50" stroke-width="1.5"/>'
    svg += f'<line x1="{S}" y1="0" x2="0" y2="{S}" stroke="#2c3e50" stroke-width="1.5"/>'
    # Diamond
    svg += f'<line x1="{M}" y1="0" x2="{S}" y2="{M}" stroke="#2c3e50" stroke-width="1.5"/>'
    svg += f'<line x1="{S}" y1="{M}" x2="{M}" y2="{S}" stroke="#2c3e50" stroke-width="1.5"/>'
    svg += f'<line x1="{M}" y1="{S}" x2="0" y2="{M}" stroke="#2c3e50" stroke-width="1.5"/>'
    svg += f'<line x1="0" y1="{M}" x2="{M}" y2="0" stroke="#2c3e50" stroke-width="1.5"/>'

    for cx, cy, ri in boxes:
        planets = chart_data.get(ri, [])
        if show_rasi_names:
            svg += f'<text x="{cx}" y="{cy - 12}" text-anchor="middle" font-size="{S*0.028}" fill="#7f8c8d" font-family="Noto Sans Bengali, Nirmala UI, sans-serif">{rasi_names[ri]}</text>'
        # Planet symbols
        if planets:
            fs = S * 0.042 if size >= 300 else S * 0.05
            line_h = fs * 1.25
            start_y = cy + 6
            for pi, p in enumerate(planets):
                svg += f'<text x="{cx}" y="{start_y + pi * line_h}" text-anchor="middle" font-size="{fs}" fill="#1a237e" font-weight="bold" font-family="Noto Sans Bengali, Nirmala UI, sans-serif">{p}</text>'

    if title:
        svg += f'<text x="{M}" y="{S - 6}" text-anchor="middle" font-size="{S*0.03}" fill="#FF6600" font-weight="bold" font-family="Noto Sans Bengali, Nirmala UI, sans-serif">{title}</text>'
    svg += '</svg>'
    return svg

# ─── HTML Template ──────────────────────────────────────────────

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
    selected_sections: list = None
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
        ('সূৰ্য্যোদয়', panchanga.get('sunrise', '—'), ''),
        ('সূৰ্য্যাস্ত', panchanga.get('sunset', '—'), ''),
        ('ৰাহুকাল', panchanga.get('rahu_kalam', '—'), ''),
        ('যমগণ্ড', panchanga.get('yama_gandam', '—'), ''),
        ('অভিজিৎ মুহূৰ্ত', panchanga.get('abhijit_muhurta', '—'), ''),
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

    # ── Divisional Charts (All 16 Varga Charts as SVG) ──
    # Large D1 chart
    d1_svg = ""
    if all_vargas and "D1" in all_vargas:
        d1_svg = _svg_chart(all_vargas["D1"], size=450, title="D1 - ৰাশি চক্ৰ (Rashi)", show_rasi_names=True)

    # Small divisional charts (D2-D60)
    small_charts_html = ""
    if all_vargas:
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

    now_str = datetime.now().strftime("%d-%m-%Y %H:%M")

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
        color: {DARK_GREY}; font-size: 10pt; line-height: 1.6;
    }}
    .header {{ text-align: center; margin-bottom: 16px; }}
    .header h1 {{ font-size: 22pt; color: {DEEP_BLUE}; font-weight: 800; }}
    .header .sub {{ font-size: 11pt; color: {DARK_GREY}; }}
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
        display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px;
        margin: 8px 0;
    }}
    .small-chart-card {{
        text-align: center; padding: 4px; background: #fafafa;
        border: 1px solid #e0e0e0; border-radius: 4px;
    }}
    .small-chart-card svg {{ width: 100%; height: auto; }}
    .small-chart-label {{
        font-size: 6pt; font-weight: 700; color: {ORANGE}; margin-top: 2px;
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
        margin-bottom: 8px; page-break-inside: avoid;
        border: 1px solid #e0e0e0; border-radius: 4px;
        overflow: hidden;
    }}
    .dp-header {{
        font-weight: 700; font-size: 8pt; color: {DEEP_BLUE};
        background: #E8EAF6; padding: 4px 8px;
    }}
    .dp-dates {{ font-size: 7pt; color: #888; font-weight: 400; }}
    .dp-body {{
        font-size: 7.5pt; padding: 6px 8px; line-height: 1.5;
        color: {DARK_GREY};
    }}

    .footer {{
        margin-top: 24px; padding-top: 10px; border-top: 2px solid {ORANGE};
        text-align: center; font-size: 7pt; color: #999;
    }}
</style>
</head>
<body>

<div class="header">
    <h1>🌟 ধ্ৰুৱতৰা AI</h1>
    <div class="sub">বৈদিক জ্যোতিষ সম্পূৰ্ণ ৰিপৰ্ট</div>
</div>
<hr class="divider">

<h2 class="section-heading">📋 ব্যক্তিগত তথ্য</h2>
<div class="info-grid">
    <div class="info-item"><b>নাম:</b> {user_name}</div>
    <div class="info-item"><b>জন্মৰ স্থান:</b> {user_place}</div>
    <div class="info-item"><b>জন্মৰ তাৰিখ:</b> {user_dob}</div>
    <div class="info-item"><b>জন্মৰ সময়:</b> {user_tob}</div>
</div>
"""

    # Build body sections using string concatenation (not f-string inline conditionals)
    if _include('panchanga'):
        html += '<h2 class="section-heading">🕉️ পঞ্চাঙ্গ</h2><div class="p-grid">' + panchanga_html + '</div>'

    if _include('planets_table'):
        html += '<h2 class="section-heading">🪐 গ্ৰহৰ অৱস্থান</h2><table><thead><tr><th>গ্ৰহ</th><th>ৰাশি</th><th>ডিগ্ৰী</th><th>নক্ষত্ৰ</th><th>নক্ষত্ৰ পতি</th></tr></thead><tbody>' + planet_rows + '</tbody></table>'

    if _include('kundli_chart'):
        html += '<h2 class="section-heading">📊 জন্ম কুণ্ডলী (D1 - ৰাশি চক্ৰ)</h2><div class="chart-large">' + d1_svg + '</div>'

    if _include('varga_charts'):
        html += '<h2 class="section-heading">📊 ষোড়শবৰ্গ বিভাগীয় কুণ্ডলী (D2 - D60)</h2><div class="charts-grid">' + small_charts_html + '</div>'

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
    <p>ধ্ৰুৱতৰা AI • বৈদিক জ্যোতিষ • {now_str}</p>
    <p>এই ৰিপৰ্ট কেৱল জ্যোতিষীয় তথ্যৰ বাবে। ই কোনো চিকিৎসা, আইনী, বা বিত্তীয় পৰামৰ্শ নহয়।</p>
</div>

</body>
</html>"""

    return html


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
    selected_sections: list = None
) -> bytes:
    """
    Generate a complete professional PDF astrology report in Assamese.
    Uses Playwright (Chromium) via subprocess for perfect Assamese text rendering.
    Returns PDF as bytes.
    """
    html_content = _build_html(
        user_name, user_dob, user_tob, user_place,
        planets_data, panchanga, dosha_results,
        yoga_results, dasa_data, ai_interpretation,
        all_vargas, tripap_data, tripap_ages, asc_rasi,
        all_dasha_predictions, sannari_html, navatara_html,
        nakshatra_phala_html, lagna_phala_html, rashi_phala_html,
        graha_bichar_html=graha_bichar_html,
        selected_sections=selected_sections
    )

    # Write HTML to temp file, call pdf_worker.py in subprocess, read PDF back
    worker_script = os.path.join(os.path.dirname(__file__), 'pdf_worker.py')
    python_exe = sys.executable

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', encoding='utf-8', delete=False) as html_file:
        html_file.write(html_content)
        html_path = html_file.name

    pdf_path = html_path + '.pdf'

    try:
        result = subprocess.run(
            [python_exe, worker_script, html_path, pdf_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            raise RuntimeError(f"PDF worker failed: {result.stderr}")

        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        return pdf_bytes
    finally:
        # Clean up temp files
        for path in [html_path, pdf_path]:
            try:
                os.unlink(path)
            except OSError:
                pass
