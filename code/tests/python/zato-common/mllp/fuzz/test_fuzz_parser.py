from __future__ import annotations

from hypothesis import given, strategies as st, settings, HealthCheck, assume

from zato.hl7v2.v2_9 import parse_message
from zato.hl7v2.tests.fakers import fake_msh, fake_pid, fake_evn, fake_pv1


hl7_safe_text = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cs",),
        blacklist_characters="\r\n|^~\\&"
    ),
    min_size=0,
    max_size=50
)


class TestFuzzParser:

    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_parser_random_input_no_crash(self, raw):
        try:
            parse_message(raw)
        except (ValueError, Exception):
            pass

    @given(st.binary(min_size=0, max_size=500))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_parser_binary_input_no_crash(self, raw):
        try:
            parse_message(raw.decode("utf-8", errors="replace"))
        except (ValueError, Exception):
            pass

    @given(hl7_safe_text, hl7_safe_text)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_parser_modified_pid_no_crash(self, family_name, given_name):
        raw = fake_msh("ADT", "A01", "ADT_A01") + fake_evn("A01") + fake_pid() + fake_pv1()
        try:
            msg = parse_message(raw)
            msg.set("PID.5.1", family_name)
            msg.set("PID.5.2", given_name)
        except (ValueError, Exception):
            pass

    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_parser_repeated_segments(self, count):
        raw = fake_msh("ADT", "A01", "ADT_A01") + fake_evn("A01")
        for _ in range(count):
            raw += fake_pid()
        raw += fake_pv1()
        try:
            parse_message(raw)
        except (ValueError, Exception):
            pass

