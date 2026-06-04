"""
ধ্ৰুৱতৰা AI - যোটক মিলন PDF ৰিপৰ্ট জেনেৰেটৰ
Jotok Milan PDF Generator: Professional Assamese marriage matching PDF report
Uses Playwright (Chromium) via subprocess for perfect Assamese text rendering.
"""

import os
import sys
import subprocess
import tempfile
import io

# ─── Colors ─────────────────────────────────────────────────────
ORANGE = '#FF6600'
DEEP_BLUE = '#1a237e'
DARK_GREY = '#333333'
LIGHT_BG = '#FFF8F0'
WHITE = '#FFFFFF'
RED = '#C62828'
GREEN = '#2E7D32'
PINK = '#E91E63'
GOLD = '#D4A017'


def generate_jotok_milan_pdf(result: dict, boy: dict, girl: dict,
                               astrologer_profile: dict = None) -> bytes:
    """
    Generate a professional Assamese marriage matching PDF report.
    Uses Playwright (Chromium) for perfect Assamese text rendering.
    Returns PDF as bytes.
    """
    html_content = _build_jotok_html(result, boy, girl, astrologer_profile)

    # Use sync Playwright directly (more reliable than subprocess)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            page = browser.new_page()
            page.set_content(html_content, wait_until='networkidle', timeout=30000)
            page.wait_for_load_state('networkidle')
            page.evaluate('document.fonts.ready')
            pdf_bytes = page.pdf(
                format='A4',
                margin={'top': '12mm', 'bottom': '12mm', 'left': '16mm', 'right': '16mm'},
                print_background=True
            )
            browser.close()
            return pdf_bytes
    except ImportError:
        pass

    # Fallback: subprocess approach
    worker_script = os.path.join(os.path.dirname(__file__), 'pdf_worker.py')
    python_exe = sys.executable

    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', encoding='utf-8', delete=False) as html_file:
        html_file.write(html_content)
        html_path = html_file.name

    pdf_path = html_path + '.pdf'

    try:
        cmd = [python_exe, worker_script, html_path, pdf_path]
        result_proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result_proc.returncode != 0:
            raise RuntimeError(f"PDF worker failed: {result_proc.stderr}")

        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        return pdf_bytes
    finally:
        for p in [html_path, pdf_path]:
            if os.path.exists(p):
                try:
                    os.unlink(p)
                except Exception:
                    pass


