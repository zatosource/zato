from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import regex


class Testregex:

    def test_create(self):
        obj = regex()
        assert obj is not None

    def test_to_dict(self):
        obj = regex()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = regex()
        j = obj.to_json()
        assert isinstance(j, str)
