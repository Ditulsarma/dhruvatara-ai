"""
ধ্ৰুৱতৰা AI - কৃত্ৰিম বুদ্ধিমত্তা বিশ্লেষণ ইঞ্জিন
AI Interpretation Engine: Generates personalized Assamese astrology interpretations
based on planetary positions, doshas, yogas, dasha periods, and gemstone recommendations.
"""

# ৰাশিৰ অধিপতি গ্ৰহ (0-indexed: মেষ=0 ... মীন=11)
RASHI_LORDS = {
    0: "মংগল", 1: "শুক্ৰ", 2: "বুধ", 3: "চন্দ্ৰ",
    4: "ৰবি", 5: "বুধ", 6: "শুক্ৰ", 7: "মংগল",
    8: "বৃহস্পতি", 9: "শনি", 10: "শনি", 11: "বৃহস্পতি"
}

RASHI_NAMES = ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"]

# ৰত্ন পৰামৰ্শ
GEMSTONES = {
    "ৰবি": "মাণিক্য (Ruby)",
    "চন্দ্ৰ": "মুকুটা (Pearl)",
    "মংগল": "ৰক্ত প্ৰবাল (Coral)",
    "বুধ": "পান্না (Emerald)",
    "বৃহস্পতি": "পোখৰাজ (Yellow Sapphire)",
    "শুক্ৰ": "হীৰা (Diamond)",
    "শনি": "নীলম (Blue Sapphire)",
    "ৰাহু": "গোমেধ (Hessonite)",
    "কেতু": "কেটচ্ আাই (Cat's Eye)",
}

# বীজ মন্ত্ৰ
BEEJA_MANTRAS = {
    "ৰবি": "ওঁ হ্ৰাং হ্ৰীং হ্ৰৌং সঃ সূৰ্যায় নমঃ",
    "চন্দ্ৰ": "ওঁ শ্ৰাং শ্ৰীং শ্ৰৌং সঃ চন্দ্ৰমসে নমঃ",
    "মংগল": "ওঁ ক্ৰাং ক্ৰীং ক্ৰৌং সঃ ভৌমায় নমঃ",
    "বুধ": "ওঁ ব্ৰাং ব্ৰীং ব্ৰৌং সঃ বুধায় নমঃ",
    "বৃহস্পতি": "ওঁ হ্ৰাং হ্ৰীং হ্ৰৌং সঃ বৃহস্পতয়ে নমঃ",
    "শুক্ৰ": "ওঁ দ্ৰাং দ্ৰীং দ্ৰৌং সঃ শুক্ৰায় নমঃ",
    "শনি": "ওঁ শ্ৰাং শ্ৰীং শ্ৰৌং সঃ শনৈশ্চৰায় নমঃ",
    "ৰাহু": "ওঁ ভ্ৰাং ভ্ৰীং ভ্ৰৌং সঃ ৰাহবে নমঃ",
    "কেতু": "ওঁ স্ত্ৰাং স্ত্ৰীং স্ত্ৰৌং সঃ কেতবে নমঃ",
}


