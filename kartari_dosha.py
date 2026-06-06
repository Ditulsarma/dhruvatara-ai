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
    HTML ফৰ্মেটত প্ৰতিটো ঘৰৰ স্থিতি ৰঙীন কাৰ্ড হিচাপে প্ৰদৰ্শন কৰে।
    """
    all_analysis = get_complete_kartari_analysis(planet_house_map)
    pap_kartari = all_analysis["house_kartari"]["pap_kartari"]
    shubh_kartari = all_analysis["house_kartari"]["shubh_kartari"]
    mixed_kartari = all_analysis["house_kartari"]["mixed_kartari"]

    pap_houses_set = set(h["house"] for h in pap_kartari["affected_houses"])
    shubh_houses_set = set(h["house"] for h in shubh_kartari["affected_houses"])
    mixed_houses_set = set(h["house"] for h in mixed_kartari["affected_houses"])

    # CSS styles
    css = """
    <style>
        .kartari-container { font-family: 'Noto Sans Bengali', 'Arial', sans-serif; }
        .kartari-title { text-align:center; font-size:1.2rem; font-weight:800; color:#5B3E96; margin-bottom:6px; }
        .kartari-subtitle { text-align:center; font-size:0.8rem; color:#888; margin-bottom:16px; }
        .kartari-summary { display:flex; gap:10px; flex-wrap:wrap; justify-content:center; margin-bottom:18px; }
        .kartari-summary-item { padding:8px 16px; border-radius:20px; font-weight:700; font-size:0.82rem; display:flex; align-items:center; gap:6px; }
        .kartari-summary-item.red { background:#FFEBEE; color:#C62828; border:1px solid #EF9A9A; }
        .kartari-summary-item.green { background:#E8F5E9; color:#2E7D32; border:1px solid #A5D6A7; }
        .kartari-summary-item.yellow { background:#FFF8E1; color:#F57F17; border:1px solid #FFE082; }
        .kartari-summary-item.gray { background:#F5F5F5; color:#757575; border:1px solid #E0E0E0; }
        .kartari-grid { display:grid; grid-template-columns:repeat(4, 1fr); gap:8px; }
        @media (max-width:600px) { .kartari-grid { grid-template-columns:repeat(2, 1fr); } }
        @media (max-width:380px) { .kartari-grid { grid-template-columns:1fr; } }
        .kartari-house-card { border-radius:12px; padding:12px; text-align:center; transition:all 0.2s ease; }
        .kartari-house-card.red { background:linear-gradient(135deg, #FFEBEE, #FFCDD2); border:2px solid #EF9A9A; }
        .kartari-house-card.green { background:linear-gradient(135deg, #E8F5E9, #C8E6C9); border:2px solid #A5D6A7; }
        .kartari-house-card.yellow { background:linear-gradient(135deg, #FFF8E1, #FFECB3); border:2px solid #FFE082; }
        .kartari-house-card.gray { background:linear-gradient(135deg, #FAFAFA, #F5F5F5); border:2px solid #E0E0E0; }
        .kartari-house-num { font-size:0.7rem; font-weight:700; color:#888; margin-bottom:2px; }
        .kartari-house-name { font-size:0.78rem; font-weight:700; color:#333; margin-bottom:4px; line-height:1.3; }
        .kartari-house-planets { font-size:0.7rem; color:#666; margin-bottom:4px; }
        .kartari-house-status { font-size:0.72rem; font-weight:700; padding:3px 10px; border-radius:12px; display:inline-block; }
        .kartari-house-status.red { background:#C62828; color:white; }
        .kartari-house-status.green { background:#2E7D32; color:white; }
        .kartari-house-status.yellow { background:#F57F17; color:white; }
        .kartari-house-status.gray { background:#9E9E9E; color:white; }
    </style>
    """

    # Build HTML
    html = [css]
    html.append('<div class="kartari-container">')
    html.append('<div class="kartari-title">🔮 কৰ্তৰী যোগ বিশ্লেষণ</div>')
    html.append('<div class="kartari-subtitle">প্ৰতিটো ঘৰৰ কৰ্তৰী স্থিতি</div>')

    # Summary badges
    pap_count = len(pap_houses_set)
    shubh_count = len(shubh_houses_set)
    mixed_count = len(mixed_houses_set)
    normal_count = 12 - pap_count - shubh_count + mixed_count  # mixed counted in both

    html.append('<div class="kartari-summary">')
    if pap_count > 0:
        html.append(f'<div class="kartari-summary-item red">🔴 পাপ কৰ্তৰী: {pap_count} ঘৰ</div>')
    else:
        html.append('<div class="kartari-summary-item gray">🔴 পাপ কৰ্তৰী: 0</div>')
    if shubh_count > 0:
        html.append(f'<div class="kartari-summary-item green">🟢 শুভ কৰ্তৰী: {shubh_count} ঘৰ</div>')
    else:
        html.append('<div class="kartari-summary-item gray">🟢 শুভ কৰ্তৰী: 0</div>')
    if mixed_count > 0:
        html.append(f'<div class="kartari-summary-item yellow">🟡 মিশ্ৰিত: {mixed_count} ঘৰ</div>')
    html.append('</div>')

    # House cards grid
    html.append('<div class="kartari-grid">')
    for house_num in range(12):
        planets_in_house = [p for p, h in planet_house_map.items() if h == house_num]
        prev_house = (house_num - 1) % 12
        next_house = (house_num + 1) % 12

        prev_planets = [p for p, h in planet_house_map.items() if h == prev_house]
        next_planets = [p for p, h in planet_house_map.items() if h == next_house]

        prev_malefic = [p for p in prev_planets if p in MALEFIC_PLANETS]
        next_malefic = [p for p in next_planets if p in MALEFIC_PLANETS]
        prev_benefic = [p for p in prev_planets if p in BENEFIC_PLANETS]
        next_benefic = [p for p in next_planets if p in BENEFIC_PLANETS]

        # Determine card color class
        if prev_malefic and next_malefic and prev_benefic and next_benefic:
            color_class = "yellow"
            status_text = "🟡 মিশ্ৰিত"
        elif prev_malefic and next_malefic:
            color_class = "red"
            status_text = "🔴 পাপ কৰ্তৰী"
        elif prev_benefic and next_benefic:
            color_class = "green"
            status_text = "🟢 শুভ কৰ্তৰী"
        else:
            color_class = "gray"
            status_text = "⚪ সাধাৰণ"

        house_name = HOUSE_CHARACTERISTICS.get(house_num, f"ঘৰ {house_num + 1}")
        # Extract short name after the dash
        if "—" in house_name:
            house_name = house_name.split("—")[0].strip()
        elif " - " in house_name:
            house_name = house_name.split(" - ")[0].strip()

        planets_str = ", ".join(planets_in_house) if planets_in_house else "খালী"

        html.append(f'''<div class="kartari-house-card {color_class}">
            <div class="kartari-house-num">ঘৰ #{house_num + 1}</div>
            <div class="kartari-house-name">{house_name}</div>
            <div class="kartari-house-planets">{planets_str}</div>
            <div class="kartari-house-status {color_class}">{status_text}</div>
        </div>''')

    html.append('</div>')
    html.append('</div>')

    return "\n".join(html)


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