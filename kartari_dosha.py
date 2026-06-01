"""
ধ্ৰুৱতৰা AI - কৰ্তৰী যোগ বিশ্লেষণ ইঞ্জিন
Kartari Yoga Engine: Pap Kartari Dosha (Malefic Kartari), Shubh Kartari Yoga (Benefic Kartari)
আৰু গ্ৰহ কৰ্তৰী অধিপতি বিশ্লেষণ
"""

# ─── গ্ৰহ শ্ৰেণী বিভাজন ────────────────────────

# অশুভ গ্ৰহ (Malefic Planets)
MALEFIC_PLANETS = ["মংগল", "শনি", "ৰাহু", "কেতু","ৰবি"]

# শুভ গ্ৰহ (Benefic Planets)
BENEFIC_PLANETS = ["বৃহস্পতি", "শুক্ৰ", "বুধ", "চন্দ্ৰ"]

# নিৰপেক্ষ/মিশ্ৰ গ্ৰহ (Neutral/Mixed)
NEUTRAL_PLANETS = [""]

# প্ৰতিটো গ্ৰহৰ অধিপতি (Lordship) ঘৰ
PLANET_LORDSHIP = {
    "ৰবি": [5],           # Sun rules 5th house (from natural zodiac)
    "চন্দ্ৰ": [4],         # Moon rules 4th house
    "মংগল": [1, 8],       # Mars rules 1st & 8th
    "বুধ": [3, 6],        # Mercury rules 3rd & 6th
    "বৃহস্পতি": [9, 12],   # Jupiter rules 9th & 12th
    "শুক্ৰ": [2, 7],       # Venus rules 2nd & 7th
    "শনি": [10, 11],      # Saturn rules 10th & 11th
    "ৰাহু": [0],          # Rahu (shadow planet)
    "কেতু": [0],          # Ketu (shadow planet)
}

# গ্ৰহৰ কাৰকত্ব (Karaka - Significations)
PLANET_KARAKA = {
    "ৰবি": "আত্মা, পিতৃ, প্ৰতিষ্ঠা, কৰ্তৃত্ব, শক্তি",
    "চন্দ্ৰ": "মন, মাতৃ, আবেগ, সুখ, মানসিক স্বাস্থ্য",
    "মংগল": "সাহস, শক্তি, যুদ্ধ, ভাতৃ, যৌনতা",
    "বুধ": "বুদ্ধি, যোগাযোগ, বাণিজ্য, সৰু ভাই-ভনী, শিক্ষা",
    "বৃহস্পতি": "জ্ঞান, ভাগ্য, সন্তান, গুৰু, ধৰ্ম",
    "শুক্ৰ": "প্ৰেম, বৈবাহিক জীৱন, বিলাসিতা, শিল্প, সৌন্দৰ্য",
    "শনি": "দীৰ্ঘায়ু, বয়স, কঠোৰ পৰিশ্ৰম, বাধা, ভাগ্য",
    "ৰাহু": "মোহ, লোভ, অপূৰ্ণ আকাঙ্ক্ষা",
    "কেতু": "আধ্যাত্মিকতা, ত্যাগ, মুক্তি",
}

# ─── ঘৰৰ বৈশিষ্ট্য (House Significations) ────────────────────────

HOUSE_CHARACTERISTICS = {
    0: "প্ৰথম ভাৱ - আত্মা, ব্যক্তিত্ব, শৰীৰ, স্বাস্থ্য, আত্মবিশ্বাস",
    1: "দ্বিতীয় ভাৱ - ধন, পৰিয়াল, বাকশক্তি, খাদ্য",
    2: "তৃতীয় ভাৱ - ভাই-ভনী, সাহস, ভ্ৰমণ, শিক্ষা",
    3: "চতুৰ্থ ভাৱ - মাতৃ, ঘৰ, সম্পত্তি, আৰাম, শান্তি",
    4: "পঞ্চম ভাৱ - সন্তান, শিক্ষা, বুদ্ধিমত্তা, প্ৰেম",
    5: "ষষ্ঠ ভাৱ - শত্ৰু, ৰোগ, ঋণ, প্ৰতিযোগিতা",
    6: "সপ্তম ভাৱ - বিবাহ, সংগী, ব্যৱসায়িক অংশীদাৰ",
    7: "অষ্টম ভাৱ - মৃত্যু, উত্তৰাধিকাৰ, ৰহস্য, দুৰ্ঘটনা",
    8: "নৱম ভাৱ - ভাগ্য, পিতৃ, ধৰ্ম, উচ্চশিক্ষা, ভ্ৰমণ",
    9: "দশম ভাৱ - পেচা, সামাজিক অৱস্থান, সুনাম",
    10: "একাদশ ভাৱ - লাভ, বন্ধু, আকাঙ্ক্ষা পূৰণ",
    11: "দ্বাদশ ভাৱ - ব্যয়, নিষ্কাশন, আধ্যাত্মিকতা, টোপনি",
}


