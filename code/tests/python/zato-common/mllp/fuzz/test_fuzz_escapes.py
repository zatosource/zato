from __future__ import annotations

from hypothesis import given, strategies as st, settings, HealthCheck

from zato.hl7v2_rs import decode_escapes, encode_escapes


class TestFuzzEscapes:

    @given(st.text(min_size=0, max_size=200))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_decode_no_crash(self, value):
        try:
            decode_escapes(value, "\\")
        except Exception:
            pass

    @given(st.text(min_size=0, max_size=200))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_encode_no_crash(self, value):
        try:
            encode_escapes(value, "|", "^", "~", "\\", "&")
        except Exception:
            pass

    @given(st.text(alphabet=st.characters(blacklist_categories=("Cs",)), min_size=1, max_size=100))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_encode_decode_roundtrip(self, value):
        encoded = encode_escapes(value, "|", "^", "~", "\\", "&")
        decoded = decode_escapes(encoded, "\\")
        assert decoded == value

