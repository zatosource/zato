from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestORUR01Cardinality:

    def test_oru_r01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["ORU_R01.PATIENT_RESULT"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["ORU_R01.ORDER_OBSERVATION"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("ORU_R01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_oru_r01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        group_counts["ORU_R01.PATIENT_RESULT"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["ORU_R01.ORDER_OBSERVATION"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("ORU_R01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_oru_r01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["ORU_R01.PATIENT_RESULT"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["ORU_R01.ORDER_OBSERVATION"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORU_R01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORUR30Cardinality:

    def test_oru_r30_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        group_counts["ORU_R30.OBSERVATION"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("ORU_R30", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_oru_r30_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        group_counts["ORU_R30.OBSERVATION"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("ORU_R30", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_oru_r30_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        group_counts["ORU_R30.OBSERVATION"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORU_R30", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOULR22Cardinality:

    def test_oul_r22_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["OUL_R22.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        group_counts["OUL_R22.ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OUL_R22", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_oul_r22_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["OUL_R22.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        group_counts["OUL_R22.ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OUL_R22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_oul_r22_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["OUL_R22.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        group_counts["OUL_R22.ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OUL_R22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOULR23Cardinality:

    def test_oul_r23_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["OUL_R23.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        group_counts["OUL_R23.CONTAINER"] = 1
        segment_counts["SAC"] = 1
        group_counts["OUL_R23.ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OUL_R23", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_oul_r23_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["OUL_R23.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        group_counts["OUL_R23.CONTAINER"] = 1
        segment_counts["SAC"] = 1
        group_counts["OUL_R23.ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OUL_R23", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_oul_r23_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["OUL_R23.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        group_counts["OUL_R23.CONTAINER"] = 1
        segment_counts["SAC"] = 1
        group_counts["OUL_R23.ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OUL_R23", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOULR24Cardinality:

    def test_oul_r24_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["OUL_R24.ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OUL_R24", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_oul_r24_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["OUL_R24.ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OUL_R24", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_oul_r24_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        group_counts["OUL_R24.ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OUL_R24", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
