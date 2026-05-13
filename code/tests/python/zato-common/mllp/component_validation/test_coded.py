from __future__ import annotations

from zato.hl7v2_rs import validate_datatype



class TestCCDComponentValidation:

    def test_ccd_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("CCD", components, "TEST.1")
        assert result.is_valid

    def test_ccd_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("CCD", components, "TEST.1")
        assert result.is_valid

class TestCDComponentValidation:

    def test_cd_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(6)]
        result = validate_datatype("CD", components, "TEST.1")
        assert result.is_valid

    def test_cd_valid_with_empty_optional(self):
        components = [[""] for _ in range(6)]
        result = validate_datatype("CD", components, "TEST.1")
        assert result.is_valid

class TestCFComponentValidation:

    def test_cf_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(22)]
        result = validate_datatype("CF", components, "TEST.1")
        assert result.is_valid

    def test_cf_valid_with_empty_optional(self):
        components = [[""] for _ in range(22)]
        result = validate_datatype("CF", components, "TEST.1")
        assert result.is_valid

class TestCNEComponentValidation:

    def test_cne_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(22)]
        result = validate_datatype("CNE", components, "TEST.1")
        assert result.is_valid

    def test_cne_valid_with_empty_optional(self):
        components = [[""] for _ in range(22)]
        result = validate_datatype("CNE", components, "TEST.1")
        assert result.is_valid

class TestCNNComponentValidation:

    def test_cnn_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(11)]
        result = validate_datatype("CNN", components, "TEST.1")
        assert result.is_valid

    def test_cnn_valid_with_empty_optional(self):
        components = [[""] for _ in range(11)]
        result = validate_datatype("CNN", components, "TEST.1")
        assert result.is_valid

class TestCPComponentValidation:

    def test_cp_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(6)]
        result = validate_datatype("CP", components, "TEST.1")
        assert result.is_valid

    def test_cp_valid_with_empty_optional(self):
        components = [[""] for _ in range(6)]
        result = validate_datatype("CP", components, "TEST.1")
        assert result.is_valid

class TestCSUComponentValidation:

    def test_csu_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(23)]
        result = validate_datatype("CSU", components, "TEST.1")
        assert result.is_valid

    def test_csu_valid_with_empty_optional(self):
        components = [[""] for _ in range(23)]
        result = validate_datatype("CSU", components, "TEST.1")
        assert result.is_valid

class TestCWEComponentValidation:

    def test_cwe_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(22)]
        result = validate_datatype("CWE", components, "TEST.1")
        assert result.is_valid

    def test_cwe_valid_with_empty_optional(self):
        components = [[""] for _ in range(22)]
        result = validate_datatype("CWE", components, "TEST.1")
        assert result.is_valid
