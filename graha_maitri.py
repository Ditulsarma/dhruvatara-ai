"""
ধ্ৰুৱতৰা AI - Graha Maitri (Planetary Friendship) Engine
Calculates Naisargik (Natural), Tatkalin (Temporary), and Panchadha (Five-fold) Maitri.
Based on classical Vedic astrology principles.
"""

# Planet indexes (matching VB.NET constants)
SUN = 0
MOON = 1
MARS = 2
MERCURY = 3
JUPITER = 4
VENUS = 5
SATURN = 6
RAHU = 7
KETU = 8

# Planet names in Assamese (internal keys)
PLANET_NAMES_ASM = [
    "ৰবি", "চন্দ্ৰ", "মংগল", "বুধ", "বৃহস্পতি", "শুক্ৰ", "শনি", "ৰাহু", "কেতু"
]

# Planet names in English (for i18n lookup)
PLANET_NAMES_EN = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"
]

# Friendship type indices
MITRA = 0       # Friend
SHATRU = 1      # Enemy
SAM = 2         # Neutral
ADHIMITRA = 3   # Very good friend
ADHISHATRU = 4  # Bitter enemy

# Friendship type names in Assamese (internal keys)
FRIENDSHIP_TYPES_ASM = [
    "মিত্ৰ", "শত্ৰু", "সম", "অতিমিত্ৰ", "অতিশত্ৰু"
]

# Friendship type names in English (for i18n lookup)
FRIENDSHIP_TYPES_EN = [
    "Mitra", "Shatru", "Sam", "Adhimitra", "Adhishatru"
]

# ─── Natural Friendship Matrix (Naisargik Maitri) ───
# 0=Mitra, 1=Shatru, 2=Sam
# Row = planet, Column = planet it relates to
# Same as VB.NET naturalFriendship matrix
NATURAL_FRIENDSHIP = [
    # Sun  Moon Mars Merc Jup  Ven  Sat  Rah  Ket
    [2,    0,   0,   2,   0,   1,   1,   1,   1],  # Sun
    [0,    2,   2,   0,   2,   2,   2,   1,   1],  # Moon
    [0,    0,   2,   1,   0,   2,   2,   1,   0],  # Mars
    [0,    1,   2,   2,   2,   0,   2,   2,   2],  # Mercury
    [0,    0,   0,   1,   2,   1,   2,   2,   2],  # Jupiter
    [1,    1,   2,   0,   2,   2,   0,   0,   0],  # Venus
    [1,    1,   1,   0,   2,   0,   2,   0,   1],  # Saturn
    [1,    1,   1,   2,   0,   0,   0,   2,   1],  # Rahu
    [1,    1,   0,   2,   2,   0,   1,   1,   2],  # Ketu
]


def get_tatkalin_relation(house1: int, house2: int) -> int:
    """
    Calculate temporary (Tatkalin) friendship between two planets
    based on their house positions (1-12).
    
    Friendly houses from a planet: 2nd, 3rd, 4th, 10th, 11th, 12th
    (positions 2,3,4,10,11,12 counting from the planet's house)
    
    Returns: 0=Mitra, 1=Shatru
    """
    # Calculate position difference (circular, 1-12)
    position_diff = (house2 - house1 + 12) % 12
    
    if position_diff == 0:
        # Same house - considered Shatru (not friendly)
        return SHATRU
    elif position_diff in (1, 11):   # 12th and 2nd houses
        return MITRA
    elif position_diff in (2, 10):   # 11th and 3rd houses
        return MITRA
    elif position_diff in (3, 9):    # 10th and 4th houses
        return MITRA
    else:
        return SHATRU


def combine_relationships(natural_rel: int, temp_rel: int) -> int:
    """
    Combine natural and temporary relationships per Panchadha rules.
    
    natural_rel: 0=Mitra, 1=Shatru, 2=Sam
    temp_rel:    0=Mitra, 1=Shatru
    
    Returns: 0=Mitra, 1=Shatru, 2=Sam, 3=Adhimitra, 4=Adhishatru
    """
    if natural_rel == MITRA and temp_rel == MITRA:
        return ADHIMITRA   # Mitra + Mitra = Adhimitra
    if natural_rel == MITRA and temp_rel == SHATRU:
        return SAM          # Mitra + Shatru = Sam
    
    if natural_rel == SHATRU and temp_rel == MITRA:
        return SAM          # Shatru + Mitra = Sam
    if natural_rel == SHATRU and temp_rel == SHATRU:
        return ADHISHATRU   # Shatru + Shatru = Adhishatru
    
    if natural_rel == SAM and temp_rel == MITRA:
        return MITRA        # Sam + Mitra = Mitra
    if natural_rel == SAM and temp_rel == SHATRU:
        return SHATRU       # Sam + Shatru = Shatru
    
    return SAM  # Default


