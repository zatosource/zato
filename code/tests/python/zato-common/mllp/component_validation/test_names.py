from __future__ import annotations

from zato.hl7v2_rs import validate_datatype



class TestFNComponentValidation:

    def test_fn_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(5)]
        result = validate_datatype("FN", components, "TEST.1")
        assert result.is_valid

    def test_fn_valid_with_empty_optional(self):
        components = [[""] for _ in range(5)]
        result = validate_datatype("FN", components, "TEST.1")
        assert result.is_valid

class TestXCNComponentValidation:

    def test_xcn_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(25)]
        result = validate_datatype("XCN", components, "TEST.1")
        assert result.is_valid

    def test_xcn_valid_with_empty_optional(self):
        components = [[""] for _ in range(25)]
        result = validate_datatype("XCN", components, "TEST.1")
        assert result.is_valid

class TestXPNComponentValidation:

    def test_xpn_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(15)]
        result = validate_datatype("XPN", components, "TEST.1")
        assert result.is_valid

    def test_xpn_valid_with_empty_optional(self):
        components = [[""] for _ in range(15)]
        result = validate_datatype("XPN", components, "TEST.1")
        assert result.is_valid