def analyze_pap_kartari_dosha(planet_house_map: dict) -> dict:
    """
    পাপ কৰ্তৰী দোষ: যদি কোনো ঘৰৰ দুয়োকাষে অশুভ গ্ৰহ বহে।
    planet_house_map: {"গ্ৰহ": ঘৰ_নম্বৰ, ...}
    """
    pap_kartari_houses = []
    
    # প্ৰতিটো ঘৰৰ বাবে পৰীক্ষা কৰক
    for house_num in range(12):
        prev_house = (house_num - 1) % 12
        next_house = (house_num + 1) % 12
        
        # এই ঘৰত কোন গ্ৰহ আছে?
        planets_in_house = [p for p, h in planet_house_map.items() if h == house_num]
        
        # আগৰ ঘৰত অশুভ গ্ৰহ আছে নেকি?
        prev_malefic = any(
            planet_house_map.get(p) == prev_house 
            for p in MALEFIC_PLANETS 
            if planet_house_map.get(p) is not None
        )
        
        # পিছৰ ঘৰত অশুভ গ্ৰহ আছে নেকি?
        next_malefic = any(
            planet_house_map.get(p) == next_house 
            for p in MALEFIC_PLANETS 
            if planet_house_map.get(p) is not None
        )
        
        # যদি দুয়োকাষে অশুভ গ্ৰহ থাকে
        if prev_malefic and next_malefic:
            pap_kartari_houses.append({
                "house": house_num,
                "house_name": HOUSE_CHARACTERISTICS.get(house_num, f"ঘৰ {house_num + 1}"),
                "planets_in_house": planets_in_house,
                "effect": "ফল নাশ কৰে"
            })
    
    return {
        "present": len(pap_kartari_houses) > 0,
        "affected_houses": pap_kartari_houses,
        "severity": len(pap_kartari_houses),
        "description": "অশুভ গ্ৰহৰ মাজত থকা ঘৰ আৰু সেই ঘৰৰ কাৰ্যকাৰিতা নষ্ট হয়"
    }


def analyze_shubh_kartari_yoga(planet_house_map: dict) -> dict:
    """
    শুভ কৰ্তৰী যোগ: যদি কোনো ঘৰৰ দুয়োকাষে শুভ গ্ৰহ বহে।
    planet_house_map: {"গ্ৰহ": ঘৰ_নম্বৰ, ...}
    """
    shubh_kartari_houses = []
    
    # প্ৰতিটো ঘৰৰ বাবে পৰীক্ষা কৰক
    for house_num in range(12):
        prev_house = (house_num - 1) % 12
        next_house = (house_num + 1) % 12
        
        # এই ঘৰত কোন গ্ৰহ আছে?
        planets_in_house = [p for p, h in planet_house_map.items() if h == house_num]
        
        # আগৰ ঘৰত শুভ গ্ৰহ আছে নেকি?
        prev_benefic = any(
            planet_house_map.get(p) == prev_house 
            for p in BENEFIC_PLANETS 
            if planet_house_map.get(p) is not None
        )
        
        # পিছৰ ঘৰত শুভ গ্ৰহ আছে নেকি?
        next_benefic = any(
            planet_house_map.get(p) == next_house 
            for p in BENEFIC_PLANETS 
            if planet_house_map.get(p) is not None
        )
        
        # যদি দুয়োকাষে শুভ গ্ৰহ থাকে
        if prev_benefic and next_benefic:
            shubh_kartari_houses.append({
                "house": house_num,
                "house_name": HOUSE_CHARACTERISTICS.get(house_num, f"ঘৰ {house_num + 1}"),
                "planets_in_house": planets_in_house,
                "effect": "ফল বৃদ্ধি কৰে"
            })
    
    return {
        "present": len(shubh_kartari_houses) > 0,
        "affected_houses": shubh_kartari_houses,
        "strength": len(shubh_kartari_houses),
        "description": "শুভ গ্ৰহৰ মাজত থকা ঘৰ আৰু সেই ঘৰৰ কাৰ্যকাৰিতা বৃদ্ধি পায়"
    }


