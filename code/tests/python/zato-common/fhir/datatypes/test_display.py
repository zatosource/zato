from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import display


class Testdisplay:

    def test_create(self):
        obj = display()
        assert obj is not None

    def test_to_dict(self):
        obj = display()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = display()
        j = obj.to_json()
        assert isinstance(j, str)
