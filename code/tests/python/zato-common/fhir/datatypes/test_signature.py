from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import Signature


class TestSignature:

    def test_create(self):
        obj = Signature()
        assert obj is not None

    def test_to_dict(self):
        obj = Signature()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = Signature()
        j = obj.to_json()
        assert isinstance(j, str)
