"""
ধ্ৰুৱতৰা AI - Authentication & Authorization Module
Handles login, registration, email/mobile verification, and feature access control.
"""

import sqlite3
import random
import string
import hashlib
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import session, redirect, url_for, request, jsonify


# ─── Database helpers ───

def get_db():
    conn = sqlite3.connect('dhrubatara.db')
    conn.row_factory = sqlite3.Row
    return conn


# ─── Admin Settings ───

def get_admin_setting(key: str, default: str = "") -> str:
    """Get an admin setting value by key."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT setting_value FROM admin_settings WHERE setting_key = ?", (key,)
        ).fetchone()
        return row["setting_value"] if row else default
    finally:
        conn.close()


def set_admin_setting(key: str, value: str) -> bool:
    """Set an admin setting value. Creates if not exists."""
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO admin_settings (setting_key, setting_value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value, updated_at = CURRENT_TIMESTAMP
        ''', (key, value))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def get_user_auto_activate_mode() -> str:
    """Get the current user auto-activate mode: 'direct' or 'admin_approval'."""
    return get_admin_setting('user_auto_activate', 'admin_approval')


# ─── OTP helpers ───

def generate_otp(length=6):
    """Generate a random numeric OTP."""
    return ''.join(random.choices(string.digits, k=length))


def generate_token(length=32):
    """Generate a random hex token."""
    return ''.join(random.choices(string.hexdigits.lower(), k=length))


# ─── Email OTP (simulated - in production use SMTP) ───

def send_email_otp(email, otp):
    """
    Send OTP via email. In production, integrate with SMTP/email service.
    For now, we store it and print to console (simulation).
    """
    print(f"\n{'='*50}")
    print(f"📧 EMAIL OTP for {email}: {otp}")
    print(f"{'='*50}\n")
    return True


# ─── Mobile OTP (simulated - in production use SMS gateway) ───

def send_mobile_otp(mobile, otp):
    """
    Send OTP via SMS. In production, integrate with SMS gateway.
    For now, we store it and print to console (simulation).
    """
    print(f"\n{'='*50}")
    print(f"📱 MOBILE OTP for {mobile}: {otp}")
    print(f"{'='*50}\n")
    return True


# ─── User Registration ───

def register_user(name, email, mobile, password):
    """Register a new user. Returns (success, message)."""
    conn = get_db()
    try:
        # Check if email already exists
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            return False, "এই ইমেইলৰে ইতিমধ্যে পঞ্জীয়ন কৰা হৈছে।"

        # Check if mobile already exists
        if mobile:
            existing_mob = conn.execute("SELECT id FROM users WHERE mobile = ?", (mobile,)).fetchone()
            if existing_mob:
                return False, "এই মোবাইল নম্বৰৰে ইতিমধ্যে পঞ্জীয়ন কৰা হৈছে।"

        password_hash = generate_password_hash(password)
        email_otp = generate_otp()
        mobile_otp = generate_otp() if mobile else None
        otp_expiry = datetime.now() + timedelta(minutes=10)

        # Check admin setting: auto-activate or require admin approval
        auto_activate_mode = get_user_auto_activate_mode()
        is_active = 1 if auto_activate_mode == 'direct' else 0

        cursor = conn.execute('''
            INSERT INTO users (name, email, mobile, password_hash, email_otp, mobile_otp, otp_expiry, is_active, is_verified_email, is_verified_mobile)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
        ''', (name, email, mobile, password_hash, email_otp, mobile_otp, otp_expiry, is_active))

        user_id = cursor.lastrowid
        conn.commit()

        # Send OTPs
        send_email_otp(email, email_otp)
        if mobile:
            send_mobile_otp(mobile, mobile_otp)

        if auto_activate_mode == 'direct':
            return True, "পঞ্জীয়ন সফল! আপোনাৰ একাউণ্ট সক্ৰিয় হৈছে। আপুনি এতিয়া লগইন কৰিব পাৰে। ইমেইললৈ OTP পঠিওৱা হৈছে।"
        else:
            return True, "পঞ্জীয়ন সফল! এডমিনৰ অনুমোদনৰ পিছত আপোনাৰ একাউণ্ট সক্ৰিয় হ'ব। আপোনাৰ ইমেইললৈ OTP পঠিওৱা হৈছে। OTPৰ ম্যাদ ১০ মিনিট।"

    except Exception as e:
        return False, f"পঞ্জীয়ন বিফল: {str(e)}"
    finally:
        conn.close()


# ─── Email Verification ───

def verify_email(email, otp):
    """Verify email with OTP."""
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, email_otp, otp_expiry FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if not user:
            return False, "ব্যৱহাৰকাৰী পোৱা নগল।"

        if user["is_verified_email"]:
            return True, "ইমেইল ইতিমধ্যে ভেৰিফাইড।"

        if user["email_otp"] != otp:
            return False, "ভুল OTP।"

        if user["otp_expiry"]:
            expiry = datetime.strptime(user["otp_expiry"], "%Y-%m-%d %H:%M:%S.%f")
            if datetime.now() > expiry:
                return False, "OTPৰ ম্যাদ উকলিছে। নতুন OTPৰ বাবে অনুগ্ৰহ কৰি পুনৰ চেষ্টা কৰক।"

        conn.execute(
            "UPDATE users SET is_verified_email = 1, email_otp = NULL WHERE id = ?",
            (user["id"],)
        )
        conn.commit()
        return True, "ইমেইল সফলভাৱে ভেৰিফাইড হ'ল!"

    except Exception as e:
        return False, f"ভেৰিফিকেচন বিফল: {str(e)}"
    finally:
        conn.close()


# ─── Mobile Verification ───

def verify_mobile(mobile, otp):
    """Verify mobile with OTP."""
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, mobile_otp, otp_expiry FROM users WHERE mobile = ?",
            (mobile,)
        ).fetchone()

        if not user:
            return False, "ব্যৱহাৰকাৰী পোৱা নগল।"

        if user["is_verified_mobile"]:
            return True, "মোবাইল ইতিমধ্যে ভেৰিফাইড।"

        if user["mobile_otp"] != otp:
            return False, "ভুল OTP।"

        if user["otp_expiry"]:
            expiry = datetime.strptime(user["otp_expiry"], "%Y-%m-%d %H:%M:%S.%f")
            if datetime.now() > expiry:
                return False, "OTPৰ ম্যাদ উকলিছে। নতুন OTPৰ বাবে অনুগ্ৰহ কৰি পুনৰ চেষ্টা কৰক।"

        conn.execute(
            "UPDATE users SET is_verified_mobile = 1, mobile_otp = NULL WHERE id = ?",
            (user["id"],)
        )
        conn.commit()
        return True, "মোবাইল সফলভাৱে ভেৰিফাইড হ'ল!"

    except Exception as e:
        return False, f"ভেৰিফিকেচন বিফল: {str(e)}"
    finally:
        conn.close()


# ─── Resend OTP ───

def resend_otp(email):
    """Resend OTP to user's email and mobile."""
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, email, mobile, is_verified_email, is_verified_mobile FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if not user:
            return False, "ব্যৱহাৰকাৰী পোৱা নগল।"

        email_otp = generate_otp()
        mobile_otp = generate_otp() if user["mobile"] else None
        otp_expiry = datetime.now() + timedelta(minutes=10)

        conn.execute('''
            UPDATE users SET email_otp = ?, mobile_otp = ?, otp_expiry = ?
            WHERE id = ?
        ''', (email_otp, mobile_otp, otp_expiry, user["id"]))
        conn.commit()

        if not user["is_verified_email"]:
            send_email_otp(user["email"], email_otp)
        if user["mobile"] and not user["is_verified_mobile"]:
            send_mobile_otp(user["mobile"], mobile_otp)

        return True, "নতুন OTP পঠিওৱা হৈছে।"

    except Exception as e:
        return False, f"OTP পুনৰ পঠিওৱাত বিফল: {str(e)}"
    finally:
        conn.close()


