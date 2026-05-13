from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import NCK


system_date_time = "test_system_date_time"


class TestNCK:
    """Comprehensive tests for NCK segment."""

    def test_nck_build_and_verify(self):
        seg = NCK()

        seg.system_date_time = system_date_time

        assert seg.system_date_time == system_date_time

    def test_nck_to_dict(self):
        seg = NCK()

        seg.system_date_time = system_date_time

        result = seg.to_dict()

        assert result["_segment_id"] == "NCK"
        assert result["system_date_time"] == system_date_time

    def test_nck_to_json(self):
        seg = NCK()

        seg.system_date_time = system_date_time

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "NCK"
        assert result["system_date_time"] == system_date_time
