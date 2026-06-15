"""
══════════════════════════════════════════════════════════════
  GRAHA DOSHA i18n Labels
══════════════════════════════════════════════════════════════
"""

DOSHA_LABELS = {
    'as': {
        'title': 'গ্ৰহ দোষ বিশ্লেষণ',
        'present_label': 'উপস্থিত',
        'absent_label': 'অনুপস্থিত',
        'remedies_heading': 'প্ৰতিকাৰ (Remedies)',
        'no_remedies': 'কোনো বিশেষ প্ৰতিকাৰ নাই।',
        'severity_levels': {
            '0': 'অনুপস্থিত', '1': 'সামান্য', '2': 'মধ্যম', '3': 'তীব্ৰ', '4': 'অতি তীব্ৰ'
        },
        'dosha_names': {
            'mangal_dosha': 'মঙ্গল দোষ',
            'kaal_sarp_dosha': 'কাল সৰ্প দোষ',
            'pitra_dosha': 'পিতৃ দোষ',
            'grahan_dosha': 'গ্ৰহণ দোষ',
            'nadi_dosha': 'নাড়ী দোষ',
            'shani_dosha': 'শনি দোষ (সাড়ে সাতী)',
            'guru_chandal_dosha': 'গুৰু-চাণ্ডাল দোষ',
            'kemadruma_dosha': 'কেমদ্ৰুম দোষ',
        },
        'shani_phase_names': {
            'Rising': 'উদীয়মান',
            'Peak': 'শীৰ্ষ',
            'Setting': 'অস্তগামী',
            'Dhaiya': 'ঢৈয়া',
            'Not Running': 'সাড়ে সাতী চলি থকা নাই',
        },
    },
    'bn': {
        'title': 'গ্রহ দোষ বিশ্লেষণ',
        'present_label': 'উপস্থিত',
        'absent_label': 'অনুপস্থিত',
        'remedies_heading': 'প্রতিকার (Remedies)',
        'no_remedies': 'কোনো বিশেষ প্রতিকার নেই।',
        'severity_levels': {
            '0': 'অনুপস্থিত', '1': 'সামান্য', '2': 'মধ্যম', '3': 'তীব্র', '4': 'অতি তীব্র'
        },
        'dosha_names': {
            'mangal_dosha': 'মঙ্গল দোষ',
            'kaal_sarp_dosha': 'কাল সর্প দোষ',
            'pitra_dosha': 'পিতৃ দোষ',
            'grahan_dosha': 'গ্রহণ দোষ',
            'nadi_dosha': 'নাড়ী দোষ',
            'shani_dosha': 'শনি দোষ (সাড়ে সাতী)',
            'guru_chandal_dosha': 'গুরু-চাণ্ডাল দোষ',
            'kemadruma_dosha': 'কেমদ্রুম দোষ',
        },
        'shani_phase_names': {
            'Rising': 'উদীয়মান',
            'Peak': 'শীর্ষ',
            'Setting': 'অস্তগামী',
            'Dhaiya': 'ঢৈয়া',
            'Not Running': 'সাড়েসাতী চলছে না',
        },
    },
    'hi': {
        'title': 'ग्रह दोष विश्लेषण',
        'present_label': 'उपस्थित',
        'absent_label': 'अनुपस्थित',
        'remedies_heading': 'प्रतिकार (Remedies)',
        'no_remedies': 'कोई विशेष प्रतिकार नहीं।',
        'severity_levels': {
            '0': 'अनुपस्थित', '1': 'सामान्य', '2': 'मध्यम', '3': 'तीव्र', '4': 'अति तीव्र'
        },
        'dosha_names': {
            'mangal_dosha': 'मंगल दोष',
            'kaal_sarp_dosha': 'काल सर्प दोष',
            'pitra_dosha': 'पितृ दोष',
            'grahan_dosha': 'ग्रहण दोष',
            'nadi_dosha': 'नाड़ी दोष',
            'shani_dosha': 'शनि दोष (साढ़ेसाती)',
            'guru_chandal_dosha': 'गुरु-चांडाल दोष',
            'kemadruma_dosha': 'केमद्रम दोष',
        },
        'shani_phase_names': {
            'Rising': 'उदीयमान',
            'Peak': 'शीर्ष',
            'Setting': 'अस्तगामी',
            'Dhaiya': 'ढैया',
            'Not Running': 'साढ़ेसाती नहीं चल रही',
        },
    },
    'en': {
        'title': 'Planetary Dosha Analysis',
        'present_label': 'Present',
        'absent_label': 'Absent',
        'remedies_heading': 'Remedies',
        'no_remedies': 'No special remedies needed.',
        'severity_levels': {
            '0': 'None', '1': 'Mild', '2': 'Moderate', '3': 'Severe', '4': 'Very Severe'
        },
        'dosha_names': {
            'mangal_dosha': 'Mangal Dosha',
            'kaal_sarp_dosha': 'Kaal Sarp Dosha',
            'pitra_dosha': 'Pitra Dosha',
            'grahan_dosha': 'Grahan Dosha',
            'nadi_dosha': 'Nadi Dosha',
            'shani_dosha': 'Shani Dosha (Sade Sati)',
            'guru_chandal_dosha': 'Guru-Chandal Dosha',
            'kemadruma_dosha': 'Kemadruma Dosha',
        },
        'shani_phase_names': {
            'Rising': 'Rising',
            'Peak': 'Peak',
            'Setting': 'Setting',
            'Dhaiya': 'Dhaiya',
            'Not Running': 'Sade Sati not running',
        },
    },
}


