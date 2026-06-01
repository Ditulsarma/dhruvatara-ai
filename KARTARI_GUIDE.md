from kartari_dosha import generate_kartari_report

# আপোনাৰ জন্মকুণ্ডলী ডেটা (ঘৰ ০-১১, 0-indexed)
my_chart = {
    "ৰবি": 4,        # সূৰ্য ৫ম ঘৰত
    "চন্দ্ৰ": 2,      # চন্দ্ৰ ৩য় ঘৰত
    "মংগল": 0,      # মংগল ১ম ঘৰত
    # ... আন সকলো গ্ৰহ
}

# সম্পূৰ্ণ ৰিপোৰ্ট প্ৰিণ্ট কৰক
report = generate_kartari_report(my_chart)
print(report)