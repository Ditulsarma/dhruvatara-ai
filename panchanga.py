"""
ধ্ৰুৱতৰা AI - পঞ্চাঙ্গ গণনা ইঞ্জিন
Panchanga Calculation Engine: Tithi, Nakshatra, Yoga, Karana, Vaar, Paksha, Ritu, Ayan
Uses high-precision astronomical calculations
"""

import swisseph as swe
from datetime import datetime, timedelta

# ─── Assamese Names ─────────────────────────────────────────────
TITHI_NAMES = [
    "প্ৰতিপদ", "দ্বিতীয়া", "তৃতীয়া", "চতুৰ্থী", "পঞ্চমী", "ষষ্ঠী", "সপ্তমী",
    "অষ্টমী", "নৱমী", "দশমী", "একাদশী", "দ্বাদশী", "ত্ৰয়োদশী", "চতুৰ্দশী",
    "পূৰ্ণিমা", "প্ৰতিপদ", "দ্বিতীয়া", "তৃতীয়া", "চতুৰ্থী", "পঞ্চমী", "ষষ্ঠী",
    "সপ্তমী", "অষ্টমী", "নৱমী", "দশমী", "একাদশী", "দ্বাদশী", "ত্ৰয়োদশী", "চতুৰ্দশী", "অমাৱস্যা"
]

NAKSHATRA_NAMES = [
    "অশ্বিনী", "ভৰণী", "কৃত্তিকা", "ৰোহিণী", "মৃগশিৰা", "আৰ্দ্ৰা", "পুনৰ্বসু",
    "পুষ্যা", "অশ্লেষা", "মঘা", "পূৰ্বফাল্গুনী", "উত্তৰফাল্গুনী", "হস্তা",
    "চিত্ৰা", "স্বাতী", "বিশাখা", "অনুৰাধা", "জ্যেষ্ঠা", "মূল", "পূৰ্বাষাঢ়া",
    "উত্তৰাষাঢ়া", "শ্ৰৱণা", "ধনিষ্ঠা", "শতভিষা", "পূৰ্বভাদ্ৰপদ", "উত্তৰভাদ্ৰপদ", "ৰেৱতী"
]

YOGA_NAMES = [
    "বিষ্কুম্ভ", "প্ৰীতি", "আয়ুষ্মান", "সৌভাগ্য", "শোভন", "অতিগণ্ড", "সুকৰ্মা",
    "ধৃতি", "শূল", "গণ্ড", "বৃদ্ধি", "ধ্ৰুৱ", "ব্যাঘাত", "হৰ্ষণ", "বজ্ৰ",
    "সিদ্ধি", "ব্যতিপাত", "বৰীয়ান", "পৰিঘ", "শিৱ", "সিদ্ধ", "সাধ্য", "শুভ",
    "শুক্ল", "ব্ৰহ্ম", "ইন্দ্ৰ", "বৈধৃতি"
]

KARANA_NAMES = [
    "বৱ", "বালৱ", "কৌলৱ", "তৈতিল", "গৰ", "বণিজ", "বিষ্টি",
    "শকুনি", "চতুষ্পদ", "নাগ", "কিংস্তুঘ্ন"
]

VAAR_NAMES = ["সোমবাৰ", "মঙ্গলবাৰ", "বুধবাৰ", "বৃহস্পতিবাৰ", "শুক্ৰবাৰ", "শনিবাৰ", "ৰবিবাৰ"]

RITU_NAMES = ["বসন্ত", "গ্ৰীষ্ম", "বৰ্ষা", "শৰৎ", "হেমন্ত", "শিশিৰ"]

MASA_NAMES = [
    "ব'হাগ", "জেঠ", "আহাৰ", "শাওণ", "ভাদ", "আহিন",
    "কাতি", "আঘোণ", "পুহ", "মাঘ", "ফাগুন", "চ'ত"
]

PAKSHA_NAMES = ["শুক্ল পক্ষ", "কৃষ্ণ পক্ষ"]


def get_julian_day(dt: datetime, offset_hours: float = -5.5) -> float:
    """Convert datetime to Julian Day (IST offset by default)"""
    return swe.julday(dt.year, dt.month, dt.day,
                      dt.hour + dt.minute / 60.0 + offset_hours)


