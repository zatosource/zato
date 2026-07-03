from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import UsageContext


class TestUsageContext:

    def test_create(self):
        obj = UsageContext()
        assert obj is not None

    def test_to_dict(self):
        obj = UsageContext()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = UsageContext()
        j = obj.to_json()
        assert isinstance(j, str)
