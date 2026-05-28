"""
ধ্ৰুৱতৰা AI - দোষ বিশ্লেষণ ইঞ্জিন
Dosha Analysis Engine: Mangal Dosha, Kaal Sarp Dosha, Pitra Dosha, Grahan Dosha,
Nadi Dosha, Shani Dosha, Guru-Chandal Dosha, Kemadruma Dosha, etc.
"""

# ─── Assamese Dosha Names & Descriptions ────────────────────────

DOSHA_INFO = {
    "mangal_dosha": {
        "name": "মঙ্গল দোষ",
        "icon": "🔥",
        "severity_levels": ["অনুপস্থিত", "সামান্য", "মধ্যম", "তীব্ৰ", "অতি তীব্ৰ"],
        "description": "মঙ্গল গ্ৰহ লগ্ন, চতুৰ্থ, সপ্তম, অষ্টম বা দ্বাদশ ভাৱত অৱস্থান কৰিলে মঙ্গল দোষ হয়। ই বৈবাহিক জীৱনত সমস্যা, কলহ, আৰু বিলম্বিত বিবাহৰ কাৰণ হ'ব পাৰে।",
        "remedies": [
            "প্ৰতিদিন হনুমান চালিচা পাঠ কৰক",
            "মঙ্গলবাৰে ব্ৰত ৰাখক",
            "সেন্দুৰ আৰু মছুৰ দালি দান কৰক",
            "ৰঙা ৰঙৰ বস্ত্ৰ পৰিহাৰ কৰক",
            "মঙ্গল গ্ৰহৰ মন্ত্ৰ জাপ কৰক: 'ওঁ ক্ৰাং ক্ৰীং ক্ৰৌং সঃ ভৌমায় নমঃ'"
        ]
    },
    "kaal_sarp_dosha": {
        "name": "কাল সৰ্প দোষ",
        "icon": "🐍",
        "severity_levels": ["অনুপস্থিত", "আংশিক", "পূৰ্ণ"],
        "description": "যেতিয়া ৰাহু আৰু কেতুৰ মাজত সকলো গ্ৰহ আবদ্ধ থাকে, তেতিয়া কাল সৰ্প দোষ হয়। ই জীৱনত বাধা, ভয়, অনিদ্ৰা, আৰু কৰ্মক্ষেত্ৰত সংঘৰ্ষৰ সৃষ্টি কৰে।",
        "remedies": [
            "নাগ পঞ্চমীৰ দিনা বিশেষ পূজা কৰক",
            "শিৱলিংগত দুগ্ধ অভিষেক কৰক",
            "ৰাহু-কেতু মন্ত্ৰ জাপ কৰক: 'ওঁ ৰাং ৰাহবে নমঃ'",
            "কাল সৰ্প দোষ নিবাৰণ পূজা কৰাওক",
            "সোমবাৰে উপবাস ৰাখক"
        ]
    },
    "pitra_dosha": {
        "name": "পিতৃ দোষ",
        "icon": "🕉️",
        "severity_levels": ["অনুপস্থিত", "উপস্থিত"],
        "description": "সূৰ্য্য ৰাহু বা শনিৰ সৈতে যুক্ত হ'লে বা ৰাহু-কেতু নৱম ভাৱত থাকিলে পিতৃ দোষ হয়। ই সন্তানহীনতা, পিতৃ-পুত্ৰৰ সম্পৰ্কত টান, আৰু পাৰিবাৰিক অশান্তিৰ কাৰণ হয়।",
        "remedies": [
            "পিতৃপক্ষত শ্ৰাদ্ধ কৰক",
            "প্ৰতিদিন সূৰ্য্যক অৰ্ঘ্য দিয়ক",
            "আহত গছৰ গুৰত জল অৰ্পণ কৰক",
            "গয়াত পিণ্ডদান কৰক",
            "পিতৃসকলৰ ফটোৰ সন্মুখত দীপ প্ৰজ্বলন কৰক"
        ]
    },
    "grahan_dosha": {
        "name": "গ্ৰহণ দোষ",
        "icon": "🌑",
        "severity_levels": ["অনুপস্থিত", "সূৰ্য্য গ্ৰহণ", "চন্দ্ৰ গ্ৰহণ", "উভয়"],
        "description": "সূৰ্য্য বা চন্দ্ৰ ৰাহু-কেতুৰ সৈতে যুক্ত হ'লে গ্ৰহণ দোষ হয়। ই স্বাস্থ্যজনিত সমস্যা, মানসিক অস্থিৰতা, আৰু কৰ্মজীৱনত অনিশ্চয়তাৰ সৃষ্টি কৰে।",
        "remedies": [
            "গ্ৰহণৰ সময়ত মন্ত্ৰ জাপ কৰক",
            "দান-পুণ্য কৰক",
            "সূৰ্য্য গ্ৰহণ দোষৰ বাবে আদিত্য হৃদয় স্তোত্ৰ পাঠ কৰক",
            "চন্দ্ৰ গ্ৰহণ দোষৰ বাবে চন্দ্ৰ গ্ৰহ মন্ত্ৰ জপ কৰক",
            "গ্ৰহণৰ পিছত স্নান কৰি শুদ্ধ থাকক"
        ]
    },
    "nadi_dosha": {
        "name": "নাড়ী দোষ",
        "icon": "🧬",
        "severity_levels": ["অনুপস্থিত", "উপস্থিত"],
        "description": "বিবাহৰ বাবে গুৰুত্বপূৰ্ণ। স্বামী-স্ত্ৰীৰ নক্ষত্ৰ একে নাড়ীত পৰিলে নাড়ী দোষ হয়। ই সন্তানহীনতা, স্বাস্থ্যজনিত সমস্যা, আৰু দাম্পত্য কলহৰ কাৰণ হ'ব পাৰে।",
        "remedies": [
            "নাড়ী দোষ নিবাৰণ পূজা কৰাওক",
            "মহামৃত্যুঞ্জয় মন্ত্ৰ জপ কৰক",
            "শিৱ-পাৰ্বতীৰ উপাসনা কৰক",
            "সন্তানৰ বাবে বিশেষ অনুষ্ঠান কৰক"
        ]
    },
    "shani_dosha": {
        "name": "শনি দোষ (সাড়ে সাতী)",
        "icon": "🪐",
        "severity_levels": ["অনুপস্থিত", "সামান্য", "সাড়ে সাতী", "ঢৈয়া", "অতি তীব্ৰ"],
        "description": "শনি গ্ৰহৰ অশুভ প্ৰভাৱ। বিশেষকৈ সাড়ে সাতী (সাত বছৰৰ সময়) অতি কষ্টদায়ক। ই আৰ্থিক সংকট, স্বাস্থ্যহানি, আৰু মানসিক চাপৰ সৃষ্টি কৰে।",
        "remedies": [
            "শনিবাৰে হনুমান মন্দিৰ দৰ্শন কৰক",
            "তিল তেলৰ দীপ জ্বলাওক",
            "শনি মন্ত্ৰ জপ কৰক: 'ওঁ শং শনৈশ্চৰায় নমঃ'",
            "ক'লা বস্ত্ৰ আৰু তিল দান কৰক",
            "শনি চালিচা পাঠ কৰক"
        ]
    },
    "guru_chandal_dosha": {
        "name": "গুৰু-চাণ্ডাল দোষ",
        "icon": "⚡",
        "severity_levels": ["অনুপস্থিত", "উপস্থিত"],
        "description": "বৃহস্পতি আৰু ৰাহুৰ যুতি হ'লে গুৰু-চাণ্ডাল দোষ হয়। ই জ্ঞান আৰু নীতিৰ বিৰোধ, ধৰ্মীয় অনাস্থা, আৰু শিক্ষাত বাধাৰ সৃষ্টি কৰে।",
        "remedies": [
            "বৃহস্পতিবাৰে ব্ৰত ৰাখক",
            "হালধীয়া ৰঙৰ বস্ত্ৰ পৰিধান কৰক",
            "গুৰু গ্ৰহৰ মন্ত্ৰ জপ কৰক: 'ওঁ গ্ৰাং গ্ৰীং গ্ৰৌং সঃ গুৰবে নমঃ'",
            "কল গছৰ পূজা কৰক",
            "আহত গছত জল অৰ্পণ কৰক"
        ]
    },
    "kemadruma_dosha": {
        "name": "কেমদ্ৰুম দোষ",
        "icon": "🌊",
        "severity_levels": ["অনুপস্থিত", "উপস্থিত"],
        "description": "চন্দ্ৰৰ দুয়োফালে কোনো গ্ৰহ নাথাকিলে কেমদ্ৰুম দোষ হয়। ই মানসিক অস্থিৰতা, অকলশৰীয়া অনুভৱ, আৰু দৰিদ্ৰতাৰ কাৰণ হ'ব পাৰে।",
        "remedies": [
            "চন্দ্ৰ গ্ৰহৰ মন্ত্ৰ জাপ কৰক: 'ওঁ শ্ৰাং শ্ৰীং শ্ৰৌং সঃ চন্দ্ৰায় নমঃ'",
            "সোমবাৰে উপবাস ৰাখক",
            "শিৱলিংগত দুগ্ধ অভিষেক কৰক",
            "মুক্তা (মোতি) ধাৰণ কৰক",
            "শ্বেত বস্ত্ৰ দান কৰক"
        ]
    }
}


