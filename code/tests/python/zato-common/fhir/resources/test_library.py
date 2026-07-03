from __future__ import annotations

from zato.fhir.r4_0_1 import Library


class TestLibrary:

    def test_create(self):
        obj = Library()
        assert obj._resource_type == "Library"

    def test_to_dict(self):
        obj = Library()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "Library"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = Library()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "Library" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = Library()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "Library", "id": "from-dict-id"}
        obj = Library.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "Library", "id": "from-json-id"}'
        obj = Library.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = Library()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = Library.from_json(json_str)
        assert obj2.id == "roundtrip-id"
