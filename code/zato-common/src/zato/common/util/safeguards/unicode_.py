# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import Final
from unicodedata import normalize as unicodedata_normalize

# Zato
from zato.common.typing_ import any_
from zato.common.util.safeguards.common import add_signal, Kind_Unicode, SafeguardResult
from zato.common.util.safeguards.walk import walk_strings

# ################################################################################################################################
# ################################################################################################################################

# Type aliases - a translation table maps character ordinals to None, which removes them.
translate_table = dict[int, None]

# ################################################################################################################################
# ################################################################################################################################

# Zero-width characters that can hide inside identifiers and split what should match as one token -
# zero-width space, zero-width non-joiner, zero-width joiner and the byte order mark.
Zero_Width_Characters = frozenset(('\u200b', '\u200c', '\u200d', '\ufeff'))

# Bidi override and isolate controls that can visually reorder text - PDF, LRO, RLO, LRI, RLI, FSI and PDI.
Bidi_Control_Characters = frozenset(('\u202c', '\u202d', '\u202e', '\u2066', '\u2067', '\u2068', '\u2069'))

# Everything above is removed outright - none of it belongs in a payload.
Smuggle_Characters = Zero_Width_Characters | Bidi_Control_Characters

# The Unicode normalization form applied to every string value.
Normalization_Form:'Final' = 'NFC'

# ################################################################################################################################
# ################################################################################################################################

# The removal table maps every smuggled character to None, so one translate call removes them all.
_removal_table:'translate_table' = {}

for _character in Smuggle_Characters:
    _removal_table[ord(_character)] = None

# ################################################################################################################################
# ################################################################################################################################

def normalize_unicode(value:'any_', result:'SafeguardResult') -> 'any_':
    """ Removes zero-width and bidi control characters from string values and applies NFC normalization.
    Removals are counted and signalled - smuggled characters are a potential sign of an attack -
    while NFC changes stay silent because composition differences are benign.
    """

    def visit(text:'str', path:'str') -> 'str':

        # Count the characters that should not be there ..
        removed = 0

        for character in Smuggle_Characters:
            removed += text.count(character)

        # .. remove them all at once when any were found, recording the finding ..
        if removed:
            text = text.translate(_removal_table)
            result.unicode_chars_removed += removed
            add_signal(result.signals, Kind_Unicode, removed, path)

        # .. and normalize composition regardless.
        out = unicodedata_normalize(Normalization_Form, text)

        return out

    out = walk_strings(value, visit)

    return out

# ################################################################################################################################
# ################################################################################################################################