def analyze_mangal_dosha(planet_house_map: dict) -> dict:
    """
    Check Mangal Dosha: Mars in 1st, 4th, 7th, 8th, or 12th house.
    planet_house_map: {"মংগল": house_index, ...} (0-indexed houses)
    """
    mangal_house = planet_house_map.get("মংগল")
    if mangal_house is None:
        return {"present": False, "severity": 0, "houses": [], "info": DOSHA_INFO["mangal_dosha"]}

    dosha_houses = [0, 3, 6, 7, 11]  # 1,4,7,8,12 (0-indexed)
    affected = [h + 1 for h in dosha_houses if h == mangal_house]

    if not affected:
        return {"present": False, "severity": 0, "houses": [], "info": DOSHA_INFO["mangal_dosha"]}

    severity = min(len(affected), 4)
    return {
        "present": True,
        "severity": severity,
        "severity_text": DOSHA_INFO["mangal_dosha"]["severity_levels"][severity],
        "houses": affected,
        "info": DOSHA_INFO["mangal_dosha"]
    }


def analyze_kaal_sarp_dosha(planet_house_map: dict, planet_longitudes: dict) -> dict:
    """
    Check Kaal Sarp Dosha: All planets between Rahu and Ketu.
    """
    rahu_lon = planet_longitudes.get("ৰাহু", 0)
    ketu_lon = planet_longitudes.get("কেতু", 0)

    if rahu_lon is None or ketu_lon is None:
        return {"present": False, "severity": 0, "info": DOSHA_INFO["kaal_sarp_dosha"]}

    # Determine the arc from Rahu to Ketu
    start = rahu_lon
    end = ketu_lon
    if end < start:
        end += 360

    planets_between = []
    all_planets = ["ৰবি", "চন্দ্ৰ", "মংগল", "বুধ", "বৃহস্পতি", "শুক্ৰ", "শনি"]
    for p_name in all_planets:
        p_lon = planet_longitudes.get(p_name, 0)
        if p_lon is None:
            continue
        if start < p_lon < end or start < p_lon + 360 < end:
            planets_between.append(p_name)

    all_trapped = len(planets_between) == len(all_planets)
    partial = len(planets_between) >= 5

    if all_trapped:
        return {
            "present": True,
            "severity": 2,
            "severity_text": DOSHA_INFO["kaal_sarp_dosha"]["severity_levels"][2],
            "planets_between": planets_between,
            "info": DOSHA_INFO["kaal_sarp_dosha"]
        }
    elif partial:
        return {
            "present": True,
            "severity": 1,
            "severity_text": DOSHA_INFO["kaal_sarp_dosha"]["severity_levels"][1],
            "planets_between": planets_between,
            "info": DOSHA_INFO["kaal_sarp_dosha"]
        }

    return {"present": False, "severity": 0, "info": DOSHA_INFO["kaal_sarp_dosha"]}


