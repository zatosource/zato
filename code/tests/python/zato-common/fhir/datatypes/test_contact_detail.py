from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import ContactDetail


class TestContactDetail:

    def test_create(self):
        obj = ContactDetail()
        assert obj is not None

    def test_to_dict(self):
        obj = ContactDetail()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = ContactDetail()
        j = obj.to_json()
        assert isinstance(j, str)
