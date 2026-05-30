"""
ধ্ৰুৱতৰা AI - মূল এপ্লিকেচন
Dhruvatara AI: Professional Assamese Vedic Astrology Platform
Powered by DhrubataraAi for high-precision calculations.
With Subscription-based User & Admin Panel.
"""

from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, session, flash
import sqlite3
import swisseph as swe
from datetime import datetime, timedelta
import io
import os
import base64
from functools import wraps
from werkzeug.utils import secure_filename
from config import DB_PATH

from panchanga import get_full_panchanga, get_rashi_lord
from dosha_engine import get_complete_dosha_analysis
from yoga_engine import get_complete_yoga_analysis
from ai_engine import generate_ai_interpretation
from pdf_generator import generate_pdf_report, get_shani_sare_sati_data
from chat_engine import chat_with_ai, PREDEFINED_QUESTIONS
from tripap_rista import get_tripap_rista, analyze_tripap_rista, TRIPAP_AGES
from dasha_engine import (
    get_full_dasha_prediction, get_all_maha_antar_predictions,
    get_eng_planet, get_asm_planet, get_planet_details, convert_planet_degrees_to_en
)
from sannari_chakra import get_sannari_data, generate_sannari_svg, generate_sannari_html_table
from navatara_chakra import get_navatara_data, generate_navatara_html, generate_navatara_svg
from nakshatra_phala import get_nakshatra_phala, get_nakshatra_phala_html
from lagna_phala import get_lagna_phala, get_lagna_phala_html
from rashi_phala import get_rashi_phala, get_rashi_phala_html
from graha_bichar import get_all_graha_bichar, get_graha_bichar_html
from kundli_chart import draw_kundli_chart, draw_all_styles
from patrika import generate_patrika_text
from small_antardasaphal import get_antardasha_phala, get_all_antardasha_phala_for_pdf
from auth_module import (
    register_user, login_user, login_admin, verify_email, verify_mobile,
    resend_otp, get_user_features, check_feature_access,
    get_all_feature_definitions, get_all_subscriptions, get_subscription_features,
    get_all_users, get_user_by_id, admin_toggle_user_active,
    admin_set_user_subscription, admin_toggle_user_feature,
    admin_remove_user_feature_override, get_user_feature_overrides,
    login_required, admin_required,
    admin_update_subscription, admin_toggle_subscription_feature,
    get_subscription_by_id
)

app = Flask(__name__)
app.secret_key = 'DhruvataraAI_2026_Secure_Secret_Key_8x7k9m2p'

# ─── Show actual errors in browser (for debugging) ───
app.config['PROPAGATE_EXCEPTIONS'] = True

# ─── Logging for Railway debugging ───
import logging
import traceback
import sys
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

# ─── Auto-initialize database on startup ───
try:
    from setup_db import setup_database
    setup_database()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database init failed: {e}")
    logger.error(traceback.format_exc())

# ─── Health check endpoint (no DB needed) ───
@app.route("/health")
def health():
    return "OK", 200

# ─── Traceback debug endpoint ───
@app.route("/traceback")
def show_traceback():
    try:
        places = get_locations()
        return render_template("index.html",
            places=places, timezones=get_all_timezones(),
            user_features=None, feature_defs=[])
    except Exception as e:
        return f"<pre>ERROR: {e}\n\n{traceback.format_exc()}</pre>", 500

# ─── Favicon handler (prevents 404 for Logo.png) ───
@app.route("/favicon.ico")
@app.route("/Logo.png")
def favicon():
    return "", 204

# ─── Image Upload Configuration ───
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_astrologer_footer_html(user_id=None):
    """Generate HTML for astrologer details footer. Falls back to admin profile if user has none."""
    if user_id is None:
        user_id = session.get('user_id', 0)
    profile = get_astrologer_profile(user_id)
    if not profile:
        return ""

    lines = []
    inst = profile.get('institution_name', '').strip()
    name = profile.get('astrologer_name', '').strip()
    bio = profile.get('astrologer_bio', '').strip()
    addr = profile.get('address', '').strip()
    mob = profile.get('mobile', '').strip()

    if inst:
        lines.append(f'<div class="astro-footer-line astro-inst">{inst}</div>')
    if name:
        lines.append(f'<div class="astro-footer-line astro-name">{name}</div>')
    if bio:
        lines.append(f'<div class="astro-footer-line astro-bio">{bio}</div>')
    if addr:
        lines.append(f'<div class="astro-footer-line astro-addr">{addr}</div>')
    if mob:
        lines.append(f'<div class="astro-footer-line astro-mob">📞 {mob}</div>')

    if not lines:
        return ""

    return f"""
<div class="astrologer-page-footer">
    {''.join(lines)}
</div>"""

