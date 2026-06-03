"""
ধ্ৰুৱতৰা AI - অংক জ্যোতিষ (Numerology) ইঞ্জিন
============================================================
Complete numerology calculations:
- Lo Shu Grid
- Mulyanka (Psychic Number)
- Bhagyanka (Destiny Number)
- Namanka (Name Number)
- Angel Number
- Missing/Present Numbers Analysis
- Name Compatibility & Correction
- Varsha Phal (Yearly Predictions)
- Pratikar (Remedies)
"""

import re
from datetime import datetime

# ─── Assamese Number Names ──────────────────────────────────────
ASM_NUMBERS = {
    1: "এক", 2: "দুই", 3: "তিনি", 4: "চাৰি", 5: "পাঁচ",
    6: "ছয়", 7: "সাত", 8: "আঠ", 9: "ন", 0: "শূন্য"
}

# ─── Assamese Planet Names for Numbers ──────────────────────────
NUMBER_PLANETS = {
    1: "ৰবি (সূৰ্য)", 2: "চন্দ্ৰ (চন্দ্ৰ)", 3: "বৃহস্পতি (গুৰু)",
    4: "ৰাহু (ৰাহু)", 5: "বুধ (বুধ)", 6: "শুক্ৰ (শুক্ৰ)",
    7: "কেতু (কেতু)", 8: "শনি (শনি)", 9: "মংগল (মঙ্গল)"
}

NUMBER_PLANETS_SHORT = {
    1: "ৰবি", 2: "চন্দ্ৰ", 3: "বৃহস্পতি", 4: "ৰাহু",
    5: "বুধ", 6: "শুক্ৰ", 7: "কেতু", 8: "শনি", 9: "মংগল"
}

# ─── Lo Shu Grid Positions ──────────────────────────────────────
# Standard Lo Shu magic square layout:
# 4 9 2
# 3 5 7
# 8 1 6
LO_SHU_GRID = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6]
]

# ─── Lo Shu Grid Planes (8 Planes/Yogas) ───────────────────────
# Each plane is a row, column, or diagonal. Complete plane = all 3 numbers present.
LO_SHU_PLANES = {
    "mental": {
        "name": "মানসিক যোগ (Mental Plane)",
        "name_short": "মানসিক যোগ",
        "cells": [(0,0), (0,1), (0,2)],  # 4-9-2 (top row)
        "numbers": [4, 9, 2],
        "description": "এই যোগটো গ্ৰীডৰ একেবাৰে ওপৰৰ শাৰীত থাকে আৰু ই মানুহৰ মগজু, স্মৃতিশক্তি আৰু বৌদ্ধিক ক্ষমতাক প্ৰতিনিধিত্ব কৰে।",
        "personality": "এওঁলোকৰ বিশ্লেষণাত্মক ক্ষমতা (Analytical Skills) অসাধাৰণ। যিকোনো কথাৰ গভীৰতালৈ যোৱাৰ প্ৰৱণতা থাকে। এওঁলোক অতি যুক্তিবাদী আৰু সহজে কাকো বিশ্বাস নকৰে।",
        "career": "গৱেষণা, আইন (উকালতি), আই.টি (IT), জ্যোতিষ বিজ্ঞান, চাৰ্টাৰ্ড একাউণ্টেণ্ট (CA) বা যিকোনো পেচা য'ত মগজুৰ বেছি প্ৰয়োজন হয়।",
        "bad_effects": "কেতিয়াবা অত্যাধিক চিন্তা কৰা (Overthinking) স্বভাৱৰ বাবে মানসিক চাপ বা হতাশাত ভুগিব পাৰে। লগতে আনক সহজে বিশ্বাস নকৰা বা সন্দেহ কৰা প্ৰৱণতা থাকিব পাৰে।"
    },
    "emotional": {
        "name": "আৱেগিক যোগ (Emotional Plane)",
        "name_short": "আৱেগিক যোগ",
        "cells": [(1,0), (1,1), (1,2)],  # 3-5-7 (middle row)
        "numbers": [3, 5, 7],
        "description": "এই যোগটো গ্ৰীডৰ মাজৰ শাৰীত থাকে আৰু ই মানুহৰ হৃদয়, আৱেগ, আৰু আধ্যাত্মিকতাক বুজায়।",
        "personality": "এই যোগ থকা ব্যক্তিসকল অতি দয়ালু, মানৱদৰদী আৰু সমাজপ্ৰিয় হয়। এওঁলোকৰ ইনটুইচন (Intuition) বা পূৰ্বাভাস পোৱাৰ ক্ষমতা বহুত প্ৰবল।",
        "career": "সমাজ সেৱা, চিকিৎসা ক্ষেত্ৰ (Healing), শিক্ষকতা, মনোবিজ্ঞান, আৰু জনসংযোগ (Public Relations)।",
        "bad_effects": "অত্যাধিক আৱেগিক হোৱাৰ ফলত মানুহে ইয়াৰ সুযোগ ল'ব পাৰে। আৱেগৰ বশৱৰ্তী হৈ কেতিয়াবা ভুল সিদ্ধান্ত লৈ জীৱনত প্ৰতাৰিত হোৱাৰ সম্ভাৱনা থাকে।"
    },
    "practical": {
        "name": "ব্যৱহাৰিক যোগ (Practical Plane)",
        "name_short": "ব্যৱহাৰিক যোগ",
        "cells": [(2,0), (2,1), (2,2)],  # 8-1-6 (bottom row)
        "numbers": [8, 1, 6],
        "description": "এইটো গ্ৰীডৰ একেবাৰে তলৰ শাৰী আৰু ই ভৌতিক পৃথিৱী, পৰিশ্ৰম, আৰু ব্যৱসায়িক বুদ্ধিক বুজায়।",
        "personality": "এওঁলোক সপোনতকৈ বাস্তৱত বেছি বিশ্বাস কৰে। কঠোৰ পৰিশ্ৰম কৰিবলৈ কেতিয়াও কুণ্ঠাবোধ নকৰে। এওঁলোকৰ ব্যৱস্থাপনা (Management) ক্ষমতা অতি সুন্দৰ।",
        "career": "ব্যৱসায়, উদ্যোগ (Manufacturing), বেংকিং, বিত্তীয় প্ৰতিষ্ঠান, আৰু যিকোনো পৰিচালনামূলক কাম।",
        "bad_effects": "কেতিয়াবা এওঁলোক অত্যাধিক ভৌতিকতাবাদী (Materialistic) হৈ পৰে। কেৱল টকা-পইচাৰ পাছত দৌৰাৰ ফলত পাৰিবাৰিক বা মানসিক শান্তি বিঘ্নিত হ'ব পাৰে।"
    },
    "thought": {
        "name": "চিন্তা বা দৃষ্টিভংগীৰ যোগ (Thought Plane)",
        "name_short": "চিন্তা যোগ",
        "cells": [(0,0), (1,0), (2,0)],  # 4-3-8 (left column)
        "numbers": [4, 3, 8],
        "description": "এইটো গ্ৰীডৰ বাওঁফালৰ থিয় শাৰী। ই পৰিকল্পনা, কৌশল আৰু ৰাজনৈতিক বুদ্ধিক বুজায়।",
        "personality": "এওঁলোকৰ মনত সদায় নতুন আৰু ডাঙৰ পৰিকল্পনা থাকে (Visionary)। ভৱিষ্যতৰ কথা আগতীয়াকৈ ভাবি কাম কৰিব পাৰে।",
        "career": "ৰাজনীতি, আৰ্কিটেক্ট (Architect), ইভেণ্ট মেনেজমেন্ট, আৰু যিকোনো প্ৰজেক্ট প্লেনিং।",
        "bad_effects": "কেৱল চিন্তা বা পৰিকল্পনা কৰাতে ব্যস্ত থাকে, কিন্তু বাস্তৱত সেইবোৰ কামত ৰূপায়ণ কৰাত (Execution) পিছ পৰি ৰয়।"
    },
    "willpower": {
        "name": "ইচ্ছা শক্তিৰ যোগ (Willpower Plane)",
        "name_short": "ইচ্ছা শক্তি যোগ",
        "cells": [(0,1), (1,1), (2,1)],  # 9-5-1 (middle column)
        "numbers": [9, 5, 1],
        "description": "এইটো গ্ৰীডৰ মাজৰ থিয় শাৰী। ই সফলতা, দৃঢ়তা আৰু ইচ্ছাশক্তিক বুজায়।",
        "personality": "এই যোগ থকাসকলে জীৱনত বহু বাধা-বিঘিনি পোৱাৰ পিছতো হাৰ নামানে। এওঁলোকৰ আত্মবিশ্বাস ইমানেই বেছি থাকে যে যিকোনো শূন্য অৱস্থাৰ পৰাও নিজকে গঢ়ি তুলিব পাৰে।",
        "career": "প্ৰতিৰক্ষা (Army/Police), নেতৃত্বমূলক পদৱী, নিজা ব্যৱসায় (Entrepreneurship)।",
        "bad_effects": "নিজৰ কথাত অটল থকাৰ বাবে কেতিয়াবা একগুঁইয়া (Stubborn) আৰু অহংকাৰী হৈ পৰিব পাৰে। আনৰ পৰামৰ্শ সহজে গ্ৰহণ কৰিব নিবিচাৰে।"
    },
    "action": {
        "name": "কৰ্ম যোগ (Action Plane)",
        "name_short": "কৰ্ম যোগ",
        "cells": [(0,2), (1,2), (2,2)],  # 2-7-6 (right column)
        "numbers": [2, 7, 6],
        "description": "এইটো গ্ৰীডৰ সোঁফালৰ থিয় শাৰী। ই শাৰীৰিক শক্তি, সক্ৰিয়তা আৰু কাৰ্যকৰী ক্ষমতাক বুজায়।",
        "personality": "এওঁলোক অতি সক্ৰিয় (Energetic)। বহি থকাতকৈ যিকোনো কাম তৎক্ষণাত কৰাত বিশ্বাসী। নতুন পৰিৱেশৰ সৈতে সহজে মিলি যাব পাৰে।",
        "career": "ক্ৰীড়া জগত (Sports), আৰক্ষী, জৰুৰীকালীন সেৱা, ভ্ৰমণ সম্পৰ্কীয় কাম, আৰু য'ত শাৰীৰিক শ্ৰমৰ প্ৰয়োজন।",
        "bad_effects": "আগপাছ নভবাকৈ বা খৰখেদাকৈ কাম কৰাৰ অভ্যাসৰ (Impulsive action) ফলত কেতিয়াবা বিপদত পৰাৰ সম্ভাৱনা থাকে।"
    },
    "golden": {
        "name": "সোণালী যোগ (Golden Plane)",
        "name_short": "সোণালী যোগ",
        "cells": [(0,0), (1,1), (2,2)],  # 4-5-6 (diagonal \)
        "numbers": [4, 5, 6],
        "description": "এইটো এটা কোণীয়া (Diagonal) যোগ। ই ল' চু গ্ৰীডৰ সৰ্বশ্ৰেষ্ঠ যোগ। ইয়াক 'ৰাজযোগ' বুলি কোৱা হয়।",
        "personality": "এই ব্যক্তিসকলে জীৱনত সহজে সফলতা লাভ কৰে। এওঁলোকৰ জীৱনত ধন-সম্পত্তি, মান-সন্মান আৰু সুস্বাস্থ্যৰ এক সুন্দৰ ভাৰসাম্য থাকে। মানুহে এওঁলোকক সহজে অনুসৰণ কৰে। জীৱনৰ আধাতকৈ বেছি সময় এওঁলোকে আৰাম আৰু বিলাসিতাৰে কটায়।",
        "career": "উচ্চ পৰ্যায়ৰ ব্যৱস্থাপনা, ৰাজনীতি, চেলিব্ৰিটি, বা যিকোনো ক্ষেত্ৰত শীৰ্ষস্থানীয় নেতৃত্ব।",
        "bad_effects": "সফলতা সহজে পোৱাৰ বাবে কেতিয়াবা অতিৰিক্ত আত্মবিশ্বাস বা অহংকাৰৰ সৃষ্টি হ'ব পাৰে, যিয়ে পাছলৈ পতন মাতি আনিব পাৰে।"
    },
    "silver": {
        "name": "ৰূপালী যোগ (Silver Plane)",
        "name_short": "ৰূপালী যোগ",
        "cells": [(0,2), (1,1), (2,0)],  # 2-5-8 (diagonal /)
        "numbers": [2, 5, 8],
        "description": "এইটো আনটো কোণীয়া যোগ। ইয়াত থকা তিনিওটা সংখ্যা (২, ৫, ৮) 'পৃথিৱী তত্ত্ব'ৰ (Earth Element)। ইয়াক 'Real Estate Yoga' বুলি কোৱা হয়।",
        "personality": "এই ব্যক্তিসকল মাটিৰ সৈতে গভীৰভাৱে সংযুক্ত। এওঁলোক অতি ধৈৰ্য্যশীল আৰু বিশ্বাসযোগ্য। এই যোগ থকা ব্যক্তিয়ে জীৱনত বহুত মাটি, ঘৰ আৰু স্থাৱৰ সম্পত্তিৰ গৰাকী হয়।",
        "career": "ৰিয়েল এষ্টেট, নিৰ্মাণ উদ্যোগ, কৃষি, মাটি-সম্পত্তি ব্যৱসায়।",
        "bad_effects": "ভৌতিক সুখ আৰু সম্পত্তিৰ প্ৰতি থকা অত্যাধিক লালসাই মানসিক শান্তি আৰু পাৰিবাৰিক সম্পৰ্কত ফাট মেলাব পাৰে।"
    }
}

