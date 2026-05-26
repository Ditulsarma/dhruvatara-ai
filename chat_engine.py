"""
ধ্ৰুৱতৰা AI - চেট ইঞ্জিন (Chat Engine)
============================================================
Uses Ollama API with deepseek-v4-pro:cloud model to answer
astrology-related questions based on the user's kundli data.
"""

import json
import requests

# ─── Ollama API Configuration ───────────────────────────────────
OLLAMA_API_KEY = "7c80477b1eed432db28cc89ff8c7b802.tFh71EvzfaFxZ6Lye2nMK4vp"
OLLAMA_MODEL = "deepseek-v4-pro:cloud"
OLLAMA_URL = "https://api.ollama.com/v1/chat/completions"

# ─── Tīkṣṇa Nakshatras (তীক্ষ্ণ নক্ষত্ৰ) ─────────────────────────
TIKSHNA_NAKSHATRAS = ["আৰ্দ্ৰা", "অশ্লেষা", "জ্যেষ্ঠা", "মূল"]

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
                house_analysis += f"\n  এই ঘৰত {hp['name']} গ্ৰহ অৱস্থান কৰিছে, {hp['rasi']} ৰাশিত, {hp_nak} নক্ষত্ৰত{hp_tikshna}।"
        else:
            house_analysis += f"\n  এই ঘৰত কোনো গ্ৰহ অৱস্থান কৰা নাই।"

        house_analysis += f"\n  এই ঘৰৰ অধিপতি: {lord_name}"
        if lord_house:
            house_analysis += f", যি {lord_house} নং ঘৰত অৱস্থান কৰিছে, {lord_nak} নক্ষত্ৰত।"
            if lord_tikshna:
                house_analysis += f" {lord_name} তীক্ষ্ণ নক্ষত্ৰ ({lord_nak})ত অৱস্থান কৰি অশুভ ফল প্ৰদান কৰিব পাৰে।"

    # Build the system prompt
    gender_text = "জাতিকা (মহিলা)" if gender == "female" else "জাতক (পুৰুষ)"
    system_prompt = f"""তুমি এজন অভিজ্ঞ বৈদিক জ্যোতিষী পণ্ডিত। তুমি অসমীয়া ভাষাত উত্তৰ দিবা।

গুৰুত্বপূৰ্ণ নিৰ্দেশনা:
- তুমি এজন গ্ৰাহকৰ জন্মকুণ্ডলীৰ ভিত্তিত তেওঁৰ প্ৰশ্নৰ উত্তৰ দিবা।
- তুমি কেৱল জ্যোতিষশাস্ত্ৰৰ সম্ভাৱনা, কাৰণ, সমস্যা, আৰু চূড়ান্ত ফলাফলৰ ওপৰত গুৰুত্ব দিবা।
- কোনো ধৰণৰ সাধাৰণ অস্বীকাৰ (generic disclaimer), অলাগতিয়াল পাতনি, বা অদৰকাৰী তথ্য লিখিব নালাগে।
- পোনপটীয়াকৈ বিশ্লেষণলৈ আহিবা।
- যদি কোনো নেতিবাচক গ্ৰহ প্ৰভাৱ বা দোষ থাকে, তেন্তে নিৰ্দিষ্ট, ব্যৱহাৰিক বৈদিক জ্যোতিষীয় প্ৰতিকাৰ (যেনে: মন্ত্ৰ, ৰত্ন, দান, ব্ৰত) অসমীয়া ভাষাত উল্লেখ কৰিবা।
- উত্তৰ বিতংভাৱে, পেৰেগ্ৰাফ আকাৰত, আৰু শুদ্ধ অসমীয়া ভাষাত দিবা।
- তুমি কেতিয়াও চিকিৎসা, আইনী, বা বিত্তীয় পৰামৰ্শ নিদিবা — কেৱল জ্যোতিষীয় বিশ্লেষণ দিবা।"""

    user_prompt = f"""তলত এজন গ্ৰাহকৰ জন্মকুণ্ডলীৰ সম্পূৰ্ণ তথ্য দিয়া হৈছে:

গ্ৰাহকৰ নাম: {user_name}, লিংগ: {gender_text}

{kundli_context}
{house_analysis}

গ্ৰাহকে সুধিছে: "{question}"

ওপৰৰ কুণ্ডলীৰ তথ্যৰ ভিত্তিত, দয়া কৰি বিতংভাৱে উত্তৰ দিয়া। উত্তৰত তলৰ বিষয়সমূহ অন্তৰ্ভুক্ত কৰিবা:

1. প্ৰশ্নৰ বিষয়ৰ সৈতে জড়িত গ্ৰহসমূহৰ অৱস্থান আৰু তাৰ শুভ/অশুভ প্ৰভাৱ
2. কোনো দোষ বা অশুভ গ্ৰহ প্ৰভাৱ থাকিলে তাৰ বিৱৰণ আৰু কাৰণ
3. বৰ্তমান চলি থকা মহাদশা/অন্তৰ্দশাৰ প্ৰভাৱ
4. চূড়ান্ত ফলাফল — কি আশা কৰিব পাৰি
5. যদি কোনো নেতিবাচক প্ৰভাৱ থাকে, তেন্তে নিৰ্দিষ্ট বৈদিক প্ৰতিকাৰ (মন্ত্ৰ, ৰত্ন, দান, ব্ৰত) অসমীয়া ভাষাত দিবা

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

        response_parts.append(f"আপোনাৰ কুণ্ডলীৰ {house_num} নং ঘৰটো {topic} স্থান।")

        if house_planets:
            planet_names = ", ".join(p["name"] for p in house_planets)
            response_parts.append(f"এই ঘৰত {planet_names} গ্ৰহ অৱস্থান কৰিছে।")
            for hp in house_planets:
                hp_nak = hp.get("nakshatra", "")
                if hp_nak in TIKSHNA_NAKSHATRAS:
                    response_parts.append(f"{hp['name']} গ্ৰহ {hp_nak} তীক্ষ্ণ নক্ষত্ৰত অৱস্থান কৰি কিছু অশুভ প্ৰভাৱ দিব পাৰে।")
        else:
            response_parts.append(f"এই ঘৰত কোনো গ্ৰহ অৱস্থান কৰা নাই।")

        response_parts.append(f"এই ঘৰৰ অধিপতি হৈছে {lord_name} গ্ৰহ।")
        if lord_house:
            response_parts.append(f"{lord_name} গ্ৰহ আপোনাৰ কুণ্ডলীৰ {lord_house} নং ঘৰত অৱস্থান কৰিছে।")
            if lord_tikshna:
                response_parts.append(f"{lord_name} গ্ৰহ {lord_nak} তীক্ষ্ণ নক্ষত্ৰত অৱস্থান কৰাৰ বাবে {topic} স্থানত কিছু বাধা-বিঘিনি আহিব পাৰে।")

    # Mangal dosha for marriage
    if topic == "বিবাহ":
        mangal = next((d for d in dosha_results if d.get("key") == "mangal_dosha" and d.get("present")), None)
        if mangal:
            response_parts.append("\nআপোনাৰ কুণ্ডলীত মাংগলিক দোষ উপস্থিত। ই বিবাহৰ ক্ষেত্ৰত বিলম্ব বা মতানৈক্যৰ সৃষ্টি কৰিব পাৰে। মাংগলিক দোষ নিবাৰণৰ বাবে হনুমান চালিচা পাঠ, মঙ্গলবাৰৰ ব্ৰত, আৰু পোৱাল ৰত্ন ধাৰণ কৰিব পাৰে।")
        else:
            response_parts.append("\nআপোনাৰ কুণ্ডলীত মাংগলিক দোষ অনুপস্থিত, যি বিবাহৰ বাবে শুভ।")

    # Current dasha
    if dasa_data:
        md = dasa_data[0]
        response_parts.append(f"\nবৰ্তমান আপুনি {md.get('md_lord', '')} মহাদশা অতিক্ৰম কৰি আছে।")
        if md.get("sub_dasas"):
            ad = md["sub_dasas"][0]
            response_parts.append(f"আৰু {ad.get('ad_lord', '')} অন্তৰ্দশা চলি আছে। এই দশাৰ প্ৰভাৱেও {topic} স্থানত পৰিব।")

    response_parts.append(f"\n【পৰামৰ্শ】")
    response_parts.append(f"আপোনাৰ {topic} স্থানৰ সম্পূৰ্ণ বিশ্লেষণৰ বাবে এজন অভিজ্ঞ জ্যোতিষীৰ পৰামৰ্শ লোৱাটো উচিত। কুণ্ডলীৰ অন্যান্য গ্ৰহৰ অৱস্থানো বিবেচনা কৰি সঠিক ফলাফল নিৰ্ণয় কৰা হয়।")

    return "\n".join(response_parts)