def get_rasi_interpretation(planet_name: str, rasi_name: str) -> str:
    """Get interpretation for a planet in a specific rashi.
    Args: planet_name (গ্ৰহৰ নাম), rasi_name (ৰাশিৰ নাম)
    """
    interpretations = {
        ("ৰবি", "মেষ"): "ৰবি মেষ ৰাশিত উচ্চ ৰাশিত অৱস্থান কৰিছে। আপুনি স্বাভিমানী, নেতৃত্বগুণ সম্পন্ন, আৰু প্ৰশাসনিক দক্ষতাৰে সমৃদ্ধ।",
        ("ৰবি", "সিংহ"): "ৰবি নিজ ৰাশিত অৱস্থান কৰি আপোনাক ৰাজকীয় ব্যক্তিত্ব, আত্মবিশ্বাস, আৰু সৃষ্টিশীলতা প্ৰদান কৰিছে।",
        ("ৰবি", "তুলা"): "ৰবি তুলা ৰাশিত নীচ ৰাশিত। আপুনি সম্পৰ্ক আৰু সহযোগিতাৰ ওপৰত গুৰুত্ব দিয়ে, কিন্তু আত্মবিশ্বাসৰ অভাৱ অনুভৱ কৰিব পাৰে।",
        ("চন্দ্ৰ", "বৃষ"): "চন্দ্ৰ বৃষ ৰাশিত উচ্চ ৰাশিত। আপুনি মানসিকভাৱে স্থিৰ, ধৈৰ্যশীল, আৰু সুখী জীৱন কটায়।",
        ("চন্দ্ৰ", "কৰ্কট"): "চন্দ্ৰ নিজ ৰাশিত অৱস্থান কৰি আপোনাক সংবেদনশীল, যত্নশীল, আৰু পাৰিবাৰিক মূল্যবোধ সম্পন্ন কৰি তুলিছে।",
        ("চন্দ্ৰ", "বৃশ্চিক"): "চন্দ্ৰ বৃশ্চিক ৰাশিত নীচ ৰাশিত। আপুনি গভীৰ অনুভূতিৰ অধিকাৰী, কিন্তু মানসিক অস্থিৰতা অনুভৱ কৰিব পাৰে।",
        ("মংগল", "মকৰ"): "মংগল মকৰ ৰাশিত উচ্চ ৰাশিত। আপুনি অত্যন্ত পৰিশ্ৰমী, উচ্চাকাংক্ষী, আৰু কৰ্মঠ ব্যক্তি।",
        ("মংগল", "মেষ"): "মংগল নিজ ৰাশিত অৱস্থান কৰি আপোনাক সাহসী, ক্ৰীড়াপ্ৰিয়, আৰু দুঃসাহসিক কৰি তুলিছে।",
        ("মংগল", "কৰ্কট"): "মংগল কৰ্কট ৰাশিত নীচ ৰাশিত। আপুনি আৱেগিকভাৱে সংবেদনশীল, কিন্তু সাহস আৰু কৰ্মস্পৃহাত কিছু অভাৱ অনুভৱ কৰিব পাৰে।",
        ("বুধ", "কন্যা"): "বুধ কন্যা ৰাশিত উচ্চ ৰাশিত। আপুনি বিশ্লেষণাত্মক, বুদ্ধিমান, আৰু পৰিপাটি কাম কৰাত পাকৈত।",
        ("বুধ", "মিথুন"): "বুধ নিজ ৰাশিত অৱস্থান কৰি আপোনাক বাক্পটু, বুদ্ধিদীপ্ত, আৰু যোগাযোগত পাৰদৰ্শী কৰি তুলিছে।",
        ("বুধ", "মীন"): "বুধ মীন ৰাশিত নীচ ৰাশিত। আপুনি কল্পনাপ্ৰৱণ, কিন্তু যুক্তিনিষ্ঠ চিন্তাত কিছু অসুবিধা অনুভৱ কৰিব পাৰে।",
        ("বৃহস্পতি", "কৰ্কট"): "বৃহস্পতি কৰ্কট ৰাশিত উচ্চ ৰাশিত। আপুনি জ্ঞানী, দয়ালু, আৰু আধ্যাত্মিকভাৱে উন্নত ব্যক্তি।",
        ("বৃহস্পতি", "ধনু"): "বৃহস্পতি নিজ ৰাশিত অৱস্থান কৰি আপোনাক ধাৰ্মিক, আশাবাদী, আৰু জ্ঞানপিপাসু কৰি তুলিছে।",
        ("বৃহস্পতি", "মকৰ"): "বৃহস্পতি মকৰ ৰাশিত নীচ ৰাশিত। আপুনি পৰিশ্ৰমী, কিন্তু জ্ঞান আৰু ভাগ্যৰ ক্ষেত্ৰত কিছু বাধাৰ সন্মুখীন হ'ব পাৰে।",
        ("শুক্ৰ", "মীন"): "শুক্ৰ মীন ৰাশিত উচ্চ ৰাশিত। আপুনি কলাপ্ৰিয়, ৰোমাণ্টিক, আৰু সৌন্দৰ্য্যবোধ সম্পন্ন।",
        ("শুক্ৰ", "তুলা"): "শুক্ৰ নিজ ৰাশিত অৱস্থান কৰি আপোনাক আকৰ্ষণীয়, কূটনীতিজ্ঞ, আৰু বিলাসী কৰি তুলিছে।",
        ("শুক্ৰ", "কন্যা"): "শুক্ৰ কন্যা ৰাশিত নীচ ৰাশিত। আপুনি পৰিপাটি আৰু সেৱাভাৱী, কিন্তু প্ৰেম আৰু বিলাসিতাত কিছু অভাৱ অনুভৱ কৰিব পাৰে।",
        ("শনি", "তুলা"): "শনি তুলা ৰাশিত উচ্চ ৰাশিত। আপুনি ন্যায়পৰায়ণ, ধৈৰ্যশীল, আৰু দীৰ্ঘম্যাদী পৰিকল্পনাত পাৰদৰ্শী।",
        ("শনি", "মকৰ"): "শনি নিজ ৰাশিত অৱস্থান কৰি আপোনাক শৃংখলাবদ্ধ, দায়িত্বশীল, আৰু পৰিশ্ৰমী কৰি তুলিছে।",
        ("শনি", "মেষ"): "শনি মেষ ৰাশিত নীচ ৰাশিত। আপুনি সাহসী, কিন্তু ধৈৰ্য্য আৰু শৃংখলাৰ ক্ষেত্ৰত কিছু অসুবিধা অনুভৱ কৰিব পাৰে।",
    }

    key = (planet_name, rasi_name)
    if key in interpretations:
        return interpretations[key]

    generic = {
        "ৰবি": f"ৰবি {rasi_name} ৰাশিত অৱস্থান কৰি আপোনাৰ ব্যক্তিত্ব আৰু আত্মবিশ্বাসক প্ৰভাৱিত কৰিছে।",
        "চন্দ্ৰ": f"চন্দ্ৰ {rasi_name} ৰাশিত অৱস্থান কৰি আপোনাৰ মন আৰু আৱেগিক জীৱনক প্ৰভাৱিত কৰিছে।",
        "মংগল": f"মংগল {rasi_name} ৰাশিত অৱস্থান কৰি আপোনাৰ সাহস, শক্তি, আৰু কৰ্মস্পৃহাক প্ৰভাৱিত কৰিছে।",
        "বুধ": f"বুধ {rasi_name} ৰাশিত অৱস্থান কৰি আপোনাৰ বুদ্ধি, যোগাযোগ, আৰু বিশ্লেষণ ক্ষমতাক প্ৰভাৱিত কৰিছে।",
        "বৃহস্পতি": f"বৃহস্পতি {rasi_name} ৰাশিত অৱস্থান কৰি আপোনাৰ জ্ঞান, ধৰ্ম, আৰু ভাগ্যক প্ৰভাৱিত কৰিছে।",
        "শুক্ৰ": f"শুক্ৰ {rasi_name} ৰাশিত অৱস্থান কৰি আপোনাৰ প্ৰেম, সৌন্দৰ্য্য, আৰু বিলাসিতাক প্ৰভাৱিত কৰিছে।",
        "শনি": f"শনি {rasi_name} ৰাশিত অৱস্থান কৰি আপোনাৰ ধৈৰ্য্য, শৃংখলা, আৰু কৰ্মফলক প্ৰভাৱিত কৰিছে।",
        "ৰাহু": f"ৰাহু {rasi_name} ৰাশিত অৱস্থান কৰি আপোনাৰ উচ্চাকাংক্ষা, মায়া, আৰু অপৰম্পৰাগত চিন্তাক প্ৰভাৱিত কৰিছে।",
        "কেতু": f"কেতু {rasi_name} ৰাশিত অৱস্থান কৰি আপোনাৰ আধ্যাত্মিকতা, বৈৰাগ্য, আৰু পূৰ্বজন্মৰ কৰ্মফলক প্ৰভাৱিত কৰিছে।",
    }

    return generic.get(planet_name, f"{planet_name} {rasi_name} ৰাশিত অৱস্থান কৰিছে।")