def analyze_pitra_dosha(planet_house_map: dict, planet_longitudes: dict) -> dict:
    """
    Check Pitra Dosha: Sun conjunct Rahu/Saturn, or Rahu/Ketu in 9th house.
    """
    present = False
    reasons = []

    sun_house = planet_house_map.get("ৰবি")
    rahu_house = planet_house_map.get("ৰাহু")
    shani_house = planet_house_map.get("শনি")
    ketu_house = planet_house_map.get("কেতু")

    # Sun conjunct Rahu
    if sun_house is not None and rahu_house is not None and sun_house == rahu_house:
        present = True
        reasons.append("সূৰ্য্য-ৰাহু যুতি")

    # Sun conjunct Saturn
    if sun_house is not None and shani_house is not None and sun_house == shani_house:
        present = True
        reasons.append("সূৰ্য্য-শনি যুতি")

    # Rahu or Ketu in 9th house
    if rahu_house == 8:  # 9th house (0-indexed)
        present = True
        reasons.append("ৰাহু নৱম ভাৱত")
    if ketu_house == 8:
        present = True
        reasons.append("কেতু নৱম ভাৱত")

    return {
        "present": present,
        "severity": 1 if present else 0,
        "severity_text": DOSHA_INFO["pitra_dosha"]["severity_levels"][1] if present else DOSHA_INFO["pitra_dosha"]["severity_levels"][0],
        "reasons": reasons,
        "info": DOSHA_INFO["pitra_dosha"]
    }


