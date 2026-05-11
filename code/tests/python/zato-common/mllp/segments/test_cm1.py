from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import CM1


set_id_cm1 = "test_set_id_cm1"
description_of_study_phase = "test_description_of_study"


class TestCM1:
    """Comprehensive tests for CM1 segment."""

    def test_cm1_build_and_verify(self):
        seg = CM1()

        seg.set_id_cm1 = set_id_cm1
        seg.description_of_study_phase = description_of_study_phase

        assert seg.set_id_cm1 == set_id_cm1
        assert seg.description_of_study_phase == description_of_study_phase

    def test_cm1_to_dict(self):
        seg = CM1()

        seg.set_id_cm1 = set_id_cm1
        seg.description_of_study_phase = description_of_study_phase

        result = seg.to_dict()

        assert result["_segment_id"] == "CM1"
        assert result["set_id_cm1"] == set_id_cm1
        assert result["description_of_study_phase"] == description_of_study_phase

    def test_cm1_to_json(self):
        seg = CM1()

        seg.set_id_cm1 = set_id_cm1
        seg.description_of_study_phase = description_of_study_phase

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CM1"
        assert result["set_id_cm1"] == set_id_cm1
        assert result["description_of_study_phase"] == description_of_study_phase
