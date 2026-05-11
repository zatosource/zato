from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import CM2


set_id_cm2 = "test_set_id_cm2"
description_of_time_point = "test_description_of_time_"


class TestCM2:
    """Comprehensive tests for CM2 segment."""

    def test_cm2_build_and_verify(self):
        seg = CM2()

        seg.set_id_cm2 = set_id_cm2
        seg.description_of_time_point = description_of_time_point

        assert seg.set_id_cm2 == set_id_cm2
        assert seg.description_of_time_point == description_of_time_point

    def test_cm2_to_dict(self):
        seg = CM2()

        seg.set_id_cm2 = set_id_cm2
        seg.description_of_time_point = description_of_time_point

        result = seg.to_dict()

        assert result["_segment_id"] == "CM2"
        assert result["set_id_cm2"] == set_id_cm2
        assert result["description_of_time_point"] == description_of_time_point

    def test_cm2_to_json(self):
        seg = CM2()

        seg.set_id_cm2 = set_id_cm2
        seg.description_of_time_point = description_of_time_point

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CM2"
        assert result["set_id_cm2"] == set_id_cm2
        assert result["description_of_time_point"] == description_of_time_point
