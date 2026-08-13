# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.api import AuditEvent, AuditSource
from zato.common.hl7.audit import get_audit_attrs, get_control_id, get_message_type, get_mrn, get_sending_facility, \
    get_wire_attrs
from zato.hl7v2 import parse_hl7
from zato.hl7v2.tests.fakers import fake, Sender_Pool
from zato.hl7v2.tests.fakers.msg_adt import fake_adta01

# ################################################################################################################################
# ################################################################################################################################

# An admission whose patient carries two identifiers - a national one first
# and the medical record number second, so extraction has to pick by type, not by position.
_adt_a01 = (
    'MSH|^~\\&|HIS|GENERAL_HOSPITAL|LAB_SYSTEM|CENTRAL_LAB|20260115103000||ADT^A01^ADT_A01|MSG000001|P|2.9\r'
    'EVN|A01|20260115103000\r'
    'PID|1||NHS7788990^^^NHS^NH~445566^^^GENERAL_HOSPITAL^MR||SMITH^JOHN^A||19850315|M\r'
    'PV1|1|I|ICU^101^A\r'
)

# A lab result whose PID lives inside a message group, not at the top level of the message
_oru_r01 = (
    'MSH|^~\\&|LAB_SYSTEM|CENTRAL_LAB|HIS|GENERAL_HOSPITAL|20260115110000||ORU^R01^ORU_R01|MSG000002|P|2.9\r'
    'PID|1||334455^^^CLINIC^MR||DOE^JANE||19900101|F\r'
    'OBR|1|ORDER001||24331-1^Lipid panel^LN\r'
    'OBX|1|NM|2093-3^Cholesterol^LN||182|mg/dL|||||F\r'
)

# An admission whose patient identifier carries no type code at all
_adt_a01_untyped_identifier = (
    'MSH|^~\\&|HIS|GENERAL_HOSPITAL|LAB_SYSTEM|CENTRAL_LAB|20260115103000||ADT^A01^ADT_A01|MSG000003|P|2.9\r'
    'EVN|A01|20260115103000\r'
    'PID|1||778899||BROWN^ALICE||19701224|F\r'
    'PV1|1|O|CLINIC^1^A\r'
)

# An acknowledgment - a message with no PID and no patient at all
_ack = (
    'MSH|^~\\&|LAB_SYSTEM|CENTRAL_LAB|HIS|GENERAL_HOSPITAL|20260115103005||ACK^A01^ACK|ACK000001|P|2.9\r'
    'MSA|AA|MSG000001\r'
)

# ################################################################################################################################
# ################################################################################################################################

class TestAuditSource:

    def test_hl7_source_and_event_types_exist(self) -> 'None':

        # The MLLP sources sit next to the other audit sources, one per direction ..
        assert AuditSource.MLLP_Channel == 'mllp-channel'
        assert AuditSource.MLLP_Outgoing == 'mllp-outgoing'

        # .. and the four HL7 event types are the shared ones every message exchange uses.
        assert AuditEvent.Message_Received == 'message-received'
        assert AuditEvent.Message_Sent == 'message-sent'
        assert AuditEvent.Ack_Sent == 'ack-sent'
        assert AuditEvent.Ack_Received == 'ack-received'

# ################################################################################################################################
# ################################################################################################################################

class TestMessageType:

    def test_code_and_trigger_are_joined(self) -> 'None':
        msg = parse_hl7(_adt_a01)
        assert get_message_type(msg) == 'ADT^A01'

# ################################################################################################################################

    def test_group_nested_message_reports_its_type(self) -> 'None':
        msg = parse_hl7(_oru_r01)
        assert get_message_type(msg) == 'ORU^R01'

# ################################################################################################################################
# ################################################################################################################################

class TestMRN:

    def test_identifier_typed_mr_wins_over_position(self) -> 'None':

        # The national identifier comes first but the MR-typed one must win.
        msg = parse_hl7(_adt_a01)
        assert get_mrn(msg) == '445566'

