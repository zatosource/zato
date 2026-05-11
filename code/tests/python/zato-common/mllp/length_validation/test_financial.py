from __future__ import annotations

from zato.hl7v2_rs import validate_field_length



class TestADJ_8Length:

    def test_adj_8_valid_within_limit(self):
        value = "x" * 250
        error = validate_field_length("ADJ", 8, value, "TEST")
        assert error is None

    def test_adj_8_valid_empty(self):
        error = validate_field_length("ADJ", 8, "", "TEST")
        assert error is None

    def test_adj_8_truncatable_exceeds_limit(self):
        value = "x" * 251
        error = validate_field_length("ADJ", 8, value, "TEST")
        assert error is None

class TestADJ_9Length:

    def test_adj_9_valid_within_limit(self):
        value = "x" * 16
        error = validate_field_length("ADJ", 9, value, "TEST")
        assert error is None

    def test_adj_9_valid_empty(self):
        error = validate_field_length("ADJ", 9, "", "TEST")
        assert error is None

    def test_adj_9_invalid_exceeds_limit(self):
        value = "x" * 17
        error = validate_field_length("ADJ", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestADJ_10Length:

    def test_adj_10_valid_within_limit(self):
        value = "x" * 16
        error = validate_field_length("ADJ", 10, value, "TEST")
        assert error is None

    def test_adj_10_valid_empty(self):
        error = validate_field_length("ADJ", 10, "", "TEST")
        assert error is None

    def test_adj_10_invalid_exceeds_limit(self):
        value = "x" * 17
        error = validate_field_length("ADJ", 10, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestFT1_10Length:

    def test_ft1_10_valid_within_limit(self):
        value = "x" * 6
        error = validate_field_length("FT1", 10, value, "TEST")
        assert error is None

    def test_ft1_10_valid_empty(self):
        error = validate_field_length("FT1", 10, "", "TEST")
        assert error is None

    def test_ft1_10_invalid_exceeds_limit(self):
        value = "x" * 7
        error = validate_field_length("FT1", 10, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestFT1_35Length:

    def test_ft1_35_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("FT1", 35, value, "TEST")
        assert error is None

    def test_ft1_35_valid_empty(self):
        error = validate_field_length("FT1", 35, "", "TEST")
        assert error is None

    def test_ft1_35_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("FT1", 35, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestFT1_42Length:

    def test_ft1_42_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("FT1", 42, value, "TEST")
        assert error is None

    def test_ft1_42_valid_empty(self):
        error = validate_field_length("FT1", 42, "", "TEST")
        assert error is None

    def test_ft1_42_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("FT1", 42, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestGP2_2Length:

    def test_gp2_2_valid_within_limit(self):
        value = "x" * 7
        error = validate_field_length("GP2", 2, value, "TEST")
        assert error is None

    def test_gp2_2_valid_empty(self):
        error = validate_field_length("GP2", 2, "", "TEST")
        assert error is None

    def test_gp2_2_truncatable_exceeds_limit(self):
        value = "x" * 8
        error = validate_field_length("GP2", 2, value, "TEST")
        assert error is None

class TestGP2_14Length:

    def test_gp2_14_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("GP2", 14, value, "TEST")
        assert error is None

    def test_gp2_14_valid_empty(self):
        error = validate_field_length("GP2", 14, "", "TEST")
        assert error is None

    def test_gp2_14_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("GP2", 14, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPSG_6Length:

    def test_psg_6_valid_within_limit(self):
        value = "x" * 254
        error = validate_field_length("PSG", 6, value, "TEST")
        assert error is None

    def test_psg_6_valid_empty(self):
        error = validate_field_length("PSG", 6, "", "TEST")
        assert error is None

    def test_psg_6_truncatable_exceeds_limit(self):
        value = "x" * 255
        error = validate_field_length("PSG", 6, value, "TEST")
        assert error is None

class TestPSL_9Length:

    def test_psl_9_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("PSL", 9, value, "TEST")
        assert error is None

    def test_psl_9_valid_empty(self):
        error = validate_field_length("PSL", 9, "", "TEST")
        assert error is None

    def test_psl_9_truncatable_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("PSL", 9, value, "TEST")
        assert error is None

class TestPSL_14Length:

    def test_psl_14_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("PSL", 14, value, "TEST")
        assert error is None

    def test_psl_14_valid_empty(self):
        error = validate_field_length("PSL", 14, "", "TEST")
        assert error is None

    def test_psl_14_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("PSL", 14, value, "TEST")
        assert error is None

class TestPSL_18Length:

    def test_psl_18_valid_within_limit(self):
        value = "x" * 40
        error = validate_field_length("PSL", 18, value, "TEST")
        assert error is None

    def test_psl_18_valid_empty(self):
        error = validate_field_length("PSL", 18, "", "TEST")
        assert error is None

    def test_psl_18_invalid_exceeds_limit(self):
        value = "x" * 41
        error = validate_field_length("PSL", 18, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPSL_24Length:

    def test_psl_24_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("PSL", 24, value, "TEST")
        assert error is None

    def test_psl_24_valid_empty(self):
        error = validate_field_length("PSL", 24, "", "TEST")
        assert error is None

    def test_psl_24_truncatable_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("PSL", 24, value, "TEST")
        assert error is None

class TestPSL_27Length:

    def test_psl_27_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("PSL", 27, value, "TEST")
        assert error is None

    def test_psl_27_valid_empty(self):
        error = validate_field_length("PSL", 27, "", "TEST")
        assert error is None

    def test_psl_27_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("PSL", 27, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPSL_34Length:

    def test_psl_34_valid_within_limit(self):
        value = "x" * 6
        error = validate_field_length("PSL", 34, value, "TEST")
        assert error is None

    def test_psl_34_valid_empty(self):
        error = validate_field_length("PSL", 34, "", "TEST")
        assert error is None

    def test_psl_34_truncatable_exceeds_limit(self):
        value = "x" * 7
        error = validate_field_length("PSL", 34, value, "TEST")
        assert error is None

class TestPSL_36Length:

    def test_psl_36_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("PSL", 36, value, "TEST")
        assert error is None

    def test_psl_36_valid_empty(self):
        error = validate_field_length("PSL", 36, "", "TEST")
        assert error is None

    def test_psl_36_truncatable_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("PSL", 36, value, "TEST")
        assert error is None

class TestPSL_37Length:

    def test_psl_37_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("PSL", 37, value, "TEST")
        assert error is None

    def test_psl_37_valid_empty(self):
        error = validate_field_length("PSL", 37, "", "TEST")
        assert error is None

    def test_psl_37_truncatable_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("PSL", 37, value, "TEST")
        assert error is None

class TestPSL_39Length:

    def test_psl_39_valid_within_limit(self):
        value = "x" * 6
        error = validate_field_length("PSL", 39, value, "TEST")
        assert error is None

    def test_psl_39_valid_empty(self):
        error = validate_field_length("PSL", 39, "", "TEST")
        assert error is None

    def test_psl_39_truncatable_exceeds_limit(self):
        value = "x" * 7
        error = validate_field_length("PSL", 39, value, "TEST")
        assert error is None

class TestPSL_41Length:

    def test_psl_41_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("PSL", 41, value, "TEST")
        assert error is None

    def test_psl_41_valid_empty(self):
        error = validate_field_length("PSL", 41, "", "TEST")
        assert error is None

    def test_psl_41_truncatable_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("PSL", 41, value, "TEST")
        assert error is None

class TestPSL_42Length:

    def test_psl_42_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("PSL", 42, value, "TEST")
        assert error is None

    def test_psl_42_valid_empty(self):
        error = validate_field_length("PSL", 42, "", "TEST")
        assert error is None

    def test_psl_42_truncatable_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("PSL", 42, value, "TEST")
        assert error is None

class TestPSL_45Length:

    def test_psl_45_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("PSL", 45, value, "TEST")
        assert error is None

    def test_psl_45_valid_empty(self):
        error = validate_field_length("PSL", 45, "", "TEST")
        assert error is None

    def test_psl_45_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("PSL", 45, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPSL_48Length:

    def test_psl_48_valid_within_limit(self):
        value = "x" * 255
        error = validate_field_length("PSL", 48, value, "TEST")
        assert error is None

    def test_psl_48_valid_empty(self):
        error = validate_field_length("PSL", 48, "", "TEST")
        assert error is None

    def test_psl_48_invalid_exceeds_limit(self):
        value = "x" * 256
        error = validate_field_length("PSL", 48, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPSS_5Length:

    def test_pss_5_valid_within_limit(self):
        value = "x" * 254
        error = validate_field_length("PSS", 5, value, "TEST")
        assert error is None

    def test_pss_5_valid_empty(self):
        error = validate_field_length("PSS", 5, "", "TEST")
        assert error is None

    def test_pss_5_truncatable_exceeds_limit(self):
        value = "x" * 255
        error = validate_field_length("PSS", 5, value, "TEST")
        assert error is None
