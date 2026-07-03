from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import bodySite


class TestbodySite:

    def test_create(self):
        obj = bodySite()
        assert obj is not None

    def test_to_dict(self):
        obj = bodySite()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = bodySite()
        j = obj.to_json()
        assert isinstance(j, str)
