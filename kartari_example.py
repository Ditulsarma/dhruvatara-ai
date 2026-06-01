"""
কৰ্তৰী যোগ চোৱাৰ উদাহৰণ
How to use Kartari Yoga Analysis
"""

from kartari_dosha import (
    generate_kartari_report,
    get_house_status_visual,
    get_complete_kartari_analysis
)

# উদাহৰণ: এজন ব্যক্তিৰ জন্মকুণ্ডলী ডেটা
# Example: Birth Chart Data (ঘৰৰ সংখ্যা 0-indexed)
example_birth_chart = {
    "ৰবি": 4,          # সূৰ্য ৫ম ঘৰত
    "চন্দ্ৰ": 2,        # চন্দ্ৰ ৩য় ঘৰত
    "মংগল": 0,        # মংগল ১ম ঘৰত
    "বুধ": 5,         # বুধ ৬ষ্ঠ ঘৰত
    "বৃহস্পতি": 7,      # বৃহস্পতি ৮ম ঘৰত
    "শুক্ৰ": 9,         # শুক্ৰ ১০ম ঘৰত
    "শনি": 1,          # শনি ২য় ঘৰত
    "ৰাহু": 3,          # ৰাহু ৪র্থ ঘৰত
    "কেতু": 9,         # কেতু ১০ম ঘৰত
}

print("\n" + "=" * 80)
print("কৰ্তৰী যোগ প্ৰদৰ্শন (Display Kartari Yoga)")
print("=" * 80)

# ১. সম্পূৰ্ণ ৰিপোৰ্ট প্ৰিণ্ট কৰক
print("\n1️⃣  সম্পূৰ্ণ ৰিপোৰ্ট চাওক:")
print("-" * 80)
report = generate_kartari_report(example_birth_chart)
print(report)

# ২. প্ৰতিটো ঘৰৰ ভিজ্যুৱেল স্থিতি চাওক
print("\n\n2️⃣  প্ৰতিটো ঘৰৰ কৰ্তৰী অৱস্থা:")
print("-" * 80)
house_status = get_house_status_visual(example_birth_chart)
for house_name, details in house_status.items():
    print(f"{house_name:12} | {details['status']:20} | {details['house_char']}")
    if details['planets']:
        print(f"{'':12} | গ্ৰহ: {', '.join(details['planets'])}")

# ৩. বিতং বিশ্লেষণ চাওক
print("\n\n3️⃣  বিতং বিশ্লেষণ ডেটা:")
print("-" * 80)
full_analysis = get_complete_kartari_analysis(example_birth_chart)

print("\n✅ শুভ কৰ্তৰী যোগ যুক্ত ঘৰ:")
if full_analysis["house_kartari"]["shubh_kartari"]["affected_houses"]:
    for house in full_analysis["house_kartari"]["shubh_kartari"]["affected_houses"]:
        print(f"  • ঘৰ #{house['house'] + 1}: {house['house_name']}")
        print(f"    প্ৰভাৱ: {house['effect']}")
else:
    print("  কোনো শুভ কৰ্তৰী নাই")

print("\n⚠️ পাপ কৰ্তৰী যোগ যুক্ত ঘৰ:")
if full_analysis["house_kartari"]["pap_kartari"]["affected_houses"]:
    for house in full_analysis["house_kartari"]["pap_kartari"]["affected_houses"]:
        print(f"  • ঘৰ #{house['house'] + 1}: {house['house_name']}")
        print(f"    প্ৰভাৱ: {house['effect']}")
else:
    print("  কোনো পাপ কৰ্তৰী নাই")

print("\n🟡 মিশ্ৰিত কৰ্তৰী যোগ যুক্ত ঘৰ:")
if full_analysis["house_kartari"]["mixed_kartari"]["affected_houses"]:
    for house in full_analysis["house_kartari"]["mixed_kartari"]["affected_houses"]:
        print(f"  • ঘৰ #{house['house'] + 1}: {house['house_name']}")
        print(f"    প্ৰভাৱ: {house['effect']}")
else:
    print("  কোনো মিশ্ৰিত কৰ্তৰী নাই")

print("\n" + "=" * 80)