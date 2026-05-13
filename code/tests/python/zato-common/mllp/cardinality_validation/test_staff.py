from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestPMUB01Cardinality:

    def test_pmu_b01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        result = validate_cardinality("PMU_B01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_pmu_b01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        result = validate_cardinality("PMU_B01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_pmu_b01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("PMU_B01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestPMUB03Cardinality:

    def test_pmu_b03_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        result = validate_cardinality("PMU_B03", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_pmu_b03_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        result = validate_cardinality("PMU_B03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_pmu_b03_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("PMU_B03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestPMUB04Cardinality:

    def test_pmu_b04_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        result = validate_cardinality("PMU_B04", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_pmu_b04_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        result = validate_cardinality("PMU_B04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_pmu_b04_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("PMU_B04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestPMUB07Cardinality:

    def test_pmu_b07_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        segment_counts["CER"] = 1
        result = validate_cardinality("PMU_B07", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_pmu_b07_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        segment_counts["CER"] = 1
        result = validate_cardinality("PMU_B07", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_pmu_b07_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        segment_counts["CER"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("PMU_B07", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestPMUB08Cardinality:

    def test_pmu_b08_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        result = validate_cardinality("PMU_B08", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_pmu_b08_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        result = validate_cardinality("PMU_B08", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_pmu_b08_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["STF"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("PMU_B08", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
