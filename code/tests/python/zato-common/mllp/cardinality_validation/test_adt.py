from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestADTA01Cardinality:

    def test_adt_a01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["RF1"] = 1
        result = validate_cardinality("ADT_A01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["RF1"] = 1
        result = validate_cardinality("ADT_A01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["RF1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA02Cardinality:

    def test_adt_a02_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A02", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a02_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a02_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA03Cardinality:

    def test_adt_a03_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["IN1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["RF1"] = 1
        result = validate_cardinality("ADT_A03", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a03_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["IN1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["RF1"] = 1
        result = validate_cardinality("ADT_A03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a03_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["IN1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["RF1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA05Cardinality:

    def test_adt_a05_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["RF1"] = 1
        result = validate_cardinality("ADT_A05", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a05_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["RF1"] = 1
        result = validate_cardinality("ADT_A05", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a05_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["RF1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A05", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA06Cardinality:

    def test_adt_a06_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("ADT_A06", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a06_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("ADT_A06", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a06_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A06", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA09Cardinality:

    def test_adt_a09_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A09", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a09_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A09", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a09_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A09", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA12Cardinality:

    def test_adt_a12_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A12", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a12_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a12_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA15Cardinality:

    def test_adt_a15_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A15", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a15_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a15_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A15", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA16Cardinality:

    def test_adt_a16_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["RF1"] = 1
        result = validate_cardinality("ADT_A16", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a16_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["RF1"] = 1
        result = validate_cardinality("ADT_A16", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a16_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["RF1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A16", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA17Cardinality:

    def test_adt_a17_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A17", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a17_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A17", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a17_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A17", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA20Cardinality:

    def test_adt_a20_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["NPU"] = 1
        result = validate_cardinality("ADT_A20", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a20_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["NPU"] = 1
        result = validate_cardinality("ADT_A20", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a20_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["NPU"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A20", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA21Cardinality:

    def test_adt_a21_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A21", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a21_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a21_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA24Cardinality:

    def test_adt_a24_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("ADT_A24", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a24_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("ADT_A24", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a24_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PID"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A24", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA37Cardinality:

    def test_adt_a37_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("ADT_A37", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a37_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("ADT_A37", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a37_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PID"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A37", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA38Cardinality:

    def test_adt_a38_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A38", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a38_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ADT_A38", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a38_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A38", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA39Cardinality:

    def test_adt_a39_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        group_counts["ADT_A39.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["MRG"] = 1
        result = validate_cardinality("ADT_A39", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a39_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        group_counts["ADT_A39.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["MRG"] = 1
        result = validate_cardinality("ADT_A39", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a39_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        group_counts["ADT_A39.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["MRG"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A39", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA43Cardinality:

    def test_adt_a43_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        group_counts["ADT_A43.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["MRG"] = 1
        result = validate_cardinality("ADT_A43", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a43_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        group_counts["ADT_A43.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["MRG"] = 1
        result = validate_cardinality("ADT_A43", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a43_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        group_counts["ADT_A43.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["MRG"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A43", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA44Cardinality:

    def test_adt_a44_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        group_counts["ADT_A44.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["MRG"] = 1
        result = validate_cardinality("ADT_A44", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a44_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        group_counts["ADT_A44.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["MRG"] = 1
        result = validate_cardinality("ADT_A44", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a44_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        group_counts["ADT_A44.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["MRG"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A44", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA45Cardinality:

    def test_adt_a45_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        group_counts["ADT_A45.MERGE_INFO"] = 1
        segment_counts["MRG"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("ADT_A45", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a45_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        group_counts["ADT_A45.MERGE_INFO"] = 1
        segment_counts["MRG"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("ADT_A45", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a45_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        group_counts["ADT_A45.MERGE_INFO"] = 1
        segment_counts["MRG"] = 1
        segment_counts["PV1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A45", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA50Cardinality:

    def test_adt_a50_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["MRG"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("ADT_A50", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a50_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["MRG"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("ADT_A50", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a50_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["MRG"] = 1
        segment_counts["PV1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A50", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA52Cardinality:

    def test_adt_a52_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("ADT_A52", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a52_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("ADT_A52", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a52_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A52", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA54Cardinality:

    def test_adt_a54_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("ADT_A54", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a54_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("ADT_A54", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a54_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A54", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA60Cardinality:

    def test_adt_a60_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IAM"] = 1
        result = validate_cardinality("ADT_A60", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a60_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IAM"] = 1
        result = validate_cardinality("ADT_A60", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a60_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IAM"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A60", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestADTA61Cardinality:

    def test_adt_a61_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("ADT_A61", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_adt_a61_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("ADT_A61", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_adt_a61_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ADT_A61", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
