"""
ধ্ৰুৱতৰা AI - পত্ৰিকা (Patrika) জেনেৰেটৰ
Generates traditional astrological birth record (পত্ৰিকা) text in 4 languages:
- Assamese (as)
- Bengali (bn)
- Hindi (hi)
- English (en)
"""

from datetime import datetime

# ─── Month names (English → target language) ──────────────────
ENGLISH_MONTHS_ASM = [
    "জানুৱাৰী", "ফেব্ৰুৱাৰী", "মাৰ্চ", "এপ্ৰিল", "মে", "জুন",
    "জুলাই", "আগষ্ট", "ছেপ্টেম্বৰ", "অক্টোবৰ", "নৱেম্বৰ", "ডিচেম্বৰ"
]

ENGLISH_MONTHS_BN = [
    "জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন",
    "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"
]

ENGLISH_MONTHS_HI = [
    "जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून",
    "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"
]

ENGLISH_MONTHS_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

MONTHS = {
    "as": ENGLISH_MONTHS_ASM,
    "bn": ENGLISH_MONTHS_BN,
    "hi": ENGLISH_MONTHS_HI,
    "en": ENGLISH_MONTHS_EN,
}


# ─── Ashtottari dasha starting lord by nakshatra (English) ───
# Based on traditional Ashtottari system (অষ্টোত্তৰী দশা):
# Nakshatra groups and their starting Mahadasha lord:
#   Ashwini(0), Bharani(1)              → Venus
#   Krittika(2), Rohini(3), Mrigashira(4) → Sun
#   Ardra(5), Punarvasu(6), Pushya(7), Ashlesha(8) → Moon
#   Magha(9), Purva Phalguni(10), Uttara Phalguni(11) → Mars
#   Hasta(12), Chitra(13), Swati(14), Vishakha(15) → Mercury
#   Anuradha(16), Jyeshtha(17), Mula(18) → Saturn
#   Purva Ashadha(19), Uttara Ashadha(20), Shravana(21) → Jupiter
#   Dhanishtha(22), Shatabhisha(23), Purva Bhadrapada(24) → Rahu
#   Uttara Bhadrapada(25), Revati(26) → Venus
ASHTOTTARI_START_EN = [
    "Venus", "Venus",                                    # 0-1: Ashwini, Bharani
    "Sun", "Sun", "Sun",                                 # 2-4: Krittika, Rohini, Mrigashira
    "Moon", "Moon", "Moon", "Moon",                      # 5-8: Ardra, Punarvasu, Pushya, Ashlesha
    "Mars", "Mars", "Mars",                              # 9-11: Magha, Purva Phalguni, Uttara Phalguni
    "Mercury", "Mercury", "Mercury", "Mercury",          # 12-15: Hasta, Chitra, Swati, Vishakha
    "Saturn", "Saturn", "Saturn",                        # 16-18: Anuradha, Jyeshtha, Mula
    "Jupiter", "Jupiter", "Jupiter",                     # 19-21: Purva Ashadha, Uttara Ashadha, Shravana
    "Rahu", "Rahu", "Rahu",                              # 22-24: Dhanishtha, Shatabhisha, Purva Bhadrapada
    "Venus", "Venus",                                    # 25-26: Uttara Bhadrapada, Revati
]

# ─── Yoni/Animal names by nakshatra (in all 4 languages) ──────
NAKSHATRA_YONI_EN = [
    "Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog", "Cat", "Sheep",
    "Cat", "Rat", "Rat", "Cow", "Buffalo", "Tiger", "Buffalo",
    "Tiger", "Deer", "Deer", "Dog", "Monkey", "Elephant", "Horse",
    "Lion", "Horse", "Lion", "Cow", "Elephant"
]

NAKSHATRA_YONI_AS = [
    "অশ্ব", "গজ", "মেষ", "সৰ্প", "সৰ্প", "শ্বান", "মাৰ্জাৰ", "মেষ",
    "মাৰ্জাৰ", "মূষিক", "মূষিক", "গো", "মহিষ", "ব্যাঘ্ৰ", "মহিষ",
    "ব্যাঘ্ৰ", "হৰিণ", "হৰিণ", "শ্বান", "বানৰ", "গজ", "অশ্ব",
    "সিংহ", "অশ্ব", "সিংহ", "গো", "গজ"
]

