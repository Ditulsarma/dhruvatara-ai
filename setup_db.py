"""
ধ্ৰুৱতৰা AI - Database Setup
Creates all tables for subscription-based user management system.
Run: python setup_db.py
"""

import sqlite3
from werkzeug.security import generate_password_hash
from config import DB_PATH

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ─── Existing table ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_name TEXT UNIQUE NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    ''')

    # ─── Admin table ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ─── Users table ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            is_active INTEGER DEFAULT 0,
            is_verified_email INTEGER DEFAULT 0,
            is_verified_mobile INTEGER DEFAULT 0,
            email_otp TEXT,
            mobile_otp TEXT,
            otp_expiry TIMESTAMP,
            subscription_id INTEGER DEFAULT 1,
            subscription_expiry DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
        )
    ''')

    # ─── Subscriptions table ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_asm TEXT NOT NULL,
            price REAL NOT NULL,
            duration_days INTEGER NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ─── Feature definitions table ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feature_definitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_key TEXT UNIQUE NOT NULL,
            feature_name TEXT NOT NULL,
            feature_name_asm TEXT NOT NULL,
            description TEXT,
            category TEXT,
            display_order INTEGER DEFAULT 0
        )
    ''')

    # ─── Subscription features ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subscription_id INTEGER NOT NULL,
            feature_key TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(id),
            FOREIGN KEY (feature_key) REFERENCES feature_definitions(feature_key),
            UNIQUE(subscription_id, feature_key)
        )
    ''')

    # ─── Per-user feature overrides ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_feature_overrides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            feature_key TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            set_by_admin_id INTEGER,
            set_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (feature_key) REFERENCES feature_definitions(feature_key),
            FOREIGN KEY (set_by_admin_id) REFERENCES admins(id),
            UNIQUE(user_id, feature_key)
        )
    ''')

    # ─── Login logs ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            is_admin INTEGER DEFAULT 0,
            ip_address TEXT,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ─── Password reset tokens ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ─── Saved Kundlis table ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_kundlis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            tob TEXT NOT NULL,
            place TEXT NOT NULL,
            gender TEXT DEFAULT 'male',
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            timezone REAL DEFAULT 5.5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ─── Admin Settings table ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ─── Insert default admin settings ───
    cursor.execute('''
        INSERT OR IGNORE INTO admin_settings (setting_key, setting_value)
        VALUES ('user_auto_activate', 'admin_approval')
    ''')

    # ─── Admin Images table ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_key TEXT NOT NULL,
            placement TEXT NOT NULL DEFAULT 'general',
            page_target TEXT DEFAULT 'all',
            filename TEXT NOT NULL,
            mime_type TEXT DEFAULT 'image/png',
            width INTEGER DEFAULT 200,
            height INTEGER DEFAULT 200,
            alt_text TEXT DEFAULT '',
            image_data BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ─── Astrologer Profiles table ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS astrologer_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            institution_name TEXT DEFAULT '',
            astrologer_name TEXT DEFAULT '',
            astrologer_bio TEXT DEFAULT '',
            address TEXT DEFAULT '',
            mobile TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ─── Admin Feature Toggles (for Numerology & other modules) ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_feature_toggles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_key TEXT UNIQUE NOT NULL,
            feature_label TEXT NOT NULL,
            feature_label_asm TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            is_enabled INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ─── Numerology Saved Reports ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS numerology_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            report_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ─── User Activity Tracking ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            activity_name TEXT NOT NULL,
            activity_name_asm TEXT NOT NULL,
            page_url TEXT,
            ip_address TEXT,
            session_start TIMESTAMP,
            session_end TIMESTAMP,
            duration_seconds INTEGER DEFAULT 0,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ─── User Daily RashiPhal Tracking ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_rashifal_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            rashi_name TEXT NOT NULL,
            period TEXT NOT NULL,
            usage_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, rashi_name, usage_date)
        )
    ''')

    # ─── User Daily Session Tracking (free users: max 3 sessions/day) ───
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_date DATE NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            logout_time TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ─── Insert default admin astrologer profile (user_id=0 for admin fallback) ───
    cursor.execute('''
        INSERT OR IGNORE INTO astrologer_profiles (user_id, institution_name, astrologer_name, astrologer_bio, address, mobile)
        VALUES (0, '', '', '', '', '')
    ''')

    # ─── Insert default admin feature toggles for Numerology ───
    numer_toggles = [
        ("numerology_lo_shu", "Lo Shu Grid", "ল' চু গ্ৰীড", "numerology", 1),
        ("numerology_missing", "Missing Numbers", "অনুপস্থিত সংখ্যা", "numerology", 1),
        ("numerology_present", "Present Numbers", "উপস্থিত সংখ্যা", "numerology", 1),
        ("numerology_mulyanka", "Mulyanka", "মূল্যাংক", "numerology", 1),
        ("numerology_bhagyanka", "Bhagyanka", "ভাগ্যাংক", "numerology", 1),
        ("numerology_namanka", "Namanka", "নামাংক", "numerology", 1),
        ("numerology_name_compat", "Name Compatibility", "নাম সামঞ্জস্য", "numerology", 1),
        ("numerology_angel", "Angel Number", "এঞ্জেল সংখ্যা", "numerology", 1),
        ("numerology_varsha_phal", "Varsha Phal", "বৰ্ষফল", "numerology", 1),
        ("numerology_pratikar", "Pratikar (Remedies)", "প্ৰতিকাৰ", "numerology", 1),
        ("numerology_final", "Final Prediction", "চূড়ান্ত ভৱিষ্যদ্বাণী", "numerology", 1),
        ("numerology_chat", "AI Chat", "AI চেট", "numerology", 1),
        ("numerology_kua", "Kua Number", "কোৱা নম্বৰ", "numerology", 1),
        ("numerology_subha", "Subha Details", "শুভ ৰং-সংখ্যা-তাৰিখ", "numerology", 1),
        ("numerology_num_compat", "Number Compatibility", "সংখ্যা মিত্ৰতা-শত্ৰুতা", "numerology", 1),
        ("numerology_gem_advice", "Gem & Rudraksha", "ৰত্ন আৰু ৰুদ্ৰাক্ষ", "numerology", 1),
        ("numerology_lal_kitab", "Lal Kitab Remedies", "লাল কিতাপ প্ৰতিকাৰ", "numerology", 1),
        ("numerology_name_breakdown", "Name Breakdown", "নামৰ আখৰ বিশ্লেষণ", "numerology", 1),
        ("numerology_chaldean", "Chaldean Chart", "Chaldean তালিকা", "numerology", 1),
        ("numerology_planes", "Lo Shu Planes", "ল' চু গ্ৰীডৰ ৮ যোগ", "numerology", 1),
    ]
    for f_key, f_label, f_label_asm, f_cat, f_enabled in numer_toggles:
        cursor.execute('''
            INSERT OR IGNORE INTO admin_feature_toggles (feature_key, feature_label, feature_label_asm, category, is_enabled)
            VALUES (?, ?, ?, ?, ?)
        ''', (f_key, f_label, f_label_asm, f_cat, f_enabled))

    # ─── Insert default admin ───
    admin_username = "DitulSarma"
    admin_password = "HARIPUR1----"
    admin_hash = generate_password_hash(admin_password)
    cursor.execute('''
        INSERT OR IGNORE INTO admins (username, password_hash)
        VALUES (?, ?)
    ''', (admin_username, admin_hash))

    # ─── Insert feature definitions ───
    features = [
        ("kundli_calculate", "Kundli Calculate", "কুণ্ডলী গণনা", "জন্ম কুণ্ডলী প্ৰস্তুত কৰক", "core", 1),
        ("varga_charts", "Varga Charts", "বিভাগীয় কুণ্ডলী", "ষোড়শবৰ্গ কুণ্ডলী চাৰ্ট", "charts", 2),
        ("panchanga", "Panchanga", "পঞ্চাঙ্গ", "পঞ্চাঙ্গ গণনা", "core", 3),
        ("dosha_analysis", "Dosha Analysis", "দোষ বিশ্লেষণ", "মাংগলিক, কালসৰ্প আদি দোষ", "analysis", 4),
        ("yoga_analysis", "Yoga Analysis", "যোগ বিশ্লেষণ", "ৰাজযোগ, ধনযোগ আদি", "analysis", 5),
        ("dasha", "Dasha", "বিংশোত্তৰী দশা", "মহাদশা-অন্তৰ্দশা-প্ৰত্যন্তৰ্দশা", "prediction", 6),
        ("ai_interpretation", "AI Interpretation", "AI বিশ্লেষণ", "কৃত্ৰিম বুদ্ধিমত্তাৰ দ্বাৰা বিশ্লেষণ", "ai", 7),
        ("pdf_report", "PDF Report", "PDF ৰিপৰ্ট", "PDF ৰিপৰ্ট ডাউনলোড", "export", 8),
        ("nakshatra_phala", "Nakshatra Phala", "নক্ষত্ৰ ফল", "নক্ষত্ৰৰ ফলাফল", "prediction", 9),
        ("lagna_phala", "Lagna Phala", "লগ্ন ফল", "লগ্নৰ ফলাফল", "prediction", 10),
        ("rashi_phala", "Rashi Phala", "ৰাশি ফল", "ৰাশিৰ ফলাফল", "prediction", 11),
        ("sannari_chakra", "Sannari Chakra", "সন্নাৰী চক্ৰ", "সন্নাৰী চক্ৰ বিশ্লেষণ", "charts", 12),
        ("navatara_chakra", "Navatara Chakra", "নৱতাৰা চক্ৰ", "নৱতাৰা চক্ৰ বিশ্লেষণ", "charts", 13),
        ("tripap_rista", "Tripap Rista", "ত্ৰিপাপ ৰিষ্ট", "ত্ৰিপাপ ৰিষ্ট বিশ্লেষণ", "analysis", 14),
        ("custom_pdf", "Custom PDF", "কাষ্টম PDF", "নিৰ্বাচিত অংশৰ PDF", "export", 15),
        ("patrika_pdf", "Patrika PDF", "পত্ৰিকা PDF", "পত্ৰিকা PDF ডাউনলোড", "export", 16),
        ("numerology", "Numerology", "অংক জ্যোতিষ", "অংক জ্যোতিষ গণনা আৰু বিশ্লেষণ", "numerology", 17),
        ("numerology_pdf", "Numerology PDF", "অংক জ্যোতিষ PDF", "অংক জ্যোতিষ PDF ৰিপৰ্ট ডাউনলোড", "numerology", 18),
        ("numerology_varsha", "Numerology Varsha Phal", "অংক জ্যোতিষ বৰ্ষফল", "১০ বছৰৰ বৰ্ষফল", "numerology", 19),
        ("numerology_chat", "Numerology AI Chat", "অংক জ্যোতিষ AI চেট", "অংক জ্যোতিষ AI চেট", "numerology", 20),
        ("pratyantar_dasha_pdf", "Pratyantar Dasha PDF", "প্ৰত্যন্তৰ দশা PDF", "প্ৰত্যন্তৰ দশা ফলসহ PDF ডাউনলোড", "export", 21),
        ("graha_maitri", "Graha Maitri", "গ্ৰহ মৈত্ৰী", "গ্ৰহৰ নৈসৰ্গিক, তাৎকালীন আৰু পঞ্চধা মৈত্ৰী চক্ৰ", "analysis", 22),
    ]

    for f_key, f_name, f_name_asm, f_desc, f_cat, f_order in features:
        cursor.execute('''
            INSERT OR IGNORE INTO feature_definitions (feature_key, feature_name, feature_name_asm, description, category, display_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (f_key, f_name, f_name_asm, f_desc, f_cat, f_order))

    # ─── Insert default subscriptions ───
    subs = [
        (1, "Free", "বিনামূলীয়া", 0.0, 36500, "সীমিত সুবিধাসহ বিনামূলীয়া প্লেন"),
        (2, "Basic", "বেচিক", 99.0, 30, "মৌলিক বৈশিষ্ট্যসমূহ"),
        (3, "Premium", "প্ৰিমিয়াম", 299.0, 90, "উন্নত বৈশিষ্ট্যসমূহ মাহেকীয়া চাবস্ক্ৰিপচন"),
        (4, "Pro", "প্ৰ'", 999.0, 365, "সকলো বৈশিষ্ট্যৰ সম্পূৰ্ণ এক্সেছ এবছৰৰ বাবে চাবস্ক্ৰিপচন"),
    ]

    for s_id, s_name, s_name_asm, s_price, s_dur, s_desc in subs:
        cursor.execute('''
            INSERT OR IGNORE INTO subscriptions (id, name, name_asm, price, duration_days, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (s_id, s_name, s_name_asm, s_price, s_dur, s_desc))

    # ─── Assign features to subscriptions ───
    # All features enabled by default EXCEPT pdf_report and custom_pdf
    all_features = [
        "kundli_calculate", "varga_charts", "panchanga", "dosha_analysis",
        "yoga_analysis", "dasha", "ai_interpretation", "nakshatra_phala",
        "lagna_phala", "sannari_chakra", "navatara_chakra",
        "tripap_rista", "graha_maitri"
    ]
    # rashi_phala is separate: disabled for free, enabled for paid
    rashi_phala_feature = "rashi_phala"
    # PDF features: disabled for free, enabled for paid plans
    pdf_features = ["pdf_report", "custom_pdf", "patrika_pdf", "pratyantar_dasha_pdf"]

    # All subscriptions get all non-PDF features enabled
    for sub_id in [1, 2, 3, 4]:
        for feat_key in all_features:
            cursor.execute('''
                INSERT OR IGNORE INTO subscription_features (subscription_id, feature_key, enabled)
                VALUES (?, ?, 1)
            ''', (sub_id, feat_key))
        # PDF features: enabled for paid plans (2,3,4), disabled for free (1)
        for feat_key in pdf_features:
            pdf_enabled = 0 if sub_id == 1 else 1
            cursor.execute('''
                INSERT OR IGNORE INTO subscription_features (subscription_id, feature_key, enabled)
                VALUES (?, ?, ?)
            ''', (sub_id, feat_key, pdf_enabled))
        # rashi_phala: enabled for paid plans (2,3,4), disabled for free (1)
        rashi_enabled = 0 if sub_id == 1 else 1
        cursor.execute('''
            INSERT OR IGNORE INTO subscription_features (subscription_id, feature_key, enabled)
            VALUES (?, ?, ?)
        ''', (sub_id, rashi_phala_feature, rashi_enabled))

    # ─── Numerology features: all plans get basic access ───
    numer_features = ["numerology", "numerology_chat"]
    for sub_id in [1, 2, 3, 4]:
        for feat_key in numer_features:
            cursor.execute('''
                INSERT OR IGNORE INTO subscription_features (subscription_id, feature_key, enabled)
                VALUES (?, ?, 1)
            ''', (sub_id, feat_key))

    # ─── Pro-only numerology features (varsha phal + pdf) ───
    numer_pro_features = ["numerology_pdf", "numerology_varsha"]
    for sub_id in [1, 2, 3, 4]:
        for feat_key in numer_pro_features:
            # Only Pro (id=4) gets these by default; others disabled
            enabled = 1 if sub_id == 4 else 0
            cursor.execute('''
                INSERT OR IGNORE INTO subscription_features (subscription_id, feature_key, enabled)
                VALUES (?, ?, ?)
            ''', (sub_id, feat_key, enabled))

    # ─── Insert geo data from locations.json ───
    import json, os
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locations.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            locations = json.load(f)
        for loc in locations:
            cursor.execute('''
                INSERT OR IGNORE INTO locations (place_name, latitude, longitude)
                VALUES (?, ?, ?)
            ''', (loc['name'], loc['lat'], loc['lon']))
        location_count = len(locations)
    except FileNotFoundError:
        print("⚠️  locations.json পোৱা নগ'ল। কোনো স্থান যোগ কৰা নহ'ল।")
        location_count = 0

    conn.commit()
    conn.close()

    # ─── Cleanup: Remove rashi_phala overrides for free users ───
    _cleanup_free_user_rashifal()

    print("✅ Database setup complete!")
    print(f"   Admin: DitulSarma")
    print(f"   4 Subscription plans created")
    print(f"   15 Feature definitions created")
    print(f"   {location_count} Locations added")


def _cleanup_free_user_rashifal():
    """Remove any rashi_phala feature overrides from free users (subscription_id=1).
    Also remove ALL overrides from Pro users so they get full subscription features.
    Also fix subscription_features table for rashi_phala and PDF features."""
    conn = sqlite3.connect(DB_PATH)
    try:
        # Fix subscription_features: ensure rashi_phala is OFF for free, ON for paid
        conn.execute("UPDATE subscription_features SET enabled = 0 WHERE subscription_id = 1 AND feature_key = 'rashi_phala'")
        conn.execute("UPDATE subscription_features SET enabled = 1 WHERE subscription_id IN (2,3,4) AND feature_key = 'rashi_phala'")

        # Fix PDF features: OFF for free, ON for paid
        pdf_features = ["pdf_report", "custom_pdf", "patrika_pdf", "pratyantar_dasha_pdf"]
        for feat in pdf_features:
            conn.execute(f"UPDATE subscription_features SET enabled = 0 WHERE subscription_id = 1 AND feature_key = '{feat}'")
            conn.execute(f"UPDATE subscription_features SET enabled = 1 WHERE subscription_id IN (2,3,4) AND feature_key = '{feat}'")

        # Remove rashi_phala overrides from free users
        conn.execute('''
            DELETE FROM user_feature_overrides
            WHERE feature_key = 'rashi_phala'
            AND user_id IN (SELECT id FROM users WHERE subscription_id = 1)
        ''')
        free_cleaned = conn.total_changes

        # Remove ALL overrides from Pro users (subscription_id > 1)
        # so they automatically get all features from their subscription plan
        conn.execute('''
            DELETE FROM user_feature_overrides
            WHERE user_id IN (SELECT id FROM users WHERE subscription_id > 1)
        ''')
        pro_cleaned = conn.total_changes - free_cleaned

        conn.commit()
        if free_cleaned > 0 or pro_cleaned > 0:
            print(f"   🧹 Cleanup: {free_cleaned} free-user rashi_phala overrides removed, {pro_cleaned} Pro-user overrides cleared")
    except Exception as e:
        print(f"   ⚠️ Cleanup error (non-fatal): {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    setup_database()
