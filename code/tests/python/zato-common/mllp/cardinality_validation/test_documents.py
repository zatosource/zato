from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestMDMT01Cardinality:

    def test_mdm_t01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TXA"] = 1
        result = validate_cardinality("MDM_T01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mdm_t01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TXA"] = 1
        result = validate_cardinality("MDM_T01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mdm_t01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TXA"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MDM_T01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestMDMT02Cardinality:

    def test_mdm_t02_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TXA"] = 1
        group_counts["MDM_T02.OBSERVATION"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("MDM_T02", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_mdm_t02_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TXA"] = 1
        group_counts["MDM_T02.OBSERVATION"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("MDM_T02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_mdm_t02_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TXA"] = 1
        group_counts["MDM_T02.OBSERVATION"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("MDM_T02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
