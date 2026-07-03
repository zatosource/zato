from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import maxValue


class TestmaxValue:

    def test_create(self):
        obj = maxValue()
        assert obj is not None

    def test_to_dict(self):
        obj = maxValue()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = maxValue()
        j = obj.to_json()
        assert isinstance(j, str)
