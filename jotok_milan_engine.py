"""
ধ্ৰুৱতৰা AI - যোটক মিলন ইঞ্জিন (Jotok Milan / Marriage Matching Engine)
Ashtakoot Guna Milan (অষ্টকূট গুণ মিলন) - 36 Points System
Plus Mangalik Dosha (মাংগলিক দোষ) Analysis for Marriage Compatibility

Based on traditional Assamese Vedic Jyotish principles.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS & LOOKUP TABLES
# ═══════════════════════════════════════════════════════════════════════════════

RASHIS = [
    "মেষ", "বৃষ", "মিথুন", "কৰ্কট",
    "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক",
    "ধনু", "মকৰ", "কুম্ভ", "মীন"
]

NAKSHATRAS = [
    "অশ্বিনী", "ভৰণী", "কৃত্তিকা", "ৰোহিণী", "মৃগশিৰা", "আৰ্দ্ৰা", "পুনৰ্বসু", "পুষ্যা", "অশ্লেষা",
    "মঘা", "পূৰ্বফাল্গুনী", "উত্তৰফাল্গুনী", "হস্তা", "চিত্ৰা", "স্বাতী", "বিশাখা", "অনুৰাধা", "জ্যেষ্ঠা",
    "মূল", "পূৰ্বাষাঢ়া", "উত্তৰাষাঢ়া", "শ্ৰৱণা", "ধনিষ্ঠা", "শতভিষা", "পূৰ্বভাদ্ৰপদ", "উত্তৰভাদ্ৰপদ", "ৰেৱতী"
]

# ─── Varna (বৰ্ণ) by Rashi ───
# Brahmin=1, Kshatriya=2, Vaishya=3, Shudra=4
VARNA_BY_RASHI = {
    "মেষ": 2, "বৃষ": 3, "মিথুন": 3, "কৰ্কট": 1,
    "সিংহ": 2, "কন্যা": 3, "তুলা": 3, "বৃশ্চিক": 1,
    "ধনু": 2, "মকৰ": 3, "কুম্ভ": 3, "মীন": 1
}

VARNA_NAMES = {1: "ব্ৰাহ্মণ", 2: "ক্ষত্ৰিয়", 3: "বৈশ্য", 4: "শূদ্ৰ"}

# ─── Vashya (বশ্য) by Rashi ───
# 1=Chatushpad (চতুষ্পদ), 2=Manava (মনুষ্য), 3=Jalachar (জলচৰ), 4=Banachar (বনচৰ), 5=Keet (কীট)
VASHYA_BY_RASHI = {
    "মেষ": 1, "বৃষ": 1, "মিথুন": 2, "কৰ্কট": 3,
    "সিংহ": 4, "কন্যা": 2, "তুলা": 2, "বৃশ্চিক": 5,
    "ধনু": 2, "মকৰ": 3, "কুম্ভ": 2, "মীন": 3
}

VASHYA_NAMES = {1: "চতুষ্পদ", 2: "মনুষ্য", 3: "জলচৰ", 4: "বনচৰ", 5: "কীট"}

# Vashya compatibility matrix (1-indexed)
VASHYA_COMPAT = {
    1: [1, 2, 3, 4],  # Chatushpad compatible with Chatushpad, Manava, Jalachar, Banachar
    2: [1, 2, 3, 4, 5],  # Manava compatible with all
    3: [1, 2, 3, 5],  # Jalachar
    4: [1, 2, 4],  # Banachar
    5: [2, 3, 5],  # Keet
}

# ─── Yoni (যোনি) by Nakshatra ───
# Each nakshatra has an animal yoni
YONI_BY_NAKSHATRA = {
    "অশ্বিনী": "অশ্ব", "ভৰণী": "গজ", "কৃত্তিকা": "মেষ", "ৰোহিণী": "সৰ্প",
    "মৃগশিৰা": "সৰ্প", "আৰ্দ্ৰা": "শ্বান", "পুনৰ্বসু": "মাৰ্জাৰ", "পুষ্যা": "মেষ",
    "অশ্লেষা": "মাৰ্জাৰ", "মঘা": "মূষিক", "পূৰ্বফাল্গুনী": "মূষিক", "উত্তৰফাল্গুনী": "গো",
    "হস্তা": "মহিষ", "চিত্ৰা": "ব্যাঘ্ৰ", "স্বাতী": "মহিষ", "বিশাখা": "ব্যাঘ্ৰ",
    "অনুৰাধা": "মৃগ", "জ্যেষ্ঠা": "মৃগ", "মূল": "শ্বান", "পূৰ্বাষাঢ়া": "বানৰ",
    "উত্তৰাষাঢ়া": "নকুল", "শ্ৰৱণা": "বানৰ", "ধনিষ্ঠা": "সিংহ", "শতভিষা": "অশ্ব",
    "পূৰ্বভাদ্ৰপদ": "সিংহ", "উত্তৰভাদ্ৰপদ": "গো", "ৰেৱতী": "গজ"
}

# Yoni compatibility: some animals are natural friends/enemies
YONI_FRIENDLY = {
    "অশ্ব": ["অশ্ব", "গজ", "মেষ", "সৰ্প", "মাৰ্জাৰ", "মূষিক", "গো", "মহিষ", "মৃগ", "বানৰ", "নকুল", "সিংহ"],
    "গজ": ["অশ্ব", "গজ", "মেষ", "সৰ্প", "মাৰ্জাৰ", "মূষিক", "গো", "মহিষ", "মৃগ", "বানৰ", "নকুল", "সিংহ"],
    "মেষ": ["অশ্ব", "গজ", "মেষ", "সৰ্প", "মাৰ্জাৰ", "মূষিক", "গো", "মহিষ", "মৃগ", "বানৰ", "নকুল", "সিংহ"],
    "সৰ্প": ["অশ্ব", "গজ", "মেষ", "সৰ্প", "মাৰ্জাৰ", "মূষিক", "গো", "মহিষ", "মৃগ", "বানৰ", "নকুল", "সিংহ"],
    "মাৰ্জাৰ": ["অশ্ব", "গজ", "মেষ", "সৰ্প", "মাৰ্জাৰ", "মূষিক", "গো", "মহিষ", "মৃগ", "বানৰ", "নকুল", "সিংহ"],
    "মূষিক": ["অশ্ব", "গজ", "মেষ", "সৰ্প", "মাৰ্জাৰ", "মূষিক", "গো", "মহিষ", "মৃগ", "বানৰ", "নকুল", "সিংহ"],
    "গো": ["অশ্ব", "গজ", "মেষ", "সৰ্প", "মাৰ্জাৰ", "মূষিক", "গো", "মহিষ", "মৃগ", "বানৰ", "নকুল", "সিংহ"],
    "মহিষ": ["অশ্ব", "গজ", "মেষ", "সৰ্প", "মাৰ্জাৰ", "মূষিক", "গো", "মহিষ", "মৃগ", "বানৰ", "নকুল", "সিংহ"],
    "মৃগ": ["অশ্ব", "গজ", "মেষ", "সৰ্প", "মাৰ্জাৰ", "মূষিক", "গো", "মহিষ", "মৃগ", "বানৰ", "নকুল", "সিংহ"],
    "বানৰ": ["অশ্ব", "গজ", "মেষ", "সৰ্প", "মাৰ্জাৰ", "মূষিক", "গো", "মহিষ", "মৃগ", "বানৰ", "নকুল", "সিংহ"],
    "নকুল": ["অশ্ব", "গজ", "মেষ", "সৰ্প", "মাৰ্জাৰ", "মূষিক", "গো", "মহিষ", "মৃগ", "বানৰ", "নকুল", "সিংহ"],
    "সিংহ": ["অশ্ব", "গজ", "মেষ", "সৰ্প", "মাৰ্জাৰ", "মূষিক", "গো", "মহিষ", "মৃগ", "বানৰ", "নকুল", "সিংহ"],
    "শ্বান": ["শ্বান", "মাৰ্জাৰ", "সিংহ", "ব্যাঘ্ৰ", "মৃগ"],
    "ব্যাঘ্ৰ": ["ব্যাঘ্ৰ", "শ্বান", "মাৰ্জাৰ", "সিংহ", "মৃগ"],
}

# Yoni enemy pairs
YONI_ENEMY = {
    "অশ্ব": ["মহিষ"],
    "মহিষ": ["অশ্ব"],
    "সৰ্প": ["নকুল"],
    "নকুল": ["সৰ্প"],
    "মূষিক": ["মাৰ্জাৰ"],
    "মাৰ্জাৰ": ["মূষিক"],
    "সিংহ": ["গজ"],
    "গজ": ["সিংহ"],
    "শ্বান": ["মৃগ"],
    "মৃগ": ["শ্বান"],
    "ব্যাঘ্ৰ": ["গো"],
    "গো": ["ব্যাঘ্ৰ"],
    "বানৰ": ["মেষ"],
    "মেষ": ["বানৰ"],
}

# ─── Graha Maitri (গ্ৰহ মৈত্ৰী) - Rashi Lords ───
RASHI_LORDS = {
    "মেষ": "মংগল", "বৃষ": "শুক্ৰ", "মিথুন": "বুধ", "কৰ্কট": "চন্দ্ৰ",
    "সিংহ": "ৰবি", "কন্যা": "বুধ", "তুলা": "শুক্ৰ", "বৃশ্চিক": "মংগল",
    "ধনু": "বৃহস্পতি", "মকৰ": "শনি", "কুম্ভ": "শনি", "মীন": "বৃহস্পতি"
}

# Planetary friendship matrix
# 5=Adhi Mitra (best friend), 4=Mitra (friend), 3=Sama (neutral), 2=Shatru (enemy), 1=Adhi Shatru (worst enemy)
PLANET_FRIENDSHIP = {
    "ৰবি":     {"ৰবি": 3, "চন্দ্ৰ": 4, "মংগল": 4, "বুধ": 3, "বৃহস্পতি": 4, "শুক্ৰ": 2, "শনি": 2},
    "চন্দ্ৰ":   {"ৰবি": 4, "চন্দ্ৰ": 3, "মংগল": 3, "বুধ": 4, "বৃহস্পতি": 3, "শুক্ৰ": 3, "শনি": 3},
    "মংগল":    {"ৰবি": 4, "চন্দ্ৰ": 4, "মংগল": 3, "বুধ": 2, "বৃহস্পতি": 4, "শুক্ৰ": 2, "শনি": 2},
    "বুধ":     {"ৰবি": 4, "চন্দ্ৰ": 3, "মংগল": 3, "বুধ": 3, "বৃহস্পতি": 3, "শুক্ৰ": 4, "শনি": 3},
    "বৃহস্পতি": {"ৰবি": 4, "চন্দ্ৰ": 4, "মংগল": 4, "বুধ": 2, "বৃহস্পতি": 3, "শুক্ৰ": 2, "শনি": 2},
    "শুক্ৰ":    {"ৰবি": 2, "চন্দ্ৰ": 3, "মংগল": 2, "বুধ": 4, "বৃহস্পতি": 2, "শুক্ৰ": 3, "শনি": 4},
    "শনি":     {"ৰবি": 2, "চন্দ্ৰ": 3, "মংগল": 2, "বুধ": 4, "বৃহস্পতি": 2, "শুক্ৰ": 4, "শনি": 3},
}

# ─── Gana (গণ) by Nakshatra ───
# 1=Deva (দেৱ), 2=Manushya (মনুষ্য), 3=Rakshasa (ৰাক্ষস)
GANA_BY_NAKSHATRA = {
    "অশ্বিনী": 1, "ভৰণী": 2, "কৃত্তিকা": 3, "ৰোহিণী": 2, "মৃগশিৰা": 1, "আৰ্দ্ৰা": 2,
    "পুনৰ্বসু": 1, "পুষ্যা": 1, "অশ্লেষা": 3, "মঘা": 3, "পূৰ্বফাল্গুনী": 2, "উত্তৰফাল্গুনী": 2,
    "হস্তা": 1, "চিত্ৰা": 3, "স্বাতী": 1, "বিশাখা": 3, "অনুৰাধা": 1, "জ্যেষ্ঠা": 3,
    "মূল": 3, "পূৰ্বাষাঢ়া": 2, "উত্তৰাষাঢ়া": 2, "শ্ৰৱণা": 1, "ধনিষ্ঠা": 3, "শতভিষা": 3,
    "পূৰ্বভাদ্ৰপদ": 2, "উত্তৰভাদ্ৰপদ": 2, "ৰেৱতী": 1
}

GANA_NAMES = {1: "দেৱ", 2: "মনুষ্য", 3: "ৰাক্ষস"}

# ─── Nadi (নাড়ী) by Nakshatra ───
# 1=Adi (আদি), 2=Madhya (মধ্য), 3=Antya (অন্ত্য)
NADI_BY_NAKSHATRA = {
    "অশ্বিনী": 1, "ভৰণী": 2, "কৃত্তিকা": 3, "ৰোহিণী": 1, "মৃগশিৰা": 2, "আৰ্দ্ৰা": 3,
    "পুনৰ্বসু": 1, "পুষ্যা": 2, "অশ্লেষা": 3, "মঘা": 1, "পূৰ্বফাল্গুনী": 2, "উত্তৰফাল্গুনী": 3,
    "হস্তা": 1, "চিত্ৰা": 2, "স্বাতী": 3, "বিশাখা": 1, "অনুৰাধা": 2, "জ্যেষ্ঠা": 3,
    "মূল": 1, "পূৰ্বাষাঢ়া": 2, "উত্তৰাষাঢ়া": 3, "শ্ৰৱণা": 1, "ধনিষ্ঠা": 2, "শতভিষা": 3,
    "পূৰ্বভাদ্ৰপদ": 1, "উত্তৰভাদ্ৰপদ": 2, "ৰেৱতী": 3
}

NADI_NAMES = {1: "আদি", 2: "মধ্য", 3: "অন্ত্য"}

# ─── Nakshatra to Rashi mapping ───
NAKSHATRA_TO_RASHI = {
    "অশ্বিনী": "মেষ", "ভৰণী": "মেষ", "কৃত্তিকা": "মেষ",
    "কৃত্তিকা": "বৃষ", "ৰোহিণী": "বৃষ", "মৃগশিৰা": "বৃষ",
    "মৃগশিৰা": "মিথুন", "আৰ্দ্ৰা": "মিথুন", "পুনৰ্বসু": "মিথুন",
    "পুনৰ্বসু": "কৰ্কট", "পুষ্যা": "কৰ্কট", "অশ্লেষা": "কৰ্কট",
    "মঘা": "সিংহ", "পূৰ্বফাল্গুনী": "সিংহ", "উত্তৰফাল্গুনী": "সিংহ",
    "উত্তৰফাল্গুনী": "কন্যা", "হস্তা": "কন্যা", "চিত্ৰা": "কন্যা",
    "চিত্ৰা": "তুলা", "স্বাতী": "তুলা", "বিশাখা": "তুলা",
    "বিশাখা": "বৃশ্চিক", "অনুৰাধা": "বৃশ্চিক", "জ্যেষ্ঠা": "বৃশ্চিক",
    "মূল": "ধনু", "পূৰ্বাষাঢ়া": "ধনু", "উত্তৰাষাঢ়া": "ধনু",
    "উত্তৰাষাঢ়া": "মকৰ", "শ্ৰৱণা": "মকৰ", "ধনিষ্ঠা": "মকৰ",
    "ধনিষ্ঠা": "কুম্ভ", "শতভিষা": "কুম্ভ", "পূৰ্বভাদ্ৰপদ": "কুম্ভ",
    "পূৰ্বভাদ্ৰপদ": "মীন", "উত্তৰভাদ্ৰপদ": "মীন", "ৰেৱতী": "মীন"
}

# Fix: some nakshatras span two rashis, we need the primary one
# For matching purposes, we use the rashi provided by the user directly
# The above mapping is for reference only


# ═══════════════════════════════════════════════════════════════════════════════
# ASHTAKOOT CALCULATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_varna(boy_rashi, girl_rashi):
    """
    ১. বৰ্ণ কূট (Varna Koota) - Max 1 Point
    Spiritual and mental compatibility based on caste/varna of rashis.
    Boy's varna should be equal to or higher than girl's varna.
    """
    boy_varna = VARNA_BY_RASHI.get(boy_rashi, 3)
    girl_varna = VARNA_BY_RASHI.get(girl_rashi, 3)

    if boy_varna <= girl_varna:  # Lower number = higher varna (1=Brahmin highest)
        score = 1
        result = "উত্তম"
    else:
        score = 0
        result = "অমিল"

    return {
        "score": score,
        "max_score": 1,
        "result": result,
        "boy_varna": VARNA_NAMES.get(boy_varna, ""),
        "girl_varna": VARNA_NAMES.get(girl_varna, ""),
        "description": f"পাত্ৰৰ বৰ্ণ {VARNA_NAMES.get(boy_varna, '')} আৰু পাত্ৰীৰ বৰ্ণ {VARNA_NAMES.get(girl_varna, '')}।"
    }


def calculate_vashya(boy_rashi, girl_rashi):
    """
    ২. বশ্য কূট (Vashya Koota) - Max 2 Points
    Mutual control, attraction, and influence between partners.
    """
    boy_vashya = VASHYA_BY_RASHI.get(boy_rashi, 2)
    girl_vashya = VASHYA_BY_RASHI.get(girl_rashi, 2)

    # Check if girl's vashya type is compatible with boy's
    if girl_vashya in VASHYA_COMPAT.get(boy_vashya, []):
        score = 2
        result = "উত্তম"
    elif boy_vashya in VASHYA_COMPAT.get(girl_vashya, []):
        score = 1
        result = "মধ্যম"
    else:
        score = 0
        result = "অমিল"

    return {
        "score": score,
        "max_score": 2,
        "result": result,
        "boy_vashya": VASHYA_NAMES.get(boy_vashya, ""),
        "girl_vashya": VASHYA_NAMES.get(girl_vashya, ""),
        "description": f"পাত্ৰৰ বশ্য {VASHYA_NAMES.get(boy_vashya, '')} আৰু পাত্ৰীৰ বশ্য {VASHYA_NAMES.get(girl_vashya, '')}।"
    }


def calculate_tara(boy_nakshatra, girl_nakshatra):
    """
    ৩. তাৰা কূট (Tara Koota) - Max 3 Points
    Destiny, health, and well-being compatibility.
    Based on nakshatra distance (Tara Bala).
    """
    boy_idx = NAKSHATRAS.index(boy_nakshatra)
    girl_idx = NAKSHATRAS.index(girl_nakshatra)

    # Count from BOY to GIRL (traditional Ashtakoot rule)
    distance = (girl_idx - boy_idx) % 27
    tara = (distance % 9) + 1  # 1-9

    # Tara classification:
    # 1=Janma (birth), 2=Sampat (wealth), 3=Vipat (danger), 4=Kshem (wellbeing),
    # 5=Pratyari (obstacle), 6=Sadhak (achiever), 7=Naidhana (death),
    # 8=Mitra (friend), 9=Parama Mitra (best friend)
    tara_names = {
        1: "জন্ম", 2: "সম্পৎ", 3: "বিপৎ", 4: "ক্ষেম", 5: "প্ৰত্যৰি",
        6: "সাধক", 7: "নৈধন", 8: "মিত্ৰ", 9: "পৰম মিত্ৰ"
    }

    # Scoring
    if tara in [2, 4, 6, 8, 9]:  # Auspicious taras
        score = 3
        result = "উত্তম"
    elif tara in [1, 5]:  # Neutral
        score = 1.5
        result = "মধ্যম"
    else:  # 3=Vipat, 7=Naidhana - inauspicious
        score = 0
        result = "অশুভ"

    return {
        "score": score,
        "max_score": 3,
        "result": result,
        "tara_number": tara,
        "tara_name": tara_names.get(tara, ""),
        "distance": distance,
        "description": f"পাত্ৰীৰ নক্ষত্ৰৰ পৰা পাত্ৰৰ নক্ষত্ৰলৈ {distance} নক্ষত্ৰৰ ব্যৱধান, তাৰা: {tara_names.get(tara, '')} ({tara})।"
    }


def calculate_yoni(boy_nakshatra, girl_nakshatra):
    """
    ৪. যোনি কূট (Yoni Koota) - Max 4 Points
    Physical compatibility, intimacy, and biological harmony.
    Based on animal yoni of nakshatras.
    """
    boy_yoni = YONI_BY_NAKSHATRA.get(boy_nakshatra, "")
    girl_yoni = YONI_BY_NAKSHATRA.get(girl_nakshatra, "")

    if boy_yoni == girl_yoni:
        score = 4
        result = "উত্তম (একে যোনি)"
    elif girl_yoni in YONI_FRIENDLY.get(boy_yoni, []):
        score = 3
        result = "উত্তম (মিত্ৰ যোনি)"
    elif boy_yoni in YONI_ENEMY.get(girl_yoni, []):
        score = 0
        result = "অশুভ (শত্ৰু যোনি)"
    else:
        score = 2
        result = "মধ্যম (সাধাৰণ)"

    return {
        "score": score,
        "max_score": 4,
        "result": result,
        "boy_yoni": boy_yoni,
        "girl_yoni": girl_yoni,
        "description": f"পাত্ৰৰ যোনি '{boy_yoni}' আৰু পাত্ৰীৰ যোনি '{girl_yoni}'।"
    }


def calculate_graha_maitri(boy_rashi, girl_rashi):
    """
    ৫. গ্ৰহ মৈত্ৰী কূট (Graha Maitri) - Max 5 Points
    Psychological disposition and friendship between Moon sign lords.
    """
    boy_lord = RASHI_LORDS.get(boy_rashi, "")
    girl_lord = RASHI_LORDS.get(girl_rashi, "")

    if boy_lord == girl_lord:
        score = 5
        result = "উত্তম (একে গ্ৰহ)"
    else:
        friendship = PLANET_FRIENDSHIP.get(boy_lord, {}).get(girl_lord, 3)
        if friendship == 5:  # Adhi Mitra
            score = 5
            result = "উত্তম (অধি মিত্ৰ)"
        elif friendship == 4:  # Mitra
            score = 4
            result = "উত্তম (মিত্ৰ)"
        elif friendship == 3:  # Sama
            score = 3
            result = "মধ্যম (সম)"
        elif friendship == 2:  # Shatru
            score = 1
            result = "অমিল (শত্ৰু)"
        else:  # Adhi Shatru
            score = 0
            result = "অশুভ (অধি শত্ৰু)"

    return {
        "score": score,
        "max_score": 5,
        "result": result,
        "boy_lord": boy_lord,
        "girl_lord": girl_lord,
        "description": f"পাত্ৰৰ ৰাশি অধিপতি '{boy_lord}' আৰু পাত্ৰীৰ ৰাশি অধিপতি '{girl_lord}'।"
    }


def calculate_gana(boy_nakshatra, girl_nakshatra):
    """
    ৬. গণ কূট (Gana Koota) - Max 6 Points
    Behavioral temperament compatibility (Deva, Manushya, Rakshasa).
    """
    boy_gana = GANA_BY_NAKSHATRA.get(boy_nakshatra, 2)
    girl_gana = GANA_BY_NAKSHATRA.get(girl_nakshatra, 2)

    if boy_gana == girl_gana:
        score = 6
        result = "উত্তম (একে গণ)"
    elif (boy_gana == 1 and girl_gana == 2) or (boy_gana == 2 and girl_gana == 1):
        # Deva + Manushya
        score = 5
        result = "উত্তম"
    elif (boy_gana == 1 and girl_gana == 3) or (boy_gana == 3 and girl_gana == 1):
        # Deva + Rakshasa
        score = 1
        result = "অমিল (দেৱ-ৰাক্ষস)"
    elif (boy_gana == 2 and girl_gana == 3) or (boy_gana == 3 and girl_gana == 2):
        # Manushya + Rakshasa
        score = 0
        result = "অমিল (মনুষ্য-ৰাক্ষস)"
    else:
        score = 0
        result = "অমিল"

    return {
        "score": score,
        "max_score": 6,
        "result": result,
        "boy_gana": GANA_NAMES.get(boy_gana, ""),
        "girl_gana": GANA_NAMES.get(girl_gana, ""),
        "description": f"পাত্ৰৰ গণ '{GANA_NAMES.get(boy_gana, '')}' আৰু পাত্ৰীৰ গণ '{GANA_NAMES.get(girl_gana, '')}'।"
    }


def calculate_bhakoot(boy_rashi, girl_rashi):
    """
    ৭. ভকূট কূট (Bhakoot Koota) - Max 7 Points
    Family welfare, prosperity, and emotional longevity.
    Based on relative rashi positions (2-12, 5-9, 6-8 dosha checks).
    """
    boy_idx = RASHIS.index(boy_rashi)
    girl_idx = RASHIS.index(girl_rashi)

    # Count from girl to boy
    distance = (boy_idx - girl_idx) % 12

    # Bhakoot dosha: 2-12, 5-9, 6-8 positions
    if distance in [2, 5, 6]:
        # Inauspicious: 2-12, 5-9, 6-8
        score = 0
        if distance == 2:
            dosha_name = "২-১২ দোষ (দ্বি-দ্বাদশ)"
        elif distance == 5:
            dosha_name = "৫-৯ দোষ (পঞ্চ-নৱম)"
        else:
            dosha_name = "৬-৮ দোষ (ষষ্ঠ-অষ্টম)"
        result = f"অশুভ ({dosha_name})"
    elif distance in [1, 3, 4, 7, 9, 10]:
        score = 7
        result = "উত্তম"
    else:  # 0, 8, 11
        score = 4
        result = "মধ্যম"

    return {
        "score": score,
        "max_score": 7,
        "result": result,
        "distance": distance,
        "description": f"পাত্ৰীৰ ৰাশিৰ পৰা পাত্ৰৰ ৰাশি {distance} ঘৰ দূৰত্বত অৱস্থিত।"
    }


def calculate_nadi(boy_nakshatra, girl_nakshatra):
    """
    ৮. নাড়ী কূট (Nadi Koota) - Max 8 Points
    Genetic health, progeny (সন্তান সুখ), and physiological compatibility.
    Same nadi = Nadi Dosha (নাড়ী দোষ).
    """
    boy_nadi = NADI_BY_NAKSHATRA.get(boy_nakshatra, 1)
    girl_nadi = NADI_BY_NAKSHATRA.get(girl_nakshatra, 1)

    if boy_nadi == girl_nadi:
        score = 0
        result = f"অশুভ (নাড়ী দোষ - {NADI_NAMES.get(boy_nadi, '')} নাড়ী)"
    else:
        score = 8
        result = "উত্তম (নাড়ী দোষ নাই)"

    return {
        "score": score,
        "max_score": 8,
        "result": result,
        "boy_nadi": NADI_NAMES.get(boy_nadi, ""),
        "girl_nadi": NADI_NAMES.get(girl_nadi, ""),
        "description": f"পাত্ৰৰ নাড়ী '{NADI_NAMES.get(boy_nadi, '')}' আৰু পাত্ৰীৰ নাড়ী '{NADI_NAMES.get(girl_nadi, '')}'।"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MANGALIK DOSHA ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

MANGAL_HOUSES = [1, 4, 7, 8, 12]  # Houses where Mars causes Mangalik Dosha

def analyze_mangalik(boy_mars_house, girl_mars_house):
    """
    Analyze Mangalik Dosha for both boy and girl.
    mars_house: 1-12 (1-indexed house number)
    Returns detailed analysis.
    """
    boy_mangalik = boy_mars_house in MANGAL_HOUSES
    girl_mangalik = girl_mars_house in MANGAL_HOUSES

    # Determine severity
    def get_severity(house):
        if house == 7:
            return "তীব্ৰ"  # 7th house is most severe for marriage
        elif house in [1, 8]:
            return "মধ্যম"
        elif house in [4, 12]:
            return "সামান্য"
        return "অনুপস্থিত"

    boy_severity = get_severity(boy_mars_house) if boy_mangalik else "অনুপস্থিত"
    girl_severity = get_severity(girl_mars_house) if girl_mangalik else "অনুপস্থিত"

    # Cancellation logic
    cancellation = ""
    if boy_mangalik and girl_mangalik:
        cancellation = "দোষ সাম্য (উভয় মাংগলিক হোৱাৰ বাবে দোষৰ প্ৰভাৱ পৰস্পৰে নিষ্ক্ৰিয় কৰে)"
    elif not boy_mangalik and not girl_mangalik:
        cancellation = "কোনো মাংগলিক দোষ নাই"

    return {
        "boy_mangalik": boy_mangalik,
        "girl_mangalik": girl_mangalik,
        "boy_mars_house": boy_mars_house,
        "girl_mars_house": girl_mars_house,
        "boy_severity": boy_severity,
        "girl_severity": girl_severity,
        "cancellation": cancellation,
        "remedies": [
            "প্ৰতিদিন হনুমান চালিচা পাঠ কৰক",
            "মঙ্গলবাৰে ব্ৰত ৰাখক আৰু হনুমান মন্দিৰ দৰ্শন কৰক",
            "সেন্দুৰ আৰু মছুৰ দালি দান কৰক",
            "ৰঙা ৰঙৰ বস্ত্ৰ পৰিহাৰ কৰক",
            "মঙ্গল গ্ৰহৰ মন্ত্ৰ জাপ কৰক: 'ওঁ ক্ৰাং ক্ৰীং ক্ৰৌং সঃ ভৌমায় নমঃ'",
            "বিবাহৰ পূৰ্বে মাংগলিক দোষ নিবাৰণ পূজা কৰাওক",
            "তুলসী গছত জল অৰ্পণ কৰক আৰু প্ৰদক্ষিণ কৰক",
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN MATCHING FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def get_complete_jotok_milan(boy_data, girl_data):
    """
    Complete marriage matching analysis.

    Parameters:
    boy_data = {
        "name": str,
        "rashi": str (e.g., "মেষ"),
        "nakshatra": str (e.g., "অশ্বিনী"),
        "charan": int (1-4),
        "lagna": str (e.g., "মেষ"),
        "mars_house": int (1-12, 1-indexed)
    }
    girl_data = same structure

    Returns a comprehensive dict with all analysis.
    """
    boy_rashi = boy_data["rashi"]
    girl_rashi = girl_data["rashi"]
    boy_nakshatra = boy_data["nakshatra"]
    girl_nakshatra = girl_data["nakshatra"]

    # Calculate all 8 kootas
    varna = calculate_varna(boy_rashi, girl_rashi)
    vashya = calculate_vashya(boy_rashi, girl_rashi)
    tara = calculate_tara(boy_nakshatra, girl_nakshatra)
    yoni = calculate_yoni(boy_nakshatra, girl_nakshatra)
    graha_maitri = calculate_graha_maitri(boy_rashi, girl_rashi)
    gana = calculate_gana(boy_nakshatra, girl_nakshatra)
    bhakoot = calculate_bhakoot(boy_rashi, girl_rashi)
    nadi = calculate_nadi(boy_nakshatra, girl_nakshatra)

    # Total score
    total_score = sum([
        varna["score"], vashya["score"], tara["score"], yoni["score"],
        graha_maitri["score"], gana["score"], bhakoot["score"], nadi["score"]
    ])

    # Mangalik analysis
    mangalik = analyze_mangalik(boy_data.get("mars_house", 0), girl_data.get("mars_house", 0))

    # Overall verdict
    if total_score >= 28:
        verdict = "উত্তম (অতি শুভ)"
        verdict_class = "excellent"
        verdict_desc = "এই যোটক অতি উত্তম। বিবাহৰ বাবে অত্যন্ত শুভ আৰু সুপাৰিশিত। দাম্পত্য জীৱন সুখময়, সমৃদ্ধিশালী আৰু দীৰ্ঘস্থায়ী হ'ব।"
    elif total_score >= 22:
        verdict = "মধ্যম (শুভ)"
        verdict_class = "good"
        verdict_desc = "এই যোটক মধ্যম শ্ৰেণীৰ। বিবাহৰ বাবে গ্ৰহণযোগ্য। সামান্য প্ৰতিকাৰৰ দ্বাৰা দাম্পত্য জীৱন সুখময় কৰিব পাৰি।"
    elif total_score >= 18:
        verdict = "মধ্যম (গ্ৰহণযোগ্য)"
        verdict_class = "average"
        verdict_desc = "এই যোটক গড় মানৰ। কিছুমান দোষ থাকিলেও উপযুক্ত প্ৰতিকাৰৰ দ্বাৰা বিবাহ সম্ভৱ। জ্যোতিষীৰ পৰামৰ্শ লোৱাটো উচিত।"
    elif total_score >= 12:
        verdict = "অমিল (সাৱধানতা প্ৰয়োজন)"
        verdict_class = "warning"
        verdict_desc = "এই যোটকত যথেষ্ট অমিল আছে। বিবাহৰ পূৰ্বে জ্যোতিষীৰ পৰামৰ্শ আৰু প্ৰতিকাৰ অতি জৰুৰী।"
    else:
        verdict = "অশুভ (বিবাহ পৰামৰ্শিত নহয়)"
        verdict_class = "bad"
        verdict_desc = "এই যোটক অশুভ। পৰম্পৰাগতভাৱে এনে যোটকত বিবাহ পৰামৰ্শিত নহয়। তথাপিও জ্যোতিষীৰ পৰামৰ্শ লওক।"

    # Check for Nadi Dosha specifically
    has_nadi_dosha = nadi["score"] == 0
    has_bhakoot_dosha = bhakoot["score"] == 0

    return {
        "boy": boy_data,
        "girl": girl_data,
        "kootas": {
            "varna": varna,
            "vashya": vashya,
            "tara": tara,
            "yoni": yoni,
            "graha_maitri": graha_maitri,
            "gana": gana,
            "bhakoot": bhakoot,
            "nadi": nadi
        },
        "total_score": total_score,
        "max_score": 36,
        "verdict": verdict,
        "verdict_class": verdict_class,
        "verdict_desc": verdict_desc,
        "mangalik": mangalik,
        "has_nadi_dosha": has_nadi_dosha,
        "has_bhakoot_dosha": has_bhakoot_dosha
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ASSAMESE REPORT GENERATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def get_koota_name_asm(koota_key):
    """Get Assamese name for a koota."""
    names = {
        "varna": "বৰ্ণ কূট",
        "vashya": "বশ্য কূট",
        "tara": "তাৰা কূট",
        "yoni": "যোনি কূট",
        "graha_maitri": "গ্ৰহ মৈত্ৰী কূট",
        "gana": "গণ কূট",
        "bhakoot": "ভকূট কূট",
        "nadi": "নাড়ী কূট"
    }
    return names.get(koota_key, koota_key)


def get_koota_icon(koota_key):
    """Get icon for a koota."""
    icons = {
        "varna": "🕉️",
        "vashya": "💑",
        "tara": "⭐",
        "yoni": "💕",
        "graha_maitri": "🪐",
        "gana": "🎭",
        "bhakoot": "🏠",
        "nadi": "🧬"
    }
    return icons.get(koota_key, "✨")
