from __future__ import annotations

from hypothesis import given, strategies as st, settings, HealthCheck

from zato.hl7v2_rs import is_valid_table_value, validate_table_value, get_table_codes


class TestFuzzTableValidation:

    @given(st.integers(min_value=0, max_value=10000), st.text(min_size=0, max_size=50))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_is_valid_no_crash(self, table_id, value):
        result = is_valid_table_value(table_id, value)
        assert isinstance(result, bool)

    @given(st.integers(min_value=0, max_value=10000), st.text(min_size=0, max_size=50))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_validate_no_crash(self, table_id, value):
        result = validate_table_value(table_id, value, "TEST.1")
        assert hasattr(result, "is_valid")
        assert hasattr(result, "errors")

    @given(st.integers(min_value=0, max_value=10000))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_get_codes_no_crash(self, table_id):
        result = get_table_codes(table_id)
        assert result is None or isinstance(result, list)

    @given(st.sampled_from([1, 2, 3, 4, 7, 8, 76, 103, 104]))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_known_tables_have_codes(self, table_id):
        codes = get_table_codes(table_id)
        assert codes is not None
        assert len(codes) > 0
        for code in codes:
            assert is_valid_table_value(table_id, code)