def calculate_naisargik_maitri() -> list:
    """
    Calculate Naisargik (Natural) Maitri matrix.
    Returns 9x9 list of lists with friendship type indices (0-2).
    Diagonal is -1 (self).
    """
    matrix = []
    for i in range(9):
        row = []
        for j in range(9):
            if i == j:
                row.append(-1)  # Self
            else:
                row.append(NATURAL_FRIENDSHIP[i][j])
        matrix.append(row)
    return matrix


def calculate_tatkalin_maitri(planet_houses: dict) -> list:
    """
    Calculate Tatkalin (Temporary) Maitri matrix.
    
    Args:
        planet_houses: dict mapping Assamese planet names to house numbers (1-12)
                       e.g. {"ৰবি": 5, "চন্দ্ৰ": 8, ...}
    
    Returns 9x9 list of lists with friendship type indices (0-1).
    Diagonal is -1 (self).
    """
    # Build house position array in planet index order
    houses = [1] * 9  # default
    for i, name in enumerate(PLANET_NAMES_ASM):
        if name in planet_houses:
            houses[i] = planet_houses[name]
    
    matrix = []
    for i in range(9):
        row = []
        for j in range(9):
            if i == j:
                row.append(-1)  # Self
            else:
                row.append(get_tatkalin_relation(houses[i], houses[j]))
        matrix.append(row)
    return matrix


def calculate_panchadha_maitri(planet_houses: dict) -> list:
    """
    Calculate Panchadha (Five-fold) Maitri matrix.
    Combines Naisargik + Tatkalin.
    
    Args:
        planet_houses: dict mapping Assamese planet names to house numbers (1-12)
    
    Returns 9x9 list of lists with friendship type indices (0-4).
    Diagonal is -1 (self).
    """
    natural = calculate_naisargik_maitri()
    tatkalin = calculate_tatkalin_maitri(planet_houses)
    
    matrix = []
    for i in range(9):
        row = []
        for j in range(9):
            if i == j:
                row.append(-1)  # Self
            else:
                row.append(combine_relationships(natural[i][j], tatkalin[i][j]))
        matrix.append(row)
    return matrix


def get_planet_names_i18n(lang: str = 'as') -> list:
    """
    Get planet names in the specified language.
    Uses the prediction_i18n module for consistent translations.
    """
    try:
        from prediction_i18n import get_panchanga_names_i18n
        pnames = get_panchanga_names_i18n(lang)
        planet_map = pnames.get('PLANET_NAMES', {})
        return [planet_map.get(en, en) for en in PLANET_NAMES_EN]
    except Exception:
        # Fallback: use Assamese names
        return PLANET_NAMES_ASM[:]


def get_friendship_types_i18n(lang: str = 'as') -> list:
    """
    Get friendship type names in the specified language.
    """
    from translations import get_text
    
    # Use translation keys for friendship types
    keys = ['maitri_mitra', 'maitri_shatru', 'maitri_sam', 
            'maitri_adhimitra', 'maitri_adhishatru']
    
    result = []
    for key in keys:
        result.append(get_text(key, lang))
    return result


