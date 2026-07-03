from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import TriggerDefinition


class TestTriggerDefinition:

    def test_create(self):
        obj = TriggerDefinition()
        assert obj is not None

    def test_to_dict(self):
        obj = TriggerDefinition()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = TriggerDefinition()
        j = obj.to_json()
        assert isinstance(j, str)
