# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.x12.syntax import ISA_Total_Length, RawSegment, Separators, X12SyntaxError, default_separators, parse_isa, \
     parse_segment, parse_segments, serialize_segment, split_segments

# ################################################################################################################################
# ################################################################################################################################

# A canonical version 00501 ISA - exactly 106 characters including the tilde terminator.
_isa_00501 = 'ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     ' + \
             '*260709*1200*^*00501*000000905*0*T*>~'

# The same interchange header in version 00401 - ISA11 is the standards identifier `U`
# and there is no repetition separator.
_isa_00401 = 'ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     ' + \
             '*260709*1200*U*00401*000000905*0*T*>~'

# An ISA using non-customary syntax characters - pipe elements, colon components
# and an exclamation mark terminator.
_isa_custom = 'ISA|00|          |00|          |ZZ|SENDERID       |ZZ|RECEIVERID     ' + \
              '|260709|1200|^|00501|000000905|0|T|:!'

# A complete 850 purchase order interchange with CR/LF pairs between segments.
_interchange_850 = _isa_00501 + '\r\n' + \
    'GS*PO*SENDERID*RECEIVERID*20260709*1200*905*X*005010~\r\n' + \
    'ST*850*0001~\r\n' + \
    'BEG*00*SA*PO-4529**20260709~\r\n' + \
    'PO1*1*10*EA*9.75*TE*UP*012345678905~\r\n' + \
    'CTT*1~\r\n' + \
    'SE*5*0001~\r\n' + \
    'GE*1*905~\r\n' + \
    'IEA*1*000000905~'

# ################################################################################################################################
# ################################################################################################################################

class TestParseISA(unittest.TestCase):

    maxDiff = None

    def test_parse_isa_00501(self) -> None:
        separators = parse_isa(_isa_00501)

        self.assertEqual(separators.element, '*')
        self.assertEqual(separators.component, '>')
        self.assertEqual(separators.repetition, '^')
        self.assertEqual(separators.terminator, '~')
        self.assertEqual(separators.version, '00501')

    def test_parse_isa_00401_has_no_repetition_separator(self) -> None:
        separators = parse_isa(_isa_00401)

        self.assertEqual(separators.repetition, '')
        self.assertEqual(separators.version, '00401')

    def test_parse_isa_custom_separators(self) -> None:
        separators = parse_isa(_isa_custom)

        self.assertEqual(separators.element, '|')
        self.assertEqual(separators.component, ':')
        self.assertEqual(separators.repetition, '^')
        self.assertEqual(separators.terminator, '!')
        self.assertEqual(separators.version, '00501')

    def test_parse_isa_too_short(self) -> None:
        with self.assertRaises(X12SyntaxError) as ctx:
            _ = parse_isa('ISA*00*          *00~')

        self.assertIn(f'at least {ISA_Total_Length} characters', str(ctx.exception))

    def test_parse_isa_wrong_tag(self) -> None:
        raw = 'GSA' + _isa_00501[3:]

        with self.assertRaises(X12SyntaxError) as ctx:
            _ = parse_isa(raw)

        self.assertIn('must start with `ISA`', str(ctx.exception))

    def test_parse_isa_misplaced_separator(self) -> None:

        # An overlong sender qualifier shifts every subsequent separator off its fixed position.
        raw = _isa_00501[:6] + '0' + _isa_00501[7:]

        with self.assertRaises(X12SyntaxError) as ctx:
            _ = parse_isa(raw)

        self.assertIn('expected element separator', str(ctx.exception))

    def test_parse_isa_alphanumeric_terminator(self) -> None:
        raw = _isa_00501[:-1] + 'A'

        with self.assertRaises(X12SyntaxError) as ctx:
            _ = parse_isa(raw)

        self.assertIn('terminator must not be a letter or digit', str(ctx.exception))

# ################################################################################################################################
# ################################################################################################################################

