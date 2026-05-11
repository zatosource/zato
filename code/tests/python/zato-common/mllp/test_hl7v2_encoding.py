# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.hl7v2.encoding import decode_er7, encode_er7

# ################################################################################################################################
# ################################################################################################################################

# Standard HL7 delimiters: field, component, repetition, escape, subcomponent
_Standard_Delimiters = ('|', '^', '~', '\\', '&')

# ################################################################################################################################
# ################################################################################################################################

class TestEncodeER7(TestCase):
    """ Tests for the encode_er7 function that escapes HL7 delimiter characters.
    """

    def test_encodes_escape_character(self) -> 'None':
        result = encode_er7('before\\after', _Standard_Delimiters)
        self.assertEqual(result, 'before\\E\\after')

# ################################################################################################################################

    def test_encodes_field_separator(self) -> 'None':
        result = encode_er7('value|other', _Standard_Delimiters)
        self.assertEqual(result, 'value\\F\\other')

# ################################################################################################################################

    def test_encodes_component_separator(self) -> 'None':
        result = encode_er7('value^other', _Standard_Delimiters)
        self.assertEqual(result, 'value\\S\\other')

# ################################################################################################################################

    def test_encodes_repetition_separator(self) -> 'None':
        result = encode_er7('value~other', _Standard_Delimiters)
        self.assertEqual(result, 'value\\R\\other')

# ################################################################################################################################

    def test_encodes_subcomponent_separator(self) -> 'None':
        result = encode_er7('value&other', _Standard_Delimiters)
        self.assertEqual(result, 'value\\T\\other')

# ################################################################################################################################

    def test_encodes_cr(self) -> 'None':
        result = encode_er7('line1\rline2', _Standard_Delimiters)
        self.assertEqual(result, 'line1\\X0D\\line2')

# ################################################################################################################################

    def test_encodes_lf(self) -> 'None':
        result = encode_er7('line1\nline2', _Standard_Delimiters)
        self.assertEqual(result, 'line1\\X0A\\line2')

# ################################################################################################################################

    def test_encodes_crlf(self) -> 'None':
        result = encode_er7('line1\r\nline2', _Standard_Delimiters)
        self.assertEqual(result, 'line1\\X0D\\\\X0A\\line2')

# ################################################################################################################################

    def test_no_special_characters_passes_through(self) -> 'None':
        result = encode_er7('plain text 123', _Standard_Delimiters)
        self.assertEqual(result, 'plain text 123')

# ################################################################################################################################

    def test_empty_string_passes_through(self) -> 'None':
        result = encode_er7('', _Standard_Delimiters)
        self.assertEqual(result, '')

# ################################################################################################################################

    def test_multiple_delimiters_all_encoded(self) -> 'None':
        result = encode_er7('a|b^c~d&e', _Standard_Delimiters)
        self.assertEqual(result, 'a\\F\\b\\S\\c\\R\\d\\T\\e')

# ################################################################################################################################

    def test_escape_character_encoded_first_prevents_double_escaping(self) -> 'None':
        # A value containing a literal backslash followed by a pipe
        result = encode_er7('\\|', _Standard_Delimiters)
        # The backslash becomes \E\ first, then the pipe becomes \F\
        self.assertEqual(result, '\\E\\\\F\\')

# ################################################################################################################################
# ################################################################################################################################

class TestDecodeER7(TestCase):
    """ Tests for the decode_er7 function that reverses HL7 escape sequences.
    """

    def test_decodes_escape_character(self) -> 'None':
        result = decode_er7('before\\E\\after', _Standard_Delimiters)
        self.assertEqual(result, 'before\\after')

# ################################################################################################################################

    def test_decodes_field_separator(self) -> 'None':
        result = decode_er7('value\\F\\other', _Standard_Delimiters)
        self.assertEqual(result, 'value|other')

# ################################################################################################################################

    def test_decodes_component_separator(self) -> 'None':
        result = decode_er7('value\\S\\other', _Standard_Delimiters)
        self.assertEqual(result, 'value^other')

# ################################################################################################################################

    def test_decodes_repetition_separator(self) -> 'None':
        result = decode_er7('value\\R\\other', _Standard_Delimiters)
        self.assertEqual(result, 'value~other')

# ################################################################################################################################

    def test_decodes_subcomponent_separator(self) -> 'None':
        result = decode_er7('value\\T\\other', _Standard_Delimiters)
        self.assertEqual(result, 'value&other')

# ################################################################################################################################

    def test_decodes_hex_cr(self) -> 'None':
        result = decode_er7('line1\\X0D\\line2', _Standard_Delimiters)
        self.assertEqual(result, 'line1\rline2')

# ################################################################################################################################

    def test_decodes_hex_lf(self) -> 'None':
        result = decode_er7('line1\\X0A\\line2', _Standard_Delimiters)
        self.assertEqual(result, 'line1\nline2')

# ################################################################################################################################

    def test_decodes_hex_crlf_multi_byte(self) -> 'None':
        result = decode_er7('line1\\X0D0A\\line2', _Standard_Delimiters)
        self.assertEqual(result, 'line1\r\nline2')

# ################################################################################################################################

    def test_decodes_hex_space(self) -> 'None':
        result = decode_er7('no\\X20\\break', _Standard_Delimiters)
        self.assertEqual(result, 'no break')

