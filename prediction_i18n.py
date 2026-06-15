"""


ধ্ৰুৱতৰা AI - Prediction i18n Wrapper


Multi-language support for all prediction engines.


Wraps existing Assamese engines and provides language-aware versions.


"""





import os


import re


import json


from translations import get_text, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE




# ─── Digit conversion utilities ───
# Assamese and Bengali use the same Eastern Nagari digit set (0-9)
ASSAMESE_BENGALI_DIGITS = {
    '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
    '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9',
}
# Devanagari digits used in Hindi (similar shape but different code points)
HINDI_DIGITS = {
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
    '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
}


def localize_number_to_english(text):
    """Convert Assamese/Bengali and Hindi digits in a string to English (0-9) digits."""
    if not isinstance(text, str):
        return text
    for digit, english in {**ASSAMESE_BENGALI_DIGITS, **HINDI_DIGITS}.items():
        text = text.replace(digit, english)
    return text


def convert_tripap_data_to_lang(data, lang):
    """Convert the TRIPAP_DATA values to the target language's digit format.

    For 'as' and 'bn': keep Assamese/Bengali digits (default behavior).
    For 'hi' and 'en': convert to English digits (0-9).
    """
    if lang in ('hi', 'en'):
        if isinstance(data, list):
            return [localize_number_to_english(v) if isinstance(v, str) else v for v in data]
        if isinstance(data, dict):
            return {k: convert_tripap_data_to_lang(v, lang) for k, v in data.items()}
    return data




# ─── Language-specific data file paths ───


_DATA_DIR = os.path.dirname(os.path.abspath(__file__))





# Planet name mappings for dasha engine (must be defined before _convert_planet_to_lang)


PLANET_NAMES_I18N = {


    'as': {


        'Sun': 'ৰবি', 'Moon': 'চন্দ্ৰ', 'Mars': 'মংগল', 'Mercury': 'বুধ',


        'Jupiter': 'বৃহস্পতি', 'Venus': 'শুক্ৰ', 'Saturn': 'শনি',


        'Rahu': 'ৰাহু', 'Ketu': 'কেতু',


    },


    'bn': {


        'Sun': 'রবি', 'Moon': 'চন্দ্র', 'Mars': 'মঙ্গল', 'Mercury': 'বুধ',


        'Jupiter': 'বৃহস্পতি', 'Venus': 'শুক্র', 'Saturn': 'শনি',


        'Rahu': 'রাহু', 'Ketu': 'কেতু',


    },


    'hi': {


        'Sun': 'रवि', 'Moon': 'चंद्र', 'Mars': 'मंगल', 'Mercury': 'बुध',


        'Jupiter': 'बृहस्पति', 'Venus': 'शुक्र', 'Saturn': 'शनि',


        'Rahu': 'राहु', 'Ketu': 'केतु',


    },


    'en': {


        'Sun': 'Sun', 'Moon': 'Moon', 'Mars': 'Mars', 'Mercury': 'Mercury',


        'Jupiter': 'Jupiter', 'Venus': 'Venus', 'Saturn': 'Saturn',


        'Rahu': 'Rahu', 'Ketu': 'Ketu',


    }


}





# Rashi names for dasha engine (must be defined before _convert_rashi_to_lang)


RASHI_NAMES_I18N = {


    'as': ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"],


    'bn': ["মেষ", "বৃষ", "মিথুন", "কর্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকর", "কুম্ভ", "মীন"],


    'hi': ["मेष", "वृष", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"],


    'en': ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],


}








# House names (Bhav names)


HOUSE_NAMES_I18N = {


    'as': ["প্ৰথম ভাব (লগ্ন/আত্ম)", "দ্বিতীয় ভাব (ধন)", "তৃতীয় ভাব (সহোদৰ)", "চতুৰ্থ ভাব (মাতৃ)",


           "পঞ্চম ভাব (পুত্ৰ)", "ষষ্ঠ ভাব (ৰোগ/শত্ৰু)", "সপ্তম ভাব (পত্নী)", "অষ্টম ভাব (আয়ু/মৃত্যু)",


           "নবম ভাব (ভাগ্য)", "দশম ভাব (কৰ্ম)", "একাদশ ভাব (লাভ)", "দ্বাদশ ভাব (ব্যয়)"],


    'bn': ["প্ৰথম ভাব (লগ্ন/আত্ম)", "দ্বিতীয় ভাব (ধন)", "তৃতীয় ভাব (সহোদৰ)", "চতুৰ্থ ভাব (মাতৃ)",


           "পঞ্চম ভাব (পুত্ৰ)", "ষষ্ঠ ভাব (ৰোগ/শত্ৰু)", "সপ্তম ভাব (পত্নী)", "অষ্টম ভাব (আয়ু/মৃত্যু)",


           "নবম ভাব (ভাগ্য)", "দশম ভাব (কৰ্ম)", "একাদশ ভাব (লাভ)", "দ্বাদশ ভাব (ব্যয়)"],


    'hi': ["प्रथम भाव (लग्न/आत्म)", "द्वितीय भाव (धन)", "तृतीय भाव (सहोदर)", "चतुर्थ भाव (मातृ)",


           "पंचम भाव (पुत्र)", "षष्ठ भाव (रोग/शत्रु)", "सप्तम भाव (पत्नी)", "अष्टम भाव (आयु/मृत्यु)",


           "नवम भाव (भाग्य)", "दशम भाव (कर्म)", "एकादश भाव (लाभ)", "द्वादश भाव (व्यय)"],


    'en': ["1st House (Lagna/ Self)", "2nd House (Wealth)", "3rd House (Siblings)", "4th House (Mother)",


           "5th House (Children)", "6th House (Disease/Enemy)", "7th House (Spouse)", "8th House (Longevity/Death)",


           "9th House (Fortune)", "10th House (Career)", "11th House (Gains)", "12th House (Expenses)"],


}








def _load_lang_json(filename_pattern, lang):


    """Load a language-specific JSON file. Pattern like 'lagna_phala_{lang}.json'"""


    path = os.path.join(_DATA_DIR, filename_pattern.format(lang=lang))


    if os.path.exists(path):


        with open(path, 'r', encoding='utf-8') as f:


            return json.load(f)


    # Fallback to Assamese


    path_as = os.path.join(_DATA_DIR, filename_pattern.format(lang='as'))


    if os.path.exists(path_as):


        with open(path_as, 'r', encoding='utf-8') as f:


            return json.load(f)


    return None








# ═══════════════════════════════════════════════════════════════


#  LAGNA PHALA (12 Lagnas)


# ═══════════════════════════════════════════════════════════════





def get_lagna_phala_i18n(lagna_index, lang='as'):


    """Get lagna phala in the specified language."""


    from lagna_phala import LAGNA_PHALA, LAGNA_NAMES


    data = _load_lang_json('lagna_phala_{lang}.json', lang)


    if data and str(lagna_index) in data:


        return data[str(lagna_index)]


    # Fallback to original Assamese


    return LAGNA_PHALA.get(lagna_index, '')








def get_lagna_phala_html_i18n(lagna_index, lang='as'):


    """Get lagna phala HTML in the specified language."""


    text = get_lagna_phala_i18n(lagna_index, lang)


    if not text:


        return ''


    lagna_name = get_rashi_name_i18n(lagna_index, lang)


    return f'<div style="font-size:0.85rem;line-height:1.8;text-align:justify;color:#2c3e50;white-space:pre-line;">{text}</div>'








# ═══════════════════════════════════════════════════════════════


#  RASHI PHALA (12 Rashis)


# ═══════════════════════════════════════════════════════════════





def get_rashi_phala_i18n(rashi_index, lang='as'):


    """Get rashi phala in the specified language."""


    from rashi_phala import RASHI_PHALA, RASHI_NAMES


    data = _load_lang_json('rashi_phala_{lang}.json', lang)


    if data and str(rashi_index) in data:


        return data[str(rashi_index)]


    return RASHI_PHALA.get(rashi_index, '')








def get_rashi_phala_html_i18n(rashi_index, lang='as'):


    """Get rashi phala HTML in the specified language."""


    text = get_rashi_phala_i18n(rashi_index, lang)


    if not text:


        return ''


    return f'<div style="font-size:0.85rem;line-height:1.8;text-align:justify;color:#2c3e50;white-space:pre-line;">{text}</div>'








# ═══════════════════════════════════════════════════════════════


#  NAKSHATRA PHALA (27 Nakshatras)


# ═══════════════════════════════════════════════════════════════





def get_nakshatra_phala_i18n(nak_index, lang='as'):


    """Get nakshatra phala in the specified language. nak_index is 1-based."""


    from nakshatra_phala import NAKSHATRA_PHALA, NAKSHATRA_NAMES


    data = _load_lang_json('nakshatra_phala_{lang}.json', lang)


    if data and str(nak_index) in data:


        return data[str(nak_index)]


    return NAKSHATRA_PHALA.get(nak_index, '')








def get_nakshatra_phala_html_i18n(nak_index, lang='as'):


    """Get nakshatra phala HTML in the specified language."""


    text = get_nakshatra_phala_i18n(nak_index, lang)


    if not text:


        return ''


    nak_name = get_nakshatra_name_i18n(nak_index - 1, lang)  # 0-based index


    return f'<div style="font-size:0.85rem;line-height:1.8;text-align:justify;color:#2c3e50;white-space:pre-line;">{text}</div>'








# ═══════════════════════════════════════════════════════════════


#  ANTARDASHA PHALA (small_antardasaphal.py)


# ═══════════════════════════════════════════════════════════════





# Reverse mapping: Assamese planet name → English planet name


_ASM_TO_ENG_PLANET = {


    'ৰবি': 'Sun', 'চন্দ্ৰ': 'Moon', 'মংগল': 'Mars', 'বুধ': 'Mercury',


    'বৃহস্পতি': 'Jupiter', 'শুক্ৰ': 'Venus', 'শনি': 'Saturn',


    'ৰাহু': 'Rahu', 'কেতু': 'Ketu',


}





# Reverse mapping: Assamese rashi name → rashi index (0-11)


# Normalize keys to NFC for consistent dictionary lookups


import unicodedata


_ASM_RASHI_TO_INDEX = {


    unicodedata.normalize('NFC', k): v


    for k, v in {


        "মেষ": 0, "বৃষ": 1, "মিথুন": 2, "কৰ্কট": 3, "সিংহ": 4, "কন্যা": 5,


        "তুলা": 6, "বৃশ্চিক": 7, "ধনু": 8, "মকৰ": 9, "কুম্ভ": 10, "মীন": 11,


    }.items()


}





def _convert_planet_to_lang(planet_name_asm, lang):


    """Convert an Assamese planet name to the target language."""


    if lang == 'as':


        return planet_name_asm


    eng = _ASM_TO_ENG_PLANET.get(planet_name_asm, planet_name_asm)


    return PLANET_NAMES_I18N.get(lang, {}).get(eng, planet_name_asm)





def _convert_rashi_to_lang(rashi_name, lang):


    """Convert a rashi name to the target language.


    Handles rashi names from any language (Assamese, Hindi, Bengali, English).


    """


    if lang == 'as':


        return rashi_name


    # Normalize input to NFC for consistent matching


    rashi_n = unicodedata.normalize('NFC', rashi_name)


    # First try Assamese lookup


    idx = _ASM_RASHI_TO_INDEX.get(rashi_n, -1)


    if idx >= 0:


        return RASHI_NAMES_I18N.get(lang, RASHI_NAMES_I18N['as'])[idx]


    # Try to find rashi index by checking all language rashi lists


    for lang_key, rashi_list in RASHI_NAMES_I18N.items():


        if rashi_n in rashi_list:


            idx = rashi_list.index(rashi_n)


            return RASHI_NAMES_I18N.get(lang, RASHI_NAMES_I18N['as'])[idx]


    return rashi_name





def get_antardasha_phala_i18n(graha_name, rashi_name, house_num, lang='as'):


    """Get antardasha phala in the specified language.


    graha_name and rashi_name should be in Assamese (as stored in planet data).


    Handles rashi name variants in the JSON files (e.g. Hindi uses both


    'वृष' and 'वृषभ' for Taurus).


    """


    from small_antardasaphal import get_antardasha_phala as _orig


    data = _load_lang_json('antardasha_phala_{lang}.json', lang)


    if data:


        # Convert to target language for key lookup


        graha_lang = _convert_planet_to_lang(graha_name, lang)


        rashi_lang = _convert_rashi_to_lang(rashi_name, lang)


        # Build list of candidate rashi names to try (handles JSON rashi name variants)


        rashi_candidates = [rashi_lang]


        # Add Assamese fallback (some JSON files use ASM rashi names)


        rashi_candidates.append(_convert_rashi_to_lang(rashi_name, 'as'))


        # Add common short/long form variants per language


        if lang == 'hi':


            rashi_candidates += ['वृषभ', 'वृष', 'वृश्चिक', 'वृश्चिक', 'कर्क', 'कर्कट', 'দনু']


        elif lang == 'bn':


            rashi_candidates += ['কৰ্কট', 'কর্কট']


        elif lang == 'en':


            rashi_candidates += ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']


        # Try each candidate


        for r_cand in rashi_candidates:


            key = f"{graha_lang}|{r_cand}|{house_num}"


            if key in data:


                return data[key]


        # Final fallback: also try English key in case JSON uses eng names


        if lang != 'en':


            rashi_n = unicodedata.normalize('NFC', rashi_name)


            rashi_idx = _ASM_RASHI_TO_INDEX.get(rashi_n, -1)


            if rashi_idx < 0:


                for lang_key, rashi_list in RASHI_NAMES_I18N.items():


                    if rashi_n in rashi_list:


                        rashi_idx = rashi_list.index(rashi_n)


                        break


            if rashi_idx >= 0:


                eng_rashi = RASHI_NAMES_I18N['en'][rashi_idx]


                eng_planet = _ASM_TO_ENG_PLANET.get(graha_name, graha_name)


                eng_key = f"{eng_planet}|{eng_rashi}|{house_num}"


                if eng_key in data:


                    return data[eng_key]


    return _orig(graha_name, rashi_name, house_num)








# ═══════════════════════════════════════════════════════════════


#  IMPORTANT ANTARDASHA (importantantardasa.py / antardasha_data.json)


# ═══════════════════════════════════════════════════════════════





def get_important_antardasha_phala_i18n(maha_lord, antar_lord, lang='as'):


    """Get important antardasha phala in the specified language.


    maha_lord and antar_lord should be in Assamese.


    """


    from importantantardasa import get_important_antardasha_phala as _orig


    data = _load_lang_json('important_antardasha_{lang}.json', lang)


    if data:


        maha_lang = _convert_planet_to_lang(maha_lord, lang)


        antar_lang = _convert_planet_to_lang(antar_lord, lang)


        key = f"{maha_lang}-{antar_lang}"


        if key in data:


            return data[key]


    return _orig(maha_lord, antar_lord)








# ═══════════════════════════════════════════════════════════════


#  Karakattwa (planetary significations)


# ═══════════════════════════════════════════════════════════════


KARAKATWA_I18N = {


    'as': {


        "Sun": "পিতৃ, চৰকাৰ, আত্মা, স্বাস্থ্য, নেতৃত্ব, ৰাজকীয় সন্মান",


        "Moon": "মাতৃ, মন, আৱেগ, শান্তি, জনসাধাৰণ, জল, দুগ্ধ",


        "Mars": "ভাতৃ, সাহস, ভূমি, স্থাৱৰ সম্পত্তি, শক্তি, ক্ৰীড়া, দুৰ্ঘটনা",


        "Mercury": "বুদ্ধি, ব্যৱসায়, বাক্ শক্তি, লেখা-মেলা, গণনা, যোগাযোগ, স্নায়ু",


        "Jupiter": "সন্তান, গুৰু, পিতৃ, শিক্ষা, ধন, ধৰ্ম, জ্ঞান, স্বামী (মহিলাৰ), ভাগ্য",


        "Venus": "পত্নী, বিবাহ, বিলাসিতা, কলা, সংগীত, সৌন্দৰ্য্য, বাহন, প্রেম",


        "Saturn": "কৰ্ম, আয়ুস, দুখ-কষ্ট, দীৰ্ঘম্যাদী পৰিকল্পনা, চাকৰ, ৰোগ",


        "Rahu": "হঠাতে ঘটা ঘটনা, বিভ্ৰান্তি, বিদেশ, উচ্চাকাংক্ষা, মায়া, অপৰম্পৰাগত চিন্তা",


        "Ketu": "আধ্যাত্মিকতা, বিচ্ছেদ, মোক্ষ, গৱেষণা, পূৰ্বজন্মৰ কৰ্মফল, একাকীত্ব",


    },


    'bn': {


        "Sun": "পিতা, সরকার, আত্মা, স্বাস্থ্য, নেতৃত্ব, রাজকীয় সম্মান",


        "Moon": "মাতা, মন, আবেগ, শান্তি, জনসাধারণ, জল, দুগ্ধ",


        "Mars": "ভাই, সাহস, ভূমি, অচল সম্পত্তি, শক্তি, ক্রীড়া, দুৰ্ঘটনা",


        "Mercury": "বুদ্ধি, ব্যবসা, বাক্শক্তি, লেখা-মেলা, গণনা, যোগাযোগ, স্নায়ু",


        "Jupiter": "সন্তান, গুরু, পিতা, শিক্ষা, ধন, ধর্ম, জ্ঞান, স্বামী, ভাগ্য",


        "Venus": "পত্নী, বিবাহ, বিলাসিতা, কলা, সংগীত, সৌন্দর্য, বাহন, প্রেম",


        "Saturn": "কর্ম, আয়ু, দুঃখ-কষ্ট, দীর্ঘকালিক যোজনা, চাকর, রোগ",


        "Rahu": "হঠাৎ ঘটনা, বিভ্রান্তি, বিদেশ, উচ্চাকাংক্ষা, মায়া, অপ্রচলিত চিন্তা",


        "Ketu": "আধ্যাত্মিকতা, বিচ্ছেদ, মোক্ষ, গবেষণা, পূর্বজন্মের কর্মফল, একাকীত্ব",


    },


    'hi': {


        "Sun": "पिता, सरकार, आत्मा, स्वास्थ्य, नेतृत्व, राजकीय सम्मान",


        "Moon": "माता, मन, आवेग, शान्ति, जनसाधारण, जल, दूध",


        "Mars": "भाइ, साहस, भूमि, अचल संपत्ति, शक्ति, क्रीड़ा, दुर्घटना",


        "Mercury": "बुद्धि, व्यापार, वाक्शक्ति, लेखन, गणना, संचार, तंत्रिका",


        "Jupiter": "संतान, गुरु, पिता, शिक्षा, धन, धर्म, ज्ञान, स्वामी, भाग्य",


        "Venus": "पत्नी, विवाह, विलासिता, कला, संगीत, सौंदर्य, वाहन, प्रेम",


        "Saturn": "कर्म, आयु, दुःख-कष्ट, दीर्घकालिक योजना, नौकर, रोग",


        "Rahu": "अचानक घटना, भ्रम, विदेश, महत्वाकांक्षा, माया, अप्रचलित चिन्ता",


        "Ketu": "आध्यात्मिकता, विच्छेद, मोक्ष, गवेषणा, पूर्वजन्म के कर्मफल, एकाकीत्व",


    },


    'en': {


        "Sun": "Father, Government, Soul, Health, Leadership, Royal Honor",


        "Moon": "Mother, Mind, Emotions, Peace, Public, Water, Milk",


        "Mars": "Siblings, Courage, Land, Property, Strength, Sports, Accidents",


        "Mercury": "Intellect, Business, Speech, Writing, Calculation, Communication, Nerves",


        "Jupiter": "Children, Guru, Father, Education, Wealth, Religion, Knowledge, Husband, Fortune",


        "Venus": "Wife, Marriage, Luxury, Arts, Music, Beauty, Vehicles, Love",


        "Saturn": "Career, Longevity, Hardship, Long-term Planning, Servants, Disease",


        "Rahu": "Sudden Events, Confusion, Foreign, Ambition, Illusion, Unconventional Thinking",


        "Ketu": "Spirituality, Separation, Moksha, Research, Past Life Karma, Solitude",


    },


}








def get_planet_name_i18n(eng_name, lang='as'):


    """Get planet name in the specified language."""


    return PLANET_NAMES_I18N.get(lang, PLANET_NAMES_I18N['as']).get(eng_name, eng_name)








def get_rashi_name_i18n(index, lang='as'):


    """Get rashi name in the specified language."""


    names = RASHI_NAMES_I18N.get(lang, RASHI_NAMES_I18N['as'])


    if 0 <= index < len(names):


        return names[index]


    return str(index)








def get_house_name_i18n(house_num, lang='as'):


    """Get house name in the specified language."""


    names = HOUSE_NAMES_I18N.get(lang, HOUSE_NAMES_I18N['as'])


    if 0 <= house_num < len(names):


        return names[house_num]


    return str(house_num)








def get_karakattwa_i18n(eng_name, lang='as'):


    """Get karakattwa in the specified language."""


    return KARAKATWA_I18N.get(lang, KARAKATWA_I18N['as']).get(eng_name, eng_name)








# ═══════════════════════════════════════════════════════════════


#  DWADASH BHAB PHALA


# ═══════════════════════════════════════════════════════════════





def get_dwadash_html_i18n(planet_houses, asc_rasi_idx, lang='as'):


    """Get dwadash bhab phala HTML in the specified language."""


    from dwadash_bhab_phala import get_dwadash_html as _orig


    data = _load_lang_json('dwadash_bhab_{lang}.json', lang)


    if data:


        # Unwrap Dwadash_Bhab_Phal key if present


        if 'Dwadash_Bhab_Phal' in data:


            data = data['Dwadash_Bhab_Phal']


        # Use language-specific data if available


        from dwadash_bhab_phala import get_dwadash_html_from_data


        try:


            return get_dwadash_html_from_data(data, planet_houses, asc_rasi_idx, lang=lang)


        except (AttributeError, TypeError):


            pass


    return _orig(planet_houses=planet_houses, asc_rasi_idx=asc_rasi_idx)








# ═══════════════════════════════════════════════════════════════


#  GRAHA BICHAR


# ═══════════════════════════════════════════════════════════════





def get_graha_bichar_html_i18n(planet_houses, lang='as'):


    """Get graha bichar HTML in the specified language."""


    from graha_bichar import get_graha_bichar_html as _orig


    data = _load_lang_json('graha_bichar_{lang}.json', lang)


    if data:


        from graha_bichar import get_graha_bichar_html_from_data


        try:


            return get_graha_bichar_html_from_data(data, planet_houses, lang)


        except (AttributeError, TypeError):


            pass


    return _orig(planet_houses)








# ═══════════════════════════════════════════════════════════════


#  PANCHANGA


# ═══════════════════════════════════════════════════════════════





def get_panchanga_labels_i18n(lang='as'):


    """Get panchanga labels in the specified language."""


    return {


        'tithi': get_text('panch_tithi', lang),


        'nakshatra': get_text('panch_nakshatra', lang),


        'yoga': get_text('panch_yoga', lang),


        'karana': get_text('panch_karana', lang),


        'vaar': get_text('panch_vaar', lang),


        'paksha': get_text('panchanga_paksha', lang),


        'sunrise': get_text('panchanga_sunrise', lang),


        'sunset': get_text('panchanga_sunset', lang),


        'masa': get_text('panchanga_masa', lang),


        'ritu': get_text('panchanga_ritu', lang),


        'ayan': get_text('panchanga_ayan', lang),


    }








# ═══════════════════════════════════════════════════════════════


#  PANCHANGA NAME LISTS - i18n (Tithi, Nakshatra, Yoga, etc.)


# ═══════════════════════════════════════════════════════════════





PANCHANGA_I18N = {


    'as': {


        'TITHI_NAMES': [


            "প্ৰতিপদ", "দ্বিতীয়া", "তৃতীয়া", "চতুৰ্থী", "পঞ্চমী", "ষষ্ঠী",


            "সপ্তমী", "অষ্টমী", "নবমী", "দশমী", "একাদশী", "দ্বাদশী",


            "ত্ৰয়োদশী", "চতুৰ্দশী", "পূৰ্ণিমা",


            "প্ৰতিপদ", "দ্বিতীয়া", "তৃতীয়া", "চতুৰ্থী", "পঞ্চমী", "ষষ্ঠী",


            "সপ্তমী", "অষ্টমী", "নবমী", "দশমী", "একাদশী", "দ্বাদশী",


            "ত্ৰয়োদশী", "চতুৰ্দশী", "অমাৱস্যা",


        ],


        'NAKSHATRA_NAMES': [


            "অশ্বিনী", "ভৰণী", "কৃত্তিকা", "ৰোহিণী", "মৃগশিৰা", "আৰ্দ্ৰা", "পুনৰ্বসু",


            "পুষ্যা", "অশ্লেষা", "মঘা", "পূৰ্বফাল্গুনী", "উত্তৰফাল্গুনী", "হস্তা",


            "চিত্ৰা", "স্বাতী", "বিশাখা", "অনুৰাধা", "জ্যেষ্ঠা", "মূল", "পূৰ্বাষাঢ়া",


            "উত্তৰাষাঢ়া", "শ্ৰৱণা", "ধনিষ্ঠা", "শতভিষা", "পূৰ্বভাদ্ৰপদ", "উত্তৰভাদ্ৰপদ", "ৰেৱতী"


        ],


        'YOGA_NAMES': [


            "বিষ্কুম্ভ", "প্রীতি", "আয়ুষ্মান", "সৌভাগ্য", "শোভন", "অতিগণ্ড",


            "সুকৰ্মা", "ধৃতি", "শূল", "গণ্ড", "বৃদ্ধি", "ধ্রুব",


            "ব্যাঘাত", "হৰ্ষণ", "বজ্র", "সিদ্ধি", "ব্যতিপাত", "বৰীয়ান",


            "পৰিঘ", "শিৱ", "সিদ্ধ", "সাধ্য", "শুভ", "শুক্ল",


            "ব্ৰহ্ম", "ইন্দ্ৰ", "বৈধৃতি",


        ],


        'KARANA_NAMES': [


            "বৱ", "বালৱ", "কৌলৱ", "তৈতিল", "গৰ", "বণিজ", "বিষ্টি",


            "শকুনি", "চতুষ্পাদ", "নাগ", "কিংস্তুঘ্ন",


        ],


        'VAAR_NAMES': ["সোমবাৰ", "মংগলবাৰ", "বুধবাৰ", "বৃহস্পতিবাৰ", "শুক্ৰবাৰ", "শনিবাৰ", "ৰবিবাৰ"],


        'RITU_NAMES': ["বসন্ত", "গ্ৰীষ্ম", "বৰ্ষা", "শৰৎ", "হেমন্ত", "শিশির"],


        'MASA_NAMES': [


            "ব'হাগ", "জেঠ", "আহাৰ", "শাওণ", "ভাদ", "আহিন",


            "কাতি", "আঘোণ", "পুহ", "মাঘ", "ফাগুন", "চ'ত"


        ],


        'PAKSHA_NAMES': ["শুক্লপক্ষ", "কৃষ্ণপক্ষ"],


        'VARNA_NAMES': ["ব্ৰাহ্মণ", "ক্ষত্রিয়", "বৈশ্য", "শূদ্র"],


        'GANA_NAMES': ["দেৱ", "মানুষ্য", "ৰাক্ষস"],


        'NADI_NAMES': ["আদি", "মধ্য", "অন্ত্য"],


        'RASHI_LORDS': [


            "মংগল", "শুক্ৰ", "বুধ", "চন্দ্ৰ", "সূৰ্য", "বুধ",


            "শুক্ৰ", "মংগল", "বৃহস্পতি", "শনি", "শনি", "বৃহস্পতি"


        ],


        'YOGINI_DIRECTIONS': {


            "পূব": "পূব", "উত্তৰ": "উত্তৰ", "অগ্নিকোণ": "অগ্নিকোণ",


            "নৈঋৎকোণ": "নৈঋৎকোণ", "দক্ষিণ": "দক্ষিণ", "পশ্চিম": "পশ্চিম",


            "বায়ুকোণ": "বায়ুকোণ", "ইশানকোণ": "ইশানকোণ",


        },


        'PLANET_NAMES': {


            "Sun": "ৰবি (সূৰ্য্য)", "Moon": "চন্দ্ৰ", "Mars": "মংগল",


            "Mercury": "বুধ", "Jupiter": "বৃহস্পতি", "Venus": "শুক্ৰ",


            "Saturn": "শনি", "Rahu": "ৰাহু", "Ketu": "কেতু",


        },


        'RASHI_NAMES': ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"],


        'divaman_unit': "ঘণ্টা {h} মিনিট {m}",


        'ratriman_unit': "ঘণ্টা {h} মিনিট {m}",


        'jata_danda_unit': "{d} দণ্ড {p} পল",


        'kaal_bela_dual': "{p1} আৰু {p2}",


        'bara_bela_dual': "{p1} আৰু {p2}",


        'next_day_suffix': " (পৰদিন)",


        'prev_day_prefix': " (আগদিনা) ",


    },


    'bn': {


        'TITHI_NAMES': [


            "প্রতিপদ", "দ্বিতীয়া", "তৃতীয়া", "চতুৰ্থী", "পঞ্চমী", "ষষ্ঠী",


            "সপ্তমী", "অষ্টমী", "নবমী", "দশমী", "একাদশী", "দ্বাদশী",


            "ত্ৰয়োদশী", "চতুৰ্দশী", "পূৰ্ণিমা",


            "প্রতিপদ", "দ্বিতীয়া", "তৃতীয়া", "চতুৰ্থী", "পঞ্চমী", "ষষ্ঠী",


            "সপ্তমী", "অষ্টমী", "নবমী", "দশমী", "একাদশী", "দ্বাদশী",


            "ত্ৰয়োদশী", "চতুৰ্দশী", "অমাৱস্যা",


        ],


        'NAKSHATRA_NAMES': [


            "অশ্বিনী", "ভরণী", "কৃত্তিকা", "রোহিণী", "মৃগশিৰা", "আৰ্দ্রা", "পুনৰ্বসু",


            "পুষ্যা", "অশ্লেষা", "মঘা", "পূৰ্বফাল্গুনী", "উত্তৰফাল্গুনী", "হস্তা",


            "চিত্রা", "স্বাতী", "বিশাখা", "অনুৰাধা", "জ্যেষ্ঠা", "মূল", "পূৰ্বাষাঢ়া",


            "উত্তৰাষাঢ়া", "শ্রবণা", "ধনিষ্ঠা", "শতভিষা", "পূৰ্বভাদ্রপদ", "উত্তরভাদ্রপদ", "ৰেৱতী"


        ],


        'YOGA_NAMES': [


            "বিষ্কুম্ভ", "প্রীতি", "আয়ুষ্মান", "সৌভাগ্য", "শোভন", "অতিগণ্ড",


            "সুকৰ্মা", "ধৃতি", "শূল", "গণ্ড", "বৃদ্ধি", "ধ্রুব",


            "ব্যাঘাত", "হৰ্ষণ", "বজ্র", "সিদ্ধি", "ব্যতিপাত", "বৰীয়ান",


            "পৰিঘ", "শিৱ", "সিদ্ধ", "সাধ্য", "শুভ", "শুক্ল",


            "ব্ৰহ্ম", "ইন্দ্ৰ", "বৈধৃতি",


        ],


        'KARANA_NAMES': [


            "বব", "বালব", "কৌলব", "তৈতিল", "গর", "বণিজ", "বিষ্টি",


            "শকুনি", "চতুষ্পাদ", "নাগ", "কিংস্তুঘ্ন",


        ],


        'VAAR_NAMES': ["সোমবার", "মঙ্গলবার", "বুধবার", "গুরুবার", "শুক্রবার", "শনিবার", "রবিবার"],


        'RITU_NAMES': ["বসন্ত", "গ্রীষ্ম", "বর্ষা", "শরৎ", "হেমন্ত", "শিশির"],


        'MASA_NAMES': [


            "বৈশাখ", "জ্যৈষ্ঠ", "আষাঢ়", "শ্রাবণ", "ভাদ্র", "আশ্বিন",


            "কার্তিক", "অগ্রহায়ণ", "পৌষ", "মাঘ", "ফাল্গুন", "চৈত্র"


        ],


        'PAKSHA_NAMES': ["শুক্লপক্ষ", "কৃষ্ণপক্ষ"],


        'VARNA_NAMES': ["ব্রাহ্মণ", "ক্ষত্রিয়", "বৈশ্য", "শূদ্র"],


        'GANA_NAMES': ["দেব", "মানুষ্য", "রাক্ষস"],


        'NADI_NAMES': ["আদি", "মধ্য", "অন্ত্য"],


        'RASHI_LORDS': [


            "মঙ্গল", "শুক্র", "বুধ", "চন্দ্র", "সূৰ্য", "বুধ",


            "শুক্র", "মঙ্গল", "বৃহস্পতি", "শনি", "শনি", "বৃহস্পতি"


        ],


        'YOGINI_DIRECTIONS': {


            "পূব": "পূর্ব", "উত্তৰ": "উত্তর", "অগ্নিকোণ": "South-East",


            "নৈঋৎকোণ": "South-West", "দক্ষিণ": "South", "পশ্চিম": "West",


            "বায়ুকোণ": "North-West", "ইশানকোণ": "North-East",


        },


        'PLANET_NAMES': {


            "Sun": "রবি", "Moon": "চন্দ্র", "Mars": "মঙ্গল",


            "Mercury": "বুধ", "Jupiter": "বৃহস্পতি", "Venus": "শুক্র",


            "Saturn": "শনি", "Rahu": "রাহু", "Ketu": "কেতু",


        },


        'RASHI_NAMES': ["মেষ", "বৃষ", "মিথুন", "কর্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকর", "কুম্ভ", "মীন"],


        'divaman_unit': "{h}h {m}m",


        'ratriman_unit': "{h}h {m}m",


        'jata_danda_unit': "{d} Danda {p} Pala",


        'kaal_bela_dual': "{p1} and {p2}",


        'bara_bela_dual': "{p1} and {p2}",


        'next_day_suffix': " (next day)",


        'prev_day_prefix': " (prev day) ",


    },


    'hi': {


        'TITHI_NAMES': [


            "प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी",


            "सप्तमी", "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी",


            "त्रयोदशी", "चतुर्दशी", "पूर्णिमा",


            "प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी",


            "सप्तमी", "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी",


            "त्रयोदशी", "चतुर्दशी", "अमावस्या",


        ],


        'NAKSHATRA_NAMES': [


            "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा", "पुनर्वसु",


            "पुष्या", "आश्लेषा", "मघा", "पूर्वाफाल्गुनी", "उत्तराफाल्गुनी", "हस्ता",


            "चित्रा", "स्वाती", "विशाखा", "अनुराधा", "ज्येष्ठा", "मूल", "पूर्वाषाढ़ा",


            "उत्तराषाढ़ा", "श्रवणा", "धनिष्ठा", "शतभिषा", "पूर्वाभाद्रपद", "उत्तराभाद्रपद", "रेवती"


        ],


        'YOGA_NAMES': [


            "विष्कुम्भ", "प्रीति", "आयुष्मान", "सौभाग्य", "शोभन", "अतिगण्ड",


            "सुकर्मा", "धृति", "शूल", "गण्ड", "वृद्धि", "ध्रुव",


            "व्याघात", "हर्षण", "वज्र", "सिद्धि", "व्यतिपात", "वरीयान",


            "परिघ", "शिव", "सिद्ध", "साध्य", "शुभ", "शुक्ल",


            "ब्रह्म", "इन्द्र", "वैधृति",


        ],


        'KARANA_NAMES': [


            "बव", "बालव", "कौलव", "तैतिल", "गर", "वणिज", "विष्टि",


            "शकुनि", "चतुष्पाद", "नाग", "किंस्तुघ्न",


        ],


        'VAAR_NAMES': ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"],


        'RITU_NAMES': ["वसंत", "ग्रीष्म", "वर्षा", "शरद", "हेमंत", "शिशिर"],


        'MASA_NAMES': [


            "वैशाख", "ज्येष्ठ", "आषाढ़", "श्रावण", "भाद्रपद", "आश्विन",


            "कार्तिक", "अग्रहायण", "पौष", "माघ", "फाल्गुन", "चैत्र"


        ],


        'PAKSHA_NAMES': ["शुक्लपक्ष", "कृष्णपक्ष"],


        'VARNA_NAMES': ["ब्राह्मण", "क्षत्रिय", "वैश्य", "शूद्र"],


        'GANA_NAMES': ["देव", "मनुष्य", "राक्षस"],


        'NADI_NAMES': ["आदि", "मध्य", "अन्त्य"],


        'RASHI_LORDS': [


            "मंगल", "शुक्र", "बुध", "चंद्र", "सूर्य", "बुध",


            "शुक्र", "मंगल", "बृहस्पति", "शनि", "शनि", "बृहस्पति"


        ],


        'YOGINI_DIRECTIONS': {


            "পূব": "पूर्व", "উত্তৰ": "उत्तर", "অগ্নিকোণ": "South-East",


            "নৈঋৎকোণ": "South-West", "দক্ষিণ": "South", "পশ্চিম": "West",


            "বায়ুকোণ": "North-West", "ইশানকোণ": "North-East",


        },


        'PLANET_NAMES': {


            "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल",


            "Mercury": "बुध", "Jupiter": "बृहस्पति", "Venus": "शुक्र",


            "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु",


        },


        'RASHI_NAMES': ["मेष", "वृष", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"],


        'divaman_unit': "{h}h {m}m",


        'ratriman_unit': "{h}h {m}m",


        'jata_danda_unit': "{d} Danda {p} Pala",


        'kaal_bela_dual': "{p1} and {p2}",


        'bara_bela_dual': "{p1} and {p2}",


        'next_day_suffix': " (next day)",


        'prev_day_prefix': " (prev day) ",


    },


    'en': {


        'TITHI_NAMES': [


            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",


            "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",


            "Trayodashi", "Chaturdashi", "Purnima",


            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",


            "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",


            "Trayodashi", "Chaturdashi", "Amavasya",


        ],


        'NAKSHATRA_NAMES': [


            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",


            "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",


            "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",


            "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"


        ],


        'YOGA_NAMES': [


            "Vishkumbha", "Preeti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",


            "Sukarma", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva",


            "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana",


            "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",


            "Brahma", "Indra", "Vaidhriti",


        ],


        'KARANA_NAMES': [


            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",


            "Shakuni", "Chatushpada", "Naga", "Kimstughna",


        ],


        'VAAR_NAMES': ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],


        'RITU_NAMES': ["Spring", "Summer", "Monsoon", "Autumn", "Pre-winter", "Winter"],


        'MASA_NAMES': [


            "Vaisakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashwina",


            "Kartika", "Agrahayana", "Pausha", "Magha", "Phalguna", "Chaitra"


        ],


        'PAKSHA_NAMES': ["Shukla Paksha", "Krishna Paksha"],


        'VARNA_NAMES': ["Brahmin", "Kshatriya", "Vaishya", "Shudra"],


        'GANA_NAMES': ["Deva", "Manushya", "Rakshasa"],


        'NADI_NAMES': ["Adi", "Madhya", "Antya"],


        'RASHI_LORDS': [


            "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",


            "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"


        ],


        'YOGINI_DIRECTIONS': {


            "পূব": "East", "উত্তৰ": "North", "অগ্নিকোণ": "South-East",


            "নৈঋৎকোণ": "South-West", "দক্ষিণ": "South", "পশ্চিম": "West",


            "বায়ুকোণ": "North-West", "ইশানকোণ": "North-East",


        },


        'PLANET_NAMES': {


            "Sun": "Sun", "Moon": "Moon", "Mars": "Mars",


            "Mercury": "Mercury", "Jupiter": "Jupiter", "Venus": "Venus",


            "Saturn": "Saturn", "Rahu": "Rahu", "Ketu": "Ketu",


        },


        'RASHI_NAMES': ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],


        'divaman_unit': "{h}h {m}m",


        'ratriman_unit': "{h}h {m}m",


        'jata_danda_unit': "{d} Danda {p} Pala",


        'kaal_bela_dual': "{p1} and {p2}",


        'bara_bela_dual': "{p1} and {p2}",


        'next_day_suffix': " (next day)",


        'prev_day_prefix': " (prev day) ",


    },


}








