from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RFI


request_date = "test_request_date"
response_due_date = "test_response_due_date"
patient_consent = "test_patient_consent"
date_additional_information_was_submitted = "test_date_additional_info"


class TestRFI:
    """Comprehensive tests for RFI segment."""

    def test_rfi_build_and_verify(self):
        seg = RFI()

        seg.request_date = request_date
        seg.response_due_date = response_due_date
        seg.patient_consent = patient_consent
        seg.date_additional_information_was_submitted = date_additional_information_was_submitted

        assert seg.request_date == request_date
        assert seg.response_due_date == response_due_date
        assert seg.patient_consent == patient_consent
        assert seg.date_additional_information_was_submitted == date_additional_information_was_submitted

    def test_rfi_to_dict(self):
        seg = RFI()

        seg.request_date = request_date
        seg.response_due_date = response_due_date
        seg.patient_consent = patient_consent
        seg.date_additional_information_was_submitted = date_additional_information_was_submitted

        result = seg.to_dict()

        assert result["_segment_id"] == "RFI"
        assert result["request_date"] == request_date
        assert result["response_due_date"] == response_due_date
        assert result["patient_consent"] == patient_consent
        assert result["date_additional_information_was_submitted"] == date_additional_information_was_submitted

    def test_rfi_to_json(self):
        seg = RFI()

        seg.request_date = request_date
        seg.response_due_date = response_due_date
        seg.patient_consent = patient_consent
        seg.date_additional_information_was_submitted = date_additional_information_was_submitted

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RFI"
        assert result["request_date"] == request_date
        assert result["response_due_date"] == response_due_date
        assert result["patient_consent"] == patient_consent
        assert result["date_additional_information_was_submitted"] == date_additional_information_was_submitted
