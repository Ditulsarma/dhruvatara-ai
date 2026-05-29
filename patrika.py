"""
ধ্ৰুৱতৰা AI - পত্ৰিকা (Patrika) জেনেৰেটৰ
Generates traditional Assamese astrological birth record (পত্ৰিকা) text.
"""

from datetime import datetime

# ─── Assamese month names (English → Assamese) ──────────────────
ENGLISH_MONTHS_ASM = [
    "জানুৱাৰী", "ফেব্ৰুৱাৰী", "মাৰ্চ", "এপ্ৰিল", "মে", "জুন",
    "জুলাই", "আগষ্ট", "ছেপ্টেম্বৰ", "অক্টোবৰ", "নৱেম্বৰ", "ডিচেম্বৰ"
]

# ─── Hora lords (order starting from weekday lord) ─────────────
HORA_LORDS_ORDER = ["ৰবি", "শুক্ৰ", "বুধ", "চন্দ্ৰ", "শনি", "বৃহস্পতি", "মংগল"]
WEEKDAY_LORDS = ["চন্দ্ৰ", "মংগল", "বুধ", "বৃহস্পতি", "শুক্ৰ", "শনি", "ৰবি"]  # Mon=0..Sun=6

# ─── Drekkana lords (D3) ───────────────────────────────────────
DREKKANA_LORDS = ["মংগল", "শুক্ৰ", "বুধ", "চন্দ্ৰ", "ৰবি", "বুধ", "শুক্ৰ", "মংগল", "বৃহস্পতি", "শনি", "শনি", "বৃহস্পতি"]

# ─── Navamsa lords (D9) ────────────────────────────────────────
NAVAMSA_LORDS = [
    "মংগল", "শুক্ৰ", "বুধ", "চন্দ্ৰ", "ৰবি", "বুধ", "শুক্ৰ", "মংগল", "বৃহস্পতি",
    "শনি", "শনি", "বৃহস্পতি", "মংগল", "শুক্ৰ", "বুধ", "চন্দ্ৰ", "ৰবি", "বুধ",
    "শুক্ৰ", "মংগল", "বৃহস্পতি", "শনি", "শনি", "বৃহস্পতি"
]

# ─── Ashtottari dasha starting lord by nakshatra ───────────────
# Based on nakshatra index (0-26)
ASHTOTTARI_START = [
    "ৰবি", "ৰবি", "ৰবি", "ৰবি", "ৰবি", "ৰবি",  # 0-5: Sun
    "চন্দ্ৰ", "চন্দ্ৰ", "চন্দ্ৰ", "চন্দ্ৰ", "চন্দ্ৰ", "চন্দ্ৰ",  # 6-11: Moon
    "মংগল", "মংগল", "মংগল", "মংগল",  # 12-15: Mars
    "বুধ", "বুধ", "বুধ", "বুধ", "বুধ",  # 16-20: Mercury
    "শনি", "শনি",  # 21-22: Saturn
    "বৃহস্পতি", "বৃহস্পতি", "বৃহস্পতি", "বৃহস্পতি",  # 23-26: Jupiter
]

# ─── Yoni/Animal names by nakshatra ────────────────────────────
NAKSHATRA_YONI_NAMES = [
    "অশ্ব", "গজ", "মেষ", "সৰ্প", "সৰ্প", "শ্বান", "মাৰ্জাৰ", "মেষ",
    "মাৰ্জাৰ", "মূষিক", "মূষিক", "গো", "মহিষ", "ব্যাঘ্ৰ", "মহিষ",
    "ব্যাঘ্ৰ", "হৰিণ", "হৰিণ", "শ্বান", "বানৰ", "গজ", "অশ্ব",
    "সিংহ", "অশ্ব", "সিংহ", "গো", "গজ"
]

# ─── Rashi lords ────────────────────────────────────────────────
RASHI_LORDS_LIST = [
    "মংগল", "শুক্ৰ", "বুধ", "চন্দ্ৰ", "ৰবি", "বুধ",
    "শুক্ৰ", "মংগল", "বৃহস্পতি", "শনি", "শনি", "বৃহস্পতি"
]

