"""
ধ্ৰুৱতৰা AI - অংক জ্যোতিষ AI চেট ইঞ্জিন
============================================================
Uses Ollama API with deepseek-v4-pro:cloud model to answer
numerology-related questions based on the user's numerology data.
Reuses the same API key and model from chat_engine.py.
"""

import json
import requests


# ─── Ollama API Configuration ───────────────────────────────────
OLLAMA_API_KEY = "7c80477b1eed432db28cc89ff8c7b802.tFh71EvzfaFxZ6Lye2nMK4vp"
OLLAMA_MODEL = "deepseek-v4-pro:cloud"
# Use the canonical URL (api.ollama.com redirects to ollama.com, which strips auth)
OLLAMA_URL = "https://ollama.com/v1/chat/completions"

# ─── Predefined Numerology Questions ────────────────────────────
NUMEROLOGY_QUESTIONS = [
    {"id": "lo_shu", "label": "মোৰ ল' চু গ্ৰীডৰ বিষয়ে বিতংভাৱে বুজাই দিয়ক।", "topic": "ল' চু গ্ৰীড"},
    {"id": "missing", "label": "মোৰ ল' চু গ্ৰীডত অনুপস্থিত সংখ্যাৰ প্ৰভাৱ কি?", "topic": "অনুপস্থিত সংখ্যা"},
    {"id": "present", "label": "মোৰ ল' চু গ্ৰীডত উপস্থিত সংখ্যাৰ প্ৰভাৱ কি?", "topic": "উপস্থিত সংখ্যা"},
    {"id": "mulyanka", "label": "মোৰ মূল্যাংকৰ বিষয়ে বিতংভাৱে বুজাই দিয়ক।", "topic": "মূল্যাংক"},
    {"id": "bhagyanka", "label": "মোৰ ভাগ্যাংকৰ বিষয়ে বিতংভাৱে বুজাই দিয়ক।", "topic": "ভাগ্যাংক"},
    {"id": "namanka", "label": "মোৰ নামাংকৰ বিষয়ে বিতংভাৱে বুজাই দিয়ক।", "topic": "নামাংক"},
    {"id": "angel", "label": "মোৰ এঞ্জেল সংখ্যাৰ অৰ্থ কি?", "topic": "এঞ্জেল সংখ্যা"},
    {"id": "name_correction", "label": "মোৰ নাম সংশোধনৰ পৰামৰ্শ দিয়ক।", "topic": "নাম সংশোধন"},
    {"id": "compensation", "label": "মোৰ নামাংক বা এঞ্জেল সংখ্যাই অনুপস্থিত সংখ্যা কেনেকৈ পূৰণ কৰে?", "topic": "সংখ্যা পূৰণ"},
    {"id": "remedies", "label": "মোৰ বাবে কি ৰত্ন, মন্ত্ৰ আৰু ৰুদ্ৰাক্ষ উপযুক্ত?", "topic": "প্ৰতিকাৰ"},
    {"id": "varsha", "label": "মোৰ আগন্তুক ১০ বছৰৰ বৰ্ষফল কেনেকুৱা?", "topic": "বৰ্ষফল"},
    {"id": "full", "label": "মোৰ সম্পূৰ্ণ অংক জ্যোতিষ ৰিপৰ্টৰ সাৰাংশ দিয়ক।", "topic": "সম্পূৰ্ণ ৰিপৰ্ট"},
]


