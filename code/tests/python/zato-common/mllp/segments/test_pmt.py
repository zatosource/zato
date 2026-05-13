from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PMT


payment_remittance_effective_date_time = "test_payment_remittance_e"
payment_remittance_expiration_date_time = "test_payment_remittance_e"
payment_remittance_date_time = "test_payment_remittance_d"
payee_transit_number = "test_payee_transit_number"
esr_code_line = "test_esr_code_line"


class TestPMT:
    """Comprehensive tests for PMT segment."""

    def test_pmt_build_and_verify(self):
        seg = PMT()

        seg.payment_remittance_effective_date_time = payment_remittance_effective_date_time
        seg.payment_remittance_expiration_date_time = payment_remittance_expiration_date_time
        seg.payment_remittance_date_time = payment_remittance_date_time
        seg.payee_transit_number = payee_transit_number
        seg.esr_code_line = esr_code_line

        assert seg.payment_remittance_effective_date_time == payment_remittance_effective_date_time
        assert seg.payment_remittance_expiration_date_time == payment_remittance_expiration_date_time
        assert seg.payment_remittance_date_time == payment_remittance_date_time
        assert seg.payee_transit_number == payee_transit_number
        assert seg.esr_code_line == esr_code_line

    def test_pmt_to_dict(self):
        seg = PMT()

        seg.payment_remittance_effective_date_time = payment_remittance_effective_date_time
        seg.payment_remittance_expiration_date_time = payment_remittance_expiration_date_time
        seg.payment_remittance_date_time = payment_remittance_date_time
        seg.payee_transit_number = payee_transit_number
        seg.esr_code_line = esr_code_line

        result = seg.to_dict()

        assert result["_segment_id"] == "PMT"
        assert result["payment_remittance_effective_date_time"] == payment_remittance_effective_date_time
        assert result["payment_remittance_expiration_date_time"] == payment_remittance_expiration_date_time
        assert result["payment_remittance_date_time"] == payment_remittance_date_time
        assert result["payee_transit_number"] == payee_transit_number
        assert result["esr_code_line"] == esr_code_line

    def test_pmt_to_json(self):
        seg = PMT()

        seg.payment_remittance_effective_date_time = payment_remittance_effective_date_time
        seg.payment_remittance_expiration_date_time = payment_remittance_expiration_date_time
        seg.payment_remittance_date_time = payment_remittance_date_time
        seg.payee_transit_number = payee_transit_number
        seg.esr_code_line = esr_code_line

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PMT"
        assert result["payment_remittance_effective_date_time"] == payment_remittance_effective_date_time
        assert result["payment_remittance_expiration_date_time"] == payment_remittance_expiration_date_time
        assert result["payment_remittance_date_time"] == payment_remittance_date_time
        assert result["payee_transit_number"] == payee_transit_number
        assert result["esr_code_line"] == esr_code_line
