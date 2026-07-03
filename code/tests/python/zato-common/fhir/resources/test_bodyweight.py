from __future__ import annotations

from zato.fhir.r4_0_1 import bodyweight


class Testbodyweight:

    def test_create(self):
        obj = bodyweight()
        assert obj._resource_type == "bodyweight"

    def test_to_dict(self):
        obj = bodyweight()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "bodyweight"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = bodyweight()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "bodyweight" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = bodyweight()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "bodyweight", "id": "from-dict-id"}
        obj = bodyweight.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "bodyweight", "id": "from-json-id"}'
        obj = bodyweight.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = bodyweight()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = bodyweight.from_json(json_str)
        assert obj2.id == "roundtrip-id"
