from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import entryFormat


class TestentryFormat:

    def test_create(self):
        obj = entryFormat()
        assert obj is not None

    def test_to_dict(self):
        obj = entryFormat()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = entryFormat()
        j = obj.to_json()
        assert isinstance(j, str)
