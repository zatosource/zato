# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The contract smoke for the theming scheme: every generated theme file
# carries the identical token set, no css outside css/themes/ holds a raw
# color, the generated Zato Dark reproduces the historical palette to
# the byte, and the converter fails readably on broken input - so a new
# token can never ship half-themed and a stray hardcoded color can never
# sneak back in.

# stdlib
import os
import re
import subprocess
import sys
import tempfile

# Zato
from zato.common.webapp import ui as webapp_ui
from zato.rule_engine_dashboard import app as dashboard_app

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

_css_dir = os.path.join(os.path.dirname(os.path.abspath(webapp_ui.__file__)), 'static', 'webapp', 'css')
_themes_dir = os.path.join(_css_dir, 'themes')
_assets_dir = os.path.join(os.path.dirname(os.path.abspath(webapp_ui.__file__)), 'static', 'webapp', 'assets')
_dashboard_css_dir = os.path.join(os.path.dirname(os.path.abspath(dashboard_app.__file__)), 'static', 'rule-engine', 'css')

# The historical palette Zato Dark must reproduce to the byte.
Historical_Palette = {
    '--background': '#0f172a',
    '--chrome': '#0b1222',
    '--panel': '#1e293b',
    '--panel-raised': '#182236',
    '--border': '#334155',
    '--text': '#e2e8f0',
    '--text2': '#cbd5e1',
    '--text3': '#94a3b8',
    '--text4': '#8091a8',
    '--text5': '#6d7f99',
    '--blue': '#3b82f6',
    '--blue-strong': '#2563eb',
    '--blue-strong-hover': '#1d4ed8',
    '--green': '#22c55e',
    '--red': '#ef4444',
    '--amber': '#f59e0b',
    '--indigo': '#6366f1',
    '--input-background': '#0f172a',
    '--cell-hover': '#17233c',
    '--column-hover': '#1a2742',
    '--column-selected': '#1c2c4f',
    '--filter-row-background': '#1b2030',
    '--filter-span-background': '#151a28',
    '--sentence-bar-background': '#131c31',
    '--problems-background': '#191d2e',
    '--problems-border': '#334155',
    '--button-text': '#ffffff',
    '--blue-tint-28': 'rgba(59,130,246,0.28)',
    '--green-tint-14': 'rgba(34,197,94,0.14)',
    '--indigo-tint-16': 'rgba(99,102,241,0.16)',
    '--shadow-strong': 'rgba(0,0,0,0.55)',
    '--shadow-soft': 'rgba(0,0,0,0.5)',
}

# ################################################################################################################################

def _tokens_of(path:'str') -> 'strdict':
    with open(path) as f:
        return dict(re.findall(r'^  (--[a-z0-9-]+):(.+);$', f.read(), re.M))

# ################################################################################################################################

def _run_broken(theme_text:'str', overrides_text:'str | None', expected:'str') -> 'None':
    """ Feeds the converter one broken theme and expects a readable failure naming the reason.
    """
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, 'in', 'overrides'))

        with open(os.path.join(tmp, 'in', 'broken.json'), 'w') as f:
            _ = f.write(theme_text)

        if overrides_text is not None:
            with open(os.path.join(tmp, 'in', 'overrides', 'broken.json'), 'w') as f:
                _ = f.write(overrides_text)

        result = subprocess.run(
            [sys.executable, '-m', 'zato.common.webapp.ui.themes',
             '--themes-dir', os.path.join(tmp, 'in'),
             '--out-css-dir', os.path.join(tmp, 'out'),
             '--out-index', os.path.join(tmp, 'index.js'),
             '--out-template', os.path.join(tmp, 'themes.html')],
            capture_output=True, text=True)

        message = result.stderr.strip()
        assert result.returncode != 0, 'The converter accepted broken input'
        assert expected in message, (expected, message)

# ################################################################################################################################
# ################################################################################################################################

def test_every_theme_carries_the_identical_token_set() -> 'None':
    theme_files = sorted(os.listdir(_themes_dir))
    theme_count = len(theme_files)
    assert theme_count == 6, theme_files

    token_sets = {}
    for name in theme_files:
        token_sets[name] = set(_tokens_of(os.path.join(_themes_dir, name)))

    first_name = theme_files[0]

    for name in theme_files[1:]:
        assert token_sets[name] == token_sets[first_name], (name, first_name)

# ################################################################################################################################

def test_the_problems_panel_always_has_its_own_color() -> 'None':
    for name in sorted(os.listdir(_themes_dir)):
        tokens = _tokens_of(os.path.join(_themes_dir, name))
        assert tokens['--problems-background'] != tokens['--background'], name

# ################################################################################################################################

def test_no_raw_color_outside_the_generated_themes() -> 'None':
    color_pattern = re.compile(r'rgba?\([^)]*\)|#[0-9a-fA-F]{3,8}\b')

    for css_dir in [_css_dir, _dashboard_css_dir]:
        for name in sorted(os.listdir(css_dir)):
            path = os.path.join(css_dir, name)
            if not os.path.isfile(path):
                continue
            with open(path) as f:
                raw = color_pattern.findall(f.read())
            assert raw == [], (name, raw)

# ################################################################################################################################

def test_every_theme_draws_a_logo_of_its_own_kind() -> 'None':
    """ Every theme names a logo file that is really there, a dark theme the white
    one, a light theme the blue one, and a light high contrast theme the black one.
    """
    expected_logo = {
        'ayu-dark.css': 'zato-logo-white.svg',
        'dark-high-contrast.css': 'zato-logo-white.svg',
        'gruvbox-dark-hard.css': 'zato-logo-white.svg',
        'zato-dark.css': 'zato-logo-white.svg',
        'zato-light.css': 'zato-logo-blue.svg',
        'light-high-contrast.css': 'zato-logo-black.svg',
    }

    for name in sorted(os.listdir(_themes_dir)):
        tokens = _tokens_of(os.path.join(_themes_dir, name))
        logo_file = expected_logo[name]

        assert tokens['--logo'] == f"url('/static/webapp/assets/{logo_file}')", (name, tokens['--logo'])
        assert os.path.exists(os.path.join(_assets_dir, logo_file)), logo_file

# ################################################################################################################################

def test_the_default_theme_reproduces_the_historical_palette() -> 'None':
    tokens = _tokens_of(os.path.join(_themes_dir, 'zato-dark.css'))

    for token, value in Historical_Palette.items():
        assert tokens[token] == value, (token, tokens[token], value)

# ################################################################################################################################

def test_the_converter_fails_readably_on_broken_input() -> 'None':
    good_overrides = '{"meta": {"origin": "here", "license": "MIT"}, "tokens": {}}'

    # Malformed JSONC
    _run_broken('{"name": "Broken", "type": "dark", "colors": {', good_overrides, 'not valid JSONC')

    # A theme without a type
    _run_broken('{"name": "Broken", "colors": {}}', good_overrides, 'theme type must be dark or light')

    # A theme without an overrides file
    _run_broken('{"name": "Broken", "type": "dark", "colors": {}}', None, 'every theme needs an overrides file')

    # An override pinning an unknown token
    _run_broken(
        '{"name": "Broken", "type": "dark", "colors": {}}',
        '{"meta": {"origin": "here", "license": "MIT"}, "tokens": {"--no-such-token": "#fff"}}',
        'unknown token')

    # An unparseable color value
    _run_broken(
        '{"name": "Broken", "type": "dark", "colors": {"editor.background": "not-a-color"}}',
        good_overrides, 'cannot parse color')

# ################################################################################################################################
# ################################################################################################################################