NAKSHATRA_YONI_BN = [
    "অশ্ব", "গজ", "মেষ", "সর্প", "সর্প", "শ্বান", "মার্জার", "মেষ",
    "মার্জার", "মূষিক", "মূষিক", "গো", "মহিষ", "ব্যাঘ্র", "মহিষ",
    "ব্যাঘ্র", "হরিণ", "হরিণ", "শ্বান", "বানর", "গজ", "অশ্ব",
    "সিংহ", "অশ্ব", "সিংহ", "গো", "গজ"
]

NAKSHATRA_YONI_HI = [
    "अश्व", "गज", "मेष", "सर्प", "सर्प", "श्वान", "मार्जार", "मेष",
    "मार्जार", "मूषक", "मूषक", "गो", "महिष", "व्याघ्र", "महिष",
    "व्याघ्र", "हरिण", "हरिण", "श्वान", "बानर", "गज", "अश्व",
    "सिंह", "अश्व", "सिंह", "गो", "गज"
]

NAKSHATRA_YONI = {
    "as": NAKSHATRA_YONI_AS,
    "bn": NAKSHATRA_YONI_BN,
    "hi": NAKSHATRA_YONI_HI,
    "en": NAKSHATRA_YONI_EN,
}


# ─── Rashi lords (in all 4 languages) ────────────────────────
RASHI_LORDS_LIST_EN = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
]

RASHI_LORDS_LIST_AS = [
    "মংগল", "শুক্ৰ", "বুধ", "চন্দ্ৰ", "ৰবি", "বুধ",
    "শুক্ৰ", "মংগল", "বৃহস্পতি", "শনি", "শনি", "বৃহস্পতি"
]

RASHI_LORDS_LIST_BN = [
    "মঙ্গল", "শুক্র", "বুধ", "চন্দ্র", "রবি", "বুধ",
    "শুক্র", "মঙ্গল", "বৃহস্পতি", "শনি", "শনি", "বৃহস্পতি"
]

RASHI_LORDS_LIST_HI = [
    "मंगल", "शुक्र", "बुध", "चंद्र", "सूर्य", "बुध",
    "शुक्र", "मंगल", "बृहस्पति", "शनि", "शनि", "बृहस्पति"
]

RASHI_LORDS = {
    "as": RASHI_LORDS_LIST_AS,
    "bn": RASHI_LORDS_LIST_BN,
    "hi": RASHI_LORDS_LIST_HI,
    "en": RASHI_LORDS_LIST_EN,
}


# ─── Nakshatra lords (in all 4 languages) ────────────────────
NAKSHATRA_LORDS_EN = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn",
    "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter",
    "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury"
]

NAKSHATRA_LORDS_AS = [
    "কেতু", "শুক্ৰ", "ৰবি", "চন্দ্ৰ", "মংগল", "ৰাহু", "বৃহস্পতি", "শনি",
    "বুধ", "কেতু", "শুক্ৰ", "ৰবি", "চন্দ্ৰ", "মংগল", "ৰাহু", "বৃহস্পতি",
    "শনি", "বুধ", "কেতু", "শুক্ৰ", "ৰবি", "চন্দ্ৰ", "মংগল", "ৰাহু",
    "বৃহস্পতি", "শনি", "বুধ"
]

NAKSHATRA_LORDS_BN = [
    "কেতু", "শুক্র", "রবি", "চন্দ্র", "মঙ্গল", "রাহু", "বৃহস্পতি", "শনি",
    "বুধ", "কেতু", "শুক্র", "রবি", "চন্দ্র", "মঙ্গল", "রাহু", "বৃহস্পতি",
    "শনি", "বুধ", "কেতু", "শুক্র", "রবি", "চন্দ্র", "মঙ্গল", "রাহু",
    "বৃহস্পতি", "শনি", "বুধ"
]

