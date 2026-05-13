from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestSIUS12Cardinality:

    def test_siu_s12_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["SCH"] = 1
        segment_counts["PID"] = 1
        group_counts["SIU_S12.RESOURCES"] = 1
        segment_counts["RGS"] = 1
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        segment_counts["AIL"] = 1
        segment_counts["AIP"] = 1
        result = validate_cardinality("SIU_S12", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_siu_s12_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["SCH"] = 1
        segment_counts["PID"] = 1
        group_counts["SIU_S12.RESOURCES"] = 1
        segment_counts["RGS"] = 1
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        segment_counts["AIL"] = 1
        segment_counts["AIP"] = 1
        result = validate_cardinality("SIU_S12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_siu_s12_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["SCH"] = 1
        segment_counts["PID"] = 1
        group_counts["SIU_S12.RESOURCES"] = 1
        segment_counts["RGS"] = 1
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        segment_counts["AIL"] = 1
        segment_counts["AIP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("SIU_S12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestSRMS01Cardinality:

    def test_srm_s01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["ARQ"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        group_counts["SRM_S01.RESOURCES"] = 1
        segment_counts["RGS"] = 1
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        segment_counts["AIL"] = 1
        segment_counts["AIP"] = 1
        result = validate_cardinality("SRM_S01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_srm_s01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["ARQ"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        group_counts["SRM_S01.RESOURCES"] = 1
        segment_counts["RGS"] = 1
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        segment_counts["AIL"] = 1
        segment_counts["AIP"] = 1
        result = validate_cardinality("SRM_S01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_srm_s01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["ARQ"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        group_counts["SRM_S01.RESOURCES"] = 1
        segment_counts["RGS"] = 1
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        segment_counts["AIL"] = 1
        segment_counts["AIP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("SRM_S01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestSRRS01Cardinality:

    def test_srr_s01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["SCH"] = 1
        segment_counts["PID"] = 1
        group_counts["SRR_S01.RESOURCES"] = 1
        segment_counts["RGS"] = 1
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        segment_counts["AIL"] = 1
        segment_counts["AIP"] = 1
        result = validate_cardinality("SRR_S01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_srr_s01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["SCH"] = 1
        segment_counts["PID"] = 1
        group_counts["SRR_S01.RESOURCES"] = 1
        segment_counts["RGS"] = 1
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        segment_counts["AIL"] = 1
        segment_counts["AIP"] = 1
        result = validate_cardinality("SRR_S01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_srr_s01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["SCH"] = 1
        segment_counts["PID"] = 1
        group_counts["SRR_S01.RESOURCES"] = 1
        segment_counts["RGS"] = 1
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        segment_counts["AIL"] = 1
        segment_counts["AIP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("SRR_S01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
