"""
ধ্ৰুৱতৰা AI - দশা ফলাফল ইঞ্জিন (Dasha Prediction Engine)
============================================================
বিংশোত্তৰী দশা পদ্ধতিৰ সম্পূৰ্ণ গতিশীল (Dynamic) ফলাফল:
- জন্ম কুণ্ডলীৰ প্ৰকৃত গ্ৰহ অৱস্থানৰ ওপৰত ভিত্তি কৰি ফলাফল
- গ্ৰহৰ ঘৰ, বল (উচ্চ/নীচ/স্বগৃ্হী/মিত্ৰ/শত্ৰু), কাৰকত্ব, নক্ষত্ৰ বিশ্লেষণ
- Point 1 আৰু Point 2 ৰ গভীৰ বিশ্লেষণ
- তীক্ষ্ন নক্ষত্ৰ (আৰ্দ্ৰা, অশ্লেষা, মূল, জ্যেষ্ঠা) বিশেষ সতৰ্কবাণী
- জ্যোতিষশাস্ত্ৰৰ বিশেষ নিয়ম (Special Rules)
- প্ৰত্যন্তৰ দশাৰ বিশেষ বিশ্লেষণ (বয়স, ৩য়/৬ষ্ঠ/১২শ পতি, তীক্ষ্ণ নক্ষত্ৰ)
"""

# ═══════════════════════════════════════════════════════════════
# ধ্ৰুৱক (Constants)
# ═══════════════════════════════════════════════════════════════

# Import Graha Bichar for antardasha integration
try:
    from graha_bichar import get_graha_bichar, GRAHA_KARAKATTWA, BHAVA_NAMES
except ImportError:
    get_graha_bichar = None
    GRAHA_KARAKATTWA = {}
    BHAVA_NAMES = []

DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

TIKSHNA_NAKSHATRAS = ["Ardra", "Ashlesha", "Mula", "Jyeshtha"]

RASI_NAMES = ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"]
SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

# গ্ৰহৰ মিত্ৰতা/শত্ৰুতা (স্থায়ী সম্বন্ধ - Naisargika Maitri)
PLANET_FRIENDS = {
    "Sun":     {"friend": ["Moon", "Mars", "Jupiter"], "enemy": ["Saturn", "Venus"], "neutral": ["Mercury"]},
    "Moon":    {"friend": ["Sun", "Mercury"], "enemy": [], "neutral": ["Mars", "Jupiter", "Venus", "Saturn"]},
    "Mars":    {"friend": ["Sun", "Moon", "Jupiter"], "enemy": ["Mercury"], "neutral": ["Venus", "Saturn"]},
    "Mercury": {"friend": ["Sun", "Venus"], "enemy": ["Moon"], "neutral": ["Mars", "Jupiter", "Saturn"]},
    "Jupiter": {"friend": ["Sun", "Moon", "Mars"], "enemy": ["Mercury", "Venus"], "neutral": ["Saturn"]},
    "Venus":   {"friend": ["Mercury", "Saturn"], "enemy": ["Sun", "Moon"], "neutral": ["Mars", "Jupiter"]},
    "Saturn":  {"friend": ["Mercury", "Venus"], "enemy": ["Sun", "Moon", "Mars"], "neutral": ["Jupiter"]},
    "Rahu":    {"friend": ["Venus", "Saturn", "Mercury"], "enemy": ["Sun", "Moon", "Mars"], "neutral": ["Jupiter"]},
    "Ketu":    {"friend": ["Venus", "Saturn", "Mercury"], "enemy": ["Sun", "Moon", "Mars"], "neutral": ["Jupiter"]},
}

# গ্ৰহৰ কাৰকত্ব
KARAKATWA = {
    "Sun":     "পিতৃ, চৰকাৰ, আত্মা, স্বাস্থ্য, নেতৃত্ব, ৰাজকীয় সন্মান",
    "Moon":    "মাতৃ, মন, আৱেগ, শান্তি, জনসাধাৰণ, জল, দুগ্ধ",
    "Mars":    "ভাতৃ, সাহস, ভূমি, স্থাৱৰ সম্পত্তি, শক্তি, ক্ৰীড়া, দুৰ্ঘটনা",
    "Mercury": "বুদ্ধি, ব্যৱসায়, বাক্ শক্তি, লেখা-মেলা, গণনা, যোগাযোগ, স্নায়ু",
    "Jupiter": "সন্তান, গুৰু, পিতৃ, শিক্ষা, ধন, ধৰ্ম, জ্ঞান, স্বামী (মহিলাৰ), ভাগ্য",
    "Venus":   "পত্নী, বিবাহ, বিলাসিতা, কলা, সংগীত, সৌন্দৰ্য্য, বাহন, প্ৰেম",
    "Saturn":  "কৰ্ম, আয়ুস, দুখ-কষ্ট, দীৰ্ঘম্যাদী পৰিকল্পনা, চাকৰ, ৰোগ",
    "Rahu":    "হঠাতে ঘটা ঘটনা, বিভ্ৰান্তি, বিদেশ, উচ্চাকাংক্ষা, মায়া, অপৰম্পৰাগত চিন্তা",
    "Ketu":    "আধ্যাত্মিকতা, বিচ্ছেদ, মোক্ষ, গৱেষণা, পূৰ্বজন্মৰ কৰ্মফল, একাকীত্ব",
}

# ঘৰৰ নাম (সৰল অসমীয়াত)
HOUSE_NAMES = {
    1: "লগ্ন (শৰীৰ, আত্মা, উন্নতি, স্বাস্থ্য)",
    2: "২য় (ধন, বানী, কুটুম্ব, সঞ্চয়, মুখ)",
    3: "৩য় (পৰাক্ৰম, ভাতৃ, চুটি যাত্ৰা, যোগাযোগ)",
    4: "৪ৰ্থ (সুখ, মাতৃ, ঘৰ, বাহন, বিদ্যা)",
    5: "৫ম (বিদ্যা, সন্তান, প্ৰেম, বুদ্ধি, পূৰ্বপুণ্য)",
    6: "৬ষ্ঠ (ৰোগ, শত্ৰু, ঋণ, প্ৰতিযোগিতা, সেৱা, চাকৰী)",
    7: "৭ম (দাম্পত্য, ব্যৱসায়িক অংশীদাৰ, জনসাধাৰণ)",
    8: "৮ম (আয়ুস, বাধা, গোপন কথা, দুৰ্ঘটনা, গৱেষণা)",
    9: "৯ম (ভাগ্য, পিতৃ, ধৰ্ম, উচ্চ শিক্ষা, বিদেশ যাত্ৰা)",
    10: "১০ম (কৰ্ম, সন্মান, প্ৰশাসন, পিতৃৰ সুখ)",
    11: "১১শ (লাভ, ইচ্ছাপূৰণ, ডাঙৰ ভাতৃ, বন্ধু)",
    12: "১২শ (ব্যয়, বিদেশ, মোক্ষ, চিকিৎসালয়, গুপ্ত শত্ৰু, বিবাদ)",
}

