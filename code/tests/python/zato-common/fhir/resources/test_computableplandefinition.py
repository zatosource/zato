from __future__ import annotations

from zato.fhir.r4_0_1 import computableplandefinition


class Testcomputableplandefinition:

    def test_create(self):
        obj = computableplandefinition()
        assert obj._resource_type == "computableplandefinition"

    def test_to_dict(self):
        obj = computableplandefinition()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "computableplandefinition"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = computableplandefinition()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "computableplandefinition" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = computableplandefinition()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "computableplandefinition", "id": "from-dict-id"}
        obj = computableplandefinition.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "computableplandefinition", "id": "from-json-id"}'
        obj = computableplandefinition.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = computableplandefinition()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = computableplandefinition.from_json(json_str)
        assert obj2.id == "roundtrip-id"
