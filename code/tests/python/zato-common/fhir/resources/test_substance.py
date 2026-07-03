from __future__ import annotations

from zato.fhir.r4_0_1 import Substance


class TestSubstance:

    def test_create(self):
        obj = Substance()
        assert obj._resource_type == "Substance"

    def test_to_dict(self):
        obj = Substance()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "Substance"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = Substance()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "Substance" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = Substance()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "Substance", "id": "from-dict-id"}
        obj = Substance.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "Substance", "id": "from-json-id"}'
        obj = Substance.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = Substance()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = Substance.from_json(json_str)
        assert obj2.id == "roundtrip-id"
