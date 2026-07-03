from __future__ import annotations

from zato.fhir.r4_0_1 import SupplyDelivery


class TestSupplyDelivery:

    def test_create(self):
        obj = SupplyDelivery()
        assert obj._resource_type == "SupplyDelivery"

    def test_to_dict(self):
        obj = SupplyDelivery()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "SupplyDelivery"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = SupplyDelivery()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "SupplyDelivery" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = SupplyDelivery()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "SupplyDelivery", "id": "from-dict-id"}
        obj = SupplyDelivery.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "SupplyDelivery", "id": "from-json-id"}'
        obj = SupplyDelivery.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = SupplyDelivery()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = SupplyDelivery.from_json(json_str)
        assert obj2.id == "roundtrip-id"
