"""
ধ্ৰুৱতৰা AI - ৰত্ন (Gemstone) ইঞ্জিন
Ratna Engine: Calculates Life Gem, Punya Gem, and Destiny Gem based on Lagna.
Also provides malefic planet effects and remedies.
"""

# ─── Rashi → Lord mapping (0-11) ───
# Same as RASHI_LORDS in panchanga
RASHI_LORDS_EN = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
]

# ─── Planet → Gemstone mapping ───
PLANET_GEMSTONE = {
    "Sun": {
        "as": "মাণিক্য (Ruby)",
        "bn": "রুবি (Ruby) বা চুনি",
        "hi": "माणिक (Ruby)",
        "en": "Ruby"
    },
    "Moon": {
        "as": "মুক্তা (Pearl)",
        "bn": "মুক্তা (Pearl)",
        "hi": "मोती (Pearl)",
        "en": "Pearl"
    },
    "Mars": {
        "as": "ৰঙা প্ৰৱাল (Red Coral)",
        "bn": "রেড কোরাল (Red Coral) বা রক্তপ্রবাল",
        "hi": "लाल मूंगा (Red Coral)",
        "en": "Red Coral"
    },
    "Mercury": {
        "as": "পান্না (Emerald)",
        "bn": "পান্না (Emerald)",
        "hi": "पन्ना (Emerald)",
        "en": "Emerald"
    },
    "Jupiter": {
        "as": "পোখৰাজ (Yellow Sapphire)",
        "bn": "পোখরাজ (Yellow Sapphire)",
        "hi": "पुखराज (Yellow Sapphire)",
        "en": "Yellow Sapphire (Pokhraj)"
    },
    "Venus": {
        "as": "হীৰা (Diamond)",
        "bn": "হীরা (Diamond)",
        "hi": "हीरा (Diamond)",
        "en": "Diamond"
    },
    "Saturn": {
        "as": "নীলম (Blue Sapphire)",
        "bn": "নীলম (Blue Sapphire)",
        "hi": "नीलम (Blue Sapphire)",
        "en": "Blue Sapphire (Neelam)"
    },
    "Rahu": {
        "as": "গোমেদ (Hessonite)",
        "bn": "গোমেদ (Hessonite)",
        "hi": "गोमेद (Hessonite)",
        "en": "Hessonite (Gomed)"
    },
    "Ketu": {
        "as": "লহসুনিয়া (Cat's Eye)",
        "bn": "লহসুনিয়া (Cat's Eye)",
        "hi": "लहसुनिया (Cat's Eye)",
        "en": "Cat's Eye (Lahsuniya)"
    },
}

