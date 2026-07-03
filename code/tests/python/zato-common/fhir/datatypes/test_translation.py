from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import translation


class Testtranslation:

    def test_create(self):
        obj = translation()
        assert obj is not None

    def test_to_dict(self):
        obj = translation()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = translation()
        j = obj.to_json()
        assert isinstance(j, str)