# ঘৰৰ সম্পূৰ্ণ বিৱৰণ
HOUSE_DETAILS = {
    1: {
        "name": "লগ্ন (প্ৰথম ঘৰ)",
        "topics": "শৰীৰ, স্বাস্থ্য, ব্যক্তিত্ব, ৰূপ-ৰং, মূৰ, মগজু, চুলি, চামৰা, নিজৰ ইচ্ছা-অনিচ্ছা, আত্মবিশ্বাস, নেতৃত্ব ক্ষমতা",
        "diseases": "মূৰৰ বিষ, مগজুৰ ৰোগ, চুলি সৰা, চামৰাৰ ৰোগ (যেনে: খহু, খজুৱতি), চকুৰ ৰোগ, অনিদ্ৰা, মানসিক চাপ, মাইগ্ৰেইন,মূৰত আঘাত",
        "good_effect": "শৰীৰ সুস্থ থাকে, আত্মবিশ্বাস বাঢ়ে, মানুহে সন্মান কৰে, নেতৃত্ব ক্ষমতা বৃদ্ধি পায়, নতুন কাম আৰম্ভ কৰিব পাৰে, ৰূপ-ৰং ভাল হয়",
        "bad_effect": "শৰীৰত ৰোগ-ব্যাধিয়ে ধৰে, মূৰৰ বিষ বা মাইগ্ৰেইনৰ সমস্যা হয়, আত্মবিশ্বাস কমি যায়, মানুহে অপমান কৰে, দুৰ্ঘটনাত পৰিব পাৰে, চুলি সৰে বা চামৰাৰ ৰোগ হয়"
    },
    2: {
        "name": "দ্বিতীয় ঘৰ",
        "topics": "ধন-সম্পত্তি, সঞ্চয়, বেংক বেলেঞ্চ, কথা কোৱাৰ ধৰণ, মুখ, দাঁত, জিভা, চকুৰ ৰশ্মি, পৰিয়াল, খোৱা-বোৱা, খাদ্যাভ্যাস, মূল্যৱান বস্তু (সোণ-ৰূপ), কুটুম্ব",
        "diseases": "দাঁতৰ বিষ, দাঁতত পোক, মুখৰ ৰোগ, জিভাৰ ৰোগ, চকুৰ ৰশ্মি কমি যোৱা, টনচিল, খাদ্যনলীৰ ৰোগ, মুখ জনিত ৰোগ, কথা বজা বা কথা কোৱাত অসুবিধা বা কথা কমকৈ কোৱা",
        "good_effect": "ধন-সম্পত্তি বৃদ্ধি পায়, বেংকত টকা জমা হয়, ভাল খোৱা-বোৱা খাবলৈ পায়, কথা কোৱাৰ ধৰণ মিঠা হয়, পৰিয়ালৰ পৰা সহায় পায়, সোণ-ৰূপ কিনিব পাৰে",
        "bad_effect": "ধন-সম্পত্তি নষ্ট হয়, ঋণ হয়, দাঁতৰ বিষ বা দাঁতৰ ৰোগ হয়, চকুৰ ৰশ্মি কমি যায়, খোৱা-বোৱাত সমস্যা হয়, বাণী কঠোৰ, পৰিয়ালৰ লগত কাজিয়া হয়"
    },
    3: {
        "name": "তৃতীয় ঘৰ",
        "topics": "ভাতৃ-ভগ্নী, সাহস, পৰাক্ৰম, চুটি যাত্ৰা, হাত, কান্ধ, বাহু, ডিঙি, (এজমা, ব্ৰংকাইটিছ),শ্বাস-প্ৰশ্বাসৰ সমস্যা, যোগাযোগ (ফোন, চিঠি, ইণ্টাৰনেট), লেখা-মেলা, সংগীত, নৃত্য, সাংবাদিকতা",
        "diseases": "হাত বা কান্ধৰ বিষ, ডিঙিৰ ৰোগ, হাওফাও জনিত ৰোগ (এজমা, ব্ৰংকাইটিছ), শ্বাস-প্ৰশ্বাসৰ সমস্যা, স্নায়ুৰ ৰোগ, কাণৰ ৰোগ, থাইৰইড",
        "good_effect": "ভাতৃ-ভগ্নীৰ পৰা সহায় পায়, সাহস বাঢ়ে, চুটি যাত্ৰা কৰিবলৈ পায়, যোগাযোগৰ মাধ্যম ভাল হয়, লেখা-মেলাৰ কামত সফলতা পায়, সংগীত বা নৃত্য শিকিব পাৰে",
        "bad_effect": "ভাতৃ-ভগ্নীৰ লগত কাজিয়া হয়, সাহস কমি যায়, চুটি যাত্ৰাত বিপদ হয়, হাত বা কান্ধত বিষ হয়, ডিঙিৰ ৰোগ হয়, উষাহ জনিতৰ ৰোগ (এজমা) হয়, স্নায়ুৰ ৰোগ হয়"
    },
    4: {
        "name": "চতুৰ্থ ঘৰ",
        "topics": "মাতৃ, ঘৰ-বাৰী, মাটি-বাৰী, বাহন (গাড়ী, মটৰ চাইকেল), সুখ-শান্তি, মনৰ শান্তি, বুকু, উষাহ জনিত, পেট, প্ৰাথমিক শিক্ষা, ঘৰুৱা জীৱন, পুৰণি বস্তু, কৃষি",
        "diseases": "বুকুৰ ৰোগ, হৃদযন্ত্ৰৰ ৰোগ, হাওফাও জনিত ৰোগ, পেটৰ ৰোগ, গেছ, বদহজম, এলাৰ্জী, পানী জমা হোৱা (Water Retention), মানসিক অশান্তি, ডিপ্ৰেছন",
        "good_effect": "মাতৃৰ পৰা মৰম-চেনেহ পায়, ঘৰ-বাৰী কিনিব পাৰে, বাহন কিনিব পাৰে, মনত শান্তি থাকে, পেটৰ ৰোগ নহয়, ঘৰুৱা জীৱন সুখী হয়, কৃষি কামত লাভ হয়",
        "bad_effect": "মাতৃৰ অসুখ হয় বা মাতৃৰ লগত কাজিয়া হয়, ঘৰ-বাৰীৰ ক্ষতি হয়, বাহন দুৰ্ঘটনাত পৰে, মনত অশান্তি থাকে, বুকুৰ ৰোগ বা হৃদযন্ত্ৰৰ ৰোগ হয়, পেটৰ ৰোগ (গেছ, বদহজম) হয়, ডিপ্ৰেছন হয়"
    },
    5: {
        "name": "পঞ্চম ঘৰ",
        "topics": "সন্তান, প্ৰেম, পঢ়া-শুনা, বুদ্ধি, জ্ঞান, পূৰ্বজন্মৰ পুণ্য, পেটৰ ওপৰ অংশ, কলিজা, গৰ্ভ, খেলা-ধূলা, চখ (Hobby), সৃষ্টিশীল কাম (আঁকা, গান গোৱা), জুৱা বা লটাৰী",
        "diseases": "পেটৰ ওপৰ অংশৰ ৰোগ, কলিজাৰ ৰোগ (জণ্ডিচ, হেপাটাইটিছ), গৰ্ভৰ ৰোগ (মহিলাৰ), সন্তান জন্ম দিয়াত অসুবিধা, বুদ্ধিৰ বিকাৰ, পঢ়াত মন নবহা, হৃদযন্ত্ৰৰ ৰোগ",
        "good_effect": "সন্তান জন্ম হয়, সন্তানে ভাল ফল দেখুৱায়, প্ৰেমত সফলতা পায়, পঢ়া-শুনাত ভাল কৰে, বুদ্ধি চোকা হয়, পূৰ্বজন্মৰ পুণ্যৰ ফল পায়, সৃষ্টিশীল কামত সফলতা পায়",
        "bad_effect": "সন্তান জন্ম দিয়াত অসুবিধা হয়, সন্তানৰ অসুখ হয়, প্ৰেমত বিফলতা পায়, পঢ়া-শুনাত মন নবহে, বুদ্ধি কমি যায়, কলিজাৰ ৰোগ (জণ্ডিচ) হয়, গৰ্ভৰ ৰোগ হয়, জুৱা বা লটাৰীত টকা নষ্ট হয়"
    },
    6: {
        "name": "ষষ্ঠ ঘৰ",
        "topics": "ৰোগ-ব্যাধি, শত্ৰু, ঋণ, আদালত-কাছাৰী, প্ৰতিযোগিতা, চাকৰি বা সেৱা, পেটৰ তল অংশ, নাৰী, অন্ত্ৰ, পেটৰ ৰোগ, জীৱ-জন্তুৰ পৰা কামোৰ, চাকৰ-নাকৰ, মামা-খুড়া",
        "diseases": "পেটৰ তল অংশৰ ৰোগ, নাৰীৰ ৰোগ, অন্ত্ৰৰ ৰোগ, ডায়েৰিয়া, কোষ্ঠকাঠিন্য, এপেণ্ডিক্স, আলচাৰ, খাদ্য বিষক্ৰিয়া, জীৱ-জন্তুৰ কামোৰৰ পৰা হোৱা ৰোগ, ছালৰ ৰোগ, এলাৰ্জী, চৰ্মৰোগ",
        "good_effect": "ৰোগ-ব্যাধি ভাল হয়, শত্ৰু পৰাজিত হয়, ঋণ পৰিশোধ কৰিব পাৰে, আদালত-কাছাৰীত জয়ী হয়, প্ৰতিযোগিতাত জিকিব পাৰে, চাকৰিত পদোন্নতি হয়, জীৱ-জন্তুৰ পৰা উপকাৰ পায়",
        "bad_effect": "ৰোগ-ব্যাধিয়ে ধৰে, শত্ৰুৱে ক্ষতি কৰে, ঋণ বাঢ়ি যায়, আদালত-কাছাৰীত হাৰে, প্ৰতিযোগিতাত পৰাজিত হয়, পেটৰ ৰোগ (ডায়েৰিয়া, কোষ্ঠকাঠিন্য, আলচাৰ) হয়, জীৱ-জন্তুৱে কামোৰে, চৰ্মৰোগ হয়"
    },
    7: {
        "name": "সপ্তম ঘৰ",
        "topics": "বিবাহ, স্বামী-স্ত্ৰীৰ সম্পৰ্ক, ব্যৱসায়িক অংশীদাৰ, জনসাধাৰণ, যৌন সম্পৰ্ক, প্ৰস্ৰাৱৰ অংগ, গৰ্ভাশয় (মহিলাৰ), কিডনী, তলপেট, বিদেশ যাত্ৰা, চুক্তি-পত্ৰ",
        "diseases": "প্ৰস্ৰাৱৰ ৰোগ, কিডনীৰ ৰোগ, গৰ্ভাশয়ৰ ৰোগ (মহিলাৰ), যৌন ৰোগ, তলপেটৰ বিষ, মূত্ৰনলীৰ সংক্ৰমণ (UTI), পাথৰী, প্ৰস্ৰাৱত জ্বলা-পোৰা",
        "good_effect": "বিবাহ হয়, স্বামী-স্ত্ৰীৰ সম্পৰ্ক ভাল হয়, ব্যৱসায়িক অংশীদাৰৰ পৰা লাভ হয়, জনসাধাৰণৰ সমৰ্থন পায়, বিদেশ যাত্ৰা কৰিব পাৰে, চুক্তি-পত্ৰত স্বাক্ষৰ কৰিব পাৰে",
        "bad_effect": "বিবাহত বিঘিনি হয়, স্বামী-স্ত্ৰীৰ কাজিয়া হয়, ব্যৱসায়িক অংশীদাৰে ঠগে, জনসাধাৰণে বিৰোধিতা কৰে, প্ৰস্ৰাৱৰ ৰোগ বা কিডনীৰ ৰোগ হয়, যৌন ৰোগ হয়, তলপেটৰ বিষ হয়"
    },
    8: {
        "name": "অষ্টম ঘৰ",
        "topics": "আয়ুস (জীৱনৰ দৈৰ্ঘ্য), মৃত্যু, দুৰ্ঘটনা, গোপন কথা, ৰহস্য, গৱেষণা, যাদু-টোনা, পূৰ্বজন্মৰ কৰ্মফল, উত্তৰাধিকাৰী সূত্ৰে পোৱা সম্পত্তি, বীমা, গুপ্ত অংগ, মলদ্বাৰ, যৌন শক্তি",
        "diseases": "গুপ্ত অংগৰ ৰোগ, মলদ্বাৰৰ ৰোগ (পাইলছ, ফিচাৰ), যৌন ৰোগ, দুৰ্ঘটনাত গুৰুতৰ আঘাত, অস্ত্ৰোপচাৰ (অপাৰেচন), ৰহস্যময় ৰোগ যিবোৰ চিকিৎসকে ধৰিব নোৱাৰে, কেন্সাৰ, টিউমাৰ, ৰক্তৰোগ",
        "good_effect": "আয়ুস বাঢ়ে, উত্তৰাধিকাৰী সূত্ৰে সম্পত্তি পায়, বীমাৰ টকা পায়, গৱেষণাত সফলতা পায়, গোপন কথা জানিব পাৰে, যৌন শক্তি বাঢ়ে, পূৰ্বজন্মৰ পুণ্যৰ ফল পায়",
        "bad_effect": "আয়ুসৰ ভয় থাকে, দুৰ্ঘটনাত পৰিব পাৰে, গুপ্ত অংগৰ ৰোগ হয়, মলদ্বাৰৰ ৰোগ (পাইলছ) হয়, অস্ত্ৰোপচাৰ কৰিব লগা হয়, ৰহস্যময় ৰোগ হয়, কেন্সাৰ বা টিউমাৰৰ ভয় থাকে, যাদু-টোনাৰ দ্বাৰা ক্ষতি হয়"
    },
    9: {
        "name": "নৱম ঘৰ",
        "topics": "ভাগ্য, পিতৃ, গুৰু, ধৰ্ম, উচ্চ শিক্ষা (কলেজ, বিশ্ববিদ্যালয়), বিদেশ যাত্ৰা, দীঘলীয়া যাত্ৰা, কৰঙণ, উৰু, সৌভাগ্য, দান-দক্ষিণা, নৈতিকতা, আইন, দৰ্শন, পূজা-পাঠ",
        "diseases": "লীভাৰ জনিত ৰোগ, উৰুৰ ৰোগ, হিপ জইণ্টৰ বিষ, ভৰিৰ ওপৰ অংশৰ ৰোগ, ৰক্তচাপ, ডায়েবেটিছ (মধুমেহ), থাইৰইড, ওজন বঢ়া বা কমা",
        "good_effect": "ভাগ্য ভাল হয়, পিতৃৰ পৰা সহায় পায়, গুৰুৰ আশীৰ্বাদ পায়, উচ্চ শিক্ষাত সফলতা পায়, বিদেশ যাত্ৰা কৰিব পাৰে, ধৰ্ম-কৰ্মত মন বহে, দান-দক্ষিণা কৰিব পাৰে, সৌভাগ্য লাভ হয়",
        "bad_effect": "ভাগ্যই সহায় নকৰে, পিতৃৰ অসুখ হয় বা পিতৃৰ লগত কাজিয়া হয়, গুৰুৰ অভাৱ হয়, উচ্চ শিক্ষাত বিফলতা পায়, বিদেশ যাত্ৰাত বিপদ হয়, কৰঙণ বা উৰুত বিষ হয়, ডায়েবেটিছ বা থাইৰইড হয়, ওজন বেচি বাঢ়ি যায়"
    },
    10: {
        "name": "দশম ঘৰ",
        "topics": "কৰ্ম, চাকৰি, ব্যৱসায়, সন্মান, প্ৰশাসন, ৰাজনীতি, পিতৃৰ সুখ, আঁঠু, হাড়, মেৰুদণ্ড, সমাজত স্থান, প্ৰতিপত্তি, কেৰিয়াৰ, লক্ষ্য, উচ্চাকাংক্ষা",
        "diseases": "আঁঠুৰ বিষ, হাড়ৰ ৰোগ (অষ্টিঅ'পৰ'ছিছ), মেৰুদণ্ডৰ বিষ, বাত বিষ, গেঁঠিয়া বাত, হাড় ভঙা, পিঠিৰ বিষ, স্নায়ুৰ ৰোগ, চাপজনিত ৰোগ (High BP)",
        "good_effect": "চাকৰিত পদোন্নতি হয়, ব্যৱসায়ত লাভ হয়, সমাজত সন্মান বাঢ়ে, ৰাজনীতিত সফলতা পায়, কেৰিয়াৰ ভাল হয়, লক্ষ্যত উপনীত হব পাৰে, পিতৃয়ে সুখী হয়",
        "bad_effect": "চাকৰি যায় বা চাকৰিত অসুবিধা হয়, ব্যৱসায়ত লোকচান হয়, সমাজত অপমান হয়, আঁঠুৰ বিষ বা হাড়ৰ ৰোগ হয়, মেৰুদণ্ডৰ বিষ হয়, বাত বিষে ধৰে, কেৰিয়াৰত বাধা আহে, লক্ষ্যত উপনীত হব নোৱাৰে"
    },
    11: {
        "name": "একাদশ ঘৰ",
        "topics": "লাভ, ইচ্ছাপূৰণ, ডাঙৰ ভাতৃ-ভগ্নী, বন্ধু-বান্ধৱ, সামাজিক জীৱন, ভৰিৰ তলুৱা, সঞ্চয়, বিনিয়োগ, সকলো ধৰণৰ লাভ, বোনাচ, উপাৰ্জন, আশা-আকাংক্ষা",
        "diseases": "ভৰিৰ তলুৱাৰ বিষ, ভৰিৰ স্নায়ুৰ ৰোগ, শিৰাৰ ৰোগ (Varicose Veins), ৰক্ত সঞ্চালনৰ সমস্যা, ভৰি ফুলা, গোৰোহাৰ বিষ, এলাৰ্জী",
        "good_effect": "সকলো ধৰণৰ লাভ হয়, ইচ্ছাপূৰণ হয়, ডাঙৰ ভাতৃ-ভগ্নীৰ পৰা সহায় পায়, বন্ধু-বান্ধৱৰ সংখ্যা বাঢ়ে, বিনিয়োগত লাভ হয়, বোনাচ বা উপাৰ্জন বাঢ়ে, আশা-আকাংক্ষা পূৰণ হয়",
        "bad_effect": "লাভৰ পৰিমাণ কমি যায়, ইচ্ছাপূৰণ নহয়, ডাঙৰ ভাতৃ-ভগ্নীৰ লগত কাজিয়া হয়, বন্ধু-বান্ধৱে ঠগে, বিনিয়োগত লোকচান হয়, ভৰিৰ তলুৱাৰ বিষ বা ভৰিৰ ৰোগ হয়, শিৰাৰ ৰোগ হয়"
    },
    12: {
        "name": "দ্বাদশ ঘৰ",
        "topics": "ব্যয়, খৰচ, বিদেশ, মোক্ষ, চিকিৎসালয়, জেল, গুপ্ত শত্ৰু, ভৰি, টোপনি, ধ্যান, একাকীত্ব, দান, আধ্যাত্মিকতা, পূৰ্বজন্মৰ স্মৃতি, লোকচান, বিলাসী খৰচ",
        "diseases": "ভৰিৰ ৰোগ, টোপনিৰ ৰোগ (অনিদ্ৰা বা বেচি টোপনি), মানসিক ৰোগ, ডিপ্ৰেছন, চিকিৎসালয়লৈ বিশেষ কাৰণত দৌৰি থকা , চকুৰ ৰোগ, কাণৰ ৰোগ, নিচাযুক্ত দ্ৰব্যৰ আসক্তি",
        "good_effect": "বিদেশ যাত্ৰা কৰিব পাৰে, আধ্যাত্মিকতাত মন বহে, ধ্যান কৰিব পাৰে, মোক্ষ লাভৰ বাট মুকলি হোৱাৰ ফালে ধাবমান, দান কৰিব পাৰে, পূৰ্বজন্মৰ পুণ্যৰ ফল পায়, চিকিৎসালয়ৰ পৰা মুক্তি পায়",
        "bad_effect": "বেচি খৰচ হয়, টকা-পইচা নষ্ট হয়, বিদেশত কষ্ট পায়, চিকিৎসালয়ত ভৰ্তি হব লগা হয়, গুপ্ত শত্ৰুৱে ক্ষতি কৰে, টোপনিৰ ৰোগ হয়, মানসিক ৰোগ বা ডিপ্ৰেছন হয়, নিচাযুক্ত দ্ৰব্যৰ প্ৰতি আসক্তি বাঢ়ে"
    }
}

