"""
ধ্ৰুৱতৰা AI - পঞ্চাঙ্গ গণনা ইঞ্জিন
Panchanga Calculation Engine: Tithi, Nakshatra, Yoga, Karana, Vaar, Paksha, Ritu, Ayan
Uses high-precision astronomical calculations with place-wise accurate sunrise/sunset.
Includes: Rahukal, Yamaganda, Gulik Kaal, Abhijit Muhurta, Yama Kaal, Kaal Bela, Rar Bela,
Divaman, Ratriman, Varna, Gana, Yoni, Nadi, Jata Danda, and more.
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

# ─── Rashi Lords (ৰাশিৰ অধিপতি) ─────────────────────────────────
RASHI_LORDS = [
    "মংগল", "শুক্ৰ", "বুধ", "চন্দ্ৰ", "ৰবি", "বুধ",
    "শুক্ৰ", "মংগল", "বৃহস্পতি", "শনি", "শনি", "বৃহস্পতি"
]

# ─── Nakshatra Attributes ───────────────────────────────────────
# Varna (বৰ্ণ): 0=ব্ৰাহ্মণ, 1=ক্ষত্ৰিয়, 2=বৈশ্য, 3=শূদ্ৰ
NAKSHATRA_VARNA = [
    1, 2, 0, 3, 0, 2, 1, 0, 3, 1, 0, 0, 2,
    0, 2, 1, 0, 1, 1, 2, 0, 0, 2, 3, 1, 0, 0
]
VARNA_NAMES = ["ব্ৰাহ্মণ", "ক্ষত্ৰিয়", "বৈশ্য", "শূদ্ৰ"]

# Gana (গণ): 0=দেৱ, 1=মানুষ্য, 2=ৰাক্ষস
NAKSHATRA_GANA = [
    0, 1, 2, 1, 0, 1, 0, 0, 2, 2, 1, 1, 0,
    2, 0, 2, 0, 2, 2, 1, 1, 0, 2, 2, 1, 1, 0
]
GANA_NAMES = ["দেৱ", "মানুষ্য", "ৰাক্ষস"]

# Yoni (যোনি) - Animal symbols
NAKSHATRA_YONI = [
    "অশ্ব (ঘোঁৰা)", "গজ (হাতী)", "মেষ (ভেড়া)", "সৰ্প (সাপ)", "সৰ্প (সাপ)",
    "শ্বান (কুকুৰ)", "মাৰ্জাৰ (মেকুৰী)", "মেষ (ভেড়া)", "মাৰ্জাৰ (মেকুৰী)",
    "মূষিক (নিগনি)", "মূষিক (নিগনি)", "গো (গৰু)", "মহিষ (ম'হ)",
    "ব্যাঘ্ৰ (বাঘ)", "মহিষ (ম'হ)", "ব্যাঘ্ৰ (বাঘ)", "হৰিণ", "হৰিণ",
    "শ্বান (কুকুৰ)", "বানৰ", "গজ (হাতী)", "অশ্ব (ঘোঁৰা)", "সিংহ",
    "অশ্ব (ঘোঁৰা)", "সিংহ", "গো (গৰু)", "গজ (হাতী)"
]

# Nadi (নাড়ী): 0=আদি, 1=মধ্য, 2=অন্ত্য
NAKSHATRA_NADI = [
    0, 1, 2, 1, 2, 0, 0, 1, 2, 0, 1, 2, 1,
    2, 0, 0, 1, 2, 0, 1, 2, 1, 2, 0, 0, 1, 2
]
NADI_NAMES = ["আদি", "মধ্য", "অন্ত্য"]

# ─── Rahu Kaal part index (0-indexed) by weekday ────────────────
# Sunday=6, Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5
RAHU_KAAL_PART = [1, 6, 4, 5, 3, 2, 0]  # 0-indexed part of 8

# Yama Gandam part index by weekday
YAMA_GANDAM_PART = [4, 3, 2, 1, 0, 6, 5]

# Gulika Kaal part index by weekday
GULIKA_KAAL_PART = [5, 4, 3, 2, 1, 0, 6]

# Yama Kaal (যমকাল) part index by weekday - different from Yama Gandam
YAMA_KAAL_PART = [3, 2, 1, 0, 6, 5, 4]

# Kaal Bela (কালবেলা) part index by weekday
# Saturday uses -1 as sentinel for dual parts (0 and 7)
KAAL_BELA_PART = [6, 5, 4, 7, 3, -1, 4]

# Rar Bela (ৰাৰবেলা) part index by weekday
# Sunday=6, Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5
# Monday = part 1, Tuesday = part 2, ... Sunday = part 0
RAR_BELA_PART = [1, 1, 2, 6, 2, 5, 3]

# Bara Bela (বাৰবেলা) part index by weekday
# দিনমানক ৮ ভাগ কৰিলে বাৰবেলা: সোম=১, মঙ্গল=২, বুধ=৩, বৃহস্পতি=৪, শুক্ৰ=৫, শনি=০+৭, ৰবি=০
# Saturday uses -1 as sentinel for dual parts (0 and 7)
BARA_BELA_PART = [1, 1, 2, 6, 2, 5, 3]


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


def calculate_karana(tithi_idx: int, remaining_pct: float = 50.0) -> dict:
    """
    Calculate Karana from Tithi index and remaining percentage.
    Each tithi has 2 halves with different karanas.
    remaining_pct > 50 means first half, <= 50 means second half.
    
    Fixed Karanas:
    - Kimstughna (10): Purnima 1st half (tithi 14, 1st half)
    - Shakuni (7): Krishna Chaturdashi 2nd half (tithi 28, 2nd half)
    - Chatushpad (8): Amavasya 1st half (tithi 29, 1st half)
    - Naga (9): Amavasya 2nd half (tithi 29, 2nd half)
    
    Movable Karanas (7): Bava(0), Balava(1), Kaulava(2), Taitila(3), Gara(4), Vanija(5), Vishti(6)
    """
    half = 0 if remaining_pct > 50 else 1  # 0=first half, 1=second half
    
    # Fixed karanas
    if tithi_idx == 14 and half == 0:   # Purnima 1st half
        karana_idx = 10  # Kimstughna
    elif tithi_idx == 28 and half == 1:  # Krishna Chaturdashi 2nd half
        karana_idx = 7   # Shakuni
    elif tithi_idx == 29 and half == 0:  # Amavasya 1st half
        karana_idx = 8   # Chatushpad
    elif tithi_idx == 29 and half == 1:  # Amavasya 2nd half
        karana_idx = 9   # Naga
    else:
        # Movable karanas: count how many movable halves before this one
        # Before tithi 14: movable_count = tithi_idx * 2 + half
        # After tithi 14: subtract 1 for the fixed Kimstughna at tithi 14 half 0
        if tithi_idx < 14:
            movable_count = tithi_idx * 2 + half
        else:
            movable_count = tithi_idx * 2 + half - 1  # skip Kimstughna
        karana_idx = movable_count % 7
    
    return {"name": KARANA_NAMES[karana_idx], "index": karana_idx, "half": half}


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


def calculate_sunrise(jd: float, lat: float, lon: float, tz_offset: float = 5.5) -> str:
    """Calculate sunrise time for given location using Swiss Ephemeris.
    Returns local time as HH:MM string in the given timezone.
    Note: JD .0 = noon UT, so frac*24 gives hours from noon. Add 12 for UT hours."""
    try:
        geopos = (lon, lat, 0)  # longitude, latitude, altitude
        # Search from 1.5 days before to catch today's sunrise
        rise_jd = swe.rise_trans(jd - 1.5, swe.SUN, swe.CALC_RISE, geopos)[1][0]
        frac = rise_jd - int(rise_jd)
        # JD .0 = noon UT, so convert: frac*24 = hours from noon, +12 = UT hours
        ut_hours = (frac * 24 + 12) % 24
        # Convert UT to local time using the user's timezone offset
        local_hours = (ut_hours + tz_offset) % 24
        hour = int(local_hours)
        minute = int((local_hours - hour) * 60)
        return f"{hour:02d}:{minute:02d}"
    except:
        return "06:00"


def calculate_sunset(jd: float, lat: float, lon: float, tz_offset: float = 5.5) -> str:
    """Calculate sunset time for given location using Swiss Ephemeris.
    Returns local time as HH:MM string in the given timezone.
    Note: JD .0 = noon UT, so frac*24 gives hours from noon. Add 12 for UT hours."""
    try:
        geopos = (lon, lat, 0)  # longitude, latitude, altitude
        # Search from 1.5 days before to catch today's sunset
        set_jd = swe.rise_trans(jd - 1.5, swe.SUN, swe.CALC_SET, geopos)[1][0]
        frac = set_jd - int(set_jd)
        # JD .0 = noon UT, so convert: frac*24 = hours from noon, +12 = UT hours
        ut_hours = (frac * 24 + 12) % 24
        # Convert UT to local time using the user's timezone offset
        local_hours = (ut_hours + tz_offset) % 24
        hour = int(local_hours)
        minute = int((local_hours - hour) * 60)
        return f"{hour:02d}:{minute:02d}"
    except:
        return "18:00"


def _time_to_minutes(time_str: str) -> int:
    """Convert HH:MM string to total minutes"""
    try:
        h, m = map(int, time_str.split(":"))
        return h * 60 + m
    except:
        return 0


def _minutes_to_time(minutes: int) -> str:
    """Convert total minutes to HH:MM string"""
    h = (minutes // 60) % 24
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def _get_kala_from_part(sunrise_str: str, sunset_str: str, part_index: int) -> str:
    """
    Calculate an inauspicious time (Kala) based on the 8-part division of the day.
    The day (sunrise to sunset) is divided into 8 equal parts.
    part_index: 0-7 (which part of the 8 is the kala)
    """
    sr_min = _time_to_minutes(sunrise_str)
    ss_min = _time_to_minutes(sunset_str)
    day_duration = ss_min - sr_min
    if day_duration <= 0:
        day_duration = 720  # fallback 12 hours
    part_duration = day_duration / 8.0
    start_min = sr_min + part_index * part_duration
    end_min = start_min + part_duration
    return f"{_minutes_to_time(int(start_min))} - {_minutes_to_time(int(end_min))}"


def get_rahu_kalam(sunrise_str: str, sunset_str: str, weekday: int) -> str:
    """Calculate accurate Rahu Kalam based on actual sunrise/sunset at the location"""
    part_idx = RAHU_KAAL_PART[weekday]
    return _get_kala_from_part(sunrise_str, sunset_str, part_idx)


def get_yama_gandam(sunrise_str: str, sunset_str: str, weekday: int) -> str:
    """Calculate accurate Yama Gandam based on actual sunrise/sunset at the location"""
    part_idx = YAMA_GANDAM_PART[weekday]
    return _get_kala_from_part(sunrise_str, sunset_str, part_idx)


def get_gulika_kalam(sunrise_str: str, sunset_str: str, weekday: int) -> str:
    """Calculate accurate Gulika Kalam based on actual sunrise/sunset at the location"""
    part_idx = GULIKA_KAAL_PART[weekday]
    return _get_kala_from_part(sunrise_str, sunset_str, part_idx)


def get_yama_kaal(sunrise_str: str, sunset_str: str, weekday: int) -> str:
    """Calculate Yama Kaal (যমকাল) based on actual sunrise/sunset"""
    part_idx = YAMA_KAAL_PART[weekday]
    return _get_kala_from_part(sunrise_str, sunset_str, part_idx)


def get_kaal_bela(sunrise_str: str, sunset_str: str, weekday: int) -> str:
    """Calculate Kaal Bela (কালবেলা) based on actual sunrise/sunset.
    শনিবাৰে দুটা ভাগ: ০ আৰু ৭"""
    part_idx = KAAL_BELA_PART[weekday]
    if part_idx == -1:
        # Saturday: two parts - 0 and 7
        part1 = _get_kala_from_part(sunrise_str, sunset_str, 0)
        part2 = _get_kala_from_part(sunrise_str, sunset_str, 7)
        return f"{part1} আৰু {part2}"
    return _get_kala_from_part(sunrise_str, sunset_str, part_idx)


def get_rar_bela(sunrise_str: str, sunset_str: str, weekday: int) -> str:
    """Calculate Rar Bela (ৰাৰবেলা) based on actual sunrise/sunset"""
    part_idx = RAR_BELA_PART[weekday]
    return _get_kala_from_part(sunrise_str, sunset_str, part_idx)


def get_bara_bela(sunrise_str: str, sunset_str: str, weekday: int) -> str:
    """Calculate Bara Bela (বাৰবেলা) based on actual sunrise/sunset.
    দিনমানক ৮ ভাগ কৰিলে বাৰবেলা: সোম=১, মঙ্গল=২, বুধ=৩, বৃহস্পতি=৪, শুক্ৰ=৫, শনি=০+৭, ৰবি=০"""
    part_idx = BARA_BELA_PART[weekday]
    if part_idx == -1:
        # Saturday: two parts - 0 and 7
        part1 = _get_kala_from_part(sunrise_str, sunset_str, 0)
        part2 = _get_kala_from_part(sunrise_str, sunset_str, 7)
        return f"{part1} আৰু {part2}"
    return _get_kala_from_part(sunrise_str, sunset_str, part_idx)


def get_abhijit_muhurta(sunrise_str: str, sunset_str: str) -> str:
    """Calculate Abhijit Muhurta (midday auspicious time ~24 min before/after local noon)"""
    try:
        sr_min = _time_to_minutes(sunrise_str)
        ss_min = _time_to_minutes(sunset_str)
        midday = sr_min + (ss_min - sr_min) // 2
        start_min = midday - 24
        end_min = midday + 24
        return f"{_minutes_to_time(start_min)} - {_minutes_to_time(end_min)}"
    except:
        return "11:36 - 12:24"


def get_divaman(sunrise_str: str, sunset_str: str) -> str:
    """Calculate day duration (দিবামান)"""
    sr_min = _time_to_minutes(sunrise_str)
    ss_min = _time_to_minutes(sunset_str)
    duration = ss_min - sr_min
    if duration <= 0:
        duration = 720
    h = duration // 60
    m = duration % 60
    return f"{h} ঘণ্টা {m} মিনিট"


def get_ratriman(sunrise_str: str, sunset_str: str) -> str:
    """Calculate night duration (ৰাত্ৰিমান)"""
    sr_min = _time_to_minutes(sunrise_str)
    ss_min = _time_to_minutes(sunset_str)
    day_dur = ss_min - sr_min
    if day_dur <= 0:
        day_dur = 720
    night_dur = 1440 - day_dur
    h = night_dur // 60
    m = night_dur % 60
    return f"{h} ঘণ্টা {m} মিনিট"


def get_jata_danda(birth_time_str: str, sunrise_str: str) -> str:
    """
    Calculate Jata Danda (জাতদণ্ড) - time elapsed since sunrise in danda/pala.
    1 danda = 24 minutes, 1 pala = 24 seconds
    """
    try:
        bt_h, bt_m = map(int, birth_time_str.split(":"))
        sr_h, sr_m = map(int, sunrise_str.split(":"))
        bt_total = bt_h * 60 + bt_m
        sr_total = sr_h * 60 + sr_m
        elapsed = bt_total - sr_total
        if elapsed < 0:
            elapsed += 1440  # birth before sunrise (previous day sunrise)
        danda = elapsed // 24
        remaining_min = elapsed % 24
        pala = remaining_min * 60 // 24
        return f"{danda} দণ্ড {pala} পল"
    except:
        return "0 দণ্ড 0 পল"


def get_nakshatra_attributes(nak_idx: int) -> dict:
    """Get Varna, Gana, Yoni, Nadi for a given nakshatra index (0-26)"""
    if nak_idx < 0 or nak_idx > 26:
        nak_idx = 0
    return {
        "varna": VARNA_NAMES[NAKSHATRA_VARNA[nak_idx]],
        "gana": GANA_NAMES[NAKSHATRA_GANA[nak_idx]],
        "yoni": NAKSHATRA_YONI[nak_idx],
        "nadi": NADI_NAMES[NAKSHATRA_NADI[nak_idx]],
    }


def get_rashi_lord(rashi_index: int) -> str:
    """Get the lord of a rashi (0-11)"""
    if rashi_index < 0 or rashi_index > 11:
        return ""
    return RASHI_LORDS[rashi_index]


def get_full_panchanga(dt: datetime, lat: float, lon: float, tz_offset: float = 5.5) -> dict:
    """
    Calculate complete Panchanga for a given datetime and location.
    Returns all five limbs + additional Muhurta info + nakshatra attributes.
    tz_offset: timezone offset from UTC in hours (e.g., 5.5 for IST)
    """
    jd = get_julian_day(dt)
    sun_lon, moon_lon = calculate_sun_moon(jd)

    tithi = calculate_tithi(sun_lon, moon_lon)
    nakshatra = calculate_nakshatra(moon_lon)
    yoga = calculate_yoga(sun_lon, moon_lon)
    karana = calculate_karana(tithi["index"], tithi["remaining_pct"])
    vaar = calculate_vaar(jd)
    ritu = calculate_ritu(sun_lon)
    masa = calculate_masa(sun_lon)
    ayanamsa = calculate_ayanamsa(jd)

    sunrise = calculate_sunrise(jd, lat, lon, tz_offset)
    sunset = calculate_sunset(jd, lat, lon, tz_offset)

    # Nakshatra attributes
    nak_attrs = get_nakshatra_attributes(nakshatra["index"])

    # Day/Night duration
    divaman = get_divaman(sunrise, sunset)
    ratriman = get_ratriman(sunrise, sunset)

    # Jata Danda
    jata_danda = get_jata_danda(dt.strftime("%H:%M"), sunrise)

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
        "rahu_kalam": get_rahu_kalam(sunrise, sunset, vaar["index"]),
        "yama_gandam": get_yama_gandam(sunrise, sunset, vaar["index"]),
        "gulika_kalam": get_gulika_kalam(sunrise, sunset, vaar["index"]),
        "abhijit_muhurta": get_abhijit_muhurta(sunrise, sunset),
        "yama_kaal": get_yama_kaal(sunrise, sunset, vaar["index"]),
        "kaal_bela": get_kaal_bela(sunrise, sunset, vaar["index"]),
        "rar_bela": get_rar_bela(sunrise, sunset, vaar["index"]),
        "bara_bela": get_bara_bela(sunrise, sunset, vaar["index"]),
        "divaman": divaman,
        "ratriman": ratriman,
        "jata_danda": jata_danda,
        "varna": nak_attrs["varna"],
        "gana": nak_attrs["gana"],
        "yoni": nak_attrs["yoni"],
        "nadi": nak_attrs["nadi"],
        "sun_longitude": round(sun_lon, 2),
        "moon_longitude": round(moon_lon, 2),
    }
