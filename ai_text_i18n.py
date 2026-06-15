"""Build a 4-language AI text generator module."""
# This will be a complete replacement for the language-dependent parts of ai_engine.py

# Multilingual text tables

# Greeting
GREETING = {
    'as': "প্ৰিয় {name},",
    'bn': "প্রিয় {name},",
    'hi': "प्रिय {name},",
    'en': "Dear {name},",
}

INTRO_BODY = {
    'as': "আপোনাৰ জন্মকুণ্ডলীৰ বৈদিক জ্যোতিষ শাস্ত্ৰৰ শুদ্ধ গণনাৰ আধাৰত এই AI বিশ্লেষণ প্ৰস্তুত কৰা হৈছে।",
    'bn': "আপনার জন্মকুণ্ডলীর বৈদিক জ্যোতিষ শাস্ত্রের শুদ্ধ গণনার ভিত্তিত এই AI বিশ্লেষণ তৈরি করা হয়েছে।",
    'hi': "आपकी जन्मकुंडली के वैदिक ज्योतिष शास्त्र की शुद्ध गणना के आधार पर यह AI विश्लेषण तैयार किया गया है।",
    'en': "This AI analysis has been prepared based on the precise calculations of Vedic astrology from your birth chart.",
}

# Section headers
SECTION_LAGNA = {
    'as': "**১। লগ্ন আৰু লগ্নফল:**",
    'bn': "**১। লগ্ন ও লগ্নফল:**",
    'hi': "**१। लग्न और लग्नफल:**",
    'en': "**1. Ascendant (Lagna) and Lagna Effects:**",
}

SECTION_PLANETS = {
    'as': "**২। গ্ৰহৰ বিশেষ অৱস্থান:**",
    'bn': "**২। গ্রহের বিশেষ অবস্থান:**",
    'hi': "**२। ग्रहों की विशेष स्थिति:**",
    'en': "**2. Special Positions of Planets:**",
}

SECTION_DOSHA_YOGA = {
    'as': "**৩। দোষ আৰু যোগ বিশ্লেষণ:**",
    'bn': "**৩। দোষ ও যোগ বিশ্লেষণ:**",
    'hi': "**३। दोष और योग विश्लेषण:**",
    'en': "**3. Dosha and Yoga Analysis:**",
}

SECTION_DASHA = {
    'as': "**৪। বৰ্তমান দশা বিশ্লেষণ:**",
    'bn': "**৪। বর্তমান দশা বিশ্লেষণ:**",
    'hi': "**४। वर्तमान दशा विश्लेषण:**",
    'en': "**4. Current Dasha Analysis:**",
}

SECTION_NAKSHATRA = {
    'as': "**৫। নক্ষত্ৰ আৰু ৰাশি:**",
    'bn': "**৫। নক্ষত্র ও রাশি:**",
    'hi': "**५। नक्षत्र और राशि:**",
    'en': "**5. Nakshatra and Rashi:**",
}

SECTION_EXTRAS = {
    'as': "**৬। অন্যান্য গুৰুত্বপূৰ্ণ বিশ্লেষণ:**",
    'bn': "**৬। অন্যান্য গুরুত্বপূর্ণ বিশ্লেষণ:**",
    'hi': "**६। अन्य महत्वपूर्ण विश्लेषण:**",
    'en': "**6. Other Important Analyses:**",
}

SECTION_GEMSTONE = {
    'as': "**৭। ৰত্ন পৰামৰ্শ, বীজ মন্ত্ৰ আৰু সাৰাংশ:**",
    'bn': "**৭। রত্ন পরামর্শ, বীজ মন্ত্র ও সারাংশ:**",
    'hi': "**७। रत्न परामर्श, बीज मंत्र और सारांश:**",
    'en': "**7. Gemstone Advice, Beej Mantras and Summary:**",
}

# Dosha/Yoga analysis
DOSHA_PRESENT = {
    'as': "উপস্থিত দোষ ({count}টা): {names}।",
    'bn': "উপস্থিত দোষ ({count}টি): {names}।",
    'hi': "वर्तमान दोष ({count}): {names}।",
    'en': "Present doshas ({count}): {names}.",
}