def get_all_images():
    """Get all admin images from DB."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT id, image_key, placement, page_target, filename, mime_type, width, height, alt_text, created_at, updated_at FROM admin_images ORDER BY placement, id"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_images_by_placement(placement, page_name=None):
    """Get images for a specific placement, optionally filtered by page."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        if page_name:
            rows = conn.execute(
                "SELECT id, image_key, placement, page_target, filename, mime_type, width, height, alt_text FROM admin_images WHERE placement = ? AND (page_target = 'all' OR page_target LIKE ?) ORDER BY id",
                (placement, f"%{page_name}%")
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, image_key, placement, page_target, filename, mime_type, width, height, alt_text FROM admin_images WHERE placement = ? ORDER BY id",
                (placement,)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_image_data(image_id):
    """Get image binary data by ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT * FROM admin_images WHERE id = ?", (image_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def save_image_to_db(image_key, placement, page_target, filename, mime_type, width, height, alt_text, image_data):
    """Save or update an image in DB."""
    conn = sqlite3.connect(DB_PATH)
    try:
        existing = conn.execute(
            "SELECT id FROM admin_images WHERE image_key = ?", (image_key,)
        ).fetchone()
        if existing:
            conn.execute('''
                UPDATE admin_images SET placement=?, page_target=?, filename=?, mime_type=?, width=?, height=?, alt_text=?, image_data=?, updated_at=CURRENT_TIMESTAMP
                WHERE image_key=?
            ''', (placement, page_target, filename, mime_type, width, height, alt_text, image_data, image_key))
        else:
            conn.execute('''
                INSERT INTO admin_images (image_key, placement, page_target, filename, mime_type, width, height, alt_text, image_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (image_key, placement, page_target, filename, mime_type, width, height, alt_text, image_data))
        conn.commit()
        return True
    except Exception as e:
        print(f"Image save error: {e}")
        return False
    finally:
        conn.close()

def delete_image_from_db(image_id):
    """Delete an image from DB."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("DELETE FROM admin_images WHERE id = ?", (image_id,))
        conn.commit()
        return True
    finally:
        conn.close()

def update_image_dimensions(image_id, width, height):
    """Update image dimensions."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("UPDATE admin_images SET width=?, height=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (width, height, image_id))
        conn.commit()
        return True
    finally:
        conn.close()

rasis = ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"]

# Planet short codes for kundli chart display (single Assamese letters)
PLANET_SHORT = {
    "ৰবি": "ৰ", "চন্দ্ৰ": "চ", "মংগল": "ম", "বুধ": "বু",
    "বৃহস্পতি": "বৃ", "শুক্ৰ": "শু", "শনি": "শ",
    "ৰাহু": "ৰা", "কেতু": "কে", "লগ্ন": "লং"
}

nakshatras = [
    "অশ্বিনী", "ভৰণী", "কৃত্তিকা", "ৰোহিণী", "মৃগশিৰা", "আৰ্দ্ৰা", "পুনৰ্বсу", "পুষ্যা", "অশ্লেষা",
    "মঘা", "পূৰ্বফাল্গুনী", "উত্তৰফাল্গুনী", "হস্তা", "চিত্ৰা", "স্বাতী", "বিশাখা", "অনুৰাধা", "জ্যেষ্ঠা",
    "মূল", "পূৰ্বাষাঢ়া", "উত্তৰাষাঢ়া", "শ্ৰৱণা", "ধনিষ্ঠা", "শতভিষা", "পূৰ্বভাদ্ৰপদ", "উত্তৰভাদ্ৰপদ", "ৰেৱতী"
]
dasa_lords = ["কেতু", "শুক্ৰ", "ৰবি", "চন্দ্ৰ", "মংগল", "ৰাহু", "বৃহস্পতি", "শনি", "বুধ"]
dasa_years = [7, 20, 6, 10, 7, 18, 16, 19, 17]

def fmt_date(ymd_str):
    """Convert YYYY-MM-DD to DD/MM/YYYY for display"""
    if not ymd_str or '-' not in str(ymd_str):
        return str(ymd_str)
    y, m, d = str(ymd_str).split('-')
    return f"{d}/{m}/{y}"

def parse_dasha_date(date_str):
    """Parse DD/MM/YYYY dasha date string to datetime object."""
    try:
        d, m, y = date_str.split('/')
        return datetime(int(y), int(m), int(d))
    except (ValueError, AttributeError):
        return datetime(1900, 1, 1)

def filter_future_dasha_predictions(all_predictions):
    """Filter dasha predictions to only include those ending today or later."""
    today = datetime.now()
    future = []
    for dp in all_predictions:
        end_date = parse_dasha_date(dp.get('end', ''))
        if end_date >= today:
            future.append(dp)
    return future

def get_current_antardasha_info(dasa_data):
    """Find the currently running mahadasha and antardasha."""
    today = datetime.now()
    for md in dasa_data:
        md_end = parse_dasha_date(md.get('end', ''))
        md_start = parse_dasha_date(md.get('start', ''))
        if md_start <= today <= md_end:
            for ad in md.get('sub_dasas', []):
                ad_end = parse_dasha_date(ad.get('end', ''))
                ad_start = parse_dasha_date(ad.get('start', ''))
                if ad_start <= today <= ad_end:
                    return {
                        'maha_lord': md['md_lord'],
                        'antar_lord': ad['ad_lord'],
                        'start': ad['start'],
                        'end': ad['end']
                    }
            # If no antardasha matches, return first antardasha of current mahadasha
            if md.get('sub_dasas'):
                ad = md['sub_dasas'][0]
                return {
                    'maha_lord': md['md_lord'],
                    'antar_lord': ad['ad_lord'],
                    'start': ad['start'],
                    'end': ad['end']
                }
    # Fallback: first mahadasha, first antardasha
    if dasa_data and dasa_data[0].get('sub_dasas'):
        return {
            'maha_lord': dasa_data[0]['md_lord'],
            'antar_lord': dasa_data[0]['sub_dasas'][0]['ad_lord'],
            'start': dasa_data[0]['sub_dasas'][0]['start'],
            'end': dasa_data[0]['sub_dasas'][0]['end']
        }
    return None


def build_antardasha_html(dasa_hierarchy, planet_degrees, lagna_sign_index,
                          selected_maha=None, include_current_and_future_only=True, gender='male'):
    """
    Build HTML for antardasha phala filtered by mahadasha selection or current+future antardashas.
    - dasa_hierarchy: list of mahadasha dicts (with 'sub_dasas')
    - planet_degrees: mapping of planet Assamese names to sidereal degrees
    - lagna_sign_index: integer lagna index (0-11)
    - selected_maha: mahadasha lord name (Assamese) to restrict to, or None for all
    - include_current_and_future_only: if True, include only antardashas whose end >= today
    Returns HTML string.
    """
    today = datetime.now()
    html = '<div style="font-size:0.85rem;line-height:1.8;">'

    # Convert planet_degrees keys from Assamese to English for get_planet_details
    planet_degrees_en = convert_planet_degrees_to_en(planet_degrees)

    for md in dasa_hierarchy:
        if selected_maha and md.get('md_lord') != selected_maha:
            continue

        maha_name = md.get('md_lord', '')
        for ad in md.get('sub_dasas', []):
            # parse dates
            try:
                ad_end = parse_dasha_date(ad.get('end', ''))
                ad_start = parse_dasha_date(ad.get('start', ''))
            except Exception:
                ad_end = datetime(1900, 1, 1)
                ad_start = datetime(1900, 1, 1)

            if include_current_and_future_only and ad_end < today:
                continue

            antar_lord = ad.get('ad_lord', '')

            # Resolve planet details to get rasi and house (use English name for lookup)
            antar_eng = get_eng_planet(antar_lord)
            pd = get_planet_details(antar_eng, planet_degrees_en, lagna_sign_index)
            phala_text = ''
            if pd:
                graha_asm = pd.get('name_asm', antar_lord)
                rasi = pd.get('rasi', '')
                house = pd.get('house', '')
                try:
                    phala_text = get_antardasha_phala(graha_asm, rasi, house)
                except Exception:
                    phala_text = ''

            # Format HTML block
            html += f'<div style="margin-bottom:12px;padding:8px 12px;background:#fff8f0;border-left:3px solid #FF6600;border-radius:4px;">'
            html += f'<strong style="color:#1a237e;">{maha_name} → {antar_lord}</strong> '
            html += f' | {ad.get("start", "") } — {ad.get("end", "") }'
            if phala_text:
                html += f'<div style="margin-top:6px;color:#333;">{apply_gender(phala_text, gender)}</div>'
            html += '</div>'

    html += '</div>'
    return html

def apply_gender(text: str, gender: str) -> str:
    """Replace জাতক/জাতিকা based on gender. Male->জাতক, Female->জাতিকা"""
    if not text:
        return text
    if gender == "female":
        text = text.replace("জাতক", "জাতিকা")
        text = text.replace("তেওঁৰ", "তাইৰ")
        text = text.replace("তেওঁক", "তাইক")
        text = text.replace("তেওঁলোক", "তাইহঁত")
    return text

def get_rasi_and_degree(longitude):
    rasi_index = int(longitude / 30) % 12
    degree = longitude % 30
    return rasi_index, rasis[rasi_index], round(degree, 2)

def get_nakshatra_details(longitude):
    nak_index = int(longitude / 13.333333) % 27
    return nak_index, nakshatras[nak_index], dasa_lords[nak_index % 9]

# --- ১/ সম্পূৰ্ণ ষোড়শবৰ্গ কুণ্ডলী গণনা ইঞ্জিন (Shodashvarga - All 16 Varga Charts) ---
def calculate_varga(p_sidereal_lon, varga_number):
    """
    Proper Vedic Shodashvarga calculations per Parasara.
    Returns 0-indexed rasi (0=Mesha...11=Meena)
    """
    total_deg = p_sidereal_lon % 360
    rasi_orig = int(total_deg / 30) % 12
    deg_in_rasi = total_deg % 30
    is_odd_sign = (rasi_orig % 2 == 0)

    if varga_number == 1:  # D1 Rashi
        return rasi_orig

    elif varga_number == 2:  # D2 Hora
        if is_odd_sign:
            return 4 if deg_in_rasi < 15 else 3
        else:
            return 3 if deg_in_rasi < 15 else 4

    elif varga_number == 3:  # D3 Drekkana
        part = int(deg_in_rasi / 10)
        if rasi_orig in [0, 3, 6, 9]:
            offsets = [0, 4, 8]
        elif rasi_orig in [1, 4, 7, 10]:
            offsets = [4, 8, 0]
        else:
            offsets = [8, 0, 4]
        return (rasi_orig + offsets[part]) % 12

    elif varga_number == 4:  # D4 Chaturthamsha
        part = int(deg_in_rasi / 7.5)
        if rasi_orig in [0, 3, 6, 9]:
            start = rasi_orig
        elif rasi_orig in [1, 4, 7, 10]:
            start = (rasi_orig + 3) % 12
        else:
            start = (rasi_orig + 6) % 12
        return (start + part) % 12

    elif varga_number == 7:  # D7 Saptamsha
        part = int(deg_in_rasi / (30.0/7))
        start = rasi_orig if is_odd_sign else (rasi_orig + 6) % 12
        return (start + part) % 12

    elif varga_number == 9:  # D9 Navamsha
        part = int(deg_in_rasi / (30.0/9))
        element_start = [0, 9, 6, 3, 0, 9, 6, 3, 0, 9, 6, 3]
        return (element_start[rasi_orig] + part) % 12

    elif varga_number == 10:  # D10 Dashamsha
        part = int(deg_in_rasi / 3.0)
        start = rasi_orig if is_odd_sign else (rasi_orig + 8) % 12
        return (start + part) % 12

    elif varga_number == 12:  # D12 Dwadasamsha
        part = int(deg_in_rasi / 2.5)
        return (rasi_orig + part) % 12

    elif varga_number == 16:  # D16 Shodashamsha
        part = int(deg_in_rasi / (30.0/16))
        if rasi_orig in [0, 3, 6, 9]:
            start = 0
        elif rasi_orig in [1, 4, 7, 10]:
            start = 4
        else:
            start = 8
        return (start + part) % 12

    elif varga_number == 20:  # D20 Vimshamsha
        part = int(deg_in_rasi / 1.5)
        if rasi_orig in [0, 3, 6, 9]:
            start = 0
        elif rasi_orig in [1, 4, 7, 10]:
            start = 8
        else:
            start = 4
        return (start + part) % 12

    elif varga_number == 24:  # D24 Chaturvimshamsha
        part = int(deg_in_rasi / (30.0/24))
        start = 4 if is_odd_sign else 3
        return (start + part) % 12

    elif varga_number == 27:  # D27 Saptavimshamsha (Bhamsha)
        part = int(deg_in_rasi / (30.0/27))
        element_start = [0, 9, 6, 3, 0, 9, 6, 3, 0, 9, 6, 3]
        return (element_start[rasi_orig] + part) % 12

    elif varga_number == 30:  # D30 Trimshamsha
        if is_odd_sign:
            if deg_in_rasi < 5: return 0
            elif deg_in_rasi < 10: return 10
            elif deg_in_rasi < 18: return 8
            elif deg_in_rasi < 25: return 2
            else: return 6
        else:
            if deg_in_rasi < 5: return 1
            elif deg_in_rasi < 12: return 5
            elif deg_in_rasi < 20: return 11
            elif deg_in_rasi < 25: return 7
            else: return 9

    elif varga_number == 40:  # D40 Khavedamsha
        part = int(deg_in_rasi / (30.0/40))
        start = 0 if is_odd_sign else 6
        return (start + part) % 12

    elif varga_number == 45:  # D45 Akshavedamsha
        part = int(deg_in_rasi / (30.0/45))
        if rasi_orig in [0, 3, 6, 9]:
            start = 0
        elif rasi_orig in [1, 4, 7, 10]:
            start = 4
        else:
            start = 8
        return (start + part) % 12

    elif varga_number == 60:  # D60 Shashtiamsha
        part = int(deg_in_rasi / 0.5)
        return part % 12

    return rasi_orig

# --- ২/ বিংশোত্তৰী ৩-তৰপীয়া দশা ইঞ্জিন (Mahadasa, Antardasa & Pratyantardasa) ---
def get_full_dasa_hierarchy(moon_sidereal_lon, birth_date):
    nak_idx, _, _ = get_nakshatra_details(moon_sidereal_lon)
    elapsed_in_nak = moon_sidereal_lon - (nak_idx * 13.333333)
    remaining_ratio = (13.333333 - elapsed_in_nak) / 13.333333
    
    current_md_idx = nak_idx % 9
    md_remaining_days = int(dasa_years[current_md_idx] * remaining_ratio * 365.25)
    
    timeline = []
    current_date = birth_date
    
    for i in range(9):
        idx = (current_md_idx + i) % 9
        md_lord = dasa_lords[idx]
        md_years = dasa_years[idx]
        
        md_end_date = current_date + timedelta(days=md_remaining_days if i == 0 else int(md_years * 365.25))
        md_entry = {"md_lord": md_lord, "start": fmt_date(current_date.strftime('%Y-%m-%d')), "end": fmt_date(md_end_date.strftime('%Y-%m-%d')), "years": md_years, "sub_dasas": []}
        
        ad_current_date = current_date
        for j in range(9):
            ad_idx = (idx + j) % 9
            ad_lord = dasa_lords[ad_idx]
            ad_days = int((md_years * dasa_years[ad_idx] / 120.0) * 365.25)
            if i == 0: ad_days = int(ad_days * remaining_ratio)
            
            ad_end_date = ad_current_date + timedelta(days=ad_days)
            if ad_end_date > md_end_date or j == 8: ad_end_date = md_end_date
            
            # প্ৰত্যন্তৰ দশা (Pratyantar) - structured list
            pd_current_date = ad_current_date
            pd_list = []
            for k in range(9):
                pd_idx = (ad_idx + k) % 9
                pd_days = int((md_years * dasa_years[ad_idx] * dasa_years[pd_idx] / 14400.0) * 365.25)
                if i == 0: pd_days = int(pd_days * remaining_ratio)
                pd_end_date = pd_current_date + timedelta(days=pd_days)
                if pd_end_date > ad_end_date or k == 8: pd_end_date = ad_end_date
                
                pd_list.append({
                    "lord": dasa_lords[pd_idx],
                    "start": fmt_date(pd_current_date.strftime('%Y-%m-%d')),
                    "end": fmt_date(pd_end_date.strftime('%Y-%m-%d'))
                })
                pd_current_date = pd_end_date
                
            md_entry["sub_dasas"].append({
                "ad_lord": ad_lord,
                "start": fmt_date(ad_current_date.strftime('%Y-%m-%d')),
                "end": fmt_date(ad_end_date.strftime('%Y-%m-%d')),
                "pratyantar": pd_list
            })
            ad_current_date = ad_end_date
            
        timeline.append(md_entry)
        current_date = md_end_date
    return timeline

def get_locations():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT place_name, latitude, longitude FROM locations ORDER BY place_name")
    places = [{"name": row[0], "lat": row[1], "lon": row[2]} for row in cursor.fetchall()]
    conn.close()
    return places

def get_coordinates(place_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT latitude, longitude FROM locations WHERE place_name = ?", (place_name,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_all_timezones():
    """Return list of common world timezones with UTC offsets."""
    return [
        {"name": "UTC-12:00 (Baker Island)", "offset": -12.0},
        {"name": "UTC-11:00 (Midway Island, Samoa)", "offset": -11.0},
        {"name": "UTC-10:00 (Hawaii)", "offset": -10.0},
        {"name": "UTC-09:30 (Marquesas Islands)", "offset": -9.5},
        {"name": "UTC-09:00 (Alaska)", "offset": -9.0},
        {"name": "UTC-08:00 (Pacific Time - US/Canada)", "offset": -8.0},
        {"name": "UTC-07:00 (Mountain Time - US/Canada)", "offset": -7.0},
        {"name": "UTC-06:00 (Central Time - US/Canada)", "offset": -6.0},
        {"name": "UTC-05:00 (Eastern Time - US/Canada)", "offset": -5.0},
        {"name": "UTC-04:00 (Atlantic Time - Canada)", "offset": -4.0},
        {"name": "UTC-03:30 (Newfoundland)", "offset": -3.5},
        {"name": "UTC-03:00 (Brazil, Argentina)", "offset": -3.0},
        {"name": "UTC-02:00 (Mid-Atlantic)", "offset": -2.0},
        {"name": "UTC-01:00 (Azores, Cape Verde)", "offset": -1.0},
        {"name": "UTC+00:00 (UK, Ireland, Portugal)", "offset": 0.0},
        {"name": "UTC+01:00 (Central Europe, France, Germany)", "offset": 1.0},
        {"name": "UTC+02:00 (Eastern Europe, Egypt, South Africa)", "offset": 2.0},
        {"name": "UTC+03:00 (Moscow, Saudi Arabia, East Africa)", "offset": 3.0},
        {"name": "UTC+03:30 (Iran)", "offset": 3.5},
        {"name": "UTC+04:00 (UAE, Oman, Mauritius)", "offset": 4.0},
        {"name": "UTC+04:30 (Afghanistan)", "offset": 4.5},
        {"name": "UTC+05:00 (Pakistan, Maldives)", "offset": 5.0},
        {"name": "UTC+05:30 (India, Sri Lanka) ★", "offset": 5.5},
        {"name": "UTC+05:45 (Nepal)", "offset": 5.75},
        {"name": "UTC+06:00 (Bangladesh, Kazakhstan)", "offset": 6.0},
        {"name": "UTC+06:30 (Myanmar)", "offset": 6.5},
        {"name": "UTC+07:00 (Thailand, Vietnam, Indonesia)", "offset": 7.0},
        {"name": "UTC+08:00 (China, Singapore, Malaysia, Australia West)", "offset": 8.0},
        {"name": "UTC+08:45 (Eucla, Australia)", "offset": 8.75},
        {"name": "UTC+09:00 (Japan, Korea)", "offset": 9.0},
        {"name": "UTC+09:30 (Australia Central)", "offset": 9.5},
        {"name": "UTC+10:00 (Australia East, Papua New Guinea)", "offset": 10.0},
        {"name": "UTC+10:30 (Lord Howe Island)", "offset": 10.5},
        {"name": "UTC+11:00 (Solomon Islands, Vanuatu)", "offset": 11.0},
        {"name": "UTC+12:00 (New Zealand, Fiji)", "offset": 12.0},
        {"name": "UTC+13:00 (Tonga, Samoa)", "offset": 13.0},
        {"name": "UTC+14:00 (Line Islands)", "offset": 14.0},
    ]

# ─── Context Processor: Inject images into all templates ───
@app.context_processor
def inject_images():
    """Inject sidebar, footer, and plans images into all templates."""
    try:
        sidebar_images = get_images_by_placement('sidebar')
        footer_images = get_images_by_placement('footer')
        plans_images = get_images_by_placement('plans')
        general_images = get_images_by_placement('general')
        all_footer_images = sidebar_images + footer_images + plans_images + general_images
        return dict(
            sidebar_images=sidebar_images,
            footer_images=footer_images,
            plans_images=plans_images,
            general_images=general_images,
            all_footer_images=all_footer_images
        )
    except Exception as e:
        logger.error(f"Context processor error: {e}")
        return dict(
            sidebar_images=[], footer_images=[], plans_images=[],
            general_images=[], all_footer_images=[]
        )

# ─── Jinja2 Filter: Check if image should show on current page ───
@app.template_filter('should_show')
def should_show_filter(image, page_name):
    """Check if an image should be displayed on the given page."""
    target = image.get('page_target', 'all') or 'all'
    if target == 'all':
        return True
    targets = [t.strip() for t in target.split(',')]
    return page_name in targets

@app.route("/")
def home():
    try:
        places = get_locations()
    except Exception as e:
        logger.error(f"get_locations failed: {e}")
        places = []
    return render_template("index.html",
        places=places,
        timezones=get_all_timezones(),
        user_features=None,
        feature_defs=[]
    )

@app.route("/api/search-places")
def api_search_places():
    """Search places by name fragment."""
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT place_name, latitude, longitude FROM locations WHERE place_name LIKE ? ORDER BY place_name LIMIT 15",
        (f"%{q}%",)
    )
    results = [{"name": row[0], "lat": row[1], "lon": row[2]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(results)

@app.route("/calculate", methods=["POST"])
def calculate():
    name = request.form.get("name")
    dob = request.form.get("dob")
    tob = request.form.get("tob")
    place = request.form.get("place", "")
    gender = request.form.get("gender", "male")

    # Get lat/lon - either from manual input or from DB
    lat_str = request.form.get("lat", "")
    lon_str = request.form.get("lon", "")
    tz_str = request.form.get("timezone", "5.5")

    try:
        lat = float(lat_str) if lat_str else None
        lon = float(lon_str) if lon_str else None
    except (ValueError, TypeError):
        lat, lon = None, None

    # If lat/lon not provided manually, try DB
    if lat is None or lon is None:
        if place:
            coords = get_coordinates(place)
            if coords:
                lat, lon = coords
            else:
                lat, lon = 26.1445, 91.7362  # Default Guwahati
        else:
            lat, lon = 26.1445, 91.7362

    try:
        tz_offset = float(tz_str)
    except (ValueError, TypeError):
        tz_offset = 5.5

    try:
        ist_time = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
        jd = swe.julday(ist_time.year, ist_time.month, ist_time.day,
                        (ist_time.hour + ist_time.minute / 60.0) - tz_offset)

        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa(jd)

        planets_dict = {
            "ৰবি": swe.SUN, "চন্দ্ৰ": swe.MOON, "মংগল": swe.MARS,
            "বুধ": swe.MERCURY, "বৃহস্পতি": swe.JUPITER, "শুক্ৰ": swe.VENUS,
            "শনি": swe.SATURN, "ৰাহু": swe.MEAN_NODE
        }

        planets_data = []
        p_sidereal_longitudes = {}
        planet_signs = {}
        planet_houses = {}

        for p_name, p_id in planets_dict.items():
            pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            p_sidereal_longitudes[p_name] = pos[0]
            r_idx, rasi, deg = get_rasi_and_degree(pos[0])
            _, nak, lord = get_nakshatra_details(pos[0])
            planets_data.append({"name": p_name, "rasi": rasi, "degree": deg,
                                 "nakshatra": nak, "lord": lord})
            planet_signs[p_name] = r_idx

        # Ketu
        p_sidereal_longitudes["কেতু"] = (p_sidereal_longitudes["ৰাহু"] + 180) % 360
        r_idx_k, ketu_rasi, ketu_deg = get_rasi_and_degree(p_sidereal_longitudes["কেতু"])
        _, ketu_nak, ketu_lord = get_nakshatra_details(p_sidereal_longitudes["কেতু"])
        planets_data.append({"name": "কেতু", "rasi": ketu_rasi, "degree": ketu_deg,
                             "nakshatra": ketu_nak, "lord": ketu_lord})
        planet_signs["কেতু"] = r_idx_k

        # Lagna (Ascendant)
        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        asc_sidereal = (ascmc[0] - ayanamsa) % 360
        p_sidereal_longitudes["লগ্ন"] = asc_sidereal
        asc_rasi_idx, asc_rasi, asc_deg = get_rasi_and_degree(asc_sidereal)
        _, asc_nak, asc_nak_lord = get_nakshatra_details(asc_sidereal)
        planets_data.append({"name": "লগ্ন", "rasi": asc_rasi, "degree": asc_deg,
                             "nakshatra": asc_nak, "lord": asc_nak_lord})
        planet_signs["লগ্ন"] = asc_rasi_idx

        # Calculate house positions for all planets
        for p_name, p_lon in p_sidereal_longitudes.items():
            house_idx = (int(p_lon / 30) - asc_rasi_idx) % 12
            planet_houses[p_name] = house_idx

        # Varga Charts - Complete Shodashvarga (16 divisional charts)
        vargas = {
            "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D7": 7, "D9": 9,
            "D10": 10, "D12": 12, "D16": 16, "D20": 20, "D24": 24,
            "D27": 27, "D30": 30, "D40": 40, "D45": 45, "D60": 60
        }
        all_vargas = {}
        for v_code, v_num in vargas.items():
            all_vargas[v_code] = {}
            for p_key, p_lon in p_sidereal_longitudes.items():
                v_idx = calculate_varga(p_lon, v_num)
                if v_idx not in all_vargas[v_code]:
                    all_vargas[v_code][v_idx] = []
                all_vargas[v_code][v_idx].append(PLANET_SHORT.get(p_key, p_key[:2]))

        # Dasha
        dasa_hierarchy = get_full_dasa_hierarchy(p_sidereal_longitudes["চন্দ্ৰ"], ist_time)

        # Panchanga
        panchanga = get_full_panchanga(ist_time, lat, lon, tz_offset)

        # Dosha Analysis
        dosha_results = get_complete_dosha_analysis(planet_houses, p_sidereal_longitudes)

        # Yoga Analysis
        yoga_results = get_complete_yoga_analysis(planet_houses, planet_signs, asc_rasi_idx)

        # Tripap Rista Analysis
        moon_nak_idx = get_nakshatra_details(p_sidereal_longitudes["চন্দ্ৰ"])[0] + 1  # 1-indexed
        tripap_data = get_tripap_rista(moon_nak_idx)
        tripap_analysis = analyze_tripap_rista(moon_nak_idx, planet_houses)

        # Sannari Chakra
        sannari_data = get_sannari_data(moon_nak_idx)
        sannari_svg = generate_sannari_svg(moon_nak_idx, nakshatras[moon_nak_idx - 1])

        # Navatara Chakra
        navatara_data = get_navatara_data(moon_nak_idx)
        navatara_svg = generate_navatara_svg(moon_nak_idx)

        # Nakshatra Phala
        nakshatra_phala_text = apply_gender(get_nakshatra_phala(moon_nak_idx), gender)

        # Lagna Phala
        lagna_phala_text = apply_gender(get_lagna_phala(asc_rasi_idx), gender)

        # Rashi Phala (Moon sign based)
        moon_rasi_idx = get_rasi_and_degree(p_sidereal_longitudes["চন্দ্ৰ"])[0]
        rashi_phala_text = apply_gender(get_rashi_phala(moon_rasi_idx), gender)

        # Lagna Lord and Moon Rashi Lord
        lagna_lord = get_rashi_lord(asc_rasi_idx)
        moon_rashi_lord = get_rashi_lord(moon_rasi_idx)

        # Graha Bichar - all planets house-wise analysis
        graha_bichar_data = get_all_graha_bichar(planet_houses)
        graha_bichar_html = get_graha_bichar_html(planet_houses)

        # AI Interpretation
        ai_interpretation = generate_ai_interpretation(
            name, planets_data, asc_rasi, dosha_results, yoga_results, dasa_hierarchy,
            asc_rasi_idx=asc_rasi_idx,
            planet_signs=planet_signs,
            moon_nak_name=nakshatras[moon_nak_idx - 1],
            moon_rasi=rasis[moon_rasi_idx],
            tripap_ages=TRIPAP_AGES.get(moon_nak_idx, []),
            navatara_data=navatara_data,
            sannari_data=sannari_data
        )

        # Dasha Predictions - all Mahadasha + Antardasha predictions
        all_dasha_predictions = get_all_maha_antar_predictions(
            dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx
        )
        # Apply gender to dasha predictions
        for dp in all_dasha_predictions:
            dp["prediction"] = apply_gender(dp["prediction"], gender)

        # Current dasha prediction (first mahadasha, first antardasha)
        current_maha_eng = get_eng_planet(dasa_hierarchy[0]["md_lord"])
        current_antar_eng = get_eng_planet(dasa_hierarchy[0]["sub_dasas"][0]["ad_lord"])
        current_dasha_prediction = apply_gender(
            get_full_dasha_prediction(
                current_maha_eng, current_antar_eng, "",
                p_sidereal_longitudes, asc_rasi_idx
            ), gender
        )

        # Apply gender to AI interpretation
        ai_interpretation = apply_gender(ai_interpretation, gender)

    except Exception as e:
        return f"<div style='padding:40px;font-family:Arial;text-align:center;'><h2 style='color:#c62828;'>গণনা ত্ৰুটি</h2><p>{str(e)}</p><a href='/'>আকৌ চেষ্টা কৰক</a></div>"

    # Get user subscription info for the result page
    user_subscription_name = "বিনামূলীয়া"
    user_subscription_id = 1
    all_subscriptions = []
    if session.get('user_id'):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT s.name_asm, s.id FROM users u JOIN subscriptions s ON u.subscription_id = s.id WHERE u.id = ?",
            (session['user_id'],)
        ).fetchone()
        if row:
            user_subscription_name = row['name_asm']
            user_subscription_id = row['id']
        # Get all subscriptions for the upgrade modal
        subs = conn.execute("SELECT * FROM subscriptions WHERE is_active = 1 ORDER BY id").fetchall()
        all_subscriptions = [dict(s) for s in subs]
        conn.close()

    # Saturn Sare Sati / Dhaiya data for result page
    shani_sare_sati_data = get_shani_sare_sati_data(moon_rasi=rasis[moon_rasi_idx], planets_data=planets_data, user_dob=dob)

    return render_template("result.html",
                           user_name=name, user_dob=dob, user_tob=tob, user_place=place,
                           gender=gender, lat=lat, lon=lon, timezone=tz_offset,
                           planets=planets_data, all_vargas=all_vargas,
                           asc_rasi_index=asc_rasi_idx, asc_rasi=asc_rasi,
                           lagna_lord=lagna_lord, moon_rashi_lord=moon_rashi_lord,
                           dasa_data=dasa_hierarchy, panchanga=panchanga,
                           dosha_results=dosha_results, yoga_results=yoga_results,
                           ai_interpretation=ai_interpretation,
                           tripap_data=tripap_data, tripap_ages=TRIPAP_AGES.get(moon_nak_idx, []),
                           all_dasha_predictions=all_dasha_predictions,
                           current_dasha_prediction=current_dasha_prediction,
                           sannari_data=sannari_data, sannari_svg=sannari_svg,
                           moon_nak_name=nakshatras[moon_nak_idx - 1],
                           navatara_data=navatara_data, navatara_svg=navatara_svg,
                           nakshatra_phala_text=nakshatra_phala_text,
                           lagna_phala_text=lagna_phala_text,
                           rashi_phala_text=rashi_phala_text,
                           moon_rasi=rasis[moon_rasi_idx],
                           graha_bichar_data=graha_bichar_data,
                           graha_bichar_html=graha_bichar_html,
                           shani_sare_sati_data=shani_sare_sati_data,
                           user_features=get_user_features(session.get('user_id', 0)),
                           user_subscription_name=user_subscription_name,
                           user_subscription_id=user_subscription_id,
                           all_subscriptions=all_subscriptions)

@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    """Generate and download PDF report."""
    name = request.form.get("name")
    dob = request.form.get("dob")
    tob = request.form.get("tob")
    place = request.form.get("place", "")
    gender = request.form.get("gender", "male")

    # If patrika public_name is provided, use it; otherwise fall back to name
    patrika_public_name = request.form.get("public_name", "").strip()
    if patrika_public_name:
        name = patrika_public_name

    # If patrika birth_district is provided, use it; otherwise fall back to place
    patrika_birth_district = request.form.get("birth_district", "").strip()
    if patrika_birth_district:
        place = patrika_birth_district

    lat_str = request.form.get("lat", "")
    lon_str = request.form.get("lon", "")
    tz_str = request.form.get("timezone", "5.5")

    try:
        lat = float(lat_str) if lat_str else None
        lon = float(lon_str) if lon_str else None
    except (ValueError, TypeError):
        lat, lon = None, None

    if lat is None or lon is None:
        if place:
            coords = get_coordinates(place)
            if coords:
                lat, lon = coords
            else:
                lat, lon = 26.1445, 91.7362
        else:
            lat, lon = 26.1445, 91.7362

    try:
        tz_offset = float(tz_str)
    except (ValueError, TypeError):
        tz_offset = 5.5

    try:
        ist_time = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
        jd = swe.julday(ist_time.year, ist_time.month, ist_time.day,
                        (ist_time.hour + ist_time.minute / 60.0) - tz_offset)

        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa(jd)

        planets_dict = {
            "ৰবি": swe.SUN, "চন্দ্ৰ": swe.MOON, "মংগল": swe.MARS,
            "বুধ": swe.MERCURY, "বৃহস্পতি": swe.JUPITER, "শুক্ৰ": swe.VENUS,
            "শনি": swe.SATURN, "ৰাহু": swe.MEAN_NODE
        }

        planets_data = []
        p_sidereal_longitudes = {}
        planet_signs = {}
        planet_houses = {}

        for p_name, p_id in planets_dict.items():
            pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            p_sidereal_longitudes[p_name] = pos[0]
            r_idx, rasi, deg = get_rasi_and_degree(pos[0])
            _, nak, lord = get_nakshatra_details(pos[0])
            planets_data.append({"name": p_name, "rasi": rasi, "degree": deg,
                                 "nakshatra": nak, "lord": lord})
            planet_signs[p_name] = r_idx

        p_sidereal_longitudes["কেতু"] = (p_sidereal_longitudes["ৰাহু"] + 180) % 360
        r_idx_k, ketu_rasi, ketu_deg = get_rasi_and_degree(p_sidereal_longitudes["কেতু"])
        _, ketu_nak, ketu_lord = get_nakshatra_details(p_sidereal_longitudes["কেতু"])
        planets_data.append({"name": "কেতু", "rasi": ketu_rasi, "degree": ketu_deg,
                             "nakshatra": ketu_nak, "lord": ketu_lord})
        planet_signs["কেতু"] = r_idx_k

        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        asc_sidereal = (ascmc[0] - ayanamsa) % 360
        p_sidereal_longitudes["লগ্ন"] = asc_sidereal
        asc_rasi_idx, asc_rasi, asc_deg = get_rasi_and_degree(asc_sidereal)
        _, asc_nak, asc_nak_lord = get_nakshatra_details(asc_sidereal)
        planets_data.append({"name": "লগ্ন", "rasi": asc_rasi, "degree": asc_deg,
                             "nakshatra": asc_nak, "lord": asc_nak_lord})
        planet_signs["লগ্ন"] = asc_rasi_idx

        for p_name, p_lon in p_sidereal_longitudes.items():
            house_idx = (int(p_lon / 30) - asc_rasi_idx) % 12
            planet_houses[p_name] = house_idx

        dasa_hierarchy = get_full_dasa_hierarchy(p_sidereal_longitudes["চন্দ্ৰ"], ist_time)
        panchanga = get_full_panchanga(ist_time, lat, lon, tz_offset)
        dosha_results = get_complete_dosha_analysis(planet_houses, p_sidereal_longitudes)
        yoga_results = get_complete_yoga_analysis(planet_houses, planet_signs, asc_rasi_idx)

        # Calculate moon indices BEFORE AI interpretation
        moon_nak_idx = get_nakshatra_details(p_sidereal_longitudes["চন্দ্ৰ"])[0] + 1
        moon_rasi_idx = get_rasi_and_degree(p_sidereal_longitudes["চন্দ্ৰ"])[0]
        navatara_data = get_navatara_data(moon_nak_idx)
        sannari_data = get_sannari_data(moon_nak_idx)

        ai_interpretation = generate_ai_interpretation(
            name, planets_data, asc_rasi, dosha_results, yoga_results, dasa_hierarchy,
            asc_rasi_idx=asc_rasi_idx,
            planet_signs=planet_signs,
            moon_nak_name=nakshatras[moon_nak_idx - 1],
            moon_rasi=rasis[moon_rasi_idx],
            tripap_ages=TRIPAP_AGES.get(moon_nak_idx, []),
            navatara_data=navatara_data,
            sannari_data=sannari_data
        )

        # Varga Charts for PDF
        vargas = {
            "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D7": 7, "D9": 9,
            "D10": 10, "D12": 12, "D16": 16, "D20": 20, "D24": 24,
            "D27": 27, "D30": 30, "D40": 40, "D45": 45, "D60": 60
        }
        all_vargas = {}
        for v_code, v_num in vargas.items():
            all_vargas[v_code] = {}
            for p_key, p_lon in p_sidereal_longitudes.items():
                v_idx = calculate_varga(p_lon, v_num)
                if v_idx not in all_vargas[v_code]:
                    all_vargas[v_code][v_idx] = []
                all_vargas[v_code][v_idx].append(PLANET_SHORT.get(p_key, p_key[:2]))

        # Tripap Rista for PDF
        tripap_data = get_tripap_rista(moon_nak_idx)
        tripap_ages = TRIPAP_AGES.get(moon_nak_idx, [])

        # Sannari Chakra for PDF
        sannari_html = generate_sannari_html_table(moon_nak_idx, nakshatras[moon_nak_idx - 1])

        # Navatara Chakra for PDF
        navatara_html = generate_navatara_html(moon_nak_idx)

        # Nakshatra Phala for PDF
        nakshatra_phala_html = apply_gender(get_nakshatra_phala_html(moon_nak_idx), gender)

        # Lagna Phala for PDF
        lagna_phala_html = apply_gender(get_lagna_phala_html(asc_rasi_idx), gender)

        # Rashi Phala for PDF (Moon sign based)
        rashi_phala_html = apply_gender(get_rashi_phala_html(moon_rasi_idx), gender)

        # Lagna Lord and Moon Rashi Lord for PDF
        lagna_lord = get_rashi_lord(asc_rasi_idx)
        moon_rashi_lord = get_rashi_lord(moon_rasi_idx)
        moon_rasi = rasis[moon_rasi_idx]

        # Graha Bichar for PDF
        graha_bichar_html = get_graha_bichar_html(planet_houses)

        # Dasha Predictions for PDF - use small_antardasaphal.py data (filtered)
        antardasha_phala_html = build_antardasha_html(
            dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx,
            selected_maha=None, include_current_and_future_only=True, gender=gender
        )

        # Apply gender to AI interpretation
        ai_interpretation = apply_gender(ai_interpretation, gender)

        # Get astrologer profile for PDF footer (user's profile, fallback to admin)
        astrologer_profile = get_astrologer_profile(session.get('user_id', 0))

        # Generate patrika text for PDF
        patrika_text = generate_patrika_text(
            public_name=name,
            secret_name=request.form.get('secret_name', ''),
            father_name=request.form.get('father_name', ''),
            mother_name=request.form.get('mother_name', ''),
            birth_district=patrika_birth_district if patrika_birth_district else place,
            residence_district=request.form.get('residence_district', ''),
            residence=request.form.get('residence', ''),
            gender=gender,
            dob=dob, tob=tob,
            asc_rasi=asc_rasi, asc_rasi_idx=asc_rasi_idx, asc_degree=asc_deg,
            moon_rasi=moon_rasi, moon_rasi_idx=moon_rasi_idx,
            nakshatra_name=nakshatras[moon_nak_idx - 1],
            nakshatra_idx=moon_nak_idx - 1,
            nakshatra_pada=panchanga.get('nakshatra', {}).get('pada', 1),
            panchanga=panchanga,
        )

        pdf_bytes = generate_pdf_report(
            name, dob, tob, place, planets_data, panchanga,
            dosha_results, yoga_results, dasa_hierarchy, ai_interpretation,
            all_vargas, tripap_data, tripap_ages, asc_rasi,
            [], sannari_html, navatara_html,
            nakshatra_phala_html, lagna_phala_html, rashi_phala_html,
            graha_bichar_html=graha_bichar_html,
            antardasha_phala_html=antardasha_phala_html,
            lagna_lord=lagna_lord, moon_rashi_lord=moon_rashi_lord,
            moon_rasi=moon_rasi, gender=gender,
            astrologer_profile=astrologer_profile,
            patrika_text=patrika_text
        )

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Dhruvatara_AI_{name.replace(" ", "_")}.pdf'
        )

    except Exception as e:
        return f"<div style='padding:40px;font-family:Arial;text-align:center;'><h2 style='color:#c62828;'>PDF নিৰ্মাণ ত্ৰুটি</h2><p>{str(e)}</p><a href='/'>আকৌ চেষ্টা কৰক</a></div>"

@app.route("/generate-patrika", methods=["POST"])
def generate_patrika():
    """Generate patrika text from form data."""
    # Check feature access - only paid users can generate patrika
    if session.get('user_id'):
        if not check_feature_access(session['user_id'], 'patrika_pdf'):
            return jsonify({'error': 'পত্ৰিকা বনাবলৈ প্ৰ\' ভাৰ্চনলৈ আপগ্ৰেড কৰক।'}), 403
    try:
        data = request.get_json()
        patrika_text = generate_patrika_text(
            public_name=data.get('public_name', ''),
            secret_name=data.get('secret_name', ''),
            father_name=data.get('father_name', ''),
            mother_name=data.get('mother_name', ''),
            birth_district=data.get('birth_district', ''),
            residence_district=data.get('residence_district', ''),
            residence=data.get('residence', ''),
            gender=data.get('blessing', data.get('gender', 'male')),
            dob=data.get('dob', ''),
            tob=data.get('tob', ''),
            asc_rasi=data.get('asc_rasi', ''),
            asc_rasi_idx=int(data.get('asc_rasi_idx', 0)),
            asc_degree=float(data.get('asc_degree', 0)),
            moon_rasi=data.get('moon_rasi', ''),
            moon_rasi_idx=int(data.get('moon_rasi_idx', 0)),
            nakshatra_name=data.get('nakshatra_name', ''),
            nakshatra_idx=int(data.get('nakshatra_idx', 0)),
            nakshatra_pada=int(data.get('nakshatra_pada', 1)),
            panchanga={
                'tithi': {'name': data.get('tithi_name', '—')},
                'paksha': data.get('paksha', ''),
                'nakshatra': {'name': data.get('nakshatra_name', '—'), 'index': int(data.get('nakshatra_idx', 0)), 'pada': int(data.get('nakshatra_pada', 1))},
                'yoga': {'name': data.get('yoga_name', '—')},
                'karana': {'name': data.get('karana_name', '—')},
                'vaar': {'name': data.get('vaar_name', '—'), 'index': int(data.get('vaar_idx', 0))},
                'masa': {'name': data.get('masa_name', '—')},
                'varna': data.get('varna', '—'),
                'gana': data.get('gana', '—'),
                'sunrise': data.get('sunrise', '06:00'),
            },
        )
        return jsonify({'patrika_text': patrika_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/download-patrika-pdf", methods=["POST"])
def download_patrika_pdf():
    """Generate PDF with patrika text below D1 chart."""
    # Check feature access - only paid users can download patrika PDF
    if session.get('user_id'):
        if not check_feature_access(session['user_id'], 'patrika_pdf'):
            return "<div style='padding:40px;font-family:Arial;text-align:center;'><h2 style='color:#c62828;'>🔒 প্ৰৱেশ নিষেধ</h2><p>পত্ৰিকা PDF ডাউনলোড কৰিবলৈ প্ৰ' ভাৰ্চনলৈ আপগ্ৰেড কৰক।</p><a href='/'>আকৌ চেষ্টা কৰক</a></div>"
    # Recalculate everything (same as download_pdf) but add patrika text
    name = request.form.get("name", request.form.get("public_name", ""))
    dob = request.form.get("dob")
    tob = request.form.get("tob")
    place = request.form.get("place", "")
    gender = request.form.get("gender", request.form.get("blessing", "male"))

    # If patrika public_name is provided, use it; otherwise fall back to name
    patrika_public_name = request.form.get("public_name", "").strip()
    if patrika_public_name:
        name = patrika_public_name

    # If patrika birth_district is provided, use it; otherwise fall back to place
    patrika_birth_district = request.form.get("birth_district", "").strip()
    if patrika_birth_district:
        place = patrika_birth_district
    
    lat_str = request.form.get("lat", "")
    lon_str = request.form.get("lon", "")
    tz_str = request.form.get("timezone", "5.5")
    
    try:
        lat = float(lat_str) if lat_str else None
        lon = float(lon_str) if lon_str else None
    except (ValueError, TypeError):
        lat, lon = None, None
    
    if lat is None or lon is None:
        if place:
            coords = get_coordinates(place)
            if coords:
                lat, lon = coords
            else:
                lat, lon = 26.1445, 91.7362
        else:
            lat, lon = 26.1445, 91.7362
    
    try:
        tz_offset = float(tz_str)
    except (ValueError, TypeError):
        tz_offset = 5.5
    
    try:
        ist_time = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
        jd = swe.julday(ist_time.year, ist_time.month, ist_time.day,
                        (ist_time.hour + ist_time.minute / 60.0) - tz_offset)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa(jd)
        
        planets_dict = {
            "ৰবি": swe.SUN, "চন্দ্ৰ": swe.MOON, "মংগল": swe.MARS,
            "বুধ": swe.MERCURY, "বৃহস্পতি": swe.JUPITER, "শুক্ৰ": swe.VENUS,
            "শনি": swe.SATURN, "ৰাহু": swe.MEAN_NODE
        }
        
        planets_data = []
        p_sidereal_longitudes = {}
        planet_signs = {}
        planet_houses = {}
        
        for p_name, p_id in planets_dict.items():
            pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            p_sidereal_longitudes[p_name] = pos[0]
            r_idx, rasi, deg = get_rasi_and_degree(pos[0])
            _, nak, lord = get_nakshatra_details(pos[0])
            planets_data.append({"name": p_name, "rasi": rasi, "degree": deg,
                                 "nakshatra": nak, "lord": lord})
            planet_signs[p_name] = r_idx
        
        p_sidereal_longitudes["কেতু"] = (p_sidereal_longitudes["ৰাহু"] + 180) % 360
        r_idx_k, ketu_rasi, ketu_deg = get_rasi_and_degree(p_sidereal_longitudes["কেতু"])
        _, ketu_nak, ketu_lord = get_nakshatra_details(p_sidereal_longitudes["কেতু"])
        planets_data.append({"name": "কেতু", "rasi": ketu_rasi, "degree": ketu_deg,
                             "nakshatra": ketu_nak, "lord": ketu_lord})
        planet_signs["কেতু"] = r_idx_k
        
        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        asc_sidereal = (ascmc[0] - ayanamsa) % 360
        p_sidereal_longitudes["লগ্ন"] = asc_sidereal
        asc_rasi_idx, asc_rasi, asc_deg = get_rasi_and_degree(asc_sidereal)
        _, asc_nak, asc_nak_lord = get_nakshatra_details(asc_sidereal)
        planets_data.append({"name": "লগ্ন", "rasi": asc_rasi, "degree": asc_deg,
                             "nakshatra": asc_nak, "lord": asc_nak_lord})
        planet_signs["লগ্ন"] = asc_rasi_idx
        
        for p_name, p_lon in p_sidereal_longitudes.items():
            house_idx = (int(p_lon / 30) - asc_rasi_idx) % 12
            planet_houses[p_name] = house_idx
        
        dasa_hierarchy = get_full_dasa_hierarchy(p_sidereal_longitudes["চন্দ্ৰ"], ist_time)
        panchanga = get_full_panchanga(ist_time, lat, lon, tz_offset)
        dosha_results = get_complete_dosha_analysis(planet_houses, p_sidereal_longitudes)
        yoga_results = get_complete_yoga_analysis(planet_houses, planet_signs, asc_rasi_idx)
        
        moon_nak_idx = get_nakshatra_details(p_sidereal_longitudes["চন্দ্ৰ"])[0] + 1
        moon_rasi_idx = get_rasi_and_degree(p_sidereal_longitudes["চন্দ্ৰ"])[0]
        navatara_data = get_navatara_data(moon_nak_idx)
        sannari_data = get_sannari_data(moon_nak_idx)
        
        ai_interpretation = generate_ai_interpretation(
            name, planets_data, asc_rasi, dosha_results, yoga_results, dasa_hierarchy,
            asc_rasi_idx=asc_rasi_idx, planet_signs=planet_signs,
            moon_nak_name=nakshatras[moon_nak_idx - 1],
            moon_rasi=rasis[moon_rasi_idx],
            tripap_ages=TRIPAP_AGES.get(moon_nak_idx, []),
            navatara_data=navatara_data, sannari_data=sannari_data
        )
        
        vargas = {"D1": 1, "D2": 2, "D3": 3, "D4": 4, "D7": 7, "D9": 9,
                  "D10": 10, "D12": 12, "D16": 16, "D20": 20, "D24": 24,
                  "D27": 27, "D30": 30, "D40": 40, "D45": 45, "D60": 60}
        all_vargas = {}
        for v_code, v_num in vargas.items():
            all_vargas[v_code] = {}
            for p_key, p_lon in p_sidereal_longitudes.items():
                v_idx = calculate_varga(p_lon, v_num)
                if v_idx not in all_vargas[v_code]:
                    all_vargas[v_code][v_idx] = []
                all_vargas[v_code][v_idx].append(PLANET_SHORT.get(p_key, p_key[:2]))
        
        tripap_data = get_tripap_rista(moon_nak_idx)
        tripap_ages = TRIPAP_AGES.get(moon_nak_idx, [])
        sannari_html = generate_sannari_html_table(moon_nak_idx, nakshatras[moon_nak_idx - 1])
        navatara_html = generate_navatara_html(moon_nak_idx)
        nakshatra_phala_html = apply_gender(get_nakshatra_phala_html(moon_nak_idx), gender)
        lagna_phala_html = apply_gender(get_lagna_phala_html(asc_rasi_idx), gender)
        rashi_phala_html = apply_gender(get_rashi_phala_html(moon_rasi_idx), gender)
        lagna_lord = get_rashi_lord(asc_rasi_idx)
        moon_rashi_lord = get_rashi_lord(moon_rasi_idx)
        moon_rasi = rasis[moon_rasi_idx]
        graha_bichar_html = get_graha_bichar_html(planet_houses)
        
        all_dasha_predictions = get_all_maha_antar_predictions(
            dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx
        )
        for dp in all_dasha_predictions:
            dp["prediction"] = apply_gender(dp["prediction"], gender)
        all_dasha_predictions = filter_future_dasha_predictions(all_dasha_predictions)
        ai_interpretation = apply_gender(ai_interpretation, gender)
        
        # Generate patrika text
        patrika_text = generate_patrika_text(
            public_name=name,
            secret_name=request.form.get('secret_name', ''),
            father_name=request.form.get('father_name', ''),
            mother_name=request.form.get('mother_name', ''),
            birth_district=patrika_birth_district if patrika_birth_district else place,
            residence_district=request.form.get('residence_district', ''),
            residence=request.form.get('residence', ''),
            gender=gender,
            dob=dob, tob=tob,
            asc_rasi=asc_rasi, asc_rasi_idx=asc_rasi_idx, asc_degree=asc_deg,
            moon_rasi=moon_rasi, moon_rasi_idx=moon_rasi_idx,
            nakshatra_name=nakshatras[moon_nak_idx - 1],
            nakshatra_idx=moon_nak_idx - 1,
            nakshatra_pada=panchanga.get('nakshatra', {}).get('pada', 1),
            panchanga=panchanga,
        )
        
        astrologer_profile = get_astrologer_profile(session.get('user_id', 0))

        # Build antardasha phala HTML for patrika PDF (current → end)
        antardasha_phala_html = build_antardasha_html(
            dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx,
            selected_maha=None, include_current_and_future_only=True, gender=gender
        )
        
        pdf_bytes = generate_pdf_report(
            name, dob, tob, place, planets_data, panchanga,
            dosha_results, yoga_results, dasa_hierarchy, ai_interpretation,
            all_vargas, tripap_data, tripap_ages, asc_rasi,
            [], sannari_html, navatara_html,
            nakshatra_phala_html, lagna_phala_html, rashi_phala_html,
            graha_bichar_html=graha_bichar_html,
            antardasha_phala_html=antardasha_phala_html,
            lagna_lord=lagna_lord, moon_rashi_lord=moon_rashi_lord,
            moon_rasi=moon_rasi, gender=gender,
            astrologer_profile=astrologer_profile,
            patrika_text=patrika_text
        )
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Dhruvatara_AI_Patrika_{name.replace(" ", "_")}.pdf'
        )
    except Exception as e:
        return f"<div style='padding:40px;font-family:Arial;text-align:center;'><h2 style='color:#c62828;'>পত্ৰিকা PDF নিৰ্মাণ ত্ৰুটি</h2><p>{str(e)}</p><a href='/'>আকৌ চেষ্টা কৰক</a></div>"

@app.route("/custom-pdf", methods=["POST"])
def custom_pdf():
    """Generate custom PDF with user-selected sections."""
    name = request.form.get("name")
    dob = request.form.get("dob")
    tob = request.form.get("tob")
    place = request.form.get("place", "")
    gender = request.form.get("gender", "male")
    selected_sections = request.form.getlist("sections")
    dasha_limit_str = request.form.get("dasha_limit", "0")

    # If patrika public_name is provided, use it; otherwise fall back to name
    patrika_public_name = request.form.get("public_name", "").strip()
    if patrika_public_name:
        name = patrika_public_name

    # If patrika birth_district is provided, use it; otherwise fall back to place
    patrika_birth_district = request.form.get("birth_district", "").strip()
    if patrika_birth_district:
        place = patrika_birth_district

    # Parse dasha_limit: "0"=all, "9"=first 9, "s9"=skip first 9
    dasha_limit = 0
    dasha_skip = 0
    try:
        if dasha_limit_str.startswith('s'):
            dasha_skip = int(dasha_limit_str[1:])
        else:
            dasha_limit = int(dasha_limit_str)
    except (ValueError, TypeError):
        dasha_limit = 0
        dasha_skip = 0

    lat_str = request.form.get("lat", "")
    lon_str = request.form.get("lon", "")
    tz_str = request.form.get("timezone", "5.5")

    try:
        lat = float(lat_str) if lat_str else None
        lon = float(lon_str) if lon_str else None
    except (ValueError, TypeError):
        lat, lon = None, None

    if lat is None or lon is None:
        if place:
            coords = get_coordinates(place)
            if coords:
                lat, lon = coords
            else:
                lat, lon = 26.1445, 91.7362
        else:
            lat, lon = 26.1445, 91.7362

    try:
        tz_offset = float(tz_str)
    except (ValueError, TypeError):
        tz_offset = 5.5

    try:
        ist_time = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
        jd = swe.julday(ist_time.year, ist_time.month, ist_time.day,
                        (ist_time.hour + ist_time.minute / 60.0) - tz_offset)

        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa(jd)

        planets_dict = {
            "ৰবি": swe.SUN, "চন্দ্ৰ": swe.MOON, "মংগল": swe.MARS,
            "বুধ": swe.MERCURY, "বৃহস্পতি": swe.JUPITER, "শুক্ৰ": swe.VENUS,
            "শনি": swe.SATURN, "ৰাহু": swe.MEAN_NODE
        }

        planets_data = []
        p_sidereal_longitudes = {}
        planet_signs = {}
        planet_houses = {}

        for p_name, p_id in planets_dict.items():
            pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            p_sidereal_longitudes[p_name] = pos[0]
            r_idx, rasi, deg = get_rasi_and_degree(pos[0])
            _, nak, lord = get_nakshatra_details(pos[0])
            planets_data.append({"name": p_name, "rasi": rasi, "degree": deg,
                                 "nakshatra": nak, "lord": lord})
            planet_signs[p_name] = r_idx

        p_sidereal_longitudes["কেতু"] = (p_sidereal_longitudes["ৰাহু"] + 180) % 360
        r_idx_k, ketu_rasi, ketu_deg = get_rasi_and_degree(p_sidereal_longitudes["কেতু"])
        _, ketu_nak, ketu_lord = get_nakshatra_details(p_sidereal_longitudes["কেতু"])
        planets_data.append({"name": "কেতু", "rasi": ketu_rasi, "degree": ketu_deg,
                             "nakshatra": ketu_nak, "lord": ketu_lord})
        planet_signs["কেতু"] = r_idx_k

        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        asc_sidereal = (ascmc[0] - ayanamsa) % 360
        p_sidereal_longitudes["লগ্ন"] = asc_sidereal
        asc_rasi_idx, asc_rasi, asc_deg = get_rasi_and_degree(asc_sidereal)
        _, asc_nak, asc_nak_lord = get_nakshatra_details(asc_sidereal)
        planets_data.append({"name": "লগ্ন", "rasi": asc_rasi, "degree": asc_deg,
                             "nakshatra": asc_nak, "lord": asc_nak_lord})
        planet_signs["লগ্ন"] = asc_rasi_idx

        for p_name, p_lon in p_sidereal_longitudes.items():
            house_idx = (int(p_lon / 30) - asc_rasi_idx) % 12
            planet_houses[p_name] = house_idx

        dasa_hierarchy = get_full_dasa_hierarchy(p_sidereal_longitudes["চন্দ্ৰ"], ist_time)
        panchanga = get_full_panchanga(ist_time, lat, lon, tz_offset)
        dosha_results = get_complete_dosha_analysis(planet_houses, p_sidereal_longitudes)
        yoga_results = get_complete_yoga_analysis(planet_houses, planet_signs, asc_rasi_idx)

        # Calculate moon indices BEFORE AI interpretation
        moon_nak_idx = get_nakshatra_details(p_sidereal_longitudes["চন্দ্ৰ"])[0] + 1
        moon_rasi_idx = get_rasi_and_degree(p_sidereal_longitudes["চন্দ্ৰ"])[0]

        # Navatara & Sannari data for AI
        navatara_data = get_navatara_data(moon_nak_idx)
        sannari_data = get_sannari_data(moon_nak_idx)

        ai_interpretation = generate_ai_interpretation(
            name, planets_data, asc_rasi, dosha_results, yoga_results, dasa_hierarchy,
            asc_rasi_idx=asc_rasi_idx,
            planet_signs=planet_signs,
            moon_nak_name=nakshatras[moon_nak_idx - 1],
            moon_rasi=rasis[moon_rasi_idx],
            tripap_ages=TRIPAP_AGES.get(moon_nak_idx, []),
            navatara_data=navatara_data,
            sannari_data=sannari_data
        )

        # Varga Charts
        vargas = {
            "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D7": 7, "D9": 9,
            "D10": 10, "D12": 12, "D16": 16, "D20": 20, "D24": 24,
            "D27": 27, "D30": 30, "D40": 40, "D45": 45, "D60": 60
        }
        all_vargas = {}
        for v_code, v_num in vargas.items():
            all_vargas[v_code] = {}
            for p_key, p_lon in p_sidereal_longitudes.items():
                v_idx = calculate_varga(p_lon, v_num)
                if v_idx not in all_vargas[v_code]:
                    all_vargas[v_code][v_idx] = []
                all_vargas[v_code][v_idx].append(PLANET_SHORT.get(p_key, p_key[:2]))

        tripap_data = get_tripap_rista(moon_nak_idx)
        tripap_ages = TRIPAP_AGES.get(moon_nak_idx, [])

        sannari_html = generate_sannari_html_table(moon_nak_idx, nakshatras[moon_nak_idx - 1])

        navatara_html = generate_navatara_html(moon_nak_idx)

        nakshatra_phala_html = apply_gender(get_nakshatra_phala_html(moon_nak_idx), gender)
        lagna_phala_html = apply_gender(get_lagna_phala_html(asc_rasi_idx), gender)

        rashi_phala_html = apply_gender(get_rashi_phala_html(moon_rasi_idx), gender)

        # Lagna Lord and Moon Rashi Lord for PDF
        lagna_lord = get_rashi_lord(asc_rasi_idx)
        moon_rashi_lord = get_rashi_lord(moon_rasi_idx)
        moon_rasi = rasis[moon_rasi_idx]

        # Graha Bichar for PDF
        graha_bichar_html = get_graha_bichar_html(planet_houses)

        all_dasha_predictions = get_all_maha_antar_predictions(
            dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx
        )
        for dp in all_dasha_predictions:
            dp["prediction"] = apply_gender(dp["prediction"], gender)

        # Filter: only include antardashas that end today or later (not past)
        all_dasha_predictions = filter_future_dasha_predictions(all_dasha_predictions)

        ai_interpretation = apply_gender(ai_interpretation, gender)

        # Apply dasha limit/skip
        if dasha_skip > 0 and dasha_skip < len(all_dasha_predictions):
            all_dasha_predictions = all_dasha_predictions[dasha_skip:]
        elif dasha_limit > 0 and dasha_limit < len(all_dasha_predictions):
            all_dasha_predictions = all_dasha_predictions[:dasha_limit]

        # Generate patrika text for custom PDF
        patrika_text = generate_patrika_text(
            public_name=name,
            secret_name=request.form.get('secret_name', ''),
            father_name=request.form.get('father_name', ''),
            mother_name=request.form.get('mother_name', ''),
            birth_district=patrika_birth_district if patrika_birth_district else place,
            residence_district=request.form.get('residence_district', ''),
            residence=request.form.get('residence', ''),
            gender=gender,
            dob=dob, tob=tob,
            asc_rasi=asc_rasi, asc_rasi_idx=asc_rasi_idx, asc_degree=asc_deg,
            moon_rasi=moon_rasi, moon_rasi_idx=moon_rasi_idx,
            nakshatra_name=nakshatras[moon_nak_idx - 1],
            nakshatra_idx=moon_nak_idx - 1,
            nakshatra_pada=panchanga.get('nakshatra', {}).get('pada', 1),
            panchanga=panchanga,
        )

        # Get astrologer profile for PDF footer (user's profile, fallback to admin)
        astrologer_profile = get_astrologer_profile(session.get('user_id', 0))

        # Build antardasha phala HTML for custom PDF (only if selected)
        antardasha_phala_html = ""
        if 'antardasha_phala' in selected_sections:
            antardasha_mode = request.form.get("antardasha_mode", "current_onward")
            antardasha_maha = request.form.get("antardasha_maha", "").strip()

            if antardasha_mode == "selected_maha" and antardasha_maha:
                # Show all antardashas of the selected mahadasha (future only)
                antardasha_phala_html = build_antardasha_html(
                    dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx,
                    selected_maha=antardasha_maha, include_current_and_future_only=True, gender=gender
                )
            elif antardasha_mode == "all_future":
                # Show all future antardashas across all mahadashas
                antardasha_phala_html = build_antardasha_html(
                    dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx,
                    selected_maha=None, include_current_and_future_only=True, gender=gender
                )
            else:
                # current_onward: current antardasha → end of current mahadasha
                antardasha_phala_html = build_antardasha_html(
                    dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx,
                    selected_maha=None, include_current_and_future_only=True, gender=gender
                )

        pdf_bytes = generate_pdf_report(
            name, dob, tob, place, planets_data, panchanga,
            dosha_results, yoga_results, dasa_hierarchy, ai_interpretation,
            all_vargas, tripap_data, tripap_ages, asc_rasi,
            all_dasha_predictions, sannari_html, navatara_html,
            nakshatra_phala_html, lagna_phala_html, rashi_phala_html,
            graha_bichar_html=graha_bichar_html,
            antardasha_phala_html=antardasha_phala_html,
            selected_sections=selected_sections,
            lagna_lord=lagna_lord, moon_rashi_lord=moon_rashi_lord,
            moon_rasi=moon_rasi, gender=gender,
            astrologer_profile=astrologer_profile,
            patrika_text=patrika_text
        )

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Dhruvatara_AI_Custom_{name.replace(" ", "_")}.pdf'
        )

    except Exception as e:
        return f"<div style='padding:40px;font-family:Arial;text-align:center;'><h2 style='color:#c62828;'>PDF নিৰ্মাণ ত্ৰুটি</h2><p>{str(e)}</p><a href='/'>আকৌ চেষ্টা কৰক</a></div>"

@app.route("/api/panchanga", methods=["GET"])
def api_panchanga():
    """API endpoint for Panchanga data."""
    lat = float(request.args.get("lat", 26.1445))
    lon = float(request.args.get("lon", 91.7362))
    now = datetime.now()
    panchanga = get_full_panchanga(now, lat, lon, tz_offset)
    return jsonify(panchanga)


@app.route("/api/dasha-prediction", methods=["POST"])
def api_dasha_prediction():
    """API endpoint for dynamic dasha predictions."""
    data = request.get_json()
    maha_eng = data.get("maha", "")
    antar_eng = data.get("antar", "")
    prat_eng = data.get("prat", "")

    # Recalculate planet positions from stored session or request data
    dob = data.get("dob", "")
    tob = data.get("tob", "")
    place = data.get("place", "")

    if not dob or not tob or not place:
        return jsonify({"error": "Missing birth data"}), 400

    lat, lon = get_coordinates(place)
    ist_time = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    jd = swe.julday(ist_time.year, ist_time.month, ist_time.day,
                    (ist_time.hour + ist_time.minute / 60.0) - 5.5)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa(jd)

    planets_dict = {
        "ৰবি": swe.SUN, "চন্দ্ৰ": swe.MOON, "মংগল": swe.MARS,
        "বুধ": swe.MERCURY, "বৃহস্পতি": swe.JUPITER, "শুক্ৰ": swe.VENUS,
        "শনি": swe.SATURN, "ৰাহু": swe.MEAN_NODE
    }

    p_sidereal_longitudes = {}
    for p_name, p_id in planets_dict.items():
        pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        p_sidereal_longitudes[p_name] = pos[0]

    p_sidereal_longitudes["কেতু"] = (p_sidereal_longitudes["ৰাহু"] + 180) % 360

    cusps, ascmc = swe.houses(jd, lat, lon, b'P')
    asc_sidereal = (ascmc[0] - ayanamsa) % 360
    asc_rasi_idx = int(asc_sidereal / 30) % 12

    # Convert planet keys to English for dasha engine
    planet_degrees_en = {}
    asm_to_en = {"ৰবি": "Sun", "চন্দ্ৰ": "Moon", "মংগল": "Mars", "বুধ": "Mercury",
                 "বৃহস্পতি": "Jupiter", "শুক্ৰ": "Venus", "শনি": "Saturn",
                 "ৰাহু": "Rahu", "কেতু": "Ketu"}
    for k, v in p_sidereal_longitudes.items():
        planet_degrees_en[asm_to_en.get(k, k)] = v

    prediction = get_full_dasha_prediction(
        maha_eng, antar_eng, prat_eng,
        planet_degrees_en, asc_rasi_idx
    )

    return jsonify({"prediction": prediction})

# ═══════════════════════════════════════════
#  অন্তৰদশা ফল API (small_antardasaphal.py)
# ═══════════════════════════════════════════

@app.route("/api/antardasha-phala", methods=["POST"])
def api_antardasha_phala():
    """API endpoint for antardasha phala from small JSON data."""
    data = request.get_json()
    graha_name = data.get("graha", "")
    rashi_name = data.get("rashi", "")
    house_num = data.get("house", 0)

    if not graha_name or not rashi_name or not house_num:
        return jsonify({"error": "Missing graha/rashi/house"}), 400

    phala_text = get_antardasha_phala(graha_name, rashi_name, int(house_num))
    return jsonify({"phala": phala_text})

# ═══════════════════════════════════════════
#  AUTH ROUTES (Login, Register, Verify)
# ═══════════════════════════════════════════

@app.route("/login")
def login_page():
    """User login/register page."""
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    """Handle user login."""
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    ip = request.remote_addr

    success, message, user_data = login_user(email, password, ip)

    if success:
        session['user_id'] = user_data['id']
        session['user_name'] = user_data['name']
        session['user_email'] = user_data['email']
        flash(message, 'success')
        return redirect(url_for('user_dashboard'))
    else:
        flash(message, 'error')
        return redirect(url_for('login_page'))


@app.route("/register", methods=["POST"])
def register_post():
    """Handle user registration."""
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    mobile = request.form.get("mobile", "").strip() or None
    password = request.form.get("password", "")

    if len(password) < 6:
        flash("পাছৱৰ্ড ন্যূনতম ৬ আখৰৰ হ'ব লাগিব।", 'error')
        return redirect(url_for('login_page'))

    success, message = register_user(name, email, mobile, password)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('login_page'))


@app.route("/verify")
@login_required
def verify_page():
    """Email/Mobile verification page."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()

    if not user:
        flash("ব্যৱহাৰকাৰী পোৱা নগল।", 'error')
        return redirect(url_for('login_page'))

    return render_template("verify.html", user=dict(user))


@app.route("/verify/email", methods=["POST"])
@login_required
def verify_email_post():
    """Handle email verification."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute("SELECT email FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()

    otp = request.form.get("email_otp", "").strip()
    success, message = verify_email(user['email'], otp)

    flash(message, 'success' if success else 'error')
    return redirect(url_for('verify_page'))


@app.route("/verify/mobile", methods=["POST"])
@login_required
def verify_mobile_post():
    """Handle mobile verification."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute("SELECT mobile FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()

    if not user['mobile']:
        flash("আপোনাৰ মোবাইল নম্বৰ পঞ্জীয়ন কৰা নাই।", 'error')
        return redirect(url_for('verify_page'))

    otp = request.form.get("mobile_otp", "").strip()
    success, message = verify_mobile(user['mobile'], otp)

    flash(message, 'success' if success else 'error')
    return redirect(url_for('verify_page'))


@app.route("/verify/resend-otp", methods=["POST"])
@login_required
def resend_otp_post():
    """Resend OTP."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute("SELECT email FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()

    success, message = resend_otp(user['email'])
    flash(message, 'success' if success else 'error')
    return redirect(url_for('verify_page'))


@app.route("/logout")
def logout():
    """Logout user or admin."""
    session.clear()
    flash("আপুনি লগআউট কৰিছে।", 'info')
    return redirect(url_for('login_page'))


# ═══════════════════════════════════════════
#  USER DASHBOARD & KUNDLI
# ═══════════════════════════════════════════

@app.route("/dashboard")
@login_required
def user_dashboard():
    """User dashboard showing available features."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    user = conn.execute('''
        SELECT u.*, s.name_asm as subscription_name
        FROM users u
        LEFT JOIN subscriptions s ON u.subscription_id = s.id
        WHERE u.id = ?
    ''', (session['user_id'],)).fetchone()

    if not user:
        session.clear()
        flash("ব্যৱহাৰকাৰী পোৱা নগল।", 'error')
        return redirect(url_for('login_page'))

    user_features = get_user_features(session['user_id'])
    feature_defs = get_all_feature_definitions()
    subscription = dict(user)

    conn.close()

    feature_icons = {
        "kundli_calculate": "🔮", "varga_charts": "📊", "panchanga": "🕉️",
        "dosha_analysis": "⚠️", "yoga_analysis": "✨", "dasha": "⏳",
        "ai_interpretation": "🤖", "pdf_report": "📄", "nakshatra_phala": "⭐",
        "lagna_phala": "🌅", "rashi_phala": "♈", "sannari_chakra": "🔄",
        "navatara_chakra": "🌐", "tripap_rista": "⚡", "custom_pdf": "📑"
    }

    return render_template("user_dashboard.html",
                           user=dict(user), subscription=subscription,
                           user_features=user_features, feature_defs=feature_defs,
                           feature_icons=feature_icons)


@app.route("/kundli")
@login_required
def kundli_page():
    """Kundli calculation page (requires kundli_calculate feature)."""
    if not check_feature_access(session['user_id'], 'kundli_calculate'):
        return render_template('feature_locked.html', feature='kundli_calculate'), 403

    conn = sqlite3.connect(DB_PATH)
    places = []
    cursor = conn.cursor()
    cursor.execute("SELECT place_name, latitude, longitude FROM locations ORDER BY place_name")
    places = [{"name": row[0], "lat": row[1], "lon": row[2]} for row in cursor.fetchall()]
    conn.close()

    timezones = get_all_timezones()
    user_features = get_user_features(session['user_id'])
    feature_defs = get_all_feature_definitions()

    return render_template("index.html", places=places, timezones=timezones,
                           user_features=user_features, feature_defs=feature_defs)


# ═══════════════════════════════════════════
#  ADMIN ROUTES
# ═══════════════════════════════════════════

@app.route("/admin/login")
def admin_login_page():
    """Admin login page."""
    if 'admin_id' in session:
        return redirect(url_for('admin_panel'))
    return render_template("admin_login.html")


@app.route("/admin/login", methods=["POST"])
def admin_login_post():
    """Handle admin login."""
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    ip = request.remote_addr

    success, message, admin_data = login_admin(username, password, ip)

    if success:
        session['admin_id'] = admin_data['id']
        session['admin_username'] = admin_data['username']
        flash(message, 'success')
        return redirect(url_for('admin_panel'))
    else:
        flash(message, 'error')
        return redirect(url_for('admin_login_page'))


@app.route("/admin/logout")
def admin_logout():
    """Admin logout."""
    session.clear()
    flash("এডমিন লগআউট সফল।", 'info')
    return redirect(url_for('admin_login_page'))


@app.route("/admin")
@admin_required
def admin_panel():
    """Admin panel dashboard."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Stats
    total_users = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
    active_users = conn.execute("SELECT COUNT(*) as c FROM users WHERE is_active = 1").fetchone()['c']
    pending_users = conn.execute("SELECT COUNT(*) as c FROM users WHERE is_active = 0").fetchone()['c']
    total_subs = conn.execute("SELECT COUNT(*) as c FROM subscriptions WHERE is_active = 1").fetchone()['c']

    # Recent users
    recent_users = conn.execute('''
        SELECT u.*, s.name_asm as subscription_name
        FROM users u LEFT JOIN subscriptions s ON u.subscription_id = s.id
        ORDER BY u.created_at DESC LIMIT 10
    ''').fetchall()

    # All users
    all_users = conn.execute('''
        SELECT u.*, s.name_asm as subscription_name
        FROM users u LEFT JOIN subscriptions s ON u.subscription_id = s.id
        ORDER BY u.created_at DESC
    ''').fetchall()

    # Subscriptions
    subscriptions = conn.execute("SELECT * FROM subscriptions WHERE is_active = 1 ORDER BY id").fetchall()

    # Feature counts per subscription
    sub_feature_counts = {}
    for sub in subscriptions:
        count = conn.execute(
            "SELECT COUNT(*) as c FROM subscription_features WHERE subscription_id = ? AND enabled = 1",
            (sub['id'],)
        ).fetchone()['c']
        sub_feature_counts[sub['id']] = count

    # Feature definitions
    feature_defs = conn.execute(
        "SELECT * FROM feature_definitions ORDER BY display_order"
    ).fetchall()

    conn.close()

    from auth_module import get_admin_setting
    user_auto_activate = get_admin_setting("user_auto_activate", "admin_approval")

    return render_template("admin_panel.html",
                           admin_username=session.get('admin_username', 'Admin'),
                           total_users=total_users, active_users=active_users,
                           pending_users=pending_users, total_subs=total_subs,
                           recent_users=[dict(u) for u in recent_users],
                           all_users=[dict(u) for u in all_users],
                           subscriptions=[dict(s) for s in subscriptions],
                           sub_feature_counts=sub_feature_counts,
                           feature_defs=[dict(f) for f in feature_defs],
                           user_auto_activate=user_auto_activate)


# ─── Admin API endpoints ───

@app.route("/admin/api/user/<int:user_id>")
@admin_required
def admin_api_get_user(user_id):
    """API: Get user details with features and overrides."""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "ব্যৱহাৰকাৰী পোৱা নগল"}), 404

    features = get_all_feature_definitions()
    overrides = get_user_feature_overrides(user_id)
    subscriptions = get_all_subscriptions()

    # Get subscription features
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    sub_features = conn.execute(
        "SELECT feature_key FROM subscription_features WHERE subscription_id = ? AND enabled = 1",
        (user['subscription_id'],)
    ).fetchall()
    conn.close()

    return jsonify({
        "user": user,
        "features": features,
        "overrides": overrides,
        "subscriptions": subscriptions,
        "sub_features": [f['feature_key'] for f in sub_features]
    })


@app.route("/admin/api/user/<int:user_id>/toggle-active", methods=["POST"])
@admin_required
def admin_api_toggle_active(user_id):
    """API: Toggle user active status."""
    data = request.get_json()
    is_active = data.get("is_active", 0)
    success, message = admin_toggle_user_active(user_id, is_active)
    return jsonify({"success": success, "message": message})


@app.route("/admin/api/user/<int:user_id>/subscription", methods=["POST"])
@admin_required
def admin_api_set_subscription(user_id):
    """API: Set user subscription."""
    data = request.get_json()
    sub_id = data.get("subscription_id", 1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    sub = conn.execute("SELECT duration_days FROM subscriptions WHERE id = ?", (sub_id,)).fetchone()
    conn.close()

    duration = sub['duration_days'] if sub else None
    success, message = admin_set_user_subscription(user_id, sub_id, duration)
    return jsonify({"success": success, "message": message})


@app.route("/admin/api/user/<int:user_id>/feature", methods=["POST"])
@admin_required
def admin_api_toggle_feature(user_id):
    """API: Toggle feature for a user."""
    data = request.get_json()
    feature_key = data.get("feature_key", "")
    enabled = data.get("enabled", True)
    success, message = admin_toggle_user_feature(user_id, feature_key, enabled)
    return jsonify({"success": success, "message": message})


@app.route("/admin/api/user/<int:user_id>/feature/reset", methods=["POST"])
@admin_required
def admin_api_reset_feature(user_id):
    """API: Reset feature override for a user."""
    data = request.get_json()
    feature_key = data.get("feature_key", "")
    success, message = admin_remove_user_feature_override(user_id, feature_key)
    return jsonify({"success": success, "message": message})


# ─── Admin: Global Settings API ───

@app.route("/admin/api/settings", methods=["GET"])
@admin_required
def admin_api_get_settings():
    """API: Get all admin settings."""
    from auth_module import get_admin_setting
    return jsonify({
        "user_auto_activate": get_admin_setting("user_auto_activate", "admin_approval")
    })


@app.route("/admin/api/settings", methods=["POST"])
@admin_required
def admin_api_set_settings():
    """API: Update an admin setting."""
    from auth_module import set_admin_setting
    data = request.get_json()
    key = data.get("key", "")
    value = data.get("value", "")
    if not key:
        return jsonify({"success": False, "message": "Setting key required."}), 400
    success = set_admin_setting(key, value)
    return jsonify({"success": success, "message": "ছেটিং আপডেট কৰা হৈছে।" if success else "ছেটিং আপডেট বিফল।"})


# ─── Admin: Image Management APIs ───

@app.route("/admin/api/images", methods=["GET"])
@admin_required
def admin_api_get_images():
    """API: Get all admin images."""
    images = get_all_images()
    # Remove image_data from response (too large), just send metadata
    for img in images:
        img.pop('image_data', None)
    return jsonify(images)


@app.route("/admin/api/images/upload", methods=["POST"])
@admin_required
def admin_api_upload_image():
    """API: Upload a new image."""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "কোনো ফাইল পোৱা নগল।"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "ফাইল নিৰ্বাচন কৰা হোৱা নাই।"}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "অনুমোদিত ফাইল ধৰণ নহয়। PNG, JPG, GIF, WEBP, SVG ব্যৱহাৰ কৰক।"}), 400

    placement = request.form.get("placement", "general")
    page_target = request.form.get("page_target", "all")
    image_key = request.form.get("image_key", "").strip()
    alt_text = request.form.get("alt_text", "").strip()
    width = int(request.form.get("width", 200))
    height = int(request.form.get("height", 200))

    if not image_key:
        image_key = f"img_{datetime.now().strftime('%Y%m%d%H%M%S')}_{placement}"

    filename = secure_filename(file.filename)
    mime_type = file.content_type or 'image/png'
    image_data = file.read()

    # Also save to disk for direct serving
    file.seek(0)
    file.save(os.path.join(UPLOAD_FOLDER, filename))

    success = save_image_to_db(image_key, placement, page_target, filename, mime_type, width, height, alt_text, image_data)
    return jsonify({"success": success, "message": "ফটো আপলোড সফল হৈছে।" if success else "ফটো আপলোড বিফল।"})


@app.route("/admin/api/images/<int:image_id>", methods=["PUT"])
@admin_required
def admin_api_update_image(image_id):
    """API: Update image dimensions or metadata."""
    data = request.get_json()
    width = data.get("width")
    height = data.get("height")
    alt_text = data.get("alt_text")
    placement = data.get("placement")

    conn = sqlite3.connect(DB_PATH)
    try:
        if width is not None and height is not None:
            conn.execute(
                "UPDATE admin_images SET width=?, height=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (int(width), int(height), image_id)
            )
        if alt_text is not None:
            conn.execute(
                "UPDATE admin_images SET alt_text=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (alt_text, image_id)
            )
        if placement is not None:
            conn.execute(
                "UPDATE admin_images SET placement=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (placement, image_id)
            )
        conn.commit()
        return jsonify({"success": True, "message": "ফটো আপডেট কৰা হৈছে।"})
    finally:
        conn.close()


@app.route("/admin/api/images/<int:image_id>", methods=["DELETE"])
@admin_required
def admin_api_delete_image(image_id):
    """API: Delete an image."""
    success = delete_image_from_db(image_id)
    return jsonify({"success": success, "message": "ফটো বিলোপ কৰা হৈছে।" if success else "বিলোপ বিফল।"})


@app.route("/api/images/<int:image_id>")
def api_serve_image(image_id):
    """Serve an image by ID."""
    img = get_image_data(image_id)
    if img and img.get('image_data'):
        return send_file(
            io.BytesIO(img['image_data']),
            mimetype=img.get('mime_type', 'image/png')
        )
    return jsonify({"error": "Image not found"}), 404


@app.route("/api/images/placement/<placement>")
def api_images_by_placement(placement):
    """Get images metadata for a placement."""
    images = get_images_by_placement(placement)
    return jsonify(images)


# ─── Admin: Subscription Plan Management APIs ───

@app.route("/admin/api/subscription/<int:sub_id>", methods=["GET"])
@admin_required
def admin_api_get_subscription(sub_id):
    """API: Get subscription details with features."""
    sub = get_subscription_by_id(sub_id)
    if not sub:
        return jsonify({"error": "চাবস্ক্ৰিপশ্যন পোৱা নগল"}), 404

    features = get_all_feature_definitions()
    sub_features = get_subscription_features(sub_id)
    sub_feature_keys = {f['feature_key']: f['enabled'] for f in sub_features}

    return jsonify({
        "subscription": sub,
        "features": features,
        "sub_feature_keys": sub_feature_keys
    })


@app.route("/admin/api/subscription/<int:sub_id>/update", methods=["POST"])
@admin_required
def admin_api_update_subscription(sub_id):
    """API: Update subscription plan details."""
    data = request.get_json()
    name = data.get("name", "")
    name_asm = data.get("name_asm", "")
    price = float(data.get("price", 0))
    duration_days = int(data.get("duration_days", 30))
    description = data.get("description", "")

    success, message = admin_update_subscription(sub_id, name, name_asm, price, duration_days, description)
    return jsonify({"success": success, "message": message})


@app.route("/admin/api/subscription/<int:sub_id>/feature", methods=["POST"])
@admin_required
def admin_api_toggle_sub_feature(sub_id):
    """API: Toggle feature for a subscription plan."""
    data = request.get_json()
    feature_key = data.get("feature_key", "")
    enabled = data.get("enabled", True)
    success, message = admin_toggle_subscription_feature(sub_id, feature_key, enabled)
    return jsonify({"success": success, "message": message})


# ═══════════════════════════════════════════
#  SAVED KUNDLIS ROUTES (Save & Search)
# ═══════════════════════════════════════════

@app.route("/api/save-kundli", methods=["POST"])
def api_save_kundli():
    """Save a kundli entry for the logged-in user."""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "প্ৰথমে লগইন কৰক।"}), 401

    user_id = session['user_id']
    name = request.form.get("name", "").strip()
    dob = request.form.get("dob", "").strip()
    tob = request.form.get("tob", "").strip()
    place = request.form.get("place", "").strip()
    gender = request.form.get("gender", "male")
    lat_str = request.form.get("lat", "")
    lon_str = request.form.get("lon", "")
    tz_str = request.form.get("timezone", "5.5")

    try:
        lat = float(lat_str) if lat_str else 26.1445
        lon = float(lon_str) if lon_str else 91.7362
        tz = float(tz_str) if tz_str else 5.5
    except (ValueError, TypeError):
        lat, lon, tz = 26.1445, 91.7362, 5.5

    if not name or not dob or not tob:
        return jsonify({"success": False, "message": "নাম, জন্ম তাৰিখ আৰু সময় আৱশ্যক।"}), 400

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute('''
            INSERT INTO saved_kundlis (user_id, name, dob, tob, place, gender, lat, lon, timezone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, dob, tob, place, gender, lat, lon, tz))
        conn.commit()
        return jsonify({"success": True, "message": "কুণ্ডলী সংৰক্ষণ সফল হৈছে।"})
    except Exception as e:
        return jsonify({"success": False, "message": f"সংৰক্ষণ বিফল: {str(e)}"}), 500
    finally:
        conn.close()


