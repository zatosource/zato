from __future__ import annotations

from zato.fhir.r4_0_1 import Contract


class TestContract:

    def test_create(self):
        obj = Contract()
        assert obj._resource_type == "Contract"

    def test_to_dict(self):
        obj = Contract()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "Contract"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = Contract()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "Contract" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = Contract()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "Contract", "id": "from-dict-id"}
        obj = Contract.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "Contract", "id": "from-json-id"}'
        obj = Contract.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = Contract()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = Contract.from_json(json_str)
        assert obj2.id == "roundtrip-id"
