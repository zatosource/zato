from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestBPSO29Cardinality:

    def test_bps_o29_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["BPS_O29.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["BPO"] = 1
        segment_counts["BPX"] = 1
        result = validate_cardinality("BPS_O29", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_bps_o29_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["BPS_O29.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["BPO"] = 1
        segment_counts["BPX"] = 1
        result = validate_cardinality("BPS_O29", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_bps_o29_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["BPS_O29.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["BPO"] = 1
        segment_counts["BPX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("BPS_O29", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestBRPO30Cardinality:

    def test_brp_o30_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        result = validate_cardinality("BRP_O30", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_brp_o30_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        result = validate_cardinality("BRP_O30", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_brp_o30_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("BRP_O30", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestBRTO32Cardinality:

    def test_brt_o32_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        result = validate_cardinality("BRT_O32", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_brt_o32_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        result = validate_cardinality("BRT_O32", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_brt_o32_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("BRT_O32", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestBTSO31Cardinality:

    def test_bts_o31_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["BTS_O31.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["BPO"] = 1
        segment_counts["BTX"] = 1
        result = validate_cardinality("BTS_O31", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_bts_o31_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["BTS_O31.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["BPO"] = 1
        segment_counts["BTX"] = 1
        result = validate_cardinality("BTS_O31", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_bts_o31_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["BTS_O31.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["BPO"] = 1
        segment_counts["BTX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("BTS_O31", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
