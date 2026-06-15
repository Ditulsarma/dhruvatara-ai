"""
ধ্ৰুৱতৰা AI - দ্বাদশ ভাব ফল ইঞ্জিন (Dwadash Bhab Phala Engine)
============================================================
বৈদিক জ্যোতিষ অনুসৰি ১২টি ভাবৰ গৃহ অধিপতিৰ বিভিন্ন স্থানত ফলাফল
প্ৰতিটি গ্ৰহৰ লগ্নৰ পৰা প্ৰতিটি স্থানত বিশদ ফল।

নতুন পদ্ধতি: প্ৰতিটো ভাবৰ অধিপতি গ্ৰহটো ক'ত অৱস্থিত সেই অনুসৰি
কেৱল সেই স্থানৰ ফলাফল দেখুৱায়।
"""

import json
import os

# Load Dwadash Bhab Phala data from JSON file
DATA_FILE = os.path.join(os.path.dirname(__file__), 'Dwadash_Bhab_Phal.json')

# Rashi Lords (ৰাশিৰ অধিপতি) - must match panchanga.py
RASHI_LORDS = [
    "মংগল", "শুক্ৰ", "বুধ", "চন্দ্ৰ", "ৰবি", "বুধ",
    "শুক্ৰ", "মংগল", "বৃহস্পতি", "শনি", "শনি", "বৃহস্পতি"
]

