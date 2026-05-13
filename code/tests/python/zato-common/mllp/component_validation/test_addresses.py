from __future__ import annotations

from zato.hl7v2_rs import validate_datatype



class TestADComponentValidation:

    def test_ad_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(8)]
        result = validate_datatype("AD", components, "TEST.1")
        assert result.is_valid

    def test_ad_valid_with_empty_optional(self):
        components = [[""] for _ in range(8)]
        result = validate_datatype("AD", components, "TEST.1")
        assert result.is_valid

class TestSADComponentValidation:

    def test_sad_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("SAD", components, "TEST.1")
        assert result.is_valid

    def test_sad_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("SAD", components, "TEST.1")
        assert result.is_valid

class TestXADComponentValidation:

    def test_xad_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(23)]
        result = validate_datatype("XAD", components, "TEST.1")
        assert result.is_valid

    def test_xad_valid_with_empty_optional(self):
        components = [[""] for _ in range(23)]
        result = validate_datatype("XAD", components, "TEST.1")
        assert result.is_valid