class TestSplitSegments(unittest.TestCase):

    maxDiff = None

    def test_split_bare_segments(self) -> None:
        raw = 'ST*850*0001~BEG*00*SA*PO-4529**20260709~SE*3*0001~'
        segments = split_segments(raw, default_separators)

        self.assertEqual(segments, ['ST*850*0001~', 'BEG*00*SA*PO-4529**20260709~', 'SE*3*0001~'])

    def test_split_segments_with_crlf(self) -> None:
        raw = 'ST*850*0001~\r\nBEG*00*SA*PO-4529**20260709~\r\nSE*3*0001~\r\n'
        segments = split_segments(raw, default_separators)

        self.assertEqual(segments, ['ST*850*0001~', 'BEG*00*SA*PO-4529**20260709~', 'SE*3*0001~'])

    def test_split_segments_with_bare_newlines(self) -> None:
        raw = 'ST*850*0001~\nBEG*00*SA*PO-4529**20260709~\nSE*3*0001~\n'
        segments = split_segments(raw, default_separators)

        self.assertEqual(segments, ['ST*850*0001~', 'BEG*00*SA*PO-4529**20260709~', 'SE*3*0001~'])

    def test_split_segments_missing_final_terminator(self) -> None:
        raw = 'ST*850*0001~SE*3*0001'
        segments = split_segments(raw, default_separators)

        self.assertEqual(segments, ['ST*850*0001~', 'SE*3*0001'])

# ################################################################################################################################
# ################################################################################################################################

class TestParseSegment(unittest.TestCase):

    maxDiff = None

    def test_parse_segment_with_components(self) -> None:
        segment = parse_segment('SV1*HC>99213*500*UN*1~', default_separators)

        self.assertEqual(segment.tag, 'SV1')
        self.assertEqual(segment.counters, [])
        self.assertEqual(segment.elements, [['HC', '99213'], ['500'], ['UN'], ['1']])

    def test_parse_segment_with_empty_elements(self) -> None:
        segment = parse_segment('BEG*00*SA*PO-4529**20260709~', default_separators)

        self.assertEqual(segment.tag, 'BEG')
        self.assertEqual(segment.elements, [['00'], ['SA'], ['PO-4529'], [''], ['20260709']])

    def test_parse_segment_preserves_repetition_separator(self) -> None:
        segment = parse_segment('REF*EJ*ID-1^ID-2~', default_separators)

        self.assertEqual(segment.elements, [['EJ'], ['ID-1^ID-2']])

    def test_parse_isa_segment_keeps_elements_verbatim(self) -> None:
        segment = parse_segment(_isa_00501, default_separators)

        self.assertEqual(segment.tag, 'ISA')
        self.assertEqual(len(segment.elements), 16)

        # ISA16 is the component separator itself and must not be split on it.
        self.assertEqual(segment.elements[15], ['>'])

        # Fixed-width padding is preserved as-is.
        self.assertEqual(segment.elements[5], ['SENDERID       '])
        self.assertEqual(segment.elements[12], ['000000905'])

    def test_parse_isa_segment_wrong_element_count(self) -> None:
        with self.assertRaises(X12SyntaxError) as ctx:
            _ = parse_segment('ISA*00*          *00~', default_separators)

        self.assertIn('exactly 16 elements', str(ctx.exception))

# ################################################################################################################################
# ################################################################################################################################

