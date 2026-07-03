from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import DataRequirement


class TestDataRequirement:

    def test_create(self):
        obj = DataRequirement()
        assert obj is not None

    def test_to_dict(self):
        obj = DataRequirement()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = DataRequirement()
        j = obj.to_json()
        assert isinstance(j, str)