def generate_lagna_interpretation(asc_rasi: str) -> str:
    """Generate interpretation based on ascendant sign."""
    lagna_interpretations = {
        "মেষ": "মেষ লগ্নৰ ব্যক্তি সাহসী, উদ্যমী, আৰু নেতৃত্বগুণ সম্পন্ন হয়। আপুনি নতুন কাম আৰম্ভ কৰাত আগ্ৰহী আৰু প্ৰতিযোগিতামূলক পৰিৱেশত উন্নতি কৰে।",
        "বৃষ": "বৃষ লগ্নৰ ব্যক্তি ধৈৰ্যশীল, স্থিৰ, আৰু বিলাসী হয়। আপুনি আৰ্থিক স্থিৰতা আৰু সুন্দৰ জীৱনশৈলী ভাল পায়।",
        "মিথুন": "মিথুন লগ্নৰ ব্যক্তি বুদ্ধিমান, কৌতূহলী, আৰু বাক্পটু হয়। আপুনি যোগাযোগ, লিখা-মেলা, আৰু শিক্ষাৰ ক্ষেত্ৰত পাৰদৰ্শী।",
        "কৰ্কট": "কৰ্কট লগ্নৰ ব্যক্তি সংবেদনশীল, যত্নশীল, আৰু পাৰিবাৰিক হয়। আপুনি ঘৰ-পৰিয়াল আৰু আৱেগিক সুৰক্ষাৰ ওপৰত গুৰুত্ব দিয়ে।",
        "সিংহ": "সিংহ লগ্নৰ ব্যক্তি ৰাজকীয়, আত্মবিশ্বাসী, আৰু সৃষ্টিশীল হয়। আপুনি নেতৃত্ব দিবলৈ ভাল পায় আৰু স্বীকৃতি বিচাৰে।",
        "কন্যা": "কন্যা লগ্নৰ ব্যক্তি বিশ্লেষণাত্মক, পৰিপাটি, আৰু সেৱাভাৱী হয়। আপুনি খুঁটি-নাটি কামত পাৰদৰ্শী আৰু স্বাস্থ্য সচেতন।",
        "তুলা": "তুলা লগ্নৰ ব্যক্তি কূটনীতিজ্ঞ, ন্যায়পৰায়ণ, আৰু সামাজিক হয়। আপুনি সম্পৰ্ক আৰু সৌন্দৰ্য্যৰ ওপৰত গুৰুত্ব দিয়ে।",
        "বৃশ্চিক": "বৃশ্চিক লগ্নৰ ব্যক্তি ৰহস্যময়, গভীৰ, আৰু সংকল্পবদ্ধ হয়। আপুনি গোপন বিষয় আৰু গৱেষণাত আগ্ৰহী।",
        "ধনু": "ধনু লগ্নৰ ব্যক্তি আশাবাদী, স্বাধীনচেতীয়া, আৰু দাৰ্শনিক হয়। আপুনি ভ্ৰমণ, উচ্চ শিক্ষা, আৰু ধৰ্মত আগ্ৰহী।",
        "মকৰ": "মকৰ লগ্নৰ ব্যক্তি উচ্চাকাংক্ষী, পৰিশ্ৰমী, আৰু শৃংখলাবদ্ধ হয়। আপুনি কৰ্মজীৱন আৰু সামাজিক মৰ্যাদাৰ ওপৰত গুৰুত্ব দিয়ে।",
        "কুম্ভ": "কুম্ভ লগ্নৰ ব্যক্তি উদ্ভাৱনী, মানৱতাবাদী, আৰু স্বাধীনচেতীয়া হয়। আপুনি সামাজিক কাম আৰু নতুন চিন্তাত আগ্ৰহী।",
        "মীন": "মীন লগ্নৰ ব্যক্তি কল্পনাপ্ৰৱণ, দয়ালু, আৰু আধ্যাত্মিক হয়। আপুনি কলা, সংগীত, আৰু আধ্যাত্মিকতাত আগ্ৰহী।",
    }
    return lagna_interpretations.get(asc_rasi, f"আপোনাৰ লগ্ন {asc_rasi} ৰাশিত।")