# ═══════════════════════════════════════════════════════════════
# নাম ৰূপান্তৰ (Name Conversion)
# ═══════════════════════════════════════════════════════════════

def get_eng_planet(name: str) -> str:
    m = {
        "সূৰ্য": "Sun", "ৰবি": "Sun", "Sun": "Sun",
        "চন্দ্ৰ": "Moon", "Moon": "Moon",
        "মংগল": "Mars", "Mars": "Mars",
        "বুধ": "Mercury", "Mercury": "Mercury",
        "বৃহস্পতি": "Jupiter", "Jupiter": "Jupiter",
        "শুক্ৰ": "Venus", "Venus": "Venus",
        "শনি": "Saturn", "Saturn": "Saturn",
        "ৰাহু": "Rahu", "Rahu": "Rahu",
        "কেতু": "Ketu", "Ketu": "Ketu",
    }
    return m.get(name.strip(), name.strip())

def get_asm_planet(name: str) -> str:
    m = {
        "Sun": "ৰবি", "Moon": "চন্দ্ৰ", "Mars": "মংগল",
        "Mercury": "বুধ", "Jupiter": "বৃহস্পতি", "Venus": "শুক্ৰ",
        "Saturn": "শনি", "Rahu": "ৰাহু", "Ketu": "কেতু",
    }
    return m.get(name.strip(), name.strip())

def convert_planet_degrees_to_en(planet_degrees: dict) -> dict:
    asm_to_en = {
        "ৰবি": "Sun", "চন্দ্ৰ": "Moon", "মংগল": "Mars", "বুধ": "Mercury",
        "বৃহস্পতি": "Jupiter", "শুক্ৰ": "Venus", "শনি": "Saturn",
        "ৰাহু": "Rahu", "কেতু": "Ketu", "লগ্ন": "Lagna",
    }
    result = {}
    for k, v in planet_degrees.items():
        en_key = asm_to_en.get(k, k)
        result[en_key] = v
    return result


