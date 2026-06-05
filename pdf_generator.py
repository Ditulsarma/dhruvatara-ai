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
    
    Uses the full birth date for accurate year calculations.
    Saturn takes approximately 2.5 years per rashi transit.
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

    # Parse full birth date from user_dob (format: YYYY-MM-DD)
    birth_date = None
    if user_dob:
        try:
            birth_date = datetime.strptime(user_dob.strip(), "%Y-%m-%d")
        except (ValueError, IndexError):
            pass

    sat_idx = rasi_names.index(shani_rasi)
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
        </div>
        <div class=\"sare-sati-analysis\">
            <h3 class=\"ss-analysis-heading\">শনিৰ সাৰে সাতিৰ ৭.৫ বছৰীয়া সময়কালৰ বিতং বিশ্লেষণ:</h3>
            <p class=\"ss-analysis-intro\">শনিৰ সাৰে সাতটি মূলতঃ ২.৫ বছৰকৈ তিনিটা ভাগত বিভক্ত কৰা হয়। প্ৰতিটো ভাগৰ প্ৰভাৱ আৰু পৰিস্থিতি বেলেগ বেলেগ হয়।</p>

            <div class=\"ss-phase-card\">
                <div class=\"ss-phase-title\">১. সাৰে সাতিৰ উদয় (১ম চৰণ - প্ৰথম ২.৫ বছৰ)</div>
                <div class=\"ss-phase-body\">
                    <p>এই সময়ছোৱাক সাৰে সাতিৰ <b>\"আৰম্ভণিৰ দুৱাৰদলি\"</b> বুলি ক'ব পাৰি। এই সময়ত শনি গ্ৰহ জন্ম ৰাশিৰ ঠিক আগৰ ঘৰত (দ্বাদশ স্থানত) থাকে।</p>
                    <p class=\"ss-sub-heading\">মুখ্য প্ৰভাৱ (সমস্যাসমূহ):</p>
                    <ul>
                        <li><b>আৰ্থিক চাপ:</b> উপাৰ্জনতকৈ খৰচৰ মাত্ৰা বহুগুণে বৃদ্ধি পায়। আৰ্থিক সংকটৰ সৃষ্টি হ'ব পাৰে।</li>
                        <li><b>কৰ্মক্ষেত্ৰত বাধা:</b> অফিচ বা ব্যৱসায়ত সহকৰ্মীৰ সৈতে মতানৈক্য হ'ব পাৰে। শনিৰ গতি লেহেমীয়া হোৱাৰ বাবে যিকোনো কাম সম্পূৰ্ণ হওঁতে পলম হয়।</li>
                        <li><b>গুপ্ত শত্ৰু:</b> আপোনাক সন্মুখৰ পৰা আক্ৰমণ নকৰিলেও, কিছুমান গুপ্ত শত্ৰুৱে পিছফালৰ পৰা লোকচান কৰাৰ চেষ্টা কৰিব পাৰে।</li>
                    </ul>
                    <p class=\"ss-sub-heading\">ল'বলগীয়া সাৱধানতা:</p>
                    <p>দুৰ্ঘটনাৰ আশংকা থকাৰ বাবে দূৰণিৰ যাত্ৰা পৰাপক্ষত এৰাই চলিব। টকা-পইচাৰ ক্ষেত্ৰত হিচাপী হ'ব আৰু ব্যৱসায়ত ডাঙৰ ৰিস্ক (Risk) একেবাৰেই নল'ব। খৰখেদা নকৰি উচিত সময়লৈকে ধৈৰ্য্য ধৰিলেহে কামত সফলতা মিলিব।</p>
                </div>
            </div>

            <div class=\"ss-phase-card\">
                <div class=\"ss-phase-title\">২. সাৰে সাতিৰ শিখৰ (২য় চৰণ - মাজৰ ২.৫ বছৰ)</div>
                <div class=\"ss-phase-body\">
                    <p>এই সময়ছোৱা সাৰে সাতিৰ <b>\"চৰম বা আটাইতকৈ কঠিন\"</b> পৰ্যায়। এই সময়ত শনি গ্ৰহ আপোনাৰ জন্ম ৰাশিতেই অৱস্থান কৰে।</p>
                    <p class=\"ss-sub-heading\">মুখ্য প্ৰভাৱ (সমস্যাসমূহ):</p>
                    <ul>
                        <li><b>মানসিক আৰু শাৰীৰিক কষ্ট:</b> মনত অকাৰণ ভয়, হতাশা আৰু তীব্ৰ মানসিক অশান্তি থাকে। স্বাস্থ্যৰ অৱনতি ঘটিব পাৰে। সৰু কাম এটাৰ বাবেও কঠোৰ সংগ্ৰাম কৰিবলগীয়া হয়।</li>
                        <li><b>সম্পৰ্কত ফাট:</b> ভাতৃ-ভগ্নী, আত্মীয়-স্বজন আনকি পত্নীৰ সৈতেও বিনা কাৰণত কাজিয়া বা মনোমালিন্য হ'ব পাৰে।</li>
                        <li><b>চৰিত্ৰত দাগ:</b> এই সময়ত শত্ৰুৱে আপোনাৰ বদনাম বা চৰিত্ৰ হনন কৰাৰ পূৰ্ণ চেষ্টা চলায়। লগতে পিতৃ-মাতৃৰ বাবেও সময়টো শুভ নহয়।</li>
                    </ul>
                    <p class=\"ss-sub-heading\">ল'বলগীয়া সাৱধানতা:</p>
                    <p>এই সময়ত মানসিকভাৱে অতিশয় দৃঢ় হোৱাৰ প্ৰয়োজন। কাৰো সৈতে তৰ্কত লিপ্ত নহ'ব আৰু নিজৰ চৰিত্ৰ সৱল কৰি ৰাখিব।</p>
                </div>
            </div>

            <div class=\"ss-phase-card\">
                <div class=\"ss-phase-title\">৩. সাৰে সাতিৰ অস্ত (৩য় চৰণ - শেষৰ ২.৫ বছৰ)</div>
                <div class=\"ss-phase-body\">
                    <p>এইটো সাৰে সাতিৰ <b>\"বিদায় বেলা\"</b>। আগৰ ৫ বছৰৰ ভয়ংকৰ কষ্টৰ পিছত এই সময়ছোৱাত ব্যক্তিয়ে কিছু সকাহ অনুভৱ কৰিবলৈ আৰম্ভ কৰে।</p>
                    <p class=\"ss-sub-heading\">মুখ্য প্ৰভাৱ (সমস্যাসমূহ):</p>
                    <ul>
                        <li><b>আৰ্থিক স্থিতি:</b> সকাহ পালেও টকা-পইচাৰ সম্পৰ্কীয় কিছুমান সমস্যা থাকি যায়। হঠাতে ধনহানি বা চুৰি হোৱাৰ সম্ভাৱনা থাকে।</li>
                        <li><b>মানসিক অৱস্থা:</b> মনলৈ সঘনাই অশুভ বা নেতিবাচক চিন্তা আহিব পাৰে। বিদ্যাৰ্থীসকলে পঢ়া-শুনাত মনোযোগ দিলেও আশানুৰূপ ফলাফল পোৱাত বাধাৰ সৃষ্টি হয়।</li>
                    </ul>
                    <p class=\"ss-sub-heading\">ল'বলগীয়া সাৱধানতা:</p>
                    <p>আটাইতকৈ গুৰুত্বপূৰ্ণ কথাটো হ'ল নিজৰ কথা-বতৰা বা <b>বাণীৰ ওপৰত নিয়ন্ত্ৰণ ৰখা</b>। ভুল কথাৰ বাবে মানুহৰ লগত শত্ৰুতা হ'ব পাৰে। যান-বাহন চলোৱা আৰু সা-সম্পত্তিৰ লেনদেন কৰোঁতে অতিশয় সাৱধান হ'ব। পিতৃ-মাতৃৰ স্বাস্থ্যৰ প্ৰতি চকু ৰাখিব।</p>
                </div>
            </div>

            <div class=\"ss-note-box\">
                <b>বিশেষ দ্ৰষ্টব্য:</b> শনিৰ সাৰে সাতিৰ প্ৰভাৱ মানুহৰ বয়সৰ ওপৰতো নিৰ্ভৰ কৰে। সৰুকালত (শৈশৱত) ইয়াৰ প্ৰভাৱ বৰ বেছি অনুভৱ নহয়, কিন্তু জীৱনৰ মাজভাগত (যৌৱন/কৰ্মজীৱনত) আৰু শেষ ভাগত (বাৰ্ধক্যত) ইয়াৰ প্ৰভাৱ অত্যন্ত গভীৰ আৰু নিৰ্ণায়ক হয়। শনি হৈছে ন্যায়াধীশ, সেয়ে সৎ কৰ্ম আৰু ধৈৰ্য্যৰে এই সময় পাৰ কৰিব পাৰি।
            </div>

            <h3 class=\"ss-analysis-heading\">শনিৰ ধেয়া (ঢৈয়া) সময়ৰ বিশ্লেষণ:</h3>

            <div class=\"ss-phase-card\">
                <div class=\"ss-phase-title\">১. শনিৰ ধেয়া: চতুৰ্থ স্থান (ৰাশিৰ পৰা চতুৰ্থত অৱস্থান)</div>
                <div class=\"ss-phase-body\">
                    <p>এই সময়ছোৱাত শনি গ্ৰহ জন্ম ৰাশিৰ পৰা চতুৰ্থ ঘৰত থাকে। ই ঘাইকৈ পাৰিবাৰিক সুখ, সম্পত্তি আৰু কৰ্মজীৱনত প্ৰভাৱ পেলায়।</p>
                    <ul>
                        <li><b>সম্পৰ্ক আৰু পৰিয়াল:</b> বন্ধু-বান্ধৱ বা আপোন মানুহৰ লগত মনোমালিন্য হোৱাৰ সম্ভাৱনা থাকে। পিতৃ-মাতৃৰ সৈতে সম্পৰ্কৰ অৱনতি ঘটিব পাৰে নাইবা তেওঁলোকৰ স্বাস্থ্যজনিত সমস্যাই দেখা দিব পাৰে। ভাতৃ-ভগ্নীৰ লগত যিকোনো ধৰণৰ লেনদেন কৰোঁতে সাৱধান হোৱা উচিত।</li>
                        <li><b>সম্পত্তি আৰু বাহন:</b> মাটি-বাৰী, সম্পত্তি বা বন্ধুৰ লগত জড়িত কামবোৰত সতৰ্ক হোৱা প্ৰয়োজন। যদি নতুনকৈ ঘৰ নিৰ্মাণ কৰি আছে, তেন্তে বিভিন্ন দিশৰ পৰা বাধা বা সমস্যা আহিব পাৰে। যান-বাহন চলোৱাৰ ক্ষেত্ৰতো বিশেষ সাৱধানতা অৱলম্বন কৰিব লাগে।</li>
                        <li><b>কৰ্মক্ষেত্ৰ:</b> অফিচ বা ব্যৱসায়ত পৰিস্থিতি কঠিন হ'ব পাৰে। কামৰ বাবে অত্যাধিক পৰিশ্ৰম কৰিবলগীয়া হয় আৰু আনৰ সৈতে প্ৰত্যক্ষ বা পৰোক্ষভাৱে বিবাদ বা মতানৈক্য হোৱাৰ শংকা থাকে।</li>
                        <li><b>বয়সৰ প্ৰভাৱ:</b> সাৰে সাতিৰ দৰেই চতুৰ্থ স্থানৰ ধেয়াৰ প্ৰভাৱো সৰুকালত বিশেষভাৱে অনুভূত নহয় যদিও জীৱনৰ মাজভাগত আৰু শেষৰ ফালে ইয়াৰ প্ৰভাৱ যথেষ্ট বেছি হয়।</li>
                    </ul>
                </div>
            </div>

            <div class=\"ss-phase-card\">
                <div class=\"ss-phase-title\">২. শনিৰ ধেয়া: অষ্টম স্থান (ৰাশিৰ পৰা অষ্টমত অৱস্থান)</div>
                <div class=\"ss-phase-body\">
                    <p>এই সময়ছোৱাত শনি জন্ম ৰাশিৰ পৰা অষ্টম ঘৰত থাকে। ইয়াক 'অষ্টম শনি' বুলিও কোৱা হয় আৰু ই সাধাৰণতে অধিক কষ্টদায়ক হ'ব পাৰে।</p>
                    <ul>
                        <li><b>কৰ্ম আৰু পাৰিবাৰিক জীৱন:</b> কৰ্মক্ষেত্ৰত কঠিন সংগ্ৰাম আৰু বিবাদৰ সৃষ্টি হ'ব পাৰে। ঠিক একেদৰে, পাৰিবাৰিক দিশতো সময়টো বৰ শুভ নহয়, অশান্তি আহিব পাৰে।</li>
                        <li><b>বাণী বা কথা-বতৰা:</b> নিজৰ কথা-বতৰাৰ ওপৰত কঠোৰ নিয়ন্ত্ৰণ ৰখাটো অত্যন্ত গুৰুত্বপূৰ্ণ। আপুনি হয়তো কাৰোবাৰ ভালৰ বাবে কথা এটা ক'ব, কিন্তু সেয়া ভুল অৰ্থত লোৱা হ'ব পাৰে আৰু সম্পৰ্ক বেয়া হ'ব পাৰে।</li>
                        <li><b>আৰ্থিক সংকট:</b> টকা-পইচাৰ তীব্ৰ অভাৱ বা আৰ্থিক সমস্যাই দেখা দিব পাৰে। ধাৰলৈ দিয়া ধন ঘূৰাই নোপোৱা, ঋণৰ সূত বা মূল ধন পৰিশোধ কৰিব নোৱাৰা, অথবা নতুন আঁচনিৰ বাবে প্ৰয়োজনীয় ধন গোটাব নোৱাৰা আদি সমস্যা হ'ব পাৰে। আত্মীয়ৰ লগত ধনৰ লেনদেন কৰোঁতে অতিশয় সাৱধান হ'ব।</li>
                        <li><b>শাৰীৰিক আৰু আইনী বিপদ:</b> অষ্টম স্থানত শনি থকাৰ বাবে দুৰ্ঘটনা হোৱা বা আঘাত পোৱাৰ সম্ভাৱনা প্ৰবল থাকে। যাৰ জন্মকুণ্ডলীত অষ্টম স্থানত অশুভ গ্ৰহ থাকে বা অষ্টম পতি অশুভ হৈ থাকে, তেওঁলোকৰ এই সময়ত ডাঙৰ বিবাদ, আনকি ক'ৰ্ট-কাছাৰীৰ (Court Case) গোচৰ পৰ্যন্ত হ'ব পাৰে। কিছুমানে চৰকাৰীভাৱে নিষিদ্ধ বা বেআইনী কামতো হাত দিয়াৰ আশংকা থাকে।</li>
                        <li><b>শিক্ষা:</b> বিদ্যাৰ্থীসকলৰ বাবে এই সময়ছোৱা প্ৰত্যাহ্বানজনক। পঢ়া-শুনাত বাধা আহিব পাৰে আৰু আশানুৰূপ ফলাফল লাভ কৰাত অসুবিধা হ'ব পাৰে।</li>
                    </ul>
                </div>
            </div>
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
    antardasha_phala_html: str = "",
    dwadash_html: str = "",
    vimsottari_summary: str = "",
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
        ('বাৰবেলা', panchanga.get('bara_bela', '—'), ''),
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
            return f'<img src="data:image/png;base64,{b64}" alt="kundli" style="width:100%;height:auto;border-radius:8px;"/>'
        # embed D1 using the PIL renderer if available
        if all_vargas and "D1" in all_vargas:
            d1_svg = _embed_chart_png(all_vargas["D1"], w=420, h=420, style='bengali')
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
        # Parse AI text into sections based on numbered points or double newlines
        ai_paragraphs = [line.strip() for line in ai_interpretation.strip().split('\n') if line.strip()]
        ai_cards = ""
        for para in ai_paragraphs:
            # Detect if it's a heading-like line (starts with number, emoji, or contains colon)
            is_heading = False
            heading_text = ""
            body_text = para
            
            # Check for patterns like "1.", "1)", "【", "★", or lines ending with ":" or "ঃ"
            if para and (para[0].isdigit() and ('.' in para[:4] or ')' in para[:4])):
                # Numbered point: "1. Something" or "1) Something"
                parts = para.split('.', 1) if '.' in para[:4] else para.split(')', 1)
                if len(parts) > 1:
                    heading_text = parts[0].strip() + '.'
                    body_text = parts[1].strip()
                    is_heading = True
            elif para.startswith('【') and '】' in para:
                heading_text = para
                body_text = ""
                is_heading = True
            elif 'ঃ' in para[:60] or ':' in para[:60]:
                parts = para.split('ঃ', 1) if 'ঃ' in para[:60] else para.split(':', 1)
                if len(parts) > 1 and len(parts[0]) < 50:
                    heading_text = parts[0].strip() + 'ঃ'
                    body_text = parts[1].strip()
                    is_heading = True
            
            if is_heading and heading_text:
                ai_cards += f'<div class="ai-card"><div class="ai-card-head">{heading_text}</div>'
                if body_text:
                    ai_cards += f'<div class="ai-card-body">{body_text}</div>'
                ai_cards += '</div>'
            else:
                ai_cards += f'<div class="ai-card"><div class="ai-card-body">{para}</div></div>'
        
        ai_html = f"""
        <div class="ai-section-wrapper">
            <div class="ai-section-header">
                <div class="ai-header-icon">🤖</div>
                <div class="ai-header-text">
                    <div class="ai-header-title">AI বিশ্লেষণ আৰু পৰামৰ্শ</div>
                    <div class="ai-header-subtitle">কৃত্ৰিম বুদ্ধিমত্তাৰ দ্বাৰা বিশ্লেষিত জন্মকুণ্ডলীৰ সম্পূৰ্ণ ফলাফল</div>
                </div>
            </div>
            <div class="ai-divider"></div>
            <div class="ai-cards-container">{ai_cards}</div>
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
        padding: 8px 14px; font-weight: 700; font-size: 9.5pt;
        color: {DEEP_BLUE}; border-bottom: 1px solid #f0e0c8;
    }}
    .ai-card-body {{
        padding: 10px 14px; font-size: 9pt; line-height: 1.9;
        color: #333; background: #fefefe;
    }}
    .ai-footer-note {{
        margin-top: 10px; padding: 8px 14px;
        background: #FFF3E0; border-left: 3px solid {ORANGE};
        border-radius: 0 6px 6px 0; font-size: 7.5pt;
        color: #E65100; display: flex; align-items: center; gap: 6px;
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
    <h1>🌟 জন্মকুণ্ডলী</h1>
    <div class="sub">বৈদিক জ্যোতিষ সম্পূৰ্ণ ৰিপৰ্ট</div>
</div>
<hr class="divider">

<!-- ═══════════════ INVOCATORY SHLOKAS ═══════════════ -->
<div class="shloka-section">
    <div class="shloka-outer-box">
        <div class="ganesh-image-container">
            {ganesh_image_html}
        </div>
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

<!-- ═══════════════ জন্মপত্ৰিকা TITLE ═══════════════ -->
<div class="patrika-title-section">
    <div class="patrika-ornament">❖  ॐ  ❖</div>
    <div class="patrika-main-title">জন্মপত্ৰিকা</div>
</div>

<!-- ═══════════ প্ৰকাশিত নাম ও তথ্য ═══════════ -->
<div style="text-align:center;">
    <div class="patrika-info-card">
        <div class="patrika-published-label">প্ৰকাশিত নাম</div>
        <div class="patrika-name">{user_name}</div>
        <div class="patrika-details">
            <b>জন্ম তাৰিখঃ</b> <span>{user_dob_formatted}</span> &nbsp;&nbsp;|&nbsp;&nbsp; <b>জন্মৰ সময়ঃ</b> <span>{user_tob}</span><br>
            <b>জন্ম স্থানঃ</b> <span>{user_place}</span>
        </div>
    </div>
</div>
<!-- ═══════════════════════════════════════════════════ -->

<!-- ═══════════════ PAGE BREAK → ২য় পৃষ্ঠা ═══════════════ -->
<div style="page-break-before: always;"></div>

<h2 class="section-heading">📋 ব্যক্তিগত তথ্য</h2>
<div class="info-grid">
    <div class="info-item"><b>নাম:</b> {user_name}</div>
    <div class="info-item"><b>লিংগ:</b> {"মহিলা (জাতিকা)" if gender == "female" else "পুৰুষ (জাতক)"}</div>
    <div class="info-item"><b>জন্মৰ স্থান:</b> {user_place}</div>
    <div class="info-item"><b>জন্মৰ তাৰিখ:</b> {user_dob_formatted}</div>
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

    # ═══════════════ PAGE BREAK → ৩য় পৃষ্ঠা (জন্ম কুণ্ডলী) ═══════════════
    if _include('kundli_chart'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">📊 জন্ম কুণ্ডলী (D1 - ৰাশি চক্ৰ)</h2>'
        html += '<div class="chart-large-page3">' + d1_svg + '</div>'
        # Patrika text below D1 chart
        if patrika_text:
            patrika_html = patrika_text.replace('\n', '<br>')
            html += '<div style="margin:12px 0;padding:14px 18px;background:linear-gradient(135deg,#FFF8E1,#FFF3E0);border:2px solid #FFCC80;border-radius:8px;font-size:9pt;line-height:2.2;text-align:justify;font-family:\'Noto Sans Bengali\',\'Nirmala UI\',sans-serif;">' + patrika_html + '</div>'

    # ═══════════════ PAGE BREAK → ৪ৰ্থ পৃষ্ঠা (বিভাগীয় কুণ্ডলী) ═══════════════
    if _include('varga_charts'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">📊 ষোড়শবৰ্গ বিভাগীয় কুণ্ডলী (D2 - D60)</h2><div class="charts-grid">' + small_charts_html + '</div>'

    shani_sare_sati_html = _render_shani_sare_sati_html(moon_rasi, planets_data, user_dob)
    if _include('shani_sare_sati'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">🌑 শনি সাৰেসাতী আৰু ঢৈয়া (০-১০০ বছৰ)</h2>' + shani_sare_sati_html

    if _include('dosha'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">⚠️ দোষ বিশ্লেষণ</h2>' + dosha_html

    if _include('yoga'):
        html += '<h2 class="section-heading">✨ যোগ বিশ্লেষণ</h2>' + yoga_html

    if _include('sannari'):
        html += '<h2 class="section-heading">🌀 সন্নাড়ী চক্ৰ</h2>' + sannari_html

    if _include('navatara'):
        html += '<h2 class="section-heading">🌀 নৱতাৰা চক্ৰ</h2>' + navatara_html

    if _include('tripap'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">☠️ ত্ৰিপাপ ৰিষ্ট বিশ্লেষণ</h2>' + tripap_html

    if _include('nakshatra_phala'):
        html += '<h2 class="section-heading">🌟 নক্ষত্ৰ ফলাফল</h2>' + nakshatra_phala_html

    if _include('lagna_phala'):
        html += '<h2 class="section-heading">🌅 লগ্ন ফলাফল</h2>' + lagna_phala_html

    if _include('rashi_phala'):
        html += '<h2 class="section-heading">🌙 ৰাশিফল (চন্দ্ৰ ৰাশি)</h2>' + rashi_phala_html

    if _include('graha_bichar'):
        html += '<h2 class="section-heading">🪐 গ্ৰহ বিচাৰ (ভাব অনুসৰি)</h2>' + graha_bichar_html

    if _include('dwadash_bhab_phala'):
        html += '<div style="page-break-before: always;"></div>'
        html += '<h2 class="section-heading">🏠 দ্বাদশ ভাব ফল (12 House Results)</h2>' + dwadash_html

    if vimsottari_summary and _include('dasha_summary'):
        html += '<h2 class="section-heading">📊 বিংশোত্তৰী দশা সাৰাংশ</h2><div style="background:#FFF8F0;border-left:4px solid #FF6600;padding:12px 16px;font-size:9pt;line-height:1.8;border-radius:6px;margin-bottom:10px;text-align:justify;font-family:\'Noto Sans Bengali\',\'Nirmala UI\',sans-serif;">' + vimsottari_summary.replace('\n', '<br>') + '</div>'
        html += '<table class="dasha-table"><thead><tr><th>মহাদশা</th><th>আৰম্ভ</th><th>সমাপ্তি</th><th>অন্তৰ্দশা (প্ৰথম ৩)</th></tr></thead><tbody>' + dasha_rows + '</tbody></table>'
    elif _include('dasha_summary'):
        html += '<h2 class="section-heading">⏳ বিংশোত্তৰী দশা সাৰাংশ</h2><table class="dasha-table"><thead><tr><th>মহাদশা</th><th>আৰম্ভ</th><th>সমাপ্তি</th><th>অন্তৰ্দশা (প্ৰথম ৩)</th></tr></thead><tbody>' + dasha_rows + '</tbody></table>'

    if _include('dasha_full'):
        html += '<h2 class="section-heading">⏳ সম্পূৰ্ণ মহাদশা আৰু অন্তৰ্দশা</h2>' + full_dasha_html

    if _include('dasha_predictions'):
        html += '<h2 class="section-heading">📝 মহাদশা-অন্তৰ্দশাৰ সম্পূৰ্ণ ফলাফল</h2>' + dasha_predictions_html

    if _include('antardasha_phala'):
        html += '<h2 class="section-heading">📖 অন্তৰদশা ফলাফল (বিস্তৃত)</h2>' + antardasha_phala_html

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
        antardasha_phala_html=antardasha_phala_html,
        dwadash_html=dwadash_html,
        vimsottari_summary=vimsottari_summary,
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
