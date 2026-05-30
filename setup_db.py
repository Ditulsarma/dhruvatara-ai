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
                    
            "Dibrugarh, Assam": { lat: 27.4722, lon: 94.9122 },
            "Guwahati, Assam": { lat: 26.1445, lon: 91.7362 },
          
            "Sivasagar, Assam": { lat: 26.9833, lon: 94.6333 },
            "Tezpur, Assam": { lat: 26.6333, lon: 92.8000 },
            "Hojai, Assam": { lat: 26.0002, lon: 92.8576 },
            "Bokakhat, Assam": { lat: 26.3800, lon: 93.3500 },
            "Nalbari, Assam": { lat: 26.26, lon: 91.26 },
            
            "Barpeta, Assam": { lat: 26.19, lon: 90.00 },
            "Guwahati, Assam": { lat: 26.11, lon: 91.44 },
            "Amingaon, Assam": { lat: 26.11, lon: 91.41 },
            "Nagaon, Assam": { lat: 26.21, lon: 92.41 },
            "Morigaon, Assam": { lat: 26.15, lon: 92.20 },
            "Golaghat, Assam": { lat: 26.31, lon: 93.58 },
            "Bokakhat, Assam": { lat: 26.38, lon: 93.35 },
            "Jorhat, Assam": { lat: 26.45, lon: 94.13 },
            "Majuli, Assam": { lat: 26.57, lon: 94.10 },
            "Sivasagar, Assam": { lat: 26.59, lon: 94.38 },
            "Dibrugarh, Assam": { lat: 27.29, lon: 94.54 },
            "Duliajan, Assam": { lat: 27.22, lon: 95.18 },
            "Moran, Assam": { lat: 27.11, lon: 94.55 },
            "Tinsukia, Assam": { lat: 27.30, lon: 95.22 },
            "Bongaigaon, Assam": { lat: 26.28, lon: 90.34 },
            "Kokrajhar, Assam": { lat: 26.24, lon: 90.16 },
            "Gossaigaon, Assam": { lat: 26.25, lon: 89.59 },
            "Dhubri, Assam": { lat: 26.01, lon: 89.59 },
            "Goalpara, Assam": { lat: 26.10, lon: 90.37 },

            "Itanagar, Arunachal Pradesh": { lat: 27.06, lon: 93.37 },
            "Shillong, Meghalaya": { lat: 25.34, lon: 91.53 },
            "Silchar, Assam": { lat: 24.49, lon: 92.48 },
            "Sarthebari, Assam": { lat: 26.23, lon: 91.10 },
            "Tamulpur, Assam": { lat: 26.38, lon: 91.34 },
            "Barpeta Road, Assam": { lat: 26.30, lon: 90.58 },

            "Bihpuria, Lakhimpur, Assam": { lat: 27.0200, lon: 93.8800 },
            "Narayanpur, Lakhimpur, Assam": { lat: 26.9800, lon: 93.8600 },
            "Laluk, Lakhimpur, Assam": { lat: 27.0900, lon: 93.9900 },
            "Nowboicha, Lakhimpur, Assam": { lat: 27.1500, lon: 93.9700 },
            "Dhakuakhana, Lakhimpur, Assam": { lat: 27.2000, lon: 94.4500 },
            "Boginadi, Lakhimpur, Assam": { lat: 27.3400, lon: 94.1300 },
            "Panigaon, Lakhimpur, Assam": { lat: 27.1800, lon: 94.1300 },
            "Azad, Lakhimpur, Assam": { lat: 27.1600, lon: 94.0300 },
            "Kadam, Lakhimpur, Assam": { lat: 27.2200, lon: 94.1800 },
            "Harmoti, Lakhimpur, Assam": { lat: 27.0600, lon: 93.8500 },
            "Bandardewa, Lakhimpur, Assam": { lat: 27.0800, lon: 93.8300 },
            "Joyhing, Lakhimpur, Assam": { lat: 27.2400, lon: 94.0200 },
            "Phulbari, Lakhimpur, Assam": { lat: 27.0500, lon: 93.9100 },
            "Ghilamara, Lakhimpur, Assam": { lat: 27.2000, lon: 94.3400 },
            "Batowmari, Lakhimpur, Assam": { lat: 27.1400, lon: 94.3900 },
            "Dhunaguri, Lakhimpur, Assam": { lat: 26.9600, lon: 93.8900 },
            "Badati, Lakhimpur, Assam": { lat: 26.9100, lon: 93.9200 },
            "Bongalmora, Lakhimpur, Assam": { lat: 27.0100, lon: 93.9500 },
            "Islampur, Lakhimpur, Assam": { lat: 27.1100, lon: 93.9200 },

            "Silapathar, Dhemaji, Assam": { lat: 27.5900, lon: 94.7300 },
            "Jonai, Dhemaji, Assam": { lat: 27.8300, lon: 95.1600 },
            "Gogamukh, Dhemaji, Assam": { lat: 27.4200, lon: 94.3400 },
            "Sissiborgaon, Dhemaji, Assam": { lat: 27.4900, lon: 94.6100 },
            "Simen Chapori, Dhemaji, Assam": { lat: 27.6700, lon: 94.8800 },
            "Machkhowa, Dhemaji, Assam": { lat: 27.2800, lon: 94.4600 },
            "Akajan, Dhemaji, Assam": { lat: 27.5300, lon: 94.6700 },
            "Kulajan, Dhemaji, Assam": { lat: 27.5100, lon: 94.6300 },
            "Dimow, Dhemaji, Assam": { lat: 27.4600, lon: 94.4100 },
            "Bordotpa, Dhemaji, Assam": { lat: 27.3200, lon: 94.4000 },
            "Butikur, Dhemaji, Assam": { lat: 27.3500, lon: 94.4300 },
            "Mingmang, Dhemaji, Assam": { lat: 27.5500, lon: 94.4500 },
            "Muktiar, Dhemaji, Assam": { lat: 27.3000, lon: 94.3500 },
            "Moridhal, Dhemaji, Assam": { lat: 27.3400, lon: 94.4000 },
            "Jiadhal, Dhemaji, Assam": { lat: 27.3500, lon: 94.3100 },
            "Pachim Dhemaji, Dhemaji, Assam": { lat: 27.2700, lon: 94.3000 },
            "Dekapam, Dhemaji, Assam": { lat: 27.7500, lon: 95.0500 },
            "Telam, Dhemaji, Assam": { lat: 27.8500, lon: 95.2100 },
            "Laimekuri, Dhemaji, Assam": { lat: 27.8800, lon: 95.3000 },

            "Garamur, Majuli, Assam": { lat: 26.9600, lon: 94.1600 },
            "Kamalabari, Majuli, Assam": { lat: 26.9400, lon: 94.0900 },
            "Auniati, Majuli, Assam": { lat: 26.9000, lon: 94.0600 },
            "Jengraimukh, Majuli, Assam": { lat: 27.0500, lon: 94.2700 },
            "Bongaon, Majuli, Assam": { lat: 26.9500, lon: 94.1500 },
            "Dakshinpat, Majuli, Assam": { lat: 26.8800, lon: 94.1800 },
            "Bhogpur, Majuli, Assam": { lat: 26.9800, lon: 94.1200 },
            "Bengenaati, Majuli, Assam": { lat: 26.9200, lon: 94.0300 },
            "Salmora, Majuli, Assam": { lat: 26.8500, lon: 94.2500 },
            "Ratanpur, Majuli, Assam": { lat: 27.0800, lon: 94.3200 },
            "Nayabazar, Majuli, Assam": { lat: 27.0200, lon: 94.2500 },
            "Karatipar, Majuli, Assam": { lat: 26.8800, lon: 94.0800 },
            "Phulani, Majuli, Assam": { lat: 27.0100, lon: 94.2100 },
            "Molual, Majuli, Assam": { lat: 26.9600, lon: 94.1800 },
            "Garmur Saru Satra, Majuli, Assam": { lat: 26.9700, lon: 94.1500 },
            "Natun Bazar, Majuli, Assam": { lat: 26.9400, lon: 94.1100 },
            "Namoni Majuli, Majuli, Assam": { lat: 26.8500, lon: 94.0100 },

            "Dergaon, Golaghat, Assam": { lat: 26.7000, lon: 93.9700 },
            "Sarupathar, Golaghat, Assam": { lat: 26.1800, lon: 93.8700 },
            "Barpathar, Golaghat, Assam": { lat: 26.2900, lon: 93.8700 },
            "Numaligarh, Golaghat, Assam": { lat: 26.6000, lon: 93.7300 },
            "Merapani, Golaghat, Assam": { lat: 26.3100, lon: 94.1100 },
            "Khumtai, Golaghat, Assam": { lat: 26.7400, lon: 93.9200 },
            "Furkating, Golaghat, Assam": { lat: 26.4500, lon: 93.9400 },
            "Kamargaon, Golaghat, Assam": { lat: 26.6500, lon: 93.6800 },
            "Kohora, Golaghat, Assam": { lat: 26.5800, lon: 93.3900 },
            "Kaziranga, Golaghat, Assam": { lat: 26.5700, lon: 93.3100 },
            "Borjuri, Golaghat, Assam": { lat: 26.6100, lon: 93.2800 },
            "Mohmaiki, Golaghat, Assam": { lat: 26.5400, lon: 93.6100 },
            "Numaligarh Ref. Township, Golaghat, Assam": { lat: 26.6200, lon: 93.7500 },
            "Badulipar, Golaghat, Assam": { lat: 26.6500, lon: 93.8100 },
            "Behora, Golaghat, Assam": { lat: 26.5200, lon: 93.5200 },
            "Rajabari, Golaghat, Assam": { lat: 26.4900, lon: 93.4700 },
            "Methoni, Golaghat, Assam": { lat: 26.5600, lon: 93.4100 },
            "Difloo, Golaghat, Assam": { lat: 26.5900, lon: 93.3300 },
            "Hatikhuli, Golaghat, Assam": { lat: 26.5800, lon: 93.4200 },
            "Kuruwabahi, Golaghat, Assam": { lat: 26.6800, lon: 93.6300 },

            "Teok, Jorhat, Assam": { lat: 26.8300, lon: 94.4100 },
            "Borholla, Jorhat, Assam": { lat: 26.4700, lon: 94.1400 },
            "Nakachari, Jorhat, Assam": { lat: 26.6600, lon: 94.3000 },
            "Cinnamara, Jorhat, Assam": { lat: 26.7100, lon: 94.2000 },
            "Nimati Ghat, Jorhat, Assam": { lat: 26.8500, lon: 94.2500 },
            "Pulibor, Jorhat, Assam": { lat: 26.7500, lon: 94.1600 },
            "Rowriah, Jorhat, Assam": { lat: 26.7300, lon: 94.1700 },
            "Barbheta, Jorhat, Assam": { lat: 26.7400, lon: 94.1900 },
            "Bhogdoi, Jorhat, Assam": { lat: 26.7600, lon: 94.2200 },
            "Kenduguri, Jorhat, Assam": { lat: 26.7700, lon: 94.2400 },
            "J.P.R, Jorhat, Assam": { lat: 26.7500, lon: 94.2100 },
            "Lichubari, Jorhat, Assam": { lat: 26.7200, lon: 94.2100 },
            "Selenghat, Jorhat, Assam": { lat: 26.8600, lon: 94.4900 },
            "Deberapar, Jorhat, Assam": { lat: 26.8200, lon: 94.4400 },
            "Kakojan, Jorhat, Assam": { lat: 26.8000, lon: 94.3400 },
            "Kaliapani, Jorhat, Assam": { lat: 26.8500, lon: 94.3600 },
            "Dhali, Jorhat, Assam": { lat: 26.8100, lon: 94.4600 },
            "Borhulla, Jorhat, Assam": { lat: 26.5100, lon: 94.1500 },
            "Madhipur, Jorhat, Assam": { lat: 26.6800, lon: 94.1800 },
            "Garmur, Jorhat, Assam": { lat: 26.7800, lon: 94.2200 },
            "Baligaon, Jorhat, Assam": { lat: 26.7900, lon: 94.1500 },
            "Amguri, Sivasagar, Assam": { lat: 26.8000, lon: 94.5300 },
            "Demow, Sivasagar, Assam": { lat: 27.1200, lon: 94.7400 },
            "Geleki, Sivasagar, Assam": { lat: 26.7800, lon: 94.6600 },
            "Sonari, Charaideo, Assam": { lat: 27.0200, lon: 95.0300 },
            "Moranhat, Charaideo, Assam": { lat: 27.1800, lon: 94.9200 },
            "Dikhowmukh, Sivasagar, Assam": { lat: 27.0100, lon: 94.4500 },
            "Gargaon, Sivasagar, Assam": { lat: 26.9300, lon: 94.7500 },
            "Namti, Sivasagar, Assam": { lat: 26.8500, lon: 94.6100 },
            "Jhanji, Sivasagar, Assam": { lat: 26.8900, lon: 94.4300 },
            "Gaurisagar, Sivasagar, Assam": { lat: 26.9300, lon: 94.5700 },
            "Nazira, Sivasagar, Assam": { lat: 26.9200, lon: 94.7300 },
            "Simaluguri, Sivasagar, Assam": { lat: 26.9000, lon: 94.7700 },
            "Santak, Sivasagar, Assam": { lat: 26.8500, lon: 94.8200 },
            "Banmukh, Sivasagar, Assam": { lat: 26.9600, lon: 94.6500 },
            "Joysagar, Sivasagar, Assam": { lat: 26.9500, lon: 94.6100 },

            
            "Namrup, Dibrugarh, Assam": { lat: 27.1800, lon: 95.3300 },
            "Tengakhat, Dibrugarh, Assam": { lat: 27.3100, lon: 95.1600 },
            "Chabua, Dibrugarh, Assam": { lat: 27.4800, lon: 95.1700 },
            "Tingkhong, Dibrugarh, Assam": { lat: 27.1400, lon: 95.0900 },
            "Khowang, Dibrugarh, Assam": { lat: 27.2600, lon: 94.8900 },
            "Naharkatia, Dibrugarh, Assam": { lat: 27.2800, lon: 95.3300 },
            "Jaipur, Dibrugarh, Assam": { lat: 27.2700, lon: 95.3800 },
            "Barbarua, Dibrugarh, Assam": { lat: 27.4200, lon: 94.9000 },
            "Lahowal, Dibrugarh, Assam": { lat: 27.4800, lon: 95.0200 },
            "Dikom, Dibrugarh, Assam": { lat: 27.5000, lon: 95.1000 },
            "Rajgarh, Dibrugarh, Assam": { lat: 27.1800, lon: 95.1200 },
            "Lepetkata, Dibrugarh, Assam": { lat: 27.3800, lon: 94.8800 },
            "Moran, Dibrugarh, Assam": { lat: 27.1800, lon: 94.9300 },
            "Rohmoria, Dibrugarh, Assam": { lat: 27.5800, lon: 95.1200 },

            
            "Margherita, Tinsukia, Assam": { lat: 27.2800, lon: 95.6700 },
            "Makum, Tinsukia, Assam": { lat: 27.5000, lon: 95.4400 },
            "Sadiya, Tinsukia, Assam": { lat: 27.8300, lon: 95.6700 },
            "Kakopathar, Tinsukia, Assam": { lat: 27.6300, lon: 95.5100 },
            "Panitola, Tinsukia, Assam": { lat: 27.5300, lon: 95.2200 },
            "Digboi Oil Town, Tinsukia, Assam": { lat: 27.3800, lon: 95.6300 },
            "Doom Dooma, Tinsukia, Assam": { lat: 27.5700, lon: 95.5700 },
            "Makum Junction, Tinsukia, Assam": { lat: 27.5100, lon: 95.4500 },
            "Margherita Coal Town, Tinsukia, Assam": { lat: 27.2900, lon: 95.6800 },
            "Ledo, Tinsukia, Assam": { lat: 27.2900, lon: 95.7400 },
            "Lekhapani, Tinsukia, Assam": { lat: 27.3100, lon: 95.8300 },
            "Talap, Tinsukia, Assam": { lat: 27.6300, lon: 95.6300 },
            "Saikhowaghat, Tinsukia, Assam": { lat: 27.7800, lon: 95.6100 },
            "Guijan, Tinsukia, Assam": { lat: 27.5800, lon: 95.3300 },
            "Jagun, Tinsukia, Assam": { lat: 27.2500, lon: 95.9100 },
            "New Bongaigaon, Bongaigaon, Assam": { lat: 26.2900, lon: 90.5200 },
            "Bijni, Chirang, Assam": { lat: 26.3100, lon: 90.5300 },
            "Basugaon, Chirang, Assam": { lat: 26.3100, lon: 90.4100 },
            "Boitamari, Bongaigaon, Assam": { lat: 26.2300, lon: 90.5800 },
            "Mererchar, Bongaigaon, Assam": { lat: 26.0600, lon: 90.3500 },
            "Jogighopa, Bongaigaon, Assam": { lat: 26.1300, lon: 90.3400 },
            "Manikpur, Bongaigaon, Assam": { lat: 26.2300, lon: 90.3800 },
            "Srijangram, Bongaigaon, Assam": { lat: 26.1900, lon: 90.4500 },
            "Chalantapara, Bongaigaon, Assam": { lat: 26.1500, lon: 90.5300 },
            "Lengtisinga, Bongaigaon, Assam": { lat: 26.1000, lon: 90.3700 },
            "Fakiragram, Kokrajhar, Assam": { lat: 26.3000, lon: 90.0800 },
            "Gossaigaon Hat, Kokrajhar, Assam": { lat: 26.4300, lon: 89.9600 },
            "Tipkai, Kokrajhar, Assam": { lat: 26.3200, lon: 90.0000 },
            "Kachugaon, Kokrajhar, Assam": { lat: 26.5400, lon: 90.0400 },
            "Dotma, Kokrajhar, Assam": { lat: 26.3700, lon: 90.1100 },
            "Balajan, Kokrajhar, Assam": { lat: 26.2100, lon: 90.2000 },
            "Serfanguri, Kokrajhar, Assam": { lat: 26.5100, lon: 90.1400 },
            "Patgaon, Kokrajhar, Assam": { lat: 26.5000, lon: 90.2500 },
            "Tulshibil, Kokrajhar, Assam": { lat: 26.4800, lon: 89.9800 },
            "Kajalgaon, Chirang, Assam": { lat: 26.5100, lon: 90.4900 },
            "Gauripur, Dhubri, Assam": { lat: 26.0800, lon: 89.9700 },
            "Golakganj, Dhubri, Assam": { lat: 26.1300, lon: 89.8400 },
            "Agomani, Dhubri, Assam": { lat: 26.1900, lon: 89.8400 },
            "Sapatgram, Dhubri, Assam": { lat: 26.3300, lon: 90.1300 },
            "Chapar, Dhubri, Assam": { lat: 26.2700, lon: 90.4600 },
            "South Salmara, South Salmara, Assam": { lat: 25.8100, lon: 89.9400 },
            "Hatsingimari, South Salmara, Assam": { lat: 25.6800, lon: 89.8800 },
            "Mankachar, South Salmara, Assam": { lat: 25.5300, lon: 89.8600 },
            "Sukchar, South Salmara, Assam": { lat: 25.7500, lon: 89.8800 },
            "Athani, Dhubri, Assam": { lat: 26.0300, lon: 90.0400 },

            
            "Lakhipur, Goalpara, Assam": { lat: 26.0000, lon: 90.3000 },
            "Balijana, Goalpara, Assam": { lat: 26.0600, lon: 90.3800 },
            "Matia, Goalpara, Assam": { lat: 26.1200, lon: 90.5800 },
            "Agia, Goalpara, Assam": { lat: 26.0800, lon: 90.4600 },
            "Rangjuli, Goalpara, Assam": { lat: 25.9600, lon: 90.7600 },
            "Krishnai, Goalpara, Assam": { lat: 26.0100, lon: 90.5400 },
            "Morrowa, Goalpara, Assam": { lat: 26.1500, lon: 90.6200 },
            "Tiplai, Goalpara, Assam": { lat: 26.0100, lon: 90.7100 },
            "Bikali, Goalpara, Assam": { lat: 25.9800, lon: 90.6600 },
            "Solmari, Goalpara, Assam": { lat: 26.1200, lon: 90.4100 },

            
            "Raha, Nagaon, Assam": { lat: 26.2300, lon: 92.5100 },
            "Dhing, Nagaon, Assam": { lat: 26.4600, lon: 92.4600 },
            "Samaguri, Nagaon, Assam": { lat: 26.3700, lon: 92.8300 },
            "Kaliabor, Nagaon, Assam": { lat: 26.5100, lon: 92.9800 },
            "Puranigudam, Nagaon, Assam": { lat: 26.3300, lon: 92.7700 },
            "Kampur, Nagaon, Assam": { lat: 26.1500, lon: 92.6200 },
            "Jakhalabandha, Nagaon, Assam": { lat: 26.5800, lon: 93.0000 },
            "Jagiroad, Morigaon, Assam": { lat: 26.1100, lon: 92.2100 },
            "Mayang, Morigaon, Assam": { lat: 26.2400, lon: 92.0400 },
            "Bhuragaon, Morigaon, Assam": { lat: 26.3400, lon: 92.2600 },
            "Laharighat, Morigaon, Assam": { lat: 26.3200, lon: 92.3100 },
            "Dharamtul, Morigaon, Assam": { lat: 26.1400, lon: 92.3500 },
            "Mikirbheta, Morigaon, Assam": { lat: 26.2100, lon: 92.2700 },

            "Doboka, Hojai, Assam": { lat: 26.0000, lon: 92.8500 },
            "Lanka, Hojai, Assam": { lat: 25.9200, lon: 92.9500 },
            "Lumding, Hojai, Assam": { lat: 25.7500, lon: 93.1700 },
            "Kheroni, Hojai, Assam": { lat: 25.9000, lon: 92.7500 },
            "Nilbagan, Hojai, Assam": { lat: 26.0600, lon: 92.8300 },
            "Jugijan, Hojai, Assam": { lat: 26.0400, lon: 92.9100 },
            "Binakandi, Hojai, Assam": { lat: 26.0800, lon: 92.9400 },
            "Udali, Hojai, Assam": { lat: 26.0000, lon: 93.0100 },
            "Modertoli, Hojai, Assam": { lat: 26.0400, lon: 92.8000 },
            "Kapasbari, Hojai, Assam": { lat: 26.0200, lon: 92.7100 },

            
            "Bokajan, Karbi Anglong, Assam": { lat: 26.0100, lon: 93.7800 },
            "Dokmoka, Karbi Anglong, Assam": { lat: 26.2200, lon: 93.1200 },
            "Howraghat, Karbi Anglong, Assam": { lat: 26.1500, lon: 93.0300 },
            "Bakalia, Karbi Anglong, Assam": { lat: 26.3800, lon: 93.2200 },
            "Manja, Karbi Anglong, Assam": { lat: 25.8100, lon: 93.5200 },
            "Hamren, West Karbi Anglong, Assam": { lat: 25.8500, lon: 92.5500 },
            "Baithalangso, West Karbi Anglong, Assam": { lat: 25.9200, lon: 92.5100 },
            "Donkamokam, West Karbi Anglong, Assam": { lat: 25.9800, lon: 92.6800 },
            "Khatkhati, Karbi Anglong, Assam": { lat: 25.9600, lon: 93.7500 },
            "Borpathar, Karbi Anglong, Assam": { lat: 26.1200, lon: 93.8500 },

            
            "Chaygaon, Kamrup, Assam": { lat: 26.0400, lon: 91.3800 },
            "Boko, Kamrup, Assam": { lat: 25.9700, lon: 91.2300 },
            "Palashbari, Kamrup, Assam": { lat: 26.1300, lon: 91.5000 },
            "Mirza, Kamrup, Assam": { lat: 26.1000, lon: 91.5200 },
            "Bijoynagar, Kamrup, Assam": { lat: 26.1100, lon: 91.5000 },
            "Goroimari, Kamrup, Assam": { lat: 26.1200, lon: 91.1800 },
            "Rampur, Kamrup, Assam": { lat: 26.0800, lon: 91.4500 },
            "Nagarbera, Kamrup, Assam": { lat: 26.1000, lon: 90.9500 },
            "Chamaria, Kamrup, Assam": { lat: 26.1500, lon: 91.0500 },
            "Sualkuchi, Kamrup, Assam": { lat: 26.1700, lon: 91.5800 },
            "Bamunigaon, Kamrup, Assam": { lat: 25.9500, lon: 91.1500 },
            "Rangia, Kamrup Rural, Assam": { lat: 26.4400, lon: 91.6200 },
            "Hajo, Kamrup Rural, Assam": { lat: 26.2500, lon: 91.5300 },
            "Baihata Chariali, Kamrup Rural, Assam": { lat: 26.3400, lon: 91.7200 },
            "Changsari, Kamrup Rural, Assam": { lat: 26.2300, lon: 91.6700 },
            "Kamalpur, Kamrup Rural, Assam": { lat: 26.3700, lon: 91.6700 },

            
            "Baghmari, Biswanath, Assam": { lat: 26.7500, lon: 93.1200 },
            "Monabari, Biswanath, Assam": { lat: 26.7800, lon: 93.2000 },
            "Gingia, Biswanath, Assam": { lat: 26.8200, lon: 93.2500 },
            "Balipukhuri, Biswanath, Assam": { lat: 26.7100, lon: 93.1500 },
            "Sakomato, Biswanath, Assam": { lat: 26.7400, lon: 93.1800 },
            "Pratapgarh, Biswanath, Assam": { lat: 26.7200, lon: 93.2200 },
            "Borgang, Biswanath, Assam": { lat: 26.8300, lon: 93.3500 },
            "Mijikajan, Biswanath, Assam": { lat: 26.8600, lon: 93.4000 },
            "Dufflaghur, Biswanath, Assam": { lat: 26.9100, lon: 93.5000 },
            "Bedeti, Biswanath, Assam": { lat: 26.8300, lon: 93.3800 },
            "Brahmajan, Biswanath, Assam": { lat: 26.8900, lon: 93.5800 },
            "Nyayabazar, Biswanath, Assam": { lat: 26.8500, lon: 93.4500 },
            "Gamiri, Biswanath, Assam": { lat: 26.8500, lon: 93.7200 },

            "Sarthebari, Barpeta, Assam": { lat: 26.3600, lon: 91.2100 },
            "Howly, Barpeta, Assam": { lat: 26.4300, lon: 90.9700 },
            "Sorbhog, Barpeta, Assam": { lat: 26.5000, lon: 90.8800 },
            "Barpeta Road, Barpeta, Assam": { lat: 26.5000, lon: 90.9700 },
            "Kalgachia, Barpeta, Assam": { lat: 26.2300, lon: 90.7300 },
            "Tarabari, Barpeta, Assam": { lat: 26.1500, lon: 90.9100 },
            "Mandia, Barpeta, Assam": { lat: 26.2500, lon: 90.8300 },
            "Jania, Barpeta, Assam": { lat: 26.3000, lon: 90.8000 },
            "Chenga, Barpeta, Assam": { lat: 26.2600, lon: 91.1300 },
            "Bhawanipur, Bajali, Assam": { lat: 26.4800, lon: 91.1000 },
            "Patacharkuchi, Bajali, Assam": { lat: 26.5200, lon: 91.1800 },
            "Tihu, Bajali, Assam": { lat: 26.4900, lon: 91.2700 },
            "Choukhuti, Bajali, Assam": { lat: 26.5600, lon: 91.1200 },
            "Pathsala, Bajali Assam": { lat: 26.29, lon: 91.10 },
            
            "Nalbari Town, Nalbari, Assam": { lat: 26.4500, lon: 91.4400 },
            "Ghograpar, Nalbari, Assam": { lat: 26.5000, lon: 91.5000 },
            "Mukalmua, Nalbari, Assam": { lat: 26.2500, lon: 91.2500 },
            "Barkhetri, Nalbari, Assam": { lat: 26.2100, lon: 91.2200 },
            "Chamata, Nalbari, Assam": { lat: 26.3800, lon: 91.3500 },
            "Belsor, Nalbari, Assam": { lat: 26.3700, lon: 91.4000 },
            "Balitara, Nalbari, Assam": { lat: 26.5300, lon: 91.4200 },
            "Kamarkuchi, Nalbari, Assam": { lat: 26.4800, lon: 91.4900 },

            
            "Dispur, Kamrup Metro, Assam": { lat: 26.1400, lon: 91.7900 },
            "Maligaon, Kamrup Metro, Assam": { lat: 26.1500, lon: 91.6900 },
            "Azara, Kamrup Metro, Assam": { lat: 26.1200, lon: 91.6000 },
            "Chandrapur, Kamrup Metro, Assam": { lat: 26.1800, lon: 91.9300 },
            "Sonapur, Kamrup Metro, Assam": { lat: 26.1200, lon: 91.9700 },
            "Khanapara, Kamrup Metro, Assam": { lat: 26.1100, lon: 91.8200 },
            "Narengi, Kamrup Metro, Assam": { lat: 26.1600, lon: 91.8400 },
            "Beltola, Kamrup Metro, Assam": { lat: 26.1100, lon: 91.7900 },
            "Panbazar, Kamrup Metro, Assam": { lat: 26.1800, lon: 91.7400 },
            "North Guwahati, Kamrup Metro, Assam": { lat: 26.2100, lon: 91.7200 },
            "Khetri, Kamrup Metro, Assam": { lat: 26.1100, lon: 92.1100 },
            "Jalukbari, Kamrup Metro, Assam": { lat: 26.1400, lon: 91.6600 },
            "Borjhar Airport, Kamrup Metro, Assam": { lat: 26.1100, lon: 91.5900 },

            
            "Daporijo, Arunachal": { lat: 27.9800, lon: 94.2200 },
            "Aalo, Arunachal": { lat: 28.1700, lon: 94.8000 },
            "Changlang, Arunachal": { lat: 27.1200, lon: 95.7300 },
            "Khonsa, Arunachal": { lat: 27.0100, lon: 95.5300 },
            "Seppa, Arunachal": { lat: 27.3600, lon: 93.3200 },
            "Yingkiong, Arunachal": { lat: 28.6100, lon: 95.0400 },
            "Miao, Arunachal": { lat: 27.4900, lon: 95.9200 },

            
            "Mawsynram, Meghalaya": { lat: 25.3000, lon: 91.5800 },
            "Dawki, Meghalaya": { lat: 25.1800, lon: 92.0100 },
            "Nongstoin, Meghalaya": { lat: 25.5200, lon: 91.2600 },
            "Khliehriat, Meghalaya": { lat: 25.3600, lon: 92.3600 },
            "Resubelpara, Meghalaya": { lat: 25.9000, lon: 90.6000 },
            "Mawkyrwat, Meghalaya": { lat: 25.3000, lon: 91.4500 },
            "Ampati, Meghalaya": { lat: 25.4600, lon: 89.9300 },

            
            "Sonai, Cachar": { lat: 24.6700, lon: 92.8600 },
            "Dholai, Cachar": { lat: 24.6000, lon: 92.8500 },
            "Udharbond, Cachar": { lat: 24.8700, lon: 92.9200 },
            "Katigorah, Cachar": { lat: 24.8800, lon: 92.5800 },
            "Badarpur, Karimganj": { lat: 24.8900, lon: 92.6000 },
            "Patharkandi, Karimganj": { lat: 24.6100, lon: 92.3100 },
            "Ramkrishna Nagar, Karimganj": { lat: 24.5800, lon: 92.4800 },
            "Lala, Hailakandi": { lat: 24.5500, lon: 92.5400 },
            "Algapur, Hailakandi": { lat: 24.7500, lon: 92.5900 },
            "Agartala, Tripura": { lat: 23.8300, lon: 91.2800 },
            "Dharmanagar, Tripura": { lat: 24.3700, lon: 92.1600 },
            "Kailashahar, Tripura": { lat: 24.3100, lon: 92.0100 },
            "Udaipur, Tripura": { lat: 23.5300, lon: 91.4800 },
            "Belonia, Tripura": { lat: 23.2500, lon: 91.4500 },
            "Ambassa, Tripura": { lat: 23.9200, lon: 91.8500 },
            "Kohima, Nagaland": { lat: 25.6700, lon: 94.1000 },
            "Dimapur, Nagaland": { lat: 25.8600, lon: 93.7300 },
            "Mokokchung, Nagaland": { lat: 26.3300, lon: 94.5300 },
            "Tuensang, Nagaland": { lat: 26.2800, lon: 94.8300 },
            "Wokha, Nagaland": { lat: 26.1000, lon: 94.2500 },
            "Zunheboto, Nagaland": { lat: 25.9600, lon: 94.4800 },
            "Imphal, Manipur": { lat: 24.8100, lon: 93.9300 },
            "Churachandpur, Manipur": { lat: 24.3300, lon: 93.6600 },
            "Thoubal, Manipur": { lat: 24.6300, lon: 93.9800 },
            "Ukhrul, Manipur": { lat: 25.1100, lon: 94.3600 },
            "Senapati, Manipur": { lat: 25.2600, lon: 94.0200 },
            "Jiribam, Manipur": { lat: 24.7900, lon: 93.1100 },

            
            "Nalbari, Assam": { lat: 26.26, lon: 91.26 },
           
            "Barpeta, Assam": { lat: 26.19, lon: 90.00 },
            "Guwahati, Assam": { lat: 26.11, lon: 91.44 },
            "Amingaon, Assam": { lat: 26.11, lon: 91.41 },
            "Nagaon, Assam": { lat: 26.21, lon: 92.41 },
            "Morigaon, Assam": { lat: 26.15, lon: 92.20 },
            "Golaghat, Assam": { lat: 26.31, lon: 93.58 },
            "Bokakhat, Assam": { lat: 26.38, lon: 93.35 },
            "Jorhat, Assam": { lat: 26.45, lon: 94.13 },
            "Majuli, Assam": { lat: 26.57, lon: 94.10 },
            "Sivasagar, Assam": { lat: 26.59, lon: 94.38 },
            "Dibrugarh, Assam": { lat: 27.29, lon: 94.54 },
            "Duliajan, Assam": { lat: 27.22, lon: 95.18 },
            "Moran, Assam": { lat: 27.11, lon: 94.55 },
            "Tinsukia, Assam": { lat: 27.30, lon: 95.22 },
            "Bongaigaon, Assam": { lat: 26.28, lon: 90.34 },
            "Kokrajhar, Assam": { lat: 26.24, lon: 90.16 },
            "Gossaigaon, Assam": { lat: 26.25, lon: 89.59 },
            "Dhubri, Assam": { lat: 26.01, lon: 89.59 },
            "Goalpara, Assam": { lat: 26.10, lon: 90.37 },
            "Silchar, Assam": { lat: 24.49, lon: 92.48 },
            "Sarthebari, Assam": { lat: 26.23, lon: 91.10 },
            "Tamulpur, Assam": { lat: 26.38, lon: 91.34 },
            "Barpeta Road, Assam": { lat: 26.30, lon: 90.58 },

            "Mushalpur, Baksa, Assam": { lat: 26.58, lon: 91.38 },
            "Salbari, Baksa, Assam": { lat: 26.63, lon: 90.96 },
            "Barama, Baksa, Assam": { lat: 26.46, lon: 91.36 },
            "Baganpara, Baksa, Assam": { lat: 26.54, lon: 91.43 },
            "Nikashi, Baksa, Assam": { lat: 26.64, lon: 91.36 },
            "Simla, Baksa, Assam": { lat: 26.60, lon: 91.22 },
            "Doomni, Baksa, Assam": { lat: 26.69, lon: 91.38 },
            "Goreswar, Tamulpur, Assam": { lat: 26.44, lon: 91.56 },
            "Darangamela, Tamulpur, Assam": { lat: 26.79, lon: 91.53 },
            "Kumarikata, Tamulpur, Assam": { lat: 26.65, lon: 91.60 },
            "Nagrijuli, Tamulpur, Assam": { lat: 26.69, lon: 91.64 },
            "Bogamati, Tamulpur, Assam": { lat: 26.80, lon: 91.73 },
            "Khandikar, Tamulpur, Assam": { lat: 26.47, lon: 91.58 },

            
            "GMCH Bhangagarh, Kamrup Metro, Assam": { lat: 26.15, lon: 91.76 },
            "MMCH Panbazar, Kamrup Metro, Assam": { lat: 26.18, lon: 91.74 },
            "BBCI Gopinath Nagar, Kamrup Metro, Assam": { lat: 26.16, lon: 91.74 },
            "Ayurvedic Hospital Jalukbari, Kamrup Metro, Assam": { lat: 26.15, lon: 91.66 },
            "ESI Hospital Beltola, Kamrup Metro, Assam": { lat: 26.12, lon: 91.79 },
            "Apollo Hospitals Christian Basti, Kamrup Metro, Assam": { lat: 26.15, lon: 91.77 },
            "GNRC Dispur, Kamrup Metro, Assam": { lat: 26.14, lon: 91.79 },
            "GNRC Six Mile, Kamrup Metro, Assam": { lat: 26.12, lon: 91.81 },
            "Pratiksha Hospital VIP Road, Kamrup Metro, Assam": { lat: 26.15, lon: 91.81 },
            "Downtown Hospital Dispur, Kamrup Metro, Assam": { lat: 26.13, lon: 91.80 },
            "Health City Khanapara, Kamrup Metro, Assam": { lat: 26.11, lon: 91.81 },
            "Narayana Amingaon, Kamrup Rural, Assam": { lat: 26.18, lon: 91.68 },
            "Excelcare Boragaon, Kamrup Metro, Assam": { lat: 26.13, lon: 91.69 },
            "Hayat Hospital Lal Ganesh, Kamrup Metro, Assam": { lat: 26.14, lon: 91.73 },
            "Marwari Hospital Athgaon, Kamrup Metro, Assam": { lat: 26.17, lon: 91.73 },
            "Nemcare Bhangagarh, Kamrup Metro, Assam": { lat: 26.16, lon: 91.76 },
            "Swagat Hospital Maligaon, Kamrup Metro, Assam": { lat: 26.16, lon: 91.69 },
            "Sanjeevani Maligaon, Kamrup Metro, Assam": { lat: 26.16, lon: 91.69 },

            "AMCH Dibrugarh, Dibrugarh, Assam": { lat: 27.46, lon: 94.92 },
            "Srishti Hospital, Dibrugarh, Assam": { lat: 27.48, lon: 94.90 },
            "Aditya Hospital, Dibrugarh, Assam": { lat: 27.46, lon: 94.91 },
            "Brahmaputra Hospital, Dibrugarh, Assam": { lat: 27.47, lon: 94.91 },
            "JMCH Jorhat, Jorhat, Assam": { lat: 26.74, lon: 94.18 },
            "Sanjivani Hospital Jorhat, Jorhat, Assam": { lat: 26.75, lon: 94.20 },
            "SMCH Silchar, Cachar, Assam": { lat: 24.78, lon: 92.79 },
            "Green Heals Hospital, Cachar, Assam": { lat: 24.81, lon: 92.80 },
            "TMCH Tezpur, Sonitpur, Assam": { lat: 26.65, lon: 92.81 },
            "Baptist Christian Hospital, Sonitpur, Assam": { lat: 26.63, lon: 92.79 },
            "FAAMCH Barpeta, Barpeta, Assam": { lat: 26.31, lon: 90.02 },
            "DMC Diphu, Karbi Anglong, Assam": { lat: 25.85, lon: 93.43 },
            "LMC North Lakhimpur, Lakhimpur, Assam": { lat: 27.24, lon: 94.01 },
            "Dhubri Medical College, Dhubri, Assam": { lat: 26.02, lon: 89.98 },
            "Nagaon Medical College, Nagaon, Assam": { lat: 26.35, lon: 92.68 },
            "Rangapara, Sonitpur, Assam": { lat: 26.81, lon: 92.65 },
            "Balipara, Sonitpur, Assam": { lat: 26.86, lon: 92.77 },
            "Jamugurihat, Sonitpur, Assam": { lat: 26.73, lon: 92.93 },
            "Sootea, Sonitpur, Assam": { lat: 26.74, lon: 93.00 },
            "Chariduar, Sonitpur, Assam": { lat: 26.90, lon: 92.79 },
            "Missamari, Sonitpur, Assam": { lat: 26.82, lon: 92.62 },
            "Thelamara, Sonitpur, Assam": { lat: 26.65, lon: 92.53 },
            "Bihaguri, Sonitpur, Assam": { lat: 26.65, lon: 92.70 },
            "Bindukuri, Sonitpur, Assam": { lat: 26.70, lon: 92.75 },
            "Barchalla, Sonitpur, Assam": { lat: 26.58, lon: 92.48 },
            "Nameri, Sonitpur, Assam": { lat: 26.93, lon: 92.86 },
            "Singri, Sonitpur, Assam": { lat: 26.60, lon: 92.48 },
            "Sirajuli, Sonitpur, Assam": { lat: 26.73, lon: 92.45 },
            "Belsiri, Sonitpur, Assam": { lat: 26.75, lon: 92.40 },
            "Rakshasmari, Sonitpur, Assam": { lat: 26.78, lon: 92.38 },
            "Hugrajuli, Sonitpur, Assam": { lat: 26.72, lon: 92.32 },
            "Borsola, Sonitpur, Assam": { lat: 26.62, lon: 92.35 },
            "Dekargaon, Sonitpur, Assam": { lat: 26.66, lon: 92.81 },
            "Parwa Chariali, Sonitpur, Assam": { lat: 26.64, lon: 92.82 },
            "Da Parbatia, Sonitpur, Assam": { lat: 26.62, lon: 92.77 },
            "Haleswar, Sonitpur, Assam": { lat: 26.67, lon: 92.79 },
            "Dolabari, Sonitpur, Assam": { lat: 26.63, lon: 92.83 },
            "Panchmile, Sonitpur, Assam": { lat: 26.67, lon: 92.84 },
            "Depota, Sonitpur, Assam": { lat: 26.64, lon: 92.74 },
            "Ketekibari, Sonitpur, Assam": { lat: 26.64, lon: 92.80 },

            
            "Deomornoi, Darrang, Assam": { lat: 26.48, lon: 91.95 },
            "Kalaigaon, Darrang, Assam": { lat: 26.54, lon: 91.98 },
            "Burhinagar, Darrang, Assam": { lat: 26.45, lon: 91.92 },
            "Aulachowka, Darrang, Assam": { lat: 26.46, lon: 92.02 },
            "Jaljali, Darrang, Assam": { lat: 26.41, lon: 92.00 },
            "Kuruwa, Darrang, Assam": { lat: 26.26, lon: 91.85 },
            "Bechimari, Darrang, Assam": { lat: 26.54, lon: 92.15 },

            "Bihpuria, Lakhimpur, Assam": { lat: 27.02, lon: 93.88 },
            "Silapathar, Dhemaji, Assam": { lat: 27.59, lon: 94.73 },
            "Kamalabari, Majuli, Assam": { lat: 26.94, lon: 94.09 },
            "Dergaon, Golaghat, Assam": { lat: 26.70, lon: 93.97 },
            "Teok, Jorhat, Assam": { lat: 26.83, lon: 94.41 },
            "Nazira, Sivasagar, Assam": { lat: 26.92, lon: 94.73 },
            "Chabua, Dibrugarh, Assam": { lat: 27.48, lon: 95.17 },
            "Doom Dooma, Tinsukia, Assam": { lat: 27.57, lon: 95.57 },
            "New Bongaigaon, Bongaigaon, Assam": { lat: 26.29, lon: 90.52 },
            "Gauripur, Dhubri, Assam": { lat: 26.08, lon: 89.97 },
            "Lakhipur, Goalpara, Assam": { lat: 26.00, lon: 90.30 },
            "Jagiroad, Morigaon, Assam": { lat: 26.11, lon: 92.21 },
            "Lanka, Hojai, Assam": { lat: 25.92, lon: 92.95 },
            "Bokajan, Karbi Anglong, Assam": { lat: 26.01, lon: 93.78 },
            "Chaygaon, Kamrup, Assam": { lat: 26.04, lon: 91.38 },
            "Borgang, Biswanath, Assam": { lat: 26.83, lon: 93.35 },
            "Howly, Barpeta, Assam": { lat: 26.43, lon: 90.97 },
            "Chamata, Nalbari, Assam": { lat: 26.38, lon: 91.35 },
            "Itanagar, Arunachal Pradesh": { lat: 27.06, lon: 93.37 },
            "Shillong, Meghalaya": { lat: 25.34, lon: 91.53 },

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
