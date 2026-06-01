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
    get_abhijit_muhurta, get_yama_kaal, get_kaal_bela, get_rar_bela,
    get_divaman, get_ratriman, get_nakshatra_attributes, get_rashi_lord,
    get_julian_day, TITHI_NAMES, NAKSHATRA_NAMES, YOGA_NAMES, KARANA_NAMES,
    VAAR_NAMES, RITU_NAMES, MASA_NAMES, PAKSHA_NAMES,
    VARNA_NAMES, GANA_NAMES, NADI_NAMES, RASHI_LORDS
)

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


def _find_tithi_boundary(dt, lat, lon, tz_offset, current_idx, direction='forward'):
    """Find tithi boundary time."""
    def calc_tithi_idx(sun_lon, moon_lon):
        return calculate_tithi(sun_lon, moon_lon)
    return _find_element_boundary(dt, lat, lon, tz_offset, calc_tithi_idx, current_idx, direction)


def _find_nakshatra_boundary(dt, lat, lon, tz_offset, current_idx, direction='forward'):
    """Find nakshatra boundary time."""
    def calc_nak_idx(sun_lon, moon_lon):
        return calculate_nakshatra(moon_lon)
    return _find_element_boundary(dt, lat, lon, tz_offset, calc_nak_idx, current_idx, direction)


def _find_yoga_boundary(dt, lat, lon, tz_offset, current_idx, direction='forward'):
    """Find yoga boundary time."""
    def calc_yoga_idx(sun_lon, moon_lon):
        return calculate_yoga(sun_lon, moon_lon)
    return _find_element_boundary(dt, lat, lon, tz_offset, calc_yoga_idx, current_idx, direction)


def _find_karana_boundary(dt, lat, lon, tz_offset, current_idx, direction='forward'):
    """Find karana boundary time."""
    def calc_karana_idx(sun_lon, moon_lon):
        tithi = calculate_tithi(sun_lon, moon_lon)
        karana = calculate_karana(tithi["index"], tithi["remaining_pct"])
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


def get_all_planet_positions(dt: datetime) -> list:
    """
    Get current planetary positions (sidereal, Lahiri ayanamsa).
    Returns list of dicts with planet name, longitude, rashi, degree, etc.
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
                "name_asm": PLANET_NAMES_ASM.get(name, name),
                "icon": PLANET_ICONS.get(name, "⭐"),
                "longitude": round(lon, 4),
                "rashi_index": rashi_idx,
                "rashi_name": RASHI_NAMES_ASM[rashi_idx],
                "rashi_icon": RASHI_ICONS[rashi_idx],
                "degree": deg,
                "minutes": minutes,
                "seconds": seconds,
                "degree_str": f"{deg}°{minutes}'{seconds}\"",
                "retrograde": retro,
                "rashi_lord": RASHI_LORDS[rashi_idx],
            })
        except Exception as e:
            planets.append({
                "name": name,
                "name_asm": PLANET_NAMES_ASM.get(name, name),
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
                "name_asm": PLANET_NAMES_ASM.get("Ketu", "কেতু"),
                "icon": PLANET_ICONS.get("Ketu", "🐍"),
                "longitude": round(ketu_lon, 4),
                "rashi_index": ketu_rashi,
                "rashi_name": RASHI_NAMES_ASM[ketu_rashi],
                "rashi_icon": RASHI_ICONS[ketu_rashi],
                "degree": kd,
                "minutes": km,
                "seconds": ks,
                "degree_str": f"{kd}°{km}'{ks}\"",
                "retrograde": False,
                "rashi_lord": RASHI_LORDS[ketu_rashi],
            })
            break

    return planets


def get_panchanga_with_times(dt: datetime, lat: float, lon: float, tz_offset: float = 5.5) -> dict:
    """
    Calculate complete Panchanga with precise From-To time ranges.
    Also includes planetary positions.
    """
    # Get base panchanga
    panchanga = get_full_panchanga(dt, lat, lon, tz_offset)

    # Get current indices
    tithi_idx = panchanga["tithi"]["index"]
    nak_idx = panchanga["nakshatra"]["index"]
    yoga_idx = panchanga["yoga"]["index"]
    karana_idx = panchanga["karana"]["index"]

    # Find boundaries for each element
    # ─── Tithi ───
    try:
        tithi_start = _find_tithi_boundary(dt, lat, lon, tz_offset, tithi_idx, 'backward')
        tithi_end = _find_tithi_boundary(dt, lat, lon, tz_offset, tithi_idx, 'forward')
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
        nak_start = _find_nakshatra_boundary(dt, lat, lon, tz_offset, nak_idx, 'backward')
        nak_end = _find_nakshatra_boundary(dt, lat, lon, tz_offset, nak_idx, 'forward')
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
        yoga_start = _find_yoga_boundary(dt, lat, lon, tz_offset, yoga_idx, 'backward')
        yoga_end = _find_yoga_boundary(dt, lat, lon, tz_offset, yoga_idx, 'forward')
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
        karana_start = _find_karana_boundary(dt, lat, lon, tz_offset, karana_idx, 'backward')
        karana_end = _find_karana_boundary(dt, lat, lon, tz_offset, karana_idx, 'forward')
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

    # Add planetary positions
    try:
        panchanga["planets"] = get_all_planet_positions(dt)
    except:
        panchanga["planets"] = []

    # Add current date/time info
    panchanga["current_date"] = dt.strftime("%d/%m/%Y")
    panchanga["current_time"] = dt.strftime("%H:%M")
    panchanga["location_name"] = f"Lat: {lat:.4f}, Lon: {lon:.4f}"

    return panchanga
