# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The contract for the theming scheme: every generated theme file carries
# the identical token set, no css outside the generated themes holds a raw
# color, the generated Zato Default reproduces the historical palette to
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
from zato.common.webapp import ui as ui_package
from zato.rule_engine_dashboard import app as dashboard_app

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strnone, strstrdict
    strlist    = strlist
    strnone    = strnone
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

_ui_dir = os.path.dirname(os.path.abspath(ui_package.__file__))
_kit_css_dir = os.path.join(_ui_dir, 'static', 'webapp', 'css')
_themes_dir = os.path.join(_kit_css_dir, 'themes')

_dashboard_dir = os.path.dirname(os.path.abspath(dashboard_app.__file__))
_dashboard_css_dir = os.path.join(_dashboard_dir, 'static', 'css')

# How many themes ship with the kit
_theme_count = 4

# The historical palette Zato Default must reproduce exactly.
_historical = {
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
# ################################################################################################################################

def _theme_files() -> 'strlist':
    out = sorted(os.listdir(_themes_dir))
    return out

# ################################################################################################################################

def _tokens_of(path:'str') -> 'strstrdict':
    with open(path) as file_object:
        contents = file_object.read()

    out = {}
    for name, value in re.findall(r'^  (--[a-z0-9-]+):(.+);$', contents, re.M):
        out[name] = value

    return out

# ################################################################################################################################

def _run_broken(theme_text:'str', overrides_text:'strnone', expected:'str') -> 'None':
    """ Feeds the converter one broken theme and expects a readable
    failure naming the reason.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        os.makedirs(os.path.join(work_dir, 'in', 'overrides'))

        with open(os.path.join(work_dir, 'in', 'broken.json'), 'w') as file_object:
            _ = file_object.write(theme_text)

        if overrides_text is not None:
            with open(os.path.join(work_dir, 'in', 'overrides', 'broken.json'), 'w') as file_object:
                _ = file_object.write(overrides_text)

        result = subprocess.run(
            [sys.executable, '-m', 'zato.common.webapp.ui.themes.convert',
             '--themes-dir', os.path.join(work_dir, 'in'),
             '--out-css-dir', os.path.join(work_dir, 'out'),
             '--out-index', os.path.join(work_dir, 'index.js'),
             '--out-template', os.path.join(work_dir, 'themes.html')],
            capture_output=True, text=True)

        message = result.stderr.strip()
        assert result.returncode != 0
        assert expected in message, message

# ################################################################################################################################
# ################################################################################################################################

def test_every_theme_carries_the_identical_token_set() -> 'None':

    theme_files = _theme_files()
    theme_file_count = len(theme_files)
    assert theme_file_count == _theme_count

    first_name = theme_files[0]
    first_path = os.path.join(_themes_dir, first_name)
    first_tokens = set(_tokens_of(first_path))

    for name in theme_files[1:]:
        path = os.path.join(_themes_dir, name)
        tokens = set(_tokens_of(path))
        assert tokens == first_tokens, name

# ################################################################################################################################

def test_the_problems_panel_always_has_its_own_color() -> 'None':

    for name in _theme_files():
        path = os.path.join(_themes_dir, name)
        tokens = _tokens_of(path)
        assert tokens['--problems-background'] != tokens['--background'], name

# ################################################################################################################################

def test_no_raw_color_outside_the_generated_themes() -> 'None':

    color_pattern = re.compile(r'rgba?\([^)]*\)|#[0-9a-fA-F]{3,8}\b')

    for css_dir in (_kit_css_dir, _dashboard_css_dir):
        for name in sorted(os.listdir(css_dir)):
            path = os.path.join(css_dir, name)
            if not os.path.isfile(path):
                continue
            with open(path) as file_object:
                raw = color_pattern.findall(file_object.read())
            assert raw == [], f'{name}: {raw}'

# ################################################################################################################################

def test_zato_default_reproduces_the_historical_palette() -> 'None':

    path = os.path.join(_themes_dir, 'zato-default.css')
    tokens = _tokens_of(path)

    for token, value in _historical.items():
        assert tokens[token] == value, token

# ################################################################################################################################

def test_the_converter_fails_readably_on_broken_input() -> 'None':

    good_overrides = '{"meta": {"origin": "here", "license": "MIT"}, "tokens": {}}'

    # Malformed JSONC ..
    _run_broken('{"name": "Broken", "type": "dark", "colors": {', good_overrides, 'not valid JSONC')

    # .. a theme without a type ..
    _run_broken('{"name": "Broken", "colors": {}}', good_overrides, 'theme type must be dark or light')

    # .. a theme without an overrides file ..
    _run_broken('{"name": "Broken", "type": "dark", "colors": {}}', None, 'every theme needs an overrides file')

    # .. an override pinning an unknown token ..
    _run_broken(
        '{"name": "Broken", "type": "dark", "colors": {}}',
        '{"meta": {"origin": "here", "license": "MIT"}, "tokens": {"--no-such-token": "#fff"}}',
        'unknown token')

    # .. and an unparseable color value.
    _run_broken(
        '{"name": "Broken", "type": "dark", "colors": {"editor.background": "not-a-color"}}',
        good_overrides, 'cannot parse color')

# ################################################################################################################################
# ################################################################################################################################
