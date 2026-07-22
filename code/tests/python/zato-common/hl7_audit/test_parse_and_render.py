# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.hl7.display import parse_and_render

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# An admission message with a composite PID-5 - the same shape the IDE's sample presets use
_adt_a01 = (
    'MSH|^~\\&|HIS|GENERAL_HOSPITAL|LAB_SYSTEM|CENTRAL_LAB|20260115103000||ADT^A01^ADT_A01|MSG000001|P|2.9\r'
    'EVN|A01|20260115103000\r'
    'PID|1||NHS7788990^^^NHS^NH||SMITH^JOHN^A||19850315|M\r'
    'PV1|1|I|ICU^101^A\r'
)

# ################################################################################################################################
# ################################################################################################################################

class TestParseAndRender:
    """ The parse-then-render convenience the IDE's parsed view and the audit log both use.
    """

    def test_a_message_renders_its_display_tree(self) -> 'None':

        text = parse_and_render(_adt_a01)
        lines = text.split('\n')

        # The header line names the message
        assert lines[0] == 'ADT^A01 (control id MSG000001)'

        # Segments appear as their own blocks, in wire order
        segment_lines:'strlist' = []

        for line in lines:
            if line:
                if not line.startswith(' '):
                    segment_lines.append(line)

        assert segment_lines[1:] == ['MSH', 'EVN', 'PID', 'PV1']

        # Fields render with their labels and wire values
        assert '  PID-8  Administrative Sex: M' in lines

    def test_a_payload_that_does_not_parse_renders_segment_by_segment(self) -> 'None':

        # An MSH header without a recognizable message structure fails the full parse
        # and renders segment by segment instead, without a header line
        text = parse_and_render('MSH|^~\\&|HIS')
        lines = text.split('\n')

        assert lines[0] == 'MSH'
        assert '  MSH-3  Sending Application: HIS' in lines

    def test_an_empty_payload_renders_as_an_empty_string(self) -> 'None':

        text = parse_and_render('')
        assert text == ''

# ################################################################################################################################
# ################################################################################################################################
