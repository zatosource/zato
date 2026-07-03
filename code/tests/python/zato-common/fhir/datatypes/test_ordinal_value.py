from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import ordinalValue


class TestordinalValue:

    def test_create(self):
        obj = ordinalValue()
        assert obj is not None

    def test_to_dict(self):
        obj = ordinalValue()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = ordinalValue()
        j = obj.to_json()
        assert isinstance(j, str)
