from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Population


class TestPopulation:

    def test_create(self):
        obj = Population()
        assert obj is not None

    def test_to_dict(self):
        obj = Population()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Population()
        j = obj.to_json()
        assert isinstance(j, str)
