from __future__ import annotations

from zato.fhir.r4_0_1 import bmi


class Testbmi:

    def test_create(self):
        obj = bmi()
        assert obj._resource_type == "bmi"

    def test_to_dict(self):
        obj = bmi()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "bmi"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = bmi()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "bmi" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = bmi()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "bmi", "id": "from-dict-id"}
        obj = bmi.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "bmi", "id": "from-json-id"}'
        obj = bmi.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = bmi()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = bmi.from_json(json_str)
        assert obj2.id == "roundtrip-id"
