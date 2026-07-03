from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Identifier


class TestIdentifier:

    def test_create(self):
        obj = Identifier()
        assert obj is not None

    def test_to_dict(self):
        obj = Identifier()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Identifier()
        j = obj.to_json()
        assert isinstance(j, str)
