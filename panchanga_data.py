"""
ধ্ৰুৱতৰা AI - পঞ্চাঙ্গ ডাটা মডিউল (সময়সীমা সহিত)
Panchanga Data Module with precise From-To time ranges for each element.
Includes: Tithi, Nakshatra, Yoga, Karana, Vaar, Paksha, Ritu, Masa,
Rahu Kaal, Yama Gandam, Gulika Kaal, Abhijit Muhurta, and more.
Also provides current planetary positions.
"""

import swisseph as swe
from datetime import datetime, timedelta
from panchanga import (
    get_full_panchanga, calculate_sun_moon, calculate_tithi, calculate_nakshatra,
    calculate_yoga, calculate_karana, calculate_vaar, calculate_ritu, calculate_masa,
    calculate_ayanamsa, calculate_sunrise, calculate_sunset,
    get_rahu_kalam, get_yama_gandam, get_gulika_kalam,
    get_abhijit_muhurta, get_yama_kaal, get_kaal_bela, get_rar_bela, get_bara_bela,
    get_divaman, get_ratriman, get_nakshatra_attributes, get_rashi_lord,
    get_julian_day
)
from prediction_i18n import get_panchanga_names_i18n, get_panchanga_planet_name_i18n, get_panchanga_rashi_name_i18n, get_panchanga_yogini_direction_i18n

# ─── Planet names in Assamese ───────────────────────────────────
PLANET_NAMES_ASM = {
    "Sun": "ৰবি (সূৰ্য্য)",
    "Moon": "চন্দ্ৰ",
    "Mars": "মংগল",
    "Mercury": "বুধ",
    "Jupiter": "বৃহস্পতি",
    "Venus": "শুক্ৰ",
    "Saturn": "শনি",
    "Rahu": "ৰাহু",
    "Ketu": "কেতু",
}

PLANET_ICONS = {
    "Sun": "☀️", "Moon": "🌙", "Mars": "🔴", "Mercury": "🟢",
    "Jupiter": "🟡", "Venus": "⚪", "Saturn": "🪐", "Rahu": "🐉", "Ketu": "🐍",
}

PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# ─── Rashi names in Assamese ────────────────────────────────────
RASHI_NAMES_ASM = [
    "মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা",
    "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"
]

RASHI_ICONS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

# ─── Yogini Direction by Tithi Number (1-30) ───────────────────
# Pattern: 8-direction cycle with specific mapping
YOGINI_DIRECTIONS = {
    1: "পূব", 2: "উত্তৰ", 3: "অগ্নিকোণ", 4: "নৈঋৎকোণ",
    5: "দক্ষিণ", 6: "পশ্চিম", 7: "বায়ুকোণ", 8: "ইশানকোণ",
    9: "পূব", 10: "উত্তৰ", 11: "অগ্নিকোণ", 12: "নৈঋৎকোণ",
    13: "দক্ষিণ", 14: "পশ্চিম", 15: "বায়ুকোণ",
    16: "পূব", 17: "উত্তৰ", 18: "অগ্নিকোণ", 19: "নৈঋৎকোণ",
    20: "দক্ষিণ", 21: "পশ্চিম", 22: "বায়ুকোণ", 23: "ইশানকোণ",
    24: "পূব", 25: "উত্তৰ", 26: "অগ্নিকোণ", 27: "নৈঋৎকোণ",
    28: "দক্ষিণ", 29: "পশ্চিম", 30: "ইশানকোণ",
}

# Direction icons for visual display
YOGINI_DIRECTION_ICONS = {
    "পূব": "➡️", "উত্তৰ": "⬆️", "অগ্নিকোণ": "↗️", "নৈঋৎকোণ": "↙️",
    "দক্ষিণ": "⬇️", "পশ্চিম": "⬅️", "বায়ুকোণ": "↖️", "ইশানকোণ": "↗️",
}

