from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestREFI12Cardinality:

    def test_ref_i12_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["AUT"] = 1
        group_counts["REF_I12.PROVIDER_CONTACT"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("REF_I12", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ref_i12_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["AUT"] = 1
        group_counts["REF_I12.PROVIDER_CONTACT"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("REF_I12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ref_i12_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["AUT"] = 1
        group_counts["REF_I12.PROVIDER_CONTACT"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("REF_I12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRPAI08Cardinality:

    def test_rpa_i08_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["AUT"] = 1
        group_counts["RPA_I08.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        group_counts["RPA_I08.PROCEDURE"] = 1
        segment_counts["PR1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("RPA_I08", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rpa_i08_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        segment_counts["AUT"] = 1
        group_counts["RPA_I08.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        group_counts["RPA_I08.PROCEDURE"] = 1
        segment_counts["PR1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("RPA_I08", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rpa_i08_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        segment_counts["AUT"] = 1
        group_counts["RPA_I08.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["IN1"] = 1
        group_counts["RPA_I08.PROCEDURE"] = 1
        segment_counts["PR1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RPA_I08", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRPII01Cardinality:

    def test_rpi_i01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["RPI_I01.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RPI_I01.INSURANCE"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("RPI_I01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rpi_i01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        group_counts["RPI_I01.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RPI_I01.INSURANCE"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("RPI_I01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rpi_i01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["RPI_I01.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RPI_I01.INSURANCE"] = 1
        segment_counts["IN1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RPI_I01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRPII04Cardinality:

    def test_rpi_i04_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["RPI_I04.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RPI_I04.INSURANCE"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("RPI_I04", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rpi_i04_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        group_counts["RPI_I04.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RPI_I04.INSURANCE"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("RPI_I04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rpi_i04_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["RPI_I04.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RPI_I04.INSURANCE"] = 1
        segment_counts["IN1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RPI_I04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRPLI02Cardinality:

    def test_rpl_i02_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["RPL_I02.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        result = validate_cardinality("RPL_I02", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rpl_i02_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        group_counts["RPL_I02.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        result = validate_cardinality("RPL_I02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rpl_i02_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["RPL_I02.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RPL_I02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRPRI03Cardinality:

    def test_rpr_i03_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["RPR_I03.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        result = validate_cardinality("RPR_I03", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rpr_i03_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSA"] = 1
        group_counts["RPR_I03.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        result = validate_cardinality("RPR_I03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rpr_i03_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["MSA"] = 1
        group_counts["RPR_I03.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RPR_I03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRQAI08Cardinality:

    def test_rqa_i08_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["AUT"] = 1
        group_counts["RQA_I08.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RQA_I08.INSURANCE"] = 1
        segment_counts["IN1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("RQA_I08", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rqa_i08_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["AUT"] = 1
        group_counts["RQA_I08.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RQA_I08.INSURANCE"] = 1
        segment_counts["IN1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("RQA_I08", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rqa_i08_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["AUT"] = 1
        group_counts["RQA_I08.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RQA_I08.INSURANCE"] = 1
        segment_counts["IN1"] = 1
        segment_counts["PR1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RQA_I08", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRQII01Cardinality:

    def test_rqi_i01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["RQI_I01.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RQI_I01.INSURANCE"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("RQI_I01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rqi_i01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        group_counts["RQI_I01.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RQI_I01.INSURANCE"] = 1
        segment_counts["IN1"] = 1
        result = validate_cardinality("RQI_I01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rqi_i01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["RQI_I01.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        group_counts["RQI_I01.INSURANCE"] = 1
        segment_counts["IN1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RQI_I01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRQPI04Cardinality:

    def test_rqp_i04_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["RQP_I04.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("RQP_I04", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rqp_i04_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        group_counts["RQP_I04.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        result = validate_cardinality("RQP_I04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rqp_i04_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        group_counts["RQP_I04.PROVIDER"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RQP_I04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestRRII12Cardinality:

    def test_rri_i12_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["AUT"] = 1
        group_counts["RRI_I12.PROVIDER_CONTACT"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["PR1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("RRI_I12", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_rri_i12_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["AUT"] = 1
        group_counts["RRI_I12.PROVIDER_CONTACT"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["PR1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        result = validate_cardinality("RRI_I12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_rri_i12_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["AUT"] = 1
        group_counts["RRI_I12.PROVIDER_CONTACT"] = 1
        segment_counts["PRD"] = 1
        segment_counts["PID"] = 1
        segment_counts["PR1"] = 1
        segment_counts["AUT"] = 1
        segment_counts["OBR"] = 1
        segment_counts["OBX"] = 1
        segment_counts["PV1"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("RRI_I12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
