from __future__ import annotations

from hypothesis import given, strategies as st, settings, HealthCheck

from zato.hl7v2.v2_9 import parse_message, serialize
from zato.hl7v2.tests.fakers import fake_msh, fake_pid, fake_evn, fake_pv1


hl7_safe_text = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cs",),
        blacklist_characters="\r\n|^~\\&"
    ),
    min_size=1,
    max_size=50
)


class TestFuzzSerialization:

    @given(hl7_safe_text)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_roundtrip_family_name(self, value):
        raw = fake_msh("ADT", "A01", "ADT_A01") + fake_evn("A01") + fake_pid() + fake_pv1()
        msg = parse_message(raw)
        msg.set("PID.5.1", value)
        serialized = serialize(msg)
        msg2 = parse_message(serialized)
        assert msg2.get("PID.5.1") == value

    @given(hl7_safe_text, hl7_safe_text)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_roundtrip_multiple_fields(self, family, given_name):
        raw = fake_msh("ADT", "A01", "ADT_A01") + fake_evn("A01") + fake_pid() + fake_pv1()
        msg = parse_message(raw)
        msg.set("PID.5.1", family)
        msg.set("PID.5.2", given_name)
        serialized = serialize(msg)
        msg2 = parse_message(serialized)
        assert msg2.get("PID.5.1") == family
        assert msg2.get("PID.5.2") == given_name

    @given(st.lists(hl7_safe_text, min_size=1, max_size=10))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_roundtrip_many_modifications(self, values):
        raw = fake_msh("ADT", "A01", "ADT_A01") + fake_evn("A01") + fake_pid() + fake_pv1()
        msg = parse_message(raw)
        for i, v in enumerate(values[:5]):            msg.set(f"PID.5.{i+1}", v)
        serialized = serialize(msg)
        msg2 = parse_message(serialized)
        for i, v in enumerate(values[:5]):
            assert msg2.get(f"PID.5.{i+1}") == v