def get_all_maitri_data(planet_houses: dict, lang: str = 'as') -> dict:
    """
    Get all three Maitri matrices with i18n labels.
    
    Args:
        planet_houses: dict mapping Assamese planet names to house numbers (1-12)
        lang: language code ('as', 'bn', 'hi', 'en')
    
    Returns:
        dict with:
        - planet_names: list of planet names in target language
        - friendship_types: list of friendship type names in target language
        - naisargik: 9x9 matrix of friendship indices
        - tatkalin: 9x9 matrix of friendship indices
        - panchadha: 9x9 matrix of friendship indices
        - planet_houses: list of house numbers for each planet
    """
    planet_names = get_planet_names_i18n(lang)
    friendship_types = get_friendship_types_i18n(lang)
    
    naisargik = calculate_naisargik_maitri()
    tatkalin = calculate_tatkalin_maitri(planet_houses)
    panchadha = calculate_panchadha_maitri(planet_houses)
    
    # Build house position array
    houses = [1] * 9
    for i, name in enumerate(PLANET_NAMES_ASM):
        if name in planet_houses:
            houses[i] = planet_houses[name]
    
    return {
        'planet_names': planet_names,
        'planet_names_asm': PLANET_NAMES_ASM,
        'friendship_types': friendship_types,
        'friendship_types_asm': FRIENDSHIP_TYPES_ASM,
        'naisargik': naisargik,
        'tatkalin': tatkalin,
        'panchadha': panchadha,
        'planet_houses': houses,
    }


def build_graha_maitri_pdf_html(planet_houses: dict, lang: str = 'as') -> str:
    """
    Build PDF-ready HTML for all three Graha Maitri charts.
    
    Args:
        planet_houses: dict mapping Assamese planet names to house numbers (1-12)
        lang: language code ('as', 'bn', 'hi', 'en')
    
    Returns:
        HTML string with all three charts styled for PDF rendering.
    """
    from translations import get_text
    
    data = get_all_maitri_data(planet_houses, lang)
    planet_names = data['planet_names']
    friendship_types = data['friendship_types']
    houses = data['planet_houses']
    
    t = lambda k: get_text(k, lang)
    
    # ── Helper: cell CSS class ──
    def _cell_class(val):
        if val == -1: return 'cell-self'
        if val == 0: return 'cell-mitra'
        if val == 1: return 'cell-shatru'
        if val == 2: return 'cell-sam'
        if val == 3: return 'cell-adhimitra'
        if val == 4: return 'cell-adhishatru'
        return ''
    
    def _swatch_color(val):
        if val == 0: return '#C8E6C9'
        if val == 1: return '#FFCDD2'
        if val == 2: return '#FFF9C4'
        if val == 3: return '#A5D6A7'
        if val == 4: return '#EF9A9A'
        return '#E0E0E0'
    
    # ── House position badges ──
    house_html = '<div class="maitri-pdf-house-row">'
    for i in range(9):
        house_html += f'<span class="maitri-pdf-house-badge">{planet_names[i]}: 🏠 {houses[i]}</span>'
    house_html += '</div>'
    
    # ── Build a single matrix table ──
    def _build_matrix(matrix, relevant_types):
        html = '<table class="maitri-pdf-table">'
        html += '<thead><tr><th></th>'
        for j in range(9):
            html += f'<th>{planet_names[j]}</th>'
        html += '</tr></thead><tbody>'
        
        for i in range(9):
            html += '<tr>'
            html += f'<td class="row-header">{planet_names[i]}</td>'
            for j in range(9):
                val = matrix[i][j]
                if val == -1:
                    html += '<td class="cell-self">—</td>'
                else:
                    cls = _cell_class(val)
                    label = friendship_types[val] if val < len(friendship_types) else '—'
                    html += f'<td class="{cls}">{label}</td>'
            html += '</tr>'
        html += '</tbody></table>'
        
        # Legend
        html += '<div class="maitri-pdf-legend">'
        for rt in relevant_types:
            if rt < len(friendship_types):
                html += f'<div class="maitri-pdf-legend-item"><span class="maitri-pdf-swatch" style="background:{_swatch_color(rt)};"></span> {friendship_types[rt]}</div>'
        html += '</div>'
        return html
    
    # ── Assemble all three sections ──
    result = house_html
    
    result += f'<h3 style="color:#1a237e;font-size:10pt;margin:12px 0 6px;">🌿 {t("maitri_naisargik")}</h3>'
    result += _build_matrix(data['naisargik'], [0, 1, 2])
    
    result += f'<h3 style="color:#1a237e;font-size:10pt;margin:16px 0 6px;">⏱️ {t("maitri_tatkalin")}</h3>'
    result += _build_matrix(data['tatkalin'], [0, 1])
    
    result += f'<h3 style="color:#1a237e;font-size:10pt;margin:16px 0 6px;">🌟 {t("maitri_panchadha")}</h3>'
    result += _build_matrix(data['panchadha'], [0, 1, 2, 3, 4])
    
    return result
