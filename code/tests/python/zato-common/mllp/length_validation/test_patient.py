from __future__ import annotations

from zato.hl7v2_rs import validate_field_length



class TestGT1_12Length:

    def test_gt1_12_valid_within_limit(self):
        value = "x" * 11
        error = validate_field_length("GT1", 12, value, "TEST")
        assert error is None

    def test_gt1_12_valid_empty(self):
        error = validate_field_length("GT1", 12, "", "TEST")
        assert error is None

    def test_gt1_12_invalid_exceeds_limit(self):
        value = "x" * 12
        error = validate_field_length("GT1", 12, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestGT1_28Length:

    def test_gt1_28_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("GT1", 28, value, "TEST")
        assert error is None

    def test_gt1_28_valid_empty(self):
        error = validate_field_length("GT1", 28, "", "TEST")
        assert error is None

    def test_gt1_28_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("GT1", 28, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestGT1_49Length:

    def test_gt1_49_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("GT1", 49, value, "TEST")
        assert error is None

    def test_gt1_49_valid_empty(self):
        error = validate_field_length("GT1", 49, "", "TEST")
        assert error is None

    def test_gt1_49_truncatable_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("GT1", 49, value, "TEST")
        assert error is None

class TestGT1_56Length:

    def test_gt1_56_valid_within_limit(self):
        value = "x" * 100
        error = validate_field_length("GT1", 56, value, "TEST")
        assert error is None

    def test_gt1_56_valid_empty(self):
        error = validate_field_length("GT1", 56, "", "TEST")
        assert error is None

    def test_gt1_56_truncatable_exceeds_limit(self):
        value = "x" * 101
        error = validate_field_length("GT1", 56, value, "TEST")
        assert error is None

class TestIN1_8Length:

    def test_in1_8_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("IN1", 8, value, "TEST")
        assert error is None

    def test_in1_8_valid_empty(self):
        error = validate_field_length("IN1", 8, "", "TEST")
        assert error is None

    def test_in1_8_invalid_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("IN1", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN1_22Length:

    def test_in1_22_valid_within_limit(self):
        value = "x" * 2
        error = validate_field_length("IN1", 22, value, "TEST")
        assert error is None

    def test_in1_22_valid_empty(self):
        error = validate_field_length("IN1", 22, "", "TEST")
        assert error is None

    def test_in1_22_invalid_exceeds_limit(self):
        value = "x" * 3
        error = validate_field_length("IN1", 22, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN1_28Length:

    def test_in1_28_valid_within_limit(self):
        value = "x" * 15
        error = validate_field_length("IN1", 28, value, "TEST")
        assert error is None

    def test_in1_28_valid_empty(self):
        error = validate_field_length("IN1", 28, "", "TEST")
        assert error is None

    def test_in1_28_invalid_exceeds_limit(self):
        value = "x" * 16
        error = validate_field_length("IN1", 28, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN1_33Length:

    def test_in1_33_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("IN1", 33, value, "TEST")
        assert error is None

    def test_in1_33_valid_empty(self):
        error = validate_field_length("IN1", 33, "", "TEST")
        assert error is None

    def test_in1_33_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("IN1", 33, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN1_34Length:

    def test_in1_34_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("IN1", 34, value, "TEST")
        assert error is None

    def test_in1_34_valid_empty(self):
        error = validate_field_length("IN1", 34, "", "TEST")
        assert error is None

    def test_in1_34_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("IN1", 34, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN1_36Length:

    def test_in1_36_valid_within_limit(self):
        value = "x" * 15
        error = validate_field_length("IN1", 36, value, "TEST")
        assert error is None

    def test_in1_36_valid_empty(self):
        error = validate_field_length("IN1", 36, "", "TEST")
        assert error is None

    def test_in1_36_invalid_exceeds_limit(self):
        value = "x" * 16
        error = validate_field_length("IN1", 36, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN1_39Length:

    def test_in1_39_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("IN1", 39, value, "TEST")
        assert error is None

    def test_in1_39_valid_empty(self):
        error = validate_field_length("IN1", 39, "", "TEST")
        assert error is None

    def test_in1_39_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("IN1", 39, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN1_45Length:

    def test_in1_45_valid_within_limit(self):
        value = "x" * 2
        error = validate_field_length("IN1", 45, value, "TEST")
        assert error is None

    def test_in1_45_valid_empty(self):
        error = validate_field_length("IN1", 45, "", "TEST")
        assert error is None

    def test_in1_45_invalid_exceeds_limit(self):
        value = "x" * 3
        error = validate_field_length("IN1", 45, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN2_2Length:

    def test_in2_2_valid_within_limit(self):
        value = "x" * 11
        error = validate_field_length("IN2", 2, value, "TEST")
        assert error is None

    def test_in2_2_valid_empty(self):
        error = validate_field_length("IN2", 2, "", "TEST")
        assert error is None

    def test_in2_2_invalid_exceeds_limit(self):
        value = "x" * 12
        error = validate_field_length("IN2", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN2_6Length:

    def test_in2_6_valid_within_limit(self):
        value = "x" * 15
        error = validate_field_length("IN2", 6, value, "TEST")
        assert error is None

    def test_in2_6_valid_empty(self):
        error = validate_field_length("IN2", 6, "", "TEST")
        assert error is None

    def test_in2_6_invalid_exceeds_limit(self):
        value = "x" * 16
        error = validate_field_length("IN2", 6, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN2_8Length:

    def test_in2_8_valid_within_limit(self):
        value = "x" * 15
        error = validate_field_length("IN2", 8, value, "TEST")
        assert error is None

    def test_in2_8_valid_empty(self):
        error = validate_field_length("IN2", 8, "", "TEST")
        assert error is None

    def test_in2_8_invalid_exceeds_limit(self):
        value = "x" * 16
        error = validate_field_length("IN2", 8, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN2_10Length:

    def test_in2_10_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("IN2", 10, value, "TEST")
        assert error is None

    def test_in2_10_valid_empty(self):
        error = validate_field_length("IN2", 10, "", "TEST")
        assert error is None

    def test_in2_10_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("IN2", 10, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN2_12Length:

    def test_in2_12_valid_within_limit(self):
        value = "x" * 25
        error = validate_field_length("IN2", 12, value, "TEST")
        assert error is None

    def test_in2_12_valid_empty(self):
        error = validate_field_length("IN2", 12, "", "TEST")
        assert error is None

    def test_in2_12_invalid_exceeds_limit(self):
        value = "x" * 26
        error = validate_field_length("IN2", 12, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN2_13Length:

    def test_in2_13_valid_within_limit(self):
        value = "x" * 25
        error = validate_field_length("IN2", 13, value, "TEST")
        assert error is None

    def test_in2_13_valid_empty(self):
        error = validate_field_length("IN2", 13, "", "TEST")
        assert error is None

    def test_in2_13_invalid_exceeds_limit(self):
        value = "x" * 26
        error = validate_field_length("IN2", 13, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN2_21Length:

    def test_in2_21_valid_within_limit(self):
        value = "x" * 1
        error = validate_field_length("IN2", 21, value, "TEST")
        assert error is None

    def test_in2_21_valid_empty(self):
        error = validate_field_length("IN2", 21, "", "TEST")
        assert error is None

    def test_in2_21_invalid_exceeds_limit(self):
        value = "x" * 2
        error = validate_field_length("IN2", 21, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestIN2_23Length:

    def test_in2_23_valid_within_limit(self):
        value = "x" * 30
        error = validate_field_length("IN2", 23, value, "TEST")
        assert error is None

    def test_in2_23_valid_empty(self):
        error = validate_field_length("IN2", 23, "", "TEST")
        assert error is None

    def test_in2_23_truncatable_exceeds_limit(self):
        value = "x" * 31
        error = validate_field_length("IN2", 23, value, "TEST")
        assert error is None

class TestIN2_46Length:

    def test_in2_46_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("IN2", 46, value, "TEST")
        assert error is None

    def test_in2_46_valid_empty(self):
        error = validate_field_length("IN2", 46, "", "TEST")
        assert error is None

    def test_in2_46_truncatable_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("IN2", 46, value, "TEST")
        assert error is None

class TestIN3_15Length:

    def test_in3_15_valid_within_limit(self):
        value = "x" * 48
        error = validate_field_length("IN3", 15, value, "TEST")
        assert error is None

    def test_in3_15_valid_empty(self):
        error = validate_field_length("IN3", 15, "", "TEST")
        assert error is None

    def test_in3_15_truncatable_exceeds_limit(self):
        value = "x" * 49
        error = validate_field_length("IN3", 15, value, "TEST")
        assert error is None

class TestIN3_21Length:

    def test_in3_21_valid_within_limit(self):
        value = "x" * 48
        error = validate_field_length("IN3", 21, value, "TEST")
        assert error is None

    def test_in3_21_valid_empty(self):
        error = validate_field_length("IN3", 21, "", "TEST")
        assert error is None

    def test_in3_21_truncatable_exceeds_limit(self):
        value = "x" * 49
        error = validate_field_length("IN3", 21, value, "TEST")
        assert error is None

class TestNK1_10Length:

    def test_nk1_10_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("NK1", 10, value, "TEST")
        assert error is None

    def test_nk1_10_valid_empty(self):
        error = validate_field_length("NK1", 10, "", "TEST")
        assert error is None

    def test_nk1_10_truncatable_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("NK1", 10, value, "TEST")
        assert error is None

class TestNK1_37Length:

    def test_nk1_37_valid_within_limit(self):
        value = "x" * 16
        error = validate_field_length("NK1", 37, value, "TEST")
        assert error is None

    def test_nk1_37_valid_empty(self):
        error = validate_field_length("NK1", 37, "", "TEST")
        assert error is None

    def test_nk1_37_truncatable_exceeds_limit(self):
        value = "x" * 17
        error = validate_field_length("NK1", 37, value, "TEST")
        assert error is None

class TestNK1_38Length:

    def test_nk1_38_valid_within_limit(self):
        value = "x" * 250
        error = validate_field_length("NK1", 38, value, "TEST")
        assert error is None

    def test_nk1_38_valid_empty(self):
        error = validate_field_length("NK1", 38, "", "TEST")
        assert error is None

    def test_nk1_38_truncatable_exceeds_limit(self):
        value = "x" * 251
        error = validate_field_length("NK1", 38, value, "TEST")
        assert error is None

class TestPID_23Length:

    def test_pid_23_valid_within_limit(self):
        value = "x" * 250
        error = validate_field_length("PID", 23, value, "TEST")
        assert error is None

    def test_pid_23_valid_empty(self):
        error = validate_field_length("PID", 23, "", "TEST")
        assert error is None

    def test_pid_23_truncatable_exceeds_limit(self):
        value = "x" * 251
        error = validate_field_length("PID", 23, value, "TEST")
        assert error is None

class TestPID_25Length:

    def test_pid_25_valid_within_limit(self):
        value = "x" * 2
        error = validate_field_length("PID", 25, value, "TEST")
        assert error is None

    def test_pid_25_valid_empty(self):
        error = validate_field_length("PID", 25, "", "TEST")
        assert error is None

    def test_pid_25_invalid_exceeds_limit(self):
        value = "x" * 3
        error = validate_field_length("PID", 25, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPID_37Length:

    def test_pid_37_valid_within_limit(self):
        value = "x" * 80
        error = validate_field_length("PID", 37, value, "TEST")
        assert error is None

    def test_pid_37_valid_empty(self):
        error = validate_field_length("PID", 37, "", "TEST")
        assert error is None

    def test_pid_37_invalid_exceeds_limit(self):
        value = "x" * 81
        error = validate_field_length("PID", 37, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPV1_26Length:

    def test_pv1_26_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("PV1", 26, value, "TEST")
        assert error is None

    def test_pv1_26_valid_empty(self):
        error = validate_field_length("PV1", 26, "", "TEST")
        assert error is None

    def test_pv1_26_invalid_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("PV1", 26, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPV1_27Length:

    def test_pv1_27_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("PV1", 27, value, "TEST")
        assert error is None

    def test_pv1_27_valid_empty(self):
        error = validate_field_length("PV1", 27, "", "TEST")
        assert error is None

    def test_pv1_27_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("PV1", 27, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPV1_32Length:

    def test_pv1_32_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("PV1", 32, value, "TEST")
        assert error is None

    def test_pv1_32_valid_empty(self):
        error = validate_field_length("PV1", 32, "", "TEST")
        assert error is None

    def test_pv1_32_invalid_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("PV1", 32, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPV1_33Length:

    def test_pv1_33_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("PV1", 33, value, "TEST")
        assert error is None

    def test_pv1_33_valid_empty(self):
        error = validate_field_length("PV1", 33, "", "TEST")
        assert error is None

    def test_pv1_33_invalid_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("PV1", 33, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPV1_46Length:

    def test_pv1_46_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("PV1", 46, value, "TEST")
        assert error is None

    def test_pv1_46_valid_empty(self):
        error = validate_field_length("PV1", 46, "", "TEST")
        assert error is None

    def test_pv1_46_invalid_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("PV1", 46, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPV1_47Length:

    def test_pv1_47_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("PV1", 47, value, "TEST")
        assert error is None

    def test_pv1_47_valid_empty(self):
        error = validate_field_length("PV1", 47, "", "TEST")
        assert error is None

    def test_pv1_47_invalid_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("PV1", 47, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPV1_48Length:

    def test_pv1_48_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("PV1", 48, value, "TEST")
        assert error is None

    def test_pv1_48_valid_empty(self):
        error = validate_field_length("PV1", 48, "", "TEST")
        assert error is None

    def test_pv1_48_invalid_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("PV1", 48, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPV1_49Length:

    def test_pv1_49_valid_within_limit(self):
        value = "x" * 12
        error = validate_field_length("PV1", 49, value, "TEST")
        assert error is None

    def test_pv1_49_valid_empty(self):
        error = validate_field_length("PV1", 49, "", "TEST")
        assert error is None

    def test_pv1_49_invalid_exceeds_limit(self):
        value = "x" * 13
        error = validate_field_length("PV1", 49, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPV1_53Length:

    def test_pv1_53_valid_within_limit(self):
        value = "x" * 50
        error = validate_field_length("PV1", 53, value, "TEST")
        assert error is None

    def test_pv1_53_valid_empty(self):
        error = validate_field_length("PV1", 53, "", "TEST")
        assert error is None

    def test_pv1_53_truncatable_exceeds_limit(self):
        value = "x" * 51
        error = validate_field_length("PV1", 53, value, "TEST")
        assert error is None

class TestPV2_5Length:

    def test_pv2_5_valid_within_limit(self):
        value = "x" * 25
        error = validate_field_length("PV2", 5, value, "TEST")
        assert error is None

    def test_pv2_5_valid_empty(self):
        error = validate_field_length("PV2", 5, "", "TEST")
        assert error is None

    def test_pv2_5_invalid_exceeds_limit(self):
        value = "x" * 26
        error = validate_field_length("PV2", 5, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPV2_6Length:

    def test_pv2_6_valid_within_limit(self):
        value = "x" * 25
        error = validate_field_length("PV2", 6, value, "TEST")
        assert error is None

    def test_pv2_6_valid_empty(self):
        error = validate_field_length("PV2", 6, "", "TEST")
        assert error is None

    def test_pv2_6_invalid_exceeds_limit(self):
        value = "x" * 26
        error = validate_field_length("PV2", 6, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPV2_10Length:

    def test_pv2_10_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("PV2", 10, value, "TEST")
        assert error is None

    def test_pv2_10_valid_empty(self):
        error = validate_field_length("PV2", 10, "", "TEST")
        assert error is None

    def test_pv2_10_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("PV2", 10, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPV2_11Length:

    def test_pv2_11_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("PV2", 11, value, "TEST")
        assert error is None

    def test_pv2_11_valid_empty(self):
        error = validate_field_length("PV2", 11, "", "TEST")
        assert error is None

    def test_pv2_11_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("PV2", 11, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestPV2_12Length:

    def test_pv2_12_valid_within_limit(self):
        value = "x" * 50
        error = validate_field_length("PV2", 12, value, "TEST")
        assert error is None

    def test_pv2_12_valid_empty(self):
        error = validate_field_length("PV2", 12, "", "TEST")
        assert error is None

    def test_pv2_12_truncatable_exceeds_limit(self):
        value = "x" * 51
        error = validate_field_length("PV2", 12, value, "TEST")
        assert error is None

class TestPV2_20Length:

    def test_pv2_20_valid_within_limit(self):
        value = "x" * 1
        error = validate_field_length("PV2", 20, value, "TEST")
        assert error is None

    def test_pv2_20_valid_empty(self):
        error = validate_field_length("PV2", 20, "", "TEST")
        assert error is None

    def test_pv2_20_invalid_exceeds_limit(self):
        value = "x" * 2
        error = validate_field_length("PV2", 20, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"
