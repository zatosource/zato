from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import originalText


class TestoriginalText:

    def test_create(self):
        obj = originalText()
        assert obj is not None

    def test_to_dict(self):
        obj = originalText()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = originalText()
        j = obj.to_json()
        assert isinstance(j, str)
