# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import pytest

# Zato
from zato.common.hl7.mllp.preprocess import parse_with_channel_defaults
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.hl7v2 import HL7Message
    HL7Message = HL7Message

# ################################################################################################################################
# ################################################################################################################################

# An admission message with LF line endings, as pasted into the IDE's request editor -
# the pre-processing pipeline must normalize them to CR before parsing
_adt_a01_with_lf = (
    'MSH|^~\\&|HIS|GENERAL_HOSPITAL|LAB_SYSTEM|CENTRAL_LAB|20260115103000||ADT^A01^ADT_A01|MSG000001|P|2.9\n'
    'EVN|A01|20260115103000\n'
    'PID|1||NHS7788990^^^NHS^NH||SMITH^JOHN^A||19850315|M\n'
    'PV1|1|I|ICU^101^A\n'
)

# A batch payload - a channel hands these to the service as raw text, unparsed
_batch = (
    'BHS|^~\\&|LAB_SYSTEM|CENTRAL_LAB|HIS|GENERAL_HOSPITAL|20260115110000\r'
    'MSH|^~\\&|LAB_SYSTEM|CENTRAL_LAB|HIS|GENERAL_HOSPITAL|20260115110000||ORU^R01^ORU_R01|MSG000002|P|2.9\r'
    'PID|1||334455^^^CLINIC^MR||DOE^JANE||19900101|F\r'
    'BTS|1\r'
)

# ################################################################################################################################
# ################################################################################################################################

class TestParseWithChannelDefaults:
    """ The channel-equivalent parse the IDE's direct invoke applies to HL7 v2 payloads.
    """

    def test_a_message_parses_into_what_a_channel_delivers(self) -> 'None':

        out = parse_with_channel_defaults(_adt_a01_with_lf)
        message = cast_('HL7Message', out)

        # The parsed message navigates like any channel-delivered one
        assert message.get('MSH.9') == 'ADT'
        assert message.get('MSH.10') == 'MSG000001'
        assert message.get('PID.8') == 'M'

    def test_a_batch_passes_through_as_raw_text(self) -> 'None':

        out = parse_with_channel_defaults(_batch)

        assert isinstance(out, str)
        assert out.startswith('BHS|')
        assert 'MSG000002' in out

    def test_a_payload_that_does_not_parse_raises(self) -> 'None':

        with pytest.raises(Exception):
            _ = parse_with_channel_defaults('This is not an HL7 message at all')

# ################################################################################################################################
# ################################################################################################################################
