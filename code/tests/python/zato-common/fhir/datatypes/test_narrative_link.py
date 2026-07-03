from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import narrativeLink


class TestnarrativeLink:

    def test_create(self):
        obj = narrativeLink()
        assert obj is not None

    def test_to_dict(self):
        obj = narrativeLink()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = narrativeLink()
        j = obj.to_json()
        assert isinstance(j, str)
