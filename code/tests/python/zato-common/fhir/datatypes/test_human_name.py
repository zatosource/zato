from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import HumanName


class TestHumanName:

    def test_create(self):
        obj = HumanName()
        assert obj is not None

    def test_to_dict(self):
        obj = HumanName()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = HumanName()
        j = obj.to_json()
        assert isinstance(j, str)