# ═══════════════════════════════════════════════════════════════
# গ্ৰহৰ অৱস্থা (Planet State: বক্ৰি/মাৰ্গী/অস্ত/উচ্চ/নীচ)
# ═══════════════════════════════════════════════════════════════

# Exaltation signs (0-indexed)
_EXALTATION_SIGNS = {
    "ৰবি": 0, "চন্দ্ৰ": 1, "মংগল": 9, "বুধ": 5,
    "বৃহস্পতি": 3, "শুক্ৰ": 11, "শনি": 6
}
# Debilitation = exaltation + 7 signs
_DEBILITATION_SIGNS = {k: (v + 7) % 12 for k, v in _EXALTATION_SIGNS.items()}

# Combust degrees (angular distance from Sun)
_COMBUST_DEGREES = {
    "চন্দ্ৰ": 12, "মংগল": 17, "বুধ": 14, "বুধ_বক্ৰি": 13,
    "বৃহস্পতি": 11, "শুক্ৰ": 10, "শুক্ৰ_বক্ৰি": 8, "শনি": 15
}

_STATE_LABELS = {
    "margi": {"as": "মাৰ্গী", "bn": "মার্গী", "hi": "मार्गी", "en": "Direct"},
    "vakri": {"as": "বক্ৰী", "bn": "বক্রী", "hi": "वक्री", "en": "Retrograde"},
    "asta": {"as": "অস্ত", "bn": "অস্ত", "hi": "अस्त", "en": "Combust"},
    "uchch": {"as": "উচ্চ", "bn": "উচ্চ", "hi": "उच्च", "en": "Exalted"},
    "nich": {"as": "নীচ", "bn": "নীচ", "hi": "नीच", "en": "Debilitated"},
}


def get_planet_state(planet_asm: str, sign_idx: int, speed: float,
                     sun_longitude: float, planet_longitude: float,
                     lang: str = 'as') -> str:
    """
    Calculate planet state: Retrograde (বক্ৰী), Direct (মাৰ্গী), Combust (অস্ত),
    Exalted (উচ্চ), Debilitated (নীচ).
    Returns a localized string with all applicable states.
    """
    def _(key): return _STATE_LABELS.get(key, {}).get(lang, key)

    states = []

    # Rahu & Ketu are always retrograde (chaya graha)
    if planet_asm in ("ৰাহু", "কেতু"):
        return _("vakri")

    # Lagna has no state
    if planet_asm == "লগ্ন":
        return "—"

    # Check exalted / debilitated
    if planet_asm in _EXALTATION_SIGNS:
        if sign_idx == _EXALTATION_SIGNS[planet_asm]:
            states.append(_("uchch"))
        elif sign_idx == _DEBILITATION_SIGNS[planet_asm]:
            states.append(_("nich"))

    # Check retrograde / direct
    is_retro = speed < 0
    if is_retro:
        states.append(_("vakri"))
    else:
        states.append(_("margi"))

    # Check combust (only for planets other than Sun, Rahu, Ketu)
    if planet_asm not in ("ৰবি", "সূৰ্য", "ৰাহু", "কেতু"):
        angular_distance = abs(planet_longitude - sun_longitude)
        if angular_distance > 180:
            angular_distance = 360 - angular_distance

        combust_limit = None
        if planet_asm == "বুধ" and is_retro:
            combust_limit = _COMBUST_DEGREES.get("বুধ_বক্ৰি")
        elif planet_asm == "শুক্ৰ" and is_retro:
            combust_limit = _COMBUST_DEGREES.get("শুক্ৰ_বক্ৰি")
        else:
            combust_limit = _COMBUST_DEGREES.get(planet_asm)

        if combust_limit and angular_distance < combust_limit:
            states.append(_("asta"))

    return " · ".join(states) if states else _("margi")

# ═══════════════════════════════════════════════════════════════
# গ্ৰহৰ সম্পূৰ্ণ তথ্য (Planet Details)
# ═══════════════════════════════════════════════════════════════

def get_planet_details(planet_eng: str, planet_degrees: dict, lagna_sign_index: int) -> dict:
    if planet_eng not in planet_degrees:
        return None

    degree = planet_degrees[planet_eng]
    sign_index = int(degree / 30.0)
    deg_in_sign = round(degree % 30, 2)
    house_num = ((sign_index - lagna_sign_index + 12) % 12) + 1
    rasi_name = RASI_NAMES[sign_index]

    strength_map = {
        "Sun":     {"উচ্চ": [0], "স্বগৃ্হী": [4], "নীচ": [6], "মিত্ৰ": [3, 7, 8, 11], "শত্ৰু": [1, 9, 10]},
        "Moon":    {"উচ্চ": [1], "স্বগৃ্হী": [3], "নীচ": [7], "মিত্ৰ": [4, 2, 5], "শত্ৰু": []},
        "Mars":    {"উচ্চ": [9], "স্বগৃ্হী": [0, 7], "নীচ": [3], "মিত্ৰ": [4, 8, 11], "শত্ৰু": [2, 5]},
        "Mercury": {"উচ্চ": [5], "স্বগৃ্হী": [2, 5], "নীচ": [11], "মিত্ৰ": [4, 1, 6], "শত্ৰু": [3]},
        "Jupiter": {"উচ্চ": [3], "স্বগৃ্হী": [8, 11], "নীচ": [9], "মিত্ৰ": [0, 4, 7], "শত্ৰু": [1, 6, 2, 5]},
        "Venus":   {"উচ্চ": [11], "স্বগৃ্হী": [1, 6], "নীচ": [5], "মিত্ৰ": [2, 9, 10], "শত্ৰু": [4, 3]},
        "Saturn":  {"উচ্চ": [6], "স্বগৃ্হী": [9, 10], "নীচ": [0], "মিত্ৰ": [1, 2, 5], "শত্ৰু": [4, 3, 7, 8, 11]},
    }

    strength = "সাধাৰণ (সম ৰাশিত)"
    strength_category = "সাধাৰণ"
    if planet_eng in strength_map:
        sm = strength_map[planet_eng]
        if sign_index in sm["উচ্চ"]:
            strength = "উচ্চ (অতি সু-অৱস্থিত)"
            strength_category = "উচ্চ"
        elif sign_index in sm["স্বগৃ্হী"]:
            strength = "স্বগৃ্হী (সু-অৱস্থিত)"
            strength_category = "স্বগৃ্হী"
        elif sign_index in sm["নীচ"]:
            strength = "নীচ (দুৰ্বলভাৱে অৱস্থিত)"
            strength_category = "নীচ"
        elif sign_index in sm["মিত্ৰ"]:
            strength = "মিত্ৰ ক্ষেত্ৰী"
            strength_category = "মিত্ৰ"
        elif sign_index in sm["শত্ৰু"]:
            strength = "শত্ৰু ক্ষেত্ৰী"
            strength_category = "শত্ৰু"
    elif planet_eng in ("Rahu", "Ketu"):
        strength = "ছায়া গ্ৰহ"
        strength_category = "ছায়া"

    owned_houses = []
    for h in range(1, 13):
        s = (lagna_sign_index + h - 1) % 12
        if SIGN_LORDS[s] == planet_eng:
            owned_houses.append(h)

    karaka = KARAKATWA.get(planet_eng, "")

    nak_index = int(degree / 13.333333)
    nak_name = NAKSHATRAS[nak_index]
    is_tikshna = nak_name in TIKSHNA_NAKSHATRAS

    lord_index = nak_index % 9
    nak_lord_eng = DASHA_LORDS[lord_index]
    nak_lord_house = None
    if nak_lord_eng in planet_degrees:
        lord_deg = planet_degrees[nak_lord_eng]
        lord_sign = int(lord_deg / 30.0)
        nak_lord_house = ((lord_sign - lagna_sign_index + 12) % 12) + 1

    nature = get_planet_nature(lagna_sign_index, planet_eng)

    is_point1_bad = False
    if house_num in (6, 8, 12):
        if strength_category in ("উচ্চ", "স্বগৃ্হী"):
            is_point1_bad = False
        else:
            is_point1_bad = True

    is_point2_bad = False
    if is_tikshna:
        is_point2_bad = True
        
    if nak_lord_eng == "Rahu":
        is_point2_bad = True
    elif nak_lord_house is not None and nak_lord_house in (6, 8, 12):
        is_point2_bad = True

    return {
        "name_en": planet_eng,
        "name_asm": get_asm_planet(planet_eng),
        "degree": degree,
        "sign_index": sign_index,
        "deg_in_sign": deg_in_sign,
        "rasi": rasi_name,
        "house": house_num,
        "strength": strength,
        "strength_category": strength_category,
        "owned_houses": owned_houses,
        "karaka": karaka,
        "nak_name": nak_name,
        "is_tikshna": is_tikshna,
        "nak_lord_eng": nak_lord_eng,
        "nak_lord_asm": get_asm_planet(nak_lord_eng),
        "nak_lord_house": nak_lord_house,
        "nature": nature,
        "is_point1_bad": is_point1_bad,
        "is_point2_bad": is_point2_bad,
    }

# ═══════════════════════════════════════════════════════════════
# লগ্ন অনুসৰি গ্ৰহৰ প্ৰকৃতি
# ═══════════════════════════════════════════════════════════════

