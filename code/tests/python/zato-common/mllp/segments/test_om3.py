from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OM3


sequence_number_test_observation_master_file = "test_sequence_number_test"
value_type = "test_value_type"


class TestOM3:
    """Comprehensive tests for OM3 segment."""

    def test_om3_build_and_verify(self):
        seg = OM3()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.value_type = value_type

        assert seg.sequence_number_test_observation_master_file == sequence_number_test_observation_master_file
        assert seg.value_type == value_type

    def test_om3_to_dict(self):
        seg = OM3()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.value_type = value_type

        result = seg.to_dict()

        assert result["_segment_id"] == "OM3"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["value_type"] == value_type

    def test_om3_to_json(self):
        seg = OM3()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.value_type = value_type

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OM3"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["value_type"] == value_type
