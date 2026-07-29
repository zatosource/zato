# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The token tables the theme converter resolves every theme against. Everything
# is resolved at conversion time: mapping chains first, then per-type defaults,
# then derived values (surface mixes and alpha tints), then the overrides.
# The pages never compute a color at runtime.

# Zato
from zato.common.webapp.settings import static_url

# ################################################################################################################################
# ################################################################################################################################

class ThemeConversionError(Exception):
    """ Raised when a theme source cannot be converted into our token set.
    """

# ################################################################################################################################
# ################################################################################################################################

# Our tokens mapped from VS Code workbench color ids, first present key
# in the chain wins, the per-type default catches the rest.
mapping = {
    '--background': ['editor.background'],
    '--chrome': ['sideBar.background'],
    '--panel': ['editorWidget.background', 'menu.background'],
    '--border': ['panel.border', 'editorWidget.border'],
    '--text': ['editor.foreground'],
    '--text2': ['foreground'],
    '--text4': ['descriptionForeground'],
    '--text5': ['disabledForeground'],
    '--blue': ['textLink.foreground', 'focusBorder'],
    '--blue-strong': ['button.background'],
    '--blue-strong-hover': ['button.hoverBackground'],
    '--button-text': ['button.foreground'],
    '--green': ['charts.green', 'terminal.ansiGreen'],
    '--red': ['editorError.foreground', 'terminal.ansiRed'],
    '--amber': ['editorWarning.foreground', 'terminal.ansiYellow'],
    '--indigo': ['charts.purple', 'terminal.ansiMagenta'],
    '--input-background': ['input.background'],
    '--cell-hover': ['list.hoverBackground'],
    '--column-hover': ['list.inactiveSelectionBackground'],
    '--column-selected': ['list.activeSelectionBackground'],
    '--scrollbar-thumb': ['scrollbarSlider.background'],
    '--scrollbar-thumb-hover': ['scrollbarSlider.hoverBackground'],
}

# ################################################################################################################################

# Default values when a theme defines none of the keys in a chain,
# taken from VS Code's own default dark and light themes.
defaults = {
    'dark': {
        '--background': '#1e1e1e',
        '--chrome': '#252526',
        '--panel': '#252526',
        '--border': '#3c3c3c',
        '--text': '#d4d4d4',
        '--text2': '#cccccc',
        '--text4': '#9d9d9d',
        '--text5': '#808080',
        '--blue': '#3794ff',
        '--blue-strong': '#0e639c',
        '--blue-strong-hover': '#1177bb',
        '--button-text': '#ffffff',
        '--green': '#89d185',
        '--red': '#f14c4c',
        '--amber': '#cca700',
        '--indigo': '#b180d7',
        '--input-background': '#3c3c3c',
        '--cell-hover': '#2a2d2e',
        '--column-hover': '#37373d',
        '--column-selected': '#04395e',
        '--scrollbar-thumb': '#79797966',
        '--scrollbar-thumb-hover': '#646464b3',
    },
    'light': {
        '--background': '#ffffff',
        '--chrome': '#f3f3f3',
        '--panel': '#f3f3f3',
        '--border': '#c8c8c8',
        '--text': '#000000',
        '--text2': '#616161',
        '--text4': '#717171',
        '--text5': '#a0a0a0',
        '--blue': '#006ab1',
        '--blue-strong': '#007acc',
        '--blue-strong-hover': '#0062a3',
        '--button-text': '#ffffff',
        '--green': '#388a34',
        '--red': '#e51400',
        '--amber': '#bf8803',
        '--indigo': '#652d90',
        '--input-background': '#ffffff',
        '--cell-hover': '#e8e8e8',
        '--column-hover': '#e4e6f1',
        '--column-selected': '#d6ebff',
        '--scrollbar-thumb': '#64646466',
        '--scrollbar-thumb-hover': '#646464b3',
    },
}

# ################################################################################################################################

