from __future__ import annotations

from zato.fhir.r4_0_1 import shareableplandefinition


class Testshareableplandefinition:

    def test_create(self):
        obj = shareableplandefinition()
        assert obj._resource_type == "shareableplandefinition"

    def test_to_dict(self):
        obj = shareableplandefinition()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "shareableplandefinition"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = shareableplandefinition()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "shareableplandefinition" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = shareableplandefinition()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "shareableplandefinition", "id": "from-dict-id"}
        obj = shareableplandefinition.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "shareableplandefinition", "id": "from-json-id"}'
        obj = shareableplandefinition.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = shareableplandefinition()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = shareableplandefinition.from_json(json_str)
        assert obj2.id == "roundtrip-id"