def get_planet_nature(lagna_index: int, planet_name: str) -> str:
    if planet_name in ("Rahu", "Ketu"):
        return "ছায়া গ্ৰহ (অৱস্থানৰ ওপৰত নিৰ্ভৰশীল)"

    nature_map = {
        0:  {"শুভ": ["Jupiter", "Sun", "Mars"], "অশুভ": ["Mercury", "Venus", "Saturn"]},
        1:  {"শুভ": ["Saturn", "Mercury"], "অশুভ": ["Jupiter", "Moon"]},
        2:  {"শুভ": ["Venus", "Mercury"], "অশুভ": ["Mars", "Jupiter", "Sun"]},
        3:  {"শুভ": ["Mars", "Jupiter"], "অশুভ": ["Mercury", "Venus"]},
        4:  {"শুভ": ["Mars", "Sun"], "অশুভ": ["Mercury", "Venus"]},
        5:  {"শুভ": ["Venus", "Mercury"], "অশুভ": ["Mars", "Moon", "Jupiter"]},
        6:  {"শুভ": ["Saturn", "Mercury", "Venus"], "অশুভ": ["Jupiter", "Moon", "Sun"]},
        7:  {"শুভ": ["Moon", "Jupiter", "Sun"], "অশুভ": ["Mercury", "Venus"]},
        8:  {"শুভ": ["Mars", "Sun", "Jupiter"], "অশুভ": ["Saturn", "Mercury", "Venus"]},
        9:  {"শুভ": ["Venus", "Mercury", "Saturn"], "অশুভ": ["Mars", "Jupiter", "Moon"]},
        10: {"শুভ": ["Venus", "Saturn"], "অশুভ": ["Jupiter", "Moon", "Mars"]},
        11: {"শুভ": ["Moon", "Mars", "Jupiter"], "অশুভ": ["Venus", "Mercury", "Saturn", "Sun"]},
    }

    if lagna_index in nature_map:
        if planet_name in nature_map[lagna_index]["শুভ"]:
            return "শুভ"
        elif planet_name in nature_map[lagna_index]["অশুভ"]:
            return "অশুভ"
    return "নিৰপেক্ষ"

def get_planet_relationship(p1: str, p2: str) -> str:
    if p1 == p2:
        return "নিজ"
    if p1 in PLANET_FRIENDS:
        if p2 in PLANET_FRIENDS[p1]["friend"]:
            return "মিত্ৰ"
        elif p2 in PLANET_FRIENDS[p1]["enemy"]:
            return "শত্ৰু"
    return "সম"

# ═══════════════════════════════════════════════════════════════
# গ্ৰহৰ অৱস্থানৰ বৰ্ণনা
# ═══════════════════════════════════════════════════════════════

def describe_planet_position(pd: dict) -> str:
    if pd is None:
        return "গ্ৰহৰ তথ্য উপলব্ধ নহয়।"
    p_asm = pd["name_asm"]
    house = pd["house"]
    rasi = pd["rasi"]
    strength = pd["strength"]
    strength_cat = pd["strength_category"]
    deg = pd["deg_in_sign"]

    desc = f"{p_asm} গ্ৰহটো {rasi} ৰাশিত {deg} ডিগ্ৰীত অৱস্থান কৰি আছে, যি লগ্নৰ পৰা {house} নং ঘৰ ({HOUSE_NAMES.get(house, '')})। "
    if strength_cat == "উচ্চ":
        desc += f"ই {rasi} ৰাশিত উচ্চ (Exalted) অৱস্থাত আছে, অৰ্থাৎ ই অতি বলৱান আৰু সু-অৱস্থিত। উচ্চ গ্ৰহই নিজৰ কাৰকত্ব আৰু ভাৱৰ সম্পূৰ্ণ শুভ ফল প্ৰদান কৰে। "
    elif strength_cat == "স্বগৃ্হী":
        desc += f"ই {rasi} ৰাশিত স্বগৃ্হী (Own Sign) অৱস্থাত আছে, অৰ্থাৎ ই নিজৰ ঘৰত বহি সু-অৱস্থিত হৈ আছে। স্বগৃ্হী গ্ৰহই স্থিৰ আৰু নিৰ্ভৰযোগ্য শুভ ফল দিয়ে। "
    elif strength_cat == "নীচ":
        desc += f"ই {rasi} ৰাশিত নীচ (Debilitated) অৱস্থাত আছে, অৰ্থাৎ ই অতি দুৰ্বল। নীচ গ্ৰহই নিজৰ কাৰকত্ব আৰু ভাৱৰ সম্পূৰ্ণ ভাল ফল দিব নোৱাৰে, কষ্ট আৰু বাধাৰ সৃষ্টি কৰে। "
    elif strength_cat == "মিত্ৰ":
        desc += f"ই {rasi} ৰাশিত মিত্ৰ ক্ষেত্ৰী অৱস্থাত আছে, অৰ্থাৎ ই মিত্ৰ গ্ৰহৰ ৰাশিত থাকি মধ্যম মানৰ শুভ ফল প্ৰদান কৰে। "
    elif strength_cat == "শত্ৰু":
        desc += f"ই {rasi} ৰাশিত শত্ৰু ক্ষেত্ৰী অৱস্থাত আছে, অৰ্থাৎ ই শত্ৰু গ্ৰহৰ ৰাশিত থাকি দুৰ্বলভাৱে অৱস্থান কৰিছে। ইয়াৰ ফল সম্পূৰ্ণ শুভ নহয়, সংগ্ৰাম আৰু বাধাৰ সৃষ্টি কৰিব পাৰে। "
    elif strength_cat == "ছায়া":
        desc += f"ই এটা ছায়া গ্ৰহ (ৰাহু/কেতু)। ছায়া গ্ৰহই যিটো ঘৰত বহে আৰু যি গ্ৰহৰ সংস্পৰ্শত থাকে, তাৰ দ্বাৰা প্ৰভাৱিত হয়। "
    else:
        desc += f"ই {rasi} ৰাশিত সাধাৰণ (সম) অৱস্থাত আছে। "

    if house in (6, 8, 12):
        if strength_cat in ("উচ্চ", "স্বগৃ্হী"):
            desc += f"{house} নং ঘৰটো সাধাৰণতে অশুভ (দুষ্টস্থান) যদিও, গ্ৰহটো উচ্চ/স্বগৃ্হী হোৱাৰ বাবে ইয়াৰ অশুভ প্ৰভাৱ বহু পৰিমাণে হ্ৰাস পাব। "
        else:
            desc += f"{house} নং ঘৰটো এটা অশুভ ঘৰ (দুষ্টস্থান)। সেয়েহে এই ঘৰত থকাৰ বাবে গ্ৰহটোৰ প্ৰকৃত শুভ ফল প্ৰকাশ নাপাব পাৰে। "
    return desc

def describe_house_lordship(pd: dict) -> str:
    if pd is None:
        return ""
    p_asm = pd["name_asm"]
    owned = pd["owned_houses"]
    if not owned:
        return f"{p_asm} এটা ছায়া গ্ৰহ হোৱাৰ বাবে ইয়াৰ কোনো নিজা ঘৰ নাই। ই যিটো ঘৰত বহে আৰু যি গ্ৰহৰ লগত থাকে, তাৰ ফলহে প্ৰদান কৰে।\n"

    desc = f"{p_asm} গ্ৰহটো "
    owned_parts = []
    for h in owned:
        hd = HOUSE_DETAILS.get(h, {})
        hname = hd.get("name", f"{h} নং ঘৰ")
        owned_parts.append(f"{hname}")
    desc += " আৰু ".join(owned_parts) + " ৰ অধিপতি।\n"
    desc += f"সেয়েহে ইয়াৰ দশাৰ সময়ত এই ঘৰসমূহৰ বিষয়বোৰত বিশেষ প্ৰভাৱ পৰিব।\n"
    for h in owned:
        if h in HOUSE_DETAILS:
            hd = HOUSE_DETAILS[h]
            desc += f"  ▸ {hd['name']}: {hd['topics']}\n"
            desc += f"    সম্ভাৱ্য ৰোগ: {hd['diseases']}\n"
    return desc

