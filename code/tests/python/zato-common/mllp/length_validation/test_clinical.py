from __future__ import annotations

from zato.hl7v2_rs import validate_field_length



class TestABS_12Length:

    def test_abs_12_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("ABS", 12, value, "TEST")
        assert error is None

    def test_abs_12_valid_empty(self):
        error = validate_field_length("ABS", 12, "", "TEST")
        assert error is None

    def test_abs_12_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("ABS", 12, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestACC_3Length:

    def test_acc_3_valid_within_limit(self):
        value = "x" * 25
        error = validate_field_length("ACC", 3, value, "TEST")
        assert error is None

    def test_acc_3_valid_empty(self):
        error = validate_field_length("ACC", 3, "", "TEST")
        assert error is None

    def test_acc_3_truncatable_exceeds_limit(self):
        value = "x" * 26
        error = validate_field_length("ACC", 3, value, "TEST")
        assert error is None

class TestACC_8Length:

    def test_acc_8_valid_within_limit(self):
        value = "x" * 1000
        error = validate_field_length("ACC", 8, value, "TEST")
        assert error is None

    def test_acc_8_valid_empty(self):
        error = validate_field_length("ACC", 8, "", "TEST")
        assert error is None

    def test_acc_8_invalid_exceeds_limit(self):
        value = "x" * 1001
        error = validate_field_length("ACC", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestACC_9Length:

    def test_acc_9_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("ACC", 9, value, "TEST")
        assert error is None

    def test_acc_9_valid_empty(self):
        error = validate_field_length("ACC", 9, "", "TEST")
        assert error is None

    def test_acc_9_invalid_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("ACC", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestACC_12Length:

    def test_acc_12_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("ACC", 12, value, "TEST")
        assert error is None

    def test_acc_12_valid_empty(self):
        error = validate_field_length("ACC", 12, "", "TEST")
        assert error is None

    def test_acc_12_truncatable_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("ACC", 12, value, "TEST")
        assert error is None

class TestAL1_5Length:

    def test_al1_5_valid_within_limit(self):
        value = "x" * 15
        error = validate_field_length("AL1", 5, value, "TEST")
        assert error is None

    def test_al1_5_valid_empty(self):
        error = validate_field_length("AL1", 5, "", "TEST")
        assert error is None

    def test_al1_5_invalid_exceeds_limit(self):
        value = "x" * 16
        error = validate_field_length("AL1", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestDG1_15Length:

    def test_dg1_15_valid_within_limit(self):
        value = "x" * 2
        error = validate_field_length("DG1", 15, value, "TEST")
        assert error is None

    def test_dg1_15_valid_empty(self):
        error = validate_field_length("DG1", 15, "", "TEST")
        assert error is None

    def test_dg1_15_invalid_exceeds_limit(self):
        value = "x" * 3
        error = validate_field_length("DG1", 15, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestDRG_6Length:

    def test_drg_6_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("DRG", 6, value, "TEST")
        assert error is None

    def test_drg_6_valid_empty(self):
        error = validate_field_length("DRG", 6, "", "TEST")
        assert error is None

    def test_drg_6_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("DRG", 6, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestDRG_15Length:

    def test_drg_15_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("DRG", 15, value, "TEST")
        assert error is None

    def test_drg_15_valid_empty(self):
        error = validate_field_length("DRG", 15, "", "TEST")
        assert error is None

    def test_drg_15_truncatable_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("DRG", 15, value, "TEST")
        assert error is None

class TestDRG_18Length:

    def test_drg_18_valid_within_limit(self):
        value = "x" * 100
        error = validate_field_length("DRG", 18, value, "TEST")
        assert error is None

    def test_drg_18_valid_empty(self):
        error = validate_field_length("DRG", 18, "", "TEST")
        assert error is None

    def test_drg_18_truncatable_exceeds_limit(self):
        value = "x" * 101
        error = validate_field_length("DRG", 18, value, "TEST")
        assert error is None

class TestDRG_19Length:

    def test_drg_19_valid_within_limit(self):
        value = "x" * 100
        error = validate_field_length("DRG", 19, value, "TEST")
        assert error is None

    def test_drg_19_valid_empty(self):
        error = validate_field_length("DRG", 19, "", "TEST")
        assert error is None

    def test_drg_19_truncatable_exceeds_limit(self):
        value = "x" * 101
        error = validate_field_length("DRG", 19, value, "TEST")
        assert error is None

class TestDRG_25Length:

    def test_drg_25_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("DRG", 25, value, "TEST")
        assert error is None

    def test_drg_25_valid_empty(self):
        error = validate_field_length("DRG", 25, "", "TEST")
        assert error is None

    def test_drg_25_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("DRG", 25, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIAM_5Length:

    def test_iam_5_valid_within_limit(self):
        value = "x" * 15
        error = validate_field_length("IAM", 5, value, "TEST")
        assert error is None

    def test_iam_5_valid_empty(self):
        error = validate_field_length("IAM", 5, "", "TEST")
        assert error is None

    def test_iam_5_invalid_exceeds_limit(self):
        value = "x" * 16
        error = validate_field_length("IAM", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIAM_8Length:

    def test_iam_8_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("IAM", 8, value, "TEST")
        assert error is None

    def test_iam_8_valid_empty(self):
        error = validate_field_length("IAM", 8, "", "TEST")
        assert error is None

    def test_iam_8_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("IAM", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIAM_12Length:

    def test_iam_12_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("IAM", 12, value, "TEST")
        assert error is None

    def test_iam_12_valid_empty(self):
        error = validate_field_length("IAM", 12, "", "TEST")
        assert error is None

    def test_iam_12_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("IAM", 12, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPR1_7Length:

    def test_pr1_7_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("PR1", 7, value, "TEST")
        assert error is None

    def test_pr1_7_valid_empty(self):
        error = validate_field_length("PR1", 7, "", "TEST")
        assert error is None

    def test_pr1_7_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("PR1", 7, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPR1_10Length:

    def test_pr1_10_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("PR1", 10, value, "TEST")
        assert error is None

    def test_pr1_10_valid_empty(self):
        error = validate_field_length("PR1", 10, "", "TEST")
        assert error is None

    def test_pr1_10_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("PR1", 10, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"
