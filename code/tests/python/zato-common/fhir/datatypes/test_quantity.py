from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Quantity


class TestQuantity:

    def test_create(self):
        obj = Quantity()
        assert obj is not None

    def test_to_dict(self):
        obj = Quantity()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Quantity()
        j = obj.to_json()
        assert isinstance(j, str)
