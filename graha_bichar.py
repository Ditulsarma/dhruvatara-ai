"""
ধ্ৰুৱতৰা AI - গ্ৰহ বিচাৰ ইঞ্জিন (Graha Bichar Engine)
============================================================
প্ৰতিটো গ্ৰহৰ ১২টা ভাবত অৱস্থান অনুসৰি ফলাফল।
লগ্নৰ পৰা গ্ৰহৰ ভাব (ঘৰ) নিৰ্ণয় কৰি ফলাফল প্ৰদান কৰা হয়।
প্ৰথমে গ্ৰহৰ কাৰকতা, তাৰ পিছত ফলাফল লিখা হয়।
"""

import json
import os

# গ্ৰহৰ কাৰকতা (Karakattwa)
GRAHA_KARAKATTWA = {
    "ৰবি": "ৰবি গ্ৰহৰ কাৰকতাৰ ভিতৰত পৰে আত্মাৰ পুষ্টি, স্বাস্থ্য, আয়ু, মৰ্যাদা, সন্মান, সৌভাগ্য, উচ্চপদ, প্ৰভুত্ব আদি। ৰবি পিতৃ কাৰক গ্ৰহ। ৰবি গ্ৰহৰ কাৰণেই ব্যক্তিয়ে ৰাজ কাৰ্য্য বা পৰিচালনা কামত দক্ষতা লাভ কৰে।",
    "চন্দ্ৰ": "চন্দ্ৰ হৈছে মাতৃ কাৰক গ্ৰহ। মাতৃ সুখ বিচাৰৰ ক্ষেত্ৰত চন্দ্ৰ গ্ৰহৰ শুভাশুভ বিচাৰ কৰিব লগা হয়। হৰ্ষ-বিষাদ, সুখ-দুখ, আনন্দ-নিৰানন্দ আদি চন্দ্ৰ গ্ৰহৰ কাৰক। মানসিক শান্তি চন্দ্ৰৰ দান।",
    "মংগল": "মংগল হৈছে ভাতৃ কাৰক গ্ৰহ। মংগল গ্ৰহৰ কাৰণেই জাতকৰ সাহস, বীৰত্ব প্ৰকাশ পায়। ভূমি লাভ, গৃহ লাভ, ভাল সৈনিক আদি সকলো মংগলৰ অনুগ্ৰহপুষ্ট। মংগল অশুভ হলে দুৰ্ঘটনা, যুদ্ধ, মামলা-মোকৰ্দ্দমা, অস্ত্ৰোপচাৰ, অকালমৃত্যু আদি সংঘটিত হয়।",
    "বুধ": "বুধ হৈছে বিদ্যা-বুদ্ধিৰ কাৰক গ্ৰহ। বুধ গ্ৰহ অশুভ হলে অস্থিৰতা, মূৰ্খতা, উন্মত্ততা, নীচ বৃত্তি, চৌৰ্যবৃত্তি, বাতুলতা আদি হয়। বুধ গ্ৰহৰ কাৰণেই বায়ু, পিত্ত, কফ, দন্তৰোগ, শিৰোৰোগ, মৃগী, বাকশক্তিহীনতা, স্মৃতিশক্তিহীনতা, চালৰ ৰোগ, জিহ্বাৰ ৰোগ আদি হয়।",
    "বৃহস্পতি": "বৃহস্পতি জ্ঞান, সাধুতা, বাকপটুতা, বিবেক, সৎচৰিত্ৰতা, ধীশক্তি প্ৰভৃতিৰ অধিকাৰী। বৃহস্পতি ধন, সম্পত্তি, পুত্ৰ আৰু জীৱনৰ সুখৰ কাৰক গ্ৰহ। বৃহস্পতি ভাগ্যৰো কাৰক গ্ৰহ।",
    "শুক্ৰ": "শুক্ৰ কাম, প্ৰীতি, প্ৰেম, ভোগ আদিৰ অধিকাৰী। শান্তি, প্ৰফুল্লতা, বিলাসিতা, উচ্চ পদ, ঐশ্বৰ্য আদি শুক্ৰই প্ৰদান কৰে। শুক্ৰ প্ৰভাৱত সংগীত, নাটক, চিত্ৰকৰ আদি শিল্পীসুলভ প্ৰতিভাৰ বিকাশ পায়। শুক্ৰ অশুভ হোৱাৰ কাৰণেই জাতক লম্পট, ইন্দ্ৰিয় সুখভোগত তৎপৰ হৈ পৰে।",
    "শনি": "শনি দুঃখবাদী গ্ৰহ। দুৰদৰ্শিতা, অধ্যৱসায়, সংযম, কৰ্তব্যনিষ্ঠা, তীক্ষ্ণবুদ্ধি আদি শনি গ্ৰহৰ দান। শনিৰ অশুভ প্ৰভাৱত শৰীৰ কম্পন, পদ বিকল হোৱা আদি ৰোগ হয়।",
    "ৰাহু": "ৰাহু প্ৰতিকূল হলে দুঃখ-কষ্ট, ৰোগ, কাজিয়া-পেচাল, অতৃপ্ত আকাংক্ষা আদিৰ বাবে তীব্ৰ জ্বালা-যন্ত্ৰণা ভোগ কৰিব লগা হয়।",
    "কেতু": "জ্যোতিষশাস্ত্ৰমতে কেতু গ্ৰহৰ অস্তিত্ব জ্যোতিৰ্বিজ্ঞানত নাই, কেৱল বৈদিক জ্যোতিষত ইয়াক এটা ছায়া গ্ৰহ হিচাপে ধৰা হয় যি নিজৰ অৱস্থা আৰু লগত থকা গ্ৰহৰ অনুসাৰে ফলাফল প্ৰদান কৰে। কিছুমান ভাৱত ই শুভ ফল দিয়ে, আনহাতে কিছুমান ভাৱত অশুভ ফল দিয়ে। বৈদিক জ্যোতিষত কেতুক এটা অমঙ্গলকাৰক গ্ৰহ বুলি ধৰা হয় যদিও ই যে সদায়েই ব্যক্তিক বেয়া ফল দিয়ে এনে নহয়। বিশেষজ্ঞসকলৰ মতে কেতুৱে ব্যক্তিক শুভ ফলো প্ৰদান কৰে। বৈদিক জ্যোতিষত কেতুক আধ্যাত্ম, বৈৰাগ্য, মোক্ষ আৰু তান্ত্ৰিক বিদ্যাৰ কাৰক বুলি ধৰা হয়। কুণ্ডলীত যদি কেতু বৃহস্পতিৰ সৈতে যুতি হয়, তেন্তে ব্যক্তিজনে ৰজাৰ দৰে জীৱন কটাব পাৰে। আনহাতে, দুৰ্বল কেতুৰ ফলত নানান সমস্যাৰ সন্মুখীন হ'ব লাগে। ব্যক্তি ক্ৰোধী আৰু উগ্ৰ স্বভাৱৰ হয়। সহজে কাম সিদ্ধ নহয়, সৰু কামৰ বাবেও অধিক পৰিশ্ৰম কৰিব লাগে আৰু হঠাতে বাধাৰ সন্মুখীন হয়। কেতু গ্ৰহৰ কাৰণে অশ্বগন্ধাৰ মূল ব্যৱহাৰ কৰা হয়। কেতুৰ কুপ্ৰভাৱৰ পৰা হাত সাৰিবলৈ কুকুৰক খাদ্য খুৱাব পাৰিলে ভাল ফল লাভ কৰিব পাৰি।",
}

