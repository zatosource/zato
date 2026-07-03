from __future__ import annotations

from zato.fhir.r4_0_1 import ImmunizationEvaluation


class TestImmunizationEvaluation:

    def test_create(self):
        obj = ImmunizationEvaluation()
        assert obj._resource_type == "ImmunizationEvaluation"

    def test_to_dict(self):
        obj = ImmunizationEvaluation()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "ImmunizationEvaluation"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = ImmunizationEvaluation()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "ImmunizationEvaluation" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = ImmunizationEvaluation()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "ImmunizationEvaluation", "id": "from-dict-id"}
        obj = ImmunizationEvaluation.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "ImmunizationEvaluation", "id": "from-json-id"}'
        obj = ImmunizationEvaluation.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = ImmunizationEvaluation()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = ImmunizationEvaluation.from_json(json_str)
        assert obj2.id == "roundtrip-id"
