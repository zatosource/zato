from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import maxSize


class TestmaxSize:

    def test_create(self):
        obj = maxSize()
        assert obj is not None

    def test_to_dict(self):
        obj = maxSize()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = maxSize()
        j = obj.to_json()
        assert isinstance(j, str)
