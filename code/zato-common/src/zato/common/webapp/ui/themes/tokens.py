# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The token tables the theme converter resolves: our tokens mapped from
# VS Code workbench color ids, per-type defaults, derived surface mixes,
# translucent tints and shadow constants.

# ################################################################################################################################
# ################################################################################################################################

# Our tokens mapped from VS Code workbench color ids, first present key
# in the chain wins, the per-type default catches the rest.
Mapping = {
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
Defaults = {
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
Mixes = {
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
Tints = {
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
Shadows = {
    'dark': {'--shadow-strong': 'rgba(0,0,0,0.55)', '--shadow-soft': 'rgba(0,0,0,0.5)'},
    'light': {'--shadow-strong': 'rgba(0,0,0,0.25)', '--shadow-soft': 'rgba(0,0,0,0.2)'},
}

# ################################################################################################################################

# The full token set every generated theme carries, in output order.
Token_Order = list(Mapping) + list(Mixes) + list(Tints) + ['--shadow-strong', '--shadow-soft']

# The problems panel must always read as its own surface: surfaces closer
# to the background than this channel distance count as the background,
# and such a surface is re-derived as a text-tinted wash instead.
Min_Surface_Distance = 12
Surface_Wash_Ratio   = 0.07

# ################################################################################################################################
# ################################################################################################################################
