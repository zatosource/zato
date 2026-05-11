from __future__ import annotations

from hypothesis import given, strategies as st, settings, HealthCheck

from zato.hl7v2.v2_9 import parse_message
from zato.hl7v2.tests.fakers import fake_msh, fake_pid, fake_evn, fake_pv1


segment_ids = st.sampled_from(["MSH", "PID", "EVN", "PV1", "msh", "pid", "evn", "pv1", "Msh", "Pid"])
field_names = st.sampled_from(["1", "2", "3", "4", "5", "patient_name", "PATIENT_NAME", "Patient_Name"])
component_names = st.sampled_from(["1", "2", "3", "family_name", "FAMILY_NAME", "xpn_1", "XPN_1"])


class TestFuzzPathAccess:

    @given(segment_ids, field_names)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_get_segment_field(self, seg, field):
        raw = fake_msh("ADT", "A01", "ADT_A01") + fake_evn("A01") + fake_pid() + fake_pv1()
        msg = parse_message(raw)
        try:
            msg.get(f"{seg}.{field}")
        except (ValueError, KeyError, AttributeError):
            pass

    @given(segment_ids, field_names, component_names)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_get_segment_field_component(self, seg, field, comp):
        raw = fake_msh("ADT", "A01", "ADT_A01") + fake_evn("A01") + fake_pid() + fake_pv1()
        msg = parse_message(raw)
        try:
            msg.get(f"{seg}.{field}.{comp}")
        except (ValueError, KeyError, AttributeError):
            pass

    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_get_random_path(self, path):
        raw = fake_msh("ADT", "A01", "ADT_A01") + fake_evn("A01") + fake_pid() + fake_pv1()
        msg = parse_message(raw)
        try:
            msg.get(path)
        except (ValueError, KeyError, AttributeError, IndexError):
            pass

    @given(st.text(min_size=1, max_size=50), st.text(min_size=0, max_size=50))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_set_random_path(self, path, value):
        raw = fake_msh("ADT", "A01", "ADT_A01") + fake_evn("A01") + fake_pid() + fake_pv1()
        msg = parse_message(raw)
        try:
            msg.set(path, value)
        except (ValueError, KeyError, AttributeError, IndexError):
            pass