def analyze_mixed_kartari_yoga(pap_kartari: dict, shubh_kartari: dict) -> dict:
    """
    মিশ্ৰিত কৰ্তৰী যোগ: যদি একেটা ঘৰ পাপ আৰু শুভ উভয় কৰ্তৰী যোগত থাকে।
    """
    pap_houses = set(h["house"] for h in pap_kartari["affected_houses"])
    shubh_houses = set(h["house"] for h in shubh_kartari["affected_houses"])
    
    mixed_houses = pap_houses.intersection(shubh_houses)
    
    mixed_results = []
    for house_num in mixed_houses:
        mixed_results.append({
            "house": house_num,
            "house_name": HOUSE_CHARACTERISTICS.get(house_num, f"ঘৰ {house_num + 1}"),
            "effect": "প্ৰাথমিক বাধা, তাৰ পিছত ভাল ফল"
        })
    
    return {
        "present": len(mixed_results) > 0,
        "affected_houses": mixed_results,
        "description": "প্ৰথমে সংকট কিন্তু পৰৱৰ্তী সময়ত উন্নতি"
    }


def analyze_planet_pap_kartari(planet_name: str, planet_house_map: dict) -> dict:
    """
    গ্ৰহৰ ওপৰত পাপ কৰ্তৰী: যদি কোনো গ্ৰহৰ দুয়োকাষে অশুভ গ্ৰহ বহে।
    """
    planet_house = planet_house_map.get(planet_name)
    if planet_house is None:
        return {"present": False}
    
    prev_house = (planet_house - 1) % 12
    next_house = (planet_house + 1) % 12
    
    # আগৰ ঘৰত অশুভ গ্ৰহ আছে নেকি?
    prev_malefic = any(
        planet_house_map.get(p) == prev_house 
        for p in MALEFIC_PLANETS 
        if planet_house_map.get(p) is not None
    )
    
    # পিছৰ ঘৰত অশুভ গ্ৰহ আছে নেকি?
    next_malefic = any(
        planet_house_map.get(p) == next_house 
        for p in MALEFIC_PLANETS 
        if planet_house_map.get(p) is not None
    )
    
    if prev_malefic and next_malefic:
        return {
            "present": True,
            "planet": planet_name,
            "karaka": PLANET_KARAKA.get(planet_name, ""),
            "lordship": PLANET_LORDSHIP.get(planet_name, []),
            "effect": f"{planet_name}ৰ কাৰকত্ব নষ্ট হয় আৰু অধিপতি ঘৰবোৰৰ বৈশিষ্ট্য নষ্ট হয়"
        }
    
    return {"present": False}


def analyze_planet_shubh_kartari(planet_name: str, planet_house_map: dict) -> dict:
    """
    গ্ৰহৰ ওপৰত শুভ কৰ্তৰী: যদি কোনো গ্ৰহৰ দুয়োকাষে শুভ গ্ৰহ বহে।
    """
    planet_house = planet_house_map.get(planet_name)
    if planet_house is None:
        return {"present": False}
    
    prev_house = (planet_house - 1) % 12
    next_house = (planet_house + 1) % 12
    
    # আগৰ ঘৰত শুভ গ্ৰহ আছে নেকি?
    prev_benefic = any(
        planet_house_map.get(p) == prev_house 
        for p in BENEFIC_PLANETS 
        if planet_house_map.get(p) is not None
    )
    
    # পিছৰ ঘৰত শুভ গ্ৰহ আছে নেকি?
    next_benefic = any(
        planet_house_map.get(p) == next_house 
        for p in BENEFIC_PLANETS 
        if planet_house_map.get(p) is not None
    )
    
    if prev_benefic and next_benefic:
        return {
            "present": True,
            "planet": planet_name,
            "karaka": PLANET_KARAKA.get(planet_name, ""),
            "lordship": PLANET_LORDSHIP.get(planet_name, []),
            "effect": f"{planet_name}ৰ কাৰকত্ব বৃদ্ধি পায় আৰু অধিপতি ঘৰবোৰৰ বৈশিষ্ট্য বৃদ্ধি পায়"
        }
    
    return {"present": False}


