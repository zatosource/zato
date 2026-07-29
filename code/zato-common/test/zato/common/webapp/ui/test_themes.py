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
import tempfile
import unittest

# Zato
from zato.common.typing_ import strdict, strnone
from zato.common.webapp.ui.themes.convert import convert_all
from zato.common.webapp.ui.themes.tokens import ThemeConversionError

# ################################################################################################################################
# ################################################################################################################################

# The UI kit's static tree, located relative to the package under test
import zato.common.webapp.ui as _ui_package

_ui_dir = os.path.dirname(os.path.abspath(_ui_package.__file__))
_css_dir = os.path.join(_ui_dir, 'static', 'webapp', 'css')
_themes_dir = os.path.join(_css_dir, 'themes')

# The themes the kit ships with, in the order the directory lists them
_expected_theme_files = [
    'ayu-dark.css', 'dark-high-contrast.css', 'gruvbox-dark-hard.css', 'light-high-contrast.css',
    'zato-dark.css', 'zato-light.css']

# The palette the very first pages were designed with - the generated
# Zato Dark must reproduce it exactly.
_historical_palette = {
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

def _tokens_of(path:'str') -> 'strdict':
    """ Reads one generated theme file into a token -> value map.
    """
    with open(path) as theme_file:
        text = theme_file.read()

    out = dict(re.findall(r'^  (--[a-z0-9-]+):(.+);$', text, re.M))
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestGeneratedThemes(unittest.TestCase):
    """ The contract every generated theme file has to keep.
    """

    def test_expected_themes_are_generated(self) -> 'None':
        theme_files = sorted(os.listdir(_themes_dir))
        self.assertEqual(theme_files, _expected_theme_files)

# ################################################################################################################################

    def test_every_theme_has_the_same_token_set(self) -> 'None':

        first_name = _expected_theme_files[0]
        first_path = os.path.join(_themes_dir, first_name)
        first_tokens = set(_tokens_of(first_path))

        for name in _expected_theme_files[1:]:
            path = os.path.join(_themes_dir, name)
            tokens = set(_tokens_of(path))
            self.assertEqual(tokens, first_tokens, f'{name} has a different token set than {first_name}')

# ################################################################################################################################

    def test_problems_panel_has_its_own_color(self) -> 'None':

        for name in _expected_theme_files:
            path = os.path.join(_themes_dir, name)
            tokens = _tokens_of(path)
            self.assertNotEqual(
                tokens['--problems-background'], tokens['--background'],
                f'{name} paints the problems panel with the page background')

# ################################################################################################################################

    def test_no_raw_color_outside_the_themes(self) -> 'None':

        color_pattern = re.compile(r'rgba?\([^)]*\)|#[0-9a-fA-F]{3,8}\b')

        for name in sorted(os.listdir(_css_dir)):
            path = os.path.join(_css_dir, name)
            if not os.path.isfile(path):
                continue

            with open(path) as css_file:
                raw = color_pattern.findall(css_file.read())

            self.assertEqual(raw, [], f'{name} holds raw colors: {raw}')

# ################################################################################################################################

    def test_zato_dark_keeps_the_historical_palette(self) -> 'None':

        path = os.path.join(_themes_dir, 'zato-dark.css')
        tokens = _tokens_of(path)

        for token, value in _historical_palette.items():
            self.assertEqual(tokens[token], value, f'zato-dark moved {token} away from {value}')

# ################################################################################################################################
# ################################################################################################################################

class TestBrokenInput(unittest.TestCase):
    """ The converter must fail readably, naming the reason, on any broken source.
    """

    def _run_broken(self, theme_text:'str', overrides_text:'strnone', expected:'str') -> 'None':
        """ Feeds the converter one broken theme and expects a readable
        failure naming the reason.
        """
        with tempfile.TemporaryDirectory() as temporary_dir:

            themes_dir = os.path.join(temporary_dir, 'in')
            overrides_dir = os.path.join(themes_dir, 'overrides')
            os.makedirs(overrides_dir)

            with open(os.path.join(themes_dir, 'broken.json'), 'w') as theme_file:
                _ = theme_file.write(theme_text)

            if overrides_text is not None:
                with open(os.path.join(overrides_dir, 'broken.json'), 'w') as overrides_file:
                    _ = overrides_file.write(overrides_text)

            out_css_dir = os.path.join(temporary_dir, 'out')
            out_index = os.path.join(temporary_dir, 'themes-index.js')
            out_template = os.path.join(temporary_dir, 'themes.html')

            with self.assertRaises(ThemeConversionError) as caught:
                convert_all(themes_dir, out_css_dir, out_index, out_template)

            self.assertIn(expected, str(caught.exception))

# ################################################################################################################################

    def test_malformed_jsonc(self) -> 'None':
        good_overrides = '{"meta": {"origin": "here", "license": "MIT"}, "tokens": {}}'
        self._run_broken('{"name": "Broken", "type": "dark", "colors": {', good_overrides, 'not valid JSONC')

# ################################################################################################################################

    def test_theme_without_a_type(self) -> 'None':
        good_overrides = '{"meta": {"origin": "here", "license": "MIT"}, "tokens": {}}'
        self._run_broken('{"name": "Broken", "colors": {}}', good_overrides, 'theme type must be dark or light')

# ################################################################################################################################

    def test_theme_without_an_overrides_file(self) -> 'None':
        self._run_broken('{"name": "Broken", "type": "dark", "colors": {}}', None, 'every theme needs an overrides file')

# ################################################################################################################################

    def test_override_pinning_an_unknown_token(self) -> 'None':
        overrides = '{"meta": {"origin": "here", "license": "MIT"}, "tokens": {"--no-such-token": "#fff"}}'
        self._run_broken('{"name": "Broken", "type": "dark", "colors": {}}', overrides, 'unknown token')

# ################################################################################################################################

    def test_unparseable_color_value(self) -> 'None':
        good_overrides = '{"meta": {"origin": "here", "license": "MIT"}, "tokens": {}}'
        self._run_broken(
            '{"name": "Broken", "type": "dark", "colors": {"editor.background": "not-a-color"}}',
            good_overrides, 'cannot parse color')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
