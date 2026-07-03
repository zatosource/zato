from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Distance


class TestDistance:

    def test_create(self):
        obj = Distance()
        assert obj is not None

    def test_to_dict(self):
        obj = Distance()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Distance()
        j = obj.to_json()
        assert isinstance(j, str)
