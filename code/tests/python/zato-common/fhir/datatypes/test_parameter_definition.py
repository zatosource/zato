from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import ParameterDefinition


class TestParameterDefinition:

    def test_create(self):
        obj = ParameterDefinition()
        assert obj is not None

    def test_to_dict(self):
        obj = ParameterDefinition()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = ParameterDefinition()
        j = obj.to_json()
        assert isinstance(j, str)