# ─── Nishedh Khadya (Forbidden Food) by Tithi Number (1-30) ────
NISHEDH_KHADYA = {
    1: "কোমোৰা", 2: "তিতা", 3: "পটল", 4: "মূলা",
    5: "বেল", 6: "নিমতিতা", 7: "তাল", 8: "নাৰিকল",
    9: "লাউ", 10: "কলম শাক", 11: "উৰহী", 12: "পুইশাক",
    13: "বেঙেনা", 14: "মাহ, মাছ-মাংস", 15: "মাছ-মাংস, তেল, সদ্ভোগ",
    16: "কোমোৰা", 17: "তিতা", 18: "পটল", 19: "মূলা",
    20: "বেল", 21: "নিমতিতা", 22: "তাল", 23: "নাৰিকল",
    24: "লাউ", 25: "কলম শাক", 26: "উৰহী", 27: "পুইশাক",
    28: "বেঙেনা", 29: "মাহ, মাছ-মাংস", 30: "মাছ-মাংস, তেল, সদ্ভোগ",
}


def get_yogini_direction(tithi_number: int) -> str:
    """Get Yogini direction for a given tithi number (1-30)."""
    return YOGINI_DIRECTIONS.get(tithi_number, "")


def get_yogini_direction_icon(direction: str) -> str:
    """Get icon for Yogini direction."""
    return YOGINI_DIRECTION_ICONS.get(direction, "🧭")


def get_nishedh_khadya(tithi_number: int) -> str:
    """Get forbidden food for a given tithi number (1-30)."""
    return NISHEDH_KHADYA.get(tithi_number, "")


# ─── Maran Dosh (মৰণ দোষ) ─────────────────────────────────────
# Baar Dosh: Sunday(6), Tuesday(1), Saturday(5) → 1 pad
MARAN_BAAR_DOSH_VAAR_INDICES = {6, 1, 5}  # 0=Mon...6=Sun

# Tithi Dosh: tithi numbers 2,7,12,17,22,27,29 → 1 pad (1-indexed)
MARAN_TITHI_DOSH_NUMBERS = {2, 7, 12, 17, 22, 27, 29}

# Nakshatra Dosh: nakshatra numbers 3,7,12,16,21,25 → 2 pad (1-indexed)
MARAN_NAKSHATRA_DOSH_NUMBERS = {3, 7, 12, 16, 21, 25}

# Vaar names in Assamese for display
VAAR_NAMES_MARAN = ["সোমবাৰ", "মংগলবাৰ", "বুধবাৰ", "বৃহস্পতিবাৰ", "শুক্ৰবাৰ", "শনিবাৰ", "ৰবিবাৰ"]


