from __future__ import annotations

from zato.fhir.r4_0_1 import EpisodeOfCare


class TestEpisodeOfCare:

    def test_create(self):
        obj = EpisodeOfCare()
        assert obj._resource_type == "EpisodeOfCare"

    def test_to_dict(self):
        obj = EpisodeOfCare()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "EpisodeOfCare"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = EpisodeOfCare()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "EpisodeOfCare" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = EpisodeOfCare()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "EpisodeOfCare", "id": "from-dict-id"}
        obj = EpisodeOfCare.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "EpisodeOfCare", "id": "from-json-id"}'
        obj = EpisodeOfCare.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = EpisodeOfCare()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = EpisodeOfCare.from_json(json_str)
        assert obj2.id == "roundtrip-id"
