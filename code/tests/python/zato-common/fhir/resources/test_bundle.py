from __future__ import annotations

from zato.fhir.r4_0_1 import Bundle


class TestBundle:

    def test_create(self):
        obj = Bundle()
        assert obj._resource_type == "Bundle"

    def test_to_dict(self):
        obj = Bundle()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "Bundle"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = Bundle()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "Bundle" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = Bundle()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "Bundle", "id": "from-dict-id"}
        obj = Bundle.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "Bundle", "id": "from-json-id"}'
        obj = Bundle.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = Bundle()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = Bundle.from_json(json_str)
        assert obj2.id == "roundtrip-id"
