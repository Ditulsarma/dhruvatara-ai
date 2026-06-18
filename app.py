"""
ধ্ৰুৱতৰা AI - মূল এপ্লিকেচন
Dhruvatara AI: Professional Assamese Vedic Astrology Platform
Powered by DhrubataraAi for high-precision calculations.
With Subscription-based User & Admin Panel.
"""

from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, session, flash, g
import sqlite3
import swisseph as swe
from datetime import datetime, timedelta
import io
import os
import json
import base64
from functools import wraps
from werkzeug.utils import secure_filename
from config import DB_PATH

# ─── Multi-language support ───
from translations import get_text, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
from lang_utils import (
    detect_language, set_language, get_current_language,
    init_language_for_request, register_template_helpers
)
from prediction_i18n import (
    get_lagna_phala_i18n, get_lagna_phala_html_i18n,
    get_rashi_phala_i18n, get_rashi_phala_html_i18n,
    get_nakshatra_phala_i18n, get_nakshatra_phala_html_i18n,
    get_antardasha_phala_i18n, get_important_antardasha_phala_i18n,
    get_planet_name_i18n, get_rashi_name_i18n, get_house_name_i18n,
    get_nakshatra_name_i18n, get_kundli_rashi_name_i18n,
    get_karakattwa_i18n, get_sade_sati_phase_name_i18n,
    get_dwadash_html_i18n, get_graha_bichar_html_i18n,
    translate_dosha_result, translate_yoga_result,
    get_dosha_labels, get_yoga_labels,
    get_shani_sare_sati_labels, translate_shani_sare_sati_data,
)
from shani_sare_sati_i18n import get_shani_sare_sati_analysis_html
from dasha_i18n import localize_dasha_hierarchy
from yoga_labels_data import YOGA_LABELS
# Inject YOGA_LABELS into prediction_i18n module namespace
import prediction_i18n
prediction_i18n.YOGA_LABELS = YOGA_LABELS

from panchanga import get_full_panchanga, get_rashi_lord
from panchanga_data import get_panchanga_with_times, get_all_planet_positions
from dosha_engine import get_complete_dosha_analysis
from yoga_engine import get_complete_yoga_analysis
from ai_engine import generate_ai_interpretation
from ai_engine_i18n import generate_ai_interpretation_i18n
from pdf_generator import generate_pdf_report, get_shani_sare_sati_data
from chat_engine import chat_with_ai, PREDEFINED_QUESTIONS
from rashifal_engine import generate_rashifal, RASHI_NAMES as RASHIFAL_RASHI_NAMES
from tripap_rista import get_tripap_rista, analyze_tripap_rista, TRIPAP_AGES
from dasha_engine import (
    get_full_dasha_prediction, get_all_maha_antar_predictions,
    get_eng_planet, get_asm_planet, get_planet_details, convert_planet_degrees_to_en,
    get_planet_state
)
from sannari_chakra import get_sannari_data, generate_sannari_svg, generate_sannari_html_table
from navatara_chakra import get_navatara_data, generate_navatara_html, generate_navatara_svg
from nakshatra_phala import get_nakshatra_phala, get_nakshatra_phala_html
from lagna_phala import get_lagna_phala, get_lagna_phala_html
from rashi_phala import get_rashi_phala, get_rashi_phala_html
from graha_bichar import get_all_graha_bichar, get_graha_bichar_html
from kundli_chart import draw_kundli_chart, draw_all_styles
from patrika import generate_patrika_text
from kartari_dosha import generate_kartari_report
from graha_maitri import get_all_maitri_data, build_graha_maitri_pdf_html
from ratna_engine import get_ratna_data, build_ratna_html
from jotok_milan_engine import get_complete_jotok_milan, get_koota_name_asm, get_koota_icon
from jotok_milan_pdf import generate_jotok_milan_pdf
from small_antardasaphal import get_antardasha_phala, get_all_antardasha_phala_for_pdf
from importantantardasa import get_important_antardasha_phala
from dwadash_bhab_phala import get_dwadash_html, get_dwadash_text, get_dwadash_json, get_dwadash_phala
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

# ─── Activity Tracking imports ───
from activity_tracker import (
    log_page_visit, log_feature_usage, log_rashifal_usage,
    get_user_rashifal_usage_today, get_user_rashifal_used_rashis_today,
    get_admin_dashboard_stats, get_user_activity_detail,
    get_all_users_activity_summary, get_special_topic_usage,
    start_user_session, end_user_session, end_all_user_sessions,
    can_free_user_login, get_today_session_count
)

# ─── Numerology imports ───
from numerology_engine import get_full_numerology_report
from numerology_pdf import generate_numerology_pdf
from numerology_chat import chat_numerology, NUMEROLOGY_QUESTIONS

# ─── Helper: Get user subscription badge info ───
def get_user_sub_info(user_id=None):
    """Get subscription name and is_pro flag for displaying Free/Pro badge."""
    if user_id is None:
        user_id = session.get('user_id', 0)
    if not user_id:
        return {'name_asm': 'অতিথি', 'is_pro': False, 'id': 0}
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT s.name_asm, s.id FROM users u JOIN subscriptions s ON u.subscription_id = s.id WHERE u.id = ?",
            (user_id,)
        ).fetchone()
        if row:
            return {'name_asm': row['name_asm'], 'is_pro': row['id'] > 1, 'id': row['id']}
        return {'name_asm': 'বিনামূলীয়া', 'is_pro': False, 'id': 1}
    finally:
        conn.close()

app = Flask(__name__)
app.secret_key = 'DhruvataraAI_2026_Secure_Secret_Key_8x7k9m2p'

# ─── Show actual errors in browser (for debugging) ───
app.config['PROPAGATE_EXCEPTIONS'] = True

# ─── Multi-language: Register template helpers ───
register_template_helpers(app)

# ─── Multi-language: Before request - detect/set language ───
@app.before_request
def before_request_language():
    """Detect and set language before each request."""
    # Check for language switch via query param
    lang_param = request.args.get('lang', None)
    if lang_param and lang_param in SUPPORTED_LANGUAGES:
        set_language(lang_param)
    # Initialize language for this request
    init_language_for_request()

# ─── Language switcher route ───
@app.route("/set-language/<lang>")
def set_language_route(lang):
    """Set language and redirect back."""
    if set_language(lang):
        flash(get_text('lang_switched', lang), 'success')
    # Redirect to referrer or home
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect(url_for('home'))

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

# Uppercase aliases for template use
RASHIS = rasis
NAKSHATRAS = nakshatras

def get_rasis_i18n(lang='as'):
    """Get rasi names in the specified language."""
    from prediction_i18n import get_panchanga_names_i18n
    return get_panchanga_names_i18n(lang)['RASHI_NAMES']

def get_nakshatras_i18n(lang='as'):
    """Get nakshatra names in the specified language."""
    from prediction_i18n import get_panchanga_names_i18n
    return get_panchanga_names_i18n(lang)['NAKSHATRA_NAMES']

def get_dasa_lords_i18n(lang='as'):
    """Get dasa lord names in the specified language."""
    from prediction_i18n import get_panchanga_names_i18n
    pnames = get_panchanga_names_i18n(lang)
    planet_names = pnames['PLANET_NAMES']
    return [
        planet_names.get('Ketu', 'Ketu'),
        planet_names.get('Venus', 'Venus'),
        planet_names.get('Sun', 'Sun'),
        planet_names.get('Moon', 'Moon'),
        planet_names.get('Mars', 'Mars'),
        planet_names.get('Rahu', 'Rahu'),
        planet_names.get('Jupiter', 'Jupiter'),
        planet_names.get('Saturn', 'Saturn'),
        planet_names.get('Mercury', 'Mercury'),
    ]

def get_planet_short_i18n(lang='as'):
    """Get planet short codes in the specified language."""
    from prediction_i18n import get_panchanga_names_i18n
    pnames = get_panchanga_names_i18n(lang)
    planet_names = pnames['PLANET_NAMES']
    short_map = {}
    for eng_key, name in planet_names.items():
        short_map[name] = name[0] if name else eng_key[0]
    from translations import get_text
    short_map[get_text('planet_lagna', lang)] = get_text('planet_lagna_short', lang)
    return short_map

def get_planet_names_i18n(lang='as'):
    """Get planet name dict (Assamese key -> i18n name)."""
    from prediction_i18n import get_panchanga_names_i18n
    pnames = get_panchanga_names_i18n(lang)
    planet_names = pnames['PLANET_NAMES']
    return {
        "ৰবি": planet_names.get('Sun', 'Sun'),
        "চন্দ্ৰ": planet_names.get('Moon', 'Moon'),
        "মংগল": planet_names.get('Mars', 'Mars'),
        "বুধ": planet_names.get('Mercury', 'Mercury'),
        "বৃহস্পতি": planet_names.get('Jupiter', 'Jupiter'),
        "শুক্ৰ": planet_names.get('Venus', 'Venus'),
        "শনি": planet_names.get('Saturn', 'Saturn'),
        "ৰাহু": planet_names.get('Rahu', 'Rahu'),
        "কেতু": planet_names.get('Ketu', 'Ketu'),
        "লগ্ন": get_text('planet_lagna', lang),
    }

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
                          selected_maha=None, include_current_and_future_only=True, gender='male', lang=None):
    """
    Build HTML for antardasha phala filtered by mahadasha selection or current+future antardashas.
    - dasa_hierarchy: list of mahadasha dicts (with 'sub_dasas')
    - planet_degrees: mapping of planet Assamese names to sidereal degrees
    - lagna_sign_index: integer lagna index (0-11)
    - selected_maha: mahadasha lord name (Assamese) to restrict to, or None for all
    - include_current_and_future_only: if True, include only antardashas whose end >= today
    Returns HTML string.
    Supports i18n via the lang parameter; falls back to current language.
    """
    if lang is None:
        try:
            lang = get_current_language()
        except Exception:
            lang = 'as'
    today = datetime.now()
    html = '<div style="font-size:0.85rem;line-height:1.8;">'

    # Convert planet_degrees keys from Assamese to English for get_planet_details
    planet_degrees_en = convert_planet_degrees_to_en(planet_degrees)

    for md in dasa_hierarchy:
        if selected_maha and md.get('md_lord') != selected_maha:
            continue

        # Use localized display names; fall back to ASM only if display missing
        maha_name = md.get('md_lord_display') or md.get('md_lord', '')
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

            antar_lord = ad.get('ad_lord_display') or ad.get('ad_lord', '')
            antar_lord_asm = ad.get('ad_lord', '')

            # Resolve planet details to get rasi and house (use English name for lookup)
            antar_eng = get_eng_planet(antar_lord_asm)
            pd = get_planet_details(antar_eng, planet_degrees_en, lagna_sign_index)
            phala_text = ''
            if pd:
                graha_asm = pd.get('name_asm', antar_lord_asm)
                rasi = pd.get('rasi', '')
                house = pd.get('house', '')
                try:
                    phala_text = get_antardasha_phala_i18n(graha_asm, rasi, house, lang)
                except Exception:
                    phala_text = ''

            # Format HTML block (localized planet names)
            html += f'<div style="margin-bottom:12px;padding:8px 12px;background:#fff8f0;border-left:3px solid #FF6600;border-radius:4px;">'
            html += f'<strong style="color:#1a237e;">{maha_name} → {antar_lord}</strong> '
            html += f' | {ad.get("start", "") } — {ad.get("end", "") }'
            if phala_text:
                html += f'<div style="margin-top:6px;color:#333;">{apply_gender(phala_text, gender)}</div>'
            html += '</div>'

    html += '</div>'
    return html

def build_important_antardasha_html(dasa_hierarchy, gender='male', lang=None):
    """
    Build HTML for antardasha phala using the new importantantardasa.py module
    (which reads from antardasha_data.json with detailed Mahadasha-Antardasha predictions).
    Includes only current and future antardashas.
    Returns HTML string.
    Supports i18n via the lang parameter; falls back to current language.
    """
    if lang is None:
        try:
            lang = get_current_language()
        except Exception:
            lang = 'as'
    today = datetime.now()
    html = '<div style="font-size:0.85rem;line-height:1.8;">'

    for md in dasa_hierarchy:
        # Use localized display names; fall back to ASM (md_lord/ad_lord) only if display missing
        maha_name = md.get('md_lord_display') or md.get('md_lord', '')
        # For the i18n function lookup we still need ASM values (it converts internally)
        maha_name_asm = md.get('md_lord', '')
        for ad in md.get('sub_dasas', []):
            # parse dates
            try:
                ad_end = parse_dasha_date(ad.get('end', ''))
                ad_start = parse_dasha_date(ad.get('start', ''))
            except Exception:
                ad_end = datetime(1900, 1, 1)
                ad_start = datetime(1900, 1, 1)

            if ad_end < today:
                continue

            antar_lord = ad.get('ad_lord_display') or ad.get('ad_lord', '')
            antar_lord_asm = ad.get('ad_lord', '')

            # Get phala from importantantardasa.py using Assamese planet names
            try:
                phala_text = get_important_antardasha_phala_i18n(maha_name_asm, antar_lord_asm, lang)
            except Exception:
                phala_text = ''

            # Format HTML block (localized planet names)
            html += f'<div style="margin-bottom:12px;padding:8px 12px;background:#fff8f0;border-left:3px solid #FF6600;border-radius:4px;">'
            html += f'<strong style="color:#1a237e;">{maha_name} \u2192 {antar_lord}</strong> '
            html += f' | {ad.get("start", "")} \u2014 {ad.get("end", "")}'
            if phala_text:
                html += f'<div style="margin-top:6px;color:#333;">{apply_gender(phala_text, gender)}</div>'
            html += '</div>'

    html += '</div>'
    return html

