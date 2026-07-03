from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import language


class Testlanguage:

    def test_create(self):
        obj = language()
        assert obj is not None

    def test_to_dict(self):
        obj = language()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = language()
        j = obj.to_json()
        assert isinstance(j, str)