def generate_dosha_interpretation(dosha_results: list) -> str:
    """Generate interpretation text for detected doshas."""
    lines = []
    present_doshas = [d for d in dosha_results if d.get('present')]

    if not present_doshas:
        return "আপোনাৰ কুণ্ডলীত কোনো গুৰুতৰ দোষ ধৰা পৰা নাই। ই এক শুভ লক্ষণ।"

    lines.append(f"আপোনাৰ কুণ্ডলীত {len(present_doshas)}টা দোষ ধৰা পৰিছে:")

    for d in present_doshas:
        info = d.get('info', {})
        name = info.get('name', d['key'])
        desc = info.get('description', '')
        severity = d.get('severity_text', '')
        lines.append(f"\n{info.get('icon', '•')} **{name}** ({severity}): {desc[:200]}...")

    lines.append("\n\nএই দোষসমূহৰ প্ৰতিকাৰৰ বাবে উপযুক্ত জ্যোতিষীয় পৰামৰ্শ গ্ৰহণ কৰক।")
    return '\n'.join(lines)


def generate_yoga_interpretation(yoga_results: list) -> str:
    """Generate interpretation text for detected yogas."""
    lines = []

    if not yoga_results:
        return "আপোনাৰ কুণ্ডলীত কোনো বিশেষ যোগ ধৰা পৰা নাই।"

    lines.append(f"আপোনাৰ কুণ্ডলীত {len(yoga_results)}টা শুভ যোগ ধৰা পৰিছে:")

    for y in yoga_results:
        lines.append(f"\n{y.get('icon', '✨')} **{y.get('name', '')}**: {y.get('description', '')[:200]}...")

    lines.append("\n\nএই যোগসমূহে আপোনাৰ জীৱনত শুভ ফল প্ৰদান কৰিব।")
    return '\n'.join(lines)