def describe_nakshatra(pd: dict, is_antardasha: bool = False) -> str:
    if pd is None:
        return ""
    p_asm = pd["name_asm"]
    p_eng = pd["name_en"]
    nak = pd["nak_name"]
    is_tikshna = pd["is_tikshna"]
    nak_lord_eng = pd["nak_lord_eng"]
    nak_lord_asm = pd["nak_lord_asm"]
    nak_lord_house = pd["nak_lord_house"]
    nature = pd.get("nature", "নিৰপেক্ষ")

    desc = f"{p_asm} গ্ৰহটো '{nak}' নক্ষত্ৰত অৱস্থান কৰিছে, যাৰ নক্ষত্ৰপতি হৈছে {nak_lord_asm}। "
    if is_tikshna:
        is_malefic = p_eng in ["Rahu", "Ketu", "Saturn", "Mars", "Sun"] or nature == "অশুভ"
        if is_antardasha and is_malefic:
            desc += f"অন্তৰদশাপতি অশুভ গ্ৰহ আৰু অশুভ নক্ষত্ৰত থকা বাবে এই সময়চোৱাত স্বাস্হ্যজনিত সমস্যা, কষ্ট বৃদ্ধি , ব্যয় বৃদ্ধি, মানসিক অশান্তি হোৱাৰ সম্ভাবনা দেখা যায়। "
        else:
            desc += f"'{nak}' এটি অতি অশুভ (তীক্ষ্ন) নক্ষত্ৰ। সেয়েহে এই নক্ষত্ৰত থকাৰ বাবে {p_asm}ৰ দশাৰ কিছু সময়ৰ বাবে (বিশেষকৈ দশাৰ আৰম্ভণি বা শেষৰ ফালে) ই অশুভ পৰিণাম প্ৰদান কৰিব পাৰে। ইয়াৰ কাৰকত্ব আৰু ই যিবোৰ ঘৰৰ অধিপতি, সেই বিষয়সমূহত কষ্ট বা বাধাৰ সৃষ্টি হ'ব পাৰে। "

    if nak_lord_eng == "Rahu":
        if is_antardasha:
            desc += f"জ্যোতিষশাস্ত্ৰৰ বিশেষ নিয়ম অনুসৰি, ৰাহু গ্ৰহ যি স্থানতেই বহি নাথাকক কিয়, অন্তৰদশাপতি যদি ৰাহুৰ নক্ষত্ৰত থাকে তেতিয়া ই সদায় অশুভ ফল প্ৰদান কৰে। সেয়েহে {p_asm}ৰ অন্তৰ্দশাৰ ফলাফল অশুভ হ'ব আৰু বাধাৰ সন্মুখীন হ'ব পাৰে। "
        else:
            desc += f"জ্যোতিষশাস্ত্ৰৰ বিশেষ নিয়ম অনুসৰি, ৰাহু গ্ৰহ যি স্থানতেই বহি নাথাকক কিয়, কোনো গ্ৰহ ৰাহুৰ নক্ষত্ৰত থাকিলে ই সদায় অশুভ ফল প্ৰদান কৰে। সেয়েহে {p_asm}ৰ দশাৰ ফলাফল অশুভ হ'ব। "
    elif nak_lord_house is not None:
        if nak_lord_house in (6, 8, 12):
            desc += f"ইয়াৰ নক্ষত্ৰপতি {nak_lord_asm} গ্ৰহটো {nak_lord_house} নং অশুভ ঘৰত অৱস্থান কৰিছে। নক্ষত্ৰপতি অশুভ ঘৰত থকাৰ বাবে, {p_asm}ৰ দশাৰ ফলাফল আৰু বেছি পৰিমাণে বেয়া হ'ব পাৰে। কাৰণ নক্ষত্ৰপতিৰ অৱস্থানেহে গ্ৰহ এটাৰ প্ৰকৃত ফল নিৰ্ণয় কৰে (KP Logic অনুসৰি)। "
        else:
            desc += f"ইয়াৰ নক্ষত্ৰপতি {nak_lord_asm} গ্ৰহটো {nak_lord_house} নং শুভ ঘৰত অৱস্থান কৰিছে। নক্ষত্ৰপতি শুভ ঘৰত থকাৰ বাবে, {p_asm}ৰ দশাৰ ফলাফল ভাল হ'ব। কাৰণ নক্ষত্ৰপতিৰ অৱস্থানেহে গ্ৰহ এটাৰ প্ৰকৃত ফল নিৰ্ণয় কৰে। "
    return desc

def describe_karaka_impact(pd: dict) -> str:
    if pd is None:
        return ""
    p_asm = pd["name_asm"]
    karaka = pd["karaka"]
    return f"{p_asm} গ্ৰহটো {karaka}। সেয়েহে ইয়াৰ দশাৰ সময়ত এই বিষয়সমূহত বিশেষ প্ৰভাৱ পৰিব।\n"

# ═══════════════════════════════════════════════════════════════
# বিশেষ দশা নিয়ম (Special Dasha Rules)
# ═══════════════════════════════════════════════════════════════

def check_special_dasha_rules(maha_pd: dict, antar_pd: dict, lagna_sign_index: int) -> str:
    if maha_pd is None or antar_pd is None:
        return ""

    rules_output = ""
    maha_eng = maha_pd["name_en"]
    antar_eng = antar_pd["name_en"]
    antar_owned = antar_pd.get("owned_houses", [])
    maha_nature = maha_pd.get("nature", "নিৰপেক্ষ")
    antar_nature = antar_pd.get("nature", "নিৰপেক্ষ")

    lagna_lord = SIGN_LORDS[lagna_sign_index]
    antar_lagna_rel = get_planet_relationship(lagna_lord, antar_eng)

    malefics = ["Rahu", "Ketu", "Saturn", "Mars", "Sun"]
    is_maha_malefic = maha_eng in malefics or maha_nature == "অশুভ"
    is_antar_malefic = antar_eng in malefics or antar_nature == "অশুভ"

    if is_maha_malefic and is_antar_malefic and antar_lagna_rel == "শত্ৰু":
        rules_output += "• বিশেষ সতৰ্কবাণী: মহাদশা অশুভ গ্ৰহ আৰু লগ্নপতিৰ শত্ৰু অন্তৰদশা ও অশুভ গ্ৰহ গতিকে, এই সময়চোৱাত স্বাস্হ্যজনিত সমস্যা, কৰ্মক্ষেত্ৰত পৰিশ্ৰম বৃদ্ধি, কষ্ট বৃদ্ধি , ব্যয় বৃদ্ধি, মানসিক অশান্তি হোৱাৰ সম্ভাবনা দেখা যায়।\n\n"

    if is_antar_malefic and (3 in antar_owned or 12 in antar_owned):
        rules_output += "• বিশেষ সতৰ্কবাণী: অশুভ স্হানৰ অধিপতি হোৱা বাবে এই সময়চোৱাত স্বাস্হ্যজনিত সমস্যা, কষ্ট বৃদ্ধি , ব্যয় বৃদ্ধি, মানসিক অশান্তি হোৱাৰ সম্ভাবনা দেখা যায়।\n\n"

    if antar_eng == "Jupiter" and (3 in antar_owned or 6 in antar_owned or 8 in antar_owned):
        rules_output += "• বিশেষ সতৰ্কবাণী: অন্তৰদশাপতি শুভ গ্ৰহ হলেও অশুভ স্হানৰ অধিপতি হোৱা বাবে এই সময়চোৱাত কষ্ট বৃদ্ধি , ব্যয় বৃদ্ধি, মানসিক অশান্তি হোৱাৰ সম্ভাবনা দেখা যায় তথাপিও এটা সময়ত কষ্টৰ ফলত উন্নতি লাভৰ যোগো আছে।\n\n"

    return rules_output

# ═══════════════════════════════════════════════════════════════
# গতিশীল মহাদশা-অন্তৰ্দশা ফলাফল (Dynamic Prediction)
# ═══════════════════════════════════════════════════════════════

