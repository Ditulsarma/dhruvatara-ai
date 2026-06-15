"""
Helper to localize dasha hierarchy planet names.
Replaces Assamese planet names with the current language's translation
for Maha Dasha, Antardasha, and Pratyantardasha.
"""

from prediction_i18n import get_planet_name_i18n, PLANET_NAMES_I18N


# Mapping of Assamese planet name -> English (for fallback conversion)
_ASM_TO_ENG = {k: v.get('en', k) for k, v in PLANET_NAMES_I18N.items()}


def localize_dasha_hierarchy(dasa_hierarchy, lang='as'):
    """
    Walk a dasha hierarchy (from get_full_dasa_hierarchy) and add
    *_display fields for the planet names in the target language.
    Falls back to the existing *_en / default fields if translation is missing.
    """
    if not dasa_hierarchy:
        return dasa_hierarchy

    for md in dasa_hierarchy:
        # Get base English name (data attribute), then localize for display
        md_eng = md.get('md_lord_en') or _to_eng(md.get('md_lord', ''))
        md['md_lord_display'] = get_planet_name_i18n(md_eng, lang)
        md['md_lord_i18n'] = get_planet_name_i18n(md_eng, lang)  # alias

        for ad in md.get('sub_dasas', []):
            ad_eng = ad.get('ad_lord_en') or _to_eng(ad.get('ad_lord', ''))
            ad['ad_lord_display'] = get_planet_name_i18n(ad_eng, lang)
            ad['ad_lord_i18n'] = get_planet_name_i18n(ad_eng, lang)

            for pd in ad.get('pratyantar', []):
                pd_eng = pd.get('lord_en') or _to_eng(pd.get('lord', ''))
                pd['lord_display'] = get_planet_name_i18n(pd_eng, lang)
                pd['lord_i18n'] = get_planet_name_i18n(pd_eng, lang)

    return dasa_hierarchy


def _to_eng(name):
    """Convert Assamese planet name to English (best-effort)."""
    if not name:
        return ''
    return _ASM_TO_ENG.get(name, name)
