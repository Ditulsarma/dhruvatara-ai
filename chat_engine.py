

"""
ধ্ৰুৱতৰা AI - চেট ইঞ্জিন (Chat Engine)
============================================================
Uses Ollama API with deepseek-v4-pro:cloud model to answer
astrology-related questions based on the user's kundli data.
"""

import json
import requests
from datetime import datetime

# ─── Ollama API Configuration ───────────────────────────────────
OLLAMA_API_KEY = "7c80477b1eed432db28cc89ff8c7b802.tFh71EvzfaFxZ6Lye2nMK4vp"
OLLAMA_MODEL = "deepseek-v4-pro:cloud"
OLLAMA_URL = "https://api.ollama.com/v1/chat/completions"

# ─── Tīkṣṇa Nakshatras (তীক্ষ্ণ নক্ষত্ৰ) ─────────────────────────
TIKSHNA_NAKSHATRAS = ["আৰ্দ্ৰা", "অশ্লেষা", "জ্যেষ্ঠা", "মূল"]

# ─── Nakshatra Lords (দশা অধিপতি ক্ৰমে) ─────────────────────────
NAKSHATRA_LORDS = [
    "কেতু", "শুক্ৰ", "ৰবি", "চন্দ্ৰ", "মংগল", "ৰাহু",
    "বৃহস্পতি", "শনি", "বুধ"
]

# ─── Natural benefic & malefic planets ──────────────────────────
NATURAL_BENEFICS = ["বৃহস্পতি", "শুক্ৰ", "বুধ", "চন্দ্ৰ"]
NATURAL_MALEFICS = ["ৰবি", "মংগল", "শনি", "ৰাহু", "কেতু"]

# ─── Dusthana houses (দুঃস্থান) ─────────────────────────────────
DUSTHANA_HOUSES = [6, 8, 12]
SHUBH_HOUSES = [1, 2, 4, 5, 7, 9, 10, 11]

# ─── Gochara (Transit) Calculation ─────────────────────────────