def generate_dasha_interpretation(dasa_data: list) -> str:
    """Generate interpretation for the CURRENTLY RUNNING dasha period (today's antardasha)."""
    if not dasa_data:
        return ""

    from datetime import datetime

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

    # Fallback to first mahadasha/antardasha if no match
    if current_md is None:
        current_md = dasa_data[0]
    if current_ad is None and current_md.get('sub_dasas'):
        current_ad = current_md['sub_dasas'][0]

    md_lord = current_md['md_lord']
    ad_lord = current_ad['ad_lord'] if current_ad else ''

    dasha_effects = {
        "ৰবি": "ৰবিৰ মহাদশাত আপুনি আত্মবিশ্বাস, নেতৃত্ব, আৰু কৰ্মক্ষেত্ৰত উন্নতি লাভ কৰিব। প্ৰশাসনিক পদ, ৰাজনীতি, আৰু চৰকাৰী ক্ষেত্ৰত সফলতাৰ সম্ভাৱনা আছে।",
        "চন্দ্ৰ": "চন্দ্ৰৰ মহাদশাত আপোনাৰ মানসিক আৰু আৱেগিক জীৱন গুৰুত্বপূৰ্ণ হ'ব। পৰিয়াল, মাতৃ, আৰু জনসাধাৰণৰ সৈতে সম্পৰ্ক উন্নত হ'ব।",
        "মংগল": "মংগলৰ মহাদশাত আপুনি সাহস, শক্তি, আৰু কৰ্মস্পৃহা লাভ কৰিব। সম্পত্তি, প্ৰতিযোগিতা, আৰু ক্ৰীড়া ক্ষেত্ৰত সফলতাৰ সম্ভাৱনা আছে।",
        "বুধ": "বুধৰ মহাদশাত আপোনাৰ বুদ্ধি, যোগাযোগ, আৰু শিক্ষাৰ ক্ষেত্ৰত উন্নতি হ'ব। ব্যৱসায়, লিখা-মেলা, আৰু গণিত বিষয়ত সফলতা লাভ কৰিব।",
        "বৃহস্পতি": "বৃহস্পতিৰ মহাদশাত আপুনি জ্ঞান, ধৰ্ম, আৰু ভাগ্যৰ প্ৰভাৱ অনুভৱ কৰিব। শিক্ষা, অৰ্থ, আৰু সন্তানৰ ক্ষেত্ৰত শুভ ফল লাভ কৰিব।",
        "শুক্ৰ": "শুক্ৰৰ মহাদশাত আপুনি সুখ, বিলাসিতা, আৰু কলাৰ প্ৰতি আকৰ্ষিত হ'ব। প্ৰেম, বিবাহ, আৰু বিত্তীয় ক্ষেত্ৰত উন্নতি হ'ব।",
        "শনি": "শনিৰ মহাদশাত আপুনি পৰিশ্ৰম, ধৈৰ্য্য, আৰু শৃংখলাৰ দ্বাৰা সফলতা লাভ কৰিব। দীৰ্ঘম্যাদী পৰিকল্পনা আৰু কৰ্মক্ষেত্ৰত উন্নতি হ'ব।",
        "ৰাহু": "ৰাহুৰ মহাদশাত আপুনি উচ্চাকাংক্ষা, প্ৰযুক্তি, আৰু বিদেশী সম্পৰ্কৰ প্ৰভাৱ অনুভৱ কৰিব। অপৰম্পৰাগত ক্ষেত্ৰত সফলতাৰ সম্ভাৱনা আছে।",
        "কেতু": "কেতুৰ মহাদশাত আপুনি আধ্যাত্মিকতা, বৈৰাগ্য, আৰু আত্মজ্ঞানৰ প্ৰতি আকৰ্ষিত হ'ব। পূৰ্বজন্মৰ কৰ্মফলৰ প্ৰভাৱ অনুভৱ কৰিব।",
    }

    antar_effects = {
        "ৰবি": "ৰবিৰ অন্তৰ্দশাত আপুনি কৰ্মক্ষেত্ৰত উন্নতি, নেতৃত্বৰ সুযোগ, আৰু চৰকাৰী কামত সফলতা লাভ কৰিব।",
        "চন্দ্ৰ": "চন্দ্ৰৰ অন্তৰ্দশাত আপোনাৰ মানসিক শান্তি, পাৰিবাৰিক সুখ, আৰু জনসাধাৰণৰ সমৰ্থন বৃদ্ধি পাব।",
        "মংগল": "মংগলৰ অন্তৰ্দশাত আপুনি সাহস, শক্তি, সম্পত্তি লাভ, আৰু প্ৰতিযোগিতাত সফলতা লাভ কৰিব।",
        "বুধ": "বুধৰ অন্তৰ্দশাত আপোনাৰ বুদ্ধি, ব্যৱসায়, যোগাযোগ, আৰু শিক্ষাৰ ক্ষেত্ৰত উন্নতি হ'ব।",
        "বৃহস্পতি": "বৃহস্পতিৰ অন্তৰ্দশাত আপুনি জ্ঞান, ধন, সন্তান, আৰু ভাগ্যৰ ক্ষেত্ৰত শুভ ফল লাভ কৰিব।",
        "শুক্ৰ": "শুক্ৰৰ অন্তৰ্দশাত আপুনি প্ৰেম, বিলাসিতা, কলা, আৰু বিত্তীয় ক্ষেত্ৰত উন্নতি লাভ কৰিব।",
        "শনি": "শনিৰ অন্তৰ্দশাত আপুনি পৰিশ্ৰম, ধৈৰ্য্য, আৰু শৃংখলাৰ দ্বাৰা দীৰ্ঘম্যাদী সফলতা লাভ কৰিব।",
        "ৰাহু": "ৰাহুৰ অন্তৰ্দশাত আপুনি উচ্চাকাংক্ষা, প্ৰযুক্তি, বিদেশী সম্পৰ্ক, আৰু অপৰম্পৰাগত ক্ষেত্ৰত সফলতা লাভ কৰিব।",
        "কেতু": "কেতুৰ অন্তৰ্দশাত আপুনি আধ্যাত্মিকতা, গৱেষণা, আৰু আত্মজ্ঞানৰ প্ৰতি আকৰ্ষিত হ'ব।",
    }

    effect = dasha_effects.get(md_lord, f"{md_lord}ৰ মহাদশা চলি আছে।")
    result = f"**বৰ্তমান মহাদশা: {md_lord}**\n\n{effect}"

    if ad_lord:
        ad_effect = antar_effects.get(ad_lord, f"{ad_lord}ৰ অন্তৰ্দশা চলি আছে।")
        result += f"\n\n**বৰ্তমান অন্তৰ্দশা: {ad_lord}**\n\n{ad_effect}"
        if current_ad:
            result += f"\n\n(সময়: {current_ad.get('start', '')} → {current_ad.get('end', '')})"

    return result


