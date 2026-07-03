from __future__ import annotations

from zato.fhir.r4_0_1 import DetectedIssue


class TestDetectedIssue:

    def test_create(self):
        obj = DetectedIssue()
        assert obj._resource_type == "DetectedIssue"

    def test_to_dict(self):
        obj = DetectedIssue()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "DetectedIssue"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = DetectedIssue()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "DetectedIssue" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = DetectedIssue()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "DetectedIssue", "id": "from-dict-id"}
        obj = DetectedIssue.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "DetectedIssue", "id": "from-json-id"}'
        obj = DetectedIssue.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = DetectedIssue()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = DetectedIssue.from_json(json_str)
        assert obj2.id == "roundtrip-id"
