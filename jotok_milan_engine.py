"""
ধ্ৰুৱতৰা AI - যোটক মিলন ইঞ্জিন (Jotok Milan / Marriage Matching Engine)
Ashtakoot Guna Milan (অষ্টকূট গুণ মিলন) - 36 Points System
Plus Mangalik Dosha (মাংগলিক দোষ) Analysis for Marriage Compatibility

Based on traditional Assamese Vedic Jyotish principles.
All scoring tables are exact as per classical Ashtakoot system.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS & LOOKUP TABLES
# ═══════════════════════════════════════════════════════════════════════════════

RASHIS = [
    "মেষ", "বৃষ", "মিথুন", "কৰ্কট",
    "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক",
    "ধনু", "মকৰ", "কুম্ভ", "মীন"
]

NAKSHATRAS = [
    "অশ্বিনী", "ভৰণী", "কৃত্তিকা", "ৰোহিণী", "মৃগশিৰা", "আৰ্দ্ৰা", "পুনৰ্বসু", "পুষ্যা", "অশ্লেষা",
    "মঘা", "পূৰ্বফাল্গুনী", "উত্তৰফাল্গুনী", "হস্তা", "চিত্ৰা", "স্বাতী", "বিশাখা", "অনুৰাধা", "জ্যেষ্ঠা",
    "মূল", "পূৰ্বাষাঢ়া", "উত্তৰাষাঢ়া", "শ্ৰৱণা", "ধনিষ্ঠা", "শতভিষা", "পূৰ্বভাদ্ৰপদ", "উত্তৰভাদ্ৰপদ", "ৰেৱতী"
]

# ─── Varna (বৰ্ণ) by Rashi ───
# Brahmin=1, Kshatriya=2, Vaishya=3, Shudra=4
VARNA_BY_RASHI = {
    "মেষ": 2, "বৃষ": 3, "মিথুন": 4, "কৰ্কট": 1,
    "সিংহ": 2, "কন্যা": 3, "তুলা": 4, "বৃশ্চিক": 1,
    "ধনু": 2, "মকৰ": 3, "কুম্ভ": 4, "মীন": 1
}

VARNA_NAMES = {1: "ব্ৰাহ্মণ", 2: "ক্ষত্ৰিয়", 3: "বৈশ্য", 4: "শূদ্ৰ"}

# ─── Vashya (বশ্য) by Rashi ───
# 1=Chatushpad (চতুষ্পদ), 2=Manava (মানৱ/দ্বিপদ), 3=Jalachar (জলচৰ), 4=Banachar (বনচৰ), 5=Keet (কীট)
VASHYA_BY_RASHI = {
    "মেষ": 1, "বৃষ": 1, "মিথুন": 2, "কৰ্কট": 3,
    "সিংহ": 4, "কন্যা": 2, "তুলা": 2, "বৃশ্চিক": 5,
    "ধনু": 2, "মকৰ": 3, "কুম্ভ": 2, "মীন": 3
}

VASHYA_NAMES = {1: "চতুষ্পদ", 2: "মানৱ", 3: "জলচৰ", 4: "বনচৰ", 5: "কীট"}

# Vashya compatibility matrix (girl_row x boy_col)
# Index: 1=Chatushpad, 2=Manava, 3=Jalachar, 4=Banachar, 5=Keet
VASHYA_MATRIX = {
    1: {1: 2, 2: 1, 3: 1, 4: 0, 5: 1},  # Chatushpad
    2: {1: 1, 2: 2, 3: 0, 4: 0, 5: 1},  # Manava
    3: {1: 1, 2: 0, 3: 2, 4: 1, 5: 1},  # Jalachar
    4: {1: 0, 2: 0, 3: 1, 4: 2, 5: 0},  # Banachar
    5: {1: 1, 2: 0, 3: 1, 4: 0, 5: 2},  # Keet
}

# ─── Tara (তাৰা) by Nakshatra ───
# 9 tara groups
TARA_GROUP = {
    "অশ্বিনী": 1, "মঘা": 1, "মূল": 1,           # জন্ম
    "ভৰণী": 2, "পূৰ্বফাল্গুনী": 2, "পূৰ্বাষাঢ়া": 2,  # সম্পদ
    "কৃত্তিকা": 3, "উত্তৰফাল্গুনী": 3, "উত্তৰাষাঢ়া": 3, # বিপদ
    "ৰোহিণী": 4, "হস্তা": 4, "শ্ৰৱণা": 4,        # ক্ষেম
    "মৃগশিৰা": 5, "চিত্ৰা": 5, "ধনিষ্ঠা": 5,      # প্ৰত্যৰি
    "আৰ্দ্ৰা": 6, "স্বাতী": 6, "শতভিষা": 6,       # সাধক
    "পুনৰ্বসু": 7, "বিশাখা": 7, "পূৰ্বভাদ্ৰপদ": 7,  # বধ
    "পুষ্যা": 8, "অনুৰাধা": 8, "উত্তৰভাদ্ৰপদ": 8,   # মিত্ৰ
    "অশ্লেষা": 9, "জ্যেষ্ঠা": 9, "ৰেৱতী": 9,      # অতি মিত্ৰ
}

TARA_NAMES = {
    1: "জন্ম", 2: "সম্পদ", 3: "বিপদ", 4: "ক্ষেম", 5: "প্ৰত্যৰি",
    6: "সাধক", 7: "বধ", 8: "মিত্ৰ", 9: "অতি মিত্ৰ"
}

# Tara compatibility matrix (girl_row x boy_col)
TARA_MATRIX = {
    1: {1: 3, 2: 3, 3: 1.5, 4: 3, 5: 1.5, 6: 3, 7: 1.5, 8: 3, 9: 3},  # জন্ম
    2: {1: 3, 2: 3, 3: 1.5, 4: 3, 5: 1.5, 6: 3, 7: 1.5, 8: 3, 9: 3},  # সম্পদ
    3: {1: 1.5, 2: 1.5, 3: 0, 4: 1.5, 5: 0, 6: 1.5, 7: 0, 8: 1.5, 9: 1.5},  # বিপদ
    4: {1: 3, 2: 3, 3: 1.5, 4: 3, 5: 1.5, 6: 3, 7: 1.5, 8: 3, 9: 3},  # ক্ষেম
    5: {1: 1.5, 2: 1.5, 3: 0, 4: 1.5, 5: 0, 6: 1.5, 7: 0, 8: 1.5, 9: 1.5},  # প্ৰত্যৰি
    6: {1: 3, 2: 3, 3: 1.5, 4: 3, 5: 1.5, 6: 3, 7: 1.5, 8: 3, 9: 3},  # সাধক
    7: {1: 1.5, 2: 1.5, 3: 0, 4: 1.5, 5: 0, 6: 1.5, 7: 0, 8: 1.5, 9: 1.5},  # বধ
    8: {1: 3, 2: 3, 3: 1.5, 4: 3, 5: 1.5, 6: 3, 7: 1.5, 8: 3, 9: 3},  # মিত্ৰ
    9: {1: 3, 2: 3, 3: 1.5, 4: 3, 5: 1.5, 6: 3, 7: 1.5, 8: 3, 9: 3},  # অতি মিত্ৰ
}

# ─── Yoni (যোনি) by Nakshatra ───
YONI_BY_NAKSHATRA = {
    "অশ্বিনী": "অশ্ব", "শতভিষা": "অশ্ব",
    "ভৰণী": "গজ", "ৰেৱতী": "গজ",
    "কৃত্তিকা": "মেষ", "পুষ্যা": "মেষ",
    "ৰোহিণী": "সৰ্প", "মৃগশিৰা": "সৰ্প",
    "আৰ্দ্ৰা": "শ্বান", "মূল": "শ্বান",
    "পুনৰ্বসু": "মাৰ্জাৰ", "অশ্লেষা": "মাৰ্জাৰ",
    "মঘা": "মূষিক", "পূৰ্বফাল্গুনী": "মূষিক",
    "উত্তৰফাল্গুনী": "গো", "উত্তৰভাদ্ৰপদ": "গো",
    "হস্তা": "মহিষ", "স্বাতী": "মহিষ",
    "চিত্ৰা": "ব্যাঘ্ৰ", "বিশাখা": "ব্যাঘ্ৰ",
    "অনুৰাধা": "মৃগ", "জ্যেষ্ঠা": "মৃগ",
    "পূৰ্বাষাঢ়া": "বানৰ", "শ্ৰৱণা": "বানৰ",
    "উত্তৰাষাঢ়া": "নকুল",
    "ধনিষ্ঠা": "সিংহ", "পূৰ্বভাদ্ৰপদ": "সিংহ",
}

YONI_LIST = ["অশ্ব", "গজ", "মেষ", "সৰ্প", "শ্বান", "মাৰ্জাৰ", "মূষিক", "গো", "মহিষ", "ব্যাঘ্ৰ", "মৃগ", "বানৰ", "নকুল", "সিংহ"]

# Yoni compatibility matrix (girl_row x boy_col)
YONI_MATRIX = {
    "অশ্ব":    {"অশ্ব": 4, "গজ": 2, "মেষ": 2, "সৰ্প": 3, "শ্বান": 2, "মাৰ্জাৰ": 2, "মূষিক": 2, "গো": 1, "মহিষ": 0, "ব্যাঘ্ৰ": 1, "মৃগ": 3, "বানৰ": 3, "নকুল": 2, "সিংহ": 1},
    "গজ":     {"অশ্ব": 2, "গজ": 4, "মেষ": 3, "সৰ্প": 3, "শ্বান": 2, "মাৰ্জাৰ": 2, "মূষিক": 2, "গো": 2, "মহিষ": 3, "ব্যাঘ্ৰ": 1, "মৃগ": 2, "বানৰ": 3, "নকুল": 2, "সিংহ": 0},
    "মেষ":    {"অশ্ব": 2, "গজ": 3, "মেষ": 4, "সৰ্প": 2, "শ্বান": 1, "মাৰ্জাৰ": 2, "মূষিক": 1, "গো": 3, "মহিষ": 3, "ব্যাঘ্ৰ": 1, "মৃগ": 2, "বানৰ": 0, "নকুল": 3, "সিংহ": 1},
    "সৰ্প":   {"অশ্ব": 3, "গজ": 3, "মেষ": 2, "সৰ্প": 4, "শ্বান": 2, "মাৰ্জাৰ": 1, "মূষিক": 1, "গো": 1, "মহিষ": 1, "ব্যাঘ্ৰ": 2, "মৃগ": 2, "বানৰ": 2, "নকুল": 0, "সিংহ": 2},
    "শ্বান":  {"অশ্ব": 2, "গজ": 2, "মেষ": 1, "সৰ্প": 2, "শ্বান": 4, "মাৰ্জাৰ": 2, "মূষিক": 1, "গো": 2, "মহিষ": 2, "ব্যাঘ্ৰ": 1, "মৃগ": 0, "বানৰ": 2, "নকুল": 1, "সিংহ": 1},
    "মাৰ্জাৰ": {"অশ্ব": 2, "গজ": 2, "মেষ": 2, "সৰ্প": 1, "শ্বান": 2, "মাৰ্জাৰ": 4, "মূষিক": 0, "গো": 2, "মহিষ": 2, "ব্যাঘ্ৰ": 1, "মৃগ": 3, "বানৰ": 3, "নকুল": 2, "সিংহ": 1},
    "মূষিক":  {"অশ্ব": 2, "গজ": 2, "মেষ": 1, "সৰ্প": 1, "শ্বান": 1, "মাৰ্জাৰ": 0, "মূষিক": 4, "গো": 2, "মহিষ": 2, "ব্যাঘ্ৰ": 2, "মৃগ": 2, "বানৰ": 2, "নকুল": 1, "সিংহ": 2},
    "গো":     {"অশ্ব": 1, "গজ": 2, "মেষ": 3, "সৰ্প": 1, "শ্বান": 2, "মাৰ্জাৰ": 2, "মূষিক": 2, "গো": 4, "মহিষ": 3, "ব্যাঘ্ৰ": 0, "মৃগ": 3, "বানৰ": 2, "নকুল": 2, "সিংহ": 1},
    "মহিষ":  {"অশ্ব": 0, "গজ": 3, "মেষ": 3, "সৰ্প": 1, "শ্বান": 2, "মাৰ্জাৰ": 2, "মূষিক": 2, "গো": 3, "মহিষ": 4, "ব্যাঘ্ৰ": 1, "মৃগ": 2, "বানৰ": 2, "নকুল": 2, "সিংহ": 1},
    "ব্যাঘ্ৰ": {"অশ্ব": 1, "গজ": 1, "মেষ": 1, "সৰ্প": 2, "শ্বান": 1, "মাৰ্জাৰ": 1, "মূষিক": 2, "গো": 0, "মহিষ": 1, "ব্যাঘ্ৰ": 4, "মৃগ": 1, "বানৰ": 1, "নকুল": 2, "সিংহ": 1},
    "মৃগ":    {"অশ্ব": 3, "গজ": 2, "মেষ": 2, "সৰ্প": 2, "শ্বান": 0, "মাৰ্জাৰ": 3, "মূষিক": 2, "গো": 3, "মহিষ": 2, "ব্যাঘ্ৰ": 1, "মৃগ": 4, "বানৰ": 2, "নকুল": 2, "সিংহ": 1},
    "বানৰ":  {"অশ্ব": 3, "গজ": 3, "মেষ": 0, "সৰ্প": 2, "শ্বান": 2, "মাৰ্জাৰ": 3, "মূষিক": 2, "গো": 2, "মহিষ": 2, "ব্যাঘ্ৰ": 1, "মৃগ": 2, "বানৰ": 4, "নকুল": 3, "সিংহ": 2},
    "নকুল":  {"অশ্ব": 2, "গজ": 2, "মেষ": 3, "সৰ্প": 0, "শ্বান": 1, "মাৰ্জাৰ": 2, "মূষিক": 1, "গো": 2, "মহিষ": 2, "ব্যাঘ্ৰ": 2, "মৃগ": 2, "বানৰ": 3, "নকুল": 4, "সিংহ": 2},
    "সিংহ":  {"অশ্ব": 1, "গজ": 0, "মেষ": 1, "সৰ্প": 2, "শ্বান": 1, "মাৰ্জাৰ": 1, "মূষিক": 2, "গো": 1, "মহিষ": 1, "ব্যাঘ্ৰ": 1, "মৃগ": 1, "বানৰ": 2, "নকুল": 2, "সিংহ": 4},
}

# ─── Graha Maitri (গ্ৰহ মৈত্ৰী) - Rashi Lords ───
RASHI_LORDS = {
    "মেষ": "সূৰ্য", "বৃষ": "শুক্ৰ", "মিথুন": "বুধ", "কৰ্কট": "চন্দ্ৰ",
    "সিংহ": "সূৰ্য", "কন্যা": "বুধ", "তুলা": "শুক্ৰ", "বৃশ্চিক": "মংগল",
    "ধনু": "বৃহস্পতি", "মকৰ": "শনি", "কুম্ভ": "শনি", "মীন": "বৃহস্পতি"
}

# Graha Maitri compatibility matrix (girl_row x boy_col)
GRAHA_MAITRI_MATRIX = {
    "সূৰ্য":     {"সূৰ্য": 5, "চন্দ্ৰ": 5, "মংগল": 5, "বুধ": 4, "বৃহস্পতি": 5, "শুক্ৰ": 0, "শনি": 0},
    "চন্দ্ৰ":   {"সূৰ্য": 5, "চন্দ্ৰ": 5, "মংগল": 4, "বুধ": 1, "বৃহস্পতি": 4, "শুক্ৰ": 0.5, "শনি": 0.5},
    "মংগল":    {"সূৰ্য": 5, "চন্দ্ৰ": 4, "মংগল": 5, "বুধ": 0.5, "বৃহস্পতি": 5, "শুক্ৰ": 3, "শনি": 0.5},
    "বুধ":     {"সূৰ্য": 4, "চন্দ্ৰ": 1, "মংগল": 0.5, "বুধ": 5, "বৃহস্পতি": 0.5, "শুক্ৰ": 5, "শনি": 4},
    "বৃহস্পতি": {"সূৰ্য": 5, "চন্দ্ৰ": 4, "মংগল": 5, "বুধ": 0.5, "বৃহস্পতি": 5, "শুক্ৰ": 0.5, "শনি": 3},
    "শুক্ৰ":    {"সূৰ্য": 0, "চন্দ্ৰ": 0.5, "মংগল": 3, "বুধ": 5, "বৃহস্পতি": 0.5, "শুক্ৰ": 5, "শনি": 5},
    "শনি":     {"সূৰ্য": 0, "চন্দ্ৰ": 0.5, "মংগল": 0.5, "বুধ": 4, "বৃহস্পতি": 3, "শুক্ৰ": 5, "শনি": 5},
}

# ─── Gana (গণ) by Nakshatra ───
# 1=Deva (দেৱ), 2=Manushya (মনুষ্য), 3=Rakshasa (ৰাক্ষস)
GANA_BY_NAKSHATRA = {
    "অশ্বিনী": 1, "ভৰণী": 2, "কৃত্তিকা": 3, "ৰোহিণী": 2, "মৃগশিৰা": 1, "আৰ্দ্ৰা": 2,
    "পুনৰ্বসু": 1, "পুষ্যা": 1, "অশ্লেষা": 3, "মঘা": 3, "পূৰ্বফাল্গুনী": 2, "উত্তৰফাল্গুনী": 2,
    "হস্তা": 1, "চিত্ৰা": 3, "স্বাতী": 1, "বিশাখা": 3, "অনুৰাধা": 1, "জ্যেষ্ঠা": 3,
    "মূল": 3, "পূৰ্বাষাঢ়া": 2, "উত্তৰাষাঢ়া": 2, "শ্ৰৱণা": 1, "ধনিষ্ঠা": 3, "শতভিষা": 3,
    "পূৰ্বভাদ্ৰপদ": 2, "উত্তৰভাদ্ৰপদ": 2, "ৰেৱতী": 1
}

GANA_NAMES = {1: "দেৱ", 2: "মনুষ্য", 3: "ৰাক্ষস"}

# Gana compatibility matrix (girl_row x boy_col)
GANA_MATRIX = {
    1: {1: 6, 2: 5, 3: 1},  # Deva
    2: {1: 6, 2: 6, 3: 0},  # Manushya
    3: {1: 0, 2: 0, 3: 6},  # Rakshasa
}

# ─── Bhakoot (ভকূট) by Rashi ───
# Bhakoot compatibility matrix (girl_row x boy_col)
BHAKOOT_MATRIX = {
    "মেষ":     {"মেষ": 7, "বৃষ": 0, "মিথুন": 7, "কৰ্কট": 7, "সিংহ": 0, "কন্যা": 0, "তুলা": 7, "বৃশ্চিক": 0, "ধনু": 0, "মকৰ": 7, "কুম্ভ": 7, "মীন": 0},
    "বৃষ":     {"মেষ": 0, "বৃষ": 7, "মিথুন": 0, "কৰ্কট": 7, "সিংহ": 7, "কন্যা": 0, "তুলা": 0, "বৃশ্চিক": 7, "ধনু": 0, "মকৰ": 0, "কুম্ভ": 7, "মীন": 7},
    "মিথুন":   {"মেষ": 7, "বৃষ": 0, "মিথুন": 7, "কৰ্কট": 0, "সিংহ": 7, "কন্যা": 7, "তুলা": 0, "বৃশ্চিক": 0, "ধনু": 7, "মকৰ": 0, "কুম্ভ": 0, "মীন": 7},
    "কৰ্কট":   {"মেষ": 7, "বৃষ": 7, "মিথুন": 0, "কৰ্কট": 7, "সিংহ": 0, "কন্যা": 7, "তুলা": 7, "বৃশ্চিক": 0, "ধনু": 0, "মকৰ": 7, "কুম্ভ": 0, "মীন": 0},
    "সিংহ":    {"মেষ": 0, "বৃষ": 0, "মিথুন": 7, "কৰ্কট": 0, "সিংহ": 7, "কন্যা": 0, "তুলা": 7, "বৃশ্চিক": 7, "ধনু": 0, "মকৰ": 0, "কুম্ভ": 7, "মীন": 0},
    "কন্যা":   {"মেষ": 0, "বৃষ": 0, "মিথুন": 7, "কৰ্কট": 7, "সিংহ": 0, "কন্যা": 7, "তুলা": 0, "বৃশ্চিক": 7, "ধনু": 7, "মকৰ": 0, "কুম্ভ": 0, "মীন": 7},
    "তুলা":    {"মেষ": 7, "বৃষ": 0, "মিথুন": 0, "কৰ্কট": 7, "সিংহ": 7, "কন্যা": 0, "তুলা": 7, "বৃশ্চিক": 0, "ধনু": 7, "মকৰ": 7, "কুম্ভ": 0, "মীন": 0},
    "বৃশ্চিক": {"মেষ": 0, "বৃষ": 7, "মিথুন": 0, "কৰ্কট": 0, "সিংহ": 7, "কন্যা": 7, "তুলা": 0, "বৃশ্চিক": 7, "ধনু": 0, "মকৰ": 7, "কুম্ভ": 7, "মীন": 0},
    "ধনু":     {"মেষ": 0, "বৃষ": 0, "মিথুন": 7, "কৰ্কট": 0, "সিংহ": 0, "কন্যা": 7, "তুলা": 7, "বৃশ্চিক": 0, "ধনু": 7, "মকৰ": 0, "কুম্ভ": 7, "মীন": 7},
    "মকৰ":     {"মেষ": 7, "বৃষ": 0, "মিথুন": 0, "কৰ্কট": 7, "সিংহ": 0, "কন্যা": 0, "তুলা": 7, "বৃশ্চিক": 7, "ধনু": 0, "মকৰ": 7, "কুম্ভ": 0, "মীন": 7},
    "কুম্ভ":    {"মেষ": 7, "বৃষ": 7, "মিথুন": 0, "কৰ্কট": 0, "সিংহ": 7, "কন্যা": 0, "তুলা": 0, "বৃশ্চিক": 7, "ধনু": 7, "মকৰ": 0, "কুম্ভ": 7, "মীন": 0},
    "মীন":     {"মেষ": 0, "বৃষ": 7, "মিথুন": 7, "কৰ্কট": 0, "সিংহ": 0, "কন্যা": 7, "তুলা": 0, "বৃশ্চিক": 0, "ধনু": 7, "মকৰ": 7, "কুম্ভ": 0, "মীন": 7},
}

# ─── Nadi (নাড়ী) by Nakshatra ───
# 1=Adi (আদি), 2=Madhya (মধ্য), 3=Antya (অন্ত্য)
NADI_BY_NAKSHATRA = {
    "অশ্বিনী": 1, "ভৰণী": 2, "কৃত্তিকা": 3, "ৰোহিণী": 1, "মৃগশিৰা": 2, "আৰ্দ্ৰা": 3,
    "পুনৰ্বসু": 1, "পুষ্যা": 2, "অশ্লেষা": 3, "মঘা": 1, "পূৰ্বফাল্গুনী": 2, "উত্তৰফাল্গুনী": 3,
    "হস্তা": 1, "চিত্ৰা": 2, "স্বাতী": 3, "বিশাখা": 1, "অনুৰাধা": 2, "জ্যেষ্ঠা": 3,
    "মূল": 1, "পূৰ্বাষাঢ়া": 2, "উত্তৰাষাঢ়া": 3, "শ্ৰৱণা": 1, "ধনিষ্ঠা": 2, "শতভিষা": 3,
    "পূৰ্বভাদ্ৰপদ": 1, "উত্তৰভাদ্ৰপদ": 2, "ৰেৱতী": 3
}

NADI_NAMES = {1: "আদি", 2: "মধ্য", 3: "অন্ত্য"}

# ─── Nakshatra to Rashi mapping ───
NAKSHATRA_TO_RASHI = {
    "অশ্বিনী": "মেষ", "ভৰণী": "মেষ", "কৃত্তিকা": "মেষ",
    "কৃত্তিকা": "বৃষ", "ৰোহিণী": "বৃষ", "মৃগশিৰা": "বৃষ",
    "মৃগশিৰা": "মিথুন", "আৰ্দ্ৰা": "মিথুন", "পুনৰ্বসু": "মিথুন",
    "পুনৰ্বসু": "কৰ্কট", "পুষ্যা": "কৰ্কট", "অশ্লেষা": "কৰ্কট",
    "মঘা": "সিংহ", "পূৰ্বফাল্গুনী": "সিংহ", "উত্তৰফাল্গুনী": "সিংহ",
    "উত্তৰফাল্গুনী": "কন্যা", "হস্তা": "কন্যা", "চিত্ৰা": "কন্যা",
    "চিত্ৰা": "তুলা", "স্বাতী": "তুলা", "বিশাখা": "তুলা",
    "বিশাখা": "বৃশ্চিক", "অনুৰাধা": "বৃশ্চিক", "জ্যেষ্ঠা": "বৃশ্চিক",
    "মূল": "ধনু", "পূৰ্বাষাঢ়া": "ধনু", "উত্তৰাষাঢ়া": "ধনু",
    "উত্তৰাষাঢ়া": "মকৰ", "শ্ৰৱণা": "মকৰ", "ধনিষ্ঠা": "মকৰ",
    "ধনিষ্ঠা": "কুম্ভ", "শতভিষা": "কুম্ভ", "পূৰ্বভাদ্ৰপদ": "কুম্ভ",
    "পূৰ্বভাদ্ৰপদ": "মীন", "উত্তৰভাদ্ৰপদ": "মীন", "ৰেৱতী": "মীন"
}

# Fix: some nakshatras span two rashis, we need the primary one
# For matching purposes, we use the rashi provided by the user directly
# The above mapping is for reference only


# ═══════════════════════════════════════════════════════════════════════════════
# ASHTAKOOT CALCULATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_varna(boy_rashi, girl_rashi):
    """
    ১. বৰ্ণ কূট (Varna Koota) - Max 1 Point
    Spiritual and mental compatibility based on caste/varna of rashis.
    Boy's varna should be equal to or higher than girl's varna.
    Lower number = higher varna (1=Brahmin highest, 4=Shudra lowest).
    """
    boy_varna = VARNA_BY_RASHI.get(boy_rashi, 3)
    girl_varna = VARNA_BY_RASHI.get(girl_rashi, 3)

    # Boy's varna number should be <= girl's varna number (boy higher or equal)
    if boy_varna <= girl_varna:
        score = 1
        result = "উত্তম"
    else:
        score = 0
        result = "অমিল"

    return {
        "score": score,
        "max_score": 1,
        "result": result,
        "boy_varna": VARNA_NAMES.get(boy_varna, ""),
        "girl_varna": VARNA_NAMES.get(girl_varna, ""),
        "description": f"পাত্ৰৰ বৰ্ণ {VARNA_NAMES.get(boy_varna, '')} আৰু পাত্ৰীৰ বৰ্ণ {VARNA_NAMES.get(girl_varna, '')}।"
    }


def calculate_vashya(boy_rashi, girl_rashi):
    """
    ২. বশ্য কূট (Vashya Koota) - Max 2 Points
    Mutual control, attraction, and influence between partners.
    Uses exact matrix: girl's vashya (row) x boy's vashya (col).
    """
    boy_vashya = VASHYA_BY_RASHI.get(boy_rashi, 2)
    girl_vashya = VASHYA_BY_RASHI.get(girl_rashi, 2)

    score = VASHYA_MATRIX.get(girl_vashya, {}).get(boy_vashya, 0)

    if score == 2:
        result = "উত্তম"
    elif score == 1:
        result = "মধ্যম"
    else:
        result = "অমিল"

    return {
        "score": score,
        "max_score": 2,
        "result": result,
        "boy_vashya": VASHYA_NAMES.get(boy_vashya, ""),
        "girl_vashya": VASHYA_NAMES.get(girl_vashya, ""),
        "description": f"পাত্ৰৰ বশ্য {VASHYA_NAMES.get(boy_vashya, '')} আৰু পাত্ৰীৰ বশ্য {VASHYA_NAMES.get(girl_vashya, '')}।"
    }


def calculate_tara(boy_nakshatra, girl_nakshatra):
    """
    ৩. তাৰা কূট (Tara Koota) - Max 3 Points
    Destiny, health, and well-being compatibility.

    Traditional method:
    1. Count from girl's nakshatra to boy's nakshatra, divide by 9, remainder = tara
    2. Count from boy's nakshatra to girl's nakshatra, divide by 9, remainder = tara
    3. Tara 3 (Vipat), 5 (Pratyari), 7 (Badha/Naidhana) are considered bad/ashubh
    4. Compare both directions:
       - Both good = 3 points (Uttam)
       - One good, one bad = 1.5 points (Madhyam)
       - Both bad = 0 points (Ashubh)
    """
    boy_idx = NAKSHATRAS.index(boy_nakshatra)
    girl_idx = NAKSHATRAS.index(girl_nakshatra)

    # Direction 1: Girl → Boy (count from girl to boy)
    dist_girl_to_boy = (boy_idx - girl_idx) % 27
    tara_girl_to_boy = (dist_girl_to_boy % 9) + 1  # 1-9

    # Direction 2: Boy → Girl (count from boy to girl)
    dist_boy_to_girl = (girl_idx - boy_idx) % 27
    tara_boy_to_girl = (dist_boy_to_girl % 9) + 1  # 1-9

    # Bad taras: 3=Vipat, 5=Pratyari, 7=Badha/Naidhana
    BAD_TARAS = [3, 5, 7]

    girl_to_boy_bad = tara_girl_to_boy in BAD_TARAS
    boy_to_girl_bad = tara_boy_to_girl in BAD_TARAS

    if not girl_to_boy_bad and not boy_to_girl_bad:
        # Both directions good
        score = 3
        result = "উত্তম"
    elif girl_to_boy_bad and boy_to_girl_bad:
        # Both directions bad
        score = 0
        result = "অশুভ"
    else:
        # One good, one bad
        score = 1.5
        result = "মধ্যম"

    return {
        "score": score,
        "max_score": 3,
        "result": result,
        "tara_girl_to_boy": tara_girl_to_boy,
        "tara_girl_to_boy_name": TARA_NAMES.get(tara_girl_to_boy, ""),
        "tara_boy_to_girl": tara_boy_to_girl,
        "tara_boy_to_girl_name": TARA_NAMES.get(tara_boy_to_girl, ""),
        "girl_to_boy_bad": girl_to_boy_bad,
        "boy_to_girl_bad": boy_to_girl_bad,
        "description": f"পাত্ৰীৰ নক্ষত্ৰৰ পৰা পাত্ৰৰ নক্ষত্ৰলৈ তাৰা: {TARA_NAMES.get(tara_girl_to_boy, '')} ({tara_girl_to_boy}), পাত্ৰৰ পৰা পাত্ৰীলৈ তাৰা: {TARA_NAMES.get(tara_boy_to_girl, '')} ({tara_boy_to_girl})।"
    }


def calculate_yoni(boy_nakshatra, girl_nakshatra):
    """
    ৪. যোনি কূট (Yoni Koota) - Max 4 Points
    Physical compatibility, intimacy, and biological harmony.
    Uses exact matrix: girl's yoni (row) x boy's yoni (col).
    """
    boy_yoni = YONI_BY_NAKSHATRA.get(boy_nakshatra, "")
    girl_yoni = YONI_BY_NAKSHATRA.get(girl_nakshatra, "")

    score = YONI_MATRIX.get(girl_yoni, {}).get(boy_yoni, 0)

    if score == 4:
        result = "উত্তম (একে যোনি)"
    elif score == 3:
        result = "উত্তম (মিত্ৰ যোনি)"
    elif score == 2:
        result = "মধ্যম (সাধাৰণ)"
    elif score == 1:
        result = "মধ্যম (সামান্য)"
    else:
        result = "অশুভ (শত্ৰু যোনি)"

    return {
        "score": score,
        "max_score": 4,
        "result": result,
        "boy_yoni": boy_yoni,
        "girl_yoni": girl_yoni,
        "description": f"পাত্ৰৰ যোনি '{boy_yoni}' আৰু পাত্ৰীৰ যোনি '{girl_yoni}'।"
    }


def calculate_graha_maitri(boy_rashi, girl_rashi):
    """
    ৫. গ্ৰহ মৈত্ৰী কূট (Graha Maitri) - Max 5 Points
    Psychological disposition and friendship between Moon sign lords.
    Uses exact matrix: girl's graha (row) x boy's graha (col).
    """
    boy_lord = RASHI_LORDS.get(boy_rashi, "")
    girl_lord = RASHI_LORDS.get(girl_rashi, "")

    score = GRAHA_MAITRI_MATRIX.get(girl_lord, {}).get(boy_lord, 0)

    if score == 5:
        result = "উত্তম (অধি মিত্ৰ)"
    elif score == 4:
        result = "উত্তম (মিত্ৰ)"
    elif score == 3:
        result = "মধ্যম (সম)"
    elif score == 1:
        result = "অমিল (শত্ৰু)"
    elif score == 0.5:
        result = "অমিল (অধি শত্ৰু)"
    else:
        result = "অশুভ (অধি শত্ৰু)"

    return {
        "score": score,
        "max_score": 5,
        "result": result,
        "boy_lord": boy_lord,
        "girl_lord": girl_lord,
        "description": f"পাত্ৰৰ ৰাশি অধিপতি '{boy_lord}' আৰু পাত্ৰীৰ ৰাশি অধিপতি '{girl_lord}'।"
    }


def calculate_gana(boy_nakshatra, girl_nakshatra):
    """
    ৬. গণ কূট (Gana Koota) - Max 6 Points
    Behavioral temperament compatibility (Deva, Manushya, Rakshasa).
    Uses exact matrix: girl's gana (row) x boy's gana (col).
    """
    boy_gana = GANA_BY_NAKSHATRA.get(boy_nakshatra, 2)
    girl_gana = GANA_BY_NAKSHATRA.get(girl_nakshatra, 2)

    score = GANA_MATRIX.get(girl_gana, {}).get(boy_gana, 0)

    if score == 6:
        result = "উত্তম (একে গণ)"
    elif score == 5:
        result = "উত্তম"
    elif score == 1:
        result = "অমিল (দেৱ-ৰাক্ষস)"
    else:
        result = "অমিল (মনুষ্য-ৰাক্ষস)"

    return {
        "score": score,
        "max_score": 6,
        "result": result,
        "boy_gana": GANA_NAMES.get(boy_gana, ""),
        "girl_gana": GANA_NAMES.get(girl_gana, ""),
        "description": f"পাত্ৰৰ গণ '{GANA_NAMES.get(boy_gana, '')}' আৰু পাত্ৰীৰ গণ '{GANA_NAMES.get(girl_gana, '')}'।"
    }


def calculate_bhakoot(boy_rashi, girl_rashi):
    """
    ৭. ভকূট কূট (Bhakoot Koota) - Max 7 Points
    Family welfare, prosperity, and emotional longevity.
    Uses exact matrix: girl's rashi (row) x boy's rashi (col).
    """
    score = BHAKOOT_MATRIX.get(girl_rashi, {}).get(boy_rashi, 0)

    if score == 7:
        result = "উত্তম"
    elif score == 4:
        result = "মধ্যম"
    else:
        # Determine which dosha
        boy_idx = RASHIS.index(boy_rashi)
        girl_idx = RASHIS.index(girl_rashi)
        distance = (boy_idx - girl_idx) % 12
        if distance == 2:
            dosha_name = "২-১২ দোষ (দ্বি-দ্বাদশ)"
        elif distance == 5:
            dosha_name = "৫-৯ দোষ (পঞ্চ-নৱম)"
        elif distance == 6:
            dosha_name = "৬-৮ দোষ (ষষ্ঠ-অষ্টম)"
        else:
            dosha_name = "অমিল"
        result = f"অশুভ ({dosha_name})"

    return {
        "score": score,
        "max_score": 7,
        "result": result,
        "description": f"পাত্ৰীৰ ৰাশি '{girl_rashi}' আৰু পাত্ৰৰ ৰাশি '{boy_rashi}'ৰ ভকূট মিলন।"
    }


def calculate_nadi(boy_nakshatra, girl_nakshatra):
    """
    ৮. নাড়ী কূট (Nadi Koota) - Max 8 Points
    Genetic health, progeny (সন্তান সুখ), and physiological compatibility.
    Same nadi = Nadi Dosha (নাড়ী দোষ) = 0 points.
    Different nadi = 8 points.
    """
    boy_nadi = NADI_BY_NAKSHATRA.get(boy_nakshatra, 1)
    girl_nadi = NADI_BY_NAKSHATRA.get(girl_nakshatra, 1)

    if boy_nadi == girl_nadi:
        score = 0
        result = f"অশুভ (নাড়ী দোষ - {NADI_NAMES.get(boy_nadi, '')} নাড়ী)"
    else:
        score = 8
        result = "উত্তম (নাড়ী দোষ নাই)"

    return {
        "score": score,
        "max_score": 8,
        "result": result,
        "boy_nadi": NADI_NAMES.get(boy_nadi, ""),
        "girl_nadi": NADI_NAMES.get(girl_nadi, ""),
        "description": f"পাত্ৰৰ নাড়ী '{NADI_NAMES.get(boy_nadi, '')}' আৰু পাত্ৰীৰ নাড়ী '{NADI_NAMES.get(girl_nadi, '')}'।"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MANGALIK DOSHA ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

MANGAL_HOUSES = [1, 4, 7, 8, 12]  # Houses where Mars causes Mangalik Dosha

def analyze_mangalik(boy_mars_house, girl_mars_house):
    """
    Analyze Mangalik Dosha for both boy and girl.
    mars_house: 1-12 (1-indexed house number)
    Returns detailed analysis.
    """
    boy_mangalik = boy_mars_house in MANGAL_HOUSES
    girl_mangalik = girl_mars_house in MANGAL_HOUSES

    # Determine severity
    def get_severity(house):
        if house == 7:
            return "তীব্ৰ"  # 7th house is most severe for marriage
        elif house in [1, 8]:
            return "মধ্যম"
        elif house in [4, 12]:
            return "সামান্য"
        return "অনুপস্থিত"

    boy_severity = get_severity(boy_mars_house) if boy_mangalik else "অনুপস্থিত"
    girl_severity = get_severity(girl_mars_house) if girl_mangalik else "অনুপস্থিত"

    # Cancellation logic
    cancellation = ""
    if boy_mangalik and girl_mangalik:
        cancellation = "দোষ সাম্য (উভয় মাংগলিক হোৱাৰ বাবে দোষৰ প্ৰভাৱ পৰস্পৰে নিষ্ক্ৰিয় কৰে)"
    elif not boy_mangalik and not girl_mangalik:
        cancellation = "কোনো মাংগলিক দোষ নাই"

    return {
        "boy_mangalik": boy_mangalik,
        "girl_mangalik": girl_mangalik,
        "boy_mars_house": boy_mars_house,
        "girl_mars_house": girl_mars_house,
        "boy_severity": boy_severity,
        "girl_severity": girl_severity,
        "cancellation": cancellation,
        "remedies": [
            "প্ৰতিদিন হনুমান চালিচা পাঠ কৰক",
            "মঙ্গলবাৰে ব্ৰত ৰাখক আৰু হনুমান মন্দিৰ দৰ্শন কৰক",
            "সেন্দুৰ আৰু মছুৰ দালি দান কৰক",
            "ৰঙা ৰঙৰ বস্ত্ৰ পৰিহাৰ কৰক",
            "মঙ্গল গ্ৰহৰ মন্ত্ৰ জাপ কৰক: 'ওঁ ক্ৰাং ক্ৰীং ক্ৰৌং সঃ ভৌমায় নমঃ'",
            "বিবাহৰ পূৰ্বে মাংগলিক দোষ নিবাৰণ পূজা কৰাওক",
            "তুলসী গছত জল অৰ্পণ কৰক আৰু প্ৰদক্ষিণ কৰক",
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN MATCHING FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def get_complete_jotok_milan(boy_data, girl_data):
    """
    Complete marriage matching analysis.

    Parameters:
    boy_data = {
        "name": str,
        "rashi": str (e.g., "মেষ"),
        "nakshatra": str (e.g., "অশ্বিনী"),
        "charan": int (1-4),
        "lagna": str (e.g., "মেষ"),
        "mars_house": int (1-12, 1-indexed)
    }
    girl_data = same structure

    Returns a comprehensive dict with all analysis.
    """
    boy_rashi = boy_data["rashi"]
    girl_rashi = girl_data["rashi"]
    boy_nakshatra = boy_data["nakshatra"]
    girl_nakshatra = girl_data["nakshatra"]

    # Calculate all 8 kootas
    varna = calculate_varna(boy_rashi, girl_rashi)
    vashya = calculate_vashya(boy_rashi, girl_rashi)
    tara = calculate_tara(boy_nakshatra, girl_nakshatra)
    yoni = calculate_yoni(boy_nakshatra, girl_nakshatra)
    graha_maitri = calculate_graha_maitri(boy_rashi, girl_rashi)
    gana = calculate_gana(boy_nakshatra, girl_nakshatra)
    bhakoot = calculate_bhakoot(boy_rashi, girl_rashi)
    nadi = calculate_nadi(boy_nakshatra, girl_nakshatra)

    # Total score
    total_score = sum([
        varna["score"], vashya["score"], tara["score"], yoni["score"],
        graha_maitri["score"], gana["score"], bhakoot["score"], nadi["score"]
    ])

    # Mangalik analysis
    mangalik = analyze_mangalik(boy_data.get("mars_house", 0), girl_data.get("mars_house", 0))

    # Overall verdict
    if total_score >= 28:
        verdict = "উত্তম (অতি শুভ)"
        verdict_class = "excellent"
        verdict_desc = "এই যোটক অতি উত্তম। বিবাহৰ বাবে অত্যন্ত শুভ আৰু সুপাৰিশিত। দাম্পত্য জীৱন সুখময়, সমৃদ্ধিশালী আৰু দীৰ্ঘস্থায়ী হ'ব।"
    elif total_score >= 22:
        verdict = "মধ্যম (শুভ)"
        verdict_class = "good"
        verdict_desc = "এই যোটক মধ্যম শ্ৰেণীৰ। বিবাহৰ বাবে গ্ৰহণযোগ্য। সামান্য প্ৰতিকাৰৰ দ্বাৰা দাম্পত্য জীৱন সুখময় কৰিব পাৰি।"
    elif total_score >= 18:
        verdict = "মধ্যম (গ্ৰহণযোগ্য)"
        verdict_class = "average"
        verdict_desc = "এই যোটক গড় মানৰ। কিছুমান দোষ থাকিলেও উপযুক্ত প্ৰতিকাৰৰ দ্বাৰা বিবাহ সম্ভৱ। জ্যোতিষীৰ পৰামৰ্শ লোৱাটো উচিত।"
    elif total_score >= 12:
        verdict = "অমিল (সাৱধানতা প্ৰয়োজন)"
        verdict_class = "warning"
        verdict_desc = "এই যোটকত যথেষ্ট অমিল আছে। বিবাহৰ পূৰ্বে জ্যোতিষীৰ পৰামৰ্শ আৰু প্ৰতিকাৰ অতি জৰুৰী।"
    else:
        verdict = "অশুভ (বিবাহ পৰামৰ্শিত নহয়)"
        verdict_class = "bad"
        verdict_desc = "এই যোটক অশুভ। পৰম্পৰাগতভাৱে এনে যোটকত বিবাহ পৰামৰ্শিত নহয়। তথাপিও জ্যোতিষীৰ পৰামৰ্শ লওক।"

    # Check for Nadi Dosha specifically
    has_nadi_dosha = nadi["score"] == 0
    has_bhakoot_dosha = bhakoot["score"] == 0

    return {
        "boy": boy_data,
        "girl": girl_data,
        "kootas": {
            "varna": varna,
            "vashya": vashya,
            "tara": tara,
            "yoni": yoni,
            "graha_maitri": graha_maitri,
            "gana": gana,
            "bhakoot": bhakoot,
            "nadi": nadi
        },
        "total_score": total_score,
        "max_score": 36,
        "verdict": verdict,
        "verdict_class": verdict_class,
        "verdict_desc": verdict_desc,
        "mangalik": mangalik,
        "has_nadi_dosha": has_nadi_dosha,
        "has_bhakoot_dosha": has_bhakoot_dosha
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ASSAMESE REPORT GENERATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def get_koota_name_asm(koota_key):
    """Get Assamese name for a koota."""
    names = {
        "varna": "বৰ্ণ কূট",
        "vashya": "বশ্য কূট",
        "tara": "তাৰা কূট",
        "yoni": "যোনি কূট",
        "graha_maitri": "গ্ৰহ মৈত্ৰী কূট",
        "gana": "গণ কূট",
        "bhakoot": "ভকূট কূট",
        "nadi": "নাড়ী কূট"
    }
    return names.get(koota_key, koota_key)


def get_koota_icon(koota_key):
    """Get icon for a koota."""
    icons = {
        "varna": "🕉️",
        "vashya": "💑",
        "tara": "⭐",
        "yoni": "💕",
        "graha_maitri": "🪐",
        "gana": "🎭",
        "bhakoot": "🏠",
        "nadi": "🧬"
    }
    return icons.get(koota_key, "✨")