# ─── Number Meanings (Assamese) ─────────────────────────────────
NUMBER_MEANINGS = {
    1: {
        "positive": "নেতৃত্ব, স্বাধীনতা, সৃষ্টিশীলতা, আত্মবিশ্বাস, সাহস",
        "negative": "অহংকাৰ, একগুঁয়েমি, আধিপত্যবাদী মনোভাৱ",
        "remedy": "সূৰ্যক জল অৰ্পণ কৰক, ৰবিবাৰে ব্ৰত ৰাখক, তাম্ৰ ধাতু ব্যৱহাৰ কৰক",
        "gem": "মাণিক্য (Ruby)",
        "rudraksha": "একমুখী ৰুদ্ৰাক্ষ",
        "mantra": "ওঁ ঘৃণি সূৰ্যায় নমঃ"
    },
    2: {
        "positive": "সংবেদনশীলতা, সহযোগিতা, কূটনীতি, ধৈৰ্য্য, প্ৰেম",
        "negative": "অতিৰিক্ত আবেগিক, অনিশ্চয়তা, নিৰ্ভৰশীলতা",
        "remedy": "চন্দ্ৰক জল অৰ্পণ কৰক, সোমবাৰে ব্ৰত ৰাখক, মুক্তা ধাৰণ কৰক",
        "gem": "মুক্তা (Pearl)",
        "rudraksha": "দ্বিমুখী ৰুদ্ৰাক্ষ",
        "mantra": "ওঁ সোঁ সোমায় নমঃ"
    },
    3: {
        "positive": "জ্ঞান, আশাবাদ, সৃষ্টিশীলতা, যোগাযোগ, সম্প্ৰসাৰণ",
        "negative": "অপচয়, অতিৰিক্ত কথা কোৱা, একাগ্ৰতাৰ অভাৱ",
        "remedy": "বৃহস্পতিৰ উপাসনা কৰক, বৃহস্পতিবাৰে ব্ৰত ৰাখক, হালধীয়া বস্ত্ৰ ধাৰণ কৰক",
        "gem": "পোখৰাজ (Yellow Sapphire)",
        "rudraksha": "ত্ৰিমুখী ৰুদ্ৰাক্ষ",
        "mantra": "ওঁ বৃং বৃহস্পতয়ে নমঃ"
    },
    4: {
        "positive": "ব্যৱহাৰিকতা, পৰিশ্ৰম, শৃংখলা, স্থিৰতা, সংগঠন",
        "negative": "অনমনীয়তা, ৰক্ষণশীলতা, একগুঁয়েমি",
        "remedy": "ৰাহুৰ উপাসনা কৰক, শনিবাৰে ব্ৰত ৰাখক, নীলা বস্ত্ৰ ধাৰণ কৰক",
        "gem": "গোমেদ (Hessonite)",
        "rudraksha": "চতুৰ্মুখী ৰুদ্ৰাক্ষ",
        "mantra": "ওঁ ৰাং ৰাহবে নমঃ"
    },
    5: {
        "positive": "বুদ্ধিমত্তা, অভিযোজন ক্ষমতা, স্বাধীনতা, কৌতূহল, ভ্ৰমণ",
        "negative": "অস্থিৰতা, অতিৰিক্ত ইন্দ্ৰিয়াসক্তি, দায়িত্বহীনতা",
        "remedy": "বুধৰ উপাসনা কৰক, বুধবাৰে ব্ৰত ৰাখক, সেউজীয়া বস্ত্ৰ ধাৰণ কৰক",
        "gem": "পান্না (Emerald)",
        "rudraksha": "পঞ্চমুখী ৰুদ্ৰাক্ষ",
        "mantra": "ওঁ বুং বুধায় নমঃ"
    },
    6: {
        "positive": "প্ৰেম, সৌন্দৰ্য্য, বিলাসিতা, কলা, সম্প্ৰীতি, দায়িত্বশীলতা",
        "negative": "অতিৰিক্ত ভোগবাদী, অহংকাৰ, ঈৰ্ষা",
        "remedy": "শুক্ৰৰ উপাসনা কৰক, শুক্ৰবাৰে ব্ৰত ৰাখক, শ্বেত বস্ত্ৰ ধাৰণ কৰক",
        "gem": "হীৰা (Diamond)",
        "rudraksha": "ষষ্ঠমুখী ৰুদ্ৰাক্ষ",
        "mantra": "ওঁ শুং শুক্ৰায় নমঃ"
    },
    7: {
        "positive": "আধ্যাত্মিকতা, অন্তৰ্দৃষ্টি, গৱেষণা, দাৰ্শনিকতা, বিশ্লেষণ",
        "negative": "একাকীত্ব, অতিৰিক্ত সন্দেহপ্ৰৱণতা, অস্থিৰতা",
        "remedy": "কেতুৰ উপাসনা কৰক, গণেশ পূজা কৰক, কেতু মন্ত্ৰ জপ কৰক",
        "gem": "লহসুনীয়া (Cat's Eye)",
        "rudraksha": "সপ্তমুখী ৰুদ্ৰাক্ষ",
        "mantra": "ওঁ ক্ৰাং কেতবে নমঃ"
    },
    8: {
        "positive": "কৰ্মঠতা, উচ্চাকাংক্ষা, শক্তি, ধন, সফলতা, ন্যায়পৰায়ণতা",
        "negative": "অতিৰিক্ত বস্তুবাদী, নিষ্ঠুৰতা, হতাশা",
        "remedy": "শনিৰ উপাসনা কৰক, শনিবাৰে ব্ৰত ৰাখক, নীলা বস্ত্ৰ ধাৰণ কৰক",
        "gem": "নীলম (Blue Sapphire)",
        "rudraksha": "অষ্টমুখী ৰুদ্ৰাক্ষ",
        "mantra": "ওঁ শং শনৈশ্চৰায় নমঃ"
    },
    9: {
        "positive": "সাহস, শক্তি, নেতৃত্ব, কৰ্মঠতা, মানৱতা, দয়া",
        "negative": "আক্ৰমণাত্মকতা, অহংকাৰ, অস্থিৰতা, দুৰ্ঘটনা প্ৰৱণতা",
        "remedy": "মংগলৰ উপাসনা কৰক, মঙ্গলবাৰে ব্ৰত ৰাখক, ৰঙা বস্ত্ৰ ধাৰণ কৰক",
        "gem": "পোৱাল (Coral)",
        "rudraksha": "নৱমুখী ৰুদ্ৰাক্ষ",
        "mantra": "ওঁ অং অঙ্গাৰকায় নমঃ"
    }
}

# ─── Angel Numbers ──────────────────────────────────────────────
ANGEL_NUMBER_MEANINGS = {
    111: "আপোনাৰ চিন্তাধাৰা দ্ৰুতগতিত বাস্তৱায়িত হৈছে। আপোনাৰ ইচ্ছাৰ প্ৰতি সাৱধান থাকক।",
    222: "আপোনাৰ জীৱনত ভাৰসাম্য আৰু সম্প্ৰীতি আহি আছে। ধৈৰ্য্য ধৰি আগবাঢ়ক।",
    333: "আপোনাৰ আধ্যাত্মিক গুৰুসকলে আপোনাক সহায় কৰি আছে। আপুনি একেলগে নহয়।",
    444: "আপোনাৰ ৰক্ষক ফৰিস্তাসকল আপোনাৰ সৈতে আছে। আপুনি সুৰক্ষিত।",
    555: "আপোনাৰ জীৱনত বৃহৎ পৰিৱৰ্তন আহি আছে। এই পৰিৱৰ্তনক স্বাগতম জনাওক।",
    666: "আপোনাৰ চিন্তাধাৰাক পুনৰ ভাৰসাম্যলৈ আনক। বস্তুবাদী চিন্তাৰ পৰা আঁতৰি আহক।",
    777: "আপুনি সঠিক পথত আছে। আপোনাৰ প্ৰচেষ্টাৰ বাবে অভিনন্দন।",
    888: "আপোনাৰ জীৱনত প্ৰাচুৰ্য্য আৰু সফলতা আহি আছে।",
    999: "এটা অধ্যায়ৰ সমাপ্তি আৰু নতুন অধ্যায়ৰ আৰম্ভণি।",
    1111: "নতুন আৰম্ভণিৰ সময়। আপোনাৰ সপোনবোৰ বাস্তৱায়িত হ'ব।",
    1212: "আপোনাৰ বিশ্বাস আৰু ধৈৰ্য্যই আপোনাক সফলতাৰ দিশে লৈ যাব।",
    1234: "আপোনাৰ জীৱনত ক্ৰমান্বয়ে উন্নতি হৈ আছে। ধাপে ধাপে আগবাঢ়ক।"
}

# ─── Alphabet to Number Mapping (Chaldean System) ───────────────
CHALDEAN_MAP = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 8, 'g': 3, 'h': 5,
    'i': 1, 'j': 1, 'k': 2, 'l': 3, 'm': 4, 'n': 5, 'o': 7, 'p': 8,
    'q': 1, 'r': 2, 's': 3, 't': 4, 'u': 6, 'v': 6, 'w': 6, 'x': 5,
    'y': 1, 'z': 7
}

# ─── Assamese/Bengali Alphabet to Number Mapping ────────────────
ASSAMESE_CHALDEAN = {
    'অ': 1, 'আ': 1, 'ই': 1, 'ঈ': 1, 'উ': 6, 'ঊ': 6, 'ঋ': 2, 'এ': 5,
    'ঐ': 5, 'ও': 7, 'ঔ': 7,
    'ক': 2, 'খ': 2, 'গ': 3, 'ঘ': 3, 'ঙ': 5,
    'চ': 3, 'ছ': 3, 'জ': 1, 'ঝ': 1, 'ঞ': 5,
    'ট': 4, 'ঠ': 4, 'ড': 4, 'ঢ': 4, 'ণ': 5,
    'ত': 4, 'থ': 4, 'দ': 4, 'ধ': 4, 'ন': 5,
    'প': 8, 'ফ': 8, 'ব': 2, 'ভ': 2, 'ম': 4,
    'য': 1, 'ৰ': 2, 'ল': 3, 'ৱ': 6,
    'শ': 3, 'ষ': 3, 'স': 3, 'হ': 5,
    'ক্ষ': 2, 'ত্ৰ': 4, 'জ্ঞ': 1, 'শ্ৰ': 3,
    'ং': 5, 'ঃ': 5, 'ঁ': 5, 'া': 1, 'ি': 1, 'ী': 1,
    'ু': 6, 'ূ': 6, 'ৃ': 2, 'ে': 5, 'ৈ': 5, 'ো': 7, 'ৌ': 7
}

# ─── Varsha Phal (Yearly Predictions) ───────────────────────────
VARSHA_PHAL_TEMPLATES = {
    1: "এই বৰ্ষটো নতুন আৰম্ভণিৰ বাবে অত্যন্ত শুভ। আপোনাৰ নেতৃত্ব ক্ষমতা বৃদ্ধি পাব। কৰ্মক্ষেত্ৰত উন্নতি আৰু নতুন সুযোগ আহিব। স্বাস্থ্যৰ প্ৰতি সচেতন থাকক।",
    2: "এই বৰ্ষটো সম্পৰ্ক আৰু সহযোগিতাৰ ওপৰত গুৰুত্ব দিব। ধৈৰ্য্য আৰু কূটনীতিৰ দ্বাৰা সফলতা লাভ কৰিব। আবেগিকভাৱে সংবেদনশীল সময়।",
    3: "এই বৰ্ষটো জ্ঞান আৰু সৃষ্টিশীলতাৰ বাবে শুভ। শিক্ষা, কলা, আৰু যোগাযোগৰ ক্ষেত্ৰত উন্নতি হ'ব। ভ্ৰমণৰ সম্ভাৱনা আছে।",
    4: "এই বৰ্ষটো পৰিশ্ৰম আৰু শৃংখলাৰ ওপৰত গুৰুত্ব দিব। স্থিৰতা আৰু সংগঠনৰ দ্বাৰা সফলতা লাভ কৰিব। ধৈৰ্য্য ধৰি কাম কৰক।",
    5: "এই বৰ্ষটো পৰিৱৰ্তন আৰু নতুনত্বৰ বাবে শুভ। বুদ্ধিমত্তা আৰু অভিযোজন ক্ষমতাৰ দ্বাৰা সফলতা লাভ কৰিব। অস্থিৰতাৰ পৰা সাৱধান থাকক।",
    6: "এই বৰ্ষটো প্ৰেম, সৌন্দৰ্য্য আৰু বিলাসিতাৰ বাবে শুভ। পাৰিবাৰিক জীৱনত সুখ-শান্তি বৃদ্ধি পাব। আৰ্থিক দিশত উন্নতি হ'ব।",
    7: "এই বৰ্ষটো আধ্যাত্মিকতা আৰু অন্তৰ্দৃষ্টিৰ বাবে শুভ। গৱেষণা আৰু বিশ্লেষণৰ ক্ষেত্ৰত সফলতা লাভ কৰিব। একাকীত্বৰ পৰা সাৱধান থাকক।",
    8: "এই বৰ্ষটো কৰ্মঠতা আৰু উচ্চাকাংক্ষাৰ বাবে শুভ। ধন আৰু সফলতা লাভৰ সম্ভাৱনা আছে। ন্যায়পৰায়ণতা বজাই ৰাখক।",
    9: "এই বৰ্ষটো সাহস আৰু শক্তিৰ বাবে শুভ। নতুন কাম আৰম্ভ কৰাৰ বাবে উপযুক্ত সময়। মানৱতা আৰু দয়াৰ কাম কৰক।"
}

# ─── Name Correction Suggestions ────────────────────────────────
NAME_CORRECTION_SUGGESTIONS = {
  1: "আপোনাৰ নামৰ বৰ্ণবোৰৰ মুঠ যোগফল 10, 19, 28, 37, 46, 55, 64, 73, 82 বা 91 কৰিলে শুভ ফল পাব।",
    2: "আপোনাৰ নামৰ বৰ্ণবোৰৰ মুঠ যোগফল 11, 20, 29, 38, 47, 56, 65, 74, 83 বা 92 কৰিলে শুভ ফল পাব।",
    3: "আপোনাৰ নামৰ বৰ্ণবোৰৰ মুঠ যোগফল 12, 21, 30, 39, 48, 57, 66, 75, 84 বা 93 কৰিলে শুভ ফল পাব।",
    4: "আপোনাৰ নামৰ বৰ্ণবোৰৰ মুঠ যোগফল 13, 22, 31, 40, 49, 58, 67, 76, 85 বা 94 কৰিলে শুভ ফল পাব।",
    5: "আপোনাৰ নামৰ বৰ্ণবোৰৰ মুঠ যোগফল 14, 23, 32, 41, 50, 59, 68, 77, 86 বা 95 কৰিলে শুভ ফল পাব।",
    6: "আপোনাৰ নামৰ বৰ্ণবোৰৰ মুঠ যোগফল 15, 24, 33, 42, 51, 60, 69, 78, 87 বা 96 কৰিলে শুভ ফল পাব।",
    7: "আপোনাৰ নামৰ বৰ্ণবোৰৰ মুঠ যোগফল 16, 25, 34, 43, 52, 61, 70, 79, 88 বা 97 কৰিলে শুভ ফল পাব।",
    8: "আপোনাৰ নামৰ বৰ্ণবোৰৰ মুঠ যোগফল 17, 26, 35, 44, 53, 62, 71, 80, 89 বা 98 কৰিলে শুভ ফল পাব।",
    9: "আপোনাৰ নামৰ বৰ্ণবোৰৰ মুঠ যোগফল 18, 27, 36, 45, 54, 63, 72, 81, 90 বা 99 কৰিলে শুভ ফল পাব।"
}


