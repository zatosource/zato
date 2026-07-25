# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.edi.envelope import Format_EDIFACT, Format_X12, read_envelope

# ################################################################################################################################
# ################################################################################################################################

_x12_payload = (
    b'ISA*00*          *00*          *ZZ*ZATORETAIL     *ZZ*PARTNERCORP    '
    + b'*260709*1200*U*00401*000000001*0*P*>~GS*PO*ZATORETAIL*PARTNERCORP*20260709*1200*1*X*004010~'
    + b'ST*850*0001~BEG*00*NE*4523891**20260709~SE*3*0001~GE*1*1~IEA*1*000000001~'
)

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

class TestX12Envelope:

    def test_all_identifiers_are_read(self) -> 'None':
        information = read_envelope(_x12_payload)

        assert information.format == Format_X12

        assert information.sender_qualifier == 'ZZ'
        assert information.sender_id == 'ZATORETAIL'
        assert information.receiver_qualifier == 'ZZ'
        assert information.receiver_id == 'PARTNERCORP'

        assert information.functional_id == 'PO'
        assert information.group_sender_id == 'ZATORETAIL'
        assert information.group_receiver_id == 'PARTNERCORP'

        assert information.document_type == '850'

        assert information.interchange_control_number == '000000001'
        assert information.group_control_number == '1'
        assert information.set_control_number == '0001'

# ################################################################################################################################

    def test_text_input_reads_the_same(self) -> 'None':
        payload_text = _x12_payload.decode('ascii')
        information = read_envelope(payload_text)

        assert information.format == Format_X12
        assert information.document_type == '850'

# ################################################################################################################################

    def test_only_the_first_st_names_the_document_type(self) -> 'None':
        two_sets = _x12_payload.replace(
            b'SE*3*0001~GE',
            b'SE*3*0001~ST*810*0002~SE*2*0002~GE',
        )

        information = read_envelope(two_sets)

        assert information.document_type == '850'
        assert information.set_control_number == '0001'

# ################################################################################################################################

    def test_malformed_isa_yields_an_empty_format(self) -> 'None':
        information = read_envelope(b'ISA*garbage')

        assert information.format == ''
        assert information.document_type == ''

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

        # EDIFACT has no functional group level.
        assert information.group_sender_id == ''
        assert information.group_receiver_id == ''
        assert information.group_control_number == ''

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
        information = read_envelope(_x12_payload)
        data = information.to_dict()

        assert data['format'] == Format_X12
        assert data['sender_id'] == 'ZATORETAIL'
        assert data['receiver_id'] == 'PARTNERCORP'
        assert data['document_type'] == '850'
        assert data['interchange_control_number'] == '000000001'
        assert data['group_control_number'] == '1'
        assert data['set_control_number'] == '0001'

# ################################################################################################################################

    def test_non_edi_fields_are_empty_strings(self) -> 'None':
        information = read_envelope(b'not edi at all')
        data = information.to_dict()

        for value in data.values():
            assert value == ''

# ################################################################################################################################
# ################################################################################################################################
