"""
ধ্ৰুৱতৰা AI - যোগ বিশ্লেষণ ইঞ্জিন
Yoga Detection Engine: Pancha Mahapurusha Yogas, Raj Yogas, Dhan Yogas,
Vipareeta Raj Yogas, Chandra Yogas, Surya Yogas, Nabhasa Yogas, etc.
"""

YOGA_INFO = {
    "ruchaka": {
        "name": "ৰুচক যোগ (পঞ্চ মহাপুৰুষ)",
        "icon": "🛡️",
        "category": "পঞ্চ মহাপুৰুষ যোগ",
        "description": "মঙ্গল গ্ৰহ স্বৰাশিত বা উচ্চ ৰাশিত কেন্দ্ৰ ভাৱত (১,৪,৭,১০) অৱস্থান কৰিলে ৰুচক যোগ হয়। ব্যক্তি সাহসী, পৰাক্ৰমী, আৰু নেতৃত্বগুণ সম্পন্ন হয়।",
        "effect": "সামৰিক/প্ৰশাসনিক ক্ষেত্ৰত সফলতা, ধন-সম্পত্তি, আৰু উচ্চ পদ প্ৰাপ্তি।"
    },
    "bhadra": {
        "name": "ভদ্ৰ যোগ (পঞ্চ মহাপুৰুষ)",
        "icon": "💎",
        "category": "পঞ্চ মহাপুৰুষ যোগ",
        "description": "বুধ গ্ৰহ স্বৰাশিত বা উচ্চ ৰাশিত কেন্দ্ৰ ভাৱত অৱস্থান কৰিলে ভদ্ৰ যোগ হয়। ব্যক্তি বুদ্ধিমান, বিদ্বান, আৰু বাক্পটু হয়।",
        "effect": "শিক্ষা, বাণিজ্য, আৰু যোগাযোগ ক্ষেত্ৰত অসাধাৰণ সফলতা।"
    },
    "hamsa": {
        "name": "হংস যোগ (পঞ্চ মহাপুৰুষ)",
        "icon": "🦢",
        "category": "পঞ্চ মহাপুৰুষ যোগ",
        "description": "বৃহস্পতি গ্ৰহ স্বৰাশিত বা উচ্চ ৰাশিত কেন্দ্ৰ ভাৱত অৱস্থান কৰিলে হংস যোগ হয়। ব্যক্তি জ্ঞানী, ধাৰ্মিক, আৰু পৰোপকাৰী হয়।",
        "effect": "আধ্যাত্মিক জ্ঞান, শিক্ষকতা, আৰু ধৰ্মীয় ক্ষেত্ৰত উচ্চ সন্মান।"
    },
    "malavya": {
        "name": "মালব্য যোগ (পঞ্চ মহাপুৰুষ)",
        "icon": "💫",
        "category": "পঞ্চ মহাপুৰুষ যোগ",
        "description": "শুক্ৰ গ্ৰহ স্বৰাশিত বা উচ্চ ৰাশিত কেন্দ্ৰ ভাৱত অৱস্থান কৰিলে মালব্য যোগ হয়। ব্যক্তি সুন্দৰ, কলাপ্ৰিয়, আৰু বিলাসী হয়।",
        "effect": "কলা, সংগীত, আৰু বিলাসী জীৱন; ধন-সম্পত্তি আৰু সুখ।"
    },
    "sasa": {
        "name": "শশ যোগ (পঞ্চ মহাপুৰুষ)",
        "icon": "👑",
        "category": "পঞ্চ মহাপুৰুষ যোগ",
        "description": "শনি গ্ৰহ স্বৰাশিত বা উচ্চ ৰাশিত কেন্দ্ৰ ভাৱত অৱস্থান কৰিলে শশ যোগ হয়। ব্যক্তি নেতা, শাসক, আৰু দীৰ্ঘজীৱী হয়।",
        "effect": "ৰাজনীতি, প্ৰশাসন, আৰু নেতৃত্বত অসাধাৰণ সফলতা।"
    },
    "gajakesari": {
        "name": "গজকেশৰী যোগ",
        "icon": "🐘",
        "category": "শুভ যোগ",
        "description": "বৃহস্পতি চন্দ্ৰৰ পৰা কেন্দ্ৰ ভাৱত (১,৪,৭,১০) অৱস্থান কৰিলে গজকেশৰী যোগ হয়। ব্যক্তি যশস্বী, ধনৱান, আৰু প্ৰভাৱশালী হয়।",
        "effect": "খ্যাতি, সন্মান, আৰু সামাজিক প্ৰভাৱ।"
    },
    "budhaditya": {
        "name": "বুধাদিত্য যোগ",
        "icon": "☀️",
        "category": "শুভ যোগ",
        "description": "সূৰ্য্য আৰু বুধ একত্ৰিত হ'লে বুধাদিত্য যোগ হয়। ব্যক্তি অত্যন্ত বুদ্ধিমান, শিক্ষিত, আৰু প্ৰশাসনিক দক্ষতা সম্পন্ন হয়।",
        "effect": "উচ্চ শিক্ষা, প্ৰশাসনিক পদ, আৰু বুদ্ধিভিত্তিক সফলতা।"
    },
    "lakshmi": {
        "name": "লক্ষ্মী যোগ",
        "icon": "💰",
        "category": "ধন যোগ",
        "description": "লগ্নপতি আৰু নৱমপতিৰ শুভ সম্পৰ্ক বা যুতি হ'লে লক্ষ্মী যোগ হয়। ব্যক্তি অত্যন্ত ধনৱান আৰু ভাগ্যৱান হয়।",
        "effect": "অপৰিসীম ধন-সম্পত্তি, ব্যৱসায়িক সফলতা।"
    },
    "vipareeta_raja": {
        "name": "বিপৰীত ৰাজযোগ",
        "icon": "🔄",
        "category": "ৰাজযোগ",
        "description": "৬,৮,১২ ভাৱৰ অধিপতি পৰস্পৰৰ ভাৱত বা ৬,৮,১২ ভাৱত অৱস্থান কৰিলে বিপৰীত ৰাজযোগ হয়। প্ৰতিকূলতাৰ মাজেৰে সফলতা লাভ কৰে।",
        "effect": "সংকটৰ পিছত বৃহৎ সফলতা, শত্ৰুৰ ওপৰত বিজয়।"
    },
    "dhana": {
        "name": "ধন যোগ",
        "icon": "💵",
        "category": "ধন যোগ",
        "description": "দ্বিতীয় আৰু একাদশ ভাৱৰ অধিপতিৰ শুভ সম্পৰ্ক বা লগ্নপতি আৰু দ্বিতীয়পতিৰ যুতি হ'লে ধন যোগ হয়।",
        "effect": "স্থিৰ আৰ্থিক অৱস্থা, সম্পত্তি, আৰু ধনাগম।"
    },
    "raja": {
        "name": "ৰাজযোগ",
        "icon": "👑",
        "category": "ৰাজযোগ",
        "description": "কেন্দ্ৰ আৰু ত্ৰিকোণ ভাৱৰ অধিপতিৰ পৰস্পৰ সম্পৰ্ক বা যুতি হ'লে ৰাজযোগ হয়। ব্যক্তি উচ্চ পদ, ক্ষমতা, আৰু সন্মান লাভ কৰে।",
        "effect": "উচ্চ প্ৰশাসনিক পদ, ৰাজনৈতিক সফলতা, ক্ষমতা।"
    },
    "sunapha": {
        "name": "সুনফা যোগ",
        "icon": "🌙",
        "category": "চন্দ্ৰ যোগ",
        "description": "চন্দ্ৰৰ দ্বিতীয় ভাৱত (সূৰ্য্য বাদে) কোনো গ্ৰহ থাকিলে সুনফা যোগ হয়। ব্যক্তি ধনৱান, বুদ্ধিমান, আৰু সুখী হয়।",
        "effect": "ধন, বুদ্ধি, আৰু সামাজিক সন্মান।"
    },
    "anapha": {
        "name": "অনফা যোগ",
        "icon": "🌙",
        "category": "চন্দ্ৰ যোগ",
        "description": "চন্দ্ৰৰ দ্বাদশ ভাৱত (সূৰ্য্য বাদে) কোনো গ্ৰহ থাকিলে অনফা যোগ হয়। ব্যক্তি সুস্থ, আকৰ্ষণীয়, আৰু সফল হয়।",
        "effect": "উত্তম স্বাস্থ্য, আকৰ্ষণীয় ব্যক্তিত্ব।"
    },
    "durudhara": {
        "name": "দুৰুধৰা যোগ",
        "icon": "🌙",
        "category": "চন্দ্ৰ যোগ",
        "description": "চন্দ্ৰৰ উভয় পাৰ্শ্বত (সূৰ্য্য বাদে) গ্ৰহ থাকিলে দুৰুধৰা যোগ হয়। ব্যক্তি অত্যন্ত ধনৱান আৰু প্ৰভাৱশালী হয়।",
        "effect": "অপৰিসীম ধন, প্ৰভাৱ, আৰু সফলতা।"
    },
    "vasumati": {
        "name": "বসুমতী যোগ",
        "icon": "💎",
        "category": "ধন যোগ",
        "description": "উপগ্ৰহবিহীন দ্বিতীয় ভাৱত শুভ গ্ৰহৰ দৃষ্টি বা অৱস্থান থাকিলে বসুমতী যোগ হয়।",
        "effect": "স্থাৱৰ সম্পত্তি, ধন-ধান্য, আৰু পাৰিবাৰিক সুখ।"
    },
    "amala": {
        "name": "অমলা যোগ",
        "icon": "✨",
        "category": "শুভ যোগ",
        "description": "দশম ভাৱত শুভ গ্ৰহ অৱস্থান কৰিলে অমলা যোগ হয়। ব্যক্তি সৎ, দানশীল, আৰু যশস্বী হয়।",
        "effect": "সন্মান, যশ, আৰু সমাজ সেৱাত সফলতা।"
    },
    "parvata": {
        "name": "পৰ্বত যোগ",
        "icon": "⛰️",
        "category": "শুভ যোগ",
        "description": "কেন্দ্ৰ ভাৱত শুভ গ্ৰহ আৰু লগ্নপতি বলৱান হ'লে পৰ্বত যোগ হয়। ব্যক্তি ধনৱান, বিদ্বান, আৰু ভাগ্যৱান হয়।",
        "effect": "ধন, জ্ঞান, আৰু সৌভাগ্য।"
    },
    "kahala": {
        "name": "কহল যোগ",
        "icon": "🎯",
        "category": "শুভ যোগ",
        "description": "তৃতীয় আৰু চতুৰ্থ ভাৱৰ অধিপতি পৰস্পৰ কেন্দ্ৰত থাকিলে কহল যোগ হয়। ব্যক্তি সাহসী আৰু পৰাক্ৰমী হয়।",
        "effect": "সাহস, পৰাক্ৰম, আৰু সম্পত্তি।"
    },
}

