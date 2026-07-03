from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import SampledData


class TestSampledData:

    def test_create(self):
        obj = SampledData()
        assert obj is not None

    def test_to_dict(self):
        obj = SampledData()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = SampledData()
        j = obj.to_json()
        assert isinstance(j, str)