def get_maran_dosh(vaar_index: int, tithi_num_full: int, nak_num_full: int) -> dict:
    """
    Calculate Maran Dosh based on Vaar, Tithi, and Nakshatra.
    vaar_index: 0=Mon...6=Sun
    tithi_num_full: 1-30
    nak_num_full: 1-27 (1-indexed nakshatra number)
    
    Returns dict with:
    - baar_dosh: bool, baar_dosh_pad: int, baar_dosh_text: str
    - tithi_dosh: bool, tithi_dosh_pad: int, tithi_dosh_text: str
    - nakshatra_dosh: bool, nakshatra_dosh_pad: int, nakshatra_dosh_text: str
    - total_pad: int, combined_name: str, combined_result: str
    """
    result = {
        "baar_dosh": False, "baar_dosh_pad": 0, "baar_dosh_text": "",
        "tithi_dosh": False, "tithi_dosh_pad": 0, "tithi_dosh_text": "",
        "nakshatra_dosh": False, "nakshatra_dosh_pad": 0, "nakshatra_dosh_text": "",
        "total_pad": 0, "combined_name": "", "combined_result": "",
        "has_any_dosh": False,
    }

    vaar_name = VAAR_NAMES_MARAN[vaar_index] if 0 <= vaar_index <= 6 else ""

    # ─── Baar Dosh ───
    if vaar_index in MARAN_BAAR_DOSH_VAAR_INDICES:
        result["baar_dosh"] = True
        result["baar_dosh_pad"] = 1
        result["baar_dosh_text"] = f"{vaar_name}ৰ মৰণত বাৰ দোষ পায় | এপদ | বাৰদোষ ফল- উপাৰ্জন হ্ৰাস |"
    else:
        result["baar_dosh_text"] = f"{vaar_name}ৰ মৰণত বাৰ দোষ নহয় |"

    # ─── Tithi Dosh ───
    if tithi_num_full in MARAN_TITHI_DOSH_NUMBERS:
        result["tithi_dosh"] = True
        result["tithi_dosh_pad"] = 1
        result["tithi_dosh_text"] = f"তিথি {tithi_num_full} ত মৰণত তিথি দোষ পায় | এপদ | তিথিদোষ ফল- উপাৰ্জন হ্ৰাস |"
    else:
        result["tithi_dosh_text"] = f"তিথি {tithi_num_full} ত মৰণত তিথি দোষ নাই |"

    # ─── Nakshatra Dosh ───
    if nak_num_full in MARAN_NAKSHATRA_DOSH_NUMBERS:
        result["nakshatra_dosh"] = True
        result["nakshatra_dosh_pad"] = 2
        result["nakshatra_dosh_text"] = f"নক্ষত্ৰ {nak_num_full} ত মৰণত নক্ষত্ৰ দোষ হয় | দ্বিপদ | নক্ষত্ৰদোষ ফল – জীৱ হানি, আত্মীয় বিৰোধ |"
    else:
        result["nakshatra_dosh_text"] = f"নক্ষত্ৰ {nak_num_full} ত মৰণত নক্ষত্ৰ দোষ নাই |"

    # ─── Combined ───
    total = result["baar_dosh_pad"] + result["tithi_dosh_pad"] + result["nakshatra_dosh_pad"]
    result["total_pad"] = total
    result["has_any_dosh"] = result["baar_dosh"] or result["tithi_dosh"] or result["nakshatra_dosh"]

    if result["baar_dosh"] and result["tithi_dosh"] and result["nakshatra_dosh"]:
        result["combined_name"] = "চতুস্পাদ (পুষ্কৰ)"
        result["combined_result"] = "বাৰদোষ ১ + তিথিদোষ ১ + নক্ষত্ৰদোষ ২ = ৪ চতুস্পাদ (পুষ্কৰ) | ফল- গোত্ৰহানি, সৰ্বক্ষতি |"
    elif result["baar_dosh"] and result["tithi_dosh"]:
        result["combined_name"] = "দ্বিপাদ"
        result["combined_result"] = "বাৰদোষ ১ + তিথিদোষ ১ = দ্বিপাদ |"
    elif result["baar_dosh"] and result["nakshatra_dosh"]:
        result["combined_name"] = "ত্ৰিপাদ"
        result["combined_result"] = "বাৰদোষ ১ + নক্ষত্ৰদোষ ২ = ত্ৰিপাদ |"
    elif result["tithi_dosh"] and result["nakshatra_dosh"]:
        result["combined_name"] = "ত্ৰিপাদ"
        result["combined_result"] = "তিথিদোষ ১ + নক্ষত্ৰদোষ ২ = ত্ৰিপাদ |"
    elif result["baar_dosh"]:
        result["combined_name"] = "এপদ"
        result["combined_result"] = "কেৱল বাৰ দোষ (এপদ) | ফল- উপাৰ্জন হ্ৰাস |"
    elif result["tithi_dosh"]:
        result["combined_name"] = "এপদ"
        result["combined_result"] = "কেৱল তিথি দোষ (এপদ) | ফল- উপাৰ্জন হ্ৰাস |"
    elif result["nakshatra_dosh"]:
        result["combined_name"] = "দ্বিপদ"
        result["combined_result"] = "কেৱল নক্ষত্ৰ দোষ (দ্বিপদ) | ফল- জীৱ হানি, আত্মীয় বিৰোধ |"
    else:
        result["combined_name"] = "দোষমুক্ত"
        result["combined_result"] = "মৰণত কোনো দোষ নাই |"

    return result


