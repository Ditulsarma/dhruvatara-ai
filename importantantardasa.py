import json
import os

def load_antardasha_data(filename='antardasha_data.json'):
    """
    JSON ফাইলৰ পৰা অন্তৰ্দশাৰ তথ্য ল'ড কৰিবলৈ।
    """
    try:
        # বৰ্তমানৰ ডাইৰেক্টৰীৰ পৰা ফাইলটোৰ সঠিক পথ নিৰ্ধাৰণ কৰা
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # JSON ফাইলটোৰ 'dasha_combinations' লিষ্টখন ঘূৰাই দিব
            return data.get("dasha_combinations", [])
    except FileNotFoundError:
        print(f"Error: {filename} পোৱা নগ'ল।")
        return []
    except json.JSONDecodeError:
        print(f"Error: {filename} পঢ়াত সমস্যা হৈছে। JSON ফৰ্মেট সঠিক নহয়।")
        return []

def get_important_antardasha_phala(maha_lord, antar_lord):
    """
    মহাদশা আৰু অন্তৰ্দশা গ্ৰহৰ নামৰ ওপৰত ভিত্তি কৰি ফলাফল দিবলৈ।
    যেনে: maha_lord="ৰবি", antar_lord="চন্দ্ৰ" দিলে "ৰবি-চন্দ্ৰ"ৰ ফলাফল ওলাব।
    """
    dasha_data = load_antardasha_data()
    
    if not dasha_data:
        return "তথ্য উপলব্ধ নহয়। অনুগ্ৰহ কৰি JSON ফাইলটো পৰীক্ষা কৰক।"
    
    # সন্ধান কৰিবলগীয়া combination (যেনে: "ৰবি-চন্দ্ৰ")
    target_combination = f"{maha_lord}-{antar_lord}"
    
    # JSON ডাটাৰ মাজত combination টো বিচাৰক
    for entry in dasha_data:
        combo = entry.get("combination", "")
        # Normalize: replace en-dash with hyphen for matching
        combo_normalized = combo.replace("\u2013", "-").replace("\u2014", "-")
        if combo_normalized == target_combination:
            return entry.get("description", "এই দশাৰ বিৱৰণ পোৱা নগ'ল।")
            
    return f"{maha_lord}ৰ মহাদশাত {antar_lord}ৰ অন্তৰ্দশাৰ ফলাফল বৰ্তমান উপলব্ধ নহয়।"

# স্ক্ৰিপ্টটো পৰীক্ষা কৰিবলৈ (Testing)
if __name__ == "__main__":
    # উদাহৰণ স্বৰূপে ৰবি মহাদশা আৰু চন্দ্ৰ অন্তৰ্দশাৰ ফলাফল বিচাৰক
    phala = get_important_antardasha_phala("ৰবি", "চন্দ্ৰ")
    print("ফলাফল:\n", phala)