# ভাবৰ নাম (House names)
BHAVA_NAMES = [
    "প্ৰথম ভাব", "দ্বিতীয় ভাব", "তৃতীয় ভাব", "চতুৰ্থ ভাব",
    "পঞ্চম ভাব", "ষষ্ঠ ভাব", "সপ্তম ভাব", "অষ্টম ভাব",
    "নবম ভাব", "দশম ভাব", "একাদশ ভাব", "দ্বাদশ ভাব"
]

# --- JSON ডাটা লোড কৰক ---
_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graha_phala_data.json')
_GRAHA_PHALA = {}

def _load_data():
    global _GRAHA_PHALA
    if not _GRAHA_PHALA:
        try:
            with open(_json_path, 'r', encoding='utf-8') as f:
                _GRAHA_PHALA = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            _GRAHA_PHALA = {}

_load_data()


def get_graha_bichar(planet_name: str, house_index: int) -> str:
    """
    প্ৰদত্ত গ্ৰহৰ নাম আৰু ভাব সূচক (০-১১, লগ্নৰ পৰা) অনুসৰি গ্ৰহ বিচাৰ ফলাফল ঘূৰাই দিয়ে।
    """
    if planet_name not in GRAHA_KARAKATTWA:
        return f"{planet_name} গ্ৰহৰ তথ্য উপলব্ধ নহয়।"
    
    karakattwa = GRAHA_KARAKATTWA.get(planet_name, "")
    bhava_name = BHAVA_NAMES[house_index] if 0 <= house_index < 12 else f"{house_index+1} সংখ্যক ভাব"
    
    phala = ""
    if planet_name in _GRAHA_PHALA:
        house_key = str(house_index)
        phala = _GRAHA_PHALA[planet_name].get(house_key, "")
    
    if not phala:
        phala = f"{planet_name} গ্ৰহ আপোনাৰ জন্মকুণ্ডলীত {bhava_name}ত অৱস্থান কৰিছে।"
    
    result = f"【{planet_name} গ্ৰহৰ কাৰকতা】\n{karakattwa}\n\n"
    result += f"【{planet_name} গ্ৰহ {bhava_name}ত অৱস্থানৰ ফলাফল】\n{phala}"
    
    return result