@app.route("/api/search-kundlis")
def api_search_kundlis():
    """Search saved kundlis by name for the logged-in user."""
    if 'user_id' not in session:
        return jsonify([])

    user_id = session['user_id']
    q = request.args.get("q", "").strip()
    if len(q) < 1:
        return jsonify([])

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT id, name, dob, tob, place, gender, lat, lon, timezone FROM saved_kundlis WHERE user_id = ? AND name LIKE ? ORDER BY created_at DESC LIMIT 10",
            (user_id, f"%{q}%")
        ).fetchall()
        results = [dict(r) for r in rows]
        return jsonify(results)
    finally:
        conn.close()


@app.route("/api/get-kundli/<int:kundli_id>")
def api_get_kundli(kundli_id):
    """Get a specific saved kundli by ID."""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT id, name, dob, tob, place, gender, lat, lon, timezone FROM saved_kundlis WHERE id = ? AND user_id = ?",
            (kundli_id, session['user_id'])
        ).fetchone()
        if row:
            return jsonify(dict(row))
        return jsonify({"error": "Not found"}), 404
    finally:
        conn.close()


@app.route("/api/delete-kundli/<int:kundli_id>", methods=["DELETE"])
def api_delete_kundli(kundli_id):
    """Delete a saved kundli."""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("DELETE FROM saved_kundlis WHERE id = ? AND user_id = ?", (kundli_id, session['user_id']))
        conn.commit()
        return jsonify({"success": True, "message": "কুণ্ডলী বিলোপ কৰা হৈছে।"})
    finally:
        conn.close()