def _find_element_boundary(dt, lat, lon, tz_offset, calc_func, current_idx, direction='forward'):
    """
    Find when an element (tithi/nakshatra/yoga/karana) changes.
    Uses binary search for precision.
    direction: 'forward' to find end, 'backward' to find start
    """
    step_minutes = 60  # Start with 1-hour steps
    max_iterations = 200
    current = dt

    # Coarse search - step until index changes
    for _ in range(max_iterations):
        if direction == 'forward':
            current = current + timedelta(minutes=step_minutes)
        else:
            current = current - timedelta(minutes=step_minutes)

        jd = get_julian_day(current)
        sun_lon, moon_lon = calculate_sun_moon(jd)
        result = calc_func(sun_lon, moon_lon)
        new_idx = result["index"] if isinstance(result, dict) else result

        if new_idx != current_idx:
            # Found the boundary, now refine with binary search
            if direction == 'forward':
                lo = current - timedelta(minutes=step_minutes)
                hi = current
            else:
                lo = current
                hi = current + timedelta(minutes=step_minutes)

            # Binary search for precision (down to ~1 second)
            for _ in range(30):
                mid = lo + (hi - lo) / 2
                jd_mid = get_julian_day(mid)
                sun_lon_mid, moon_lon_mid = calculate_sun_moon(jd_mid)
                mid_result = calc_func(sun_lon_mid, moon_lon_mid)
                mid_idx = mid_result["index"] if isinstance(mid_result, dict) else mid_result

                if mid_idx == current_idx:
                    if direction == 'forward':
                        lo = mid
                    else:
                        hi = mid
                else:
                    if direction == 'forward':
                        hi = mid
                    else:
                        lo = mid

            return lo + (hi - lo) / 2

    # Fallback: estimate based on average duration
    if direction == 'forward':
        return dt + timedelta(hours=12)
    else:
        return dt - timedelta(hours=12)


def _find_tithi_boundary(dt, lat, lon, tz_offset, current_idx, direction='forward', lang='as'):
    """Find tithi boundary time."""
    def calc_tithi_idx(sun_lon, moon_lon):
        return calculate_tithi(sun_lon, moon_lon, lang)
    return _find_element_boundary(dt, lat, lon, tz_offset, calc_tithi_idx, current_idx, direction)


def _find_nakshatra_boundary(dt, lat, lon, tz_offset, current_idx, direction='forward', lang='as'):
    """Find nakshatra boundary time."""
    def calc_nak_idx(sun_lon, moon_lon):
        return calculate_nakshatra(moon_lon, lang)
    return _find_element_boundary(dt, lat, lon, tz_offset, calc_nak_idx, current_idx, direction)


def _find_yoga_boundary(dt, lat, lon, tz_offset, current_idx, direction='forward', lang='as'):
    """Find yoga boundary time."""
    def calc_yoga_idx(sun_lon, moon_lon):
        return calculate_yoga(sun_lon, moon_lon, lang)
    return _find_element_boundary(dt, lat, lon, tz_offset, calc_yoga_idx, current_idx, direction)


def _find_karana_boundary(dt, lat, lon, tz_offset, current_idx, direction='forward', lang='as'):
    """Find karana boundary time."""
    def calc_karana_idx(sun_lon, moon_lon):
        tithi = calculate_tithi(sun_lon, moon_lon, lang)
        karana = calculate_karana(tithi["index"], tithi["remaining_pct"], lang)
        return karana
    return _find_element_boundary(dt, lat, lon, tz_offset, calc_karana_idx, current_idx, direction)


def _format_boundary_time(boundary_dt, tz_offset):
    """Format a boundary datetime to HH:MM string.
    The boundary_dt is already in local time (from the search which uses local datetimes)."""
    return boundary_dt.strftime("%H:%M")