def _calculate_gochara(planets_data: list, planet_houses: dict, moon_rasi: str) -> dict:
    """
    Calculate current transit (gochara) positions for Saturn, Rahu, and Jupiter.
    Returns a dict with transit analysis for each key planet.
    
    Saturn transit rules (Sade Sati / Dhaiya):
    - Sade Sati: Saturn transiting 12th, 1st, or 2nd from Moon sign
    - Dhaiya: Saturn transiting 4th or 8th from Moon sign
    - Saturn 7th from Lagna or Moon = Ashtam Shani / Saptam Shani
    
    Jupiter transit rules:
    - Jupiter's aspect on Lagna/Moon can neutralize Saturn's malefic effects
    - Jupiter in 2,5,7,9,11 from Moon = shubh
    - Jupiter in 6,8,12 from Moon = ashubh
    """
    rasi_names = ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা",
                  "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"]
    
    # Find Moon's rasi index
    moon_rasi_idx = rasi_names.index(moon_rasi) if moon_rasi in rasi_names else -1
    
    # Find Lagna rasi index (from planets_data, the ascendant)
    lagna_rasi_idx = -1
    for p in planets_data:
        if p.get("name") == "লগ্ন":
            lagna_rasi = p.get("rasi", "")
            if lagna_rasi in rasi_names:
                lagna_rasi_idx = rasi_names.index(lagna_rasi)
            break
    
    # Get current transit positions of Saturn, Rahu, Jupiter from planets_data
    saturn_house = planet_houses.get("শনি", -1) + 1 if planet_houses.get("শনি", -1) >= 0 else None
    rahu_house = planet_houses.get("ৰাহু", -1) + 1 if planet_houses.get("ৰাহু", -1) >= 0 else None
    jupiter_house = planet_houses.get("বৃহস্পতি", -1) + 1 if planet_houses.get("বৃহস্পতি", -1) >= 0 else None
    
    # Get Saturn's rasi
    saturn_rasi_idx = -1
    for p in planets_data:
        if p.get("name") == "শনি":
            sat_rasi = p.get("rasi", "")
            if sat_rasi in rasi_names:
                saturn_rasi_idx = rasi_names.index(sat_rasi)
            break
    
    # Get Jupiter's rasi
    jupiter_rasi_idx = -1
    for p in planets_data:
        if p.get("name") == "বৃহস্পতি":
            jup_rasi = p.get("rasi", "")
            if jup_rasi in rasi_names:
                jupiter_rasi_idx = rasi_names.index(jup_rasi)
            break
    
    # Get Rahu's rasi
    rahu_rasi_idx = -1
    for p in planets_data:
        if p.get("name") == "ৰাহু":
            rh_rasi = p.get("rasi", "")
            if rh_rasi in rasi_names:
                rahu_rasi_idx = rasi_names.index(rh_rasi)
            break
    
    gochara = {
        "saturn": {"house": saturn_house, "rasi_idx": saturn_rasi_idx},
        "rahu": {"house": rahu_house, "rasi_idx": rahu_rasi_idx},
        "jupiter": {"house": jupiter_house, "rasi_idx": jupiter_rasi_idx},
        "analysis": []
    }
    
    # ─── Saturn Gochara Analysis ───
    if moon_rasi_idx >= 0 and saturn_rasi_idx >= 0:
        # Saturn's position relative to Moon (distance in signs)
        sat_from_moon = (saturn_rasi_idx - moon_rasi_idx) % 12
        
        if sat_from_moon in [12, 0, 1]:  # 12th, 1st, 2nd from Moon
            gochara["saturn"]["sade_sati"] = True
            phase = "প্ৰথম" if sat_from_moon == 12 else ("মধ্য" if sat_from_moon == 0 else "শেষ")
            gochara["analysis"].append(f"শনি গ্ৰহৰ সাৰে সাতি চলি আছে ({phase} পৰ্যায়)। চন্দ্ৰ ৰাশিৰ পৰা {sat_from_moon+1 if sat_from_moon < 12 else 1} নং ঘৰত শনি অৱস্থান কৰিছে। সাৰে সাতি কালত মানসিক অস্থিৰতা, আৰ্থিক টনাটনি, স্বাস্থ্যজনিত সমস্যা, আৰু কৰ্মক্ষেত্ৰত বাধাৰ সম্ভাৱনা থাকে।")
        elif sat_from_moon == 4:
            gochara["saturn"]["dhaiya"] = True
            gochara["analysis"].append("শনি গ্ৰহৰ ধেয়া (Dhaiya) চলি আছে। চন্দ্ৰ ৰাশিৰ পৰা ৪ৰ্থ ঘৰত শনি অৱস্থান কৰিছে। এই সময়ত ঘৰ-পৰিয়াল, মাতৃ, সুখ-শান্তি, আৰু স্থাৱৰ সম্পত্তিৰ ক্ষেত্ৰত বাধাৰ সম্ভাৱনা থাকে।")
        elif sat_from_moon == 8:
            gochara["saturn"]["dhaiya"] = True
            gochara["analysis"].append("শনি গ্ৰহৰ ধেয়া (Dhaiya) চলি আছে। চন্দ্ৰ ৰাশিৰ পৰা ৮ম ঘৰত শনি অৱস্থান কৰিছে। এই সময়ত আয়ুস, গোপন শত্ৰু, আকস্মিক বিপদ, আৰু স্বাস্থ্যজনিত গুৰুতৰ সমস্যাৰ সম্ভাৱনা থাকে।")
        elif sat_from_moon == 7:
            gochara["analysis"].append("শনি গ্ৰহ চন্দ্ৰ ৰাশিৰ পৰা ৭ম ঘৰত অৱস্থান কৰিছে। ই সম্পৰ্ক, বিবাহ, আৰু অংশীদাৰিত্বৰ ক্ষেত্ৰত বাধা-বিঘিনিৰ সৃষ্টি কৰিব পাৰে।")
    
    # Saturn from Lagna
    if lagna_rasi_idx >= 0 and saturn_rasi_idx >= 0:
        sat_from_lagna = (saturn_rasi_idx - lagna_rasi_idx) % 12
        if sat_from_lagna == 7:
            gochara["analysis"].append("শনি গ্ৰহ লগ্নৰ পৰা ৭ম ঘৰত অৱস্থান কৰিছে (সপ্তম শনি)। ই সম্পৰ্ক, বিবাহ, আৰু সহযোগিতাৰ ক্ষেত্ৰত প্ৰত্যাহ্বান সৃষ্টি কৰিব পাৰে।")
        elif sat_from_lagna == 0:
            gochara["analysis"].append("শনি গ্ৰহ লগ্নত অৱস্থান কৰিছে (লগ্নগত শনি)। ই ব্যক্তিগত স্বাস্থ্য, আত্মবিশ্বাস, আৰু নতুন কাম আৰম্ভ কৰাত বাধাৰ সৃষ্টি কৰিব পাৰে।")
    
    # ─── Jupiter Gochara Analysis ───
    if moon_rasi_idx >= 0 and jupiter_rasi_idx >= 0:
        jup_from_moon = (jupiter_rasi_idx - moon_rasi_idx) % 12
        if jup_from_moon in [2, 5, 7, 9, 11]:
            gochara["jupiter"]["shubh"] = True
            gochara["analysis"].append(f"বৃহস্পতি গ্ৰহ চন্দ্ৰ ৰাশিৰ পৰা {jup_from_moon} নং শুভ ঘৰত অৱস্থান কৰিছে। বৃহস্পতিৰ এই শুভ অৱস্থানে শনিৰ অশুভ প্ৰভাৱ বহু পৰিমাণে নিষ্ক্ৰিয় কৰিব। জ্ঞান, ভাগ্য, আৰু ধন লাভৰ সম্ভাৱনা বৃদ্ধি পাব।")
        elif jup_from_moon in [6, 8, 12]:
            gochara["jupiter"]["shubh"] = False
            gochara["analysis"].append(f"বৃহস্পতি গ্ৰহ চন্দ্ৰ ৰাশিৰ পৰা {jup_from_moon} নং দুঃস্থানত অৱস্থান কৰিছে। বৃহস্পতিৰ এই অৱস্থানে শনিৰ অশুভ প্ৰভাৱ আৰু অধিক বৃদ্ধি কৰিব পাৰে। এই সময়ত ধৈৰ্য্য আৰু সাৱধানতা অৱলম্বন কৰা উচিত।")
    
    if lagna_rasi_idx >= 0 and jupiter_rasi_idx >= 0:
        jup_from_lagna = (jupiter_rasi_idx - lagna_rasi_idx) % 12
        if jup_from_lagna in [2, 5, 7, 9, 11]:
            gochara["jupiter"]["lagna_shubh"] = True
        elif jup_from_lagna in [6, 8, 12]:
            gochara["jupiter"]["lagna_shubh"] = False
    
    # ─── Combined Saturn-Jupiter Analysis ───
    if gochara.get("saturn", {}).get("sade_sati") or gochara.get("saturn", {}).get("dhaiya"):
        if gochara.get("jupiter", {}).get("shubh"):
            gochara["analysis"].append("গুৰুত্বপূৰ্ণ: বৃহস্পতি গ্ৰহ বৰ্তমান শুভ অৱস্থানত থকাৰ বাবে শনিৰ সাৰে সাতি/ধেয়াৰ অশুভ প্ৰভাৱ কিছু পৰিমাণে হ্ৰাস পাব। বৃহস্পতিৰ ৰক্ষাকৱচে আপোনাক বেছি ক্ষতিৰ পৰা ৰক্ষা কৰিব। তথাপি সাৱধানতা অৱলম্বন কৰা উচিত।")
        elif gochara.get("jupiter", {}).get("shubh") is False:
            gochara["analysis"].append("সতৰ্কবাণী: বৃহস্পতি গ্ৰহ বৰ্তমান দুঃস্থানত অৱস্থান কৰাৰ বাবে শনিৰ সাৰে সাতি/ধেয়াৰ অশুভ প্ৰভাৱ অধিক তীব্ৰ হ'ব। এই সময়ত অতি সাৱধানতা অৱলম্বন কৰা উচিত। যিকোনো গুৰুত্বপূৰ্ণ সিদ্ধান্ত সাৱধানে ল'ব।")
    
    # ─── Rahu Gochara Analysis ───
    if moon_rasi_idx >= 0 and rahu_rasi_idx >= 0:
        rahu_from_moon = (rahu_rasi_idx - moon_rasi_idx) % 12
        if rahu_from_moon in [1, 2, 4, 5, 7, 8, 9, 12]:
            gochara["analysis"].append(f"ৰাহু গ্ৰহ চন্দ্ৰ ৰাশিৰ পৰা {rahu_from_moon} নং ঘৰত অৱস্থান কৰিছে। ৰাহুৰ এই গোচৰে মানসিক অস্থিৰতা, ভ্ৰম, আৰু অপ্ৰত্যাশিত পৰিঘটনাৰ সম্ভাৱনা বৃদ্ধি কৰে।")
    
    if lagna_rasi_idx >= 0 and rahu_rasi_idx >= 0:
        rahu_from_lagna = (rahu_rasi_idx - lagna_rasi_idx) % 12
        if rahu_from_lagna in [1, 7]:
            gochara["analysis"].append(f"ৰাহু গ্ৰহ লগ্নৰ পৰা {rahu_from_lagna} নং ঘৰত অৱস্থান কৰিছে। ই ব্যক্তিগত জীৱনত গুৰুত্বপূৰ্ণ পৰিৱৰ্তন আৰু উচ্চাকাংক্ষা বৃদ্ধিৰ ইংগিত দিয়ে।")
    
    return gochara

