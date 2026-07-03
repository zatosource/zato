from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Money


class TestMoney:

    def test_create(self):
        obj = Money()
        assert obj is not None

    def test_to_dict(self):
        obj = Money()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Money()
        j = obj.to_json()
        assert isinstance(j, str)