NAKSHATRA_LORDS_HI = [
    "केतु", "शुक्र", "सूर्य", "चंद्र", "मंगल", "राहु", "बृहस्पति", "शनि",
    "बुध", "केतु", "शुक्र", "सूर्य", "चंद्र", "मंगल", "राहु", "बृहस्पति",
    "शनि", "बुध", "केतु", "शुक्र", "सूर्य", "चंद्र", "मंगल", "राहु",
    "बृहस्पति", "शनि", "बुध"
]

NAKSHATRA_LORDS = {
    "as": NAKSHATRA_LORDS_AS,
    "bn": NAKSHATRA_LORDS_BN,
    "hi": NAKSHATRA_LORDS_HI,
    "en": NAKSHATRA_LORDS_EN,
}


# ─── Pada names (in all 4 languages) ────────────────────────
PADA_NAMES_AS = ["প্ৰথম", "দ্বিতীয়", "তৃতীয়", "চতুৰ্থ"]
PADA_NAMES_BN = ["প্রথম", "দ্বিতীয়", "তৃতীয়", "চতুর্থ"]
PADA_NAMES_HI = ["प्रथম", "द्वितीय", "तृতীয়", "चतुर्थ"]
PADA_NAMES_EN = ["First", "Second", "Third", "Fourth"]

PADA_NAMES = {
    "as": PADA_NAMES_AS,
    "bn": PADA_NAMES_BN,
    "hi": PADA_NAMES_HI,
    "en": PADA_NAMES_EN,
}


def calculate_shaka_year(gregorian_year: int) -> int:
    """Shaka Samvat = Gregorian year - 78 (approximate)"""
    return gregorian_year - 78


def calculate_bhaskara_year(gregorian_year: int) -> int:
    """Bhaskarabda = Gregorian year - 593 (Assamese calendar)"""
    return gregorian_year - 593


def _translate_planet(eng_name: str, lang: str) -> str:
    """Translate English planet name to the target language."""
    mapping = {
        "as": {"Sun": "ৰবি", "Moon": "চন্দ্ৰ", "Mars": "মংগল", "Mercury": "বুধ",
               "Jupiter": "বৃহস্পতি", "Venus": "শুক্ৰ", "Saturn": "শনি",
               "Rahu": "ৰাহু", "Ketu": "কেতু"},
        "bn": {"Sun": "রবি", "Moon": "চন্দ্র", "Mars": "মঙ্গল", "Mercury": "বুধ",
               "Jupiter": "বৃহস্পতি", "Venus": "শুক্র", "Saturn": "শনি",
               "Rahu": "রাহু", "Ketu": "কেতু"},
        "hi": {"Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध",
               "Jupiter": "बृहस्पति", "Venus": "शुक्र", "Saturn": "शनि",
               "Rahu": "राहु", "Ketu": "केतु"},
        "en": {"Sun": "Sun", "Moon": "Moon", "Mars": "Mars", "Mercury": "Mercury",
               "Jupiter": "Jupiter", "Venus": "Venus", "Saturn": "Saturn",
               "Rahu": "Rahu", "Ketu": "Ketu"},
    }
    return mapping.get(lang, mapping["en"]).get(eng_name, eng_name)


def get_hora_lord(rasi_index: int, degree: float, lang: str = "as") -> str:
    """
    Get Hora (D2) lord based on rasi and degree.
    Returns the localized name.
    """
    is_odd_rasi = (rasi_index % 2 == 0)
    first_half = (degree < 15.0)
    lord_en = "Sun" if (is_odd_rasi == first_half) else "Moon"
    return _translate_planet(lord_en, lang)


def get_drekkana_lord(rasi_index: int, degree: float, lang: str = "as") -> str:
    """
    Get Drekkana (D3) lord based on rasi and degree.
    Returns the localized name.
    """
    drek_index = int(degree / 10.0)  # 0, 1, or 2
    drekkana_rasi = (rasi_index + drek_index * 4) % 12
    return RASHI_LORDS.get(lang, RASHI_LORDS_LIST_EN)[drekkana_rasi]


