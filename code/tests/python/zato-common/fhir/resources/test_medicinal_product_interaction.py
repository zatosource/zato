from __future__ import annotations

from zato.fhir.r4_0_1 import MedicinalProductInteraction


class TestMedicinalProductInteraction:

    def test_create(self):
        obj = MedicinalProductInteraction()
        assert obj._resource_type == "MedicinalProductInteraction"

    def test_to_dict(self):
        obj = MedicinalProductInteraction()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "MedicinalProductInteraction"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = MedicinalProductInteraction()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "MedicinalProductInteraction" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = MedicinalProductInteraction()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "MedicinalProductInteraction", "id": "from-dict-id"}
        obj = MedicinalProductInteraction.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "MedicinalProductInteraction", "id": "from-json-id"}'
        obj = MedicinalProductInteraction.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = MedicinalProductInteraction()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = MedicinalProductInteraction.from_json(json_str)
        assert obj2.id == "roundtrip-id"
