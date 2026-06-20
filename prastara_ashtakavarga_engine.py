"""
ধ্ৰুৱতৰা AI - Prastara Ashtakavarga (PAV) Engine
================================================
Generates the complete Prastara Ashtakavarga (PAV) 3D matrices for all 7 planets.

PAV is the detailed breakdown of Bhinna Ashtakavarga (BAV). While BAV shows the
total bindus per sign for each planet, PAV reveals exactly WHICH contributor
(kakshya lord) contributed each individual bindu.

Architecture:
  - 3D Matrix: Planet[7] × Sign[12] × KakshyaLord[8]
  - Each cell is 1 (Bindu / point) or 0 (Rekha / no point)
  - The 8 Kakshya Lords follow the standard astronomical distance order
    (farthest to nearest from Earth):
      1. Saturn    2. Jupiter    3. Mars      4. Sun
      5. Venus     6. Mercury    7. Moon      8. Lagna (Ascendant)

Kakshya Division:
  - Each sign (30°) is divided into 8 equal kakshyas of 3°45' (3.75°) each.
  - Kakshya index = floor(degree_within_sign / 3.75)

Based on classical Vedic Astrology (BPHS) Ashtakavarga principles.
Integrates seamlessly with the existing BAV/SAV engine (ashtakavarga_engine.py).
"""

import math
from typing import Dict, List, Tuple, Optional, Union

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# ─── Planet keys (internal English names) ───
PLANET_KEYS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# ─── Kakshya Lords in strict astronomical distance order (farthest → nearest) ───
# Index 0 = outermost (Saturn), Index 7 = innermost (Lagna/Ascendant)
# This is the INTERNAL computation order used for kakshya degree division.
KAKSHYA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Lagna"]

# ─── Display Order: Standard Vedic weekday sequence ───
# The UI must display columns in the traditional planetary weekday order:
#   Sun → Moon → Mars → Mercury → Jupiter → Venus → Saturn → Lagna
# This list maps display column index (0-7) → internal KAKSHYA_LORDS index.
# E.g., DISPLAY_ORDER[0] = 3 means display column 0 (Sun) pulls data from
# internal kakshya index 3 (which is "Sun" in KAKSHYA_LORDS).
DISPLAY_ORDER = [3, 6, 2, 5, 1, 4, 0, 7]
#                Sun Moon Mars Merc Jup Ven Sat Lagna
#                ↑   ↑    ↑    ↑    ↑   ↑   ↑   ↑
#                idx3 idx6 idx2 idx5 idx1 idx4 idx0 idx7  (in KAKSHYA_LORDS)

# ─── Display column lord names (weekday order) ───
DISPLAY_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"]

# ─── Mapping: Kakshya Lord → BAV reference key ───
# Each kakshya lord corresponds to a contributor in the BAV_REFERENCES dict.
# This is the bridge between PAV kakshyas and BAV benefic-house rules.
KAKSHYA_TO_REF_KEY = {
    "Saturn":   "from_Saturn",
    "Jupiter":  "from_Jupiter",
    "Mars":     "from_Mars",
    "Sun":      "from_Sun",
    "Venus":    "from_Venus",
    "Mercury":  "from_Mercury",
    "Moon":     "from_Moon",
    "Lagna":    "from_Lagna",
}

# ─── Kakshya degree span ───
# Standard: 30° / 8 = 3.75° = 3°45' per kakshya
KAKSHYA_SPAN_DEGREES = 3.75

# ─── Zodiac sign names (1-indexed: 1=Aries ... 12=Pisces) ───
ZODIAC_SIGNS = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
}

# ─── Bhinna Ashtakavarga (BAV) Benefic House Reference Arrays ──────────────────
# These are the classical 8-fold benefic point rules from BPHS.
# Format: { target_planet: { from_contributor: [list of benefic houses (1-12)] } }
# A benefic house means: when the contributor is in sign X, the target planet
# receives a bindu in the sign that is H houses away from X.
#
# These are the SAME rules used by ashtakavarga_engine.py for BAV calculation.
# PAV simply disaggregates the BAV total by showing each contributor's vote.

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

# Expected total bindus per planet (for cross-validation with BAV)
EXPECTED_BAV_TOTALS = {
    "Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
    "Jupiter": 56, "Venus": 52, "Saturn": 39
}

