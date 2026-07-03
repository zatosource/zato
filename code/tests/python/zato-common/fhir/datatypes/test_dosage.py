from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Dosage


class TestDosage:

    def test_create(self):
        obj = Dosage()
        assert obj is not None

    def test_to_dict(self):
        obj = Dosage()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Dosage()
        j = obj.to_json()
        assert isinstance(j, str)
