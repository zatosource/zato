from __future__ import annotations

from zato.hl7v2_rs import validate_datatype



class TestCXComponentValidation:

    def test_cx_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(12)]
        result = validate_datatype("CX", components, "TEST.1")
        assert result.is_valid

    def test_cx_valid_with_empty_optional(self):
        components = [[""] for _ in range(12)]
        result = validate_datatype("CX", components, "TEST.1")
        assert result.is_valid

class TestDLNComponentValidation:

    def test_dln_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("DLN", components, "TEST.1")
        assert result.is_valid

    def test_dln_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("DLN", components, "TEST.1")
        assert result.is_valid

class TestEIComponentValidation:

    def test_ei_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(4)]
        result = validate_datatype("EI", components, "TEST.1")
        assert result.is_valid

    def test_ei_valid_with_empty_optional(self):
        components = [[""] for _ in range(4)]
        result = validate_datatype("EI", components, "TEST.1")
        assert result.is_valid

class TestERLComponentValidation:

    def test_erl_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(6)]
        result = validate_datatype("ERL", components, "TEST.1")
        assert result.is_valid

    def test_erl_valid_with_empty_optional(self):
        components = [[""] for _ in range(6)]
        result = validate_datatype("ERL", components, "TEST.1")
        assert result.is_valid

class TestHDComponentValidation:

    def test_hd_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(3)]
        result = validate_datatype("HD", components, "TEST.1")
        assert result.is_valid

    def test_hd_valid_with_empty_optional(self):
        components = [[""] for _ in range(3)]
        result = validate_datatype("HD", components, "TEST.1")
        assert result.is_valid

class TestPLComponentValidation:

    def test_pl_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(11)]
        result = validate_datatype("PL", components, "TEST.1")
        assert result.is_valid

    def test_pl_valid_with_empty_optional(self):
        components = [[""] for _ in range(11)]
        result = validate_datatype("PL", components, "TEST.1")
        assert result.is_valid

class TestPLNComponentValidation:

    def test_pln_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(4)]
        result = validate_datatype("PLN", components, "TEST.1")
        assert result.is_valid

    def test_pln_valid_with_empty_optional(self):
        components = [[""] for _ in range(4)]
        result = validate_datatype("PLN", components, "TEST.1")
        assert result.is_valid

class TestXONComponentValidation:

    def test_xon_valid_with_all_components(self):
        components = [["value" + str(idx)] for idx in range(10)]
        result = validate_datatype("XON", components, "TEST.1")
        assert result.is_valid

    def test_xon_valid_with_empty_optional(self):
        components = [[""] for _ in range(10)]
        result = validate_datatype("XON", components, "TEST.1")
        assert result.is_valid
