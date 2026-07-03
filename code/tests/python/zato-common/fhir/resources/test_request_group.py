from __future__ import annotations

from zato.fhir.r4_0_1 import RequestGroup


class TestRequestGroup:

    def test_create(self):
        obj = RequestGroup()
        assert obj._resource_type == "RequestGroup"

    def test_to_dict(self):
        obj = RequestGroup()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "RequestGroup"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = RequestGroup()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "RequestGroup" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = RequestGroup()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "RequestGroup", "id": "from-dict-id"}
        obj = RequestGroup.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "RequestGroup", "id": "from-json-id"}'
        obj = RequestGroup.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = RequestGroup()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = RequestGroup.from_json(json_str)
        assert obj2.id == "roundtrip-id"