# ═══════════════════════════════════════════════════════════════════
#  CORE CALCULATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def reduce_to_single_digit(num: int) -> int:
    """Reduce a number to a single digit (1-9)."""
    while num > 9:
        num = sum(int(d) for d in str(num))
    return num


def reduce_to_master(num: int) -> int:
    """Reduce to single digit, but preserve 11, 22, 33 as master numbers."""
    if num in (11, 22, 33):
        return num
    return reduce_to_single_digit(num)


def get_chaldean_value(text: str) -> int:
    """Calculate Chaldean numerology value for a given text (English)."""
    total = 0
    for char in text.lower():
        if char in CHALDEAN_MAP:
            total += CHALDEAN_MAP[char]
    return total


def get_assamese_chaldean_value(text: str) -> int:
    """Calculate Chaldean numerology value for Assamese text."""
    total = 0
    for char in text:
        if char in ASSAMESE_CHALDEAN:
            total += ASSAMESE_CHALDEAN[char]
    return total


def calculate_mulyanka(dob: str) -> dict:
    """
    Calculate Mulyanka (Psychic/Radical Number) from date of birth.
    Mulyanka = day of birth reduced to single digit.
    """
    try:
        day = int(dob.split('-')[2])
    except (ValueError, IndexError):
        return {"value": 0, "description": "গণনা কৰিব পৰা নগল"}

    value = reduce_to_single_digit(day)
    planet = NUMBER_PLANETS.get(value, "")
    planet_short = NUMBER_PLANETS_SHORT.get(value, "")

    description = f"আপোনাৰ মূল্যাংক {value} ({planet})। এই সংখ্যাই আপোনাৰ ব্যক্তিত্ব, চিন্তাধাৰা আৰু মানসিক প্ৰৱণতা প্ৰকাশ কৰে। {NUMBER_MEANINGS.get(value, {}).get('positive', '')}"

    return {
        "value": value,
        "planet": planet,
        "planet_short": planet_short,
        "description": description,
        "positive": NUMBER_MEANINGS.get(value, {}).get('positive', ''),
        "negative": NUMBER_MEANINGS.get(value, {}).get('negative', '')
    }


def calculate_bhagyanka(dob: str) -> dict:
    """
    Calculate Bhagyanka (Destiny/Life Path Number) from full date of birth.
    Bhagyanka = sum of all digits in DOB reduced to single digit.
    """
    try:
        digits = ''.join(dob.split('-'))
        total = sum(int(d) for d in digits)
    except (ValueError, IndexError):
        return {"value": 0, "description": "গণনা কৰিব পৰা নগল"}

    value = reduce_to_single_digit(total)
    planet = NUMBER_PLANETS.get(value, "")
    planet_short = NUMBER_PLANETS_SHORT.get(value, "")

    description = f"আপোনাৰ ভাগ্যাংক {value} ({planet})। এই সংখ্যাই আপোনাৰ জীৱনৰ উদ্দেশ্য, ভাগ্য আৰু ভৱিষ্যতৰ দিশ নিৰ্দেশ কৰে। {NUMBER_MEANINGS.get(value, {}).get('positive', '')}"

    return {
        "value": value,
        "planet": planet,
        "planet_short": planet_short,
        "description": description,
        "positive": NUMBER_MEANINGS.get(value, {}).get('positive', ''),
        "negative": NUMBER_MEANINGS.get(value, {}).get('negative', '')
    }


def calculate_namanka(name: str) -> dict:
    """
    Calculate Namanka (Name Number) from the person's full name.
    Uses both English and Assamese Chaldean mappings.
    """
    if not name or not name.strip():
        return {"value": 0, "description": "নাম প্ৰদান কৰা হোৱা নাই"}

    # Try Assamese first, then English
    asm_total = get_assamese_chaldean_value(name)
    eng_total = get_chaldean_value(name)

    # Use whichever gives a non-zero result, prefer Assamese
    if asm_total > 0:
        total = asm_total
    else:
        total = eng_total

    if total == 0:
        return {"value": 0, "description": "গণনা কৰিব পৰা নগল"}

    value = reduce_to_single_digit(total)
    planet = NUMBER_PLANETS.get(value, "")
    planet_short = NUMBER_PLANETS_SHORT.get(value, "")

    description = f"আপোনাৰ নামাংক {value} ({planet})। এই সংখ্যাই আপোনাৰ নামৰ কম্পন আৰু সামাজিক পৰিচয় প্ৰকাশ কৰে। {NUMBER_MEANINGS.get(value, {}).get('positive', '')}"

    return {
        "value": value,
        "planet": planet,
        "planet_short": planet_short,
        "raw_total": total,
        "description": description,
        "positive": NUMBER_MEANINGS.get(value, {}).get('positive', ''),
        "negative": NUMBER_MEANINGS.get(value, {}).get('negative', '')
    }


def calculate_lo_shu_grid(dob: str, mulyanka: int = 0, bhagyanka: int = 0) -> dict:
    """
    Calculate the Lo Shu Grid from DOB + Mulyanka + Bhagyanka.
    (Namanka and Kua/Angel Number are separate compensators, NOT included in the grid.)
    Returns a 3x3 grid with repeated digit strings (e.g., "11" for two 1s).
    """
    try:
        digits = ''.join(dob.split('-'))
    except (ValueError, IndexError):
        digits = ""

    # Build the full number pool: DOB digits + Mulyanka + Bhagyanka
    full_numbers = digits + str(mulyanka) + str(bhagyanka)

    # Count occurrences of each digit 1-9
    counts = {i: 0 for i in range(1, 10)}
    for ch in full_numbers:
        if ch.isdigit():
            num = int(ch)
            if num != 0:
                counts[num] = counts.get(num, 0) + 1

    # Build the 3x3 grid in Lo Shu layout with repeated digit strings
    grid = [["", "", ""], ["", "", ""], ["", "", ""]]
    for i in range(3):
        for j in range(3):
            num = LO_SHU_GRID[i][j]
            cnt = counts.get(num, 0)
            if cnt > 0:
                grid[i][j] = str(num) * cnt  # e.g., "11" for two 1s

    missing = [n for n in range(1, 10) if counts.get(n, 0) == 0]
    present = [n for n in range(1, 10) if counts.get(n, 0) > 0]

    return {
        "grid": grid,
        "counts": counts,
        "missing": missing,
        "present": present,
        "source": "DOB + Mulyanka + Bhagyanka"
    }


def analyze_missing_numbers(missing: list) -> list:
    """Provide detailed predictions for missing numbers in Lo Shu Grid."""
    analysis = []
    for num in missing:
        planet = NUMBER_PLANETS.get(num, "")
        meaning = NUMBER_MEANINGS.get(num, {})
        analysis.append({
            "number": num,
            "planet": planet,
            "effect": f"আপোনাৰ ল' চু গ্ৰীডত {num} সংখ্যাটো অনুপস্থিত ({planet})। {meaning.get('negative', '')} এই দিশবোৰত আপুনি কিছু অসুবিধাৰ সন্মুখীন হ'ব পাৰে।",
            "remedy": meaning.get('remedy', ''),
            "gem": meaning.get('gem', ''),
            "rudraksha": meaning.get('rudraksha', ''),
            "mantra": meaning.get('mantra', '')
        })
    return analysis


def analyze_present_numbers(present: list, counts: dict) -> list:
    """Provide detailed predictions for present numbers in Lo Shu Grid."""
    analysis = []
    for num in present:
        planet = NUMBER_PLANETS.get(num, "")
        meaning = NUMBER_MEANINGS.get(num, {})
        count = counts.get(num, 0)
        intensity = "সাধাৰণ" if count == 1 else ("মধ্যম" if count == 2 else "অতি শক্তিশালী")
        analysis.append({
            "number": num,
            "planet": planet,
            "count": count,
            "intensity": intensity,
            "effect": f"আপোনাৰ ল' চু গ্ৰীডত {num} সংখ্যাটো {count} বাৰ উপস্থিত ({intensity})। {meaning.get('positive', '')} এই দিশবোৰত আপুনি স্বাভাৱিকভাৱে দক্ষ।"
        })
    return analysis


def calculate_angel_number(dob: str, name: str = "", gender: str = "male") -> dict:
    """
    Calculate Angel Number (same as Kua Number in this system).
    Formula: Sum of birth year digits → reduce → Male: 11 - reduced, Female: 4 + reduced.
    Kua 5 becomes 2 for male, 8 for female.
    """
    try:
        year_str = dob.split('-')[0]
        year_val = int(year_str)
    except (ValueError, IndexError):
        return {"value": 0, "description": "গণনা কৰিব পৰা নগল"}

    total = sum(int(d) for d in year_str)
    reduced = reduce_to_single_digit(total)

    gender_lower = gender.lower().strip()
    if gender_lower in ("male", "পুৰুষ"):
        kua = reduce_to_single_digit(11 - reduced)
        if kua == 5:
            kua = 2
    else:
        kua = reduce_to_single_digit(4 + reduced)
        if kua == 5:
            kua = 8

    # Angel number meanings based on Kua
    angel_meanings = {
        1: "আপোনাৰ এঞ্জেল সংখ্যা ১। নতুন আৰম্ভণি, নেতৃত্ব আৰু স্বাধীনতাৰ বাৰ্তা। আপোনাৰ জীৱনত নতুন সুযোগ আহি আছে।",
        2: "আপোনাৰ এঞ্জেল সংখ্যা ২। ভাৰসাম্য, সহযোগিতা আৰু ধৈৰ্য্যৰ বাৰ্তা। সম্পৰ্কত সুখ-শান্তি বৃদ্ধি পাব।",
        3: "আপোনাৰ এঞ্জেল সংখ্যা ৩। সৃষ্টিশীলতা, আনন্দ আৰু প্ৰকাশৰ বাৰ্তা। আপোনাৰ প্ৰতিভা বিকশিত হ'ব।",
        4: "আপোনাৰ এঞ্জেল সংখ্যা ৪। পৰিশ্ৰম, শৃংখলা আৰু স্থিৰতাৰ বাৰ্তা। কঠোৰ পৰিশ্ৰমৰ ফল শীঘ্ৰে পাব।",
        6: "আপোনাৰ এঞ্জেল সংখ্যা ৬। প্ৰেম, পৰিয়াল আৰু দায়িত্বৰ বাৰ্তা। পাৰিবাৰিক জীৱনত সুখ-শান্তি বৃদ্ধি পাব।",
        7: "আপোনাৰ এঞ্জেল সংখ্যা ৭। আধ্যাত্মিকতা, জ্ঞান আৰু অন্তৰ্দৃষ্টিৰ বাৰ্তা। আপুনি সঠিক পথত আছে।",
        8: "আপোনাৰ এঞ্জেল সংখ্যা ৮। সফলতা, প্ৰাচুৰ্য্য আৰু ক্ষমতাৰ বাৰ্তা। আৰ্থিক উন্নতিৰ যোগ আছে।",
        9: "আপোনাৰ এঞ্জেল সংখ্যা ৯। সমাপ্তি, মানৱতা আৰু সেৱাৰ বাৰ্তা। পুৰণি অধ্যায়ৰ সমাপ্তি ঘটিব।",
    }

    meaning = angel_meanings.get(kua, f"আপোনাৰ এঞ্জেল সংখ্যা {kua}। এই সংখ্যাই আপোনাৰ জীৱনত ঐশ্বৰিক দিশনিৰ্দেশনা প্ৰদান কৰে।")

    return {
        "value": kua,
        "raw_total": total,
        "description": meaning
    }


def analyze_name_compatibility(mulyanka: int, namanka: int, bhagyanka: int) -> dict:
    """
    Analyze if the current name is compatible with Mulyanka and Bhagyanka.
    Returns compatibility score and suggestions.
    """
    if mulyanka == 0 or namanka == 0:
        return {"compatible": False, "score": 0, "description": "গণনা কৰিব পৰা নগল"}

    # Check compatibility
    compatible = True
    reasons = []

    # Rule 1: Namanka should not conflict with Mulyanka
    if namanka == mulyanka:
        compatible = True
        reasons.append(f"আপোনাৰ নামাংক ({namanka}) আৰু মূল্যাংক ({mulyanka}) একে। ই অত্যন্ত শুভ।")
    elif namanka == 4 and mulyanka == 8:
        compatible = False
        reasons.append(f"নামাংক ৪ আৰু মূল্যাংক ৮ৰ মাজত বিৰোধ আছে।")
    elif namanka == 8 and mulyanka == 4:
        compatible = False
        reasons.append(f"নামাংক ৮ আৰু মূল্যাংক ৪ৰ মাজত বিৰোধ আছে।")
    else:
        # Check if namanka is friendly to mulyanka
        friendly_pairs = {1: [1, 2, 3, 5, 9], 2: [1, 2, 3, 5], 3: [1, 2, 3, 5, 9],
                          4: [5, 6, 7], 5: [1, 2, 3, 4, 5, 6, 7, 8, 9],
                          6: [4, 5, 6, 7], 7: [4, 5, 6, 7], 8: [5, 6, 8],
                          9: [1, 3, 5, 9]}
        if namanka in friendly_pairs.get(mulyanka, []):
            compatible = True
            reasons.append(f"নামাংক {namanka} আৰু মূল্যাংক {mulyanka} পৰস্পৰ বন্ধুত্বপূৰ্ণ।")
        else:
            compatible = False
            reasons.append(f"নামাংক {namanka} আৰু মূল্যাংক {mulyanka}ৰ মাজত সামঞ্জস্য নাই।")

    # Rule 2: Namanka should be friendly with Bhagyanka
    if namanka != bhagyanka:
        friendly_pairs = {1: [1, 2, 3, 5, 9], 2: [1, 2, 3, 5], 3: [1, 2, 3, 5, 9],
                          4: [5, 6, 7], 5: [1, 2, 3, 4, 5, 6, 7, 8, 9],
                          6: [4, 5, 6, 7], 7: [4, 5, 6, 7], 8: [5, 6, 8],
                          9: [1, 3, 5, 9]}
        if namanka not in friendly_pairs.get(bhagyanka, []):
            compatible = False
            reasons.append(f"নামাংক {namanka} আৰু ভাগ্যাংক {bhagyanka}ৰ মাজত সামঞ্জস্য নাই।")

    score = 100 if compatible else 40

    # Generate correction suggestion
    correction = ""
    if not compatible:
        # Suggest a name number that's friendly to both mulyanka and bhagyanka
        friendly_pairs = {1: [1, 2, 3, 5, 9], 2: [1, 2, 3, 5], 3: [1, 2, 3, 5, 9],
                          4: [5, 6, 7], 5: [1, 2, 3, 4, 5, 6, 7, 8, 9],
                          6: [4, 5, 6, 7], 7: [4, 5, 6, 7], 8: [5, 6, 8],
                          9: [1, 3, 5, 9]}
        m_friends = set(friendly_pairs.get(mulyanka, []))
        b_friends = set(friendly_pairs.get(bhagyanka, []))
        common = m_friends & b_friends
        if common:
            suggested = min(common)
            correction = f"আপোনাৰ নাম পৰিৱৰ্তন কৰি নামাংক {suggested} লৈ অনাৰ পৰামৰ্শ দিয়া হৈছে। {NAME_CORRECTION_SUGGESTIONS.get(suggested, '')}"
        else:
            correction = NAME_CORRECTION_SUGGESTIONS.get(mulyanka, '')

    return {
        "compatible": compatible,
        "score": score,
        "reasons": reasons,
        "correction": correction,
        "description": "আপোনাৰ নাম আপোনাৰ জন্ম সংখ্যাৰ সৈতে " + ("সামঞ্জস্যপূৰ্ণ।" if compatible else "সামঞ্জস্যপূৰ্ণ নহয়। নাম পৰিৱৰ্তনৰ পৰামৰ্শ দিয়া হৈছে।")
    }


