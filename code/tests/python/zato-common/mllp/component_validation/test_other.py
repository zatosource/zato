from __future__ import annotations

from zato.hl7v2_rs import validate_datatype



class TestDLTComponentValidation:

    def test_dlt_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(4)]
        result = validate_datatype("DLT", components, "TEST.1")
        assert result.is_valid

    def test_dlt_valid_with_empty_optional(self):
        components = [[""] for _ in range(4)]
        result = validate_datatype("DLT", components, "TEST.1")
        assert result.is_valid

class TestEIPComponentValidation:

    def test_eip_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("EIP", components, "TEST.1")
        assert result.is_valid

    def test_eip_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("EIP", components, "TEST.1")
        assert result.is_valid

class TestMAComponentValidation:

    def test_ma_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(5)]
        result = validate_datatype("MA", components, "TEST.1")
        assert result.is_valid

    def test_ma_valid_with_empty_optional(self):
        components = [[""] for _ in range(5)]
        result = validate_datatype("MA", components, "TEST.1")
        assert result.is_valid

class TestMOCComponentValidation:

    def test_moc_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("MOC", components, "TEST.1")
        assert result.is_valid

    def test_moc_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("MOC", components, "TEST.1")
        assert result.is_valid

class TestOGComponentValidation:

    def test_og_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(4)]
        result = validate_datatype("OG", components, "TEST.1")
        assert result.is_valid

    def test_og_valid_with_empty_optional(self):
        components = [[""] for _ in range(4)]
        result = validate_datatype("OG", components, "TEST.1")
        assert result.is_valid

class TestPPNComponentValidation:

    def test_ppn_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(26)]
        result = validate_datatype("PPN", components, "TEST.1")
        assert result.is_valid

    def test_ppn_valid_with_empty_optional(self):
        components = [[""] for _ in range(26)]
        result = validate_datatype("PPN", components, "TEST.1")
        assert result.is_valid

class TestQSCComponentValidation:

    def test_qsc_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(4)]
        result = validate_datatype("QSC", components, "TEST.1")
        assert result.is_valid

    def test_qsc_valid_with_empty_optional(self):
        components = [[""] for _ in range(4)]
        result = validate_datatype("QSC", components, "TEST.1")
        assert result.is_valid

class TestRCDComponentValidation:

    def test_rcd_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("RCD", components, "TEST.1")
        assert result.is_valid

    def test_rcd_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("RCD", components, "TEST.1")
        assert result.is_valid

class TestRPComponentValidation:

    def test_rp_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(4)]
        result = validate_datatype("RP", components, "TEST.1")
        assert result.is_valid

    def test_rp_valid_with_empty_optional(self):
        components = [[""] for _ in range(4)]
        result = validate_datatype("RP", components, "TEST.1")
        assert result.is_valid

class TestVHComponentValidation:

    def test_vh_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(4)]
        result = validate_datatype("VH", components, "TEST.1")
        assert result.is_valid

    def test_vh_valid_with_empty_optional(self):
        components = [[""] for _ in range(4)]
        result = validate_datatype("VH", components, "TEST.1")
        assert result.is_valid

class TestVIDComponentValidation:

    def test_vid_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("VID", components, "TEST.1")
        assert result.is_valid

    def test_vid_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("VID", components, "TEST.1")
        assert result.is_valid
