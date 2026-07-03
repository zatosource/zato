from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Narrative


class TestNarrative:

    def test_create(self):
        obj = Narrative()
        assert obj is not None

    def test_to_dict(self):
        obj = Narrative()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Narrative()
        j = obj.to_json()
        assert isinstance(j, str)
