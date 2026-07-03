from __future__ import annotations

from zato.fhir.r4_0_1 import heartrate


class Testheartrate:

    def test_create(self):
        obj = heartrate()
        assert obj._resource_type == "heartrate"

    def test_to_dict(self):
        obj = heartrate()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "heartrate"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = heartrate()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "heartrate" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = heartrate()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "heartrate", "id": "from-dict-id"}
        obj = heartrate.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "heartrate", "id": "from-json-id"}'
        obj = heartrate.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = heartrate()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = heartrate.from_json(json_str)
        assert obj2.id == "roundtrip-id"
