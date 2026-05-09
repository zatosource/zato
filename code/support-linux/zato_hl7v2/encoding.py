from __future__ import annotations

# stdlib
import re

# ################################################################################################################################
# ################################################################################################################################

# Pattern matching generic hex escape sequences: \Xhh...\
# The hex digits between X and the trailing escape must be even-length and valid hex.
_Hex_Escape_Pattern = re.compile(r'\\X([0-9A-Fa-f]+)\\')

# ################################################################################################################################
# ################################################################################################################################

def _decode_hex_match(match:'re.Match[str]') -> 'str':
    """ Converts a regex match of \\Xhh...\\ into the corresponding characters.
    If the hex string has odd length, the match is returned unchanged (tolerance).
    """

    hex_digits = match.group(1)
    hex_length = len(hex_digits)

    # .. odd-length hex is invalid per spec, leave it unchanged ..
    is_odd = hex_length % 2 != 0

    if is_odd:
        out = match.group(0)
        return out

    # .. decode each pair of hex digits into a byte, interpret as latin-1
    # .. so that single-byte values map 1:1 to Unicode code points ..
    raw_bytes = bytes.fromhex(hex_digits)

    out = raw_bytes.decode('latin-1')
    return out

# ################################################################################################################################
# ################################################################################################################################

def encode_er7(value:'str', delimiters:'tuple[str, str, str, str, str]') -> 'str':
    """ Escapes HL7 delimiter characters, CR, and LF inside a field value.
    The escape character itself must be replaced first so that delimiters
    replaced later do not get double-escaped.
    """
    field, component, repetition, escape, subcomponent = delimiters

    # .. escape the escape character first to avoid double-escaping ..
    result = value
    result = result.replace(escape, f'{escape}E{escape}')

    # .. escape each delimiter with its HL7 mnemonic ..
    result = result.replace(field, f'{escape}F{escape}')
    result = result.replace(component, f'{escape}S{escape}')
    result = result.replace(repetition, f'{escape}R{escape}')
    result = result.replace(subcomponent, f'{escape}T{escape}')

    # .. CR is the HL7 segment terminator, so it must be hex-escaped
    # .. when it appears inside a field value ..
    result = result.replace('\r', f'{escape}X0D{escape}')

    # .. LF must also be hex-escaped because the preprocessing pipeline
    # .. converts bare LF to CR, so an unescaped LF would be corrupted
    # .. on the next parse round-trip ..
    result = result.replace('\n', f'{escape}X0A{escape}')

    return result

# ################################################################################################################################
# ################################################################################################################################

def decode_er7(value:'str', delimiters:'tuple[str, str, str, str, str]') -> 'str':
    """ Reverses HL7 escape sequences back to literal characters.
    The escape character itself must be restored last so that intermediate
    results do not interfere with other replacements.
    """
    field, component, repetition, escape, subcomponent = delimiters
    result = value

    # .. restore each delimiter mnemonic to its literal character ..
    result = result.replace(f'{escape}F{escape}', field)
    result = result.replace(f'{escape}S{escape}', component)
    result = result.replace(f'{escape}R{escape}', repetition)
    result = result.replace(f'{escape}T{escape}', subcomponent)

    # .. strip highlighting markers (they have no meaning in plain text) ..
    result = result.replace(f'{escape}H{escape}', '')
    result = result.replace(f'{escape}.H{escape}', '')

    # .. decode all hex escape sequences (\Xhh...\) into literal characters ..
    result = _Hex_Escape_Pattern.sub(_decode_hex_match, result)

    # .. restore the escape character last to avoid collisions ..
    result = result.replace(f'{escape}E{escape}', escape)

    return result

# ################################################################################################################################
# ################################################################################################################################