def get_panchanga_names_i18n(lang='as'):


    """Get all panchanga name lists in the specified language."""


    return PANCHANGA_I18N.get(lang, PANCHANGA_I18N['as'])








def get_panchanga_name_i18n(list_key, index, lang='as'):


    """Get a single panchanga name by list key and index."""


    data = PANCHANGA_I18N.get(lang, PANCHANGA_I18N['as'])


    names = data.get(list_key, [])


    if 0 <= index < len(names):


        return names[index]


    return str(index)








def get_panchanga_planet_name_i18n(eng_name, lang='as'):


    """Get planet name for panchanga display in the specified language."""


    data = PANCHANGA_I18N.get(lang, PANCHANGA_I18N['as'])


    return data.get('PLANET_NAMES', {}).get(eng_name, eng_name)








def get_panchanga_rashi_name_i18n(index, lang='as'):


    """Get rashi name for panchanga display in the specified language."""


    data = PANCHANGA_I18N.get(lang, PANCHANGA_I18N['as'])


    names = data.get('RASHI_NAMES', [])


    if 0 <= index < len(names):


        return names[index]


    return str(index)








def get_panchanga_yogini_direction_i18n(as_direction, lang='as'):


    """Translate yogini direction from Assamese key to target language."""


    data = PANCHANGA_I18N.get(lang, PANCHANGA_I18N['as'])


    return data.get('YOGINI_DIRECTIONS', {}).get(as_direction, as_direction)








# ═══════════════════════════════════════════════════════════════


#  SADE SATI


# ═══════════════════════════════════════════════════════════════





def get_sade_sati_phase_name_i18n(phase_name, lang='as'):


    """Translate sade sati phase name."""


    phase_map = {


        'as': {


            'Rising': 'উদীয়মান',


            'Peak': 'শীৰ্ষ',


            'Setting': 'অস্তগামী',


            'Dhaiya': 'দhaiয়া',


            'Not Running': 'সাৰেসাতী চলি থকা নাই',


        },


        'bn': {


            'Rising': 'উদীয়মান',


            'Peak': 'শীৰ্ষ',


            'Setting': 'অস্তগামী',


            'Dhaiya': 'দhaiয়া',


            'Not Running': 'সাড়েসাতী চলছে না',


        },


        'hi': {


            'Rising': 'उदीयमान',


            'Peak': 'शीर्ष',


            'Setting': 'अस्तगामी',


            'Dhaiya': 'ढैया',


            'Not Running': 'साढ़ेसाती नहीं चल रही',


        },


        'en': {


            'Rising': 'Rising',


            'Peak': 'Peak',


            'Setting': 'Setting',


            'Dhaiya': 'Dhaiya',


            'Not Running': 'Sade Sati not running',


        },


    }


    return phase_map.get(lang, phase_map['as']).get(phase_name, phase_name)








# ═══════════════════════════════════════════════════════════════


#  TRIPAP RISTA - Row labels i18n


# ═══════════════════════════════════════════════════════════════





TRIPAP_ROW_LABELS_I18N = {


    'as': {


        "r1": "ঘৰ নং (১-১২)", "r2": "ঘৰ নং (৩৭-৪৮)", "r3": "গ্ৰহ",


        "r4": "গ্ৰহ", "r5": "গ্ৰহ", "r6": "ঘৰ নং (১৩-২৪)",


        "r7": "ঘৰ নং (৪৯-৬০)", "r8": "গ্ৰহ", "r9": "গ্ৰহ",


        "r10": "গ্ৰহ", "r11": "ঘৰ নং (২৫-৩৬)", "r12": "ঘৰ নং (৬১-৭২)",


        "r13": "গ্ৰহ", "r14": "গ্ৰহ", "r15": "গ্ৰহ",


        "col_desc": "বিৱৰণ",


        "col_house": "ঘৰ {}",


        "row_label": "শাৰী",


    },


    'bn': {


        "r1": "ঘর নং (১-১২)", "r2": "ঘর নং (৩৭-৪৮)", "r3": "গ্রহ",


        "r4": "গ্রহ", "r5": "গ্রহ", "r6": "ঘর নং (১৩-২৪)",


        "r7": "ঘর নং (৪৯-৬০)", "r8": "গ্রহ", "r9": "গ্রহ",


        "r10": "গ্রহ", "r11": "ঘর নং (২৫-৩৬)", "r12": "ঘর নং (৬১-৭২)",


        "r13": "গ্রহ", "r14": "গ্রহ", "r15": "গ্রহ",


        "col_desc": "বিবরণ",


        "col_house": "ঘৰ {}",


        "row_label": "সারি",


    },


    'hi': {


        "r1": "घर क्र. (1-12)", "r2": "घर क्र. (37-48)", "r3": "ग्रह",


        "r4": "ग्रह", "r5": "ग्रह", "r6": "घर क्र. (13-24)",


        "r7": "घर क्र. (49-60)", "r8": "ग्रह", "r9": "ग्रह",


        "r10": "ग्रह", "r11": "घर क्र. (25-36)", "r12": "घर क्र. (61-72)",


        "r13": "ग्रह", "r14": "ग्रह", "r15": "ग्रह",


        "col_desc": "विवरण",


        "col_house": "घर {}",


        "row_label": "पंक्ति",


    },


    'en': {


        "r1": "House No. (1-12)", "r2": "House No. (37-48)", "r3": "Planet",


        "r4": "Planet", "r5": "Planet", "r6": "House No. (13-24)",


        "r7": "House No. (49-60)", "r8": "Planet", "r9": "Planet",


        "r10": "Planet", "r11": "House No. (25-36)", "r12": "House No. (61-72)",


        "r13": "Planet", "r14": "Planet", "r15": "Planet",


        "col_desc": "Description",


        "col_house": "House {}",


        "row_label": "Row",


    },


}





def get_tripap_row_label_i18n(row_key, lang='as'):


    """Get tripap rista row label in the specified language."""


    return TRIPAP_ROW_LABELS_I18N.get(lang, TRIPAP_ROW_LABELS_I18N['as']).get(row_key, row_key)








# ═══════════════════════════════════════════════════════════════


#  TRIPAP RISTA - Planet names i18n


# ═══════════════════════════════════════════════════════════════





TRIPAP_PLANET_MAP_I18N = {


    'as': {"কে": "কেতু", "শু": "শুক্ৰ", "ৰ": "ৰবি", "চ": "চন্দ্ৰ",


           "ম": "মংগল", "বু": "বুধ", "শ": "শনি", "বৃ": "বৃহস্পতি", "ৰা": "ৰাহু"},


    'bn': {"কে": "কেতু", "শু": "শুক্র", "ৰ": "রবি", "চ": "চন্দ্র",


           "ম": "মঙ্গল", "বু": "বুধ", "শ": "শনি", "বৃ": "বৃহস্পতি", "ৰা": "রাহু"},


    'hi': {"কে": "केतु", "শু": "शुक्र", "ৰ": "सूर्य", "চ": "चंद्र",


           "ম": "मंगल", "বু": "बुध", "শ": "शनि", "বৃ": "बृहस्पति", "ৰা": "राहु"},


    'en': {"কে": "Ketu", "শু": "Venus", "ৰ": "Sun", "চ": "Moon",


           "ম": "Mars", "বু": "Mercury", "শ": "Saturn", "বৃ": "Jupiter", "ৰা": "Rahu"},


}





def get_tripap_planet_map_i18n(lang='as'):


    """Get tripap rista planet map in the specified language."""


    return TRIPAP_PLANET_MAP_I18N.get(lang, TRIPAP_PLANET_MAP_I18N['as'])








# ═══════════════════════════════════════════════════════════════


#  NAKSHATRA NAMES - i18n (used by navatara, sannari, etc.)


# ═══════════════════════════════════════════════════════════════





NAKSHATRA_NAMES_I18N_LIST = {


    'as': [


        "অশ্বিনী", "ভৰণী", "কৃত্তিকা", "ৰোহিণী", "মৃগশিৰা", "আৰ্দ্ৰা", "পুনৰ্বসু",


        "পুষ্যা", "অশ্লেষা", "মঘা", "পূৰ্বফাল্গুনী", "উত্তৰফাল্গুনী", "হস্তা",


        "চিত্ৰা", "স্বাতী", "বিশাখা", "অনুৰাধা", "জ্যেষ্ঠা", "মূল", "পূৰ্বাষাঢ়া",


        "উত্তৰাষাঢ়া", "শ্ৰৱণা", "ধনিষ্ঠা", "শতভিষা", "পূৰ্বভাদ্ৰপদ", "উত্তৰভাদ্ৰপদ", "ৰেৱতী"


    ],


    'bn': [


        "অশ্বিনী", "ভরণী", "কৃত্তিকা", "রোহিণী", "মৃগশিৰা", "আৰ্দ্রা", "পুনৰ্বসু",


        "পুষ্যা", "অশ্লেষা", "মঘা", "পূৰ্বফাল্গুনী", "উত্তৰফাল্গুনী", "হস্তা",


        "চিত্রা", "স্বাতী", "বিশাখা", "অনুৰাধা", "জ্যেষ্ঠা", "মূল", "পূৰ্বাষাঢ়া",


        "উত্তৰাষাঢ়া", "শ্রবণা", "ধনিষ্ঠা", "শতভিষা", "পূৰ্বভাদ্রপদ", "উত্তরভাদ্রপদ", "ৰেৱতী"


    ],


    'hi': [


        "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा", "पुनर्वसु",


        "पुष्या", "आश्लेषा", "मघा", "पूर्वाफाल्गुनी", "उत्तराफाल्गुनी", "हस्ता",


        "चित्रा", "स्वाती", "विशाखा", "अनुराधा", "ज्येष्ठा", "मूल", "पूर्वाषाढ़ा",


        "उत्तराषाढ़ा", "श्रवणा", "धनिष्ठा", "शतभिषा", "पूर्वाभाद्रपद", "उत्तराभाद्रपद", "रेवती"


    ],


    'en': [


        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",


        "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",


        "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",


        "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"


    ],


}





def get_nakshatra_name_i18n(index, lang='as'):


    """Get nakshatra name by 0-based index in the specified language."""


    names = NAKSHATRA_NAMES_I18N_LIST.get(lang, NAKSHATRA_NAMES_I18N_LIST['as'])


    if 0 <= index < len(names):


        return names[index]


    return str(index + 1)





def get_nakshatra_names_list_i18n(lang='as'):


    """Get the full list of 27 nakshatra names in the specified language."""


    return NAKSHATRA_NAMES_I18N_LIST.get(lang, NAKSHATRA_NAMES_I18N_LIST['as'])








# ═══════════════════════════════════════════════════════════════


#  JOTOK Milan - User input conversion helpers


# ═══════════════════════════════════════════════════════════════





import unicodedata





def _get_script(text):


    """Detect the primary script used in the text. Returns 'bengali', 'devanagari', or 'latin'."""


    if not text:


        return 'latin'


    for char in text:


        code = ord(char)


        if 0x0980 <= code <= 0x09FF:


            return 'bengali'


        elif 0x0900 <= code <= 0x097F:


            return 'devanagari'


    return 'latin'





def convert_nakshatra_to_asm(nakshatra_str, user_lang):


    """Convert a nakshatra name from user's language to Assamese for engine lookup.


    Uses index-based mapping and auto-detects script if user_lang seems wrong."""


    if not nakshatra_str:


        return nakshatra_str


    


    # If user_lang is as, return as-is (Assamese)


    if user_lang == 'as':


        return nakshatra_str


    


    # Auto-detect script and use appropriate language list


    detected_script = _get_script(nakshatra_str)


    


    # Map detected script to language


    if detected_script == 'bengali':


        effective_lang = 'bn'


    elif detected_script == 'devanagari':


        effective_lang = 'hi'


    else:


        effective_lang = 'en'  # Use English list for Latin/English script


    


    nakshatra_str_nfc = unicodedata.normalize('NFC', nakshatra_str)


    


    # Find nakshatra in the effective language list by exact match (NFC then NFD)


    nakshatra_list = NAKSHATRA_NAMES_I18N_LIST.get(effective_lang, [])


    for idx, name in enumerate(nakshatra_list):


        name_nfc = unicodedata.normalize('NFC', name)


        if name_nfc == nakshatra_str_nfc:


            return NAKSHATRA_NAMES_I18N_LIST['as'][idx]


    


    # Try NFD form


    nakshatra_str_nfd = unicodedata.normalize('NFD', nakshatra_str)


    for idx, name in enumerate(nakshatra_list):


        name_nfd = unicodedata.normalize('NFD', name)


        if name_nfd == nakshatra_str_nfd:


            return NAKSHATRA_NAMES_I18N_LIST['as'][idx]


    


    return nakshatra_str  # Return original if not found





def convert_rashi_to_asm(rashi_str, user_lang):


    """Convert a rashi name from user's language to Assamese for engine lookup.


    Uses index-based mapping and auto-detects script if user_lang seems wrong."""


    if not rashi_str:


        return rashi_str


    


    # If user_lang is as, return as-is (Assamese)


    if user_lang == 'as':


        return rashi_str


    


    # Auto-detect script and use appropriate language list


    detected_script = _get_script(rashi_str)


    


    # Map detected script to language


    if detected_script == 'bengali':


        effective_lang = 'bn'


    elif detected_script == 'devanagari':


        effective_lang = 'hi'


    else:


        effective_lang = 'en'  # Use English list for Latin/English script


    


    rashi_str_nfc = unicodedata.normalize('NFC', rashi_str)


    


    # Find rashi in the effective language list by exact match (NFC then NFD)


    rashi_list = RASHI_NAMES_I18N.get(effective_lang, [])


    for idx, name in enumerate(rashi_list):


        name_nfc = unicodedata.normalize('NFC', name)


        if name_nfc == rashi_str_nfc:


            return RASHI_NAMES_I18N['as'][idx]


    


    # Try NFD form


    rashi_str_nfd = unicodedata.normalize('NFD', rashi_str)


    for idx, name in enumerate(rashi_list):


        name_nfd = unicodedata.normalize('NFD', name)


        if name_nfd == rashi_str_nfd:


            return RASHI_NAMES_I18N['as'][idx]


    


    return rashi_str  # Return original if not found








# ═══════════════════════════════════════════════════════════════


#  SANNARI CHAKRA - Labels i18n


# ═══════════════════════════════════════════════════════════════





SANNARI_LABELS_I18N = {


    'as': {


        'janma': 'জন্ম', 'karma': 'কৰ্ম', 'samudaya': 'সমুদয়',


        'manasa': 'মানস', 'sanghatika': 'সাংঘাতিক', 'binasha': 'বিনাশ',


        'title': 'সন্নাড়ী চক্র',


        'nak_no': 'নক্ষত্র নং',


        'section': 'বিভাগ',


        'invalid': 'অবৈধ নক্ষত্র সংখ্যা',


    },


    'bn': {


        'janma': 'জন্ম', 'karma': 'কর্ম', 'samudaya': 'সমুদয়',


        'manasa': 'মানস', 'sanghatika': 'সাংঘাতিক', 'binasha': 'বিনাশ',


        'title': 'সন্নাড়ী চক্র',


        'nak_no': 'নক্ষত্র নং',


        'section': 'বিভাগ',


        'invalid': 'অবৈধ নক্ষত্র সংখ্যা',


    },


    'hi': {


        'janma': 'जन्म', 'karma': 'कर्म', 'samudaya': 'समुदय',


        'manasa': 'मानस', 'sanghatika': 'सांघातिक', 'binasha': 'विनाश',


        'title': 'सन्नाड़ी चक्र',


        'nak_no': 'नक्षत्र क्र.',


        'section': 'विभाग',


        'invalid': 'अमान्य नक्षत्र संख्या',


    },


    'en': {


        'janma': 'Janma', 'karma': 'Karma', 'samudaya': 'Samudaya',


        'manasa': 'Manasa', 'sanghatika': 'Sanghatika', 'binasha': 'Vinasha',


        'title': 'Sannari Chakra',


        'nak_no': 'Nak. No.',


        'section': 'Section',


        'invalid': 'Invalid Nakshatra Number',


    },


}





def get_sannari_label_i18n(key, lang='as'):


    """Get sannari chakra label in the specified language."""


    return SANNARI_LABELS_I18N.get(lang, SANNARI_LABELS_I18N['as']).get(key, key)








# ═══════════════════════════════════════════════════════════════


#  NAVATARA CHAKRA - Labels i18n


# ═══════════════════════════════════════════════════════════════





NAVATARA_LABELS_I18N = {


    'as': {


        'janma': 'জন্ম', 'sampat': 'সম্পদ', 'vipat': 'বিপদ',


        'kshema': 'ক্ষেম', 'pratyari': 'প্রত্যাৰি', 'sadhak': 'সাধক',


        'badha': 'বধ', 'mitra': 'মিত্ৰ', 'param_mitra': 'পৰমমিত্ৰ',


        'title': 'নৱতাৰা চক্র',


        'note': 'নবতাৰা চক্রত উল্লেখিত নক্ষত্ৰত গ্ৰহ সঞ্চাৰ হলে শুভ গ্ৰহই হওঁক বা অশুভ গ্ৰহই হওঁক উল্লেখিত নামানুসারে স্থিতি নক্ষত্ৰ কালত শুভা শুভ ফল সম্পাদিত হব। ৰঙা চিহ্ন থকা নক্ষত্রসমুহত জাতকৰ শুভকৰ্ম বৰ্জন কৰিব।',


        'invalid': 'অবৈধ নক্ষত্র সংখ্যা',


    },


    'bn': {


        'janma': 'জন্ম', 'sampat': 'সম্পদ', 'vipat': 'বিপদ',


        'kshema': 'ক্ষেম', 'pratyari': 'প্রত্যাৰি', 'sadhak': 'সাধক',


        'badha': 'বধ', 'mitra': 'মিত্ৰ', 'param_mitra': 'পৰমমিত্ৰ',


        'title': 'নবতারা চক্র',


        'note': 'নবতারা চক্রে উল্লেখিত নক্ষত্রে গ্রহ সঞ্চার হলে শুভ গ্রহই হওক বা অশুভ গ্রহই হওক উল্লেখিত নামানুসারে স্থিতি নক্ষত্র কালত শুভা শুভ ফল সম্পাদিত হব। লাল চিহ্ন থকা নক্ষত্রসমুহত জাতকৰ শুভকৰ্ম বৰ্জন কৰিব।',


        'invalid': 'অবৈধ নক্ষত্র সংখ্যা',


    },


    'hi': {


        'janma': 'जन्म', 'sampat': 'सम्पद', 'vipat': 'विपद',


        'kshema': 'क्षेम', 'pratyari': 'प्रत्याौरि', 'sadhak': 'साधक',


        'badha': 'बध', 'mitra': 'मित्र', 'param_mitra': 'परम मित्र',


        'title': 'नवतारा चक्र',


        'note': 'नवतारा चक्र में उल्लेखित नक्षत्रों में ग्रह संचार होने पर शुभ ग्रह हो या अशुभ ग्रह, उल्लेखित नामानुसार स्थिति नक्षत्र काल में शुभा शुभ फल प्राप्त होगा। लाल चिह्न वाले नक्षत्रों में जातक शुभ कर्म बर्जन करें।',


        'invalid': 'अमान्य नक्षत्र संख्या',


    },


    'en': {


        'janma': 'Janma', 'sampat': 'Sampat', 'vipat': 'Vipat',


        'kshema': 'Kshema', 'pratyari': 'Pratyari', 'sadhak': 'Sadhak',


        'badha': 'Badha', 'mitra': 'Mitra', 'param_mitra': 'Param Mitra',


        'title': 'Navatara Chakra',


        'note': 'When planets transit through the nakshatras mentioned in Navatara Chakra, whether benefic or malefic, results will manifest according to the named category. Avoid auspicious activities in red-marked nakshatras.',


        'invalid': 'Invalid Nakshatra Number',


    },


}





def get_navatara_label_i18n(key, lang='as'):


    """Get navatara chakra label in the specified language."""


    return NAVATARA_LABELS_I18N.get(lang, NAVATARA_LABELS_I18N['as']).get(key, key)





def get_navatara_tara_names_i18n(lang='as'):


    """Get all 9 tara names in the specified language."""


    labels = NAVATARA_LABELS_I18N.get(lang, NAVATARA_LABELS_I18N['as'])


    return [labels['janma'], labels['sampat'], labels['vipat'], labels['kshema'],


            labels['pratyari'], labels['sadhak'], labels['badha'], labels['mitra'], labels['param_mitra']]








# ═══════════════════════════════════════════════════════════════


#  KUNDLI CHART - Planet/Rashi names i18n


# ═══════════════════════════════════════════════════════════════





KUNDLI_PLANET_NAMES_I18N = {


    'as': {"ৰ": "ৰবি", "চ": "চন্দ্ৰ", "ম": "মংগল", "বু": "বুধ",


           "বৃ": "বৃহস্পতি", "শু": "শুক্ৰ", "শ": "শনি",


           "ৰা": "ৰাহু", "কে": "কেতু", "লং": "লগ্ন"},


    'bn': {"ৰ": "রবি", "চ": "চন্দ্র", "ম": "মঙ্গল", "বু": "বুধ",


           "বৃ": "বৃহস্পতি", "শু": "শুক্র", "শ": "শনি",


           "ৰা": "রাহু", "কে": "কেতু", "লং": "লগ্ন"},


    'hi': {"ৰ": "सूर्य", "চ": "चंद्र", "ম": "मंगल", "বু": "बुध",


           "বৃ": "बृहस्पति", "শু": "शुक्र", "শ": "शनि",


           "ৰা": "राहु", "কে": "केतु", "লং": "लग्न"},


    'en': {"ৰ": "Sun", "চ": "Moon", "ম": "Mars", "বু": "Mercury",


           "বৃ": "Jupiter", "শু": "Venus", "শ": "Saturn",


           "ৰা": "Rahu", "কে": "Ketu", "লং": "Lagna"},


}





KUNDLI_PLANET_SHORT_I18N = {


    'as': {"ৰ": "ৰ", "চ": "চ", "ম": "ম", "বু": "বু",


           "বৃ": "বৃ", "শু": "শু", "শ": "শ",


           "ৰা": "ৰা", "কে": "কে", "লং": "লং"},


    'bn': {"ৰ": "র", "চ": "চ", "ম": "ম", "বু": "বু",


           "বৃ": "বৃ", "শু": "শু", "শ": "শ",


           "ৰা": "রা", "কে": "কে", "লং": "লং"},


    'hi': {"ৰ": "सू", "চ": "चं", "ম": "मं", "বু": "बु",


           "বৃ": "बृ", "শু": "शु", "শ": "श",


           "ৰা": "रा", "কে": "के", "লং": "ल"},


    'en': {"ৰ": "Su", "চ": "Mo", "ম": "Ma", "বু": "Me",


           "বৃ": "Ju", "শু": "Ve", "শ": "Sa",


           "ৰা": "Ra", "কে": "Ke", "লং": "As"},


}





KUNDLI_RASI_NAMES_I18N = {


    'as': ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"],


    'bn': ["মেষ", "বৃষ", "মিথুন", "কর্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকর", "কুম্ভ", "মীন"],


    'hi': ["मेष", "वृष", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"],


    'en': ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],


}





KUNDLI_RASI_NUMBERS_I18N = {


    'as': ["১", "২", "৩", "৪", "৫", "৬", "৭", "৮", "৯", "১০", "১১", "১২"],


    'bn': ["১", "২", "৩", "৪", "৫", "৬", "৭", "৮", "৯", "১০", "১১", "১২"],


    'hi': ["१", "२", "३", "४", "५", "६", "७", "८", "९", "१०", "११", "१२"],


    'en': ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],


}





def get_kundli_planet_name_i18n(short_code, lang='as'):


    """Get kundli planet full name in the specified language."""


    return KUNDLI_PLANET_NAMES_I18N.get(lang, KUNDLI_PLANET_NAMES_I18N['as']).get(short_code, short_code)





def get_kundli_planet_short_i18n(short_code, lang='as'):


    """Get kundli planet short display in the specified language."""


    return KUNDLI_PLANET_SHORT_I18N.get(lang, KUNDLI_PLANET_SHORT_I18N['as']).get(short_code, short_code)





def get_kundli_rashi_name_i18n(index, lang='as'):


    """Get kundli rashi name in the specified language."""


    names = KUNDLI_RASI_NAMES_I18N.get(lang, KUNDLI_RASI_NAMES_I18N['as'])


    if 0 <= index < len(names):


        return names[index]


    return str(index)