def load_dwadash_data():
    """Load Dwadash Bhab Phala data from JSON file"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('Dwadash_Bhab_Phal', {})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading Dwadash Bhab Phala data: {e}")
        return {}

# Global cache
_dwadash_data = load_dwadash_data()

HOUSE_NAMES = [
    "প্ৰথম ভাব (লগ্ন/আত্ম)",
    "দ্বিতীয় ভাব (ধন)",
    "তৃতীয় ভাব (সহোদৰ)",
    "চতুৰ্থ ভাব (মাতৃ)",
    "পঞ্চম ভাব (পুত্ৰ)",
    "ষষ্ঠ ভাব (ৰোগ/শত্ৰু)",
    "সপ্তম ভাব (পত্নী)",
    "অষ্টম ভাব (আয়ু/মৃত্যু)",
    "নবম ভাব (ভাগ্য)",
    "দশম ভাব (কৰ্ম)",
    "একাদশ ভাব (লাভ)",
    "দ্বাদশ ভাব (ব্যয়)"
]

# Short Assamese names for house lords (used in direct titles)
HOUSE_LORD_SHORT_I18N = {
    'as': ["লগ্নপতি","ধনপতি","সহজপতি","চতুৰ্থপতি","পঞ্চমপতি","ষষ্ঠপতি","সপ্তমপতি","অষ্টমপতি","নবমপতি","দশমপতি","একাদশপতি","দ্বাদশপতি"],
    'bn': ["লগ্নপতি","ধনপতি","সহজপতি","চতুৰ্থপতি","পঞ্চমপতি","ষষ্ঠপতি","সপ্তমপতি","অষ্টমপতি","নবমপতি","দশমপতি","একাদশপতি","দ্বাদশপতি"],
    'hi': ["लग्नपति","धनपति","सहजपति","चतुर्थपति","पंचमपति","षष्ठपति","सप्तमपति","अष्टमपति","नवमपति","दशमपति","एकादशपति","द्वादशपति"],
    'en': ["Lagnapati","Dhanapati","Sahajapati","Chaturthpati","Panchampati","Shasthpati","Saptampati","Ashtampati","Navampati","Dashampati","Ekadashpati","Dwadashpati"],
}

# Short names for house placements (used in direct titles)
HOUSE_PLACEMENT_SHORT_I18N = {
    'as': ["লগ্নত","দ্বিতীয়ত","তৃতীয়ত","চতুৰ্থত","পঞ্চমত","ষষ্ঠত","সপ্তমত","অষ্টমত","নবমত","দশমত","একাদশত","দ্বাদশত"],
    'bn': ["লগ্নত","দ্বিতীয়ত","তৃতীয়ত","চতুৰ্থত","পঞ্চমত","ষষ্ঠত","সপ্তমত","অষ্টমত","নবমত","দশমত","একাদশত","দ্বাদশত"],
    'hi': ["लग्न में","द्वितीय में","तृतीय में","चतुर्थ में","पंचम में","षष्ठ में","सप्तम में","अष्टम में","नवम में","दशम में","एकादश में","द्वादश में"],
    'en': ["in Lagna","in 2nd","in 3rd","in 4th","in 5th","in 6th","in 7th","in 8th","in 9th","in 10th","in 11th","in 12th"],
}

# i18n titles and labels
_DWADASH_TITLES_I18N = {
    'as': {"result_of": "ৰ বিভিন্ন স্থানত ফলাফল", "placed_in": " অৱস্থিত হলে:"},
    'bn': {"result_of": "ৰ বিভিন্ন স্থানত ফলাফল", "placed_in": " অৱস্থিত হলে:"},
    'hi': {"result_of": " के विभिन्न स्थानों में फल", "placed_in": " में स्थित होने पर:"},
    'en': {"result_of": " - Results in Various Positions", "placed_in": " placed in:"},
}

# Fallback Assamese (keep original)
HOUSE_LORD_SHORT = HOUSE_LORD_SHORT_I18N['as']
HOUSE_PLACEMENT_SHORT = HOUSE_PLACEMENT_SHORT_I18N['as']

HOUSE_LORDS = [
    "1stHouse_Lord",
    "2ndHouse_Lord",
    "3rdHouse_Lord",
    "4thHouse_Lord",
    "5thHouse_Lord",
    "6thHouse_Lord",
    "7thHouse_Lord",
    "8thHouse_Lord",
    "9thHouse_Lord",
    "10thHouse_Lord",
    "11thHouse_Lord",
    "12thHouse_Lord"
]

def get_dwadash_phala(house_lord_index, position_index):
    """
    Get Dwadash Bhab Phala for a specific house lord in a specific position
    
    Args:
        house_lord_index: 0-11 (which house lord)
        position_index: 0-11 (which house position)
    
    Returns:
        str: The phala text, or empty string if not found
    """
    if house_lord_index < 0 or house_lord_index > 11 or position_index < 0 or position_index > 11:
        return ""
    
    house_key = HOUSE_LORDS[house_lord_index]
    position_key = str(position_index + 1)  # JSON keys are 1-indexed ("1"-"12")
    
    if house_key in _dwadash_data:
        house_data = _dwadash_data[house_key]
        if position_key in house_data:
            return house_data[position_key]
    
    return ""

def get_house_lord_results(house_lord_index):
    """
    Get all 12 position results for a specific house lord
    
    Args:
        house_lord_index: 0-11 (which house lord)
    
    Returns:
        dict: Position -> Phala text mapping
    """
    if house_lord_index < 0 or house_lord_index > 11:
        return {}
    
    house_key = HOUSE_LORDS[house_lord_index]
    
    if house_key in _dwadash_data:
        return _dwadash_data[house_key]
    
    return {}

def get_all_dwadash_houses():
    """Get all 12 house lords data"""
    return _dwadash_data

def _compute_house_lord_placement(house_idx, asc_rasi_idx, planet_houses):
    """
    Compute which house the lord of a given house is placed in.
    
    Args:
        house_idx: 0-11 (the house whose lord we're finding)
        asc_rasi_idx: 0-11 (ascendant rashi index)
        planet_houses: dict mapping planet names (Assamese) to house indices (0-11)
    
    Returns:
        tuple: (lord_name, placement_house_idx) or (None, None) if not found
    """
    # The rashi that falls in this house
    rashi_idx = (asc_rasi_idx + house_idx) % 12
    lord_name = RASHI_LORDS[rashi_idx]
    
    # Find where this lord planet is placed
    if lord_name in planet_houses:
        placement_house = planet_houses[lord_name]
        return lord_name, placement_house
    
    return None, None

def get_dwadash_html(planet_houses=None, asc_rasi_idx=None, selected_houses=None):
    """
    Generate HTML for Dwadash Bhab Phala showing only the actual placement
    of each house lord (not all 12 positions).
    
    Args:
        planet_houses: dict mapping planet names to house indices (0-11)
        asc_rasi_idx: 0-11 ascendant rashi index
        selected_houses: List of house indices to display (0-11), or None for all
    
    Returns:
        str: HTML content for Dwadash results
    """
    if selected_houses is None:
        selected_houses = list(range(12))
    
    # If no chart data provided, fall back to showing all positions
    if planet_houses is None or asc_rasi_idx is None:
        return _get_dwadash_html_all(selected_houses)
    
    html = '<div class="dwadash-phala-container">'
    
    for house_idx in selected_houses:
        if house_idx < 0 or house_idx > 11:
            continue
        
        lord_name, placement_house = _compute_house_lord_placement(house_idx, asc_rasi_idx, planet_houses)
        
        if lord_name is None:
            continue
        
        # Get the phala for this house lord in its actual placement
        phala = get_dwadash_phala(house_idx, placement_house)
        
        if not phala:
            continue
        
        # Build direct Assamese title: e.g. "সহজপতি দ্বাদশত অবস্থিত হলে:"
        lord_short = HOUSE_LORD_SHORT[house_idx]
        place_short = HOUSE_PLACEMENT_SHORT[placement_house]
        direct_title = f"{lord_short} {place_short} অৱস্থিত হলে:"
        
        html += f'''<div class="dwadash-house-section">
            <div class="dwadash-house-title">
                <span class="dwadash-icon">🏠</span>
                <h4>{direct_title}</h4>
                <span class="dwadash-badge">{lord_name}</span>
            </div>
            <div class="dwadash-positions">
                <div class="dwadash-position-item">
                    <div class="position-phala">{phala}</div>
                </div>
            </div>
        </div>'''
    
    html += '</div>'
    return html

def get_dwadash_html_from_data(data: dict, planet_houses=None, asc_rasi_idx=None, selected_houses=None, lang='as'):
    """i18n-aware version: uses provided data dict instead of default JSON.
    data format: {house_lord_key: {position_key: phala_text}}
    e.g. {"1stHouse_Lord": {"1": "...", "2": "..."}, ...}
    """
    if selected_houses is None:
        selected_houses = list(range(12))

    lords = HOUSE_LORD_SHORT_I18N.get(lang, HOUSE_LORD_SHORT_I18N['as'])
    places = HOUSE_PLACEMENT_SHORT_I18N.get(lang, HOUSE_PLACEMENT_SHORT_I18N['as'])
    titles = _DWADASH_TITLES_I18N.get(lang, _DWADASH_TITLES_I18N['as'])

    if planet_houses is None or asc_rasi_idx is None:
        # Fallback: show all positions from the provided data
        html = '<div class="dwadash-phala-container">'
        for house_idx in selected_houses:
            if house_idx < 0 or house_idx > 11:
                continue
            house_key = HOUSE_LORDS[house_idx]
            if house_key not in data:
                continue
            house_lord_results = data[house_key]
            lord_short = lords[house_idx]
            result_of = titles['result_of']
            html += f'''<div class="dwadash-house-section">
                <div class="dwadash-house-title">
                    <span class="dwadash-icon">🏠</span>
                    <h4>{lord_short}{result_of}</h4>
                </div>
                <div class="dwadash-positions">'''
            for pos_idx in range(12):
                phala = house_lord_results.get(str(pos_idx + 1), "")
                if phala:
                    place_short = places[pos_idx]
                    html += f'''<div class="dwadash-position-item">
                        <div class="position-label">➤ {lord_short} {place_short}:</div>
                        <div class="position-phala">{phala}</div>
                    </div>'''
            html += '</div></div>'
        html += '</div>'
        return html

    # Normal mode: show only actual placements
    html = '<div class="dwadash-phala-container">'
    for house_idx in selected_houses:
        if house_idx < 0 or house_idx > 11:
            continue
        lord_name, placement_house = _compute_house_lord_placement(house_idx, asc_rasi_idx, planet_houses)
        if lord_name is None:
            continue
        house_key = HOUSE_LORDS[house_idx]
        if house_key not in data:
            continue
        phala = data[house_key].get(str(placement_house + 1), "")
        if not phala:
            continue
        lord_short = lords[house_idx]
        place_short = places[placement_house]
        placed_in = titles['placed_in']
        direct_title = f"{lord_short} {place_short}{placed_in}"
        html += f'''<div class="dwadash-house-section">
            <div class="dwadash-house-title">
                <span class="dwadash-icon">🏠</span>
                <h4>{direct_title}</h4>
                <span class="dwadash-badge">{lord_name}</span>
            </div>
            <div class="dwadash-positions">
                <div class="dwadash-position-item">
                    <div class="position-phala">{phala}</div>
                </div>
            </div>
        </div>'''
    html += '</div>'
    return html

def _get_dwadash_html_all(selected_houses=None):
    """Fallback: show all 12 positions for each house lord (when chart data unavailable)"""
    if selected_houses is None:
        selected_houses = list(range(12))
    
    html = '<div class="dwadash-phala-container">'
    
    for house_idx in selected_houses:
        if house_idx < 0 or house_idx > 11:
            continue
        
        house_lord_results = get_house_lord_results(house_idx)
        
        if not house_lord_results:
            continue
        
        lord_short = HOUSE_LORD_SHORT[house_idx]
        
        html += f'''<div class="dwadash-house-section">
            <div class="dwadash-house-title">
                <span class="dwadash-icon">🏠</span>
                <h4>{lord_short}ৰ বিভিন্ন স্থানত ফলাফল</h4>
            </div>
            <div class="dwadash-positions">'''
        
        for pos_idx in range(12):
            phala = house_lord_results.get(str(pos_idx + 1), "")  # JSON keys are 1-indexed
            if phala:
                place_short = HOUSE_PLACEMENT_SHORT[pos_idx]
                html += f'''<div class="dwadash-position-item">
                    <div class="position-label">➤ {lord_short} {place_short}:</div>
                    <div class="position-phala">{phala}</div>
                </div>'''
        
        html += '''</div></div>'''
    
    html += '</div>'
    return html

def get_dwadash_text(planet_houses=None, asc_rasi_idx=None, selected_houses=None):
    """
    Generate plain text for Dwadash Bhab Phala (for PDF) showing only
    the actual placement of each house lord.
    """
    if selected_houses is None:
        selected_houses = list(range(12))
    
    text = "দ্বাদশ ভাব ফল বিশ্লেষণ\n"
    text += "=" * 50 + "\n\n"
    
    for house_idx in selected_houses:
        if house_idx < 0 or house_idx > 11:
            continue
        
        if planet_houses and asc_rasi_idx is not None:
            lord_name, placement_house = _compute_house_lord_placement(house_idx, asc_rasi_idx, planet_houses)
            if lord_name is None:
                continue
            phala = get_dwadash_phala(house_idx, placement_house)
            if phala:
                lord_short = HOUSE_LORD_SHORT[house_idx]
                place_short = HOUSE_PLACEMENT_SHORT[placement_house]
                text += f"{lord_short} {place_short} অৱস্থিত হলে:\n"
                text += "-" * 40 + "\n"
                text += f"\n{phala}\n\n"
        else:
            house_lord_results = get_house_lord_results(house_idx)
            if not house_lord_results:
                continue
            lord_short = HOUSE_LORD_SHORT[house_idx]
            text += f"{lord_short}ৰ বিভিন্ন স্থানত ফলাফল:\n"
            text += "-" * 40 + "\n"
            for pos_idx in range(12):
                phala = house_lord_results.get(str(pos_idx + 1), "")
                if phala:
                    place_short = HOUSE_PLACEMENT_SHORT[pos_idx]
                    text += f"\n➤ {lord_short} {place_short}: {phala}\n"
            text += "\n"
    
    return text

def get_dwadash_json(planet_houses=None, asc_rasi_idx=None, selected_houses=None):
    """
    Get Dwadash Bhab Phala data as JSON showing only actual placements.
    """
    if selected_houses is None:
        selected_houses = list(range(12))
    
    result = {
        "title": "দ্বাদশ ভাব ফল (12 House Results)",
        "houses": []
    }
    
    for house_idx in selected_houses:
        if house_idx < 0 or house_idx > 11:
            continue
        
        if planet_houses and asc_rasi_idx is not None:
            lord_name, placement_house = _compute_house_lord_placement(house_idx, asc_rasi_idx, planet_houses)
            if lord_name is None:
                continue
            phala = get_dwadash_phala(house_idx, placement_house)
            if phala:
                result["houses"].append({
                    "house_index": house_idx,
                    "house_name": HOUSE_NAMES[house_idx],
                    "lord_name": lord_name,
                    "lord_placement_house": placement_house,
                    "lord_placement_name": HOUSE_NAMES[placement_house],
                    "phala": phala
                })
        else:
            house_lord_results = get_house_lord_results(house_idx)
            if not house_lord_results:
                continue
            positions = []
            for pos_idx in range(12):
                phala = house_lord_results.get(str(pos_idx + 1), "")  # JSON keys are 1-indexed
                if phala:
                    positions.append({
                        "position_index": pos_idx,
                        "position_name": HOUSE_NAMES[pos_idx],
                        "phala": phala
                    })
            result["houses"].append({
                "house_index": house_idx,
                "house_name": HOUSE_NAMES[house_idx],
                "positions": positions
            })
    
    return result
