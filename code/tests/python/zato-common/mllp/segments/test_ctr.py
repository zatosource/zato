from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import CTR


contract_description = "test_contract_description"
effective_date = "test_effective_date"
expiration_date = "test_expiration_date"
price_protection_date = "test_price_protection_dat"
contract_priority = "test_contract_priority"


class TestCTR:
    """Comprehensive tests for CTR segment."""

    def test_ctr_build_and_verify(self):
        seg = CTR()

        seg.contract_description = contract_description
        seg.effective_date = effective_date
        seg.expiration_date = expiration_date
        seg.price_protection_date = price_protection_date
        seg.contract_priority = contract_priority

        assert seg.contract_description == contract_description
        assert seg.effective_date == effective_date
        assert seg.expiration_date == expiration_date
        assert seg.price_protection_date == price_protection_date
        assert seg.contract_priority == contract_priority

    def test_ctr_to_dict(self):
        seg = CTR()

        seg.contract_description = contract_description
        seg.effective_date = effective_date
        seg.expiration_date = expiration_date
        seg.price_protection_date = price_protection_date
        seg.contract_priority = contract_priority

        result = seg.to_dict()

        assert result["_segment_id"] == "CTR"
        assert result["contract_description"] == contract_description
        assert result["effective_date"] == effective_date
        assert result["expiration_date"] == expiration_date
        assert result["price_protection_date"] == price_protection_date
        assert result["contract_priority"] == contract_priority

    def test_ctr_to_json(self):
        seg = CTR()

        seg.contract_description = contract_description
        seg.effective_date = effective_date
        seg.expiration_date = expiration_date
        seg.price_protection_date = price_protection_date
        seg.contract_priority = contract_priority

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CTR"
        assert result["contract_description"] == contract_description
        assert result["effective_date"] == effective_date
        assert result["expiration_date"] == expiration_date
        assert result["price_protection_date"] == price_protection_date
        assert result["contract_priority"] == contract_priority
