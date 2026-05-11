from __future__ import annotations

from zato.hl7v2_rs import validate_cardinality



class TestEACU07Cardinality:

    def test_eac_u07_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        group_counts["EAC_U07.COMMAND"] = 1
        segment_counts["ECD"] = 1
        segment_counts["SAC"] = 1
        result = validate_cardinality("EAC_U07", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_eac_u07_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EQU"] = 1
        group_counts["EAC_U07.COMMAND"] = 1
        segment_counts["ECD"] = 1
        segment_counts["SAC"] = 1
        result = validate_cardinality("EAC_U07", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_eac_u07_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        group_counts["EAC_U07.COMMAND"] = 1
        segment_counts["ECD"] = 1
        segment_counts["SAC"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("EAC_U07", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestEANU09Cardinality:

    def test_ean_u09_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        group_counts["EAN_U09.NOTIFICATION"] = 1
        segment_counts["NDS"] = 1
        result = validate_cardinality("EAN_U09", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ean_u09_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EQU"] = 1
        group_counts["EAN_U09.NOTIFICATION"] = 1
        segment_counts["NDS"] = 1
        result = validate_cardinality("EAN_U09", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ean_u09_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        group_counts["EAN_U09.NOTIFICATION"] = 1
        segment_counts["NDS"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("EAN_U09", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestEARU08Cardinality:

    def test_ear_u08_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        group_counts["EAR_U08.COMMAND_RESPONSE"] = 1
        segment_counts["ECD"] = 1
        segment_counts["SAC"] = 1
        segment_counts["ECR"] = 1
        result = validate_cardinality("EAR_U08", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ear_u08_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EQU"] = 1
        group_counts["EAR_U08.COMMAND_RESPONSE"] = 1
        segment_counts["ECD"] = 1
        segment_counts["SAC"] = 1
        segment_counts["ECR"] = 1
        result = validate_cardinality("EAR_U08", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ear_u08_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        group_counts["EAR_U08.COMMAND_RESPONSE"] = 1
        segment_counts["ECD"] = 1
        segment_counts["SAC"] = 1
        segment_counts["ECR"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("EAR_U08", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestESRU02Cardinality:

    def test_esr_u02_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        result = validate_cardinality("ESR_U02", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_esr_u02_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EQU"] = 1
        result = validate_cardinality("ESR_U02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_esr_u02_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ESR_U02", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestESUU01Cardinality:

    def test_esu_u01_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        result = validate_cardinality("ESU_U01", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_esu_u01_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EQU"] = 1
        result = validate_cardinality("ESU_U01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_esu_u01_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("ESU_U01", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestINRU06Cardinality:

    def test_inr_u06_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        segment_counts["INV"] = 1
        result = validate_cardinality("INR_U06", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_inr_u06_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EQU"] = 1
        segment_counts["INV"] = 1
        result = validate_cardinality("INR_U06", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_inr_u06_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        segment_counts["INV"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("INR_U06", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestINRU14Cardinality:

    def test_inr_u14_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        result = validate_cardinality("INR_U14", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_inr_u14_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EQU"] = 1
        result = validate_cardinality("INR_U14", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_inr_u14_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("INR_U14", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestINUU05Cardinality:

    def test_inu_u05_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        segment_counts["INV"] = 1
        result = validate_cardinality("INU_U05", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_inu_u05_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EQU"] = 1
        segment_counts["INV"] = 1
        result = validate_cardinality("INU_U05", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_inu_u05_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        segment_counts["INV"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("INU_U05", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestLSUU12Cardinality:

    def test_lsu_u12_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        segment_counts["EQP"] = 1
        result = validate_cardinality("LSU_U12", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_lsu_u12_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EQU"] = 1
        segment_counts["EQP"] = 1
        result = validate_cardinality("LSU_U12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_lsu_u12_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        segment_counts["EQP"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("LSU_U12", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestSSRU04Cardinality:

    def test_ssr_u04_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        group_counts["SSR_U04.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        result = validate_cardinality("SSR_U04", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ssr_u04_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EQU"] = 1
        group_counts["SSR_U04.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        result = validate_cardinality("SSR_U04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ssr_u04_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        group_counts["SSR_U04.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("SSR_U04", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestSSUU03Cardinality:

    def test_ssu_u03_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        group_counts["SSU_U03.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        segment_counts["SPM"] = 1
        result = validate_cardinality("SSU_U03", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_ssu_u03_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EQU"] = 1
        group_counts["SSU_U03.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        segment_counts["SPM"] = 1
        result = validate_cardinality("SSU_U03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_ssu_u03_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        group_counts["SSU_U03.SPECIMEN_CONTAINER"] = 1
        segment_counts["SAC"] = 1
        segment_counts["SPM"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("SSU_U03", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)

class TestTCUU10Cardinality:

    def test_tcu_u10_valid_all_required_present(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        group_counts["TCU_U10.TEST_CONFIGURATION"] = 1
        segment_counts["TCC"] = 1
        result = validate_cardinality("TCU_U10", segment_counts, group_counts, choice_children, "TEST")
        assert result.is_valid

    def test_tcu_u10_invalid_missing_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["EQU"] = 1
        group_counts["TCU_U10.TEST_CONFIGURATION"] = 1
        segment_counts["TCC"] = 1
        result = validate_cardinality("TCU_U10", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MIN" in e.code for e in result.errors)

    def test_tcu_u10_invalid_exceeds_msh(self):
        segment_counts = {}
        group_counts = {}
        choice_children = {}
        segment_counts["MSH"] = 1
        segment_counts["EQU"] = 1
        group_counts["TCU_U10.TEST_CONFIGURATION"] = 1
        segment_counts["TCC"] = 1
        segment_counts["MSH"] = 2
        result = validate_cardinality("TCU_U10", segment_counts, group_counts, choice_children, "TEST")
        assert not result.is_valid
        assert any("CARDINALITY_MAX" in e.code for e in result.errors)