def build_pratyantar_dasha_html(dasa_hierarchy, planet_degrees, lagna_sign_index, gender='male', lang=None):
    """
    Build HTML for pratyantar dasha phala (3rd level dasha).
    Shows ALL pratyantar dashas from today onward across ALL antardashas
    (not just the currently running one). Each pratyantar gets phala from small_antardasaphal.py.
    Returns HTML string.
    Supports i18n via the lang parameter; falls back to current language.
    """
    from translations import get_text as _get_text
    if lang is None:
        try:
            lang = get_current_language()
        except Exception:
            lang = 'as'
    # Localized labels
    lbl_mahadasha = _get_text('mahadasha', lang) or 'Mahadasha'
    lbl_antardasha = _get_text('antardasha', lang) or 'Antardasha'
    lbl_pratyantar = _get_text('pratyantar_dasha', lang) or 'Pratyantar Dasha'
    lbl_unavailable = _get_text('pratyantar_unavailable', lang) or ''
    lbl_no_pratyantar = _get_text('no_pratyantar', lang) or ''
    today = datetime.now()
    html = '<div style="font-size:0.85rem;line-height:1.8;">'

    # Convert planet_degrees keys from Assamese to English for get_planet_details
    planet_degrees_en = convert_planet_degrees_to_en(planet_degrees)

    for md in dasa_hierarchy:
        maha_name = md.get('md_lord_display') or md.get('md_lord', '')
        for ad in md.get('sub_dasas', []):
            # parse antardasha dates
            try:
                ad_end = parse_dasha_date(ad.get('end', ''))
                ad_start = parse_dasha_date(ad.get('start', ''))
            except Exception:
                ad_end = datetime(1900, 1, 1)
                ad_start = datetime(1900, 1, 1)

            # Skip antardashas that have already ended
            if ad_end < today:
                continue

            antar_lord = ad.get('ad_lord_display') or ad.get('ad_lord', '')

            # Header for this antardasha (localized)
            html += f'<div style="margin-bottom:16px;padding:10px 14px;background:linear-gradient(135deg,#1a237e,#283593);color:white;border-radius:6px;">'
            html += f'<strong style="font-size:1rem;">{maha_name} {lbl_mahadasha} \u2192 {antar_lord} {lbl_antardasha}</strong> '
            html += f'<span style="font-size:0.8rem;opacity:0.85;">({ad.get("start","")} \u2014 {ad.get("end","")})</span>'
            html += '</div>'

            # Now iterate pratyantar dashas within this antardasha
            pd_list = ad.get('pratyantar', [])
            if not pd_list:
                if lbl_unavailable:
                    html += f'<div style="padding:8px;color:#888;">{lbl_unavailable}</div>'
                continue

            has_any_pd = False
            for pd in pd_list:
                pd_lord = pd.get('lord_display') or pd.get('lord', '')
                pd_start = pd.get('start', '')
                pd_end = pd.get('end', '')

                # Parse pratyantar dates
                try:
                    pd_end_dt = parse_dasha_date(pd_end)
                    pd_start_dt = parse_dasha_date(pd_start)
                except Exception:
                    pd_end_dt = datetime(1900, 1, 1)
                    pd_start_dt = datetime(1900, 1, 1)

                # Only include pratyantar that ends today or later
                if pd_end_dt < today:
                    continue

                has_any_pd = True

                # Get phala for this pratyantar lord (use the English lord for planet lookup,
                # but the i18n function needs the Assamese graha name for its key conversion)
                pd_lord_eng = pd.get('lord_en') or get_eng_planet(pd.get('lord', ''))
                pd_detail = get_planet_details(pd_lord_eng, planet_degrees_en, lagna_sign_index)
                phala_text = ''
                if pd_detail:
                    graha_asm = pd_detail.get('name_asm', pd.get('lord', ''))
                    rasi = pd_detail.get('rasi', '')
                    house = pd_detail.get('house', '')
                    try:
                        phala_text = get_antardasha_phala_i18n(graha_asm, rasi, house, lang)
                    except Exception:
                        phala_text = ''

                # Format HTML block (localized)
                html += f'<div style="margin-bottom:10px;padding:8px 12px;background:#f3e5f5;border-left:3px solid #6A1B9A;border-radius:4px;">'
                html += f'<strong style="color:#6A1B9A;">\u2514 {pd_lord} {lbl_pratyantar}</strong> '
                html += f'<span style="font-size:0.8rem;color:#888;">({pd_start} \u2014 {pd_end})</span>'
                if phala_text:
                    html += f'<div style="margin-top:6px;color:#333;">{apply_gender(phala_text, gender)}</div>'
                html += '</div>'

            if not has_any_pd:
                if lbl_no_pratyantar:
                    html += f'<div style="padding:8px;color:#888;">{lbl_no_pratyantar}</div>'

    html += '</div>'
    return html

def build_vimsottari_summary(dasa_hierarchy, lang=None):
    """
    Build a complete Vimsottari Dasha Summary showing ALL 9 Mahadashas
    with their start and end dates, plus the currently running Antardasha.
    Returns a localized string for the given language.
    """
    from translations import get_text as _get_text
    if lang is None:
        try:
            lang = get_current_language()
        except Exception:
            lang = 'as'
    # Localized labels
    lbl_title = _get_text('vimsottari_summary_title', lang) or '【বিংশোত্তৰী দশা সাৰাংশ】'
    lbl_mahadasha = _get_text('mahadasha', lang) or 'মহাদশা'
    lbl_years = _get_text('vimsottari_years', lang) or 'বছৰ'
    lbl_from_to = _get_text('vimsottari_from_to', lang) or 'ৰ পৰা'
    lbl_until = _get_text('vimsottari_until', lang) or 'লৈ'
    lbl_current = _get_text('vimsottari_current', lang) or 'বৰ্তমান'
    lbl_under = _get_text('vimsottari_under', lang) or 'অন্তৰ্গত'
    lbl_antardasha = _get_text('antardasha', lang) or 'অন্তৰ্দশা'
    lbl_current_dasha = _get_text('vimsottari_current_dasha', lang) or 'বৰ্তমান চলি থকা দশা'
    lbl_unknown = _get_text('vimsottari_unknown', lang) or 'অজানা'

    if not dasa_hierarchy or len(dasa_hierarchy) == 0:
        return ""

    today = datetime.now()
    lines = []
    lines.append(lbl_title)
    lines.append("")

    current_md_lord = ""
    current_ad_lord = ""
    current_ad_start = ""
    current_ad_end = ""

    for i, md in enumerate(dasa_hierarchy):
        # Use localized display name; fall back to ASM only if display missing
        md_lord = md.get('md_lord_display') or md.get('md_lord', lbl_unknown)
        md_start = md.get('start', '')
        md_end = md.get('end', '')
        md_years = md.get('years', '')

        # Mark the currently running mahadasha
        md_start_dt = parse_dasha_date(md_start)
        md_end_dt = parse_dasha_date(md_end)
        is_current_md = (md_start_dt <= today <= md_end_dt)

        marker = f" ★ {lbl_current}" if is_current_md else ""
        # Localized format: "{i+1}. {md_lord} {lbl_mahadasha} ({md_years} {lbl_years}): {md_start} {lbl_from_to} {md_end} {lbl_until}{marker}"
        lines.append(f"{i+1}. {md_lord} {lbl_mahadasha} ({md_years} {lbl_years}): {md_start} {lbl_from_to} {md_end} {lbl_until}{marker}")

        # Find current antardasha
        if is_current_md:
            current_md_lord = md_lord
            for ad in md.get('sub_dasas', []):
                ad_start_dt = parse_dasha_date(ad.get('start', ''))
                ad_end_dt = parse_dasha_date(ad.get('end', ''))
                if ad_start_dt <= today <= ad_end_dt:
                    current_ad_lord = ad.get('ad_lord_display') or ad.get('ad_lord', '')
                    current_ad_start = ad.get('start', '')
                    current_ad_end = ad.get('end', '')
                    break

    lines.append("")
    if current_md_lord and current_ad_lord:
        # Localized: "{lbl_current_dasha}: {current_md_lord} {lbl_mahadasha} {lbl_under} {current_ad_lord} {lbl_antardasha} ({current_ad_start} {lbl_from_to} {current_ad_end} {lbl_until})।"
        lines.append(f"{lbl_current_dasha}: {current_md_lord} {lbl_mahadasha} {lbl_under} {current_ad_lord} {lbl_antardasha} ({current_ad_start} {lbl_from_to} {current_ad_end} {lbl_until})।")

    return "\n".join(lines)

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

def get_rasi_and_degree(longitude, lang=None):
    if lang is None:
        lang = get_current_language()
    rasi_index = int(longitude / 30) % 12
    rasi_names = get_rasis_i18n(lang)
    degree = longitude % 30
    return rasi_index, rasi_names[rasi_index], round(degree, 2)

