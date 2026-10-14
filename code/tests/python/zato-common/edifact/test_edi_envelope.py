# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.edi.envelope import Format_EDIFACT, read_envelope

# ################################################################################################################################
# ################################################################################################################################

_edifact_payload = (
    b"UNA:+.? 'UNB+UNOC:3+SENDERID:ZZ+RECEIVERID:ZZ+260709:1200+REF001'"
    + b"UNH+1+ORDERS:D:96A:UN'UNT+2+1'UNZ+1+REF001'"
)

_edifact_payload_no_una = (
    b"UNB+UNOC:3+SENDERID:ZZ+RECEIVERID:ZZ+260709:1200+REF001'"
    + b"UNH+1+ORDERS:D:96A:UN'UNT+2+1'UNZ+1+REF001'"
)

# ################################################################################################################################
# ################################################################################################################################

class TestEDIFACTEnvelope:

    def test_all_identifiers_are_read(self) -> 'None':
        information = read_envelope(_edifact_payload)

        assert information.format == Format_EDIFACT

        assert information.sender_id == 'SENDERID'
        assert information.sender_qualifier == 'ZZ'
        assert information.receiver_id == 'RECEIVERID'
        assert information.receiver_qualifier == 'ZZ'

        assert information.document_type == 'ORDERS'

        assert information.interchange_control_number == 'REF001'
        assert information.set_control_number == '1'

# ################################################################################################################################

    def test_text_input_reads_the_same(self) -> 'None':
        payload_text = _edifact_payload.decode('ascii')
        information = read_envelope(payload_text)

        assert information.format == Format_EDIFACT
        assert information.document_type == 'ORDERS'

# ################################################################################################################################

    def test_una_is_optional(self) -> 'None':
        information = read_envelope(_edifact_payload_no_una)

        assert information.format == Format_EDIFACT
        assert information.sender_id == 'SENDERID'
        assert information.document_type == 'ORDERS'

# ################################################################################################################################
# ################################################################################################################################

class TestNonEDIPayloads:

    def test_json_is_not_edi(self) -> 'None':
        information = read_envelope(b'{"hello": "world"}')

        assert information.format == ''

# ################################################################################################################################

    def test_empty_input_is_not_edi(self) -> 'None':
        information = read_envelope(b'')

        assert information.format == ''

# ################################################################################################################################

    def test_binary_input_is_not_edi(self) -> 'None':
        information = read_envelope(b'%PDF-1.7 Test bill of lading content')

        assert information.format == ''

# ################################################################################################################################
# ################################################################################################################################

class TestToDict:

    def test_all_fields_are_present(self) -> 'None':
        information = read_envelope(_edifact_payload)
        data = information.to_dict()

        assert data['format'] == Format_EDIFACT
        assert data['sender_id'] == 'SENDERID'
        assert data['receiver_id'] == 'RECEIVERID'
        assert data['document_type'] == 'ORDERS'
        assert data['interchange_control_number'] == 'REF001'
        assert data['set_control_number'] == '1'

# ################################################################################################################################

    def test_non_edi_fields_are_empty_strings(self) -> 'None':
        information = read_envelope(b'not edi at all')
        data = information.to_dict()

        for value in data.values():
            assert value == ''

# ################################################################################################################################
# ################################################################################################################################
