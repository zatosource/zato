from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import replaces


class Testreplaces:

    def test_create(self):
        obj = replaces()
        assert obj is not None

    def test_to_dict(self):
        obj = replaces()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = replaces()
        j = obj.to_json()
        assert isinstance(j, str)