def analyze_grahan_dosha(planet_house_map: dict) -> dict:
    """
    Check Grahan Dosha: Sun or Moon conjunct Rahu/Ketu.
    """
    sun_house = planet_house_map.get("ৰবি")
    moon_house = planet_house_map.get("চন্দ্ৰ")
    rahu_house = planet_house_map.get("ৰাহু")
    ketu_house = planet_house_map.get("কেতু")

    solar_eclipse = False
    lunar_eclipse = False

    if sun_house is not None and (sun_house == rahu_house or sun_house == ketu_house):
        solar_eclipse = True
    if moon_house is not None and (moon_house == rahu_house or moon_house == ketu_house):
        lunar_eclipse = True

    if solar_eclipse and lunar_eclipse:
        severity = 3
        severity_text = DOSHA_INFO["grahan_dosha"]["severity_levels"][3]
    elif solar_eclipse:
        severity = 1
        severity_text = DOSHA_INFO["grahan_dosha"]["severity_levels"][1]
    elif lunar_eclipse:
        severity = 2
        severity_text = DOSHA_INFO["grahan_dosha"]["severity_levels"][2]
    else:
        severity = 0
        severity_text = DOSHA_INFO["grahan_dosha"]["severity_levels"][0]

    return {
        "present": solar_eclipse or lunar_eclipse,
        "severity": severity,
        "severity_text": severity_text,
        "solar_eclipse": solar_eclipse,
        "lunar_eclipse": lunar_eclipse,
        "info": DOSHA_INFO["grahan_dosha"]
    }