def calculate_sun_moon(jd: float):
    """Get sidereal Sun and Moon longitudes"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    sun_pos, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    moon_pos, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    return sun_pos[0], moon_pos[0]


def calculate_tithi(sun_lon: float, moon_lon: float) -> dict:
    """Calculate Tithi from Sun-Moon angular difference"""
    diff = (moon_lon - sun_lon) % 360
    tithi_idx = int(diff / 12.0)
    tithi_name = TITHI_NAMES[tithi_idx]
    paksha = PAKSHA_NAMES[0] if tithi_idx < 15 else PAKSHA_NAMES[1]
    tithi_num = (tithi_idx % 15) + 1
    remaining = (12.0 - (diff % 12.0)) / 12.0 * 100
    return {
        "name": tithi_name,
        "number": tithi_num,
        "paksha": paksha,
        "index": tithi_idx,
        "remaining_pct": round(remaining, 1)
    }


def calculate_nakshatra(moon_lon: float) -> dict:
    """Calculate Nakshatra from Moon longitude"""
    nak_idx = int(moon_lon / 13.333333) % 27
    pada = int((moon_lon % 13.333333) / 3.333333) + 1
    remaining = (13.333333 - (moon_lon % 13.333333)) / 13.333333 * 100
    return {
        "name": NAKSHATRA_NAMES[nak_idx],
        "index": nak_idx,
        "pada": pada,
        "remaining_pct": round(remaining, 1)
    }


def calculate_yoga(sun_lon: float, moon_lon: float) -> dict:
    """Calculate Yoga from Sun + Moon longitude"""
    total = (sun_lon + moon_lon) % 360
    yoga_idx = int(total / 13.333333) % 27
    remaining = (13.333333 - (total % 13.333333)) / 13.333333 * 100
    return {
        "name": YOGA_NAMES[yoga_idx],
        "index": yoga_idx,
        "remaining_pct": round(remaining, 1)
    }


def calculate_karana(tithi_idx: int) -> dict:
    """Calculate Karana from Tithi index"""
    if tithi_idx == 28:  # First half of Amavasya
        karana_idx = 7  # Shakuni
    elif tithi_idx == 29:  # Second half of Amavasya
        karana_idx = 8  # Chatushpad
    elif tithi_idx == 14:  # First half of Purnima
        karana_idx = 9  # Naga
    elif tithi_idx == 15:  # Second half of Purnima
        karana_idx = 10  # Kimstughna
    else:
        karana_idx = (tithi_idx % 7) if tithi_idx < 14 else ((tithi_idx - 1) % 7)
    return {"name": KARANA_NAMES[karana_idx], "index": karana_idx}


def calculate_vaar(jd: float) -> dict:
    """Calculate day of week (Vaar)"""
    weekday = int(jd + 0.5) % 7
    return {"name": VAAR_NAMES[weekday], "index": weekday}


def calculate_ritu(sun_lon: float) -> dict:
    """Calculate Ritu (season) from Sun longitude"""
    ritu_idx = int(sun_lon / 60) % 6
    return {"name": RITU_NAMES[ritu_idx], "index": ritu_idx}


def calculate_masa(sun_lon: float) -> dict:
    """Calculate Assamese solar month from Sun longitude"""
    masa_idx = int(sun_lon / 30) % 12
    return {"name": MASA_NAMES[masa_idx], "index": masa_idx}


def calculate_ayanamsa(jd: float) -> float:
    """Get Lahiri Ayanamsa"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.get_ayanamsa(jd)


def calculate_sunrise(jd: float, lat: float, lon: float) -> str:
    """Calculate sunrise time for given location"""
    try:
        rise_time = swe.rise_trans(jd, swe.SUN, lon, lat, 0, 0, 0, swe.CALC_RISE)[1][0]
        hour = int(rise_time)
        minute = int((rise_time - hour) * 60)
        return f"{hour:02d}:{minute:02d}"
    except:
        return "06:00"


def calculate_sunset(jd: float, lat: float, lon: float) -> str:
    """Calculate sunset time for given location"""
    try:
        set_time = swe.rise_trans(jd, swe.SUN, lon, lat, 0, 0, 0, swe.CALC_SET)[1][0]
        hour = int(set_time)
        minute = int((set_time - hour) * 60)
        return f"{hour:02d}:{minute:02d}"
    except:
        return "18:00"