def generate_gemstone_recommendation(asc_rasi_idx: int, planet_signs: dict) -> str:
    """Generate gemstone recommendations based on lagna lord, 5th lord, and 9th lord."""
    lines = []

    lagna_lord = RASHI_LORDS.get(asc_rasi_idx, "")
    fifth_house_idx = (asc_rasi_idx + 4) % 12
    fifth_lord = RASHI_LORDS.get(fifth_house_idx, "")
    ninth_house_idx = (asc_rasi_idx + 8) % 12
    ninth_lord = RASHI_LORDS.get(ninth_house_idx, "")

    lines.append("**ৰত্ন পৰামৰ্শ:**")
    lines.append("")
    lines.append("বৈদিক জ্যোতিষ অনুসৰি, লগ্নপতি, পঞ্চমপতি আৰু নৱমপতি গ্ৰহৰ ৰত্ন ধাৰণ কৰিলে শুভ ফল লাভ হয়। আপোনাৰ কুণ্ডলী অনুসৰি:")
    lines.append("")

    if lagna_lord:
        gem = GEMSTONES.get(lagna_lord, "")
        lines.append(f"• **লগ্নপতি {lagna_lord}** ৰ ৰত্ন: **{gem}** — এই ৰত্ন ধাৰণ কৰিলে আপোনাৰ আত্মবিশ্বাস, স্বাস্থ্য আৰু ব্যক্তিত্বৰ উন্নতি হ'ব।")

    if fifth_lord:
        gem = GEMSTONES.get(fifth_lord, "")
        lines.append(f"• **পঞ্চমপতি {fifth_lord}** ৰ ৰত্ন: **{gem}** — এই ৰত্ন ধাৰণ কৰিলে আপোনাৰ বুদ্ধি, সন্তান, আৰু সৃষ্টিশীলতাৰ উন্নতি হ'ব।")

    if ninth_lord:
        gem = GEMSTONES.get(ninth_lord, "")
        lines.append(f"• **নৱমপতি {ninth_lord}** ৰ ৰত্ন: **{gem}** — এই ৰত্ন ধাৰণ কৰিলে আপোনাৰ ভাগ্য, ধৰ্ম, আৰু উচ্চ শিক্ষাৰ উন্নতি হ'ব।")

    lines.append("")
    lines.append("**ৰত্ন ধাৰণৰ নিয়ম:**")
    lines.append("• ৰত্ন সদায় শুদ্ধ আৰু প্ৰাকৃতিক হ'ব লাগে। কৃত্ৰিম বা ৰাসায়নিকভাৱে পৰিশোধিত ৰত্ন গ্ৰহণযোগ্য নহয়।")
    lines.append("• ৰত্ন ধাৰণৰ আগতে অভিজ্ঞ জ্যোতিষীৰ পৰামৰ্শ লোৱা উচিত।")
    lines.append("• ৰত্ন নিজ ৰাশিৰ গ্ৰহৰ বাবে নিৰ্ধাৰিত ধাতুৰ আঙুঠিত ধাৰণ কৰিব লাগে।")
    lines.append("• ৰত্ন ধাৰণৰ আগতে শুদ্ধি (পূজা-অভিষেক) কৰি ল'ব লাগে।")
    lines.append("• ৰত্ন নিৰ্দিষ্ট আঙুলিত ধাৰণ কৰিব লাগে।")
    lines.append("")

    lines.append("**বীজ মন্ত্ৰ:**")
    lines.append("")
    lords = []
    if lagna_lord:
        lords.append(("লগ্নপতি", lagna_lord))
    if fifth_lord and fifth_lord != lagna_lord:
        lords.append(("পঞ্চমপতি", fifth_lord))
    if ninth_lord and ninth_lord not in [lagna_lord, fifth_lord]:
        lords.append(("নৱমপতি", ninth_lord))

    for title, lord in lords:
        mantra = BEEJA_MANTRAS.get(lord, "")
        if mantra:
            lines.append(f"• **{title} {lord}** ৰ বীজ মন্ত্ৰ: `{mantra}`")

    lines.append("")
    lines.append("এই মন্ত্ৰসমূহ নিতৌ ১০৮ বাৰ জাপ কৰিলে গ্ৰহদোষ নাশ হয় আৰু শুভ ফল লাভ হয়।")

    return '\n'.join(lines)


def generate_overall_summary(planets_data: list, asc_rasi: str, dosha_count: int, yoga_count: int) -> str:
    """Generate an overall summary of the chart."""
    summaries = []

    if yoga_count >= 3:
        summaries.append("আপোনাৰ কুণ্ডলী অত্যন্ত শুভ যোগসম্পন্ন। জীৱনত বহু ক্ষেত্ৰত সফলতা লাভ কৰাৰ সম্ভাৱনা আছে।")
    elif yoga_count >= 1:
        summaries.append("আপোনাৰ কুণ্ডলীত শুভ যোগ আছে, যিয়ে জীৱনৰ বিভিন্ন ক্ষেত্ৰত সহায় কৰিব।")
    else:
        summaries.append("আপোনাৰ কুণ্ডলীত বিশেষ যোগ নাথাকিলেও, পৰিশ্ৰম আৰু সততাৰ দ্বাৰা সফলতা লাভ কৰিব পাৰিব।")

    if dosha_count >= 3:
        summaries.append("কেইবাটাও দোষ থকাৰ বাবে জীৱনত কিছু বাধাৰ সন্মুখীন হ'ব পাৰে। উপযুক্ত প্ৰতিকাৰ গ্ৰহণ কৰিলে এই বাধাসমূহ অতিক্ৰম কৰিব পাৰিব।")
    elif dosha_count == 0:
        summaries.append("কোনো গুৰুতৰ দোষ নথকাটো এক অতি শুভ লক্ষণ।")

    return ' '.join(summaries)