def get_nakshatra_details(longitude, lang=None):
    if lang is None:
        lang = get_current_language()
    nak_index = int(longitude / 13.333333) % 27
    nak_names = get_nakshatras_i18n(lang)
    dasa_lords_i18n = get_dasa_lords_i18n(lang)
    return nak_index, nak_names[nak_index], dasa_lords_i18n[nak_index % 9]

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
    
    # English dasa lords for language-neutral matching (used by JS)
    dasa_lords_en = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    
    for i in range(9):
        idx = (current_md_idx + i) % 9
        md_lord = dasa_lords[idx]
        md_years = dasa_years[idx]
        
        md_end_date = current_date + timedelta(days=md_remaining_days if i == 0 else int(md_years * 365.25))
        md_entry = {"md_lord": md_lord, "md_lord_en": dasa_lords_en[idx], "start": fmt_date(current_date.strftime('%Y-%m-%d')), "end": fmt_date(md_end_date.strftime('%Y-%m-%d')), "years": md_years, "sub_dasas": []}
        
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
                    "lord_en": dasa_lords_en[pd_idx],
                    "start": fmt_date(pd_current_date.strftime('%Y-%m-%d')),
                    "end": fmt_date(pd_end_date.strftime('%Y-%m-%d'))
                })
                pd_current_date = pd_end_date
                
            md_entry["sub_dasas"].append({
                "ad_lord": ad_lord,
                "ad_lord_en": dasa_lords_en[ad_idx],
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
    """Default landing page - redirects to login."""
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login_page'))


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
        lang = get_current_language()
        pnames = get_planet_names_i18n(lang)

        for p_name, p_id in planets_dict.items():
            pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            p_sidereal_longitudes[p_name] = pos[0]
            p_speed = pos[3]  # longitude speed (deg/day) for retrograde detection
            r_idx, rasi, deg = get_rasi_and_degree(pos[0])
            nak_idx, nak, lord = get_nakshatra_details(pos[0])
            # Map Assamese planet name to English for i18n
            asm_to_en = {"ৰবি": "Sun", "চন্দ্ৰ": "Moon", "মংগল": "Mars", "বুধ": "Mercury",
                        "বৃহস্পতি": "Jupiter", "শুক্ৰ": "Venus", "শনি": "Saturn", "ৰাহু": "Rahu"}
            state = get_planet_state(p_name, r_idx, p_speed,
                                     p_sidereal_longitudes.get("ৰবি", 0), pos[0], lang)
            planets_data.append({"name": pnames.get(p_name, p_name), "name_asm": p_name, "name_en": asm_to_en.get(p_name, ""),
                                 "rasi": rasi, "rasi_idx": r_idx, "degree": deg,
                                 "nakshatra": nak, "nak_idx": int(pos[0] / 13.333333) % 27, "lord": lord,
                                 "state": state})
            planet_signs[p_name] = r_idx

        # Ketu
        p_sidereal_longitudes["কেতু"] = (p_sidereal_longitudes["ৰাহু"] + 180) % 360
        r_idx_k, ketu_rasi, ketu_deg = get_rasi_and_degree(p_sidereal_longitudes["কেতু"])
        ketu_idx, ketu_nak, ketu_lord = get_nakshatra_details(p_sidereal_longitudes["কেতু"])
        ketu_idx = int(p_sidereal_longitudes["কেতু"] / 13.333333) % 27
        ketu_state = get_planet_state("কেতু", r_idx_k, -1,
                                      p_sidereal_longitudes.get("ৰবি", 0), p_sidereal_longitudes["কেতু"], lang)
        planets_data.append({"name": pnames.get("কেতু", "কেতু"), "name_asm": "কেতু", "name_en": "Ketu",
                             "rasi": ketu_rasi, "rasi_idx": r_idx_k, "degree": ketu_deg,
                             "nakshatra": ketu_nak, "nak_idx": ketu_idx, "lord": ketu_lord,
                             "state": ketu_state})
        planet_signs["কেতু"] = r_idx_k

        # Lagna (Ascendant)
        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        asc_sidereal = (ascmc[0] - ayanamsa) % 360
        p_sidereal_longitudes["লগ্ন"] = asc_sidereal
        asc_rasi_idx, asc_rasi, asc_deg = get_rasi_and_degree(asc_sidereal)
        asc_nak_idx, asc_nak, asc_nak_lord = get_nakshatra_details(asc_sidereal)
        asc_nak_idx = int(asc_sidereal / 13.333333) % 27
        lagna_state = get_planet_state("লগ্ন", asc_rasi_idx, 0,
                                       p_sidereal_longitudes.get("ৰবি", 0), asc_sidereal, lang)
        planets_data.append({"name": pnames.get("লগ্ন", "লগ্ন"), "name_asm": "লগ্ন", "name_en": "Lagna",
                             "rasi": asc_rasi, "rasi_idx": asc_rasi_idx, "degree": asc_deg,
                             "nakshatra": asc_nak, "nak_idx": asc_nak_idx, "lord": asc_nak_lord,
                             "state": lagna_state})
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
        # Localize planet names in dasha hierarchy to current language
        dasa_hierarchy = localize_dasha_hierarchy(dasa_hierarchy, lang=lang)

        # Panchanga
        panchanga = get_full_panchanga(ist_time, lat, lon, tz_offset, lang=lang)

        # Dosha Analysis (i18n)
        dosha_results_raw = get_complete_dosha_analysis(planet_houses, p_sidereal_longitudes)
        dosha_results = translate_dosha_result(dosha_results_raw, lang)

        # Yoga Analysis (i18n)
        yoga_results_raw = get_complete_yoga_analysis(planet_houses, planet_signs, asc_rasi_idx)
        yoga_results = translate_yoga_result(yoga_results_raw, lang)

        # Tripap Rista Analysis (i18n)
        moon_nak_idx = get_nakshatra_details(p_sidereal_longitudes["চন্দ্ৰ"])[0] + 1  # 1-indexed
        lang = get_current_language()
        tripap_data = get_tripap_rista(moon_nak_idx, lang)
        tripap_analysis = analyze_tripap_rista(moon_nak_idx, planet_houses)

        # Sannari Chakra (i18n)
        sannari_data = get_sannari_data(moon_nak_idx, lang)
        sannari_svg = generate_sannari_svg(moon_nak_idx, nakshatras[moon_nak_idx - 1], lang=lang)

        # Navatara Chakra (i18n)
        navatara_data = get_navatara_data(moon_nak_idx, lang)
        navatara_svg = generate_navatara_svg(moon_nak_idx, lang=lang)

        # Nakshatra Phala (i18n)
        nakshatra_phala_text = apply_gender(get_nakshatra_phala_i18n(moon_nak_idx, lang), gender)

        # Lagna Phala (i18n)
        lagna_phala_text = apply_gender(get_lagna_phala_i18n(asc_rasi_idx, lang), gender)

        # Rashi Phala (Moon sign based) (i18n)
        moon_rasi_idx = get_rasi_and_degree(p_sidereal_longitudes["চন্দ্ৰ"])[0]
        rashi_phala_text = apply_gender(get_rashi_phala_i18n(moon_rasi_idx, lang), gender)

        # Lagna Lord and Moon Rashi Lord (i18n - use user's language)
        lagna_lord = get_rashi_lord(asc_rasi_idx, lang)
        moon_rashi_lord = get_rashi_lord(moon_rasi_idx, lang)

        # Graha Bichar - all planets house-wise analysis (i18n)
        graha_bichar_data = get_all_graha_bichar(planet_houses)
        graha_bichar_html = get_graha_bichar_html_i18n(planet_houses, lang)

        # AI Interpretation
        ai_interpretation = (generate_ai_interpretation_i18n if lang != 'as' else generate_ai_interpretation)(
            name, planets_data, asc_rasi, dosha_results, yoga_results, dasa_hierarchy,
            asc_rasi_idx=asc_rasi_idx,
            planet_signs=planet_signs,
            moon_nak_name=get_nakshatra_name_i18n(moon_nak_idx - 1, lang),
            moon_rasi=get_rashi_name_i18n(moon_rasi_idx, lang),
            tripap_ages=TRIPAP_AGES.get(moon_nak_idx, []),
            navatara_data=navatara_data,
            sannari_data=sannari_data,
            lang=lang
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
    shani_sare_sati_data = get_shani_sare_sati_data(moon_rasi=get_rashi_name_i18n(moon_rasi_idx, lang), planets_data=planets_data, user_dob=dob, lang=lang)
    shani_sare_sati_data = translate_shani_sare_sati_data(shani_sare_sati_data, lang)

    # Dwadash Bhab Phala - 12 House Results (only actual placements) (i18n)
    dwadash_html = get_dwadash_html_i18n(planet_houses=planet_houses, asc_rasi_idx=asc_rasi_idx, lang=lang)
    dwadash_json_data = get_dwadash_json(planet_houses=planet_houses, asc_rasi_idx=asc_rasi_idx)

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
                           moon_nak_name=get_nakshatra_name_i18n(moon_nak_idx - 1, lang),
                           moon_nak_idx=moon_nak_idx,
                           navatara_data=navatara_data, navatara_svg=navatara_svg,
                           nakshatra_phala_text=nakshatra_phala_text,
                           lagna_phala_text=lagna_phala_text,
                           rashi_phala_text=rashi_phala_text,
                           moon_rasi=get_rashi_name_i18n(moon_rasi_idx, lang),
                           graha_bichar_data=graha_bichar_data,
                           graha_bichar_html=graha_bichar_html,
                           shani_sare_sati_data=shani_sare_sati_data,
                           dwadash_html=dwadash_html,
                           dwadash_json_data=dwadash_json_data,
                           planet_houses=planet_houses,
                           user_features=get_user_features(session.get('user_id', 0)),
                           user_subscription_name=user_subscription_name,
                           user_subscription_id=user_subscription_id,
                           all_subscriptions=all_subscriptions,
                           user_sub_info=get_user_sub_info(session.get('user_id', 0)),
                           lang=get_current_language(),
                           dosha_labels=get_dosha_labels(lang),
                           yoga_labels=get_yoga_labels(lang),
                           shani_sare_sati_labels=get_shani_sare_sati_labels(lang),
                           shani_sare_sati_analysis_html=get_shani_sare_sati_analysis_html(lang))

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
        # [i18n fix] Get user's language and planet name map for PDF
        _pdf_lang = get_current_language()
        pnames = get_planet_names_i18n(_pdf_lang)

        for p_name, p_id in planets_dict.items():
            pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            p_sidereal_longitudes[p_name] = pos[0]
            p_speed = pos[3]
            r_idx, rasi, deg = get_rasi_and_degree(pos[0])
            nak_idx, nak, lord = get_nakshatra_details(pos[0])
            # Use language-localized planet name to fix the mixing bug
            display_name = pnames.get(p_name, p_name)
            state = get_planet_state(p_name, r_idx, p_speed,
                                     p_sidereal_longitudes.get("ৰবি", 0), pos[0], _pdf_lang)
            planets_data.append({"name": display_name, "name_asm": p_name, "name_en": get_eng_planet(p_name), "rasi": rasi, "rasi_idx": r_idx, "degree": deg,
                                 "nakshatra": nak, "nak_idx": nak_idx, "lord": lord,
                                 "state": state})
            planet_signs[p_name] = r_idx

        p_sidereal_longitudes["কেতু"] = (p_sidereal_longitudes["ৰাহু"] + 180) % 360
        r_idx_k, ketu_rasi, ketu_deg = get_rasi_and_degree(p_sidereal_longitudes["কেতু"])
        ketu_idx, ketu_nak, ketu_lord = get_nakshatra_details(p_sidereal_longitudes["কেতু"])
        ketu_state = get_planet_state("কেতু", r_idx_k, -1,
                                      p_sidereal_longitudes.get("ৰবি", 0), p_sidereal_longitudes["কেতু"], _pdf_lang)
        planets_data.append({"name": pnames.get("কেতু", "কেতু"), "name_asm": "কেতু", "name_en": "Ketu", "rasi": ketu_rasi, "rasi_idx": r_idx_k, "degree": ketu_deg,
                             "nakshatra": ketu_nak, "nak_idx": ketu_idx, "lord": ketu_lord,
                             "state": ketu_state})
        planet_signs["কেতু"] = r_idx_k

        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        asc_sidereal = (ascmc[0] - ayanamsa) % 360
        p_sidereal_longitudes["লগ্ন"] = asc_sidereal
        asc_rasi_idx, asc_rasi, asc_deg = get_rasi_and_degree(asc_sidereal)
        asc_nak_idx, asc_nak, asc_nak_lord = get_nakshatra_details(asc_sidereal)
        lagna_state = get_planet_state("লগ্ন", asc_rasi_idx, 0,
                                       p_sidereal_longitudes.get("ৰবি", 0), asc_sidereal, _pdf_lang)
        planets_data.append({"name": pnames.get("লগ্ন", "লগ্ন"), "name_asm": "লগ্ন", "name_en": "Lagna", "rasi": asc_rasi, "rasi_idx": asc_rasi_idx, "degree": asc_deg,
                             "nakshatra": asc_nak, "nak_idx": asc_nak_idx, "lord": asc_nak_lord,
                             "state": lagna_state})
        planet_signs["লগ্ন"] = asc_rasi_idx

        for p_name, p_lon in p_sidereal_longitudes.items():
            house_idx = (int(p_lon / 30) - asc_rasi_idx) % 12
            planet_houses[p_name] = house_idx

        dasa_hierarchy = get_full_dasa_hierarchy(p_sidereal_longitudes["চন্দ্ৰ"], ist_time)
        lang = get_current_language()
        dasa_hierarchy = localize_dasha_hierarchy(dasa_hierarchy, lang=lang)
        panchanga = get_full_panchanga(ist_time, lat, lon, tz_offset, lang=lang)
        dosha_results_raw = get_complete_dosha_analysis(planet_houses, p_sidereal_longitudes)
        dosha_results = translate_dosha_result(dosha_results_raw, lang)
        yoga_results_raw = get_complete_yoga_analysis(planet_houses, planet_signs, asc_rasi_idx)
        yoga_results = translate_yoga_result(yoga_results_raw, lang)

        # Calculate moon indices BEFORE AI interpretation
        moon_nak_idx = get_nakshatra_details(p_sidereal_longitudes["চন্দ্ৰ"])[0] + 1
        moon_rasi_idx = get_rasi_and_degree(p_sidereal_longitudes["চন্দ্ৰ"])[0]
        navatara_data = get_navatara_data(moon_nak_idx)
        sannari_data = get_sannari_data(moon_nak_idx)

        ai_interpretation = (generate_ai_interpretation_i18n if lang != 'as' else generate_ai_interpretation)(
            name, planets_data, asc_rasi, dosha_results, yoga_results, dasa_hierarchy,
            asc_rasi_idx=asc_rasi_idx,
            planet_signs=planet_signs,
            moon_nak_name=get_nakshatra_name_i18n(moon_nak_idx - 1, lang),
            moon_rasi=get_rashi_name_i18n(moon_rasi_idx, lang),
            tripap_ages=TRIPAP_AGES.get(moon_nak_idx, []),
            navatara_data=navatara_data,
            sannari_data=sannari_data,
            lang=lang
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
        tripap_data = get_tripap_rista(moon_nak_idx, lang)
        tripap_ages = TRIPAP_AGES.get(moon_nak_idx, [])

        # Sannari Chakra for PDF (with language support)
        sannari_html = generate_sannari_html_table(moon_nak_idx, nakshatras[moon_nak_idx - 1], lang=lang)

        # Navatara Chakra for PDF (with language support)
        navatara_html = generate_navatara_html(moon_nak_idx, lang=lang)

        # Nakshatra Phala for PDF
        nakshatra_phala_html = apply_gender(get_nakshatra_phala_html_i18n(moon_nak_idx, lang), gender)

        # Lagna Phala for PDF
        lagna_phala_html = apply_gender(get_lagna_phala_html_i18n(asc_rasi_idx, lang), gender)

        # Rashi Phala for PDF (Moon sign based)
        rashi_phala_html = apply_gender(get_rashi_phala_html(moon_rasi_idx), gender)

        # Lagna Lord and Moon Rashi Lord for PDF (i18n - use user's language)
        lagna_lord = get_rashi_lord(asc_rasi_idx, lang)
        moon_rashi_lord = get_rashi_lord(moon_rasi_idx, lang)
        moon_rasi = get_rashi_name_i18n(moon_rasi_idx, lang)

        # Graha Bichar for PDF (i18n)
        graha_bichar_html = get_graha_bichar_html_i18n(planet_houses, lang)

        # Dasha Predictions for PDF - use importantantardasa.py (new detailed JSON data)
        antardasha_phala_html = build_important_antardasha_html(
            dasa_hierarchy, gender=gender, lang=lang
        )

        # Build pratyantar dasha phala HTML (today onward, current antardasha only)
        pratyantar_dasha_html = build_pratyantar_dasha_html(
            dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx, gender=gender, lang=lang
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
            nakshatra_name=get_nakshatra_name_i18n(moon_nak_idx - 1, lang),
            nakshatra_idx=moon_nak_idx - 1,
            nakshatra_pada=panchanga.get('nakshatra', {}).get('pada', 1),
            panchanga=panchanga,
            lang=lang,
        )

        # Dwadash Bhab Phala for PDF (only actual placements) (i18n)
        dwadash_html = get_dwadash_html_i18n(planet_houses=planet_houses, asc_rasi_idx=asc_rasi_idx, lang=lang)

        # Vimsottari Dasha Summary for PDF
        vimsottari_summary = build_vimsottari_summary(dasa_hierarchy, lang=lang)

        # Graha Maitri for PDF
        graha_maitri_html = build_graha_maitri_pdf_html(planet_houses, lang)

        # Kartari Yoga for PDF (Subh Kartari / Paap Kartari)
        kartari_html = generate_kartari_report(planet_houses, lang)

        # Ratna (Gemstones) for PDF
        ratna_html = build_ratna_html(asc_rasi_idx, lang)

        pdf_bytes = generate_pdf_report(
            name, dob, tob, place, planets_data, panchanga,
            dosha_results, yoga_results, dasa_hierarchy, ai_interpretation,
            all_vargas, tripap_data, tripap_ages, asc_rasi,
            [], sannari_html, navatara_html,
            nakshatra_phala_html, lagna_phala_html, rashi_phala_html,
            graha_bichar_html=graha_bichar_html,
            antardasha_phala_html=antardasha_phala_html,
            dwadash_html=dwadash_html,
            vimsottari_summary=vimsottari_summary,
            lagna_lord=lagna_lord, moon_rashi_lord=moon_rashi_lord,
            moon_rasi=moon_rasi, gender=gender,
            astrologer_profile=astrologer_profile,
            patrika_text=patrika_text,
            pratyantar_dasha_html=pratyantar_dasha_html,
            graha_maitri_html=graha_maitri_html,
            kartari_html=kartari_html,
            ratna_html=ratna_html,
            lang=lang
        )

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Dhruvatara_AI_{name.replace(" ", "_")}.pdf'
        )

    except Exception as e:
        return f"<div style='padding:40px;font-family:Arial;text-align:center;'><h2 style='color:#c62828;'>PDF নিৰ্মাণ ত্ৰুটি</h2><p>{str(e)}</p><a href='/'>আকৌ চেষ্টা কৰক</a></div>"

@app.route("/api/kartari-report", methods=["POST"])
def api_kartari_report():
    try:
        data = request.get_json(silent=True) or request.form
        planet_houses = data.get('planet_houses')
        if isinstance(planet_houses, str):
            planet_houses = json.loads(planet_houses)
        if not planet_houses:
            return jsonify({'success': False, 'message': 'Planet house data missing.'}), 400
        lang = data.get('lang', get_current_language())
        report = generate_kartari_report(planet_houses, lang)
        return jsonify({'success': True, 'report': report})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ═══════════════════════════════════════════
#  GRAHA MAITRI (Planetary Friendship)
# ═══════════════════════════════════════════

@app.route("/graha-maitri")
@login_required
def graha_maitri_page():
    """Graha Maitri page - shows planetary friendship charts."""
    lang = get_current_language()
    user_features = get_user_features(session['user_id'])
    feature_defs = get_all_feature_definitions()
    sidebar_images = get_images_by_placement('sidebar')
    footer_images = get_images_by_placement('footer')
    plans_images = get_images_by_placement('plans')
    general_images = get_images_by_placement('general')
    all_footer_images = sidebar_images + footer_images + plans_images + general_images
    
    return render_template("graha_maitri.html",
                           lang=lang,
                           user_features=user_features,
                           feature_defs=feature_defs,
                           user_sub_info=get_user_sub_info(session['user_id']),
                           all_footer_images=all_footer_images)


@app.route("/api/graha-maitri", methods=["POST"])
@login_required
def api_graha_maitri():
    """API endpoint to calculate Graha Maitri from planet house positions."""
    try:
        data = request.get_json(silent=True) or {}
        planet_houses = data.get('planet_houses', {})
        lang = data.get('lang', get_current_language())
        
        if not planet_houses:
            return jsonify({'success': False, 'message': 'Planet house data missing.'}), 400
        
        maitri_data = get_all_maitri_data(planet_houses, lang)
        return jsonify({'success': True, 'data': maitri_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ═══════════════════════════════════════════
#  RATNA (Gemstones)
# ═══════════════════════════════════════════

@app.route("/ratna")
@login_required
def ratna_page():
    """Ratna page - shows gemstone recommendations based on Lagna."""
    lang = get_current_language()
    user_features = get_user_features(session['user_id'])
    feature_defs = get_all_feature_definitions()
    sidebar_images = get_images_by_placement('sidebar')
    footer_images = get_images_by_placement('footer')
    plans_images = get_images_by_placement('plans')
    general_images = get_images_by_placement('general')
    all_footer_images = sidebar_images + footer_images + plans_images + general_images
    
    # Try to get ascendant rashi from sessionStorage (passed via query param or session)
    asc_rasi_idx = request.args.get('asc', None)
    ratna_data = None
    if asc_rasi_idx is not None:
        try:
            asc_rasi_idx = int(asc_rasi_idx)
            ratna_data = get_ratna_data(asc_rasi_idx, lang)
        except (ValueError, TypeError):
            pass
    
    return render_template("ratna.html",
                           lang=lang,
                           user_features=user_features,
                           feature_defs=feature_defs,
                           user_sub_info=get_user_sub_info(session['user_id']),
                           all_footer_images=all_footer_images,
                           ratna_data=ratna_data)


@app.route("/api/ratna", methods=["POST"])
@login_required
def api_ratna():
    """API endpoint to get Ratna (gemstone) data from ascendant rashi index."""
    try:
        data = request.get_json(silent=True) or {}
        asc_rasi_idx = data.get('asc_rasi_idx', None)
        lang = data.get('lang', get_current_language())
        
        if asc_rasi_idx is None:
            return jsonify({'success': False, 'message': 'Ascendant rashi index missing.'}), 400
        
        asc_rasi_idx = int(asc_rasi_idx)
        if asc_rasi_idx < 0 or asc_rasi_idx > 11:
            return jsonify({'success': False, 'message': 'Invalid ascendant rashi index.'}), 400
        
        ratna_data = get_ratna_data(asc_rasi_idx, lang)
        return jsonify({'success': True, 'data': ratna_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route("/generate-patrika", methods=["POST"])
def generate_patrika():
    """Generate patrika text from form data."""
    # Check feature access - only paid users can generate patrika
    if session.get('user_id'):
        if not check_feature_access(session['user_id'], 'patrika_pdf'):
            return jsonify({'error': 'পত্ৰিকা বনাবলৈ প্ৰ\' ভাৰ্চনলৈ আপগ্ৰেড কৰক।'}), 403
    try:
        data = request.get_json()
        lang = data.get("lang", get_current_language())
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
            lang=lang,
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
        # [i18n fix] Get planet name map for PDF
        _pdf_lang = get_current_language()
        pnames = get_planet_names_i18n(_pdf_lang)
        
        for p_name, p_id in planets_dict.items():
            pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            p_sidereal_longitudes[p_name] = pos[0]
            p_speed = pos[3]
            r_idx, rasi, deg = get_rasi_and_degree(pos[0])
            nak_idx, nak, lord = get_nakshatra_details(pos[0])
            state = get_planet_state(p_name, r_idx, p_speed,
                                     p_sidereal_longitudes.get("ৰবি", 0), pos[0], _pdf_lang)
            planets_data.append({"name": p_name, "name_asm": p_name, "name_en": get_eng_planet(p_name), "rasi": rasi, "rasi_idx": r_idx, "degree": deg,
                                 "nakshatra": nak, "nak_idx": nak_idx, "lord": lord,
                                 "state": state})
            planet_signs[p_name] = r_idx
        
        p_sidereal_longitudes["কেতু"] = (p_sidereal_longitudes["ৰাহু"] + 180) % 360
        r_idx_k, ketu_rasi, ketu_deg = get_rasi_and_degree(p_sidereal_longitudes["কেতু"])
        ketu_idx, ketu_nak, ketu_lord = get_nakshatra_details(p_sidereal_longitudes["কেতু"])
        ketu_state = get_planet_state("কেতু", r_idx_k, -1,
                                      p_sidereal_longitudes.get("ৰবি", 0), p_sidereal_longitudes["কেতু"], _pdf_lang)
        planets_data.append({"name": pnames.get("কেতু", "কেতু"), "name_asm": "কেতু", "name_en": "Ketu", "rasi": ketu_rasi, "rasi_idx": r_idx_k, "degree": ketu_deg,
                             "nakshatra": ketu_nak, "nak_idx": ketu_idx, "lord": ketu_lord,
                             "state": ketu_state})
        planet_signs["কেতু"] = r_idx_k
        
        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        asc_sidereal = (ascmc[0] - ayanamsa) % 360
        p_sidereal_longitudes["লগ্ন"] = asc_sidereal
        asc_rasi_idx, asc_rasi, asc_deg = get_rasi_and_degree(asc_sidereal)
        asc_nak_idx, asc_nak, asc_nak_lord = get_nakshatra_details(asc_sidereal)
        lagna_state = get_planet_state("লগ্ন", asc_rasi_idx, 0,
                                       p_sidereal_longitudes.get("ৰবি", 0), asc_sidereal, _pdf_lang)
        planets_data.append({"name": pnames.get("লগ্ন", "লগ্ন"), "name_asm": "লগ্ন", "name_en": "Lagna", "rasi": asc_rasi, "rasi_idx": asc_rasi_idx, "degree": asc_deg,
                             "nakshatra": asc_nak, "nak_idx": asc_nak_idx, "lord": asc_nak_lord,
                             "state": lagna_state})
        planet_signs["লগ্ন"] = asc_rasi_idx
        
        for p_name, p_lon in p_sidereal_longitudes.items():
            house_idx = (int(p_lon / 30) - asc_rasi_idx) % 12
            planet_houses[p_name] = house_idx
        
        dasa_hierarchy = get_full_dasa_hierarchy(p_sidereal_longitudes["চন্দ্ৰ"], ist_time)
        lang = get_current_language()
        dasa_hierarchy = localize_dasha_hierarchy(dasa_hierarchy, lang=lang)
        panchanga = get_full_panchanga(ist_time, lat, lon, tz_offset, lang=lang)
        dosha_results_raw = get_complete_dosha_analysis(planet_houses, p_sidereal_longitudes)
        dosha_results = translate_dosha_result(dosha_results_raw, lang)
        yoga_results_raw = get_complete_yoga_analysis(planet_houses, planet_signs, asc_rasi_idx)
        yoga_results = translate_yoga_result(yoga_results_raw, lang)
        
        moon_nak_idx = get_nakshatra_details(p_sidereal_longitudes["চন্দ্ৰ"])[0] + 1
        moon_rasi_idx = get_rasi_and_degree(p_sidereal_longitudes["চন্দ্ৰ"])[0]
        navatara_data = get_navatara_data(moon_nak_idx)
        sannari_data = get_sannari_data(moon_nak_idx)
        
        ai_interpretation = ""  # AI বিশ্লেষণ পত্ৰিকা PDF-ত দিয়া নহয়
        
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

        tripap_data = get_tripap_rista(moon_nak_idx, lang)
        tripap_ages = TRIPAP_AGES.get(moon_nak_idx, [])
        sannari_html = generate_sannari_html_table(moon_nak_idx, nakshatras[moon_nak_idx - 1], lang=lang)
        navatara_html = generate_navatara_html(moon_nak_idx, lang=lang)
        nakshatra_phala_html = apply_gender(get_nakshatra_phala_html_i18n(moon_nak_idx, lang), gender)
        lagna_phala_html = apply_gender(get_lagna_phala_html_i18n(asc_rasi_idx, lang), gender)
        rashi_phala_html = apply_gender(get_rashi_phala_html_i18n(moon_rasi_idx, lang), gender)
        lagna_lord = get_rashi_lord(asc_rasi_idx, lang)
        moon_rashi_lord = get_rashi_lord(moon_rasi_idx, lang)
        moon_rasi = get_rashi_name_i18n(moon_rasi_idx, lang)
        graha_bichar_html = get_graha_bichar_html_i18n(planet_houses, lang)

        all_dasha_predictions = get_all_maha_antar_predictions(
            dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx
        )
        for dp in all_dasha_predictions:
            dp["prediction"] = apply_gender(dp["prediction"], gender)
        all_dasha_predictions = filter_future_dasha_predictions(all_dasha_predictions)
        
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
            nakshatra_name=get_nakshatra_name_i18n(moon_nak_idx - 1, lang),
            nakshatra_idx=moon_nak_idx - 1,
            nakshatra_pada=panchanga.get('nakshatra', {}).get('pada', 1),
            panchanga=panchanga,
            lang=lang,
        )
        
        astrologer_profile = get_astrologer_profile(session.get('user_id', 0))

        # Build antardasha phala HTML for patrika PDF (current → end) using importantantardasa.py
        antardasha_phala_html = build_important_antardasha_html(
            dasa_hierarchy, gender=gender, lang=lang
        )

        # NOTE: Pratyantar Dasha Phal NOT included in Patrika PDF

        # Dwadash Bhab Phala for PDF (only actual placements) (i18n)
        dwadash_html = get_dwadash_html_i18n(planet_houses=planet_houses, asc_rasi_idx=asc_rasi_idx, lang=lang)

        # Vimsottari Dasha Summary for PDF
        vimsottari_summary = build_vimsottari_summary(dasa_hierarchy, lang=lang)
        
        # Graha Maitri for PDF
        graha_maitri_html = build_graha_maitri_pdf_html(planet_houses, lang)

        # Kartari Yoga for PDF (Subh Kartari / Paap Kartari)
        kartari_html = generate_kartari_report(planet_houses, lang)

        # Ratna (Gemstones) for PDF
        ratna_html = build_ratna_html(asc_rasi_idx, lang)

        # Patrika PDF excludes pratyantar dasha section
        patrika_selected_sections = [
            'planets_table', 'kundli_chart', 'varga_charts', 'panchanga',
            'shani_sare_sati', 'dosha', 'yoga', 'sannari', 'navatara', 'tripap',
            'graha_maitri', 'kartari', 'nakshatra_phala', 'lagna_phala',
            'rashi_phala', 'graha_bichar', 'dwadash_bhab_phala',
            'dasha_summary', 'dasha_full', 'dasha_predictions', 'antardasha_phala',
            'ratna'
        ]
        
        pdf_bytes = generate_pdf_report(
            name, dob, tob, place, planets_data, panchanga,
            dosha_results, yoga_results, dasa_hierarchy, ai_interpretation,
            all_vargas, tripap_data, tripap_ages, asc_rasi,
            [], sannari_html, navatara_html,
            nakshatra_phala_html, lagna_phala_html, rashi_phala_html,
            graha_bichar_html=graha_bichar_html,
            antardasha_phala_html=antardasha_phala_html,
            dwadash_html=dwadash_html,
            vimsottari_summary=vimsottari_summary,
            selected_sections=patrika_selected_sections,
            lagna_lord=lagna_lord, moon_rashi_lord=moon_rashi_lord,
            moon_rasi=moon_rasi, gender=gender,
            astrologer_profile=astrologer_profile,
            patrika_text=patrika_text,
            graha_maitri_html=graha_maitri_html,
            kartari_html=kartari_html,
            ratna_html=ratna_html,
            lang=lang
        )
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Dhruvatara_AI_Patrika_{name.replace(" ", "_")}.pdf'
        )
    except Exception as e:
        return f"<div style='padding:40px;font-family:Arial;text-align:center;'><h2 style='color:#c62828;'>পত্ৰিকা PDF নিৰ্মাণ ত্ৰুটি</h2><p>{str(e)}</p><a href='/'>আকৌ চেষ্টা কৰক</a></div>"

@app.route("/download-pratyantar-pdf", methods=["POST"])
def download_pratyantar_pdf():
    """Generate PDF with Pratyantar Dasha phala (3rd level dasha results)."""
    # Check feature access - only paid users can download pratyantar PDF
    if session.get('user_id'):
        if not check_feature_access(session['user_id'], 'pratyantar_dasha_pdf'):
            return "<div style='padding:40px;font-family:Arial;text-align:center;'><h2 style='color:#c62828;'>🔒 প্ৰৱেশ নিষেধ</h2><p>প্ৰত্যন্তৰ দশা ফল PDF ডাউনলোড কৰিবলৈ প্ৰ' ভাৰ্চনলৈ আপগ্ৰেড কৰক।</p><a href='/'>আকৌ চেষ্টা কৰক</a></div>"

    name = request.form.get("name", request.form.get("public_name", ""))
    dob = request.form.get("dob")
    tob = request.form.get("tob")
    place = request.form.get("place", "")
    gender = request.form.get("gender", "male")

    patrika_public_name = request.form.get("public_name", "").strip()
    if patrika_public_name:
        name = patrika_public_name

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
        # [i18n fix] Get user's language and planet name map for PDF
        _pdf_lang = get_current_language()
        pnames = get_planet_names_i18n(_pdf_lang)

        for p_name, p_id in planets_dict.items():
            pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            p_sidereal_longitudes[p_name] = pos[0]
            p_speed = pos[3]
            r_idx, rasi, deg = get_rasi_and_degree(pos[0])
            nak_idx, nak, lord = get_nakshatra_details(pos[0])
            # Use language-localized planet name to fix the mixing bug
            display_name = pnames.get(p_name, p_name)
            state = get_planet_state(p_name, r_idx, p_speed,
                                     p_sidereal_longitudes.get("ৰবি", 0), pos[0], _pdf_lang)
            planets_data.append({"name": display_name, "name_asm": p_name, "name_en": get_eng_planet(p_name), "rasi": rasi, "rasi_idx": r_idx, "degree": deg,
                                 "nakshatra": nak, "nak_idx": nak_idx, "lord": lord,
                                 "state": state})
            planet_signs[p_name] = r_idx

        p_sidereal_longitudes["কেতু"] = (p_sidereal_longitudes["ৰাহু"] + 180) % 360
        r_idx_k, ketu_rasi, ketu_deg = get_rasi_and_degree(p_sidereal_longitudes["কেতু"])
        ketu_idx, ketu_nak, ketu_lord = get_nakshatra_details(p_sidereal_longitudes["কেতু"])
        ketu_state = get_planet_state("কেতু", r_idx_k, -1,
                                      p_sidereal_longitudes.get("ৰবি", 0), p_sidereal_longitudes["কেতু"], _pdf_lang)
        planets_data.append({"name": pnames.get("কেতু", "কেতু"), "name_asm": "কেতু", "name_en": "Ketu", "rasi": ketu_rasi, "rasi_idx": r_idx_k, "degree": ketu_deg,
                             "nakshatra": ketu_nak, "nak_idx": ketu_idx, "lord": ketu_lord,
                             "state": ketu_state})
        planet_signs["কেতু"] = r_idx_k

        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        asc_sidereal = (ascmc[0] - ayanamsa) % 360
        p_sidereal_longitudes["লগ্ন"] = asc_sidereal
        asc_rasi_idx, asc_rasi, asc_deg = get_rasi_and_degree(asc_sidereal)
        asc_nak_idx, asc_nak, asc_nak_lord = get_nakshatra_details(asc_sidereal)
        lagna_state = get_planet_state("লগ্ন", asc_rasi_idx, 0,
                                       p_sidereal_longitudes.get("ৰবি", 0), asc_sidereal, _pdf_lang)
        planets_data.append({"name": pnames.get("লগ্ন", "লগ্ন"), "name_asm": "লগ্ন", "name_en": "Lagna", "rasi": asc_rasi, "rasi_idx": asc_rasi_idx, "degree": asc_deg,
                             "nakshatra": asc_nak, "nak_idx": asc_nak_idx, "lord": asc_nak_lord,
                             "state": lagna_state})
        planet_signs["লগ্ন"] = asc_rasi_idx

        for p_name, p_lon in p_sidereal_longitudes.items():
            house_idx = (int(p_lon / 30) - asc_rasi_idx) % 12
            planet_houses[p_name] = house_idx

        dasa_hierarchy = get_full_dasa_hierarchy(p_sidereal_longitudes["চন্দ্ৰ"], ist_time)
        lang = get_current_language()
        dasa_hierarchy = localize_dasha_hierarchy(dasa_hierarchy, lang=lang)
        panchanga = get_full_panchanga(ist_time, lat, lon, tz_offset, lang=lang)
        dosha_results_raw = get_complete_dosha_analysis(planet_houses, p_sidereal_longitudes)
        dosha_results = translate_dosha_result(dosha_results_raw, lang)
        yoga_results_raw = get_complete_yoga_analysis(planet_houses, planet_signs, asc_rasi_idx)
        yoga_results = translate_yoga_result(yoga_results_raw, lang)

        moon_nak_idx = get_nakshatra_details(p_sidereal_longitudes["চন্দ্ৰ"])[0] + 1
        moon_rasi_idx = get_rasi_and_degree(p_sidereal_longitudes["চন্দ্ৰ"])[0]
        navatara_data = get_navatara_data(moon_nak_idx)
        sannari_data = get_sannari_data(moon_nak_idx)

        ai_interpretation = ""  # AI বিশ্লেষণ প্ৰত্যান্তৰ দশাফল PDF-ত দিয়া নহয়

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

        tripap_data = get_tripap_rista(moon_nak_idx, lang)
        tripap_ages = TRIPAP_AGES.get(moon_nak_idx, [])
        sannari_html = generate_sannari_html_table(moon_nak_idx, nakshatras[moon_nak_idx - 1], lang=lang)
        navatara_html = generate_navatara_html(moon_nak_idx, lang=lang)
        nakshatra_phala_html = apply_gender(get_nakshatra_phala_html_i18n(moon_nak_idx, lang), gender)
        lagna_phala_html = apply_gender(get_lagna_phala_html_i18n(asc_rasi_idx, lang), gender)
        rashi_phala_html = apply_gender(get_rashi_phala_html_i18n(moon_rasi_idx, lang), gender)
        lagna_lord = get_rashi_lord(asc_rasi_idx, lang)
        moon_rashi_lord = get_rashi_lord(moon_rasi_idx, lang)
        moon_rasi = get_rashi_name_i18n(moon_rasi_idx, lang)
        graha_bichar_html = get_graha_bichar_html_i18n(planet_houses, lang)

        all_dasha_predictions = get_all_maha_antar_predictions(
            dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx
        )
        for dp in all_dasha_predictions:
            dp["prediction"] = apply_gender(dp["prediction"], gender)
        all_dasha_predictions = filter_future_dasha_predictions(all_dasha_predictions)

        # Build antardasha phala HTML
        antardasha_phala_html = build_important_antardasha_html(
            dasa_hierarchy, gender=gender, lang=lang
        )

        # Build pratyantar dasha phala HTML (today onward, current antardasha only)
        pratyantar_dasha_html = build_pratyantar_dasha_html(
            dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx, gender=gender, lang=lang
        )

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
            nakshatra_name=get_nakshatra_name_i18n(moon_nak_idx - 1, lang),
            nakshatra_idx=moon_nak_idx - 1,
            nakshatra_pada=panchanga.get('nakshatra', {}).get('pada', 1),
            panchanga=panchanga,
            lang=lang,
        )

        astrologer_profile = get_astrologer_profile(session.get('user_id', 0))

        # Dwadash Bhab Phala (i18n)
        dwadash_html = get_dwadash_html_i18n(planet_houses=planet_houses, asc_rasi_idx=asc_rasi_idx, lang=lang)

        # Vimsottari Dasha Summary
        vimsottari_summary = build_vimsottari_summary(dasa_hierarchy, lang=lang)

        # Graha Maitri for PDF
        graha_maitri_html = build_graha_maitri_pdf_html(planet_houses, lang)

        # Kartari Yoga for PDF (Subh Kartari / Paap Kartari)
        kartari_html = generate_kartari_report(planet_houses, lang)

        # Ratna (Gemstones) for PDF
        ratna_html = build_ratna_html(asc_rasi_idx, lang)

        pdf_bytes = generate_pdf_report(
            name, dob, tob, place, planets_data, panchanga,
            dosha_results, yoga_results, dasa_hierarchy, ai_interpretation,
            all_vargas, tripap_data, tripap_ages, asc_rasi,
            [], sannari_html, navatara_html,
            nakshatra_phala_html, lagna_phala_html, rashi_phala_html,
            graha_bichar_html=graha_bichar_html,
            antardasha_phala_html=antardasha_phala_html,
            dwadash_html=dwadash_html,
            vimsottari_summary=vimsottari_summary,
            lagna_lord=lagna_lord, moon_rashi_lord=moon_rashi_lord,
            moon_rasi=moon_rasi, gender=gender,
            astrologer_profile=astrologer_profile,
            patrika_text=patrika_text,
            pratyantar_dasha_html=pratyantar_dasha_html,
            graha_maitri_html=graha_maitri_html,
            kartari_html=kartari_html,
            ratna_html=ratna_html,
            lang=lang
        )

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Dhruvatara_AI_Pratyantar_{name.replace(" ", "_")}.pdf'
        )
    except Exception as e:
        return f"<div style='padding:40px;font-family:Arial;text-align:center;'><h2 style='color:#c62828;'>প্ৰত্যন্তৰ দশা PDF নিৰ্মাণ ত্ৰুটি</h2><p>{str(e)}</p><a href='/'>আকৌ চেষ্টা কৰক</a></div>"

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
        # [i18n fix] Get user's language and planet name map for PDF
        _pdf_lang = get_current_language()
        pnames = get_planet_names_i18n(_pdf_lang)

        for p_name, p_id in planets_dict.items():
            pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            p_sidereal_longitudes[p_name] = pos[0]
            r_idx, rasi, deg = get_rasi_and_degree(pos[0])
            nak_idx, nak, lord = get_nakshatra_details(pos[0])
            # Use language-localized planet name to fix the mixing bug
            display_name = pnames.get(p_name, p_name)
            planets_data.append({"name": display_name, "name_asm": p_name, "name_en": get_eng_planet(p_name), "rasi": rasi, "rasi_idx": r_idx, "degree": deg,
                                 "nakshatra": nak, "nak_idx": nak_idx, "lord": lord})
            planet_signs[p_name] = r_idx

        p_sidereal_longitudes["কেতু"] = (p_sidereal_longitudes["ৰাহু"] + 180) % 360
        r_idx_k, ketu_rasi, ketu_deg = get_rasi_and_degree(p_sidereal_longitudes["কেতু"])
        ketu_idx, ketu_nak, ketu_lord = get_nakshatra_details(p_sidereal_longitudes["কেতু"])
        planets_data.append({"name": pnames.get("কেতু", "কেতু"), "name_asm": "কেতু", "name_en": "Ketu", "rasi": ketu_rasi, "rasi_idx": r_idx_k, "degree": ketu_deg,
                             "nakshatra": ketu_nak, "nak_idx": ketu_idx, "lord": ketu_lord})
        planet_signs["কেতু"] = r_idx_k

        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        asc_sidereal = (ascmc[0] - ayanamsa) % 360
        p_sidereal_longitudes["লগ্ন"] = asc_sidereal
        asc_rasi_idx, asc_rasi, asc_deg = get_rasi_and_degree(asc_sidereal)
        asc_nak_idx, asc_nak, asc_nak_lord = get_nakshatra_details(asc_sidereal)
        planets_data.append({"name": pnames.get("লগ্ন", "লগ্ন"), "name_asm": "লগ্ন", "name_en": "Lagna", "rasi": asc_rasi, "rasi_idx": asc_rasi_idx, "degree": asc_deg,
                             "nakshatra": asc_nak, "nak_idx": asc_nak_idx, "lord": asc_nak_lord})
        planet_signs["লগ্ন"] = asc_rasi_idx

        for p_name, p_lon in p_sidereal_longitudes.items():
            house_idx = (int(p_lon / 30) - asc_rasi_idx) % 12
            planet_houses[p_name] = house_idx

        dasa_hierarchy = get_full_dasa_hierarchy(p_sidereal_longitudes["চন্দ্ৰ"], ist_time)
        lang = get_current_language()
        dasa_hierarchy = localize_dasha_hierarchy(dasa_hierarchy, lang=lang)
        panchanga = get_full_panchanga(ist_time, lat, lon, tz_offset, lang=lang)
        dosha_results_raw = get_complete_dosha_analysis(planet_houses, p_sidereal_longitudes)
        dosha_results = translate_dosha_result(dosha_results_raw, lang)
        yoga_results_raw = get_complete_yoga_analysis(planet_houses, planet_signs, asc_rasi_idx)
        yoga_results = translate_yoga_result(yoga_results_raw, lang)

        # Calculate moon indices BEFORE AI interpretation
        moon_nak_idx = get_nakshatra_details(p_sidereal_longitudes["চন্দ্ৰ"])[0] + 1
        moon_rasi_idx = get_rasi_and_degree(p_sidereal_longitudes["চন্দ্ৰ"])[0]

        # Navatara & Sannari data for AI
        navatara_data = get_navatara_data(moon_nak_idx)
        sannari_data = get_sannari_data(moon_nak_idx)

        ai_interpretation = (generate_ai_interpretation_i18n if lang != 'as' else generate_ai_interpretation)(
            name, planets_data, asc_rasi, dosha_results, yoga_results, dasa_hierarchy,
            asc_rasi_idx=asc_rasi_idx,
            planet_signs=planet_signs,
            moon_nak_name=get_nakshatra_name_i18n(moon_nak_idx - 1, lang),
            moon_rasi=get_rashi_name_i18n(moon_rasi_idx, lang),
            tripap_ages=TRIPAP_AGES.get(moon_nak_idx, []),
            navatara_data=navatara_data,
            sannari_data=sannari_data,
            lang=lang
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

        tripap_data = get_tripap_rista(moon_nak_idx, lang)
        tripap_ages = TRIPAP_AGES.get(moon_nak_idx, [])

        sannari_html = generate_sannari_html_table(moon_nak_idx, nakshatras[moon_nak_idx - 1], lang=lang)

        navatara_html = generate_navatara_html(moon_nak_idx, lang=lang)

        nakshatra_phala_html = apply_gender(get_nakshatra_phala_html_i18n(moon_nak_idx, lang), gender)
        lagna_phala_html = apply_gender(get_lagna_phala_html_i18n(asc_rasi_idx, lang), gender)

        rashi_phala_html = apply_gender(get_rashi_phala_html_i18n(moon_rasi_idx, lang), gender)

        # Lagna Lord and Moon Rashi Lord for PDF (i18n - use user's language)
        lagna_lord = get_rashi_lord(asc_rasi_idx, lang)
        moon_rashi_lord = get_rashi_lord(moon_rasi_idx, lang)
        moon_rasi = get_rashi_name_i18n(moon_rasi_idx, lang)

        # Graha Bichar for PDF (i18n)
        graha_bichar_html = get_graha_bichar_html_i18n(planet_houses, lang)

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
            nakshatra_name=get_nakshatra_name_i18n(moon_nak_idx - 1, lang),
            nakshatra_idx=moon_nak_idx - 1,
            nakshatra_pada=panchanga.get('nakshatra', {}).get('pada', 1),
            panchanga=panchanga,
            lang=lang,
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
                    selected_maha=antardasha_maha, include_current_and_future_only=True, gender=gender, lang=lang
                )
            elif antardasha_mode == "all_future":
                # Show all future antardashas across all mahadashas
                antardasha_phala_html = build_antardasha_html(
                    dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx,
                    selected_maha=None, include_current_and_future_only=True, gender=gender, lang=lang
                )
            else:
                # current_onward: current antardasha → end of current mahadasha
                antardasha_phala_html = build_antardasha_html(
                    dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx,
                    selected_maha=None, include_current_and_future_only=True, gender=gender, lang=lang
                )

        # Build pratyantar dasha phala HTML for custom PDF (only if selected)
        pratyantar_dasha_html = ""
        if 'pratyantar_dasha' in selected_sections:
            pratyantar_dasha_html = build_pratyantar_dasha_html(
                dasa_hierarchy, p_sidereal_longitudes, asc_rasi_idx, gender=gender, lang=lang
            )

        # Dwadash Bhab Phala for PDF (only if selected, only actual placements) (i18n)
        dwadash_html = ""
        if 'dwadash_bhab_phala' in selected_sections:
            dwadash_html = get_dwadash_html_i18n(planet_houses=planet_houses, asc_rasi_idx=asc_rasi_idx, lang=lang)

        # Vimsottari Dasha Summary for PDF
        vimsottari_summary = ""
        if 'dasha_summary' in selected_sections:
            vimsottari_summary = build_vimsottari_summary(dasa_hierarchy, lang=lang)

        # Graha Maitri for PDF (only if selected)
        graha_maitri_html = ""
        if 'graha_maitri' in selected_sections:
            graha_maitri_html = build_graha_maitri_pdf_html(planet_houses, lang)

        # Kartari Yoga for PDF (only if selected)
        kartari_html = ""
        if 'kartari' in selected_sections:
            kartari_html = generate_kartari_report(planet_houses, lang)

        # Ratna (Gemstones) for PDF (only if selected)
        ratna_html = ""
        if 'ratna' in selected_sections:
            ratna_html = build_ratna_html(asc_rasi_idx, lang)

        pdf_bytes = generate_pdf_report(
            name, dob, tob, place, planets_data, panchanga,
            dosha_results, yoga_results, dasa_hierarchy, ai_interpretation,
            all_vargas, tripap_data, tripap_ages, asc_rasi,
            all_dasha_predictions, sannari_html, navatara_html,
            nakshatra_phala_html, lagna_phala_html, rashi_phala_html,
            graha_bichar_html=graha_bichar_html,
            antardasha_phala_html=antardasha_phala_html,
            dwadash_html=dwadash_html,
            vimsottari_summary=vimsottari_summary,
            selected_sections=selected_sections,
            lagna_lord=lagna_lord, moon_rashi_lord=moon_rashi_lord,
            moon_rasi=moon_rasi, gender=gender,
            astrologer_profile=astrologer_profile,
            patrika_text=patrika_text,
            pratyantar_dasha_html=pratyantar_dasha_html,
            graha_maitri_html=graha_maitri_html,
            kartari_html=kartari_html,
            ratna_html=ratna_html,
            lang=lang
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
    lang = request.args.get("lang", get_current_language())
    now = datetime.now()
    # timezone offset (hours) - optional query param 'tz', default 5.5
    try:
        tz_offset = float(request.args.get("tz", request.args.get("timezone", 5.5)))
    except (ValueError, TypeError):
        tz_offset = 5.5
    panchanga = get_full_panchanga(now, lat, lon, tz_offset, lang=lang)
    return jsonify(panchanga)


@app.route("/api/panchanga-full", methods=["GET"])
def api_panchanga_full():
    """API endpoint for full Panchanga with time ranges and planetary positions."""
    try:
        lat = float(request.args.get("lat", 26.1445))
        lon = float(request.args.get("lon", 91.7362))
    except (ValueError, TypeError):
        lat, lon = 26.1445, 91.7362
    lang = request.args.get("lang", get_current_language())
    now = datetime.now()
    try:
        tz_offset = float(request.args.get("tz", request.args.get("timezone", 5.5)))
    except (ValueError, TypeError):
        tz_offset = 5.5
    panchanga = get_panchanga_with_times(now, lat, lon, tz_offset, lang=lang)
    return jsonify(panchanga)


@app.route("/api/panchanga-widget", methods=["GET"])
def api_panchanga_widget():
    """Return HTML widget for Today's Panchanga. Supports optional date param."""
    try:
        lat = float(request.args.get("lat", 26.1445))
        lon = float(request.args.get("lon", 91.7362))
    except (ValueError, TypeError):
        lat, lon = 26.1445, 91.7362
    lang = request.args.get("lang", get_current_language())
    try:
        tz_offset = float(request.args.get("tz", request.args.get("timezone", 5.5)))
    except (ValueError, TypeError):
        tz_offset = 5.5

    # Support custom date via ?date=YYYY-MM-DD
    date_str = request.args.get("date", "").strip()
    if date_str:
        try:
            now = datetime.strptime(date_str, "%Y-%m-%d")
            # Set time to noon for panchanga calculation
            now = now.replace(hour=12, minute=0, second=0)
        except ValueError:
            now = datetime.now()
    else:
        now = datetime.now()

    panchanga = get_panchanga_with_times(now, lat, lon, tz_offset, lang=lang)
    return render_template("panchanga_widget.html", panchanga=panchanga, lat=lat, lon=lon, tz=tz_offset)


@app.route("/api/locations", methods=["GET"])
def api_locations():
    """Return all locations from locations.json for panchanga widget."""
    try:
        loc_path = os.path.join(os.path.dirname(__file__), "locations.json")
        with open(loc_path, "r", encoding="utf-8") as f:
            locations = json.load(f)
        # Return simplified list with name, lat, lon
        result = [{"name": loc["name"], "lat": loc["lat"], "lon": loc["lon"]} for loc in locations]
        return jsonify(result)
    except Exception as e:
        return jsonify([])


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

    lang = request.args.get("lang", get_current_language())
    # graha_name is English (e.g. "Sun") from JS - convert to Assamese for the lookup
    from dasha_engine import get_asm_planet
    graha_name_asm = get_asm_planet(graha_name)
    # rashi_name from JS is in user's language (Assamese/Hindi/Bengali/English)
    # Convert to Assamese for the i18n function to use for key lookup
    import unicodedata
    from prediction_i18n import _ASM_RASHI_TO_INDEX
    rashi_idx = -1
    # Normalize input to NFC for consistent matching
    rashi_name_n = unicodedata.normalize('NFC', rashi_name)
    # Try to find rashi index (rashi names in user's lang might match ASM index mapping)
    rashi_names_asm = ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"]
    rashi_names_asm_n = [unicodedata.normalize('NFC', r) for r in rashi_names_asm]
    if rashi_name_n in rashi_names_asm_n:
        rashi_idx = rashi_names_asm_n.index(rashi_name_n)
    elif rashi_name_n in _ASM_RASHI_TO_INDEX:
        rashi_idx = _ASM_RASHI_TO_INDEX[rashi_name_n]
    
    # If rashi is in user's language (not Assamese), we need to convert it
    # The i18n function will convert it to target language, but we need ASM input
    if rashi_idx < 0:
        # Try English rashi names
        rashi_names_en = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        if rashi_name_n in rashi_names_en:
            rashi_idx = rashi_names_en.index(rashi_name_n)
    
    if rashi_idx >= 0:
        rashi_name_asm = rashi_names_asm[rashi_idx]
    else:
        rashi_name_asm = rashi_name  # fallback
    
    phala_text = get_antardasha_phala_i18n(graha_name_asm, rashi_name_asm, int(house_num), lang)
    return jsonify({"phala": phala_text})

# ═══════════════════════════════════════════
#  অন্তৰদশা ফল API (importantantardasa.py - new detailed JSON)
# ═══════════════════════════════════════════

@app.route("/api/important-antardasha-phala", methods=["POST"])
def api_important_antardasha_phala():
    """API endpoint for antardasha phala from the new detailed JSON (antardasha_data.json)."""
    data = request.get_json()
    maha_lord = data.get("maha", "")
    antar_lord = data.get("antar", "")

    if not maha_lord or not antar_lord:
        return jsonify({"error": "Missing maha/antar lords"}), 400

    lang = request.args.get("lang", get_current_language())
    # Convert English planet names to Assamese for i18n lookup
    from dasha_engine import get_asm_planet
    maha_asm = get_asm_planet(maha_lord)
    antar_asm = get_asm_planet(antar_lord)
    phala_text = get_important_antardasha_phala_i18n(maha_asm, antar_asm, lang)
    return jsonify({"phala": phala_text})

# ═══════════════════════════════════════════
#  AUTH ROUTES (Login, Register, Verify)
# ═══════════════════════════════════════════

@app.route("/login")
def login_page():
    """User login/register page."""
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))
    # Compute today's panchanga for Guwahati (default)
    from panchanga_data import get_panchanga_with_times
    lang = get_current_language()
    panchanga = get_panchanga_with_times(datetime.now(), 26.1445, 91.7362, 5.5, lang=lang)
    return render_template("login.html", panchanga=panchanga)


@app.route("/login", methods=["POST"])
def login_post():
    """Handle user login."""
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    ip = request.remote_addr

    success, message, user_data = login_user(email, password, ip)

    if success:
        # Check free user session limit (max 3 sessions/day)
        sub_id = user_data.get('subscription_id', 1)
        can_login, limit_msg = can_free_user_login(user_data['id'], sub_id)
        if not can_login:
            flash(limit_msg, 'error')
            return redirect(url_for('login_page'))

        session['user_id'] = user_data['id']
        session['user_name'] = user_data['name']
        session['user_email'] = user_data['email']
        session['subscription_id'] = sub_id
        session['login_time'] = datetime.now().isoformat()

        # Start session tracking
        start_user_session(user_data['id'])

        # Log login activity
        log_page_visit(user_data['id'], 'login', 'লগইন', '/login', ip)
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
        flash(get_text('password_min_length', get_current_language()), 'error')
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
        flash(get_text('user_not_found', get_current_language()), 'error')
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
        flash(get_text('mobile_not_registered', get_current_language()), 'error')
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
    if 'user_id' in session:
        end_all_user_sessions(session['user_id'])
    session.clear()
    flash(get_text('logout_message', get_current_language()), 'info')
    return redirect(url_for('login_page'))


# ═══════════════════════════════════════════
#  HEARTBEAT & INACTIVITY TRACKING
# ═══════════════════════════════════════════

@app.route("/api/heartbeat", methods=["POST"])
def api_heartbeat():
    """Heartbeat endpoint to track user activity. Returns auto-logout signal if inactive > 3 min (free users only)."""
    # Free-user inactivity timeout (in seconds). Pro users have no inactivity limit.
    FREE_USER_INACTIVITY_LIMIT_SECONDS = 180  # 3 minutes

    if 'user_id' not in session:
        return jsonify({"logged_in": False, "auto_logout": True}), 401

    user_id = session['user_id']
    data = request.get_json(silent=True) or {}
    last_activity = data.get('last_activity', 0)  # seconds since last activity

    # If inactive for more than the free-user limit, signal auto-logout for free users only.
    # Pro users (subscription_id > 1) are never auto-logged out for inactivity.
    sub_id = session.get('subscription_id', 1)
    if sub_id == 1 and last_activity > FREE_USER_INACTIVITY_LIMIT_SECONDS:
        end_all_user_sessions(user_id)
        session.clear()
        return jsonify({
            "logged_in": False,
            "auto_logout": True,
            "message": "আপুনি ৩ মিনিটতকৈ বেছি সময় নিষ্ক্ৰিয় আছিল। বিনামূলীয়া ব্যৱহাৰকাৰীৰ বাবে চেচন স্বয়ংক্ৰিয়ভাৱে বন্ধ কৰা হ'ল।"
        })

    return jsonify({"logged_in": True, "auto_logout": False})


# ═══════════════════════════════════════════
#  SUBSCRIPTION / UPGRADE PAGE
# ═══════════════════════════════════════════

@app.route("/subscription")
def subscription_page():
    """Subscription/upgrade page showing all plans."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Get all subscriptions
    subs = conn.execute("SELECT * FROM subscriptions WHERE is_active = 1 ORDER BY id").fetchall()
    all_subscriptions = [dict(s) for s in subs]

    # Get user info if logged in
    user_subscription_name = "বিনামূলীয়া"
    user_subscription_id = 1
    if session.get('user_id'):
        row = conn.execute(
            "SELECT s.name_asm, s.id FROM users u JOIN subscriptions s ON u.subscription_id = s.id WHERE u.id = ?",
            (session['user_id'],)
        ).fetchone()
        if row:
            user_subscription_name = row['name_asm']
            user_subscription_id = row['id']

    # Get subscription features for each plan
    sub_features = {}
    for sub in all_subscriptions:
        features = conn.execute('''
            SELECT fd.feature_name_asm, fd.feature_key
            FROM subscription_features sf
            JOIN feature_definitions fd ON sf.feature_key = fd.feature_key
            WHERE sf.subscription_id = ? AND sf.enabled = 1
            ORDER BY fd.display_order
        ''', (sub['id'],)).fetchall()
        sub_features[sub['id']] = [dict(f) for f in features]

    conn.close()

    return render_template("subscription.html",
                           all_subscriptions=all_subscriptions,
                           user_subscription_name=user_subscription_name,
                           user_subscription_id=user_subscription_id,
                           sub_features=sub_features,
                           user_sub_info=get_user_sub_info(session.get('user_id', 0)))


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
        flash(get_text('user_not_found', get_current_language()), 'error')
        return redirect(url_for('login_page'))

    user_features = get_user_features(session['user_id'])
    feature_defs = get_all_feature_definitions()
    subscription = dict(user)

    conn.close()

    # Log dashboard visit
    log_page_visit(session['user_id'], 'dashboard', 'ডেশ্ববৰ্ড', '/dashboard')

    feature_icons = {
        "kundli_calculate": "🔮", "varga_charts": "📊", "panchanga": "🕉️",
        "dosha_analysis": "⚠️", "yoga_analysis": "✨", "dasha": "⏳",
        "ai_interpretation": "🤖", "pdf_report": "📄", "nakshatra_phala": "⭐",
        "lagna_phala": "🌅", "rashi_phala": "♈", "sannari_chakra": "🔄",
        "navatara_chakra": "🌐", "tripap_rista": "⚡", "custom_pdf": "📑",
        "numerology": "🔢", "numerology_chat": "💬", "numerology_pdf": "📋",
        "numerology_varsha": "📅", "graha_maitri": "🤝"
    }

    return render_template("user_dashboard.html",
                           user=dict(user), subscription=subscription,
                           user_features=user_features, feature_defs=feature_defs,
                           feature_icons=feature_icons,
                           user_sub_info=get_user_sub_info(session['user_id']))


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

    # Compute today's panchanga for Guwahati (default)
    from panchanga_data import get_panchanga_with_times
    lang = get_current_language()
    panchanga = get_panchanga_with_times(datetime.now(), 26.1445, 91.7362, 5.5, lang=lang)

    return render_template("index.html", places=places, timezones=timezones,
                           user_features=user_features, feature_defs=feature_defs,
                           panchanga=panchanga,
                           user_sub_info=get_user_sub_info(session['user_id']))


# ═══════════════════════════════════════════
#  RASHIFAL ROUTES (দৈনিক, মাহেকীয়া, বছেৰেকীয়া ৰাশিফল)
# ═══════════════════════════════════════════

@app.route("/rashifal")
def rashifal_page():
    """Rashifal (horoscope) page — login required. Free users get 1 per day."""
    if 'user_id' not in session:
        flash(get_text('rashifal_login_required', get_current_language()), 'error')
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    # Check if user has rashi_phala feature access (paid users)
    has_full_access = check_feature_access(user_id, 'rashi_phala')

    # Get today's usage for free users
    today_used_rashis = []
    today_count = 0
    if not has_full_access:
        today_count = get_user_rashifal_usage_today(user_id)
        today_used_rashis = get_user_rashifal_used_rashis_today(user_id)

    # Log page visit
    log_page_visit(user_id, 'rashifal', 'ৰাশিফল', '/rashifal')

    return render_template("rashifal.html",
                           has_full_access=has_full_access,
                           today_count=today_count,
                           today_used_rashis=today_used_rashis,
                           user_sub_info=get_user_sub_info(user_id))


@app.route("/api/rashifal", methods=["POST"])
def api_rashifal():
    """API endpoint to generate rashifal using Ollama AI. With access control."""
    data = request.get_json()
    rashi = data.get("rashi", "").strip()
    period = data.get("period", "daily").strip()

    if not rashi or rashi not in RASHIFAL_RASHI_NAMES:
        return jsonify({"success": False, "error": "অনুগ্ৰহ কৰি এটা বৈধ ৰাশি বাছনি কৰক।"}), 400

    if period not in ("daily", "monthly", "yearly"):
        return jsonify({"success": False, "error": "অবৈধ সময়সীমা।"}), 400

    # Access control: login required
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "ৰাশিফল চাবলৈ প্ৰথমে লগইন কৰক।", "require_login": True}), 401

    user_id = session['user_id']
    has_full_access = check_feature_access(user_id, 'rashi_phala')

    # Free user: only 1 rashi per day
    if not has_full_access:
        today_count = get_user_rashifal_usage_today(user_id)
        today_used = get_user_rashifal_used_rashis_today(user_id)

        if today_count >= 1 and rashi not in today_used:
            return jsonify({
                "success": False,
                "error": "বিনামূলীয়া ব্যৱহাৰকাৰীয়ে দৈনিক মাত্ৰ এটা ৰাশিফলহে চাব পাৰে। অধিক ৰাশিফলৰ বাবে প্ৰ' ভাৰ্চনলৈ আপগ্ৰেড কৰক।",
                "limit_reached": True,
                "upgrade_needed": True
            }), 403

    try:
        rashifal_text = generate_rashifal(rashi, period)

        # Log usage
        log_rashifal_usage(user_id, rashi, period)
        log_feature_usage(user_id, 'rashifal_view', f'{rashi} ৰাশিফল ({period})',
                          f'Viewed {rashi} rashifal ({period})')

        return jsonify({
            "success": True,
            "rashifal": rashifal_text,
            "has_full_access": has_full_access,
            "today_count": get_user_rashifal_usage_today(user_id) if not has_full_access else 0
        })
    except Exception as e:
        logger.error(f"Rashifal generation error: {e}")
        return jsonify({"success": False, "error": "ৰাশিফল প্ৰস্তুত কৰিব নোৱাৰিলে। পিছত পুনৰ চেষ্টা কৰক।"}), 500


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
    flash(get_text('admin_logout_success', get_current_language()), 'info')
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
    """API: Set user subscription. Auto-manages feature overrides."""
    data = request.get_json()
    sub_id = data.get("subscription_id", 1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    sub = conn.execute("SELECT duration_days FROM subscriptions WHERE id = ?", (sub_id,)).fetchone()
    conn.close()

    duration = sub['duration_days'] if sub else None
    success, message = admin_set_user_subscription(user_id, sub_id, duration)

    if success:
        # Auto-manage feature overrides based on new subscription
        if sub_id == 1:
            # Free user: remove rashi_phala and PDF feature overrides
            admin_remove_user_feature_override(user_id, 'rashi_phala')
            for feat in ['pdf_report', 'custom_pdf', 'patrika_pdf', 'pratyantar_dasha_pdf']:
                admin_remove_user_feature_override(user_id, feat)
        else:
            # Pro user: remove ALL overrides so they get full subscription features
            conn2 = sqlite3.connect(DB_PATH)
            try:
                conn2.execute(
                    "DELETE FROM user_feature_overrides WHERE user_id = ?",
                    (user_id,)
                )
                conn2.commit()
            finally:
                conn2.close()

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


# ─── Adv_Nakshatra API ───

@app.route("/api/adv-nakshatra/<int:nak_id>")
def api_adv_nakshatra(nak_id):
    """Return detailed nakshatra data from Adv_Nakshatra.json for a given nakshatra ID (1-27)."""
    try:
        json_path = os.path.join(os.path.dirname(__file__), "Adv_Nakshatra.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for entry in data:
            if entry.get("nakshatra_id") == nak_id:
                return jsonify(entry)
        return jsonify({"error": "নক্ষত্ৰ পোৱা নগ'ল"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/adv-lagna/<int:lagna_id>")
def api_adv_lagna(lagna_id):
    """Return detailed lagna data from Adv_Lagna.json for a given lagna ID (0-11)."""
    try:
        json_path = os.path.join(os.path.dirname(__file__), "Adv_Lagna.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for entry in data:
            if entry.get("lagna_id") == lagna_id:
                return jsonify(entry)
        return jsonify({"error": "লগ্ন পোৱা নগ'ল"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
#  ADMIN ANALYTICS & ACTIVITY TRACKING ROUTES
# ═══════════════════════════════════════════

@app.route("/admin/api/analytics/dashboard")
@admin_required
def admin_api_analytics_dashboard():
    """API: Get comprehensive analytics dashboard data."""
    stats = get_admin_dashboard_stats()
    special_topics = get_special_topic_usage()
    stats['special_topics'] = special_topics
    return jsonify(stats)


@app.route("/admin/api/analytics/users-summary")
@admin_required
def admin_api_users_summary():
    """API: Get activity summary for all users."""
    users = get_all_users_activity_summary()
    return jsonify(users)


@app.route("/admin/api/analytics/user/<int:user_id>")
@admin_required
def admin_api_user_analytics(user_id):
    """API: Get detailed analytics for a specific user."""
    detail = get_user_activity_detail(user_id)
    if not detail:
        return jsonify({"error": "ব্যৱহাৰকাৰী পোৱা নগল"}), 404
    return jsonify(detail)


@app.route("/admin/api/analytics/special-topics")
@admin_required
def admin_api_special_topics():
    """API: Get special topic usage stats."""
    topics = get_special_topic_usage()
    return jsonify(topics)


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
        # [i18n fix] Get user's language and planet name map for PDF
        _pdf_lang = get_current_language()
        pnames = get_planet_names_i18n(_pdf_lang)

        for p_name, p_id in planets_dict.items():
            pos, _ = swe.calc_ut(jd, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            p_sidereal_longitudes[p_name] = pos[0]
            r_idx, rasi, deg = get_rasi_and_degree(pos[0])
            nak_idx, nak, lord = get_nakshatra_details(pos[0])
            # Use language-localized planet name to fix the mixing bug
            display_name = pnames.get(p_name, p_name)
            planets_data.append({"name": display_name, "name_asm": p_name, "name_en": get_eng_planet(p_name), "rasi": rasi, "rasi_idx": r_idx, "degree": deg,
                                 "nakshatra": nak, "nak_idx": nak_idx, "lord": lord})
            planet_signs[p_name] = r_idx

        p_sidereal_longitudes["কেতু"] = (p_sidereal_longitudes["ৰাহু"] + 180) % 360
        r_idx_k, ketu_rasi, ketu_deg = get_rasi_and_degree(p_sidereal_longitudes["কেতু"])
        ketu_idx, ketu_nak, ketu_lord = get_nakshatra_details(p_sidereal_longitudes["কেতু"])
        planets_data.append({"name": pnames.get("কেতু", "কেতু"), "name_asm": "কেতু", "name_en": "Ketu", "rasi": ketu_rasi, "rasi_idx": r_idx_k, "degree": ketu_deg,
                             "nakshatra": ketu_nak, "nak_idx": ketu_idx, "lord": ketu_lord})
        planet_signs["কেতু"] = r_idx_k

        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        asc_sidereal = (ascmc[0] - ayanamsa) % 360
        p_sidereal_longitudes["লগ্ন"] = asc_sidereal
        asc_rasi_idx, asc_rasi, asc_deg = get_rasi_and_degree(asc_sidereal)
        asc_nak_idx, asc_nak, asc_nak_lord = get_nakshatra_details(asc_sidereal)
        planets_data.append({"name": pnames.get("লগ্ন", "লগ্ন"), "name_asm": "লগ্ন", "name_en": "Lagna", "rasi": asc_rasi, "rasi_idx": asc_rasi_idx, "degree": asc_deg,
                             "nakshatra": asc_nak, "nak_idx": asc_nak_idx, "lord": asc_nak_lord})
        planet_signs["লগ্ন"] = asc_rasi_idx

        for p_name, p_lon in p_sidereal_longitudes.items():
            house_idx = (int(p_lon / 30) - asc_rasi_idx) % 12
            planet_houses[p_name] = house_idx

        moon_nak_idx = get_nakshatra_details(p_sidereal_longitudes["চন্দ্ৰ"])[0] + 1
        moon_rasi_idx = get_rasi_and_degree(p_sidereal_longitudes["চন্দ্ৰ"])[0]

        dasa_hierarchy = get_full_dasa_hierarchy(p_sidereal_longitudes["চন্দ্ৰ"], ist_time)
        dasa_hierarchy = localize_dasha_hierarchy(dasa_hierarchy, lang=get_current_language())
        dosha_results = get_complete_dosha_analysis(planet_houses, p_sidereal_longitudes)

        lagna_lord = get_rashi_lord(asc_rasi_idx, lang=get_current_language())
        moon_rashi_lord = get_rashi_lord(moon_rasi_idx, lang=get_current_language())

        return jsonify({
            "success": True,
            "planets": planets_data,
            "planet_houses": planet_houses,
            "planet_signs": planet_signs,
            "asc_rasi": asc_rasi,
            "asc_rasi_idx": asc_rasi_idx,
            "moon_nak_name": get_nakshatra_name_i18n(moon_nak_idx - 1, get_current_language()),
            "moon_rasi": get_rashi_name_i18n(moon_rasi_idx, get_current_language()),
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
                           user_features=get_user_features(session.get('user_id', 0)),
                           user_sub_info=get_user_sub_info(session.get('user_id', 0)))


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
#  NUMEROLOGY (অংক জ্যোতিষ) ROUTES
# ═══════════════════════════════════════════

def get_admin_feature_toggles(category: str = None) -> dict:
    """Get admin feature toggles from DB. Returns {feature_key: is_enabled}."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        if category:
            rows = conn.execute(
                "SELECT feature_key, is_enabled FROM admin_feature_toggles WHERE category = ?",
                (category,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT feature_key, is_enabled FROM admin_feature_toggles"
            ).fetchall()
        return {r['feature_key']: bool(r['is_enabled']) for r in rows}
    except Exception:
        return {}
    finally:
        conn.close()


def set_admin_feature_toggle(feature_key: str, is_enabled: bool) -> bool:
    """Set an admin feature toggle."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "UPDATE admin_feature_toggles SET is_enabled = ?, updated_at = CURRENT_TIMESTAMP WHERE feature_key = ?",
            (1 if is_enabled else 0, feature_key)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


@app.route("/numerology")
@login_required
def numerology_page():
    """Numerology input form page."""
    if not check_feature_access(session['user_id'], 'numerology'):
        return render_template('feature_locked.html', feature='numerology'), 403

    user_features = get_user_features(session['user_id'])
    feature_defs = get_all_feature_definitions()
    admin_toggles = get_admin_feature_toggles('numerology')

    return render_template("numerology.html",
                           user_features=user_features,
                           feature_defs=feature_defs,
                           admin_toggles=admin_toggles,
                           user_name=session.get('user_name', ''),
                           user_sub_info=get_user_sub_info(session['user_id']))


@app.route("/numerology/calculate", methods=["POST"])
@login_required
def numerology_calculate():
    """Calculate numerology report."""
    if not check_feature_access(session['user_id'], 'numerology'):
        return jsonify({"success": False, "message": "অংক জ্যোতিষ ফিচাৰ আপোনাৰ বাবে উপলব্ধ নহয়।"}), 403

    name = request.form.get("name", "").strip()
    dob = request.form.get("dob", "").strip()
    gender = request.form.get("gender", "male").strip()

    if not name or not dob:
        return jsonify({"success": False, "message": "নাম আৰু জন্ম তাৰিখ আৱশ্যক।"}), 400

    try:
        report = get_full_numerology_report(name, dob, gender)

        # Save report to DB
        if session.get('user_id'):
            conn = sqlite3.connect(DB_PATH)
            try:
                conn.execute(
                    "INSERT INTO numerology_reports (user_id, name, dob, report_data) VALUES (?, ?, ?, ?)",
                    (session['user_id'], name, dob, json.dumps(report, ensure_ascii=False))
                )
                conn.commit()
            except Exception:
                pass
            finally:
                conn.close()

        # Get admin toggles
        admin_toggles = get_admin_feature_toggles('numerology')

        # Check pro features
        is_pro = check_feature_access(session['user_id'], 'numerology_varsha')
        has_pdf = check_feature_access(session['user_id'], 'numerology_pdf')

        return jsonify({
            "success": True,
            "report": report,
            "admin_toggles": admin_toggles,
            "is_pro": is_pro,
            "has_pdf": has_pdf
        })
    except Exception as e:
        logger.error(f"Numerology calc error: {e}")
        return jsonify({"success": False, "message": f"গণনা ত্ৰুটি: {str(e)}"}), 500


@app.route("/numerology/download-pdf", methods=["POST"])
@login_required
def numerology_download_pdf():
    """Generate and download numerology PDF report."""
    if not check_feature_access(session['user_id'], 'numerology_pdf'):
        return "<div style='padding:40px;font-family:Arial;text-align:center;'><h2 style='color:#c62828;'>🔒 প্ৰৱেশ নিষেধ</h2><p>PDF ডাউনলোড কৰিবলৈ প্ৰ' ভাৰ্চনলৈ আপগ্ৰেড কৰক।</p><a href='/numerology'>আকৌ চেষ্টা কৰক</a></div>"

    name = request.form.get("name", "").strip()
    dob = request.form.get("dob", "").strip()
    selected_sections = request.form.getlist("sections")

    if not name or not dob:
        return "<div style='padding:40px;font-family:Arial;text-align:center;'><h2 style='color:#c62828;'>ত্ৰুটি</h2><p>নাম আৰু জন্ম তাৰিখ আৱশ্যক।</p></div>"

    try:
        report = get_full_numerology_report(name, dob)
        astrologer_profile = get_astrologer_profile(session.get('user_id', 0))

        pdf_bytes = generate_numerology_pdf(report, selected_sections, astrologer_profile)

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Dhruvatara_AI_Numerology_{name.replace(" ", "_")}.pdf'
        )
    except Exception as e:
        logger.error(f"Numerology PDF error: {e}")
        return f"<div style='padding:40px;font-family:Arial;text-align:center;'><h2 style='color:#c62828;'>PDF নিৰ্মাণ ত্ৰুটি</h2><p>{str(e)}</p><a href='/numerology'>আকৌ চেষ্টা কৰক</a></div>"


@app.route("/numerology/chat")
@login_required
def numerology_chat_page():
    """Numerology AI Chat page."""
    if not check_feature_access(session['user_id'], 'numerology_chat'):
        return render_template('feature_locked.html', feature='numerology_chat'), 403

    return render_template("numerology_chat.html",
                           questions=NUMEROLOGY_QUESTIONS,
                           user_features=get_user_features(session.get('user_id', 0)),
                           user_sub_info=get_user_sub_info(session.get('user_id', 0)))


@app.route("/api/numerology/chat", methods=["POST"])
@login_required
def api_numerology_chat():
    """Handle numerology AI chat requests."""
    if not check_feature_access(session['user_id'], 'numerology_chat'):
        return jsonify({"success": False, "message": "AI চেট ফিচাৰ আপোনাৰ বাবে উপলব্ধ নহয়।"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request"}), 400

    question = data.get("question", "")
    name = data.get("name", "")
    dob = data.get("dob", "")

    if not question:
        return jsonify({"success": False, "message": "প্ৰশ্ন খালী"}), 400

    if not name or not dob:
        return jsonify({"success": False, "message": "নাম আৰু জন্ম তাৰিখ আৱশ্যক।"}), 400

    try:
        report = get_full_numerology_report(name, dob)
        response = chat_numerology(name, question, report)
        return jsonify({"success": True, "response": response})
    except Exception as e:
        logger.error(f"Numerology chat error: {e}")
        return jsonify({"success": False, "message": f"ত্ৰুটি: {str(e)}"}), 500


# ─── Admin API: Numerology Feature Toggles ───

@app.route("/admin/api/numerology-toggles", methods=["GET"])
@admin_required
def admin_api_get_numerology_toggles():
    """API: Get all numerology admin feature toggles."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM admin_feature_toggles WHERE category = 'numerology' ORDER BY id"
        ).fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


@app.route("/admin/api/numerology-toggles", methods=["POST"])
@admin_required
def admin_api_set_numerology_toggle():
    """API: Set a numerology admin feature toggle."""
    data = request.get_json()
    feature_key = data.get("feature_key", "")
    is_enabled = data.get("is_enabled", True)

    if not feature_key:
        return jsonify({"success": False, "message": "Feature key required."}), 400

    success = set_admin_feature_toggle(feature_key, is_enabled)
    return jsonify({
        "success": success,
        "message": "ফিচাৰ টগল আপডেট কৰা হৈছে।" if success else "আপডেট বিফল।"
    })


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
    lang = get_current_language()
    
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
                title = f"{name} {get_text('result_title', lang)} ({varga_code})"
            else:
                title = f"{get_text('result_kundli_chart', lang)} ({varga_code})"
        except Exception as e:
            logger.error(f"Chart image calculation error: {e}")
            title = f"{get_text('result_kundli_chart', lang)} ({varga_code})"
    
    try:
        if style == "all":
            buf = draw_all_styles(ascendant_index=ascendant_index, planet_data=planet_data, lang=lang)
        else:
            buf = draw_kundli_chart(
                style=style,
                ascendant_index=ascendant_index,
                planet_data=planet_data,
                title=title,
                lang=lang
            )
        return send_file(buf, mimetype="image/png")
    except Exception as e:
        logger.error(f"Chart drawing error: {e}")
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
#  যোটক মিলন / MARRIAGE MATCHING ROUTES (Jotok Milan)
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/jotok-milan")
def jotok_milan_page():
    """Marriage matching input form page."""
    user_features = get_user_features(session.get('user_id', 0))
    feature_defs = get_all_feature_definitions()
    return render_template("jotok_milan.html",
                           user_features=user_features,
                           feature_defs=feature_defs,
                           rashis=RASHIS,
                           nakshatras=NAKSHATRAS,
                           user_sub_info=get_user_sub_info(session.get('user_id', 0)))


@app.route("/jotok-milan/calculate", methods=["POST"])
def jotok_milan_calculate():
    """Calculate marriage matching (যোটক মিলন) result."""
    try:
        # Boy data - check for auto-calculated fields first, then fall back to manual
        boy_name = request.form.get("boy_name", "").strip()
        boy_rashi = request.form.get("boy_rashi_calc", "").strip() or request.form.get("boy_rashi", "").strip()
        boy_nakshatra = request.form.get("boy_nakshatra_calc", "").strip() or request.form.get("boy_nakshatra", "").strip()
        boy_charan = int(request.form.get("boy_charan_calc", "0") or request.form.get("boy_charan", "1"))
        boy_lagna = request.form.get("boy_lagna_calc", "").strip() or request.form.get("boy_lagna", "").strip()
        boy_mars_house = int(request.form.get("boy_mars_house_calc", "0") or request.form.get("boy_mars_house", "0"))

        # Girl data - check for auto-calculated fields first, then fall back to manual
        girl_name = request.form.get("girl_name", "").strip()
        girl_rashi = request.form.get("girl_rashi_calc", "").strip() or request.form.get("girl_rashi", "").strip()
        girl_nakshatra = request.form.get("girl_nakshatra_calc", "").strip() or request.form.get("girl_nakshatra", "").strip()
        girl_charan = int(request.form.get("girl_charan_calc", "0") or request.form.get("girl_charan", "1"))
        girl_lagna = request.form.get("girl_lagna_calc", "").strip() or request.form.get("girl_lagna", "").strip()
        girl_mars_house = int(request.form.get("girl_mars_house_calc", "0") or request.form.get("girl_mars_house", "0"))

        # Validate required fields
        if not boy_name or not girl_name:
            return render_template("jotok_milan.html",
                                   error="অনুগ্ৰহ কৰি পাত্ৰ আৰু পাত্ৰী উভয়ৰে নাম প্ৰদান কৰক।",
                                   rashis=RASHIS, nakshatras=NAKSHATRAS,
                                   user_features=get_user_features(session.get('user_id', 0)),
                                   feature_defs=get_all_feature_definitions())

        if not boy_rashi or not girl_rashi or not boy_nakshatra or not girl_nakshatra:
            return render_template("jotok_milan.html",
                                   error="অনুগ্ৰহ কৰি পাত্ৰ আৰু পাত্ৰী উভয়ৰে জন্মৰ সম্পূৰ্ণ তথ্য প্ৰদান কৰক। ৰাশি-নক্ষত্ৰ স্বয়ংক্ৰিয়ভাৱে গণনা কৰিবলৈ জন্ম তাৰিখ, সময়, আৰু স্থান দিয়ক।",
                                   rashis=RASHIS, nakshatras=NAKSHATRAS,
                                   user_features=get_user_features(session.get('user_id', 0)),
                                   feature_defs=get_all_feature_definitions())

        # Convert user inputs to Assamese for engine lookup
        from prediction_i18n import convert_nakshatra_to_asm, convert_rashi_to_asm
        user_lang = session.get('lang', 'as')
        boy_nakshatra_asm = convert_nakshatra_to_asm(boy_nakshatra, user_lang)
        girl_nakshatra_asm = convert_nakshatra_to_asm(girl_nakshatra, user_lang)
        boy_rashi_asm = convert_rashi_to_asm(boy_rashi, user_lang)
        girl_rashi_asm = convert_rashi_to_asm(girl_rashi, user_lang)

        boy_data = {
            "name": boy_name,
            "rashi": boy_rashi_asm,
            "nakshatra": boy_nakshatra_asm,
            "charan": boy_charan,
            "lagna": boy_lagna,
            "mars_house": boy_mars_house
        }

        girl_data = {
            "name": girl_name,
            "rashi": girl_rashi_asm,
            "nakshatra": girl_nakshatra_asm,
            "charan": girl_charan,
            "lagna": girl_lagna,
            "mars_house": girl_mars_house
        }

        # Calculate matching
        result = get_complete_jotok_milan(boy_data, girl_data)

        # Get subscription info for the result page
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
            subs = conn.execute("SELECT * FROM subscriptions WHERE is_active = 1 ORDER BY id").fetchall()
            all_subscriptions = [dict(s) for s in subs]
            conn.close()

        # Check if user can download PDF (subscription_id > 1 = paid user)
        can_download_pdf = user_subscription_id > 1

        # Get i18n labels for Jotok Milan
        from prediction_i18n import get_jotok_labels, translate_jotok_result
        jotok_lang = session.get('lang', 'as')
        jotok_labels = get_jotok_labels(jotok_lang)
        
        # Translate engine result to target language
        translated_result = translate_jotok_result(result, jotok_lang)

        return render_template("jotok_milan_result.html",
                               result=translated_result,
                               boy=translated_result['boy'],
                               girl=translated_result['girl'],
                               get_koota_name_asm=get_koota_name_asm,
                               get_koota_icon=get_koota_icon,
                               jotok_labels=jotok_labels,
                               user_features=get_user_features(session.get('user_id', 0)),
                               user_subscription_name=user_subscription_name,
                               user_subscription_id=user_subscription_id,
                               all_subscriptions=all_subscriptions,
                               can_download_pdf=can_download_pdf,
                               user_sub_info=get_user_sub_info(session.get('user_id', 0)))

    except Exception as e:
        logger.error(f"Jotok Milan calculation error: {e}")
        logger.error(traceback.format_exc())
        return render_template("jotok_milan.html",
                               error=f"গণনা ত্ৰুটি: {str(e)}",
                               rashis=RASHIS, nakshatras=NAKSHATRAS,
                               user_features=get_user_features(session.get('user_id', 0)),
                               feature_defs=get_all_feature_definitions())


@app.route("/api/jotok-calc-planets", methods=["POST"])
def api_jotok_calc_planets():
    """API: Auto-calculate rashi, nakshatra, lagna, and mars house from DOB/Time/Place."""
    try:
        data = request.get_json()
        dob = data.get("dob", "")
        tob = data.get("tob", "")
        lat = float(data.get("lat", 26.1445))
        lon = float(data.get("lon", 91.7362))

        if not dob or not tob:
            return jsonify({"error": "জন্ম তাৰিখ আৰু সময় আৱশ্যক।"}), 400

        # Use IST (UTC+5:30) as default for India
        tz_offset = 5.5

        ist_time = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
        jd = swe.julday(ist_time.year, ist_time.month, ist_time.day,
                        (ist_time.hour + ist_time.minute / 60.0) - tz_offset)

        swe.set_sid_mode(swe.SIDM_LAHIRI)
        ayanamsa = swe.get_ayanamsa(jd)

        # Moon position → Rashi & Nakshatra
        moon_pos, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        moon_lon = moon_pos[0]
        rasi_idx, rasi_name, rasi_deg = get_rasi_and_degree(moon_lon)
        nak_idx, nak_name, nak_lord = get_nakshatra_details(moon_lon)

        # Charan/Pada (1-4) based on degree within nakshatra
        # Each nakshatra spans 13°20' = 13.3333°, each charan = 3°20' = 3.3333°
        deg_in_nak = moon_lon % 13.333333
        charan = int(deg_in_nak / 3.333333) + 1  # 1-4

        # Lagna (Ascendant)
        cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        asc_sidereal = (ascmc[0] - ayanamsa) % 360
        asc_rasi_idx, asc_rasi, asc_deg = get_rasi_and_degree(asc_sidereal)

        # Mars position → House
        mars_pos, _ = swe.calc_ut(jd, swe.MARS, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        mars_lon = mars_pos[0]
        mars_house = (int(mars_lon / 30) - asc_rasi_idx) % 12 + 1  # 1-indexed

        # Check if Mangalik
        mangalik = mars_house in [1, 4, 7, 8, 12]

        return jsonify({
            "rashi": rasi_name,
            "nakshatra": nak_name,
            "charan": charan,
            "lagna": asc_rasi,
            "mars_house": mars_house,
            "mangalik": mangalik
        })

    except Exception as e:
        logger.error(f"Jotok planet calc error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"গণনা ত্ৰুটি: {str(e)}"}), 500


@app.route("/jotok-milan/download-pdf", methods=["POST"])
def jotok_milan_download_pdf():
    """Generate and download Jotok Milan PDF report."""
    try:
        # Boy data
        boy_name = request.form.get("boy_name", "").strip()
        boy_rashi = request.form.get("boy_rashi_calc", "").strip() or request.form.get("boy_rashi", "").strip()
        boy_nakshatra = request.form.get("boy_nakshatra_calc", "").strip() or request.form.get("boy_nakshatra", "").strip()
        boy_charan = int(request.form.get("boy_charan_calc", "0") or request.form.get("boy_charan", "1"))
        boy_lagna = request.form.get("boy_lagna_calc", "").strip() or request.form.get("boy_lagna", "").strip()
        boy_mars_house = int(request.form.get("boy_mars_house_calc", "0") or request.form.get("boy_mars_house", "0"))

        # Girl data
        girl_name = request.form.get("girl_name", "").strip()
        girl_rashi = request.form.get("girl_rashi_calc", "").strip() or request.form.get("girl_rashi", "").strip()
        girl_nakshatra = request.form.get("girl_nakshatra_calc", "").strip() or request.form.get("girl_nakshatra", "").strip()
        girl_charan = int(request.form.get("girl_charan_calc", "0") or request.form.get("girl_charan", "1"))
        girl_lagna = request.form.get("girl_lagna_calc", "").strip() or request.form.get("girl_lagna", "").strip()
        girl_mars_house = int(request.form.get("girl_mars_house_calc", "0") or request.form.get("girl_mars_house", "0"))

        # Convert user inputs to Assamese for engine lookup
        from prediction_i18n import convert_nakshatra_to_asm, convert_rashi_to_asm
        user_lang = session.get('lang', 'as')
        boy_nakshatra_asm = convert_nakshatra_to_asm(boy_nakshatra, user_lang)
        girl_nakshatra_asm = convert_nakshatra_to_asm(girl_nakshatra, user_lang)
        boy_rashi_asm = convert_rashi_to_asm(boy_rashi, user_lang)
        girl_rashi_asm = convert_rashi_to_asm(girl_rashi, user_lang)

        boy_data = {
            "name": boy_name, "rashi": boy_rashi_asm, "nakshatra": boy_nakshatra_asm,
            "charan": boy_charan, "lagna": boy_lagna, "mars_house": boy_mars_house
        }
        girl_data = {
            "name": girl_name, "rashi": girl_rashi_asm, "nakshatra": girl_nakshatra_asm,
            "charan": girl_charan, "lagna": girl_lagna, "mars_house": girl_mars_house
        }

        # Calculate matching
        result = get_complete_jotok_milan(boy_data, girl_data)

        # Get astrologer profile (user's profile first, fallback to admin)
        user_id = session.get('user_id', 0)
        astrologer_profile = get_astrologer_profile(user_id)

        # Generate PDF
        lang = session.get('lang', 'as')
        pdf_bytes = generate_jotok_milan_pdf(result, boy_data, girl_data, astrologer_profile, lang=lang)

        # Create filename
        filename = f"Jotok_Milan_{boy_name}_{girl_name}.pdf".replace(" ", "_")

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Jotok Milan PDF error: {e}")
        logger.error(traceback.format_exc())
        return f"<div style='padding:40px;text-align:center;font-family:sans-serif;'><h2 style='color:#C62828;'>PDF নিৰ্মাণ ত্ৰুটি</h2><p>{str(e)}</p><a href='/jotok-milan'>আকৌ চেষ্টা কৰক</a></div>", 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