# Surfaces the VS Code format has no id for, derived as mixes between two
# already resolved tokens: token -> (from_token, to_token, ratio toward to).
mixes = {
    '--panel-raised': ('--background', '--panel', 0.62),
    '--text3': ('--background', '--text', 0.63),
    '--filter-row-background': ('--background', '--panel', 0.55),
    '--filter-span-background': ('--background', '--panel', 0.30),
    '--sentence-bar-background': ('--background', '--panel', 0.40),
    '--problems-background': ('--background', '--panel', 0.55),
    '--problems-border': ('--background', '--text', 0.25),
}

# ################################################################################################################################

# Translucent washes over the base palette: token -> (source token, alpha
# as a literal string so the output stays byte-stable).
tints = {
    '--blue-tint-05': ('--blue', '0.05'),
    '--blue-tint-07': ('--blue', '0.07'),
    '--blue-tint-10': ('--blue', '0.10'),
    '--blue-tint-12': ('--blue', '0.12'),
    '--blue-tint-14': ('--blue', '0.14'),
    '--blue-tint-16': ('--blue', '0.16'),
    '--blue-tint-28': ('--blue', '0.28'),
    '--blue-tint-35': ('--blue', '0.35'),
    '--blue-tint-45': ('--blue', '0.45'),
    '--green-tint-10': ('--green', '0.10'),
    '--green-tint-13': ('--green', '0.13'),
    '--green-tint-14': ('--green', '0.14'),
    '--green-tint-55': ('--green', '0.55'),
    '--red-tint-10': ('--red', '0.10'),
    '--red-tint-16': ('--red', '0.16'),
    '--amber-tint-09': ('--amber', '0.09'),
    '--indigo-tint-12': ('--indigo', '0.12'),
    '--indigo-tint-16': ('--indigo', '0.16'),
}

# ################################################################################################################################

# Box shadow colors, constant per theme type: light surfaces want much
# lighter shadows than dark ones.
shadows = {
    'dark': {'--shadow-strong': 'rgba(0,0,0,0.55)', '--shadow-soft': 'rgba(0,0,0,0.5)'},
    'light': {'--shadow-strong': 'rgba(0,0,0,0.25)', '--shadow-soft': 'rgba(0,0,0,0.2)'},
}

# ################################################################################################################################

# The color a rule name is written in wherever one is listed, over a wash that
# darkens whatever surface it sits on. A dark theme takes the bright yellow, a
# light one the same hue burnt down to where it still reads on a pale surface.
rule_names = {
    'dark': {'--rule-name': '#fffb00', '--rule-name-background': 'rgba(0,0,0,0.30)'},
    'light': {'--rule-name': '#6b5300', '--rule-name-background': 'rgba(0,0,0,0.06)'},
}

# ################################################################################################################################

# The logo file a theme is drawn with: a dark theme takes the white one,
# a light theme the blue one, and a theme whose overrides meta names a
# file takes that one - a light high contrast theme wants the black one.
logos = {
    'dark': 'zato-logo-white.svg',
    'light': 'zato-logo-blue.svg',
}

# Where the logo files are served from. The url is absolute because a relative
# one inside a custom property is resolved against a base that differs between
# browsers - the declaring file in some, the file that uses the property in
# others - and the logo is declared in a theme file yet used from tokens.css.
logo_directory = static_url + 'webapp/assets'

# How strongly the logo is drawn: softened everywhere, full strength in
# the high contrast themes, which pin it in their overrides.
logo_opacity = '0.75'

# ################################################################################################################################

# The full token set every generated theme carries, in output order.
token_order = list(mapping) + list(mixes) + list(tints) + \
    ['--shadow-strong', '--shadow-soft', '--rule-name', '--rule-name-background', '--logo', '--logo-opacity']

# The problems panel must always read as its own surface: surfaces closer
# to the background than this channel distance count as the background,
# and such a surface is re-derived as a text-tinted wash instead.
min_surface_distance = 12
surface_wash_ratio = 0.07

# ################################################################################################################################
# ################################################################################################################################
