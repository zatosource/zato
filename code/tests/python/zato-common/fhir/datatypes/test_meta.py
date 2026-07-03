from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Meta


class TestMeta:

    def test_create(self):
        obj = Meta()
        assert obj is not None

    def test_to_dict(self):
        obj = Meta()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Meta()
        j = obj.to_json()
        assert isinstance(j, str)