def get_kundli_rashi_number_i18n(index, lang='as'):


    """Get kundli rashi number in the specified language."""


    nums = KUNDLI_RASI_NUMBERS_I18N.get(lang, KUNDLI_RASI_NUMBERS_I18N['as'])


    if 0 <= index < len(nums):


        return nums[index]


    return str(index + 1)








# ═══════════════════════════════════════════════════════════════


#  JOTOK MILAN (Marriage Matching) - i18n Labels


# ═══════════════════════════════════════════════════════════════





JOTOK_LABELS = {


    'as': {


        'title': 'যোটক মিলন', 'title_sub': 'অষ্টকূট গুণ মিলন',


        'boy_label': 'পাত্ৰ', 'girl_label': 'পাত্ৰী',


        'rashi': 'ৰাশি', 'nakshatra': 'নক্ষত্ৰ', 'charan': 'চৰণ', 'lagna': 'লগ্ন',


        'mars_house': 'মঙ্গল', 'mars_house_unit': 'ম ঘৰ',


        'mangalik': 'মাংগলিক', 'not_mangalik': 'অমাংগলিক',


        'total_guna': 'সৰ্বমুঠ গুণ',


        'summary_heading': 'অষ্টকূট গুণ মিলন - সাৰাংশ',


        'detail_heading': 'অষ্টকূটৰ সবিশেষ বিশ্লেষণ',


        'mangalik_heading': 'মাংগলিক দোষ (কূজ দোষ) বিচাৰ',


        'koota_names': {'varna': 'বৰ্ণ কূট', 'vashya': 'বশ্য কূট', 'tara': 'তাৰা কূট', 'yoni': 'যোনি কূট', 'graha_maitri': 'গ্ৰহ মৈত্ৰী কূট', 'gana': 'গণ কূট', 'bhakoot': 'ভকূট কূট', 'nadi': 'নাড়ী কূট'},


        'koota_icons': {'varna': '🕉️', 'vashya': '💑', 'tara': '⭐', 'yoni': '💕', 'graha_maitri': '🪐', 'gana': '🎭', 'bhakoot': '🏠', 'nadi': '🧬'},


        'score': 'প্ৰাপ্ত', 'max_score': 'সৰ্বোচ্চ', 'status': 'স্থিতি', 'order': 'ক্ৰম', 'koota_name': 'কূটৰ নাম',


        'varna_names': {1: 'ব্ৰাহ্মণ', 2: 'ক্ষত্ৰিয়', 3: 'বৈশ্য', 4: 'শূদ্ৰ'},


        'vashya_names': {1: 'চতুষ্পদ', 2: 'মানৱ', 3: 'জলচৰ', 4: 'বনচৰ', 5: 'কীট'},


        'tara_names': {1: 'জন্ম', 2: 'সম্পদ', 3: 'বিপদ', 4: 'ক্ষেম', 5: 'প্ৰত্যৰি', 6: 'সাধক', 7: 'বধ', 8: 'মিত্ৰ', 9: 'অতি মিত্ৰ'},


        'gana_names': {1: 'দেৱ', 2: 'মনুষ্য', 3: 'ৰাক্ষস'},


        'nadi_names': {1: 'আদি', 2: 'মধ্য', 3: 'অন্ত্য'},


        # Reverse mappings: Assamese string → target language


        'varna_rev': {'ব্ৰাহ্মণ': 'ব্ৰাহ্মণ', 'ক্ষত্ৰিয়': 'ক্ষত্ৰিয়', 'বৈশ্য': 'বৈশ্য', 'শূদ্ৰ': 'শূদ্ৰ'},


        'vashya_rev': {'চতুষ্পদ': 'চতুষ্পদ', 'মানৱ': 'মানৱ', 'জলচৰ': 'জলচৰ', 'বনচৰ': 'বনচৰ', 'কীট': 'কীট'},


        'yoni_rev': {'অশ্ব': 'অশ্ব', 'গজ': 'গজ', 'মেষ': 'মেষ', 'সৰ্প': 'সৰ্প', 'শ্বান': 'শ্বান', 'মাৰ্জাৰ': 'মাৰ্জাৰ', 'মূষিক': 'মূষিক', 'গো': 'গো', 'মহিষ': 'মহিষ', 'ব্যাঘ্ৰ': 'ব্যাঘ্ৰ', 'মৃগ': 'মৃগ', 'বানৰ': 'বানৰ', 'নকুল': 'নকুল', 'সিংহ': 'সিংহ'},


        'lord_rev': {'সূৰ্য': 'সূৰ্য', 'চন্দ্ৰ': 'চন্দ্ৰ', 'মংগল': 'মংগল', 'বুধ': 'বুধ', 'বৃহস্পতি': 'বৃহস্পতি', 'শুক্ৰ': 'শুক্ৰ', 'শনি': 'শনি'},


        'gana_rev': {'দেৱ': 'দেৱ', 'মনুষ্য': 'মনুষ্য', 'ৰাক্ষস': 'ৰাক্ষস'},


        'nadi_rev': {'আদি': 'আদি', 'মধ্য': 'মধ্য', 'অন্ত্য': 'অন্ত্য'},


'rashi_rev': {'মেষ': 'মেষ', 'বৃষ': 'বৃষ', 'মিথুন': 'মিথুন', 'কৰ্কট': 'কৰ্কট', 'সিংহ': 'সিংহ', 'কন্যা': 'কন্যা', 'তুলা': 'তুলা', 'বৃশ্চিক': 'বৃশ্চিক', 'ধনু': 'ধনু', 'মকৰ': 'মকৰ', 'কুম্ভ': 'কুম্ভ', 'মীন': 'মীন'},


        'nakshatra_rev': {'অশ্বিনী': 'অশ্বিনী', 'ভৰণী': 'ভৰণী', 'কৃত্তিকা': 'কৃত্তিকা', 'ৰোহিণী': 'ৰোহিণী', 'মৃগশিৰা': 'মৃগশিৰা', 'আৰ্দ্ৰা': 'আৰ্দ্ৰা', 'পুনৰ্বসু': 'পুনৰ্বসু', 'পুষ্যা': 'পুষ্যা', 'অশ্লেষা': 'অশ্লেষা', 'মঘা': 'মঘা', 'পূৰ্বফাল্গুনী': 'পূৰ্বফাল্গুনী', 'উত্তৰফাল্গুনী': 'উত্তৰফাল্গুনী', 'হস্তা': 'হস্তা', 'চিত্ৰা': 'চিত্ৰা', 'স্বাতী': 'স্বাতী', 'বিশাখা': 'বিশাখা', 'অনুৰাধা': 'অনুৰাধা', 'জ্যেষ্ঠা': 'জ্যেষ্ঠা', 'মূল': 'মূল', 'পূৰ্বাষাঢ়া': 'পূৰ্বাষাঢ়া', 'উত্তৰাষাঢ়া': 'উত্তৰাষাঢ়া', 'শ্ৰৱণা': 'শ্ৰৱণা', 'ধনিষ্ঠা': 'ধনিষ্ঠা', 'শতভিষা': 'শতভিষা', 'পূৰ্বভাদ্ৰপদ': 'পূৰ্বভাদ্ৰপদ', 'উত্তৰভাদ্ৰপদ': 'উত্তৰভাদ্ৰপদ', 'ৰেৱতী': 'ৰেৱতী'},


        'verdict_excellent': 'উত্তম (অতি শুভ)', 'verdict_good': 'মধ্যম (শুভ)', 'verdict_average': 'মধ্যম (গ্ৰহণযোগ্য)', 'verdict_warning': 'অমিল (সাৱধানতা প্ৰয়োজন)', 'verdict_bad': 'অশুভ (বিবাহ পৰামৰ্শিত নহয়)',


        'guna': 'গুণ', 'boy': 'পাত্ৰ', 'girl': 'পাত্ৰী',


        'mangalik_both': 'পাত্ৰ আৰু পাত্ৰী উভয়ে মাংগলিক - দোষ সাম্য। উভয়ৰে মাংগলিক দোষ পৰস্পৰে নিষ্ক্ৰিয় কৰে। ই বিবাহৰ বাবে এক সুখবৰ!',


        'mangalik_boy': 'পাত্ৰ মাংগলিক কিন্তু পাত্ৰী অমাংগলিক। মাংগলিক দোষ নিবাৰণৰ বাবে প্ৰতিকাৰ কৰাটো জৰুৰী।',


        'mangalik_girl': 'পাত্ৰী মাংগলিক কিন্তু পাত্ৰ অমাংগলিক। মাংগলিক দোষ নিবাৰণৰ বাবে প্ৰতিকাৰ কৰাটো জৰুৰী।',


        'mangalik_none': 'পাত্ৰ আৰু পাত্ৰী উভয়ে অমাংগলিক। মাংগলিক দোষ নাই। ই বিবাহৰ বাবে শুভ!',


        'mars_in_house': 'মঙ্গল', 'house_suffix': 'ম ঘৰ',


        'download_pdf': 'PDF ডাউনলোড কৰক', 'new_matching': 'নতুন যোটক মিলন বিচাৰ কৰক',


        'profile_info': 'বিৱৰণ', 'moon_sign': 'ৰাশি (Moon Sign)', 'charan_pada': 'চৰণ / পাদ', 'mars_position': 'মঙ্গলৰ অৱস্থান',


        'charan_unit': 'ম চৰণ',


        # Koota detailed descriptions (Assamese)


        'koota_descriptions': {


            'varna': {


                'title': '১। বৰ্ণ কূট - আধ্যাত্মিক আৰু মানসিক সামঞ্জস্য',


                'good': 'পাত্ৰ-পাত্ৰীৰ আধ্যাত্মিক আৰু মানসিক সামঞ্জস্য অতি উত্তম। পাত্ৰৰ বৰ্ণ পাত্ৰীতকৈ উচ্চ বা সমান হোৱাৰ বাবে ই এক সুস্থ আৰু সন্তুলিত দাম্পত্য জীৱনৰ ইংগিত দিয়ে। তেওঁলোকৰ মাজত পাৰস্পৰিক শ্ৰদ্ধা, বুজাবুজি আৰু আধ্যাত্মিক চিন্তাৰ মিল থাকিব।',


                'mid': 'পাত্ৰ-পাত্ৰীৰ মাজত বৰ্ণৰ পাৰ্থক্য আছে। যদি পাত্ৰীৰ বৰ্ণ পাত্ৰতকৈ উচ্চ হয়, তেন্তে দাম্পত্য জীৱনত কেতিয়াবা মানসিক দূৰত্ব আৰু অহংকাৰৰ সংঘাত হ\'ব পাৰে। পাৰস্পৰিক শ্ৰদ্ধা আৰু বুজাবুজিৰ দ্বাৰা এই অমিল দূৰ কৰিব পাৰি।',


                'bad': 'পাত্ৰ-পাত্ৰীৰ মাজত গুৰুত্বপূৰ্ণ বৰ্ণ অমিল আছে। ইয়াৰ ফলত দাম্পত্য জীৱনত মানসিক দূৰত্ব আৰু সংঘাত হ\'ব পাৰে। আধ্যাত্মিক অভ্যাস আৰু পাৰস্পৰিক বুজাবুজিৰ দ্বাৰা এই অমিল দূৰ কৰিব পাৰি।',


                'pred_good': '<strong>শুভ ফল:</strong> পাত্ৰ-পাত্ৰীৰ বৰ্ণগত সামঞ্জস্য অত্যন্ত উত্তম। পাত্ৰৰ বৰ্ণ পাত্ৰীতকৈ উচ্চ বা সমান হোৱাৰ বাবে ই এক সুস্থ আৰু সমতাপূৰ্ণ দাম্পত্য সম্পৰ্কৰ ইংগিত দিয়ে। ইয়াৰ অৰ্থ হ\'ল যে তেওঁলোকৰ মাজত পাৰস্পৰিক শ্ৰদ্ধা, বুজাবুজি আৰু আধ্যাত্মিক চিন্তাধাৰাৰ মিল থাকিব। তেওঁলোকৰ মানসিক স্তৰ একে হোৱাৰ বাবে জীৱনৰ গুৰুত্বপূৰ্ণ সিদ্ধান্তসমূহত সহমতত উপনীত হ\'ব পাৰিব। ই দাম্পত্য জীৱনক শক্তিশালী কৰে আৰু পৰিয়ালত শান্তি বজাই ৰাখে।',


                'pred_mid': '<strong>সাৱধানতা:</strong> পাত্ৰ-পাত্ৰীৰ বৰ্ণগত অমিল আছে। পাত্ৰীৰ বৰ্ণ পাত্ৰতকৈ উচ্চ হোৱাৰ বাবে দাম্পত্য জীৱনত কেতিয়াবা মানসিক দূৰত্ব আৰু অহংকাৰৰ সংঘাত হ\'ব পাৰে। জীৱনৰ গুৰুত্বপূৰ্ণ সিদ্ধান্তত মতভেদৰ সম্ভাৱনা থাকে। তথাপিও, পাৰস্পৰিক শ্ৰদ্ধা আৰু বুজাবুজিৰ দ্বাৰা এই অমিল সহজে অতিক্ৰম কৰিব পাৰি। আধ্যাত্মিক চৰ্চা আৰু ধ্যানৰ দ্বাৰা মানসিক সমতা আনিব পাৰি।',


                'pred_bad': '<strong>সাৱধানতা:</strong> পাত্ৰ-পাত্ৰীৰ বৰ্ণগত অমিল গুৰুতৰ। দাম্পত্য জীৱনত মানসিক দূৰত্ব আৰু সংঘাতৰ অধিক সম্ভাৱনা আছে। আধ্যাত্মিক অভ্যাস আৰু পাৰস্পৰিক বুজাবুজিৰ দ্বাৰা এই অমিল দূৰ কৰিব লাগিব। বিশেষ পূজা-অৰ্চনা আৰু জ্যোতিষীৰ পৰামৰ্শ লোৱা উচিত হ\'ব।'


            },


            'vashya': {


                'title': '২। বশ্য কূট - পৰস্পৰ আকৰ্ষণ আৰু নিয়ন্ত্ৰণ',


                'good': 'বশ্য কূটত পূৰ্ণ গুণ - তেওঁলোকৰ মাজত গভীৰ পৰস্পৰ আকৰ্ষণ আৰু প্ৰভাৱৰ সম্পৰ্ক আছে। তেওঁলোকৰ মাজত এক স্বাভাৱিক চুম্বকীয় আকৰ্ষণ থাকিব যিয়ে দাম্পত্য জীৱনক গভীৰ আৰু প্ৰগাঢ় কৰি ৰাখিব।',


                'mid': 'বশ্য কূটত আংশিক মিল আছে। পৰস্পৰ বুজাবুজি আৰু শ্ৰদ্ধাৰ দ্বাৰা ভাৰসাম্য বজাই ৰাখিব পাৰি।',


                'bad': 'বশ্য কূটত অমিল আছে। স্বাভাৱিক আকৰ্ষণৰ অভাৱ হ\'ব পাৰে। ইজনে সিজনৰ প্ৰতি সহনশীলতা বৃদ্ধি কৰা উচিত।',


                'pred_good': '<strong>শুভ ফল:</strong> বশ্য কূটত পূৰ্ণ গুণ প্ৰাপ্ত হোৱাৰ বাবে গভীৰ পৰস্পৰ আকৰ্ষণ আৰু প্ৰভাৱৰ সম্পৰ্ক সূচিত হয়। পাত্ৰ-পাত্ৰীৰ মাজত এক স্বাভাৱিক চুম্বকীয় আকৰ্ষণ থাকিব, যিয়ে তেওঁলোকৰ দাম্পত্য জীৱনক প্ৰগাঢ় কৰি ৰাখিব। তেওঁলোকে ইজনে সিজনৰ ওপৰত ইতিবাচক প্ৰভাৱ পেলাব আৰু জীৱনৰ প্ৰত্যাহ্বানসমূহ একেলগে মোকাবিলা কৰিব। ই এক সুখী আৰু স্থায়ী বিবাহৰ বাবে অত্যন্ত শুভ লক্ষণ।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> বশ্য কূটত আংশিক মিল আছে। পাত্ৰ-পাত্ৰীৰ মাজত আকৰ্ষণ আছে কিন্তু পূৰ্ণ পৰস্পৰ প্ৰভাৱ নাথাকিব। কোনো এজনৰ প্ৰভাৱ আনজনৰ ওপৰত অধিক হ\'ব পাৰে। ইয়াৰ ফলস্বৰূপে দাম্পত্য জীৱনত কেতিয়াবা ভাৰসাম্যহীনতা আহিব পাৰে। পাৰস্পৰিক বুজাবুজি আৰু শ্ৰদ্ধাৰ দ্বাৰা এই স্থিতিৰ সমাধান সম্ভৱ।',


                'pred_bad': '<strong>সাৱধানতা:</strong> বশ্য কূটত অমিল আছে। পাত্ৰ-পাত্ৰীৰ মাজত স্বাভাৱিক আকৰ্ষণৰ অভাৱ হ\'ব পাৰে। তেওঁলোকৰ ব্যক্তিত্ব আৰু জীৱনশৈলীৰ পাৰ্থক্যই দাম্পত্য জীৱনত সংঘাতৰ সৃষ্টি কৰিব পাৰে। ইজনে সিজনৰ প্ৰতি সহনশীলতা বৃদ্ধি কৰা আৰু একেলগে সময় কটোৱাৰ অভ্যাস গঢ়ি তোলা উচিত।'


            },


            'tara': {


                'title': '৩। তাৰা কূট - ভাগ্য, স্বাস্থ্য আৰু মংগল',


                'good': 'তাৰা কূটত পূৰ্ণ গুণ - অত্যন্ত শুভ! দাম্পত্য জীৱনত ভাগ্যৰ সহায় পোৱা যাব। স্বাস্থ্য সুৰক্ষিত থাকিব।',


                'mid': 'তাৰা কূটত মধ্যম গুণ। দাম্পত্য জীৱনত কিছু উত্থান-পতন হ\'ব পাৰে। সাৱধানতা অৱলম্বন কৰক।',


                'bad': 'তাৰা কূটত অশুভ গুণ - বিপদ বা নৈধন তাৰা। স্বাস্থ্য সম্পৰ্কীয় সমস্যা বা অপ্ৰত্যাশিত বিপদৰ সম্ভাৱনা। বিশেষ পূজা-অৰ্চনা আৰু সাৱধানতাৰ প্ৰয়োজন।',


                'pred_good': '<strong>শুভ ফল:</strong> তাৰা কূটত পূৰ্ণ গুণ - অত্যন্ত শুভ! পাত্ৰৰ নক্ষত্ৰৰ পৰা পাত্ৰীৰ নক্ষত্ৰলৈ দূৰত্ব শুভ তাৰাত আছে। ইয়াৰ অৰ্থ হ\'ল যে তেওঁলোকৰ দাম্পত্য জীৱনত ভাগ্যৰ সহায় পোৱা যাব। স্বাস্থ্যৰ ক্ষেত্ৰত ই অত্যন্ত শুভ - দুয়োৰে আয়ুস আৰু স্বাস্থ্য সুৰক্ষিত থাকিব। জীৱনৰ সংকটত তেওঁলোকে ঐশ্বৰিক সহায় লাভ কৰিব। ই এক অত্যন্ত মংগলময় দাম্পত্য জীৱনৰ ইংগিত।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> তাৰা কূটত মধ্যম গুণ - জন্ম বা প্ৰত্যৰি তাৰা। ইয়াৰ অৰ্থ হ\'ল যে দাম্পত্য জীৱনত কিছু উত্থান-পতন হ\'ব পাৰে। স্বাস্থ্যৰ ক্ষেত্ৰত সাৱধানতা অৱলম্বন কৰা উচিত। নিয়মিত স্বাস্থ্য পৰীক্ষা আৰু সন্তুলিত জীৱনশৈলীৰ দ্বাৰা এই প্ৰভাৱ নিয়ন্ত্ৰণ কৰিব পাৰি। ভাগ্যৰ সহায় কিছু পৰিমাণে পোৱা যাব।',


                'pred_bad': '<strong>অশুভ ফল:</strong> তাৰা কূটত অশুভ গুণ - বিপদ বা নৈধন তাৰা। ইয়াৰ অৰ্থ হ\'ল যে দাম্পত্য জীৱনত স্বাস্থ্য সম্পৰ্কীয় সমস্যা বা অপ্ৰত্যাশিত সংকট আহিব পাৰে। বিশেষকৈ বিবাহৰ প্ৰাৰম্ভিক বছৰসমূহত সাৱধানতা অৱলম্বন কৰা উচিত। নিয়মিত পূজা-অৰ্চনা, দান-পুণ্য আৰু স্বাস্থ্যৰ যত্ন লোৱাৰ দ্বাৰা এই অশুভ প্ৰভাৱ হ্ৰাস কৰিব পাৰি।'


            },


            'yoni': {


                'title': '৪। যোনি কূট - শাৰীৰিক সামঞ্জস্য আৰু জৈৱিক সমতা',


                'good': 'যোনি কূটত উৎকৃষ্ট গুণ। শাৰীৰিক আৰু জৈৱিক স্তৰত গভীৰ সামঞ্জস্য আছে। দাম্পত্য জীৱন প্ৰেম আৰু ঘনিষ্ঠতাৰে পৰিপূৰ্ণ হ\'ব।',


                'mid': 'যোনি কূটত মধ্যম গুণ। শাৰীৰিক সম্পৰ্কত কিছু পাৰ্থক্য থাকিব পাৰে, কিন্তু প্ৰেমৰ দ্বাৰা অতিক্ৰম কৰিব পাৰি।',


                'bad': 'যোনি কূটত অমিল - শত্ৰু যোনি। শাৰীৰিক সম্পৰ্কত গুৰুতৰ অমিল হ\'ব পাৰে। বিশেষ পূজা-অৰ্চনাৰ পৰামৰ্শ দিয়া হয়।',


                'pred_good': '<strong>শুভ ফল:</strong> যোনি কূটত সৰ্বোচ্চ গুণ - পাত্ৰ-পাত্ৰীৰ একেই যোনি! ই অত্যন্ত বিৰল আৰু অত্যন্ত শুভ। ইয়াৰ অৰ্থ হ\'ল যে তেওঁলোকৰ মাজত শাৰীৰিক আৰু জৈৱিক স্তৰত গভীৰ সামঞ্জস্য থাকিব। তেওঁলোকৰ দাম্পত্য জীৱন প্ৰেম, ঘনিষ্ঠতা আৰু পৰস্পৰ আকৰ্ষণেৰে পৰিপূৰ্ণ হ\'ব। সন্তান সুখৰ ক্ষেত্ৰতো ই অত্যন্ত শুভ। তেওঁলোকৰ মাজত এক স্বাভাৱিক বুজাবুজি থাকিব যিয়ে সম্পৰ্কক দীৰ্ঘস্থায়ী কৰি ৰাখিব।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> যোনি কূটত মধ্যম গুণ। পাত্ৰ-পাত্ৰীৰ যোনি সম্পৰ্ক স্বাভাৱিক - বিশেষ মিত্ৰতাও নাই, শত্ৰুতাও নাই। শাৰীৰিক সম্পৰ্কত কিছু পাৰ্থক্য থাকিব পাৰে তথাপিও পাৰস্পৰিক বুজাবুজি আৰু প্ৰেমৰ দ্বাৰা ইয়াক অতিক্ৰম কৰিব পাৰি।',


                'pred_bad': '<strong>অশুভ ফল:</strong> যোনি কূটত অমিল - শত্ৰু যোনি। পাত্ৰ-পাত্ৰীৰ যোনি ইজনে সিজনৰ শত্ৰু হোৱাৰ বাবে শাৰীৰিক সম্পৰ্কত গুৰুতৰ অমিল হ\'ব। ইয়াৰ ফলস্বৰূপে দাম্পত্য জীৱনত অসন্তুষ্টি আৰু দূৰত্ব আহিব পাৰে। সন্তানৰ ক্ষেত্ৰতো সমস্যা হ\'ব পাৰে। বিশেষ পূজা-অৰ্চনা আৰু জ্যোতিষীৰ পৰামৰ্শ লোৱা উচিত।'


            },


            'graha_maitri': {


                'title': '৫। গ্ৰহ মৈত্ৰী কূট - মানসিক স্বভাৱ আৰু গ্ৰহগত মিত্ৰতা',


                'good': 'গ্ৰহ মৈত্ৰী কূটত উৎকৃষ্ট গুণ। দুয়োৰে ৰাশি অধিপতি গ্ৰহ পৰস্পৰৰ ভাল মিত্ৰ বা একেই। মানসিক স্বভাৱ আৰু চিন্তাধাৰাত ভাল মিল থাকিব।',


                'mid': 'গ্ৰহ মৈত্ৰী কূটত মধ্যম গুণ। মানসিক স্বভাৱত কিছু পাৰ্থক্য থাকিব পাৰে কিন্তু গুৰুতৰ সংঘাত নহয়।',


                'bad': 'গ্ৰহ মৈত্ৰী কূটত অমিল - ৰাশি অধিপতি শত্ৰু। মানসিক স্বভাৱত গুৰুত্বপূৰ্ণ পাৰ্থক্য থাকিব। মতভেদৰ অধিক সম্ভাৱনা আছে।',


                'pred_good': '<strong>শুভ ফল:</strong> গ্ৰহ মৈত্ৰী কূটত সৰ্বোচ্চ গুণ! পাত্ৰ-পাত্ৰীৰ ৰাশিৰ অধিপতি গ্ৰহ পৰস্পৰৰ পৰম মিত্ৰ বা একেই গ্ৰহ। ইয়াৰ অৰ্থ হ\'ল যে তেওঁলোকৰ মানসিক স্বভাৱ, চিন্তাধাৰা আৰু জীৱনৰ প্ৰতি দৃষ্টিভংগী অত্যন্ত মিলে। তেওঁলোকে ইজনে সিজনক সহজে বুজিব আৰু জীৱনৰ প্ৰত্যাহ্বানসমূহ একেলগে মোকাবিলা কৰিব। ই দাম্পত্য জীৱনৰ বাবে এক অত্যন্ত শক্তিশালী আধাৰ।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> গ্ৰহ মৈত্ৰী কূটত মধ্যম গুণ - ৰাশি অধিপতি গ্ৰহ পৰস্পৰৰ সম (neutral)। তেওঁলোকৰ মানসিক স্বভাৱত কিছু পাৰ্থক্য থাকিব পাৰে তথাপিও গুৰুতৰ সংঘাত নহয়। পাৰস্পৰিক বুজাবুজি বৃদ্ধিৰ বাবে একেলগে সময় কটোৱা আৰু কথা-বতৰা হোৱা উচিত।',


                'pred_bad': '<strong>অশুভ ফল:</strong> গ্ৰহ মৈত্ৰী কূটত অমিল - ৰাশি অধিপতি গ্ৰহ পৰস্পৰৰ শত্ৰু। তেওঁলোকৰ মানসিক স্বভাৱ আৰু চিন্তাধাৰাত গুৰুতৰ পাৰ্থক্য থাকিব। দাম্পত্য জীৱনত মতভেদ আৰু কন্দলৰ অধিক সম্ভাৱনা আছে। পাৰস্পৰিক সহনশীলতা আৰু বুজাবুজি বৃদ্ধিৰ বাবে প্ৰচেষ্টা কৰা উচিত।'


            },


            'gana': {


                'title': '৬। গণ কূট - স্বভাৱগত মিল আৰু আচৰণ',


                'good': 'গণ কূটত উৎকৃষ্ট গুণ। স্বভাৱ, আচৰণ আৰু জীৱনশৈলীত ভাল মিল আছে। দাম্পত্য জীৱনত সংঘাতৰ পৰিমাণ নূন্যতম হ\'ব।',


                'mid': 'গণ কূটত মধ্যম গুণ। স্বভাৱৰ পাৰ্থক্যই কেতিয়াবা সংঘাতৰ সৃষ্টি কৰিব পাৰে। পাৰস্পৰিক বুজাবুজি আৱশ্যক।',


                'bad': 'গণ কূটত অমিল। স্বভাৱত গুৰুত্বপূৰ্ণ পাৰ্থক্য আছে। দাম্পত্য জীৱনত সংঘাতৰ অধিক সম্ভাৱনা আছে। জ্যোতিষীৰ পৰামৰ্শ লওক।',


                'pred_good': '<strong>শুভ ফল:</strong> গণ কূটত সৰ্বোচ্চ গুণ - পাত্ৰ-পাত্ৰীৰ একেই গণ! তেওঁলোকৰ স্বভাৱ, আচৰণ আৰু জীৱনশৈলী অত্যন্ত মিলে। ইয়াৰ ফলস্বৰূপে তেওঁলোকৰ মাজত স্বাভাৱিক বুজাবুজি থাকিব আৰু দাম্পত্য জীৱনত সংঘাতৰ পৰিমাণ নূন্যতম হ\'ব। একেলগে জীৱন কটোৱাটো তেওঁলোকৰ বাবে সহজ আৰু আনন্দময় হ\'ব।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> গণ কূটত মধ্যম গুণ - দেৱ-মনুষ্য সম্পৰ্ক। পাত্ৰ-পাত্ৰীৰ স্বভাৱত ভাল সামঞ্জস্য আছে। দেৱ গণৰ ব্যক্তি আধ্যাত্মিক আৰু শান্ত প্ৰকৃতিৰ, আনহাতে মনুষ্য গণৰ ব্যক্তি বাস্তৱবাদী আৰু কৰ্মঠ। এই মিশ্ৰণে দাম্পত্য জীৱনত এক সুস্থ সন্তুলন আনিব।',


                'pred_bad': '<strong>অশুভ ফল:</strong> গণ কূটত অমিল - দেৱ-ৰাক্ষস সম্পৰ্ক। স্বভাৱত অত্যন্ত গুৰুত্বপূৰ্ণ পাৰ্থক্য আছে। দেৱ গণৰ শান্ত আৰু আধ্যাত্মিক প্ৰকৃতি ৰাক্ষস গণৰ তীব্ৰ আৰু আক্ৰমণাত্মক প্ৰকৃতিৰ সৈতে খাপ নাখাব পাৰে। দাম্পত্য জীৱনত গুৰুতৰ সংঘাতৰ সম্ভাৱনা আছে। জ্যোতিষীৰ পৰামৰ্শ আৰু বিশেষ প্ৰতিকাৰৰ প্ৰয়োগৰ আৱশ্যক।'


            },


            'bhakoot': {


                'title': '৭। ভকূট কূট - পাৰিবাৰিক কল্যাণ আৰু সমৃদ্ধি',


                'good': 'ভকূট কূটত পূৰ্ণ গুণ - কোনো ভকূট দোষ নাই! পাৰিবাৰিক কল্যাণ, আৰ্থিক সমৃদ্ধি আৰু সুখ-শান্তি বিৰাজ কৰিব।',


                'mid': 'ভকূট কূটত মধ্যম গুণ। পাৰিবাৰিক জীৱনত কিছু উত্থান-পতন হ\'ব পাৰে।',


                'bad': 'ভকূট কূটত দোষ উপস্থিত! পাৰিবাৰিক অশান্তি আৰু আৰ্থিক সংকটৰ সম্ভাৱনা। ভকূট দোষ নিবাৰণৰ প্ৰতিকাৰ কৰক।',


                'pred_good': '<strong>শুভ ফল:</strong> ভকূট কূটত পূৰ্ণ গুণ - কোনো ভকূট দোষ নাই! ইয়াৰ অৰ্থ হ\'ল যে পাত্ৰ-পাত্ৰীৰ দাম্পত্য জীৱনত পাৰিবাৰিক কল্যাণ, আৰ্থিক সমৃদ্ধি আৰু সুখ-শান্তি বিৰাজ কৰিব। তেওঁলোকৰ সংসাৰ ধন-ধান্যেৰে পৰিপূৰ্ণ হ\'ব আৰু পৰিয়ালত আনন্দৰ পৰিৱেশ থাকিব। ই বিবাহৰ বাবে অত্যন্ত শুভ লক্ষণ।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> ভকূট কূটত মধ্যম গুণ। পাৰিবাৰিক জীৱনত কিছু উত্থান-পতন হ\'ব পাৰে কিন্তু গুৰুতৰ সংকট নহয়। আৰ্থিক স্থিৰতাৰ বাবে প্ৰচেষ্টা কৰা উচিত। পৰিয়ালৰ সদস্যসকলৰ মাজত বুজাবুজি বৃদ্ধিৰ বাবে পাৰিবাৰিক আলোচনা আৰু একেলগে সময় কটোৱা গুৰুত্বপূৰ্ণ।',


                'pred_bad': '<strong>অশুভ ফল:</strong> ভকূট কূটত {{ result.kootas.bhakoot.result }} দোষ উপস্থিত! ইয়াৰ অৰ্থ হ\'ল যে দাম্পত্য জীৱনত পাৰিবাৰিক অশান্তি, আৰ্থিক সংকট আৰু মানসিক অস্থিৰতা আহিব পাৰে। বিশেষকৈ বিবাহৰ প্ৰাৰম্ভিক বছৰসমূহত সাৱধানতা অৱলম্বন কৰা উচিত। ভকূট দোষ নিবাৰণৰ বাবে বিশেষ পূজা-অৰ্চনা আৰু জ্যোতিষীৰ পৰামৰ্শ লোৱা অত্যন্ত আৱশ্যক।'


            },


            'nadi': {


                'title': '৮। নাড়ী কূট - সন্তান সুখ আৰু জিনগত স্বাস্থ্য',


                'good': 'নাড়ী কূটত পূৰ্ণ গুণ - নাড়ী দোষ সম্পূৰ্ণৰূপে অনুপস্থিত! সন্তান সুখ অত্যন্ত শুভ। সুস্থ আৰু বুদ্ধিমান সন্তান প্ৰাপ্ত হ\'ব।',


                'bad': 'নাড়ী কূটত অমিল - নাড়ী দোষ উপস্থিত! সন্তানৰ ক্ষেত্ৰত সমস্যা আৰু স্বাস্থ্য সম্পৰ্কীয় জটিলতাৰ সম্ভাৱনা। নাড়ী দোষ নিবাৰণৰ বাবে বিশেষ পূজা আৰু জ্যোতিষীৰ পৰামৰ্শ অত্যন্ত আৱশ্যক।',


                'pred_good': '<strong>শুভ ফল:</strong> নাড়ী কূটত পূৰ্ণ গুণ - নাড়ী দোষ সম্পূৰ্ণৰূপে অনুপস্থিত! সন্তান সুখ অত্যন্ত শুভ। সুস্থ আৰু বুদ্ধিমান সন্তান প্ৰাপ্ত হ\'ব। জীৱনত ইতিবাচক শক্তি আৰু উৎসাহ বিৰাজ কৰিব। ই দাম্পত্য জীৱন আৰু সন্তানৰ বাবে অত্যন্ত মংগলকাৰী।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> নাড়ী কূটত মধ্যম গুণ - নাড়ী দোষ আংশিকভাৱে উপস্থিত। সন্তান সুখৰ সম্ভাৱনা কম হ\'ব পাৰে। বিশেষ পূজা-অৰ্চনা আৰু জ্যোতিষীৰ পৰামৰ্শৰ দ্বাৰা এই দোষ হ্ৰাস কৰিব পাৰি।',


                'pred_bad': '<strong>অশুভ ফল:</strong> নাড়ী কূটত অমিল - নাড়ী দোষ উপস্থিত! সন্তানৰ ক্ষেত্ৰত সমস্যা আৰু স্বাস্থ্য সম্পৰ্কীয় জটিলতাৰ অধিক সম্ভাৱনা আছে। নাড়ী দোষ নিবাৰণৰ বাবে বিশেষ পূজা আৰু জ্যোতিষীৰ পৰামৰ্শ অত্যন্ত আৱশ্যক। সময়মতে উচিত প্ৰতিকাৰৰ দ্বাৰা এই দোষ হ্ৰাস কৰিব পাৰি।'


            }


        },


        # Description templates (with {boy_*} and {girl_*} placeholders)


        'description_templates': {


            'varna': '{boy_label}ৰ বৰ্ণ {boy_varna} আৰু {girl_label}ৰ বৰ্ণ {girl_varna}।',


            'vashya': '{boy_label}ৰ বশ্য {boy_vashya} আৰু {girl_label}ৰ বশ্য {girl_vashya}।',


            'tara': '{girl_label}ৰ নক্ষত্ৰৰ পৰা {boy_label}ৰ নক্ষত্ৰলৈ তাৰা: {tara_girl_to_boy_name} ({tara_girl_to_boy}), {boy_label}ৰ পৰা {girl_label}লৈ তাৰা: {tara_boy_to_girl_name} ({tara_boy_to_girl})।',


            'yoni': "{boy_label}ৰ যোনি '{boy_yoni}' আৰু {girl_label}ৰ যোনি '{girl_yoni}'।",


            'graha_maitri': "{boy_label}ৰ ৰাশি অধিপতি '{boy_lord}' আৰু {girl_label}ৰ ৰাশি অধিপতি '{girl_lord}'।",


            'gana': "{boy_label}ৰ গণ '{boy_gana}' আৰু {girl_label}ৰ গণ '{girl_gana}'।",


            'bhakoot': "{girl_label}ৰ ৰাশি '{girl_rashi}' আৰু {boy_label}ৰ ৰাশি '{boy_rashi}'ৰ ভকূট মিলন।",


            'nadi': "{boy_label}ৰ নাড়ী '{boy_nadi}' আৰু {girl_label}ৰ নাড়ী '{girl_nadi}'।",


        },


        # Result mappings (Assamese engine result → display text)


        'result_map': {


            'উত্তম': 'উত্তম', 'মধ্যম': 'মধ্যম', 'অমিল': 'অমিল', 'অশুভ': 'অশুভ',


            'উত্তম (অতি শুভ)': 'উত্তম (অতি শুভ)',


            'উত্তম (একে যোনি)': 'উত্তম (একে যোনি)',


            'উত্তম (মিত্ৰ যোনি)': 'উত্তম (মিত্ৰ যোনি)',


            'মধ্যম (সাধাৰণ)': 'মধ্যম (সাধাৰণ)',


            'মধ্যম (সামান্য)': 'মধ্যম (সামান্য)',


            'অশুভ (শত্ৰু যোনি)': 'অশুভ (শত্ৰু যোনি)',


            'উত্তম (অধি মিত্ৰ)': 'উত্তম (অধি মিত্ৰ)',


            'উত্তম (মিত্ৰ)': 'উত্তম (মিত্ৰ)',


            'মধ্যম (সম)': 'মধ্যম (সম)',


            'অমিল (শত্ৰু)': 'অমিল (শত্ৰু)',


            'অমিল (অধি শত্ৰু)': 'অমিল (অধি শত্ৰু)',


            'অশুভ (অধি শত্ৰু)': 'অশুভ (অধি শত্ৰু)',


            'উত্তম (একে গণ)': 'উত্তম (একে গণ)',


            'অমিল (দেৱ-ৰাক্ষস)': 'অমিল (দেৱ-ৰাক্ষস)',


            'অমিল (মনুষ্য-ৰাক্ষস)': 'অমিল (মনুষ্য-ৰাক্ষস)',


            'উত্তম (নাড়ী দোষ নাই)': 'উত্তম (নাড়ী দোষ নাই)',


        },


        'verdict_map': {


            'উত্তম (অতি শুভ)': 'উত্তম (অতি শুভ)',


            'মধ্যম (শুভ)': 'মধ্যম (শুভ)',


            'মধ্যম (গ্ৰহণযোগ্য)': 'মধ্যম (গ্ৰহণযোগ্য)',


            'অমিল (সাৱধানতা প্ৰয়োজন)': 'অমিল (সাৱধানতা প্ৰয়োজন)',


            'অশুভ (বিবাহ পৰামৰ্শিত নহয়)': 'অশুভ (বিবাহ পৰামৰ্শিত নহয়)',


        },


        'verdict_desc_map': {


            'এই যোটক অতি উত্তম। বিবাহৰ বাবে অত্যন্ত শুভ আৰু সুপাৰিশিত। দাম্পত্য জীৱন সুখময়, সমৃদ্ধিশালী আৰু দীৰ্ঘস্থায়ী হ\'ব।': 'এই যোটক অতি উত্তম। বিবাহৰ বাবে অত্যন্ত শুভ আৰু সুপাৰিশিত। দাম্পত্য জীৱন সুখময়, সমৃদ্ধিশালী আৰু দীৰ্ঘস্থায়ী হ\'ব।',


            'এই যোটক মধ্যম শ্ৰেণীৰ। বিবাহৰ বাবে গ্ৰহণযোগ্য। সামান্য প্ৰতিকাৰৰ দ্বাৰা দাম্পত্য জীৱন সুখময় কৰিব পাৰি।': 'এই যোটক মধ্যম শ্ৰেণীৰ। বিবাহৰ বাবে গ্ৰহণযোগ্য। সামান্য প্ৰতিকাৰৰ দ্বাৰা দাম্পত্য জীৱন সুখময় কৰিব পাৰি।',


            'এই যোটক গড় মানৰ। কিছুমান দোষ থাকিলেও উপযুক্ত প্ৰতিকাৰৰ দ্বাৰা বিবাহ সম্ভৱ। জ্যোতিষীৰ পৰামৰ্শ লোৱাটো উচিত।': 'এই যোটক গড় মানৰ। কিছুমান দোষ থাকিলেও উপযুক্ত প্ৰতিকাৰৰ দ্বাৰা বিবাহ সম্ভৱ। জ্যোতিষীৰ পৰামৰ্শ লোৱাটো উচিত।',


            'এই যোটকত যথেষ্ট অমিল আছে। বিবাহৰ পূৰ্বে জ্যোতিষীৰ পৰামৰ্শ আৰু প্ৰতিকাৰ অতি জৰুৰী।': 'এই যোটকত যথেষ্ট অমিল আছে। বিবাহৰ পূৰ্বে জ্যোতিষীৰ পৰামৰ্শ আৰু প্ৰতিকাৰ অতি জৰুৰী।',


            'এই যোটক অশুভ। পৰম্পৰাগতভাৱে এনে যোটকত বিবাহ পৰামৰ্শিত নহয়। তথাপিও জ্যোতিষীৰ পৰামৰ্শ লওক।': 'এই যোটক অশুভ। পৰম্পৰাগতভাৱে এনে যোটকত বিবাহ পৰামৰ্শিত নহয়। তথাপিও জ্যোতিষীৰ পৰামৰ্শ লওক।',


        },


        'remedies': [


            'প্ৰতিদিন হনুমান চালিচা পাঠ কৰক',


            'মঙ্গলবাৰে ব্ৰত ৰাখক আৰু হনুমান মন্দিৰ দৰ্শন কৰক',


            'সেন্দুৰ আৰু মছুৰ দালি দান কৰক',


            'ৰঙা ৰঙৰ বস্ত্ৰ পৰিহাৰ কৰক',


            "মঙ্গল গ্ৰহৰ মন্ত্ৰ জাপ কৰক: 'ওঁ ক্ৰাং ক্ৰীং ক্ৰৌং সঃ ভৌমায় নমঃ'",


            'বিবাহৰ পূৰ্বে মাংগলিক দোষ নিবাৰণ পূজা কৰাওক',


            'তুলসী গছত জল অৰ্পণ কৰক আৰু প্ৰদক্ষিণ কৰক',


        ],


        'pdf_title': '💍 যোটক মিলন ৰিপৰ্ট',


        'pdf_score_unit': '/ {max_score} গুণ',


        'pdf_mars_position': 'মঙ্গল {house}ম ঘৰত',


        'pdf_conclusion_title': '🌟 সৰ্বমুঠ মূল্যাংকন আৰু সিদ্ধান্ত',


        'pdf_conclusion_text': '{boy} আৰু {girl}ৰ যোটক মিলনত সৰ্বমুঠ {total} / {max_score} গুণ প্ৰাপ্ত হৈছে।',


        'pdf_blessing': '✨ ঈশ্বৰে আপোনালোকৰ দাম্পত্য জীৱন সুখময়, সমৃদ্ধিশালী আৰু দীৰ্ঘস্থায়ী কৰি তোলক।\nশুভম ভৱতু। 🙏',


        'pdf_nadi_warning': '⚠️ <b>নাড়ী দোষ</b> উপস্থিত - নাড়ী দোষ নিবাৰণ নকৰাকৈ বিবাহ পৰামৰ্শিত নহয়।',


        'pdf_bhakoot_warning': '⚠️ <b>ভকূট দোষ</b> উপস্থিত - পাৰিবাৰিক কল্যাণৰ বাবে প্ৰতিকাৰ কৰক।',


        'pdf_footer': '© ধ্ৰুৱতৰা AI · দিতুল শৰ্মাৰ দ্বাৰা নিৰ্মিত প্ৰথম অসমীয়া জ্যোতিষ চফ্টৱেৰ',


        'pdf_astro_title': 'শ্ৰমেণ গণ্যতে কোষ্ঠীং',


        'mangalik_heading': 'মাংগলিক দোষ (কূজ দোষ) বিচাৰ',


        'mangalik_remedies_heading': 'মাংগলিক দোষৰ প্ৰতিকাৰ (Remedies)',


        'important_label': 'গুৰুত্বপূৰ্ণ',


        'severity_map': {'তীব্ৰ': 'তীব্ৰ', 'মধ্যম': 'মধ্যম', 'সামান্য': 'সামান্য', 'অনুপস্থিত': 'অনুপস্থিত'},


        'cancellation_map': {


            'দোষ সাম্য (উভয় মাংগলিক হোৱাৰ বাবে দোষৰ প্ৰভাৱ পৰস্পৰে নিষ্ক্ৰিয় কৰে)': 'দোষ সাম্য (উভয় মাংগলিক হোৱাৰ বাবে দোষৰ প্ৰভাৱ পৰস্পৰে নিষ্ক্ৰিয় কৰে)',


            'কোনো মাংগলিক দোষ নাই': 'কোনো মাংগলিক দোষ নাই',


        },


        'conclusion_heading': 'সৰ্বমুঠ মূল্যাংকন আৰু সিদ্ধান্ত',


        'conclusion_text': '{boy} আৰু {girl}ৰ যোটক মিলনত সৰ্বমুঠ {total} / {max_score} গুণ প্ৰাপ্ত হৈছে।',


        'nadi_warning': 'এই যোটকত নাড়ী দোষ উপস্থিত আছে। নাড়ী দোষ নিবাৰণ নকৰাকৈ বিবাহ কৰাটো পৰামৰ্শিত নহয়। জ্যোতিষীৰ পৰামৰ্শ লৈ উপযুক্ত প্ৰতিকাৰ কৰক।',


        'bhakoot_warning': 'এই যোটকত ভকূট দোষ উপস্থিত আছে। পাৰিবাৰিক কল্যাণৰ বাবে ভকূট দোষ নিবাৰণৰ প্ৰতিকাৰ কৰাটো উচিত।',


        'blessing': 'ঈশ্বৰে আপোনালোকৰ দাম্পত্য জীৱন সুখময়, সমৃদ্ধিশালী আৰু দীৰ্ঘস্থায়ী কৰি তোলক।\nশুভম ভৱতু। 🙏',


        'new_matching_btn': 'নতুন যোটক মিলন বিচাৰ কৰক',


        'mars_in_house_label': 'মঙ্গল {house}ম ঘৰত',





    },


    'bn': {


        'title': 'যোটক মিলন', 'title_sub': 'অষ্টকূট গুণ মিলন',


        'boy_label': 'পাত্র', 'girl_label': 'পাত্রী',


        'rashi': 'রাশি', 'nakshatra': 'নক্ষত্র', 'charan': 'চরণ', 'lagna': 'লগ্ন',


        'mars_house': 'মঙ্গল', 'mars_house_unit': 'ম ঘর',


        'mangalik': 'মাঙ্গলিক', 'not_mangalik': 'অমাঙ্গলিক',


        'total_guna': 'সর্বমোট গুণ',


        'summary_heading': 'অষ্টকূট গুণ মিলন - সারাংশ',


        'detail_heading': 'অষ্টকূটের বিস্তারিত বিশ্লেষণ',


        'mangalik_heading': 'মাঙ্গলিক দোষ (কুজ দোষ) বিচার',


        'koota_names': {'varna': 'বর্ণ কূট', 'vashya': 'বশ্য কূট', 'tara': 'তারা কূট', 'yoni': 'যোনি কূট', 'graha_maitri': 'গ্রহ মৈত্রী কূট', 'gana': 'গণ কূট', 'bhakoot': 'ভকূট কূট', 'nadi': 'নাড়ী কূট'},


        'koota_icons': {'varna': '🕉️', 'vashya': '💑', 'tara': '⭐', 'yoni': '💕', 'graha_maitri': '🪐', 'gana': '🎭', 'bhakoot': '🏠', 'nadi': '🧬'},


        'score': 'প্রাপ্ত', 'max_score': 'সর্বোচ্চ', 'status': 'স্থিতি', 'order': 'ক্রম', 'koota_name': 'কূটের নাম',


        'varna_names': {1: 'ব্রাহ্মণ', 2: 'ক্ষত্রিয়', 3: 'বৈশ্য', 4: 'শূদ্র'},


        'vashya_names': {1: 'চতুষ্পদ', 2: 'মানব', 3: 'জলচর', 4: 'বনচর', 5: 'কীট'},


        'tara_names': {1: 'জন্ম', 2: 'সম্পদ', 3: 'বিপদ', 4: 'ক্ষেম', 5: 'প্রত্যরি', 6: 'সাধক', 7: 'বধ', 8: 'মিত্র', 9: 'অতি মিত্র'},


        'gana_names': {1: 'দেব', 2: 'মনুষ্য', 3: 'রাক্ষস'},


        'nadi_names': {1: 'আদি', 2: 'মধ্য', 3: 'অন্ত্য'},


        # Reverse mappings: Assamese string → target language


        'varna_rev': {'ব্ৰাহ্মণ': 'ব্রাহ্মণ', 'ক্ষত্ৰিয়': 'ক্ষত্রিয়', 'বৈশ্য': 'বৈশ্য', 'শূদ্ৰ': 'শূদ্র'},


        'vashya_rev': {'চতুষ্পদ': 'চতুষ্পদ', 'মানৱ': 'মানব', 'জলচৰ': 'জলচর', 'বনচৰ': 'বনচর', 'কীট': 'কীট'},


        'yoni_rev': {'অশ্ব': 'অশ্ব', 'গজ': 'গজ', 'মেষ': 'মেষ', 'সৰ্প': 'সর্প', 'শ্বান': 'শ্বান', 'মাৰ্জাৰ': 'মার্জার', 'মূষিক': 'মূষিক', 'গো': 'গো', 'মহিষ': 'মহিষ', 'ব্যাঘ্ৰ': 'ব্যাঘ্র', 'মৃগ': 'মৃগ', 'বানৰ': 'বানর', 'নকুল': 'নকুল', 'সিংহ': 'সিংহ'},


        'lord_rev': {'সূৰ্য': 'সূর্য', 'চন্দ্ৰ': 'চন্দ্র', 'মংগল': 'মঙ্গল', 'বুধ': 'বুধ', 'বৃহস্পতি': 'বৃহস্পতি', 'শুক্ৰ': 'শুক্র', 'শনি': 'শনি'},


        'gana_rev': {'দেৱ': 'দেব', 'মনুষ্য': 'মনুষ্য', 'ৰাক্ষস': 'রাক্ষস'},


        'nadi_rev': {'আদি': 'আদি', 'মধ্য': 'মধ্য', 'অন্ত্য': 'অন্ত্য'},


        'verdict_excellent': 'উত্তম (অতি শুভ)', 'verdict_good': 'মধ্যম (শুভ)', 'verdict_average': 'মধ্যম (গ্রহণযোগ্য)', 'verdict_warning': 'অমিল (সাবধানতা প্রয়োজন)', 'verdict_bad': 'অশুভ (বিবাহ পরামর্শিত নয়)',


        'guna': 'গুণ', 'boy': 'পাত্র', 'girl': 'পাত্রী',


        'mangalik_both': 'পাত্র ও পাত্রী উভয়েই মাঙ্গলিক - দোষ সাম্য। উভয়ের মাঙ্গলিক দোষ পরস্পর নিষ্ক্রিয় করে। এটি বিবাহের জন্য এক সুসংবাদ!',


        'mangalik_boy': 'পাত্র মাঙ্গলিক কিন্তু পাত্রী অমাঙ্গলিক। মাঙ্গলিক দোষ নিরসনের জন্য প্রতিকার জরুরি।',


        'mangalik_girl': 'পাত্রী মাঙ্গলিক কিন্তু পাত্র অমাঙ্গলিক। মাঙ্গলিক দোষ নিরসনের জন্য প্রতিকার জরুরি।',


        'mangalik_none': 'পাত্র ও পাত্রী উভয়েই অমাঙ্গলিক। মাঙ্গলিক দোষ নেই। এটি বিবাহের জন্য শুভ!',


        'mars_in_house': 'মঙ্গল', 'house_suffix': 'ম ঘর',


        'download_pdf': 'PDF ডাউনলোড করুন', 'new_matching': 'নতুন যোটক মিলন বিচার করুন',


        'profile_info': 'বিবরণ', 'moon_sign': 'রাশি (Moon Sign)', 'charan_pada': 'চরণ / পাদ', 'mars_position': 'মঙ্গলের অবস্থান',


        'charan_unit': 'ম চরণ',


        # Koota detailed descriptions (Bengali)


        'koota_descriptions': {


            'varna': {


                'title': '১। বর্ণ কূট - আধ্যাত্মিক ও মানসিক সামঞ্জস্য',


                'good': 'পাত্র-পাত্রীর বর্ণগত সামঞ্জস্য অতি উত্তম। পাত্রের বর্ণ পাত্রীর চেয়ে উচ্চ বা সমান হওয়ায় এটি একটি সুস্থ ও সমতাপূর্ণ দাম্পত্য সম্পর্কের ইঙ্গিত দেয়। তাদের মধ্যে পারস্পরিক শ্রদ্ধা, বোঝাপড়া এবং আধ্যাত্মিক চিন্তার মিল থাকবে।',


                'mid': 'পাত্র-পাত্রীর বর্ণগত পার্থক্য আছে। পাত্রীর বর্ণ পাত্রের চেয়ে উচ্চ হওয়ায় দাম্পত্য জীবনে কখনো মানসিক দূরত্ব ও অহংকারের সংঘাত হতে পারে। পারস্পরিক শ্রদ্ধা ও বোঝাপড়ার মাধ্যমে এই অমিল অতিক্রম করা যায়।',


                'bad': 'পাত্র-পাত্রীর বর্ণগত অমিল আছে। দাম্পত্য জীবনে মানসিক দূরত্ব ও সংঘাতের সম্ভাবনা বেশি। আধ্যাত্মিক চর্চা ও পারস্পরিক বোঝাপড়ার মাধ্যমে এই অমিল অতিক্রম করা যায়।',


                'pred_good': '<strong>শুভ ফল:</strong> পাত্র-পাত্রীর বর্ণগত সামঞ্জস্য অতি উত্তম। পাত্রের বর্ণ পাত্রীর চেয়ে উচ্চ বা সমান হওয়ায় এটি একটি সুস্থ ও সমতাপূর্ণ দাম্পত্য সম্পর্কের ইঙ্গিত দেয়। এর অর্থ হল যে তাদের মধ্যে পারস্পরিক শ্রদ্ধা, বোঝাপড়া এবং আধ্যাত্মিক চিন্তাধারার মিল থাকবে। তাদের মানসিক স্তর এক হওয়ার জন্য জীবনের গুরুত্বপূর্ণ সিদ্ধান্তসমূহে সহমতে উপনীত হতে পারবে। এটি দাম্পত্য জীবনের ভিত্তি সবল করে এবং পরিবারে শান্তি বিরাজ করে।',


                'pred_mid': '<strong>সাবধানতা:</strong> পাত্র-পাত্রীর বর্ণগত পার্থক্য আছে। পাত্রীর বর্ণ পাত্রের চেয়ে উচ্চ হওয়ায় দাম্পত্য জীবনে কখনো মানসিক দূরত্ব ও অহংকারের সংঘাত হতে পারে। জীবনের গুরুত্বপূর্ণ সিদ্ধান্তে মতানৈক্য হওয়ার সম্ভাবনা থাকে। তথাপি পারস্পরিক শ্রদ্ধা ও বোঝাপড়ার মাধ্যমে এই অমিল সহজে অতিক্রম করা যায়। আধ্যাত্মিক চর্চা ও ধ্যানের মাধ্যমে মানসিক সমতা আনা সম্ভব।',


                'pred_bad': '<strong>সাবধানতা:</strong> পাত্র-পাত্রীর বর্ণগত অমিল গুরুতর। দাম্পত্য জীবনে মানসিক দূরত্ব ও সংঘাতের সম্ভাবনা বেশি। আধ্যাত্মিক চর্চা ও পারস্পরিক বোঝাপড়ার মাধ্যমে এই অমিল অতিক্রম করতে হবে। বিশেষ পূজা-অর্চনা ও জ্যোতিষীর পরামর্শ নেওয়া উচিত।'


            },


            'vashya': {


                'title': '২। বশ্য কূট - পারস্পরিক আকর্ষণ ও নিয়ন্ত্রণ',


                'good': 'বশ্য কূটে পূর্ণ গুণ - একটি গভীর পারস্পরিক আকর্ষণ ও প্রভাবের সম্পর্ক। তাদের মধ্যে একটি স্বাভাবিক চুম্বকীয় আকর্ষণ থাকবে, যা দাম্পত্য জীবনকে গভীর ও প্রগাঢ় করে রাখবে।',


                'mid': 'বশ্য কূটে আংশিক মিল। পারস্পরিক বোঝাপড়া ও সম্মানের সাথে ভারসাম্য বজায় রাখা যায়।',


                'bad': 'বশ্য কূটে অমিল। স্বাভাবিক আকর্ষণের অভাব হতে পারে। পরস্পরের প্রতি সহনশীলতা বাড়ানো উচিত।',


                'pred_good': '<strong>শুভ ফল:</strong> বশ্য কূটে পূর্ণ গুণ প্রাপ্তি এক গভীর পারস্পরিক আকর্ষণ ও প্রভাবের সম্পর্ক নির্দেশ করে। পাত্র-পাত্রীর মধ্যে একটি স্বাভাবিক চুম্বকীয় আকর্ষণ থাকবে, যা তাদের দাম্পত্য জীবনকে প্রগাঢ় করে রাখবে। তারা পরস্পরের প্রতি এক সুস্থ প্রভাব বিস্তার করবে এবং জীবনের চ্যালেঞ্জসমূহ একত্রে মোকাবিলা করতে পারবে। এটি একটি সুখী ও স্থায়ী বিবাহের জন্য অতি শুভ লক্ষণ।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> বশ্য কূটে আংশিক মিল আছে। পাত্র-পাত্রীর মধ্যে আকর্ষণ থাকলেও সম্পূর্ণ পারস্পরিক প্রভাব না থাকতে পারে। কোনো একজনের প্রভাব অন্যজনের ওপর বেশি হতে পারে। এর ফলে কখনো দাম্পত্য জীবনে ভারসাম্যহীনতা আসতে পারে। পারস্পরিক বোঝাপড়া ও সম্মানের মাধ্যমে এই পরিস্থিতির সমাধান সম্ভব।',


                'pred_bad': '<strong>সাবধানতা:</strong> বশ্য কূটে অমিল আছে। পাত্র-পাত্রীর মধ্যে স্বাভাবিক আকর্ষণের অভাব হতে পারে। তাদের ব্যক্তিত্ব ও জীবনশৈলীর পার্থক্য দাম্পত্য জীবনে সংঘাতের সৃষ্টি করতে পারে। পরস্পরের প্রতি সহনশীলতা বৃদ্ধি করা এবং একত্রে সময় কাটানোর অভ্যাস গড়ে তোলা উচিত।'


            },


            'tara': {


                'title': '৩। তারা কূট - ভাগ্য, স্বাস্থ্য ও মঙ্গল',


                'good': 'তারা কূটে পূর্ণ গুণ - অত্যন্ত শুভ! দাম্পত্য জীবনে ভাগ্যের সহায় থাকবে। স্বাস্থ্য সুরক্ষিত থাকবে।',


                'mid': 'তারা কূটে মধ্যম গুণ। দাম্পত্য জীবনে কিছু উত্থান-পতন থাকতে পারে। সাবধানতা অবলম্বন করা উচিত।',


                'bad': 'তারা কূটে অশুভ গুণ - বিপৎ বা নৈধন তারা। স্বাস্থ্যজনিত সমস্যা বা অপ্রত্যাশিত বিপদের সম্ভাবনা। পূজা-অর্চনা ও সাবধানতার প্রয়োজন।',


                'pred_good': '<strong>শুভ ফল:</strong> তারা কূটে পূর্ণ গুণ - এটি অত্যন্ত শুভ! পাত্রীর নক্ষত্র থেকে পাত্রের নক্ষত্র পর্যন্ত ব্যবধান শুভ তারায় পড়েছে। এর অর্থ হল যে তাদের দাম্পত্য জীবনে ভাগ্যের সহায় থাকবে। স্বাস্থ্যের ক্ষেত্রে এটি অতি শুভ - উভয়ের আয়ু ও স্বাস্থ্য সুরক্ষিত থাকবে। জীবনের সংকটসমূহে তারা ঐশ্বরিক সহায়তা লাভ করবে। এটি একটি অতি মঙ্গলময় দাম্পত্য জীবনের ইঙ্গিত।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> তারা কূটে মধ্যম গুণ - জন্ম বা প্রত্যরি তারা। এর অর্থ হল যে দাম্পত্য জীবনে কিছু উত্থান-পতন থাকতে পারে। স্বাস্থ্যের ক্ষেত্রে সাবধানতা অবলম্বন করা উচিত। নিয়মিত স্বাস্থ্য পরীক্ষা ও সুষম জীবনশৈলীর মাধ্যমে এই প্রভাব নিয়ন্ত্রণ করা সম্ভব। ভাগ্যের সহায় কিছু পরিমাণে থাকবে।',


                'pred_bad': '<strong>অশুভ ফল:</strong> তারা কূটে অশুভ গুণ - বিপৎ বা নৈধন তারা। এর অর্থ হল যে দাম্পত্য জীবনে স্বাস্থ্যজনিত সমস্যা বা অপ্রত্যাশিত বিপদ আসতে পারে। বিশেষ করে বিবাহের প্রারম্ভিক বছরসমূহে সাবধানতা অবলম্বন করা উচিত। নিয়মিত পূজা-অর্চনা, দান-পুণ্য এবং স্বাস্থ্যের প্রতি যত্নশীল হওয়ার মাধ্যমে এই অশুভ প্রভাব কমানো সম্ভব।'


            },


            'yoni': {


                'title': '৪। যোনি কূট - শারীরিক সামঞ্জস্য ও জৈবিক সমতা',


                'good': 'যোনি কূটে উত্তম গুণ। শারীরিক ও জৈবিক স্তরে গভীর সামঞ্জস্য থাকবে। দাম্পত্য জীবন প্রেম ও ঘনিষ্ঠতায় পূর্ণ হবে।',


                'mid': 'যোনি কূটে মধ্যম গুণ। শারীরিক সম্পর্কে কিছু পার্থক্য থাকতে পারে, কিন্তু প্রেমের মাধ্যমে অতিক্রম করা যায়।',


                'bad': 'যোনি কূটে অমিল - শত্রু যোনি। শারীরিক সম্পর্কে গুরুতর অমিল হতে পারে। বিশেষ পূজা-অর্চনার প্রয়োজন।',


                'pred_good': '<strong>শুভ ফল:</strong> যোনি কূটে সর্বোচ্চ গুণ - পাত্র-পাত্রীর একই যোনি! এটি অত্যন্ত বিরল এবং অতি শুভ। এর অর্থ হল যে তাদের মধ্যে শারীরিক ও জৈবিক স্তরে গভীর সামঞ্জস্য থাকবে। তাদের দাম্পত্য জীবন প্রেম, ঘনিষ্ঠতা এবং পারস্পরিক আকর্ষণে পূর্ণ হবে। সন্তান সুখের ক্ষেত্রেও এটি অতি শুভ। তাদের মধ্যে এক স্বাভাবিক বোঝাপড়া থাকবে যা সম্পর্ককে দীর্ঘস্থায়ী করে রাখবে।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> যোনি কূটে মধ্যম গুণ। পাত্র-পাত্রীর যোনি সম্পর্ক সাধারণ - বিশেষ মিত্রতাও নেই, শত্রুতাও নেই। শারীরিক সম্পর্কে কিছু পার্থক্য থাকতে পারে তথাপি পারস্পরিক বোঝাপড়া ও প্রেমের মাধ্যমে এটি অতিক্রম করা সম্ভব।',


                'pred_bad': '<strong>অশুভ ফল:</strong> যোনি কূটে অমিল - শত্রু যোনি। পাত্র-পাত্রীর যোনি পরস্পরের শত্রু হওয়ার জন্য শারীরিক সম্পর্কে গুরুতর অমিল হতে পারে। এর ফলে দাম্পত্য জীবনে অসন্তুষ্টি ও দূরত্ব আসতে পারে। সন্তানের ক্ষেত্রেও সমস্যা হতে পারে। বিশেষ পূজা-অর্চনা ও জ্যোতিষীর পরামর্শ নেওয়া উচিত।'


            },


            'graha_maitri': {


                'title': '৫। গ্রহ মৈত্রী কূট - মানসিক স্বভাব ও গ্রহগত বন্ধুত্ব',


                'good': 'গ্রহ মৈত্রী কূটে উত্তম গুণ। রাশি অধিপতি গ্রহদ্বয় পরস্পরের মিত্র বা এক। মানসিক স্বভাব ও চিন্তাধারার মধ্যে ভাল সামঞ্জস্য থাকবে।',


                'mid': 'গ্রহ মৈত্রী কূটে মধ্যম গুণ। মানসিক স্বভাবে কিছু পার্থক্য থাকতে পারে কিন্তু গুরুতর সংঘাত নয়।',


                'bad': 'গ্রহ মৈত্রী কূটে অমিল - রাশি অধিপতি শত্রু। মানসিক স্বভাবে গুরুত্বপূর্ণ পার্থক্য থাকবে। মতানৈক্যের সম্ভাবনা বেশি।',


                'pred_good': '<strong>শুভ ফল:</strong> গ্রহ মৈত্রী কূটে সর্বোচ্চ গুণ! পাত্র-পাত্রীর রাশি অধিপতি গ্রহদ্বয় পরস্পরের পরম মিত্র বা একই গ্রহ। এর অর্থ হল যে তাদের মানসিক স্বভাব, চিন্তাধারা এবং জীবনের প্রতি দৃষ্টিভঙ্গি অতি মিল থাকা। তারা পরস্পরকে সহজে বুঝতে পারবে এবং জীবনের চ্যালেঞ্জসমূহ একত্রে মোকাবিলা করতে পারবে। এটি দাম্পত্য জীবনের জন্য এক অতি শক্তিশালী ভিত্তি।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> গ্রহ মৈত্রী কূটে মধ্যম গুণ - রাশি অধিপতি গ্রহদ্বয় পরস্পরের সম (neutral)। তাদের মানসিক স্বভাবে কিছু পার্থক্য থাকতে পারে তথাপি গুরুতর সংঘাত নয়। পারস্পরিক বোঝাপড়া বৃদ্ধির জন্য একত্রে সময় কাটানো ও কথা বলা উচিত।',


                'pred_bad': '<strong>অশুভ ফল:</strong> গ্রহ মৈত্রী কূটে অমিল - রাশি অধিপতি গ্রহদ্বয় পরস্পরের শত্রু। তাদের মানসিক স্বভাব ও চিন্তাধারার মধ্যে গুরুত্বপূর্ণ পার্থক্য থাকবে। দাম্পত্য জীবনে মতানৈক্য ও ঝগড়া হওয়ার সম্ভাবনা বেশি। পারস্পরিক সহনশীলতা ও বোঝাপড়া বৃদ্ধির জন্য প্রচেষ্টা করা উচিত।'


            },


            'gana': {


                'title': '৬। গণ কূট - স্বভাবগত মিল ও আচরণ',


                'good': 'গণ কূটে উত্তম গুণ। স্বভাব, আচরণ ও জীবনশৈলীর মধ্যে ভাল সামঞ্জস্য। দাম্পত্য জীবনে সংঘাতের পরিমাণ ন্যূনতম হবে।',


                'mid': 'গণ কূটে মধ্যম গুণ। স্বভাবের পার্থক্য কখনো সংঘাতের সৃষ্টি করতে পারে। পারস্পরিক বোঝাপড়ার প্রয়োজন।',


                'bad': 'গণ কূটে অমিল। স্বভাবের মধ্যে গুরুত্বপূর্ণ পার্থক্য আছে। দাম্পত্য জীবনে সংঘাতের সম্ভাবনা বেশি। জ্যোতিষীর পরামর্শ নিন।',


                'pred_good': '<strong>শুভ ফল:</strong> গণ কূটে সর্বোচ্চ গুণ - পাত্র-পাত্রীর একই গণ! তাদের স্বভাব, আচরণ এবং জীবনশৈলী অতি মিল থাকা। এর ফলে তাদের মধ্যে স্বাভাবিক বোঝাপড়া থাকবে এবং দাম্পত্য জীবনে সংঘাতের পরিমাণ ন্যূনতম হবে। একত্রে জীবন কাটানো তাদের জন্য সহজ ও আনন্দময় হবে।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> গণ কূটে মধ্যম গুণ - দেব-মনুষ্য সম্পর্ক। পাত্র-পাত্রীর স্বভাবের মধ্যে ভাল সামঞ্জস্য আছে। দেব গণের ব্যক্তি আধ্যাত্মিক ও শান্ত প্রকৃতির, অন্যদিকে মনুষ্য গণের ব্যক্তি বাস্তববাদী ও কর্মঠ। এই মিশ্রণ দাম্পত্য জীবনে এক সুস্থ ভারসাম্য আনবে।',


                'pred_bad': '<strong>অশুভ ফল:</strong> গণ কূটে অমিল - দেব-রাক্ষস সম্পর্ক। স্বভাবের মধ্যে অতি গুরুত্বপূর্ণ পার্থক্য আছে। দেব গণের শান্ত ও আধ্যাত্মিক স্বভাব রাক্ষস গণের তীব্র ও আক্রমণাত্মক স্বভাবের সাথে খাপ খাবে না। দাম্পত্য জীবনে গুরুতর সংঘাত হওয়ার সম্ভাবনা আছে। জ্যোতিষীর পরামর্শ ও বিশেষ প্রতিকারের প্রয়োজন।'


            },


            'bhakoot': {


                'title': '৭। ভকূট কূট - পারিবারিক কল্যাণ ও সমৃদ্ধি',


                'good': 'ভকূট কূটে পূর্ণ গুণ - কোনো ভকূট দোষ নেই! পারিবারিক কল্যাণ, অর্থনৈতিক সমৃদ্ধি ও সুখ-শান্তি বিরাজ করবে।',


                'mid': 'ভকূট কূটে মধ্যম গুণ। পারিবারিক জীবনে কিছু উত্থান-পতন থাকতে পারে।',


                'bad': 'ভকূট কূটে দোষ উপস্থিত! পারিবারিক অশান্তি ও অর্থনৈতিক সংকটের সম্ভাবনা। ভকূট দোষ নিরসনের প্রতিকার করুন।',


                'pred_good': '<strong>শুভ ফল:</strong> ভকূট কূটে পূর্ণ গুণ - কোনো ভকূট দোষ নেই! এর অর্থ হল যে পাত্র-পাত্রীর দাম্পত্য জীবনে পারিবারিক কল্যাণ, অর্থনৈতিক সমৃদ্ধি এবং সুখ-শান্তি বিরাজ করবে। তাদের সংসার ধন-ধান্যে পরিপূর্ণ হবে এবং পরিবারে আনন্দের পরিবেশ বিরাজ করবে। এটি বিবাহের জন্য অতি শুভ লক্ষণ।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> ভকূট কূটে মধ্যম গুণ। পারিবারিক জীবনে কিছু উত্থান-পতন থাকতে পারে তথাপি গুরুতর সংকট নয়। অর্থনৈতিক ক্ষেত্রে স্থিরতার জন্য প্রচেষ্টা করা উচিত। পরিবারের সদস্যদের মধ্যে বোঝাপড়া বৃদ্ধির জন্য পারিবারিক আলোচনা ও একত্রে সময় কাটানো গুরুত্বপূর্ণ।',


                'pred_bad': '<strong>অশুভ ফল:</strong> ভকূট কূটে {{ result.kootas.bhakoot.result }} উপস্থিত! এর অর্থ হল যে দাম্পত্য জীবনে পারিবারিক অশান্তি, অর্থনৈতিক সংকট এবং মানসিক অস্থিরতা আসতে পারে। বিশেষ করে বিবাহের প্রারম্ভিক বছরসমূহে সাবধানতা অবলম্বন করা উচিত। ভকূট দোষ নিবারণের জন্য বিশেষ পূজা-অর্চনা ও জ্যোতিষীর পরামর্শ নেওয়া অতি জরুরি।'


            },


            'nadi': {


                'title': '৮। নাড়ী কূট - সন্তান সুখ ও জিনগত স্বাস্থ্য',


                'good': 'নাড়ী কূটে পূর্ণ গুণ - নাড়ী দোষ সম্পূর্ণ অনুপস্থিত! সন্তান সুখ অতি শুভ। সুস্থ ও বুদ্ধিমান সন্তান লাভ করবেন।',


                'bad': 'নাড়ী কূটে অমিল - নাড়ী দোষ উপস্থিত! সন্তানের ক্ষেত্রে সমস্যা ও স্বাস্থ্যজনিত জটিলতার সম্ভাবনা। নাড়ী দোষ নিরসনের জন্য বিশেষ পূজা ও জ্যোতিষীর পরামর্শ অতি জরুরি।',


                'pred_good': '<strong>শুভ ফল:</strong> নাড়ী কূটে পূর্ণ গুণ - নাড়ী দোষ সম্পূর্ণ অনুপস্থিত! সন্তান সুখ অতি শুভ। সুস্থ ও বুদ্ধিমান সন্তান লাভ করবেন। জীবনে সক্রিয় ইতিবাচক শক্তি ও উৎসাহ বিরাজ করবে। এটি দাম্পত্য জীবন ও সন্তানের জন্য অতি মঙ্গলকারী।',


                'pred_mid': '<strong>মধ্যম ফল:</strong> নাড়ী কূটে মধ্যম গুণ - নাড়ী দোষ আংশিকভাবে উপস্থিত। সন্তান সুখের সম্ভাবনা কম হতে পারে। বিশেষ পূজা-অর্চনা ও জ্যোতিষীর পরামর্শের মাধ্যমে এই দোষ কমানো সম্ভব।',


                'pred_bad': '<strong>অশুভ ফল:</strong> নাড়ী কূটে অমিল - নাড়ী দোষ উপস্থিত! সন্তানের ক্ষেত্রে সমস্যা ও স্বাস্থ্যজনিত জটিলতার অধিক সম্ভাবনা আছে। নাড়ী দোষ নিবারণের জন্য বিশেষ পূজা ও জ্যোতিষীর পরামর্শ অতি আবশ্যক। সময়মতো উচিত প্রতিকারের মাধ্যমে এই দোষ কমানো সম্ভব।'


            }


        },


        # Description templates (with {boy_*} and {girl_*} placeholders)


        'description_templates': {


            'varna': '{boy_label}র বর্ণ {boy_varna} এবং {girl_label}র বর্ণ {girl_varna}।',


            'vashya': '{boy_label}র বশ্য {boy_vashya} এবং {girl_label}র বশ্য {girl_vashya}।',


            'tara': '{girl_label}র নক্ষত্র থেকে {boy_label}র নক্ষত্রে তারা: {tara_girl_to_boy_name} ({tara_girl_to_boy}), {boy_label} থেকে {girl_label}এ তারা: {tara_boy_to_girl_name} ({tara_boy_to_girl})।',


            'yoni': "{boy_label}র যোনি '{boy_yoni}' এবং {girl_label}র যোনি '{girl_yoni}'।",


            'graha_maitri': "{boy_label}র রাশি অধিপতি '{boy_lord}' এবং {girl_label}র রাশি অধিপতি '{girl_lord}'।",


            'gana': "{boy_label}র গণ '{boy_gana}' এবং {girl_label}র গণ '{girl_gana}'।",


            'bhakoot': "{girl_label}র রাশি '{girl_rashi}' এবং {boy_label}র রাশি '{boy_rashi}'র ভকূট মিলন।",


            'nadi': "{boy_label}র নাড়ী '{boy_nadi}' এবং {girl_label}র নাড়ী '{girl_nadi}'।",


        },


        'result_map': {


            'উত্তম': 'উত্তম', 'মধ্যম': 'মধ্যম', 'অমিল': 'অমিল', 'অশুভ': 'অশুভ',


            'উত্তম (অতি শুভ)': 'উত্তম (অতি শুভ)',


            'উত্তম (একে যোনি)': 'উত্তম (একই যোনি)',


            'উত্তম (মিত্ৰ যোনি)': 'উত্তম (মিত্র যোনি)',


            'মধ্যম (সাধাৰণ)': 'মধ্যম (সাধারণ)',


            'মধ্যম (সামান্য)': 'মধ্যম (সামান্য)',


            'অশুভ (শত্ৰু যোনি)': 'অশুভ (শত্রু যোনি)',


            'উত্তম (অধি মিত্ৰ)': 'উত্তম (অধি মিত্র)',


            'উত্তম (মিত্ৰ)': 'উত্তম (মিত্র)',


            'মধ্যম (সম)': 'মধ্যম (সম)',


            'অমিল (শত্ৰু)': 'অমিল (শত্রু)',


            'অমিল (অধি শত্ৰু)': 'অমিল (অধি শত্রু)',


            'অশুভ (অধি শত্ৰু)': 'অশুভ (অধি শত্রু)',


            'উত্তম (একে গণ)': 'উত্তম (একই গণ)',


            'অমিল (দেৱ-ৰাক্ষস)': 'অমিল (দেব-রাক্ষস)',


            'অমিল (মনুষ্য-ৰাক্ষস)': 'অমিল (মনুষ্য-রাক্ষস)',


            'উত্তম (নাড়ী দোষ নাই)': 'উত্তম (নাড়ী দোষ নেই)',


        },


        'verdict_map': {


            'উত্তম (অতি শুভ)': 'উত্তম (অতি শুভ)',


            'মধ্যম (শুভ)': 'মধ্যম (শুভ)',


            'মধ্যম (গ্ৰহণযোগ্য)': 'মধ্যম (গ্রহণযোগ্য)',


            'অমিল (সাৱধানতা প্ৰয়োজন)': 'অমিল (সাবধানতা প্রয়োজন)',


            'অশুভ (বিবাহ পৰামৰ্শিত নহয়)': 'অশুভ (বিবাহ পরামর্শিত নয়)',


        },


        'verdict_desc_map': {


            'এই যোটক অতি উত্তম। বিবাহৰ বাবে অত্যন্ত শুভ আৰু সুপাৰিশিত। দাম্পত্য জীৱন সুখময়, সমৃদ্ধিশালী আৰু দীৰ্ঘস্থায়ী হ\'ব।': 'এই যোটক অতি উত্তম। বিবাহের জন্য অত্যন্ত শুভ ও সুপারিশিত। দাম্পত্য জীবন সুখময়, সমৃদ্ধিশালী ও দীর্ঘস্থায়ী হবে।',


            'এই যোটক মধ্যম শ্ৰেণীৰ। বিবাহৰ বাবে গ্ৰহণযোগ্য। সামান্য প্ৰতিকাৰৰ দ্বাৰা দাম্পত্য জীৱন সুখময় কৰিব পাৰি।': 'এই যোটক মধ্যম শ্রেণীর। বিবাহের জন্য গ্রহণযোগ্য। সামান্য প্রতিকারের মাধ্যমে দাম্পত্য জীবন সুখময় করা যায়।',


            'এই যোটক গড় মানৰ। কিছুমান দোষ থাকিলেও উপযুক্ত প্ৰতিকাৰৰ দ্বাৰা বিবাহ সম্ভৱ। জ্যোতিষীৰ পৰামৰ্শ লোৱাটো উচিত।': 'এই যোটক গড় মানের। কিছু দোষ থাকলেও উপযুক্ত প্রতিকারের মাধ্যমে বিবাহ সম্ভব। জ্যোতিষীর পরামর্শ নেওয়া উচিত।',


            'এই যোটকত যথেষ্ট অমিল আছে। বিবাহৰ পূৰ্বে জ্যোতিষীৰ পৰামৰ্শ আৰু প্ৰতিকাৰ অতি জৰুৰী।': 'এই যোটকে যথেষ্ট অমিল আছে। বিবাহের পূর্বে জ্যোতিষীর পরামর্শ ও প্রতিকার অতি জরুরি।',


            'এই যোটক অশুভ। পৰম্পৰাগতভাৱে এনে যোটকত বিবাহ পৰামৰ্শিত নহয়। তথাপিও জ্যোতিষীৰ পৰামৰ্শ লওক।': 'এই যোটক অশুভ। পরম্পরাগতভাবে এমন যোটকে বিবাহ পরামর্শিত নয়। তবুও জ্যোতিষীর পরামর্শ নিন।',


        },


        'remedies': [


            'প্রতিদিন হনুমান চালিসা পাঠ করুন',


            'মঙ্গলবারে ব্রত রাখুন এবং হনুমান মন্দির দর্শন করুন',


            'সিঁদুর এবং মসুর ডাল দান করুন',


            'লাল রঙের বস্ত্র পরিহার করুন',


            "মঙ্গল গ্রহের মন্ত্র জপ করুন: 'ওঁ ক্রাং ক্রীং ক্রৌং সঃ ভৌমায় নমঃ'",


            'বিবাহের পূর্বে মাঙ্গলিক দোষ নিবারণ পূজা করান',


            'তুলসী গাছে জল অর্পণ করুন এবং প্রদক্ষিণ করুন',


        ],


        'pdf_title': '💍 যোটক মিলন রিপোর্ট',


        'pdf_score_unit': '/ {max_score} গুণ',


        'pdf_mars_position': 'মঙ্গল {house}ম ঘরে',


        'pdf_conclusion_title': '🌟 সর্বমোট মূল্যাঙ্কন ও সিদ্ধান্ত',


        'pdf_conclusion_text': '{boy} এবং {girl}র যোটক মিলনে সর্বমোট {total} / {max_score} গুণ প্রাপ্ত হয়েছে।',


        'pdf_blessing': '✨ ঈশ্বর আপনাদের দাম্পত্য জীবন সুখময়, সমৃদ্ধিশালী ও দীর্ঘস্থায়ী করুন।\nশুভম ভবতু। 🙏',


        'pdf_nadi_warning': '⚠️ <b>নাড়ী দোষ</b> উপস্থিত - নাড়ী দোষ নিবারণ না করে বিবাহ পরামর্শিত নয়।',


        'pdf_bhakoot_warning': '⚠️ <b>ভকূট দোষ</b> উপস্থিত - পারিবারিক কল্যাণের জন্য প্রতিকার করুন।',


        'pdf_footer': '© ধ্রুবতারা AI · দিতুল শর্মার দ্বারা নির্মিত প্রথম অসমীয়া জ্যোতিষ সফটওয়্যার',


        'pdf_astro_title': 'শ্রমেণ গণ্যতে কোষ্ঠীং',


        'mangalik_heading': 'মাঙ্গলিক দোষ (কুজ দোষ) বিচার',


        'mangalik_remedies_heading': 'মাঙ্গলিক দোষের প্রতিকার (Remedies)',


        'important_label': 'গুরুত্বপূর্ণ',


        'severity_map': {'তীব্ৰ': 'তীব্র', 'মধ্যম': 'মধ্যম', 'সামান্য': 'সামান্য', 'অনুপস্থিত': 'অনুপস্থিত'},


        'cancellation_map': {


            'দোষ সাম্য (উভয় মাংগলিক হোৱাৰ বাবে দোষৰ প্ৰভাৱ পৰস্পৰে নিষ্ক্ৰিয় কৰে)': 'দোষ সাম্য (উভয় মাঙ্গলিক হওয়ার জন্য দোষের প্রভাব পরস্পর নিষ্ক্রিয় করে)',


            'কোনো মাংগলিক দোষ নাই': 'কোনো মাঙ্গলিক দোষ নেই',


        },


        'conclusion_heading': 'সর্বমোট মূল্যাঙ্কন ও সিদ্ধান্ত',


        'conclusion_text': '{boy} এবং {girl}র যোটক মিলনে সর্বমোট {total} / {max_score} গুণ প্রাপ্ত হয়েছে।',


        'nadi_warning': 'এই যোটকে নাড়ী দোষ উপস্থিত আছে। নাড়ী দোষ নিবারণ না করে বিবাহ করা পরামর্শিত নয়। জ্যোতিষীর পরামর্শ নিয়ে উপযুক্ত প্রতিকার করুন।',


        'bhakoot_warning': 'এই যোটকে ভকূট দোষ উপস্থিত আছে। পারিবারিক কল্যাণের জন্য ভকূট দোষ নিবারণের প্রতিকার করা উচিত।',


        'blessing': 'ঈশ্বর আপনাদের দাম্পত্য জীবন সুখময়, সমৃদ্ধিশালী ও দীর্ঘস্থায়ী করুন।\nশুভম ভবতু। 🙏',


        'new_matching_btn': 'নতুন যোটক মিলন বিচার করুন',


        'mars_in_house_label': 'মঙ্গল {house}ম ঘরে',





    },


    'hi': {


        'title': 'योटक मिलन', 'title_sub': 'अष्टकूट गुण मिलन',


        'boy_label': 'वर', 'girl_label': 'वधू',


        'rashi': 'राशि', 'nakshatra': 'नक्षत्र', 'charan': 'चरण', 'lagna': 'लग्न',


        'mars_house': 'मंगल', 'mars_house_unit': 'वाँ भाव',


        'mangalik': 'मांगलिक', 'not_mangalik': 'अमांगलिक',


        'total_guna': 'कुल गुण',


        'summary_heading': 'अष्टकूट गुण मिलन - सारांश',


        'detail_heading': 'अष्टकूट का विस्तृत विश्लेषण',


        'mangalik_heading': 'मांगलिक दोष (कुज दोष) विचार',


        'koota_names': {'varna': 'वर्ण कूट', 'vashya': 'वश्य कूट', 'tara': 'तारा कूट', 'yoni': 'योनि कूट', 'graha_maitri': 'ग्रह मैत्री कूट', 'gana': 'गण कूट', 'bhakoot': 'भकूट कूट', 'nadi': 'नाड़ी कूट'},


        'koota_icons': {'varna': '🕉️', 'vashya': '💑', 'tara': '⭐', 'yoni': '💕', 'graha_maitri': '🪐', 'gana': '🎭', 'bhakoot': '🏠', 'nadi': '🧬'},


        'score': 'प्राप्त', 'max_score': 'अधिकतम', 'status': 'स्थिति', 'order': 'क्रम', 'koota_name': 'कूट का नाम',


        'varna_names': {1: 'ब्राह्मण', 2: 'क्षत्रिय', 3: 'वैश्य', 4: 'शूद्र'},


        'vashya_names': {1: 'चतुष्पद', 2: 'मानव', 3: 'जलचर', 4: 'वनचर', 5: 'कीट'},


        'tara_names': {1: 'जन्म', 2: 'सम्पद', 3: 'विपद', 4: 'क्षेम', 5: 'प्रत्यरि', 6: 'साधक', 7: 'वध', 8: 'मित्र', 9: 'अति मित्र'},


        'gana_names': {1: 'देव', 2: 'मनुष्य', 3: 'राक्षस'},


        'nadi_names': {1: 'आदि', 2: 'मध्य', 3: 'अन्त्य'},


        # Reverse mappings: Assamese string → target language


        'varna_rev': {'ব্ৰাহ্মণ': 'ब्राह्मण', 'ক্ষত্ৰিয়': 'क्षत्रिय', 'বৈশ্য': 'वैश्य', 'শূদ্ৰ': 'शूद्र'},


        'vashya_rev': {'চতুষ্পদ': 'चतुष्पद', 'মানৱ': 'मानव', 'জলচৰ': 'जलचर', 'বনচৰ': 'वनचर', 'কীট': 'कीट'},


        'yoni_rev': {'অশ্ব': 'अश्व', 'গজ': 'गज', 'মেষ': 'मेष', 'সৰ্প': 'सर्प', 'শ্বান': 'श्वान', 'মাৰ্জাৰ': 'मार्जार', 'মূষিক': 'मूषिक', 'গো': 'गो', 'মহিষ': 'महिष', 'ব্যাঘ্ৰ': 'व्याघ्र', 'মৃগ': 'मृग', 'বানৰ': 'वानर', 'নকুল': 'नकुल', 'সিংহ': 'सिंह'},


        'lord_rev': {'সূৰ্য': 'सूर्य', 'চন্দ্ৰ': 'चंद्र', 'মংগল': 'मंगल', 'বুধ': 'बुध', 'বৃহস্পতি': 'बृहस्पति', 'শুক্ৰ': 'शुक्र', 'শনি': 'शनि'},


        'gana_rev': {'দেৱ': 'देव', 'মনুষ্য': 'मनुष्य', 'ৰাক্ষস': 'राक्षस'},


        'nadi_rev': {'আদি': 'आदि', 'মধ্য': 'मध्य', 'অন্ত্য': 'अन्त्य'},


        'rashi_rev': {'মেষ': 'मेष', 'বৃষ': 'वृष', 'মিথুন': 'मिथुन', 'কৰ্কট': 'कर्क', 'সিংহ': 'सिंह', 'কন্যা': 'कन्या', 'তুলা': 'तुला', 'বৃশ্চিক': 'वृश्चिक', 'ধনু': 'धनु', 'মকৰ': 'मकर', 'কুম্ভ': 'कुंभ', 'মীন': 'मीन'},


        'nakshatra_rev': {'অশ্বিনী': 'अश्विनी', 'ভৰণী': 'भरणी', 'কৃত্তিকা': 'कृत्तिका', 'ৰোহিণী': 'रोहिणी', 'মৃগশিৰা': 'मृगशिरा', 'আৰ্দ্ৰা': 'आर्द्रा', 'পুনৰ্বসু': 'पुनर्वसु', 'পুষ্যা': 'पुष्या', 'অশ্লেষা': 'आश्लेषा', 'মঘা': 'मघा', 'পূৰ্বফাল্গুনী': 'पूर्वाफाल्गुनी', 'উত্তৰফাল্গুনী': 'उत्तराफाल्गुनी', 'হস্তা': 'हस्ता', 'চিত্ৰা': 'चित्रा', 'স্বাতী': 'स्वाती', 'বিশাখা': 'विशाखा', 'অনুৰাধা': 'अनुराधा', 'জ্যেষ্ঠা': 'ज्येष्ठा', 'মূল': 'मूल', 'পূৰ্বাষাঢ়া': 'पूर्वाषाढ़ा', 'উত্তৰাষাঢ়া': 'उत्तराषाढ़ा', 'শ্ৰৱণা': 'श्रवणा', 'ধনিষ্ঠা': 'धनिष्ठा', 'শতভিষা': 'शतभिषा', 'পূৰ্বভাদ্ৰপদ': 'पूर्वाभाद्रपद', 'উত্তৰভাদ্ৰপদ': 'उत्तराभाद्रपद', 'ৰেৱতী': 'रेवती'},


        'verdict_excellent': 'उत्तम (अति शुभ)', 'verdict_good': 'मध्यम (शुभ)', 'verdict_average': 'मध्यम (ग्रहणीय)', 'verdict_warning': 'अमिल (सावधानी आवश्यक)', 'verdict_bad': 'अशुभ (विवाह अनुशंसित नहीं)',


        'guna': 'गुण', 'boy': 'वर', 'girl': 'वधू',


        'mangalik_both': 'वर और वधू दोनों मांगलिक - दोष साम्य। दोनों का मांगलिक दोष परस्पर निष्क्रिय करता है। यह विवाह के लिए शुभ संदेश है!',


        'mangalik_boy': 'वर मांगलिक किन्तु वधू अमांगलिक। मांगलिक दोष निवारण के लिए उपाय आवश्यक।',


        'mangalik_girl': 'वधू मांगलिक किन्तु वर अमांगलिक। मांगलिक दोष निवारण के लिए उपाय आवश्यक।',


        'mangalik_none': 'वर और वधू दोनों अमांगलिक। मांगलिक दोष नहीं। यह विवाह के लिए शुभ है!',


        'mars_in_house': 'मंगल', 'house_suffix': 'वाँ भाव',


        'download_pdf': 'PDF डाउनलोड करें', 'new_matching': 'नया योटक मिलन जानें',


        'profile_info': 'विवरण', 'moon_sign': 'राशि (Moon Sign)', 'charan_pada': 'चरण / पाद', 'mars_position': 'मंगल की स्थिति',


        'charan_unit': 'वाँ चरण',


        # Koota detailed descriptions (Hindi)


        'koota_descriptions': {


            'varna': {


                'title': '१। वर्ण कूट - आध्यात्मिक एवं मानसिक संगतता',


                'good': 'वर-वधू की वर्णगत संगतता अत्युतम। वर का वर्ण वधू से उच्च या समान होने से यह एक स्वस्थ एवं समतापूर्ण दाम्पत्य संबंध का संकेत देता है। उनमें परस्पर सम्मान, बोधगम्यता और आध्यात्मिक चिंतन की मिलन होगी।',


                'mid': 'वर-वधू की वर्णगत भिन्नता है। वधू का वर्ण वर से उच्च होने से दाम्पत्य जीवन में कभी मानसिक दूरी और अहंकार का संघर्ष हो सकता है। परस्पर सम्मान और बोधगम्यता से यह अमिल अत्यिक्रम कर सकते हैं।',


                'bad': 'वर-वधू की वर्णगत अमिल है। दाम्पत्य जीवन में मानसिक दूरी और संघर्ष की संभावना अधिक है। आध्यात्मिक चिंतन और परस्पर बोधगम्यता से यह अमिल अत्यिक्रम कर सकते हैं।',


                'pred_good': '<strong>शुभ फल:</strong> वर-वधू की वर्णगत संगतता अत्यंत उत्तम है। वर का वर्ण वधू से उच्च या समान होने के कारण यह एक स्वस्थ और समतापूर्ण दाम्पिक संबंध का संकेत है। इसका अर्थ है कि उनके बीच परस्पर सम्मान, बुझबुझ और आध्यात्मिक विचारधारा का मिलान होगा। उनकी मानसिक स्तर एक जैसा होने से जीवन के महत्वपूर्ण निर्णयों में सहमति बनेगी। यह दाम्पिक जीवन को मजबूत करता है और परिवार में शांति बनाए रखता है।',


                'pred_mid': '<strong>सावधानता:</strong> वर-वधू की वर्णगत असंगति है। वधू का वर्ण वर से उच्च होने के कारण दाम्पिक जीवन में कभी-कभी मानसिक दूरी और अहंकार का संघर्ष हो सकता है। जीवन के महत्वपूर्ण निर्णयों में मतभेद की संभावना है। तथापि, परस्पर सम्मान और बुझबुझ के द्वारा यह असंगति आसानी से पार किया जा सकता है। आध्यात्मिक अभ्यास और ध्यान से मानसिक समता लाई जा सकती है।',


                'pred_bad': '<strong>सावधानता:</strong> वर-वधू की वर्णगत असंगति गंभीर है। दाम्पिक जीवन में मानसिक दूरी और संघर्ष की अधिक संभावना है। आध्यात्मिक अभ्यास और परस्पर बुझबुझ के द्वारा इस असंगति को दूर करना होगा। विशेष पूजा-अर्चना और ज्योतिषी की सलाह लेना उचित होगा।'


            },


            'vashya': {


                'title': '२। वश्य कूट - परस्पर आकर्षण एवं नियंत्रण',


                'good': 'वश्य कूट में पूर्ण गुण - एक गहन परस्पर आकर्षण एवं प्रभाव का संबंध। उनमें एक स्वाभाविक चुम्बकीय आकर्षण होगा, जो दाम्पत्य जीवन को गहन बनाए रखेगा।',


                'mid': 'वश्य कूट में आंशिक मिल। परस्पर बोधगम्यता और सम्मान से संतुलन बनाए रख सकते हैं।',


                'bad': 'वश्य कूट में अमिल। स्वाभाविक आकर्षण की कमी हो सकती है। पारस्परिक सहनशीलता बढ़ानी चाहिए।',


                'pred_good': '<strong>शुभ फल:</strong> वश्य कूट में पूर्ण गुण प्राप्त होने से गहन परस्पर आकर्षण और प्रभाव का संबंध इंगित होता है। वर-वधू के बीच एक स्वाभाविक चुंबकीय आकर्षण होगा, जो उनके दाम्पिक जीवन को प्रगाढ़ बनाए रखेगा। वे एक-दूसरे पर सकारात्मक प्रभाव डालेंगे और जीवन की चुनौतियों को साथ मिलकर संभालेंगे। यह एक सुखी और स्थायी विवाह के लिए अत्यंत शुभ लक्षण है।',


                'pred_mid': '<strong>मध्यम फल:</strong> वश्य कूट में आंशिक मिलान है। वर-वधू के बीच आकर्षण है लेकिन पूर्ण परस्पर प्रभाव नहीं होगा। किसी एक का प्रभाव दूसरे पर अधिक हो सकता है। इसके परिणामस्वरूप दाम्पिक जीवन में कभी-कभी असंतुलन आ सकता है। परस्पर बुझबुझ और सम्मान से इस स्थिति का समाधान संभव है।',


                'pred_bad': '<strong>सावधानता:</strong> वश्य कूट में असंगति है। वर-वधू के बीच स्वाभाविक आकर्षण की कमी हो सकती है। उनकी व्यक्तित्व और जीवनशैली के अंतर से दाम्पिक जीवन में संघर्ष हो सकते हैं। एक-दूसरे के प्रति सहनशीलता बढ़ाना और साथ समय बिताने की आदत विकसित करना चाहिए।'


            },


            'tara': {


                'title': '३। तारा कूट - भाग्य, स्वास्थ्य एवं मंगल',


                'good': 'तारा कूट में पूर्ण गुण - अत्यंत शुभ! दाम्पत्य जीवन में भाग्य का सहयोग मिलेगा। स्वास्थ्य सुरक्षित रहेगा।',


                'mid': 'तारा कूट में मध्यम गुण। दाम्पत्य जीवन में कुछ उत्थान-पतन हो सकते हैं। सावधानी बरतें।',


                'bad': 'तारा कूट में अशुभ गुण - विपद या नैधन तारा। स्वास्थ्य संबंधी समस्याएं या अप्रत्याशित विपद की संभावना। पूजा-अर्चना और सावधानी आवश्यक।',


                'pred_good': '<strong>शुभ फल:</strong> तारा कूट में पूर्ण गुण - अत्यंत शुभ! वर की नक्षत्र से वधु की नक्षत्र तक का अंतर शुभ तारा में है। इसका अर्थ है कि उनके दाम्पिक जीवन में भाग्य का सहायता मिलेगा। स्वास्थ्य के क्षेत्र में यह अत्यंत शुभ है - दोनों की आयु और स्वास्थ्य सुरक्षित रहेगा। जीवन के संकटों में उन्हें ईश्वरीय सहायता मिलेगी। यह एक अत्यंत मंगलमय दाम्पिक जीवन का संकेत है।',


                'pred_mid': '<strong>मध्यम फल:</strong> तारा कूट में मध्यम गुण - जन्म या प्रत्यारी तारा। इसका अर्थ है कि दाम्पिक जीवन में कुछ उतार-चढ़ाव हो सकते हैं। स्वास्थ्य के क्षेत्र में सावधानी बरतनी चाहिए। नियमित स्वास्थ्य जांच और संतुलित जीवनशैली से इस प्रभाव को नियंत्रित किया जा सकता है। भाग्य का सहायता कुछ हद तक मिलेगा।',


                'pred_bad': '<strong>अशुभ फल:</strong> तारा कूट में अशुभ गुण - विपत या नैधन तारा। इसका अर्थ है कि दाम्पिक जीवन में स्वास्थ्य संबंधी समस्याएं या अप्रत्याशित संकट आ सकते हैं। विशेषकर विवाह के प्रारंभिक वर्षों में सावधानी बरतनी चाहिए। नियमित पूजा-अर्चना, दान-पुण्य और स्वास्थ्य की देखभाल से यह अशुभ प्रभाव कम किया जा सकता है।'


            },


            'yoni': {


                'title': '४। योनि कूट - शारीरिक संगतता एवं जैविक समता',


                'good': 'योनि कूट में उत्तम गुण। शारीरिक और जैविक स्तर पर गहन संगतता होगी। दाम्पत्य जीवन प्रेम और घनिष्ठता से परिपूर्ण होगा।',


                'mid': 'योनि कूट में मध्यम गुण। शारीरिक संबंध में कुछ भिन्नता हो सकती है, किन्तु प्रेम के माध्यम से अत्यिक्रम कर सकते हैं।',


                'bad': 'योनि कूट में अमिल - शत्रु योनि। शारीरिक संबंध में गंभीर अमिल हो सकती है। विशेष पूजा-अर्चना की आवश्यकता है।',


                'pred_good': '<strong>शुभ फल:</strong> योनि कूट में सर्वोच्च गुण - वर-वधू की एक ही योनि! यह अत्यंत दुर्लभ और अत्यंत शुभ है। इसका अर्थ है कि उनके बीच शारीरिक और जैविक स्तर पर गहन संगतता होगी। उनका दाम्पिक जीवन प्रेम, घनिष्ठता और परस्पर आकर्षण से परिपूर्ण होगा। संतान सुख के क्षेत्र में भी यह अत्यंत शुभ है। उनके बीच एक स्वाभाविक बुझबुझ होगी जो संबंध को दीर्घकालिक बनाए रखेगी।',


                'pred_mid': '<strong>मध्यम फल:</strong> योनि कूट में मध्यम गुण। वर-वधू की योनि संबंध सामान्य है - विशेष मित्रता नहीं, शत्रुता भी नहीं। शारीरिक संबंध में कुछ अंतर हो सकते हैं तथापि परस्पर बुझबुझ और प्रेम से इसे पार किया जा सकता है।',


                'pred_bad': '<strong>अशुभ फल:</strong> योनि कूट में असंगति - शत्रु योनि। वर-वधू की योनि एक-दूसरे की शत्रु होने से शारीरिक संबंध में गंभीर असंगति होगी। इसके परिणामस्वरूप दाम्पिक जीवन में असंतुष्टि और दूरी आ सकती है। संतान के क्षेत्र में भी समस्याएं हो सकती हैं। विशेष पूजा-अर्चना और ज्योतिषी की सलाह लेनी चाहिए।'


            },


            'graha_maitri': {


                'title': '५। ग्रह मैत्री कूट - मानसिक स्वभाव एवं ग्रहगत मित्रता',


                'good': 'ग्रह मैत्री कूट में उत्तम गुण। राशि अधिपति ग्रह दोनों परस्पर मित्र या एक। मानसिक स्वभाव और चिंतन में अच्छी संगतता होगी।',


                'mid': 'ग्रह मैत्री कूट में मध्यम गुण। मानसिक स्वभाव में कुछ भिन्नता हो सकती है किन्तु गंभीर संघर्ष नहीं।',


                'bad': 'ग्रह मैत्री कूट में अमिल - राशि अधिपति शत्रु। मानसिक स्वभाव में गंभीर भिन्नता होगी। मतभेद की संभावना अधिक है।',


                'pred_good': '<strong>शुभ फल:</strong> ग्रह मैत्री कूट में सर्वोच्च गुण! वर-वधू की राशि के अधिपति ग्रह परस्पर के परम मित्र या एक ही ग्रह हैं। इसका अर्थ है कि उनके मानसिक स्वभाव, विचारधारा और जीवन के प्रति दृष्टिकोण अत्यंत मिलते हैं। वे एक-दूसरे को आसानी से समझेंगे और जीवन की चुनौतियों को साथ मिलकर संभालेंगे। यह दाम्पिक जीवन के लिए एक अत्यंत शक्तिशाली आधार है।',


                'pred_mid': '<strong>मध्यम फल:</strong> ग्रह मैत्री कूट में मध्यम गुण - राशि अधिपति ग्रह परस्पर के सम (neutral) हैं। उनके मानसिक स्वभाव में कुछ अंतर हो सकते हैं तथापि गंभीर संघर्ष नहीं। परस्पर बुझबुझ बढ़ाने के लिए साथ समय बिताना और बातचीत करना चाहिए।',


                'pred_bad': '<strong>अशुभ फल:</strong> ग्रह मैत्री कूट में असंगति - राशि अधिपति ग्रह परस्पर के शत्रु हैं। उनके मानसिक स्वभाव और विचारधारा में गंभीर अंतर होगा। दाम्पिक जीवन में मतभेद और कलह की अधिक संभावना है। परस्पर सहनशीलता और बुझबुझ बढ़ाने के लिए प्रयास करना चाहिए।'


            },


            'gana': {


                'title': '६। गण कूट - स्वभावगत मिल एवं व्यवहार',


                'good': 'गण कूट में उत्तम गुण। स्वभाव, व्यवहार और जीवनशैली में अच्छी संगतता। दाम्पत्य जीवन में संघर्ष की मात्रा न्यूनतम होगी।',


                'mid': 'गण कूट में मध्यम गुण। स्वभाव की भिन्नता कभी संघर्ष का सृजन कर सकती है। परस्पर बोधगम्यता आवश्यक।',


                'bad': 'गण कूट में अमिल। स्वभाव में गंभीर भिन्नता है। दाम्पत्य जीवन में संघर्ष की संभावना अधिक है। ज्योतिषी की सलाह लें।',


                'pred_good': '<strong>शुभ फल:</strong> गण कूट में सर्वोच्च गुण - वर-वधू की एक ही गण है! उनके स्वभाव, व्यवहार और जीवनशैली अत्यंत मिलते हैं। इसके परिणामस्वरूप उनके बीच स्वाभाविक बुझबुझ होगी और दाम्पिक जीवन में संघर्ष की मात्रा न्यूनतम होगी। साथ जीवन बिताना उनके लिए आसान और आनंददायक होगा।',


                'pred_mid': '<strong>मध्यम फल:</strong> गण कूट में मध्यम गुण - देव-मनुष्य संबंध। वर-वधू के स्वभाव में अच्छी संगतता है। देव गण का व्यक्ति आध्यात्मिक और शांत प्रकृति का है, जबकि मनुष्य गण का व्यक्ति यथार्थवादी और कर्मठ है। यह मिश्रण दाम्पिक जीवन में एक स्वस्थ संतुलन लाएगा।',


                'pred_bad': '<strong>अशुभ फल:</strong> गण कूट में असंगति - देव-राक्षस संबंध। स्वभाव में अत्यंत महत्वपूर्ण अंतर है। देव गण की शांत और आध्यात्मिक प्रकृति राक्षस गण की तीव्र और आक्रामक प्रकृति के साथ मेल नहीं खा सकती। दाम्पिक जीवन में गंभीर संघर्ष की संभावना है। ज्योतिषी की सलाह और विशेष प्रतिकार के प्रयोग की आवश्यकता है।'


            },


            'bhakoot': {


                'title': '७। भकूट कूट - पारिवारिक कल्याण एवं समृद्धि',


                'good': 'भकूट कूट में पूर्ण गुण - कोई भकूट दोष नहीं! पारिवारिक कल्याण, आर्थिक समृद्धि और सुख-शांति बनी रहेगी।',


                'mid': 'भकूट कूट में मध्यम गुण। पारिवारिक जीवन में कुछ उत्थान-पतन हो सकते हैं।',


                'bad': 'भकूट कूट में दोष उपस्थित! पारिवारिक अशांति और आर्थिक संकट की संभावना। भकूट दोष निवारण का उपाय करें।',


                'pred_good': '<strong>शुभ फल:</strong> भकूट कूट में पूर्ण गुण - कोई भकूट दोष नहीं! इसका अर्थ है कि वर-वधू के दाम्पिक जीवन में पारिवारिक कल्याण, आर्थिक समृद्धि और सुख-शांति बनी रहेगी। उनका घर धन-धान्य से परिपूर्ण होगा और परिवार में आनंद का वातावरण होगा। यह विवाह के लिए अत्यंत शुभ लक्षण है।',


                'pred_mid': '<strong>मध्यम फल:</strong> भकूट कूट में मध्यम गुण। पारिवारिक जीवन में कुछ उतार-चढ़ाव हो सकते हैं लेकिन गंभीर संकट नहीं। आर्थिक स्थिरता के लिए प्रयास करना चाहिए। परिवार के सदस्यों के बीच बुझबुझ बढ़ाने के लिए पारिवारिक चर्चा और साथ समय बिताना महत्वपूर्ण है।',


                'pred_bad': '<strong>अशुभ फल:</strong> भकूट कूट में दोष उपस्थित! इसका अर्थ है कि दाम्पिक जीवन में पारिवारिक अशांति, आर्थिक संकट और मानसिक अस्थिरता आ सकती है। विशेषकर विवाह के प्रारंभिक वर्षों में सावधानी बरतनी चाहिए। भकूट दोष निवारण के लिए विशेष पूजा-अर्चना और ज्योतिषी की सलाह लेना अत्यंत आवश्यक है।'


            },


            'nadi': {


                'title': '८। नाड़ी कूट - सन्तान सुख एवं जिनगत स्वास्थ्य',


                'good': 'नाड़ी कूट में पूर्ण गुण - नाड़ी दोष पूर्ण अनुपस्थित! सन्तान सुख अत्यंत शुभ। स्वस्थ और बुद्धिमान सन्तान प्राप्त होंगे।',


                'bad': 'नाड़ी कूट में अमिल - नाड़ी दोष उपस्थित! सन्तान के क्षेत्र में समस्या और स्वास्थ्य संबंधी जटिलताओं की संभावना। नाड़ी दोष निवारण हेतु विशेष पूजा और ज्योतिषी की सलाह अत्यंत जरूरी।',


                'pred_good': '<strong>शुभ फल:</strong> नाड़ी कूट में पूर्ण गुण - नाड़ी दोष पूर्णतः अनुपस्थित! संतान सुख अत्यंत शुभ है। स्वस्थ और बुद्धिमान संतान प्राप्त होगी। जीवन में सकारात्मक ऊर्जा और उत्साह बना रहेगा। यह दाम्पिक जीवन और संतान के लिए अत्यंत मंगलकारी है।',


                'pred_mid': '<strong>मध्यम फल:</strong> नाड़ी कूट में मध्यम गुण - नाड़ी दोष आंशिक रूप से उपस्थित है। संतान सुख की संभावना कम हो सकती है। विशेष पूजा-अर्चना और ज्योतिषी की सलाह से इस दोष को कम किया जा सकता है।',


                'pred_bad': '<strong>अशुभ फल:</strong> नाड़ी कूट में असंगति - नाड़ी दोष उपस्थित! संतान के क्षेत्र में समस्याएं और स्वास्थ्य संबंधी जटिलताओं की अधिक संभावना है। नाड़ी दोष निवारण के लिए विशेष पूजा और ज्योतिषी के परामर्श अत्यंत आवश्यक है। समय पर उचित प्रतिकार से इस दोष को कम किया जा सकता है।'


            }


        },


        # Description templates (with {boy_*} and {girl_*} placeholders)


        'description_templates': {


            'varna': '{boy_label} का वर्ण {boy_varna} और {girl_label} का वर्ण {girl_varna}।',


            'vashya': '{boy_label} का वश्य {boy_vashya} और {girl_label} का वश्य {girl_vashya}।',


            'tara': '{girl_label} के नक्षत्र से {boy_label} के नक्षत्र तक तारा: {tara_girl_to_boy_name} ({tara_girl_to_boy}), {boy_label} से {girl_label} तक तारा: {tara_boy_to_girl_name} ({tara_boy_to_girl})।',


            'yoni': "{boy_label} की योनि '{boy_yoni}' और {girl_label} की योनि '{girl_yoni}'।",


            'graha_maitri': "{boy_label} के राशि अधिपति '{boy_lord}' और {girl_label} के राशि अधिपति '{girl_lord}'।",


            'gana': "{boy_label} का गण '{boy_gana}' और {girl_label} का गण '{girl_gana}'।",


            'bhakoot': "{girl_label} की राशि '{girl_rashi}' और {boy_label} की राशि '{boy_rashi}' का भकूट मिलन।",


            'nadi': "{boy_label} की नाड़ी '{boy_nadi}' और {girl_label} की नाड़ी '{girl_nadi}'।",


        },


        'result_map': {


            'উত্তম': 'उत्तम', 'মধ্যম': 'मध्यम', 'অমিল': 'अमिल', 'অশুভ': 'अशुभ',


            'উত্তম (অতি শুভ)': 'उत्तम (अति शुभ)',


            'উত্তম (একে যোনি)': 'उत्तम (एक योनि)',


            'উত্তম (মিত্ৰ যোনি)': 'उत्तम (मित्र योनि)',


            'মধ্যম (সাধাৰণ)': 'मध्यम (साधारण)',


            'মধ্যম (সামান্য)': 'मध्यम (सामान्य)',


            'অশুভ (শত্ৰু যোনি)': 'अशुभ (शत्रु योनि)',


            'উত্তম (অধি মিত্ৰ)': 'उत्तम (अधि मित्र)',


            'উত্তম (মিত্ৰ)': 'उत्तम (मित्र)',


            'মধ্যম (সম)': 'मध्यम (सम)',


            'অমিল (শত্ৰু)': 'अमिल (शत्रु)',


            'অমিল (অধি শত্ৰু)': 'अमिल (अधि शत्रु)',


            'অশুভ (অধি শত্ৰু)': 'अशुभ (अधि शत्रु)',


            'উত্তম (একে গণ)': 'उत्तम (एक गण)',


            'অমিল (দেৱ-ৰাক্ষস)': 'अमिल (देव-राक्षस)',


            'অমিল (মনুষ্য-ৰাক্ষস)': 'अमिल (मनुष्य-राक्षस)',


            'উত্তম (নাড়ী দোষ নাই)': 'उत्तम (नाड़ी दोष नहीं)',


        },


        'verdict_map': {


            'উত্তম (অতি শুভ)': 'उत्तम (अति शुभ)',


            'মধ্যম (শুভ)': 'मध्यम (शुभ)',


            'মধ্যম (গ্ৰহণযোগ্য)': 'मध्यम (ग्रहणीय)',


            'অমিল (সাৱধানতা প্ৰয়োজন)': 'अमिल (सावधानी आवश्यक)',


            'অশুভ (বিবাহ পৰামৰ্শিত নহয়)': 'अशुभ (विवाह अनुशंसित नहीं)',


        },


        'verdict_desc_map': {


            'এই যোটক অতি উত্তম। বিবাহৰ বাবে অত্যন্ত শুভ আৰু সুপাৰিশিত। দাম্পত্য জীৱন সুখময়, সমৃদ্ধিশালী আৰু দীৰ্ঘস্থায়ী হ\'ব।': 'यह योटक अति उत्तम है। विवाह के लिए अत्यंत शुभ एवं सुपारिशित है। दाम्पत्य जीवन सुखमय, समृद्धिशाली एवं दीर्घस्थायी होगा।',


            'এই যোটক মধ্যম শ্ৰেণীৰ। বিবাহৰ বাবে গ্ৰহণযোগ্য। সামান্য প্ৰতিকাৰৰ দ্বাৰা দাম্পত্য জীৱন সুখময় কৰিব পাৰি।': 'यह योटक मध्यम श्रेणी का है। विवाह के लिए ग्रहणीय है। सामान्य उपायों से दाम्पत्य जीवन सुखमय बनाया जा सकता है।',


            'এই যোটক গড় মানৰ। কিছুমান দোষ থাকিলেও উপযুক্ত প্ৰতিকাৰৰ দ্বাৰা বিবাহ সম্ভৱ। জ্যোতিষীৰ পৰামৰ্শ লোৱাটো উচিত।': 'यह योटक औसत स्तर का है। कुछ दोष होने पर भी उपयुक्त उपायों से विवाह संभव है। ज्योतिषी का परामर्श लेना उचित है।',


            'এই যোটকত যথেষ্ট অমিল আছে। বিবাহৰ পূৰ্বে জ্যোতিষীৰ পৰামৰ্শ আৰু প্ৰতিকাৰ অতি জৰুৰী।': 'इस योटक में पर्याप्त अमिल है। विवाह से पूर्व ज्योतिषी का परामर्श एवं उपाय अति आवश्यक है।',


            'এই যোটক অশুভ। পৰম্পৰাগতভাৱে এনে যোটকত বিবাহ পৰামৰ্শিত নহয়। তথাপিও জ্যোতিষীৰ পৰামৰ্শ লওক।': 'यह योटक अशुभ है। परंपरागत रूप से ऐसे योटक में विवाह अनुशंसित नहीं है। तथापि ज्योतिषी का परामर्श लें।',


        },


        'remedies': [


            'प्रतिदिन हनुमान चालीसा का पाठ करें',


            'मंगलवार को व्रत रखें और हनुमान मंदिर के दर्शन करें',


            'सिंदूर और मसूर दाल का दान करें',


            'लाल रंग के वस्त्रों का परिहार करें',


            "मंगल ग्रह के मंत्र का जाप करें: 'ॐ क्रां क्रीं क्रौं सः भौमाय नमः'",


            'विवाह से पूर्व मांगलिक दोष निवारण पूजा कराएं',


            'तुलसी के पौधे में जल अर्पित करें और परिक्रमा करें',


        ],


        'pdf_title': '💍 योटक मिलन रिपोर्ट',


        'pdf_score_unit': '/ {max_score} गुण',


        'pdf_mars_position': 'मंगल {house}वें भाव में',


        'pdf_conclusion_title': '🌟 सर्वमूल्यांकन एवं सिद्धांत',


        'pdf_conclusion_text': '{boy} और {girl} के योटक मिलन में कुल {total} / {max_score} गुण प्राप्त हुए हैं।',


        'pdf_blessing': '✨ ईश्वर आपके दाम्पत्य जीवन को सुखमय, समृद्धिशाली एवं दीर्घस्थायी करे।\nशुभम भवतु। 🙏',


        'pdf_nadi_warning': '⚠️ <b>नाड़ी दोष</b> उपस्थित - नाड़ी दोष निवारण के बिना विवाह अनुशंसित नहीं।',


        'pdf_bhakoot_warning': '⚠️ <b>भकूट दोष</b> उपस्थित - पारिवारिक कल्याण हेतु उपाय करें।',


        'pdf_footer': '© ध्रुवतारा AI · दितुल शर्मा द्वारा निर्मित प्रथम असमिया ज्योतिष सॉफ्टवेयर',


        'pdf_astro_title': 'श्रमेण गण्यते कोष्ठीम्',


        'mangalik_heading': 'मांगलिक दोष (कुज दोष) विचार',


        'mangalik_remedies_heading': 'मांगलिक दोष के उपाय (Remedies)',


        'important_label': 'महत्वपूर्ण',


        'severity_map': {'তীব্ৰ': 'तीव्र', 'মধ্যম': 'मध्यम', 'সামান্য': 'सामान्य', 'অনুপস্থিত': 'अनुपस्थित'},


        'cancellation_map': {


            'দোষ সাম্য (উভয় মাংগলিক হোৱাৰ বাবে দোষৰ প্ৰভাৱ পৰস্পৰে নিষ্ক্ৰিয় কৰে)': 'दोष साम्य (दोनों मांगलिक होने से दोष का प्रभाव परस्पर निष्क्रिय होता है)',


            'কোনো মাংগলিক দোষ নাই': 'कोई मांगलिक दोष नहीं',


        },


        'conclusion_heading': 'कुल मूल्यांकन एवं निष्कर्ष',


        'conclusion_text': '{boy} और {girl} के योटक मिलन में कुल {total} / {max_score} गुण प्राप्त हुए हैं।',


        'nadi_warning': 'इस योटक में नाड़ी दोष उपस्थित है। नाड़ी दोष निवारण के बिना विवाह करना अनुशंसित नहीं है। ज्योतिषी की सलाह लेकर उचित उपाय करें।',


        'bhakoot_warning': 'इस योटक में भकूट दोष उपस्थित है। पारिवारिक कल्याण हेतु भकूट दोष निवारण के उपाय करें।',


        'blessing': 'ईश्वर आपके दाम्पत्य जीवन को सुखमय, समृद्धिशाली एवं दीर्घस्थायी करे।\nशुभम भवतु। 🙏',


        'new_matching_btn': 'नया योटक मिलन जानें',


        'mars_in_house_label': 'मंगल {house}वें भाव में',





    },


    'en': {


        'title': 'Marriage Matching', 'title_sub': 'Ashtakoot Guna Milan',


        'boy_label': 'Groom', 'girl_label': 'Bride',


        'rashi': 'Rashi', 'nakshatra': 'Nakshatra', 'charan': 'Charan', 'lagna': 'Lagna',


        'mars_house': 'Mars', 'mars_house_unit': 'th House',


        'mangalik': 'Mangalik', 'not_mangalik': 'Non-Mangalik',


        'total_guna': 'Total Guna',


        'summary_heading': 'Ashtakoot Guna Milan - Summary',


        'detail_heading': 'Detailed Koota Analysis',


        'mangalik_heading': 'Mangalik Dosha (Kuja Dosha) Analysis',


        'koota_names': {'varna': 'Varna Koota', 'vashya': 'Vashya Koota', 'tara': 'Tara Koota', 'yoni': 'Yoni Koota', 'graha_maitri': 'Graha Maitri Koota', 'gana': 'Gana Koota', 'bhakoot': 'Bhakoot Koota', 'nadi': 'Nadi Koota'},


        'koota_icons': {'varna': '🕉️', 'vashya': '💑', 'tara': '⭐', 'yoni': '💕', 'graha_maitri': '🪐', 'gana': '🎭', 'bhakoot': '🏠', 'nadi': '🧬'},


        'score': 'Score', 'max_score': 'Max', 'status': 'Status', 'order': '#', 'koota_name': 'Koota Name',


        'varna_names': {1: 'Brahmin', 2: 'Kshatriya', 3: 'Vaishya', 4: 'Shudra'},


        'vashya_names': {1: 'Chatushpad', 2: 'Manava', 3: 'Jalachara', 4: 'Vanachara', 5: 'Keeta'},


        'tara_names': {1: 'Janma', 2: 'Sampat', 3: 'Vipat', 4: 'Kshema', 5: 'Pratyari', 6: 'Sadhana', 7: 'Vadha', 8: 'Mitra', 9: 'Ati Mitra'},


        'gana_names': {1: 'Deva', 2: 'Manushya', 3: 'Rakshasa'},


        'nadi_names': {1: 'Adi', 2: 'Madhya', 3: 'Antya'},


        # Reverse mappings: Assamese string → target language


        'varna_rev': {'ব্ৰাহ্মণ': 'Brahmin', 'ক্ষত্ৰিয়': 'Kshatriya', 'বৈশ্য': 'Vaishya', 'শূদ্ৰ': 'Shudra'},


        'vashya_rev': {'চতুষ্পদ': 'Chatushpad', 'মানৱ': 'Manava', 'জলচৰ': 'Jalachara', 'বনচৰ': 'Vanachara', 'কীট': 'Keeta'},


        'yoni_rev': {'অশ্ব': 'Horse', 'গজ': 'Elephant', 'মেষ': 'Sheep', 'সৰ্প': 'Serpent', 'শ্বান': 'Dog', 'মাৰ্জাৰ': 'Cat', 'মূষিক': 'Rat', 'গো': 'Cow', 'মহিষ': 'Buffalo', 'ব্যাঘ্ৰ': 'Tiger', 'মৃগ': 'Deer', 'বানৰ': 'Monkey', 'নকুল': 'Mongoose', 'সিংহ': 'Lion'},


        'lord_rev': {'সূৰ্য': 'Sun', 'চন্দ্ৰ': 'Moon', 'মংগল': 'Mars', 'বুধ': 'Mercury', 'বৃহস্পতি': 'Jupiter', 'শুক্ৰ': 'Venus', 'শনি': 'Saturn'},


        'gana_rev': {'দেৱ': 'Deva', 'মনুষ্য': 'Manushya', 'ৰাক্ষস': 'Rakshasa'},


        'nadi_rev': {'আদি': 'Adi', 'মধ্য': 'Madhya', 'অন্ত্য': 'Antya'},


        'rashi_rev': {'মেষ': 'Aries', 'বৃষ': 'Taurus', 'মিথুন': 'Gemini', 'কৰ্কট': 'Cancer', 'সিংহ': 'Leo', 'কন্যা': 'Virgo', 'তুলা': 'Libra', 'বৃশ্চিক': 'Scorpio', 'ধনু': 'Sagittarius', 'মকৰ': 'Capricorn', 'কুম্ভ': 'Aquarius', 'মীন': 'Pisces'},


        'nakshatra_rev': {'অশ্বিনী': 'Ashwini', 'ভৰণী': 'Bharani', 'কৃত্তিকা': 'Krittika', 'ৰোহিণী': 'Rohini', 'মৃগশিৰা': 'Mrigashira', 'আৰ্দ্ৰা': 'Ardra', 'পুনৰ্বসু': 'Punarvasu', 'পুষ্যা': 'Pushya', 'অশ্লেষা': 'Ashlesha', 'মঘা': 'Magha', 'পূৰ্বফাল্গুনী': 'Purva Phalguni', 'উত্তৰফাল্গুনী': 'Uttara Phalguni', 'হস্তা': 'Hasta', 'চিত্ৰা': 'Chitra', 'স্বাতী': 'Swati', 'বিশাখা': 'Vishakha', 'অনুৰাধা': 'Anuradha', 'জ্যেষ্ঠা': 'Jyeshtha', 'মূল': 'Mula', 'পূৰ্বাষাঢ়া': 'Purva Ashadha', 'উত্তৰাষাঢ়া': 'Uttara Ashadha', 'শ্ৰৱণা': 'Shravana', 'ধনিষ্ঠা': 'Dhanishta', 'শতভিষা': 'Shatabhisha', 'পূৰ্বভাদ্ৰপদ': 'Purva Bhadrapada', 'উত্তৰভাদ্ৰপদ': 'Uttara Bhadrapada', 'ৰেৱতী': 'Revati'},


        'verdict_excellent': 'Excellent (Very Auspicious)', 'verdict_good': 'Good (Auspicious)', 'verdict_average': 'Average (Acceptable)', 'verdict_warning': 'Poor (Caution Needed)', 'verdict_bad': 'Inauspicious (Not Recommended)',


        'guna': 'Guna', 'boy': 'Groom', 'girl': 'Bride',


        'mangalik_both': 'Both Groom and Bride are Mangalik - Dosha is balanced. Their Mangalik doshas cancel each other. This is auspicious for marriage!',


        'mangalik_boy': 'Groom is Mangalik but Bride is Non-Mangalik. Remedies for Mangalik dosha are recommended.',


        'mangalik_girl': 'Bride is Mangalik but Groom is Non-Mangalik. Remedies for Mangalik dosha are recommended.',


        'mangalik_none': 'Both Groom and Bride are Non-Mangalik. No Mangalik dosha. This is auspicious!',


        'mars_in_house': 'Mars', 'house_suffix': 'th House',


        'download_pdf': 'Download PDF', 'new_matching': 'New Matching',


        'profile_info': 'Details', 'moon_sign': 'Moon Sign', 'charan_pada': 'Charan / Pada', 'mars_position': 'Mars Position',


        'charan_unit': 'th Charan',


        # Koota detailed descriptions (English)


        'koota_descriptions': {


            'varna': {


                'title': '1. Varna Koota - Spiritual and Mental Compatibility',


                'good': 'The spiritual and mental compatibility between the groom and bride is excellent. Since the groom\'s varna is equal to or higher than the bride\'s, this indicates a healthy and balanced married life. There will be mutual respect, understanding, and alignment in spiritual thinking.',


                'mid': 'There is a varna difference between the groom and bride. If the bride\'s varna is higher than the groom\'s, there may be occasional mental distance and ego conflicts in married life. These can be overcome through mutual respect and understanding.',


                'bad': 'There is a significant varna mismatch between the groom and bride. This may lead to mental distance and conflicts in married life. Spiritual practices and mutual understanding can help overcome this incompatibility.',


                'pred_good': '<strong>Auspicious Result:</strong> The spiritual and mental compatibility between the groom and bride is excellent. Since the groom\'s varna is equal to or higher than the bride\'s, this indicates a healthy and balanced married life. There will be mutual respect, understanding, and alignment in spiritual thinking. Their mental levels match, enabling agreement on important life decisions. This strengthens the foundation of married life and maintains peace in the family.',


                'pred_mid': '<strong>Caution:</strong> There is a varna difference between the groom and bride. If the bride\'s varna is higher than the groom\'s, there may be occasional mental distance and ego conflicts in married life. Disagreements on important life decisions are possible. However, this incompatibility can be easily overcome through mutual respect and understanding. Spiritual practices and meditation can help bring mental equilibrium.',


                'pred_bad': '<strong>Caution:</strong> There is a significant varna mismatch between the groom and bride. This may lead to mental distance and conflicts in married life. The possibility of disagreements and ego conflicts is high. Spiritual practices and mutual understanding are strongly recommended to overcome this incompatibility. Consultation with an astrologer for special remedies may be helpful.'


            },


            'vashya': {


                'title': '2. Vashya Koota - Mutual Attraction and Control',


                'good': 'Vashya Koota shows full points - a deep mutual attraction and influence exists between them. There will be a natural magnetic attraction that keeps the married life profound and engaged.',


                'mid': 'Vashya Koota shows partial match. Balance can be maintained through mutual understanding and respect.',


                'bad': 'Vashya Koota shows incompatibility. There may be a lack of natural attraction. Increasing tolerance towards each other is recommended.',


                'pred_good': '<strong>Auspicious Result:</strong> Vashya Koota shows full points, indicating a deep mutual attraction and influence between them. There will be a natural magnetic attraction that keeps the married life profound and engaged. They will exert a positive influence on each other and face life\'s challenges together. This is an extremely auspicious sign for a happy and lasting marriage.',


                'pred_mid': '<strong>Average Result:</strong> Vashya Koota shows partial match. While there is attraction between the groom and bride, there may not be complete mutual influence. One may have more influence over the other. This may occasionally cause imbalance in married life. This situation can be resolved through mutual understanding and respect.',


                'pred_bad': '<strong>Caution:</strong> Vashya Koota shows incompatibility. There may be a lack of natural attraction between the groom and bride. Differences in personality and lifestyle may create conflicts in married life. Increasing tolerance towards each other and developing the habit of spending quality time together is recommended.'


            },


            'tara': {


                'title': '3. Tara Koota - Destiny, Health and Well-being',


                'good': 'Tara Koota shows full points - extremely auspicious! Fortune will favor the married life. Health will be protected.',


                'mid': 'Tara Koota shows medium points. There may be some fluctuations in married life. Caution is advised.',


                'bad': 'Tara Koota shows inauspicious points - Vipat or Naidhana tara. There is a possibility of health issues or unexpected dangers. Special prayers and caution are recommended.',


                'pred_good': '<strong>Auspicious Result:</strong> Tara Koota shows full points - extremely auspicious! The distance from the bride\'s nakshatra to the groom\'s nakshatra falls in an auspicious tara. This means fortune will favor their married life. In terms of health, this is extremely auspicious - both\'s longevity and health will be protected. They will receive divine help during life\'s crises. This is a sign of an extremely auspicious married life.',


                'pred_mid': '<strong>Average Result:</strong> Tara Koota shows medium points - Janma or Pratyak Tara. This means there may be some fluctuations in married life. Caution should be taken regarding health. Regular health checkups and a balanced lifestyle can help control this influence. Fortune\'s help will be available to some extent.',


                'pred_bad': '<strong>Inauspicious Result:</strong> Tara Koota shows inauspicious points - Vipat or Naidhana tara. This means health-related problems or unexpected dangers may occur in married life. Caution should be taken especially during the initial years of marriage. This inauspicious influence can be reduced through regular prayers, charity, and taking care of health.'


            },


            'yoni': {


                'title': '4. Yoni Koota - Physical Compatibility and Biological Harmony',


                'good': 'Yoni Koota shows excellent points. There is deep physical and biological harmony. Married life will be filled with love and intimacy.',


                'mid': 'Yoni Koota shows medium points. There may be some physical differences, but these can be overcome through love.',


                'bad': 'Yoni Koota shows incompatibility - enemy yoni. There may be serious physical incompatibilities. Special prayers are recommended.',


                'pred_good': '<strong>Auspicious Result:</strong> Yoni Koota shows the highest points - the groom and bride have the same yoni! This is extremely rare and highly auspicious. This means there will be deep physical and biological harmony between them. Their married life will be filled with love, intimacy, and mutual attraction. This is also highly auspicious for progeny happiness. There will be a natural understanding between them that will keep the relationship lasting.',


                'pred_mid': '<strong>Average Result:</strong> Yoni Koota shows medium points. The yoni relationship between the groom and bride is normal - neither special friendship nor enmity. There may be some physical differences in the relationship, but these can be overcome through love and mutual understanding.',


                'pred_bad': '<strong>Inauspicious Result:</strong> Yoni Koota shows incompatibility - enemy yoni. The yoni of the groom and bride being mutual enemies will cause serious incompatibilities in the physical relationship. This may result in dissatisfaction and distance in married life. There may also be problems related to progeny. Special prayers and astrologer\'s consultation are recommended.'


            },


            'graha_maitri': {


                'title': '5. Graha Maitri Koota - Mental Nature and Planetary Friendship',


                'good': 'Graha Maitri Koota shows excellent points. The ruling planets of both horoscopes are mutual friends or the same. There will be good mental compatibility and alignment in thinking.',


                'mid': 'Graha Maitri Koota shows medium points. There may be some mental differences but no serious conflicts.',


                'bad': 'Graha Maitri Koota shows incompatibility - the ruling planets of both horoscopes are enemies. There will be significant mental differences. The possibility of disagreements is high.',


                'pred_good': '<strong>Auspicious Result:</strong> Graha Maitri Koota shows the highest points! The ruling planets of both the groom\'s and bride\'s horoscopes are mutual best friends or the same planet. This means their mental nature, thinking, and outlook on life are highly similar. They will understand each other easily and face life\'s challenges together. This is an extremely strong foundation for married life.',


                'pred_mid': '<strong>Average Result:</strong> Graha Maitri Koota shows medium points - the ruling planets of both horoscopes are neutral to each other. There may be some differences in their mental natures but no serious conflicts. To increase mutual understanding, they should spend time together and communicate more.',


                'pred_bad': '<strong>Inauspicious Result:</strong> Graha Maitri Koota shows incompatibility - the ruling planets of both horoscopes are enemies. There will be significant differences in their mental nature and thinking. The possibility of disagreements and conflicts in married life is high. Efforts should be made to increase mutual tolerance and understanding.'


            },


            'gana': {


                'title': '6. Gana Koota - Temperamental Match and Behavior',


                'good': 'Gana Koota shows excellent points. There is good compatibility in nature, behavior, and lifestyle. The amount of conflict in married life will be minimal.',


                'mid': 'Gana Koota shows medium points. Differences in nature may sometimes create conflicts. Mutual understanding is needed.',


                'bad': 'Gana Koota shows incompatibility. There are significant differences in nature. The possibility of conflict in married life is high. Consult an astrologer.',


                'pred_good': '<strong>Auspicious Result:</strong> Gana Koota shows the highest points - the groom and bride have the same gana! Their nature, behavior, and lifestyle are highly compatible. As a result, there will be a natural understanding between them and the amount of conflict in married life will be minimal. Spending life together will be easy and enjoyable for them.',


                'pred_mid': '<strong>Average Result:</strong> Gana Koota shows medium points - Deva-Manushya relationship. There is good compatibility between the groom and bride\'s natures. The person with Deva gana is spiritual and calm in nature, while the person with Manushya gana is realistic and hardworking. This combination brings a healthy balance in married life.',


                'pred_bad': '<strong>Inauspicious Result:</strong> Gana Koota shows incompatibility - Deva-Rakshasa relationship. There are extremely significant differences in nature. The calm and spiritual nature of Deva gana may not match with the intense and aggressive nature of Rakshasa gana. There is a high possibility of serious conflicts in married life. Astrologer\'s consultation and special remedies are recommended.'


            },


            'bhakoot': {


                'title': '7. Bhakoot Koota - Family Welfare and Prosperity',


                'good': 'Bhakoot Koota shows full points - no Bhakoot dosha! Family welfare, financial prosperity, and happiness will prevail.',


                'mid': 'Bhakoot Koota shows medium points. There may be some fluctuations in family life.',


                'bad': 'Bhakoot Koota shows dosha present! There is a possibility of family unrest and financial crisis. Remedies for Bhakoot dosha are recommended.',


                'pred_good': '<strong>Auspicious Result:</strong> Bhakoot Koota shows full points - no Bhakoot dosha! This means family welfare, financial prosperity, and happiness will prevail in their married life. Their home will be filled with wealth and prosperity, and there will be a joyful atmosphere in the family. This is an extremely auspicious sign for marriage.',


                'pred_mid': '<strong>Average Result:</strong> Bhakoot Koota shows medium points. There may be some fluctuations in family life but no serious crises. Efforts should be made for financial stability. To increase understanding among family members, family discussions and spending quality time together are important.',


                'pred_bad': '<strong>Inauspicious Result:</strong> Bhakoot Koota shows {{ result.kootas.bhakoot.result }} dosha present! This means family unrest, financial crisis, and mental instability may occur in married life. Caution should be taken especially during the initial years of marriage. Special prayers and astrologer\'s consultation are extremely important for Bhakoot dosha remedy.'


            },


            'nadi': {


                'title': '8. Nadi Koota - Progeny Happiness and Genetic Health',


                'good': 'Nadi Koota shows full points - Nadi dosha is completely absent! Progeny happiness is extremely auspicious. You will have healthy and intelligent children.',


                'bad': 'Nadi Koota shows incompatibility - Nadi dosha is present! There is a possibility of problems related to children and health complications. Special prayers and astrologer\'s consultation are extremely important for Nadi dosha remedy.',


                'pred_good': '<strong>Auspicious Result:</strong> Nadi Koota shows full points - Nadi dosha is completely absent! Progeny happiness is extremely auspicious. You will have healthy and intelligent children. Positive energy and enthusiasm will remain in life. This is extremely auspicious for married life and progeny.',


                'pred_mid': '<strong>Average Result:</strong> Nadi Koota shows medium points - Nadi dosha is partially present. Progeny happiness may be limited. This dosha can be reduced through special prayers and astrologer\'s consultation.',


                'pred_bad': '<strong>Inauspicious Result:</strong> Nadi Koota shows incompatibility - Nadi dosha is present! There is a high possibility of problems related to children and health complications. Special prayers and astrologer\'s consultation are extremely important for Nadi dosha remedy. With timely appropriate remedies, this dosha can be reduced.'


            }


        },


        # Description templates (with {boy_*} and {girl_*} placeholders)


        'description_templates': {


            'varna': "{boy_label}'s varna is {boy_varna} and {girl_label}'s varna is {girl_varna}.",


            'vashya': "{boy_label}'s vashya is {boy_vashya} and {girl_label}'s vashya is {girl_vashya}.",


            'tara': "From {girl_label}'s nakshatra to {boy_label}'s nakshatra, tara: {tara_girl_to_boy_name} ({tara_girl_to_boy}); from {boy_label} to {girl_label}, tara: {tara_boy_to_girl_name} ({tara_boy_to_girl}).",


            'yoni': "{boy_label}'s yoni is '{boy_yoni}' and {girl_label}'s yoni is '{girl_yoni}'.",


            'graha_maitri': "{boy_label}'s rashi lord is '{boy_lord}' and {girl_label}'s rashi lord is '{girl_lord}'.",


            'gana': "{boy_label}'s gana is '{boy_gana}' and {girl_label}'s gana is '{girl_gana}'.",


            'bhakoot': "{girl_label}'s rashi '{girl_rashi}' and {boy_label}'s rashi '{boy_rashi}' bhakoot matching.",


            'nadi': "{boy_label}'s nadi is '{boy_nadi}' and {girl_label}'s nadi is '{girl_nadi}'.",


        },


        'result_map': {


            'উত্তম': 'Excellent', 'মধ্যম': 'Average', 'অমিল': 'Incompatible', 'অশুভ': 'Inauspicious',


            'উত্তম (অতি শুভ)': 'Excellent (Very Auspicious)',


            'উত্তম (একে যোনি)': 'Excellent (Same Yoni)',


            'উত্তম (মিত্ৰ যোনি)': 'Excellent (Friendly Yoni)',


            'মধ্যম (সাধাৰণ)': 'Average (Normal)',


            'মধ্যম (সামান্য)': 'Average (Minor)',


            'অশুভ (শত্ৰু যোনি)': 'Inauspicious (Enemy Yoni)',


            'উত্তম (অধি মিত্ৰ)': 'Excellent (Best Friend)',


            'উত্তম (মিত্ৰ)': 'Excellent (Friend)',


            'মধ্যম (সম)': 'Average (Neutral)',


            'অমিল (শত্ৰু)': 'Incompatible (Enemy)',


            'অমিল (অধি শত্ৰু)': 'Incompatible (Arch Enemy)',


            'অশুভ (অধি শত্ৰু)': 'Inauspicious (Arch Enemy)',


            'উত্তম (একে গণ)': 'Excellent (Same Gana)',


            'অমিল (দেৱ-ৰাক্ষস)': 'Incompatible (Deva-Rakshasa)',


            'অমিল (মনুষ্য-ৰাক্ষস)': 'Incompatible (Manushya-Rakshasa)',


            'উত্তম (নাড়ী দোষ নাই)': 'Excellent (No Nadi Dosha)',


        },


        'verdict_map': {


            'উত্তম (অতি শুভ)': 'Excellent (Very Auspicious)',


            'মধ্যম (শুভ)': 'Good (Auspicious)',


            'মধ্যম (গ্ৰহণযোগ্য)': 'Average (Acceptable)',


            'অমিল (সাৱধানতা প্ৰয়োজন)': 'Poor (Caution Needed)',


            'অশুভ (বিবাহ পৰামৰ্শিত নহয়)': 'Inauspicious (Not Recommended)',


        },


        'verdict_desc_map': {


            'এই যোটক অতি উত্তম। বিবাহৰ বাবে অত্যন্ত শুভ আৰু সুপাৰিশিত। দাম্পত্য জীৱন সুখময়, সমৃদ্ধিশালী আৰু দীৰ্ঘস্থায়ী হ\'ব।': 'This matching is excellent. Highly auspicious and recommended for marriage. Married life will be happy, prosperous, and long-lasting.',


            'এই যোটক মধ্যম শ্ৰেণীৰ। বিবাহৰ বাবে গ্ৰহণযোগ্য। সামান্য প্ৰতিকাৰৰ দ্বাৰা দাম্পত্য জীৱন সুখময় কৰিব পাৰি।': 'This matching is of medium grade. Acceptable for marriage. Minor remedies can make married life happy.',


            'এই যোটক গড় মানৰ। কিছুমান দোষ থাকিলেও উপযুক্ত প্ৰতিকাৰৰ দ্বাৰা বিবাহ সম্ভৱ। জ্যোতিষীৰ পৰামৰ্শ লোৱাটো উচিত।': 'This matching is average. Despite some doshas, marriage is possible with appropriate remedies. Astrologer consultation is advised.',


            'এই যোটকত যথেষ্ট অমিল আছে। বিবাহৰ পূৰ্বে জ্যোতিষীৰ পৰামৰ্শ আৰু প্ৰতিকাৰ অতি জৰুৰী।': 'This matching has significant incompatibilities. Astrologer consultation and remedies are essential before marriage.',


            'এই যোটক অশুভ। পৰম্পৰাগতভাৱে এনে যোটকত বিবাহ পৰামৰ্শিত নহয়। তথাপিও জ্যোতিষীৰ পৰামৰ্শ লওক।': 'This matching is inauspicious. Traditionally, marriage is not recommended in such matchings. Still, consult an astrologer.',


        },


        'remedies': [


            'Recite Hanuman Chalisa daily',


            'Observe fast on Tuesdays and visit Hanuman temple',


            'Donate vermilion (sindoor) and masoor dal (red lentils)',


            'Avoid wearing red-colored clothes',


            "Chant Mars mantra: 'Om Kram Kreem Kroum Sah Bhaumaya Namah'",


            'Perform Mangalik Dosha Nivaran Puja before marriage',


            'Offer water to Tulsi plant and perform parikrama',


        ],


        'pdf_title': '💍 Marriage Matching Report',


        'pdf_score_unit': '/ {max_score} Guna',


        'pdf_mars_position': 'Mars in {house}th House',


        'pdf_conclusion_title': '🌟 Overall Assessment & Conclusion',


        'pdf_conclusion_text': 'In the marriage matching of {boy} and {girl}, a total of {total} / {max_score} Guna has been obtained.',


        'pdf_blessing': '✨ May God make your married life happy, prosperous, and long-lasting.\nShubham Bhavatu. 🙏',


        'pdf_nadi_warning': '⚠️ <b>Nadi Dosha</b> present - marriage is not recommended without Nadi Dosha remedy.',


        'pdf_bhakoot_warning': '⚠️ <b>Bhakoot Dosha</b> present - perform remedies for family welfare.',


        'pdf_footer': '© Dhrubatara AI · First Assamese Astrology Software by Ditul Sarma',


        'pdf_astro_title': 'Shramena Ganyate Koshtheem',


        'mangalik_heading': 'Mangalik Dosha (Kuja Dosha) Analysis',


        'mangalik_remedies_heading': 'Mangalik Dosha Remedies',


        'important_label': 'Important',


        'severity_map': {'তীব্ৰ': 'Severe', 'মধ্যম': 'Moderate', 'সামান্য': 'Mild', 'অনুপস্থিত': 'Absent'},


        'cancellation_map': {


            'দোষ সাম্য (উভয় মাংগলিক হোৱাৰ বাবে দোষৰ প্ৰভাৱ পৰস্পৰে নিষ্ক্ৰিয় কৰে)': 'Dosha Samya (Both are Mangalik, so the dosha effects cancel each other)',


            'কোনো মাংগলিক দোষ নাই': 'No Mangalik Dosha',


        },


        'conclusion_heading': 'Overall Assessment & Conclusion',


        'conclusion_text': 'In the marriage matching of {boy} and {girl}, a total of {total} / {max_score} Guna has been obtained.',


        'nadi_warning': 'This matching has Nadi Dosha present. Marriage without Nadi Dosha remedy is not recommended. Consult an astrologer for appropriate remedies.',


        'bhakoot_warning': 'This matching has Bhakoot Dosha present. For family welfare, Bhakoot Dosha remedies should be performed.',


        'blessing': 'May God make your married life happy, prosperous, and long-lasting.\nShubham Bhavatu. 🙏',


        'new_matching_btn': 'New Matching',


        'mars_in_house_label': 'Mars in {house}th House',





    }


}





