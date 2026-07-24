# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Color math for the theme converter: parsing hex notations, flattening
# translucent colors over opaque backgrounds and mixing two colors.

# ################################################################################################################################
# ################################################################################################################################

rgbtuple  = tuple[int, int, int]
rgbatuple = tuple[int, int, int, float]

# Two hex digits per channel in the full #rrggbbaa notation
_full_hex_length = 8

# The maximum value of one 8-bit color channel
_channel_max = 255

# ################################################################################################################################

def parse_hex(value:'str', name:'str') -> 'rgbatuple':
    """ Turns #rgb, #rgba, #rrggbb or #rrggbbaa into (r, g, b, a) with the
    alpha in 0..1.
    """
    text = value.strip().lstrip('#')
    text_length = len(text)

    # A short #rgb or #rgba form doubles every digit ..
    if text_length in (3, 4):
        doubled = []
        for char in text:
            doubled.append(char + char)
        text = ''.join(doubled)

    # .. a six-digit form is fully opaque ..
    if len(text) == 6:
        text += 'ff'

    # .. and anything else than eight digits by now is not a color.
    if len(text) != _full_hex_length:
        raise SystemExit(f'{name}: cannot parse color {value!r}')

    red   = int(text[0:2], 16)
    green = int(text[2:4], 16)
    blue  = int(text[4:6], 16)
    alpha = int(text[6:8], 16) / _channel_max

    out = (red, green, blue, alpha)
    return out

# ################################################################################################################################

def to_hex(rgb:'rgbtuple') -> 'str':
    out = '#{:02x}{:02x}{:02x}'.format(*rgb)
    return out

# ################################################################################################################################

def composite(foreground:'rgbtuple', alpha:'float', background:'rgbtuple') -> 'rgbtuple':
    """ Flattens a translucent color over an opaque background, our tokens
    are always opaque so the tint math has real channels to work with.
    """
    red   = round(foreground[0] * alpha + background[0] * (1 - alpha))
    green = round(foreground[1] * alpha + background[1] * (1 - alpha))
    blue  = round(foreground[2] * alpha + background[2] * (1 - alpha))

    out = (red, green, blue)
    return out

# ################################################################################################################################

def mix(from_rgb:'rgbtuple', to_rgb:'rgbtuple', ratio:'float') -> 'rgbtuple':
    """ Linear interpolation between two colors, ratio toward the second.
    """
    red   = round(from_rgb[0] + (to_rgb[0] - from_rgb[0]) * ratio)
    green = round(from_rgb[1] + (to_rgb[1] - from_rgb[1]) * ratio)
    blue  = round(from_rgb[2] + (to_rgb[2] - from_rgb[2]) * ratio)

    out = (red, green, blue)
    return out

# ################################################################################################################################
# ################################################################################################################################
