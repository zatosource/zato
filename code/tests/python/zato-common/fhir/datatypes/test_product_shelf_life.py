from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import ProductShelfLife


class TestProductShelfLife:

    def test_create(self):
        obj = ProductShelfLife()
        assert obj is not None

    def test_to_dict(self):
        obj = ProductShelfLife()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = ProductShelfLife()
        j = obj.to_json()
        assert isinstance(j, str)
