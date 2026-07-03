from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Annotation


class TestAnnotation:

    def test_create(self):
        obj = Annotation()
        assert obj is not None

    def test_to_dict(self):
        obj = Annotation()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Annotation()
        j = obj.to_json()
        assert isinstance(j, str)
