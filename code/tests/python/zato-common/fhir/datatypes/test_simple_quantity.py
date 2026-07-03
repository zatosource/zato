from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import SimpleQuantity


class TestSimpleQuantity:

    def test_create(self):
        obj = SimpleQuantity()
        assert obj is not None

    def test_to_dict(self):
        obj = SimpleQuantity()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = SimpleQuantity()
        j = obj.to_json()
        assert isinstance(j, str)
