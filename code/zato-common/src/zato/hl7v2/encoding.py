# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
delimiters_tuple = tuple[str, str, str, str, str]
strlist          = list[str]

# ################################################################################################################################
# ################################################################################################################################

# How many blank lines a ".sp" formatting code produces when its count is missing or not numeric.
_default_sp_line_count = 1

# Formatting codes that map directly to a line break.
_formatting_line_breaks = {
    'br': '\n',
    'sp': '\n',
}

# ################################################################################################################################
# ################################################################################################################################

def encode_er7(value:'str', delimiters:'delimiters_tuple') -> 'str':
    """ Escapes HL7 delimiter characters and CR/LF inside a field value.
    The escape character itself is replaced first so that delimiters replaced later do not get double-escaped.
    """
    field, component, repetition, escape, subcomponent = delimiters

    # Build the mnemonic escape sequences upfront ..
    escape_escape       = f'{escape}E{escape}'
    field_escape        = f'{escape}F{escape}'
    component_escape    = f'{escape}S{escape}'
    repetition_escape   = f'{escape}R{escape}'
    subcomponent_escape = f'{escape}T{escape}'
    cr_escape           = f'{escape}X0D{escape}'
    lf_escape           = f'{escape}X0A{escape}'

    # .. escape the escape character first to prevent double-escaping ..
    out = value.replace(escape, escape_escape)

    # .. escape each delimiter with its HL7 mnemonic ..
    out = out.replace(field, field_escape)
    out = out.replace(component, component_escape)
    out = out.replace(repetition, repetition_escape)
    out = out.replace(subcomponent, subcomponent_escape)

    # .. CR is the segment terminator and LF is never allowed inside a field value,
    # .. so both are hex-escaped when they appear in the data.
    out = out.replace('\r', cr_escape)
    out = out.replace('\n', lf_escape)

    return out

# ################################################################################################################################
# ################################################################################################################################

def decode_er7(value:'str', delimiters:'delimiters_tuple') -> 'str':
    """ Reverses HL7 escape sequences back to their literal characters.
    Mnemonic escapes are replaced first, then highlighting and character set markers are stripped,
    hex escapes are decoded into the bytes they name and formatting codes either produce line breaks or are stripped.
    """
    field, component, repetition, escape, subcomponent = delimiters

    # Build the mnemonic escape sequences upfront ..
    escape_escape       = f'{escape}E{escape}'
    field_escape        = f'{escape}F{escape}'
    component_escape    = f'{escape}S{escape}'
    repetition_escape   = f'{escape}R{escape}'
    subcomponent_escape = f'{escape}T{escape}'
    highlight_on        = f'{escape}H{escape}'
    highlight_off       = f'{escape}N{escape}'

    # .. and the regular expressions for the variable-body escapes.
    esc_re             = re.escape(escape)
    charset_single_re  = f'{esc_re}C[^{esc_re}]*{esc_re}'
    charset_multi_re   = f'{esc_re}M[^{esc_re}]*{esc_re}'
    hex_re             = f'{esc_re}X([0-9A-Fa-f]+){esc_re}'
    formatting_re      = f'{esc_re}\\.([^{esc_re}]*){esc_re}'

    # Replace mnemonic escape sequences with the literal delimiter characters ..
    out = value.replace(field_escape, field)
    out = out.replace(component_escape, component)
    out = out.replace(repetition_escape, repetition)
    out = out.replace(subcomponent_escape, subcomponent)
    out = out.replace(escape_escape, escape)

    # .. strip highlighting markers - they are presentation-only ..
    out = out.replace(highlight_on, '')
    out = out.replace(highlight_off, '')

    # .. strip single-byte and multi-byte character set escapes ..
    out = re.sub(charset_single_re, '', out)
    out = re.sub(charset_multi_re, '', out)

    # .. decode hex escapes into the characters their bytes represent ..
    out = re.sub(hex_re, _hex_replace, out)

    # .. and handle formatting codes last.
    out = re.sub(formatting_re, _formatting_replace, out)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _hex_replace(match:'re.Match[str]') -> 'str':
    """ Decodes a hex escape body into text, keeping invalid sequences unchanged.
    """
    body = match.group(1)
    body_length = len(body)
    has_full_pairs = body_length % 2 == 0

    # Odd-length hex does not form complete bytes - keep the original sequence ..
    if not has_full_pairs:
        out = match.group(0)
        return out

    # .. convert each pair of hex digits into one byte ..
    decoded_bytes = bytes.fromhex(body)

    # .. and interpret the bytes as UTF-8, or character by character when they are not valid UTF-8.
    try:
        out = decoded_bytes.decode('utf-8')
    except UnicodeDecodeError:
        characters:'strlist' = []
        for byte_value in decoded_bytes:
            character = chr(byte_value)
            characters.append(character)
        out = ''.join(characters)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _formatting_replace(match:'re.Match[str]') -> 'str':
    """ Decodes an HL7 formatting code into its text equivalent.
    """
    body = match.group(1)

    # Simple line-break codes map directly to their output ..
    if line_break := _formatting_line_breaks.get(body):
        out = line_break

    # .. ".sp N" produces N blank lines ..
    elif body.startswith('sp '):
        count_text = body[3:].strip()
        if count_text.isdigit():
            line_count = int(count_text)
        else:
            line_count = _default_sp_line_count
        out = '\n' * line_count

    # .. every other formatting code is presentation-only and is stripped.
    else:
        out = ''

    return out

# ################################################################################################################################
# ################################################################################################################################