def calculate_varsha_phal(bhagyanka: int, start_year: int = None) -> list:
    """
    Calculate Varsha Phal (Yearly Predictions) for the next 10 years.
    Based on Bhagyanka and personal year number.
    """
    if start_year is None:
        start_year = datetime.now().year

    predictions = []
    for i in range(10):
        year = start_year + i
        personal_year = reduce_to_single_digit(bhagyanka + reduce_to_single_digit(year))
        base = VARSHA_PHAL_TEMPLATES.get(personal_year, "এই বৰ্ষটো মধ্যম ফলপ্ৰদ হ'ব।")
        predictions.append({
            "year": year,
            "personal_year_number": personal_year,
            "prediction": f"{year} চনৰ বাবে: {base}"
        })
    return predictions


def get_pratikar(mulyanka: int, missing_numbers: list) -> dict:
    """
    Generate customized remedies (Pratikar) based on Ratna (Gemstones),
    Mantra, and Rudraksha.
    """
    remedies = {
        "gems": [],
        "mantras": [],
        "rudraksha": [],
        "general": []
    }

    # Remedies for missing numbers
    for num in missing_numbers:
        meaning = NUMBER_MEANINGS.get(num, {})
        if meaning.get('gem'):
            remedies["gems"].append(f"{num} সংখ্যাৰ বাবে: {meaning['gem']}")
        if meaning.get('mantra'):
            remedies["mantras"].append(f"{num} সংখ্যাৰ বাবে: {meaning['mantra']}")
        if meaning.get('rudraksha'):
            remedies["rudraksha"].append(f"{num} সংখ্যাৰ বাবে: {meaning['rudraksha']}")

    # General remedy based on Mulyanka
    meaning = NUMBER_MEANINGS.get(mulyanka, {})
    if meaning.get('remedy'):
        remedies["general"].append(meaning['remedy'])

    return remedies


def get_final_prediction(mulyanka: dict, bhagyanka: dict, namanka: dict,
                         missing: list, present: list, compatibility: dict,
                         angel: dict) -> str:
    """Generate a comprehensive final summary prediction."""
    parts = []

    parts.append(f"আপোনাৰ মূল্যাংক {mulyanka.get('value', 0)} ({mulyanka.get('planet', '')})। {mulyanka.get('description', '')}")
    parts.append(f"আপোনাৰ ভাগ্যাংক {bhagyanka.get('value', 0)} ({bhagyanka.get('planet', '')})। {bhagyanka.get('description', '')}")
    parts.append(f"আপোনাৰ নামাংক {namanka.get('value', 0)} ({namanka.get('planet', '')})। {namanka.get('description', '')}")

    if missing:
        missing_nums = ', '.join([str(n) for n in missing])
        parts.append(f"আপোনাৰ ল' চু গ্ৰীডত {missing_nums} সংখ্যাকেইটা অনুপস্থিত। এই সংখ্যাকেইটাৰ দ্বাৰা প্ৰতিনিধিত্ব কৰা গুণসমূহৰ অভাৱ আপোনাৰ জীৱনত অনুভৱ হ'ব পাৰে। উপযুক্ত ৰত্ন, মন্ত্ৰ আৰু ৰুদ্ৰাক্ষ ধাৰণ কৰি এই অভাৱ পূৰণ কৰিব পাৰে।")

    if present:
        present_nums = ', '.join([str(n) for n in present])
        parts.append(f"আপোনাৰ ল' চু গ্ৰীডত {present_nums} সংখ্যাকেইটা উপস্থিত। এই সংখ্যাকেইটাই আপোনাৰ শক্তিশালী দিশসমূহ প্ৰতিনিধিত্ব কৰে।")

    parts.append(f"আপোনাৰ এঞ্জেল সংখ্যা {angel.get('value', 0)}। {angel.get('description', '')}")

    if compatibility.get('compatible'):
        parts.append("আপোনাৰ নাম আপোনাৰ জন্ম সংখ্যাৰ সৈতে সামঞ্জস্যপূৰ্ণ। নাম পৰিৱৰ্তনৰ প্ৰয়োজন নাই।")
    else:
        parts.append(f"আপোনাৰ নাম আপোনাৰ জন্ম সংখ্যাৰ সৈতে সম্পূৰ্ণ সামঞ্জস্যপূৰ্ণ নহয়। {compatibility.get('correction', '')}")

    return '\n\n'.join(parts)


# ═══════════════════════════════════════════════════════════════════
#  COMPENSATION ANALYSIS (Namanka & Kua/Angel fill missing numbers)
# ═══════════════════════════════════════════════════════════════════

def analyze_compensation(missing: list, namanka: int, kua: int, angel: int) -> dict:
    """
    Analyze how Namanka and Kua/Angel Number compensate for missing numbers
    in the Lo Shu Grid. These numbers are NOT plotted in the grid but act as
    external compensators that fill the gaps.
    """
    compensated = []
    not_compensated = []
    details = []

    for num in missing:
        compensators = []
        if namanka == num:
            compensators.append(f"নামাংক {namanka} ({NUMBER_PLANETS_SHORT.get(num, '')})")
        if kua == num:
            compensators.append(f"কোৱা নম্বৰ (Kua) {kua} ({NUMBER_PLANETS_SHORT.get(num, '')})")
        if angel == num:
            compensators.append(f"এঞ্জেল সংখ্যা {angel}")

        if compensators:
            compensated.append(num)
            planet = NUMBER_PLANETS.get(num, "")
            meaning = NUMBER_MEANINGS.get(num, {})
            details.append({
                "number": num,
                "planet": planet,
                "compensated_by": compensators,
                "effect": f"ল' চু গ্ৰীডত {num} ({planet}) অনুপস্থিত, কিন্তু {' আৰু '.join(compensators)}ৰ দ্বাৰা ইয়াৰ অভাৱ পূৰণ হৈছে। {meaning.get('positive', '')}",
                "remedy": meaning.get('remedy', ''),
                "gem": meaning.get('gem', ''),
                "mantra": meaning.get('mantra', '')
            })
        else:
            not_compensated.append(num)

    return {
        "compensated": compensated,
        "not_compensated": not_compensated,
        "details": details,
        "summary": _build_compensation_summary(compensated, not_compensated, namanka, kua, angel)
    }


def _build_compensation_summary(compensated: list, not_compensated: list,
                                namanka: int, kua: int, angel: int) -> str:
    """Build a human-readable summary of compensation analysis."""
    parts = []

    if compensated:
        nums = ', '.join([str(n) for n in compensated])
        parts.append(f"✅ আপোনাৰ ল' চু গ্ৰীডত {nums} সংখ্যাকেইটা অনুপস্থিত, কিন্তু নামাংক ({namanka}), কোৱা নম্বৰ ({kua}), বা এঞ্জেল সংখ্যা ({angel})ৰ দ্বাৰা এই অভাৱ পূৰণ হৈছে। এই সংখ্যাকেইটাই বাহ্যিকভাৱে গ্ৰীডৰ দোষ নিবাৰণ কৰে।")

    if not_compensated:
        nums = ', '.join([str(n) for n in not_compensated])
        parts.append(f"⚠️ আপোনাৰ ল' চু গ্ৰীডত {nums} সংখ্যাকেইটা অনুপস্থিত আৰু নামাংক, কোৱা নম্বৰ বা এঞ্জেল সংখ্যাৰ দ্বাৰাও পূৰণ হোৱা নাই। এই সংখ্যাকেইটাৰ বাবে ৰত্ন, মন্ত্ৰ আৰু ৰুদ্ৰাক্ষ ধাৰণৰ পৰামৰ্শ দিয়া হৈছে।")

    if not compensated and not not_compensated:
        parts.append("🎉 আপোনাৰ ল' চু গ্ৰীড সম্পূৰ্ণ! কোনো সংখ্যা অনুপস্থিত নাই।")

    return '\n\n'.join(parts)


# ═══════════════════════════════════════════════════════════════════
#  LO SHU GRID PLANES ANALYSIS (8 Planes/Yogas)
# ═══════════════════════════════════════════════════════════════════

def analyze_lo_shu_planes(counts: dict) -> list:
    """
    Analyze all 8 Lo Shu Grid planes. Returns list of plane dicts with
    completion status (complete/partial/missing).
    """
    results = []
    for key, plane in LO_SHU_PLANES.items():
        present_count = 0
        missing_nums = []
        for num in plane['numbers']:
            if counts.get(num, 0) > 0:
                present_count += 1
            else:
                missing_nums.append(num)

        if present_count == 3:
            status = "complete"
            status_text = "✅ সম্পূৰ্ণ"
            status_class = "complete"
        elif present_count == 2:
            status = "partial"
            status_text = "🟡 আংশিক (২টা সংখ্যা উপস্থিত)"
            status_class = "partial"
        elif present_count == 1:
            status = "weak"
            status_text = "🟠 দুৰ্বল (১টা সংখ্যা উপস্থিত)"
            status_class = "weak"
        else:
            status = "missing"
            status_text = "❌ অনুপস্থিত"
            status_class = "missing"

        results.append({
            "key": key,
            "name": plane['name'],
            "name_short": plane['name_short'],
            "numbers": plane['numbers'],
            "status": status,
            "status_text": status_text,
            "status_class": status_class,
            "present_count": present_count,
            "missing_numbers": missing_nums,
            "description": plane['description'],
            "personality": plane['personality'],
            "career": plane['career'],
            "bad_effects": plane['bad_effects'],
            "partial_note": f"অনুপস্থিত সংখ্যা: {', '.join([str(n) for n in missing_nums])}। এই সংখ্যাকেইটা উপস্থিত থাকিলে যোগটো সম্পূৰ্ণ হ'ব।" if status != "complete" else ""
        })

    return results


def get_full_numerology_report(name: str, dob: str, gender: str = "male") -> dict:
    """
    Generate a complete numerology report with all calculations.
    gender: "male" or "female" — affects Kua/Angel number calculation.
    """
    # Core calculations
    mulyanka = calculate_mulyanka(dob)
    bhagyanka = calculate_bhagyanka(dob)
    namanka = calculate_namanka(name)
    kua = calculate_kua_number(dob, gender)
    angel = calculate_angel_number(dob, name, gender)  # Angel = Kua (same formula)

    # Lo Shu Grid = DOB + Mulyanka + Bhagyanka (Namanka & Kua are compensators)
    lo_shu = calculate_lo_shu_grid(dob, mulyanka['value'], bhagyanka['value'])

    # Compensation analysis: Namanka & Kua/Angel fill missing numbers
    # Note: Angel Number = Kua Number (same calculation), so only one compensator
    compensation = analyze_compensation(lo_shu['missing'], namanka['value'], kua['value'], angel['value'])

    # Lo Shu Grid Planes (8 Planes/Yogas)
    planes = analyze_lo_shu_planes(lo_shu['counts'])

    # Analysis
    missing_analysis = analyze_missing_numbers(lo_shu['missing'])
    present_analysis = analyze_present_numbers(lo_shu['present'], lo_shu['counts'])
    compatibility = analyze_name_compatibility(mulyanka['value'], namanka['value'], bhagyanka['value'])
    varsha_phal = calculate_varsha_phal(bhagyanka['value'])
    pratikar = get_pratikar(mulyanka['value'], lo_shu['missing'])
    final = get_final_prediction(mulyanka, bhagyanka, namanka,
                                 lo_shu['missing'], lo_shu['present'],
                                 compatibility, angel)

    return {
        "name": name,
        "dob": dob,
        "mulyanka": mulyanka,
        "bhagyanka": bhagyanka,
        "namanka": namanka,
        "lo_shu_grid": lo_shu,
        "compensation": compensation,
        "planes": planes,
        "missing_analysis": missing_analysis,
        "present_analysis": present_analysis,
        "angel_number": angel,
        "name_compatibility": compatibility,
        "varsha_phal": varsha_phal,
        "pratikar": pratikar,
        "final_prediction": final,
        # ─── Desktop app features ───
        "kua_number": kua,
        "subha_details": get_subha_details(mulyanka['value']),
        "number_compatibility": get_number_compatibility(mulyanka['value']),
        "lal_kitab_remedies": get_lal_kitab_remedies(mulyanka['value']),
        "gem_rudraksha_advice": get_gem_rudraksha_advice(mulyanka['value']),
        "chaldean_chart": get_chaldean_reference_chart(),
        "name_breakdown": get_name_breakdown(name),
        "detailed_varsha_phal": get_detailed_varsha_phal(dob, 10),
        "enhanced_lo_shu": calculate_enhanced_lo_shu_grid(dob, mulyanka['value'], bhagyanka['value'], namanka['value'], kua['value'])
    }