# ─── User Login ───

def login_user(email, password, ip_address=None):
    """Authenticate a user. Returns (success, message, user_data_or_None)."""
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if not user:
            conn.execute(
                "INSERT INTO login_logs (user_id, is_admin, ip_address, success) VALUES (NULL, 0, ?, 0)",
                (ip_address,)
            )
            conn.commit()
            return False, "ইমেইল বা পাছৱৰ্ড ভুল।", None

        if not check_password_hash(user["password_hash"], password):
            conn.execute(
                "INSERT INTO login_logs (user_id, is_admin, ip_address, success) VALUES (?, 0, ?, 0)",
                (user["id"], ip_address)
            )
            conn.commit()
            return False, "ইমেইল বা পাছৱৰ্ড ভুল।", None

        if not user["is_active"]:
            conn.execute(
                "INSERT INTO login_logs (user_id, is_admin, ip_address, success) VALUES (?, 0, ?, 0)",
                (user["id"], ip_address)
            )
            conn.commit()
            return False, "আপোনাৰ একাউণ্ট এতিয়াও এডমিনৰ দ্বাৰা সক্ৰিয় কৰা হোৱা নাই। অনুগ্ৰহ কৰি অপেক্ষা কৰক।", None

        # Check subscription expiry
        if user["subscription_expiry"]:
            expiry = datetime.strptime(user["subscription_expiry"], "%Y-%m-%d")
            if datetime.now().date() > expiry.date():
                # Downgrade to free
                conn.execute(
                    "UPDATE users SET subscription_id = 1, subscription_expiry = NULL WHERE id = ?",
                    (user["id"],)
                )
                conn.commit()
                user = conn.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()

        conn.execute(
            "INSERT INTO login_logs (user_id, is_admin, ip_address, success) VALUES (?, 0, ?, 1)",
            (user["id"], ip_address)
        )
        conn.commit()

        user_data = dict(user)
        return True, "লগিন সফল!", user_data

    except Exception as e:
        return False, f"লগিন বিফল: {str(e)}", None
    finally:
        conn.close()


