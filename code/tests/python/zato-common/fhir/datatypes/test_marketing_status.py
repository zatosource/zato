from __future__ import annotations

from zato.fhir.r4_0_1.datatypes import MarketingStatus


class TestMarketingStatus:

    def test_create(self):
        obj = MarketingStatus()
        assert obj is not None

    def test_to_dict(self):
        obj = MarketingStatus()
        d = obj.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        obj = MarketingStatus()
        j = obj.to_json()
        assert isinstance(j, str)
