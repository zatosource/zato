from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Timing


class TestTiming:

    def test_create(self):
        obj = Timing()
        assert obj is not None

    def test_to_dict(self):
        obj = Timing()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Timing()
        j = obj.to_json()
        assert isinstance(j, str)
