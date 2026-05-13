from __future__ import annotations

from zato.hl7v2_rs import validate_datatype



class TestDRComponentValidation:

    def test_dr_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("DR", components, "TEST.1")
        assert result.is_valid

    def test_dr_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("DR", components, "TEST.1")
        assert result.is_valid

class TestRIComponentValidation:

    def test_ri_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("RI", components, "TEST.1")
        assert result.is_valid

    def test_ri_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("RI", components, "TEST.1")
        assert result.is_valid