def _build_numerology_context(report: dict) -> str:
    """Build a comprehensive Assamese context string from numerology report for the AI."""

    parts = []

    parts.append(f"ব্যক্তিৰ নাম: {report.get('name', '')}")
    parts.append(f"জন্ম তাৰিখ: {report.get('dob', '')}")

    m = report.get('mulyanka', {})
    parts.append(f"\nমূল্যাংক (Psychic Number): {m.get('value', '')} — গ্ৰহ: {m.get('planet', '')}")
    parts.append(f"মূল্যাংকৰ সকাৰাত্মক দিশ: {m.get('positive', '')}")
    parts.append(f"মূল্যাংকৰ নকাৰাত্মক দিশ: {m.get('negative', '')}")

    b = report.get('bhagyanka', {})
    parts.append(f"\nভাগ্যাংক (Destiny Number): {b.get('value', '')} — গ্ৰহ: {b.get('planet', '')}")
    parts.append(f"ভাগ্যাংকৰ সকাৰাত্মক দিশ: {b.get('positive', '')}")

    n = report.get('namanka', {})
    parts.append(f"\nনামাংক (Name Number): {n.get('value', '')} — গ্ৰহ: {n.get('planet', '')}")
    parts.append(f"নামাংকৰ মূল যোগফল: {n.get('raw_total', '')}")

    lo_shu = report.get('lo_shu_grid', {})
    missing = lo_shu.get('missing', [])
    present = lo_shu.get('present', [])
    counts = lo_shu.get('counts', {})

    parts.append(f"\nল' চু গ্ৰীড (DOB + মূল্যাংক + ভাগ্যাংকৰ পৰা):")
    parts.append(f"  উপস্থিত সংখ্যা: {', '.join([str(x) for x in present])}")
    parts.append(f"  অনুপস্থিত সংখ্যা: {', '.join([str(x) for x in missing])}")

    # Grid layout
    grid = lo_shu.get('grid', [["", "", ""], ["", "", ""], ["", "", ""]])
    parts.append(f"  গ্ৰীড বিন্যাস:")
    for row in grid:
        r0 = row[0] if row[0] else '—'
        r1 = row[1] if row[1] else '—'
        r2 = row[2] if row[2] else '—'
        parts.append(f"    {r0} | {r1} | {r2}")

    # Kua Number
    kua = report.get('kua_number', {})
    parts.append(f"\nকোৱা নম্বৰ (Kua Number): {kua.get('value', '')} — {kua.get('group', '')}")

    a = report.get('angel_number', {})
    parts.append(f"\nএঞ্জেল সংখ্যা: {a.get('value', '')}")
    parts.append(f"এঞ্জেল সংখ্যাৰ অৰ্থ: {a.get('description', '')}")

    # ─── Compensation Analysis ───
    comp = report.get('compensation', {})
    if comp:
        parts.append(f"\n═══ নামাংক আৰু কোৱা নম্বৰৰ দ্বাৰা পূৰণ বিশ্লেষণ ═══")
        parts.append(f"গুৰুত্বপূৰ্ণ: নামাংক ({n.get('value', '')}) আৰু কোৱা নম্বৰ ({kua.get('value', '')}) ল' চু গ্ৰীডত প্লট কৰা নহয়, কিন্তু ইহঁতে অনুপস্থিত সংখ্যাৰ অভাৱ পূৰণ কৰে।")
        if comp.get('compensated'):
            parts.append(f"পূৰণ হোৱা সংখ্যা: {', '.join([str(x) for x in comp['compensated']])}")
        if comp.get('not_compensated'):
            parts.append(f"পূৰণ নোহোৱা সংখ্যা: {', '.join([str(x) for x in comp['not_compensated']])}")
        if comp.get('summary'):
            parts.append(comp['summary'])
        if comp.get('details'):
            for d in comp['details']:
                parts.append(f"  {d['number']} ({d['planet']}): {' আৰু '.join(d['compensated_by'])}ৰ দ্বাৰা পূৰিত। ৰত্ন: {d.get('gem', '')} | মন্ত্ৰ: {d.get('mantra', '')}")

    nc = report.get('name_compatibility', {})
    parts.append(f"\nনাম সামঞ্জস্য: {'সামঞ্জস্যপূৰ্ণ' if nc.get('compatible') else 'সামঞ্জস্যপূৰ্ণ নহয়'}")
    parts.append(f"স্ক'ৰ: {nc.get('score', 0)}%")
    if nc.get('correction'):
        parts.append(f"নাম সংশোধনৰ পৰামৰ্শ: {nc['correction']}")

    # Missing numbers analysis
    missing_analysis = report.get('missing_analysis', [])
    if missing_analysis:
        parts.append("\nঅনুপস্থিত সংখ্যাৰ বিশ্লেষণ:")
        for ma in missing_analysis:
            parts.append(f"  {ma['number']} ({ma['planet']}): {ma['effect']}")

    # Present numbers analysis
    present_analysis = report.get('present_analysis', [])
    if present_analysis:
        parts.append("\nউপস্থিত সংখ্যাৰ বিশ্লেষণ:")
        for pa in present_analysis:
            parts.append(f"  {pa['number']} ({pa['planet']}, {pa['count']}×): {pa['effect']}")

    # Pratikar
    pr = report.get('pratikar', {})
    if pr.get('gems'):
        parts.append(f"\nপৰামৰ্শিত ৰত্ন: {', '.join(pr['gems'])}")
    if pr.get('mantras'):
        parts.append(f"পৰামৰ্শিত মন্ত্ৰ: {', '.join(pr['mantras'])}")
    if pr.get('rudraksha'):
        parts.append(f"পৰামৰ্শিত ৰুদ্ৰাক্ষ: {', '.join(pr['rudraksha'])}")

    return '\n'.join(parts)