def get_jotok_labels(lang='as'):


    """Get Jotok Milan labels in the specified language."""


    return JOTOK_LABELS.get(lang, JOTOK_LABELS['as'])








def get_dosha_labels(lang='as'):


    """Get Graha Dosha labels in the specified language."""


    return DOSHA_LABELS.get(lang, DOSHA_LABELS['as'])








# ═══════════════════════════════════════════════════════════════
#  GRAHA YOGA i18n Labels
# ═══════════════════════════════════════════════════════════════

YOGA_LABELS = {
    'as': {
        'title': 'গ্ৰহ যোগ বিশ্লেষণ',
        'effect_label': 'ফল',
        'category_label': 'শ্রেণী',
        'no_yoga': 'কোনো বিশেষ যোগ ধৰা পৰা নাই।',
        'yoga_names': {
            'ruchaka': 'ৰুচক যোগ (পঞ্চ মহাপুৰুষ)',
            'bhadra': 'ভদ্ৰ যোগ (পঞ্চ মহাপুৰুষ)',
            'hamsa': 'হংস যোগ (পঞ্চ মহাপুৰুষ)',
            'malavya': 'মালব্য যোগ (পঞ্চ মহাপুৰুষ)',
            'sasa': 'শশ যোগ (পঞ্চ মহাপুৰুষ)',
            'gajakesari': 'গজকেশৰী যোগ',
            'budhaditya': 'বুধাদিত্য যোগ',
            'lakshmi': 'লক্ষ্মী যোগ',
            'vipareeta_raja': 'বিপৰীত ৰাজযোগ',
            'dhana': 'ধন যোগ',
            'raja': 'ৰাজযোগ',
            'sunapha': 'সুনফা যোগ',
            'anapha': 'অনফা যোগ',
            'durudhara': 'দুৰুধৰা যোগ',
            'vasumati': 'বসুমতী যোগ',
            'amala': 'অমলা যোগ',
            'parvata': 'পৰ্বত যোগ',
            'kahala': 'কহল যোগ',
        },
        'yoga_categories': {
            'পঞ্চ মহাপুৰুষ যোগ': 'পঞ্চ মহাপুৰুষ যোগ',
            'শুভ যোগ': 'শুভ যোগ',
            'ধন যোগ': 'ধন যোগ',
            'ৰাজযোগ': 'ৰাজযোগ',
            'চন্দ্ৰ যোগ': 'চন্দ্ৰ যোগ',
        },
        'yoga_descriptions': {},
    },
    'bn': {
        'title': 'গ্রহ যোগ বিশ্লেষণ',
        'effect_label': 'ফল',
        'category_label': 'শ্রেণী',
        'no_yoga': 'কোনো বিশেষ যোগ ধরা পড়েনি।',
        'yoga_names': {
            'ruchaka': 'রুচক যোগ (পঞ্চ মহাপুরুষ)',
            'bhadra': 'ভদ্র যোগ (পঞ্চ মহাপুরুষ)',
            'hamsa': 'হংস যোগ (পঞ্চ মহাপুরুষ)',
            'malavya': 'মালব্য যোগ (পঞ্চ মহাপুরুষ)',
            'sasa': 'শশ যোগ (পঞ্চ মহাপুরুষ)',
            'gajakesari': 'গজকেশরী যোগ',
            'budhaditya': 'বুধাদিত্য যোগ',
            'lakshmi': 'লক্ষ্মী যোগ',
            'vipareeta_raja': 'বিপরীত রাজযোগ',
            'dhana': 'ধন যোগ',
            'raja': 'রাজযোগ',
            'sunapha': 'সুনফা যোগ',
            'anapha': 'অনফা যোগ',
            'durudhara': 'দুরুধরা যোগ',
            'vasumati': 'বসুমতী যোগ',
            'amala': 'অমলা যোগ',
            'parvata': 'পর্বত যোগ',
            'kahala': 'কহল যোগ',
        },
        'yoga_categories': {
            'পঞ্চ মহাপুৰুষ যোগ': 'পঞ্চ মহাপুরুষ যোগ',
            'শুভ যোগ': 'শুভ যোগ',
            'ধন যোগ': 'ধন যোগ',
            'ৰাজযোগ': 'রাজযোগ',
            'চন্দ্ৰ যোগ': 'চন্দ্র যোগ',
        },
        'yoga_descriptions': {},
    },
    'hi': {
        'title': 'ग्रह योग विश्लेषण',
        'effect_label': 'फल',
        'category_label': 'श्रेणी',
        'no_yoga': 'कोई विशेष योग नहीं मिला।',
        'yoga_names': {
            'ruchaka': 'रुचक योग (पंच महापुरुष)',
            'bhadra': 'भद्र योग (पंच महापुरुष)',
            'hamsa': 'हंस योग (पंच महापुरुष)',
            'malavya': 'मालव्य योग (पंच महापुरुष)',
            'sasa': 'शश योग (पंच महापुरुष)',
            'gajakesari': 'गजकेशरी योग',
            'budhaditya': 'बुधादित्य योग',
            'lakshmi': 'लक्ष्मी योग',
            'vipareeta_raja': 'विपरीत राजयोग',
            'dhana': 'धन योग',
            'raja': 'राजयोग',
            'sunapha': 'सुनफा योग',
            'anapha': 'अनफा योग',
            'durudhara': 'दुरुधरा योग',
            'vasumati': 'वसुमती योग',
            'amala': 'अमला योग',
            'parvata': 'पर्वत योग',
            'kahala': 'कहल योग',
        },
        'yoga_categories': {
            'পঞ্চ মহাপুৰুষ যোগ': 'पंच महापुरुष योग',
            'শুভ যোগ': 'शुभ योग',
            'ধন যোগ': 'धन योग',
            'ৰাজযোগ': 'राजयोग',
            'চন্দ্ৰ যোগ': 'चंद्र योग',
        },
        'yoga_descriptions': {},
    },
    'en': {
        'title': 'Planetary Yoga Analysis',
        'effect_label': 'Effect',
        'category_label': 'Category',
        'no_yoga': 'No special yogas found.',
        'yoga_names': {
            'ruchaka': 'Ruchaka Yoga (Pancha Mahapurusha)',
            'bhadra': 'Bhadra Yoga (Pancha Mahapurusha)',
            'hamsa': 'Hamsa Yoga (Pancha Mahapurusha)',
            'malavya': 'Malavya Yoga (Pancha Mahapurusha)',
            'sasa': 'Sasa Yoga (Pancha Mahapurusha)',
            'gajakesari': 'Gajakesari Yoga',
            'budhaditya': 'Budhaditya Yoga',
            'lakshmi': 'Lakshmi Yoga',
            'vipareeta_raja': 'Vipareeta Raja Yoga',
            'dhana': 'Dhana Yoga',
            'raja': 'Raja Yoga',
            'sunapha': 'Sunapha Yoga',
            'anapha': 'Anapha Yoga',
            'durudhara': 'Durudhara Yoga',
            'vasumati': 'Vasumati Yoga',
            'amala': 'Amala Yoga',
            'parvata': 'Parvata Yoga',
            'kahala': 'Kahala Yoga',
        },
        'yoga_categories': {
            'পঞ্চ মহাপুৰুষ যোগ': 'Pancha Mahapurusha Yoga',
            'শুভ যোগ': 'Shubh Yoga',
            'ধন যোগ': 'Dhana Yoga',
            'ৰাজযোগ': 'Raja Yoga',
            'চন্দ্ৰ যোগ': 'Chandra Yoga',
        },
        'yoga_descriptions': {},
    },
}