# ─── Predefined Questions ───────────────────────────────────────
PREDEFINED_QUESTIONS = [
    {"id": "marriage", "label": "মোৰ বিবাহ স্থান কেনেকুৱা হ'ব?", "house": 7, "topic": "বিবাহ"},
    {"id": "children", "label": "মোৰ সন্তান স্থান কেনেকুৱা হ'ব?", "house": 5, "topic": "সন্তান"},
    {"id": "career", "label": "মোৰ কৰ্ম স্থান কেনেকুৱা হ'ব?", "house": 10, "topic": "কৰ্ম"},
    {"id": "education", "label": "মোৰ বিদ্যা স্থান কেনেকুৱা হ'ব?", "house": 4, "topic": "বিদ্যা"},
    {"id": "antardasha", "label": "মোৰ অন্তৰ্দশা ফল কেনেকুৱা হ'ব?", "house": None, "topic": "অন্তৰ্দশা"},
    {"id": "finance", "label": "মোৰ ধন স্থান কেনেকুৱা হ'ব?", "house": 2, "topic": "ধন"},
    {"id": "health", "label": "মোৰ স্বাস্থ্য কেনেকুৱা হ'ব?", "house": 1, "topic": "স্বাস্থ্য"},
    {"id": "family", "label": "মোৰ পাৰিবাৰিক জীৱন কেনেকুৱা হ'ব?", "house": 2, "topic": "পৰিয়াল"},
    {"id": "fortune", "label": "মোৰ ভাগ্য কেনেকুৱা হ'ব?", "house": 9, "topic": "ভাগ্য"},
    {"id": "spiritual", "label": "মোৰ আধ্যাত্মিক জীৱন কেনেকুৱা হ'ব?", "house": 12, "topic": "আধ্যাত্মিক"},
]


def _build_kundli_context(planets_data: list, planet_houses: dict, planet_signs: dict,
                          asc_rasi: str, moon_nak_name: str, moon_rasi: str,
                          dosha_results: list, dasa_data: list,
                          lagna_lord: str = "", moon_rashi_lord: str = "") -> str:
    """Build a comprehensive Assamese context string from kundli data for the AI."""

    rasi_names = ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা",
                  "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"]

    nakshatra_names = [
        "অশ্বিনী", "ভৰণী", "কৃত্তিকা", "ৰোহিণী", "মৃগশিৰা", "আৰ্দ্ৰা", "পুনৰ্বসু",
        "পুষ্যা", "অশ্লেষা", "মঘা", "পূৰ্বফাল্গুনী", "উত্তৰফাল্গুনী", "হস্তা",
        "চিত্ৰা", "স্বাতী", "বিশাখা", "অনুৰাধা", "জ্যেষ্ঠা", "মূল", "পূৰ্বাষাঢ়া",
        "উত্তৰাষাঢ়া", "শ্ৰৱণা", "ধনিষ্ঠা", "শতভিষা", "পূৰ্বভাদ্ৰপদ", "উত্তৰভাদ্ৰপদ", "ৰেৱতী"
    ]

    context_parts = []

    # Basic info
    context_parts.append(f"লগ্ন: {asc_rasi}")
    context_parts.append(f"লগ্নৰ অধিপতি: {lagna_lord}")
    context_parts.append(f"জন্ম ৰাশি (চন্দ্ৰ ৰাশি): {moon_rasi}")
    context_parts.append(f"জন্ম ৰাশিৰ অধিপতি: {moon_rashi_lord}")
    context_parts.append(f"চন্দ্ৰৰ নক্ষত্ৰ: {moon_nak_name}")

    # Planet positions with house, sign, nakshatra
    context_parts.append("\nগ্ৰহৰ অৱস্থান:")
    for p in planets_data:
        p_name = p.get("name", "")
        p_rasi = p.get("rasi", "")
        p_nak = p.get("nakshatra", "")
        p_lord = p.get("lord", "")
        house_idx = planet_houses.get(p_name, -1)
        house_num = house_idx + 1 if house_idx >= 0 else "?"
        tikshna_mark = " [তীক্ষ্ণ নক্ষত্ৰ]" if p_nak in TIKSHNA_NAKSHATRAS else ""
        context_parts.append(
            f"  {p_name}: {house_num} নং ঘৰত, {p_rasi} ৰাশিত, {p_nak} নক্ষত্ৰত{tikshna_mark}, নক্ষত্ৰ পতি: {p_lord}"
        )

    # Dosha info
    present_doshas = [d for d in dosha_results if d.get("present")]
    if present_doshas:
        context_parts.append("\nউপস্থিত দোষ:")
        for d in present_doshas:
            info = d.get("info", {})
            d_name = info.get("name", d.get("key", ""))
            d_sev = d.get("severity_text", "")
            context_parts.append(f"  {d_name}: {d_sev}")

    # Mangal dosha check for marriage
    mangal_dosha = next((d for d in dosha_results if d.get("key") == "mangal_dosha" and d.get("present")), None)
    if mangal_dosha:
        context_parts.append("\nমাংগলিক দোষ: উপস্থিত (বিবাহৰ ক্ষেত্ৰত প্ৰভাৱ পেলাব পাৰে)")
    else:
        context_parts.append("\nমাংগলিক দোষ: অনুপস্থিত")

    # Current dasha
    if dasa_data:
        md = dasa_data[0]
        context_parts.append(f"\nবৰ্তমান মহাদশা: {md.get('md_lord', '')} ({md.get('start', '')} ৰ পৰা {md.get('end', '')} লৈ)")
        if md.get("sub_dasas"):
            ad = md["sub_dasas"][0]
            context_parts.append(f"বৰ্তমান অন্তৰ্দশা: {ad.get('ad_lord', '')} ({ad.get('start', '')} ৰ পৰা {ad.get('end', '')} লৈ)")

    return "\n".join(context_parts)


def _get_house_planets(planet_houses: dict, planets_data: list, house_num: int) -> list:
    """Get planets in a specific house (1-12)."""
    house_idx = house_num - 1
    result = []
    for p in planets_data:
        p_name = p.get("name", "")
        if planet_houses.get(p_name) == house_idx:
            result.append(p)
    return result


def _get_house_lord_planet(house_num: int, planet_signs: dict, asc_rasi_idx: int) -> dict:
    """Find which planet is the lord of a given house."""
    rasi_lords = ["মংগল", "শুক্ৰ", "বুধ", "চন্দ্ৰ", "ৰবি", "বুধ",
                  "শুক্ৰ", "মংগল", "বৃহস্পতি", "শনি", "শনি", "বৃহস্পতি"]
    house_rasi_idx = (asc_rasi_idx + house_num - 1) % 12
    lord_name = rasi_lords[house_rasi_idx]
    return {"lord_name": lord_name, "lord_rasi_idx": house_rasi_idx}


