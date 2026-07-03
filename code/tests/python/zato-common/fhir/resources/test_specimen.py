from __future__ import annotations

from zato.fhir.r4_0_1 import Specimen


class TestSpecimen:

    def test_create(self):
        obj = Specimen()
        assert obj._resource_type == "Specimen"

    def test_to_dict(self):
        obj = Specimen()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "Specimen"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = Specimen()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "Specimen" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = Specimen()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "Specimen", "id": "from-dict-id"}
        obj = Specimen.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "Specimen", "id": "from-json-id"}'
        obj = Specimen.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = Specimen()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = Specimen.from_json(json_str)
        assert obj2.id == "roundtrip-id"
