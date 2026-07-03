from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Contributor


class TestContributor:

    def test_create(self):
        obj = Contributor()
        assert obj is not None

    def test_to_dict(self):
        obj = Contributor()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Contributor()
        j = obj.to_json()
        assert isinstance(j, str)
