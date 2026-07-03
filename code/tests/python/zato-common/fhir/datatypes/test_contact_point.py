from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import ContactPoint


class TestContactPoint:

    def test_create(self):
        obj = ContactPoint()
        assert obj is not None

    def test_to_dict(self):
        obj = ContactPoint()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = ContactPoint()
        j = obj.to_json()
        assert isinstance(j, str)