# ─── Nakshatra lords ───────────────────────────────────────────
NAKSHATRA_LORDS = [
    "কেতু", "শুক্ৰ", "ৰবি", "চন্দ্ৰ", "মংগল", "ৰাহু", "বৃহস্পতি", "শনি",
    "বুধ", "কেতু", "শুক্ৰ", "ৰবি", "চন্দ্ৰ", "মংগল", "ৰাহু", "বৃহস্পতি",
    "শনি", "বুধ", "কেতু", "শুক্ৰ", "ৰবি", "চন্দ্ৰ", "মংগল", "ৰাহু",
    "বৃহস্পতি", "শনি", "বুধ"
]

# ─── Pada names ─────────────────────────────────────────────────
PADA_NAMES = ["প্ৰথম", "দ্বিতীয়", "তৃতীয়", "চতুৰ্থ"]


def calculate_shaka_year(gregorian_year: int) -> int:
    """Shaka Samvat = Gregorian year - 78 (approximate)"""
    return gregorian_year - 78


def calculate_bhaskara_year(gregorian_year: int) -> int:
    """Bhaskarabda = Gregorian year - 593 (Assamese calendar)"""
    return gregorian_year - 593


def get_hora_lord(weekday_index: int, birth_hour: float, sunrise_hour: float = 6.0) -> str:
    """
    Calculate Hora lord at birth time.
    weekday_index: 0=Mon..6=Sun
    birth_hour: hour of birth (0-24)
    sunrise_hour: approximate sunrise hour
    """
    # Find the starting lord for this weekday
    start_lord = WEEKDAY_LORDS[weekday_index]
    start_idx = HORA_LORDS_ORDER.index(start_lord)
    
    # Each hora is ~1 hour. Count horas since sunrise.
    hours_since_sunrise = birth_hour - sunrise_hour
    if hours_since_sunrise < 0:
        hours_since_sunrise += 24
    
    hora_index = int(hours_since_sunrise) % 7
    lord_idx = (start_idx + hora_index) % 7
    return HORA_LORDS_ORDER[lord_idx]


def get_drekkana_lord(rasi_index: int, degree: float) -> str:
    """Get Drekkana (D3) lord based on rasi and degree."""
    drek_index = int(degree / 10)  # 0, 1, or 2
    return DREKKANA_LORDS[rasi_index]


def get_navamsa_lord(rasi_index: int, degree: float) -> str:
    """Get Navamsa (D9) lord based on rasi and degree."""
    nav_index = int(degree / 3.333333)  # 0-8
    return NAVAMSA_LORDS[rasi_index]


def get_ashtottari_lord(nakshatra_index: int) -> str:
    """Get Ashtottari dasha starting lord from nakshatra."""
    return ASHTOTTARI_START[nakshatra_index % 27]


def get_vimshottari_lord(nakshatra_index: int) -> str:
    """Get Vimshottari dasha starting lord from nakshatra."""
    return NAKSHATRA_LORDS[nakshatra_index % 27]