# ═══════════════════════════════════════════════════════════════════════════════
# CORE CALCULATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _to_sign_0based(sign_1based: int) -> int:
    """Convert 1-based sign number (1-12) to 0-based index (0-11)."""
    return (sign_1based - 1) % 12


def _to_sign_1based(sign_0based: int) -> int:
    """Convert 0-based sign index (0-11) to 1-based sign number (1-12)."""
    return sign_0based + 1


def _calculate_house_from(ref_sign_1based: int, target_sign_1based: int) -> int:
    """
    Calculate the house position of target_sign relative to ref_sign.

    Formula: House = ((Target_Sign - Reference_Sign + 12) % 12) + 1

    Args:
        ref_sign_1based: The reference/source sign (1-12).
        target_sign_1based: The target sign (1-12).

    Returns:
        House number (1-12) representing target_sign's position counted
        from ref_sign. E.g., if ref=Aries(1) and target=Taurus(2), returns 2.
    """
    house = ((target_sign_1based - ref_sign_1based + 12) % 12) + 1
    return house


def _is_bindu(target_planet: str, contributor_ref_key: str, house: int) -> int:
    """
    Determine if a contributor grants a bindu (1) or rekha (0) to the target
    planet at a given house position.

    Args:
        target_planet: The planet receiving the point (e.g., "Sun").
        contributor_ref_key: The contributor reference key (e.g., "from_Mars").
        house: The house position (1-12) from contributor to target sign.

    Returns:
        1 if bindu (benefic), 0 if rekha (not benefic).
    """
    refs = BAV_REFERENCES.get(target_planet)
    if not refs:
        return 0
    benefic_houses = refs.get(contributor_ref_key, [])
    return 1 if house in benefic_houses else 0


def _get_contributor_sign(contributor_ref_key: str, planet_signs: dict,
                          lagna_sign: int) -> Optional[int]:
    """
    Get the natal sign (1-12) of a contributor.

    Args:
        contributor_ref_key: e.g., "from_Saturn", "from_Lagna".
        planet_signs: dict mapping planet_key → 1-based sign number.
        lagna_sign: 1-based Lagna sign number.

    Returns:
        1-based sign number, or None if position unknown.
    """
    if contributor_ref_key == "from_Lagna":
        return lagna_sign
    planet_name = contributor_ref_key.replace("from_", "")
    return planet_signs.get(planet_name)


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def GetTransitKakshya(degree_within_sign: float) -> Dict[str, Union[int, str]]:
    """
    Calculate the active Kakshya for a planet at a given degree within a sign.

    Each sign (30°) is divided into 8 equal kakshyas of 3°45' (3.75°) each.
    Kakshya index = floor(degree_within_sign / 3.75).

    Args:
        degree_within_sign: The planet's exact degree position within its
            current sign (0.0 to 30.0). E.g., if a planet is at 15°30' in
            Aries, pass 15.5.

    Returns:
        dict with:
            - 'kakshya_index': 0-based index (0-7) of the active kakshya.
            - 'kakshya_lord':  Name of the ruling planet/Lagna for this kakshya.
            - 'kakshya_start': Starting degree of this kakshya within the sign.
            - 'kakshya_end':   Ending degree of this kakshya within the sign.
            - 'kakshya_span':  The degree span of one kakshya (3.75°).

    Example:
        >>> GetTransitKakshya(15.5)
        {'kakshya_index': 4, 'kakshya_lord': 'Venus', 'kakshya_start': 15.0,
         'kakshya_end': 18.75, 'kakshya_span': 3.75}

    Kakshya Lord Mapping (index → lord):
        0: Saturn    1: Jupiter    2: Mars      3: Sun
        4: Venus     5: Mercury    6: Moon      7: Lagna
    """
    # Clamp degree to valid range [0, 30)
    deg = degree_within_sign % 30.0

    # Calculate kakshya index: floor(degree / 3.75)
    kakshya_index = int(math.floor(deg / KAKSHYA_SPAN_DEGREES))

    # Edge case: if degree is exactly 30.0 (or very close), clamp to index 7
    if kakshya_index >= 8:
        kakshya_index = 7

    kakshya_lord = KAKSHYA_LORDS[kakshya_index]
    kakshya_start = kakshya_index * KAKSHYA_SPAN_DEGREES
    kakshya_end = kakshya_start + KAKSHYA_SPAN_DEGREES

    return {
        "kakshya_index": kakshya_index,
        "kakshya_lord": kakshya_lord,
        "kakshya_start": round(kakshya_start, 4),
        "kakshya_end": round(min(kakshya_end, 30.0), 4),
        "kakshya_span": KAKSHYA_SPAN_DEGREES,
    }