def chat_with_ai(user_name: str, question: str, planets_data: list,
                 planet_houses: dict, planet_signs: dict,
                 asc_rasi: str, asc_rasi_idx: int,
                 moon_nak_name: str, moon_rasi: str,
                 dosha_results: list, dasa_data: list,
                 lagna_lord: str = "", moon_rashi_lord: str = "",
                 gender: str = "male") -> str:
    """
    Send a chat question to Ollama AI with full kundli context.
    Returns the AI's response in Assamese.
    """

    # Build kundli context
    kundli_context = _build_kundli_context(
        planets_data, planet_houses, planet_signs,
        asc_rasi, moon_nak_name, moon_rasi,
        dosha_results, dasa_data,
        lagna_lord, moon_rashi_lord
    )

    # ─── Gochara (Transit) Analysis ───
    gochara = _calculate_gochara(planets_data, planet_houses, moon_rasi)
    gochara_context = ""
    if gochara.get("analysis"):
        gochara_context = "\n\n【বৰ্তমান গোচৰ (Transit) বিশ্লেষণ】\n"
        for line in gochara["analysis"]:
            gochara_context += f"  • {line}\n"

    # Determine which predefined question this is
    topic = "সাধাৰণ"
    house_num = None
    for pq in PREDEFINED_QUESTIONS:
        if pq["label"] == question:
            topic = pq["topic"]
            house_num = pq["house"]
            break

    # Build house-specific analysis
    house_analysis = ""
    if house_num is not None:
        house_planets = _get_house_planets(planet_houses, planets_data, house_num)
        house_lord = _get_house_lord_planet(house_num, planet_signs, asc_rasi_idx)
        lord_name = house_lord["lord_name"]

        # Find where the house lord sits
        lord_house = None
        lord_nak = ""
        lord_tikshna = False
        for p in planets_data:
            if p.get("name") == lord_name:
                lord_house = planet_houses.get(lord_name, -1) + 1
                lord_nak = p.get("nakshatra", "")
                lord_tikshna = lord_nak in TIKSHNA_NAKSHATRAS
                break

        house_analysis += f"\n\n{house_num} নং ঘৰৰ ({topic} স্থান) বিশ্লেষণ:"
        if house_planets:
            for hp in house_planets:
                hp_nak = hp.get("nakshatra", "")
                hp_tikshna = " [তীক্ষ্ণ নক্ষত্ৰ]" if hp_nak in TIKSHNA_NAKSHATRAS else ""
                hp_lord = hp.get("lord", "")
                house_analysis += f"\n  এই ঘৰত {hp['name']} গ্ৰহ অৱস্থান কৰিছে, {hp['rasi']} ৰাশিত, {hp_nak} নক্ষত্ৰত{hp_tikshna}।"
                # Nakshatra lord position analysis
                if hp_lord:
                    lord_house_num = planet_houses.get(hp_lord, -1) + 1 if planet_houses.get(hp_lord, -1) >= 0 else None
                    if lord_house_num is not None:
                        lord_is_benefic = hp_lord in NATURAL_BENEFICS
                        lord_in_dusthana = lord_house_num in DUSTHANA_HOUSES
                        lord_in_shubh = lord_house_num in SHUBH_HOUSES
                        if lord_is_benefic and lord_in_shubh:
                            house_analysis += f" {hp['name']}ৰ নক্ষত্ৰ অধিপতি {hp_lord} এজন শুভ গ্ৰহ আৰু {lord_house_num} নং শুভ ঘৰত অৱস্থান কৰিছে — ই {topic} স্থানৰ বাবে অতি শুভ।"
                        elif lord_is_benefic and lord_in_dusthana:
                            house_analysis += f" {hp['name']}ৰ নক্ষত্ৰ অধিপতি {hp_lord} শুভ গ্ৰহ হ'লেও {lord_house_num} নং দুঃস্থানত অৱস্থান কৰিছে — ই {topic} স্থানত কিছু বাধাৰ সৃষ্টি কৰিব পাৰে।"
                        elif not lord_is_benefic and lord_in_shubh:
                            house_analysis += f" {hp['name']}ৰ নক্ষত্ৰ অধিপতি {hp_lord} অশুভ গ্ৰহ কিন্তু {lord_house_num} নং শুভ ঘৰত অৱস্থান কৰিছে — ই {topic} স্থানত মিশ্ৰিত ফল দিব।"
                        elif not lord_is_benefic and lord_in_dusthana:
                            house_analysis += f" {hp['name']}ৰ নক্ষত্ৰ অধিপতি {hp_lord} অশুভ গ্ৰহ আৰু {lord_house_num} নং দুঃস্থানত অৱস্থান কৰিছে — ই {topic} স্থানৰ বাবে অতি অশুভ, গুৰুতৰ সমস্যাৰ সংকেত।"
        else:
            house_analysis += f"\n  এই ঘৰত কোনো গ্ৰহ অৱস্থান কৰা নাই।"

        house_analysis += f"\n  এই ঘৰৰ অধিপতি: {lord_name}"
        if lord_house:
            house_analysis += f", যি {lord_house} নং ঘৰত অৱস্থান কৰিছে, {lord_nak} নক্ষত্ৰত।"
            if lord_tikshna:
                house_analysis += f" {lord_name} তীক্ষ্ণ নক্ষত্ৰ ({lord_nak})ত অৱস্থান কৰি অশুভ ফল প্ৰদান কৰিব পাৰে।"
            # House lord's nakshatra lord analysis
            lord_nak_lord = None
            for p in planets_data:
                if p.get("name") == lord_name:
                    lord_nak_lord = p.get("lord", "")
                    break
            if lord_nak_lord:
                lord_nl_house = planet_houses.get(lord_nak_lord, -1) + 1 if planet_houses.get(lord_nak_lord, -1) >= 0 else None
                if lord_nl_house is not None:
                    lord_nl_benefic = lord_nak_lord in NATURAL_BENEFICS
                    lord_nl_dusthana = lord_nl_house in DUSTHANA_HOUSES
                    if lord_nl_benefic and not lord_nl_dusthana:
                        house_analysis += f" {lord_name}ৰ নক্ষত্ৰ অধিপতি {lord_nak_lord} শুভ গ্ৰহ আৰু {lord_nl_house} নং ঘৰত অৱস্থান কৰি {topic} স্থানক সুদৃঢ় কৰিছে।"
                    elif not lord_nl_benefic and lord_nl_dusthana:
                        house_analysis += f" {lord_name}ৰ নক্ষত্ৰ অধিপতি {lord_nak_lord} অশুভ গ্ৰহ আৰু {lord_nl_house} নং দুঃস্থানত অৱস্থান কৰি {topic} স্থানত গুৰুতৰ বাধাৰ সৃষ্টি কৰিব পাৰে।"

    # Build the system prompt
    gender_text = "জাতিকা (মহিলা)" if gender == "female" else "জাতক (পুৰুষ)"
    system_prompt = f"""তুমি এজন অভিজ্ঞ বৈদিক জ্যোতিষী পণ্ডিত। তুমি অসমীয়া ভাষাত উত্তৰ দিবা।

গুৰুত্বপূৰ্ণ নিৰ্দেশনা:
- তুমি নিজেই এজন বিশেষজ্ঞ জ্যোতিষী। তুমি কেতিয়াও গ্ৰাহকক "আন এজন জ্যোতিষীৰ পৰামৰ্শ লওক" বুলি নকবা। তুমি নিজেই সম্পূৰ্ণ বিশ্লেষণ আৰু পৰামৰ্শ দিবা।
- তুমি এজন গ্ৰাহকৰ জন্মকুণ্ডলীৰ ভিত্তিত তেওঁৰ প্ৰশ্নৰ উত্তৰ দিবা।
- তুমি কেৱল জ্যোতিষশাস্ত্ৰৰ সম্ভাৱনা, কাৰণ, সমস্যা, আৰু চূড়ান্ত ফলাফলৰ ওপৰত গুৰুত্ব দিবা।
- কোনো ধৰণৰ সাধাৰণ অস্বীকাৰ (generic disclaimer), অলাগতিয়াল পাতনি, বা অদৰকাৰী তথ্য লিখিব নালাগে।
- পোনপটীয়াকৈ বিশ্লেষণলৈ আহিবা।

জ্যোতিষীয় বিশ্লেষণৰ গুৰুত্বপূৰ্ণ সূত্ৰ (এই সূত্ৰসমূহ ব্যৱহাৰ কৰি বিশ্লেষণ কৰিবা):
1. নক্ষত্ৰ অধিপতি সূত্ৰ: কোনো গ্ৰহৰ নক্ষত্ৰৰ অধিপতি যদি শুভ গ্ৰহ হয় আৰু শুভ ঘৰত (1,2,4,5,7,9,10,11) অৱস্থান কৰে, তেন্তে সেই গ্ৰহই শুভ ফল দিব — গ্ৰহটো নিজে অশুভ হ'লেও। বিপৰীতে, নক্ষত্ৰ অধিপতি অশুভ গ্ৰহ হৈ দুঃস্থানত (6,8,12) থাকিলে অতি অশুভ ফল দিব।
2. ঘৰৰ অধিপতি সূত্ৰ: ঘৰৰ অধিপতি গ্ৰহ যি ঘৰত অৱস্থান কৰে, সেই ঘৰৰ বিষয়সমূহৰ ওপৰত প্ৰভাৱ পৰে। যেনে: 7ম ঘৰৰ অধিপতি 8ম ঘৰত থাকিলে বিবাহিত জীৱনত বাধা, মতানৈক্য, বা জীৱনসংগীৰ স্বাস্থ্যজনিত সমস্যা হ'ব পাৰে।
3. মাংগলিক দোষ সূত্ৰ: মংগল 1,2,4,7,8,12 ঘৰত থাকিলে মাংগলিক দোষ হয় — বিবাহত বিলম্ব, মতানৈক্য, বা বিচ্ছেদৰ সম্ভাৱনা থাকে।
4. তীক্ষ্ণ নক্ষত্ৰ সূত্ৰ: কোনো গ্ৰহ আৰ্দ্ৰা, অশ্লেষা, জ্যেষ্ঠা, বা মূল নক্ষত্ৰত থাকিলে তাৰ ফল অশুভ হয় — বিশেষকৈ সম্পৰ্ক আৰু স্বাস্থ্যৰ ক্ষেত্ৰত।
5. দশা সূত্ৰ: বৰ্তমানৰ মহাদশা আৰু অন্তৰ্দশাৰ গ্ৰহসমূহৰ অৱস্থান অনুসৰি ফলাফলৰ তীব্ৰতা নিৰ্ণয় কৰা হয়। দশাৰ গ্ৰহ যদি প্ৰশ্নৰ ঘৰৰ সৈতে সম্বন্ধযুক্ত, তেন্তে সেই সময়ত বিশেষ প্ৰভাৱ পৰে।
6. শনি-মংগল যুতি সূত্ৰ: শনি আৰু মংগল একেলগে কোনো ঘৰত থাকিলে (বিশেষকৈ 7ম ঘৰত) বিবাহিত জীৱনত গুৰুতৰ সমস্যা, দাম্পত্য কলহ, বা দীৰ্ঘম্যাদী বিচ্ছেদৰ সম্ভাৱনা থাকে।
7. গোচৰ (Transit) সূত্ৰ — শনিৰ সাৰে সাতি/ধেয়া: শনি গ্ৰহ চন্দ্ৰ ৰাশিৰ পৰা ১২, ১, ২ ঘৰত থাকিলে সাৰে সাতি (সাড়ে সাতি) হয় — মানসিক অস্থিৰতা, আৰ্থিক টনাটনি, স্বাস্থ্যজনিত সমস্যা হয়। ৪ৰ্থ বা ৮ম ঘৰত থাকিলে ধেয়া (Dhaiya) হয়। লগ্নৰ পৰা ৭ম ঘৰত থাকিলে সপ্তম শনি হয়।
8. গোচৰ সূত্ৰ — বৃহস্পতিৰ ৰক্ষাকৱচ: বৃহস্পতি গ্ৰহ চন্দ্ৰ ৰাশিৰ পৰা ২,৫,৭,৯,১১ ঘৰত থাকিলে শুভ হয় আৰু শনিৰ অশুভ প্ৰভাৱ বহু পৰিমাণে নিষ্ক্ৰিয় কৰে। কিন্তু বৃহস্পতি ৬,৮,১২ ঘৰত থাকিলে অশুভ হয় আৰু শনিৰ অশুভ প্ৰভাৱ অধিক তীব্ৰ কৰে।
9. গোচৰ সূত্ৰ — ৰাহু: ৰাহু গ্ৰহ চন্দ্ৰ ৰাশিৰ পৰা ১,২,৪,৫,৭,৮,৯,১২ ঘৰত থাকিলে মানসিক অস্থিৰতা, ভ্ৰম, অপ্ৰত্যাশিত পৰিঘটনা বৃদ্ধি কৰে। লগ্নৰ পৰা ১,৭ ঘৰত থাকিলে জীৱনত গুৰুত্বপূৰ্ণ পৰিৱৰ্তন আনে।

- যদি কোনো নেতিবাচক গ্ৰহ প্ৰভাৱ বা দোষ থাকে, তেন্তে নিৰ্দিষ্ট, ব্যৱহাৰিক বৈদিক জ্যোতিষীয় প্ৰতিকাৰ (যেনে: মন্ত্ৰ, ৰত্ন, দান, ব্ৰত) অসমীয়া ভাষাত উল্লেখ কৰিবা।
- উত্তৰ বিতংভাৱে, পেৰেগ্ৰাফ আকাৰত, আৰু শুদ্ধ অসমীয়া ভাষাত দিবা।
- তুমি কেতিয়াও চিকিৎসা, আইনী, বা বিত্তীয় পৰামৰ্শ নিদিবা — কেৱল জ্যোতিষীয় বিশ্লেষণ দিবা।"""

    user_prompt = f"""তলত এজন গ্ৰাহকৰ জন্মকুণ্ডলীৰ সম্পূৰ্ণ তথ্য দিয়া হৈছে:

গ্ৰাহকৰ নাম: {user_name}, লিংগ: {gender_text}

{kundli_context}
{gochara_context}
{house_analysis}

গ্ৰাহকে সুধিছে: "{question}"

ওপৰৰ কুণ্ডলীৰ তথ্যৰ ভিত্তিত, দয়া কৰি বিতংভাৱে উত্তৰ দিয়া। উত্তৰত তলৰ বিষয়সমূহ অন্তৰ্ভুক্ত কৰিবা:

1. প্ৰশ্নৰ বিষয়ৰ সৈতে জড়িত গ্ৰহসমূহৰ অৱস্থান আৰু তাৰ শুভ/অশুভ প্ৰভাৱ
2. কোনো দোষ বা অশুভ গ্ৰহ প্ৰভাৱ থাকিলে তাৰ বিৱৰণ আৰু কাৰণ
3. বৰ্তমান চলি থকা মহাদশা/অন্তৰ্দশাৰ প্ৰভাৱ
4. বৰ্তমানৰ গোচৰ (Transit) — বিশেষকৈ শনি, ৰাহু, আৰু বৃহস্পতিৰ গোচৰৰ প্ৰভাৱ
5. চূড়ান্ত ফলাফল — কি আশা কৰিব পাৰি
6. যদি কোনো নেতিবাচক প্ৰভাৱ থাকে, তেন্তে নিৰ্দিষ্ট বৈদিক প্ৰতিকাৰ (মন্ত্ৰ, ৰত্ন, দান, ব্ৰত) অসমীয়া ভাষাত দিবা

মনত ৰাখিবা: কোনো পাতনি বা অস্বীকাৰ নালাগে। পোনপটীয়াকৈ বিশ্লেষণ দিয়া।"""

    # Call Ollama API
    try:
        headers = {
            "Authorization": f"Bearer {OLLAMA_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        response = requests.post(OLLAMA_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return _fallback_response(question, planets_data, planet_houses, planet_signs,
                                      asc_rasi_idx, dosha_results, dasa_data, moon_nak_name)

    except Exception as e:
        print(f"Ollama API error: {e}")
        return _fallback_response(question, planets_data, planet_houses, planet_signs,
                                  asc_rasi_idx, dosha_results, dasa_data, moon_nak_name)


