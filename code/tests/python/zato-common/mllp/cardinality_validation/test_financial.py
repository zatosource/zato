from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestBARP01Cardinality:

    def test_bar_p01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        group_counts["BAR_P01.VISIT"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DG1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("BAR_P01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_bar_p01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        group_counts["BAR_P01.VISIT"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DG1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("BAR_P01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_bar_p01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        group_counts["BAR_P01.VISIT"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DG1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("BAR_P01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestBARP02Cardinality:

    def test_bar_p02_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        group_counts["BAR_P02.PATIENT"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("BAR_P02", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_bar_p02_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        group_counts["BAR_P02.PATIENT"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("BAR_P02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_bar_p02_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        group_counts["BAR_P02.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("BAR_P02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestBARP05Cardinality:

    def test_bar_p05_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        group_counts["BAR_P05.VISIT"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DG1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("BAR_P05", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_bar_p05_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        group_counts["BAR_P05.VISIT"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DG1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("BAR_P05", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_bar_p05_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        group_counts["BAR_P05.VISIT"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DG1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("BAR_P05", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestBARP06Cardinality:

    def test_bar_p06_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        group_counts["BAR_P06.PATIENT"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("BAR_P06", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_bar_p06_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        group_counts["BAR_P06.PATIENT"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("BAR_P06", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_bar_p06_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        group_counts["BAR_P06.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("BAR_P06", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestBARP10Cardinality:

    def test_bar_p10_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DG1"] = 1
        segment_counts["GP1"] = 1
        segment_counts["PR1"] = 1
        result = validate_cardinality("BAR_P10", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_bar_p10_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DG1"] = 1
        segment_counts["GP1"] = 1
        segment_counts["PR1"] = 1
        result = validate_cardinality("BAR_P10", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_bar_p10_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DG1"] = 1
        segment_counts["GP1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("BAR_P10", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestBARP12Cardinality:

    def test_bar_p12_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DG1"] = 1
        segment_counts["PR1"] = 1
        result = validate_cardinality("BAR_P12", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_bar_p12_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DG1"] = 1
        segment_counts["PR1"] = 1
        result = validate_cardinality("BAR_P12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_bar_p12_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["DG1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("BAR_P12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestDFTP03Cardinality:

    def test_dft_p03_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        group_counts["DFT_P03.FINANCIAL"] = 1
        segment_counts["FT1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["NTE"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DG1"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("DFT_P03", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_dft_p03_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        group_counts["DFT_P03.FINANCIAL"] = 1
        segment_counts["FT1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["NTE"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DG1"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("DFT_P03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_dft_p03_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        group_counts["DFT_P03.FINANCIAL"] = 1
        segment_counts["FT1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["NTE"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DG1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("DFT_P03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestDFTP11Cardinality:

    def test_dft_p11_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DG1"] = 1
        segment_counts["IN1"] = 1
        group_counts["DFT_P11.FINANCIAL"] = 1
        segment_counts["FT1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DG1"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("DFT_P11", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_dft_p11_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DG1"] = 1
        segment_counts["IN1"] = 1
        group_counts["DFT_P11.FINANCIAL"] = 1
        segment_counts["FT1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DG1"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("DFT_P11", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_dft_p11_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EVN"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DG1"] = 1
        segment_counts["IN1"] = 1
        group_counts["DFT_P11.FINANCIAL"] = 1
        segment_counts["FT1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DG1"] = 1
        segment_counts["IN1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("DFT_P11", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
