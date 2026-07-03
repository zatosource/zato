from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import ProdCharacteristic


class TestProdCharacteristic:

    def test_create(self):
        obj = ProdCharacteristic()
        assert obj is not None

    def test_to_dict(self):
        obj = ProdCharacteristic()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = ProdCharacteristic()
        j = obj.to_json()
        assert isinstance(j, str)