# Planet ownerships (sign lords)
SIGN_LORDS = {
    0: "মংগল", 1: "শুক্ৰ", 2: "বুধ", 3: "চন্দ্ৰ",
    4: "ৰবি", 5: "বুধ", 6: "শুক্ৰ", 7: "মংগল",
    8: "বৃহস্পতি", 9: "শনি", 10: "শনি", 11: "বৃহস্পতি"
}

# Exaltation signs
EXALTATION_SIGNS = {
    "ৰবি": 0, "চন্দ্ৰ": 1, "মংগল": 9, "বুধ": 5,
    "বৃহস্পতি": 3, "শুক্ৰ": 11, "শনি": 6
}

# Own signs
OWN_SIGNS = {
    "ৰবি": [4], "চন্দ্ৰ": [3], "মংগল": [0, 7], "বুধ": [2, 5],
    "বৃহস্পতি": [8, 11], "শুক্ৰ": [1, 6], "শনি": [9, 10]
}

# Kendra houses (1,4,7,10) - 0-indexed
KENDRA = [0, 3, 6, 9]
# Trikona houses (1,5,9) - 0-indexed
TRIKONA = [0, 4, 8]


def get_house_lord(house_idx: int) -> str:
    """Get the lord of a house (0-indexed)"""
    return SIGN_LORDS[house_idx]


