from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import mimeType


class TestmimeType:

    def test_create(self):
        obj = mimeType()
        assert obj is not None

    def test_to_dict(self):
        obj = mimeType()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = mimeType()
        j = obj.to_json()
        assert isinstance(j, str)
