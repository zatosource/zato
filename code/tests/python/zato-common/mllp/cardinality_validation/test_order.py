from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestOMBO27Cardinality:

    def test_omb_o27_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMB_O27.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["BPO"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OMB_O27", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_omb_o27_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMB_O27.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["BPO"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OMB_O27", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_omb_o27_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMB_O27.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["BPO"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OMB_O27", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOMDO03Cardinality:

    def test_omd_o03_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMD_O03.ORDER_DIET"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["ODS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["ODT"] = 1
        result = validate_cardinality("OMD_O03", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_omd_o03_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMD_O03.ORDER_DIET"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["ODS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["ODT"] = 1
        result = validate_cardinality("OMD_O03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_omd_o03_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMD_O03.ORDER_DIET"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["ODS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["ODT"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OMD_O03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOMGO19Cardinality:

    def test_omg_o19_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMG_O19.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OMG_O19.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["PRT"] = 1
        group_counts["OMG_O19.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OMG_O19", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_omg_o19_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMG_O19.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OMG_O19.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["PRT"] = 1
        group_counts["OMG_O19.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OMG_O19", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_omg_o19_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMG_O19.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OMG_O19.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["PRT"] = 1
        group_counts["OMG_O19.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OMG_O19", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOMIO23Cardinality:

    def test_omi_o23_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMI_O23.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["IPC"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OMI_O23", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_omi_o23_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMI_O23.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["IPC"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OMI_O23", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_omi_o23_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMI_O23.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["IPC"] = 1
        segment_counts["DEV"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OMI_O23", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOMLO21Cardinality:

    def test_oml_o21_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O21.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OML_O21.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OML_O21.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OML_O21", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_oml_o21_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O21.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OML_O21.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OML_O21.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OML_O21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_oml_o21_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O21.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OML_O21.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OML_O21.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OML_O21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOMLO33Cardinality:

    def test_oml_o33_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O33.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        group_counts["OML_O33.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OML_O33.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OML_O33.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OML_O33", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_oml_o33_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O33.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        group_counts["OML_O33.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OML_O33.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OML_O33.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OML_O33", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_oml_o33_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O33.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        group_counts["OML_O33.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OML_O33.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OML_O33.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OML_O33", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOMLO35Cardinality:

    def test_oml_o35_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O35.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        group_counts["OML_O35.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        group_counts["OML_O35.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OML_O35.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OML_O35.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OML_O35", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_oml_o35_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O35.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        group_counts["OML_O35.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        group_counts["OML_O35.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OML_O35.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OML_O35.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OML_O35", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_oml_o35_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O35.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        group_counts["OML_O35.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        group_counts["OML_O35.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OML_O35.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OML_O35.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OML_O35", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOMLO39Cardinality:

    def test_oml_o39_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O39.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SHP"] = 1
        segment_counts["OBX"] = 1
        group_counts["OML_O39.PACKAGE"] = 1
        segment_counts["PAC"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OML_O39", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_oml_o39_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O39.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SHP"] = 1
        segment_counts["OBX"] = 1
        group_counts["OML_O39.PACKAGE"] = 1
        segment_counts["PAC"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        result = validate_cardinality("OML_O39", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_oml_o39_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O39.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SHP"] = 1
        segment_counts["OBX"] = 1
        group_counts["OML_O39.PACKAGE"] = 1
        segment_counts["PAC"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["DEV"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OML_O39", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOMLO59Cardinality:

    def test_oml_o59_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O59.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OML_O59.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OML_O59.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OML_O59", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_oml_o59_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O59.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OML_O59.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OML_O59.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OML_O59", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_oml_o59_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OML_O59.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OML_O59.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OML_O59.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OML_O59", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOMNO07Cardinality:

    def test_omn_o07_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMN_O07.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RQD"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OMN_O07", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_omn_o07_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMN_O07.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RQD"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OMN_O07", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_omn_o07_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMN_O07.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RQD"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OMN_O07", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOMPO09Cardinality:

    def test_omp_o09_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PD1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMP_O09.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OMP_O09", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_omp_o09_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PD1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMP_O09.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OMP_O09", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_omp_o09_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PD1"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMP_O09.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OMP_O09", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOMQO57Cardinality:

    def test_omq_o57_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMQ_O57.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OMQ_O57.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["PRT"] = 1
        group_counts["OMQ_O57.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OMQ_O57", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_omq_o57_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMQ_O57.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OMQ_O57.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["PRT"] = 1
        group_counts["OMQ_O57.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OMQ_O57", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_omq_o57_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMQ_O57.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["TXA"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OMQ_O57.ORDER_PRIOR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["PRT"] = 1
        group_counts["OMQ_O57.OBSERVATION_PRIOR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OMQ_O57", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOMSO05Cardinality:

    def test_oms_o05_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMS_O05.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RQD"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OMS_O05", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_oms_o05_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMS_O05.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RQD"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OMS_O05", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_oms_o05_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["OMS_O05.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RQD"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OMS_O05", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOPLO37Cardinality:

    def test_opl_o37_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PRT"] = 1
        segment_counts["GT1"] = 1
        group_counts["OPL_O37.ORDER"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["IN1"] = 1
        group_counts["OPL_O37.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        group_counts["OPL_O37.OBSERVATION_REQUEST"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OPL_O37.ORDER_PRIOR"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OPL_O37.OBSERVATION_RESULT_GROUP"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OPL_O37", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_opl_o37_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PRT"] = 1
        segment_counts["GT1"] = 1
        group_counts["OPL_O37.ORDER"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["IN1"] = 1
        group_counts["OPL_O37.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        group_counts["OPL_O37.OBSERVATION_REQUEST"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OPL_O37.ORDER_PRIOR"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OPL_O37.OBSERVATION_RESULT_GROUP"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OPL_O37", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_opl_o37_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PRT"] = 1
        segment_counts["GT1"] = 1
        group_counts["OPL_O37.ORDER"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["IN1"] = 1
        group_counts["OPL_O37.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        group_counts["OPL_O37.OBSERVATION_REQUEST"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        group_counts["OPL_O37.ORDER_PRIOR"] = 1
        segment_counts["OBR"] = 1
        segment_counts["PRT"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OPL_O37.OBSERVATION_RESULT_GROUP"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OPL_O37", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOPRO38Cardinality:

    def test_opr_o38_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["OPR_O38.ORDER"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PID"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        result = validate_cardinality("OPR_O38", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_opr_o38_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        group_counts["OPR_O38.ORDER"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PID"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        result = validate_cardinality("OPR_O38", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_opr_o38_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["OPR_O38.ORDER"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PID"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OPR_O38", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOPUR25Cardinality:

    def test_opu_r25_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        group_counts["OPU_R25.ACCESSION_DETAIL"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        group_counts["OPU_R25.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        group_counts["OPU_R25.ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OPU_R25.RESULT"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OPU_R25", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_opu_r25_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        group_counts["OPU_R25.ACCESSION_DETAIL"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        group_counts["OPU_R25.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        group_counts["OPU_R25.ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OPU_R25.RESULT"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OPU_R25", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_opu_r25_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        group_counts["OPU_R25.ACCESSION_DETAIL"] = 1
        segment_counts["NK1"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        group_counts["OPU_R25.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        group_counts["OPU_R25.ORDER"] = 1
        segment_counts["OBR"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        group_counts["OPU_R25.RESULT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OPU_R25", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORAR33Cardinality:

    def test_ora_r33_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["ORC"] = 1
        result = validate_cardinality("ORA_R33", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ora_r33_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["ORC"] = 1
        result = validate_cardinality("ORA_R33", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ora_r33_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["ORC"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORA_R33", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORAR41Cardinality:

    def test_ora_r41_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        result = validate_cardinality("ORA_R41", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ora_r41_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        result = validate_cardinality("ORA_R41", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ora_r41_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORA_R41", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORBO28Cardinality:

    def test_orb_o28_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        result = validate_cardinality("ORB_O28", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_orb_o28_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        result = validate_cardinality("ORB_O28", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_orb_o28_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORB_O28", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORDO04Cardinality:

    def test_ord_o04_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORD_O04.ORDER_DIET"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        result = validate_cardinality("ORD_O04", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ord_o04_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORD_O04.ORDER_DIET"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        result = validate_cardinality("ORD_O04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ord_o04_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORD_O04.ORDER_DIET"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORD_O04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORGO20Cardinality:

    def test_org_o20_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORG_O20.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SPM"] = 1
        result = validate_cardinality("ORG_O20", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_org_o20_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORG_O20.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SPM"] = 1
        result = validate_cardinality("ORG_O20", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_org_o20_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORG_O20.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SPM"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORG_O20", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORIO24Cardinality:

    def test_ori_o24_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORI_O24.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["IPC"] = 1
        result = validate_cardinality("ORI_O24", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ori_o24_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORI_O24.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["IPC"] = 1
        result = validate_cardinality("ORI_O24", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ori_o24_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORI_O24.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["IPC"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORI_O24", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORLO22Cardinality:

    def test_orl_o22_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SPM"] = 1
        result = validate_cardinality("ORL_O22", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_orl_o22_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SPM"] = 1
        result = validate_cardinality("ORL_O22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_orl_o22_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SPM"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORL_O22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORLO34Cardinality:

    def test_orl_o34_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORL_O34.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("ORL_O34", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_orl_o34_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORL_O34.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("ORL_O34", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_orl_o34_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORL_O34.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORL_O34", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORLO36Cardinality:

    def test_orl_o36_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORL_O36.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        group_counts["ORL_O36.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("ORL_O36", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_orl_o36_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORL_O36.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        group_counts["ORL_O36.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("ORL_O36", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_orl_o36_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORL_O36.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        group_counts["ORL_O36.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORL_O36", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORLO40Cardinality:

    def test_orl_o40_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SHP"] = 1
        group_counts["ORL_O40.PACKAGE"] = 1
        segment_counts["PAC"] = 1
        segment_counts["SPM"] = 1
        segment_counts["SAC"] = 1
        result = validate_cardinality("ORL_O40", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_orl_o40_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SHP"] = 1
        group_counts["ORL_O40.PACKAGE"] = 1
        segment_counts["PAC"] = 1
        segment_counts["SPM"] = 1
        segment_counts["SAC"] = 1
        result = validate_cardinality("ORL_O40", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_orl_o40_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SHP"] = 1
        group_counts["ORL_O40.PACKAGE"] = 1
        segment_counts["PAC"] = 1
        segment_counts["SPM"] = 1
        segment_counts["SAC"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORL_O40", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORLO53Cardinality:

    def test_orl_o53_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SPM"] = 1
        result = validate_cardinality("ORL_O53", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_orl_o53_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SPM"] = 1
        result = validate_cardinality("ORL_O53", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_orl_o53_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SPM"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORL_O53", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORLO54Cardinality:

    def test_orl_o54_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORL_O54.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("ORL_O54", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_orl_o54_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORL_O54.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("ORL_O54", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_orl_o54_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORL_O54.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORL_O54", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORLO55Cardinality:

    def test_orl_o55_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORL_O55.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        group_counts["ORL_O55.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("ORL_O55", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_orl_o55_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORL_O55.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        group_counts["ORL_O55.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        result = validate_cardinality("ORL_O55", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_orl_o55_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORL_O55.SPECIMEN"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        group_counts["ORL_O55.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORL_O55", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORLO56Cardinality:

    def test_orl_o56_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SHP"] = 1
        group_counts["ORL_O56.PACKAGE"] = 1
        segment_counts["PAC"] = 1
        segment_counts["SPM"] = 1
        segment_counts["SAC"] = 1
        result = validate_cardinality("ORL_O56", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_orl_o56_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SHP"] = 1
        group_counts["ORL_O56.PACKAGE"] = 1
        segment_counts["PAC"] = 1
        segment_counts["SPM"] = 1
        segment_counts["SAC"] = 1
        result = validate_cardinality("ORL_O56", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_orl_o56_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBR"] = 1
        segment_counts["SHP"] = 1
        group_counts["ORL_O56.PACKAGE"] = 1
        segment_counts["PAC"] = 1
        segment_counts["SPM"] = 1
        segment_counts["SAC"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORL_O56", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORMO01Cardinality:

    def test_orm_o01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["ORM_O01.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ORM_O01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_orm_o01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["ORM_O01.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("ORM_O01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_orm_o01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["IN1"] = 1
        group_counts["ORM_O01.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORM_O01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORNO08Cardinality:

    def test_orn_o08_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORN_O08.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RQD"] = 1
        result = validate_cardinality("ORN_O08", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_orn_o08_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORN_O08.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RQD"] = 1
        result = validate_cardinality("ORN_O08", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_orn_o08_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORN_O08.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RQD"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORN_O08", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORPO10Cardinality:

    def test_orp_o10_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORP_O10.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        result = validate_cardinality("ORP_O10", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_orp_o10_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORP_O10.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        result = validate_cardinality("ORP_O10", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_orp_o10_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORP_O10.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["RXC"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORP_O10", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORSO06Cardinality:

    def test_ors_o06_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORS_O06.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RQD"] = 1
        result = validate_cardinality("ORS_O06", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ors_o06_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORS_O06.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RQD"] = 1
        result = validate_cardinality("ORS_O06", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ors_o06_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORS_O06.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["RQD"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORS_O06", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestORXO58Cardinality:

    def test_orx_o58_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORX_O58.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TXA"] = 1
        result = validate_cardinality("ORX_O58", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_orx_o58_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORX_O58.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TXA"] = 1
        result = validate_cardinality("ORX_O58", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_orx_o58_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["ORX_O58.ORDER"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TXA"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ORX_O58", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOSMR26Cardinality:

    def test_osm_r26_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["OSM_R26.SHIPMENT"] = 1
        segment_counts["SHP"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        group_counts["OSM_R26.PACKAGE"] = 1
        segment_counts["PAC"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OSM_R26", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_osm_r26_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        group_counts["OSM_R26.SHIPMENT"] = 1
        segment_counts["SHP"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        group_counts["OSM_R26.PACKAGE"] = 1
        segment_counts["PAC"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        result = validate_cardinality("OSM_R26", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_osm_r26_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["OSM_R26.SHIPMENT"] = 1
        segment_counts["SHP"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        group_counts["OSM_R26.PACKAGE"] = 1
        segment_counts["PAC"] = 1
        segment_counts["SPM"] = 1
        segment_counts["OBX"] = 1
        segment_counts["SAC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PID"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["OBX"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OSM_R26", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOSUO51Cardinality:

    def test_osu_o51_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["OSU_O51.ORDER_STATUS"] = 1
        segment_counts["ORC"] = 1
        result = validate_cardinality("OSU_O51", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_osu_o51_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        group_counts["OSU_O51.ORDER_STATUS"] = 1
        segment_counts["ORC"] = 1
        result = validate_cardinality("OSU_O51", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_osu_o51_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["OSU_O51.ORDER_STATUS"] = 1
        segment_counts["ORC"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OSU_O51", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestOSUO52Cardinality:

    def test_osu_o52_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["OSU_O52.ORDER_STATUS"] = 1
        segment_counts["ORC"] = 1
        result = validate_cardinality("OSU_O52", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_osu_o52_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["OSU_O52.ORDER_STATUS"] = 1
        segment_counts["ORC"] = 1
        result = validate_cardinality("OSU_O52", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_osu_o52_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        group_counts["OSU_O52.ORDER_STATUS"] = 1
        segment_counts["ORC"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("OSU_O52", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