def get_complete_kartari_analysis(planet_house_map: dict) -> dict:
    """
    সম্পূৰ্ণ কৰ্তৰী যোগ বিশ্লেষণ - ঘৰ আৰু গ্ৰহ উভয়ৰ বাবে।
    """
    # ঘৰৰ কৰ্তৰী বিশ্লেষণ
    pap_kartari = analyze_pap_kartari_dosha(planet_house_map)
    shubh_kartari = analyze_shubh_kartari_yoga(planet_house_map)
    mixed_kartari = analyze_mixed_kartari_yoga(pap_kartari, shubh_kartari)
    
    # গ্ৰহৰ কৰ্তৰী বিশ্লেষণ
    all_planets = ["ৰবি", "চন্দ্ৰ", "মংগল", "বুধ", "বৃহস্পতি", "শুক্ৰ", "শনি", "ৰাহু", "কেতু"]
    
    planet_pap_kartari = {}
    planet_shubh_kartari = {}
    
    for planet in all_planets:
        if planet in planet_house_map:
            planet_pap_kartari[planet] = analyze_planet_pap_kartari(planet, planet_house_map)
            planet_shubh_kartari[planet] = analyze_planet_shubh_kartari(planet, planet_house_map)
    
    return {
        "house_kartari": {
            "pap_kartari": pap_kartari,
            "shubh_kartari": shubh_kartari,
            "mixed_kartari": mixed_kartari
        },
        "planet_kartari": {
            "pap_kartari": planet_pap_kartari,
            "shubh_kartari": planet_shubh_kartari
        }
    }


def generate_kartari_report(planet_house_map: dict) -> str:
    """
    জন্মকুণ্ডলীৰ বাবে কৰ্তৰী যোগ ৰিপোৰ্ট প্ৰস্তুত কৰক।
    ধুনীয়া ফৰ্মেটত প্ৰতিটো ঘৰৰ স্থিতি প্ৰদৰ্শন কৰে।
    """
    report = []
    report.append("=" * 80)
    report.append("কৰ্তৰী যোগ বিশ্লেষণ ৰিপোৰ্ট (Kartari Yoga Analysis Report)")
    report.append("=" * 80)
    report.append("")
    
    # সকলো ঘৰৰ বাবে বিশ্লেষণ
    all_analysis = get_complete_kartari_analysis(planet_house_map)
    pap_kartari = all_analysis["house_kartari"]["pap_kartari"]
    shubh_kartari = all_analysis["house_kartari"]["shubh_kartari"]
    mixed_kartari = all_analysis["house_kartari"]["mixed_kartari"]
    
    # প্ৰতিটো ঘৰ ১-১২ ৰ বাবে বিতং প্ৰদৰ্শন
    report.append("\n📊 ঘৰৰ কৰ্তৰী যোগ বিশ্লেষণ:")
    report.append("-" * 80)
    
    for house_num in range(12):
        planets_in_house = [p for p, h in planet_house_map.items() if h == house_num]
        prev_house = (house_num - 1) % 12
        next_house = (house_num + 1) % 12
        
        prev_planets = [p for p, h in planet_house_map.items() if h == prev_house]
        next_planets = [p for p, h in planet_house_map.items() if h == next_house]
        
        # অশুভ গ্ৰহ চিহ্নিত কৰক
        prev_malefic = [p for p in prev_planets if p in MALEFIC_PLANETS]
        next_malefic = [p for p in next_planets if p in MALEFIC_PLANETS]
        
        # শুভ গ্ৰহ চিহ্নিত কৰক
        prev_benefic = [p for p in prev_planets if p in BENEFIC_PLANETS]
        next_benefic = [p for p in next_planets if p in BENEFIC_PLANETS]
        
        # ৰিপোৰ্ট প্ৰস্তুত কৰক
        report.append(f"\n🏠 ঘৰ #{house_num + 1} ({HOUSE_CHARACTERISTICS.get(house_num, '')})")
        report.append(f"   এই ঘৰত গ্ৰহ: {', '.join(planets_in_house) if planets_in_house else 'কোনো গ্ৰহ নাই'}")
        
        # আগৰ ঘৰৰ অৱস্থা
        report.append(f"   ← আগৰ ঘৰ ({house_num}): {', '.join(prev_planets) if prev_planets else 'খালী'}")
        
        # পিছৰ ঘৰৰ অৱস্থা
        report.append(f"   পিছৰ ঘৰ ({house_num + 2}) →: {', '.join(next_planets) if next_planets else 'খালী'}")
        
        # কৰ্তৰী অৱস্থা নিৰ্ণয়
        if prev_malefic and next_malefic:
            report.append(f"   ⚠️  পাপ কৰ্তৰী দোষ: হয় (অশুভ গ্ৰহ: {prev_malefic[0]} ← ঘৰ → {next_malefic[0]})")
            report.append(f"       প্ৰভাৱ: এই ঘৰৰ বৈশিষ্ট্য নষ্ট হয় 🔴")
        
        if prev_benefic and next_benefic:
            report.append(f"   ✅ শুভ কৰ্তৰী যোগ: হয় (শুভ গ্ৰহ: {prev_benefic[0]} ← ঘৰ → {next_benefic[0]})")
            report.append(f"       প্ৰভাৱ: এই ঘৰৰ বৈশিষ্ট্য বৃদ্ধি পায় 🟢")
        
        if prev_malefic and next_malefic and prev_benefic and next_benefic:
            report.append(f"   🟡 মিশ্ৰিত কৰ্তৰী: প্ৰথমে বাধা কিন্তু পৰৱৰ্তী সময়ত ভাল ফল")
        
        if not (prev_malefic and next_malefic) and not (prev_benefic and next_benefic):
            report.append(f"   ⚪ কোনো কৰ্তৰী নাই: এই ঘৰৰ স্বাভাৱিক ফল পোৱা যাব")
    
    # সাৰাংশ
    report.append("\n" + "=" * 80)
    report.append("📋 সাৰাংশ (Summary):")
    report.append("=" * 80)
    
    pap_houses = len(pap_kartari["affected_houses"])
    shubh_houses = len(shubh_kartari["affected_houses"])
    mixed_houses = len(mixed_kartari["affected_houses"])
    
    if pap_houses > 0:
        report.append(f"\n🔴 পাপ কৰ্তৰী দোষ আছে ({pap_houses}টা ঘৰত):")
        for h in pap_kartari["affected_houses"]:
            report.append(f"   • ঘৰ #{h['house'] + 1}: {h['house_name']}")
    else:
        report.append("\n✅ পাপ কৰ্তৰী দোষ নাই")
    
    if shubh_houses > 0:
        report.append(f"\n🟢 শুভ কৰ্তৰী যোগ আছে ({shubh_houses}টা ঘৰত):")
        for h in shubh_kartari["affected_houses"]:
            report.append(f"   • ঘৰ #{h['house'] + 1}: {h['house_name']}")
    else:
        report.append("\n⚪ শুভ কৰ্তৰী যোগ নাই")
    
    if mixed_houses > 0:
        report.append(f"\n🟡 মিশ্ৰিত কৰ্তৰী যোগ ({mixed_houses}টা ঘৰত) - প্ৰাথমিক প্ৰত্যাহ্বান তাৰ পিছত উন্নতি:")
        for h in mixed_kartari["affected_houses"]:
            report.append(f"   • ঘৰ #{h['house'] + 1}: {h['house_name']}")
    
    report.append("\n" + "=" * 80)
    
    return "\n".join(report)


