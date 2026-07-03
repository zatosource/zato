from __future__ import annotations

from hypothesis import given, strategies as st, settings, HealthCheck

from zato.fhir.r4_0_1 import DeviceRequest
from zato.fhir.validation import validate


fhir_safe_text = st.text(
    alphabet=st.characters(
        blacklist_categories=("Cs",),
        blacklist_characters="\x00"
    ),
    min_size=0,
    max_size=100
)

fhir_code = st.text(
    alphabet=st.sampled_from("abcdefghijklmnopqrstuvwxyz0123456789-"),
    min_size=1,
    max_size=20
)


class TestFuzzDeviceRequest:

    @given(fhir_safe_text)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_device_request_id(self, value: str) -> None:
        r = DeviceRequest()
        r.id = value
        d = r.to_dict()
        assert d.get('resourceType') == 'DeviceRequest'

    @given(fhir_safe_text)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_device_request_roundtrip(self, value: str) -> None:
        r = DeviceRequest()
        r.id = value
        json_str = r.to_json()
        r2 = DeviceRequest.from_json(json_str)
        assert r2.id == value

    @given(st.lists(fhir_safe_text, min_size=0, max_size=10))
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_device_request_extension_values(self, values: list[str]) -> None:
        r = DeviceRequest()
        r.id = 'fuzz-test'
        r.extension = [{'url': f'http://example.org/ext{i}', 'valueString': v} for i, v in enumerate(values)]
        d = r.to_dict()
        assert len(d.get('extension', [])) == len(values)

    @given(fhir_safe_text, fhir_safe_text)
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_device_request_meta_fields(self, version_id: str, source: str) -> None:
        r = DeviceRequest()
        r.id = 'fuzz-test'
        r.meta = {'versionId': version_id, 'source': source}
        d = r.to_dict()
        assert d.get('meta', {}).get('versionId') == version_id

    @given(st.binary(min_size=0, max_size=200))
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_device_request_binary_to_string(self, data: bytes) -> None:
        r = DeviceRequest()
        r.id = data.decode('utf-8', errors='replace')
        d = r.to_dict()
        assert d.get('resourceType') == 'DeviceRequest'

    def test_device_request_validation_no_crash(self) -> None:
        r = DeviceRequest()
        r.id = 'test-validation'
        result = validate(r)
        assert result is not None
