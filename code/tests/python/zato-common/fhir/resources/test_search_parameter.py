from __future__ import annotations

from zato.fhir.r4_0_1 import SearchParameter


class TestSearchParameter:

    def test_create(self):
        obj = SearchParameter()
        assert obj._resource_type == "SearchParameter"

    def test_to_dict(self):
        obj = SearchParameter()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "SearchParameter"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = SearchParameter()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "SearchParameter" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = SearchParameter()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "SearchParameter", "id": "from-dict-id"}
        obj = SearchParameter.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "SearchParameter", "id": "from-json-id"}'
        obj = SearchParameter.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = SearchParameter()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = SearchParameter.from_json(json_str)
        assert obj2.id == "roundtrip-id"
