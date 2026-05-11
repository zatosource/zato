from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import DPS


effective_date_time = "test_effective_date_time"
expiration_date_time = "test_expiration_date_time"


class TestDPS:
    """Comprehensive tests for DPS segment."""

    def test_dps_build_and_verify(self):
        seg = DPS()

        seg.effective_date_time = effective_date_time
        seg.expiration_date_time = expiration_date_time

        assert seg.effective_date_time == effective_date_time
        assert seg.expiration_date_time == expiration_date_time

    def test_dps_to_dict(self):
        seg = DPS()

        seg.effective_date_time = effective_date_time
        seg.expiration_date_time = expiration_date_time

        result = seg.to_dict()

        assert result["_segment_id"] == "DPS"
        assert result["effective_date_time"] == effective_date_time
        assert result["expiration_date_time"] == expiration_date_time

    def test_dps_to_json(self):
        seg = DPS()

        seg.effective_date_time = effective_date_time
        seg.expiration_date_time = expiration_date_time

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "DPS"
        assert result["effective_date_time"] == effective_date_time
        assert result["expiration_date_time"] == expiration_date_time
