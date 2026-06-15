"""ai_engine_i18n.py - Master 4-language AI text generation."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime
from ai_text_i18n import (
    GREETING, INTRO_BODY, SECTION_LAGNA, SECTION_PLANETS, SECTION_DOSHA_YOGA,
    SECTION_DASHA, SECTION_NAKSHATRA, SECTION_EXTRAS, SECTION_GEMSTONE,
    DOSHA_PRESENT, DOSHA_NONE, YOGA_PRESENT, NAKSHATRA_LINE, RASHI_LINE,
    TRIPAP_AGES, NAVATARA_DESC, SANNARI_DESC,
    GEMSTONE_TITLE, GEMSTONE_TITLE_5, GEMSTONE_TITLE_9, GEMSTONE_WORD, MANTRA_WORD,
    GEMSTONE_NOTE,
    SUMMARY_GOOD, SUMMARY_OK, SUMMARY_NONE, SUMMARY_DOSHA, SUMMARY_NO_DOSHA, SUMMARY_HEADER,
    DASHA_HEADER_MD, DASHA_HEADER_AD, DASHA_PERIOD,
)
from ai_text_i18n_extra import LAGNA_INTERPRETATIONS, LAGNA_SUMMARIES, DASHA_EFFECTS, ANTAR_EFFECTS
from ai_text_dasha_i18n import RASI_INTERPRETATIONS, GENERIC_PLANET_INTERPRETATION
from ai_i18n_helpers import get_planet_name, get_rashi_name, get_rashi_in_phrase


# ============== Helper functions ==============

def _planet_in_rashi_i18n(planet_as, rashi_as, lang):
    """Get interpretation for a planet in a rashi, in the target language."""
    planet_lang = get_planet_name(planet_as, lang)
    rashi_phrase = get_rashi_in_phrase(rashi_as, lang)
    # Check specific (exalted/debilitated/own sign) interpretations
    if (planet_as, rashi_as) in RASI_INTERPRETATIONS:
        template = RASI_INTERPRETATIONS[(planet_as, rashi_as)].get(lang, '')
        if template:
            return template.format(planet=planet_lang, rashi_phrase=rashi_phrase)
    # Fallback to generic interpretation
    template = GENERIC_PLANET_INTERPRETATION.get(lang, GENERIC_PLANET_INTERPRETATION['as']).get(planet_as, '')
    if template:
        return template.format(rashi_phrase=rashi_phrase)
    return ''


def _lagna_interpretation_i18n(asc_rasi, lang):
    """Get lagna interpretation in the target language."""
    return LAGNA_INTERPRETATIONS.get(lang, LAGNA_INTERPRETATIONS['as']).get(asc_rasi, '')


def _lagna_summary_i18n(asc_rasi, lang):
    """Get lagna summary in the target language."""
    return LAGNA_SUMMARIES.get(lang, LAGNA_SUMMARIES['as']).get(asc_rasi, '')


def _dasha_effect_i18n(planet_as, lang):
    """Get mahadasha effect for a planet in the target language."""
    return DASHA_EFFECTS.get(lang, DASHA_EFFECTS['as']).get(planet_as, '')


def _antar_effect_i18n(planet_as, lang):
    """Get antardasha effect for a planet in the target language."""
    return ANTAR_EFFECTS.get(lang, ANTAR_EFFECTS['as']).get(planet_as, '')


# ============== Main function ==============

def generate_ai_interpretation_i18n(
    user_name: str, planets_data: list, asc_rasi: str,
    dosha_results: list, yoga_results: list, dasa_data: list,
    lang: str = 'as',
    asc_rasi_idx: int = 0,
    planet_signs: dict = None,
    moon_nak_name: str = "",
    moon_rasi: str = "",
    tripap_ages: list = None,
    navatara_data: dict = None,
    sannari_data: dict = None,
) -> str:
    """Generate a compact AI-powered interpretation in the target language."""
    lines = []
    lines.append(GREETING.get(lang, GREETING['as']).format(name=user_name))
    lines.append("")
    lines.append(INTRO_BODY.get(lang, INTRO_BODY['as']))
    lines.append("")

    # ── ১। লগ্ন + লগ্নফল (merged) ──
    lines.append(SECTION_LAGNA.get(lang, SECTION_LAGNA['as']))
    lines.append(_lagna_interpretation_i18n(asc_rasi, lang))
    lines.append(_lagna_summary_i18n(asc_rasi, lang))
    lines.append("")

    # ── ২। গ্ৰহৰ অৱস্থান (compact - only key planets) ──
    lines.append(SECTION_PLANETS.get(lang, SECTION_PLANETS['as']))
    key_planets = ["ৰবি", "চন্দ্ৰ", "মংগল", "বুধ", "বৃহস্পতি", "শুক্ৰ", "শনি"]
    for p in planets_data:
        if p['name'] in key_planets:
            interp = _planet_in_rashi_i18n(p['name'], p['rasi'], lang)
            lines.append(f"• {interp}")
    rahu_ketu = [p for p in planets_data if p['name'] in ("ৰাহু", "কেতু")]
    if rahu_ketu:
        for p in rahu_ketu:
            interp = _planet_in_rashi_i18n(p['name'], p['rasi'], lang)
            lines.append(f"• {interp}")
    lines.append("")

    # ── ৩। দোষ + যোগ (merged) ──
    present_doshas = [d for d in dosha_results if d.get('present')]
    lines.append(SECTION_DOSHA_YOGA.get(lang, SECTION_DOSHA_YOGA['as']))
    if present_doshas:
        dosha_names = []
        for d in present_doshas:
            info = d.get('info', {})
            name = info.get('name', d.get('key', ''))
            severity = d.get('severity_text', '')
            dosha_names.append(f"{name} ({severity})")
        dosha_text = DOSHA_PRESENT.get(lang, DOSHA_PRESENT['as']).format(
            count=len(present_doshas), names=', '.join(dosha_names)
        )
        lines.append(dosha_text)
    else:
        lines.append(DOSHA_NONE.get(lang, DOSHA_NONE['as']))

    if yoga_results:
        yoga_names = [y.get('name', '') for y in yoga_results[:5]]
        yoga_text = YOGA_PRESENT.get(lang, YOGA_PRESENT['as']).format(
            count=len(yoga_results), names=', '.join(yoga_names)
        )
        lines.append(yoga_text)
    lines.append("")

    # ── ৪। দশা বিশ্লেষণ (compact) ──
    lines.append(SECTION_DASHA.get(lang, SECTION_DASHA['as']))
    lines.append(generate_dasha_interpretation_i18n(dasa_data, lang))
    lines.append("")

    # ── ৫। নক্ষত্ৰ + ৰাশি (merged) ──
    if moon_nak_name or moon_rasi:
        lines.append(SECTION_NAKSHATRA.get(lang, SECTION_NAKSHATRA['as']))
        if moon_nak_name:
            lines.append(NAKSHATRA_LINE.get(lang, NAKSHATRA_LINE['as']).format(name=moon_nak_name))
        if moon_rasi:
            lines.append(RASHI_LINE.get(lang, RASHI_LINE['as']).format(name=moon_rasi))
        lines.append("")

    # ── ৬। ত্ৰিপাপ ৰিষ্ট + নৱতাৰা + সন্নাড়ী (merged) ──
    extras = []
    if tripap_ages:
        ages_str = ', '.join(str(a) for a in tripap_ages)
        extras.append(TRIPAP_AGES.get(lang, TRIPAP_AGES['as']).format(ages=ages_str))
    if navatara_data:
        extras.append(NAVATARA_DESC.get(lang, NAVATARA_DESC['as']))
    if sannari_data:
        extras.append(SANNARI_DESC.get(lang, SANNARI_DESC['as']))
    if extras:
        lines.append(SECTION_EXTRAS.get(lang, SECTION_EXTRAS['as']))
        for e in extras:
            lines.append(f"• {e}")
        lines.append("")

    # ── ৭। ৰত্ন পৰামৰ্শ + বীজ মন্ত্ৰ + সাৰাংশ (merged) ──
    lines.append(SECTION_GEMSTONE.get(lang, SECTION_GEMSTONE['as']))
    if planet_signs:
        lines.append(generate_gemstone_recommendation_compact_i18n(asc_rasi_idx, planet_signs, lang))
    lines.append("")
    lines.append(f"{SUMMARY_HEADER.get(lang, SUMMARY_HEADER['as'])} {generate_overall_summary_i18n(planets_data, asc_rasi, len(present_doshas), len(yoga_results), lang)}")
    lines.append("")

    # Closing signature
    closing_text_map = {
        'as': "— ধ্ৰুৱতৰা AI, আপোনাৰ বিশ্বাসযোগ্য জ্যোতিষ সহায়ক",
        'bn': "— ধ্রুবতারা AI, আপনার বিশ্বস্ত জ্যোতিষ সহায়ক",
        'hi': "— ध्रुवतारा AI, आपका विश्वसनीय ज्योतिष सहायक",
        'en': "— Dhrubatara AI, your trusted astrology assistant",
    }
    lines.append(closing_text_map.get(lang, closing_text_map['as']))

    return '\n'.join(lines)


def generate_dasha_interpretation_i18n(dasa_data, lang='as'):
    """Generate interpretation for the CURRENTLY RUNNING dasha period."""
    if not dasa_data:
        return ""

    def parse_dasha_date(date_str):
        try:
            d, m, y = date_str.split('/')
            return datetime(int(y), int(m), int(d))
        except (ValueError, AttributeError):
            return datetime(1900, 1, 1)

    today = datetime.now()

    # Find the currently running mahadasha and antardasha
    current_md = None
    current_ad = None
    for md in dasa_data:
        md_end = parse_dasha_date(md.get('end', ''))
        md_start = parse_dasha_date(md.get('start', ''))
        if md_start <= today <= md_end:
            current_md = md
            for ad in md.get('sub_dasas', []):
                ad_end = parse_dasha_date(ad.get('end', ''))
                ad_start = parse_dasha_date(ad.get('start', ''))
                if ad_start <= today <= ad_end:
                    current_ad = ad
                    break
            break

    if current_md is None:
        current_md = dasa_data[0]
    if current_ad is None and current_md.get('sub_dasas'):
        current_ad = current_md['sub_dasas'][0]

    md_lord = current_md['md_lord']
    ad_lord = current_ad['ad_lord'] if current_ad else ''

    md_lang = get_planet_name(md_lord, lang)
    ad_lang = get_planet_name(ad_lord, lang) if ad_lord else ''

    md_effect = _dasha_effect_i18n(md_lord, lang)
    md_header = DASHA_HEADER_MD.get(lang, DASHA_HEADER_MD['as']).format(lord=md_lang)
    result = f"{md_header}\n\n{md_effect}"

    if ad_lord:
        ad_effect = _antar_effect_i18n(ad_lord, lang)
        ad_header = DASHA_HEADER_AD.get(lang, DASHA_HEADER_AD['as']).format(lord=ad_lang)
        result += f"\n\n{ad_header}\n\n{ad_effect}"
        if current_ad:
            period_text = DASHA_PERIOD.get(lang, DASHA_PERIOD['as']).format(
                start=current_ad.get('start', ''),
                end=current_ad.get('end', '')
            )
            result += f"\n\n{period_text}"

    return result


def generate_gemstone_recommendation_compact_i18n(asc_rasi_idx, planet_signs, lang='as'):
    """Compact gemstone + mantra recommendation in target language."""
    # RASHI_LORDS in target language (assamese, bengali, hindi, english)
    RASHI_LORDS_LANG = {
        'as': {
            0: "মংগল", 1: "শুক্ৰ", 2: "বুধ", 3: "চন্দ্ৰ",
            4: "ৰবি", 5: "বুধ", 6: "শুক্ৰ", 7: "মংগল",
            8: "বৃহস্পতি", 9: "শনি", 10: "শনি", 11: "বৃহস্পতি"
        },
        'bn': {
            0: "মঙ্গল", 1: "শুক্র", 2: "বুধ", 3: "চন্দ্র",
            4: "রবি", 5: "বুধ", 6: "শুক্র", 7: "মঙ্গল",
            8: "বৃহস্পতি", 9: "শনি", 10: "শনি", 11: "বৃহস্পতি"
        },
        'hi': {
            0: "मंगल", 1: "शुक्र", 2: "बुध", 3: "चंद्र",
            4: "सूर्य", 5: "बुध", 6: "शुक्र", 7: "मंगल",
            8: "बृहस्पति", 9: "शनि", 10: "शनि", 11: "बृहस्पति"
        },
        'en': {
            0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon",
            4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars",
            8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter"
        },
    }
    RASHI_LORDS_AS = RASHI_LORDS_LANG.get(lang, RASHI_LORDS_LANG['as'])

    # Map each language's planet name to its gemstone name + mantra
    # (Use local-language planet names as keys; the lookup is in the target language)
    GEMSTONES = {
        'as': {
            "ৰবি": "মাণিক্য (Ruby)", "চন্দ্ৰ": "মুকুটা (Pearl)",
            "মংগল": "ৰক্ত প্ৰবাল (Coral)", "বুধ": "পান্না (Emerald)",
            "বৃহস্পতি": "পোখৰাজ (Yellow Sapphire)", "শুক্ৰ": "হীৰা (Diamond)",
            "শনি": "নীলম (Blue Sapphire)", "ৰাহু": "গোমেধ (Hessonite)",
            "কেতু": "কেটচ্ আই (Cat's Eye)",
        },
        'bn': {
            "সূৰ্য": "মাণিক্য (Ruby)", "চন্দ্র": "মুকুটা (Pearl)",
            "মঙ্গল": "রক্ত প্রবাল (Coral)", "বুধ": "পান্না (Emerald)",
            "বৃহস্পতি": "পোখরাজ (Yellow Sapphire)", "শুক্র": "হীরা (Diamond)",
            "শনি": "নীলম (Blue Sapphire)", "রাহু": "গোমেধ (Hessonite)",
            "কেতু": "কেটস্ আই (Cat's Eye)",
        },
        'hi': {
            "सूर्य": "माणिक्य (Ruby)", "चंद्र": "मुक्ता (Pearl)",
            "मंगल": "रक्त प्रवाल (Coral)", "बुध": "पन्ना (Emerald)",
            "बृहस्पति": "पोखराज (Yellow Sapphire)", "शुक्र": "हीरा (Diamond)",
            "शनि": "नीलम (Blue Sapphire)", "राहु": "गोमेद (Hessonite)",
            "केतु": "कैट्स आई (Cat's Eye)",
        },
        'en': {
            "Sun": "Ruby", "Moon": "Pearl",
            "Mars": "Coral", "Mercury": "Emerald",
            "Jupiter": "Yellow Sapphire", "Venus": "Diamond",
            "Saturn": "Blue Sapphire", "Rahu": "Hessonite",
            "Ketu": "Cat's Eye",
        },
    }
    # Map planet in target language -> mantra
    BEEJA_MANTRAS = {
        'as': {
            "ৰবি": "ওঁ হ্ৰাং হ্ৰীং হ্ৰৌং সঃ সূৰ্যায় নমঃ",
            "চন্দ্ৰ": "ওঁ শ্ৰাং শ্ৰীং শ্ৰৌং সঃ চন্দ্ৰমসে নমঃ",
            "মংগল": "ওঁ ক্ৰাং ক্ৰীং ক্ৰৌং সঃ ভৌমায় নমঃ",
            "বুধ": "ওঁ ব্ৰাং ব্ৰীং ব্ৰৌং সঃ বুধায় নমঃ",
            "বৃহস্পতি": "ওঁ হ্ৰাং হ্ৰীং হ্ৰৌং সঃ বৃহস্পতয়ে নমঃ",
            "শুক্ৰ": "ওঁ দ্ৰাং দ্ৰীং দ্ৰৌং সঃ শুক্ৰায় নমঃ",
            "শনি": "ওঁ শ্ৰাং শ্ৰীং শ্ৰৌং সঃ শনৈশ্চৰায় নমঃ",
            "ৰাহু": "ওঁ ভ্ৰাং ভ্ৰীং ভ্ৰৌং সঃ ৰাহবে নমঃ",
            "কেতু": "ওঁ স্ত্ৰাং স্ত্ৰীং স্ত্ৰৌং সঃ কেতবে নমঃ",
        },
        'bn': {
            "সূৰ্য": "ওঁ হ্রাং হ্রীং হ্রৌং সঃ সূর্যায় নমঃ",
            "চন্দ্র": "ওঁ শ্রাং শ্রীং শ্রৌং সঃ চন্দ্রমসে নমঃ",
            "মঙ্গল": "ওঁ ক্রাং ক্রীং ক্রৌং সঃ ভৌমায় নমঃ",
            "বুধ": "ওঁ ব্রাং ব্রীং ব্রৌং সঃ বুধায় নমঃ",
            "বৃহস্পতি": "ওঁ হ্রাং হ্রীং হ্রৌং সঃ বৃহস্পতয়ে নমঃ",
            "শুক্র": "ওঁ দ্রাং দ্রীং দ্রৌং সঃ শুক্রায় নমঃ",
            "শনি": "ওঁ শ্রাং শ্রীং শ্রৌং সঃ শনৈশ্চরায় নমঃ",
            "রাহু": "ওঁ ভ্রাং ভ্রীং ভ্রৌং সঃ রাহবে নমঃ",
            "কেতু": "ওঁ স্ত্রাং স্ত্রীং স্ত্রৌং সঃ কেতবে নমঃ",
        },
        'hi': {
            "सूर्य": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः",
            "चंद्र": "ॐ श्रां श्रीं श्रौं सः चन्द्रमसे नमः",
            "मंगल": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः",
            "बुध": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः",
            "बृहस्पति": "ॐ ह्रां ह्रीं ह्रौं सः बृहस्पतये नमः",
            "शुक्र": "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः",
            "शनि": "ॐ श्रां श्रीं श्रौं सः शनैश्चराय नमः",
            "राहु": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः",
            "केतु": "ॐ स्त्रां स्त्रीं स्त्रौं सः केतवे नमः",
        },
        'en': {
            "Sun": "Om Hraam Hreem Hraum Sah Suryaya Namah",
            "Moon": "Om Shraam Shreem Shraum Sah Chandramase Namah",
            "Mars": "Om Kraam Kreem Kraum Sah Bhaumaya Namah",
            "Mercury": "Om Braam Breem Braum Sah Budhaya Namah",
            "Jupiter": "Om Hraam Hreem Hraum Sah Brihaspataye Namah",
            "Venus": "Om Draam Dreem Draum Sah Shukraya Namah",
            "Saturn": "Om Shraam Shreem Shraum Sah Shanaischaraya Namah",
            "Rahu": "Om Bhraam Bhreem Bhraum Sah Rahave Namah",
            "Ketu": "Om Straam Streem Straum Sah Ketave Namah",
        },
    }

    lagna_lord = RASHI_LORDS_AS.get(asc_rasi_idx, "")
    fifth_house_idx = (asc_rasi_idx + 4) % 12
    fifth_lord = RASHI_LORDS_AS.get(fifth_house_idx, "")
    ninth_house_idx = (asc_rasi_idx + 8) % 12
    ninth_lord = RASHI_LORDS_AS.get(ninth_house_idx, "")

    # Pick language-specific gemstone/mantra maps
    gem_map = GEMSTONES.get(lang, GEMSTONES['as'])
    mantra_map = BEEJA_MANTRAS.get(lang, BEEJA_MANTRAS['as'])

    lords = []
    if lagna_lord:
        lords.append(("lagna", lagna_lord, GEMSTONE_TITLE.get(lang, GEMSTONE_TITLE['as'])))
    if fifth_lord and fifth_lord != lagna_lord:
        lords.append(("fifth", fifth_lord, GEMSTONE_TITLE_5.get(lang, GEMSTONE_TITLE_5['as'])))
    if ninth_lord and ninth_lord not in [lagna_lord, fifth_lord]:
        lords.append(("ninth", ninth_lord, GEMSTONE_TITLE_9.get(lang, GEMSTONE_TITLE_9['as'])))

    gem_word = GEMSTONE_WORD.get(lang, GEMSTONE_WORD['as'])
    mantra_word = MANTRA_WORD.get(lang, MANTRA_WORD['as'])

    lines = []
    for which, lord, title_text in lords:
        gem = gem_map.get(lord, "")
        mantra = mantra_map.get(lord, "")
        # lord is already in the target language, so don't re-translate
        lord_lang = lord
        if gem:
            lines.append(f"• {title_text} {lord_lang}: {gem_word} — {gem}")
        if mantra:
            lines.append(f"  {mantra_word} — {mantra}")

    if lords:
        lines.append("")
        lines.append(GEMSTONE_NOTE.get(lang, GEMSTONE_NOTE['as']))

    return '\n'.join(lines)


def generate_overall_summary_i18n(planets_data, asc_rasi, dosha_count, yoga_count, lang='as'):
    """Generate an overall summary in the target language."""
    summaries = []
    if yoga_count >= 3:
        summaries.append(SUMMARY_GOOD.get(lang, SUMMARY_GOOD['as']))
    elif yoga_count >= 1:
        summaries.append(SUMMARY_OK.get(lang, SUMMARY_OK['as']))
    else:
        summaries.append(SUMMARY_NONE.get(lang, SUMMARY_NONE['as']))

    if dosha_count >= 3:
        summaries.append(SUMMARY_DOSHA.get(lang, SUMMARY_DOSHA['as']))
    elif dosha_count == 0:
        summaries.append(SUMMARY_NO_DOSHA.get(lang, SUMMARY_NO_DOSHA['as']))

    return ' '.join(summaries)


if __name__ == '__main__':
    # Test
    print("=== Test 4-language AI interpretation ===")
    sample_planets = [
        {'name': 'ৰবি', 'rasi': 'মেষ'},
        {'name': 'চন্দ্ৰ', 'rasi': 'বৃষ'},
    ]
    for lang in ('as', 'bn', 'hi', 'en'):
        print(f"\n--- {lang.upper()} ---")
        text = generate_ai_interpretation_i18n(
            user_name="Test User",
            planets_data=sample_planets,
            asc_rasi="মেষ",
            dosha_results=[],
            yoga_results=[],
            dasa_data=[],
            lang=lang,
            moon_nak_name="অশ্বিনী" if lang == 'as' else None,
        )
        print(text[:1500])
