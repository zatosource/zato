from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OM4


sequence_number_test_observation_master_file = "test_sequence_number_test"
derived_specimen = "test_derived_specimen"
preparation = "test_preparation"
special_handling_requirements = "test_special_handling_req"
specimen_requirements = "test_specimen_requirement"
specimen_preference = "test_specimen_preference"
preferred_specimen_attribture_sequence_id = "test_preferred_specimen_a"


class TestOM4:
    """Comprehensive tests for OM4 segment."""

    def test_om4_build_and_verify(self):
        seg = OM4()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.derived_specimen = derived_specimen
        seg.preparation = preparation
        seg.special_handling_requirements = special_handling_requirements
        seg.specimen_requirements = specimen_requirements
        seg.specimen_preference = specimen_preference
        seg.preferred_specimen_attribture_sequence_id = preferred_specimen_attribture_sequence_id

        assert seg.sequence_number_test_observation_master_file == sequence_number_test_observation_master_file
        assert seg.derived_specimen == derived_specimen
        assert seg.preparation == preparation
        assert seg.special_handling_requirements == special_handling_requirements
        assert seg.specimen_requirements == specimen_requirements
        assert seg.specimen_preference == specimen_preference
        assert seg.preferred_specimen_attribture_sequence_id == preferred_specimen_attribture_sequence_id

    def test_om4_to_dict(self):
        seg = OM4()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.derived_specimen = derived_specimen
        seg.preparation = preparation
        seg.special_handling_requirements = special_handling_requirements
        seg.specimen_requirements = specimen_requirements
        seg.specimen_preference = specimen_preference
        seg.preferred_specimen_attribture_sequence_id = preferred_specimen_attribture_sequence_id

        result = seg.to_dict()

        assert result["_segment_id"] == "OM4"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["derived_specimen"] == derived_specimen
        assert result["preparation"] == preparation
        assert result["special_handling_requirements"] == special_handling_requirements
        assert result["specimen_requirements"] == specimen_requirements
        assert result["specimen_preference"] == specimen_preference
        assert result["preferred_specimen_attribture_sequence_id"] == preferred_specimen_attribture_sequence_id

    def test_om4_to_json(self):
        seg = OM4()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.derived_specimen = derived_specimen
        seg.preparation = preparation
        seg.special_handling_requirements = special_handling_requirements
        seg.specimen_requirements = specimen_requirements
        seg.specimen_preference = specimen_preference
        seg.preferred_specimen_attribture_sequence_id = preferred_specimen_attribture_sequence_id

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OM4"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["derived_specimen"] == derived_specimen
        assert result["preparation"] == preparation
        assert result["special_handling_requirements"] == special_handling_requirements
        assert result["specimen_requirements"] == specimen_requirements
        assert result["specimen_preference"] == specimen_preference
        assert result["preferred_specimen_attribture_sequence_id"] == preferred_specimen_attribture_sequence_id