def get_yoga_labels(lang='as'):


    """Get Graha Yoga labels in the specified language."""


    return YOGA_LABELS.get(lang, YOGA_LABELS['as'])








SHANI_SARE_SATI_LABELS = {


    'as': {


        'title': 'শনিৰ সাৰে সাতি',


        'intro': 'এই তালিকাখন শনিৰ প্ৰতি ৰাশীত প্ৰায় ২.৫ বছৰৰ চলাচলৰ ভিত্তিত অনুমান কৰা হৈছে। আসল সময়কাল বর্তমান গ্ৰহ গতিবিধি আৰু জন্মে থকা শনিৰ অবস্থানৰ ওপৰত নিৰ্ভৰ কৰে।',


        'age_col': 'আনুমানিক বয়স',


        'year_col': 'আনুমানিক চন',


        'shani_rasi_col': 'শনি ৰাশি',


        'phase_col': 'দশা',


        'no_data': 'শনি সাৰেসাতী বা ঢৈয়াৰ তথ্য উপলব্ধ নহয়।',


    },


    'bn': {


        'title': 'শনির সারে সাতি',


        'intro': 'এই তালিকাখন শনির প্রতি রাশীত প্রায় ২.৫ বছরের চলাচলের ভিত্তিত অনুমান করা হয়েছে। আসল সময়কাল বর্তমান গ্রহ গতিবিধি এবং জন্মে থকা শনির অবস্থানের ওপরত নির্ভর করে।',


        'age_col': 'আনুমানিক বয়স',


        'year_col': 'আনুমানিক সন',


        'shani_rasi_col': 'শনি রাশি',


        'phase_col': 'দশা',


        'no_data': 'শনি সারেসাতী বা ঢৈয়ার তথ্য উপলব্ধ নেই।',


    },


    'hi': {


        'title': 'शनि की साढ़ेसाती',


        'intro': 'यह सारणी शनि की प्रत्येक राशि में लगभग ২.৫ वर्ष की यात्रा के आधार पर अनुमानित है। वास्तविक समयकाल वर्तमान ग्रह गतिविधि और जन्म के समय शनि की स्थिति पर निर्भर करता है।',


        'age_col': 'आनुमानिक आयु',


        'year_col': 'आनुमानिक वर्ष',


        'shani_rasi_col': 'शनि राशि',


        'phase_col': 'चरण',


        'no_data': 'शनि साढ़ेसाती या ढৈয়а की जानकारी उपलब्ध नहीं है।',


    },


    'en': {


        'title': 'Saturn Sade Sati',


        'intro': 'This table is estimated based on Saturn transit through each rashi lasting approximately 2.5 years. Actual duration depends on current planetary motion and the position of Saturn at birth.',


        'age_col': 'Est. Age',


        'year_col': 'Est. Year',


        'shani_rasi_col': 'Saturn Rashi',


        'phase_col': 'Phase',


        'no_data': 'No Sade Sati or Dhaiya data available.',


    },


}