def _format_boundary_date_time(boundary_dt, tz_offset):
    """Format boundary datetime to full date-time string (already local time)."""
    return boundary_dt.strftime("%d/%m/%Y %H:%M")


def _is_previous_day(boundary_dt, current_dt):
    """Check if boundary datetime is from previous day."""
    return boundary_dt.date() < current_dt.date()


def _is_next_day(boundary_dt, current_dt):
    """Check if boundary datetime is on next day."""
    return boundary_dt.date() > current_dt.date()


def _get_next_element_name(current_idx, names_list, prefix=""):
    """Get the name of the next element in a cyclic list."""
    next_idx = (current_idx + 1) % len(names_list)
    return f"{prefix}{names_list[next_idx]}"


def get_all_planet_positions(dt: datetime, lang: str = 'as') -> list:
    """
    Get current planetary positions (sidereal, Lahiri ayanamsa).
    Returns list of dicts with planet name, longitude, rashi, degree, etc.
    lang: language code ('as', 'bn', 'hi', 'en')
    """
    jd = get_julian_day(dt)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    planet_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE,  # Mean North Node (Rahu)
    }

    planets = []

    for name, pid in planet_ids.items():
        try:
            pos, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            lon = pos[0] % 360
            rashi_idx = int(lon / 30)
            degree_in_rashi = lon % 30
            deg = int(degree_in_rashi)
            min_part = (degree_in_rashi - deg) * 60
            minutes = int(min_part)
            seconds = int((min_part - minutes) * 60)

            # Retrograde check
            retro = pos[3] < 0 if len(pos) > 3 else False

            planets.append({
                "name": name,
                "name_asm": get_panchanga_planet_name_i18n(name, lang),
                "icon": PLANET_ICONS.get(name, "⭐"),
                "longitude": round(lon, 4),
                "rashi_index": rashi_idx,
                "rashi_name": get_panchanga_rashi_name_i18n(rashi_idx, lang),
                "rashi_icon": RASHI_ICONS[rashi_idx],
                "degree": deg,
                "minutes": minutes,
                "seconds": seconds,
                "degree_str": f"{deg}°{minutes}'{seconds}\"",
                "retrograde": retro,
                "rashi_lord": get_rashi_lord(rashi_idx, lang),
            })
        except Exception as e:
            planets.append({
                "name": name,
                "name_asm": get_panchanga_planet_name_i18n(name, lang),
                "icon": PLANET_ICONS.get(name, "⭐"),
                "error": str(e),
            })

    # Calculate Ketu (180° opposite to Rahu)
    for p in planets:
        if p["name"] == "Rahu" and "longitude" in p:
            ketu_lon = (p["longitude"] + 180) % 360
            ketu_rashi = int(ketu_lon / 30)
            ketu_deg_in_rashi = ketu_lon % 30
            kd = int(ketu_deg_in_rashi)
            km = int((ketu_deg_in_rashi - kd) * 60)
            ks = int((((ketu_deg_in_rashi - kd) * 60) - km) * 60)
            planets.append({
                "name": "Ketu",
                "name_asm": get_panchanga_planet_name_i18n("Ketu", lang),
                "icon": PLANET_ICONS.get("Ketu", "🐍"),
                "longitude": round(ketu_lon, 4),
                "rashi_index": ketu_rashi,
                "rashi_name": get_panchanga_rashi_name_i18n(ketu_rashi, lang),
                "rashi_icon": RASHI_ICONS[ketu_rashi],
                "degree": kd,
                "minutes": km,
                "seconds": ks,
                "degree_str": f"{kd}°{km}'{ks}\"",
                "retrograde": False,
                "rashi_lord": get_rashi_lord(ketu_rashi, lang),
            })
            break

    return planets