def analyze_shani_dosha(planet_house_map: dict, moon_house: int) -> dict:
    """
    Check Shani Dosha / Sade Sati: Saturn's transit relative to Moon.
    moon_house: Moon's house index (0-indexed)
    """
    shani_house = planet_house_map.get("শনি")
    if shani_house is None:
        return {"present": False, "severity": 0, "info": DOSHA_INFO["shani_dosha"]}

    # Sade Sati: Saturn in 12th, 1st, or 2nd from Moon
    relative = (shani_house - moon_house) % 12
    if relative == 11:  # 12th from Moon
        severity = 1
        severity_text = DOSHA_INFO["shani_dosha"]["severity_levels"][1]
        phase = "প্ৰথম চৰণ (উদয়)"
    elif relative == 0:  # 1st from Moon (on Moon)
        severity = 3
        severity_text = DOSHA_INFO["shani_dosha"]["severity_levels"][3]
        phase = "মধ্য চৰণ (শিখৰ)"
    elif relative == 1:  # 2nd from Moon
        severity = 2
        severity_text = DOSHA_INFO["shani_dosha"]["severity_levels"][2]
        phase = "শেষ চৰণ (অস্ত)"
    elif relative == 3:  # Dhaiya: Saturn in 4th from Moon
        severity = 2
        severity_text = DOSHA_INFO["shani_dosha"]["severity_levels"][4]
        phase = "ঢৈয়া (চতুৰ্থ ভাৱ)"
    elif relative == 7:  # Dhaiya: Saturn in 8th from Moon
        severity = 2
        severity_text = DOSHA_INFO["shani_dosha"]["severity_levels"][4]
        phase = "ঢৈয়া (অষ্টম ভাৱ)"
    else:
        return {"present": False, "severity": 0, "info": DOSHA_INFO["shani_dosha"]}

    return {
        "present": True,
        "severity": severity,
        "severity_text": severity_text,
        "phase": phase,
        "info": DOSHA_INFO["shani_dosha"]
    }


def analyze_guru_chandal_dosha(planet_house_map: dict) -> dict:
    """Check Guru-Chandal Dosha: Jupiter conjunct Rahu."""
    guru_house = planet_house_map.get("বৃহস্পতি")
    rahu_house = planet_house_map.get("ৰাহু")

    present = (guru_house is not None and rahu_house is not None and guru_house == rahu_house)

    return {
        "present": present,
        "severity": 1 if present else 0,
        "severity_text": DOSHA_INFO["guru_chandal_dosha"]["severity_levels"][1] if present else DOSHA_INFO["guru_chandal_dosha"]["severity_levels"][0],
        "info": DOSHA_INFO["guru_chandal_dosha"]
    }


def analyze_kemadruma_dosha(planet_house_map: dict) -> dict:
    """
    Check Kemadruma Dosha: No planets in 2nd and 12th from Moon.
    """
    moon_house = planet_house_map.get("চন্দ্ৰ")
    if moon_house is None:
        return {"present": False, "severity": 0, "info": DOSHA_INFO["kemadruma_dosha"]}

    house_2nd = (moon_house + 1) % 12
    house_12th = (moon_house - 1) % 12

    planets_excluding_moon = ["ৰবি", "মংগল", "বুধ", "বৃহস্পতি", "শুক্ৰ", "শনি", "ৰাহু", "কেতু"]

    has_2nd = any(planet_house_map.get(p) == house_2nd for p in planets_excluding_moon)
    has_12th = any(planet_house_map.get(p) == house_12th for p in planets_excluding_moon)

    present = not has_2nd and not has_12th

    return {
        "present": present,
        "severity": 1 if present else 0,
        "severity_text": DOSHA_INFO["kemadruma_dosha"]["severity_levels"][1] if present else DOSHA_INFO["kemadruma_dosha"]["severity_levels"][0],
        "info": DOSHA_INFO["kemadruma_dosha"]
    }


def get_complete_dosha_analysis(planet_house_map: dict, planet_longitudes: dict) -> list:
    """
    Run all dosha analyses and return results.
    """
    moon_house = planet_house_map.get("চন্দ্ৰ", 0)

    results = [
        {"key": "mangal_dosha", **analyze_mangal_dosha(planet_house_map)},
        {"key": "kaal_sarp_dosha", **analyze_kaal_sarp_dosha(planet_house_map, planet_longitudes)},
        {"key": "pitra_dosha", **analyze_pitra_dosha(planet_house_map, planet_longitudes)},
        {"key": "grahan_dosha", **analyze_grahan_dosha(planet_house_map)},
        {"key": "shani_dosha", **analyze_shani_dosha(planet_house_map, moon_house)},
        {"key": "guru_chandal_dosha", **analyze_guru_chandal_dosha(planet_house_map)},
        {"key": "kemadruma_dosha", **analyze_kemadruma_dosha(planet_house_map)},
    ]

    return results