DOSHA_NONE = {
    'as': "কোনো গুৰুতৰ দোষ ধৰা পৰা নাই — ই এক শুভ লক্ষণ।",
    'bn': "কোনো গুরুতর দোষ পাওয়া যায়নি — এটি শুভ লক্ষণ।",
    'hi': "कोई गंभीर दोष नहीं पाया गया — यह एक शुभ संकेत है।",
    'en': "No serious dosha found — this is an auspicious sign.",
}

YOGA_PRESENT = {
    'as': "শুভ যোগ ({count}টা): {names}।",
    'bn': "শুভ যোগ ({count}টি): {names}।",
    'hi': "शुभ योग ({count}): {names}।",
    'en': "Auspicious yogas ({count}): {names}.",
}

# Nakshatra/Rashi
NAKSHATRA_LINE = {
    'as': "জন্ম নক্ষত্ৰ: {name}। এই নক্ষত্ৰৰ প্ৰভাৱত আপোনাৰ ব্যক্তিত্ব আৰু জীৱনশৈলী গঢ় লৈছে।",
    'bn': "জন্ম নক্ষত্র: {name}। এই নক্ষত্রের প্রভাবে আপনার ব্যক্তিত্ব ও জীবনশৈলী গড়ে উঠেছে।",
    'hi': "जन्म नक्षत्र: {name}। इस नक्षत्र के प्रभाव से आपका व्यक्तित्व और जीवनशैली निर्मित हुई है।",
    'en': "Birth Nakshatra: {name}. Your personality and lifestyle are shaped by the influence of this nakshatra.",
}

RASHI_LINE = {
    'as': "চন্দ্ৰ ৰাশি: {name}। চন্দ্ৰ ৰাশিৰ পৰা আপোনাৰ মন, আৱেগ, আৰু দৈনন্দিন জীৱনৰ ফলাফল নিৰ্ণয় কৰা হয়।",
    'bn': "চন্দ্র রাশি: {name}। চন্দ্র রাশি থেকে আপনার মন, আবেগ এবং দৈনন্দিন জীবনের ফলাফল নির্ধারিত হয়।",
    'hi': "चंद्र राशि: {name}। चंद्र राशि से आपके मन, भावनाओं और दैनंदिन जीवन के परिणाम निर्धारित होते हैं।",
    'en': "Moon Rashi: {name}. Your mind, emotions, and daily life outcomes are determined by the Moon sign.",
}

# Tripap/Navatara/Sannari
TRIPAP_AGES = {
    'as': "ত্ৰিপাপ ৰিষ্টৰ সম্ভাব্য বয়স: {ages} — এই বয়সসমূহত বিশেষ সাৱধানতা অৱলম্বন কৰক।",
    'bn': "ত্রিপাপ রিষ্টের সম্ভাব্য বয়স: {ages} — এই বয়সগুলোতে বিশেষ সতর্কতা অবলম্বন করুন।",
    'hi': "त्रिपाप रिष्ट की संभावित आयु: {ages} — इन आयु में विशेष सावधानी बरतें।",
    'en': "Possible Tripap Rista ages: {ages} — exercise special caution at these ages.",
}

NAVATARA_DESC = {
    'as': "নৱতাৰা চক্ৰ: জন্ম নক্ষত্ৰৰ পৰা ২৭ নক্ষত্ৰক ৯ ভাগত বিভক্ত কৰি জীৱনৰ শুভ-অশুভ সময় নিৰ্ণয় কৰা হয়।",
    'bn': "নবতারা চক্র: জন্ম নক্ষত্র থেকে ২৭ নক্ষত্রক ৯ ভাগে ভাগ করে জীবনের শুভ-অশুভ সময় নির্ধারণ করা হয়।",
    'hi': "नवतारा चक्र: जन्म नक्षत्र से 27 नक्षत्रों को 9 भागों में विभाजित कर जीवन के शुभ-अशुभ समय का निर्धारण किया जाता है।",
    'en': "Navatara Chakra: 27 nakshatras from the birth nakshatra are divided into 9 parts to determine auspicious and inauspicious times in life.",
}