def generate_ai_interpretation(
    user_name: str, planets_data: list, asc_rasi: str,
    dosha_results: list, yoga_results: list, dasa_data: list,
    asc_rasi_idx: int = 0,
    planet_signs: dict = None,
    moon_nak_name: str = "",
    moon_rasi: str = "",
    tripap_ages: list = None,
    navatara_data: dict = None,
    sannari_data: dict = None,
) -> str:
    """
    Generate a compact AI-powered interpretation in Assamese (fits ~3 PDF pages).
    Merges related sections and removes redundancy with other PDF sections.
    """
    lines = []
    lines.append(f"প্ৰিয় {user_name},")
    lines.append("")
    lines.append("আপোনাৰ জন্মকুণ্ডলীৰ বৈদিক জ্যোতিষ শাস্ত্ৰৰ শুদ্ধ গণনাৰ আধাৰত এই AI বিশ্লেষণ প্ৰস্তুত কৰা হৈছে।")
    lines.append("")

    # ── ১। লগ্ন + লগ্নফল (merged) ──
    lines.append("**১। লগ্ন আৰু লগ্নফল:**")
    lines.append(generate_lagna_interpretation(asc_rasi))
    lagna_summaries = {
        "মেষ": "সাহসী, উদ্যমী, নেতৃত্বগুণ সম্পন্ন। কৰ্মক্ষেত্ৰত সফলতাৰ বাবে পৰিশ্ৰম আৰু ধৈৰ্য্যৰ প্ৰয়োজন।",
        "বৃষ": "ধৈৰ্যশীল, স্থিৰ, বিলাসী। আৰ্থিক স্থিৰতা আৰু পাৰিবাৰিক সুখৰ বাবে পৰিশ্ৰম কৰে।",
        "মিথুন": "বুদ্ধিমান, বাক্পটু, কৌতূহলী। যোগাযোগ আৰু শিক্ষাৰ ক্ষেত্ৰত সফলতা লাভ কৰে।",
        "কৰ্কট": "সংবেদনশীল, যত্নশীল, পাৰিবাৰিক। ঘৰ-পৰিয়াল আৰু আৱেগিক সুৰক্ষাৰ ওপৰত গুৰুত্ব দিয়ে।",
        "সিংহ": "ৰাজকীয়, আত্মবিশ্বাসী, সৃষ্টিশীল। নেতৃত্ব আৰু প্ৰশাসনিক ক্ষেত্ৰত সফলতা লাভ কৰে।",
        "কন্যা": "বিশ্লেষণাত্মক, পৰিপাটি, সেৱাভাৱী। স্বাস্থ্য আৰু সেৱাৰ ক্ষেত্ৰত সফলতা লাভ কৰে।",
        "তুলা": "কূটনীতিজ্ঞ, ন্যায়পৰায়ণ, সামাজিক। সম্পৰ্ক আৰু সৌন্দৰ্য্যৰ ক্ষেত্ৰত সফলতা লাভ কৰে।",
        "বৃশ্চিক": "ৰহস্যময়, গভীৰ, সংকল্পবদ্ধ। গৱেষণা আৰু গোপন বিষয়ত সফলতা লাভ কৰে।",
        "ধনু": "আশাবাদী, স্বাধীনচেতীয়া, দাৰ্শনিক। উচ্চ শিক্ষা আৰু ধৰ্মৰ ক্ষেত্ৰত সফলতা লাভ কৰে।",
        "মকৰ": "উচ্চাকাংক্ষী, পৰিশ্ৰমী, শৃংখলাবদ্ধ। কৰ্মজীৱন আৰু সামাজিক মৰ্যাদাৰ ক্ষেত্ৰত সফলতা লাভ কৰে।",
        "কুম্ভ": "উদ্ভাৱনী, মানৱতাবাদী, স্বাধীনচেতীয়া। প্ৰযুক্তি আৰু সমাজসেৱাৰ ক্ষেত্ৰত সফলতা লাভ কৰে।",
        "মীন": "কল্পনাপ্ৰৱণ, দয়ালু, আধ্যাত্মিক। কলা আৰু আধ্যাত্মিকতাৰ ক্ষেত্ৰত সফলতা লাভ কৰে।",
    }
    lines.append(lagna_summaries.get(asc_rasi, ""))
    lines.append("")

    # ── ২। গ্ৰহৰ অৱস্থান (compact - only key planets) ──
    lines.append("**২। গ্ৰহৰ বিশেষ অৱস্থান:**")
    key_planets = ["ৰবি", "চন্দ্ৰ", "মংগল", "বুধ", "বৃহস্পতি", "শুক্ৰ", "শনি"]
    for p in planets_data:
        if p['name'] in key_planets:
            interp = get_rasi_interpretation(p['name'], p['rasi'])
            lines.append(f"• {interp}")
    # Rahu & Ketu combined
    rahu_ketu = [p for p in planets_data if p['name'] in ("ৰাহু", "কেতু")]
    if rahu_ketu:
        for p in rahu_ketu:
            interp = get_rasi_interpretation(p['name'], p['rasi'])
            lines.append(f"• {interp}")
    lines.append("")

    # ── ৩। দোষ + যোগ (merged) ──
    present_doshas = [d for d in dosha_results if d.get('present')]
    lines.append(f"**৩। দোষ আৰু যোগ বিশ্লেষণ:**")
    if present_doshas:
        dosha_names = []
        for d in present_doshas:
            info = d.get('info', {})
            name = info.get('name', d.get('key', ''))
            severity = d.get('severity_text', '')
            dosha_names.append(f"{name} ({severity})")
        lines.append(f"উপস্থিত দোষ ({len(present_doshas)}টা): {', '.join(dosha_names)}।")
    else:
        lines.append("কোনো গুৰুতৰ দোষ ধৰা পৰা নাই — ই এক শুভ লক্ষণ।")

    if yoga_results:
        yoga_names = [y.get('name', '') for y in yoga_results[:5]]
        lines.append(f"শুভ যোগ ({len(yoga_results)}টা): {', '.join(yoga_names)}।")
    lines.append("")

    # ── ৪। দশা বিশ্লেষণ (compact) ──
    lines.append("**৪। বৰ্তমান দশা বিশ্লেষণ:**")
    lines.append(generate_dasha_interpretation(dasa_data))
    lines.append("")

    # ── ৫। নক্ষত্ৰ + ৰাশি (merged) ──
    if moon_nak_name or moon_rasi:
        lines.append("**৫। নক্ষত্ৰ আৰু ৰাশি:**")
        if moon_nak_name:
            lines.append(f"জন্ম নক্ষত্ৰ: {moon_nak_name}। এই নক্ষত্ৰৰ প্ৰভাৱত আপোনাৰ ব্যক্তিত্ব আৰু জীৱনশৈলী গঢ় লৈছে।")
        if moon_rasi:
            lines.append(f"চন্দ্ৰ ৰাশি: {moon_rasi}। চন্দ্ৰ ৰাশিৰ পৰা আপোনাৰ মন, আৱেগ, আৰু দৈনন্দিন জীৱনৰ ফলাফল নিৰ্ণয় কৰা হয়।")
        lines.append("")

    # ── ৬। ত্ৰিপাপ ৰিষ্ট + নৱতাৰা + সন্নাড়ী (merged) ──
    extras = []
    if tripap_ages:
        ages_str = ', '.join(str(a) for a in tripap_ages)
        extras.append(f"ত্ৰিপাপ ৰিষ্টৰ সম্ভাব্য বয়স: {ages_str} — এই বয়সসমূহত বিশেষ সাৱধানতা অৱলম্বন কৰক।")
    if navatara_data:
        extras.append("নৱতাৰা চক্ৰ: জন্ম নক্ষত্ৰৰ পৰা ২৭ নক্ষত্ৰক ৯ ভাগত বিভক্ত কৰি জীৱনৰ শুভ-অশুভ সময় নিৰ্ণয় কৰা হয়।")
    if sannari_data:
        extras.append("সন্নাড়ী চক্ৰ: জন্ম নক্ষত্ৰৰ আধাৰত দেহ, অৰ্থ, ভ্ৰাতৃ, মাতৃ, পুত্ৰ, শত্ৰু, দাৰা আদিৰ বিষয়ে সূচনা দিয়ে।")
    if extras:
        lines.append("**৬। অন্যান্য গুৰুত্বপূৰ্ণ বিশ্লেষণ:**")
        for e in extras:
            lines.append(f"• {e}")
        lines.append("")

    # ── ৭। ৰত্ন পৰামৰ্শ + বীজ মন্ত্ৰ + সাৰাংশ (merged) ──
    lines.append("**৭। ৰত্ন পৰামৰ্শ, বীজ মন্ত্ৰ আৰু সাৰাংশ:**")
    if planet_signs:
        lines.append(generate_gemstone_recommendation_compact(asc_rasi_idx, planet_signs))
    lines.append("")
    lines.append(f"**সাৰাংশ:** {generate_overall_summary(planets_data, asc_rasi, len(present_doshas), len(yoga_results))}")
    lines.append("")
    lines.append("— ধ্ৰুৱতৰা AI, আপোনাৰ বিশ্বাসযোগ্য জ্যোতিষ সহায়ক")

    return '\n'.join(lines)


