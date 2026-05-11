from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import CSS


study_scheduled_patient_time_point = "test_study_scheduled_pati"


class TestCSS:
    """Comprehensive tests for CSS segment."""

    def test_css_build_and_verify(self):
        seg = CSS()

        seg.study_scheduled_patient_time_point = study_scheduled_patient_time_point

        assert seg.study_scheduled_patient_time_point == study_scheduled_patient_time_point

    def test_css_to_dict(self):
        seg = CSS()

        seg.study_scheduled_patient_time_point = study_scheduled_patient_time_point

        result = seg.to_dict()

        assert result["_segment_id"] == "CSS"
        assert result["study_scheduled_patient_time_point"] == study_scheduled_patient_time_point

    def test_css_to_json(self):
        seg = CSS()

        seg.study_scheduled_patient_time_point = study_scheduled_patient_time_point

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CSS"
        assert result["study_scheduled_patient_time_point"] == study_scheduled_patient_time_point