SANNARI_DESC = {
    'as': "সন্নাড়ী চক্ৰ: জন্ম নক্ষত্ৰৰ আধাৰত দেহ, অৰ্থ, ভ্ৰাতৃ, মাতৃ, পুত্ৰ, শত্ৰু, দাৰা আদিৰ বিষয়ে সূচনা দিয়ে।",
    'bn': "সন্নাড়ী চক্র: জন্ম নক্ষত্রের ভিত্তিতে দেহ, অর্থ, ভ্রাতা, মাতা, পুত্র, শত্রু, দারা ইত্যাদি সম্পর্কে ইঙ্গিত দেয়।",
    'hi': "सन्नाड़ी चक्र: जन्म नक्षत्र के आधार पर देह, अर्थ, भ्राता, माता, पुत्र, शत्रु, दारा आदि के विषय में संकेत देता है।",
    'en': "Sannari Chakra: Based on the birth nakshatra, it indicates aspects related to body, wealth, siblings, mother, children, enemies, and spouse.",
}

# Gemstone titles (localized per language)
GEMSTONE_TITLE = {
    'as': "লগ্নপতি",
    'bn': "লগ্নপতি",
    'hi': "लग्नपति",
    'en': "Lagna Lord",
}
GEMSTONE_TITLE_5 = {
    'as': "পঞ্চমপতি",
    'bn': "পঞ্চমপতি",
    'hi': "पंचमपति",
    'en': "5th Lord",
}
GEMSTONE_TITLE_9 = {
    'as': "নৱমপতি",
    'bn': "নবমপতি",
    'hi': "नवमपति",
    'en': "9th Lord",
}
GEMSTONE_WORD = {
    'as': "ৰত্ন",
    'bn': "রত্ন",
    'hi': "रत्न",
    'en': "Gemstone",
}
MANTRA_WORD = {
    'as': "মন্ত্ৰ",
    'bn': "মন্ত্র",
    'hi': "मंत्र",
    'en': "Mantra",
}
GEMSTONE_NOTE = {
    'as': "ৰত্ন সদায় শুদ্ধ-প্ৰাকৃতিক হ'ব লাগে আৰু অভিজ্ঞ জ্যোতিষীৰ পৰামৰ্শ লৈহে ধাৰণ কৰিব। মন্ত্ৰ নিতৌ ১০৮ বাৰ জাপ কৰিলে গ্ৰহদোষ নাশ হয়।",
    'bn': "রত্ন সর্বদা শুদ্ধ-প্রাকৃতিক হতে হবে এবং অভিজ্ঞ জ্যোতিষীর পরামর্শ নিয়ে ধারণ করতে হবে। মন্ত্র প্রতিদিন ১০৮ বার জপ করলে গ্রহদোষ নাশ হয়।",
    'hi': "रत्न सदैव शुद्ध-प्राकृतिक होना चाहिए और अनुभवी ज्योतिषी की सलाह लेकर ही धारण करना चाहिए। मंत्र प्रतिदिन 108 बार जपने से ग्रहदोष नष्ट होता है।",
    'en': "Gemstones must always be natural and pure, and should only be worn after consulting an experienced astrologer. Chanting mantras 108 times daily removes planetary afflictions.",
}