def get_navamsa_lord(rasi_index: int, degree: float, lang: str = "as") -> str:
    """
    Get Navamsa (D9) lord based on rasi and degree.
    Returns the localized name.
    """
    nav_index = int(degree / 3.333333)  # 0-8

    # Determine starting rashi for navamsa based on element
    element = rasi_index % 4
    if element == 0:   # Fiery
        start_rasi = 0  # Aries
    elif element == 1: # Earthy
        start_rasi = 9  # Capricorn
    elif element == 2: # Airy
        start_rasi = 6  # Libra
    else:              # Watery
        start_rasi = 3  # Cancer

    navamsa_rasi = (start_rasi + nav_index) % 12
    return RASHI_LORDS.get(lang, RASHI_LORDS_LIST_EN)[navamsa_rasi]


def get_ashtottari_lord(nakshatra_index: int, lang: str = "as") -> str:
    """Get Ashtottari dasha starting lord from nakshatra."""
    eng_name = ASHTOTTARI_START_EN[nakshatra_index % 27]
    return _translate_planet(eng_name, lang)


def get_vimshottari_lord(nakshatra_index: int, lang: str = "as") -> str:
    """Get Vimshottari dasha starting lord from nakshatra."""
    eng_name = NAKSHATRA_LORDS_EN[nakshatra_index % 27]
    return _translate_planet(eng_name, lang)


