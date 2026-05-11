from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import REL


set_id_rel = "test_set_id_rel"
negation_indicator = "test_negation_indicator"
priority_no = "test_priority_no"
priority_sequence_no_rel_preference_for_consideration = "test_priority_sequence_no"
separability_indicator = "test_separability_indicat"
source_information_instance_object_type = "test_source_information_i"
target_information_instance_object_type = "test_target_information_i"


class TestREL:
    """Comprehensive tests for REL segment."""

    def test_rel_build_and_verify(self):
        seg = REL()

        seg.set_id_rel = set_id_rel
        seg.negation_indicator = negation_indicator
        seg.priority_no = priority_no
        seg.priority_sequence_no_rel_preference_for_consideration = priority_sequence_no_rel_preference_for_consideration
        seg.separability_indicator = separability_indicator
        seg.source_information_instance_object_type = source_information_instance_object_type
        seg.target_information_instance_object_type = target_information_instance_object_type

        assert seg.set_id_rel == set_id_rel
        assert seg.negation_indicator == negation_indicator
        assert seg.priority_no == priority_no
        assert seg.priority_sequence_no_rel_preference_for_consideration == priority_sequence_no_rel_preference_for_consideration
        assert seg.separability_indicator == separability_indicator
        assert seg.source_information_instance_object_type == source_information_instance_object_type
        assert seg.target_information_instance_object_type == target_information_instance_object_type

    def test_rel_to_dict(self):
        seg = REL()

        seg.set_id_rel = set_id_rel
        seg.negation_indicator = negation_indicator
        seg.priority_no = priority_no
        seg.priority_sequence_no_rel_preference_for_consideration = priority_sequence_no_rel_preference_for_consideration
        seg.separability_indicator = separability_indicator
        seg.source_information_instance_object_type = source_information_instance_object_type
        seg.target_information_instance_object_type = target_information_instance_object_type

        result = seg.to_dict()

        assert result["_segment_id"] == "REL"
        assert result["set_id_rel"] == set_id_rel
        assert result["negation_indicator"] == negation_indicator
        assert result["priority_no"] == priority_no
        assert result["priority_sequence_no_rel_preference_for_consideration"] == priority_sequence_no_rel_preference_for_consideration
        assert result["separability_indicator"] == separability_indicator
        assert result["source_information_instance_object_type"] == source_information_instance_object_type
        assert result["target_information_instance_object_type"] == target_information_instance_object_type

    def test_rel_to_json(self):
        seg = REL()

        seg.set_id_rel = set_id_rel
        seg.negation_indicator = negation_indicator
        seg.priority_no = priority_no
        seg.priority_sequence_no_rel_preference_for_consideration = priority_sequence_no_rel_preference_for_consideration
        seg.separability_indicator = separability_indicator
        seg.source_information_instance_object_type = source_information_instance_object_type
        seg.target_information_instance_object_type = target_information_instance_object_type

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "REL"
        assert result["set_id_rel"] == set_id_rel
        assert result["negation_indicator"] == negation_indicator
        assert result["priority_no"] == priority_no
        assert result["priority_sequence_no_rel_preference_for_consideration"] == priority_sequence_no_rel_preference_for_consideration
        assert result["separability_indicator"] == separability_indicator
        assert result["source_information_instance_object_type"] == source_information_instance_object_type
        assert result["target_information_instance_object_type"] == target_information_instance_object_type