def get_shani_sare_sati_labels(lang='as'):


    """Get Shani Sare Sati labels in the specified language."""


    return SHANI_SARE_SATI_LABELS.get(lang, SHANI_SARE_SATI_LABELS['as'])








def translate_shani_sare_sati_data(data, lang='as'):


    """Translate shani sare sati data phase names (English keys from pdf_generator to target lang)."""


    if not data:


        return data


    phase_map = DOSHA_LABELS.get(lang, DOSHA_LABELS['as']).get('shani_phase_names', {})


    translated = []


    for item in data:


        t = dict(item)


        if 'phase' in t:


            t['phase'] = phase_map.get(t['phase'], t['phase'])


        translated.append(t)


    return translated








def translate_jotok_result(result, lang='as'):


    """


    Translate a Jotok Milan result dict from Assamese (engine output) to the target language.


    Returns a new dict with translated body text (descriptions, results, verdicts, remedies).


    """


    if lang == 'as':


        return result  # No translation needed


    


    L = get_jotok_labels(lang)


    


    # Translate koota results


    translated_kootas = {}


    desc_templates = L.get('description_templates', {})


    result_map = L.get('result_map', {})


    boy_label = L.get('boy_label', 'Groom')


    girl_label = L.get('girl_label', 'Bride')


    


    # Helper: translate an Assamese string value using reverse map


    def _tr(rev_key, val):


        if val is None or val == '':


            return ''


        # Try integer lookup first


        int_map = L.get(rev_key.replace('_rev', '_names'), {})


        if isinstance(val, int) and val in int_map:


            return int_map[val]


        # Try reverse string lookup


        rev_map = L.get(rev_key, {})


        if val in rev_map:


            return rev_map[val]


        return str(val)


    


    for key, k in result.get('kootas', {}).items():


        tk = dict(k)  # Copy


        


        # Translate result string (with fallback for dynamic strings)


        raw_result = k['result']


        translated_result = result_map.get(raw_result, None)


        if translated_result is None:


            # Try partial translation for dynamic strings like 'অশুভ (৫-৯ দোষ (পঞ্চ-নৱম))'


            # Replace known Assamese words


            partial = raw_result


            for asm_word, tgt_word in [


                ('অশুভ', result_map.get('অশুভ', 'Inauspicious')),


                ('উত্তম', result_map.get('উত্তম', 'Excellent')),


                ('মধ্যম', result_map.get('মধ্যম', 'Average')),


                ('অমিল', result_map.get('অমিল', 'Incompatible')),


                ('দোষ', 'Dosha' if lang == 'en' else ('दोष' if lang == 'hi' else ('দোষ' if lang == 'bn' else 'দোষ'))),


                ('দ্বি-দ্বাদশ', '2-12' if lang == 'en' else ('२-१२' if lang == 'hi' else ('২-১২' if lang == 'bn' else 'দ্বি-দ্বাদশ'))),


                ('পঞ্চ-নৱম', '5-9' if lang == 'en' else ('५-९' if lang == 'hi' else ('৫-৯' if lang == 'bn' else 'পঞ্চ-নৱম'))),


                ('ষষ্ঠ-অষ্টম', '6-8' if lang == 'en' else ('६-८' if lang == 'hi' else ('৬-৮' if lang == 'bn' else 'ষষ্ঠ-অষ্টম'))),


            ]:


                if asm_word in partial:


                    partial = partial.replace(asm_word, tgt_word)


            # Replace Bengali digits with target script digits


            bengali_digits = '০১২৩৪৫৬৭৮৯'


            if lang == 'en':


                for i, bd in enumerate(bengali_digits):


                    partial = partial.replace(bd, str(i))


            elif lang == 'hi':


                hindi_digits = '०१२३४५६७८९'


                for i, bd in enumerate(bengali_digits):


                    partial = partial.replace(bd, hindi_digits[i])


            translated_result = partial


        tk['result'] = translated_result


        


        # Translate description using template


        template = desc_templates.get(key, '')


        if template:


            fmt_args = {


                'boy_label': boy_label,


                'girl_label': girl_label,


                'boy_varna': _tr('varna_rev', k.get('boy_varna', '')),


                'girl_varna': _tr('varna_rev', k.get('girl_varna', '')),


                'boy_vashya': _tr('vashya_rev', k.get('boy_vashya', '')),


                'girl_vashya': _tr('vashya_rev', k.get('girl_vashya', '')),


                'tara_girl_to_boy': k.get('tara_girl_to_boy', ''),


                'tara_girl_to_boy_name': _tr('tara_names', k.get('tara_girl_to_boy', 0)),


                'tara_boy_to_girl': k.get('tara_boy_to_girl', ''),


                'tara_boy_to_girl_name': _tr('tara_names', k.get('tara_boy_to_girl', 0)),


                'boy_yoni': _tr('yoni_rev', k.get('boy_yoni', '')),


                'girl_yoni': _tr('yoni_rev', k.get('girl_yoni', '')),


                'boy_lord': _tr('lord_rev', k.get('boy_lord', '')),


                'girl_lord': _tr('lord_rev', k.get('girl_lord', '')),


                'boy_gana': _tr('gana_rev', k.get('boy_gana', '')),


                'girl_gana': _tr('gana_rev', k.get('girl_gana', '')),


                'boy_rashi': _tr('rashi_rev', k.get('boy_rashi', '')),


                'girl_rashi': _tr('rashi_rev', k.get('girl_rashi', '')),


                'boy_nadi': _tr('nadi_rev', k.get('boy_nadi', '')),


                'girl_nadi': _tr('nadi_rev', k.get('girl_nadi', '')),


            }


            try:


                # For bhakoot, get rashi from boy/girl data (not in koota dict)


                if key == 'bhakoot':


                    fmt_args['boy_rashi'] = result.get('boy', {}).get('rashi', '')


                    fmt_args['girl_rashi'] = result.get('girl', {}).get('rashi', '')


                tk['description'] = template.format(**fmt_args)


            except (KeyError, ValueError):


                pass  # Keep original if formatting fails


        


        translated_kootas[key] = tk


    


    # Translate verdict


    verdict_map = L.get('verdict_map', {})


    verdict_desc_map = L.get('verdict_desc_map', {})


    


    # Translate boy/girl profile data


    def _tr_profile(person):


        if not person:


            return {}


        p = dict(person)


        p['rashi'] = _tr('rashi_rev', p.get('rashi', ''))


        p['nakshatra'] = _tr('nakshatra_rev', p.get('nakshatra', ''))


        p['lagna'] = _tr('rashi_rev', p.get('lagna', ''))


        return p


    


    translated = {


        'boy': _tr_profile(result.get('boy', {})),


        'girl': _tr_profile(result.get('girl', {})),


        'kootas': translated_kootas,


        'total_score': result.get('total_score', 0),


        'max_score': result.get('max_score', 36),


        'verdict': verdict_map.get(result.get('verdict', ''), result.get('verdict', '')),


        'verdict_class': result.get('verdict_class', ''),


        'verdict_desc': verdict_desc_map.get(result.get('verdict_desc', ''), result.get('verdict_desc', '')),


        'mangalik': result.get('mangalik', {}),


        'has_nadi_dosha': result.get('has_nadi_dosha', False),


        'has_bhakoot_dosha': result.get('has_bhakoot_dosha', False),


    }


    


    # Translate mangalik severity, cancellation, and remedies


    mangalik = translated['mangalik']


    severity_map = L.get('severity_map', {})


    cancellation_map = L.get('cancellation_map', {})


    if 'boy_severity' in mangalik:


        mangalik['boy_severity'] = severity_map.get(mangalik['boy_severity'], mangalik['boy_severity'])


    if 'girl_severity' in mangalik:


        mangalik['girl_severity'] = severity_map.get(mangalik['girl_severity'], mangalik['girl_severity'])


    if 'cancellation' in mangalik and mangalik['cancellation']:


        mangalik['cancellation'] = cancellation_map.get(mangalik['cancellation'], mangalik['cancellation'])


    if 'remedies' in mangalik:


        mangalik['remedies'] = L.get('remedies', mangalik['remedies'])


    


    return translated


