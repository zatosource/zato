from __future__ import annotations

from zato.hl7v2_rs import validate_field_length



class TestMFE_2Length:

    def test_mfe_2_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("MFE", 2, value, "TEST")
        assert error is None

    def test_mfe_2_valid_empty(self):
        error = validate_field_length("MFE", 2, "", "TEST")
        assert error is None

    def test_mfe_2_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("MFE", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM1_1Length:

    def test_om1_1_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("OM1", 1, value, "TEST")
        assert error is None

    def test_om1_1_valid_empty(self):
        error = validate_field_length("OM1", 1, "", "TEST")
        assert error is None

    def test_om1_1_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("OM1", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM1_6Length:

    def test_om1_6_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("OM1", 6, value, "TEST")
        assert error is None

    def test_om1_6_valid_empty(self):
        error = validate_field_length("OM1", 6, "", "TEST")
        assert error is None

    def test_om1_6_truncatable_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("OM1", 6, value, "TEST")
        assert error is None

class TestOM1_8Length:

    def test_om1_8_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("OM1", 8, value, "TEST")
        assert error is None

    def test_om1_8_valid_empty(self):
        error = validate_field_length("OM1", 8, "", "TEST")
        assert error is None

    def test_om1_8_truncatable_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("OM1", 8, value, "TEST")
        assert error is None

class TestOM1_9Length:

    def test_om1_9_valid_within_limit(self):
        value = "x" * 30
        error = validate_field_length("OM1", 9, value, "TEST")
        assert error is None

    def test_om1_9_valid_empty(self):
        error = validate_field_length("OM1", 9, "", "TEST")
        assert error is None

    def test_om1_9_truncatable_exceeds_limit(self):
        value = "x" * 31
        error = validate_field_length("OM1", 9, value, "TEST")
        assert error is None

class TestOM1_11Length:

    def test_om1_11_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("OM1", 11, value, "TEST")
        assert error is None

    def test_om1_11_valid_empty(self):
        error = validate_field_length("OM1", 11, "", "TEST")
        assert error is None

    def test_om1_11_invalid_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("OM1", 11, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM1_20Length:

    def test_om1_20_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("OM1", 20, value, "TEST")
        assert error is None

    def test_om1_20_valid_empty(self):
        error = validate_field_length("OM1", 20, "", "TEST")
        assert error is None

    def test_om1_20_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("OM1", 20, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM1_37Length:

    def test_om1_37_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("OM1", 37, value, "TEST")
        assert error is None

    def test_om1_37_valid_empty(self):
        error = validate_field_length("OM1", 37, "", "TEST")
        assert error is None

    def test_om1_37_invalid_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("OM1", 37, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM1_39Length:

    def test_om1_39_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("OM1", 39, value, "TEST")
        assert error is None

    def test_om1_39_valid_empty(self):
        error = validate_field_length("OM1", 39, "", "TEST")
        assert error is None

    def test_om1_39_invalid_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("OM1", 39, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM1_40Length:

    def test_om1_40_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("OM1", 40, value, "TEST")
        assert error is None

    def test_om1_40_valid_empty(self):
        error = validate_field_length("OM1", 40, "", "TEST")
        assert error is None

    def test_om1_40_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("OM1", 40, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM1_44Length:

    def test_om1_44_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("OM1", 44, value, "TEST")
        assert error is None

    def test_om1_44_valid_empty(self):
        error = validate_field_length("OM1", 44, "", "TEST")
        assert error is None

    def test_om1_44_invalid_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("OM1", 44, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM2_1Length:

    def test_om2_1_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("OM2", 1, value, "TEST")
        assert error is None

    def test_om2_1_valid_empty(self):
        error = validate_field_length("OM2", 1, "", "TEST")
        assert error is None

    def test_om2_1_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("OM2", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM2_3Length:

    def test_om2_3_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("OM2", 3, value, "TEST")
        assert error is None

    def test_om2_3_valid_empty(self):
        error = validate_field_length("OM2", 3, "", "TEST")
        assert error is None

    def test_om2_3_invalid_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("OM2", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM2_5Length:

    def test_om2_5_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("OM2", 5, value, "TEST")
        assert error is None

    def test_om2_5_valid_empty(self):
        error = validate_field_length("OM2", 5, "", "TEST")
        assert error is None

    def test_om2_5_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("OM2", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM3_1Length:

    def test_om3_1_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("OM3", 1, value, "TEST")
        assert error is None

    def test_om3_1_valid_empty(self):
        error = validate_field_length("OM3", 1, "", "TEST")
        assert error is None

    def test_om3_1_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("OM3", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM4_1Length:

    def test_om4_1_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("OM4", 1, value, "TEST")
        assert error is None

    def test_om4_1_valid_empty(self):
        error = validate_field_length("OM4", 1, "", "TEST")
        assert error is None

    def test_om4_1_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("OM4", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM4_3Length:

    def test_om4_3_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("OM4", 3, value, "TEST")
        assert error is None

    def test_om4_3_valid_empty(self):
        error = validate_field_length("OM4", 3, "", "TEST")
        assert error is None

    def test_om4_3_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("OM4", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM4_4Length:

    def test_om4_4_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("OM4", 4, value, "TEST")
        assert error is None

    def test_om4_4_valid_empty(self):
        error = validate_field_length("OM4", 4, "", "TEST")
        assert error is None

    def test_om4_4_truncatable_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("OM4", 4, value, "TEST")
        assert error is None

class TestOM5_1Length:

    def test_om5_1_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("OM5", 1, value, "TEST")
        assert error is None

    def test_om5_1_valid_empty(self):
        error = validate_field_length("OM5", 1, "", "TEST")
        assert error is None

    def test_om5_1_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("OM5", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM6_1Length:

    def test_om6_1_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("OM6", 1, value, "TEST")
        assert error is None

    def test_om6_1_valid_empty(self):
        error = validate_field_length("OM6", 1, "", "TEST")
        assert error is None

    def test_om6_1_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("OM6", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM7_1Length:

    def test_om7_1_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("OM7", 1, value, "TEST")
        assert error is None

    def test_om7_1_valid_empty(self):
        error = validate_field_length("OM7", 1, "", "TEST")
        assert error is None

    def test_om7_1_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("OM7", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM7_4Length:

    def test_om7_4_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("OM7", 4, value, "TEST")
        assert error is None

    def test_om7_4_valid_empty(self):
        error = validate_field_length("OM7", 4, "", "TEST")
        assert error is None

    def test_om7_4_invalid_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("OM7", 4, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM7_5Length:

    def test_om7_5_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("OM7", 5, value, "TEST")
        assert error is None

    def test_om7_5_valid_empty(self):
        error = validate_field_length("OM7", 5, "", "TEST")
        assert error is None

    def test_om7_5_truncatable_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("OM7", 5, value, "TEST")
        assert error is None

class TestOM7_8Length:

    def test_om7_8_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("OM7", 8, value, "TEST")
        assert error is None

    def test_om7_8_valid_empty(self):
        error = validate_field_length("OM7", 8, "", "TEST")
        assert error is None

    def test_om7_8_truncatable_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("OM7", 8, value, "TEST")
        assert error is None

class TestOM7_10Length:

    def test_om7_10_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("OM7", 10, value, "TEST")
        assert error is None

    def test_om7_10_valid_empty(self):
        error = validate_field_length("OM7", 10, "", "TEST")
        assert error is None

    def test_om7_10_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("OM7", 10, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOM7_15Length:

    def test_om7_15_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("OM7", 15, value, "TEST")
        assert error is None

    def test_om7_15_valid_empty(self):
        error = validate_field_length("OM7", 15, "", "TEST")
        assert error is None

    def test_om7_15_truncatable_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("OM7", 15, value, "TEST")
        assert error is None

class TestOM7_17Length:

    def test_om7_17_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("OM7", 17, value, "TEST")
        assert error is None

    def test_om7_17_valid_empty(self):
        error = validate_field_length("OM7", 17, "", "TEST")
        assert error is None

    def test_om7_17_truncatable_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("OM7", 17, value, "TEST")
        assert error is None

class TestOM7_22Length:

    def test_om7_22_valid_within_limit(self):
        value = "x" * 1
        error = validate_field_length("OM7", 22, value, "TEST")
        assert error is None

    def test_om7_22_valid_empty(self):
        error = validate_field_length("OM7", 22, "", "TEST")
        assert error is None

    def test_om7_22_invalid_exceeds_limit(self):
        value = "x" * 2
        error = validate_field_length("OM7", 22, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"