def generate_gemstone_recommendation_compact(asc_rasi_idx: int, planet_signs: dict) -> str:
    """Compact gemstone + mantra recommendation (shorter version for PDF)."""
    lines = []
    lagna_lord = RASHI_LORDS.get(asc_rasi_idx, "")
    fifth_house_idx = (asc_rasi_idx + 4) % 12
    fifth_lord = RASHI_LORDS.get(fifth_house_idx, "")
    ninth_house_idx = (asc_rasi_idx + 8) % 12
    ninth_lord = RASHI_LORDS.get(ninth_house_idx, "")

    lords = []
    if lagna_lord:
        lords.append(("লগ্নপতি", lagna_lord))
    if fifth_lord and fifth_lord != lagna_lord:
        lords.append(("পঞ্চমপতি", fifth_lord))
    if ninth_lord and ninth_lord not in [lagna_lord, fifth_lord]:
        lords.append(("নৱমপতি", ninth_lord))

    for title, lord in lords:
        gem = GEMSTONES.get(lord, "")
        mantra = BEEJA_MANTRAS.get(lord, "")
        if gem:
            lines.append(f"• {title} {lord}: ৰত্ন — {gem}")
        if mantra:
            lines.append(f"  মন্ত্ৰ — {mantra}")

    if lords:
        lines.append("")
        lines.append("ৰত্ন সদায় শুদ্ধ-প্ৰাকৃতিক হ'ব লাগে আৰু অভিজ্ঞ জ্যোতিষীৰ পৰামৰ্শ লৈহে ধাৰণ কৰিব। মন্ত্ৰ নিতৌ ১০৮ বাৰ জাপ কৰিলে গ্ৰহদোষ নাশ হয়।")

    return '\n'.join(lines)
