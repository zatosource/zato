from __future__ import annotations

from zato.fhir.r4_0_1 import vitalspanel


class Testvitalspanel:

    def test_create(self):
        obj = vitalspanel()
        assert obj._resource_type == "vitalspanel"

    def test_to_dict(self):
        obj = vitalspanel()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "vitalspanel"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = vitalspanel()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "vitalspanel" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = vitalspanel()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "vitalspanel", "id": "from-dict-id"}
        obj = vitalspanel.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "vitalspanel", "id": "from-json-id"}'
        obj = vitalspanel.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = vitalspanel()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = vitalspanel.from_json(json_str)
        assert obj2.id == "roundtrip-id"