# ═══════════════════════════════════════════════════════════════════
#  NEW: KUA NUMBER (কোৱা নম্বৰ) - From VB.Net Desktop App
# ═══════════════════════════════════════════════════════════════════

def calculate_kua_number(dob: str, gender: str = "male") -> dict:
    """
    Calculate Kua Number based on birth year and gender.
    Formula: Male = 11 - reduced_year, Female = 4 + reduced_year
    Kua 5 becomes 2 for male, 8 for female.
    """
    try:
        year_str = dob.split('-')[0]
        year_val = int(year_str)
    except (ValueError, IndexError):
        return {"value": 0, "description": "গণনা কৰিব পৰা নগল"}

    # Sum all digits of year
    total = sum(int(d) for d in year_str)
    reduced = reduce_to_single_digit(total)

    gender_lower = gender.lower().strip()
    if gender_lower in ("male", "পুৰুষ"):
        kua = reduce_to_single_digit(11 - reduced)
        if kua == 5:
            kua = 2
    elif gender_lower in ("female", "মহিলা"):
        kua = reduce_to_single_digit(4 + reduced)
        if kua == 5:
            kua = 8
    else:
        # Default to male formula
        kua = reduce_to_single_digit(11 - reduced)
        if kua == 5:
            kua = 2

    # Kua number predictions
    kua_predictions = {
        1: {
            "group": "পূব দিশ (East Group)",
            "directions": {
                "ধন আৰু সফলতা": "দক্ষিণ-পূব",
                "স্বাস্থ্য আৰু দীৰ্ঘায়ু": "পূব",
                "প্ৰেম আৰু সম্পৰ্ক": "দক্ষিণ",
                "ব্যক্তিগত বিকাশ": "উত্তৰ"
            }
        },
        2: {
            "group": "পশ্চিম দিশ (West Group)",
            "directions": {
                "ধন আৰু সফলতা": "উত্তৰ-পূব",
                "স্বাস্থ্য আৰু দীৰ্ঘায়ু": "পশ্চিম",
                "প্ৰেম আৰু সম্পৰ্ক": "উত্তৰ-পশ্চিম",
                "ব্যক্তিগত বিকাশ": "দক্ষিণ-পশ্চিম"
            }
        },
        3: {
            "group": "পূব দিশ (East Group)",
            "directions": {
                "ধন আৰু সফলতা": "দক্ষিণ",
                "স্বাস্থ্য আৰু দীৰ্ঘায়ু": "উত্তৰ",
                "প্ৰেম আৰু সম্পৰ্ক": "দক্ষিণ-পূব",
                "ব্যক্তিগত বিকাশ": "পূব"
            }
        },
        4: {
            "group": "পূব দিশ (East Group)",
            "directions": {
                "ধন আৰু সফলতা": "উত্তৰ",
                "স্বাস্থ্য আৰু দীৰ্ঘায়ু": "দক্ষিণ",
                "প্ৰেম আৰু সম্পৰ্ক": "পূব",
                "ব্যক্তিগত বিকাশ": "দক্ষিণ-পূব"
            }
        },
        6: {
            "group": "পশ্চিম দিশ (West Group)",
            "directions": {
                "ধন আৰু সফলতা": "পশ্চিম",
                "স্বাস্থ্য আৰু দীৰ্ঘায়ু": "উত্তৰ-পূব",
                "প্ৰেম আৰু সম্পৰ্ক": "দক্ষিণ-পশ্চিম",
                "ব্যক্তিগত বিকাশ": "উত্তৰ-পশ্চিম"
            }
        },
        7: {
            "group": "পশ্চিম দিশ (West Group)",
            "directions": {
                "ধন আৰু সফলতা": "উত্তৰ-পশ্চিম",
                "স্বাস্থ্য আৰু দীৰ্ঘায়ু": "দক্ষিণ-পশ্চিম",
                "প্ৰেম আৰু সম্পৰ্ক": "উত্তৰ-পূব",
                "ব্যক্তিগত বিকাশ": "পশ্চিম"
            }
        },
        8: {
            "group": "পশ্চিম দিশ (West Group)",
            "directions": {
                "ধন আৰু সফলতা": "দক্ষিণ-পশ্চিম",
                "স্বাস্থ্য আৰু দীৰ্ঘায়ু": "উত্তৰ-পশ্চিম",
                "প্ৰেম আৰু সম্পৰ্ক": "পশ্চিম",
                "ব্যক্তিগত বিকাশ": "উত্তৰ-পূব"
            }
        },
        9: {
            "group": "পূব দিশ (East Group)",
            "directions": {
                "ধন আৰু সফলতা": "পূব",
                "স্বাস্থ্য আৰু দীৰ্ঘায়ু": "দক্ষিণ-পূব",
                "প্ৰেম আৰু সম্পৰ্ক": "উত্তৰ",
                "ব্যক্তিগত বিকাশ": "দক্ষিণ"
            }
        }
    }

    pred = kua_predictions.get(kua, {})
    return {
        "value": kua,
        "group": pred.get("group", ""),
        "directions": pred.get("directions", {}),
        "description": f"আপোনাৰ কোৱা নম্বৰ {kua}। {pred.get('group', '')}ৰ ব্যক্তি।"
    }


# ═══════════════════════════════════════════════════════════════════
#  NEW: SUBHA DETAILS (শুভ ৰং, সংখ্যা, তাৰিখ) - From VB.Net
# ═══════════════════════════════════════════════════════════════════

def get_subha_details(mulyanka: int) -> dict:
    """Get auspicious color, number, and dates based on Mulyanka."""
    subha_data = {
        1: {"color": "হালধীয়া, সোণালী, কমলা", "number": "১, ২, ৩, ৯", "tarikh": "১, ১০, ১৯, ২৮"},
        2: {"color": "বগা, পাতল সেউজীয়া, ৰূপালী", "number": "১, ২, ৪, ৭", "tarikh": "২, ১১, ২০, ২৯"},
        3: {"color": "হালধীয়া, বেঙুনীয়া, গুলপীয়া", "number": "৩, ৬, ৯", "tarikh": "৩, ১২, ২১, ৩০"},
        4: {"color": "নীলা, ছাই ৰং, খাকী", "number": "১, ৪, ৮", "tarikh": "৪, ১৩, ২২, ৩১"},
        5: {"color": "সেউজীয়া, পাতল ৰং", "number": "৫, ৯", "tarikh": "৫, ১৪, ২৩"},
        6: {"color": "বগা, পাতল নীলা, গুলপীয়া", "number": "৩, ৬, ৯", "tarikh": "৬, ১৫, ২৪"},
        7: {"color": "পাতল সেউজীয়া, বগা, পাতল হালধীয়া", "number": "১, ২, ৭", "tarikh": "৭, ১৬, ২৫"},
        8: {"color": "ক'লা, ডাঠ নীলা, ছাই ৰং", "number": "৮", "tarikh": "৮, ১৭, ২৬"},
        9: {"color": "ৰঙা, গোলাপী, গাঢ় ৰঙা", "number": "১, ৩, ৬, ৯", "tarikh": "৯, ১৮, ২৭"},
    }
    return subha_data.get(mulyanka, {"color": "উপলব্ধ নাই", "number": "উপলব্ধ নাই", "tarikh": "উপলব্ধ নাই"})


# ═══════════════════════════════════════════════════════════════════
#  NEW: NUMBER COMPATIBILITY (মিত্ৰ-শত্ৰু-সম সংখ্যা) - From VB.Net
# ═══════════════════════════════════════════════════════════════════

def get_number_compatibility(mulyanka: int) -> dict:
    """Get friendly, enemy, and neutral numbers based on Mulyanka."""
    compat_data = {
        1: {"friendly": "১, ২, ৩, ৯", "enemy": "৬, ৭, ৮", "neutral": "৪, ৫"},
        2: {"friendly": "১, ৫", "enemy": "৪, ৬, ৮", "neutral": "২, ৩, ৭, ৯"},
        3: {"friendly": "১, ২, ৯", "enemy": "৪, ৬, ৮", "neutral": "৩, ৫, ৭"},
        4: {"friendly": "৫, ৬, ৮", "enemy": "২, ৩, ৯", "neutral": "১, ৪, ৭"},
        5: {"friendly": "১, ৪, ৬", "enemy": "কোনো শত্ৰু নাই", "neutral": "২, ৩, ৫, ৭, ৮, ৯"},
        6: {"friendly": "৪, ৫, ৮", "enemy": "১, ২, ৩, ৯", "neutral": "৬, ৭"},
        7: {"friendly": "৫, ৬, ৮", "enemy": "১, ২, ৩, ৯", "neutral": "৪, ৭"},
        8: {"friendly": "৪, ৫, ৬", "enemy": "১, ২, ৩, ৭, ৯", "neutral": "৮"},
        9: {"friendly": "১, ২, ৩", "enemy": "৬, ৭, ৮", "neutral": "৪, ৫, ৯"},
    }
    return compat_data.get(mulyanka, {"friendly": "-", "enemy": "-", "neutral": "-"})


# ═══════════════════════════════════════════════════════════════════
#  NEW: LAL KITAB REMEDIES (লাল কিতাপৰ প্ৰতিকাৰ) - From VB.Net
# ═══════════════════════════════════════════════════════════════════

def get_lal_kitab_remedies(mulyanka: int) -> list:
    """Get Lal Kitab home remedies based on Mulyanka."""
    remedies = {
        1: [
            "ৰাতিপুৱা উঠি পিতৃক সেৱা কৰিব আৰু সন্মান কৰিব।",
            "তামৰ পাত্ৰত ৰখা পানী খাব।",
            "ৰঙা বান্দৰক বা গৰুক ঘেঁহু আৰু গুৰ খুৱাব।",
            "ঘৰৰ পূব দিশ সদায় পৰিষ্কাৰ কৰি ৰাখিব।"
        ],
        2: [
            "মাতৃৰ পৰা আশীৰ্বাদ ল'ব আৰু তেওঁক সদায় সুখী ৰাখিব।",
            "সোমবাৰে শিৱলিংগত গাখীৰ বা পানী ঢালিব।",
            "ৰাতিৰ ভাগত গাখীৰ খোৱা পৰিহাৰ কৰিব।",
            "আনৰ পৰা কেতিয়াও বিনামূলীয়াকৈ গাখীৰ বা পানী নাখাব।"
        ],
        3: [
            "সদায় কপালত হালধী বা কেশৰৰ ফোঁট ল'ব।",
            "গুৰু, সাধু বা বয়সস্থ লোকক সন্মান কৰিব আৰু সহায় কৰিব।",
            "বৃহস্পতিবাৰে হালধীয়া বস্তু (যেনে- বুট দাইল, কল) দান কৰিব।",
            "ঘৰত তুলসী গছ ৰুব আৰু নিয়মীয়াকৈ পানী দিব।"
        ],
        4: [
            "সদায় লগত এটা সৰু বৰ্গাকৃতিৰ ৰূপৰ টুকুৰা ৰাখিব।",
            "কুকুৰক (বিশেষকৈ ৰাস্তাৰ কুকুৰক) ৰুটী বা বিস্কুট খুৱাব।",
            "মদ, ধপাত আৰু নিচাজাতীয় দ্ৰব্য সম্পূৰ্ণৰূপে পৰিহাৰ কৰিব।",
            "শৌচালয় আৰু গা ধোৱা ঘৰ সদায় পৰিষ্কাৰ কৰি ৰাখিব।"
        ],
        5: [
            "গৰুক নিয়মীয়াকৈ সেউজীয়া ঘাঁহ বা পালেং শাক খুৱাব।",
            "নিজৰ ভনীয়েক, পেহীয়েক বা ভাগিনীয়কক সন্মান কৰিব আৰু উপহাৰ দিব।",
            "দাঁত সদায় পৰিষ্কাৰকৈ ৰাখিব (ফিতকিৰিৰে দাঁত মাজিব পাৰে)।",
            "ঘৰত বহল পাতৰ সেউজীয়া গছ ৰাখিব।"
        ],
        6: [
            "সদায় পৰিষ্কাৰ আৰু ইস্ত্ৰি কৰা কাপোৰ পিন্ধিব।",
            "নিয়মীয়াকৈ সুগন্ধি ব্যৱহাৰ কৰিব।",
            "মহিলাসকলক সদায় সন্মান কৰিব আৰু পত্নীক সুখী ৰাখিব।",
            "নিজৰ খোৱা আহাৰৰ পৰা অলপ অংশ গৰুক খুৱাব।"
        ],
        7: [
            "কুকুৰক (বিশেষকৈ ক'লা আৰু বগা ৰঙৰ) আহাৰ দিব।",
            "সাধু-সন্ন্যাসী বা দৰিদ্ৰ লোকক ক'লা-বগা কম্বল দান কৰিব।",
            "কপালত কেশৰৰ ফোঁট লগাব।",
            "কান্ধত বা হাতত ক'লা আৰু বগা সূতাৰ এক ধাগা বান্ধিব পাৰে।"
        ],
        8: [
            "অন্ধ, বিকলাঙ্গ বা পৰিশ্ৰমী বনুৱাক সহায় কৰিব আৰু খাবলৈ দিব।",
            "আমিষ আহাৰ (মঙহ) আৰু মদৰ পৰা সম্পূৰ্ণৰূপে আঁতৰত থাকিব।",
            "কাউৰীক নিয়মীয়াকৈ আহাৰ দিব।",
            "শনিবাৰে সৰিয়হৰ তেল দান কৰিব বা চাকি জ্বলাব।"
        ],
        9: [
            "খং নিয়ন্ত্ৰণ কৰিব আৰু নিজৰ ভাতৃৰ সৈতে সুসম্পৰ্ক বজাই ৰাখিব।",
            "হনুমান চালীসা পাঠ কৰিব আৰু হনুমান বন্দনা কৰিব।",
            "মঙলবাৰে মিঠাই বা মিঠা ৰুটী বান্দৰক বা দৰিদ্ৰক দান কৰিব।",
            "ৰাতিপুৱা মৌ (Honey) খাব পাৰে।"
        ]
    }
    return remedies.get(mulyanka, ["সঠিক সংখ্যা পোৱা নগ'ল।"])


# ═══════════════════════════════════════════════════════════════════
#  NEW: GEM & RUDRAKSHA ADVICE (ৰত্ন আৰু ৰুদ্ৰাক্ষ) - From VB.Net
# ═══════════════════════════════════════════════════════════════════

