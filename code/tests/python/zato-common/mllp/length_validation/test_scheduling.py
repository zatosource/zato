from __future__ import annotations

from zato.hl7v2_rs import validate_field_length



class TestAIG_6Length:

    def test_aig_6_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("AIG", 6, value, "TEST")
        assert error is None

    def test_aig_6_valid_empty(self):
        error = validate_field_length("AIG", 6, "", "TEST")
        assert error is None

    def test_aig_6_truncatable_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("AIG", 6, value, "TEST")
        assert error is None

class TestAPR_4Length:

    def test_apr_4_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("APR", 4, value, "TEST")
        assert error is None

    def test_apr_4_valid_empty(self):
        error = validate_field_length("APR", 4, "", "TEST")
        assert error is None

    def test_apr_4_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("APR", 4, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestARQ_3Length:

    def test_arq_3_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("ARQ", 3, value, "TEST")
        assert error is None

    def test_arq_3_valid_empty(self):
        error = validate_field_length("ARQ", 3, "", "TEST")
        assert error is None

    def test_arq_3_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("ARQ", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestARQ_9Length:

    def test_arq_9_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("ARQ", 9, value, "TEST")
        assert error is None

    def test_arq_9_valid_empty(self):
        error = validate_field_length("ARQ", 9, "", "TEST")
        assert error is None

    def test_arq_9_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("ARQ", 9, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestARQ_12Length:

    def test_arq_12_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("ARQ", 12, value, "TEST")
        assert error is None

    def test_arq_12_valid_empty(self):
        error = validate_field_length("ARQ", 12, "", "TEST")
        assert error is None

    def test_arq_12_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("ARQ", 12, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestARQ_14Length:

    def test_arq_14_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("ARQ", 14, value, "TEST")
        assert error is None

    def test_arq_14_valid_empty(self):
        error = validate_field_length("ARQ", 14, "", "TEST")
        assert error is None

    def test_arq_14_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("ARQ", 14, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"

class TestSCH_3Length:

    def test_sch_3_valid_within_limit(self):
        value = "x" * 5
        error = validate_field_length("SCH", 3, value, "TEST")
        assert error is None

    def test_sch_3_valid_empty(self):
        error = validate_field_length("SCH", 3, "", "TEST")
        assert error is None

    def test_sch_3_invalid_exceeds_limit(self):
        value = "x" * 6
        error = validate_field_length("SCH", 3, value, "TEST")
        assert error is not None
        assert error.code == "INVALID_LENGTH"
