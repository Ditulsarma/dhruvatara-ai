"""ai_i18n_helpers.py - Planet and Rashi name mapping + suffix helpers."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from translations import get_text


def _build_planet_map():
    """Build planet name mapping - each language uses its own script."""
    return {
        # ৰবি (as) -> রবি (bn) / सूर्य (hi) / Sun (en)
        "ৰবি": {"as": "ৰবি", "bn": "রবি", "hi": "सूर्य", "en": "Sun"},
        # চন্দ্ৰ (as) -> চন্দ্র (bn) / चंद्र (hi) / Moon (en)
        "চন্দ্ৰ": {"as": "চন্দ্ৰ", "bn": "চন্দ্র", "hi": "चंद्र", "en": "Moon"},
        # মংগল (as) -> মঙ্গল (bn) / मंगल (hi) / Mars (en)
        "মংগল": {"as": "মংগল", "bn": "মঙ্গল", "hi": "मंगल", "en": "Mars"},
        # বুধ (as) -> বুধ (bn) / बुध (hi) / Mercury (en)
        "বুধ": {"as": "বুধ", "bn": "বুধ", "hi": "बुध", "en": "Mercury"},
        # বৃহস্পতি (as) -> বৃহস্পতি (bn) / बृहस्पति (hi) / Jupiter (en)
        "বৃহস্পতি": {"as": "বৃহস্পতি", "bn": "বৃহস্পতি", "hi": "बृहस्पति", "en": "Jupiter"},
        # শুক্ৰ (as) -> শুক্র (bn) / शुक्र (hi) / Venus (en)
        "শুক্ৰ": {"as": "শুক্ৰ", "bn": "শুক্র", "hi": "शुक्र", "en": "Venus"},
        # শনি (as) -> শনি (bn) / शनि (hi) / Saturn (en)
        "শনি": {"as": "শনি", "bn": "শনি", "hi": "शनि", "en": "Saturn"},
        # ৰাহু (as) -> রাহু (bn) / राहु (hi) / Rahu (en)
        "ৰাহু": {"as": "ৰাহু", "bn": "রাহু", "hi": "राहु", "en": "Rahu"},
        # কেতু (as) -> কেতু (bn) / केतु (hi) / Ketu (en)
        "কেতু": {"as": "কেতু", "bn": "কেতু", "hi": "केतु", "en": "Ketu"},
    }


def _build_rashi_map():
    """Build rashi name mapping from translations. Uses 1-indexed rashi_N keys."""
    as_rashis = ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা",
                 "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"]
    return {
        as_name: {
            "as": as_name,
            "bn": get_text(f'rashi_{idx + 1}', 'bn'),
            "hi": get_text(f'rashi_{idx + 1}', 'hi'),
            "en": get_text(f'rashi_{idx + 1}', 'en'),
        }
        for idx, as_name in enumerate(as_rashis)
    }


PLANET_NAME_MAP = _build_planet_map()
RASHI_NAME_MAP = _build_rashi_map()


def get_planet_name(as_name, lang):
    """Get planet name in the target language."""
    return PLANET_NAME_MAP.get(as_name, {}).get(lang, as_name)


def get_rashi_name(as_name, lang):
    """Get rashi name in the target language."""
    return RASHI_NAME_MAP.get(as_name, {}).get(lang, as_name)


def get_rashi_in_phrase(as_name, lang):
    """Get the rashi reference in target language (e.g. 'in Aries' / 'মেষ ৰাশিত')."""
    rashi = get_rashi_name(as_name, lang)
    if lang == 'as':
        return f"{rashi} ৰাশিত"
    elif lang == 'bn':
        return f"{rashi} ৰাশিতে"
    elif lang == 'hi':
        return f"{rashi} राशि में"
    else:  # en
        return f"in {rashi}"
