from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PRC


minimum_quantity = "test_minimum_quantity"
maximum_quantity = "test_maximum_quantity"
effective_start_date = "test_effective_start_date"
effective_end_date = "test_effective_end_date"
chargeable_flag = "test_chargeable_flag"
active_inactive_flag = "test_active_inactive_flag"


class TestPRC:
    """Comprehensive tests for PRC segment."""

    def test_prc_build_and_verify(self):
        seg = PRC()

        seg.minimum_quantity = minimum_quantity
        seg.maximum_quantity = maximum_quantity
        seg.effective_start_date = effective_start_date
        seg.effective_end_date = effective_end_date
        seg.chargeable_flag = chargeable_flag
        seg.active_inactive_flag = active_inactive_flag

        assert seg.minimum_quantity == minimum_quantity
        assert seg.maximum_quantity == maximum_quantity
        assert seg.effective_start_date == effective_start_date
        assert seg.effective_end_date == effective_end_date
        assert seg.chargeable_flag == chargeable_flag
        assert seg.active_inactive_flag == active_inactive_flag

    def test_prc_to_dict(self):
        seg = PRC()

        seg.minimum_quantity = minimum_quantity
        seg.maximum_quantity = maximum_quantity
        seg.effective_start_date = effective_start_date
        seg.effective_end_date = effective_end_date
        seg.chargeable_flag = chargeable_flag
        seg.active_inactive_flag = active_inactive_flag

        result = seg.to_dict()

        assert result["_segment_id"] == "PRC"
        assert result["minimum_quantity"] == minimum_quantity
        assert result["maximum_quantity"] == maximum_quantity
        assert result["effective_start_date"] == effective_start_date
        assert result["effective_end_date"] == effective_end_date
        assert result["chargeable_flag"] == chargeable_flag
        assert result["active_inactive_flag"] == active_inactive_flag

    def test_prc_to_json(self):
        seg = PRC()

        seg.minimum_quantity = minimum_quantity
        seg.maximum_quantity = maximum_quantity
        seg.effective_start_date = effective_start_date
        seg.effective_end_date = effective_end_date
        seg.chargeable_flag = chargeable_flag
        seg.active_inactive_flag = active_inactive_flag

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PRC"
        assert result["minimum_quantity"] == minimum_quantity
        assert result["maximum_quantity"] == maximum_quantity
        assert result["effective_start_date"] == effective_start_date
        assert result["effective_end_date"] == effective_end_date
        assert result["chargeable_flag"] == chargeable_flag
        assert result["active_inactive_flag"] == active_inactive_flag
