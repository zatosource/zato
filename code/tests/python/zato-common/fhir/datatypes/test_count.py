from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Count


class TestCount:

    def test_create(self):
        obj = Count()
        assert obj is not None

    def test_to_dict(self):
        obj = Count()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Count()
        j = obj.to_json()
        assert isinstance(j, str)
