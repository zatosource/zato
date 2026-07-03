from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import MoneyQuantity


class TestMoneyQuantity:

    def test_create(self):
        obj = MoneyQuantity()
        assert obj is not None

    def test_to_dict(self):
        obj = MoneyQuantity()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = MoneyQuantity()
        j = obj.to_json()
        assert isinstance(j, str)