def get_all_graha_bichar(planet_houses: dict) -> dict:
    """
    সকলো গ্ৰহৰ বাবে গ্ৰহ বিচাৰ ফলাফল ঘূৰাই দিয়ে।
    Args: planet_houses = {গ্ৰহৰ নাম: ভাব সূচক (০-১১)}
    Returns: {গ্ৰহৰ নাম: {"bhava": ..., "karakattwa": ..., "phala": ...}}
    """
    results = {}
    for planet_name, house_idx in planet_houses.items():
        if planet_name in GRAHA_KARAKATTWA:
            bhava_name = BHAVA_NAMES[house_idx] if 0 <= house_idx < 12 else f"{house_idx+1} সংখ্যক ভাব"
            phala = ""
            if planet_name in _GRAHA_PHALA:
                phala = _GRAHA_PHALA[planet_name].get(str(house_idx), "")
            results[planet_name] = {
                "bhava": bhava_name,
                "house_index": house_idx,
                "karakattwa": GRAHA_KARAKATTWA[planet_name],
                "phala": phala
            }
    return results


def get_graha_bichar_html(planet_houses: dict) -> str:
    """সকলো গ্ৰহৰ বাবে HTML ফৰ্মেটত গ্ৰহ বিচাৰ ফলাফল ঘূৰাই দিয়ে।"""
    all_results = get_all_graha_bichar(planet_houses)
    html_parts = ['<div class="graha-bichar-container">']
    for planet_name, data in all_results.items():
        phala_text = data["phala"].replace('\n', '<br>') if data["phala"] else ""
        html_parts.append(f'<div class="graha-card" style="background:#fff;border-radius:12px;padding:20px;margin:16px 0;box-shadow:0 2px 12px rgba(0,0,0,0.06);border-left:4px solid #FF6600;">')
        html_parts.append(f'<h3 style="color:#1a237e;margin:0 0 12px 0;">{planet_name} গ্ৰহ — {data["bhava"]}ত অৱস্থিত</h3>')
        html_parts.append(f'<div style="background:#f5f0ff;padding:12px;border-radius:8px;margin-bottom:12px;"><strong>কাৰকতা:</strong> {data["karakattwa"]}</div>')
        html_parts.append(f'<div><strong>ফলাফল:</strong><p style="line-height:1.8;">{phala_text}</p></div>')
        html_parts.append('</div>')
    html_parts.append('</div>')
    return '\n'.join(html_parts)