class TestSerializeSegment(unittest.TestCase):

    maxDiff = None

    def test_serialize_segment_roundtrip(self) -> None:
        wire_text = 'PO1*1*10*EA*9.75*TE*UP*012345678905~'
        segment = parse_segment(wire_text, default_separators)
        serialized = serialize_segment(segment, default_separators)

        self.assertEqual(serialized, wire_text)

    def test_serialize_segment_with_components_roundtrip(self) -> None:
        wire_text = 'SV1*HC>99213>25*500*UN*1~'
        segment = parse_segment(wire_text, default_separators)
        serialized = serialize_segment(segment, default_separators)

        self.assertEqual(serialized, wire_text)

    def test_serialize_isa_pads_fixed_width_elements(self) -> None:
        elements = [
            ['00'], [''], ['00'], [''],
            ['ZZ'], ['SENDERID'], ['ZZ'], ['RECEIVERID'],
            ['260709'], ['1200'], ['^'], ['00501'],
            ['905'], ['0'], ['T'], ['>'],
        ]
        segment = RawSegment('ISA', [], elements)
        serialized = serialize_segment(segment, default_separators)

        self.assertEqual(serialized, _isa_00501)

    def test_serialize_isa_roundtrip_is_byte_exact(self) -> None:
        segment = parse_segment(_isa_00501, default_separators)
        serialized = serialize_segment(segment, default_separators)

        self.assertEqual(serialized, _isa_00501)

    def test_serialize_isa_rejects_overlong_element(self) -> None:
        elements = [
            ['00'], [''], ['00'], [''],
            ['ZZ'], ['SENDER-ID-TOO-LONG'], ['ZZ'], ['RECEIVERID'],
            ['260709'], ['1200'], ['^'], ['00501'],
            ['905'], ['0'], ['T'], ['>'],
        ]
        segment = RawSegment('ISA', [], elements)

        with self.assertRaises(X12SyntaxError) as ctx:
            _ = serialize_segment(segment, default_separators)

        self.assertIn('at most 15 characters', str(ctx.exception))

    def test_serialize_rejects_element_separator_in_data(self) -> None:
        segment = RawSegment('REF', [], [['EJ'], ['ID*1']])

        with self.assertRaises(X12SyntaxError) as ctx:
            _ = serialize_segment(segment, default_separators)

        self.assertIn('Separator `*` must not appear in data', str(ctx.exception))

    def test_serialize_rejects_component_separator_in_data(self) -> None:
        segment = RawSegment('REF', [], [['EJ'], ['ID>1']])

        with self.assertRaises(X12SyntaxError) as ctx:
            _ = serialize_segment(segment, default_separators)

        self.assertIn('Separator `>` must not appear in data', str(ctx.exception))

    def test_serialize_rejects_terminator_in_data(self) -> None:
        segment = RawSegment('REF', [], [['EJ'], ['ID~1']])

        with self.assertRaises(X12SyntaxError) as ctx:
            _ = serialize_segment(segment, default_separators)

        self.assertIn('Separator `~` must not appear in data', str(ctx.exception))

    def test_serialize_allows_repetition_separator_in_data(self) -> None:
        segment = RawSegment('REF', [], [['EJ'], ['ID-1^ID-2']])
        serialized = serialize_segment(segment, default_separators)

        self.assertEqual(serialized, 'REF*EJ*ID-1^ID-2~')

    def test_serialize_with_custom_separators(self) -> None:
        separators = Separators(element='|', component=':', terminator='!')
        segment = RawSegment('SV1', [], [['HC', '99213'], ['500']])
        serialized = serialize_segment(segment, separators)

        self.assertEqual(serialized, 'SV1|HC:99213|500!')

# ################################################################################################################################
# ################################################################################################################################

class TestParseSegments(unittest.TestCase):

    maxDiff = None

    def test_parse_full_interchange(self) -> None:
        separators = parse_isa(_interchange_850)
        segments = parse_segments(_interchange_850, separators)

        tags:'list[str]' = []
        for segment in segments:
            tags.append(segment.tag)

        self.assertEqual(tags, ['ISA', 'GS', 'ST', 'BEG', 'PO1', 'CTT', 'SE', 'GE', 'IEA'])
        self.assertEqual(len(segments[0].elements), 16)

    def test_full_interchange_roundtrip(self) -> None:
        separators = parse_isa(_interchange_850)
        segments = parse_segments(_interchange_850, separators)

        serialized_texts:'list[str]' = []
        for segment in segments:
            serialized = serialize_segment(segment, separators)
            serialized_texts.append(serialized)

        # Serialization reproduces the wire text exactly, minus the decorative CR/LF pairs.
        expected = _interchange_850.replace('\r\n', '')
        self.assertEqual(''.join(serialized_texts), expected)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