# ─── Planet → Malefic Effects & Remedies (i18n) ───
MALEFIC_REMEDIES = {
    "as": {
        "title": "গ্ৰহৰ অশুভ ফল আৰু প্ৰতিকাৰ",
        "planets": {
            "Sun": {
                "name": "ৰবি (Sun)",
                "effects": "ৰবি অশুভ হলে স্থান নাশ, চক্ষুৰোগ, শিৰঃপীড়া, পিতৃৰ অশুভ, তাপজনিত কষ্ট, ব্ৰণৰোগ, আৰু প্ৰমোচন বা পদোন্নতিত বাধা আহে ।",
                "remedy": "প্ৰতিকাৰ: গ্রহ শান্তি পাঠ ।",
                "mantra": 'বীজমন্ত্র: "ওঁ হ্রীং হ্রীং সূর্যায়" ।'
            },
            "Mars": {
                "name": "মংগল (Mars)",
                "effects": "মংগল অশুভ হলে ৰক্তদুষিত কষ্ট, অস্ত্ৰোপ্ৰচাৰ, অস্ত্রাঘাত, আকস্মিক দুর্ঘটনা, অস্ত্রাগ্নি যান্ত্রদি ভয়, শৌচ কিম্বা দন্তপীড়া, আৰু উদোগত অশুভ ফল পোৱা যায় ।",
                "remedy": "প্ৰতিকাৰ: গ্রহ শান্তি পাঠ ।",
                "mantra": 'বীজমন্ত্র: "ওঁ হুং শ্রীং মঙ্গলায়" ।'
            },
            "Saturn": {
                "name": "শনি (Saturn)",
                "effects": "শনি অশুভ হলে মৃত্যু তুল্য কষ্ট, স্বাস্থ্যক্ষতি, বৃথা ভ্রমণ, মামলা মোকদ্দমাত জৰিত হোৱা, মিছা অপবাদ, বন্ধন ভয়, শাৰিৰীক ক্লেশ, বন্ধু বিচ্ছেদ, আত্মীয় হানি, ভুল বুজা বুজি, লোৰ দ্বাৰা আক্ৰান্ত, অস্ত্রাগ্নি যানাদি ভয়, ৰোগ বৃদ্ধি, আৰু অর্থহানি হব পাৰে ।",
                "remedy": "প্ৰতিকাৰ: শনি বাৰ পালন আৰু গ্রহ শান্তি পাঠ ।",
                "mantra": 'বীজমন্ত্র: "ওঁ ঐং হ্রীং শ্রীং শনৈশ্চৰায়" ।'
            },
            "Rahu": {
                "name": "ৰাহু (Rahu)",
                "effects": "ৰাহু অশুভ হলে স্বাস্থ্যহানি, হতাশা, ক্লিষ্টতা, দুঃচিন্তা, বৃথা ভ্রমণ, শত্রুভয়, কার্য্যহানি, বাধা, পতন কিম্বা আঘাত কষ্ট, উদৰ ৰোগ, আৰু শয়নবিলাসী হয় ।",
                "remedy": "প্ৰতিকাৰ: চণ্ডাল ভোজন আৰু গ্রহ শান্তি পাঠ ।",
                "mantra": 'বীজমন্ত্র: "ওঁ ঐং হ্রীং ৰাহবে" ।'
            },
            "Ketu": {
                "name": "কেতু (Ketu)",
                "effects": "কেতু অশুভ হলে অর্থব্যয়, অপমান, আয়হ্রাস, ভুল বুজা বুজি, চৰ্মৰোগ, চঞ্চলতা বৃদ্ধি, বিচ্ছেদ, আকস্মিক দুর্ঘটনা, আৰু মানসিক উদ্বিগ্নতা (টেনচন) বৃদ্ধি পায় ।",
                "remedy": "প্ৰতিকাৰ: গ্রহ শান্তি পাঠ ।",
                "mantra": 'বীজমন্ত্র: "ওঁ হ্রীং ঐং কেতবে" ।'
            },
        },
        "closing": "|| ভগৱানে আপোনাৰ কল্যাণ কৰিব ||"
    },
    "bn": {
        "title": "গ্রহের অশুভ ফল এবং প্রতিকার",
        "planets": {
            "Sun": {
                "name": "রবি (Sun)",
                "effects": "রবি অশুভ হলে স্থান নাশ, চক্ষুরোগ, শিরঃপীড়া (মাথা ব্যথা), পিতার অশুভ, তাপজনিত কষ্ট, ব্রণরোগ এবং পদোন্নতিতে (প্রমোশন) বাধা আসে ।",
                "remedy": "প্রতিকার: গ্রহ শান্তি পাঠ ।",
                "mantra": 'বীজমন্ত্র: "ওঁ হ্রীং হ্রীং সূর্যায়" ।'
            },
            "Mars": {
                "name": "মঙ্গল (Mars)",
                "effects": "মঙ্গল অশুভ হলে রক্তদূষিত কষ্ট, অস্ত্রোপচার, অস্ত্রাঘাত, আকস্মিক দুর্ঘটনা, অস্ত্র ও অগ্নিজনিত বা যন্ত্রপাতির ভয়, শৌচ বা দন্তপীড়া (দাঁতের ব্যথা), এবং উদ্যোগে অশুভ ফল পাওয়া যায় ।",
                "remedy": "প্রতিকার: গ্রহ শান্তি পাঠ ।",
                "mantra": 'বীজমন্ত্র: "ওঁ হুং শ্রীং মঙ্গলায়" ।'
            },
            "Saturn": {
                "name": "শনি (Saturn)",
                "effects": "শনি অশুভ হলে মৃত্যুতুল্য কষ্ট, স্বাস্থ্যক্ষতি, বৃথা ভ্রমণ, মামলা-মোকদ্দমায় জড়িত হওয়া, মিথ্যা অপবাদ, বন্ধন ভয়, শারীরিক ক্লেশ, বন্ধু বিচ্ছেদ, আত্মীয় হানি, ভুল বোঝাবুঝি, লোহার দ্বারা আঘাতপ্রাপ্ত হওয়া, অস্ত্র-অগ্নি-যানবাহন ইত্যাদির ভয়, রোগ বৃদ্ধি এবং অর্থহানি হতে পারে ।",
                "remedy": "প্রতিকার: শনিবার পালন এবং গ্রহ শান্তি পাঠ ।",
                "mantra": 'বীজমন্ত্র: "ওঁ ঐং হ্রীং শ্রীং শনৈশ্চরায়" ।'
            },
            "Rahu": {
                "name": "রাহু (Rahu)",
                "effects": "রাহু অশুভ হলে স্বাস্থ্যহানি, হতাশা, ক্লান্তি/কষ্ট, দুশ্চিন্তা, বৃথা ভ্রমণ, শত্রুভয়, কার্যহানি, বাধা, পতন বা আঘাতের কষ্ট , উদর রোগ এবং শয়নবিলাসী হয় ।",
                "remedy": "প্রতিকার: চণ্ডাল ভোজন এবং গ্রহ শান্তি পাঠ ।",
                "mantra": 'বীজমন্ত্র: "ওঁ ঐং হ্রীং রাহবে" ।'
            },
            "Ketu": {
                "name": "কেতু (Ketu)",
                "effects": "কেতু অশুভ হলে অর্থব্যয়, অপমান, আয়হ্রাস, ভুল বোঝাবুঝি, চর্মরোগ, চঞ্চলতা বৃদ্ধি, বিচ্ছেদ, আকস্মিক দুর্ঘটনা এবং মানসিক উদ্বিগ্নতা (টেনশন) বৃদ্ধি পায় ।",
                "remedy": "প্রতিকার: গ্রহ শান্তি পাঠ ।",
                "mantra": 'বীজমন্ত্র: "ওঁ হ্রীং ঐং কেতবে" ।'
            },
        },
        "closing": "|| ভগবান আপনার কল্যাণ করুন ||"
    },
    "hi": {
        "title": "ग्रहों के अशुभ फल और उनके उपाय (प्रतिकार)",
        "planets": {
            "Sun": {
                "name": "रवि (Sun)",
                "effects": "सूर्य के अशुभ होने पर स्थान का नाश, नेत्र रोग, सिरदर्द, पिता के लिए अशुभ, गर्मी से संबंधित कष्ट, मुंहासे (त्वचा रोग), और पदोन्नति (प्रमोशन) में बाधा आती है ।",
                "remedy": "उपाय: ग्रह शांति पाठ ।",
                "mantra": 'बीज मंत्र: "ॐ ह्रीं ह्रीं सूर्याय" ।'
            },
            "Mars": {
                "name": "मंगल (Mars)",
                "effects": "मंगल के अशुभ होने पर रक्त दूषित कष्ट, सर्जरी (ऑपरेशन), हथियारों से चोट, अचानक दुर्घटनाएं, हथियार-आग-मशीनरी आदि का डर, शौच या दांत का दर्द, और उद्यम (व्यवसाय) में अशुभ फल मिलते हैं ।",
                "remedy": "उपाय: ग्रह शांति पाठ ।",
                "mantra": 'बीज मंत्र: "ॐ हुं श्रीं मंगलाय" ।'
            },
            "Saturn": {
                "name": "शनि (Saturn)",
                "effects": "शनि के अशुभ होने पर मृत्यु के समान कष्ट, स्वास्थ्य की हानि, व्यर्थ की यात्रा, मुकदमेबाजी में शामिल होना, झूठा आरोप, बंधन (कैद) का डर, शारीरिक कष्ट, दोस्तों से अलगाव, रिश्तेदारों का नुकसान, गलतफहमी, लोहे से चोट, हथियार-आग-वाहनों का डर, बीमारियों में वृद्धि, और धन की हानि होती है ।",
                "remedy": "उपाय: शनिवार का पालन और ग्रह शांति पाठ ।",
                "mantra": 'बीज मंत्र: "ॐ ऐं ह्रीं श्रीं शनैश्चराय" ।'
            },
            "Rahu": {
                "name": "राहु (Rahu)",
                "effects": "राहु के अशुभ होने पर स्वास्थ्य की हानि, निराशा, थकान/कष्ट, चिंता, व्यर्थ की यात्रा, दुश्मनों का डर, कार्य में हानि और बाधा, और गिरने या चोट लगने का कष्ट होता है । इसके अलावा पेट के रोग होते हैं और व्यक्ति सोने का शौकीन (आलसी) हो जाता है ।",
                "remedy": "उपाय: चांडाल भोजन और ग्रह शांति पाठ ।",
                "mantra": 'बीज मंत्र: "ॐ ऐं ह्रीं राहवे" ।'
            },
            "Ketu": {
                "name": "केतु (Ketu)",
                "effects": "केतु के अशुभ होने पर धन का खर्च, अपमान, आय में कमी, गलतफहमी, त्वचा रोग, चंचलता में वृद्धि, अलगाव, अचानक दुर्घटनाएं और मानसिक चिंता (टेंशन) बढ़ती है ।",
                "remedy": "उपाय: ग्रह शांति पाठ ।",
                "mantra": 'बीज मंत्र: "ॐ ह्रीं ऐं केतवे" ।'
            },
        },
        "closing": "|| भगवान आपका कल्याण करें ||"
    },
    "en": {
        "title": "Malefic Effects of Planets and Remedies",
        "planets": {
            "Sun": {
                "name": "Sun (Ravi)",
                "effects": "If the Sun is malefic, it causes loss of position, eye diseases, headaches, inauspiciousness for the father, suffering due to heat, acne/pimples, and obstacles in promotion.",
                "remedy": "Remedy: Graha Shanti Path (Planetary peace recitation).",
                "mantra": 'Bija Mantra: "Om Hreem Hreem Suryaya"'
            },
            "Mars": {
                "name": "Mars (Mangal)",
                "effects": "If Mars is malefic, it causes blood-related suffering, surgeries, injuries from weapons, sudden accidents, fear of weapons/fire/machinery, bowel or dental pain, and inauspicious results in enterprise.",
                "remedy": "Remedy: Graha Shanti Path.",
                "mantra": 'Bija Mantra: "Om Hung Shreem Mangalaya"'
            },
            "Saturn": {
                "name": "Saturn (Shani)",
                "effects": "If Saturn is malefic, it causes death-like suffering, loss of health, useless wandering, involvement in lawsuits, false accusations, fear of confinement, physical distress, separation from friends, loss of relatives, misunderstandings, attacks by iron, fear of weapons/fire/vehicles, increase in diseases, and loss of wealth.",
                "remedy": "Remedy: Observing Saturday fasting/rituals and Graha Shanti Path.",
                "mantra": 'Bija Mantra: "Om Aing Hreem Shreem Shanaishcharaya"'
            },
            "Rahu": {
                "name": "Rahu",
                "effects": "If Rahu is malefic, it causes loss of health, frustration, fatigue, anxiety, useless wandering, fear of enemies, loss of work, obstacles, suffering from falls or injuries, stomach diseases, and makes one fond of sleeping (lethargic).",
                "remedy": "Remedy: Chandal Bhojan (feeding the poor/outcasts) and Graha Shanti Path.",
                "mantra": 'Bija Mantra: "Om Aing Hreem Rahave"'
            },
            "Ketu": {
                "name": "Ketu",
                "effects": "If Ketu is malefic, it causes financial expenditure, insults, decrease in income, misunderstandings, skin diseases, increased restlessness, separation, sudden accidents, and mental anxiety (tension).",
                "remedy": "Remedy: Graha Shanti Path.",
                "mantra": 'Bija Mantra: "Om Hreem Aing Ketave"'
            },
        },
        "closing": "|| May God bless you ||"
    }
}