def get_rahu_kalam(sunrise_time: str, weekday: int) -> str:
    """Calculate Rahu Kalam based on weekday"""
    rahu_times = {
        0: ("07:30", "09:00"),   # Monday
        1: ("15:00", "16:30"),   # Tuesday
        2: ("12:00", "13:30"),   # Wednesday
        3: ("13:30", "15:00"),   # Thursday
        4: ("10:30", "12:00"),   # Friday
        5: ("09:00", "10:30"),   # Saturday
        6: ("16:30", "18:00"),   # Sunday
    }
    start, end = rahu_times.get(weekday, ("07:30", "09:00"))
    return f"{start} - {end}"


def get_yama_gandam(weekday: int) -> str:
    """Calculate Yama Gandam based on weekday"""
    yama_times = {
        0: ("10:30", "12:00"),
        1: ("09:00", "10:30"),
        2: ("07:30", "09:00"),
        3: ("06:00", "07:30"),
        4: ("15:00", "16:30"),
        5: ("13:30", "15:00"),
        6: ("12:00", "13:30"),
    }
    start, end = yama_times.get(weekday, ("10:30", "12:00"))
    return f"{start} - {end}"


def get_gulika_kalam(weekday: int) -> str:
    """Calculate Gulika Kalam based on weekday"""
    gulika_times = {
        0: ("13:30", "15:00"),
        1: ("12:00", "13:30"),
        2: ("10:30", "12:00"),
        3: ("09:00", "10:30"),
        4: ("07:30", "09:00"),
        5: ("06:00", "07:30"),
        6: ("15:00", "16:30"),
    }
    start, end = gulika_times.get(weekday, ("13:30", "15:00"))
    return f"{start} - {end}"


def get_abhijit_muhurta(sunrise_str: str, sunset_str: str) -> str:
    """Calculate Abhijit Muhurta (midday auspicious time)"""
    try:
        sr_h, sr_m = map(int, sunrise_str.split(":"))
        ss_h, ss_m = map(int, sunset_str.split(":"))
        sr_total = sr_h * 60 + sr_m
        ss_total = ss_h * 60 + ss_m
        midday = sr_total + (ss_total - sr_total) // 2
        start_h = (midday - 24) // 60
        start_m = (midday - 24) % 60
        end_h = (midday + 24) // 60
        end_m = (midday + 24) % 60
        return f"{start_h:02d}:{start_m:02d} - {end_h:02d}:{end_m:02d}"
    except:
        return "11:36 - 12:24"


def get_full_panchanga(dt: datetime, lat: float, lon: float) -> dict:
    """
    Calculate complete Panchanga for a given datetime and location.
    Returns all five limbs + additional Muhurta info.
    """
    jd = get_julian_day(dt)
    sun_lon, moon_lon = calculate_sun_moon(jd)

    tithi = calculate_tithi(sun_lon, moon_lon)
    nakshatra = calculate_nakshatra(moon_lon)
    yoga = calculate_yoga(sun_lon, moon_lon)
    karana = calculate_karana(tithi["index"])
    vaar = calculate_vaar(jd)
    ritu = calculate_ritu(sun_lon)
    masa = calculate_masa(sun_lon)
    ayanamsa = calculate_ayanamsa(jd)

    sunrise = calculate_sunrise(jd, lat, lon)
    sunset = calculate_sunset(jd, lat, lon)

    return {
        "tithi": tithi,
        "nakshatra": nakshatra,
        "yoga": yoga,
        "karana": karana,
        "vaar": vaar,
        "ritu": ritu,
        "masa": masa,
        "paksha": tithi["paksha"],
        "ayanamsa": round(ayanamsa, 4),
        "sunrise": sunrise,
        "sunset": sunset,
        "rahu_kalam": get_rahu_kalam(sunrise, vaar["index"]),
        "yama_gandam": get_yama_gandam(vaar["index"]),
        "gulika_kalam": get_gulika_kalam(vaar["index"]),
        "abhijit_muhurta": get_abhijit_muhurta(sunrise, sunset),
        "sun_longitude": round(sun_lon, 2),
        "moon_longitude": round(moon_lon, 2),
    }
