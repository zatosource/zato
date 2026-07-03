from __future__ import annotations

from hypothesis import given, strategies as st, settings, HealthCheck

from zato.fhir.r4_0_1 import cdshooksrequestgroup
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


class TestFuzzcdshooksrequestgroup:

    @given(fhir_safe_text)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cdshooksrequestgroup_id(self, value):
        r = cdshooksrequestgroup()
        r.id = value
        d = r.to_dict()
        assert d.get('resourceType') == 'cdshooksrequestgroup'

    @given(fhir_safe_text)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cdshooksrequestgroup_roundtrip(self, value):
        r = cdshooksrequestgroup()
        r.id = value
        json_str = r.to_json()
        r2 = cdshooksrequestgroup.from_json(json_str)
        assert r2.id == value

    @given(st.lists(fhir_safe_text, min_size=0, max_size=10))
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cdshooksrequestgroup_extension_values(self, values):
        r = cdshooksrequestgroup()
        r.id = 'fuzz-test'
        r.extension = [{'url': f'http://example.org/ext{i}', 'valueString': v} for i, v in enumerate(values)]
        d = r.to_dict()
        assert len(d.get('extension', [])) == len(values)

    @given(fhir_safe_text, fhir_safe_text)
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cdshooksrequestgroup_meta_fields(self, version_id, source):
        r = cdshooksrequestgroup()
        r.id = 'fuzz-test'
        r.meta = {'versionId': version_id, 'source': source}
        d = r.to_dict()
        assert d.get('meta', {}).get('versionId') == version_id

    @given(st.binary(min_size=0, max_size=200))
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_cdshooksrequestgroup_binary_to_string(self, data):
        r = cdshooksrequestgroup()
        r.id = data.decode('utf-8', errors='replace')
        d = r.to_dict()
        assert d.get('resourceType') == 'cdshooksrequestgroup'

    def test_cdshooksrequestgroup_validation_no_crash(self):
        r = cdshooksrequestgroup()
        r.id = 'test-validation'
        result = validate(r)
        assert result is not None
