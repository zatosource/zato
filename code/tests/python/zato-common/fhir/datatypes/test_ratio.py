from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Ratio


class TestRatio:

    def test_create(self):
        obj = Ratio()
        assert obj is not None

    def test_to_dict(self):
        obj = Ratio()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Ratio()
        j = obj.to_json()
        assert isinstance(j, str)
