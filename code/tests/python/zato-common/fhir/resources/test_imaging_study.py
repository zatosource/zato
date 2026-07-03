from __future__ import annotations

from zato.fhir.r4_0_1 import ImagingStudy


class TestImagingStudy:

    def test_create(self):
        obj = ImagingStudy()
        assert obj._resource_type == "ImagingStudy"

    def test_to_dict(self):
        obj = ImagingStudy()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "ImagingStudy"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = ImagingStudy()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "ImagingStudy" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = ImagingStudy()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "ImagingStudy", "id": "from-dict-id"}
        obj = ImagingStudy.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "ImagingStudy", "id": "from-json-id"}'
        obj = ImagingStudy.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = ImagingStudy()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = ImagingStudy.from_json(json_str)
        assert obj2.id == "roundtrip-id"
