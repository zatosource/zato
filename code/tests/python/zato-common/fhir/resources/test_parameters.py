from __future__ import annotations

from zato.fhir.r4_0_1 import Parameters


class TestParameters:

    def test_create(self):
        obj = Parameters()
        assert obj._resource_type == "Parameters"

    def test_to_dict(self):
        obj = Parameters()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "Parameters"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = Parameters()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "Parameters" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = Parameters()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "Parameters", "id": "from-dict-id"}
        obj = Parameters.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "Parameters", "id": "from-json-id"}'
        obj = Parameters.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = Parameters()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = Parameters.from_json(json_str)
        assert obj2.id == "roundtrip-id"