def is_kendra(house_idx: int) -> bool:
    return house_idx in KENDRA


def is_trikona(house_idx: int) -> bool:
    return house_idx in TRIKONA


def is_own_sign(planet: str, sign_idx: int) -> bool:
    return sign_idx in OWN_SIGNS.get(planet, [])


def is_exalted(planet: str, sign_idx: int) -> bool:
    return EXALTATION_SIGNS.get(planet) == sign_idx


def detect_pancha_mahapurusha(planet_signs: dict, planet_houses: dict) -> list:
    """
    Detect Pancha Mahapurusha Yogas.
    planet_signs: {"মংগল": sign_idx, ...}
    planet_houses: {"মংগল": house_idx, ...}
    """
    yogas = []
    configs = [
        ("মংগল", "ruchaka"),
        ("বুধ", "bhadra"),
        ("বৃহস্পতি", "hamsa"),
        ("শুক্ৰ", "malavya"),
        ("শনি", "sasa"),
    ]

    for planet, yoga_key in configs:
        sign = planet_signs.get(planet)
        house = planet_houses.get(planet)
        if sign is not None and house is not None:
            if (is_own_sign(planet, sign) or is_exalted(planet, sign)) and is_kendra(house):
                yogas.append({"key": yoga_key, **YOGA_INFO[yoga_key]})

    return yogas