def _build_jotok_html(result: dict, boy: dict, girl: dict,
                       astrologer_profile: dict = None) -> str:
    """Build complete HTML for the Jotok Milan PDF report."""

    total = result['total_score']
    max_score = result['max_score']
    verdict = result['verdict']
    verdict_class = result['verdict_class']
    verdict_desc = result['verdict_desc']
    mangalik = result['mangalik']
    kootas = result['kootas']

    # ─── Koota order ───
    koota_order = ['varna', 'vashya', 'tara', 'yoni', 'graha_maitri', 'gana', 'bhakoot', 'nadi']
    koota_names = {
        'varna': 'বৰ্ণ কূট', 'vashya': 'বশ্য কূট', 'tara': 'তাৰা কূট',
        'yoni': 'যোনি কূট', 'graha_maitri': 'গ্ৰহ মৈত্ৰী কূট',
        'gana': 'গণ কূট', 'bhakoot': 'ভকূট কূট', 'nadi': 'নাড়ী কূট'
    }
    koota_icons = {
        'varna': '🕉️', 'vashya': '💑', 'tara': '⭐', 'yoni': '💕',
        'graha_maitri': '🪐', 'gana': '🎭', 'bhakoot': '🏠', 'nadi': '🧬'
    }

    # ─── Koota Summary Table ───
    koota_rows = ""
    for key in koota_order:
        k = kootas[key]
        score_color = GREEN if k['score'] >= k['max_score'] * 0.7 else (RED if k['score'] == 0 else '#E65100')
        koota_rows += f"""
        <tr>
            <td style="text-align:left;font-weight:700;">{koota_icons.get(key,'')} {koota_names.get(key,key)}</td>
            <td style="font-weight:800;color:{score_color};">{k['score']}</td>
            <td>{k['max_score']}</td>
            <td style="font-size:7pt;">{k['result']}</td>
        </tr>"""

    # ─── Detailed Koota Analysis ───
    koota_details_html = ""
    koota_descriptions = {
        'varna': {
            'title': '১। বৰ্ণ কূট — আধ্যাত্মিক আৰু মানসিক সামঞ্জস্য',
            'good': 'পাত্ৰ-পাত্ৰীৰ বৰ্ণগত সামঞ্জস্য অতি উত্তম। পাত্ৰৰ বৰ্ণ পাত্ৰীতকৈ উচ্চ বা সমান হোৱাৰ বাবে ই এক সুস্থ আৰু সমতাপূৰ্ণ দাম্পত্য সম্পৰ্কৰ ইংগিত দিয়ে। তেওঁলোকৰ মাজত পাৰস্পৰিক শ্ৰদ্ধা, বুজাবুজি, আৰু আধ্যাত্মিক চিন্তাধাৰাৰ মিল থাকিব।',
            'bad': "পাত্ৰ-পাত্ৰীৰ বৰ্ণগত অমিল আছে। দাম্পত্য জীৱনত কেতিয়াবা মানসিক দূৰত্ব আৰু অহংকাৰৰ সংঘাত হ'ব পাৰে। পাৰস্পৰিক শ্ৰদ্ধা আৰু বুজাবুজিৰ দ্বাৰা এই অমিল অতিক্ৰম কৰিব পাৰি।"
        },
        'vashya': {
            'title': '২। বশ্য কূট — পাৰস্পৰিক আকৰ্ষণ আৰু নিয়ন্ত্ৰণ',
            'good': 'বশ্য কূটত পূৰ্ণ গুণ — এক গভীৰ পাৰস্পৰিক আকৰ্ষণ আৰু প্ৰভাৱৰ সম্পৰ্ক। তেওঁলোকৰ মাজত এক স্বাভাৱিক চুম্বকীয় আকৰ্ষণ থাকিব, যিয়ে দাম্পত্য জীৱনক প্ৰগাঢ় কৰি ৰাখিব।',
            'mid': 'বশ্য কূটত আংশিক মিল। পাৰস্পৰিক বুজাবুজি আৰু সম্মানেৰে ভাৰসাম্য ৰক্ষা কৰিব পাৰি।',
            'bad': "বশ্য কূটত অমিল। স্বাভাৱিক আকৰ্ষণৰ অভাৱ হ'ব পাৰে। পৰস্পৰৰ প্ৰতি সহনশীলতা বৃদ্ধি কৰা উচিত।"
        },
        'tara': {
            'title': '৩। তাৰা কূট — ভাগ্য, স্বাস্থ্য আৰু মঙ্গল',
            'good': 'তাৰা কূটত পূৰ্ণ গুণ — অত্যন্ত শুভ! দাম্পত্য জীৱনত ভাগ্যৰ সহায় থাকিব। স্বাস্থ্য সুৰক্ষিত থাকিব।',
            'mid': 'তাৰা কূটত মধ্যম গুণ। দাম্পত্য জীৱনত কিছুমান উত্থান-পতন থাকিব পাৰে। সাৱধানতা অৱলম্বন কৰা উচিত।',
            'bad': 'তাৰা কূটত অশুভ গুণ — বিপৎ বা নৈধন তাৰা। স্বাস্থ্যজনিত সমস্যা বা অপ্রত্যাশিত বিপদৰ সম্ভাৱনা। পূজা-অৰ্চনা আৰু সাৱধানতাৰ প্ৰয়োজন।'
        },
        'yoni': {
            'title': '৪। যোনি কূট — শাৰীৰিক সামঞ্জস্য আৰু জৈৱিক সমতা',
            'good': "যোনি কূটত উত্তম গুণ। শাৰীৰিক আৰু জৈৱিক স্তৰত গভীৰ সামঞ্জস্য থাকিব। দাম্পত্য জীৱন প্ৰেম আৰু ঘনিষ্ঠতাৰে পৰিপূৰ্ণ হ'ব।",
            'mid': 'যোনি কূটত মধ্যম গুণ। শাৰীৰিক সম্পৰ্কত কিছু পাৰ্থক্য থাকিব পাৰে, কিন্তু প্ৰেমৰ দ্বাৰা অতিক্ৰম কৰিব পাৰি।',
            'bad': "যোনি কূটত অমিল — শত্ৰু যোনি। শাৰীৰিক সম্পৰ্কত গুৰুতৰ অমিল হ'ব পাৰে। বিশেষ পূজা-অৰ্চনাৰ প্ৰয়োজন।"
        },
        'graha_maitri': {
            'title': '৫। গ্ৰহ মৈত্ৰী কূট — মানসিক স্বভাৱ আৰু গ্ৰহগত বন্ধুত্ব',
            'good': 'গ্ৰহ মৈত্ৰী কূটত উত্তম গুণ। ৰাশি অধিপতি গ্ৰহদ্বয় পৰস্পৰৰ মিত্ৰ বা একে। মানসিক স্বভাৱ আৰু চিন্তাধাৰাৰ মাজত ভাল সামঞ্জস্য থাকিব।',
            'mid': 'গ্ৰহ মৈত্ৰী কূটত মধ্যম গুণ। মানসিক স্বভাৱত কিছু পাৰ্থক্য থাকিব পাৰে কিন্তু গুৰুতৰ সংঘাত নহয়।',
            'bad': 'গ্ৰহ মৈত্ৰী কূটত অমিল — ৰাশি অধিপতি শত্ৰু। মানসিক স্বভাৱত গুৰুতৰ পাৰ্থক্য থাকিব। মতানক্যৰ সম্ভাৱনা বেছি।'
        },
        'gana': {
            'title': '৬। গণ কূট — স্বভাৱগত মিল আৰু আচৰণ',
            'good': "গণ কূটত উত্তম গুণ। স্বভাৱ, আচৰণ, আৰু জীৱনশৈলীৰ মাজত ভাল সামঞ্জস্য। দাম্পত্য জীৱনত সংঘাতৰ পৰিমাণ নূন্যতম হ'ব।",
            'mid': 'গণ কূটত মধ্যম গুণ। স্বভাৱৰ পাৰ্থক্যই কেতিয়াবা সংঘাতৰ সৃষ্টি কৰিব পাৰে। পাৰস্পৰিক বুজাবুজিৰ প্ৰয়োজন।',
            'bad': 'গণ কূটত অমিল। স্বভাৱৰ মাজত গুৰুতৰ পাৰ্থক্য আছে। দাম্পত্য জীৱনত সংঘাতৰ সম্ভাৱনা বেছি। জ্যোতিষীৰ পৰামৰ্শ লওক।'
        },
        'bhakoot': {
            'title': '৭। ভকূট কূট — পাৰিবাৰিক কল্যাণ আৰু সমৃদ্ধি',
            'good': 'ভকূট কূটত পূৰ্ণ গুণ — কোনো ভকূট দোষ নাই! পাৰিবাৰিক কল্যাণ, অৰ্থনৈতিক সমৃদ্ধি, আৰু সুখ-শান্তি বিৰাজ কৰিব।',
            'mid': 'ভকূট কূটত মধ্যম গুণ। পাৰিবাৰিক জীৱনত কিছু উত্থান-পতন থাকিব পাৰে।',
            'bad': 'ভকূট কূটত দোষ উপস্থিত! পাৰিবাৰিক অশান্তি আৰু অৰ্থনৈতিক সংকটৰ সম্ভাৱনা। ভকূট দোষ নিবাৰণৰ প্ৰতিকাৰ কৰক।'
        },
        'nadi': {
            'title': '৮। নাড়ী কূট — সন্তান সুখ আৰু জিনগত স্বাস্থ্য',
            'good': 'নাড়ী কূটত পূৰ্ণ গুণ — নাড়ী দোষ সম্পূৰ্ণ অনুপস্থিত! সন্তান সুখ অতি শুভ। সুস্থ আৰু বুদ্ধিমান সন্তান লাভ কৰিব।',
            'bad': 'নাড়ী কূটত অমিল — নাড়ী দোষ উপস্থিত! সন্তানৰ ক্ষেত্ৰত সমস্যা আৰু স্বাস্থ্যজনিত জটিলতাৰ সম্ভাৱনা। নাড়ী দোষ নিবাৰণৰ বাবে বিশেষ পূজা আৰু জ্যোতিষীৰ পৰামৰ্শ অতি জৰুৰী।'
        }
    }

    for key in koota_order:
        k = kootas[key]
        desc = koota_descriptions.get(key, {})
        title = desc.get('title', key)
        if k['score'] >= k['max_score'] * 0.7:
            prediction = desc.get('good', '')
        elif k['score'] == 0:
            prediction = desc.get('bad', '')
        else:
            prediction = desc.get('mid', desc.get('good', ''))

        score_badge_class = 'kd-excellent' if k['score'] >= k['max_score'] * 0.7 else ('kd-bad' if k['score'] == 0 else 'kd-average')

        koota_details_html += f"""
        <div class="koota-detail">
            <div class="kd-header">
                <span class="kd-title">{title}</span>
                <span class="kd-score {score_badge_class}">{k['score']} / {k['max_score']} গুণ</span>
            </div>
            <div class="kd-desc">{k['description']}</div>
            <div class="kd-prediction">{prediction}</div>
        </div>"""

    # ─── Mangalik Section ───
    boy_mangalik = "⚠️ মাংগলিক" if mangalik['boy_mangalik'] else "✅ অমাংগলিক"
    girl_mangalik = "⚠️ মাংগলিক" if mangalik['girl_mangalik'] else "✅ অমাংগলিক"

    mangalik_analysis = ""
    if mangalik['boy_mangalik'] and mangalik['girl_mangalik']:
        mangalik_analysis = "পাত্ৰ আৰু পাত্ৰী উভয়ে মাংগলিক — <b>দোষ সাম্য</b>। উভয়ৰে মাংগলিক দোষ পৰস্পৰে নিষ্ক্ৰিয় কৰে। ই বিবাহৰ বাবে এক সুখবৰ!"
    elif mangalik['boy_mangalik']:
        mangalik_analysis = "পাত্ৰ মাংগলিক কিন্তু পাত্ৰী অমাংগলিক। মাংগলিক দোষ নিবাৰণৰ বাবে প্ৰতিকাৰ কৰাটো জৰুৰী।"
    elif mangalik['girl_mangalik']:
        mangalik_analysis = "পাত্ৰী মাংগলিক কিন্তু পাত্ৰ অমাংগলিক। মাংগলিক দোষ নিবাৰণৰ বাবে প্ৰতিকাৰ কৰাটো জৰুৰী।"
    else:
        mangalik_analysis = "পাত্ৰ আৰু পাত্ৰী উভয়ে অমাংগলিক। মাংগলিক দোষ সম্পূৰ্ণ অনুপস্থিত — অতি শুভ লক্ষণ।"

    remedies_html = ""
    if mangalik['boy_mangalik'] or mangalik['girl_mangalik']:
        remedies_items = ''.join(f'<li>{r}</li>' for r in mangalik.get('remedies', [])[:5])
        remedies_html = f'<div class="remedies"><h4>🛐 মাংগলিক দোষৰ প্ৰতিকাৰ:</h4><ul>{remedies_items}</ul></div>'

    # ─── Verdict styling ───
    verdict_colors = {
        'excellent': (GREEN, '#E8F5E9'),
        'good': ('#388E3C', '#E8F5E9'),
        'average': ('#E65100', '#FFF3E0'),
        'warning': (RED, '#FFEBEE'),
        'bad': ('#B71C1C', '#FFEBEE'),
    }
    v_color, v_bg = verdict_colors.get(verdict_class, (DEEP_BLUE, LIGHT_BG))

    # ─── Astrologer Header ───
    astro_header_html = ""
    if astrologer_profile:
        inst = astrologer_profile.get('institution_name', '').strip()
        name = astrologer_profile.get('astrologer_name', '').strip()
        bio = astrologer_profile.get('astrologer_bio', '').strip()
        addr = astrologer_profile.get('address', '').strip()
        mob = astrologer_profile.get('mobile', '').strip()

        lines = []
        if inst:
            lines.append(f'<div class="astro-inst">{inst}</div>')
        if name:
            lines.append(f'<div class="astro-name">{name}</div>')
        if bio:
            lines.append(f'<div class="astro-bio">{bio}</div>')
        if addr:
            lines.append(f'<div class="astro-addr">{addr}</div>')
        if mob:
            lines.append(f'<div class="astro-mob">📞 {mob}</div>')

        if lines:
            astro_header_html = f"""
            <div class="astro-header">
                <div class="astro-title">শ্ৰমেণ গণ্যতে কোষ্ঠীং </div>
                {''.join(lines)}
            </div>"""

    # ─── Nadi/Bhakoot warnings ───
    warnings_html = ""
    if result.get('has_nadi_dosha'):
        warnings_html += '<div class="warning-box">⚠️ <b>নাড়ী দোষ</b> উপস্থিত — নাড়ী দোষ নিবাৰণ নকৰাকৈ বিবাহ পৰামৰ্শিত নহয়।</div>'
    if result.get('has_bhakoot_dosha'):
        warnings_html += '<div class="warning-box">⚠️ <b>ভকূট দোষ</b> উপস্থিত — পাৰিবাৰিক কল্যাণৰ বাবে প্ৰতিকাৰ কৰক।</div>'

    # ═══════════════════════════════════════════════════════════════
    # FULL HTML
    # ═══════════════════════════════════════════════════════════════
    html = f"""<!DOCTYPE html>
<html lang="as">
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    @page {{ size: A4; margin: 12mm 16mm; }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: 'Noto Sans Bengali', 'Nirmala UI', 'Vrinda', sans-serif;
        color: {DARK_GREY}; font-size: 8pt; line-height: 1.5;
    }}

    /* ─── Astrologer Header (Top Center) ─── */
    .astro-header {{
        text-align: center; margin-bottom: 14px;
        padding: 12px 16px;
        background: linear-gradient(135deg, #FFF8F0, #FFF3E0);
        border: 2px solid {ORANGE}; border-radius: 8px;
    }}
    .astro-title {{
        font-size: 11pt; font-weight: 800; color: {ORANGE};
        margin-bottom: 6px; letter-spacing: 1px;
    }}
    .astro-inst {{ font-weight: 700; color: {DEEP_BLUE}; font-size: 9pt; }}
    .astro-name {{ font-weight: 600; color: {ORANGE}; font-size: 8.5pt; }}
    .astro-bio {{ color: #666; font-size: 7pt; font-style: italic; }}
    .astro-addr {{ color: #777; font-size: 7pt; }}
    .astro-mob {{ color: {DEEP_BLUE}; font-size: 7pt; font-weight: 500; }}

    /* ─── Main Title ─── */
    .main-title {{
        text-align: center; margin-bottom: 16px;
        padding: 16px;
        background: linear-gradient(135deg, {DEEP_BLUE}, #283593);
        color: white; border-radius: 8px;
    }}
    .main-title h1 {{ font-size: 18pt; font-weight: 800; }}
    .main-title .couple {{ font-size: 12pt; margin-top: 4px; }}
    .main-title .heart {{ color: #ff4081; }}

    /* ─── Score Circle ─── */
    .score-section {{
        text-align: center; margin: 16px 0;
    }}
    .score-circle {{
        display: inline-block; width: 90px; height: 90px;
        border-radius: 50%; border: 4px solid {v_color};
        background: {v_bg}; line-height: 1.2;
        padding-top: 18px;
    }}
    .score-num {{ font-size: 22pt; font-weight: 900; color: {v_color}; }}
    .score-max {{ font-size: 8pt; color: #888; }}
    .verdict-badge {{
        display: inline-block; padding: 6px 20px; border-radius: 20px;
        font-size: 10pt; font-weight: 700; margin-top: 8px;
        background: {v_color}; color: white;
    }}

    /* ─── Profile Cards ─── */
    .profile-row {{ display: flex; gap: 12px; margin-bottom: 14px; }}
    .profile-card {{
        flex: 1; border-radius: 6px; padding: 12px 14px;
        border: 1px solid #e8e0d5; background: white;
    }}
    .profile-card.boy {{ border-left: 4px solid {DEEP_BLUE}; }}
    .profile-card.girl {{ border-left: 4px solid {PINK}; }}
    .profile-card h3 {{ font-size: 10pt; margin-bottom: 6px; }}
    .profile-card.boy h3 {{ color: {DEEP_BLUE}; }}
    .profile-card.girl h3 {{ color: {PINK}; }}
    .profile-table {{ width: 100%; font-size: 8pt; }}
    .profile-table td {{ padding: 3px 2px; border-bottom: 1px dotted #eee; }}
    .profile-table td:first-child {{ font-weight: 600; color: #888; width: 45%; }}

    /* ─── Section Headings ─── */
    h2.section-heading {{
        font-size: 12pt; color: {ORANGE}; margin: 16px 0 8px;
        padding-bottom: 3px; border-bottom: 2px solid #e8e0d5;
    }}

    /* ─── Koota Summary Table ─── */
    .koota-table {{ width: 100%; border-collapse: collapse; margin-bottom: 12px; font-size: 8pt; }}
    .koota-table th {{ background: {DEEP_BLUE}; color: white; padding: 6px 8px; font-weight: 700; }}
    .koota-table td {{ padding: 5px 8px; border: 1px solid #e0e0e0; text-align: center; }}
    .koota-table tr:nth-child(even) {{ background: {LIGHT_BG}; }}
    .koota-table .total-row td {{
        font-weight: 800; font-size: 9pt; background: #FFF3E0;
        border-top: 2px solid {ORANGE};
    }}

    /* ─── Koota Detail Cards ─── */
    .koota-detail {{
        border: 1px solid #e8e0d5; border-radius: 6px;
        padding: 10px 14px; margin-bottom: 8px;
        background: #fdfdfd;
    }}
    .kd-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
    .kd-title {{ font-weight: 700; font-size: 9pt; color: {DEEP_BLUE}; }}
    .kd-score {{
        padding: 2px 10px; border-radius: 12px; font-size: 7pt; font-weight: 700;
    }}
    .kd-excellent {{ background: #E8F5E9; color: {GREEN}; }}
    .kd-average {{ background: #FFF3E0; color: #E65100; }}
    .kd-bad {{ background: #FFEBEE; color: {RED}; }}
    .kd-desc {{ font-size: 7.5pt; color: #666; margin-bottom: 4px; }}
    .kd-prediction {{
        font-size: 8pt; color: {DARK_GREY}; padding: 8px 10px;
        background: {LIGHT_BG}; border-radius: 4px;
        border-left: 3px solid {ORANGE};
    }}

    /* ─── Mangalik Section ─── */
    .mangalik-section {{
        background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
        border: 1px solid #FFCC80; border-radius: 8px;
        padding: 14px 16px; margin-bottom: 12px;
    }}
    .mangalik-section h2 {{ color: #E65100; }}
    .mangalik-row {{ display: flex; gap: 12px; margin: 10px 0; }}
    .mangalik-item {{
        flex: 1; background: white; border-radius: 6px;
        padding: 10px; text-align: center;
    }}
    .mangalik-item .mi-label {{ font-size: 7pt; color: #888; }}
    .mangalik-item .mi-value {{ font-size: 9pt; font-weight: 700; margin-top: 2px; }}
    .mi-yes {{ color: {RED}; }}
    .mi-no {{ color: {GREEN}; }}
    .remedies {{ margin-top: 10px; }}
    .remedies h4 {{ font-size: 9pt; color: #E65100; margin-bottom: 4px; }}
    .remedies ul {{ margin-left: 16px; font-size: 7.5pt; color: #555; }}
    .remedies li {{ margin-bottom: 2px; }}

    /* ─── Conclusion ─── */
    .conclusion {{
        background: linear-gradient(135deg, #E8EAF6, #C5CAE9);
        border: 2px solid {DEEP_BLUE}; border-radius: 8px;
        padding: 16px 20px; text-align: center; margin: 16px 0;
    }}
    .conclusion h2 {{ color: {DEEP_BLUE}; border: none; }}
    .conclusion-text {{ font-size: 9pt; line-height: 1.7; margin: 10px 0; }}
    .blessing {{ font-size: 10pt; font-weight: 700; color: {ORANGE}; font-style: italic; margin-top: 10px; }}

    .warning-box {{
        background: #FFEBEE; color: {RED}; border: 1px solid #FFCDD2;
        border-radius: 4px; padding: 8px 12px; margin: 6px 0;
        font-size: 8pt; font-weight: 600;
    }}

    .footer-note {{
        text-align: center; font-size: 7pt; color: #aaa; margin-top: 20px;
        border-top: 1px solid #e8e0d5; padding-top: 8px;
    }}
</style>
</head>
<body>

{astro_header_html}

<div class="main-title">
    <h1>💍 যোটক মিলন ৰিপৰ্ট</h1>
    <div class="couple">{boy['name']} <span class="heart">💖</span> {girl['name']}</div>
</div>

<div class="score-section">
    <div class="score-circle">
        <div class="score-num">{total}</div>
        <div class="score-max">/ {max_score} গুণ</div>
    </div>
    <div class="verdict-badge">{verdict}</div>
</div>

<!-- Profile Cards -->
<div class="profile-row">
    <div class="profile-card boy">
        <h3>🧑 পাত্ৰ — {boy['name']}</h3>
        <table class="profile-table">
            <tr><td>ৰাশি</td><td>♈ {boy['rashi']}</td></tr>
            <tr><td>নক্ষত্ৰ</td><td>⭐ {boy['nakshatra']}</td></tr>
            <tr><td>চৰণ</td><td>🦶 {boy['charan']}ম</td></tr>
            <tr><td>লগ্ন</td><td>🌅 {boy.get('lagna', '—')}</td></tr>
            <tr><td>মঙ্গল</td><td>🔥 {boy['mars_house']}ম ঘৰ</td></tr>
        </table>
    </div>
    <div class="profile-card girl">
        <h3>👩 পাত্ৰী — {girl['name']}</h3>
        <table class="profile-table">
            <tr><td>ৰাশি</td><td>♈ {girl['rashi']}</td></tr>
            <tr><td>নক্ষত্ৰ</td><td>⭐ {girl['nakshatra']}</td></tr>
            <tr><td>চৰণ</td><td>🦶 {girl['charan']}ম</td></tr>
            <tr><td>লগ্ন</td><td>🌅 {girl.get('lagna', '—')}</td></tr>
            <tr><td>মঙ্গল</td><td>🔥 {girl['mars_house']}ম ঘৰ</td></tr>
        </table>
    </div>
</div>

<!-- Ashtakoot Summary -->
<h2 class="section-heading">📊 অষ্টকূট গুণ মিলন — সাৰাংশ</h2>
<table class="koota-table">
    <thead><tr><th>ক্ৰম</th><th>কূটৰ নাম</th><th>প্ৰাপ্ত</th><th>সৰ্বোচ্চ</th><th>স্থিতি</th></tr></thead>
    <tbody>
        {koota_rows}
        <tr class="total-row">
            <td colspan="2">🌟 সৰ্বমুঠ গুণ</td>
            <td style="color:{DEEP_BLUE};">{total}</td>
            <td>{max_score}</td>
            <td style="color:{DEEP_BLUE};">{verdict}</td>
        </tr>
    </tbody>
</table>

<!-- Detailed Koota Analysis -->
<h2 class="section-heading">🔍 অষ্টকূটৰ সবিশেষ বিশ্লেষণ</h2>
{koota_details_html}

<!-- Mangalik Dosha -->
<div class="mangalik-section">
    <h2 class="section-heading" style="color:#E65100;">🔥 মাংগলিক দোষ (কূজ দোষ) বিচাৰ</h2>
    <div class="mangalik-row">
        <div class="mangalik-item">
            <div class="mi-label">🧑 পাত্ৰ ({boy['name']})</div>
            <div class="mi-value {'mi-yes' if mangalik['boy_mangalik'] else 'mi-no'}">{boy_mangalik}</div>
            <div style="font-size:7pt;color:#888;">মঙ্গল {boy['mars_house']}ম ঘৰত</div>
        </div>
        <div class="mangalik-item">
            <div class="mi-label">👩 পাত্ৰী ({girl['name']})</div>
            <div class="mi-value {'mi-yes' if mangalik['girl_mangalik'] else 'mi-no'}">{girl_mangalik}</div>
            <div style="font-size:7pt;color:#888;">মঙ্গল {girl['mars_house']}ম ঘৰত</div>
        </div>
    </div>
    <div class="kd-prediction" style="margin-top:8px;">{mangalik_analysis}</div>
    {remedies_html}
</div>

{warnings_html}

<!-- Conclusion -->
<div class="conclusion">
    <h2 class="section-heading" style="color:{DEEP_BLUE};border:none;">🌟 সৰ্বমুঠ মূল্যাংকন আৰু সিদ্ধান্ত</h2>
    <div class="conclusion-text">
        <p><b>{boy['name']}</b> আৰু <b>{girl['name']}</b>ৰ যোটক মিলনত সৰ্বমুঠ <b>{total} / {max_score}</b> গুণ প্ৰাপ্ত হৈছে।</p>
        <p>{verdict_desc}</p>
    </div>
    <div class="blessing">
        ✨ ঈশ্বৰে আপোনালোকৰ দাম্পত্য জীৱন সুখময়, সমৃদ্ধিশালী আৰু দীৰ্ঘস্থায়ী কৰি তোলক।<br>
        শুভম ভৱতু। 🙏
    </div>
</div>

<div class="footer-note">
    © ২০২৬ ধ্ৰুৱতৰা AI • dhrubataraai.com • সৰ্বস্বত্ব সংৰক্ষিত
</div>

</body>
</html>"""

    return html
