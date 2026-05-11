from __future__ import annotations

from zato.hl7v2_rs import validate_datatype



class TestAUIComponentValidation:

    def test_aui_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("AUI", components, "TEST.1")
        assert result.is_valid

    def test_aui_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("AUI", components, "TEST.1")
        assert result.is_valid

class TestCCPComponentValidation:

    def test_ccp_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("CCP", components, "TEST.1")
        assert result.is_valid

    def test_ccp_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("CCP", components, "TEST.1")
        assert result.is_valid

class TestFCComponentValidation:

    def test_fc_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("FC", components, "TEST.1")
        assert result.is_valid

    def test_fc_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("FC", components, "TEST.1")
        assert result.is_valid

class TestJCCComponentValidation:

    def test_jcc_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("JCC", components, "TEST.1")
        assert result.is_valid

    def test_jcc_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("JCC", components, "TEST.1")
        assert result.is_valid

class TestMSGComponentValidation:

    def test_msg_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("MSG", components, "TEST.1")
        assert result.is_valid

    def test_msg_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("MSG", components, "TEST.1")
        assert result.is_valid

class TestPIPComponentValidation:

    def test_pip_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(5)]
        result = validate_datatype("PIP", components, "TEST.1")
        assert result.is_valid

    def test_pip_valid_with_empty_optional(self):
        components = [[""] for _ in range(5)]
        result = validate_datatype("PIP", components, "TEST.1")
        assert result.is_valid

class TestPTComponentValidation:

    def test_pt_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("PT", components, "TEST.1")
        assert result.is_valid

    def test_pt_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("PT", components, "TEST.1")
        assert result.is_valid

class TestQIPComponentValidation:

    def test_qip_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("QIP", components, "TEST.1")
        assert result.is_valid

    def test_qip_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("QIP", components, "TEST.1")
        assert result.is_valid

class TestRPTComponentValidation:

    def test_rpt_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(11)]
        result = validate_datatype("RPT", components, "TEST.1")
        assert result.is_valid

    def test_rpt_valid_with_empty_optional(self):
        components = [[""] for _ in range(11)]
        result = validate_datatype("RPT", components, "TEST.1")
        assert result.is_valid

class TestSCVComponentValidation:

    def test_scv_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("SCV", components, "TEST.1")
        assert result.is_valid

    def test_scv_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("SCV", components, "TEST.1")
        assert result.is_valid

class TestSRTComponentValidation:

    def test_srt_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("SRT", components, "TEST.1")
        assert result.is_valid

    def test_srt_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("SRT", components, "TEST.1")
        assert result.is_valid

class TestWVIComponentValidation:

    def test_wvi_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("WVI", components, "TEST.1")
        assert result.is_valid

    def test_wvi_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("WVI", components, "TEST.1")
        assert result.is_valid

class TestWVSComponentValidation:

    def test_wvs_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("WVS", components, "TEST.1")
        assert result.is_valid

    def test_wvs_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("WVS", components, "TEST.1")
        assert result.is_valid
