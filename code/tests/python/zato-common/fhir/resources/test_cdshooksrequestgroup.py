from __future__ import annotations

from zato.fhir.r4_0_1 import cdshooksrequestgroup


class Testcdshooksrequestgroup:

    def test_create(self):
        obj = cdshooksrequestgroup()
        assert obj._resource_type == "cdshooksrequestgroup"

    def test_to_dict(self):
        obj = cdshooksrequestgroup()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "cdshooksrequestgroup"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = cdshooksrequestgroup()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "cdshooksrequestgroup" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = cdshooksrequestgroup()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "cdshooksrequestgroup", "id": "from-dict-id"}
        obj = cdshooksrequestgroup.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "cdshooksrequestgroup", "id": "from-json-id"}'
        obj = cdshooksrequestgroup.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = cdshooksrequestgroup()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = cdshooksrequestgroup.from_json(json_str)
        assert obj2.id == "roundtrip-id"
