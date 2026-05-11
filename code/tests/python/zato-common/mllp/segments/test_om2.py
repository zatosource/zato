from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OM2


sequence_number_test_observation_master_file = "test_sequence_number_test"
si_conversion_factor = "test_si_conversion_factor"
minimum_meaningful_increments = "test_minimum_meaningful_i"


class TestOM2:
    """Comprehensive tests for OM2 segment."""

    def test_om2_build_and_verify(self):
        seg = OM2()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.si_conversion_factor = si_conversion_factor
        seg.minimum_meaningful_increments = minimum_meaningful_increments

        assert seg.sequence_number_test_observation_master_file == sequence_number_test_observation_master_file
        assert seg.si_conversion_factor == si_conversion_factor
        assert seg.minimum_meaningful_increments == minimum_meaningful_increments

    def test_om2_to_dict(self):
        seg = OM2()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.si_conversion_factor = si_conversion_factor
        seg.minimum_meaningful_increments = minimum_meaningful_increments

        result = seg.to_dict()

        assert result["_segment_id"] == "OM2"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["si_conversion_factor"] == si_conversion_factor
        assert result["minimum_meaningful_increments"] == minimum_meaningful_increments

    def test_om2_to_json(self):
        seg = OM2()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.si_conversion_factor = si_conversion_factor
        seg.minimum_meaningful_increments = minimum_meaningful_increments

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OM2"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["si_conversion_factor"] == si_conversion_factor
        assert result["minimum_meaningful_increments"] == minimum_meaningful_increments