def get_panchanga_with_times(dt: datetime, lat: float, lon: float, tz_offset: float = 5.5, lang: str = 'as') -> dict:
    """
    Calculate complete Panchanga with precise From-To time ranges.
    Also includes planetary positions.
    lang: language code ('as', 'bn', 'hi', 'en')
    """
    names = get_panchanga_names_i18n(lang)
    TITHI_NAMES = names['TITHI_NAMES']
    NAKSHATRA_NAMES = names['NAKSHATRA_NAMES']
    YOGA_NAMES = names['YOGA_NAMES']
    KARANA_NAMES = names['KARANA_NAMES']
    PAKSHA_NAMES = names['PAKSHA_NAMES']

    # Get base panchanga
    panchanga = get_full_panchanga(dt, lat, lon, tz_offset, lang)

    # Get current indices
    tithi_idx = panchanga["tithi"]["index"]
    nak_idx = panchanga["nakshatra"]["index"]
    yoga_idx = panchanga["yoga"]["index"]
    karana_idx = panchanga["karana"]["index"]

    # Find boundaries for each element
    # ─── Tithi ───
    try:
        tithi_start = _find_tithi_boundary(dt, lat, lon, tz_offset, tithi_idx, 'backward', lang)
        tithi_end = _find_tithi_boundary(dt, lat, lon, tz_offset, tithi_idx, 'forward', lang)
        panchanga["tithi"]["time_from"] = _format_boundary_time(tithi_start, tz_offset)
        panchanga["tithi"]["time_to"] = _format_boundary_time(tithi_end, tz_offset)
        panchanga["tithi"]["datetime_from"] = _format_boundary_date_time(tithi_start, tz_offset)
        panchanga["tithi"]["datetime_to"] = _format_boundary_date_time(tithi_end, tz_offset)
        panchanga["tithi"]["from_prev_day"] = _is_previous_day(tithi_start, dt)
        panchanga["tithi"]["to_next_day"] = _is_next_day(tithi_end, dt)
        # Next tithi
        next_tithi_idx = (tithi_idx + 1) % 30
        panchanga["tithi"]["next_name"] = TITHI_NAMES[next_tithi_idx]
        panchanga["tithi"]["next_paksha"] = PAKSHA_NAMES[0] if next_tithi_idx < 15 else PAKSHA_NAMES[1]
    except:
        panchanga["tithi"]["time_from"] = "--:--"
        panchanga["tithi"]["time_to"] = "--:--"
        panchanga["tithi"]["from_prev_day"] = False
        panchanga["tithi"]["to_next_day"] = False
        panchanga["tithi"]["next_name"] = ""

    # ─── Nakshatra ───
    try:
        nak_start = _find_nakshatra_boundary(dt, lat, lon, tz_offset, nak_idx, 'backward', lang)
        nak_end = _find_nakshatra_boundary(dt, lat, lon, tz_offset, nak_idx, 'forward', lang)
        panchanga["nakshatra"]["time_from"] = _format_boundary_time(nak_start, tz_offset)
        panchanga["nakshatra"]["time_to"] = _format_boundary_time(nak_end, tz_offset)
        panchanga["nakshatra"]["datetime_from"] = _format_boundary_date_time(nak_start, tz_offset)
        panchanga["nakshatra"]["datetime_to"] = _format_boundary_date_time(nak_end, tz_offset)
        panchanga["nakshatra"]["from_prev_day"] = _is_previous_day(nak_start, dt)
        panchanga["nakshatra"]["to_next_day"] = _is_next_day(nak_end, dt)
        # Next nakshatra
        next_nak_idx = (nak_idx + 1) % 27
        panchanga["nakshatra"]["next_name"] = NAKSHATRA_NAMES[next_nak_idx]
    except:
        panchanga["nakshatra"]["time_from"] = "--:--"
        panchanga["nakshatra"]["time_to"] = "--:--"
        panchanga["nakshatra"]["from_prev_day"] = False
        panchanga["nakshatra"]["to_next_day"] = False
        panchanga["nakshatra"]["next_name"] = ""

    # ─── Yoga ───
    try:
        yoga_start = _find_yoga_boundary(dt, lat, lon, tz_offset, yoga_idx, 'backward', lang)
        yoga_end = _find_yoga_boundary(dt, lat, lon, tz_offset, yoga_idx, 'forward', lang)
        panchanga["yoga"]["time_from"] = _format_boundary_time(yoga_start, tz_offset)
        panchanga["yoga"]["time_to"] = _format_boundary_time(yoga_end, tz_offset)
        panchanga["yoga"]["datetime_from"] = _format_boundary_date_time(yoga_start, tz_offset)
        panchanga["yoga"]["datetime_to"] = _format_boundary_date_time(yoga_end, tz_offset)
        panchanga["yoga"]["from_prev_day"] = _is_previous_day(yoga_start, dt)
        panchanga["yoga"]["to_next_day"] = _is_next_day(yoga_end, dt)
        # Next yoga
        next_yoga_idx = (yoga_idx + 1) % 27
        panchanga["yoga"]["next_name"] = YOGA_NAMES[next_yoga_idx]
    except:
        panchanga["yoga"]["time_from"] = "--:--"
        panchanga["yoga"]["time_to"] = "--:--"
        panchanga["yoga"]["from_prev_day"] = False
        panchanga["yoga"]["to_next_day"] = False
        panchanga["yoga"]["next_name"] = ""

    # ─── Karana ───
    try:
        karana_start = _find_karana_boundary(dt, lat, lon, tz_offset, karana_idx, 'backward', lang)
        karana_end = _find_karana_boundary(dt, lat, lon, tz_offset, karana_idx, 'forward', lang)
        panchanga["karana"]["time_from"] = _format_boundary_time(karana_start, tz_offset)
        panchanga["karana"]["time_to"] = _format_boundary_time(karana_end, tz_offset)
        panchanga["karana"]["datetime_from"] = _format_boundary_date_time(karana_start, tz_offset)
        panchanga["karana"]["datetime_to"] = _format_boundary_date_time(karana_end, tz_offset)
        panchanga["karana"]["from_prev_day"] = _is_previous_day(karana_start, dt)
        panchanga["karana"]["to_next_day"] = _is_next_day(karana_end, dt)
        # Next karana
        next_karana_idx = (karana_idx + 1) % 11
        panchanga["karana"]["next_name"] = KARANA_NAMES[next_karana_idx]
    except:
        panchanga["karana"]["time_from"] = "--:--"
        panchanga["karana"]["time_to"] = "--:--"
        panchanga["karana"]["from_prev_day"] = False
        panchanga["karana"]["to_next_day"] = False
        panchanga["karana"]["next_name"] = ""

    # Add Nakshatra attributes with time ranges
    nak_attrs = panchanga.get("varna", ""), panchanga.get("gana", ""), panchanga.get("yoni", ""), panchanga.get("nadi", "")
    # These attributes last as long as the nakshatra, so same time range
    panchanga["varna_time_from"] = panchanga["nakshatra"].get("time_from", "--:--")
    panchanga["varna_time_to"] = panchanga["nakshatra"].get("time_to", "--:--")
    panchanga["gana_time_from"] = panchanga["nakshatra"].get("time_from", "--:--")
    panchanga["gana_time_to"] = panchanga["nakshatra"].get("time_to", "--:--")
    panchanga["yoni_time_from"] = panchanga["nakshatra"].get("time_from", "--:--")
    panchanga["yoni_time_to"] = panchanga["nakshatra"].get("time_to", "--:--")
    panchanga["nadi_time_from"] = panchanga["nakshatra"].get("time_from", "--:--")
    panchanga["nadi_time_to"] = panchanga["nakshatra"].get("time_to", "--:--")

    # ─── Next Nakshatra Attributes (for days with 2 nakshatras) ───
    if panchanga["nakshatra"].get("to_next_day") and panchanga["nakshatra"].get("next_name"):
        next_nak_idx = (panchanga["nakshatra"]["index"] + 1) % 27
        next_attrs = get_nakshatra_attributes(next_nak_idx, lang)
        panchanga["next_varna"] = next_attrs["varna"]
        panchanga["next_gana"] = next_attrs["gana"]
        panchanga["next_yoni"] = next_attrs["yoni"]
        panchanga["next_nadi"] = next_attrs["nadi"]
        # Next nakshatra attributes start after current nakshatra ends
        panchanga["next_varna_time_from"] = panchanga["nakshatra"].get("time_to", "--:--")
        panchanga["next_varna_time_to"] = "--:--" + names['next_day_suffix']
        panchanga["next_gana_time_from"] = panchanga["nakshatra"].get("time_to", "--:--")
        panchanga["next_gana_time_to"] = "--:--" + names['next_day_suffix']
        panchanga["next_yoni_time_from"] = panchanga["nakshatra"].get("time_to", "--:--")
        panchanga["next_yoni_time_to"] = "--:--" + names['next_day_suffix']
        panchanga["next_nadi_time_from"] = panchanga["nakshatra"].get("time_to", "--:--")
        panchanga["next_nadi_time_to"] = "--:--" + names['next_day_suffix']

    # Add planetary positions
    try:
        panchanga["planets"] = get_all_planet_positions(dt, lang)
    except:
        panchanga["planets"] = []

    # Add current date/time info
    panchanga["current_date"] = dt.strftime("%d/%m/%Y")
    panchanga["current_time"] = dt.strftime("%H:%M")
    panchanga["location_name"] = f"Lat: {lat:.4f}, Lon: {lon:.4f}"

    # ─── Yogini Direction & Nishedh Khadya ───
    # Tithi number 1-30 (full cycle) for yogini/khadya mapping
    tithi_num_full = tithi_idx + 1  # 1-30
    panchanga["yogini_direction"] = get_yogini_direction(tithi_num_full)
    panchanga["yogini_direction_icon"] = get_yogini_direction_icon(panchanga["yogini_direction"])
    panchanga["nishedh_khadya"] = get_nishedh_khadya(tithi_num_full)

    # Next tithi info (for days with 2 tithis)
    next_tithi_idx = (tithi_idx + 1) % 30
    next_tithi_num_full = next_tithi_idx + 1
    panchanga["next_yogini_direction"] = get_yogini_direction(next_tithi_num_full)
    panchanga["next_yogini_direction_icon"] = get_yogini_direction_icon(panchanga["next_yogini_direction"])
    panchanga["next_nishedh_khadya"] = get_nishedh_khadya(next_tithi_num_full)

    # ─── Maran Dosh (মৰণ দোষ) ───
    vaar_idx = panchanga["vaar"]["index"]  # 0=Mon...6=Sun
    nak_num_full = nak_idx + 1  # 1-27 (1-indexed)
    next_nak_idx = (nak_idx + 1) % 27
    next_nak_num_full = next_nak_idx + 1

    # Current tithi + current nakshatra maran dosh
    panchanga["maran_dosh"] = get_maran_dosh(vaar_idx, tithi_num_full, nak_num_full)

    # Next tithi + next nakshatra maran dosh (for days with 2 tithis/nakshatras)
    panchanga["maran_dosh_next_tithi"] = get_maran_dosh(vaar_idx, next_tithi_num_full, nak_num_full)
    panchanga["maran_dosh_next_nak"] = get_maran_dosh(vaar_idx, tithi_num_full, next_nak_num_full)
    panchanga["maran_dosh_next_both"] = get_maran_dosh(vaar_idx, next_tithi_num_full, next_nak_num_full)

    # Flags for whether next tithi/nakshatra exist in this day
    panchanga["has_next_tithi_today"] = panchanga["tithi"].get("to_next_day", False)
    panchanga["has_next_nak_today"] = panchanga["nakshatra"].get("to_next_day", False)

    return panchanga
