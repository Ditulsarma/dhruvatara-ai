"""
ধ্ৰুৱতৰা AI - ৰাশিফল ইঞ্জিন (Rashifal Engine)
============================================================
Uses Ollama API with gemini-3-flash-preview:cloud model to generate
daily, monthly, and yearly horoscopes (ৰাশিফল) for all 12 zodiac signs.
"""

import requests

# ─── Ollama API Configuration ───────────────────────────────────
OLLAMA_API_KEY = "7c80477b1eed432db28cc89ff8c7b802.tFh71EvzfaFxZ6Lye2nMK4vp"
OLLAMA_MODEL = "gemini-3-flash-preview:cloud"
OLLAMA_URL = "https://ollama.com/v1/chat/completions"

# ─── Rashi Names ────────────────────────────────────────────────
RASHI_NAMES = [
    "মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা",
    "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"
]

RASHI_EMOJIS = {
    "মেষ": "♈", "বৃষ": "♉", "মিথুন": "♊", "কৰ্কট": "♋",
    "সিংহ": "♌", "কন্যা": "♍", "তুলা": "♎", "বৃশ্চিক": "♏",
    "ধনু": "♐", "মকৰ": "♑", "কুম্ভ": "♒", "মীন": "♓"
}

PERIOD_LABELS = {
    "daily": "দৈনিক ৰাশিফল",
    "monthly": "মাহেকীয়া ৰাশিফল",
    "yearly": "বছেৰেকীয়া ৰাশিফল"
}