def GeneratePrastaraAshtakavarga(planet_signs: Dict[str, int],
                                 lagna_sign: int) -> Dict:
    """
    Generate the complete Prastara Ashtakavarga (PAV) 3D matrix for all
    7 planets.

    The PAV is a jagged 3D structure: Planet[7] × Sign[12] × KakshyaLord[8].
    Each cell is 1 (Bindu) or 0 (Rekha), indicating whether the kakshya lord
    (contributor) grants a point to the target planet in that sign.

    Args:
        planet_signs: dict mapping planet_key (English) → 1-based sign number.
            Example: {"Sun": 9, "Moon": 12, "Mars": 7, "Mercury": 9,
                      "Jupiter": 9, "Venus": 8, "Saturn": 7}
        lagna_sign: 1-based Ascendant (Lagna) sign number (1-12).

    Returns:
        A comprehensive dict with the following keys:
        - 'pav':  The full 3D PAV matrix.
                 Structure: {planet: [[1/0 × 8 kakshyas] × 12 signs]}
                 Access: pav['Sun'][sign_idx][kakshya_idx] → 1 or 0

        - 'pav_by_sign':  PAV transposed: {planet: [[1/0 × 12 signs] × 8 kakshyas]}
                 Access: pav_by_sign['Sun'][kakshya_idx][sign_idx] → 1 or 0

        - 'bav_from_pav':  BAV totals derived from PAV (for cross-validation).
                 {planet: [total_bindus × 12 signs]}

        - 'bav_totals':  {planet: total_bindus_across_all_signs}

        - 'kakshya_lords':  ["Saturn", "Jupiter", "Mars", "Sun", "Venus",
                             "Mercury", "Moon", "Lagna"]

        - 'kakshya_to_ref_key':  Mapping from kakshya lord to BAV ref key.

        - 'planet_signs':  The input planet positions.

        - 'lagna_sign':  The input Lagna sign.

        - 'validation':  Dict with validation results comparing PAV-derived
                         BAV against expected classical totals.

    Example Usage:
        >>> natal = {"Sun": 5, "Moon": 8, "Mars": 3, "Mercury": 4,
        ...          "Jupiter": 11, "Venus": 6, "Saturn": 2}
        >>> result = GeneratePrastaraAshtakavarga(natal, lagna_sign=1)
        >>> # Check if Saturn (kakshya 0) contributes to Sun in Aries (sign 0):
        >>> result['pav']['Sun'][0][0]  # → 1 or 0
    """
    # ─── Validate inputs ───
    for planet in PLANET_KEYS:
        if planet not in planet_signs:
            raise ValueError(f"Missing natal position for planet: {planet}")
        sign = planet_signs[planet]
        if not (1 <= sign <= 12):
            raise ValueError(f"Invalid sign {sign} for {planet}. Must be 1-12.")
    if not (1 <= lagna_sign <= 12):
        raise ValueError(f"Invalid Lagna sign {lagna_sign}. Must be 1-12.")

    # ─── Build the 3D PAV matrix ───
    # Structure: pav[planet][sign_idx][kakshya_idx] = 1 or 0
    #   - planet: one of PLANET_KEYS (7)
    #   - sign_idx: 0-11 (Aries=0 ... Pisces=11)
    #   - kakshya_idx: 0-7 (Saturn=0 ... Lagna=7)
    pav = {}

    # Alternative view: pav_by_sign[planet][kakshya_idx][sign_idx] = 1 or 0
    pav_by_sign = {}

    # Derived BAV totals (summing across kakshyas per sign)
    bav_from_pav = {}
    bav_totals = {}

    for target_planet in PLANET_KEYS:
        # Initialize: 12 signs × 8 kakshyas, all zeros
        planet_pav = [[0] * 8 for _ in range(12)]
        planet_pav_by_sign = [[0] * 12 for _ in range(8)]

        refs = BAV_REFERENCES.get(target_planet, {})

        # For each sign (0-11), for each kakshya lord (0-7)
        for sign_idx in range(12):
            target_sign_1based = _to_sign_1based(sign_idx)

            for kakshya_idx, kakshya_lord in enumerate(KAKSHYA_LORDS):
                ref_key = KAKSHYA_TO_REF_KEY[kakshya_lord]

                # Get the contributor's natal sign
                contributor_sign = _get_contributor_sign(
                    ref_key, planet_signs, lagna_sign
                )

                if contributor_sign is None:
                    # Contributor position unknown → rekha (0)
                    continue

                # Calculate house: target_sign from contributor's natal sign
                house = _calculate_house_from(contributor_sign, target_sign_1based)

                # Determine bindu (1) or rekha (0)
                bindu = _is_bindu(target_planet, ref_key, house)

                # Store in both views
                planet_pav[sign_idx][kakshya_idx] = bindu
                planet_pav_by_sign[kakshya_idx][sign_idx] = bindu

        pav[target_planet] = planet_pav
        pav_by_sign[target_planet] = planet_pav_by_sign

        # Derive BAV from PAV: sum across kakshyas for each sign
        derived_bav = [sum(planet_pav[s][k] for k in range(8)) for s in range(12)]
        bav_from_pav[target_planet] = derived_bav
        bav_totals[target_planet] = sum(derived_bav)

    # ─── Validation ───
    validation = {}
    for planet in PLANET_KEYS:
        expected = EXPECTED_BAV_TOTALS.get(planet, 0)
        actual = bav_totals[planet]
        validation[planet] = {
            "expected_total": expected,
            "pav_derived_total": actual,
            "match": actual == expected,
        }
    all_match = all(v["match"] for v in validation.values())
    validation["all_match"] = all_match

    # ─── Assemble result ───
    return {
        "pav": pav,
        "pav_by_sign": pav_by_sign,
        "bav_from_pav": bav_from_pav,
        "bav_totals": bav_totals,
        "kakshya_lords": KAKSHYA_LORDS,
        "kakshya_to_ref_key": KAKSHYA_TO_REF_KEY,
        "kakshya_span_degrees": KAKSHYA_SPAN_DEGREES,
        "planet_signs": planet_signs,
        "lagna_sign": lagna_sign,
        "validation": validation,
    }


