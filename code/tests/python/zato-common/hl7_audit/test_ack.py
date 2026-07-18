# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.api import AuditClassification, AuditOutcome
from zato.common.hl7.audit import interpret_ack, interpret_ack_code, interpret_ack_timeout, ACKStatus
from zato.hl7v2 import parse_hl7
from zato.hl7v2.tests.fakers import fake
from zato.hl7v2.tests.fakers.msg_ack import fake_ack

# ################################################################################################################################
# ################################################################################################################################

# A negative acknowledgment - the receiving application reported an error for our message
_ack_application_error = (
    'MSH|^~\\&|LAB_SYSTEM|CENTRAL_LAB|HIS|GENERAL_HOSPITAL|20260115103005||ACK^A01^ACK|ACK000001|P|2.9\r'
    'MSA|AE|MSG000001\r'
)

# A response that should have been an acknowledgment but carries no MSA at all
_response_without_msa = (
    'MSH|^~\\&|LAB_SYSTEM|CENTRAL_LAB|HIS|GENERAL_HOSPITAL|20260115103005||ADT^A01^ADT_A01|MSG000009|P|2.9\r'
    'EVN|A01|20260115103005\r'
    'PID|1||112233^^^CLINIC^MR||GREEN^PAUL||19601111|M\r'
    'PV1|1|I|ICU^102^B\r'
)

# ################################################################################################################################
# ################################################################################################################################

class TestPositiveCodes:

    def test_application_accept(self) -> 'None':
        result = interpret_ack_code(ACKStatus.Application_Accept, 'MSG000001')

        assert result.ack_status == 'AA'
        assert result.outcome == AuditOutcome.OK
        assert result.application_outcome == ''
        assert result.classification == ''
        assert result.control_id == 'MSG000001'

# ################################################################################################################################

    def test_commit_accept(self) -> 'None':
        result = interpret_ack_code(ACKStatus.Commit_Accept)

        assert result.ack_status == 'CA'
        assert result.outcome == AuditOutcome.OK
        assert result.application_outcome == ''
        assert result.classification == ''

# ################################################################################################################################
# ################################################################################################################################

class TestNegativeCodes:

    def test_application_error_is_unclassified(self) -> 'None':

        # An error may need a resend or a repair - a person decides, so no classification.
        result = interpret_ack_code(ACKStatus.Application_Error)

        assert result.ack_status == 'AE'
        assert result.outcome == AuditOutcome.Error
        assert result.application_outcome == 'AE'
        assert result.classification == ''

# ################################################################################################################################

    def test_commit_error_is_unclassified(self) -> 'None':
        result = interpret_ack_code(ACKStatus.Commit_Error)

        assert result.outcome == AuditOutcome.Error
        assert result.application_outcome == 'CE'
        assert result.classification == ''

# ################################################################################################################################

    def test_application_reject_is_permanent(self) -> 'None':

        # A reject can never succeed as-is - the message must change first.
        result = interpret_ack_code(ACKStatus.Application_Reject)

        assert result.ack_status == 'AR'
        assert result.outcome == AuditOutcome.Error
        assert result.application_outcome == 'AR'
        assert result.classification == AuditClassification.Permanent

# ################################################################################################################################

    def test_commit_reject_is_permanent(self) -> 'None':
        result = interpret_ack_code(ACKStatus.Commit_Reject)

        assert result.outcome == AuditOutcome.Error
        assert result.application_outcome == 'CR'
        assert result.classification == AuditClassification.Permanent

# ################################################################################################################################

    def test_unknown_code_is_an_unclassified_error(self) -> 'None':

        # The acknowledgment itself was not understood - the code is kept for display
        # but does not become an application outcome.
        result = interpret_ack_code('XX')

        assert result.ack_status == 'XX'
        assert result.outcome == AuditOutcome.Error
        assert result.application_outcome == ''
        assert result.classification == ''

# ################################################################################################################################
# ################################################################################################################################

class TestTimeout:

    def test_no_acknowledgment_is_a_transient_failure(self) -> 'None':

        # Resending the same message once the receiver is back can work.
        result = interpret_ack_timeout()

        assert result.ack_status == ACKStatus.Timeout
        assert result.outcome == AuditOutcome.Error
        assert result.application_outcome == ''
        assert result.classification == AuditClassification.Transient
        assert result.control_id == ''

# ################################################################################################################################
# ################################################################################################################################

class TestParsedMessages:

    def test_negative_acknowledgment_message(self) -> 'None':
        msg = parse_hl7(_ack_application_error)

        result = interpret_ack(msg)

        assert result.ack_status == 'AE'
        assert result.outcome == AuditOutcome.Error
        assert result.application_outcome == 'AE'
        assert result.control_id == 'MSG000001'

# ################################################################################################################################

    def test_faked_positive_acknowledgment(self) -> 'None':

        # A generated acknowledgment proves interpretation agrees with the model's own field access.
        fake.seed_instance(314159)
        msg = parse_hl7(fake_ack())

        result = interpret_ack(msg)

        assert result.ack_status == 'AA'
        assert result.outcome == AuditOutcome.OK
        assert result.control_id == msg.get('msa.message_control_id')

# ################################################################################################################################

    def test_response_without_msa_is_an_error(self) -> 'None':

        # The sender expected an acknowledgment and received something else entirely.
        msg = parse_hl7(_response_without_msa)

        result = interpret_ack(msg)

        assert result.ack_status == ''
        assert result.outcome == AuditOutcome.Error
        assert result.application_outcome == ''
        assert result.control_id == ''

# ################################################################################################################################
# ################################################################################################################################
