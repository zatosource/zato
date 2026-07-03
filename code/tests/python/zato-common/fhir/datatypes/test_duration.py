from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Duration


class TestDuration:

    def test_create(self):
        obj = Duration()
        assert obj is not None

    def test_to_dict(self):
        obj = Duration()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Duration()
        j = obj.to_json()
        assert isinstance(j, str)
