from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OM5


sequence_number_test_observation_master_file = "test_sequence_number_test"
observation_id_suffixes = "test_observation_id_suffi"


class TestOM5:
    """Comprehensive tests for OM5 segment."""

    def test_om5_build_and_verify(self):
        seg = OM5()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.observation_id_suffixes = observation_id_suffixes

        assert seg.sequence_number_test_observation_master_file == sequence_number_test_observation_master_file
        assert seg.observation_id_suffixes == observation_id_suffixes

    def test_om5_to_dict(self):
        seg = OM5()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.observation_id_suffixes = observation_id_suffixes

        result = seg.to_dict()

        assert result["_segment_id"] == "OM5"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["observation_id_suffixes"] == observation_id_suffixes

    def test_om5_to_json(self):
        seg = OM5()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.observation_id_suffixes = observation_id_suffixes

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OM5"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["observation_id_suffixes"] == observation_id_suffixes