def chat_numerology(user_name: str, question: str, report: dict) -> str:
    """
    Send a numerology question to Ollama AI with full numerology context.
    Returns the AI's response in Assamese.
    """

    context = _build_numerology_context(report)

    system_prompt = f"""তুমি এজন বিশেষজ্ঞ অংক জ্যোতিষী (Numerologist)। তোমাৰ নাম ধ্ৰুৱতৰা AI। 
তুমি অসমীয়া ভাষাত উত্তৰ দিবা। তোমাৰ উত্তৰ বিতং, তথ্যপূৰ্ণ আৰু সহানুভূতিশীল হ'ব লাগে।

তুমি তলত দিয়া অংক জ্যোতিষৰ তথ্যসমূহৰ ওপৰত ভিত্তি কৰি উত্তৰ দিবা:

{context}

গুৰুত্বপূৰ্ণ নিৰ্দেশনা:
১. তুমি প্ৰথমে ব্যক্তিৰ নামাংক আৰু এঞ্জেল সংখ্যাৰ সৈতে ল' চু গ্ৰীডৰ অনুপস্থিত সংখ্যাসমূহৰ সম্পৰ্ক বিশ্লেষণ কৰিবা।
২. যদি নামাংক বা এঞ্জেল সংখ্যা অনুপস্থিত সংখ্যাৰ সৈতে মিলে, তেন্তে বুজাই দিবা যে এই সংখ্যাই কেনেকৈ অনুপস্থিত সংখ্যাৰ অভাৱ পূৰণ কৰে।
৩. উদাহৰণস্বৰূপে: যদি ল' চু গ্ৰীডত ৫ সংখ্যাটো অনুপস্থিত কিন্তু নামাংক ৫, তেন্তে নামাংক ৫ (বুধ গ্ৰহ)ই বুদ্ধিমত্তা আৰু যোগাযোগৰ অভাৱ পূৰণ কৰিব।
৪. প্ৰতিটো সংখ্যাৰ গ্ৰহ, ৰত্ন, মন্ত্ৰ আৰু ৰুদ্ৰাক্ষৰ বিষয়ে উল্লেখ কৰিবা।
৫. তোমাৰ উত্তৰ সৰল আৰু সহজবোধ্য অসমীয়া ভাষাত হ'ব লাগে।
৬. প্ৰয়োজন অনুসৰি সংখ্যাৰ সাৰণী বা তালিকা ব্যৱহাৰ কৰিব পাৰা।
৭. উত্তৰৰ শেষত এটা সংক্ষিপ্ত সাৰাংশ দিবা।

মনে ৰাখিবা: তুমি এজন সহায়কাৰী আৰু বিশ্বাসযোগ্য জ্যোতিষী। তোমাৰ পৰামৰ্শ ব্যৱহাৰিক আৰু কাৰ্যকৰী হ'ব লাগে।"""

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{user_name}ৰ প্ৰশ্ন: {question}"}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "ক্ষমা কৰিব, উত্তৰ প্ৰস্তুত কৰিব পৰা নগল।")
    except requests.exceptions.Timeout:
        return "ক্ষমা কৰিব, AI চাৰ্ভাৰে সঁহাৰি দিবলৈ বেছি সময় লৈছে। অনুগ্ৰহ কৰি পুনৰ চেষ্টা কৰক।"
    except requests.exceptions.RequestException as e:
        return f"ক্ষমা কৰিব, AI সেৱাত ত্ৰুটি হৈছে: {str(e)}"
    except Exception as e:
        return f"ক্ষমা কৰিব, এটা অনাকাংক্ষিত ত্ৰুটি হৈছে: {str(e)}"