def _fallback_response(question: str, planets_data: list, planet_houses: dict,
                       planet_signs: dict, asc_rasi_idx: int,
                       dosha_results: list, dasa_data: list,
                       moon_nak_name: str) -> str:
    """Generate a fallback response when the AI API is unavailable."""

    rasi_names = ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা",
                  "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"]

    # Determine topic from question
    topic = "সাধাৰণ"
    house_num = None
    for pq in PREDEFINED_QUESTIONS:
        if pq["label"] == question:
            topic = pq["topic"]
            house_num = pq["house"]
            break

    response_parts = [f"【{topic} স্থানৰ জ্যোতিষীয় বিশ্লেষণ】\n"]

    house_planet_names = []

    if house_num is not None:
        house_planets = _get_house_planets(planet_houses, planets_data, house_num)
        house_planet_names = [p.get("name") for p in house_planets] if house_planets else []
        
        house_lord = _get_house_lord_planet(house_num, planet_signs, asc_rasi_idx)
        lord_name = house_lord["lord_name"]

        # Find where the house lord sits
        lord_house = None
        lord_nak = ""
        lord_tikshna = False
        lord_nak_lord = ""
        for p in planets_data:
            if p.get("name") == lord_name:
                lord_house = planet_houses.get(lord_name, -1) + 1
                lord_nak = p.get("nakshatra", "")
                lord_tikshna = lord_nak in TIKSHNA_NAKSHATRAS
                lord_nak_lord = p.get("lord", "")
                break

        response_parts.append(f"আপোনাৰ কুণ্ডলীৰ {house_num} নং ঘৰটো {topic} স্থান।")

        if house_planets:
            planet_names_str = ", ".join(house_planet_names)
            response_parts.append(f"এই ঘৰত {planet_names_str} গ্ৰহ অৱস্থান কৰিছে।")
            for hp in house_planets:
                hp_nak = hp.get("nakshatra", "")
                hp_lord = hp.get("lord", "")
                if hp_nak in TIKSHNA_NAKSHATRAS:
                    response_parts.append(f"{hp['name']} গ্ৰহ {hp_nak} তীক্ষ্ণ নক্ষত্ৰত অৱস্থান কৰি অশুভ প্ৰভাৱ দিব পাৰে।")
                # Nakshatra lord analysis
                if hp_lord:
                    nl_house = planet_houses.get(hp_lord, -1) + 1 if planet_houses.get(hp_lord, -1) >= 0 else None
                    if nl_house is not None:
                        nl_benefic = hp_lord in NATURAL_BENEFICS
                        nl_dusthana = nl_house in DUSTHANA_HOUSES
                        if nl_benefic and not nl_dusthana:
                            response_parts.append(f"{hp['name']}ৰ নক্ষত্ৰ অধিপতি {hp_lord} শুভ গ্ৰহ আৰু {nl_house} নং শুভ ঘৰত অৱস্থান কৰিছে — ই {topic} স্থানৰ বাবে শুভ সংকেত।")
                        elif nl_benefic and nl_dusthana:
                            response_parts.append(f"{hp['name']}ৰ নক্ষত্ৰ অধিপতি {hp_lord} শুভ গ্ৰহ হ'লেও {nl_house} নং দুঃস্থানত অৱস্থান কৰিছে — ই {topic} স্থানত কিছু বাধাৰ সৃষ্টি কৰিব পাৰে।")
                        elif not nl_benefic and not nl_dusthana:
                            response_parts.append(f"{hp['name']}ৰ নক্ষত্ৰ অধিপতি {hp_lord} অশুভ গ্ৰহ কিন্তু {nl_house} নং শুভ ঘৰত অৱস্থান কৰিছে — ই {topic} স্থানত মিশ্ৰিত ফল দিব।")
                        elif not nl_benefic and nl_dusthana:
                            response_parts.append(f"{hp['name']}ৰ নক্ষত্ৰ অধিপতি {hp_lord} অশুভ গ্ৰহ আৰু {nl_house} নং দুঃস্থানত অৱস্থান কৰিছে — ই {topic} স্থানৰ বাবে অতি অশুভ, গুৰুতৰ সমস্যাৰ সংকেত।")
        else:
            response_parts.append(f"এই ঘৰত কোনো গ্ৰহ অৱস্থান কৰা নাই।")

        response_parts.append(f"এই ঘৰৰ অধিপতি হৈছে {lord_name} গ্ৰহ।")
        if lord_house:
            response_parts.append(f"{lord_name} গ্ৰহ আপোনাৰ কুণ্ডলীৰ {lord_house} নং ঘৰত অৱস্থান কৰিছে।")
            if lord_tikshna:
                response_parts.append(f"{lord_name} গ্ৰহ {lord_nak} তীক্ষ্ণ নক্ষত্ৰত অৱস্থান কৰাৰ বাবে {topic} স্থানত বাধা-বিঘিনি আহিব পাৰে।")
            # House lord's nakshatra lord analysis
            if lord_nak_lord:
                lnl_house = planet_houses.get(lord_nak_lord, -1) + 1 if planet_houses.get(lord_nak_lord, -1) >= 0 else None
                if lnl_house is not None:
                    lnl_benefic = lord_nak_lord in NATURAL_BENEFICS
                    lnl_dusthana = lnl_house in DUSTHANA_HOUSES
                    if lnl_benefic and not lnl_dusthana:
                        response_parts.append(f"{lord_name}ৰ নক্ষত্ৰ অধিপতি {lord_nak_lord} শুভ গ্ৰহ আৰু {lnl_house} নং ঘৰত অৱস্থান কৰি {topic} স্থানক সুদৃঢ় কৰিছে।")
                    elif not lnl_benefic and lnl_dusthana:
                        response_parts.append(f"{lord_name}ৰ নক্ষত্ৰ অধিপতি {lord_nak_lord} অশুভ গ্ৰহ আৰু {lnl_house} নং দুঃস্থানত অৱস্থান কৰি {topic} স্থানত গুৰুতৰ বাধাৰ সৃষ্টি কৰিব পাৰে।")

    # ─── Advanced Rule-based predictions ───
    
    # 1. Marriage-specific rules
    if topic == "বিবাহ":
        mangal = next((d for d in dosha_results if d.get("key") == "mangal_dosha" and d.get("present")), None)
        if mangal:
            response_parts.append("\nআপোনাৰ কুণ্ডলীত মাংগলিক দোষ উপস্থিত। ই বিবাহৰ ক্ষেত্ৰত বিলম্ব বা মতানৈক্যৰ সৃষ্টি কৰিব পাৰে। মাংগলিক দোষ নিবাৰণৰ বাবে হনুমান চালিচা পাঠ, মঙ্গলবাৰৰ ব্ৰত, আৰু ৰক্ত প্ৰবাল ৰত্ন ধাৰণ কৰিব পাৰে।")
        else:
            response_parts.append("\nআপোনাৰ কুণ্ডলীত মাংগলিক দোষ অনুপস্থিত, যি বিবাহৰ বাবে শুভ।")

        if lord_house == 8:
            response_parts.append(f"সূত্ৰ: ৭ম ঘৰৰ অধিপতি {lord_name} ৮ম ঘৰত অৱস্থান কৰিছে। ই বিবাহিত জীৱনত মতানৈক্য, জীৱনসংগীৰ স্বাস্থ্যজনিত সমস্যা, বা কৰ্মসূত্ৰে দূৰৈত থকাৰ সম্ভাৱনা সৃষ্টি কৰে।")
        if lord_house == 6:
            response_parts.append(f"সূত্ৰ: ৭ম ঘৰৰ অধিপতি {lord_name} ৬ষ্ঠ ঘৰত অৱস্থান কৰিছে। ই বিবাহিত জীৱনত কলহ, স্বাস্থ্যজনিত সমস্যা, বা আইনী জটিলতাৰ সম্ভাৱনা সৃষ্টি কৰিব পাৰে নাইবা বিবাহত উচ্চ শ্ৰেণী নাইবা নিম্ন শ্ৰেণীৰ কথা আহি পৰিব পাৰে।")
        if lord_house == 12:
            response_parts.append(f"সূত্ৰ: ৭ম ঘৰৰ অধিপতি {lord_name} ১২শ ঘৰত অৱস্থান কৰিছে। ই বিবাহিত জীৱনত কৰ্মসুত্ৰে নাইবা অন্য ক্ষেত্ৰক লৈ দূৰত্ব আনিব পাৰে, বিচ্ছেদ, বা বিদেশ যাত্ৰাৰ সম্ভাৱনা সৃষ্টি কৰে।")

        if lord_house in [1, 4, 5, 7, 9, 10]:
            response_parts.append(f"সূত্ৰ: ৭ম ঘৰৰ অধিপতি {lord_name} কেন্দ্ৰ বা ত্ৰিকোণত অৱস্থান কৰিছে। ই অতি শুভ যোগ। ই এক সুস্থিৰ, সুখী আৰু সমৰ্থনকাৰী জীৱনসংগী লাভৰ ইংগিত দিয়ে।")

        if "শনি" in house_planet_names and "মংগল" in house_planet_names:
            response_parts.append("সূত্ৰ: ৭ম ঘৰত শনি-মংগলৰ যুতি অতি অশুভ। ই দাম্পত্য কলহ, দীৰ্ঘম্যাদী বিচ্ছেদ, বা বিবাহ বিচ্ছেদৰ সম্ভাৱনা সৃষ্টি কৰে।")
            
        if "শুক্ৰ" in house_planet_names and ("ৰাহু" in house_planet_names or "কেতু" in house_planet_names):
            response_parts.append("সূত্ৰ: বিবাহ স্থানত শুক্ৰ আৰু ৰাহু/কেতুৰ প্ৰভাৱে দাম্পত্য জীৱনত ভুল বুজাবুজি বা মোহভংগৰ সৃষ্টি কৰিব পাৰে। পাৰস্পৰিক বিশ্বাস বজাই ৰখাটো অতি প্ৰয়োজন।")

    # 2. Career-specific rules
    if topic == "কৰ্ম":
        if lord_house == 6:
            response_parts.append(f"সূত্ৰ: ১০ম ঘৰৰ অধিপতি {lord_name} ৬ষ্ঠ ঘৰত অৱস্থান কৰিছে। ই কৰ্মক্ষেত্ৰত প্ৰতিযোগিতা, স্বাস্থ্যজনিত বাধা, বা চাকৰিৰ ক্ষেত্ৰত বিলম্ব হলেও পিছলৈকে শুভ সংবাদ দিব পাৰে।")
        if lord_house == 8:
            response_parts.append(f"সূত্ৰ: ১০ম ঘৰৰ অধিপতি {lord_name} ৮ম ঘৰত অৱস্থান কৰিছে। ই কৰ্মক্ষেত্ৰত আকস্মিক পৰিৱৰ্তন, গোপন শত্ৰু, বা আৰ্থিক অনিশ্চয়তাৰ সম্ভাৱনা সৃষ্টি কৰে।")
        if lord_house == 12:
            response_parts.append(f"সূত্ৰ: ১০ম ঘৰৰ অধিপতি {lord_name} ১২শ ঘৰত অৱস্থান কৰিছে। ই বিদেশত কৰ্ম, আধ্যাত্মিক ক্ষেত্ৰত কৰ্ম, বা কৰ্মক্ষেত্ৰত দূৰত্বৰ সম্ভাৱনা সৃষ্টি কৰে।")

        if lord_house == 9:
            response_parts.append(f"সূত্ৰ: ১০ম ঘৰৰ অধিপতি {lord_name} ৯ম ঘৰত (ভাগ্য স্থান) অৱস্থান কৰাটো এটি শক্তিশালী ৰাজযোগ। ই কৰ্মক্ষেত্ৰত অপাৰ সফলতা, সন্মান আৰু ভাগ্যৰ পূৰ্ণ সমৰ্থন কঢ়িয়াই আনে।")
            
        if "সূৰ্য" in house_planet_names and lord_house == 10:
            response_parts.append("সূত্ৰ: কৰ্মস্থানত (১০ম ঘৰত) সূৰ্যৰ অৱস্থানে প্ৰবল নেতৃত্বৰ ক্ষমতা দিয়ে। ই চৰকাৰী চাকৰি, ৰাজনীতি, প্ৰশাসন বা সমাজত উচ্চ পদবী লাভৰ সুন্দৰ সম্ভাৱনা সৃষ্টি কৰে।")

    # 3. Children-specific rules
    if topic == "সন্তান":
        if lord_house == 6:
            response_parts.append(f"সূত্ৰ: ৫ম ঘৰৰ অধিপতি {lord_name} ৬ষ্ঠ ঘৰত অৱস্থান কৰিছে। ই সন্তান লাভত বিলম্ব বা স্বাস্থ্যজনিত সমস্যাৰ সম্ভাৱনা সৃষ্টি কৰে।")
        if lord_house == 8:
            response_parts.append(f"সূত্ৰ: ৫ম ঘৰৰ অধিপতি {lord_name} ৮ম ঘৰত অৱস্থান কৰিছে। ই সন্তান লাভত গুৰুতৰ বাধা বা অনিশ্চয়তাৰ সম্ভাৱনা সৃষ্টি কৰে।")

    # 4. Health-specific rules
    if topic == "স্বাস্থ্য":
        if lord_house == 6:
            response_parts.append(f"সূত্ৰ: লগ্নৰ অধিপতি {lord_name} ৬ষ্ঠ ঘৰত অৱস্থান কৰিছে। ই স্বাস্থ্যৰ ক্ষেত্ৰত ৰোগ প্ৰতিৰোধ ক্ষমতা কমি যোৱাৰ সম্ভাৱনা সৃষ্টি কৰে।")
        if lord_house == 8:
            response_parts.append(f"সূত্ৰ: লগ্নৰ অধিপতি {lord_name} ৮ম ঘৰত অৱস্থান কৰিছে। ই দীৰ্ঘম্যাদী ৰোগ বা আকস্মিক স্বাস্থ্যজনিত সমস্যাৰ সম্ভাৱনা সৃষ্টি কৰে।")
            
        if lord_house in [1, 4, 5, 7, 9, 10]:
            response_parts.append(f"সূত্ৰ: লগ্নৰ অধিপতি {lord_name} কেন্দ্ৰ বা ত্ৰিকোণত থকাৰ বাবে আপোনাৰ শাৰীৰিক গঠন মজবুত আৰু ৰোগ প্ৰতিৰোধ ক্ষমতা শক্তিশালী হ'ব।")

    # 5. Finance-specific rules
    if topic == "ধন":
        if lord_house == 6:
            response_parts.append(f"সূত্ৰ: ২য় ঘৰৰ অধিপতি {lord_name} ৬ষ্ঠ ঘৰত অৱস্থান কৰিছে। ই আৰ্থিক ক্ষেত্ৰত ঋণ, খৰচ বৃদ্ধি, বা অনিশ্চয়তাৰ সম্ভাৱনা সৃষ্টি কৰে।")
        if lord_house == 8:
            response_parts.append(f"সূত্ৰ: ২য় ঘৰৰ অধিপতি {lord_name} ৮ম ঘৰত অৱস্থান কৰিছে। ই আৰ্থিক ক্ষেত্ৰত আকস্মিক লোকচান বা গোপন ব্যয়ৰ সম্ভাৱনা সৃষ্টি কৰে।")
        if lord_house == 12:
            response_parts.append(f"সূত্ৰ: ২য় ঘৰৰ অধিপতি {lord_name} ১২শ ঘৰত অৱস্থান কৰিছে। ই অযথা ব্যয়, বিদেশত বিনিয়োগ, বা আৰ্থিক ক্ষতিৰ সম্ভাৱনা সৃষ্টি কৰে।")
            
        if lord_house == 11:
            response_parts.append(f"সূত্ৰ: ২য় ঘৰৰ অধিপতি {lord_name} ১১শ ঘৰত (লাভ) অৱস্থান কৰিছে। এইটো এটা অতি শক্তিশালী 'ধন যোগ', যিয়ে প্ৰচুৰ আৰ্থিক লাভ, ব্যৱসায়ত উন্নতি আৰু স্থায়ী সঞ্চয়ৰ ইংগিত দিয়ে।")
            
        if lord_house in [1, 4, 5, 7, 9, 10]:
            response_parts.append(f"সূত্ৰ: ধন স্থানৰ অধিপতি {lord_name} শুভ স্থানত থকাৰ বাবে আপোনাৰ আৰ্থিক অৱস্থা সাধাৰণতে সচ্ছল হ'ব আৰু নিজৰ প্ৰচেষ্টাত ধন উপাৰ্জন কৰিবলৈ সক্ষম হ'ব।")

    # 6. Education-specific rules
    if topic == "বিদ্যা":
        if lord_house == 6:
            response_parts.append(f"সূত্ৰ: বিদ্যাস্থানৰ অধিপতি {lord_name} ৬ষ্ঠ ঘৰত অৱস্থান কৰিছে। ই শিক্ষাৰ ক্ষেত্ৰত বাধা, প্ৰতিযোগিতা, বা স্বাস্থ্যজনিত সমস্যাৰ সম্ভাৱনা সৃষ্টি কৰে।")
        if lord_house == 12:
            response_parts.append(f"সূত্ৰ: বিদ্যাস্থানৰ অধিপতি {lord_name} ১২শ ঘৰত অৱস্থান কৰিছে। ই বিদেশত শিক্ষা বা শিক্ষাৰ ক্ষেত্ৰত দূৰত্বৰ সম্ভাৱনা সৃষ্টি কৰে।")
            
        if lord_house in [1, 4, 5, 9, 10]:
            response_parts.append(f"সূত্ৰ: বিদ্যা আৰু বুদ্ধিৰ অধিপতি {lord_name} শুভ স্থানত আছে। ই উচ্চ শিক্ষা, তীক্ষ্ণ মেধা আৰু প্ৰতিযোগিতামূলক পৰীক্ষাত সফলতাৰ যোগ বনাইছে।")
            
        if "বুধ" in house_planet_names and "বৃহস্পতি" in house_planet_names:
            response_parts.append("সূত্ৰ: বিদ্যাস্থানত বুধ (বুদ্ধি) আৰু বৃহস্পতিৰ (জ্ঞান) প্ৰভাৱে জাতকক অত্যন্ত জ্ঞানী, যুক্তিবাদী আৰু শিক্ষাক্ষেত্ৰত পাৰ্গত কৰি তোলে।")

    # Current dasha
    if dasa_data:
        md = dasa_data[0]
        response_parts.append(f"\nবৰ্তমান আপুনি {md.get('md_lord', '')} মহাদশা অতিক্ৰম কৰি আছে।")
        if md.get("sub_dasas"):
            ad = md["sub_dasas"][0]
            response_parts.append(f"আৰু {ad.get('ad_lord', '')} অন্তৰ্দশা চলি আছে। এই দশাৰ প্ৰভাৱেও {topic} স্থানত পৰিব।")

    # ─── Gochara (Transit) Analysis ───
    # Extract moon_rasi from planets_data for gochara calculation
    moon_rasi_fb = ""
    for p in planets_data:
        if p.get("name") == "চন্দ্ৰ":
            moon_rasi_fb = p.get("rasi", "")
            break
    if moon_rasi_fb:
        gochara = _calculate_gochara(planets_data, planet_houses, moon_rasi_fb)
        if gochara.get("analysis"):
            response_parts.append(f"\n【বৰ্তমান গোচৰ (Transit) বিশ্লেষণ】")
            for line in gochara["analysis"]:
                response_parts.append(f"• {line}")

    # Brief analysis summary
    response_parts.append(f"\n【সাৰাংশ】")
    response_parts.append(f"ওপৰোক্ত বিশ্লেষণ অনুসৰি, আপোনাৰ '{topic}' স্থানৰ গ্ৰহ অৱস্থান আৰু বৰ্তমানৰ দশাৰ প্ৰভাৱ বিবেচনা কৰি ক'ব পাৰি যে এই বিষয়ত আপুনি ধৈৰ্য্য আৰু সচেতনতা অৱলম্বন কৰা উচিত। শুভ গ্ৰহৰ প্ৰভাৱ থাকিলে সফলতা লাভ কৰিব, আৰু অশুভ প্ৰভাৱ থাকিলে উপযুক্ত প্ৰতিকাৰ গ্ৰহণ কৰিলে পৰিস্থিতিৰ উন্নতি হ'ব।")

    return "\n".join(response_parts)