# ─── Ratna Descriptions (i18n) ───
RATNA_DESCRIPTIONS = {
    "as": {
        "title": "ৰত্নৰ বিৱৰণ আৰু প্ৰভাৱ",
        "life_gem": {
            "label": "জীৱন ৰত্ন (Life Gem)",
            "desc": "জীৱন ৰত্ন ধাৰন কৰিলে যিকোনো বাধাৰ পৰা বহুত পৰিমাণে পৰিত্ৰাণ পাব পাৰি আৰু ই জাতকক প্ৰসন্ন তথা সফল হোৱাত সহায় কৰে । সাধাৰণতে এই ৰত্ন ব্যক্তিৰ সৰ্বাংগীণ উন্নতিৰ কাৰণে ধাৰন কৰা হয় । আপোনাৰ ক্ষেত্ৰত জীৱন ৰত্ন হৈছে {gemstone} ।"
        },
        "punya_gem": {
            "label": "পুণ্য ৰত্ন (Punya Gem)",
            "desc": "আমাৰ জীৱনটো হৈছে পৰিশ্ৰম আৰু ভাগ্যৰ দ্বাৰা হোৱা সংমিশ্রণ । এই ৰত্ন ধাৰন কৰি সকলো কাম-কাজক আপোনাৰ সপক্ষে কাম কৰিবলৈ দিব পাৰি । বিদ্যা-বুদ্ধিৰ উপৰিও সকলো ধৰনৰ সফলতাক এই ৰত্নই সহজতে আহৰন কৰাত সহায় কৰিব । আপোনাৰ ক্ষেত্ৰত পুণ্য ৰত্ন হৈছে {gemstone} ।"
        },
        "destiny_gem": {
            "label": "ভাগ্য ৰত্ন (Destiny Gem)",
            "desc": "ভাগ্য ৰত্ন ধাৰন কৰিলে ভাগ্য স্থান ভাল হয় আৰু সকলো ক্ষেত্ৰতে উন্নতি প্ৰপ্তিৰ ক্ষেত্ৰত অৰিহনা যোগায় । যেতিয়াই আপোনাক ভাগ্যৰ দৰকাৰ হয়, এই ৰত্নই সেই সময়ৰ নিয়তিক আপোনাৰ সপক্ষে কাম কৰোৱাত সহায়ক হব । এই ৰত্ন অতি দৰকাৰী ৰত্ন আৰু আপোনাৰ ক্ষেত্ৰত ভাগ্য ৰত্ন হৈছে {gemstone} ।"
        }
    },
    "bn": {
        "title": "রত্নের বিবরণ এবং প্রভাব",
        "life_gem": {
            "label": "জীবন রত্ন (Life Gem)",
            "desc": "জীবন রত্ন ধারণ করলে যেকোনো বাধা থেকে অনেকাংশে পরিত্রাণ পাওয়া যায় এবং এটি জাতককে প্রসন্ন ও সফল হতে সাহায্য করে । সাধারণত এই রত্ন ব্যক্তির সর্বাঙ্গীণ উন্নতির জন্য ধারণ করা হয়, এবং আপনার ক্ষেত্রে জীবন রত্ন হলো {gemstone} ।"
        },
        "punya_gem": {
            "label": "পুণ্য রত্ন (Punya Gem)",
            "desc": "আমাদের জীবন হলো পরিশ্রম এবং ভাগ্যের সংমিশ্রণ । এই রত্ন ধারণ করে সমস্ত কাজকর্মকে আপনার সপক্ষে কাজ করতে দিন । বিদ্যা-বুদ্ধি ছাড়াও সব ধরনের সাফল্য এই রত্ন সহজে অর্জন করতে সাহায্য করবে, এবং আপনার ক্ষেত্রে পুণ্য রত্ন হলো {gemstone} ।"
        },
        "destiny_gem": {
            "label": "ভাগ্য রত্ন (Destiny Gem)",
            "desc": "ভাগ্য রত্ন ধারণ করলে ভাগ্য স্থান ভালো হয় এবং সব ক্ষেত্রে উন্নতি লাভের ক্ষেত্রে সাহায্য করে । যখনই আপনার ভাগ্যের দরকার হবে, এই রত্ন সেই সময়ের নিয়তিকে আপনার সপক্ষে কাজ করাতে সহায়ক হবে । এই রত্নটি অত্যন্ত প্রয়োজনীয় রত্ন, এবং আপনার ক্ষেত্রে ভাগ্য রত্ন হলো {gemstone} ।"
        }
    },
    "hi": {
        "title": "रत्नों का विवरण और प्रभाव",
        "life_gem": {
            "label": "जीवन रत्न (Life Gem)",
            "desc": "जीवन रत्न धारण करने से किसी भी प्रकार की बाधा से काफी हद तक छुटकारा पाया जा सकता है और यह जातक को प्रसन्न और सफल होने में मदद करेगा । आमतौर पर यह रत्न व्यक्ति की सर्वांगीण उन्नति के लिए धारण किया जाता है । आपके लिए जीवन रत्न {gemstone} है ।"
        },
        "punya_gem": {
            "label": "पुण्य रत्न (Punya Gem)",
            "desc": "हमारा जीवन परिश्रम और भाग्य का मिश्रण है । इस रत्न को धारण करके सभी कार्यों को अपने पक्ष में काम करने दें । विद्या और बुद्धि के अलावा, यह रत्न सभी प्रकार की सफलता को आसानी से प्राप्त करने में मदद करेगा । आपके लिए पुण्य रत्न {gemstone} है ।"
        },
        "destiny_gem": {
            "label": "भाग्य रत्न (Destiny Gem)",
            "desc": "भाग्य रत्न धारण करने से भाग्य स्थान अच्छा होता है और यह सभी क्षेत्रों में उन्नति प्राप्त करने में योगदान देता है । जब भी आपको भाग्य की आवश्यकता होती है, यह रत्न उस समय की नियति को आपके पक्ष में काम कराने में सहायक होगा । यह बहुत ही आवश्यक रत्न है और आपके लिए भाग्य रत्न {gemstone} है ।"
        }
    },
    "en": {
        "title": "Gemstone Details and Effects",
        "life_gem": {
            "label": "Life Gem (Jivan Ratna)",
            "desc": "Wearing the Life Gem can provide relief from many obstacles to a great extent, and it will help the native become happy and successful. Generally, this gemstone is worn for the all-round development of a person. In your case, the Life Gem is {gemstone}."
        },
        "punya_gem": {
            "label": "Punya Gem (Gem of Merit)",
            "desc": "Our life is a combination of hard work and luck. By wearing this gemstone, you allow all your tasks to work in your favor. In addition to knowledge and intellect, this gemstone will help you easily achieve all kinds of success. In your case, the Punya Gem is {gemstone}."
        },
        "destiny_gem": {
            "label": "Destiny Gem (Bhagya Ratna)",
            "desc": "Wearing the Destiny Gem improves the house of fortune and contributes to achieving progress in all fields. Whenever you need luck, this gemstone will be helpful in making destiny work in your favor at that time. This is a very important gemstone. In your case, the Destiny Gem is {gemstone}."
        }
    }
}


