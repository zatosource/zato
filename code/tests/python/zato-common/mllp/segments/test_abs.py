from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ABS


date_time_of_attestation = "test_date_time_of_attesta"
abstract_completion_date_time = "test_abstract_completion_"
caesarian_section_indicator = "test_caesarian_section_in"
gestation_period_weeks = "test_gestation_period_wee"
stillborn_indicator = "test_stillborn_indicator"


class TestABS:
    """Comprehensive tests for ABS segment."""

    def test_abs_build_and_verify(self):
        seg = ABS()

        seg.date_time_of_attestation = date_time_of_attestation
        seg.abstract_completion_date_time = abstract_completion_date_time
        seg.caesarian_section_indicator = caesarian_section_indicator
        seg.gestation_period_weeks = gestation_period_weeks
        seg.stillborn_indicator = stillborn_indicator

        assert seg.date_time_of_attestation == date_time_of_attestation
        assert seg.abstract_completion_date_time == abstract_completion_date_time
        assert seg.caesarian_section_indicator == caesarian_section_indicator
        assert seg.gestation_period_weeks == gestation_period_weeks
        assert seg.stillborn_indicator == stillborn_indicator

    def test_abs_to_dict(self):
        seg = ABS()

        seg.date_time_of_attestation = date_time_of_attestation
        seg.abstract_completion_date_time = abstract_completion_date_time
        seg.caesarian_section_indicator = caesarian_section_indicator
        seg.gestation_period_weeks = gestation_period_weeks
        seg.stillborn_indicator = stillborn_indicator

        result = seg.to_dict()

        assert result["_segment_id"] == "ABS"
        assert result["date_time_of_attestation"] == date_time_of_attestation
        assert result["abstract_completion_date_time"] == abstract_completion_date_time
        assert result["caesarian_section_indicator"] == caesarian_section_indicator
        assert result["gestation_period_weeks"] == gestation_period_weeks
        assert result["stillborn_indicator"] == stillborn_indicator

    def test_abs_to_json(self):
        seg = ABS()

        seg.date_time_of_attestation = date_time_of_attestation
        seg.abstract_completion_date_time = abstract_completion_date_time
        seg.caesarian_section_indicator = caesarian_section_indicator
        seg.gestation_period_weeks = gestation_period_weeks
        seg.stillborn_indicator = stillborn_indicator

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ABS"
        assert result["date_time_of_attestation"] == date_time_of_attestation
        assert result["abstract_completion_date_time"] == abstract_completion_date_time
        assert result["caesarian_section_indicator"] == caesarian_section_indicator
        assert result["gestation_period_weeks"] == gestation_period_weeks
        assert result["stillborn_indicator"] == stillborn_indicator
