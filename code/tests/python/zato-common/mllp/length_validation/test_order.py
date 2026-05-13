from __future__ import annotations

from zato.hl7v2_rs import validate_field_length



class TestOBR_13Length:

    def test_obr_13_valid_within_limit(self):
        value = "x" * 300
        error = validate_field_length("OBR", 13, value, "TEST")
        assert error is None

    def test_obr_13_valid_empty(self):
        error = validate_field_length("OBR", 13, "", "TEST")
        assert error is None

    def test_obr_13_invalid_exceeds_limit(self):
        value = "x" * 301
        error = validate_field_length("OBR", 13, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOBR_18Length:

    def test_obr_18_valid_within_limit(self):
        value = "x" * 199
        error = validate_field_length("OBR", 18, value, "TEST")
        assert error is None

    def test_obr_18_valid_empty(self):
        error = validate_field_length("OBR", 18, "", "TEST")
        assert error is None

    def test_obr_18_invalid_exceeds_limit(self):
        value = "x" * 200
        error = validate_field_length("OBR", 18, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOBR_19Length:

    def test_obr_19_valid_within_limit(self):
        value = "x" * 199
        error = validate_field_length("OBR", 19, value, "TEST")
        assert error is None

    def test_obr_19_valid_empty(self):
        error = validate_field_length("OBR", 19, "", "TEST")
        assert error is None

    def test_obr_19_invalid_exceeds_limit(self):
        value = "x" * 200
        error = validate_field_length("OBR", 19, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOBR_20Length:

    def test_obr_20_valid_within_limit(self):
        value = "x" * 199
        error = validate_field_length("OBR", 20, value, "TEST")
        assert error is None

    def test_obr_20_valid_empty(self):
        error = validate_field_length("OBR", 20, "", "TEST")
        assert error is None

    def test_obr_20_invalid_exceeds_limit(self):
        value = "x" * 200
        error = validate_field_length("OBR", 20, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOBR_21Length:

    def test_obr_21_valid_within_limit(self):
        value = "x" * 199
        error = validate_field_length("OBR", 21, value, "TEST")
        assert error is None

    def test_obr_21_valid_empty(self):
        error = validate_field_length("OBR", 21, "", "TEST")
        assert error is None

    def test_obr_21_invalid_exceeds_limit(self):
        value = "x" * 200
        error = validate_field_length("OBR", 21, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOBR_37Length:

    def test_obr_37_valid_within_limit(self):
        value = "x" * 16
        error = validate_field_length("OBR", 37, value, "TEST")
        assert error is None

    def test_obr_37_valid_empty(self):
        error = validate_field_length("OBR", 37, "", "TEST")
        assert error is None

    def test_obr_37_invalid_exceeds_limit(self):
        value = "x" * 17
        error = validate_field_length("OBR", 37, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOBX_4Length:

    def test_obx_4_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("OBX", 4, value, "TEST")
        assert error is None

    def test_obx_4_valid_empty(self):
        error = validate_field_length("OBX", 4, "", "TEST")
        assert error is None

    def test_obx_4_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("OBX", 4, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOBX_7Length:

    def test_obx_7_valid_within_limit(self):
        value = "x" * 60
        error = validate_field_length("OBX", 7, value, "TEST")
        assert error is None

    def test_obx_7_valid_empty(self):
        error = validate_field_length("OBX", 7, "", "TEST")
        assert error is None

    def test_obx_7_invalid_exceeds_limit(self):
        value = "x" * 61
        error = validate_field_length("OBX", 7, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestOBX_9Length:

    def test_obx_9_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("OBX", 9, value, "TEST")
        assert error is None

    def test_obx_9_valid_empty(self):
        error = validate_field_length("OBX", 9, "", "TEST")
        assert error is None

    def test_obx_9_truncatable_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("OBX", 9, value, "TEST")
        assert error is None

class TestOBX_13Length:

    def test_obx_13_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("OBX", 13, value, "TEST")
        assert error is None

    def test_obx_13_valid_empty(self):
        error = validate_field_length("OBX", 13, "", "TEST")
        assert error is None

    def test_obx_13_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("OBX", 13, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXA_1Length:

    def test_rxa_1_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("RXA", 1, value, "TEST")
        assert error is None

    def test_rxa_1_valid_empty(self):
        error = validate_field_length("RXA", 1, "", "TEST")
        assert error is None

    def test_rxa_1_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("RXA", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXA_2Length:

    def test_rxa_2_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("RXA", 2, value, "TEST")
        assert error is None

    def test_rxa_2_valid_empty(self):
        error = validate_field_length("RXA", 2, "", "TEST")
        assert error is None

    def test_rxa_2_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("RXA", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXA_12Length:

    def test_rxa_12_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXA", 12, value, "TEST")
        assert error is None

    def test_rxa_12_valid_empty(self):
        error = validate_field_length("RXA", 12, "", "TEST")
        assert error is None

    def test_rxa_12_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXA", 12, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXA_15Length:

    def test_rxa_15_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXA", 15, value, "TEST")
        assert error is None

    def test_rxa_15_valid_empty(self):
        error = validate_field_length("RXA", 15, "", "TEST")
        assert error is None

    def test_rxa_15_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXA", 15, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXA_23Length:

    def test_rxa_23_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("RXA", 23, value, "TEST")
        assert error is None

    def test_rxa_23_valid_empty(self):
        error = validate_field_length("RXA", 23, "", "TEST")
        assert error is None

    def test_rxa_23_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("RXA", 23, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXC_8Length:

    def test_rxc_8_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("RXC", 8, value, "TEST")
        assert error is None

    def test_rxc_8_valid_empty(self):
        error = validate_field_length("RXC", 8, "", "TEST")
        assert error is None

    def test_rxc_8_truncatable_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("RXC", 8, value, "TEST")
        assert error is None

class TestRXD_1Length:

    def test_rxd_1_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("RXD", 1, value, "TEST")
        assert error is None

    def test_rxd_1_valid_empty(self):
        error = validate_field_length("RXD", 1, "", "TEST")
        assert error is None

    def test_rxd_1_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("RXD", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXD_7Length:

    def test_rxd_7_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXD", 7, value, "TEST")
        assert error is None

    def test_rxd_7_valid_empty(self):
        error = validate_field_length("RXD", 7, "", "TEST")
        assert error is None

    def test_rxd_7_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXD", 7, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXD_9Length:

    def test_rxd_9_valid_within_limit(self):
        value = "x" * 200
        error = validate_field_length("RXD", 9, value, "TEST")
        assert error is None

    def test_rxd_9_valid_empty(self):
        error = validate_field_length("RXD", 9, "", "TEST")
        assert error is None

    def test_rxd_9_invalid_exceeds_limit(self):
        value = "x" * 201
        error = validate_field_length("RXD", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXD_18Length:

    def test_rxd_18_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXD", 18, value, "TEST")
        assert error is None

    def test_rxd_18_valid_empty(self):
        error = validate_field_length("RXD", 18, "", "TEST")
        assert error is None

    def test_rxd_18_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXD", 18, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXD_28Length:

    def test_rxd_28_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("RXD", 28, value, "TEST")
        assert error is None

    def test_rxd_28_valid_empty(self):
        error = validate_field_length("RXD", 28, "", "TEST")
        assert error is None

    def test_rxd_28_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("RXD", 28, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXE_12Length:

    def test_rxe_12_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("RXE", 12, value, "TEST")
        assert error is None

    def test_rxe_12_valid_empty(self):
        error = validate_field_length("RXE", 12, "", "TEST")
        assert error is None

    def test_rxe_12_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("RXE", 12, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXE_15Length:

    def test_rxe_15_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXE", 15, value, "TEST")
        assert error is None

    def test_rxe_15_valid_empty(self):
        error = validate_field_length("RXE", 15, "", "TEST")
        assert error is None

    def test_rxe_15_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXE", 15, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXE_22Length:

    def test_rxe_22_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXE", 22, value, "TEST")
        assert error is None

    def test_rxe_22_valid_empty(self):
        error = validate_field_length("RXE", 22, "", "TEST")
        assert error is None

    def test_rxe_22_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXE", 22, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXE_23Length:

    def test_rxe_23_valid_within_limit(self):
        value = "x" * 6
        error = validate_field_length("RXE", 23, value, "TEST")
        assert error is None

    def test_rxe_23_valid_empty(self):
        error = validate_field_length("RXE", 23, "", "TEST")
        assert error is None

    def test_rxe_23_invalid_exceeds_limit(self):
        value = "x" * 7
        error = validate_field_length("RXE", 23, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXE_33Length:

    def test_rxe_33_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("RXE", 33, value, "TEST")
        assert error is None

    def test_rxe_33_valid_empty(self):
        error = validate_field_length("RXE", 33, "", "TEST")
        assert error is None

    def test_rxe_33_truncatable_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("RXE", 33, value, "TEST")
        assert error is None

class TestRXG_1Length:

    def test_rxg_1_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("RXG", 1, value, "TEST")
        assert error is None

    def test_rxg_1_valid_empty(self):
        error = validate_field_length("RXG", 1, "", "TEST")
        assert error is None

    def test_rxg_1_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("RXG", 1, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXG_2Length:

    def test_rxg_2_valid_within_limit(self):
        value = "x" * 4
        error = validate_field_length("RXG", 2, value, "TEST")
        assert error is None

    def test_rxg_2_valid_empty(self):
        error = validate_field_length("RXG", 2, "", "TEST")
        assert error is None

    def test_rxg_2_invalid_exceeds_limit(self):
        value = "x" * 5
        error = validate_field_length("RXG", 2, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXG_14Length:

    def test_rxg_14_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXG", 14, value, "TEST")
        assert error is None

    def test_rxg_14_valid_empty(self):
        error = validate_field_length("RXG", 14, "", "TEST")
        assert error is None

    def test_rxg_14_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXG", 14, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXG_15Length:

    def test_rxg_15_valid_within_limit(self):
        value = "x" * 6
        error = validate_field_length("RXG", 15, value, "TEST")
        assert error is None

    def test_rxg_15_valid_empty(self):
        error = validate_field_length("RXG", 15, "", "TEST")
        assert error is None

    def test_rxg_15_invalid_exceeds_limit(self):
        value = "x" * 7
        error = validate_field_length("RXG", 15, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXG_19Length:

    def test_rxg_19_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXG", 19, value, "TEST")
        assert error is None

    def test_rxg_19_valid_empty(self):
        error = validate_field_length("RXG", 19, "", "TEST")
        assert error is None

    def test_rxg_19_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXG", 19, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXG_23Length:

    def test_rxg_23_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("RXG", 23, value, "TEST")
        assert error is None

    def test_rxg_23_valid_empty(self):
        error = validate_field_length("RXG", 23, "", "TEST")
        assert error is None

    def test_rxg_23_truncatable_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("RXG", 23, value, "TEST")
        assert error is None

class TestRXO_13Length:

    def test_rxo_13_valid_within_limit(self):
        value = "x" * 3
        error = validate_field_length("RXO", 13, value, "TEST")
        assert error is None

    def test_rxo_13_valid_empty(self):
        error = validate_field_length("RXO", 13, "", "TEST")
        assert error is None

    def test_rxo_13_invalid_exceeds_limit(self):
        value = "x" * 4
        error = validate_field_length("RXO", 13, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXO_17Length:

    def test_rxo_17_valid_within_limit(self):
        value = "x" * 20
        error = validate_field_length("RXO", 17, value, "TEST")
        assert error is None

    def test_rxo_17_valid_empty(self):
        error = validate_field_length("RXO", 17, "", "TEST")
        assert error is None

    def test_rxo_17_invalid_exceeds_limit(self):
        value = "x" * 21
        error = validate_field_length("RXO", 17, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXO_21Length:

    def test_rxo_21_valid_within_limit(self):
        value = "x" * 6
        error = validate_field_length("RXO", 21, value, "TEST")
        assert error is None

    def test_rxo_21_valid_empty(self):
        error = validate_field_length("RXO", 21, "", "TEST")
        assert error is None

    def test_rxo_21_invalid_exceeds_limit(self):
        value = "x" * 7
        error = validate_field_length("RXO", 21, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestRXO_25Length:

    def test_rxo_25_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("RXO", 25, value, "TEST")
        assert error is None

    def test_rxo_25_valid_empty(self):
        error = validate_field_length("RXO", 25, "", "TEST")
        assert error is None

    def test_rxo_25_truncatable_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("RXO", 25, value, "TEST")
        assert error is None

class TestTQ1_10Length:

    def test_tq1_10_valid_within_limit(self):
        value = "x" * 250
        error = validate_field_length("TQ1", 10, value, "TEST")
        assert error is None

    def test_tq1_10_valid_empty(self):
        error = validate_field_length("TQ1", 10, "", "TEST")
        assert error is None

    def test_tq1_10_invalid_exceeds_limit(self):
        value = "x" * 251
        error = validate_field_length("TQ1", 10, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestTQ1_11Length:

    def test_tq1_11_valid_within_limit(self):
        value = "x" * 250
        error = validate_field_length("TQ1", 11, value, "TEST")
        assert error is None

    def test_tq1_11_valid_empty(self):
        error = validate_field_length("TQ1", 11, "", "TEST")
        assert error is None

    def test_tq1_11_invalid_exceeds_limit(self):
        value = "x" * 251
        error = validate_field_length("TQ1", 11, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestTQ1_14Length:

    def test_tq1_14_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("TQ1", 14, value, "TEST")
        assert error is None

    def test_tq1_14_valid_empty(self):
        error = validate_field_length("TQ1", 14, "", "TEST")
        assert error is None

    def test_tq1_14_invalid_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("TQ1", 14, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestTQ2_9Length:

    def test_tq2_9_valid_within_limit(self):
        value = "x" * 10
        error = validate_field_length("TQ2", 9, value, "TEST")
        assert error is None

    def test_tq2_9_valid_empty(self):
        error = validate_field_length("TQ2", 9, "", "TEST")
        assert error is None

    def test_tq2_9_invalid_exceeds_limit(self):
        value = "x" * 11
        error = validate_field_length("TQ2", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"
