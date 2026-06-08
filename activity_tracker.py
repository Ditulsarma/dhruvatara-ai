"""
ধ্ৰুৱতৰা AI - User Activity Tracking Module
Tracks user page visits, session duration, feature usage, and RashiPhal usage.
"""
import sqlite3
from datetime import datetime, date
from config import DB_PATH


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def log_user_activity(user_id, activity_type, activity_name, activity_name_asm,
                      page_url=None, ip_address=None, session_start=None,
                      session_end=None, duration_seconds=0, details=None):
    """Log a user activity event."""
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO user_activity
            (user_id, activity_type, activity_name, activity_name_asm,
             page_url, ip_address, session_start, session_end,
             duration_seconds, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, activity_type, activity_name, activity_name_asm,
              page_url, ip_address, session_start, session_end,
              duration_seconds, details))
        conn.commit()
        return True
    except Exception as e:
        print(f"Activity log error: {e}")
        return False
    finally:
        conn.close()


def log_page_visit(user_id, page_name, page_name_asm, page_url, ip_address=None):
    """Log a page visit with current timestamp as session_start."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return log_user_activity(
        user_id=user_id,
        activity_type='page_visit',
        activity_name=page_name,
        activity_name_asm=page_name_asm,
        page_url=page_url,
        ip_address=ip_address,
        session_start=now,
        details=f"Visited {page_name_asm}"
    )


def log_feature_usage(user_id, feature_name, feature_name_asm, details=None):
    """Log a feature usage event."""
    return log_user_activity(
        user_id=user_id,
        activity_type='feature_usage',
        activity_name=feature_name,
        activity_name_asm=feature_name_asm,
        details=details
    )


def log_rashifal_usage(user_id, rashi_name, period):
    """Log a RashiPhal usage for daily tracking."""
    conn = get_db()
    try:
        today = date.today().isoformat()
        conn.execute('''
            INSERT OR IGNORE INTO user_rashifal_usage
            (user_id, rashi_name, period, usage_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, rashi_name, period, today))
        conn.commit()
        return True
    except Exception as e:
        print(f"Rashifal usage log error: {e}")
        return False
    finally:
        conn.close()


def get_user_rashifal_usage_today(user_id):
    """Get how many RashiPhals a user has viewed today."""
    conn = get_db()
    try:
        today = date.today().isoformat()
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM user_rashifal_usage WHERE user_id = ? AND usage_date = ?",
            (user_id, today)
        ).fetchone()
        return row['cnt'] if row else 0
    finally:
        conn.close()


def get_user_rashifal_used_rashis_today(user_id):
    """Get list of rashi names the user has already viewed today."""
    conn = get_db()
    try:
        today = date.today().isoformat()
        rows = conn.execute(
            "SELECT rashi_name FROM user_rashifal_usage WHERE user_id = ? AND usage_date = ?",
            (user_id, today)
        ).fetchall()
        return [r['rashi_name'] for r in rows]
    finally:
        conn.close()


# ─── Session Tracking (Free users: max 3 sessions/day) ───

def start_user_session(user_id):
    """Start a new session for a user. Returns session_id or None."""
    conn = get_db()
    try:
        today = date.today().isoformat()
        cursor = conn.execute('''
            INSERT INTO user_sessions (user_id, session_date, login_time, is_active)
            VALUES (?, ?, CURRENT_TIMESTAMP, 1)
        ''', (user_id, today))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Session start error: {e}")
        return None
    finally:
        conn.close()


def end_user_session(user_id):
    """End the most recent active session for a user."""
    conn = get_db()
    try:
        conn.execute('''
            UPDATE user_sessions SET logout_time = CURRENT_TIMESTAMP, is_active = 0
            WHERE user_id = ? AND is_active = 1
            ORDER BY login_time DESC LIMIT 1
        ''', (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Session end error: {e}")
        return False
    finally:
        conn.close()


def get_today_session_count(user_id):
    """Get number of sessions a user has started today."""
    conn = get_db()
    try:
        today = date.today().isoformat()
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM user_sessions WHERE user_id = ? AND session_date = ?",
            (user_id, today)
        ).fetchone()
        return row['cnt'] if row else 0
    finally:
        conn.close()


def can_free_user_login(user_id, subscription_id):
    """Check if a free user (subscription_id=1) can login (max 3 sessions/day)."""
    # Paid users (subscription_id > 1) have unlimited sessions
    if subscription_id and subscription_id > 1:
        return True, ""
    
    count = get_today_session_count(user_id)
    if count >= 3:
        return False, "আপুনি আজি ৩ বাৰ লগইন কৰিছে। বিনামূলীয়া ব্যৱহাৰকাৰীয়ে দৈনিক ৩ বাৰতকৈ বেছি লগইন কৰিব নোৱাৰে। অধিক সুবিধাৰ বাবে প্ৰ' ভাৰ্চনলৈ আপগ্ৰেড কৰক।"
    return True, ""


def end_all_user_sessions(user_id):
    """End all active sessions for a user (used on logout)."""
    conn = get_db()
    try:
        conn.execute('''
            UPDATE user_sessions SET logout_time = CURRENT_TIMESTAMP, is_active = 0
            WHERE user_id = ? AND is_active = 1
        ''', (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"End all sessions error: {e}")
        return False
    finally:
        conn.close()


# ─── Admin Analytics Functions ───

def get_admin_dashboard_stats():
    """Get comprehensive stats for admin dashboard."""
    conn = get_db()
    try:
        # Total users
        total_users = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
        active_users = conn.execute("SELECT COUNT(*) as c FROM users WHERE is_active = 1").fetchone()['c']
        pending_users = conn.execute("SELECT COUNT(*) as c FROM users WHERE is_active = 0").fetchone()['c']

        # Today's logins
        today = date.today().isoformat()
        today_logins = conn.execute(
            "SELECT COUNT(*) as c FROM login_logs WHERE DATE(login_time) = ? AND success = 1 AND is_admin = 0",
            (today,)
        ).fetchone()['c']

        # Today's active users (unique users who logged in today)
        today_active = conn.execute(
            "SELECT COUNT(DISTINCT user_id) as c FROM login_logs WHERE DATE(login_time) = ? AND success = 1 AND is_admin = 0",
            (today,)
        ).fetchone()['c']

        # Total page visits today
        today_visits = conn.execute(
            "SELECT COUNT(*) as c FROM user_activity WHERE DATE(created_at) = ? AND activity_type = 'page_visit'",
            (today,)
        ).fetchone()['c']

        # Total RashiPhal views today
        today_rashifal = conn.execute(
            "SELECT COUNT(*) as c FROM user_rashifal_usage WHERE usage_date = ?",
            (today,)
        ).fetchone()['c']

        # Feature usage counts
        feature_usage = conn.execute('''
            SELECT activity_name_asm, COUNT(*) as cnt
            FROM user_activity
            WHERE activity_type = 'feature_usage'
            GROUP BY activity_name
            ORDER BY cnt DESC
            LIMIT 10
        ''').fetchall()

        # Page visit counts
        page_visits = conn.execute('''
            SELECT activity_name_asm, COUNT(*) as cnt
            FROM user_activity
            WHERE activity_type = 'page_visit'
            GROUP BY activity_name
            ORDER BY cnt DESC
        ''').fetchall()

        return {
            'total_users': total_users,
            'active_users': active_users,
            'pending_users': pending_users,
            'today_logins': today_logins,
            'today_active': today_active,
            'today_visits': today_visits,
            'today_rashifal': today_rashifal,
            'feature_usage': [dict(r) for r in feature_usage],
            'page_visits': [dict(r) for r in page_visits],
        }
    finally:
        conn.close()


def get_user_activity_detail(user_id):
    """Get detailed activity for a specific user."""
    conn = get_db()
    try:
        # User info
        user = conn.execute('''
            SELECT u.*, s.name_asm as subscription_name
            FROM users u
            LEFT JOIN subscriptions s ON u.subscription_id = s.id
            WHERE u.id = ?
        ''', (user_id,)).fetchone()

        if not user:
            return None

        # Login history
        logins = conn.execute('''
            SELECT * FROM login_logs WHERE user_id = ? AND is_admin = 0
            ORDER BY login_time DESC LIMIT 50
        ''', (user_id,)).fetchall()

        # Page visits
        page_visits = conn.execute('''
            SELECT activity_name_asm, page_url, COUNT(*) as visit_count,
                   MAX(created_at) as last_visit
            FROM user_activity
            WHERE user_id = ? AND activity_type = 'page_visit'
            GROUP BY activity_name, page_url
            ORDER BY visit_count DESC
        ''', (user_id,)).fetchall()

        # Feature usage
        features_used = conn.execute('''
            SELECT activity_name_asm, COUNT(*) as usage_count,
                   MAX(created_at) as last_used
            FROM user_activity
            WHERE user_id = ? AND activity_type = 'feature_usage'
            GROUP BY activity_name
            ORDER BY usage_count DESC
        ''', (user_id,)).fetchall()

        # RashiPhal usage
        rashifal_usage = conn.execute('''
            SELECT rashi_name, period, usage_date, COUNT(*) as cnt
            FROM user_rashifal_usage
            WHERE user_id = ?
            GROUP BY rashi_name, period
            ORDER BY usage_date DESC
        ''', (user_id,)).fetchall()

        # Recent activity (last 100)
        recent_activity = conn.execute('''
            SELECT * FROM user_activity
            WHERE user_id = ?
            ORDER BY created_at DESC LIMIT 100
        ''', (user_id,)).fetchall()

        # Daily usage summary (last 30 days)
        daily_summary = conn.execute('''
            SELECT DATE(created_at) as day,
                   COUNT(CASE WHEN activity_type = 'page_visit' THEN 1 END) as page_visits,
                   COUNT(CASE WHEN activity_type = 'feature_usage' THEN 1 END) as feature_uses
            FROM user_activity
            WHERE user_id = ? AND created_at >= DATE('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY day DESC
        ''', (user_id,)).fetchall()

        return {
            'user': dict(user),
            'logins': [dict(r) for r in logins],
            'page_visits': [dict(r) for r in page_visits],
            'features_used': [dict(r) for r in features_used],
            'rashifal_usage': [dict(r) for r in rashifal_usage],
            'recent_activity': [dict(r) for r in recent_activity],
            'daily_summary': [dict(r) for r in daily_summary],
        }
    finally:
        conn.close()


def get_all_users_activity_summary():
    """Get activity summary for all users."""
    conn = get_db()
    try:
        users = conn.execute('''
            SELECT u.id, u.name, u.email, u.is_active, u.created_at as joined,
                   s.name_asm as subscription_name,
                   (SELECT COUNT(*) FROM login_logs WHERE user_id = u.id AND success = 1) as total_logins,
                   (SELECT MAX(login_time) FROM login_logs WHERE user_id = u.id AND success = 1) as last_login,
                   (SELECT COUNT(*) FROM user_activity WHERE user_id = u.id AND activity_type = 'page_visit') as total_page_visits,
                   (SELECT COUNT(*) FROM user_activity WHERE user_id = u.id AND activity_type = 'feature_usage') as total_feature_uses,
                   (SELECT COUNT(*) FROM user_rashifal_usage WHERE user_id = u.id) as total_rashifal_views,
                   (SELECT COUNT(*) FROM user_rashifal_usage WHERE user_id = u.id AND usage_date = DATE('now')) as today_rashifal_views
            FROM users u
            LEFT JOIN subscriptions s ON u.subscription_id = s.id
            ORDER BY u.created_at DESC
        ''').fetchall()

        return [dict(u) for u in users]
    finally:
        conn.close()


def get_special_topic_usage():
    """Get usage stats for special topics: RashiPhal, Jytak Bisar, Numerology, Vedic Astrology, AI Chatting."""
    conn = get_db()
    try:
        topics = {
            'rashifal': 'ৰাশিফল',
            'kundli': 'জ্যোতিষ বিচাৰ',
            'numerology': 'অংক জ্যোতিষ',
            'vedic': 'বৈদিক জ্যোতিষ',
            'ai_chat': 'AI চেটিং',
        }

        results = {}
        for key, name in topics.items():
            count = conn.execute('''
                SELECT COUNT(*) as cnt FROM user_activity
                WHERE (activity_name LIKE ? OR activity_name_asm LIKE ? OR page_url LIKE ?)
            ''', (f'%{key}%', f'%{name}%', f'%{key}%')).fetchone()['c']
            results[key] = {'name': name, 'total_uses': count}

        return results
    finally:
        conn.close()