# ─── Admin Login ───

def login_admin(username, password, ip_address=None):
    """Authenticate an admin. Returns (success, message, admin_data_or_None)."""
    conn = get_db()
    try:
        admin = conn.execute(
            "SELECT * FROM admins WHERE username = ?",
            (username,)
        ).fetchone()

        if not admin:
            conn.execute(
                "INSERT INTO login_logs (user_id, is_admin, ip_address, success) VALUES (NULL, 1, ?, 0)",
                (ip_address,)
            )
            conn.commit()
            return False, "ইউজাৰনেম বা পাছৱৰ্ড ভুল।", None

        if not check_password_hash(admin["password_hash"], password):
            conn.execute(
                "INSERT INTO login_logs (user_id, is_admin, ip_address, success) VALUES (?, 1, ?, 0)",
                (admin["id"], ip_address)
            )
            conn.commit()
            return False, "ইউজাৰনেম বা পাছৱৰ্ড ভুল।", None

        conn.execute(
            "INSERT INTO login_logs (user_id, is_admin, ip_address, success) VALUES (?, 1, ?, 1)",
            (admin["id"], ip_address)
        )
        conn.commit()

        admin_data = dict(admin)
        return True, "এডমিন লগিন সফল!", admin_data

    except Exception as e:
        return False, f"লগিন বিফল: {str(e)}", None
    finally:
        conn.close()


# ─── Feature Access Control ───