def generate_rashifal(rashi_name: str, period: str) -> str:
    """
    Generate horoscope for a given rashi and period using Ollama API.
    
    Args:
        rashi_name: Assamese name of the zodiac sign (e.g., "মেষ")
        period: "daily", "monthly", or "yearly"
    
    Returns:
        Horoscope text in Assamese
    """
    period_label = PERIOD_LABELS.get(period, "ৰাশিফল")
    emoji = RASHI_EMOJIS.get(rashi_name, "")

    system_prompt = f"""তুমি এজন অভিজ্ঞ বৈদিক জ্যোতিষী পণ্ডিত। তুমি অসমীয়া ভাষাত ৰাশিফল প্ৰস্তুত কৰিবা।

গুৰুত্বপূৰ্ণ নিৰ্দেশনা:
- তুমি বৰ্তমানৰ গ্ৰহ-নক্ষত্ৰৰ অৱস্থান, গোচৰ (transit), আৰু চন্দ্ৰ ৰাশিৰ ভিত্তিত ৰাশিফল প্ৰস্তুত কৰিবা।
- তুমি কেৱল জ্যোতিষশাস্ত্ৰৰ সম্ভাৱনা আৰু ফলাফলৰ ওপৰত গুৰুত্ব দিবা।
- কোনো ধৰণৰ সাধাৰণ অস্বীকাৰ (generic disclaimer), অলাগতিয়াল পাতনি, বা অদৰকাৰী তথ্য লিখিব নালাগে।
- পোনপটীয়াকৈ ৰাশিফলৰ বিশ্লেষণলৈ আহিবা।
- ৰাশিফলত তলৰ বিষয়সমূহ অন্তৰ্ভুক্ত কৰিবা:
  ১. স্বাস্থ্য
  ২. ধন-সম্পত্তি / আৰ্থিক
  ৩. পৰিয়াল / প্ৰেম / সম্পৰ্ক
  ৪. কৰ্ম / শিক্ষা
  ৫. শুভ টিপছ আৰু প্ৰতিকাৰ (যদি প্ৰযোজ্য)
- উত্তৰ সুন্দৰভাৱে পেৰেগ্ৰাফ আকাৰত, শুদ্ধ অসমীয়া ভাষাত দিবা।
- প্ৰতিটো বিষয়ৰ বাবে বুলেট পইণ্ট ব্যৱহাৰ নকৰিবা — বৰ্ণনামূলক বাক্যত লিখিবা।"""

    user_prompt = f"""{emoji} {rashi_name} ৰাশিৰ বাবে {period_label} প্ৰস্তুত কৰা।

বৰ্তমান সময়: জুন ২০২৬। বৰ্তমানৰ গ্ৰহ-গোচৰৰ অৱস্থান অনুসৰি {rashi_name} ৰাশিৰ জাতক-জাতিকাৰ বাবে {period_label}ৰ সম্পূৰ্ণ বিশ্লেষণ দিয়া।

ৰাশিফলত তলৰ বিষয়সমূহ সামৰি ল'বা:
- স্বাস্থ্যৰ অৱস্থা আৰু পৰামৰ্শ
- আৰ্থিক / ধন-সম্পত্তিৰ সম্ভাৱনা
- পৰিয়াল, প্ৰেম, আৰু সম্পৰ্কৰ দিশ
- কৰ্মক্ষেত্ৰ বা শিক্ষাৰ সম্ভাৱনা
- শুভ টিপছ, সাৱধানতা, আৰু প্ৰতিকাৰ (যদি থাকে)

ৰাশিফলটো কমেও ৩০০-৪০০ শব্দৰ হ'ব লাগে।"""

    try:
        headers = {
            "Authorization": f"Bearer {OLLAMA_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 2000
        }

        response = requests.post(OLLAMA_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return _fallback_rashifal(rashi_name, period)

    except Exception as e:
        print(f"Ollama API error in rashifal: {e}")
        return _fallback_rashifal(rashi_name, period)


def _fallback_rashifal(rashi_name: str, period: str) -> str:
    """Generate a fallback horoscope when the AI API is unavailable."""
    period_label = PERIOD_LABELS.get(period, "ৰাশিফল")
    emoji = RASHI_EMOJIS.get(rashi_name, "")

    return f"""{emoji} **{rashi_name} ৰাশিৰ {period_label}**

স্বাস্থ্য: আপোনাৰ স্বাস্থ্য এই সময়ত মধ্যম ধৰণৰ হ'ব। নিয়মীয়া ব্যায়াম আৰু সুষম আহাৰ গ্ৰহণ কৰিলে স্বাস্থ্য ভালে থাকিব। মানসিক চাপ কমাবলৈ ধ্যান বা যোগাভ্যাস কৰিব পাৰে।

ধন-সম্পত্তি: আৰ্থিক দিশত এই সময়ত সাৱধানতা অৱলম্বন কৰা উচিত। ডাঙৰ বিনিয়োগ কৰাৰ আগতে ভালদৰে চিন্তা-চৰ্চা কৰি ল'ব। অযথা খৰচ নকৰাটোৱেই শ্ৰেয়।

পৰিয়াল আৰু সম্পৰ্ক: পাৰিবাৰিক জীৱনত শান্তি বজাই ৰাখিবলৈ পাৰস্পৰিক বুজাবুজি অতি প্ৰয়োজনীয়। প্ৰেমৰ সম্পৰ্কত থকা সকলে ধৈৰ্য্য ধৰি চলিব।

কৰ্ম আৰু শিক্ষা: কৰ্মক্ষেত্ৰত নতুন সুযোগ আহিব পাৰে। ছাত্ৰ-ছাত্ৰীসকলে পঢ়াত মনোযোগ দিলে ভাল ফলাফল লাভ কৰিব।

শুভ টিপছ: প্ৰতিদিনে সূৰ্যক অৰ্ঘ্য দিয়ক। পিতৃ-মাতৃৰ সেৱা কৰক। দান-দক্ষিণা কৰিলে শুভ ফল লাভ হ'ব।

[বিঃদ্ৰঃ এইটো এটা স্বয়ংক্ৰিয়ভাৱে প্ৰস্তুত কৰা ৰাশিফল। AI সেৱা উপলব্ধ নথকাৰ বাবে এই ফলবেক ৰাশিফল দেখুওৱা হৈছে।]"""
