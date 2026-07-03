from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import CodeableConcept


class TestCodeableConcept:

    def test_create(self):
        obj = CodeableConcept()
        assert obj is not None

    def test_to_dict(self):
        obj = CodeableConcept()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = CodeableConcept()
        j = obj.to_json()
        assert isinstance(j, str)