def get_house_status_visual(planet_house_map: dict) -> dict:
    """
    প্ৰতিটো ঘৰৰ কৰ্তৰী স্থিতি ভিজ্যুৱেলী প্ৰদৰ্শন কৰক।
    """
    status_map = {}
    
    for house_num in range(12):
        prev_house = (house_num - 1) % 12
        next_house = (house_num + 1) % 12
        
        # আগৰ ঘৰত অশুভ গ্ৰহ আছে নেকি?
        prev_malefic = any(
            planet_house_map.get(p) == prev_house 
            for p in MALEFIC_PLANETS 
            if planet_house_map.get(p) is not None
        )
        
        # পিছৰ ঘৰত অশুভ গ্ৰহ আছে নেকি?
        next_malefic = any(
            planet_house_map.get(p) == next_house 
            for p in MALEFIC_PLANETS 
            if planet_house_map.get(p) is not None
        )
        
        # আগৰ ঘৰত শুভ গ্ৰহ আছে নেকি?
        prev_benefic = any(
            planet_house_map.get(p) == prev_house 
            for p in BENEFIC_PLANETS 
            if planet_house_map.get(p) is not None
        )
        
        # পিছৰ ঘৰত শুভ গ্ৰহ আছে নেকি?
        next_benefic = any(
            planet_house_map.get(p) == next_house 
            for p in BENEFIC_PLANETS 
            if planet_house_map.get(p) is not None
        )
        
        # স্থিতি নিৰ্ধাৰণ কৰক
        if prev_malefic and next_malefic:
            status = "🔴 পাপ কৰ্তৰী"
        elif prev_benefic and next_benefic:
            status = "🟢 শুভ কৰ্তৰী"
        elif (prev_malefic or next_malefic) and (prev_benefic or next_benefic):
            status = "🟡 মিশ্ৰিত"
        else:
            status = "⚪ সাধাৰণ"
        
        status_map[f"ঘৰ {house_num + 1}"] = {
            "status": status,
            "house_char": HOUSE_CHARACTERISTICS.get(house_num, ""),
            "planets": [p for p, h in planet_house_map.items() if h == house_num]
        }
    
    return status_map