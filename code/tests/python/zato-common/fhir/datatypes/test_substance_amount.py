from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import SubstanceAmount


class TestSubstanceAmount:

    def test_create(self):
        obj = SubstanceAmount()
        assert obj is not None

    def test_to_dict(self):
        obj = SubstanceAmount()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = SubstanceAmount()
        j = obj.to_json()
        assert isinstance(j, str)