def get_user_features(user_id):
    """
    Get all features available to a user, considering:
    1. Subscription plan features
    2. Per-user overrides (admin can enable/disable per user)
    Returns dict of {feature_key: enabled_bool}
    """
    conn = get_db()
    try:
        # Get user's subscription
        user = conn.execute(
            "SELECT subscription_id FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not user:
            return {}

        sub_id = user["subscription_id"]

        # Get subscription features
        sub_features = conn.execute('''
            SELECT sf.feature_key, sf.enabled
            FROM subscription_features sf
            WHERE sf.subscription_id = ?
        ''', (sub_id,)).fetchall()

        features = {}
        for row in sub_features:
            features[row["feature_key"]] = bool(row["enabled"])

        # Apply per-user overrides
        overrides = conn.execute('''
            SELECT feature_key, enabled FROM user_feature_overrides
            WHERE user_id = ?
        ''', (user_id,)).fetchall()

        for row in overrides:
            features[row["feature_key"]] = bool(row["enabled"])

        return features

    finally:
        conn.close()


def check_feature_access(user_id, feature_key):
    """Check if a user has access to a specific feature."""
    features = get_user_features(user_id)
    return features.get(feature_key, False)


def get_all_feature_definitions():
    """Get all feature definitions."""
    conn = get_db()
    try:
        features = conn.execute(
            "SELECT * FROM feature_definitions ORDER BY display_order"
        ).fetchall()
        return [dict(f) for f in features]
    finally:
        conn.close()


def get_all_subscriptions():
    """Get all subscription plans."""
    conn = get_db()
    try:
        subs = conn.execute(
            "SELECT * FROM subscriptions WHERE is_active = 1 ORDER BY id"
        ).fetchall()
        return [dict(s) for s in subs]
    finally:
        conn.close()


def get_subscription_features(subscription_id):
    """Get features for a specific subscription."""
    conn = get_db()
    try:
        features = conn.execute('''
            SELECT sf.feature_key, sf.enabled, fd.feature_name_asm
            FROM subscription_features sf
            JOIN feature_definitions fd ON sf.feature_key = fd.feature_key
            WHERE sf.subscription_id = ?
            ORDER BY fd.display_order
        ''', (subscription_id,)).fetchall()
        return [dict(f) for f in features]
    finally:
        conn.close()


# ─── Admin: User Management ───

def get_all_users():
    """Get all registered users (for admin panel)."""
    conn = get_db()
    try:
        users = conn.execute('''
            SELECT u.*, s.name_asm as subscription_name
            FROM users u
            LEFT JOIN subscriptions s ON u.subscription_id = s.id
            ORDER BY u.created_at DESC
        ''').fetchall()
        return [dict(u) for u in users]
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Get a single user by ID."""
    conn = get_db()
    try:
        user = conn.execute('''
            SELECT u.*, s.name_asm as subscription_name
            FROM users u
            LEFT JOIN subscriptions s ON u.subscription_id = s.id
            WHERE u.id = ?
        ''', (user_id,)).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()


def admin_toggle_user_active(user_id, is_active):
    """Admin: Activate or deactivate a user."""
    conn = get_db()
    try:
        conn.execute("UPDATE users SET is_active = ? WHERE id = ?", (is_active, user_id))
        conn.commit()
        return True, "ব্যৱহাৰকাৰীৰ স্থিতি সলনি কৰা হ'ল।"
    except Exception as e:
        return False, f"ত্ৰুটি: {str(e)}"
    finally:
        conn.close()


def admin_set_user_subscription(user_id, subscription_id, duration_days=None):
    """Admin: Set user's subscription plan."""
    conn = get_db()
    try:
        if duration_days:
            expiry = (datetime.now() + timedelta(days=duration_days)).strftime("%Y-%m-%d")
            conn.execute(
                "UPDATE users SET subscription_id = ?, subscription_expiry = ? WHERE id = ?",
                (subscription_id, expiry, user_id)
            )
        else:
            conn.execute(
                "UPDATE users SET subscription_id = ? WHERE id = ?",
                (subscription_id, user_id)
            )
        conn.commit()
        return True, "চাবস্ক্ৰিপশ্যন সলনি কৰা হ'ল।"
    except Exception as e:
        return False, f"ত্ৰুটি: {str(e)}"
    finally:
        conn.close()


def admin_toggle_user_feature(user_id, feature_key, enabled):
    """Admin: Enable or disable a specific feature for a user."""
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO user_feature_overrides (user_id, feature_key, enabled)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, feature_key) DO UPDATE SET enabled = ?
        ''', (user_id, feature_key, enabled, enabled))
        conn.commit()
        status = "সক্ষম" if enabled else "অক্ষম"
        return True, f"ফিচাৰ {status} কৰা হ'ল।"
    except Exception as e:
        return False, f"ত্ৰুটি: {str(e)}"
    finally:
        conn.close()


def admin_remove_user_feature_override(user_id, feature_key):
    """Admin: Remove per-user feature override (revert to subscription default)."""
    conn = get_db()
    try:
        conn.execute(
            "DELETE FROM user_feature_overrides WHERE user_id = ? AND feature_key = ?",
            (user_id, feature_key)
        )
        conn.commit()
        return True, "ফিচাৰ অভাৰৰাইড আঁতৰোৱা হ'ল।"
    except Exception as e:
        return False, f"ত্ৰুটি: {str(e)}"
    finally:
        conn.close()


def get_user_feature_overrides(user_id):
    """Get all feature overrides for a user."""
    conn = get_db()
    try:
        overrides = conn.execute('''
            SELECT ufo.*, fd.feature_name_asm
            FROM user_feature_overrides ufo
            JOIN feature_definitions fd ON ufo.feature_key = fd.feature_key
            WHERE ufo.user_id = ?
            ORDER BY fd.display_order
        ''', (user_id,)).fetchall()
        return [dict(o) for o in overrides]
    finally:
        conn.close()


# ─── Admin: Subscription Plan Management ───

def admin_update_subscription(subscription_id, name, name_asm, price, duration_days, description):
    """Admin: Update a subscription plan's details."""
    conn = get_db()
    try:
        conn.execute('''
            UPDATE subscriptions
            SET name = ?, name_asm = ?, price = ?, duration_days = ?, description = ?
            WHERE id = ?
        ''', (name, name_asm, price, duration_days, description, subscription_id))
        conn.commit()
        return True, "চাবস্ক্ৰিপশ্যন প্লেন আপডেট কৰা হ'ল।"
    except Exception as e:
        return False, f"ত্ৰুটি: {str(e)}"
    finally:
        conn.close()


def admin_toggle_subscription_feature(subscription_id, feature_key, enabled):
    """Admin: Enable/disable a feature for a subscription plan."""
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO subscription_features (subscription_id, feature_key, enabled)
            VALUES (?, ?, ?)
            ON CONFLICT(subscription_id, feature_key) DO UPDATE SET enabled = ?
        ''', (subscription_id, feature_key, enabled, enabled))
        conn.commit()
        status = "সক্ষম" if enabled else "অক্ষম"
        return True, f"ছাবস্ক্ৰিপশ্যন ফিচাৰ {status} কৰা হ'ল।"
    except Exception as e:
        return False, f"ত্ৰুটি: {str(e)}"
    finally:
        conn.close()


def get_subscription_by_id(subscription_id):
    """Get a single subscription by ID."""
    conn = get_db()
    try:
        sub = conn.execute("SELECT * FROM subscriptions WHERE id = ?", (subscription_id,)).fetchone()
        return dict(sub) if sub else None
    finally:
        conn.close()


# ─── Decorators ───

def login_required(f):
    """Decorator to require user login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login_page'))
        return f(*args, **kwargs)
    return decorated_function


def feature_required(feature_key):
    """Decorator to check feature access."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login_page'))
            if not check_feature_access(session['user_id'], feature_key):
                from flask import render_template as rt
                return rt('feature_locked.html', feature=feature_key), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
