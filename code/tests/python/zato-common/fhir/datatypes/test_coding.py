from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Coding


class TestCoding:

    def test_create(self):
        obj = Coding()
        assert obj is not None

    def test_to_dict(self):
        obj = Coding()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Coding()
        j = obj.to_json()
        assert isinstance(j, str)
