from __future__ import annotations

from zato.fhir.r4_0_1 import CatalogEntry


class TestCatalogEntry:

    def test_create(self):
        obj = CatalogEntry()
        assert obj._resource_type == "CatalogEntry"

    def test_to_dict(self):
        obj = CatalogEntry()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "CatalogEntry"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = CatalogEntry()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "CatalogEntry" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = CatalogEntry()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "CatalogEntry", "id": "from-dict-id"}
        obj = CatalogEntry.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "CatalogEntry", "id": "from-json-id"}'
        obj = CatalogEntry.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = CatalogEntry()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = CatalogEntry.from_json(json_str)
        assert obj2.id == "roundtrip-id"
