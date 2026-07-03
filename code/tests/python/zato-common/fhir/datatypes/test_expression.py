from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Expression


class TestExpression:

    def test_create(self):
        obj = Expression()
        assert obj is not None

    def test_to_dict(self):
        obj = Expression()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Expression()
        j = obj.to_json()
        assert isinstance(j, str)