def get_maha_antar_prediction(maha_eng: str, antar_eng: str, planet_degrees: dict, lagna_sign_index: int) -> str:
    if "ৰবি" in planet_degrees or "Sun" not in planet_degrees:
        planet_degrees = convert_planet_degrees_to_en(planet_degrees)

    maha_pd = get_planet_details(maha_eng, planet_degrees, lagna_sign_index)
    antar_pd = get_planet_details(antar_eng, planet_degrees, lagna_sign_index)

    maha_asm = get_asm_planet(maha_eng)
    antar_asm = get_asm_planet(antar_eng)

    if maha_pd is None or antar_pd is None:
        return f"{maha_asm}ৰ মহাদশাত {antar_asm}ৰ অন্তৰ্দশাই জাতকৰ জীৱনলৈ মিশ্ৰিত ফল কঢ়িয়াই আনে। (গ্ৰহৰ তথ্য উপলব্ধ নহয়)"

    rel = get_planet_relationship(maha_eng, antar_eng)
    result = f"▶ {maha_asm} মহাদশাৰ {antar_asm} অন্তৰ্দশাৰ ফলাফল:\n\n"

    result += f"【{maha_asm} মহাদশাৰ গ্ৰহৰ অৱস্থান বিশ্লেষণ】\n"
    result += describe_planet_position(maha_pd) + "\n"
    result += describe_house_lordship(maha_pd)
    result += describe_karaka_impact(maha_pd)
    result += describe_nakshatra(maha_pd, is_antardasha=False) + "\n\n"

    result += f"【{antar_asm} অন্তৰ্দশাৰ গ্ৰহৰ অৱস্থান বিশ্লেষণ】\n"
    result += describe_planet_position(antar_pd) + "\n"
    result += describe_house_lordship(antar_pd)
    result += describe_karaka_impact(antar_pd)
    result += describe_nakshatra(antar_pd, is_antardasha=True) + "\n\n"

    result += f"【{maha_asm} আৰু {antar_asm} ৰ পৰস্পৰ সম্বন্ধ】\n"
    if rel == "মিত্ৰ":
        result += f"{maha_asm} আৰু {antar_asm} পৰস্পৰ মিত্ৰ গ্ৰহ। দুয়ো মিত্ৰ হোৱাৰ বাবে ইহঁতৰ দশাৰ ফলাফল পৰস্পৰক সহায় কৰিব আৰু ফল অধিক শুভ হ'ব। "
    elif rel == "শত্ৰু":
        result += f"{maha_asm} আৰু {antar_asm} পৰস্পৰ শত্ৰু গ্ৰহ। দুয়ো শত্ৰু হোৱাৰ বাবে ইহঁতৰ দশাৰ ফলাফলত সংঘাত হ'ব আৰু ফল মিশ্ৰিত বা বেয়া হ'ব পাৰে। "
    elif rel == "নিজ":
        result += f"{maha_asm} আৰু {antar_asm} একেটা গ্ৰহ। নিজৰ মহাদশাত নিজৰ অন্তৰ্দশাই গ্ৰহটোৰ প্ৰভাৱ দ্বিগুণ কৰি তুলিব। "
    else:
        result += f"{maha_asm} আৰু {antar_asm} পৰস্পৰ সম (Neutral) গ্ৰহ। দুয়ো সম হোৱাৰ বাবে ইহঁতৰ দশাৰ ফলাফল মধ্যম মানৰ হ'ব। "

    result += f"{maha_asm} লগ্নৰ বাবে '{maha_pd['nature']}' গ্ৰহ আৰু {antar_asm} লগ্নৰ বাবে '{antar_pd['nature']}' গ্ৰহ।\n\n"

    result += f"【Point 1, 2, 3 (দশা বিশ্লেষণ)】\n"
    result += f"• {maha_asm} (মহাদশা):\n"
    if maha_pd["is_point1_bad"]:
        result += f"  Point 1 (নিজৰ অৱস্থান): বেয়া — {maha_asm} {maha_pd['house']} নং অশুভ ঘৰত আছে।\n"
    else:
        result += f"  Point 1 (নিজৰ অৱস্থান): ভাল — {maha_asm} {maha_pd['house']} নং ঘৰত শুভভাৱে আছে।\n"

    if maha_pd["is_point2_bad"]:
        reasons = []
        if maha_pd["is_tikshna"]:
            reasons.append(f"'{maha_pd['nak_name']}' তীক্ষ্ন নক্ষত্ৰত আছে")
        if maha_pd["nak_lord_eng"] == "Rahu":
            reasons.append(f"নক্ষত্ৰপতি ৰাহু হোৱাৰ বাবে (ৰাহুৰ নক্ষত্ৰত থকা গ্ৰহ সদায় অশুভ ফল দিয়ে)")
        elif maha_pd["nak_lord_house"] in (6, 8, 12):
            reasons.append(f"নক্ষত্ৰপতি {maha_pd['nak_lord_asm']} {maha_pd['nak_lord_house']} নং অশুভ ঘৰত আছে")
        result += f"  Point 2 (নক্ষত্ৰ): বেয়া — {' আৰু '.join(reasons)}।\n"
    else:
        result += f"  Point 2 (নক্ষত্ৰ): ভাল — নক্ষত্ৰ আৰু নক্ষত্ৰপতিৰ অৱস্থান শুভ।\n"

    result += f"• {antar_asm} (অন্তৰ্দশা):\n"
    if antar_pd["is_point1_bad"]:
        result += f"  Point 1 (নিজৰ অৱস্থান): বেয়া — {antar_asm} {antar_pd['house']} নং অশুভ ঘৰত আছে।\n"
    else:
        result += f"  Point 1 (নিজৰ অৱস্থান): ভাল — {antar_asm} {antar_pd['house']} নং ঘৰত শুভভাৱে আছে।\n"

    if antar_pd["is_point2_bad"]:
        reasons = []
        if antar_pd["is_tikshna"]:
            reasons.append(f"'{antar_pd['nak_name']}' তীক্ষ্ন নক্ষত্ৰত আছে")
        if antar_pd["nak_lord_eng"] == "Rahu":
            reasons.append(f"নক্ষত্ৰপতি ৰাহু হোৱাৰ বাবে (ৰাহুৰ নক্ষত্ৰত থকা গ্ৰহ সদায় অশুভ ফল দিয়ে)")
        elif antar_pd["nak_lord_house"] in (6, 8, 12):
            reasons.append(f"নক্ষত্ৰপতি {antar_pd['nak_lord_asm']} {antar_pd['nak_lord_house']} নং অশুভ ঘৰত আছে")
        result += f"  Point 2 (নক্ষত্ৰ): বেয়া — {' আৰু '.join(reasons)}।\n"
    else:
        result += f"  Point 2 (নক্ষত্ৰ): ভাল — নক্ষত্ৰ আৰু নক্ষত্ৰপতিৰ অৱস্থান শুভ।\n"

    result += "\n【চূড়ান্ত সিদ্ধান্ত】\n"
    maha_bad = (1 if maha_pd["is_point1_bad"] else 0) + (1 if maha_pd["is_point2_bad"] else 0)
    antar_bad = (1 if antar_pd["is_point1_bad"] else 0) + (1 if antar_pd["is_point2_bad"] else 0)
    total_bad = maha_bad + antar_bad

    result += f"ওপৰোক্ত বিশ্লেষণৰ পৰা দেখা যায় যে, {maha_asm}ৰ মহাদশা আৰু {antar_asm}ৰ অন্তৰ্দশাৰ সময়ছোৱাত:\n\n"
    maha_owned = maha_pd["owned_houses"]
    antar_owned = antar_pd["owned_houses"]
    all_houses = list(set(maha_owned + antar_owned))

    if all_houses:
        house_str = ", ".join([f"{h} নং" for h in sorted(all_houses)])
        result += f"• এই দশাৰ সময়ত {house_str} ঘৰৰ বিষয়সমূহত বিশেষ প্ৰভাৱ পৰিব।\n"
        for h in sorted(all_houses):
            if h in HOUSE_DETAILS:
                hd = HOUSE_DETAILS[h]
                result += f"\n  ▸ {hd['name']}ৰ বিষয়সমূহ:\n    {hd['topics']}\n    সম্ভাৱ্য ৰোগ: {hd['diseases']}\n"
                if total_bad <= 1:
                    result += f"    শুভ ফল: {hd['good_effect']}\n"
                elif total_bad >= 3:
                    result += f"    অশুভ ফল: {hd['bad_effect']}\n"
                else:
                    result += f"    মিশ্ৰিত ফল: ভাল আৰু বেয়া দুয়োটাৰে মিশ্ৰণ হ'ব।\n"

    result += f"\n• {maha_asm}ৰ কাৰকত্ব ({maha_pd['karaka'].split(',')[0]}) আৰু {antar_asm}ৰ কাৰকত্ব ({antar_pd['karaka'].split(',')[0]}) সম্পৰ্কীয় বিষয়সমূহত প্ৰভাৱ পৰিব।\n\n"

    if total_bad == 0:
        result += f"দুয়োটা গ্ৰহৰে Point 1 আৰু Point 2 ভাল হোৱাৰ বাবে, এই দশাৰ সময়ছোৱা অত্যন্ত শুভ আৰু ফলপ্ৰসূ হ'ব। তেওঁ ওপৰোক্ত ঘৰ আৰু কাৰকত্বৰ বিষয়সমূহত সৰ্বোত্তম ফল লাভ কৰিব আৰু সকলো ক্ষেত্ৰতে উন্নতি দেখা পোৱা যাব । "
        if rel == "মিত্ৰ":
            result += f"দুয়ো গ্ৰহ পৰস্পৰ মিত্ৰ হোৱাৰ বাবে ফল আৰু অধিক শুভ হ'ব। "
        elif rel == "শত্ৰু":
            result += f"যদিও দুয়ো গ্ৰহ পৰস্পৰ শত্ৰু, তথাপি নিজ নিজ অৱস্থান ভাল হোৱাৰ বাবে ফল বেছি বেয়া নহ'ব। "
    elif total_bad <= 2:
        result += f"কিছুসংখ্যক Point বেয়া হোৱাৰ বাবে, এই দশাৰ সময়ছোৱাত মিশ্ৰিত ফল লাভ হ'ব। কিছুমান বিষয়ত ভাল ফল আৰু কিছুমান বিষয়ত সংগ্ৰাম বা বাধাৰ সন্মুখীন হ'ব লাগিব। "
    else:
        result += f"অধিকাংশ Point বেয়া হোৱাৰ বাবে, এই দশাৰ সময়ছোৱা সংগ্ৰামপূৰ্ণ হ'ব পাৰে। ওপৰোক্ত ঘৰ আৰু কাৰকত্বৰ বিষয়সমূহত বাধা, কষ্ট বা লোকচানৰ সন্মুখীন হ'ব লাগিব পাৰে। লগতে, কষ্ট আৰু পৰিশ্ৰমৰ সময়, যাত্ৰাও অধিক কৰিব লাগিব পাৰে, খৰচ বৃদ্ধি হব, স্বাস্হ্যজনিত সমস্যাও আহি পৰিব পাৰে। "

    if maha_pd["is_tikshna"]:
        result += f"\n\n⚠️ বিশেষ সতৰ্কবাণী: {maha_asm} গ্ৰহটো '{maha_pd['nak_name']}' তীক্ষ্ন নক্ষত্ৰত অৱস্থান কৰিছে। সেয়েহে এই মহাদশাৰ কিছু সময়ৰ বাবে (বিশেষকৈ দশাৰ আৰম্ভণি বা শেষৰ ফালে) {maha_asm}ৰ কাৰকত্ব ({maha_pd['karaka'].split(',')[0]}) আৰু ই যিবোৰ ঘৰৰ অধিপতি, সেই বিষয়সমূহত অশুভ পৰিণাম ভুগিব লগা হ'ব পাৰে। লগতে,কষ্ট আৰু পৰিশ্ৰমৰ সময় হব, যাত্ৰাও অধিক কৰিব লাগিব পাৰে, খৰচ বৃদ্ধি হব, স্বাস্হ্যজনিত সমস্যাও আহি পৰিব পাৰে। "
    if antar_pd["is_tikshna"]:
        result += f"\n\n⚠️ বিশেষ সতৰ্কবাণী: {antar_asm} গ্ৰহটো '{antar_pd['nak_name']}' তীক্ষ্ন নক্ষত্ৰত অৱস্থান কৰিছে। সেয়েহে এই অন্তৰ্দশাৰ কিছু সময়ৰ বাবে {antar_asm}ৰ কাৰকত্ব ({antar_pd['karaka'].split(',')[0]}) আৰু ই যিবোৰ ঘৰৰ অধিপতি, সেই বিষয়সমূহত অশুভ পৰিণাম ভুগিব লগা হ'ব পাৰে। লগতে, কষ্ট আৰু পৰিশ্ৰমৰ সময় হব, যাত্ৰাও অধিক কৰিব লাগিব পাৰে, খৰচ বৃদ্ধি হব, স্বাস্হ্যজনিত সমস্যাও আহি পৰিব পাৰে। "
    
    special_rules_text = check_special_dasha_rules(maha_pd, antar_pd, lagna_sign_index)
    if special_rules_text:
        result += f"\n\n【জ্যোতিষশাস্ত্ৰৰ বিশেষ নিয়মৰ প্ৰভাৱ】\n{special_rules_text}"

    # ─── Graha Bichar Integration for Mahadasha Planet ONLY ───
    # (Antardasha graha bichar is NOT included here — it's already shown
    #  in the separate Graha Bichar section of the PDF to avoid duplication)
    if get_graha_bichar and maha_asm in GRAHA_KARAKATTWA:
        maha_house_idx = maha_pd["house"] - 1  # 0-indexed for graha_bichar
        graha_bichar_maha = get_graha_bichar(maha_asm, maha_house_idx)
        if graha_bichar_maha:
            result += f"\n\n【{maha_asm} মহাদশাৰ গ্ৰহ বিচাৰ (ভাব অনুসৰি)】\n"
            result += graha_bichar_maha + "\n"

    result += "\n"
    return result