def get_gem_rudraksha_advice(mulyanka: int) -> dict:
    """Get detailed gemstone and rudraksha advice based on Mulyanka."""
    advice = {
        1: {"gem": "চুনি (Ruby)", "weight": "৫-৭ ৰতি", "finger": "অনামিকা (Ring Finger)",
            "metal": "সোণ বা তাম", "rudraksha": "এক মুখী বা ১২ মুখী ৰুদ্ৰাক্ষ"},
        2: {"gem": "মুকুতা (Pearl)", "weight": "৫-৮ ৰতি", "finger": "কনিষ্ঠা (Little Finger)",
            "metal": "ৰূপ", "rudraksha": "দুই মুখী ৰুদ্ৰাক্ষ"},
        3: {"gem": "পখৰাজ (Yellow Sapphire)", "weight": "৪-৭ ৰতি", "finger": "তৰ্জনী (Index Finger)",
            "metal": "সোণ", "rudraksha": "পাঁচ মুখী ৰুদ্ৰাক্ষ"},
        4: {"gem": "গোমেদ (Gomedh)", "weight": "৫-৯ ৰতি", "finger": "মধ্যমা (Middle Finger)",
            "metal": "পঞ্চধাতু বা ৰূপ", "rudraksha": "আঠ মুখী ৰুদ্ৰাক্ষ"},
        5: {"gem": "পান্না (Emerald)", "weight": "৩-৬ ৰতি", "finger": "কনিষ্ঠা (Little Finger)",
            "metal": "সোণ বা ৰূপ", "rudraksha": "চাৰি মুখী ৰুদ্ৰাক্ষ"},
        6: {"gem": "হীৰা (Diamond) বা বগা পখৰাজ", "weight": "০.৫০ কেৰেট (হীৰা) বা ৫-৭ ৰতি", "finger": "অনামিকা বা মধ্যমা",
            "metal": "প্লেটিনাম, ৰূপ বা সোণ", "rudraksha": "ছয় মুখী ৰুদ্ৰাক্ষ"},
        7: {"gem": "বৈদূৰ্যমণি (Cat's Eye)", "weight": "৫-৭ ৰতি", "finger": "মধ্যমা বা কনিষ্ঠা",
            "metal": "ৰূপ", "rudraksha": "ন মুখী ৰুদ্ৰাক্ষ"},
        8: {"gem": "নীলম (Blue Sapphire)", "weight": "৪-৭ ৰতি", "finger": "মধ্যমা (Middle Finger)",
            "metal": "পঞ্চধাতু বা লো", "rudraksha": "সাত মুখী ৰুদ্ৰাক্ষ"},
        9: {"gem": "মুগা বা প্ৰবাল (Red Coral)", "weight": "৬-৯ ৰতি", "finger": "অনামিকা (Ring Finger)",
            "metal": "তাম বা সোণ", "rudraksha": "তিনি মুখী ৰুদ্ৰাক্ষ"},
    }
    return advice.get(mulyanka, {"gem": "-", "weight": "-", "finger": "-", "metal": "-", "rudraksha": "-"})


# ═══════════════════════════════════════════════════════════════════
#  NEW: CHALDEAN REFERENCE CHART - From VB.Net
# ═══════════════════════════════════════════════════════════════════

def get_chaldean_reference_chart() -> str:
    """Return the Chaldean letter-value reference chart."""
    return """Chaldean পদ্ধতিৰ আখৰৰ মান (Letter Values):

১ (1) : A, I, J, Q, Y
২ (2) : B, K, R
৩ (3) : C, G, L, S
৪ (4) : D, M, T
৫ (5) : E, H, N, X
৬ (6) : U, V, W
৭ (7) : O, Z
৮ (8) : F, P

(বিঃদ্ৰঃ Chaldean পদ্ধতিত ৯ নম্বৰৰ বাবে কোনো আখৰ নিৰ্ধাৰণ কৰা হোৱা নাই।)"""


# ═══════════════════════════════════════════════════════════════════
#  NEW: NAME BREAKDOWN (নামৰ আখৰ অনুযায়ী মান) - From VB.Net
# ═══════════════════════════════════════════════════════════════════

def get_name_breakdown(name: str) -> dict:
    """Get letter-by-letter breakdown of name value."""
    if not name or not name.strip():
        return {"breakdown": "", "total": 0, "namanka": 0}

    name_upper = name.upper().strip()
    breakdown_parts = []
    total = 0

    for c in name_upper:
        val = CHALDEAN_MAP.get(c.lower(), 0)
        if val > 0:
            total += val
            breakdown_parts.append(f"{c}({val})")
        elif c == ' ':
            breakdown_parts.append("[Space]")

    breakdown_str = " + ".join(breakdown_parts)
    namanka = reduce_to_single_digit(total)

    return {
        "breakdown": breakdown_str,
        "total": total,
        "namanka": namanka
    }


# ═══════════════════════════════════════════════════════════════════
#  NEW: DETAILED VARSHA PHAL (বিস্তৃত বৰ্ষফল) - From VB.Net
# ═══════════════════════════════════════════════════════════════════