def GetPAVTableForPlanet(pav_data: Dict, planet: str) -> Dict:
    """
    Extract a clean 2D table (Sign × KakshyaLord) for a single planet
    from the full PAV result. Ideal for rendering in data grids or tables.

    Args:
        pav_data: Full result dict from GeneratePrastaraAshtakavarga().
        planet: Planet key (e.g., "Sun", "Jupiter").

    Returns:
        dict with:
            - 'planet': The planet name.
            - 'headers': List of 8 kakshya lord names.
            - 'sign_names': List of 12 zodiac sign names.
            - 'rows': List of 12 rows, each row is a list of 8 ints (1/0).
            - 'row_totals': List of 12 ints (BAV per sign).
            - 'grand_total': Total bindus for this planet.
    """
    planet_pav = pav_data["pav"].get(planet)
    if not planet_pav:
        raise ValueError(f"Planet '{planet}' not found in PAV data.")

    rows = planet_pav  # 12 × 8 matrix
    row_totals = [sum(row) for row in rows]
    grand_total = sum(row_totals)

    return {
        "planet": planet,
        "headers": KAKSHYA_LORDS,
        "sign_names": [ZODIAC_SIGNS[i] for i in range(1, 13)],
        "rows": rows,
        "row_totals": row_totals,
        "grand_total": grand_total,
    }


def GetPAVTableByKakshya(pav_data: Dict, planet: str) -> Dict:
    """
    Extract a transposed 2D table (KakshyaLord × Sign) for a single planet.
    Useful for analyzing which signs each kakshya lord contributes to.

    Args:
        pav_data: Full result dict from GeneratePrastaraAshtakavarga().
        planet: Planet key (e.g., "Sun", "Jupiter").

    Returns:
        dict with:
            - 'planet': The planet name.
            - 'headers': List of 12 zodiac sign names.
            - 'kakshya_names': List of 8 kakshya lord names.
            - 'rows': List of 8 rows, each row is a list of 12 ints (1/0).
            - 'row_totals': List of 8 ints (total bindus contributed by each lord).
    """
    planet_pav_by_sign = pav_data["pav_by_sign"].get(planet)
    if not planet_pav_by_sign:
        raise ValueError(f"Planet '{planet}' not found in PAV data.")

    rows = planet_pav_by_sign  # 8 × 12 matrix
    row_totals = [sum(row) for row in rows]

    return {
        "planet": planet,
        "headers": [ZODIAC_SIGNS[i] for i in range(1, 13)],
        "kakshya_names": KAKSHYA_LORDS,
        "rows": rows,
        "row_totals": row_totals,
    }