# ─── Chat Routes ─────────────────────────────────────────────────

@app.route("/api/calculate-kundli", methods=["POST"])
def api_calculate_kundli():
    """Calculate kundli data and return as JSON for the chat feature."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request"}), 400

    name = data.get("name", "")
    dob = data.get("dob", "")
    tob = data.get("tob", "")
    place = data.get("place", "")
    gender = data.get("gender", "male")
    lat = float(data.get("lat", 26.1445))
    lon = float(data.get("lon", 91.7362))
    tz_offset = float(data.get("timezone", 5.5))

    try:
        ist_time = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
        jd = swe.julday(ist_time.year, ist_time.month, ist_time.day,
                        (ist_time.hour + ist_time.minute / 60.0) - tz_offset)

        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa(jd)

        planets_dict = {
            "ৰবি": swe.SUN, "চন্দ্ৰ": swe.MOON, "মংগল": swe.MARS,
            "বুধ": swe.MERCURY, "বৃহস্পতি": swe.JUPITER, "শুক্ৰ": swe.VENUS,
            "শনি": swe.SATURN, "ৰাহু": swe.MEAN_NODE
        }

        planets_data = []
        p_sidereal_longitudes = {}
        planet_signs = {}
        planet_houses = {}

        for p_name, p_id in planets_dict.items():
            pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            p_sidereal_longitudes[p_name] = pos[0]
            r_idx, rasi, deg = get_rasi_and_degree(pos[0])
            _, nak, lord = get_nakshatra_details(pos[0])
            planets_data.append({"name": p_name, "rasi": rasi, "degree": deg,
                                 "nakshatra": nak, "lord": lord})
            planet_signs[p_name] = r_idx

        p_sidereal_longitudes["কেতু"] = (p_sidereal_longitudes["ৰাহু"] + 180) % 360
        r_idx_k, ketu_rasi, ketu_deg = get_rasi_and_degree(p_sidereal_longitudes["কেতু"])
        _, ketu_nak, ketu_lord = get_nakshatra_details(p_sidereal_longitudes["কেতু"])
        planets_data.append({"name": "কেতু", "rasi": ketu_rasi, "degree": ketu_deg,
                             "nakshatra": ketu_nak, "lord": ketu_lord})
        planet_signs["কেতু"] = r_idx_k

        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        asc_sidereal = (ascmc[0] - ayanamsa) % 360
        p_sidereal_longitudes["লগ্ন"] = asc_sidereal
        asc_rasi_idx, asc_rasi, asc_deg = get_rasi_and_degree(asc_sidereal)
        _, asc_nak, asc_nak_lord = get_nakshatra_details(asc_sidereal)
        planets_data.append({"name": "লগ্ন", "rasi": asc_rasi, "degree": asc_deg,
                             "nakshatra": asc_nak, "lord": asc_nak_lord})
        planet_signs["লগ্ন"] = asc_rasi_idx

        for p_name, p_lon in p_sidereal_longitudes.items():
            house_idx = (int(p_lon / 30) - asc_rasi_idx) % 12
            planet_houses[p_name] = house_idx

        moon_nak_idx = get_nakshatra_details(p_sidereal_longitudes["চন্দ্ৰ"])[0] + 1
        moon_rasi_idx = get_rasi_and_degree(p_sidereal_longitudes["চন্দ্ৰ"])[0]

        dasa_hierarchy = get_full_dasa_hierarchy(p_sidereal_longitudes["চন্দ্ৰ"], ist_time)
        dosha_results = get_complete_dosha_analysis(planet_houses, p_sidereal_longitudes)

        lagna_lord = get_rashi_lord(asc_rasi_idx)
        moon_rashi_lord = get_rashi_lord(moon_rasi_idx)

        return jsonify({
            "success": True,
            "planets": planets_data,
            "planet_houses": planet_houses,
            "planet_signs": planet_signs,
            "asc_rasi": asc_rasi,
            "asc_rasi_idx": asc_rasi_idx,
            "moon_nak_name": nakshatras[moon_nak_idx - 1],
            "moon_rasi": rasis[moon_rasi_idx],
            "dosha_results": dosha_results,
            "dasa_data": dasa_hierarchy,
            "lagna_lord": lagna_lord,
            "moon_rashi_lord": moon_rashi_lord
        })
    except Exception as e:
        logger.error(f"API kundli calc error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/chat", methods=["GET"])
def chat_page():
    """Render the AI chat page."""
    # Get user's saved kundli data if logged in
    kundli_data = None
    if session.get('user_id'):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM saved_kundlis WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (session['user_id'],)
        ).fetchone()
        conn.close()
        if row:
            kundli_data = dict(row)

    return render_template("chat.html",
                           predefined_questions=PREDEFINED_QUESTIONS,
                           kundli_data=kundli_data,
                           user_features=get_user_features(session.get('user_id', 0)))


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Handle AI chat requests with kundli context."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request"}), 400

    question = data.get("question", "")
    name = data.get("name", "গ্ৰাহক")
    gender = data.get("gender", "male")

    # Get kundli data from request
    planets_data = data.get("planets", [])
    planet_houses = data.get("planet_houses", {})
    planet_signs = data.get("planet_signs", {})
    asc_rasi = data.get("asc_rasi", "")
    asc_rasi_idx = data.get("asc_rasi_idx", 0)
    moon_nak_name = data.get("moon_nak_name", "")
    moon_rasi = data.get("moon_rasi", "")
    dosha_results = data.get("dosha_results", [])
    dasa_data = data.get("dasa_data", [])
    lagna_lord = data.get("lagna_lord", "")
    moon_rashi_lord = data.get("moon_rashi_lord", "")

    if not question:
        return jsonify({"success": False, "message": "প্ৰশ্ন খালী"}), 400

    try:
        response = chat_with_ai(
            user_name=name,
            question=question,
            planets_data=planets_data,
            planet_houses=planet_houses,
            planet_signs=planet_signs,
            asc_rasi=asc_rasi,
            asc_rasi_idx=asc_rasi_idx,
            moon_nak_name=moon_nak_name,
            moon_rasi=moon_rasi,
            dosha_results=dosha_results,
            dasa_data=dasa_data,
            lagna_lord=lagna_lord,
            moon_rashi_lord=moon_rashi_lord,
            gender=gender
        )
        return jsonify({"success": True, "response": response})
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"success": False, "message": f"ত্ৰুটি: {str(e)}"}), 500


# ═══════════════════════════════════════════
#  ASTROLOGER PROFILE ROUTES (Admin manages per-user astrologer details)
# ═══════════════════════════════════════════

def get_astrologer_profile(user_id: int) -> dict:
    """Get astrologer profile for a user. Falls back to admin (user_id=0) if not set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM astrologer_profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
        if row:
            return dict(row)
        # Fallback to admin profile (user_id=0)
        row = conn.execute(
            "SELECT * FROM astrologer_profiles WHERE user_id = 0"
        ).fetchone()
        return dict(row) if row else {}
    finally:
        conn.close()


