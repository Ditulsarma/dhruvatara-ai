"""
ধ্ৰুৱতৰা AI - অষ্টকবৰ্গ ইঞ্জিন (Ashtakavarga Engine)
Calculates Bhinna Ashtakavarga (BAV) for 7 planets, Sarvashtakavarga (SAV),
Yogarekha (যোগৰেখা) and Yogabindu (যোগবিন্দু).

Based on classical Vedic Astrology Ashtakavarga principles.
Uses modulo arithmetic: Target_Sign = ((Reference_Planet_Sign + Benefic_House - 1) % 12)
"""

# ─── Planet names in English (internal keys) ───
PLANET_KEYS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# ─── Zodiac sign names (1-indexed: 1=Aries ... 12=Pisces) ───
ZODIAC_SIGNS = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
}

# ─── Bhinna Ashtakavarga (BAV) Reference Arrays ──────────────────────
# Each planet distributes bindus (points) based on house positions from
# all 7 planets AND the Lagna (Ascendant).
# Format: { planet_key: { from_planet_or_lagna: [list of benefic houses] } }

BAV_REFERENCES = {
    "Sun": {
        "from_Sun":      [1, 2, 4, 7, 8, 9, 10, 11],
        "from_Moon":     [3, 6, 10, 11],
        "from_Mars":     [1, 2, 4, 7, 8, 9, 10, 11],
        "from_Mercury":  [3, 5, 6, 9, 10, 11, 12],
        "from_Jupiter":  [5, 6, 9, 11],
        "from_Venus":    [6, 7, 12],
        "from_Saturn":   [1, 2, 4, 7, 8, 9, 10, 11],
        "from_Lagna":    [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "from_Sun":      [3, 6, 7, 8, 10, 11],
        "from_Moon":     [1, 3, 6, 7, 10, 11],
        "from_Mars":     [2, 3, 5, 6, 9, 10, 11],
        "from_Mercury":  [1, 3, 4, 5, 7, 8, 10, 11],
        "from_Jupiter":  [1, 4, 7, 8, 10, 11, 12],
        "from_Venus":    [3, 4, 5, 7, 9, 10, 11],
        "from_Saturn":   [3, 5, 6, 11],
        "from_Lagna":    [3, 6, 10, 11],
    },
    "Mars": {
        "from_Sun":      [3, 5, 6, 10, 11],
        "from_Moon":     [3, 6, 11],
        "from_Mars":     [1, 2, 4, 7, 8, 10, 11],
        "from_Mercury":  [3, 5, 6, 11],
        "from_Jupiter":  [6, 10, 11, 12],
        "from_Venus":    [6, 8, 11, 12],
        "from_Saturn":   [1, 4, 7, 8, 9, 10, 11],
        "from_Lagna":    [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "from_Sun":      [5, 6, 9, 11, 12],
        "from_Moon":     [2, 4, 6, 8, 10, 11],
        "from_Mars":     [1, 2, 4, 7, 8, 9, 10, 11],
        "from_Mercury":  [1, 3, 5, 6, 9, 10, 11, 12],
        "from_Jupiter":  [6, 8, 11, 12],
        "from_Venus":    [1, 2, 3, 4, 5, 8, 9, 11],
        "from_Saturn":   [1, 2, 4, 7, 8, 9, 10, 11],
        "from_Lagna":    [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "from_Sun":      [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "from_Moon":     [2, 5, 7, 9, 11],
        "from_Mars":     [1, 2, 4, 7, 8, 10, 11],
        "from_Mercury":  [1, 2, 4, 5, 6, 9, 10, 11],
        "from_Jupiter":  [1, 2, 3, 4, 5, 7, 8, 10, 11],
        "from_Venus":    [2, 5, 9, 10, 11, 12],
        "from_Saturn":   [3, 5, 6, 12],
        "from_Lagna":    [1, 2, 4, 5, 6, 9, 10, 11],
    },
    "Venus": {
        "from_Sun":      [8, 11, 12],
        "from_Moon":     [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "from_Mars":     [3, 5, 6, 9, 11, 12],
        "from_Mercury":  [3, 5, 6, 9, 11],
        "from_Jupiter":  [5, 8, 9, 10, 11],
        "from_Venus":    [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "from_Saturn":   [3, 4, 5, 8, 9, 10, 11],
        "from_Lagna":    [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "from_Sun":      [1, 2, 4, 7, 8, 10, 11],
        "from_Moon":     [3, 6, 11],
        "from_Mars":     [3, 5, 6, 10, 11, 12],
        "from_Mercury":  [6, 8, 9, 10, 11, 12],
        "from_Jupiter":  [5, 6, 11, 12],
        "from_Venus":    [6, 11, 12],
        "from_Saturn":   [3, 5, 6, 11],
        "from_Lagna":    [1, 3, 4, 6, 10, 11],
    },
}

# Expected total bindus per planet (for validation)
EXPECTED_BAV_TOTALS = {
    "Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
    "Jupiter": 56, "Venus": 52, "Saturn": 39
}

# Grand total for SAV validation
EXPECTED_SAV_TOTAL = 337

# ─── Benefic planets for Yogabindu calculation ───
BENEFIC_PLANETS = ["Jupiter", "Venus", "Mercury", "Moon"]

# ─── Yogarekha threshold ───
YOGAREKHA_THRESHOLD = 28  # Signs with SAV >= 28 have Yogarekha


def _to_sign_1based(sign_0based: int) -> int:
    """Convert 0-based sign index (0-11) to 1-based sign number (1-12)."""
    return sign_0based + 1


def _to_sign_0based(sign_1based: int) -> int:
    """Convert 1-based sign number (1-12) to 0-based index (0-11)."""
    return (sign_1based - 1) % 12


def _calculate_target_sign(ref_sign_1based: int, benefic_house: int) -> int:
    """
    Core formula: Target_Sign = ((Reference_Planet_Sign + Benefic_House - 1) % 12)
    Returns 1-based sign number (1-12). If result is 0, returns 12.
    """
    target = ((ref_sign_1based + benefic_house - 1) % 12)
    if target == 0:
        target = 12
    return target


def calculate_bav_for_planet(planet_key: str, planet_signs: dict, lagna_sign: int) -> list:
    """
    Calculate Bhinna Ashtakavarga (BAV) for a single planet.
    
    Args:
        planet_key: "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", or "Saturn"
        planet_signs: dict mapping planet_key -> 1-based sign number (1-12)
        lagna_sign: 1-based sign number for Ascendant (1-12)
    
    Returns:
        list of 12 integers (index 0 = Aries/1, index 11 = Pisces/12),
        each representing the number of bindus (points) in that sign.
    """
    refs = BAV_REFERENCES.get(planet_key)
    if not refs:
        return [0] * 12
    
    # Initialize 12-sign array (0-based index, 0=Aries/1 ... 11=Pisces/12)
    bav = [0] * 12
    
    # For each reference planet (and Lagna), distribute bindus
    for ref_key, benefic_houses in refs.items():
        if ref_key == "from_Lagna":
            ref_sign = lagna_sign
        else:
            # Extract planet name from "from_Sun" -> "Sun"
            source_planet = ref_key.replace("from_", "")
            ref_sign = planet_signs.get(source_planet)
            if ref_sign is None:
                continue  # Skip if planet position unknown
        
        # For each benefic house, calculate target sign and add a bindu
        for house in benefic_houses:
            target_sign = _calculate_target_sign(ref_sign, house)
            target_idx = _to_sign_0based(target_sign)
            bav[target_idx] += 1
    
    return bav


def calculate_all_bav(planet_signs: dict, lagna_sign: int) -> dict:
    """
    Calculate Bhinna Ashtakavarga for all 7 planets.
    
    Args:
        planet_signs: dict mapping planet_key (English) -> 1-based sign number (1-12)
        lagna_sign: 1-based sign number for Ascendant (1-12)
    
    Returns:
        dict: {
            "bav": { planet_key: [12 ints], ... },
            "bav_totals": { planet_key: total_bindus, ... },
            "planet_signs": { planet_key: sign_number, ... },
            "lagna_sign": lagna_sign
        }
    """
    all_bav = {}
    bav_totals = {}
    
    for planet in PLANET_KEYS:
        bav = calculate_bav_for_planet(planet, planet_signs, lagna_sign)
        all_bav[planet] = bav
        bav_totals[planet] = sum(bav)
    
    return {
        "bav": all_bav,
        "bav_totals": bav_totals,
        "planet_signs": planet_signs,
        "lagna_sign": lagna_sign
    }


def calculate_sav(all_bav: dict) -> dict:
    """
    Calculate Sarvashtakavarga (SAV) from all 7 BAVs.
    
    SAV_for_Sign_X = Sun_BAV[X] + Moon_BAV[X] + Mars_BAV[X] + 
                     Merc_BAV[X] + Jup_BAV[X] + Ven_BAV[X] + Sat_BAV[X]
    
    Args:
        all_bav: dict mapping planet_key -> [12 ints]
    
    Returns:
        dict: {
            "sav": [12 ints],
            "sav_total": int (must equal 337),
            "valid": bool
        }
    """
    sav = [0] * 12
    
    for planet in PLANET_KEYS:
        bav = all_bav.get(planet, [0] * 12)
        for i in range(12):
            sav[i] += bav[i]
    
    sav_total = sum(sav)
    valid = (sav_total == EXPECTED_SAV_TOTAL)
    
    return {
        "sav": sav,
        "sav_total": sav_total,
        "valid": valid
    }


def calculate_yogarekha(sav: list) -> list:
    """
    Calculate Yogarekha (যোগৰেখা) for each sign.
    
    A sign has Yogarekha if its SAV points >= 28 (threshold).
    Returns list of 12 booleans.
    """
    return [pts >= YOGAREKHA_THRESHOLD for pts in sav]


def calculate_yogabindu(all_bav: dict, sav: list) -> dict:
    """
    Calculate Yogabindu (যোগবিন্দু).
    
    Yogabindu = Sum of SAV points contributed ONLY by benefic planets
    (Jupiter, Venus, Mercury, Moon) across all 12 signs.
    
    Also calculates per-sign Yogabindu.
    
    Returns:
        dict with total_yogabindu and per_sign_yogabindu
    """
    per_sign = [0] * 12
    for planet in BENEFIC_PLANETS:
        bav = all_bav.get(planet, [0] * 12)
        for i in range(12):
            per_sign[i] += bav[i]
    
    total = sum(per_sign)
    
    return {
        "total_yogabindu": total,
        "per_sign_yogabindu": per_sign,
        "benefic_planets": BENEFIC_PLANETS
    }


def get_complete_ashtakavarga(planet_signs: dict, lagna_sign: int) -> dict:
    """
    Complete Ashtakavarga calculation: BAV, SAV, Yogarekha, Yogabindu.
    
    Args:
        planet_signs: dict mapping English planet name -> 1-based sign number (1-12)
        lagna_sign: 1-based Ascendant sign number (1-12)
    
    Returns:
        Complete dict with all calculations and validation.
    """
    # Step 1: Calculate all BAVs
    bav_data = calculate_all_bav(planet_signs, lagna_sign)
    
    # Step 2: Calculate SAV
    sav_data = calculate_sav(bav_data["bav"])
    
    # Step 3: Calculate Yogarekha
    yogarekha = calculate_yogarekha(sav_data["sav"])
    
    # Step 4: Calculate Yogabindu
    yogabindu = calculate_yogabindu(bav_data["bav"], sav_data["sav"])
    
    return {
        **bav_data,
        "sav": sav_data["sav"],
        "sav_total": sav_data["sav_total"],
        "sav_valid": sav_data["valid"],
        "yogarekha": yogarekha,
        "yogabindu": yogabindu,
    }


# ─── i18n Planet Name Mapping ──────────────────────────────────────

PLANET_NAMES_I18N = {
    'as': {
        'Sun': 'ৰবি', 'Moon': 'চন্দ্ৰ', 'Mars': 'মংগল', 'Mercury': 'বুধ',
        'Jupiter': 'বৃহস্পতি', 'Venus': 'শুক্ৰ', 'Saturn': 'শনি',
    },
    'bn': {
        'Sun': 'রবি', 'Moon': 'চন্দ্র', 'Mars': 'মঙ্গল', 'Mercury': 'বুধ',
        'Jupiter': 'বৃহস্পতি', 'Venus': 'শুক্র', 'Saturn': 'শনি',
    },
    'hi': {
        'Sun': 'रवि', 'Moon': 'चंद्र', 'Mars': 'मंगल', 'Mercury': 'बुध',
        'Jupiter': 'बृहस्पति', 'Venus': 'शुक्र', 'Saturn': 'शनि',
    },
    'en': {
        'Sun': 'Sun', 'Moon': 'Moon', 'Mars': 'Mars', 'Mercury': 'Mercury',
        'Jupiter': 'Jupiter', 'Venus': 'Venus', 'Saturn': 'Saturn',
    }
}

RASHI_NAMES_I18N = {
    'as': ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"],
    'bn': ["মেষ", "বৃষ", "মিথুন", "কর্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকর", "কুম্ভ", "মীন"],
    'hi': ["मेष", "वृष", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"],
    'en': ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
}


def generate_ashtakavarga_html(data: dict, lang: str = 'as') -> str:
    """
    Generate complete Ashtakavarga HTML report with BAV tables, SAV table,
    Yogarekha and Yogabindu.
    
    Args:
        data: Complete ashtakavarga data from get_complete_ashtakavarga()
        lang: Language code ('as', 'bn', 'hi', 'en')
    
    Returns:
        HTML string with styled tables and analysis.
    """
    from translations import get_text
    
    t = lambda k: get_text(k, lang)
    pnames = PLANET_NAMES_I18N.get(lang, PLANET_NAMES_I18N['en'])
    rnames = RASHI_NAMES_I18N.get(lang, RASHI_NAMES_I18N['en'])
    
    html_parts = []
    
    # ─── CSS Styles ───
    html_parts.append('''
    <style>
        .ashtak-container { font-family: 'Noto Sans Bengali', 'Nirmala UI', 'Kalpurush', sans-serif; }
        .ashtak-section { margin-bottom: 28px; }
        .ashtak-section h3 { color: #1a237e; font-size: 1.05rem; margin-bottom: 10px; 
            padding: 8px 14px; background: linear-gradient(135deg, #E8EAF6, #FFF8E1);
            border-radius: 8px; border-left: 4px solid #FF6600; }
        .ashtak-section h4 { color: #5B3E96; font-size: 0.95rem; margin: 8px 0 6px 0; }
        .ashtak-table-wrap { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
        .ashtak-table { width: 100%; min-width: 600px; border-collapse: collapse; font-size: 0.82rem;
            margin: 8px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-radius: 8px; overflow: hidden; }
        .ashtak-table th { background: #1a237e; color: white; padding: 7px 6px; text-align: center;
            font-weight: 700; font-size: 0.78rem; white-space: nowrap; }
        .ashtak-table td { padding: 6px 5px; text-align: center; border: 1px solid #e0e0e0; }
        .ashtak-table tr:nth-child(even) { background: #f5f5f5; }
        .ashtak-table tr:nth-child(odd) { background: #fff; }
        .ashtak-table .bindu-cell { font-weight: 700; color: #1a237e; }
        .ashtak-table .zero-cell { color: #bbb; }
        .ashtak-table .total-col { background: #FFF3E0; font-weight: 700; color: #FF6600; }
        .ashtak-table .total-row { background: #E8EAF6; font-weight: 700; }
        .ashtak-sav-table th { background: #FF6600; }
        .ashtak-sav-table .high-cell { background: #C8E6C9; font-weight: 700; color: #2E7D32; }
        .ashtak-sav-table .low-cell { background: #FFCDD2; font-weight: 700; color: #C62828; }
        .ashtak-sav-table .mid-cell { background: #FFF9C4; }
        .ashtak-summary { background: linear-gradient(135deg, #E8EAF6, #FFF8E1);
            padding: 16px 20px; border-radius: 12px; margin: 16px 0;
            border: 2px solid #FF6600; }
        .ashtak-summary h4 { color: #FF6600; margin: 0 0 10px 0; font-size: 1rem; }
        .ashtak-summary p { margin: 4px 0; font-size: 0.9rem; line-height: 1.6; }
        .ashtak-yogarekha { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }
        .ashtak-yogarekha-item { padding: 6px 12px; border-radius: 20px; font-size: 0.82rem;
            font-weight: 600; }
        .ashtak-yogarekha-yes { background: #C8E6C9; color: #2E7D32; border: 1px solid #4CAF50; }
        .ashtak-yogarekha-no { background: #f5f5f5; color: #999; border: 1px solid #ddd; }
        .ashtak-legend { font-size: 0.78rem; color: #666; margin: 8px 0; }
        .ashtak-valid { color: #2E7D32; font-weight: 700; }
        .ashtak-invalid { color: #C62828; font-weight: 700; }
        @media (max-width: 768px) {
            .ashtak-table { font-size: 0.68rem; min-width: 520px; }
            .ashtak-table th { font-size: 0.65rem; padding: 5px 3px; }
            .ashtak-table td { padding: 4px 3px; }
            .ashtak-section h3 { font-size: 0.9rem; }
            .ashtak-section h4 { font-size: 0.82rem; }
        }
    </style>
    ''')
    
    # ─── Main Container ───
    html_parts.append('<div class="ashtak-container">')
    
    # ─── Title ───
    html_parts.append(f'<h2 style="color:#FF6600;text-align:center;margin-bottom:4px;">{t("ashtakavarga_title")}</h2>')
    html_parts.append(f'<p style="text-align:center;color:#666;font-size:0.85rem;margin-bottom:20px;">{t("ashtakavarga_subtitle")}</p>')
    
    # ─── 1. Bhinna Ashtakavarga (BAV) Tables ───
    html_parts.append(f'<div class="ashtak-section"><h3>📊 {t("ashtak_bav_heading")}</h3>')
    
    for planet in PLANET_KEYS:
        bav = data["bav"].get(planet, [0]*12)
        total = sum(bav)
        expected = EXPECTED_BAV_TOTALS.get(planet, 0)
        pname = pnames.get(planet, planet)
        
        html_parts.append(f'<h4>🪐 {pname} — {t("ashtak_total_bindu")}: {total} ({t("ashtak_expected")}: {expected})</h4>')
        html_parts.append('<div class="ashtak-table-wrap"><table class="ashtak-table">')
        html_parts.append('<tr><th>#</th>')
        for i in range(12):
            html_parts.append(f'<th>{rnames[i]}</th>')
        html_parts.append('<th class="total-col">মুঠ</th></tr>')
        
        html_parts.append('<tr>')
        html_parts.append(f'<td style="font-weight:700;color:#FF6600;">{pname}</td>')
        for i in range(12):
            val = bav[i]
            cls = "bindu-cell" if val > 0 else "zero-cell"
            html_parts.append(f'<td class="{cls}">{val}</td>')
        html_parts.append(f'<td class="total-col">{total}</td>')
        html_parts.append('</tr>')
        html_parts.append('</table></div>')
    html_parts.append('</div>')  # end BAV section
    
    # ─── 2. Sarvashtakavarga (SAV) Table ───
    html_parts.append(f'<div class="ashtak-section"><h3>📊 {t("ashtak_sav_heading")}</h3>')
    
    sav = data["sav"]
    sav_total = data["sav_total"]
    valid = data["sav_valid"]
    yogarekha = data["yogarekha"]
    
    html_parts.append('<div class="ashtak-table-wrap"><table class="ashtak-table ashtak-sav-table">')
    html_parts.append('<tr><th>#</th>')
    for i in range(12):
        html_parts.append(f'<th>{rnames[i]}</th>')
    html_parts.append('<th class="total-col">মুঠ</th></tr>')
    
    # SAV row
    html_parts.append('<tr>')
    html_parts.append(f'<td style="font-weight:700;color:#FF6600;">{t("ashtak_sav_label")}</td>')
    for i in range(12):
        val = sav[i]
        if val >= 30:
            cls = "high-cell"
        elif val < 25:
            cls = "low-cell"
        else:
            cls = "mid-cell"
        html_parts.append(f'<td class="{cls}">{val}</td>')
    html_parts.append(f'<td class="total-col">{sav_total}</td>')
    html_parts.append('</tr>')
    
    # Yogarekha row
    html_parts.append('<tr>')
    html_parts.append(f'<td style="font-weight:700;color:#5B3E96;">{t("ashtak_yogarekha_label")}</td>')
    for i in range(12):
        if yogarekha[i]:
            html_parts.append(f'<td style="color:#2E7D32;font-weight:700;">✓ {t("ashtak_yes")}</td>')
        else:
            html_parts.append(f'<td style="color:#999;">✗ {t("ashtak_no")}</td>')
    html_parts.append('<td class="total-col"></td>')
    html_parts.append('</tr>')
    
    html_parts.append('</table>')
    
    # Validation
    valid_class = "ashtak-valid" if valid else "ashtak-invalid"
    valid_text = t("ashtak_sav_valid") if valid else t("ashtak_sav_invalid")
    html_parts.append(f'<p class="ashtak-legend">{t("ashtak_sav_validation")}: <span class="{valid_class}">{sav_total} / 337 — {valid_text}</span></p>')
    
    html_parts.append('</div>')  # end SAV section
    
    # ─── 3. Yogarekha (যোগৰেখা) ───
    html_parts.append(f'<div class="ashtak-section"><h3>✨ {t("ashtak_yogarekha_heading")}</h3>')
    html_parts.append(f'<p style="font-size:0.88rem;color:#555;">{t("ashtak_yogarekha_desc")}</p>')
    
    html_parts.append('<div class="ashtak-yogarekha">')
    yogarekha_count = 0
    for i in range(12):
        if yogarekha[i]:
            html_parts.append(f'<span class="ashtak-yogarekha-item ashtak-yogarekha-yes">✓ {rnames[i]} ({sav[i]})</span>')
            yogarekha_count += 1
        else:
            html_parts.append(f'<span class="ashtak-yogarekha-item ashtak-yogarekha-no">{rnames[i]} ({sav[i]})</span>')
    html_parts.append('</div>')
    
    html_parts.append(f'<p style="font-size:0.85rem;color:#1a237e;font-weight:600;">{t("ashtak_yogarekha_count")}: {yogarekha_count} / 12</p>')
    html_parts.append('</div>')
    
    # ─── 4. Yogabindu (যোগবিন্দু) ───
    html_parts.append(f'<div class="ashtak-section"><h3>💎 {t("ashtak_yogabindu_heading")}</h3>')
    html_parts.append(f'<p style="font-size:0.88rem;color:#555;">{t("ashtak_yogabindu_desc")}</p>')
    
    yb = data["yogabindu"]
    html_parts.append(f'<p style="font-size:0.9rem;"><strong>{t("ashtak_yogabindu_total")}:</strong> <span style="color:#FF6600;font-size:1.1rem;font-weight:700;">{yb["total_yogabindu"]}</span></p>')
    
    # Per-sign Yogabindu table
    html_parts.append('<div class="ashtak-table-wrap"><table class="ashtak-table">')
    html_parts.append('<tr><th>#</th>')
    for i in range(12):
        html_parts.append(f'<th>{rnames[i]}</th>')
    html_parts.append('<th class="total-col">মুঠ</th></tr>')
    
    html_parts.append('<tr>')
    html_parts.append(f'<td style="font-weight:700;color:#5B3E96;">{t("ashtak_yogabindu_label")}</td>')
    for i in range(12):
        val = yb["per_sign_yogabindu"][i]
        cls = "bindu-cell" if val > 0 else "zero-cell"
        html_parts.append(f'<td class="{cls}">{val}</td>')
    html_parts.append(f'<td class="total-col">{yb["total_yogabindu"]}</td>')
    html_parts.append('</tr>')
    html_parts.append('</table></div>')
    
    html_parts.append('</div>')
    
    # ─── 5. Summary ───
    html_parts.append(f'<div class="ashtak-summary"><h4>📋 {t("ashtak_summary_heading")}</h4>')
    
    # Count signs with Yogarekha
    yr_signs = [rnames[i] for i in range(12) if yogarekha[i]]
    yr_signs_str = ", ".join(yr_signs) if yr_signs else t("ashtak_none")
    
    html_parts.append(f'<p><strong>{t("ashtak_sav_total_label")}:</strong> {sav_total} / 337</p>')
    html_parts.append(f'<p><strong>{t("ashtak_yogarekha_signs")}:</strong> {yr_signs_str} ({yogarekha_count} {t("ashtak_signs")})</p>')
    html_parts.append(f'<p><strong>{t("ashtak_yogabindu_total")}:</strong> {yb["total_yogabindu"]}</p>')
    
    # Interpretation
    if yogarekha_count >= 5:
        strength = t("ashtak_strength_strong")
    elif yogarekha_count >= 3:
        strength = t("ashtak_strength_moderate")
    else:
        strength = t("ashtak_strength_weak")
    
    html_parts.append(f'<p><strong>{t("ashtak_overall_strength")}:</strong> {strength}</p>')
    html_parts.append('</div>')
    
    html_parts.append('</div>')  # end container
    
    return "\n".join(html_parts)


def generate_ashtakavarga_pdf_html(data: dict, lang: str = 'as') -> str:
    """
    Generate Ashtakavarga HTML optimized for PDF rendering.
    Same as generate_ashtakavarga_html but with PDF-friendly styling.
    """
    # Reuse the same HTML generator - it already uses inline styles compatible with PDF
    return generate_ashtakavarga_html(data, lang)
