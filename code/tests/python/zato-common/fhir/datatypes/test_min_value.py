from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import minValue


class TestminValue:

    def test_create(self):
        obj = minValue()
        assert obj is not None

    def test_to_dict(self):
        obj = minValue()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = minValue()
        j = obj.to_json()
        assert isinstance(j, str)