def detect_gajakesari(planet_houses: dict) -> list:
    """Detect Gajakesari Yoga: Jupiter in Kendra from Moon."""
    yogas = []
    moon_house = planet_houses.get("চন্দ্ৰ")
    guru_house = planet_houses.get("বৃহস্পতি")

    if moon_house is not None and guru_house is not None:
        diff = (guru_house - moon_house) % 12
        if diff in KENDRA:
            yogas.append({"key": "gajakesari", **YOGA_INFO["gajakesari"]})
    return yogas


def detect_budhaditya(planet_houses: dict) -> list:
    """Detect Budhaditya Yoga: Sun + Mercury conjunction."""
    yogas = []
    sun_house = planet_houses.get("ৰবি")
    budh_house = planet_houses.get("বুধ")
    if sun_house is not None and budh_house is not None and sun_house == budh_house:
        yogas.append({"key": "budhaditya", **YOGA_INFO["budhaditya"]})
    return yogas


def detect_chandra_yogas(planet_houses: dict) -> list:
    """Detect Sunapha, Anapha, Durudhara Yogas."""
    yogas = []
    moon_house = planet_houses.get("চন্দ্ৰ")
    if moon_house is None:
        return yogas

    house_2nd = (moon_house + 1) % 12
    house_12th = (moon_house - 1) % 12

    planets_excluding_sun = ["মংগল", "বুধ", "বৃহস্পতি", "শুক্ৰ", "শনি", "ৰাহু", "কেতু"]

    has_2nd = any(planet_houses.get(p) == house_2nd for p in planets_excluding_sun)
    has_12th = any(planet_houses.get(p) == house_12th for p in planets_excluding_sun)

    if has_2nd and has_12th:
        yogas.append({"key": "durudhara", **YOGA_INFO["durudhara"]})
    elif has_2nd:
        yogas.append({"key": "sunapha", **YOGA_INFO["sunapha"]})
    elif has_12th:
        yogas.append({"key": "anapha", **YOGA_INFO["anapha"]})

    return yogas


