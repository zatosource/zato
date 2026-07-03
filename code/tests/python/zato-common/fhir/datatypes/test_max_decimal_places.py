from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import maxDecimalPlaces


class TestmaxDecimalPlaces:

    def test_create(self):
        obj = maxDecimalPlaces()
        assert obj is not None

    def test_to_dict(self):
        obj = maxDecimalPlaces()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = maxDecimalPlaces()
        j = obj.to_json()
        assert isinstance(j, str)
