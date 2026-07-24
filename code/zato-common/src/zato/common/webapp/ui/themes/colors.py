# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Color arithmetic for the theme converter - parsing hex notations,
# flattening translucent colors and interpolating between two colors.

# Zato
from zato.common.webapp.ui.themes.tokens import ThemeConversionError

# ################################################################################################################################
# ################################################################################################################################

rgb_tuple  = tuple[int, int, int]
rgba_tuple = tuple[int, int, int, float]

# ################################################################################################################################

# The alpha channel of a fully opaque color
_full_alpha = 1.0

# The divisor turning a 0-255 alpha channel into 0..1
_alpha_max = 255

# ################################################################################################################################

def parse_hex(value:'str', name:'str') -> 'rgba_tuple':
    """ Turns #rgb, #rgba, #rrggbb or #rrggbbaa into (r, g, b, a) with the
    alpha in 0..1.
    """
    text = value.strip().lstrip('#')

    # A short notation doubles every digit ..
    if len(text) in (3, 4):
        doubled = []
        for char in text:
            doubled.append(char + char)
        text = ''.join(doubled)

    # .. a color without an alpha channel is fully opaque ..
    if len(text) == 6:
        text += 'ff'

    # .. and anything else is not a color we can read.
    if len(text) != 8:
        raise ThemeConversionError(f'{name}: cannot parse color {value!r}')

    red = int(text[0:2], 16)
    green = int(text[2:4], 16)
    blue = int(text[4:6], 16)
    alpha = int(text[6:8], 16) / _alpha_max

    out = (red, green, blue, alpha)
    return out

# ################################################################################################################################

def to_hex(rgb:'rgb_tuple') -> 'str':
    out = '#{:02x}{:02x}{:02x}'.format(*rgb)
    return out

# ################################################################################################################################

def composite(fg:'rgb_tuple', alpha:'float', bg:'rgb_tuple') -> 'rgb_tuple':
    """ Flattens a translucent color over an opaque background, our tokens
    are always opaque so the tint math has real channels to work with.
    """
    fg_red, fg_green, fg_blue = fg
    bg_red, bg_green, bg_blue = bg

    red = round(fg_red * alpha + bg_red * (1 - alpha))
    green = round(fg_green * alpha + bg_green * (1 - alpha))
    blue = round(fg_blue * alpha + bg_blue * (1 - alpha))

    out = (red, green, blue)
    return out

# ################################################################################################################################

def mix(from_rgb:'rgb_tuple', to_rgb:'rgb_tuple', ratio:'float') -> 'rgb_tuple':
    """ Linear interpolation between two colors, ratio toward the second.
    """
    from_red, from_green, from_blue = from_rgb
    to_red, to_green, to_blue = to_rgb

    red = round(from_red + (to_red - from_red) * ratio)
    green = round(from_green + (to_green - from_green) * ratio)
    blue = round(from_blue + (to_blue - from_blue) * ratio)

    out = (red, green, blue)
    return out

# ################################################################################################################################

def channel_distance(first:'rgb_tuple', second:'rgb_tuple') -> 'int':
    """ The sum of absolute per-channel differences between two colors.
    """
    first_red, first_green, first_blue = first
    second_red, second_green, second_blue = second

    out = abs(first_red - second_red) + abs(first_green - second_green) + abs(first_blue - second_blue)
    return out

# ################################################################################################################################

def is_opaque(alpha:'float') -> 'bool':
    out = alpha >= _full_alpha
    return out

# ################################################################################################################################
# ################################################################################################################################
