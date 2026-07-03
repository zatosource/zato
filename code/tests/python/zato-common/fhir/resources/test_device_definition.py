from __future__ import annotations

from zato.fhir.r4_0_1 import DeviceDefinition


class TestDeviceDefinition:

    def test_create(self):
        obj = DeviceDefinition()
        assert obj._resource_type == "DeviceDefinition"

    def test_to_dict(self):
        obj = DeviceDefinition()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "DeviceDefinition"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = DeviceDefinition()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "DeviceDefinition" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = DeviceDefinition()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "DeviceDefinition", "id": "from-dict-id"}
        obj = DeviceDefinition.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "DeviceDefinition", "id": "from-json-id"}'
        obj = DeviceDefinition.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = DeviceDefinition()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = DeviceDefinition.from_json(json_str)
        assert obj2.id == "roundtrip-id"