"""


══════════════════════════════════════════════════════════════


  GRAHA DOSHA i18n Labels


══════════════════════════════════════════════════════════════


"""





DOSHA_LABELS = {


    'as': {


        'title': 'গ্ৰহ দোষ বিশ্লেষণ',


        'present_label': 'উপস্থিত',


        'absent_label': 'অনুপস্থিত',


        'remedies_heading': 'প্ৰতিকাৰ (Remedies)',


        'no_remedies': 'কোনো বিশেষ প্ৰতিকাৰ নাই।',


        'severity_levels': {


            '0': 'অনুপস্থিত', '1': 'সামান্য', '2': 'মধ্যম', '3': 'তীব্ৰ', '4': 'অতি তীব্ৰ'


        },


        'dosha_names': {


            'mangal_dosha': 'মঙ্গল দোষ',


            'kaal_sarp_dosha': 'কাল সৰ্প দোষ',


            'pitra_dosha': 'পিতৃ দোষ',


            'grahan_dosha': 'গ্ৰহণ দোষ',


            'nadi_dosha': 'নাড়ী দোষ',


            'shani_dosha': 'শনি দোষ (সাড়ে সাতী)',


            'guru_chandal_dosha': 'গুৰু-চাণ্ডাল দোষ',


            'kemadruma_dosha': 'কেমদ্ৰুম দোষ',


        },


        'descriptions': {


            'mangal_dosha': "মঙ্গল গ্রহ লগ্ন, চতুর্থ, সপ্তম, অষ্টম বা দ্বাদশ ভাবত অবস্থান কৰিলে মঙ্গল দোষ হয়। ই বৈবাহিক জীৱনত সমস্যা, কলহ, আৰু বিলম্বিত বিবাহৰ কাৰণ হ'ব পাৰে।",


            'kaal_sarp_dosha': "যতিয়া ৰাহু আৰু কেতুৰ মাজত সকলো গ্রহ আবদ্ধ থাকে, তেতিয়া কাল সর্প দোষ হয়। ই জীৱনত বাধা, ভয়, অনিদ্রা, আৰু কর্মক্ষেত্রত সংঘর্ষৰ সৃষ্টি কৰে।",


            'pitra_dosha': "সূর্য্য ৰাহু বা শনিৰ সৈতে যুক্ত হ'লে বা ৰাহু-কেতু নবম ভাবত থাকিলে পিতৃ দোষ হয়। ই সন্তানহীনতা, পিতৃ-পুত্রৰ সম্পর্কত টান, আৰু পারিবারিক অশান্তিৰ কাৰণ হয়।",


            'grahan_dosha': "সূর্য্য বা চন্দ্র ৰাহু-কেতুৰ সৈতে যুক্ত হ'লে গ্রহণ দোষ হয়। ই স্বাস্থ্যজনিত সমস্যা, মানসিক অস্থিৰতা, আৰু কর্মজীৱনত অনিশ্চয়তাৰ সৃষ্টি কৰে।",


            'nadi_dosha': "বিবাহৰ বাবে গুরুত্বপূর্ণ। স্বামী-স্ত্রীৰ নক্ষত্র একে নাড়ীত পৰিলে নাড়ী দোষ হয়। ই সন্তানহীনতা, স্বাস্থ্যজনিত সমস্যা, আৰু দাম্পত্য কলহৰ কাৰণ হ'ব পাৰে।",


            'shani_dosha': "শনি গ্রহৰ অশুভ প্রভাৱ। বিশেষকৈ সাড়ে সাতী (সাত বছৰৰ সময়) অতি কষ্টদায়ক। ই আর্থিক সংকট, স্বাস্থ্যহানি, আৰু মানসিক চাপৰ সৃষ্টি কৰে।",


            'guru_chandal_dosha': "বৃহস্পতি আৰু ৰাহুৰ নাইবা কেতু গ্রহৰ সৈতে যুতি হ'লে গুরু-চাণ্ডাল দোষ হয়। ই জ্ঞান আৰু নীতিৰ বিরোধ, ধর্মীয় অনাস্থা, আৰু শিক্ষাত বাধাৰ সৃষ্টি কৰে।",


            'kemadruma_dosha': "চন্দ্রৰ দুয়োফালে কোনো গ্রহ নাথাকিলে কেমদ্রুম দোষ হয়। ই মানসিক অস্থিৰতা, অকলশৰীয়া অনুভৱ, আৰু দরিদ্রতাৰ কাৰণ হ'ব পাৰে।",


        },


        'remedies_list': {


            'mangal_dosha': ["প্রতিদিন হনুমান চালিচা পাঠ কৰক", "মঙ্গলবারে ব্রত ৰাখক", "সেন্দুৰ আৰু মঙ্গল ফুল চড়ক", "লাল পুরোহিত পরিধান কৰক", "তুলসী দূর্বা বলি দিয়ক"],


            'kaal_sarp_dosha': ["নাগ পঞ্চমীৰ দিনা বিশেষ পূজা কৰক", "শিৱলিংগত দুগ্ধ অভিষেক কৰক", "রাহু-কেতু মন্ত্র জপ কৰক", "গরুৰ নাড়ী বলি দিয়ক", "নাগ দোষ নিবাৰণ যজ্ঞ কৰক"],


            'pitra_dosha': ["পিতৃপক্ষত শ্রাদ্ধ কৰক", "প্রতিদিন সূর্য্যক অর্ঘ্য দিয়ক", "আহত গছৰ গুরত ফুল দিয়ক", "পিতৃ দোষ নিবাৰণ বন্দনা কৰক"],


            'grahan_dosha': ["গ্রহণৰ সময়ত মন্ত্র জাপ কৰক", "দান-পুণ্য কৰক", "আদিত্য হৃদয় স্তোত্র পাঠ কৰক", "সূর্য্যক জল অর্পণ কৰক"],


            'nadi_dosha': ["নাড়ী দোষ নিবাৰণ পূজা কৰাওক", "মহামৃত্যুঞ্জয় মন্ত্র জপ কৰক", "শিৱ-পার্বতীৰ উপাসনা কৰক", "সন্তানৰ বাবে বিশেষ অনুষ্ঠান কৰক"],


            'shani_dosha': ["শনিবারে হনুমান মন্দিৰ দর্শন কৰক", "তিল তেলৰ দীপ জ্বলাওক", "শনি মন্ত্র জপ কৰক: 'ওঁ শং শনৈশ্চরায় নমঃ'", "কালা বস্ত্র আৰু তিল দান কৰক", "শনি চালিচা পাঠ কৰক"],


            'guru_chandal_dosha': ["বৃহস্পতিবারে ব্রত ৰাখক", "হালধীয়া রঙৰ বস্ত্র পরিধান কৰক", "গুরু মন্ত্র জপ কৰক", "ব্রাহ্মণক খাদ্য দান কৰক", "গুরু-চাণ্ডাল দোষ নিবাৰণ জপ"],


            'kemadruma_dosha': ["চন্দ্র গ্রহৰ মন্ত্র জপ কৰক: 'ওঁ শ্রাং শ্রীং শ্রৌং সঃ চন্দ্রায় নমঃ'", "চন্দ্র পূজা কৰক", "গরুৰ দুধ দান কৰক", "সরোবর মন্দিৰ দর্শন কৰক"],


        },


        'shani_phase_names': {


            'Rising': 'উদীয়মান',


            'Peak': 'শীৰ্ষ',


            'Setting': 'অস্তগামী',


            'Dhaiya': 'ঢৈয়া',


            'Not Running': 'সাড়ে সাতী চলি থকা নাই',


        },


    },


    'bn': {


        'title': 'গ্রহ দোষ বিশ্লেষণ',


        'present_label': 'উপস্থিত',


        'absent_label': 'অনুপস্থিত',


        'remedies_heading': 'প্রতিকার (Remedies)',


        'no_remedies': 'কোনো বিশেষ প্রতিকার নেই।',


        'severity_levels': {


            '0': 'অনুপস্থিত', '1': 'সামান্য', '2': 'মধ্যম', '3': 'তীব্র', '4': 'অতি তীব্র'


        },


        'dosha_names': {


            'mangal_dosha': 'মঙ্গল দোষ',


            'kaal_sarp_dosha': 'কাল সর্প দোষ',


            'pitra_dosha': 'পিতৃ দোষ',


            'grahan_dosha': 'গ্রহণ দোষ',


            'nadi_dosha': 'নাড়ী দোষ',


            'shani_dosha': 'শনি দোষ (সাড়ে সাতী)',


            'guru_chandal_dosha': 'গুরু-চাণ্ডাল দোষ',


            'kemadruma_dosha': 'কেমদ্রুম দোষ',


        },


        'descriptions': {


            'mangal_dosha': '\'মঙ্গল গ্রহ লগ্ন, চতুর্থ, সপ্তম, অষ্টম বা দ্বাদশ ভাবত অবস্থান করলে মঙ্গল দোষ হয়। এটি বৈবাহিক জীবনত সমস্যা, কলহ, আৰু বিলম্বিত বিবাহৰ কাৰণ হ\'ব পাৰে।',


            'kaal_sarp_dosha': 'যখন রাহু আৰু কেতুৰ মাজত সকলো গ্রহ আবদ্ধ থাকে, তখন কাল সর্প দোষ হয়। এটি জীবনত বাধা, ভয়, অনিদ্রা, আৰু কর্মক্ষেত্রত সংঘর্ষৰ সৃষ্টি কৰে।',


            'pitra_dosha': '\'সূর্য্য রাহু বা শনিৰ সৈতে যুক্ত হ\'লে বা রাহু-কেতু নবম ভাবত থাকলে পিতৃ দোষ হয়। এটি সন্তানহীনতা, পিতৃ-পুত্রৰ সম্পর্কত টান, আৰু পারিবারিক অশান্তিৰ কাৰণ হয়।',


            'grahan_dosha': '\'সূর্য্য বা চন্দ্র রাহু-কেতুৰ সৈতে যুক্ত হ\'লে গ্রহণ দোষ হয়। এটি স্বাস্থ্যজনিত সমস্যা, মানসিক অস্থিৰতা, আৰু কর্মজীবনত অনিশ্চয়তাৰ সৃষ্টি কৰে।',


            'nadi_dosha': '\'বিবাহৰ বাবে গুরুত্বপূর্ণ। স্বামী-স্ত্রীৰ নক্ষত্র একে নাড়ীত পড়লে নাড়ী দোষ হয়। এটি সন্তানহীনতা, স্বাস্থ্যজনিত সমস্যা, আৰু দাম্পত্য কলহৰ কাৰণ হ\'ব পাৰে।',


            'shani_dosha': 'শনি গ্রহৰ অশুভ প্রভাব। বিশেষকৈ সাড়ে সাতী (সাত বছরৰ সময়) অতি কষ্টদায়ক। এটি আর্থিক সংকট, স্বাস্থ্যহানি, আৰু মানসিক চাপৰ সৃষ্টি কৰে।',


            'guru_chandal_dosha': '\'বৃহস্পতি আৰু রাহুৰ নাইবা কেতু গ্রহৰ সৈতে যুতি হ\'লে গুরু-চাণ্ডাল দোষ হয়। এটি জ্ঞান আৰু নীতিৰ বিৰোধ, ধর্মীয় অনাস্থা, আৰু শিক্ষাত বাধাৰ সৃষ্টি কৰে।',


            'kemadruma_dosha': '\'চন্দ্রৰ দুইফালে কোনো গ্রহ নাथাকলে কেমদ্রুম দোষ হয়। এটি মানসিক অস্থিৰতা, একলশৰীয়া অনুভৱ, আৰু দারিদ্রতাৰ কাৰণ হ\'ব পাৰে।',


        },


        'remedies_list': {


            'mangal_dosha': ['প্রতিদিন হনুমান চালিচা পাঠ করুন', 'মঙ্গলবারে ব্রত রাখুন', 'সেন্দুর আৰু মছুর দালি দান করুন', 'লাল রঙৰ বস্ত্র পৰিহাৰ করুন', "মঙ্গল গ্রহৰ মন্ত্র জপ করুন: 'ওঁ ক্রাং ক্রীং ক্রৌং সঃ ভৌমায় নমঃ'"],


            'kaal_sarp_dosha': ['নাগ পঞ্চমীৰ দিনা বিশেষ পূজা করুন', 'শিৱলিংগত দুগ্ধ অভিষেক করুন', "রাহু-কেতু মন্ত্র জপ করুন: 'ওঁ রাং রাহবে নমঃ'", 'কাল সর্প দোষ নিবারণ পূজা করুন', 'সোমবারে উপবাস রাখুন'],


            'pitra_dosha': ['পিতৃপক্ষত শ্রাদ্ধ করুন', 'প্রতিদিন সূর্য্যক অর্ঘ্য দিয়ক', 'আহত গছৰ গুৰত জল অর্পণ করুন', 'গয়াত পিণ্ডদান করুন', 'পিতৃসকলৰ ফটোৰ সন্মুখত দীপ প্রজ্বলন করুন'],


            'grahan_dosha': ['গ্রহণৰ সময়ত মন্ত্র জপ করুন', 'দান-পুণ্য করুন', 'আদিত্য হৃদয় স্তোত্র পাঠ করুন', 'চন্দ্র গ্রহ মন্ত্র জপ করুন', 'গ্রহণৰ পিছে স্নান করে শুদ্ধ থাকুন'],


            'nadi_dosha': ['নাড়ী দোষ নিবারণ পূজা করুন', 'মহামৃত্যুঞ্জয় মন্ত্র জপ করুন', 'শিৱ-পার্বতীৰ উপাসনা করুন', 'সন্তানৰ বাবে বিশেষ অনুষ্ঠান করুন'],


            'shani_dosha': ['শনিবারে হনুমান মন্দিৰ দর্শন করুন', 'তিল তেলৰ দীপ জ্বালাওক', "শনি মন্ত্র জপ করুন: 'ওঁ শং শনৈশ্চৰায় নমঃ'", 'কালা বস্ত্র আৰু তিল দান করুন', 'শনি চালিচা পাঠ করুন'],


            'guru_chandal_dosha': ['বৃহস্পতিবারে ব্রত রাখুন', 'হলদে রঙৰ বস্ত্র পরিধান করুন', "গুরু গ্রহৰ মন্ত্র জপ করুন: 'ওঁ গ্রাং গ্রীং গ্রৌং সঃ গুৰবে নমঃ'", 'কল গছৰ পূজা করুন', 'আহত গছত জল অর্পণ করুন'],


            'kemadruma_dosha': ["চন্দ্র গ্রহৰ মন্ত্র জপ করুন: 'ওঁ শ্রাং শ্রীং শ্রৌং সঃ চন্দ্রায় নমঃ'", 'সোমবারে উপবাস রাখুন', 'শিৱলিংগত দুগ্ধ অভিষেক করুন', 'মুক্তা ধাৰণ করুন', 'শ্বেত বস্ত্র দান করুন'],


        },


        'shani_phase_names': {


            'Rising': 'উদীয়মান',


            'Peak': 'শীর্ষ',


            'Setting': 'অস্তগামী',


            'Dhaiya': 'ঢৈয়া',


            'Not Running': 'সাড়েসাতী চলছে না',


        },


    },


    'hi': {


        'title': 'ग्रह दोष विश्लेषण',


        'present_label': 'उपस्थित',


        'absent_label': 'अनुपस्थित',


        'remedies_heading': 'प्रतिकार (Remedies)',


        'no_remedies': 'कोई विशेष प्रतिकार नहीं।',


        'severity_levels': {


            '0': 'अनुपस्थित', '1': 'सामान्य', '2': 'मध्यम', '3': 'तीव्र', '4': 'अति तीव्र'


        },


        'dosha_names': {


            'mangal_dosha': 'मंगल दोष',


            'kaal_sarp_dosha': 'काल सर्प दोष',


            'pitra_dosha': 'पितृ दोष',


            'grahan_dosha': 'ग्रहण दोष',


            'nadi_dosha': 'नाड़ी दोष',


            'shani_dosha': 'शनि दोष (साढ़ेसाती)',


            'guru_chandal_dosha': 'गुरु-चांडाल दोष',


            'kemadruma_dosha': 'केमद्रम दोष',


        },


        'descriptions': {


            'mangal_dosha': 'मंगल ग्रह लग्न, चतुर्थ, सप्तम, अष्टम या द्वादश भाव में होने पर मंगल दोष होता है। यह विवाह जीवन में समस्या, कलह और विलंबित विवाह का कारण बन सकता है।',


            'kaal_sarp_dosha': 'जब राहु और केतु के बीच सभी ग्रह बंद होते हैं, तब काल सर्प दोष होता है। यह जीवन में बाधा, भय, अनिद्रा और करियर में संघर्ष का कारण बनता है।',


            'pitra_dosha': 'सूर्य राहु या शनि के साथ या राहु-केतु नवम भाव में होने पर पितृ दोष होता है। यह संतानहीनता, पिता-पुत्र संबंधों में तनाव और पारिवारिक अशांति का कारण बनता है।',


            'grahan_dosha': 'सूर्य या चंद्रमा राहु-केतु के साथ होने पर ग्रहण दोष होता है। यह स्वास्थ्य संबंधी समस्याएं, मानसिक अस्थिरता और करियर में अनिश्चितता पैदा करता है।',


            'nadi_dosha': 'विवाह के लिए महत्वपूर्ण। पति-पत्नी के नक्षत्र एक ही नाड़ी में पड़ने पर नाड़ी दोष होता है। यह संतानहीनता, स्वास्थ्य समस्याएं और दांपत्य कलह का कारण बन सकता है।',


            'shani_dosha': 'शनि ग्रह की अशुभ प्रभाव। विशेषकर साढ़ेसाती (सात साल का समय) अत्यंत कष्टदायक। यह आर्थिक संकट, स्वास्थ्य हानि और मानसिक तनाव पैदा करता है।',


            'guru_chandal_dosha': 'बृहस्पति और राहु या केतु के साथ होने पर गुरु-चांडाल दोष होता है। यह ज्ञान और नीति का विरोध, धार्मिक अविश्वास और शिक्षा में बाधा पैदा करता है।',


            'kemadruma_dosha': 'चंद्रमा के दोनों तरफ कोई ग्रह नहीं होने पर केमद्रम दोष होता है। यह मानसिक अस्थिरता, अकेलापन और गरीबी का कारण बन सकता है।',


        },


        'remedies_list': {


            'mangal_dosha': ['प्रतिदिन हनुमान चालीसा पाठ करें', 'मंगलवार को व्रत रखें', 'सेंदुर और मछली दाल दान करें', 'लाल रंग के कपड़े परिहार करें', "मंगल ग्रह का मंत्र जप करें: 'ओँ क्राँ क्रीं क्रौं सः भौमाय नमः'"],


            'kaal_sarp_dosha': ['नाग पंचमी को विशेष पूजा करें', 'शिवलिंग पर दूध अभिषेक करें', "राहु-केतु मंत्र जप करें: 'ओँ राँ राहवे नमः'", 'काल सर्प दोष निवारण पूजा करवाएं', 'सोमवार को उपवास रखें'],


            'pitra_dosha': ['पितृपक्ष में श्राद्ध करें', 'प्रतिदिन सूर्य को अर्घ्य दें', 'घायल वृक्ष की जड़ में जल अर्पण करें', 'गया में पिंडदान करें', 'पितरों की फोटो के सामने दीप प्रज्वलित करें'],


            'grahan_dosha': ['ग्रहण के समय मंत्र जप करें', 'दान-पुण्य करें', 'आदित्य हृदय स्तोत्र पाठ करें', 'चंद्र ग्रह मंत्र जप करें', 'ग्रहण के बाद स्नान कर शुद्ध रहें'],


            'nadi_dosha': ['नाड़ी दोष निवारण पूजा करवाएं', 'महामृत्युंजय मंत्र जप करें', 'शिव-पार्वती की उपासना करें', 'संतान के लिए विशेष अनुष्ठान करें'],


            'shani_dosha': ['शनिवार को हनुमान मंदिर दर्शन करें', 'तिल तेल का दीपक जलाएं', "शनि मंत्र जप करें: 'ओँ शं शनैश्चराय नमः'", 'काले कपड़े और तिल दान करें', 'शनि चालीसा पाठ करें'],


            'guru_chandal_dosha': ['बृहस्पतिवार को व्रत रखें', 'पीले रंग के कपड़े पहनें', "गुरु ग्रह का मंत्र जप करें: 'ओँ ग्राँ ग्रीं ग्रौं सः गुरवे नमः'", 'केले के पेड़ की पूजा करें', 'घायल वृक्ष पर जल अर्पण करें'],


            'kemadruma_dosha': ["चंद्र ग्रह का मंत्र जप करें: 'ओँ श्राँ श्रीं श्रौं सः चंद्राय नमः'", 'सोमवार को उपवास रखें', 'शिवलिंग पर दूध अभिषेक करें', 'मोती (मोती) धारण करें', 'सफेद कपड़े दान करें'],


        },


        'shani_phase_names': {


            'Rising': 'उदीयमान',


            'Peak': 'शीर्ष',


            'Setting': 'अस्तगामी',


            'Dhaiya': 'ढैया',


            'Not Running': 'साढ़ेसाती नहीं चल रही',


        },


    },


    'en': {


        'title': 'Planetary Dosha Analysis',


        'present_label': 'Present',


        'absent_label': 'Absent',


        'remedies_heading': 'Remedies',


        'no_remedies': 'No special remedies needed.',


        'severity_levels': {


            '0': 'None', '1': 'Mild', '2': 'Moderate', '3': 'Severe', '4': 'Very Severe'


        },


        'dosha_names': {


            'mangal_dosha': 'Mangal Dosha',


            'kaal_sarp_dosha': 'Kaal Sarp Dosha',


            'pitra_dosha': 'Pitra Dosha',


            'grahan_dosha': 'Grahan Dosha',


            'nadi_dosha': 'Nadi Dosha',


            'shani_dosha': 'Shani Dosha (Sade Sati)',


            'guru_chandal_dosha': 'Guru-Chandal Dosha',


            'kemadruma_dosha': 'Kemadruma Dosha',


        },


        'descriptions': {


            'mangal_dosha': 'Mangal Dosha occurs when Mars is in the 1st, 4th, 7th, 8th, or 12th house. It can cause problems in married life, conflicts, and delayed marriage.',


            'kaal_sarp_dosha': 'Kaal Sarp Dosha occurs when all planets are between Rahu and Ketu. It causes obstacles in life, fear, insomnia, and career conflicts.',


            'pitra_dosha': 'Pitra Dosha occurs when Sun is with Rahu or Saturn, or when Rahu-Ketu are in the 9th house. It causes childlessness, strained father-son relationships, and family discord.',


            'grahan_dosha': 'Grahan Dosha occurs when Sun or Moon is conjoined with Rahu-Ketu. It causes health issues, mental instability, and career uncertainty.',


            'nadi_dosha': 'Nadi Dosha is important for marriage. It occurs when the nakshatras of husband and wife are in the same nadi. It can cause childlessness, health problems, and marital conflicts.',


            'shani_dosha': 'Shani Dosha indicates the malefic influence of Saturn. Especially Sade Sati (7.5 years) is extremely painful. It causes financial crisis, health issues, and mental stress.',


            'guru_chandal_dosha': 'Guru-Chandal Dosha occurs when Jupiter is conjoined with Rahu or Ketu. It causes opposition to knowledge and ethics, religious disbelief, and obstacles in education.',


            'kemadruma_dosha': 'Kemadruma Dosha occurs when there are no planets on either side of Moon. It causes mental instability, feeling of loneliness, and poverty.',


        },


        'remedies_list': {


            'mangal_dosha': ['Read Hanuman Chalisa daily', 'Keep fast on Tuesdays', 'Donate red cloth and lentils', 'Avoid wearing red clothes', "Chant Mars mantra: 'Om Kram Krim Kraum Sah Bhaumaya Namah'"],


            'kaal_sarp_dosha': ['Perform special puja on Nag Panchami', 'Perform Abhishek with milk on Shivling', "Chant Rahu-Ketu mantra: 'Om Ram Rahube Namah'", 'Perform Kaal Sarp Dosha Nivaran puja', 'Keep fast on Mondays'],


            'pitra_dosha': ['Perform Shradh during Pitru Paksha', 'Offer Arghya to Sun daily', 'Offer water at the root of a wounded tree', 'Perform Pindadan at Gaya', "Light a lamp in front of ancestors' photos"],


            'grahan_dosha': ['Chant mantras during Grahan', 'Perform charity', 'Read Aditya Hridaya Stotram', 'Chant Moon mantra', 'Take bath and remain pure after Grahan'],


            'nadi_dosha': ['Perform Nadi Dosha Nivaran puja', 'Chant Mahamrityunjaya mantra', 'Worship Shiv-Parvati', 'Perform special rituals for children'],


            'shani_dosha': ['Visit Hanuman temple on Saturdays', 'Light a lamp with sesame oil', "Chant Saturn mantra: 'Om Sham Shanaischaraya Namah'", 'Donate black clothes and sesame', 'Read Shani Chalisa'],


            'guru_chandal_dosha': ['Keep fast on Thursdays', 'Wear yellow clothes', "Chant Jupiter mantra: 'Om Gram Grim Graum Sah Gurave Namah'", 'Worship banana tree', 'Offer water to a wounded tree'],


            'kemadruma_dosha': ["Chant Moon mantra: 'Om Shram Shrim Shraum Sah Chandraya Namah'", 'Keep fast on Mondays', 'Perform Abhishek with milk on Shivling', 'Wear pearl (motty)', 'Donate white clothes'],


        },


        'shani_phase_names': {


            'Rising': 'Rising',


            'Peak': 'Peak',


            'Setting': 'Setting',


            'Dhaiya': 'Dhaiya',


            'Not Running': 'Sade Sati not running',


        },


    },


}