def translate_dosha_result(results, lang='as'):
    """
    Translate dosha analysis results from Assamese to target language.
    Returns a new list with translated text fields.
    """
    if not results:
        return results

    L = DOSHA_LABELS.get(lang, DOSHA_LABELS['as'])
    severity_map = L.get('severity_levels', {})
    dosha_name_map = L.get('dosha_names', {})

    translated = []
    for dosha in results:
        d = dict(dosha)
        key = d.get('key', '')

        # Translate dosha name
        if 'info' in d and d['info']:
            info = dict(d['info'])
            # Translate name using dosha_name_map
            info['name'] = dosha_name_map.get(key, info.get('name', key))
            # Translate severity_text
            if 'severity_text' in d:
                d['severity_text'] = severity_map.get(str(d['severity']), d['severity_text'])
            # Translate remedies
            if 'remedies' in info and info['remedies']:
                info['remedies'] = info['remedies']  # Keep as-is for now (already in target lang from engine)
            d['info'] = info

        # Translate phase for shani dosha
        if key == 'shani_dosha' and 'phase' in d:
            shani_phases = L.get('shani_phase_names', {})
            d['phase'] = shani_phases.get(d['phase'], d['phase'])

        translated.append(d)

    return translated


# ═══════════════════════════════════════════════════════════════
#  GRAHA YOGA i18n Labels
# ═══════════════════════════════════════════════════════════════