def get_ratna_data(asc_rasi_idx: int, lang: str = 'as') -> dict:
    """
    Calculate Life Gem, Punya Gem, and Destiny Gem based on Lagna (ascendant).
    
    Args:
        asc_rasi_idx: Ascendant rashi index (0-11)
        lang: language code ('as', 'bn', 'hi', 'en')
    
    Returns:
        dict with life_gem, punya_gem, destiny_gem, and malefic_remedies
    """
    if asc_rasi_idx < 0 or asc_rasi_idx > 11:
        asc_rasi_idx = 0
    
    # Lagna Lord (1st house lord)
    lagna_lord_en = RASHI_LORDS_EN[asc_rasi_idx]
    
    # 5th Lord: 5th house from lagna = (lagna_idx + 4) % 12
    fifth_house_idx = (asc_rasi_idx + 4) % 12
    fifth_lord_en = RASHI_LORDS_EN[fifth_house_idx]
    
    # 9th Lord: 9th house from lagna = (lagna_idx + 8) % 12
    ninth_house_idx = (asc_rasi_idx + 8) % 12
    ninth_lord_en = RASHI_LORDS_EN[ninth_house_idx]
    
    # Get gemstone names in target language
    life_gem = PLANET_GEMSTONE.get(lagna_lord_en, {}).get(lang, lagna_lord_en)
    punya_gem = PLANET_GEMSTONE.get(fifth_lord_en, {}).get(lang, fifth_lord_en)
    destiny_gem = PLANET_GEMSTONE.get(ninth_lord_en, {}).get(lang, ninth_lord_en)
    
    # Get descriptions in target language
    desc_data = RATNA_DESCRIPTIONS.get(lang, RATNA_DESCRIPTIONS['as'])
    
    life_desc = desc_data['life_gem']['desc'].replace('{gemstone}', life_gem)
    punya_desc = desc_data['punya_gem']['desc'].replace('{gemstone}', punya_gem)
    destiny_desc = desc_data['destiny_gem']['desc'].replace('{gemstone}', destiny_gem)
    
    # Get malefic remedies in target language
    remedies_data = MALEFIC_REMEDIES.get(lang, MALEFIC_REMEDIES['as'])
    
    return {
        'lagna_lord_en': lagna_lord_en,
        'fifth_lord_en': fifth_lord_en,
        'ninth_lord_en': ninth_lord_en,
        'life_gem': life_gem,
        'punya_gem': punya_gem,
        'destiny_gem': destiny_gem,
        'life_gem_label': desc_data['life_gem']['label'],
        'punya_gem_label': desc_data['punya_gem']['label'],
        'destiny_gem_label': desc_data['destiny_gem']['label'],
        'life_gem_desc': life_desc,
        'punya_gem_desc': punya_desc,
        'destiny_gem_desc': destiny_desc,
        'ratna_title': desc_data['title'],
        'remedies_title': remedies_data['title'],
        'remedies_planets': remedies_data['planets'],
        'remedies_closing': remedies_data['closing'],
    }


