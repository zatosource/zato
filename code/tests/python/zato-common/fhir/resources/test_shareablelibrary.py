from __future__ import annotations

from zato.fhir.r4_0_1 import shareablelibrary


class Testshareablelibrary:

    def test_create(self):
        obj = shareablelibrary()
        assert obj._resource_type == "shareablelibrary"

    def test_to_dict(self):
        obj = shareablelibrary()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "shareablelibrary"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = shareablelibrary()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "shareablelibrary" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = shareablelibrary()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "shareablelibrary", "id": "from-dict-id"}
        obj = shareablelibrary.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "shareablelibrary", "id": "from-json-id"}'
        obj = shareablelibrary.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = shareablelibrary()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = shareablelibrary.from_json(json_str)
        assert obj2.id == "roundtrip-id"
