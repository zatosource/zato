from __future__ import annotations

from zato.fhir.r4_0_1 import ClaimResponse


class TestClaimResponse:

    def test_create(self):
        obj = ClaimResponse()
        assert obj._resource_type == "ClaimResponse"

    def test_to_dict(self):
        obj = ClaimResponse()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "ClaimResponse"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = ClaimResponse()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "ClaimResponse" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = ClaimResponse()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "ClaimResponse", "id": "from-dict-id"}
        obj = ClaimResponse.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "ClaimResponse", "id": "from-json-id"}'
        obj = ClaimResponse.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = ClaimResponse()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = ClaimResponse.from_json(json_str)
        assert obj2.id == "roundtrip-id"
