# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The settings module reads its environment variables at import time.

# stdlib
import importlib
import sys

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strstrdict

    # Add dummy assignments to satisfy type checkers
    any_ = any_
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

_module_name = 'zato.admin.settings'

_env_keys = [
    'Zato_Dashboard_Debug',
    'Zato_Dashboard_Session_Timeout',
    'Zato_Dashboard_CSRF_Trusted_Origins',
    'Zato_Django_CSRF_TRUSTED_ORIGINS',
]

# Two hours, what the module uses when the variable is not set.
_default_session_timeout = 60 * 60 * 2

_multiple_origins = 'https://one.example.com, https://two.example.com ,https://three.example.com'

# ################################################################################################################################

def _import_settings(monkeypatch:'any_', env:'strstrdict') -> 'any_':
    """ Imports the settings module afresh with only the given environment variables set.
    """

    # Clear whatever the environment already holds ..
    for key in _env_keys:
        monkeypatch.delenv(key, raising=False)

    # .. set only what this test wants ..
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    # .. drop any copy imported earlier ..
    if _module_name in sys.modules:
        del sys.modules[_module_name]

    # .. and import it afresh.
    out = importlib.import_module(_module_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSettingsEnvironment:
    """ The environment variables the Dashboard settings module reads.
    """

    def test_debug_is_off_by_default(self:'any_', monkeypatch:'any_') -> 'None':

        settings = _import_settings(monkeypatch, {})
        assert settings.DEBUG is False

# ################################################################################################################################

    def test_debug_is_read_from_the_environment(self:'any_', monkeypatch:'any_') -> 'None':

        settings = _import_settings(monkeypatch, {'Zato_Dashboard_Debug':'True'})
        assert settings.DEBUG is True

        settings = _import_settings(monkeypatch, {'Zato_Dashboard_Debug':'False'})
        assert settings.DEBUG is False

# ################################################################################################################################

    def test_session_timeout_has_its_default(self:'any_', monkeypatch:'any_') -> 'None':

        settings = _import_settings(monkeypatch, {})
        assert settings.SESSION_COOKIE_AGE == _default_session_timeout

# ################################################################################################################################

    def test_session_timeout_is_read_as_an_integer(self:'any_', monkeypatch:'any_') -> 'None':

        settings = _import_settings(monkeypatch, {'Zato_Dashboard_Session_Timeout':'3600'})

        assert settings.SESSION_COOKIE_AGE == 3600

# ################################################################################################################################

    def test_csrf_trusted_origins_accepts_multiple_values(self:'any_', monkeypatch:'any_') -> 'None':

        env = {'Zato_Dashboard_CSRF_Trusted_Origins':_multiple_origins}
        settings = _import_settings(monkeypatch, env)

        expected = ['https://one.example.com', 'https://two.example.com', 'https://three.example.com']
        assert settings.CSRF_TRUSTED_ORIGINS == expected

# ################################################################################################################################

    def test_csrf_trusted_origins_accepts_a_single_value(self:'any_', monkeypatch:'any_') -> 'None':

        env = {'Zato_Dashboard_CSRF_Trusted_Origins':'https://dashboard.example.com'}
        settings = _import_settings(monkeypatch, env)

        assert settings.CSRF_TRUSTED_ORIGINS == ['https://dashboard.example.com']

# ################################################################################################################################

    def test_the_session_cookie_flags(self:'any_', monkeypatch:'any_') -> 'None':

        settings = _import_settings(monkeypatch, {})

        assert settings.SESSION_COOKIE_HTTPONLY is True
        assert settings.SESSION_COOKIE_SAMESITE == 'Lax'

# ################################################################################################################################

    def test_the_middleware_includes_the_x_frame_options_entry(self:'any_', monkeypatch:'any_') -> 'None':

        settings = _import_settings(monkeypatch, {})

        assert 'django.middleware.clickjacking.XFrameOptionsMiddleware' in settings.MIDDLEWARE

# ################################################################################################################################
# ################################################################################################################################