# ─── Patrika text templates by language ──────────────────────
PATRIKA_TEMPLATES = {
    "as": {
        "child_male": "কুমাৰ",
        "child_female": "কুমাৰী",
        "blessing_male": "বালক সু-কীৰ্তিশালী",
        "blessing_female": "বালিকা সু-কীৰ্তিশালিনী",
        "prefix_male": "শ্ৰীমান",
        "prefix_female": "শ্ৰীমতী",
        "pronoun_male": "তেওঁৰ",
        "pronoun_female": "তাইৰ",
        "pronoun_obj_male": "তেওঁ",
        "pronoun_obj_female": "তাই",
        "text": "শুভমস্তু শকাব্দদয় {shaka_year}, ভাস্কৰাব্দ {bhaskara_year}, ইংৰাজী {day} {month_name} {gregorian_year} চন, জন্ম দিবাঃ {tob} মি: সময় | জন্মৰ স্থান: {birth_district} | সৌৰ {masa_name} মাহৰ {vaar_name}ে, অয়নাংশ পৰিশোধিত {asc_rasi} লগ্নত, {lagna_lord} লগ্নাধিপতি, {moon_rasi} ৰাশি, {rashi_lord} ৰাশ্যাধিপতি, {nakshatra_name} নক্ষত্ৰৰ, {pada_name} ভোগ্য চৰনত, নক্ষত্ৰাধিপতি {nakshatra_lord}, অ.সিতপক্ষীয় {paksha}ৰ {tithi_name} তিথিত, {yoga_name} যোগত, {gana}গণ, {varna} বৰ্ণ, {karana_name} কৰণ, {hora_lord}ৰ হোৰাত, {drekkana_lord}ৰ দ্ৰেক্কানত, {navamsa_lord}ৰ নবাংশত, {yoni}ৰ অস্থিত, অষ্টোত্তৰী মতে {ashtottari_lord} আৰু বিংশোত্তৰী {vimshottari_lord}ৰ মহাদশাত তথা নানা শুভা-শুভ যোগত {residence_district} জিলান্তৰ্গত {residence} নিবাসী পৰম ধাৰ্মিক শ্ৰীযুক্ত {father_name} মহোদয়ৰ ঘৰত ধৰ্মপত্নী শ্ৰীযুক্তা {mother_name}ৰ উদৰত শুভ {child_word} জন্ম হয়|\n\n{pronoun} লোক প্ৰকাশিত নাম -> {prefix} {public_name}\nগুপ্ত নাম -> {prefix} {secret_name}\n\nদেৱ দ্বিজৰ আশীৰ্বাদত আদিত্যাদি নৱগ্ৰহৰ প্ৰসাদাৎ\n{blessing} | দীৰ্ঘজীৱি হওঁক ||"
    },
    "bn": {
        "child_male": "কুমার",
        "child_female": "কুমারী",
        "blessing_male": "বালক সু-কীর্তিশালী",
        "blessing_female": "বালিকা সু-কীর্তিশালিনী",
        "prefix_male": "শ্রীমান",
        "prefix_female": "শ্রীমতী",
        "pronoun_male": "তাঁর",
        "pronoun_female": "তাঁর",
        "pronoun_obj_male": "তিনি",
        "pronoun_obj_female": "তিনি",
        "text": "শুভমস্তু শকাব্দায় {shaka_year}, ভাস্করাব্দ {bhaskara_year}, ইংরেজি {day} {month_name} {gregorian_year} সাল, জন্ম দিবাঃ {tob} মি: সময় | জন্মস্থান: {birth_district} | সৌর {masa_name} মাসের {vaar_name} বারে, অয়নাংশ পরিশোধিত {asc_rasi} লগ্নে, {lagna_lord} লগ্নাধিপতি, {moon_rasi} রাশি, {rashi_lord} রাশ্যধিপতি, {nakshatra_name} নক্ষত্রের, {pada_name} ভোগ্য চরণে, নক্ষত্রাধিপতি {nakshatra_lord}, অ.সিতপক্ষীয় {paksha}-র {tithi_name} তিথিতে, {yoga_name} যোগে, {gana} গণ, {varna} বর্ণ, {karana_name} করণ, {hora_lord}-এর হোরায়, {drekkana_lord}-এর দ্রেক্কানে, {navamsa_lord}-এর নবাংশে, {yoni}-তে অবস্থিত, অষ্টোত্তরী মতে {ashtottari_lord} এবং বিংশোত্তরী {vimshottari_lord}-এর মহাদশায় তথা নানা শুভাশুভ যোগে {residence_district} জিলান্তর্গত {residence} নিবাসী পরম ধার্মিক শ্রীযুক্ত {father_name} মহোদয়ের গৃহে ধর্মপত্নী শ্রীযুক্তা {mother_name}-এর উদরে শুভ {child_word} জন্ম হয়|\n\n{pronoun} লোক প্রকাশিত নাম -> {prefix} {public_name}\nগুপ্ত নাম -> {prefix} {secret_name}\n\nদেব দ্বিজের আশীর্বাদে আদিত্যাদি নবগ্রহের প্রসাদে\n{blessing} | দীর্ঘজীবী হোক ||"
    },
    "hi": {
        "child_male": "कुमार",
        "child_female": "कुमारी",
        "blessing_male": "बालक सु-कीर्तिशाली",
        "blessing_female": "बालिका सु-कीर्तिशालिनी",
        "prefix_male": "श्रीमान",
        "prefix_female": "श्रीमती",
        "pronoun_male": "उनका",
        "pronoun_female": "उनका",
        "pronoun_obj_male": "वे",
        "pronoun_obj_female": "वे",
        "text": "शुभमस्तु शकाब्द {shaka_year}, भास्कराब्द {bhaskara_year}, अंग्रेजी {day} {month_name} {gregorian_year} साल, जन्म समय: {tob} मि: | जन्म स्थान: {birth_district} | सौर {masa_name} मास के {vaar_name} को, अयनांश परिशोधित {asc_rasi} लग्न में, {lagna_lord} लग्नाधिपति, {moon_rasi} राशि, {rashi_lord} राश्याधिपति, {nakshatra_name} नक्षत्र के, {pada_name} भोग्य चरण में, नक्षत्राधिपति {nakshatra_lord}, अ./सितपक्षीय {paksha} की {tithi_name} तिथि में, {yoga_name} योग में, {gana} गण, {varna} वर्ण, {karana_name} करण, {hora_lord} की होरा में, {drekkana_lord} के द्रेष्काण में, {navamsa_lord} के नवांश में, {yoni} योनि में स्थित, अष्टोत्तरी मतानुसार {ashtottari_lord} और विंशोत्तरी {vimshottari_lord} की महादशा में तथा नाना शुभाशुभ योगों में {residence_district} जिलान्तर्गत {residence} निवासी परम धार्मिक श्रीयुक्त {father_name} महोदय के गृह में धर्मपत्नी श्रीमती {mother_name} के उदर से शुभ {child_word} का जन्म हुआ।\n\n{pronoun} लोक प्रकाशित नाम -> {prefix} {public_name}\nगुप्त नाम -> {prefix} {secret_name}\n\nदेव और द्विज के आशीर्वाद से, आदित्यादि नवग्रहों के प्रसाद से\n{blessing} | दीर्घजीवी हों ||"
    },
    "en": {
        "child_male": "baby boy",
        "child_female": "baby girl",
        "blessing_male": "May the boy be highly glorious and renowned",
        "blessing_female": "May the girl be highly glorious and renowned",
        "prefix_male": "Master",
        "prefix_female": "Miss",
        "pronoun_male": "Their",
        "pronoun_female": "Their",
        "pronoun_obj_male": "they",
        "pronoun_obj_female": "they",
        "text": "May it be auspicious (Shubhamastu). In the Shaka year {shaka_year}, Bhaskara year {bhaskara_year}, corresponding to the Gregorian date {day} {month_name} {gregorian_year}, time of birth: {tob} | Place of birth: {birth_district} | On {vaar_name} of the solar {masa_name} month, in the Ayanamsa-corrected {asc_rasi} Ascendant (Lagna) with {lagna_lord} as the Ascendant lord; in the {moon_rasi} Moon sign (Rashi) with {rashi_lord} as the sign lord; under the {nakshatra_name} Nakshatra, {pada_name} Pada (quarter), with {nakshatra_lord} as the Nakshatra lord; during the {paksha} phase, {tithi_name} Tithi, {yoga_name} Yoga, {gana} Gana, {varna} Varna, and {karana_name} Karana; in the Hora of {hora_lord}, Drekkana of {drekkana_lord}, Navamsa of {navamsa_lord}, and classified under {yoni} Yoni; under the planetary ruling period (Mahadasha) of {ashtottari_lord} as per the Ashtottari system and {vimshottari_lord} as per the Vimshottari system, and amidst various auspicious and inauspicious planetary alignments—an auspicious {child_word} was born to the highly virtuous Mr. {father_name} and his legally wedded wife Mrs. {mother_name}, residing at {residence} in the {residence_district} district.\n\n{pronoun} publicly known name -> {prefix} {public_name}\nSecret/Astrological name -> {prefix} {secret_name}\n\nBy the blessings of the Deities and the Learned (Dwijas), and by the grace of the Sun and the Nine Planets (Navagrahas):\n{blessing} | May {pronoun_obj} be blessed with a long life ||"
    },
}


