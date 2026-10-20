# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.file_transfer.api import Encoding

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# One line of text per encoding a schedule reads files in, made of characters that only this encoding,
# or the encodings of the same region, can represent.
Encoding_Samples = {
    Encoding.UTF_8:       'Zürich, Trenčín, Αθήνα, שלום, İstanbul, € 100',
    Encoding.UTF_16_LE:   'Zürich, Trenčín, Αθήνα, שלום, İstanbul, € 100',
    Encoding.UTF_16_BE:   'Zürich, Trenčín, Αθήνα, שלום, İstanbul, € 100',
    Encoding.CP1252:      'Café Müller, Señor Peña, Œuvre, € 100',
    Encoding.ISO_8859_1:  'Café Müller, Señor Peña, Ålesund, 100 £',
    Encoding.ISO_8859_15: 'Café Müller, Œuvre, Šárka, € 100',
    Encoding.CP1250:      'Trenčín, Příliš žluťoučký kůň, Győr, € 100',
    Encoding.ISO_8859_2:  'Trenčín, Příliš žluťoučký kůň, Győr',
    Encoding.CP1257:      'Rīga, Šiauliai, Kaunas, Tõnu, € 100',
    Encoding.CP1254:      'İstanbul, Şişli, Ağrı, Çorum, € 100',
    Encoding.CP1253:      'Αθήνα, Θεσσαλονίκη, Ηράκλειο, € 100',
    Encoding.ISO_8859_7:  'Αθήνα, Θεσσαλονίκη, Ηράκλειο',
    Encoding.CP1255:      'שלום, תל אביב, ירושלים, ₪ 100',
    Encoding.ISO_8859_8:  'שלום, תל אביב, ירושלים',
    Encoding.CP850:       'Café Müller, Señor Peña, Ålesund',
    Encoding.CP852:       'Trenčín, Příliš žluťoučký kůň, Győr',
    Encoding.CP037:       'Invoice 100, Café Müller, Señor',
    Encoding.CP500:       'Invoice 100, Café Müller, Señor',
    Encoding.CP1140:      'Invoice € 100, Café Müller',
}

# What a byte order mark is as text - encoded in a Unicode encoding, it becomes that encoding's own mark.
_byte_order_mark = '\ufeff'

# ################################################################################################################################
# ################################################################################################################################

def sample_lines(encoding:'str') -> 'strlist':
    """ The lines of the sample file of an encoding, without their line breaks.
    """
    sample = Encoding_Samples[encoding]
    sample_upper = sample.upper()

    out = [sample, sample_upper, sample]
    return out

# ################################################################################################################################

def sample_text(encoding:'str', line_break:'str' = '\n') -> 'str':
    """ The text of the sample file of an encoding, each line ending with the given line break.
    """
    lines = sample_lines(encoding)

    out = ''
    for line in lines:
        out += line + line_break

    return out

# ################################################################################################################################

def sample_bytes(encoding:'str', line_break:'str' = '\n', should_add_byte_order_mark:'bool' = False) -> 'bytes':
    """ The bytes of the sample file of an encoding, opening with the encoding's byte order mark if asked to.
    """
    text = sample_text(encoding, line_break)

    if should_add_byte_order_mark:
        text = _byte_order_mark + text

    out = text.encode(encoding)
    return out

# ################################################################################################################################
# ################################################################################################################################