def translate_dosha_result(results, lang='as'):


    """


    Translate dosha analysis results from Assamese to target language.


    Returns a new list with translated text fields.


    """


    if not results:


        return results





    L = DOSHA_LABELS.get(lang, DOSHA_LABELS['as'])


    severity_map = L.get('severity_levels', {})


    dosha_name_map = L.get('dosha_names', {})


    desc_map = L.get('descriptions', {})


    remedies_map = L.get('remedies_list', {})





    translated = []


    for dosha in results:


        d = dict(dosha)


        key = d.get('key', d.get('dosha', ''))


        


        if not key and 'info' in d:


            key = d['info'].get('key', d['info'].get('name', ''))





        if 'info' in d and d['info']:


            info = dict(d['info'])


            info['name'] = dosha_name_map.get(key, info.get('name', key))


            if desc_map.get(key):


                info['description'] = desc_map[key]


            if 'severity_text' in d:


                d['severity_text'] = severity_map.get(str(d['severity']), d['severity_text'])


            if remedies_map.get(key):


                info['remedies'] = remedies_map[key]


            d['info'] = info





        if key == 'shani_dosha' and 'phase' in d:


            shani_phases = L.get('shani_phase_names', {})


            d['phase'] = shani_phases.get(d['phase'], d['phase'])





        translated.append(d)





    return translated


def translate_yoga_result(results, lang='as'):
    """
    Translate yoga analysis results from Assamese to target language.
    Returns a new list with translated text fields (name, category, description, effect).
    """
    if not results:
        return results

    L = YOGA_LABELS.get(lang, YOGA_LABELS['as'])
    yoga_name_map = L.get('yoga_names', {})
    yoga_cat_map = L.get('yoga_categories', {})
    yoga_desc_map = L.get('yoga_descriptions', {})

    translated = []
    for yoga in results:
        y = dict(yoga)
        key = y.get('key', '')

        # Translate yoga name
        y['name'] = yoga_name_map.get(key, y.get('name', key))

        # Translate category
        if 'category' in y:
            y['category'] = yoga_cat_map.get(y['category'], y['category'])

        # Translate description and effect using localized descriptions
        localized = yoga_desc_map.get(key, {})
        if localized:
            if 'description' in y:
                y['description'] = localized.get('description', y['description'])
            if 'effect' in y:
                y['effect'] = localized.get('effect', y['effect'])

        translated.append(y)

    return translated