def get_detailed_varsha_phal(dob: str, num_years: int = 10) -> list:
    """Get detailed yearly predictions like the VB.Net desktop app."""
    try:
        parts = dob.split('-')
        day = int(parts[2])
        month = int(parts[1])
    except (ValueError, IndexError):
        return []

    current_year = datetime.now().year
    predictions = []

    for offset in range(num_years):
        year = current_year + offset
        # Personal year formula: sum of birth day digits + birth month digits + year digits
        total = (day // 10) + (day % 10) + (month // 10) + (month % 10)
        temp = year
        while temp > 0:
            total += temp % 10
            temp //= 10
        personal_year = reduce_to_single_digit(total)

        prediction_text = _get_yearly_prediction_text(personal_year, year)
        predictions.append({
            "year": year,
            "personal_year_number": personal_year,
            "prediction": prediction_text
        })

    return predictions


def _get_yearly_prediction_text(personal_year: int, year: int) -> str:
    """Get the detailed yearly prediction text (from VB.Net GetYearlyPredictionText / DisplayPersonalYearPrediction)."""
    predictions = {
        1: f"""====সংখ্যাতত্ব বৰ্ষফল - {year}====
        ব্যক্তিগত বৰ্ষ ১: নতুন আৰম্ভণি আৰু সুযোগৰ বছৰ
=========================================================

সাধাৰণ বিৱৰণ:
ব্যক্তিগত বৰ্ষ ১ (ৰবি গ্ৰহ) হৈছে নৱজাগৰণ আৰু নতুন আৰম্ভণিৰ সময়। ৯ বছৰীয়া চক্ৰৰ এইটো প্ৰথম বছৰ হোৱাৰ বাবে, এই সময়ছোৱাত আপুনি যি বীজ সিঁচিব, তাৰ ফলেই পৰৱৰ্তী আঠ বছৰলৈ ভোগ কৰিব। এই বছৰটোৱে আপোনাক সাহস, আত্মবিশ্বাস আৰু নেতৃত্বৰ গুণ প্ৰদান কৰিব। পুৰণি চিন্তাধাৰা আৰু এলাহ ত্যাগ কৰি নতুন উদ্যমেৰে জীৱনৰ যিকোনো দিশত আগবাঢ়ি যোৱাৰ বাবে এইটো সৰ্বোত্তম সময়।

কেৰিয়াৰ আৰু আৰ্থিক দিশ:
কৰ্মক্ষেত্ৰত এই বছৰটো অতি ফলপ্ৰসূ হ'ব। নতুন চাকৰি, পদোন্নতি বা ব্যৱসায়ত নতুন প্ৰকল্প আৰম্ভ কৰাৰ প্ৰবল যোগ আছে। আৰ্থিক দিশত উন্নতি হ'ব যদিও নতুন বিনিয়োগৰ বাবে মূলধনৰ প্ৰয়োজন হ'ব পাৰে। নিজৰ ওপৰত বিশ্বাস ৰাখি লোৱা সিদ্ধান্তই সফলতা আনিব।

প্ৰেম, পৰিয়াল আৰু সম্পৰ্ক:
সম্পৰ্কৰ ক্ষেত্ৰত আপুনি অধিক স্বাধীনচিতিয়া অনুভৱ কৰিব। কেতিয়াবা নিজৰ মত সাব্যস্ত কৰিবলৈ গৈ পৰিয়ালৰ সদস্যৰ লগত সামান্য মতানৈক্য হ'ব পাৰে। অৱশ্যে, নতুন বন্ধুত্ব গঢ়ি উঠাৰো সম্ভাৱনা আছে।

স্বাস্থ্য:
শক্তি আৰু উৎসাহ বৃদ্ধি পাব। অৱশ্যে অতিৰিক্ত পৰিশ্ৰম আৰু মানসিক চাপৰ বাবে মূৰৰ কামোৰণি বা চকুৰ সমস্যা হ'ব পাৰে। শাৰীৰিক ব্যায়ামৰ প্ৰয়োজন।

শুভ দিশ:
নেতৃত্ব, স্বাধীনতা, নতুন পৰিকল্পনা, সক্ৰিয়তা আৰু আত্মনিৰ্ভৰশীলতা।

অশুভ দিশ আৰু সাৱধানতা:
অহংকাৰ, খৰধৰকৈ সিদ্ধান্ত লোৱা, আনৰ পৰামৰ্শ আওকাণ কৰা আৰু খং। এইবোৰ নিয়ন্ত্ৰণ নকৰিলে ভাল সুযোগ হাতছাড়া হ'ব পাৰে।

প্ৰতিকাৰ আৰু পৰামৰ্শ:
১. প্ৰতিদিনে ৰাতিপুৱা সূৰ্য দেৱতাক জল অৰ্পণ কৰক। জীয়াই থকা দেউতাক বা পিতৃস্থানীয় ব্যক্তিক সন্মান কৰক।
২. ৰঙা বা কমলা ৰঙৰ কাপোৰৰ ব্যৱহাৰ বৃদ্ধি কৰক।
৩. গুৰুত্বপূৰ্ণ কাম আৰম্ভ কৰাৰ আগতে অভিজ্ঞ লোকৰ পৰামৰ্শ ল'বলৈ নাপাহৰিব।""",

        2: f"""====সংখ্যাতত্ব বৰ্ষফল - {year}====
        ব্যক্তিগত বৰ্ষ ২: ধৈৰ্য্য, সহযোগিতা আৰু সম্পৰ্কৰ বছৰ
=========================================================

সাধাৰণ বিৱৰণ:
যোৱা বছৰৰ দ্ৰুত গতিৰ বিপৰীতে, ব্যক্তিগত বৰ্ষ ২ (চন্দ্ৰ গ্ৰহ) হৈছে শান্তি, অপেক্ষা আৰু ধৈৰ্য্যৰ বছৰ। এই সময়ছোৱা গছপুলি এটাক সাৰ-পানী দি ডাঙৰ কৰাৰ দৰে। ইয়াত খৰধৰ কৰিলে বা বলপ্ৰয়োগ কৰিলে ফল পোৱা নাযাব। আনৰ সৈতে সহযোগিতা, কূটনীতি আৰু আৱেগিক বুজাবুজিৰ জৰিয়তেহে আপুনি এই বছৰত আগবাঢ়িব পাৰিব। আপোনাৰ অন্তৰ্দৃষ্টি (Intuition) এই বছৰত অতি প্ৰখৰ হ'ব।

কেৰিয়াৰ আৰু আৰ্থিক দিশ:
অংশীদাৰী ব্যৱসায় বা আনৰ লগত মিলি কৰা কামত সফলতা লাভ কৰিব। কৰ্মস্থানত শান্তিপূৰ্ণ পৰিৱেশ বিচাৰিব। আৰ্থিক দিশত হঠাতে ডাঙৰ লাভ নহ'লেও, অৱস্থা সুস্থিৰ হৈ থাকিব। বিনিয়োগৰ ক্ষেত্ৰত সাৱধান হোৱা ভাল।

প্ৰেম, পৰিয়াল আৰু সম্পৰ্ক:
এই বছৰটো সম্পৰ্কৰ বাবে অতি গুৰুত্বপূৰ্ণ। প্ৰেম আৰু বিবাহৰ বাবে সুন্দৰ সময়। পৰিয়ালৰ সদস্যৰ সৈতে আৱেগিক বান্ধোন দৃঢ় হ'ব। কিন্তু আপুনি অতিমাত্ৰা সংবেদনশীল হোৱাৰ বাবে সৰু কথাতে আঘাত পাব পাৰে।

স্বাস্থ্য:
মানসিক স্বাস্থ্যৰ ওপৰত বেছি গুৰুত্ব দিব লাগিব। মানসিক অৱসাদ, পেটৰ সমস্যা বা টোপনিৰ অভাৱ হ'ব পাৰে। পৰ্যাপ্ত জিৰণিৰ প্ৰয়োজন।

শুভ দিশ:
কূটনীতি, প্ৰেম, সহযোগিতা, দলবদ্ধ প্ৰচেষ্টা আৰু আৱেগিক সমতা।

অশুভ দিশ আৰু সাৱধানতা:
অতিমাত্ৰা আৱেগিক হোৱা, সিদ্ধান্তহীনতা, আত্মবিশ্বাসৰ অভাৱ আৰু নিৰাশা। আনৰ কথা শুনি সহজে ভোল নাযাব।

প্ৰতিকাৰ আৰু পৰামৰ্শ:
১. ভগৱান শিৱৰ আৰাধনা কৰক আৰু সোমবাৰে শিৱলিংগত জল বা গাখীৰ অৰ্পণ কৰক।
২. ৰূপৰ পাত্ৰত পানী খোৱাৰ অভ্যাস কৰক। বগা আৰু পাতল নীলা ৰং ব্যৱহাৰ কৰক।
৩. যোগ বা ধ্যানৰ জৰিয়তে মন শান্ত ৰখাৰ চেষ্টা কৰক।""",

        3: f"""====সংখ্যাতত্ব বৰ্ষফল - {year}====
        ব্যক্তিগত বৰ্ষ ৩: সৃজনশীলতা, প্ৰকাশ আৰু আনন্দৰ বছৰ
=========================================================

সাধাৰণ বিৱৰণ:
ব্যক্তিগত বৰ্ষ ৩ (বৃহস্পতি গ্ৰহ) হৈছে জীৱনক উপভোগ কৰাৰ সময়। যোৱা দুবছৰৰ পৰিশ্ৰমৰ পিছত, এই বছৰটোৱে আপোনালৈ আনন্দ আৰু সামাজিকতা কঢ়িয়াই আনিব। আপোনাৰ সৃজনীশীল প্ৰতিভা, যেনে- লিখা-মেলা, গান-বাজনা, অভিনয় বা কথা-বতৰাৰ কলা বিকশিত হ'ব। বন্ধু-বান্ধৱৰ লগত সময় কটোৱা, ভ্ৰমণ কৰা আৰু নতুন মানুহৰ সৈতে চিনাকি হোৱাৰ বাবে এইটো সৰ্বশ্ৰেষ্ঠ সময়।

কেৰিয়াৰ আৰু আৰ্থিক দিশ:
যোগাযোগ, কলা, শিক্ষা আৰু মাধ্যমৰ (Media) লগত জড়িত লোকসকলৰ বাবে এইটো এটা লাভজনক বছৰ। কৰ্মক্ষেত্ৰত আপোনাৰ ধাৰণাসমূহ প্ৰশংসিত হ'ব। অৱশ্যে, আৰ্থিক দিশত অলপ সাৱধান হ'ব লাগিব, কাৰণ এই বছৰত আপোনাৰ খৰচ কৰাৰ প্ৰৱণতা বাঢ়িব পাৰে।

প্ৰেম, পৰিয়াল আৰু সম্পৰ্ক:
সামাজিক জীৱন অতি সক্ৰিয় হ'ব। পৰিয়ালত কোনো শুভ কাৰ্য বা উৎসৱৰ আয়োজন হ'ব পাৰে। সন্তান লাভৰ বাবেও এই বছৰটো অতি শুভ।

স্বাস্থ্য:
সাধাৰণতে স্বাস্থ্য ভাল থাকিব। কিন্তু খাদ্যাভ্যাসৰ অনিয়মৰ বাবে মেদবহুলতা বা লিভাৰৰ সমস্যা হ'ব পাৰে। জীৱনশৈলী শৃংখলাবদ্ধ ৰখা প্ৰয়োজন।

শুভ দিশ:
আনন্দময় পৰিৱেশ, আত্মপ্ৰকাশ, বুদ্ধি, সৃজনশীলতা আৰু জনপ্ৰিয়তা।

অশুভ দিশ আৰু সাৱধানতা:
অযথা ব্যয়, লক্ষ্যৰ পৰা বিচ্যুত হোৱা, লোকৰ বদনাম গোৱা (gossiping) আৰু দায়িত্বহীনতা। কামবোৰ আধৰুৱাকৈ এৰাৰ প্ৰৱণতা থাকিব পাৰে।

প্ৰতিকাৰ আৰু পৰামৰ্শ:
১. ভগৱান বিষ্ণু বা গুৰুৰ আৰাধনা কৰক। বৃহস্পতিবাৰে হালধীয়া বস্তু বা চানা ডাইল দান কৰক।
২. হালধীয়া আৰু সোণালী ৰঙৰ কাপোৰ পৰিধান কৰিলে শুভ ফল পাব।
৩. নিজৰ শক্তি আৰু সময় সঠিক লক্ষ্যত কেন্দ্ৰীভূত কৰক, অবাবত সময় নষ্ট নকৰিব।""",

        4: f"""====সংখ্যাতত্ব বৰ্ষফল - {year}====
        ব্যক্তিগত বৰ্ষ ৪: কঠোৰ পৰিশ্ৰম, ভেটি নিৰ্মাণ আৰু শৃংখলাৰ বছৰ
=========================================================

সাধাৰণ বিৱৰণ:
ব্যক্তিগত বৰ্ষ ৪ (ৰাহু গ্ৰহ) হৈছে জীৱনৰ গুৰুত্বপূৰ্ণ ভেটি নিৰ্মাণ কৰাৰ সময়। যোৱা বছৰৰ আমোদ-প্ৰমোদৰ পিছত, এই বছৰটোৱে আপোনাক বাস্তৱৰ মুখামুখি কৰাব। এই বছৰত ভাগ্যতকৈ কৰ্মৰ ওপৰত বেছি নিৰ্ভৰ কৰিব লাগিব। কঠোৰ পৰিশ্ৰম, শৃংখলা, আৰু পৰিকল্পনাবদ্ধভাৱে কাম কৰিলেহে সফলতা হাতলৈ আহিব। আলস্য আৰু গাফিলতি কৰিলে এই বছৰত লোকচানৰ সন্মুখীন হ'বলগীয়া হ'ব পাৰে।

কেৰিয়াৰ আৰু আৰ্থিক দিশ:
কৰ্মক্ষেত্ৰত দায়িত্ব আৰু কামৰ হেঁচা যথেষ্ট বৃদ্ধি পাব। নতুন প্ৰকল্প হাতত ল'ব পাৰে। মাটি-বাৰী, ঘৰ নিৰ্মাণ বা সম্পত্তিৰ লগত জড়িত কামৰ বাবে এই সময় অনুকূল। আৰ্থিক দিশত অপ্ৰত্যাশিত খৰচ আহিব পাৰে, সেয়েহে সঞ্চয়ৰ প্ৰতি গুৰুত্ব দিয়াটো অতি প্ৰয়োজনীয়।

প্ৰেম, পৰিয়াল আৰু সম্পৰ্ক:
কৰ্মব্যস্ততাৰ বাবে পৰিয়াল বা প্ৰিয়জনক পৰ্যাপ্ত সময় দিব নোৱাৰিব পাৰে, যাৰ ফলত ভুল বুজাবুজিৰ সৃষ্টি হ'ব পাৰে। সম্পৰ্কবোৰত স্থিৰতা অনাৰ প্ৰয়াস কৰক।

স্বাস্থ্য:
কঠোৰ পৰিশ্ৰম আৰু মানসিক চাপৰ ফলত ভাগৰ, গাঁঠিৰ বিষ বা স্নায়ৱিক দুৰ্বলতা হ'ব পাৰে। নিয়মীয়া স্বাস্থ্য পৰীক্ষা আৰু বিশ্ৰামৰ প্ৰয়োজন।

শুভ দিশ:
স্থিৰতা, বাস্তৱবাদী চিন্তা, পৰিশ্ৰম, সংগঠন আৰু ভৱিষ্যতৰ পৰিকল্পনা।

অশুভ দিশ আৰু সাৱধানতা:
অস্থিৰতা, হতাশা, একোঁচীয়া স্বভাৱ আৰু অপ্ৰত্যাশিত বাধা। কোনো চমু পথ (shortcut) গ্ৰহণ কৰি ধন ঘটিবলৈ চেষ্টা নকৰিব।

প্ৰতিকাৰ আৰু পৰামৰ্শ:
১. ৰাস্তাৰ কুকুৰক খাবলৈ দিয়ক আৰু পৰিষ্কাৰ-পৰিচ্ছন্নতা বজাই ৰাখক।
২. ডাঠ নীলা বা মুগা (Brown) ৰঙৰ ব্যৱহাৰ কৰিব পাৰে। গণেশ ভগৱানক স্মৰণ কৰক।
৩. যিকোনো কাম হাতত লোৱাৰ আগতে তাৰ আইনী আৰু ব্যৱহাৰিক দিশবোৰ ভালদৰে পৰীক্ষা কৰি ল'ব।""",

        5: f"""====সংখ্যাতত্ব বৰ্ষফল - {year}====
        ব্যক্তিগত বৰ্ষ ৫: পৰিৱৰ্তন, স্বাধীনতা আৰু বিস্তাৰৰ বছৰ
=========================================================

সাধাৰণ বিৱৰণ:
ব্যক্তিগত বৰ্ষ ৫ (বুধ গ্ৰহ) হৈছে ৯ বছৰীয়া চক্ৰৰ ঠিক মাজৰ বছৰ। এইটো এটা অস্থিৰ কিন্তু ৰোমাঞ্চকৰ সময়। যোৱা বছৰৰ কঠোৰ বান্ধোনৰ পৰা মুকলি হৈ এই বছৰত আপুনি স্বাধীনতা বিচাৰিব। জীৱনৰ বহু দিশত হঠাতে পৰিৱৰ্তন আহিব পাৰে। স্থান পৰিৱৰ্তন, নতুন কৰ্মসংস্থাপন, বা বিদেশ ভ্ৰমণৰ যোগ আছে। নতুন সুযোগ গ্ৰহণ কৰিবলৈ সদায় সাজু থাকক।

কেৰিয়াৰ আৰু আৰ্থিক দিশ:
কেৰিয়াৰত পৰিৱৰ্তনৰ বতাহ বলিব। নতুন চাকৰিৰ প্ৰস্তাৱ বা ব্যৱসায়ত নতুন দিশ উন্মোচন হ'ব পাৰে। যোগাযোগ, বিক্ৰী (Sales), আৰু প্ৰচাৰৰ জৰিয়তে আৰ্থিক লাভ হ'ব। অৱশ্যে অতিমাত্ৰা ৰিস্ক (risk) ল'লে আৰ্থিক ক্ষতিও হ'ব পাৰে।

প্ৰেম, পৰিয়াল আৰু সম্পৰ্ক:
আপোনাৰ সামাজিক পৰিসৰ বৃদ্ধি পাব। নতুন প্ৰেমৰ সম্পৰ্ক গঢ় লৈ উঠিব পাৰে। কিন্তু বৰ্তমানৰ সম্পৰ্কত যদি একঘেয়ামী আছিল, তেন্তে তাত ভাঙোন ধৰাৰো আশংকা থাকে। বুজাবুজিৰে চলক।

স্বাস্থ্য:
দুৰ্ঘটনা, স্নায়ুৰ সমস্যা বা ছালৰ ৰোগ হ'ব পাৰে। খৰধৰকৈ গাড়ী চলোৱা বা ভ্ৰমণৰ সময়ত সাৱধানতা অৱলম্বন কৰাটো বাঞ্চনীয়।

শুভ দিশ:
নতুন সুযোগ, ভ্ৰমণ, স্বাধীনতা, যোগাযোগ দক্ষতা আৰু পৰিস্থিতিৰ লগত খাপ খাব পৰা ক্ষমতা।

অশুভ দিশ আৰু সাৱধানতা:
অস্থিৰতা, মনোযোগৰ অভাৱ, অত্যধিক ভোগবিলাস, আৰু জুৱা বা ফাষ্ট-মানিৰ প্ৰতি আকৰ্ষণ। হঠকাৰী সিদ্ধান্ত ল'ব নালাগে।

প্ৰতিকাৰ আৰু পৰামৰ্শ:
১. গৰুক সেউজীয়া ঘাঁহ খাবলৈ দিয়ক আৰু সেউজীয়া ৰঙৰ কাপোৰ পৰিধান কৰক।
২. ভগৱান গণেশৰ উপাসনা কৰক, ই বুদ্ধি আৰু স্থিৰতা প্ৰদান কৰিব।
৩. পৰিৱৰ্তনক ভয় নকৰিব, কিন্তু যিকোনো গুৰুত্বপূৰ্ণ সিদ্ধান্ত লোৱাৰ আগতে দুবাৰ ভাবিব।""",

        6: f"""====সংখ্যাতত্ব বৰ্ষফল - {year}====
        ব্যক্তিগত বৰ্ষ ৬: পৰিয়াল, প্ৰেম, ঘৰ আৰু দায়িত্বৰ বছৰ
=========================================================

সাধাৰণ বিৱৰণ:
যোৱা বছৰৰ অস্থিৰতা আৰু পৰিৱৰ্তনৰ পিছত, ব্যক্তিগত বৰ্ষ ৬ (শুক্ৰ গ্ৰহ) য়ে আপোনাৰ জীৱনলৈ স্থিৰতা আৰু শান্তি ঘূৰাই আনিব। এই বছৰটো মূলতঃ পৰিয়াল, প্ৰেম, আৰু গৃহকেন্দ্ৰিক। আপোনাৰ কান্ধত পৰিয়ালৰ নতুন দায়িত্ব আহিব পাৰে। ঘৰ সজোৱা, নতুন বাহন কিনা, বা পৰিয়ালৰ লগত সময় কটোৱাত আপুনি বেছি গুৰুত্ব দিব। সমাজ সেৱা আৰু আনক সহায় কৰাৰ প্ৰৱণতাও বৃদ্ধি পাব।

কেৰিয়াৰ আৰু আৰ্থিক দিশ:
আৰ্থিক দিশত এই বছৰটো অতি শুভ। কৰ্মক্ষেত্ৰত আপোনাৰ দায়িত্ববোধ প্ৰশংসিত হ'ব। কলা, ডিজাইন, চিকিৎসা বা সেৱামূলক কামৰ লগত জড়িত সকলৰ বাবে উন্নতিৰ পথ মুকলি হ'ব। ঘৰুৱা প্ৰয়োজনীয়তাৰ বাবে খৰচ বাঢ়িব পাৰে।

প্ৰেম, পৰিয়াল আৰু সম্পৰ্ক:
বিবাহৰ যোগ অতি প্ৰবল। যিসকলৰ ইতিমধ্যে বিবাহ হৈছে, তেওঁলোকৰ সংসাৰলৈ নতুন আলহী (সন্তান) অহাৰ সম্ভাৱনা আছে। পৰিয়ালৰ কোনো জেষ্ঠ ব্যক্তিৰ স্বাস্থ্যৰ যত্ন ল'বলগীয়া হ'ব পাৰে।

স্বাস্থ্য:
সাধাৰণতে স্বাস্থ্য ভাল থাকিব, কিন্তু আনৰ চিন্তা বেছিকৈ কৰাৰ বাবে মানসিক চাপ আহিব পাৰে। ডিঙি, থাইৰয়ড বা প্ৰজনন তন্ত্ৰৰ লগত জড়িত সৰু-সুৰা সমস্যা হ'ব পাৰে।

শুভ দিশ:
প্ৰেম, বিবাহ, গৃহ শান্তি, দায়িত্ববোধ, কলা আৰু সৌন্দৰ্য।

অশুভ দিশ আৰু সাৱধানতা:
আনৰ সমস্যাক নিজৰ কৰি লোৱা, অতিমাত্ৰা আৱেগিক হোৱা আৰু আধিপত্য বিস্তাৰ কৰাৰ চেষ্টা কৰা। পৰিয়ালৰ সদস্যৰ ওপৰত নিজৰ মত জাপি নিদিব।

প্ৰতিকাৰ আৰু পৰামৰ্শ:
১. মা লক্ষ্মী বা দুৰ্গাৰ আৰাধনা কৰক। শুক্ৰবাৰে বগা মিঠাই বা ক্ষীৰ দান কৰক।
২. মহিলাসকলক সন্মান কৰক আৰু পৰিষ্কাৰ-পৰিচ্ছন্ন সাজ-পোছাক পৰিধান কৰক (বগা বা গুলপীয়া ৰং শুভ)।
৩. নিজৰ প্ৰয়োজনীয়তাক আওকাণ কৰি কেৱল আনৰ বাবে জীয়াই নাথাকিব, নিজৰো যত্ন লওক।""",

        7: f"""====সংখ্যাতত্ব বৰ্ষফল - {year}====
        ব্যক্তিগত বৰ্ষ ৭: আত্মবিশ্লেষণ, আধ্যাত্মিকতা আৰু জ্ঞানৰ বছৰ
=========================================================

সাধাৰণ বিৱৰণ:
ব্যক্তিগত বৰ্ষ ৭ (কেতু গ্ৰহ) হৈছে বিশ্ৰাম, আত্মচিন্তা আৰু আধ্যাত্মিক বিকাশৰ সময়। বাহ্যিক জগতৰ দৌৰা-দৌৰিৰ পৰা আঁতৰি আহি নিজৰ ভিতৰখন জুমি চোৱাৰ এইটো উপযুক্ত সময়। জীৱনৰ প্ৰকৃত অৰ্থ বিচাৰি আপোনাৰ মনত নানা প্ৰশ্নৰ উদয় হ'ব। গৱেষণা, পঢ়া-শুনা আৰু যিকোনো বিষয়ৰ গভীৰতালৈ যোৱাৰ বাবে এই বছৰটো অতিকৈ ফলপ্ৰসূ। ভিৰৰ মাজত থকাতকৈ নিৰ্জনতাত সময় কটাবলৈ আপুনি বেছি ভাল পাব।

কেৰিয়াৰ আৰু আৰ্থিক দিশ:
আৰ্থিক দিশত এই বছৰটোৱে খুব দ্ৰুত গতি প্ৰদান নকৰে। ব্যৱসায়ত ডাঙৰ পৰিৱৰ্তন বা নতুন প্ৰকল্প হাতত লোৱাৰ পৰিৱৰ্তে, চলি থকা কামবোৰ নিখুঁত কৰাত গুৰুত্ব দিয়ক। শিক্ষাৰ্থী, গৱেষক আৰু আইটি (IT) ক্ষেত্ৰৰ লোকসকলৰ বাবে অত্যন্ত শুভ সময়।

প্ৰেম, পৰিয়াল আৰু সম্পৰ্ক:
সামাজিক জীৱন আৰু সম্পৰ্কৰ ক্ষেত্ৰত আপুনি কিছু আঁতৰি থাকিব পাৰে। আপোনাৰ নীৰৱতা আৰু একাকীত্বক পৰিয়ালৰ মানুহে ভুল বুজিব পাৰে। প্ৰিয়জনক আপোনাৰ মানসিক অৱস্থাৰ বিষয়ে বুজাই কোৱাটো দৰকাৰী।

স্বাস্থ্য:
মানসিক অৱসাদ, ডিপ্ৰেছন (Depression) বা এলাহ ভাৱ আহিব পাৰে। স্নায়ুজনিত ৰোগ বা কোনো ধৰিব নোৱাৰা ৰোগে আমনি কৰিব পাৰে। প্ৰাকৃতিক পৰিৱেশত সময় কটোৱাটো উপকাৰী।

শুভ দিশ:
গভীৰ চিন্তা, আধ্যাত্মিক জ্ঞান, ধ্যান, গৱেষণা আৰু অন্তৰ্দৃষ্টি।

অশুভ দিশ আৰু সাৱধানতা:
নিৰাশাবাদ, অতিমাত্ৰা সন্দেহৱাদী হোৱা, আৰু সমাজৰ পৰা সম্পূৰ্ণৰূপে বিচ্ছিন্ন হৈ পৰা। আৰ্থিক চুক্তিত সাৱধান হ'ব।

প্ৰতিকাৰ আৰু পৰামৰ্শ:
১. নিয়মিতভাৱে ধ্যান (Meditation) বা যোগাসন কৰক। ধৰ্মীয় স্থান দৰ্শন কৰিলে মানসিক শান্তি পাব।
২. কুকুৰক খাবলৈ দিয়ক আৰু দুখীয়া লোকক কম্বল বা গৰম কাপোৰ দান কৰক।
৩. ডাঙৰ আৰ্থিক পৰিকল্পনাসমূহ পৰৱৰ্তী বছৰলৈ পিছুৱাই দিয়াটো বুদ্ধিমানৰ কাম হ'ব।""",

        8: f"""====সংখ্যাতত্ব বৰ্ষফল - {year}====
        ব্যক্তিগত বৰ্ষ ৮: সফলতা, কৰ্মফল আৰু বিত্তীয় লাভৰ বছৰ
=========================================================

সাধাৰণ বিৱৰণ:
ব্যক্তিগত বৰ্ষ ৮ (শনি গ্ৰহ) হৈছে ক্ষমতা, অৰ্থ আৰু সাফল্যৰ বছৰ। যোৱা সাত বছৰ ধৰি আপুনি যি কঠোৰ পৰিশ্ৰম কৰি আহিছে, এই বছৰত তাৰ ফল লাভ কৰিব। ইয়াক 'কৰ্মফলৰ বছৰ' বুলিও কোৱা হয়, অৰ্থাৎ ভাল কৰ্মৰ ভাল ফল আৰু বেয়া কৰ্মৰ বেয়া ফল পোৱা যাব। আপোনাৰ আত্মবিশ্বাস তুংগত থাকিব আৰু জীৱনৰ ডাঙৰ সিদ্ধান্তবোৰ লোৱাৰ সাহস দিশাব পাৰিব। সামাজিক প্ৰতিষ্ঠা আৰু ক্ষমতা বৃদ্ধি পাব।

কেৰিয়াৰ আৰু আৰ্থিক দিশ:
কেৰিয়াৰ আৰু ব্যৱসায়ত বৃহৎ সফলতা লাভৰ যোগ আছে। পদোন্নতি, নতুন ব্যৱসায় আৰম্ভ বা ডাঙৰ আৰ্থিক চুক্তি স্বাক্ষৰ হোৱাৰ সম্ভাৱনা প্ৰবল। সম্পত্তি ক্ৰয়-বিক্ৰয়ৰ জৰিয়তে লাভৱান হ'ব। অৱশ্যে, সফলতাৰ সমান্তৰালভাৱে দায়িত্বও বহুগুণে বৃদ্ধি পাব।

প্ৰেম, পৰিয়াল আৰু সম্পৰ্ক:
কৰ্মব্যস্ততাৰ বাবে পৰিয়ালক সময় দিয়াটো কঠিন হৈ পৰিব। টকা-পইচা বা সম্পত্তিৰ বিষয়ক লৈ আত্মীয়ৰ লগত মতানৈক্য হ'ব পাৰে। ব্যৱসায়িক দৃষ্টিভংগীৰে ব্যক্তিগত সম্পৰ্কবোৰ বিচাৰ নকৰিব।

স্বাস্থ্য:
অতিৰিক্ত পৰিশ্ৰমৰ বাবে শাৰীৰিক অৱসাদ, উচ্চ ৰক্তচাপ বা হাড়ৰ সমস্যা (যেনে- কঁকালৰ বিষ) হ'ব পাৰে। কৰ্ম আৰু জিৰণিৰ মাজত সমতা ৰক্ষা কৰাটো অতি প্ৰয়োজনীয়।

শুভ দিশ:
আৰ্থিক লাভ, ব্যৱসায়িক বৃদ্ধি, নেতৃত্ব, ক্ষমতা আৰু ন্যায় বিচাৰ।

অশুভ দিশ আৰু সাৱধানতা:
অতিমাত্ৰা ভৌতিকতাবাদী হোৱা, অহংকাৰ, আৰু অন্যায় পথৰে ধন ঘটাৰ প্ৰৱণতা। আইন-কানুনৰ উলংঘন কৰিলে ডাঙৰ বিপদত পৰিব পাৰে।

প্ৰতিকাৰ আৰু পৰামৰ্শ:
১. শনি দেৱৰ আৰাধনা কৰক। শনিবাৰে সৰিয়হৰ তেলৰ চাকি জ্বলাওক আৰু শ্ৰমিক শ্ৰেণীৰ লোকক সহায় কৰক।
২. নীলা আৰু ক'লা ৰং শুভ। যিকোনো ক্ষেত্ৰতে সততা আৰু ন্যায় বজাই ৰাখক।
৩. লাভৱান হোৱা ধনৰ এটা অংশ দুখীয়া-নিচলাৰ সহায়ৰ বাবে দান কৰিব।""",

        9: f"""====সংখ্যাতত্ব বৰ্ষফল - {year}====
        ব্যক্তিগত বৰ্ষ ৯: পূৰ্ণতা, সমাপ্তি আৰু মানৱতাৰ বছৰ
=========================================================

সাধাৰণ বিৱৰণ:
ব্যক্তিগত বৰ্ষ ৯ (মংগল গ্ৰহ) হৈছে ৯ বছৰীয়া চক্ৰৰ একেবাৰে শেষৰ বছৰ। এইটো সমাপ্তি আৰু পৰিষ্কাৰ কৰাৰ সময়। আপোনাৰ জীৱনৰ যিবোৰ বস্তু, ব্যক্তি বা অভ্যাসে এতিয়া আৰু কোনো যোগাত্মক প্ৰভাৱ পেলোৱা নাই, সেইবোৰক বিদায় দিয়াৰ সময় আহি পৰিছে। এই বছৰত আপুনি পুৰণি অধ্যায়বোৰ সামৰণি মাৰি অহা বছৰৰ নতুন চক্ৰৰ (বৰ্ষ ১) বাবে সাজু হ'ব লাগিব। সমাজ সেৱা আৰু বিশ্বজনীন প্ৰেমৰ ভাৱনা জাগ্ৰত হ'ব।

কেৰিয়াৰ আৰু আৰ্থিক দিশ:
কোনো দীৰ্ঘদিনীয়া প্ৰকল্প এই বছৰত সম্পূৰ্ণ হ'ব আৰু তাৰ পৰা আৰ্থিক লাভ পাব। কিন্তু একেবাৰে নতুন আৰু দীৰ্ঘম্যাদী ব্যৱসায় বা চাকৰি এই বছৰত আৰম্ভ নকৰাই ভাল। বিদেশ যাত্ৰা বা দূৰৈৰ স্থানৰ পৰা কৰা ব্যৱসায়ত সফলতা লাভ কৰিব।

প্ৰেম, পৰিয়াল আৰু সম্পৰ্ক:
যিবোৰ সম্পৰ্কৰ ভেটি দুৰ্বল, সেইবোৰ এই বছৰত ভাঙি যাব পাৰে। আনহাতে, প্ৰকৃত সম্পৰ্কবোৰ অধিক সুদৃঢ় হ'ব। আৱেগিকভাৱে কিছু অস্থিৰতা অনুভৱ কৰিব পাৰে, কিয়নো পুৰণি স্মৃতিয়ে আমনি কৰিব পাৰে। ক্ষমাদান কৰিবলৈ শিকাটো এই বছৰৰ মূল মন্ত্ৰ।

স্বাস্থ্য:
আৱেগিক চাপৰ প্ৰভাৱ শাৰীৰিক স্বাস্থ্যত পৰিব পাৰে। ৰক্তচাপ, তেজৰ সংক্ৰমণ বা দুৰ্ঘটনাজনিত আঘাটৰ পৰা সাৱধান হ'ব। সঘনাই খং উঠা নিয়ন্ত্ৰণ কৰিব।

শুভ দিশ:
মানৱীয়তা, ক্ষমা, আধৰুৱা কামৰ সমাপ্তি, দান-ধৰ্ম আৰু বিশ্বজনীন দৃষ্টিভংগী।

অশুভ দিশ আৰু সাৱধানতা:
অতীতক খামুচি ধৰি থকা, অত্যাধিক খং, হঠকাৰিতা আৰু নিৰাশা। পুৰণি কথাক লৈ বিবাদত লিপ্ত নহ'ব।

প্ৰতিকাৰ আৰু পৰামৰ্শ:
১. হনুমান জীৰ উপাসনা কৰক। মঙলবাৰে ৰঙা বস্তু বা দাইল দান কৰক।
২. ৰক্তদান বা অনাথ আশ্ৰমত সহায় কৰাটো অতি উপকাৰী হ'ব।
৩. যি যাব বিচাৰিছে তাক যাবলৈ দিয়ক। অতীতৰ ক্ষোভ মনৰ পৰা উলিয়াই পেলাওক।""",
    }
    return predictions.get(personal_year, f"{year} চনৰ বাবে মধ্যম ফলপ্ৰদ হ'ব।")


# ═══════════════════════════════════════════════════════════════════
#  NEW: ENHANCED LO SHU GRID (Kua + Namanka included) - From VB.Net
# ═══════════════════════════════════════════════════════════════════

def calculate_enhanced_lo_shu_grid(dob: str, mulyanka: int, bhagyanka: int, namanka: int = 0, kua: int = 0) -> dict:
    """
    Enhanced Lo Shu Grid that includes Mulyanka, Bhagyanka, Kua Number, and Namanka.
    Same as VB.Net GenerateLoShuGridNew().
    """
    try:
        digits = ''.join(dob.split('-'))
    except (ValueError, IndexError):
        digits = ""

    full_numbers = digits + str(mulyanka) + str(bhagyanka) + str(kua) + str(namanka)

    counts = {i: 0 for i in range(1, 10)}
    for ch in full_numbers:
        if ch.isdigit():
            num = int(ch)
            if num > 0:
                counts[num] = counts.get(num, 0) + 1

    grid = [["", "", ""], ["", "", ""], ["", "", ""]]
    for i in range(3):
        for j in range(3):
            num = LO_SHU_GRID[i][j]
            cnt = counts.get(num, 0)
            if cnt > 0:
                grid[i][j] = str(num) * cnt  # e.g., "11" for two 1s

    missing = [n for n in range(1, 10) if counts.get(n, 0) == 0]
    present = [n for n in range(1, 10) if counts.get(n, 0) > 0]

    return {
        "grid": grid,
        "counts": counts,
        "missing": missing,
        "present": present,
        "includes_kua_namanka": True
    }