# Summary
SUMMARY_GOOD = {
    'as': "আপোনাৰ কুণ্ডলী অত্যন্ত শুভ যোগসম্পন্ন। জীৱনত বহু ক্ষেত্ৰত সফলতা লাভ কৰাৰ সম্ভাৱনা আছে।",
    'bn': "আপনার কুণ্ডলী অত্যন্ত শুভ যোগসম্পন্ন। জীবনে বিভিন্ন ক্ষেত্রে সাফল্য অর্জনের সম্ভাবনা রয়েছে।",
    'hi': "आपकी कुंडली अत्यंत शुभ योगों से युक्त है। जीवन के कई क्षेत्रों में सफलता प्राप्ति की संभावना है।",
    'en': "Your chart is endowed with very auspicious yogas. You have the potential to achieve success in many areas of life.",
}
SUMMARY_OK = {
    'as': "আপোনাৰ কুণ্ডলীত শুভ যোগ আছে, যিয়ে জীৱনৰ বিভিন্ন ক্ষেত্ৰত সহায় কৰিব।",
    'bn': "আপনার কুণ্ডলীতে শুভ যোগ রয়েছে, যা জীবনের বিভিন্ন ক্ষেত্রে সাহায্য করবে।",
    'hi': "आपकी कुंडली में शुभ योग हैं, जो जीवन के विभिन्न क्षेत्रों में सहायक होंगे।",
    'en': "Your chart contains auspicious yogas, which will support you in various areas of life.",
}
SUMMARY_NONE = {
    'as': "আপোনাৰ কুণ্ডলীত বিশেষ যোগ নাথাকিলেও, পৰিশ্ৰম আৰু সততাৰ দ্বাৰা সফলতা লাভ কৰিব পাৰিব।",
    'bn': "আপনার কুণ্ডলীতে বিশেষ যোগ না থাকলেও, পরিশ্রম ও সততার মাধ্যমে সাফল্য অর্জন করতে পারবেন।",
    'hi': "आपकी कुंडली में विशेष योग न होने पर भी, परिश्रम और सत्यनिष्ठा से सफलता प्राप्त कर सकते हैं।",
    'en': "Even though your chart has no special yogas, you can achieve success through hard work and integrity.",
}
SUMMARY_DOSHA = {
    'as': "কেইবাটাও দোষ থকাৰ বাবে জীৱনত কিছু বাধাৰ সন্মুখীন হ'ব পাৰে। উপযুক্ত প্ৰতিকাৰ গ্ৰহণ কৰিলে এই বাধাসমূহ অতিক্ৰম কৰিব পাৰিব।",
    'bn': "কয়েকটি দোষ থাকার কারণে জীবনে কিছু বাধার সম্মুখীন হতে পারেন। উপযুক্ত প্রতিকার গ্রহণ করলে এই বাধাগুলো অতিক্রম করতে পারবেন।",
    'hi': "कई दोषों के कारण जीवन में कुछ बाधाएं आ सकती हैं। उचित उपाय करने से इन बाधाओं को पार किया जा सकता है।",
    'en': "Due to several doshas, you may face some obstacles in life. With proper remedies, these can be overcome.",
}
SUMMARY_NO_DOSHA = {
    'as': "কোনো গুৰুতৰ দোষ নথকাটো এক অতি শুভ লক্ষণ।",
    'bn': "কোনো গুরুতর দোষ না থাকা এক অতি শুভ লক্ষণ।",
    'hi': "कोई गंभीर दोष न होना एक अत्यंत शुभ संकेत है।",
    'en': "The absence of any serious dosha is a very auspicious sign.",
}
SUMMARY_HEADER = {
    'as': "**সাৰাংশ:**",
    'bn': "**সারাংশ:**",
    'hi': "**सारांश:**",
    'en': "**Summary:**",
}

# Dasha
DASHA_HEADER_MD = {
    'as': "**বৰ্তমান মহাদশা: {lord}**",
    'bn': "**বর্তমান মহাদশা: {lord}**",
    'hi': "**वर्तमान महादशा: {lord}**",
    'en': "**Current Mahadasha: {lord}**",
}
DASHA_HEADER_AD = {
    'as': "**বৰ্তমান অন্তৰ্দশা: {lord}**",
    'bn': "**বর্তমান অন্তর্দশা: {lord}**",
    'hi': "**वर्तमान अंतर्दशा: {lord}**",
    'en': "**Current Antardasha: {lord}**",
}
DASHA_PERIOD = {
    'as': "(সময়: {start} → {end})",
    'bn': "(সময়কাল: {start} → {end})",
    'hi': "(समय: {start} → {end})",
    'en': "(Period: {start} → {end})",
}
print('All translation tables loaded.')
print(f'Languages: {list(GREETING.keys())}')