def generate_patrika_text(
    # Form data
    public_name: str,
    secret_name: str,
    father_name: str,
    mother_name: str,
    birth_district: str,
    residence_district: str,
    residence: str,
    gender: str,  # "male" or "female"
    # Astrological data
    dob: str,  # "YYYY-MM-DD"
    tob: str,  # "HH:MM"
    asc_rasi: str,
    asc_rasi_idx: int,
    asc_degree: float,
    moon_rasi: str,
    moon_rasi_idx: int,
    nakshatra_name: str,
    nakshatra_idx: int,
    nakshatra_pada: int,
    panchanga: dict,
    vimshottari_lord: str = "",
    ashtottari_lord: str = "",
    lang: str = "as",  # Language code: 'as', 'bn', 'hi', 'en'
) -> str:
    """
    Generate the traditional Patrika text in the specified language.
    Returns formatted text in the target language.

    Supported languages:
    - 'as': Assamese
    - 'bn': Bengali
    - 'hi': Hindi
    - 'en': English
    """
    # Validate language - default to Assamese if invalid
    if lang not in PATRIKA_TEMPLATES:
        lang = "as"

    template = PATRIKA_TEMPLATES[lang]

    # Parse date
    dt = datetime.strptime(dob, "%Y-%m-%d")
    gregorian_year = dt.year
    day = dt.day
    month_name = MONTHS.get(lang, ENGLISH_MONTHS_ASM)[dt.month - 1]

    # Calculate years
    shaka_year = calculate_shaka_year(gregorian_year)
    bhaskara_year = calculate_bhaskara_year(gregorian_year)

    # Get panchanga data
    tithi = panchanga.get('tithi', {})
    paksha = panchanga.get('paksha', '')
    nakshatra = panchanga.get('nakshatra', {})
    yoga = panchanga.get('yoga', {})
    karana = panchanga.get('karana', {})
    vaar = panchanga.get('vaar', {})
    masa = panchanga.get('masa', {})
    varna = panchanga.get('varna', '')
    gana = panchanga.get('gana', '')
    sunrise = panchanga.get('sunrise', '06:00')

    # Parse sunrise
    try:
        sr_parts = sunrise.split(":")
        sunrise_hour = int(sr_parts[0]) + int(sr_parts[1]) / 60.0
    except Exception:
        sunrise_hour = 6.0

    # Calculate derived values (localized)
    hora_lord = get_hora_lord(asc_rasi_idx, asc_degree, lang)
    drekkana_lord = get_drekkana_lord(asc_rasi_idx, asc_degree, lang)
    navamsa_lord = get_navamsa_lord(asc_rasi_idx, asc_degree, lang)

    if not vimshottari_lord:
        vimshottari_lord = get_vimshottari_lord(nakshatra_idx, lang)
    if not ashtottari_lord:
        ashtottari_lord = get_ashtottari_lord(nakshatra_idx, lang)

    # Lagna lord and rashi lord (localized)
    rashi_lords = RASHI_LORDS.get(lang, RASHI_LORDS_LIST_EN)
    lagna_lord = rashi_lords[asc_rasi_idx]
    rashi_lord = rashi_lords[moon_rasi_idx]

    # Nakshatra lord (localized)
    nakshatra_lords = NAKSHATRA_LORDS.get(lang, NAKSHATRA_LORDS_EN)
    nakshatra_lord = nakshatra_lords[nakshatra_idx]

    # Yoni (localized)
    yoni = NAKSHATRA_YONI.get(lang, NAKSHATRA_YONI_EN)[nakshatra_idx]

    # Pada name (localized)
    pada_name = PADA_NAMES.get(lang, PADA_NAMES_AS)[nakshatra_pada - 1] if 1 <= nakshatra_pada <= 4 else ""

    # Gender text (localized)
    if gender == "female":
        child_word = template["child_female"]
        blessing = template["blessing_female"]
        prefix = template["prefix_female"]
        pronoun = template.get("pronoun_female", "")
        pronoun_obj = template.get("pronoun_obj_female", "")
    else:
        child_word = template["child_male"]
        blessing = template["blessing_male"]
        prefix = template["prefix_male"]
        pronoun = template.get("pronoun_male", "")
        pronoun_obj = template.get("pronoun_obj_male", "")

    # Build the patrika text using the template
    text = template["text"].format(
        shaka_year=shaka_year,
        bhaskara_year=bhaskara_year,
        gregorian_year=gregorian_year,
        day=day,
        month_name=month_name,
        tob=tob,
        birth_district=birth_district,
        masa_name=masa.get('name', '—'),
        vaar_name=vaar.get('name', '—'),
        asc_rasi=asc_rasi,
        lagna_lord=lagna_lord,
        moon_rasi=moon_rasi,
        rashi_lord=rashi_lord,
        nakshatra_name=nakshatra_name,
        pada_name=pada_name,
        nakshatra_lord=nakshatra_lord,
        paksha=paksha,
        tithi_name=tithi.get('name', '—'),
        yoga_name=yoga.get('name', '—'),
        gana=gana,
        varna=varna,
        karana_name=karana.get('name', '—'),
        hora_lord=hora_lord,
        drekkana_lord=drekkana_lord,
        navamsa_lord=navamsa_lord,
        yoni=yoni,
        ashtottari_lord=ashtottari_lord,
        vimshottari_lord=vimshottari_lord,
        residence_district=residence_district,
        residence=residence,
        father_name=father_name,
        mother_name=mother_name,
        child_word=child_word,
        prefix=prefix,
        public_name=public_name,
        secret_name=secret_name,
        blessing=blessing,
        pronoun=pronoun,
        pronoun_obj=pronoun_obj,
    )

    return text