# ═══════════════════════════════════════════════════════════════
# গতিশীল প্ৰত্যন্তৰ দশা ফলাফল (Dynamic Pratyantar Prediction)
# ═══════════════════════════════════════════════════════════════

def get_pratyantar_prediction(prat_eng: str, antar_eng: str, planet_degrees: dict, lagna_sign_index: int, age: int = 41) -> str:
    """প্ৰত্যন্তৰ দশাৰ গতিশীল আৰু নিয়ম আধাৰিত ৩টা লাইনৰ ফলাফল"""
    if "ৰবি" in planet_degrees or "Sun" not in planet_degrees:
        planet_degrees = convert_planet_degrees_to_en(planet_degrees)

    prat_pd = get_planet_details(prat_eng, planet_degrees, lagna_sign_index)
    antar_pd = get_planet_details(antar_eng, planet_degrees, lagna_sign_index) if antar_eng else None
    
    if prat_pd is None:
        return f"\nবৰ্তমান প্ৰত্যন্তৰ দশাৰ তথ্য উপলব্ধ নহয়।"

    prat_asm = prat_pd["name_asm"]
    antar_asm = antar_pd["name_asm"] if antar_pd else ""

    malefics = ["Rahu", "Ketu", "Saturn", "Mars", "Sun"]
    is_prat_malefic = (prat_eng in malefics) or (prat_pd.get("nature", "নিৰপেক্ষ") == "অশুভ")
    
    is_antar_malefic = False
    if antar_pd:
        is_antar_malefic = (antar_eng in malefics) or (antar_pd.get("nature", "নিৰপেক্ষ") == "অশুভ")

    result = f"\n▶ {prat_asm} প্ৰত্যন্তৰ দশাৰ প্ৰভাৱ:\n\n"
    
    # লাইন ১: অশুভ/শুভ অৱস্থানৰ প্ৰভাৱ
    if is_prat_malefic:
        line1 = f"• যিহেতু {prat_asm} এটা অশুভ গ্ৰহ আৰু ই যিটো স্থানত ({prat_pd['house']} নং ঘৰত) বহি আছে, সেই স্থানটোৰ ক্ষেত্ৰতো হানি বা ক্ষতি হ'ব।"
    else:
        line1 = f"• যিহেতু {prat_asm} এটা শুভ গ্ৰহ আৰু ই যিটো স্থানত ({prat_pd['house']} নং ঘৰত) বহি আছে, সেই স্থানটোৰ ক্ষেত্ৰতো শুভ ফল লাভ কৰিব।"
        
    # লাইন ২: বিশেষ নিয়ম (Special rules for PD)
    l2_parts = []
    if is_antar_malefic and is_prat_malefic:
        l2_parts.append("অন্তৰদশাপতি অশুভ গ্ৰহ আৰু প্ৰত্যন্তৰ দশাপতিও অশুভ গ্ৰহ হোৱা বাবে এইটো অশুভ সময় হ'ব, মানসিক অশান্তি, স্বাস্হ্যজনিত সমস্যা, কষ্ট আৰু পৰিশ্ৰম, বিবাদ ইত্যাদি হোৱাৰ সম্ভাবনা থাকে।")
        
    owned = prat_pd["owned_houses"]
    if 3 in owned:
        l2_parts.append("৩য় পতি গ্ৰহৰ প্ৰত্যন্তৰ দশাত কষ্ট আৰু পৰিশ্ৰমৰ সময়, যাত্ৰাও অধিক কৰিব লাগিব পাৰে আৰু স্বাস্হ্যজনিত সমস্যাও আহি পৰিব পাৰে।")
    if 6 in owned:
        l2_parts.append("৬ষ্ঠ পতি গ্ৰহৰ প্ৰত্যন্তৰ দশাত কষ্ট আৰু পৰিশ্ৰমৰ সময়, যাত্ৰাও অধিক কৰিব লাগিব পাৰে, খৰচ বৃদ্ধি হব, স্বাস্হ্যজনিত সমস্যাও আহি পৰিব পাৰে।")
    if 12 in owned:
        l2_parts.append("১২শ পতি গ্ৰহৰ প্ৰত্যন্তৰ দশাত কষ্ট আৰু পৰিশ্ৰমৰ সময়, যাত্ৰাও অধিক কৰিব লাগিব পাৰে লগতে ব্যয়ৰ মাত্ৰাও বৃদ্ধি পাব।")
        
    if prat_eng == "Venus":
        l2_parts.append("শুক্ৰ গ্ৰহৰ প্ৰত্যন্তৰ দশাৰ সময়চোৱাত নতুন বস্তু হোৱাৰ যোগ থাকে।")
        
    line2 = "• " + " ".join(l2_parts) if l2_parts else f"• ই {', '.join([str(h)+' নং' for h in owned])} ঘৰৰ অধিপতি হিচাপে সেই স্থানৰ ফল প্ৰদান কৰিব।"
    if not l2_parts and not owned:
         line2 = "• ই এটা ছায়া গ্ৰহ হোৱাৰ বাবে নিজৰ অৱস্থান আৰু সংযুতি অনুসৰি ফল দিব।"
         
    # লাইন ৩: বয়স, কাৰকত্ব আৰু তীক্ষ্ণ নক্ষত্ৰৰ প্ৰভাৱ
    age_focus = "বিদ্যা আৰু স্বাস্থ্য" if age < 25 else "কৰ্ম, স্বাস্থ্য, উন্নতি আৰু বিবাহ"
    line3 = f"• আপোনাৰ বয়স অনুসৰি এই সময়ত মূলত: {age_focus}ৰ ওপৰত প্ৰভাৱ পৰিব। "
    
    if prat_pd["is_tikshna"] and antar_pd:
        antar_owned_str = ", ".join([f"{h} নং" for h in antar_pd["owned_houses"]]) if antar_pd["owned_houses"] else "অৱস্থিত"
        line3 += f"লগতে, তীক্ষ্ণ নক্ষত্ৰৰ প্ৰত্যন্তৰ দশাত গ্ৰহটোৰ কাৰকতা ({prat_pd['karaka'].split(',')[0]}) আৰু অন্তৰদশাপতিৰ অধিপতি স্থানবোৰকো ({antar_owned_str} ঘৰ) অশুভ ফল প্ৰদান কৰিব।"
    else:
        line3 += f"লগতে গ্ৰহটোৰ কাৰকতা ({prat_pd['karaka'].split(',')[0]}) সম্বন্ধীয় ফল দেখা যাব।"

    return result + f"{line1}\n{line2}\n{line3}\n"

# ═══════════════════════════════════════════════════════════════
# সম্পূৰ্ণ দশা ফলাফল (মহাদশা + অন্তৰ্দশা + প্ৰত্যন্তৰ)
# ═══════════════════════════════════════════════════════════════

def get_full_dasha_prediction(
    maha_eng: str, antar_eng: str, prat_eng: str,
    planet_degrees: dict, lagna_sign_index: int, age: int = 41
) -> str:
    if "ৰবি" in planet_degrees or "Sun" not in planet_degrees:
        planet_degrees = convert_planet_degrees_to_en(planet_degrees)

    maha_asm = get_asm_planet(maha_eng)
    antar_asm = get_asm_planet(antar_eng) if antar_eng else ""
    prat_asm = get_asm_planet(prat_eng) if prat_eng else ""

    result = "=" * 55 + "\n"
    result += "               বৰ্তমানৰ দশা আৰু ফলাফল বিশ্লেষণ               \n"
    result += "=" * 55 + "\n\n"

    result += f"বৰ্তমান {maha_asm}ৰ মহাদশা"
    if antar_eng:
        result += f"ত {antar_asm}ৰ অন্তৰ্দশা"
    if prat_eng:
        result += f" আৰু {prat_asm}ৰ প্ৰত্যন্তৰ দশা"
    result += " চলি আছে।\n\n"

    if antar_eng:
        result += get_maha_antar_prediction(maha_eng, antar_eng, planet_degrees, lagna_sign_index)
    else:
        result += f"{maha_asm}ৰ মহাদশাই জাতকৰ জীৱনলৈ এক নতুন দিশ কঢ়িয়াই আনে। সম্পূৰ্ণ ফলাফল জানিবলৈ অন্তৰ্দশা নিৰ্বাচন কৰক।\n"

    if prat_eng:
        result += get_pratyantar_prediction(prat_eng, antar_eng, planet_degrees, lagna_sign_index, age)

    return result

# ═══════════════════════════════════════════════════════════════
# সকলো মহাদশা-অন্তৰ্দশাৰ ফলাফল
# ═══════════════════════════════════════════════════════════════

def get_all_maha_antar_predictions(dasa_data: list, planet_degrees: dict, lagna_sign_index: int) -> list:
    if "ৰবি" in planet_degrees or "Sun" not in planet_degrees:
        planet_degrees = convert_planet_degrees_to_en(planet_degrees)

    all_predictions = []

    for md in dasa_data:
        maha_eng = get_eng_planet(md["md_lord"])
        maha_asm = get_asm_planet(maha_eng)

        for ad in md.get("sub_dasas", []):
            antar_eng = get_eng_planet(ad["ad_lord"])
            antar_asm = get_asm_planet(antar_eng)

            prediction = get_maha_antar_prediction(
                maha_eng, antar_eng, planet_degrees, lagna_sign_index
            )

            all_predictions.append({
                "maha_lord": md["md_lord"],
                "maha_eng": maha_eng,
                "maha_asm": maha_asm,
                "antar_lord": ad["ad_lord"],
                "antar_eng": antar_eng,
                "antar_asm": antar_asm,
                "start": ad["start"],
                "end": ad["end"],
                "prediction": prediction,
            })

    return all_predictions