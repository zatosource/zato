from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import CDM


charge_description_short = "test_charge_description_s"
charge_description_long = "test_charge_description_l"
active_inactive_flag = "test_active_inactive_flag"
resource_load = "test_resource_load"
room_fee_indicator = "test_room_fee_indicator"


class TestCDM:
    """Comprehensive tests for CDM segment."""

    def test_cdm_build_and_verify(self):
        seg = CDM()

        seg.charge_description_short = charge_description_short
        seg.charge_description_long = charge_description_long
        seg.active_inactive_flag = active_inactive_flag
        seg.resource_load = resource_load
        seg.room_fee_indicator = room_fee_indicator

        assert seg.charge_description_short == charge_description_short
        assert seg.charge_description_long == charge_description_long
        assert seg.active_inactive_flag == active_inactive_flag
        assert seg.resource_load == resource_load
        assert seg.room_fee_indicator == room_fee_indicator

    def test_cdm_to_dict(self):
        seg = CDM()

        seg.charge_description_short = charge_description_short
        seg.charge_description_long = charge_description_long
        seg.active_inactive_flag = active_inactive_flag
        seg.resource_load = resource_load
        seg.room_fee_indicator = room_fee_indicator

        result = seg.to_dict()

        assert result["_segment_id"] == "CDM"
        assert result["charge_description_short"] == charge_description_short
        assert result["charge_description_long"] == charge_description_long
        assert result["active_inactive_flag"] == active_inactive_flag
        assert result["resource_load"] == resource_load
        assert result["room_fee_indicator"] == room_fee_indicator

    def test_cdm_to_json(self):
        seg = CDM()

        seg.charge_description_short = charge_description_short
        seg.charge_description_long = charge_description_long
        seg.active_inactive_flag = active_inactive_flag
        seg.resource_load = resource_load
        seg.room_fee_indicator = room_fee_indicator

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CDM"
        assert result["charge_description_short"] == charge_description_short
        assert result["charge_description_long"] == charge_description_long
        assert result["active_inactive_flag"] == active_inactive_flag
        assert result["resource_load"] == resource_load
        assert result["room_fee_indicator"] == room_fee_indicator