def generate_patrika_text(
    # Form data
    public_name: str,
    secret_name: str,
    father_name: str,
    mother_name: str,
    birth_district: str,
    residence_district: str,
    residence: str,
    gender: str,  # "male" or "female"
    # Astrological data
    dob: str,  # "YYYY-MM-DD"
    tob: str,  # "HH:MM"
    asc_rasi: str,
    asc_rasi_idx: int,
    asc_degree: float,
    moon_rasi: str,
    moon_rasi_idx: int,
    nakshatra_name: str,
    nakshatra_idx: int,
    nakshatra_pada: int,
    panchanga: dict,
    vimshottari_lord: str = "",
    ashtottari_lord: str = "",
) -> str:
    """
    Generate the traditional Assamese Patrika text.
    Returns formatted Assamese text.
    """
    # Parse date
    dt = datetime.strptime(dob, "%Y-%m-%d")
    gregorian_year = dt.year
    day = dt.day
    month_asm = ENGLISH_MONTHS_ASM[dt.month - 1]
    
    # Parse time
    time_parts = tob.split(":")
    birth_hour = int(time_parts[0])
    birth_min = int(time_parts[1])
    
    # Calculate years
    shaka_year = calculate_shaka_year(gregorian_year)
    bhaskara_year = calculate_bhaskara_year(gregorian_year)
    
    # Get panchanga data
    tithi = panchanga.get('tithi', {})
    paksha = panchanga.get('paksha', '')
    nakshatra = panchanga.get('nakshatra', {})
    yoga = panchanga.get('yoga', {})
    karana = panchanga.get('karana', {})
    vaar = panchanga.get('vaar', {})
    masa = panchanga.get('masa', {})
    varna = panchanga.get('varna', '')
    gana = panchanga.get('gana', '')
    sunrise = panchanga.get('sunrise', '06:00')
    
    # Parse sunrise
    try:
        sr_parts = sunrise.split(":")
        sunrise_hour = int(sr_parts[0]) + int(sr_parts[1]) / 60.0
    except:
        sunrise_hour = 6.0
    
    # Calculate derived values
    weekday_idx = vaar.get('index', 0)
    hora_lord = get_hora_lord(weekday_idx, birth_hour + birth_min / 60.0, sunrise_hour)
    drekkana_lord = get_drekkana_lord(asc_rasi_idx, asc_degree)
    navamsa_lord = get_navamsa_lord(asc_rasi_idx, asc_degree)
    
    if not vimshottari_lord:
        vimshottari_lord = get_vimshottari_lord(nakshatra_idx)
    if not ashtottari_lord:
        ashtottari_lord = get_ashtottari_lord(nakshatra_idx)
    
    # Lagna lord and rashi lord
    lagna_lord = RASHI_LORDS_LIST[asc_rasi_idx]
    rashi_lord = RASHI_LORDS_LIST[moon_rasi_idx]
    
    # Nakshatra lord
    nakshatra_lord = NAKSHATRA_LORDS[nakshatra_idx]
    
    # Yoni
    yoni = NAKSHATRA_YONI_NAMES[nakshatra_idx]
    
    # Pada name
    pada_name = PADA_NAMES[nakshatra_pada - 1] if 1 <= nakshatra_pada <= 4 else ""
    
    # Gender text
    if gender == "female":
        child_word = "কুমাৰী"
        blessing = "বালিকা সু-কীৰ্তিশালিনী"
        prefix = "শ্ৰীমতী"
    else:
        child_word = "কুমাৰ"
        blessing = "বালক সু-কীৰ্তিশালী"
        prefix = "শ্ৰীমান"
    
    # Build the patrika text
    text = f"""শুভমস্তু শকাব্দদয় {shaka_year}, ভাস্কৰাব্দ {bhaskara_year}, ইংৰাজী {day} {month_asm} {gregorian_year} চন, জন্ম দিবাঃ {tob} মি: সময় | জন্মৰ স্থান: {birth_district} | সৌৰ {masa.get('name', '—')} মাহৰ {vaar.get('name', '—')}ে, অয়নাংশ পৰিশোধিত {asc_rasi} লগ্নত, {lagna_lord} লগ্নাধিপতি, {moon_rasi} ৰাশি, {rashi_lord} ৰাশ্যাধিপতি, {nakshatra_name} নক্ষত্ৰৰ, {pada_name} ভোগ্য চৰনত, নক্ষত্ৰাধিপতি {nakshatra_lord}, অ.সিতপক্ষীয় {paksha}ৰ {tithi.get('name', '—')} তিথিত, {yoga.get('name', '—')} যোগত, {gana}গণ, {varna} বৰ্ণ, {karana.get('name', '—')} কৰণ, {hora_lord}ৰ হোৰাত, {drekkana_lord}ৰ দ্ৰেক্কানত, {navamsa_lord}ৰ নবাংশত, {yoni}ৰ অস্থিত, অষ্টোত্তৰী মতে {ashtottari_lord} আৰু বিংশোত্তৰী {vimshottari_lord}ৰ মহাদশাত তথা নানা শুভা-শুভ যোগত {residence_district} জিলান্তৰ্গত {residence} নিবাসী পৰম ধাৰ্মিক শ্ৰীযুক্ত {father_name} মহোদয়ৰ ঘৰত ধৰ্মপত্নী শ্ৰীযুক্তা {mother_name}ৰ উদৰত শুভ {child_word} জন্ম হয়|

তেওঁৰ লোক প্ৰকাশিত নাম -> {prefix} {public_name}
গুপ্ত নাম -> {prefix} {secret_name}

দেৱ দ্বিজৰ আশীৰ্বাদত আদিত্যাদি নৱগ্ৰহৰ প্ৰসাদাৎ
{blessing} | দীৰ্ঘজীৱি হওঁক ||"""

    return text