# ################################################################################################################################

    def test_decodes_hex_esc_byte(self) -> 'None':
        result = decode_er7('start\\X1B\\end', _Standard_Delimiters)
        self.assertEqual(result, 'start\x1bend')

# ################################################################################################################################

    def test_decodes_hex_lowercase(self) -> 'None':
        result = decode_er7('line1\\X0d\\line2', _Standard_Delimiters)
        self.assertEqual(result, 'line1\rline2')

# ################################################################################################################################

    def test_strips_highlighting_start(self) -> 'None':
        result = decode_er7('before\\H\\bold\\H\\after', _Standard_Delimiters)
        self.assertEqual(result, 'beforeboldafter')

# ################################################################################################################################

    def test_strips_highlighting_end(self) -> 'None':
        result = decode_er7('before\\.H\\normal', _Standard_Delimiters)
        self.assertEqual(result, 'beforenormal')

# ################################################################################################################################

    def test_strips_highlighting_pair(self) -> 'None':
        result = decode_er7('text\\H\\important\\.H\\rest', _Standard_Delimiters)
        self.assertEqual(result, 'textimportantrest')

# ################################################################################################################################

    def test_mixed_escape_sequences(self) -> 'None':
        encoded = 'name\\S\\value\\F\\field\\X0D\\newline\\H\\bold\\.H\\'
        result = decode_er7(encoded, _Standard_Delimiters)
        self.assertEqual(result, 'name^value|field\rnewlinebold')

# ################################################################################################################################

    def test_invalid_hex_odd_length_passes_through(self) -> 'None':
        # Odd-length hex is not valid, should be left unchanged
        result = decode_er7('data\\X0D1\\more', _Standard_Delimiters)
        self.assertEqual(result, 'data\\X0D1\\more')

# ################################################################################################################################

    def test_invalid_hex_non_hex_chars_passes_through(self) -> 'None':
        # Non-hex characters between \X and \ do not match the pattern
        result = decode_er7('data\\XZZZZ\\more', _Standard_Delimiters)
        self.assertEqual(result, 'data\\XZZZZ\\more')

# ################################################################################################################################

    def test_empty_string_passes_through(self) -> 'None':
        result = decode_er7('', _Standard_Delimiters)
        self.assertEqual(result, '')

# ################################################################################################################################

    def test_no_escape_sequences_passes_through(self) -> 'None':
        result = decode_er7('plain text 123', _Standard_Delimiters)
        self.assertEqual(result, 'plain text 123')

# ################################################################################################################################
# ################################################################################################################################

class TestRoundTrip(TestCase):
    """ Tests that encode_er7 followed by decode_er7 produces the original value.
    """

    def test_round_trip_plain_text(self) -> 'None':
        original = 'Hello world 123'
        encoded = encode_er7(original, _Standard_Delimiters)
        decoded = decode_er7(encoded, _Standard_Delimiters)
        self.assertEqual(decoded, original)

# ################################################################################################################################

    def test_round_trip_all_delimiters(self) -> 'None':
        original = 'a|b^c~d&e\\f'
        encoded = encode_er7(original, _Standard_Delimiters)
        decoded = decode_er7(encoded, _Standard_Delimiters)
        self.assertEqual(decoded, original)

# ################################################################################################################################

    def test_round_trip_cr(self) -> 'None':
        original = 'line1\rline2'
        encoded = encode_er7(original, _Standard_Delimiters)
        decoded = decode_er7(encoded, _Standard_Delimiters)
        self.assertEqual(decoded, original)

# ################################################################################################################################

    def test_round_trip_lf(self) -> 'None':
        original = 'line1\nline2'
        encoded = encode_er7(original, _Standard_Delimiters)
        decoded = decode_er7(encoded, _Standard_Delimiters)
        self.assertEqual(decoded, original)

# ################################################################################################################################

    def test_round_trip_crlf(self) -> 'None':
        original = 'line1\r\nline2'
        encoded = encode_er7(original, _Standard_Delimiters)
        decoded = decode_er7(encoded, _Standard_Delimiters)
        self.assertEqual(decoded, original)

# ################################################################################################################################

    def test_round_trip_escape_adjacent_to_delimiter(self) -> 'None':
        original = '\\|'
        encoded = encode_er7(original, _Standard_Delimiters)
        decoded = decode_er7(encoded, _Standard_Delimiters)
        self.assertEqual(decoded, original)

# ################################################################################################################################

    def test_round_trip_multiple_escapes(self) -> 'None':
        original = '\\\\||^^~~&&'
        encoded = encode_er7(original, _Standard_Delimiters)
        decoded = decode_er7(encoded, _Standard_Delimiters)
        self.assertEqual(decoded, original)

# ################################################################################################################################

    def test_round_trip_non_standard_delimiters(self) -> 'None':
        delimiters = ('#', '@', '!', '/', '$')
        original = 'a#b@c!d$e/f'
        encoded = encode_er7(original, delimiters)
        decoded = decode_er7(encoded, delimiters)
        self.assertEqual(decoded, original)

# ################################################################################################################################

    def test_round_trip_mixed_content(self) -> 'None':
        original = "Patient name: O'Brien | Room 5^B & family\r\nNotes~more"
        encoded = encode_er7(original, _Standard_Delimiters)
        decoded = decode_er7(encoded, _Standard_Delimiters)
        self.assertEqual(decoded, original)

# ################################################################################################################################
# ################################################################################################################################
