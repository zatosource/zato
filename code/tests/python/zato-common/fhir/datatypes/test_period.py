from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Period


class TestPeriod:

    def test_create(self):
        obj = Period()
        assert obj is not None

    def test_to_dict(self):
        obj = Period()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Period()
        j = obj.to_json()
        assert isinstance(j, str)
