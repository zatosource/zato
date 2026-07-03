from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Range


class TestRange:

    def test_create(self):
        obj = Range()
        assert obj is not None

    def test_to_dict(self):
        obj = Range()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Range()
        j = obj.to_json()
        assert isinstance(j, str)
