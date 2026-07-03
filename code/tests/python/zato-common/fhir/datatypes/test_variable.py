from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import variable


class Testvariable:

    def test_create(self):
        obj = variable()
        assert obj is not None

    def test_to_dict(self):
        obj = variable()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = variable()
        j = obj.to_json()
        assert isinstance(j, str)
