from __future__ import annotations

from zato.hl7v2_rs import validate_field_length



class TestAFF_5Length:

    def test_aff_5_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("AFF", 5, value, "TEST")
        assert error is None

    def test_aff_5_valid_empty(self):
        error = validate_field_length("AFF", 5, "", "TEST")
        assert error is None

    def test_aff_5_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("AFF", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestARV_5Length:

    def test_arv_5_valid_within_limit(self):
        value = "x" * 250
        error = validate_field_length("ARV", 5, value, "TEST")
        assert error is None

    def test_arv_5_valid_empty(self):
        error = validate_field_length("ARV", 5, "", "TEST")
        assert error is None

    def test_arv_5_invalid_exceeds_limit(self):
        value = "x" * 251
        error = validate_field_length("ARV", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestAUT_3Length:

    def test_aut_3_valid_within_limit(self):
        value = "x" * 45
        error = validate_field_length("AUT", 3, value, "TEST")
        assert error is None

    def test_aut_3_valid_empty(self):
        error = validate_field_length("AUT", 3, "", "TEST")
        assert error is None

    def test_aut_3_truncatable_exceeds_limit(self):
        value = "x" * 46
        error = validate_field_length("AUT", 3, value, "TEST")
        assert error is None

class TestBHS_8Length:

    def test_bhs_8_valid_within_limit(self):
        value = "x" * 40
        error = validate_field_length("BHS", 8, value, "TEST")
        assert error is None

    def test_bhs_8_valid_empty(self):
        error = validate_field_length("BHS", 8, "", "TEST")
        assert error is None

    def test_bhs_8_invalid_exceeds_limit(self):
        value = "x" * 41
        error = validate_field_length("BHS", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestBHS_9Length:

    def test_bhs_9_valid_within_limit(self):
        value = "x" * 40
        error = validate_field_length("BHS", 9, value, "TEST")
        assert error is None

    def test_bhs_9_valid_empty(self):
        error = validate_field_length("BHS", 9, "", "TEST")
        assert error is None

    def test_bhs_9_invalid_exceeds_limit(self):
        value = "x" * 41
        error = validate_field_length("BHS", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestBHS_10Length:

    def test_bhs_10_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("BHS", 10, value, "TEST")
        assert error is None

    def test_bhs_10_valid_empty(self):
        error = validate_field_length("BHS", 10, "", "TEST")
        assert error is None

    def test_bhs_10_truncatable_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("BHS", 10, value, "TEST")
        assert error is None

class TestBHS_11Length:

    def test_bhs_11_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("BHS", 11, value, "TEST")
        assert error is None

    def test_bhs_11_valid_empty(self):
        error = validate_field_length("BHS", 11, "", "TEST")
        assert error is None

    def test_bhs_11_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("BHS", 11, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestBHS_12Length:

    def test_bhs_12_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("BHS", 12, value, "TEST")
        assert error is None

    def test_bhs_12_valid_empty(self):
        error = validate_field_length("BHS", 12, "", "TEST")
        assert error is None

    def test_bhs_12_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("BHS", 12, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestBPO_4Length:

    def test_bpo_4_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("BPO", 4, value, "TEST")
        assert error is None

    def test_bpo_4_valid_empty(self):
        error = validate_field_length("BPO", 4, "", "TEST")
        assert error is None

    def test_bpo_4_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("BPO", 4, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestBPO_5Length:

    def test_bpo_5_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("BPO", 5, value, "TEST")
        assert error is None

    def test_bpo_5_valid_empty(self):
        error = validate_field_length("BPO", 5, "", "TEST")
        assert error is None

    def test_bpo_5_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("BPO", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestBPX_14Length:

    def test_bpx_14_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("BPX", 14, value, "TEST")
        assert error is None

    def test_bpx_14_valid_empty(self):
        error = validate_field_length("BPX", 14, "", "TEST")
        assert error is None

    def test_bpx_14_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("BPX", 14, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestBPX_15Length:

    def test_bpx_15_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("BPX", 15, value, "TEST")
        assert error is None

    def test_bpx_15_valid_empty(self):
        error = validate_field_length("BPX", 15, "", "TEST")
        assert error is None

    def test_bpx_15_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("BPX", 15, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestBTS_1Length:

    def test_bts_1_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("BTS", 1, value, "TEST")
        assert error is None

    def test_bts_1_valid_empty(self):
        error = validate_field_length("BTS", 1, "", "TEST")
        assert error is None

    def test_bts_1_invalid_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("BTS", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestBTS_2Length:

    def test_bts_2_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("BTS", 2, value, "TEST")
        assert error is None

    def test_bts_2_valid_empty(self):
        error = validate_field_length("BTS", 2, "", "TEST")
        assert error is None

    def test_bts_2_truncatable_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("BTS", 2, value, "TEST")
        assert error is None

class TestBTX_8Length:

    def test_btx_8_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("BTX", 8, value, "TEST")
        assert error is None

    def test_btx_8_valid_empty(self):
        error = validate_field_length("BTX", 8, "", "TEST")
        assert error is None

    def test_btx_8_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("BTX", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestBTX_9Length:

    def test_btx_9_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("BTX", 9, value, "TEST")
        assert error is None

    def test_btx_9_valid_empty(self):
        error = validate_field_length("BTX", 9, "", "TEST")
        assert error is None

    def test_btx_9_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("BTX", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestCDM_3Length:

    def test_cdm_3_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("CDM", 3, value, "TEST")
        assert error is None

    def test_cdm_3_valid_empty(self):
        error = validate_field_length("CDM", 3, "", "TEST")
        assert error is None

    def test_cdm_3_truncatable_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("CDM", 3, value, "TEST")
        assert error is None

class TestCDM_4Length:

    def test_cdm_4_valid_within_limit(self):
        value = "x" * 250
        error = validate_field_length("CDM", 4, value, "TEST")
        assert error is None

    def test_cdm_4_valid_empty(self):
        error = validate_field_length("CDM", 4, "", "TEST")
        assert error is None

    def test_cdm_4_truncatable_exceeds_limit(self):
        value = "x" * 251
        error = validate_field_length("CDM", 4, value, "TEST")
        assert error is None

class TestCDM_5Length:

    def test_cdm_5_valid_within_limit(self):
        value = "x" * 1
        error = validate_field_length("CDM", 5, value, "TEST")
        assert error is None

    def test_cdm_5_valid_empty(self):
        error = validate_field_length("CDM", 5, "", "TEST")
        assert error is None

    def test_cdm_5_invalid_exceeds_limit(self):
        value = "x" * 2
        error = validate_field_length("CDM", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestCDM_10Length:

    def test_cdm_10_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("CDM", 10, value, "TEST")
        assert error is None

    def test_cdm_10_valid_empty(self):
        error = validate_field_length("CDM", 10, "", "TEST")
        assert error is None

    def test_cdm_10_invalid_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("CDM", 10, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestCER_2Length:

    def test_cer_2_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("CER", 2, value, "TEST")
        assert error is None

    def test_cer_2_valid_empty(self):
        error = validate_field_length("CER", 2, "", "TEST")
        assert error is None

    def test_cer_2_invalid_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("CER", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestCER_3Length:

    def test_cer_3_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("CER", 3, value, "TEST")
        assert error is None

    def test_cer_3_valid_empty(self):
        error = validate_field_length("CER", 3, "", "TEST")
        assert error is None

    def test_cer_3_invalid_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("CER", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestCER_13Length:

    def test_cer_13_valid_within_limit(self):
        value = "x" * 250
        error = validate_field_length("CER", 13, value, "TEST")
        assert error is None

    def test_cer_13_valid_empty(self):
        error = validate_field_length("CER", 13, "", "TEST")
        assert error is None

    def test_cer_13_invalid_exceeds_limit(self):
        value = "x" * 251
        error = validate_field_length("CER", 13, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestCM0_4Length:

    def test_cm0_4_valid_within_limit(self):
        value = "x" * 300
        error = validate_field_length("CM0", 4, value, "TEST")
        assert error is None

    def test_cm0_4_valid_empty(self):
        error = validate_field_length("CM0", 4, "", "TEST")
        assert error is None

    def test_cm0_4_truncatable_exceeds_limit(self):
        value = "x" * 301
        error = validate_field_length("CM0", 4, value, "TEST")
        assert error is None

class TestCM0_7Length:

    def test_cm0_7_valid_within_limit(self):
        value = "x" * 8
        error = validate_field_length("CM0", 7, value, "TEST")
        assert error is None

    def test_cm0_7_valid_empty(self):
        error = validate_field_length("CM0", 7, "", "TEST")
        assert error is None

    def test_cm0_7_invalid_exceeds_limit(self):
        value = "x" * 9
        error = validate_field_length("CM0", 7, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestCM1_3Length:

    def test_cm1_3_valid_within_limit(self):
        value = "x" * 300
        error = validate_field_length("CM1", 3, value, "TEST")
        assert error is None

    def test_cm1_3_valid_empty(self):
        error = validate_field_length("CM1", 3, "", "TEST")
        assert error is None

    def test_cm1_3_invalid_exceeds_limit(self):
        value = "x" * 301
        error = validate_field_length("CM1", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestCM2_3Length:

    def test_cm2_3_valid_within_limit(self):
        value = "x" * 300
        error = validate_field_length("CM2", 3, value, "TEST")
        assert error is None

    def test_cm2_3_valid_empty(self):
        error = validate_field_length("CM2", 3, "", "TEST")
        assert error is None

    def test_cm2_3_invalid_exceeds_limit(self):
        value = "x" * 301
        error = validate_field_length("CM2", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestCNS_1Length:

    def test_cns_1_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("CNS", 1, value, "TEST")
        assert error is None

    def test_cns_1_valid_empty(self):
        error = validate_field_length("CNS", 1, "", "TEST")
        assert error is None

    def test_cns_1_invalid_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("CNS", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestCNS_2Length:

    def test_cns_2_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("CNS", 2, value, "TEST")
        assert error is None

    def test_cns_2_valid_empty(self):
        error = validate_field_length("CNS", 2, "", "TEST")
        assert error is None

    def test_cns_2_invalid_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("CNS", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestCTR_2Length:

    def test_ctr_2_valid_within_limit(self):
        value = "x" * 999
        error = validate_field_length("CTR", 2, value, "TEST")
        assert error is None

    def test_ctr_2_valid_empty(self):
        error = validate_field_length("CTR", 2, "", "TEST")
        assert error is None

    def test_ctr_2_truncatable_exceeds_limit(self):
        value = "x" * 1000
        error = validate_field_length("CTR", 2, value, "TEST")
        assert error is None

class TestDEV_6Length:

    def test_dev_6_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("DEV", 6, value, "TEST")
        assert error is None

    def test_dev_6_valid_empty(self):
        error = validate_field_length("DEV", 6, "", "TEST")
        assert error is None

    def test_dev_6_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("DEV", 6, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestDEV_7Length:

    def test_dev_7_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("DEV", 7, value, "TEST")
        assert error is None

    def test_dev_7_valid_empty(self):
        error = validate_field_length("DEV", 7, "", "TEST")
        assert error is None

    def test_dev_7_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("DEV", 7, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestDEV_8Length:

    def test_dev_8_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("DEV", 8, value, "TEST")
        assert error is None

    def test_dev_8_valid_empty(self):
        error = validate_field_length("DEV", 8, "", "TEST")
        assert error is None

    def test_dev_8_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("DEV", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestDMI_4Length:

    def test_dmi_4_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("DMI", 4, value, "TEST")
        assert error is None

    def test_dmi_4_valid_empty(self):
        error = validate_field_length("DMI", 4, "", "TEST")
        assert error is None

    def test_dmi_4_truncatable_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("DMI", 4, value, "TEST")
        assert error is None

class TestDMI_5Length:

    def test_dmi_5_valid_within_limit(self):
        value = "x" * 7
        error = validate_field_length("DMI", 5, value, "TEST")
        assert error is None

    def test_dmi_5_valid_empty(self):
        error = validate_field_length("DMI", 5, "", "TEST")
        assert error is None

    def test_dmi_5_truncatable_exceeds_limit(self):
        value = "x" * 8
        error = validate_field_length("DMI", 5, value, "TEST")
        assert error is None

class TestDON_25Length:

    def test_don_25_valid_within_limit(self):
        value = "x" * 75
        error = validate_field_length("DON", 25, value, "TEST")
        assert error is None

    def test_don_25_valid_empty(self):
        error = validate_field_length("DON", 25, "", "TEST")
        assert error is None

    def test_don_25_truncatable_exceeds_limit(self):
        value = "x" * 76
        error = validate_field_length("DON", 25, value, "TEST")
        assert error is None

class TestDON_26Length:

    def test_don_26_valid_within_limit(self):
        value = "x" * 25
        error = validate_field_length("DON", 26, value, "TEST")
        assert error is None

    def test_don_26_valid_empty(self):
        error = validate_field_length("DON", 26, "", "TEST")
        assert error is None

    def test_don_26_truncatable_exceeds_limit(self):
        value = "x" * 26
        error = validate_field_length("DON", 26, value, "TEST")
        assert error is None

class TestDSC_1Length:

    def test_dsc_1_valid_within_limit(self):
        value = "x" * 180
        error = validate_field_length("DSC", 1, value, "TEST")
        assert error is None

    def test_dsc_1_valid_empty(self):
        error = validate_field_length("DSC", 1, "", "TEST")
        assert error is None

    def test_dsc_1_invalid_exceeds_limit(self):
        value = "x" * 181
        error = validate_field_length("DSC", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestDSP_3Length:

    def test_dsp_3_valid_within_limit(self):
        value = "x" * 300
        error = validate_field_length("DSP", 3, value, "TEST")
        assert error is None

    def test_dsp_3_valid_empty(self):
        error = validate_field_length("DSP", 3, "", "TEST")
        assert error is None

    def test_dsp_3_invalid_exceeds_limit(self):
        value = "x" * 301
        error = validate_field_length("DSP", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestDSP_4Length:

    def test_dsp_4_valid_within_limit(self):
        value = "x" * 2
        error = validate_field_length("DSP", 4, value, "TEST")
        assert error is None

    def test_dsp_4_valid_empty(self):
        error = validate_field_length("DSP", 4, "", "TEST")
        assert error is None

    def test_dsp_4_invalid_exceeds_limit(self):
        value = "x" * 3
        error = validate_field_length("DSP", 4, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestDSP_5Length:

    def test_dsp_5_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("DSP", 5, value, "TEST")
        assert error is None

    def test_dsp_5_valid_empty(self):
        error = validate_field_length("DSP", 5, "", "TEST")
        assert error is None

    def test_dsp_5_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("DSP", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestECD_1Length:

    def test_ecd_1_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("ECD", 1, value, "TEST")
        assert error is None

    def test_ecd_1_valid_empty(self):
        error = validate_field_length("ECD", 1, "", "TEST")
        assert error is None

    def test_ecd_1_invalid_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("ECD", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestEQP_2Length:

    def test_eqp_2_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("EQP", 2, value, "TEST")
        assert error is None

    def test_eqp_2_valid_empty(self):
        error = validate_field_length("EQP", 2, "", "TEST")
        assert error is None

    def test_eqp_2_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("EQP", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestERR_6Length:

    def test_err_6_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("ERR", 6, value, "TEST")
        assert error is None

    def test_err_6_valid_empty(self):
        error = validate_field_length("ERR", 6, "", "TEST")
        assert error is None

    def test_err_6_truncatable_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("ERR", 6, value, "TEST")
        assert error is None

class TestERR_7Length:

    def test_err_7_valid_within_limit(self):
        value = "x" * 2048
        error = validate_field_length("ERR", 7, value, "TEST")
        assert error is None

    def test_err_7_valid_empty(self):
        error = validate_field_length("ERR", 7, "", "TEST")
        assert error is None

    def test_err_7_truncatable_exceeds_limit(self):
        value = "x" * 2049
        error = validate_field_length("ERR", 7, value, "TEST")
        assert error is None

class TestERR_8Length:

    def test_err_8_valid_within_limit(self):
        value = "x" * 250
        error = validate_field_length("ERR", 8, value, "TEST")
        assert error is None

    def test_err_8_valid_empty(self):
        error = validate_field_length("ERR", 8, "", "TEST")
        assert error is None

    def test_err_8_truncatable_exceeds_limit(self):
        value = "x" * 251
        error = validate_field_length("ERR", 8, value, "TEST")
        assert error is None

class TestFAC_6Length:

    def test_fac_6_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("FAC", 6, value, "TEST")
        assert error is None

    def test_fac_6_valid_empty(self):
        error = validate_field_length("FAC", 6, "", "TEST")
        assert error is None

    def test_fac_6_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("FAC", 6, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestFAC_10Length:

    def test_fac_10_valid_within_limit(self):
        value = "x" * 199
        error = validate_field_length("FAC", 10, value, "TEST")
        assert error is None

    def test_fac_10_valid_empty(self):
        error = validate_field_length("FAC", 10, "", "TEST")
        assert error is None

    def test_fac_10_invalid_exceeds_limit(self):
        value = "x" * 200
        error = validate_field_length("FAC", 10, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestFHS_8Length:

    def test_fhs_8_valid_within_limit(self):
        value = "x" * 40
        error = validate_field_length("FHS", 8, value, "TEST")
        assert error is None

    def test_fhs_8_valid_empty(self):
        error = validate_field_length("FHS", 8, "", "TEST")
        assert error is None

    def test_fhs_8_invalid_exceeds_limit(self):
        value = "x" * 41
        error = validate_field_length("FHS", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestFHS_9Length:

    def test_fhs_9_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("FHS", 9, value, "TEST")
        assert error is None

    def test_fhs_9_valid_empty(self):
        error = validate_field_length("FHS", 9, "", "TEST")
        assert error is None

    def test_fhs_9_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("FHS", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestFHS_10Length:

    def test_fhs_10_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("FHS", 10, value, "TEST")
        assert error is None

    def test_fhs_10_valid_empty(self):
        error = validate_field_length("FHS", 10, "", "TEST")
        assert error is None

    def test_fhs_10_truncatable_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("FHS", 10, value, "TEST")
        assert error is None

class TestFHS_11Length:

    def test_fhs_11_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("FHS", 11, value, "TEST")
        assert error is None

    def test_fhs_11_valid_empty(self):
        error = validate_field_length("FHS", 11, "", "TEST")
        assert error is None

    def test_fhs_11_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("FHS", 11, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestFHS_12Length:

    def test_fhs_12_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("FHS", 12, value, "TEST")
        assert error is None

    def test_fhs_12_valid_empty(self):
        error = validate_field_length("FHS", 12, "", "TEST")
        assert error is None

    def test_fhs_12_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("FHS", 12, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestFTS_1Length:

    def test_fts_1_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("FTS", 1, value, "TEST")
        assert error is None

    def test_fts_1_valid_empty(self):
        error = validate_field_length("FTS", 1, "", "TEST")
        assert error is None

    def test_fts_1_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("FTS", 1, value, "TEST")
        assert error is None

class TestFTS_2Length:

    def test_fts_2_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("FTS", 2, value, "TEST")
        assert error is None

    def test_fts_2_valid_empty(self):
        error = validate_field_length("FTS", 2, "", "TEST")
        assert error is None

    def test_fts_2_truncatable_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("FTS", 2, value, "TEST")
        assert error is None

class TestGOL_6Length:

    def test_gol_6_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("GOL", 6, value, "TEST")
        assert error is None

    def test_gol_6_valid_empty(self):
        error = validate_field_length("GOL", 6, "", "TEST")
        assert error is None

    def test_gol_6_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("GOL", 6, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestGOL_17Length:

    def test_gol_17_valid_within_limit(self):
        value = "x" * 300
        error = validate_field_length("GOL", 17, value, "TEST")
        assert error is None

    def test_gol_17_valid_empty(self):
        error = validate_field_length("GOL", 17, "", "TEST")
        assert error is None

    def test_gol_17_invalid_exceeds_limit(self):
        value = "x" * 301
        error = validate_field_length("GOL", 17, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIAR_4Length:

    def test_iar_4_valid_within_limit(self):
        value = "x" * 250
        error = validate_field_length("IAR", 4, value, "TEST")
        assert error is None

    def test_iar_4_valid_empty(self):
        error = validate_field_length("IAR", 4, "", "TEST")
        assert error is None

    def test_iar_4_invalid_exceeds_limit(self):
        value = "x" * 251
        error = validate_field_length("IAR", 4, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIIM_3Length:

    def test_iim_3_valid_within_limit(self):
        value = "x" * 250
        error = validate_field_length("IIM", 3, value, "TEST")
        assert error is None

    def test_iim_3_valid_empty(self):
        error = validate_field_length("IIM", 3, "", "TEST")
        assert error is None

    def test_iim_3_invalid_exceeds_limit(self):
        value = "x" * 251
        error = validate_field_length("IIM", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIIM_8Length:

    def test_iim_8_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("IIM", 8, value, "TEST")
        assert error is None

    def test_iim_8_valid_empty(self):
        error = validate_field_length("IIM", 8, "", "TEST")
        assert error is None

    def test_iim_8_truncatable_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("IIM", 8, value, "TEST")
        assert error is None

class TestIIM_12Length:

    def test_iim_12_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("IIM", 12, value, "TEST")
        assert error is None

    def test_iim_12_valid_empty(self):
        error = validate_field_length("IIM", 12, "", "TEST")
        assert error is None

    def test_iim_12_truncatable_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("IIM", 12, value, "TEST")
        assert error is None

class TestILT_2Length:

    def test_ilt_2_valid_within_limit(self):
        value = "x" * 250
        error = validate_field_length("ILT", 2, value, "TEST")
        assert error is None

    def test_ilt_2_valid_empty(self):
        error = validate_field_length("ILT", 2, "", "TEST")
        assert error is None

    def test_ilt_2_invalid_exceeds_limit(self):
        value = "x" * 251
        error = validate_field_length("ILT", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestILT_5Length:

    def test_ilt_5_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("ILT", 5, value, "TEST")
        assert error is None

    def test_ilt_5_valid_empty(self):
        error = validate_field_length("ILT", 5, "", "TEST")
        assert error is None

    def test_ilt_5_truncatable_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("ILT", 5, value, "TEST")
        assert error is None

class TestILT_9Length:

    def test_ilt_9_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("ILT", 9, value, "TEST")
        assert error is None

    def test_ilt_9_valid_empty(self):
        error = validate_field_length("ILT", 9, "", "TEST")
        assert error is None

    def test_ilt_9_truncatable_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("ILT", 9, value, "TEST")
        assert error is None

class TestINV_7Length:

    def test_inv_7_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("INV", 7, value, "TEST")
        assert error is None

    def test_inv_7_valid_empty(self):
        error = validate_field_length("INV", 7, "", "TEST")
        assert error is None

    def test_inv_7_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("INV", 7, value, "TEST")
        assert error is None

class TestINV_8Length:

    def test_inv_8_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("INV", 8, value, "TEST")
        assert error is None

    def test_inv_8_valid_empty(self):
        error = validate_field_length("INV", 8, "", "TEST")
        assert error is None

    def test_inv_8_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("INV", 8, value, "TEST")
        assert error is None

class TestINV_9Length:

    def test_inv_9_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("INV", 9, value, "TEST")
        assert error is None

    def test_inv_9_valid_empty(self):
        error = validate_field_length("INV", 9, "", "TEST")
        assert error is None

    def test_inv_9_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("INV", 9, value, "TEST")
        assert error is None

class TestINV_10Length:

    def test_inv_10_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("INV", 10, value, "TEST")
        assert error is None

    def test_inv_10_valid_empty(self):
        error = validate_field_length("INV", 10, "", "TEST")
        assert error is None

    def test_inv_10_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("INV", 10, value, "TEST")
        assert error is None

class TestINV_16Length:

    def test_inv_16_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("INV", 16, value, "TEST")
        assert error is None

    def test_inv_16_valid_empty(self):
        error = validate_field_length("INV", 16, "", "TEST")
        assert error is None

    def test_inv_16_invalid_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("INV", 16, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIPC_9Length:

    def test_ipc_9_valid_within_limit(self):
        value = "x" * 16
        error = validate_field_length("IPC", 9, value, "TEST")
        assert error is None

    def test_ipc_9_valid_empty(self):
        error = validate_field_length("IPC", 9, "", "TEST")
        assert error is None

    def test_ipc_9_invalid_exceeds_limit(self):
        value = "x" * 17
        error = validate_field_length("IPC", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIPR_8Length:

    def test_ipr_8_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("IPR", 8, value, "TEST")
        assert error is None

    def test_ipr_8_valid_empty(self):
        error = validate_field_length("IPR", 8, "", "TEST")
        assert error is None

    def test_ipr_8_invalid_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("IPR", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestITM_2Length:

    def test_itm_2_valid_within_limit(self):
        value = "x" * 999
        error = validate_field_length("ITM", 2, value, "TEST")
        assert error is None

    def test_itm_2_valid_empty(self):
        error = validate_field_length("ITM", 2, "", "TEST")
        assert error is None

    def test_itm_2_truncatable_exceeds_limit(self):
        value = "x" * 1000
        error = validate_field_length("ITM", 2, value, "TEST")
        assert error is None

class TestITM_8Length:

    def test_itm_8_valid_within_limit(self):
        value = "x" * 999
        error = validate_field_length("ITM", 8, value, "TEST")
        assert error is None

    def test_itm_8_valid_empty(self):
        error = validate_field_length("ITM", 8, "", "TEST")
        assert error is None

    def test_itm_8_invalid_exceeds_limit(self):
        value = "x" * 1000
        error = validate_field_length("ITM", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestITM_9Length:

    def test_itm_9_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("ITM", 9, value, "TEST")
        assert error is None

    def test_itm_9_valid_empty(self):
        error = validate_field_length("ITM", 9, "", "TEST")
        assert error is None

    def test_itm_9_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("ITM", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestITM_20Length:

    def test_itm_20_valid_within_limit(self):
        value = "x" * 6
        error = validate_field_length("ITM", 20, value, "TEST")
        assert error is None

    def test_itm_20_valid_empty(self):
        error = validate_field_length("ITM", 20, "", "TEST")
        assert error is None

    def test_itm_20_truncatable_exceeds_limit(self):
        value = "x" * 7
        error = validate_field_length("ITM", 20, value, "TEST")
        assert error is None

class TestIVC_9Length:

    def test_ivc_9_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("IVC", 9, value, "TEST")
        assert error is None

    def test_ivc_9_valid_empty(self):
        error = validate_field_length("IVC", 9, "", "TEST")
        assert error is None

    def test_ivc_9_invalid_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("IVC", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIVC_15Length:

    def test_ivc_15_valid_within_limit(self):
        value = "x" * 250
        error = validate_field_length("IVC", 15, value, "TEST")
        assert error is None

    def test_ivc_15_valid_empty(self):
        error = validate_field_length("IVC", 15, "", "TEST")
        assert error is None

    def test_ivc_15_invalid_exceeds_limit(self):
        value = "x" * 251
        error = validate_field_length("IVC", 15, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIVC_26Length:

    def test_ivc_26_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("IVC", 26, value, "TEST")
        assert error is None

    def test_ivc_26_valid_empty(self):
        error = validate_field_length("IVC", 26, "", "TEST")
        assert error is None

    def test_ivc_26_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("IVC", 26, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIVC_27Length:

    def test_ivc_27_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("IVC", 27, value, "TEST")
        assert error is None

    def test_ivc_27_valid_empty(self):
        error = validate_field_length("IVC", 27, "", "TEST")
        assert error is None

    def test_ivc_27_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("IVC", 27, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIVC_30Length:

    def test_ivc_30_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("IVC", 30, value, "TEST")
        assert error is None

    def test_ivc_30_valid_empty(self):
        error = validate_field_length("IVC", 30, "", "TEST")
        assert error is None

    def test_ivc_30_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("IVC", 30, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIVT_3Length:

    def test_ivt_3_valid_within_limit(self):
        value = "x" * 999
        error = validate_field_length("IVT", 3, value, "TEST")
        assert error is None

    def test_ivt_3_valid_empty(self):
        error = validate_field_length("IVT", 3, "", "TEST")
        assert error is None

    def test_ivt_3_invalid_exceeds_limit(self):
        value = "x" * 1000
        error = validate_field_length("IVT", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIVT_5Length:

    def test_ivt_5_valid_within_limit(self):
        value = "x" * 999
        error = validate_field_length("IVT", 5, value, "TEST")
        assert error is None

    def test_ivt_5_valid_empty(self):
        error = validate_field_length("IVT", 5, "", "TEST")
        assert error is None

    def test_ivt_5_invalid_exceeds_limit(self):
        value = "x" * 1000
        error = validate_field_length("IVT", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIVT_22Length:

    def test_ivt_22_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("IVT", 22, value, "TEST")
        assert error is None

    def test_ivt_22_valid_empty(self):
        error = validate_field_length("IVT", 22, "", "TEST")
        assert error is None

    def test_ivt_22_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("IVT", 22, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIVT_23Length:

    def test_ivt_23_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("IVT", 23, value, "TEST")
        assert error is None

    def test_ivt_23_valid_empty(self):
        error = validate_field_length("IVT", 23, "", "TEST")
        assert error is None

    def test_ivt_23_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("IVT", 23, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIVT_24Length:

    def test_ivt_24_valid_within_limit(self):
        value = "x" * 8
        error = validate_field_length("IVT", 24, value, "TEST")
        assert error is None

    def test_ivt_24_valid_empty(self):
        error = validate_field_length("IVT", 24, "", "TEST")
        assert error is None

    def test_ivt_24_truncatable_exceeds_limit(self):
        value = "x" * 9
        error = validate_field_length("IVT", 24, value, "TEST")
        assert error is None

class TestIVT_25Length:

    def test_ivt_25_valid_within_limit(self):
        value = "x" * 8
        error = validate_field_length("IVT", 25, value, "TEST")
        assert error is None

    def test_ivt_25_valid_empty(self):
        error = validate_field_length("IVT", 25, "", "TEST")
        assert error is None

    def test_ivt_25_truncatable_exceeds_limit(self):
        value = "x" * 9
        error = validate_field_length("IVT", 25, value, "TEST")
        assert error is None

class TestLDP_3Length:

    def test_ldp_3_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("LDP", 3, value, "TEST")
        assert error is None

    def test_ldp_3_valid_empty(self):
        error = validate_field_length("LDP", 3, "", "TEST")
        assert error is None

    def test_ldp_3_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("LDP", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestLDP_5Length:

    def test_ldp_5_valid_within_limit(self):
        value = "x" * 1
        error = validate_field_length("LDP", 5, value, "TEST")
        assert error is None

    def test_ldp_5_valid_empty(self):
        error = validate_field_length("LDP", 5, "", "TEST")
        assert error is None

    def test_ldp_5_invalid_exceeds_limit(self):
        value = "x" * 2
        error = validate_field_length("LDP", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestLDP_9Length:

    def test_ldp_9_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("LDP", 9, value, "TEST")
        assert error is None

    def test_ldp_9_valid_empty(self):
        error = validate_field_length("LDP", 9, "", "TEST")
        assert error is None

    def test_ldp_9_invalid_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("LDP", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestLOC_2Length:

    def test_loc_2_valid_within_limit(self):
        value = "x" * 48
        error = validate_field_length("LOC", 2, value, "TEST")
        assert error is None

    def test_loc_2_valid_empty(self):
        error = validate_field_length("LOC", 2, "", "TEST")
        assert error is None

    def test_loc_2_truncatable_exceeds_limit(self):
        value = "x" * 49
        error = validate_field_length("LOC", 2, value, "TEST")
        assert error is None

class TestLOC_3Length:

    def test_loc_3_valid_within_limit(self):
        value = "x" * 1
        error = validate_field_length("LOC", 3, value, "TEST")
        assert error is None

    def test_loc_3_valid_empty(self):
        error = validate_field_length("LOC", 3, "", "TEST")
        assert error is None

    def test_loc_3_invalid_exceeds_limit(self):
        value = "x" * 2
        error = validate_field_length("LOC", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestLOC_8Length:

    def test_loc_8_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("LOC", 8, value, "TEST")
        assert error is None

    def test_loc_8_valid_empty(self):
        error = validate_field_length("LOC", 8, "", "TEST")
        assert error is None

    def test_loc_8_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("LOC", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestLOC_9Length:

    def test_loc_9_valid_within_limit(self):
        value = "x" * 1
        error = validate_field_length("LOC", 9, value, "TEST")
        assert error is None

    def test_loc_9_valid_empty(self):
        error = validate_field_length("LOC", 9, "", "TEST")
        assert error is None

    def test_loc_9_invalid_exceeds_limit(self):
        value = "x" * 2
        error = validate_field_length("LOC", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestMFA_2Length:

    def test_mfa_2_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("MFA", 2, value, "TEST")
        assert error is None

    def test_mfa_2_valid_empty(self):
        error = validate_field_length("MFA", 2, "", "TEST")
        assert error is None

    def test_mfa_2_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("MFA", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestMSH_8Length:

    def test_msh_8_valid_within_limit(self):
        value = "x" * 40
        error = validate_field_length("MSH", 8, value, "TEST")
        assert error is None

    def test_msh_8_valid_empty(self):
        error = validate_field_length("MSH", 8, "", "TEST")
        assert error is None

    def test_msh_8_invalid_exceeds_limit(self):
        value = "x" * 41
        error = validate_field_length("MSH", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestMSH_14Length:

    def test_msh_14_valid_within_limit(self):
        value = "x" * 180
        error = validate_field_length("MSH", 14, value, "TEST")
        assert error is None

    def test_msh_14_valid_empty(self):
        error = validate_field_length("MSH", 14, "", "TEST")
        assert error is None

    def test_msh_14_invalid_exceeds_limit(self):
        value = "x" * 181
        error = validate_field_length("MSH", 14, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestNDS_1Length:

    def test_nds_1_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("NDS", 1, value, "TEST")
        assert error is None

    def test_nds_1_valid_empty(self):
        error = validate_field_length("NDS", 1, "", "TEST")
        assert error is None

    def test_nds_1_invalid_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("NDS", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestODS_4Length:

    def test_ods_4_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("ODS", 4, value, "TEST")
        assert error is None

    def test_ods_4_valid_empty(self):
        error = validate_field_length("ODS", 4, "", "TEST")
        assert error is None

    def test_ods_4_truncatable_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("ODS", 4, value, "TEST")
        assert error is None

class TestODT_3Length:

    def test_odt_3_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("ODT", 3, value, "TEST")
        assert error is None

    def test_odt_3_valid_empty(self):
        error = validate_field_length("ODT", 3, "", "TEST")
        assert error is None

    def test_odt_3_truncatable_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("ODT", 3, value, "TEST")
        assert error is None

class TestOMC_1Length:

    def test_omc_1_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("OMC", 1, value, "TEST")
        assert error is None

    def test_omc_1_valid_empty(self):
        error = validate_field_length("OMC", 1, "", "TEST")
        assert error is None

    def test_omc_1_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("OMC", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOVR_3Length:

    def test_ovr_3_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("OVR", 3, value, "TEST")
        assert error is None

    def test_ovr_3_valid_empty(self):
        error = validate_field_length("OVR", 3, "", "TEST")
        assert error is None

    def test_ovr_3_truncatable_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("OVR", 3, value, "TEST")
        assert error is None

class TestPCR_2Length:

    def test_pcr_2_valid_within_limit(self):
        value = "x" * 1
        error = validate_field_length("PCR", 2, value, "TEST")
        assert error is None

    def test_pcr_2_valid_empty(self):
        error = validate_field_length("PCR", 2, "", "TEST")
        assert error is None

    def test_pcr_2_invalid_exceeds_limit(self):
        value = "x" * 2
        error = validate_field_length("PCR", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPCR_12Length:

    def test_pcr_12_valid_within_limit(self):
        value = "x" * 199
        error = validate_field_length("PCR", 12, value, "TEST")
        assert error is None

    def test_pcr_12_valid_empty(self):
        error = validate_field_length("PCR", 12, "", "TEST")
        assert error is None

    def test_pcr_12_invalid_exceeds_limit(self):
        value = "x" * 200
        error = validate_field_length("PCR", 12, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPDC_3Length:

    def test_pdc_3_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("PDC", 3, value, "TEST")
        assert error is None

    def test_pdc_3_valid_empty(self):
        error = validate_field_length("PDC", 3, "", "TEST")
        assert error is None

    def test_pdc_3_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("PDC", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPDC_4Length:

    def test_pdc_4_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("PDC", 4, value, "TEST")
        assert error is None

    def test_pdc_4_valid_empty(self):
        error = validate_field_length("PDC", 4, "", "TEST")
        assert error is None

    def test_pdc_4_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("PDC", 4, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPDC_6Length:

    def test_pdc_6_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("PDC", 6, value, "TEST")
        assert error is None

    def test_pdc_6_valid_empty(self):
        error = validate_field_length("PDC", 6, "", "TEST")
        assert error is None

    def test_pdc_6_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("PDC", 6, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPDC_7Length:

    def test_pdc_7_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("PDC", 7, value, "TEST")
        assert error is None

    def test_pdc_7_valid_empty(self):
        error = validate_field_length("PDC", 7, "", "TEST")
        assert error is None

    def test_pdc_7_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("PDC", 7, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPDC_8Length:

    def test_pdc_8_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("PDC", 8, value, "TEST")
        assert error is None

    def test_pdc_8_valid_empty(self):
        error = validate_field_length("PDC", 8, "", "TEST")
        assert error is None

    def test_pdc_8_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("PDC", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPDC_11Length:

    def test_pdc_11_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("PDC", 11, value, "TEST")
        assert error is None

    def test_pdc_11_valid_empty(self):
        error = validate_field_length("PDC", 11, "", "TEST")
        assert error is None

    def test_pdc_11_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("PDC", 11, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPEO_13Length:

    def test_peo_13_valid_within_limit(self):
        value = "x" * 600
        error = validate_field_length("PEO", 13, value, "TEST")
        assert error is None

    def test_peo_13_valid_empty(self):
        error = validate_field_length("PEO", 13, "", "TEST")
        assert error is None

    def test_peo_13_invalid_exceeds_limit(self):
        value = "x" * 601
        error = validate_field_length("PEO", 13, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPEO_14Length:

    def test_peo_14_valid_within_limit(self):
        value = "x" * 600
        error = validate_field_length("PEO", 14, value, "TEST")
        assert error is None

    def test_peo_14_valid_empty(self):
        error = validate_field_length("PEO", 14, "", "TEST")
        assert error is None

    def test_peo_14_invalid_exceeds_limit(self):
        value = "x" * 601
        error = validate_field_length("PEO", 14, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPEO_15Length:

    def test_peo_15_valid_within_limit(self):
        value = "x" * 600
        error = validate_field_length("PEO", 15, value, "TEST")
        assert error is None

    def test_peo_15_valid_empty(self):
        error = validate_field_length("PEO", 15, "", "TEST")
        assert error is None

    def test_peo_15_invalid_exceeds_limit(self):
        value = "x" * 601
        error = validate_field_length("PEO", 15, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPEO_16Length:

    def test_peo_16_valid_within_limit(self):
        value = "x" * 600
        error = validate_field_length("PEO", 16, value, "TEST")
        assert error is None

    def test_peo_16_valid_empty(self):
        error = validate_field_length("PEO", 16, "", "TEST")
        assert error is None

    def test_peo_16_invalid_exceeds_limit(self):
        value = "x" * 601
        error = validate_field_length("PEO", 16, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPEO_17Length:

    def test_peo_17_valid_within_limit(self):
        value = "x" * 600
        error = validate_field_length("PEO", 17, value, "TEST")
        assert error is None

    def test_peo_17_valid_empty(self):
        error = validate_field_length("PEO", 17, "", "TEST")
        assert error is None

    def test_peo_17_invalid_exceeds_limit(self):
        value = "x" * 601
        error = validate_field_length("PEO", 17, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPES_6Length:

    def test_pes_6_valid_within_limit(self):
        value = "x" * 16
        error = validate_field_length("PES", 6, value, "TEST")
        assert error is None

    def test_pes_6_valid_empty(self):
        error = validate_field_length("PES", 6, "", "TEST")
        assert error is None

    def test_pes_6_invalid_exceeds_limit(self):
        value = "x" * 17
        error = validate_field_length("PES", 6, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPES_7Length:

    def test_pes_7_valid_within_limit(self):
        value = "x" * 600
        error = validate_field_length("PES", 7, value, "TEST")
        assert error is None

    def test_pes_7_valid_empty(self):
        error = validate_field_length("PES", 7, "", "TEST")
        assert error is None

    def test_pes_7_invalid_exceeds_limit(self):
        value = "x" * 601
        error = validate_field_length("PES", 7, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPES_8Length:

    def test_pes_8_valid_within_limit(self):
        value = "x" * 600
        error = validate_field_length("PES", 8, value, "TEST")
        assert error is None

    def test_pes_8_valid_empty(self):
        error = validate_field_length("PES", 8, "", "TEST")
        assert error is None

    def test_pes_8_invalid_exceeds_limit(self):
        value = "x" * 601
        error = validate_field_length("PES", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPKG_4Length:

    def test_pkg_4_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("PKG", 4, value, "TEST")
        assert error is None

    def test_pkg_4_valid_empty(self):
        error = validate_field_length("PKG", 4, "", "TEST")
        assert error is None

    def test_pkg_4_invalid_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("PKG", 4, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPM1_7Length:

    def test_pm1_7_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("PM1", 7, value, "TEST")
        assert error is None

    def test_pm1_7_valid_empty(self):
        error = validate_field_length("PM1", 7, "", "TEST")
        assert error is None

    def test_pm1_7_invalid_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("PM1", 7, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPMT_9Length:

    def test_pmt_9_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("PMT", 9, value, "TEST")
        assert error is None

    def test_pmt_9_valid_empty(self):
        error = validate_field_length("PMT", 9, "", "TEST")
        assert error is None

    def test_pmt_9_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("PMT", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPMT_12Length:

    def test_pmt_12_valid_within_limit(self):
        value = "x" * 100
        error = validate_field_length("PMT", 12, value, "TEST")
        assert error is None

    def test_pmt_12_valid_empty(self):
        error = validate_field_length("PMT", 12, "", "TEST")
        assert error is None

    def test_pmt_12_invalid_exceeds_limit(self):
        value = "x" * 101
        error = validate_field_length("PMT", 12, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPRB_17Length:

    def test_prb_17_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("PRB", 17, value, "TEST")
        assert error is None

    def test_prb_17_valid_empty(self):
        error = validate_field_length("PRB", 17, "", "TEST")
        assert error is None

    def test_prb_17_invalid_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("PRB", 17, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPRB_20Length:

    def test_prb_20_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("PRB", 20, value, "TEST")
        assert error is None

    def test_prb_20_valid_empty(self):
        error = validate_field_length("PRB", 20, "", "TEST")
        assert error is None

    def test_prb_20_truncatable_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("PRB", 20, value, "TEST")
        assert error is None

class TestPRB_24Length:

    def test_prb_24_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("PRB", 24, value, "TEST")
        assert error is None

    def test_prb_24_valid_empty(self):
        error = validate_field_length("PRB", 24, "", "TEST")
        assert error is None

    def test_prb_24_invalid_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("PRB", 24, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPRC_4Length:

    def test_prc_4_valid_within_limit(self):
        value = "x" * 1
        error = validate_field_length("PRC", 4, value, "TEST")
        assert error is None

    def test_prc_4_valid_empty(self):
        error = validate_field_length("PRC", 4, "", "TEST")
        assert error is None

    def test_prc_4_invalid_exceeds_limit(self):
        value = "x" * 2
        error = validate_field_length("PRC", 4, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPRC_6Length:

    def test_prc_6_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("PRC", 6, value, "TEST")
        assert error is None

    def test_prc_6_valid_empty(self):
        error = validate_field_length("PRC", 6, "", "TEST")
        assert error is None

    def test_prc_6_invalid_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("PRC", 6, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPRC_7Length:

    def test_prc_7_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("PRC", 7, value, "TEST")
        assert error is None

    def test_prc_7_valid_empty(self):
        error = validate_field_length("PRC", 7, "", "TEST")
        assert error is None

    def test_prc_7_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("PRC", 7, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPRC_8Length:

    def test_prc_8_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("PRC", 8, value, "TEST")
        assert error is None

    def test_prc_8_valid_empty(self):
        error = validate_field_length("PRC", 8, "", "TEST")
        assert error is None

    def test_prc_8_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("PRC", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPRC_13Length:

    def test_prc_13_valid_within_limit(self):
        value = "x" * 1
        error = validate_field_length("PRC", 13, value, "TEST")
        assert error is None

    def test_prc_13_valid_empty(self):
        error = validate_field_length("PRC", 13, "", "TEST")
        assert error is None

    def test_prc_13_invalid_exceeds_limit(self):
        value = "x" * 2
        error = validate_field_length("PRC", 13, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPRC_18Length:

    def test_prc_18_valid_within_limit(self):
        value = "x" * 1
        error = validate_field_length("PRC", 18, value, "TEST")
        assert error is None

    def test_prc_18_valid_empty(self):
        error = validate_field_length("PRC", 18, "", "TEST")
        assert error is None

    def test_prc_18_invalid_exceeds_limit(self):
        value = "x" * 2
        error = validate_field_length("PRC", 18, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPSH_1Length:

    def test_psh_1_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("PSH", 1, value, "TEST")
        assert error is None

    def test_psh_1_valid_empty(self):
        error = validate_field_length("PSH", 1, "", "TEST")
        assert error is None

    def test_psh_1_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("PSH", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPSH_2Length:

    def test_psh_2_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("PSH", 2, value, "TEST")
        assert error is None

    def test_psh_2_valid_empty(self):
        error = validate_field_length("PSH", 2, "", "TEST")
        assert error is None

    def test_psh_2_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("PSH", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPSH_9Length:

    def test_psh_9_valid_within_limit(self):
        value = "x" * 600
        error = validate_field_length("PSH", 9, value, "TEST")
        assert error is None

    def test_psh_9_valid_empty(self):
        error = validate_field_length("PSH", 9, "", "TEST")
        assert error is None

    def test_psh_9_invalid_exceeds_limit(self):
        value = "x" * 601
        error = validate_field_length("PSH", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPSH_12Length:

    def test_psh_12_valid_within_limit(self):
        value = "x" * 600
        error = validate_field_length("PSH", 12, value, "TEST")
        assert error is None

    def test_psh_12_valid_empty(self):
        error = validate_field_length("PSH", 12, "", "TEST")
        assert error is None

    def test_psh_12_invalid_exceeds_limit(self):
        value = "x" * 601
        error = validate_field_length("PSH", 12, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPSH_13Length:

    def test_psh_13_valid_within_limit(self):
        value = "x" * 16
        error = validate_field_length("PSH", 13, value, "TEST")
        assert error is None

    def test_psh_13_valid_empty(self):
        error = validate_field_length("PSH", 13, "", "TEST")
        assert error is None

    def test_psh_13_invalid_exceeds_limit(self):
        value = "x" * 17
        error = validate_field_length("PSH", 13, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPSH_14Length:

    def test_psh_14_valid_within_limit(self):
        value = "x" * 16
        error = validate_field_length("PSH", 14, value, "TEST")
        assert error is None

    def test_psh_14_valid_empty(self):
        error = validate_field_length("PSH", 14, "", "TEST")
        assert error is None

    def test_psh_14_invalid_exceeds_limit(self):
        value = "x" * 17
        error = validate_field_length("PSH", 14, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestQAK_1Length:

    def test_qak_1_valid_within_limit(self):
        value = "x" * 32
        error = validate_field_length("QAK", 1, value, "TEST")
        assert error is None

    def test_qak_1_valid_empty(self):
        error = validate_field_length("QAK", 1, "", "TEST")
        assert error is None

    def test_qak_1_invalid_exceeds_limit(self):
        value = "x" * 33
        error = validate_field_length("QAK", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestQAK_4Length:

    def test_qak_4_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("QAK", 4, value, "TEST")
        assert error is None

    def test_qak_4_valid_empty(self):
        error = validate_field_length("QAK", 4, "", "TEST")
        assert error is None

    def test_qak_4_invalid_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("QAK", 4, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestQAK_5Length:

    def test_qak_5_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("QAK", 5, value, "TEST")
        assert error is None

    def test_qak_5_valid_empty(self):
        error = validate_field_length("QAK", 5, "", "TEST")
        assert error is None

    def test_qak_5_invalid_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("QAK", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestQAK_6Length:

    def test_qak_6_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("QAK", 6, value, "TEST")
        assert error is None

    def test_qak_6_valid_empty(self):
        error = validate_field_length("QAK", 6, "", "TEST")
        assert error is None

    def test_qak_6_invalid_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("QAK", 6, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestQID_1Length:

    def test_qid_1_valid_within_limit(self):
        value = "x" * 32
        error = validate_field_length("QID", 1, value, "TEST")
        assert error is None

    def test_qid_1_valid_empty(self):
        error = validate_field_length("QID", 1, "", "TEST")
        assert error is None

    def test_qid_1_invalid_exceeds_limit(self):
        value = "x" * 33
        error = validate_field_length("QID", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestQPD_2Length:

    def test_qpd_2_valid_within_limit(self):
        value = "x" * 32
        error = validate_field_length("QPD", 2, value, "TEST")
        assert error is None

    def test_qpd_2_valid_empty(self):
        error = validate_field_length("QPD", 2, "", "TEST")
        assert error is None

    def test_qpd_2_invalid_exceeds_limit(self):
        value = "x" * 33
        error = validate_field_length("QPD", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestQPD_3Length:

    def test_qpd_3_valid_within_limit(self):
        value = "x" * 256
        error = validate_field_length("QPD", 3, value, "TEST")
        assert error is None

    def test_qpd_3_valid_empty(self):
        error = validate_field_length("QPD", 3, "", "TEST")
        assert error is None

    def test_qpd_3_invalid_exceeds_limit(self):
        value = "x" * 257
        error = validate_field_length("QPD", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestQRI_1Length:

    def test_qri_1_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("QRI", 1, value, "TEST")
        assert error is None

    def test_qri_1_valid_empty(self):
        error = validate_field_length("QRI", 1, "", "TEST")
        assert error is None

    def test_qri_1_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("QRI", 1, value, "TEST")
        assert error is None

class TestRDF_1Length:

    def test_rdf_1_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("RDF", 1, value, "TEST")
        assert error is None

    def test_rdf_1_valid_empty(self):
        error = validate_field_length("RDF", 1, "", "TEST")
        assert error is None

    def test_rdf_1_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("RDF", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestREL_14Length:

    def test_rel_14_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("REL", 14, value, "TEST")
        assert error is None

    def test_rel_14_valid_empty(self):
        error = validate_field_length("REL", 14, "", "TEST")
        assert error is None

    def test_rel_14_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("REL", 14, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestREL_15Length:

    def test_rel_15_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("REL", 15, value, "TEST")
        assert error is None

    def test_rel_15_valid_empty(self):
        error = validate_field_length("REL", 15, "", "TEST")
        assert error is None

    def test_rel_15_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("REL", 15, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRQ1_1Length:

    def test_rq1_1_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("RQ1", 1, value, "TEST")
        assert error is None

    def test_rq1_1_valid_empty(self):
        error = validate_field_length("RQ1", 1, "", "TEST")
        assert error is None

    def test_rq1_1_invalid_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("RQ1", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRQ1_3Length:

    def test_rq1_3_valid_within_limit(self):
        value = "x" * 16
        error = validate_field_length("RQ1", 3, value, "TEST")
        assert error is None

    def test_rq1_3_valid_empty(self):
        error = validate_field_length("RQ1", 3, "", "TEST")
        assert error is None

    def test_rq1_3_invalid_exceeds_limit(self):
        value = "x" * 17
        error = validate_field_length("RQ1", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRQ1_5Length:

    def test_rq1_5_valid_within_limit(self):
        value = "x" * 16
        error = validate_field_length("RQ1", 5, value, "TEST")
        assert error is None

    def test_rq1_5_valid_empty(self):
        error = validate_field_length("RQ1", 5, "", "TEST")
        assert error is None

    def test_rq1_5_invalid_exceeds_limit(self):
        value = "x" * 17
        error = validate_field_length("RQ1", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRQD_5Length:

    def test_rqd_5_valid_within_limit(self):
        value = "x" * 6
        error = validate_field_length("RQD", 5, value, "TEST")
        assert error is None

    def test_rqd_5_valid_empty(self):
        error = validate_field_length("RQD", 5, "", "TEST")
        assert error is None

    def test_rqd_5_truncatable_exceeds_limit(self):
        value = "x" * 7
        error = validate_field_length("RQD", 5, value, "TEST")
        assert error is None

class TestRXV_5Length:

    def test_rxv_5_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXV", 5, value, "TEST")
        assert error is None

    def test_rxv_5_valid_empty(self):
        error = validate_field_length("RXV", 5, "", "TEST")
        assert error is None

    def test_rxv_5_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXV", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXV_8Length:

    def test_rxv_8_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXV", 8, value, "TEST")
        assert error is None

    def test_rxv_8_valid_empty(self):
        error = validate_field_length("RXV", 8, "", "TEST")
        assert error is None

    def test_rxv_8_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXV", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXV_10Length:

    def test_rxv_10_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXV", 10, value, "TEST")
        assert error is None

    def test_rxv_10_valid_empty(self):
        error = validate_field_length("RXV", 10, "", "TEST")
        assert error is None

    def test_rxv_10_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXV", 10, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXV_12Length:

    def test_rxv_12_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXV", 12, value, "TEST")
        assert error is None

    def test_rxv_12_valid_empty(self):
        error = validate_field_length("RXV", 12, "", "TEST")
        assert error is None

    def test_rxv_12_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXV", 12, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXV_14Length:

    def test_rxv_14_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXV", 14, value, "TEST")
        assert error is None

    def test_rxv_14_valid_empty(self):
        error = validate_field_length("RXV", 14, "", "TEST")
        assert error is None

    def test_rxv_14_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXV", 14, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXV_20Length:

    def test_rxv_20_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXV", 20, value, "TEST")
        assert error is None

    def test_rxv_20_valid_empty(self):
        error = validate_field_length("RXV", 20, "", "TEST")
        assert error is None

    def test_rxv_20_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXV", 20, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSAC_16Length:

    def test_sac_16_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("SAC", 16, value, "TEST")
        assert error is None

    def test_sac_16_valid_empty(self):
        error = validate_field_length("SAC", 16, "", "TEST")
        assert error is None

    def test_sac_16_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("SAC", 16, value, "TEST")
        assert error is None

class TestSAC_17Length:

    def test_sac_17_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("SAC", 17, value, "TEST")
        assert error is None

    def test_sac_17_valid_empty(self):
        error = validate_field_length("SAC", 17, "", "TEST")
        assert error is None

    def test_sac_17_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("SAC", 17, value, "TEST")
        assert error is None

class TestSAC_18Length:

    def test_sac_18_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("SAC", 18, value, "TEST")
        assert error is None

    def test_sac_18_valid_empty(self):
        error = validate_field_length("SAC", 18, "", "TEST")
        assert error is None

    def test_sac_18_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("SAC", 18, value, "TEST")
        assert error is None

class TestSAC_19Length:

    def test_sac_19_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("SAC", 19, value, "TEST")
        assert error is None

    def test_sac_19_valid_empty(self):
        error = validate_field_length("SAC", 19, "", "TEST")
        assert error is None

    def test_sac_19_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("SAC", 19, value, "TEST")
        assert error is None

class TestSAC_21Length:

    def test_sac_21_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("SAC", 21, value, "TEST")
        assert error is None

    def test_sac_21_valid_empty(self):
        error = validate_field_length("SAC", 21, "", "TEST")
        assert error is None

    def test_sac_21_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("SAC", 21, value, "TEST")
        assert error is None

class TestSAC_22Length:

    def test_sac_22_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("SAC", 22, value, "TEST")
        assert error is None

    def test_sac_22_valid_empty(self):
        error = validate_field_length("SAC", 22, "", "TEST")
        assert error is None

    def test_sac_22_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("SAC", 22, value, "TEST")
        assert error is None

class TestSAC_23Length:

    def test_sac_23_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("SAC", 23, value, "TEST")
        assert error is None

    def test_sac_23_valid_empty(self):
        error = validate_field_length("SAC", 23, "", "TEST")
        assert error is None

    def test_sac_23_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("SAC", 23, value, "TEST")
        assert error is None

class TestSAC_32Length:

    def test_sac_32_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("SAC", 32, value, "TEST")
        assert error is None

    def test_sac_32_valid_empty(self):
        error = validate_field_length("SAC", 32, "", "TEST")
        assert error is None

    def test_sac_32_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("SAC", 32, value, "TEST")
        assert error is None

class TestSAC_34Length:

    def test_sac_34_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("SAC", 34, value, "TEST")
        assert error is None

    def test_sac_34_valid_empty(self):
        error = validate_field_length("SAC", 34, "", "TEST")
        assert error is None

    def test_sac_34_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("SAC", 34, value, "TEST")
        assert error is None

class TestSAC_36Length:

    def test_sac_36_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("SAC", 36, value, "TEST")
        assert error is None

    def test_sac_36_valid_empty(self):
        error = validate_field_length("SAC", 36, "", "TEST")
        assert error is None

    def test_sac_36_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("SAC", 36, value, "TEST")
        assert error is None

class TestSAC_38Length:

    def test_sac_38_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("SAC", 38, value, "TEST")
        assert error is None

    def test_sac_38_valid_empty(self):
        error = validate_field_length("SAC", 38, "", "TEST")
        assert error is None

    def test_sac_38_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("SAC", 38, value, "TEST")
        assert error is None

class TestSCD_2Length:

    def test_scd_2_valid_within_limit(self):
        value = "x" * 16
        error = validate_field_length("SCD", 2, value, "TEST")
        assert error is None

    def test_scd_2_valid_empty(self):
        error = validate_field_length("SCD", 2, "", "TEST")
        assert error is None

    def test_scd_2_invalid_exceeds_limit(self):
        value = "x" * 17
        error = validate_field_length("SCD", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSCD_5Length:

    def test_scd_5_valid_within_limit(self):
        value = "x" * 16
        error = validate_field_length("SCD", 5, value, "TEST")
        assert error is None

    def test_scd_5_valid_empty(self):
        error = validate_field_length("SCD", 5, "", "TEST")
        assert error is None

    def test_scd_5_invalid_exceeds_limit(self):
        value = "x" * 17
        error = validate_field_length("SCD", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSCP_1Length:

    def test_scp_1_valid_within_limit(self):
        value = "x" * 2
        error = validate_field_length("SCP", 1, value, "TEST")
        assert error is None

    def test_scp_1_valid_empty(self):
        error = validate_field_length("SCP", 1, "", "TEST")
        assert error is None

    def test_scp_1_invalid_exceeds_limit(self):
        value = "x" * 3
        error = validate_field_length("SCP", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSCP_5Length:

    def test_scp_5_valid_within_limit(self):
        value = "x" * 999
        error = validate_field_length("SCP", 5, value, "TEST")
        assert error is None

    def test_scp_5_valid_empty(self):
        error = validate_field_length("SCP", 5, "", "TEST")
        assert error is None

    def test_scp_5_invalid_exceeds_limit(self):
        value = "x" * 1000
        error = validate_field_length("SCP", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSCP_6Length:

    def test_scp_6_valid_within_limit(self):
        value = "x" * 2
        error = validate_field_length("SCP", 6, value, "TEST")
        assert error is None

    def test_scp_6_valid_empty(self):
        error = validate_field_length("SCP", 6, "", "TEST")
        assert error is None

    def test_scp_6_invalid_exceeds_limit(self):
        value = "x" * 3
        error = validate_field_length("SCP", 6, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSDD_3Length:

    def test_sdd_3_valid_within_limit(self):
        value = "x" * 999
        error = validate_field_length("SDD", 3, value, "TEST")
        assert error is None

    def test_sdd_3_valid_empty(self):
        error = validate_field_length("SDD", 3, "", "TEST")
        assert error is None

    def test_sdd_3_invalid_exceeds_limit(self):
        value = "x" * 1000
        error = validate_field_length("SDD", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSDD_6Length:

    def test_sdd_6_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("SDD", 6, value, "TEST")
        assert error is None

    def test_sdd_6_valid_empty(self):
        error = validate_field_length("SDD", 6, "", "TEST")
        assert error is None

    def test_sdd_6_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("SDD", 6, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSDD_7Length:

    def test_sdd_7_valid_within_limit(self):
        value = "x" * 15
        error = validate_field_length("SDD", 7, value, "TEST")
        assert error is None

    def test_sdd_7_valid_empty(self):
        error = validate_field_length("SDD", 7, "", "TEST")
        assert error is None

    def test_sdd_7_invalid_exceeds_limit(self):
        value = "x" * 16
        error = validate_field_length("SDD", 7, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSFT_2Length:

    def test_sft_2_valid_within_limit(self):
        value = "x" * 15
        error = validate_field_length("SFT", 2, value, "TEST")
        assert error is None

    def test_sft_2_valid_empty(self):
        error = validate_field_length("SFT", 2, "", "TEST")
        assert error is None

    def test_sft_2_truncatable_exceeds_limit(self):
        value = "x" * 16
        error = validate_field_length("SFT", 2, value, "TEST")
        assert error is None

class TestSFT_3Length:

    def test_sft_3_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("SFT", 3, value, "TEST")
        assert error is None

    def test_sft_3_valid_empty(self):
        error = validate_field_length("SFT", 3, "", "TEST")
        assert error is None

    def test_sft_3_truncatable_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("SFT", 3, value, "TEST")
        assert error is None

class TestSFT_4Length:

    def test_sft_4_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("SFT", 4, value, "TEST")
        assert error is None

    def test_sft_4_valid_empty(self):
        error = validate_field_length("SFT", 4, "", "TEST")
        assert error is None

    def test_sft_4_truncatable_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("SFT", 4, value, "TEST")
        assert error is None

class TestSGH_2Length:

    def test_sgh_2_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("SGH", 2, value, "TEST")
        assert error is None

    def test_sgh_2_valid_empty(self):
        error = validate_field_length("SGH", 2, "", "TEST")
        assert error is None

    def test_sgh_2_truncatable_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("SGH", 2, value, "TEST")
        assert error is None

class TestSGT_2Length:

    def test_sgt_2_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("SGT", 2, value, "TEST")
        assert error is None

    def test_sgt_2_valid_empty(self):
        error = validate_field_length("SGT", 2, "", "TEST")
        assert error is None

    def test_sgt_2_truncatable_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("SGT", 2, value, "TEST")
        assert error is None

class TestSHP_8Length:

    def test_shp_8_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("SHP", 8, value, "TEST")
        assert error is None

    def test_shp_8_valid_empty(self):
        error = validate_field_length("SHP", 8, "", "TEST")
        assert error is None

    def test_shp_8_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("SHP", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSID_2Length:

    def test_sid_2_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("SID", 2, value, "TEST")
        assert error is None

    def test_sid_2_valid_empty(self):
        error = validate_field_length("SID", 2, "", "TEST")
        assert error is None

    def test_sid_2_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("SID", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSID_3Length:

    def test_sid_3_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("SID", 3, value, "TEST")
        assert error is None

    def test_sid_3_valid_empty(self):
        error = validate_field_length("SID", 3, "", "TEST")
        assert error is None

    def test_sid_3_invalid_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("SID", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSLT_2Length:

    def test_slt_2_valid_within_limit(self):
        value = "x" * 999
        error = validate_field_length("SLT", 2, value, "TEST")
        assert error is None

    def test_slt_2_valid_empty(self):
        error = validate_field_length("SLT", 2, "", "TEST")
        assert error is None

    def test_slt_2_invalid_exceeds_limit(self):
        value = "x" * 1000
        error = validate_field_length("SLT", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSLT_5Length:

    def test_slt_5_valid_within_limit(self):
        value = "x" * 30
        error = validate_field_length("SLT", 5, value, "TEST")
        assert error is None

    def test_slt_5_valid_empty(self):
        error = validate_field_length("SLT", 5, "", "TEST")
        assert error is None

    def test_slt_5_invalid_exceeds_limit(self):
        value = "x" * 31
        error = validate_field_length("SLT", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSPM_13Length:

    def test_spm_13_valid_within_limit(self):
        value = "x" * 6
        error = validate_field_length("SPM", 13, value, "TEST")
        assert error is None

    def test_spm_13_valid_empty(self):
        error = validate_field_length("SPM", 13, "", "TEST")
        assert error is None

    def test_spm_13_invalid_exceeds_limit(self):
        value = "x" * 7
        error = validate_field_length("SPM", 13, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSPM_26Length:

    def test_spm_26_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("SPM", 26, value, "TEST")
        assert error is None

    def test_spm_26_valid_empty(self):
        error = validate_field_length("SPM", 26, "", "TEST")
        assert error is None

    def test_spm_26_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("SPM", 26, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSTF_15Length:

    def test_stf_15_valid_within_limit(self):
        value = "x" * 40
        error = validate_field_length("STF", 15, value, "TEST")
        assert error is None

    def test_stf_15_valid_empty(self):
        error = validate_field_length("STF", 15, "", "TEST")
        assert error is None

    def test_stf_15_invalid_exceeds_limit(self):
        value = "x" * 41
        error = validate_field_length("STF", 15, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSTF_18Length:

    def test_stf_18_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("STF", 18, value, "TEST")
        assert error is None

    def test_stf_18_valid_empty(self):
        error = validate_field_length("STF", 18, "", "TEST")
        assert error is None

    def test_stf_18_truncatable_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("STF", 18, value, "TEST")
        assert error is None

class TestTCC_8Length:

    def test_tcc_8_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("TCC", 8, value, "TEST")
        assert error is None

    def test_tcc_8_valid_empty(self):
        error = validate_field_length("TCC", 8, "", "TEST")
        assert error is None

    def test_tcc_8_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("TCC", 8, value, "TEST")
        assert error is None

class TestVAR_6Length:

    def test_var_6_valid_within_limit(self):
        value = "x" * 512
        error = validate_field_length("VAR", 6, value, "TEST")
        assert error is None

    def test_var_6_valid_empty(self):
        error = validate_field_length("VAR", 6, "", "TEST")
        assert error is None

    def test_var_6_invalid_exceeds_limit(self):
        value = "x" * 513
        error = validate_field_length("VAR", 6, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestVND_3Length:

    def test_vnd_3_valid_within_limit(self):
        value = "x" * 999
        error = validate_field_length("VND", 3, value, "TEST")
        assert error is None

    def test_vnd_3_valid_empty(self):
        error = validate_field_length("VND", 3, "", "TEST")
        assert error is None

    def test_vnd_3_invalid_exceeds_limit(self):
        value = "x" * 1000
        error = validate_field_length("VND", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestZL7_1Length:

    def test_zl7_1_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("ZL7", 1, value, "TEST")
        assert error is None

    def test_zl7_1_valid_empty(self):
        error = validate_field_length("ZL7", 1, "", "TEST")
        assert error is None

    def test_zl7_1_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("ZL7", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestZL7_2Length:

    def test_zl7_2_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("ZL7", 2, value, "TEST")
        assert error is None

    def test_zl7_2_valid_empty(self):
        error = validate_field_length("ZL7", 2, "", "TEST")
        assert error is None

    def test_zl7_2_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("ZL7", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"
