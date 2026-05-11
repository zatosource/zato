from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestVXUV04Cardinality:

    def test_vxu_v04_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXA"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("VXU_V04", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_vxu_v04_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXA"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("VXU_V04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_vxu_v04_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXA"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("VXU_V04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
