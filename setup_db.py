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

    # ─── Insert default admin astrologer profile (user_id=0 for admin fallback) ───
    cursor.execute('''
        INSERT OR IGNORE INTO astrologer_profiles (user_id, institution_name, astrologer_name, astrologer_bio, address, mobile)
        VALUES (0, '', '', '', '', '')
    ''')

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
        "lagna_phala", "rashi_phala", "sannari_chakra", "navatara_chakra",
        "tripap_rista"
    ]
    # PDF features are disabled by default for all plans
    pdf_features = ["pdf_report", "custom_pdf", "patrika_pdf"]

    # All subscriptions get all non-PDF features enabled
    for sub_id in [1, 2, 3, 4]:
        for feat_key in all_features:
            cursor.execute('''
                INSERT OR IGNORE INTO subscription_features (subscription_id, feature_key, enabled)
                VALUES (?, ?, 1)
            ''', (sub_id, feat_key))
        # PDF features are disabled by default
        for feat_key in pdf_features:
            cursor.execute('''
                INSERT OR IGNORE INTO subscription_features (subscription_id, feature_key, enabled)
                VALUES (?, ?, 0)
            ''', (sub_id, feat_key))

    # ─── Insert geo data ───
    geo_data = {
        "Dibrugarh, Assam": (27.4722, 94.9122), "Guwahati, Assam": (26.1445, 91.7362),
         "Sivasagar, Assam": (26.9833, 94.6333),
        "Tezpur, Assam": (26.6333, 92.8000), "Hojai, Assam": (26.0002, 92.8576),
        "Bokakhat, Assam": (26.3800, 93.3500), "Nalbari, Assam": (26.26, 91.26),
        "Barpeta, Assam": (26.19, 90.00), "Amingaon, Assam": (26.11, 91.41),
        "Nagaon, Assam": (26.21, 92.41), "Morigaon, Assam": (26.15, 92.20),
        "Golaghat, Assam": (26.31, 93.58), "Jorhat, Assam": (26.45, 94.13),
        "Majuli, Assam": (26.57, 94.10), "Duliajan, Assam": (27.22, 95.18),
        "Moran, Assam": (27.11, 94.55), "Tinsukia, Assam": (27.30, 95.22),
        "Bongaigaon, Assam": (26.28, 90.34), "Kokrajhar, Assam": (26.24, 90.16),
        "Gossaigaon, Assam": (26.25, 89.59), "Dhubri, Assam": (26.01, 89.59),
        "Goalpara, Assam": (26.10, 90.37), "Itanagar, Arunachal Pradesh": (27.06, 93.37),
        "Shillong, Meghalaya": (25.34, 91.53), "Silchar, Assam": (24.49, 92.48),
        "Sarthebari, Assam": (26.23, 91.10), "Tamulpur, Assam": (26.38, 91.34),
        "Barpeta Road, Assam": (26.30, 90.58),
        "Bihpuria, Lakhimpur, Assam": (27.0200, 93.8800),
        "Narayanpur, Lakhimpur, Assam": (26.9800, 93.8600),
        "Laluk, Lakhimpur, Assam": (27.0900, 93.9900),
        "Nowboicha, Lakhimpur, Assam": (27.1500, 93.9700),
        "Dhakuakhana, Lakhimpur, Assam": (27.2000, 94.4500),
        "Boginadi, Lakhimpur, Assam": (27.3400, 94.1300),
        "Panigaon, Lakhimpur, Assam": (27.1800, 94.1300),
        "Azad, Lakhimpur, Assam": (27.1600, 94.0300),
        "Kadam, Lakhimpur, Assam": (27.2200, 94.1800),
        "Harmoti, Lakhimpur, Assam": (27.0600, 93.8500),
        "Bandardewa, Lakhimpur, Assam": (27.0800, 93.8300),
        "Joyhing, Lakhimpur, Assam": (27.2400, 94.0200),
        "Phulbari, Lakhimpur, Assam": (27.0500, 93.9100),
        "Ghilamara, Lakhimpur, Assam": (27.2000, 94.3400),
        "Batowmari, Lakhimpur, Assam": (27.1400, 94.3900),
        "Dhunaguri, Lakhimpur, Assam": (26.9600, 93.8900),
        "Badati, Lakhimpur, Assam": (26.9100, 93.9200),
        "Bongalmora, Lakhimpur, Assam": (27.0100, 93.9500),
        "Islampur, Lakhimpur, Assam": (27.1100, 93.9200),
        "Silapathar, Dhemaji, Assam": (27.5900, 94.7300),
        "Jonai, Dhemaji, Assam": (27.8300, 95.1600),
        "Gogamukh, Dhemaji, Assam": (27.4200, 94.3400),
        "Sissiborgaon, Dhemaji, Assam": (27.4900, 94.6100),
        "Simen Chapori, Dhemaji, Assam": (27.6700, 94.8800),
        "Machkhowa, Dhemaji, Assam": (27.2800, 94.4600),
        "Dergaon, Golaghat, Assam": (26.7000, 93.9700),
        "Sarupathar, Golaghat, Assam": (26.1800, 93.8700),
        "Numaligarh, Golaghat, Assam": (26.6000, 93.7300),
        "Kaziranga, Golaghat, Assam": (26.5700, 93.3100),
        "Teok, Jorhat, Assam": (26.8300, 94.4100),
        "Nimati Ghat, Jorhat, Assam": (26.8500, 94.2500),
        "Amguri, Sivasagar, Assam": (26.8000, 94.5300),
        "Sonari, Charaideo, Assam": (27.0200, 95.0300),
        "Nazira, Sivasagar, Assam": (26.9200, 94.7300),
        "Namrup, Dibrugarh, Assam": (27.1800, 95.3300),
        "Chabua, Dibrugarh, Assam": (27.4800, 95.1700),
        "Naharkatia, Dibrugarh, Assam": (27.2800, 95.3300),
        "Margherita, Tinsukia, Assam": (27.2800, 95.6700),
        "Digboi Oil Town, Tinsukia, Assam": (27.3800, 95.6300),
        "Doom Dooma, Tinsukia, Assam": (27.5700, 95.5700),
        "Ledo, Tinsukia, Assam": (27.2900, 95.7400),
        "Jagiroad, Morigaon, Assam": (26.1100, 92.2100),
        "Lanka, Hojai, Assam": (25.9200, 92.9500),
        "Lumding, Hojai, Assam": (25.7500, 93.1700),
        "Raha, Nagaon, Assam": (26.2300, 92.5100),
        "Kaliabor, Nagaon, Assam": (26.5100, 92.9800),
        "Gauripur, Dhubri, Assam": (26.0800, 89.9700),
        "Lakhipur, Goalpara, Assam": (26.0000, 90.3000),
        "Dibrugarh, Assam": (27.4722, 94.9122),
        "Guwahati, Assam": (26.1445, 91.7362),
        "Sivasagar, Assam": (26.9833, 94.6333),
        "Tezpur, Assam": (26.6333, 92.8000),
        "Hojai, Assam": (26.0002, 92.8576),
        "Bokakhat, Assam": (26.3800, 93.3500),
        "Nalbari, Assam": (26.26, 91.26),
        "Barpeta, Assam": (26.19, 90.00),
        "Amingaon, Assam": (26.11, 91.41),
        "Nagaon, Assam": (26.21, 92.41),
        "Morigaon, Assam": (26.15, 92.20),
        "Golaghat, Assam": (26.31, 93.58),
        "Jorhat, Assam": (26.45, 94.13),
        "Majuli, Assam": (26.57, 94.10),
        "Duliajan, Assam": (27.22, 95.18),
        "Moran, Assam": (27.11, 94.55),
        "Tinsukia, Assam": (27.30, 95.22),
        "Bongaigaon, Assam": (26.28, 90.34),
        "Kokrajhar, Assam": (26.24, 90.16),
        "Gossaigaon, Assam": (26.25, 89.59),
        "Dhubri, Assam": (26.01, 89.59),
        "Goalpara, Assam": (26.10, 90.37),
        "Itanagar, Arunachal Pradesh": (27.06, 93.37),
        "Shillong, Meghalaya": (25.34, 91.53),
        "Silchar, Assam": (24.49, 92.48),
        "Sarthebari, Assam": (26.23, 91.10),
        "Tamulpur, Assam": (26.38, 91.34),
        "Barpeta Road, Assam": (26.30, 90.58),
        "Pathsala, Assam": (26.4994, 91.1786),

    }

    for place_name, (lat, lon) in geo_data.items():
        cursor.execute('''
            INSERT OR IGNORE INTO locations (place_name, latitude, longitude)
            VALUES (?, ?, ?)
        ''', (place_name, lat, lon))

    conn.commit()
    conn.close()
    print("✅ Database setup complete!")
    print(f"   Admin: DitulSarma")
    print(f"   4 Subscription plans created")
    print(f"   15 Feature definitions created")
    print(f"   {len(geo_data)} Locations added")

if __name__ == "__main__":
    setup_database()
