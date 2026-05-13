from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestCCFI22Cardinality:

    def test_ccf_i22_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("CCF_I22", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ccf_i22_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        result = validate_cardinality("CCF_I22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ccf_i22_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("CCF_I22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestCCII22Cardinality:

    def test_cci_i22_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCI_I22.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["AIS"] = 1
        choice_children["CCI_I22.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CCI_I22.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        result = validate_cardinality("CCI_I22", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_cci_i22_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCI_I22.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["AIS"] = 1
        choice_children["CCI_I22.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CCI_I22.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        result = validate_cardinality("CCI_I22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_cci_i22_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCI_I22.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["AIS"] = 1
        choice_children["CCI_I22.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CCI_I22.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("CCI_I22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_cci_i22_choice_none_cci_i22_resource_object(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCI_I22.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["CCI_I22.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        group_counts["CCI_I22.RESOURCE_OBJECT"] = 1
        result = validate_cardinality("CCI_I22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_cci_i22_choice_multiple_cci_i22_resource_object(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCI_I22.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["CCI_I22.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCI_I22.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        choice_children["CCI_I22.RESOURCE_OBJECT"] = ["AIS", "AIG"]
        result = validate_cardinality("CCI_I22", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestCCMI21Cardinality:

    def test_ccm_i21_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCM_I21.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["AIS"] = 1
        choice_children["CCM_I21.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CCM_I21.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["PRT"] = 1
        choice_children["CCM_I21.PARTICIPATION_PATHWAY_OBJECT"] = ["PRT"]
        result = validate_cardinality("CCM_I21", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ccm_i21_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCM_I21.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["AIS"] = 1
        choice_children["CCM_I21.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CCM_I21.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["PRT"] = 1
        choice_children["CCM_I21.PARTICIPATION_PATHWAY_OBJECT"] = ["PRT"]
        result = validate_cardinality("CCM_I21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ccm_i21_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCM_I21.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["AIS"] = 1
        choice_children["CCM_I21.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CCM_I21.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["PRT"] = 1
        choice_children["CCM_I21.PARTICIPATION_PATHWAY_OBJECT"] = ["PRT"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("CCM_I21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_ccm_i21_choice_none_ccm_i21_resource_object(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCM_I21.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["CCM_I21.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["PRT"] = 1
        choice_children["CCM_I21.PARTICIPATION_PATHWAY_OBJECT"] = ["PRT"]
        group_counts["CCM_I21.RESOURCE_OBJECT"] = 1
        result = validate_cardinality("CCM_I21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_ccm_i21_choice_multiple_ccm_i21_resource_object(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCM_I21.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["CCM_I21.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCM_I21.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["PRT"] = 1
        choice_children["CCM_I21.PARTICIPATION_PATHWAY_OBJECT"] = ["PRT"]
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        choice_children["CCM_I21.RESOURCE_OBJECT"] = ["AIS", "AIG"]
        result = validate_cardinality("CCM_I21", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestCCQI19Cardinality:

    def test_ccq_i19_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["RF1"] = 1
        segment_counts["PRD"] = 1
        result = validate_cardinality("CCQ_I19", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ccq_i19_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["RF1"] = 1
        segment_counts["PRD"] = 1
        result = validate_cardinality("CCQ_I19", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ccq_i19_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["RF1"] = 1
        segment_counts["PRD"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("CCQ_I19", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestCCRI16Cardinality:

    def test_ccr_i16_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["RF1"] = 1
        group_counts["CCR_I16.PROVIDER_CONTACT"] = 1
        segment_counts["PRD"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        group_counts["CCR_I16.CLINICAL_ORDER_DETAIL"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCR_I16.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCR_I16.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["CCR_I16.CLINICAL_ORDER_OBJECT"] = ["OBR"]
        segment_counts["AIS"] = 1
        choice_children["CCR_I16.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CCR_I16.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        result = validate_cardinality("CCR_I16", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ccr_i16_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["RF1"] = 1
        group_counts["CCR_I16.PROVIDER_CONTACT"] = 1
        segment_counts["PRD"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        group_counts["CCR_I16.CLINICAL_ORDER_DETAIL"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCR_I16.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCR_I16.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["CCR_I16.CLINICAL_ORDER_OBJECT"] = ["OBR"]
        segment_counts["AIS"] = 1
        choice_children["CCR_I16.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CCR_I16.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        result = validate_cardinality("CCR_I16", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ccr_i16_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["RF1"] = 1
        group_counts["CCR_I16.PROVIDER_CONTACT"] = 1
        segment_counts["PRD"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        group_counts["CCR_I16.CLINICAL_ORDER_DETAIL"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCR_I16.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCR_I16.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["CCR_I16.CLINICAL_ORDER_OBJECT"] = ["OBR"]
        segment_counts["AIS"] = 1
        choice_children["CCR_I16.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CCR_I16.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("CCR_I16", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_ccr_i16_choice_none_ccr_i16_resource_object(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["RF1"] = 1
        group_counts["CCR_I16.PROVIDER_CONTACT"] = 1
        segment_counts["PRD"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        group_counts["CCR_I16.CLINICAL_ORDER_DETAIL"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCR_I16.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCR_I16.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["CCR_I16.CLINICAL_ORDER_OBJECT"] = ["OBR"]
        segment_counts["OBR"] = 1
        choice_children["CCR_I16.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        group_counts["CCR_I16.RESOURCE_OBJECT"] = 1
        result = validate_cardinality("CCR_I16", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_ccr_i16_choice_multiple_ccr_i16_resource_object(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["RF1"] = 1
        group_counts["CCR_I16.PROVIDER_CONTACT"] = 1
        segment_counts["PRD"] = 1
        segment_counts["ORC"] = 1
        segment_counts["TQ1"] = 1
        group_counts["CCR_I16.CLINICAL_ORDER_DETAIL"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCR_I16.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCR_I16.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["CCR_I16.CLINICAL_ORDER_OBJECT"] = ["OBR"]
        segment_counts["OBR"] = 1
        choice_children["CCR_I16.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCR_I16.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        choice_children["CCR_I16.RESOURCE_OBJECT"] = ["AIS", "AIG"]
        result = validate_cardinality("CCR_I16", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestCCUI20Cardinality:

    def test_ccu_i20_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["RF1"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCU_I20.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["AIS"] = 1
        choice_children["CCU_I20.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CCU_I20.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        result = validate_cardinality("CCU_I20", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ccu_i20_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["RF1"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCU_I20.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["AIS"] = 1
        choice_children["CCU_I20.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CCU_I20.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        result = validate_cardinality("CCU_I20", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ccu_i20_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["RF1"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCU_I20.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["AIS"] = 1
        choice_children["CCU_I20.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CCU_I20.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("CCU_I20", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_ccu_i20_choice_none_ccu_i20_resource_object(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["RF1"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCU_I20.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["CCU_I20.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        group_counts["CCU_I20.RESOURCE_OBJECT"] = 1
        result = validate_cardinality("CCU_I20", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_ccu_i20_choice_multiple_ccu_i20_resource_object(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["RF1"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CCU_I20.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["CCU_I20.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CCU_I20.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        choice_children["CCU_I20.RESOURCE_OBJECT"] = ["AIS", "AIG"]
        result = validate_cardinality("CCU_I20", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestCQUI19Cardinality:

    def test_cqu_i19_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["RF1"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CQU_I19.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["AIS"] = 1
        choice_children["CQU_I19.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CQU_I19.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        result = validate_cardinality("CQU_I19", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_cqu_i19_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["RF1"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CQU_I19.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["AIS"] = 1
        choice_children["CQU_I19.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CQU_I19.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        result = validate_cardinality("CQU_I19", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_cqu_i19_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["RF1"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CQU_I19.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["AIS"] = 1
        choice_children["CQU_I19.RESOURCE_OBJECT"] = ["AIS"]
        segment_counts["OBR"] = 1
        choice_children["CQU_I19.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("CQU_I19", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_cqu_i19_choice_none_cqu_i19_resource_object(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["RF1"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CQU_I19.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["CQU_I19.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        group_counts["CQU_I19.RESOURCE_OBJECT"] = 1
        result = validate_cardinality("CQU_I19", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_cqu_i19_choice_multiple_cqu_i19_resource_object(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["RF1"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["SCH"] = 1
        segment_counts["RGS"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["CQU_I19.PATIENT_VISITS"] = 1
        segment_counts["PV1"] = 1
        segment_counts["ORC"] = 1
        segment_counts["RXO"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXE"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["CQU_I19.CLINICAL_HISTORY_OBJECT"] = ["OBR"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_CLINICAL_HISTORY_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_PROBLEM_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_GOAL_OBJECT"] = ["ROL"]
        segment_counts["ROL"] = 1
        choice_children["CQU_I19.PARTICIPATION_PATHWAY_OBJECT"] = ["ROL"]
        segment_counts["AIS"] = 1
        segment_counts["AIG"] = 1
        choice_children["CQU_I19.RESOURCE_OBJECT"] = ["AIS", "AIG"]
        result = validate_cardinality("CQU_I19", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestCRMC01Cardinality:

    def test_crm_c01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["CRM_C01.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["CSR"] = 1
        result = validate_cardinality("CRM_C01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_crm_c01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        group_counts["CRM_C01.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["CSR"] = 1
        result = validate_cardinality("CRM_C01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_crm_c01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["CRM_C01.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["CSR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("CRM_C01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestCSUC09Cardinality:

    def test_csu_c09_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["CSU_C09.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["CSR"] = 1
        group_counts["CSU_C09.STUDY_PHASE"] = 1
        group_counts["CSU_C09.STUDY_SCHEDULE"] = 1
        group_counts["CSU_C09.STUDY_OBSERVATION"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        group_counts["CSU_C09.STUDY_PHARM"] = 1
        segment_counts["ORC"] = 1
        group_counts["CSU_C09.RX_ADMIN"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("CSU_C09", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_csu_c09_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        group_counts["CSU_C09.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["CSR"] = 1
        group_counts["CSU_C09.STUDY_PHASE"] = 1
        group_counts["CSU_C09.STUDY_SCHEDULE"] = 1
        group_counts["CSU_C09.STUDY_OBSERVATION"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        group_counts["CSU_C09.STUDY_PHARM"] = 1
        segment_counts["ORC"] = 1
        group_counts["CSU_C09.RX_ADMIN"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        result = validate_cardinality("CSU_C09", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_csu_c09_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["CSU_C09.PATIENT"] = 1
        segment_counts["PID"] = 1
        segment_counts["PV1"] = 1
        segment_counts["CSR"] = 1
        group_counts["CSU_C09.STUDY_PHASE"] = 1
        group_counts["CSU_C09.STUDY_SCHEDULE"] = 1
        group_counts["CSU_C09.STUDY_OBSERVATION"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBR"] = 1
        segment_counts["TQ1"] = 1
        segment_counts["OBX"] = 1
        group_counts["CSU_C09.STUDY_PHARM"] = 1
        segment_counts["ORC"] = 1
        group_counts["CSU_C09.RX_ADMIN"] = 1
        segment_counts["RXA"] = 1
        segment_counts["RXR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("CSU_C09", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestPGLPC6Cardinality:

    def test_pgl_pc6_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PGL_PC6.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PGL_PC6.GOAL"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["PGL_PC6.CHOICE"] = ["OBR"]
        result = validate_cardinality("PGL_PC6", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_pgl_pc6_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        group_counts["PGL_PC6.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PGL_PC6.GOAL"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["PGL_PC6.CHOICE"] = ["OBR"]
        result = validate_cardinality("PGL_PC6", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_pgl_pc6_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PGL_PC6.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PGL_PC6.GOAL"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["PGL_PC6.CHOICE"] = ["OBR"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("PGL_PC6", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_pgl_pc6_choice_none_pgl_pc6_choice(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PGL_PC6.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PGL_PC6.GOAL"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["PGL_PC6.CHOICE"] = 1
        result = validate_cardinality("PGL_PC6", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_pgl_pc6_choice_multiple_pgl_pc6_choice(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PGL_PC6.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PGL_PC6.GOAL"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        segment_counts["anyHL7Segment"] = 1
        choice_children["PGL_PC6.CHOICE"] = ["OBR", "anyHL7Segment"]
        result = validate_cardinality("PGL_PC6", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestPPGPCGCardinality:

    def test_ppg_pcg_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PPG_PCG.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPG_PCG.PATHWAY"] = 1
        segment_counts["PTH"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["PPG_PCG.CHOICE"] = ["OBR"]
        result = validate_cardinality("PPG_PCG", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ppg_pcg_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        group_counts["PPG_PCG.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPG_PCG.PATHWAY"] = 1
        segment_counts["PTH"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["PPG_PCG.CHOICE"] = ["OBR"]
        result = validate_cardinality("PPG_PCG", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ppg_pcg_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PPG_PCG.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPG_PCG.PATHWAY"] = 1
        segment_counts["PTH"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["PPG_PCG.CHOICE"] = ["OBR"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("PPG_PCG", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_ppg_pcg_choice_none_ppg_pcg_choice(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PPG_PCG.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPG_PCG.PATHWAY"] = 1
        segment_counts["PTH"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["PPG_PCG.CHOICE"] = 1
        result = validate_cardinality("PPG_PCG", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_ppg_pcg_choice_multiple_ppg_pcg_choice(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PPG_PCG.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPG_PCG.PATHWAY"] = 1
        segment_counts["PTH"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        segment_counts["anyHL7Segment"] = 1
        choice_children["PPG_PCG.CHOICE"] = ["OBR", "anyHL7Segment"]
        result = validate_cardinality("PPG_PCG", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestPPPPCBCardinality:

    def test_ppp_pcb_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PPP_PCB.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPP_PCB.PATHWAY"] = 1
        segment_counts["PTH"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["PPP_PCB.CHOICE"] = ["OBR"]
        result = validate_cardinality("PPP_PCB", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ppp_pcb_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        group_counts["PPP_PCB.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPP_PCB.PATHWAY"] = 1
        segment_counts["PTH"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["PPP_PCB.CHOICE"] = ["OBR"]
        result = validate_cardinality("PPP_PCB", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ppp_pcb_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PPP_PCB.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPP_PCB.PATHWAY"] = 1
        segment_counts["PTH"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["PPP_PCB.CHOICE"] = ["OBR"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("PPP_PCB", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_ppp_pcb_choice_none_ppp_pcb_choice(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PPP_PCB.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPP_PCB.PATHWAY"] = 1
        segment_counts["PTH"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["PPP_PCB.CHOICE"] = 1
        result = validate_cardinality("PPP_PCB", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_ppp_pcb_choice_multiple_ppp_pcb_choice(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PPP_PCB.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPP_PCB.PATHWAY"] = 1
        segment_counts["PTH"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        segment_counts["anyHL7Segment"] = 1
        choice_children["PPP_PCB.CHOICE"] = ["OBR", "anyHL7Segment"]
        result = validate_cardinality("PPP_PCB", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)

class TestPPRPC1Cardinality:

    def test_ppr_pc1_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PPR_PC1.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPR_PC1.PROBLEM"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["PPR_PC1.CHOICE"] = ["OBR"]
        result = validate_cardinality("PPR_PC1", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ppr_pc1_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["PID"] = 1
        group_counts["PPR_PC1.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPR_PC1.PROBLEM"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["PPR_PC1.CHOICE"] = ["OBR"]
        result = validate_cardinality("PPR_PC1", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ppr_pc1_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PPR_PC1.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPR_PC1.PROBLEM"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        choice_children["PPR_PC1.CHOICE"] = ["OBR"]
        segment_counts["MSH"] = 2
        result = validate_cardinality("PPR_PC1", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

    def test_ppr_pc1_choice_none_ppr_pc1_choice(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PPR_PC1.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPR_PC1.PROBLEM"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        group_counts["PPR_PC1.CHOICE"] = 1
        result = validate_cardinality("PPR_PC1", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_NONE" in e.code for e in result.errors)

    def test_ppr_pc1_choice_multiple_ppr_pc1_choice(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["PID"] = 1
        group_counts["PPR_PC1.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PV1"] = 1
        group_counts["PPR_PC1.PROBLEM"] = 1
        segment_counts["PRB"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["PTH"] = 1
        segment_counts["OBX"] = 1
        segment_counts["GOL"] = 1
        segment_counts["ROL"] = 1
        segment_counts["PRT"] = 1
        segment_counts["OBX"] = 1
        segment_counts["ORC"] = 1
        segment_counts["OBX"] = 1
        segment_counts["OBR"] = 1
        segment_counts["anyHL7Segment"] = 1
        choice_children["PPR_PC1.CHOICE"] = ["OBR", "anyHL7Segment"]
        result = validate_cardinality("PPR_PC1", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CHOICE_MULTIPLE" in e.code for e in result.errors)
