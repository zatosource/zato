from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OM6


sequence_number_test_observation_master_file = "test_sequence_number_test"
derivation_rule = "test_derivation_rule"


class TestOM6:
    """Comprehensive tests for OM6 segment."""

    def test_om6_build_and_verify(self):
        seg = OM6()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.derivation_rule = derivation_rule

        assert seg.sequence_number_test_observation_master_file == sequence_number_test_observation_master_file
        assert seg.derivation_rule == derivation_rule

    def test_om6_to_dict(self):
        seg = OM6()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.derivation_rule = derivation_rule

        result = seg.to_dict()

        assert result["_segment_id"] == "OM6"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["derivation_rule"] == derivation_rule

    def test_om6_to_json(self):
        seg = OM6()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.derivation_rule = derivation_rule

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OM6"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["derivation_rule"] == derivation_rule