def save_astrologer_profile(user_id: int, data: dict) -> tuple:
    """Save or update astrologer profile for a user. Returns (success, message)."""
    conn = sqlite3.connect(DB_PATH)
    try:
        existing = conn.execute(
            "SELECT id FROM astrologer_profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
        if existing:
            conn.execute('''
                UPDATE astrologer_profiles
                SET institution_name=?, astrologer_name=?, astrologer_bio=?,
                    address=?, mobile=?, updated_at=CURRENT_TIMESTAMP
                WHERE user_id=?
            ''', (
                data.get('institution_name', ''),
                data.get('astrologer_name', ''),
                data.get('astrologer_bio', ''),
                data.get('address', ''),
                data.get('mobile', ''),
                user_id
            ))
        else:
            conn.execute('''
                INSERT INTO astrologer_profiles (user_id, institution_name, astrologer_name, astrologer_bio, address, mobile)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data.get('institution_name', ''),
                data.get('astrologer_name', ''),
                data.get('astrologer_bio', ''),
                data.get('address', ''),
                data.get('mobile', '')
            ))
        conn.commit()
        return True, "জ্যোতিষীৰ বিৱৰণ সফলভাৱে ছেভ কৰা হ'ল।"
    except Exception as e:
        return False, f"ছেভ কৰাত বিফল: {str(e)}"
    finally:
        conn.close()


@app.route("/admin/api/astrologer-profile/<int:user_id>", methods=["GET"])
@admin_required
def admin_api_get_astrologer_profile(user_id):
    """API: Get astrologer profile for a user."""
    profile = get_astrologer_profile(user_id)
    return jsonify({"success": True, "profile": profile})


@app.route("/admin/api/astrologer-profile/<int:user_id>", methods=["POST"])
@admin_required
def admin_api_save_astrologer_profile(user_id):
    """API: Save astrologer profile for a user."""
    data = request.get_json()
    success, message = save_astrologer_profile(user_id, data)
    return jsonify({"success": success, "message": message})


@app.route("/admin/api/astrologer-profile/admin", methods=["GET"])
@admin_required
def admin_api_get_admin_astrologer_profile():
    """API: Get admin's own astrologer profile (user_id=0)."""
    profile = get_astrologer_profile(0)
    return jsonify({"success": True, "profile": profile})


@app.route("/admin/api/astrologer-profile/admin", methods=["POST"])
@admin_required
def admin_api_save_admin_astrologer_profile():
    """API: Save admin's own astrologer profile (user_id=0)."""
    data = request.get_json()
    success, message = save_astrologer_profile(0, data)
    return jsonify({"success": success, "message": message})


# ═══════════════════════════════════════════════════════════════════════════════
# Matplotlib Kundli Chart Image Routes
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/chart-image", methods=["GET"])
def api_chart_image():
    """
    Generate a Kundli chart image using matplotlib.
    Query params:
        style: "bengali" (default), "north", "south", or "all"
        asc: ascendant rasi index (0-11, default 0)
        varga: which varga chart to use (default "D1")
        name, dob, tob, place, gender, lat, lon, timezone: for full calculation
    """
    style = request.args.get("style", "bengali")
    asc_str = request.args.get("asc", "0")
    
    try:
        ascendant_index = int(asc_str) % 12
    except (ValueError, TypeError):
        ascendant_index = 0
    
    # If full birth data is provided, calculate planet positions
    name = request.args.get("name", "")
    dob = request.args.get("dob", "")
    tob = request.args.get("tob", "")
    place = request.args.get("place", "")
    varga_code = request.args.get("varga", "D1")
    
    planet_data = {}
    title = ""
    
    if dob and tob:
        try:
            lat_str = request.args.get("lat", "")
            lon_str = request.args.get("lon", "")
            tz_str = request.args.get("timezone", "5.5")
            
            lat = float(lat_str) if lat_str else None
            lon = float(lon_str) if lon_str else None
            
            if (lat is None or lon is None) and place:
                coords = get_coordinates(place)
                if coords:
                    lat, lon = coords
                else:
                    lat, lon = 26.1445, 91.7362
            
            tz_offset = float(tz_str) if tz_str else 5.5
            
            ist_time = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
            jd = swe.julday(ist_time.year, ist_time.month, ist_time.day,
                            (ist_time.hour + ist_time.minute / 60.0) - tz_offset)
            
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            ayanamsa = swe.get_ayanamsa(jd)
            
            planets_dict = {
                "ৰবি": swe.SUN, "চন্দ্ৰ": swe.MOON, "মংগল": swe.MARS,
                "বুধ": swe.MERCURY, "বৃহস্পতি": swe.JUPITER, "শুক্ৰ": swe.VENUS,
                "শনি": swe.SATURN, "ৰাহু": swe.MEAN_NODE
            }
            
            p_sidereal_longitudes = {}
            for p_name, p_id in planets_dict.items():
                pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
                p_sidereal_longitudes[p_name] = pos[0]
            p_sidereal_longitudes["কেতু"] = (p_sidereal_longitudes["ৰাহু"] + 180) % 360
            
            # Lagna
            cusps, ascmc = swe.houses(jd, lat, lon, b'P')
            asc_sidereal = (ascmc[0] - ayanamsa) % 360
            p_sidereal_longitudes["লগ্ন"] = asc_sidereal
            ascendant_index = int(asc_sidereal / 30) % 12
            
            # Calculate varga
            varga_num = int(varga_code[1:]) if varga_code.startswith("D") else 1
            for p_key, p_lon in p_sidereal_longitudes.items():
                v_idx = calculate_varga(p_lon, varga_num)
                if v_idx not in planet_data:
                    planet_data[v_idx] = []
                planet_data[v_idx].append(PLANET_SHORT.get(p_key, p_key[:2]))
            
            if name:
                title = f"{name}ৰ কুণ্ডলী ({varga_code})"
            else:
                title = f"কুণ্ডলী চক্ৰ ({varga_code})"
        except Exception as e:
            logger.error(f"Chart image calculation error: {e}")
            # Fall back to empty chart
            title = f"কুণ্ডলী চক্ৰ ({varga_code})"
    
    try:
        if style == "all":
            buf = draw_all_styles(ascendant_index=ascendant_index, planet_data=planet_data)
        else:
            buf = draw_kundli_chart(
                style=style,
                ascendant_index=ascendant_index,
                planet_data=planet_data,
                title=title
            )
        return send_file(buf, mimetype="image/png")
    except Exception as e:
        logger.error(f"Chart drawing error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
