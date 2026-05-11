from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import DMI


average_length_of_stay = "test_average_length_of_st"
relative_weight = "test_relative_weight"


class TestDMI:
    """Comprehensive tests for DMI segment."""

    def test_dmi_build_and_verify(self):
        seg = DMI()

        seg.average_length_of_stay = average_length_of_stay
        seg.relative_weight = relative_weight

        assert seg.average_length_of_stay == average_length_of_stay
        assert seg.relative_weight == relative_weight

    def test_dmi_to_dict(self):
        seg = DMI()

        seg.average_length_of_stay = average_length_of_stay
        seg.relative_weight = relative_weight

        result = seg.to_dict()

        assert result["_segment_id"] == "DMI"
        assert result["average_length_of_stay"] == average_length_of_stay
        assert result["relative_weight"] == relative_weight

    def test_dmi_to_json(self):
        seg = DMI()

        seg.average_length_of_stay = average_length_of_stay
        seg.relative_weight = relative_weight

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "DMI"
        assert result["average_length_of_stay"] == average_length_of_stay
        assert result["relative_weight"] == relative_weight