def GetTransitKakshyaForLongitude(total_longitude: float) -> Dict:
    """
    Calculate the active Kakshya for a planet given its absolute longitude
    (0° to 360°). This is a convenience wrapper around GetTransitKakshya.

    Args:
        total_longitude: The planet's absolute longitude in degrees (0-360).
            E.g., a planet at 15°30' in Aries → 15.5.
            A planet at 15°30' in Taurus → 45.5.

    Returns:
        Same dict as GetTransitKakshya, plus:
            - 'sign_number': 1-based sign number (1-12).
            - 'sign_name': Name of the sign.
            - 'degree_in_sign': The degree within the sign (0-30).
            - 'absolute_longitude': The input longitude.
    """
    total_longitude = total_longitude % 360.0

    # Determine sign: 0-based sign index = floor(longitude / 30)
    sign_idx = int(math.floor(total_longitude / 30.0))
    if sign_idx >= 12:
        sign_idx = 11  # clamp for 360.0 edge case

    sign_number = sign_idx + 1
    sign_name = ZODIAC_SIGNS.get(sign_number, f"Sign{sign_number}")
    degree_in_sign = total_longitude - (sign_idx * 30.0)

    kakshya_info = GetTransitKakshya(degree_in_sign)

    return {
        **kakshya_info,
        "sign_number": sign_number,
        "sign_name": sign_name,
        "degree_in_sign": round(degree_in_sign, 4),
        "absolute_longitude": round(total_longitude, 4),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HTML RENDERING (for UI integration)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_pav_html(pav_data: Dict, lang: str = 'en') -> str:
    """
    Generate a complete HTML report for the Prastara Ashtakavarga.

    Produces a styled, responsive HTML page with:
    - One PAV table per planet (Signs × Kakshya Lords).
    - Bindu (1) cells highlighted, Rekha (0) cells dimmed.
    - Row totals (BAV per sign) and column totals (contributions per lord).
    - Validation summary.

    Args:
        pav_data: Full result dict from GeneratePrastaraAshtakavarga().
        lang: Language code ('as', 'bn', 'hi', 'en').

    Returns:
        HTML string.
    """
    # ─── i18n planet and sign names ───
    PLANET_NAMES_I18N = {
        'as': {'Sun': 'ৰবি', 'Moon': 'চন্দ্ৰ', 'Mars': 'মংগল', 'Mercury': 'বুধ',
               'Jupiter': 'বৃহস্পতি', 'Venus': 'শুক্ৰ', 'Saturn': 'শনি', 'Lagna': 'লগ্ন'},
        'bn': {'Sun': 'রবি', 'Moon': 'চন্দ্র', 'Mars': 'মঙ্গল', 'Mercury': 'বুধ',
               'Jupiter': 'বৃহস্পতি', 'Venus': 'শুক্র', 'Saturn': 'শনি', 'Lagna': 'লগ্ন'},
        'hi': {'Sun': 'रवि', 'Moon': 'चंद्र', 'Mars': 'मंगल', 'Mercury': 'बुध',
               'Jupiter': 'बृहस्पति', 'Venus': 'शुक्र', 'Saturn': 'शनि', 'Lagna': 'लग्न'},
        'en': {'Sun': 'Sun', 'Moon': 'Moon', 'Mars': 'Mars', 'Mercury': 'Mercury',
               'Jupiter': 'Jupiter', 'Venus': 'Venus', 'Saturn': 'Saturn', 'Lagna': 'Lagna'},
    }
    RASHI_NAMES_I18N = {
        'as': ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"],
        'bn': ["মেষ", "বৃষ", "মিথুন", "কর্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকর", "কুম্ভ", "মীন"],
        'hi': ["मेष", "वृष", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"],
        'en': ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
    }

    pnames = PLANET_NAMES_I18N.get(lang, PLANET_NAMES_I18N['en'])
    rnames = RASHI_NAMES_I18N.get(lang, RASHI_NAMES_I18N['en'])

    html_parts = []

    # ─── CSS ───
    html_parts.append('''
    <style>
        /* ─── PAV Container ─── */
        .pav-container {
            font-family: 'Inter', 'Segoe UI', 'Noto Sans Bengali', 'Nirmala UI', 'Kalpurush', system-ui, sans-serif;
            color: #1F2937;
        }

        /* ─── Section Card ─── */
        .pav-section {
            margin-bottom: 28px;
            background: #FFFFFF;
            border-radius: 14px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
            overflow: hidden;
            border: 1px solid #E5E7EB;
        }
        .pav-section-header {
            padding: 14px 20px;
            background: linear-gradient(135deg, #F8FAFC, #F0F4FF);
            border-bottom: 1px solid #E5E7EB;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .pav-section-header .planet-icon {
            font-size: 1.3rem;
        }
        .pav-section-header h3 {
            margin: 0;
            color: #1E293B;
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: -0.01em;
        }
        .pav-section-header .bindu-badge {
            margin-left: auto;
            background: #EEF2FF;
            color: #4338CA;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 700;
        }

        /* ─── PAV Table ─── */
        .pav-table-wrap { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
        .pav-table {
            width: 100%;
            min-width: 620px;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 0.82rem;
            table-layout: fixed;
        }
        /* Column width distribution: Rashi ~14%, each Kakshya ~9%, Total ~8% */
        .pav-table col.col-rashi      { width: 14%; }
        .pav-table col.col-kakshya    { width: 9%; }
        .pav-table col.col-total      { width: 8%; }

        /* ─── THEAD: Kakshya Lord Headers ─── */
        .pav-table thead th {
            background: #1E293B;
            color: #FFFFFF;
            padding: 12px 8px;
            text-align: center;
            font-weight: 600;
            font-size: 0.75rem;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            border-bottom: 2px solid #0F172A;
            white-space: nowrap;
        }
        .pav-table thead th:first-child {
            border-radius: 0;
            background: #0F172A;
            font-weight: 700;
            font-size: 0.78rem;
        }
        .pav-table thead th:last-child {
            background: #312E81;
            font-weight: 700;
        }

        /* ─── TBODY: Data Cells ─── */
        .pav-table tbody td {
            padding: 12px 8px;
            text-align: center;
            border-bottom: 1px solid #F1F5F9;
            background: #FFFFFF;
            transition: background 0.15s ease;
        }
        .pav-table tbody tr:hover td {
            background: #F8FAFC;
        }

        /* Row Header (Zodiac Sign) */
        .pav-table tbody td.rashi-label {
            font-weight: 700;
            color: #1E293B;
            background: #F8FAFC;
            border-right: 2px solid #E2E8F0;
            text-align: left;
            padding-left: 16px;
            font-size: 0.84rem;
            letter-spacing: 0.01em;
        }
        .pav-table tbody tr:hover td.rashi-label {
            background: #F1F5F9;
        }

        /* Bindu Cell (Active Point) */
        .pav-table tbody td.bindu-cell {
            background: #D1FAE5;
            position: relative;
        }
        .pav-table tbody td.bindu-cell::after {
            content: '';
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #059669;
            border-radius: 50%;
            box-shadow: 0 0 0 2px rgba(5,150,105,0.15);
        }
        .pav-table tbody tr:hover td.bindu-cell {
            background: #A7F3D0;
        }

        /* Rekha Cell (Empty) */
        .pav-table tbody td.rekha-cell {
            color: #CBD5E1;
            background: #F9FAFB;
        }
        .pav-table tbody td.rekha-cell::after {
            content: '·';
            color: #CBD5E1;
            font-size: 1rem;
        }
        .pav-table tbody tr:hover td.rekha-cell {
            background: #F1F5F9;
        }

        /* Row Total Cell */
        .pav-table tbody td.row-total {
            font-weight: 700;
            color: #1E40AF;
            background: #EEF2FF;
            border-left: 2px solid #C7D2FE;
            font-size: 0.88rem;
        }
        .pav-table tbody tr:hover td.row-total {
            background: #E0E7FF;
        }

        /* ─── TFOOT: Summary Rows ─── */
        .pav-table tfoot td {
            padding: 12px 8px;
            text-align: center;
            font-weight: 700;
            font-size: 0.82rem;
            border-top: 2px solid #E2E8F0;
        }
        /* Kakshya Lord name labels */
        .pav-table tfoot td.lord-label {
            background: #F1F5F9;
            color: #475569;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        /* Σ Lord row */
        .pav-table tfoot tr.sigma-lord td {
            background: #FFF7ED;
            color: #C2410C;
            font-size: 0.85rem;
        }
        .pav-table tfoot tr.sigma-lord td:first-child {
            background: #FFF7ED;
            color: #9A3412;
            font-weight: 700;
            text-align: left;
            padding-left: 16px;
        }
        .pav-table tfoot tr.sigma-lord td:last-child {
            background: #FFEDD5;
            color: #9A3412;
            font-size: 0.92rem;
            font-weight: 800;
        }

        /* ─── Validation Card ─── */
        .pav-validation {
            background: #FFFFFF;
            padding: 18px 22px;
            border-radius: 14px;
            margin: 18px 0;
            border: 1px solid #E5E7EB;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .pav-validation h4 {
            color: #4338CA;
            margin: 0 0 12px 0;
            font-size: 0.9rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .pav-validation .val-row {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 4px 0;
            font-size: 0.82rem;
        }
        .pav-validation .val-planet {
            font-weight: 600;
            color: #1E293B;
            min-width: 80px;
        }
        .pav-validation .val-eq {
            color: #64748B;
            font-size: 0.78rem;
        }
        .pav-valid {
            color: #059669;
            font-weight: 700;
            background: #D1FAE5;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.72rem;
        }
        .pav-invalid {
            color: #DC2626;
            font-weight: 700;
            background: #FEE2E2;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.72rem;
        }
        .pav-validation .val-all {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #E5E7EB;
            font-weight: 700;
            font-size: 0.85rem;
        }

        /* ─── Responsive ─── */
        @media (max-width: 768px) {
            .pav-table { font-size: 0.68rem; min-width: 520px; }
            .pav-table thead th,
            .pav-table tbody td,
            .pav-table tfoot td { padding: 6px 3px; }
            .pav-table thead th { font-size: 0.62rem; }
            .pav-table tbody td.rashi-label { padding-left: 6px; font-size: 0.7rem; }
            .pav-table tbody td.bindu-cell::after { width: 7px; height: 7px; }
            .pav-section-header { padding: 10px 14px; }
            .pav-section-header h3 { font-size: 0.85rem; }
            .pav-section-header .bindu-badge { font-size: 0.7rem; padding: 3px 8px; }
        }
    </style>
    ''')

    html_parts.append('<div class="pav-container">')

    # ─── Title ───
    html_parts.append('<h2 style="color:#1E293B;text-align:center;margin-bottom:2px;font-weight:800;font-size:1.15rem;letter-spacing:-0.02em;">'
                      '📋 Prastara Ashtakavarga</h2>')
    html_parts.append('<p style="text-align:center;color:#64748B;font-size:0.82rem;margin-bottom:22px;">'
                      '8-Fold Kakshya Breakdown — Bindu (●) / Rekha (·)</p>')

    # ─── PAV Tables for each planet ───
    for planet in PLANET_KEYS:
        table_data = GetPAVTableForPlanet(pav_data, planet)
        by_kakshya = GetPAVTableByKakshya(pav_data, planet)
        pname = pnames.get(planet, planet)

        # Section card
        html_parts.append('<div class="pav-section">')

        # Section header
        html_parts.append('<div class="pav-section-header">')
        html_parts.append(f'<span class="planet-icon">🪐</span>')
        html_parts.append(f'<h3>{pname}</h3>')
        html_parts.append(f'<span class="bindu-badge">{table_data["grand_total"]} Bindus</span>')
        html_parts.append('</div>')

        # ─── TABLE: Weekday-order column structure ───
        # Columns: Rashi | Sun | Moon | Mars | Mercury | Jupiter | Venus | Saturn | Lagna | Σ
        html_parts.append('<div class="pav-table-wrap"><table class="pav-table">')

        # Colgroup for proportional widths
        html_parts.append('<colgroup>')
        html_parts.append('<col class="col-rashi">')
        for _ in range(8):
            html_parts.append('<col class="col-kakshya">')
        html_parts.append('<col class="col-total">')
        html_parts.append('</colgroup>')

        # ─── THEAD: Column headers in weekday order ───
        html_parts.append('<thead><tr>')
        html_parts.append('<th>Rashi</th>')
        for lord_name_en in DISPLAY_LORDS:
            lord_name = pnames.get(lord_name_en, lord_name_en)
            html_parts.append(f'<th>{lord_name}</th>')
        html_parts.append('<th>মুঠ</th>')
        html_parts.append('</tr></thead>')

        # ─── TBODY: 12 data rows (one per zodiac sign) ───
        # Data is stored internally in KAKSHYA_LORDS order (Saturn=0...Lagna=7).
        # DISPLAY_ORDER maps display column → internal kakshya index.
        html_parts.append('<tbody>')
        for sign_idx in range(12):
            html_parts.append('<tr>')
            # Row header: zodiac sign name
            html_parts.append(f'<td class="rashi-label">{rnames[sign_idx]}</td>')
            # 8 kakshya cells in weekday display order
            for display_col in range(8):
                internal_idx = DISPLAY_ORDER[display_col]
                val = table_data["rows"][sign_idx][internal_idx]
                if val == 1:
                    html_parts.append('<td class="bindu-cell"></td>')
                else:
                    html_parts.append('<td class="rekha-cell"></td>')
            # Row total (unchanged — sum is order-independent)
            html_parts.append(f'<td class="row-total">{table_data["row_totals"][sign_idx]}</td>')
            html_parts.append('</tr>')
        html_parts.append('</tbody>')

        # ─── TFOOT: Lord labels + Σ Lord totals (weekday order) ───
        html_parts.append('<tfoot>')
        # Row 1: Kakshya lord name labels
        html_parts.append('<tr>')
        html_parts.append('<td class="lord-label">Kakshya Lord</td>')
        for lord_name_en in DISPLAY_LORDS:
            lord_name = pnames.get(lord_name_en, lord_name_en)
            html_parts.append(f'<td class="lord-label">{lord_name}</td>')
        html_parts.append('<td class="lord-label"></td>')
        html_parts.append('</tr>')
        # Row 2: Σ Lord — total bindus contributed by each lord (remapped)
        html_parts.append('<tr class="sigma-lord">')
        html_parts.append('<td>মুঠ</td>')
        for display_col in range(8):
            internal_idx = DISPLAY_ORDER[display_col]
            html_parts.append(f'<td>{by_kakshya["row_totals"][internal_idx]}</td>')
        html_parts.append(f'<td>{table_data["grand_total"]}</td>')
        html_parts.append('</tr>')
        html_parts.append('</tfoot>')

        html_parts.append('</table></div>')
        html_parts.append('</div>')  # end pav-section

    html_parts.append('</div>')  # end container

    return "\n".join(html_parts)


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION BRIDGE: Use PAV alongside existing BAV/SAV engine
# ═══════════════════════════════════════════════════════════════════════════════

def GenerateCompleteAshtakavargaWithPAV(planet_signs: Dict[str, int],
                                        lagna_sign: int) -> Dict:
    """
    Generate the complete Ashtakavarga package including BAV, SAV, and PAV.

    This is the one-stop function that produces everything needed for a full
    Ashtakavarga report. It calls the existing BAV/SAV engine AND the new
    PAV engine, cross-validates them, and returns a unified result.

    Args:
        planet_signs: dict mapping planet_key → 1-based sign number.
        lagna_sign: 1-based Lagna sign number.

    Returns:
        Unified dict with BAV, SAV, PAV, and cross-validation.
    """
    # Import the existing engine (lazy import to avoid circular deps)
    from ashtakavarga_engine import get_complete_ashtakavarga

    # Get BAV + SAV from existing engine
    bav_sav_data = get_complete_ashtakavarga(planet_signs, lagna_sign)

    # Get PAV from this engine
    pav_data = GeneratePrastaraAshtakavarga(planet_signs, lagna_sign)

    # Cross-validate: PAV-derived BAV should match existing BAV
    cross_check = {}
    for planet in PLANET_KEYS:
        bav_from_existing = bav_sav_data["bav"].get(planet, [0]*12)
        bav_from_pav = pav_data["bav_from_pav"].get(planet, [0]*12)
        cross_check[planet] = {
            "bav_existing": bav_from_existing,
            "bav_from_pav": bav_from_pav,
            "match": bav_from_existing == bav_from_pav,
        }
    all_cross_match = all(v["match"] for v in cross_check.values())

    return {
        **bav_sav_data,
        "pav": pav_data["pav"],
        "pav_by_sign": pav_data["pav_by_sign"],
        "kakshya_lords": KAKSHYA_LORDS,
        "kakshya_span_degrees": KAKSHYA_SPAN_DEGREES,
        "pav_validation": pav_data["validation"],
        "cross_validation": cross_check,
        "all_cross_match": all_cross_match,
    }