def build_ratna_html(asc_rasi_idx: int, lang: str = 'as') -> str:
    """
    Build HTML for the Ratna (Gemstone) section for web page and PDF.
    
    Args:
        asc_rasi_idx: Ascendant rashi index (0-11)
        lang: language code ('as', 'bn', 'hi', 'en')
    
    Returns:
        HTML string with gemstone details and malefic remedies.
    """
    data = get_ratna_data(asc_rasi_idx, lang)
    
    # CSS
    css = """
    <style>
        .ratna-container { font-family: 'Noto Sans Bengali', 'Noto Sans Devanagari', 'Arial', sans-serif; }
        .ratna-section-title { text-align:center; font-size:1.15rem; font-weight:800; color:#5B3E96; margin-bottom:16px; }
        .ratna-gem-cards { display:grid; grid-template-columns:repeat(3, 1fr); gap:14px; margin-bottom:20px; }
        @media (max-width:768px) { .ratna-gem-cards { grid-template-columns:1fr; } }
        .ratna-gem-card { border-radius:12px; padding:18px 16px; text-align:center; box-shadow:0 4px 16px rgba(0,0,0,0.06); }
        .ratna-gem-card.life { background:linear-gradient(135deg, #FFF3E0, #FFE0B2); border:2px solid #FF9800; }
        .ratna-gem-card.punya { background:linear-gradient(135deg, #E8F5E9, #C8E6C9); border:2px solid #4CAF50; }
        .ratna-gem-card.destiny { background:linear-gradient(135deg, #E3F2FD, #BBDEFB); border:2px solid #2196F3; }
        .ratna-gem-icon { font-size:2rem; margin-bottom:6px; }
        .ratna-gem-label { font-size:0.9rem; font-weight:700; color:#333; margin-bottom:4px; }
        .ratna-gem-name { font-size:1rem; font-weight:800; color:#1a237e; margin-bottom:8px; }
        .ratna-gem-desc { font-size:0.8rem; color:#555; line-height:1.6; text-align:justify; }
        .ratna-remedies-title { text-align:center; font-size:1.1rem; font-weight:800; color:#C62828; margin:24px 0 16px; }
        .ratna-remedy-card { background:#FFF; border-radius:10px; padding:14px 16px; margin-bottom:10px; border:1px solid #e0e0e0; box-shadow:0 2px 8px rgba(0,0,0,0.04); }
        .ratna-remedy-planet { font-size:0.9rem; font-weight:700; color:#1a237e; margin-bottom:6px; }
        .ratna-remedy-effects { font-size:0.8rem; color:#555; line-height:1.6; margin-bottom:6px; }
        .ratna-remedy-solution { font-size:0.8rem; color:#2E7D32; font-weight:600; margin-bottom:4px; }
        .ratna-remedy-mantra { font-size:0.78rem; color:#6A1B9A; font-weight:600; font-style:italic; }
        .ratna-closing { text-align:center; font-size:0.9rem; font-weight:700; color:#5B3E96; margin-top:20px; padding:12px; }
    </style>
    """
    
    html = [css]
    html.append('<div class="ratna-container">')
    
    # ── Gemstone Section ──
    html.append(f'<div class="ratna-section-title">💎 {data["ratna_title"]}</div>')
    html.append('<div class="ratna-gem-cards">')
    
    # Life Gem
    html.append(f'''<div class="ratna-gem-card life">
        <div class="ratna-gem-icon">❤️</div>
        <div class="ratna-gem-label">{data["life_gem_label"]}</div>
        <div class="ratna-gem-name">{data["life_gem"]}</div>
        <div class="ratna-gem-desc">{data["life_gem_desc"]}</div>
    </div>''')
    
    # Punya Gem
    html.append(f'''<div class="ratna-gem-card punya">
        <div class="ratna-gem-icon">🌟</div>
        <div class="ratna-gem-label">{data["punya_gem_label"]}</div>
        <div class="ratna-gem-name">{data["punya_gem"]}</div>
        <div class="ratna-gem-desc">{data["punya_gem_desc"]}</div>
    </div>''')
    
    # Destiny Gem
    html.append(f'''<div class="ratna-gem-card destiny">
        <div class="ratna-gem-icon">🔮</div>
        <div class="ratna-gem-label">{data["destiny_gem_label"]}</div>
        <div class="ratna-gem-name">{data["destiny_gem"]}</div>
        <div class="ratna-gem-desc">{data["destiny_gem_desc"]}</div>
    </div>''')
    
    html.append('</div>')
    
    # ── Malefic Remedies Section ──
    html.append(f'<div class="ratna-remedies-title">⚠️ {data["remedies_title"]}</div>')
    
    malefic_order = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
    for planet_key in malefic_order:
        planet_data = data["remedies_planets"].get(planet_key, {})
        if not planet_data:
            continue
        html.append(f'''<div class="ratna-remedy-card">
            <div class="ratna-remedy-planet">🪐 {planet_data["name"]}</div>
            <div class="ratna-remedy-effects">{planet_data["effects"]}</div>
            <div class="ratna-remedy-solution">{planet_data["remedy"]}</div>
            <div class="ratna-remedy-mantra">{planet_data["mantra"]}</div>
        </div>''')
    
    html.append(f'<div class="ratna-closing">{data["remedies_closing"]}</div>')
    html.append('</div>')
    
    return "\n".join(html)
