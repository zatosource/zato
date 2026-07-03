from __future__ import annotations

from zato.fhir.r4_0_1 import SupplyRequest


class TestSupplyRequest:

    def test_create(self):
        obj = SupplyRequest()
        assert obj._resource_type == "SupplyRequest"

    def test_to_dict(self):
        obj = SupplyRequest()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "SupplyRequest"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = SupplyRequest()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "SupplyRequest" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = SupplyRequest()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "SupplyRequest", "id": "from-dict-id"}
        obj = SupplyRequest.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "SupplyRequest", "id": "from-json-id"}'
        obj = SupplyRequest.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = SupplyRequest()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = SupplyRequest.from_json(json_str)
        assert obj2.id == "roundtrip-id"