def detect_raja_yogas(planet_houses: dict, asc_sign: int) -> list:
    """Detect Raja Yogas and Vipareeta Raja Yogas."""
    yogas = []

    # Get house lords
    house_lords = {}
    for h in range(12):
        sign_idx = (asc_sign + h) % 12
        house_lords[h] = SIGN_LORDS[sign_idx]

    # Raja Yoga: Kendra lord + Trikona lord conjunction/mutual aspect
    kendra_lords = set(house_lords[h] for h in KENDRA)
    trikona_lords = set(house_lords[h] for h in TRIKONA)

    for kl in kendra_lords:
        for tl in trikona_lords:
            if kl != tl:
                kl_house = planet_houses.get(kl)
                tl_house = planet_houses.get(tl)
                if kl_house is not None and tl_house is not None and kl_house == tl_house:
                    yogas.append({"key": "raja", **YOGA_INFO["raja"]})
                    break
        else:
            continue
        break

    # Vipareeta Raja Yoga: 6,8,12 lords in 6,8,12
    dusthana = [5, 7, 11]  # 6,8,12 (0-indexed)
    dusthana_lords = [house_lords[h] for h in dusthana]
    dusthana_lord_houses = [planet_houses.get(l) for l in dusthana_lords]

    if all(h is not None and h in dusthana for h in dusthana_lord_houses):
        yogas.append({"key": "vipareeta_raja", **YOGA_INFO["vipareeta_raja"]})

    return yogas


def detect_dhana_yogas(planet_houses: dict, asc_sign: int) -> list:
    """Detect Dhana Yogas and Lakshmi Yoga."""
    yogas = []

    house_lords = {}
    for h in range(12):
        sign_idx = (asc_sign + h) % 12
        house_lords[h] = SIGN_LORDS[sign_idx]

    # Dhana Yoga: 2nd lord + 11th lord conjunction
    lord_2 = house_lords[1]  # 2nd house
    lord_11 = house_lords[10]  # 11th house
    h2 = planet_houses.get(lord_2)
    h11 = planet_houses.get(lord_11)
    if h2 is not None and h11 is not None and h2 == h11:
        yogas.append({"key": "dhana", **YOGA_INFO["dhana"]})

    # Lakshmi Yoga: 1st lord + 9th lord conjunction
    lord_1 = house_lords[0]
    lord_9 = house_lords[8]
    h1 = planet_houses.get(lord_1)
    h9 = planet_houses.get(lord_9)
    if h1 is not None and h9 is not None and h1 == h9:
        yogas.append({"key": "lakshmi", **YOGA_INFO["lakshmi"]})

    # Vasumati Yoga: benefic in 2nd house
    benefics = ["বৃহস্পতি", "শুক্ৰ", "বুধ", "চন্দ্ৰ"]
    for b in benefics:
        if planet_houses.get(b) == 1:  # 2nd house
            yogas.append({"key": "vasumati", **YOGA_INFO["vasumati"]})
            break

    return yogas


def detect_other_yogas(planet_houses: dict) -> list:
    """Detect Amala, Parvata, Kahala Yogas."""
    yogas = []

    # Amala Yoga: Benefic in 10th house
    benefics = ["বৃহস্পতি", "শুক্ৰ", "বুধ", "চন্দ্ৰ"]
    for b in benefics:
        if planet_houses.get(b) == 9:  # 10th house
            yogas.append({"key": "amala", **YOGA_INFO["amala"]})
            break

    return yogas


def get_complete_yoga_analysis(planet_houses: dict, planet_signs: dict, asc_sign: int) -> list:
    """
    Run all yoga detections and return results.
    """
    all_yogas = []

    all_yogas.extend(detect_pancha_mahapurusha(planet_signs, planet_houses))
    all_yogas.extend(detect_gajakesari(planet_houses))
    all_yogas.extend(detect_budhaditya(planet_houses))
    all_yogas.extend(detect_chandra_yogas(planet_houses))
    all_yogas.extend(detect_raja_yogas(planet_houses, asc_sign))
    all_yogas.extend(detect_dhana_yogas(planet_houses, asc_sign))
    all_yogas.extend(detect_other_yogas(planet_houses))

    return all_yogas