YOGA_LABELS = {
    'as': {
        'title': 'গ্ৰহ যোগ বিশ্লেষণ',
        'effect_label': 'ফল',
        'category_label': 'শ্রেণী',
        'no_yoga': 'কোনো বিশেষ যোগ ধৰা পৰা নাই।',
        'yoga_names': {
            'ruchaka': 'ৰুচক যোগ (পঞ্চ মহাপুৰুষ)',
            'bhadra': 'ভদ্ৰ যোগ (পঞ্চ মহাপুৰুষ)',
            'hamsa': 'হংস যোগ (পঞ্চ মহাপুৰুষ)',
            'malavya': 'মালব্য যোগ (পঞ্চ মহাপুৰুষ)',
            'sasa': 'শশ যোগ (পঞ্চ মহাপুৰুষ)',
            'gajakesari': 'গজকেশৰী যোগ',
            'budhaditya': 'বুধাদিত্য যোগ',
            'lakshmi': 'লক্ষ্মী যোগ',
            'vipareeta_raja': 'বিপৰীত ৰাজযোগ',
            'dhana': 'ধন যোগ',
            'raja': 'ৰাজযোগ',
            'sunapha': 'সুনফা যোগ',
            'anapha': 'অনফা যোগ',
            'durudhara': 'দুৰুধৰা যোগ',
            'vasumati': 'বসুমতী যোগ',
            'amala': 'অমলা যোগ',
            'parvata': 'পৰ্বত যোগ',
            'kahala': 'কহল যোগ',
        },
        'yoga_categories': {
            'পঞ্চ মহাপুৰুষ যোগ': 'পঞ্চ মহাপুৰুষ যোগ',
            'শুভ যোগ': 'শুভ যোগ',
            'ধন যোগ': 'ধন যোগ',
            'ৰাজযোগ': 'ৰাজযোগ',
            'চন্দ্ৰ যোগ': 'চন্দ্ৰ যোগ',
        },
    },
    'bn': {
        'title': 'গ্রহ যোগ বিশ্লেষণ',
        'effect_label': 'ফল',
        'category_label': 'শ্রেণী',
        'no_yoga': 'কোনো বিশেষ যোগ ধরা পড়েনি।',
        'yoga_names': {
            'ruchaka': 'রুচক যোগ (পঞ্চ মহাপুরুষ)',
            'bhadra': 'ভদ্র যোগ (পঞ্চ মহাপুরুষ)',
            'hamsa': 'হংস যোগ (পঞ্চ মহাপুরুষ)',
            'malavya': 'মালব্য যোগ (পঞ্চ মহাপুরুষ)',
            'sasa': 'শশ যোগ (পঞ্চ মহাপুরুষ)',
            'gajakesari': 'গজকেশরী যোগ',
            'budhaditya': 'বুধাদিত্য যোগ',
            'lakshmi': 'লক্ষ্মী যোগ',
            'vipareeta_raja': 'বিপরীত রাজযোগ',
            'dhana': 'ধন যোগ',
            'raja': 'রাজযোগ',
            'sunapha': 'সুনফা যোগ',
            'anapha': 'অনফা যোগ',
            'durudhara': 'দুরুধরা যোগ',
            'vasumati': 'বসুমতী যোগ',
            'amala': 'অমলা যোগ',
            'parvata': 'পর্বত যোগ',
            'kahala': 'কহল যোগ',
        },
        'yoga_categories': {
            'পঞ্চ মহাপুৰুষ যোগ': 'পঞ্চ মহাপুরুষ যোগ',
            'শুভ যোগ': 'শুভ যোগ',
            'ধন যোগ': 'ধন যোগ',
            'ৰাজযোগ': 'রাজযোগ',
            'চন্দ্ৰ যোগ': 'চন্দ্র যোগ',
        },
    },
    'hi': {
        'title': 'ग्रह योग विश्लेषण',
        'effect_label': 'फल',
        'category_label': 'श्रेणी',
        'no_yoga': 'कोई विशेष योग नहीं मिला।',
        'yoga_names': {
            'ruchaka': 'रुचक योग (पंच महापुरुष)',
            'bhadra': 'भद्र योग (पंच महापुरुष)',
            'hamsa': 'हंस योग (पंच महापुरुष)',
            'malavya': 'मालव्य योग (पंच महापुरुष)',
            'sasa': 'शश योग (पंच महापुरुष)',
            'gajakesari': 'गजकेशरी योग',
            'budhaditya': 'बुधादित्य योग',
            'lakshmi': 'लक्ष्मी योग',
            'vipareeta_raja': 'विपरीत राजयोग',
            'dhana': 'धन योग',
            'raja': 'राजयोग',
            'sunapha': 'सुनफा योग',
            'anapha': 'अनफा योग',
            'durudhara': 'दुरुधरा योग',
            'vasumati': 'वसुमती योग',
            'amala': 'अमला योग',
            'parvata': 'पर्वत योग',
            'kahala': 'कहल योग',
        },
        'yoga_categories': {
            'পঞ্চ মহাপুৰুষ যোগ': 'पंच महापुरुष योग',
            'শুভ যোগ': 'शुभ योग',
            'ধন যোগ': 'धन योग',
            'ৰাজযোগ': 'राजयोग',
            'চন্দ্ৰ যোগ': 'चंद्र योग',
        },
    },
    'en': {
        'title': 'Planetary Yoga Analysis',
        'effect_label': 'Effect',
        'category_label': 'Category',
        'no_yoga': 'No special yogas found.',
        'yoga_names': {
            'ruchaka': 'Ruchaka Yoga (Pancha Mahapurusha)',
            'bhadra': 'Bhadra Yoga (Pancha Mahapurusha)',
            'hamsa': 'Hamsa Yoga (Pancha Mahapurusha)',
            'malavya': 'Malavya Yoga (Pancha Mahapurusha)',
            'sasa': 'Sasa Yoga (Pancha Mahapurusha)',
            'gajakesari': 'Gajakesari Yoga',
            'budhaditya': 'Budhaditya Yoga',
            'lakshmi': 'Lakshmi Yoga',
            'vipareeta_raja': 'Vipareeta Raja Yoga',
            'dhana': 'Dhana Yoga',
            'raja': 'Raja Yoga',
            'sunapha': 'Sunapha Yoga',
            'anapha': 'Anapha Yoga',
            'durudhara': 'Durudhara Yoga',
            'vasumati': 'Vasumati Yoga',
            'amala': 'Amala Yoga',
            'parvata': 'Parvata Yoga',
            'kahala': 'Kahala Yoga',
        },
        'yoga_categories': {
            'পঞ্চ মহাপুৰুষ যোগ': 'Pancha Mahapurusha Yoga',
            'শুভ যোগ': 'Shubh Yoga',
            'ধন যোগ': 'Dhana Yoga',
            'ৰাজযোগ': 'Raja Yoga',
            'চন্দ্ৰ যোগ': 'Chandra Yoga',
        },
    },
}


def translate_yoga_result(results, lang='as'):
    """
    Translate yoga analysis results from Assamese to target language.
    Returns a new list with translated text fields.
    """
    if not results:
        return results

    L = YOGA_LABELS.get(lang, YOGA_LABELS['as'])
    yoga_name_map = L.get('yoga_names', {})
    yoga_cat_map = L.get('yoga_categories', {})

    translated = []
    for yoga in results:
        y = dict(yoga)
        key = y.get('key', '')

        # Translate yoga name
        y['name'] = yoga_name_map.get(key, y.get('name', key))

        # Translate category
        if 'category' in y:
            y['category'] = yoga_cat_map.get(y['category'], y['category'])

        translated.append(y)

    return translated