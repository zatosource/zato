from __future__ import annotations

from zato.hl7v2_rs import validate_datatype



class TestXTNComponentValidation:

    def test_xtn_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(18)]
        result = validate_datatype("XTN", components, "TEST.1")
        assert result.is_valid

    def test_xtn_valid_with_empty_optional(self):
        components = [[""] for _ in range(18)]
        result = validate_datatype("XTN", components, "TEST.1")
        assert result.is_valid