# ################################################################################################################################

    def test_group_nested_pid_is_found(self) -> 'None':

        # The ORU's PID sits inside a patient-result group, not at the top level.
        msg = parse_hl7(_oru_r01)
        assert get_mrn(msg) == '334455'

# ################################################################################################################################

    def test_untyped_identifier_is_the_default(self) -> 'None':

        # With no identifier typed MR, the first identifier is what an operator searches by.
        msg = parse_hl7(_adt_a01_untyped_identifier)
        assert get_mrn(msg) == '778899'

# ################################################################################################################################

    def test_message_without_pid_has_no_mrn(self) -> 'None':
        msg = parse_hl7(_ack)
        assert get_mrn(msg) == ''

# ################################################################################################################################
# ################################################################################################################################

class TestSendingFacilityAndControlID:

    def test_sending_facility_is_the_namespace_id(self) -> 'None':
        msg = parse_hl7(_adt_a01)
        assert get_sending_facility(msg) == 'GENERAL_HOSPITAL'

# ################################################################################################################################

    def test_control_id_comes_from_msh_10(self) -> 'None':
        msg = parse_hl7(_adt_a01)
        assert get_control_id(msg) == 'MSG000001'

# ################################################################################################################################

    def test_a_generated_message_comes_from_an_interface(self) -> 'None':

        # A generated message's sending side is one of the interfaces the fakers know,
        # so the facility a report names as the caller is a system, never a person.
        fake.seed_instance(314159)

        for _ in range(20):

            msg = parse_hl7(fake_adta01())

            sending_application = msg.get('msh.sending_application')
            sending_facility = get_sending_facility(msg)

            assert (sending_application, sending_facility) in Sender_Pool

# ################################################################################################################################
# ################################################################################################################################

class TestWireAttrs:

    def test_type_and_trigger_come_off_the_wire(self) -> 'None':
        msh_line = _adt_a01.split('\r', 1)[0]

        attrs = get_wire_attrs(msh_line)

        assert attrs == {
            'msg_type': 'ADT^A01',
            'facility': 'GENERAL_HOSPITAL',
        }

# ################################################################################################################################

    def test_a_type_without_a_trigger_stands_alone(self) -> 'None':
        msh_line = 'MSH|^~\\&|HIS|GENERAL_HOSPITAL|LAB_SYSTEM|CENTRAL_LAB|20260115103000||ACK|MSG000004|P|2.9'

        attrs = get_wire_attrs(msh_line)

        assert attrs['msg_type'] == 'ACK'
        assert attrs['facility'] == 'GENERAL_HOSPITAL'

# ################################################################################################################################

    def test_a_line_with_no_msh_yields_empty_attrs(self) -> 'None':

        # Wire data is external input - an empty message sent from the Dashboard invoker
        # must yield empty attributes rather than an error.
        for msh_line in ('', 'MSH', 'abc'):

            attrs = get_wire_attrs(msh_line)

            assert attrs == {
                'msg_type': '',
                'facility': '',
            }

# ################################################################################################################################
# ################################################################################################################################

class TestAuditAttrs:

    def test_attrs_carry_the_searchable_fields(self) -> 'None':
        msg = parse_hl7(_adt_a01)

        attrs = get_audit_attrs(msg)

        assert attrs == {
            'msg_type': 'ADT^A01',
            'mrn': '445566',
            'facility': 'GENERAL_HOSPITAL',
        }

# ################################################################################################################################

    def test_attrs_match_the_model_on_a_faked_admission(self) -> 'None':

        # A generated admission proves extraction agrees with the model's own field access,
        # whatever the concrete values are.
        fake.seed_instance(271828)
        msg = parse_hl7(fake_adta01())

        attrs = get_audit_attrs(msg)

        assert attrs['msg_type'] == 'ADT^A01'
        assert attrs['mrn'] == msg.get('pid.patient_identifier_list[0]')
        assert attrs['facility'] == msg.get('msh.sending_facility')
        assert get_control_id(msg) == msg.get('msh.message_control_id')

# ################################################################################################################################
# ################################################################################################################################
