"""
ধ্ৰুৱতৰা AI - Language Utilities
Language detection, switching, and Jinja template helpers.
"""

from flask import session, request, g
from translations import get_text, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, get_all_texts


# ─── Persistent language cookie ───
# Cookie name used to remember the user's last-chosen language across
# browser sessions. max_age is set to 1 year below.
LANG_COOKIE_NAME = "dhrubatara_lang"
LANG_COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 1 year


def detect_language() -> str:
    """
    Detect the current language from:
    1. URL prefix (e.g., /bn/...)
    2. Session cookie
    3. Persistent browser cookie (set on first language switch)
    4. Accept-Language header
    5. Default (Assamese)
    """
    # 1. Check session
    lang = session.get('lang', None)
    if lang and lang in SUPPORTED_LANGUAGES:
        return lang

    # 2. Check persistent browser cookie (remembers user's choice forever)
    if request:
        cookie_lang = request.cookies.get(LANG_COOKIE_NAME)
        if cookie_lang and cookie_lang in SUPPORTED_LANGUAGES:
            # Promote the cookie value to the session for this request
            session['lang'] = cookie_lang
            return cookie_lang

    # 3. Check Accept-Language header
    if request:
        accept_lang = request.headers.get('Accept-Language', '')
        if accept_lang:
            # Parse the first language
            first_lang = accept_lang.split(',')[0].split(';')[0].strip()
            # Map common browser language codes
            lang_map = {
                'as': 'as', 'asm': 'as',
                'bn': 'bn', 'ben': 'bn',
                'hi': 'hi', 'hin': 'hi',
                'en': 'en', 'eng': 'en', 'en-us': 'en', 'en-gb': 'en',
            }
            mapped = lang_map.get(first_lang.lower(), None)
            if mapped and mapped in SUPPORTED_LANGUAGES:
                return mapped

    # 4. Default
    return DEFAULT_LANGUAGE


def set_language(lang: str) -> bool:
    """Set the language in session and a persistent browser cookie.

    The cookie outlives the Flask session, so the user's choice is
    remembered on subsequent visits (even after closing the browser or
    clearing server-side session data).
    """
    if lang not in SUPPORTED_LANGUAGES:
        return False
    session['lang'] = lang
    # Store the choice in a long-lived cookie so the next visit
    # does not fall back to the default (Assamese) again.
    # We do this by setting a flag on `g` and letting the
    # `after_request` hook (registered in `register_template_helpers`)
    # actually write the cookie to the response.
    g.set_lang_cookie = lang
    return True


def get_current_language() -> str:
    """Get the current language, detecting if needed."""
    if 'lang' not in session:
        session['lang'] = detect_language()
    return session['lang']


def init_language_for_request():
    """Initialize language for the current request context."""
    lang = get_current_language()
    g.lang = lang
    g.t = lambda key: get_text(key, lang)
    g.supported_languages = SUPPORTED_LANGUAGES
    return lang


def register_template_helpers(app):
    """Register Jinja template helpers for translations."""

    @app.context_processor
    def inject_language():
        """Inject language-related variables into all templates."""
        lang = get_current_language()
        return {
            'lang': lang,
            '_': lambda key: get_text(key, lang),
            'supported_languages': SUPPORTED_LANGUAGES,
            'current_language': SUPPORTED_LANGUAGES.get(lang, SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE]),
            'all_texts': get_all_texts(lang),
        }

    @app.after_request
    def _persist_language_cookie(response):
        """If a language switch was requested, persist it in a long-lived
        cookie so the user's choice is remembered on the next visit.
        """
        new_lang = getattr(g, 'set_lang_cookie', None)
        if new_lang and new_lang in SUPPORTED_LANGUAGES:
            response.set_cookie(
                LANG_COOKIE_NAME,
                new_lang,
                max_age=LANG_COOKIE_MAX_AGE,
                path='/',
                samesite='Lax',
            )
        return response

    # Add the _() function as a global Jinja function
    app.jinja_env.globals['_'] = lambda key: get_text(key, get_current_language())
    app.jinja_env.globals['get_text'] = get_text
    app.jinja_env.globals['supported_languages'] = SUPPORTED_LANGUAGES
