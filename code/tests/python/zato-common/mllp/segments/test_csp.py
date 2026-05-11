from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import CSP


datetime_study_phase_began = "test_datetime_study_phase"
datetime_study_phase_ended = "test_datetime_study_phase"


class TestCSP:
    """Comprehensive tests for CSP segment."""

    def test_csp_build_and_verify(self):
        seg = CSP()

        seg.datetime_study_phase_began = datetime_study_phase_began
        seg.datetime_study_phase_ended = datetime_study_phase_ended

        assert seg.datetime_study_phase_began == datetime_study_phase_began
        assert seg.datetime_study_phase_ended == datetime_study_phase_ended

    def test_csp_to_dict(self):
        seg = CSP()

        seg.datetime_study_phase_began = datetime_study_phase_began
        seg.datetime_study_phase_ended = datetime_study_phase_ended

        result = seg.to_dict()

        assert result["_segment_id"] == "CSP"
        assert result["datetime_study_phase_began"] == datetime_study_phase_began
        assert result["datetime_study_phase_ended"] == datetime_study_phase_ended

    def test_csp_to_json(self):
        seg = CSP()

        seg.datetime_study_phase_began = datetime_study_phase_began
        seg.datetime_study_phase_ended = datetime_study_phase_ended

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CSP"
        assert result["datetime_study_phase_began"] == datetime_study_phase_began
        assert result["datetime_study_phase_ended"] == datetime_study_phase_ended
