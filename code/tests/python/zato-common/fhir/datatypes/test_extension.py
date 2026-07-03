from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Extension


class TestExtension:

    def test_create(self):
        obj = Extension()
        assert obj is not None

    def test_to_dict(self):
        obj = Extension()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Extension()
        j = obj.to_json()
        assert isinstance(j, str)
