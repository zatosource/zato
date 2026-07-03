from __future__ import annotations

from zato.fhir.r4_0_1 import ExampleScenario


class TestExampleScenario:

    def test_create(self):
        obj = ExampleScenario()
        assert obj._resource_type == "ExampleScenario"

    def test_to_dict(self):
        obj = ExampleScenario()
        obj.id = "test-id-123"
        d = obj.to_dict()
        assert d["resourceType"] == "ExampleScenario"
        assert d["id"] == "test-id-123"

    def test_to_json(self):
        obj = ExampleScenario()
        obj.id = "test-id-456"
        j = obj.to_json()
        assert "ExampleScenario" in j
        assert "test-id-456" in j

    def test_to_json_indent(self):
        obj = ExampleScenario()
        obj.id = "test-id-789"
        j = obj.to_json(indent=2)
        assert "\n" in j

    def test_from_dict(self):
        data = {"resourceType": "ExampleScenario", "id": "from-dict-id"}
        obj = ExampleScenario.from_dict(data)
        assert obj.id == "from-dict-id"

    def test_from_json(self):
        json_str = '{"resourceType": "ExampleScenario", "id": "from-json-id"}'
        obj = ExampleScenario.from_json(json_str)
        assert obj.id == "from-json-id"

    def test_roundtrip(self):
        obj = ExampleScenario()
        obj.id = "roundtrip-id"
        json_str = obj.to_json()
        obj2 = ExampleScenario.from_json(json_str)
        assert obj2.id == "roundtrip-id"
