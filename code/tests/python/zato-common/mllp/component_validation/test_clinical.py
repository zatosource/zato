from __future__ import annotations

from zato.hl7v2_rs import validate_datatype



class TestDDIComponentValidation:

    def test_ddi_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("DDI", components, "TEST.1")
        assert result.is_valid

    def test_ddi_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("DDI", components, "TEST.1")
        assert result.is_valid

class TestDINComponentValidation:

    def test_din_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("DIN", components, "TEST.1")
        assert result.is_valid

    def test_din_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("DIN", components, "TEST.1")
        assert result.is_valid

class TestDLDComponentValidation:

    def test_dld_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("DLD", components, "TEST.1")
        assert result.is_valid

    def test_dld_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("DLD", components, "TEST.1")
        assert result.is_valid

class TestDTNComponentValidation:

    def test_dtn_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("DTN", components, "TEST.1")
        assert result.is_valid

    def test_dtn_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("DTN", components, "TEST.1")
        assert result.is_valid

class TestEDComponentValidation:

    def test_ed_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(5)]
        result = validate_datatype("ED", components, "TEST.1")
        assert result.is_valid

    def test_ed_valid_with_empty_optional(self):
        components = [[""] for _ in range(5)]
        result = validate_datatype("ED", components, "TEST.1")
        assert result.is_valid

class TestICDComponentValidation:

    def test_icd_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("ICD", components, "TEST.1")
        assert result.is_valid

    def test_icd_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("ICD", components, "TEST.1")
        assert result.is_valid

class TestNDLComponentValidation:

    def test_ndl_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(11)]
        result = validate_datatype("NDL", components, "TEST.1")
        assert result.is_valid

    def test_ndl_valid_with_empty_optional(self):
        components = [[""] for _ in range(11)]
        result = validate_datatype("NDL", components, "TEST.1")
        assert result.is_valid

class TestOCDComponentValidation:

    def test_ocd_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("OCD", components, "TEST.1")
        assert result.is_valid

    def test_ocd_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("OCD", components, "TEST.1")
        assert result.is_valid

class TestOSPComponentValidation:

    def test_osp_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("OSP", components, "TEST.1")
        assert result.is_valid

    def test_osp_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("OSP", components, "TEST.1")
        assert result.is_valid

class TestPRLComponentValidation:

    def test_prl_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("PRL", components, "TEST.1")
        assert result.is_valid

    def test_prl_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("PRL", components, "TEST.1")
        assert result.is_valid

class TestPTAComponentValidation:

    def test_pta_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(4)]
        result = validate_datatype("PTA", components, "TEST.1")
        assert result.is_valid

    def test_pta_valid_with_empty_optional(self):
        components = [[""] for _ in range(4)]
        result = validate_datatype("PTA", components, "TEST.1")
        assert result.is_valid

class TestRFRComponentValidation:

    def test_rfr_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(7)]
        result = validate_datatype("RFR", components, "TEST.1")
        assert result.is_valid

    def test_rfr_valid_with_empty_optional(self):
        components = [[""] for _ in range(7)]
        result = validate_datatype("RFR", components, "TEST.1")
        assert result.is_valid

class TestRMCComponentValidation:

    def test_rmc_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(4)]
        result = validate_datatype("RMC", components, "TEST.1")
        assert result.is_valid

    def test_rmc_valid_with_empty_optional(self):
        components = [[""] for _ in range(4)]
        result = validate_datatype("RMC", components, "TEST.1")
        assert result.is_valid

class TestSPDComponentValidation:

    def test_spd_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(4)]
        result = validate_datatype("SPD", components, "TEST.1")
        assert result.is_valid

    def test_spd_valid_with_empty_optional(self):
        components = [[""] for _ in range(4)]
        result = validate_datatype("SPD", components, "TEST.1")
        assert result.is_valid

class TestUVCComponentValidation:

    def test_uvc_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(4)]
        result = validate_datatype("UVC", components, "TEST.1")
        assert result.is_valid

    def test_uvc_valid_with_empty_optional(self):
        components = [[""] for _ in range(4)]
        result = validate_datatype("UVC", components, "TEST.1")
        assert result.is_valid

class TestVRComponentValidation:

    def test_vr_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("VR", components, "TEST.1")
        assert result.is_valid

    def test_vr_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("VR", components, "TEST.1")
        assert result.is_valid
