from __future__ import annotations

from zato.fhir.r4_0_1 import ImmunizationRecommendation


class TestImmunizationRecommendation:

    def test_create(self):
        obj = ImmunizationRecommendation()
        assert obj._resource_type == "ImmunizationRecommendation"

    def test_to_dict(self):
        obj = ImmunizationRecommendation()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "ImmunizationRecommendation"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = ImmunizationRecommendation()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "ImmunizationRecommendation" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = ImmunizationRecommendation()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "ImmunizationRecommendation", "id": "from-dict-id"}
        obj = ImmunizationRecommendation.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "ImmunizationRecommendation", "id": "from-json-id"}'
        obj = ImmunizationRecommendation.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = ImmunizationRecommendation()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = ImmunizationRecommendation.from_json(json_str)
        assert obj2.id == "roundtrip-id"
