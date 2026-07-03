from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import geolocation


class Testgeolocation:

    def test_create(self):
        obj = geolocation()
        assert obj is not None

    def test_to_dict(self):
        obj = geolocation()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = geolocation()
        j = obj.to_json()
        assert isinstance(j, str)
