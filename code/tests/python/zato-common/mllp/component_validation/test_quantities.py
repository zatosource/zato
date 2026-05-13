from __future__ import annotations

from zato.hl7v2_rs import validate_datatype



class TestCQComponentValidation:

    def test_cq_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("CQ", components, "TEST.1")
        assert result.is_valid

    def test_cq_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("CQ", components, "TEST.1")
        assert result.is_valid

class TestMOComponentValidation:

    def test_mo_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("MO", components, "TEST.1")
        assert result.is_valid

    def test_mo_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("MO", components, "TEST.1")
        assert result.is_valid

class TestMOPComponentValidation:

    def test_mop_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("MOP", components, "TEST.1")
        assert result.is_valid

    def test_mop_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("MOP", components, "TEST.1")
        assert result.is_valid

class TestNAComponentValidation:

    def test_na_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(5)]
        result = validate_datatype("NA", components, "TEST.1")
        assert result.is_valid

    def test_na_valid_with_empty_optional(self):
        components = [[""] for _ in range(5)]
        result = validate_datatype("NA", components, "TEST.1")
        assert result.is_valid

class TestNRComponentValidation:

    def test_nr_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(2)]
        result = validate_datatype("NR", components, "TEST.1")
        assert result.is_valid

    def test_nr_valid_with_empty_optional(self):
        components = [[""] for _ in range(2)]
        result = validate_datatype("NR", components, "TEST.1")
        assert result.is_valid

class TestSNComponentValidation:

    def test_sn_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(4)]
        result = validate_datatype("SN", components, "TEST.1")
        assert result.is_valid

    def test_sn_valid_with_empty_optional(self):
        components = [[""] for _ in range(4)]
        result = validate_datatype("SN", components, "TEST.1")
        assert result.is_valid
