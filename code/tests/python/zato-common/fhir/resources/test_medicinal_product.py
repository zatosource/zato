from __future__ import annotations

from zato.fhir.r4_0_1 import MedicinalProduct


class TestMedicinalProduct:

    def test_create(self):
        obj = MedicinalProduct()
        assert obj._resource_type == "MedicinalProduct"

    def test_to_dict(self):
        obj = MedicinalProduct()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "MedicinalProduct"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = MedicinalProduct()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "MedicinalProduct" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = MedicinalProduct()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "MedicinalProduct", "id": "from-dict-id"}
        obj = MedicinalProduct.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "MedicinalProduct", "id": "from-json-id"}'
        obj = MedicinalProduct.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = MedicinalProduct()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = MedicinalProduct.from_json(json_str)
        assert obj2.id == "roundtrip-id"
