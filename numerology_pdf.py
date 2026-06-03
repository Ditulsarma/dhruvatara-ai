"""
ধ্ৰুৱতৰা AI - অংক জ্যোতিষ PDF জেনেৰেটৰ
Numerology PDF Report Generator: Generates stylish Assamese numerology PDF reports
using Playwright (Chromium) for perfect Assamese/Bengali text rendering.
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
GOLD = '#D4A017'
PURPLE = '#6A1B9A'


def _build_numerology_html(report: dict, selected_sections: list = None,
                           astrologer_profile: dict = None) -> str:
    """Build complete HTML for the numerology PDF report."""

    if selected_sections is None:
        selected_sections = ['lo_shu', 'missing', 'present', 'mulyanka', 'bhagyanka',
                             'namanka', 'name_compat', 'angel', 'pratikar', 'final']

    name = report.get('name', '')
    dob = report.get('dob', '')

    # Format DOB
    try:
        y, m, d = dob.split('-')
        dob_display = f"{d}/{m}/{y}"
    except (ValueError, IndexError):
        dob_display = dob

    html = f'''<!DOCTYPE html>
<html lang="as">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;500;600;700;800&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Noto Sans Bengali', 'Nirmala UI', sans-serif;
            color: #2c3e50; background: #FFF8F0; font-size: 11px;
            line-height: 1.8; padding: 0;
        }}
        .cover {{
            background: linear-gradient(135deg, #1a237e, #283593);
            color: white; padding: 40px 30px; text-align: center;
            border-radius: 0 0 30px 30px; margin-bottom: 20px;
        }}
        .cover h1 {{ font-size: 24px; font-weight: 800; margin-bottom: 4px; }}
        .cover .subtitle {{ font-size: 13px; opacity: 0.85; }}
        .cover .info {{ margin-top: 16px; font-size: 12px; }}
        .cover .info span {{ display: inline-block; margin: 0 12px; }}
        .section {{
            background: white; border-radius: 12px; padding: 18px 20px;
            margin: 12px 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            border: 1px solid #e8e0d5; page-break-inside: avoid;
        }}
        .section h2 {{
            font-size: 15px; color: #1a237e; margin-bottom: 10px;
            border-bottom: 2px solid #FF6600; padding-bottom: 6px;
            display: flex; align-items: center; gap: 8px;
        }}
        .section h3 {{
            font-size: 13px; color: #FF6600; margin: 10px 0 6px;
        }}
        .grid-table {{
            border-collapse: collapse; margin: 10px auto; width: 280px;
        }}
        .grid-table td {{
            border: 2px solid #1a237e; width: 80px; height: 80px;
            text-align: center; vertical-align: middle; font-size: 28px;
            font-weight: 800; color: #1a237e; border-radius: 4px;
        }}
        .grid-table td.empty {{ color: #ccc; font-size: 18px; }}
        .grid-table td.highlight {{ background: #FFF3E0; }}
        .number-card {{
            display: inline-block; background: #FFF8F0; border-radius: 8px;
            padding: 8px 14px; margin: 4px; border-left: 3px solid #FF6600;
            font-size: 10px;
        }}
        .number-card .num {{ font-size: 18px; font-weight: 800; color: #FF6600; }}
        .remedy-box {{
            background: #E8F5E9; border-radius: 8px; padding: 12px 16px;
            margin: 8px 0; border-left: 3px solid #2E7D32;
        }}
        .remedy-box h4 {{ color: #2E7D32; font-size: 12px; margin-bottom: 4px; }}
        .warn-box {{
            background: #FFF3E0; border-radius: 8px; padding: 12px 16px;
            margin: 8px 0; border-left: 3px solid #E65100;
        }}
        .info-row {{
            display: flex; gap: 10px; flex-wrap: wrap; margin: 8px 0;
        }}
        .info-chip {{
            background: #E3F2FD; border-radius: 20px; padding: 6px 14px;
            font-size: 10px; font-weight: 600; color: #1565C0;
        }}
        .year-row {{
            display: flex; justify-content: space-between; padding: 6px 10px;
            border-bottom: 1px dotted #ddd; font-size: 10px;
        }}
        .year-row:nth-child(odd) {{ background: #fafafa; }}
        .year-num {{ font-weight: 700; color: #FF6600; min-width: 50px; }}
        .footer {{
            text-align: center; padding: 16px; font-size: 9px;
            color: #999; border-top: 1px solid #e8e0d5; margin-top: 20px;
        }}
        .astro-footer {{
            text-align: center; padding: 8px 16px; font-size: 9px;
            color: #555;
        }}
        .astro-footer .astro-name {{ font-weight: 700; font-size: 10px; color: #1a237e; }}
        .astro-footer .astro-inst {{ font-size: 10px; color: #FF6600; font-weight: 600; }}
    </style>
</head>
<body>
<div class="cover">
    <h1>🔢 অংক জ্যোতিষ ৰিপৰ্ট</h1>
    <div class="subtitle">ধ্ৰুৱতৰা AI - Numerology Report</div>
    <div class="info">
        <span>👤 {name}</span>
        <span>📅 {dob_display}</span>
    </div>
</div>
'''

    # ─── Lo Shu Grid ───
    if 'lo_shu' in selected_sections:
        grid = report.get('lo_shu_grid', {}).get('grid', [["", "", ""], ["", "", ""], ["", "", ""]])
        html += '''
<div class="section">
    <h2>🔢 ল' চু গ্ৰীড (Lo Shu Grid)</h2>
    <table class="grid-table">
'''
        for i in range(3):
            html += '<tr>'
            for j in range(3):
                val = grid[i][j]
                has_value = val and str(val).strip() != '' and str(val) != '0'
                cls = 'highlight' if has_value else 'empty'
                display = str(val) if has_value else '—'
                html += f'<td class="{cls}">{display}</td>'
            html += '</tr>'
        html += '''
    </table>
    <p style="text-align:center;font-size:10px;color:#888;margin-top:6px;">ল' চু গ্ৰীড আপোনাৰ জন্ম তাৰিখৰ সংখ্যাৰ ওপৰত আধাৰিত।</p>
</div>
'''

    # ─── Missing Numbers ───
    if 'missing' in selected_sections:
        missing_analysis = report.get('missing_analysis', [])
        if missing_analysis:
            html += '<div class="section"><h2>❌ অনুপস্থিত সংখ্যা</h2>'
            for m in missing_analysis:
                html += f'''
<div class="number-card">
    <span class="num">{m['number']}</span> — {m['planet']}<br>
    {m['effect']}
</div>'''
            html += '</div>'

    # ─── Present Numbers ───
    if 'present' in selected_sections:
        present_analysis = report.get('present_analysis', [])
        if present_analysis:
            html += '<div class="section"><h2>✅ উপস্থিত সংখ্যা</h2>'
            for p in present_analysis:
                html += f'''
<div class="number-card">
    <span class="num">{p['number']}</span> ({p['count']}×) — {p['planet']}<br>
    {p['effect']}
</div>'''
            html += '</div>'

    # ─── Core Numbers ───
    if 'mulyanka' in selected_sections:
        m = report.get('mulyanka', {})
        html += f'''
<div class="section">
    <h2>🎯 মূল্যাংক (Psychic Number)</h2>
    <div class="info-row">
        <span class="info-chip">সংখ্যা: {m.get('value', '—')}</span>
        <span class="info-chip">গ্ৰহ: {m.get('planet', '—')}</span>
    </div>
    <p>{m.get('description', '')}</p>
    <p><strong>সকাৰাত্মক:</strong> {m.get('positive', '')}</p>
    <p><strong>নকাৰাত্মক:</strong> {m.get('negative', '')}</p>
</div>'''

    if 'bhagyanka' in selected_sections:
        b = report.get('bhagyanka', {})
        html += f'''
<div class="section">
    <h2>🌟 ভাগ্যাংক (Destiny Number)</h2>
    <div class="info-row">
        <span class="info-chip">সংখ্যা: {b.get('value', '—')}</span>
        <span class="info-chip">গ্ৰহ: {b.get('planet', '—')}</span>
    </div>
    <p>{b.get('description', '')}</p>
    <p><strong>সকাৰাত্মক:</strong> {b.get('positive', '')}</p>
    <p><strong>নকাৰাত্মক:</strong> {b.get('negative', '')}</p>
</div>'''

    if 'namanka' in selected_sections:
        n = report.get('namanka', {})
        html += f'''
<div class="section">
    <h2>📛 নামাংক (Name Number)</h2>
    <div class="info-row">
        <span class="info-chip">সংখ্যা: {n.get('value', '—')}</span>
        <span class="info-chip">গ্ৰহ: {n.get('planet', '—')}</span>
        <span class="info-chip">মূল যোগফল: {n.get('raw_total', '—')}</span>
    </div>
    <p>{n.get('description', '')}</p>
</div>'''

    # ─── Name Compatibility ───
    if 'name_compat' in selected_sections:
        nc = report.get('name_compatibility', {})
        compat_icon = '✅' if nc.get('compatible') else '⚠️'
        html += f'''
<div class="section">
    <h2>{compat_icon} নাম সামঞ্জস্য</h2>
    <p>স্ক'ৰ: <strong>{nc.get('score', 0)}%</strong></p>
    <p>{nc.get('description', '')}</p>
'''
        for reason in nc.get('reasons', []):
            html += f'<p>• {reason}</p>'
        if nc.get('correction'):
            html += f'<div class="warn-box"><strong>💡 নাম সংশোধনৰ পৰামৰ্শ:</strong><br>{nc["correction"]}</div>'
        html += '</div>'

    # ─── Angel Number ───
    if 'angel' in selected_sections:
        a = report.get('angel_number', {})
        html += f'''
<div class="section">
    <h2>👼 এঞ্জেল সংখ্যা</h2>
    <div class="info-row">
        <span class="info-chip" style="font-size:16px;font-weight:800;">{a.get('value', '—')}</span>
    </div>
    <p>{a.get('description', '')}</p>
</div>'''

    # ─── Varsha Phal ───
    if 'varsha_phal' in selected_sections:
        vp = report.get('detailed_varsha_phal', report.get('varsha_phal', []))
        if vp:
            html += '<div class="section"><h2>📅 বৰ্ষফল (১০ বছৰ)</h2>'
            for v in vp:
                html += f'''
<div class="year-row">
    <span class="year-num">{v['year']}</span>
    <span style="color:#888;">ব্যক্তিগত বৰ্ষ: {v['personal_year_number']}</span>
    <span style="flex:1;margin-left:10px;white-space:pre-line;">{v['prediction']}</span>
</div>'''
            html += '</div>'

    # ─── Lo Shu Grid Planes (8 Yogas) ───
    if 'planes' in selected_sections:
        planes = report.get('planes', [])
        if planes:
            html += '<div class="section"><h2>🧩 ল\' চু গ্ৰীডৰ ৮ যোগ (Planes)</h2>'
            for p in planes:
                status_icon = {'complete': '✅', 'partial': '🟡', 'weak': '🟠', 'missing': '❌'}.get(p.get('status_class', ''), '❌')
                html += f'''
<div style="margin-bottom:14px;padding:12px 16px;background:#fafafa;border-left:4px solid #1a237e;border-radius:6px;">
    <strong style="font-size:12px;color:#1a237e;">{p.get('name_short', '')}</strong>
    <span style="font-size:10px;margin-left:8px;">{status_icon} {p.get('status_text', '')}</span>
    <div style="font-size:10px;color:#666;">সংখ্যা: {' — '.join([str(n) for n in p.get('numbers', [])])}</div>
    <p style="font-size:10px;line-height:1.6;">{p.get('description', '')}</p>'''
                if p.get('status') == 'complete':
                    html += f'''
    <p style="font-size:10px;"><strong>✅ শুভ প্ৰভাৱ (Good Effect):</strong> {p.get('personality', '')}</p>
    <p style="font-size:10px;"><strong>💼 উপযুক্ত পেচা:</strong> {p.get('career', '')}</p>'''
                else:
                    html += f'''
    <p style="font-size:10px;color:#C62828;"><strong>⚠️ কুপ্ৰভাৱ (Bad Effect):</strong> {p.get('bad_effects', '')}</p>'''
                if p.get('partial_note'):
                    html += f'<p style="font-size:9px;color:#888;">{p.get("partial_note", "")}</p>'
                html += '</div>'
            html += '</div>'

    # ─── Pratikar (Remedies) ───
    if 'pratikar' in selected_sections:
        pr = report.get('pratikar', {})
        html += '<div class="section"><h2>🪬 প্ৰতিকাৰ (Remedies)</h2>'

        if pr.get('gems'):
            html += '<div class="remedy-box"><h4>💎 ৰত্ন</h4>'
            for g in pr['gems']:
                html += f'<p>• {g}</p>'
            html += '</div>'

        if pr.get('mantras'):
            html += '<div class="remedy-box"><h4>🕉️ মন্ত্ৰ</h4>'
            for m_item in pr['mantras']:
                html += f'<p>• {m_item}</p>'
            html += '</div>'

        if pr.get('rudraksha'):
            html += '<div class="remedy-box"><h4>📿 ৰুদ্ৰাক্ষ</h4>'
            for r in pr['rudraksha']:
                html += f'<p>• {r}</p>'
            html += '</div>'

        if pr.get('general'):
            html += '<div class="remedy-box"><h4>🌿 সাধাৰণ উপায়</h4>'
            for g_item in pr['general']:
                html += f'<p>• {g_item}</p>'
            html += '</div>'

        html += '</div>'

    # ─── Final Prediction ───
    if 'final' in selected_sections:
        final = report.get('final_prediction', '')
        if final:
            html += f'''
<div class="section">
    <h2>📋 চূড়ান্ত ভৱিষ্যদ্বাণী</h2>
    <p style="white-space:pre-line;">{final}</p>
</div>'''

    # ─── Footer ───
    html += '<div class="footer">ধ্ৰুৱতৰা AI | অংক জ্যোতিষ ৰিপৰ্ট | ' + datetime.now().strftime('%d/%m/%Y') + '</div>'

    # ─── Astrologer Footer ───
    if astrologer_profile:
        inst = astrologer_profile.get('institution_name', '').strip()
        astro_name = astrologer_profile.get('astrologer_name', '').strip()
        bio = astrologer_profile.get('astrologer_bio', '').strip()
        addr = astrologer_profile.get('address', '').strip()
        mob = astrologer_profile.get('mobile', '').strip()
        footer_lines = []
        if inst:
            footer_lines.append(f'<div class="astro-inst">{inst}</div>')
        if astro_name:
            footer_lines.append(f'<div class="astro-name">{astro_name}</div>')
        if bio:
            footer_lines.append(f'<div>{bio}</div>')
        if addr:
            footer_lines.append(f'<div>{addr}</div>')
        if mob:
            footer_lines.append(f'<div>📞 {mob}</div>')
        if footer_lines:
            html += '<div class="astro-footer">' + ''.join(footer_lines) + '</div>'

    html += '</body></html>'
    return html


def generate_numerology_pdf(report: dict, selected_sections: list = None,
                            astrologer_profile: dict = None) -> bytes:
    """
    Generate a stylish numerology PDF report.
    Uses Playwright subprocess for reliable PDF generation.
    """
    html = _build_numerology_html(report, selected_sections, astrologer_profile)

    # Write HTML to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html)
        html_path = f.name

    pdf_path = html_path.replace('.html', '.pdf')

    try:
        # Use the pdf_worker.py script
        worker_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pdf_worker.py')
        result = subprocess.run(
            [sys.executable, worker_path, html_path, pdf_path],
            capture_output=True, text=True, timeout=60
        )

        if result.returncode != 0:
            raise RuntimeError(f"PDF worker failed: {result.stderr}")

        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        return pdf_bytes

    finally:
        # Cleanup temp files
        try:
            os.unlink(html_path)
        except OSError:
            pass
        try:
            os.unlink(pdf_path)
        except OSError:
            pass
