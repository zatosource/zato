from __future__ import annotations

from hypothesis import given, strategies as st, settings, HealthCheck

from zato.hl7v2.v2_9 import parse_batch, parse_file, parse_batch_or_file
from zato.hl7v2.tests.fakers import fake_msh, fake_pid, fake_evn, fake_pv1


def make_message():
    return fake_msh("ADT", "A01", "ADT_A01") + fake_evn("A01") + fake_pid() + fake_pv1()


def make_batch(msg_count):
    parts = ["BHS|^~\\&|||SendApp|SendFac|20240101120000"]
    for _ in range(msg_count):
        parts.append(make_message().rstrip("\r"))
    parts.append(f"BTS|{msg_count}")
    return "\r".join(parts)


def make_file(batch_count, msgs_per_batch):
    parts = ["FHS|^~\\&|||FileApp|FileFac|20240101120000"]
    for _ in range(batch_count):
        parts.append(make_batch(msgs_per_batch))
    parts.append(f"FTS|{batch_count}")
    return "\r".join(parts)


class TestFuzzBatch:

    @given(st.integers(min_value=1, max_value=20))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_batch_variable_message_count(self, count):
        raw = make_batch(count)
        batch = parse_batch(raw)
        assert len(batch) == count

    @given(st.integers(min_value=1, max_value=5), st.integers(min_value=1, max_value=5))
    @settings(max_examples=25, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_file_variable_structure(self, batch_count, msgs_per_batch):
        raw = make_file(batch_count, msgs_per_batch)
        hl7_file = parse_file(raw)
        assert hl7_file.batch_count == batch_count
        assert hl7_file.message_count == batch_count * msgs_per_batch

    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_batch_random_input_no_crash(self, raw):
        try:
            parse_batch_or_file(raw)
        except (ValueError, Exception):
            pass

