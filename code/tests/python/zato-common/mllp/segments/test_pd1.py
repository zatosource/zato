from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PD1


separate_bill = "test_separate_bill"
protection_indicator = "test_protection_indicator"
protection_indicator_effective_date = "test_protection_indicator"
immunization_registry_status_effective_date = "test_immunization_registr"
publicity_code_effective_date = "test_publicity_code_effec"
advance_directive_last_verified_date = "test_advance_directive_la"
retirement_date = "test_retirement_date"


class TestPD1:
    """Comprehensive tests for PD1 segment."""

    def test_pd1_build_and_verify(self):
        seg = PD1()

        seg.separate_bill = separate_bill
        seg.protection_indicator = protection_indicator
        seg.protection_indicator_effective_date = protection_indicator_effective_date
        seg.immunization_registry_status_effective_date = immunization_registry_status_effective_date
        seg.publicity_code_effective_date = publicity_code_effective_date
        seg.advance_directive_last_verified_date = advance_directive_last_verified_date
        seg.retirement_date = retirement_date

        assert seg.separate_bill == separate_bill
        assert seg.protection_indicator == protection_indicator
        assert seg.protection_indicator_effective_date == protection_indicator_effective_date
        assert seg.immunization_registry_status_effective_date == immunization_registry_status_effective_date
        assert seg.publicity_code_effective_date == publicity_code_effective_date
        assert seg.advance_directive_last_verified_date == advance_directive_last_verified_date
        assert seg.retirement_date == retirement_date

    def test_pd1_to_dict(self):
        seg = PD1()

        seg.separate_bill = separate_bill
        seg.protection_indicator = protection_indicator
        seg.protection_indicator_effective_date = protection_indicator_effective_date
        seg.immunization_registry_status_effective_date = immunization_registry_status_effective_date
        seg.publicity_code_effective_date = publicity_code_effective_date
        seg.advance_directive_last_verified_date = advance_directive_last_verified_date
        seg.retirement_date = retirement_date

        result = seg.to_dict()

        assert result["_segment_id"] == "PD1"
        assert result["separate_bill"] == separate_bill
        assert result["protection_indicator"] == protection_indicator
        assert result["protection_indicator_effective_date"] == protection_indicator_effective_date
        assert result["immunization_registry_status_effective_date"] == immunization_registry_status_effective_date
        assert result["publicity_code_effective_date"] == publicity_code_effective_date
        assert result["advance_directive_last_verified_date"] == advance_directive_last_verified_date
        assert result["retirement_date"] == retirement_date

    def test_pd1_to_json(self):
        seg = PD1()

        seg.separate_bill = separate_bill
        seg.protection_indicator = protection_indicator
        seg.protection_indicator_effective_date = protection_indicator_effective_date
        seg.immunization_registry_status_effective_date = immunization_registry_status_effective_date
        seg.publicity_code_effective_date = publicity_code_effective_date
        seg.advance_directive_last_verified_date = advance_directive_last_verified_date
        seg.retirement_date = retirement_date

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PD1"
        assert result["separate_bill"] == separate_bill
        assert result["protection_indicator"] == protection_indicator
        assert result["protection_indicator_effective_date"] == protection_indicator_effective_date
        assert result["immunization_registry_status_effective_date"] == immunization_registry_status_effective_date
        assert result["publicity_code_effective_date"] == publicity_code_effective_date
        assert result["advance_directive_last_verified_date"] == advance_directive_last_verified_date
        assert result["retirement_date"] == retirement_date
