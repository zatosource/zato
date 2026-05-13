from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import SLT


device_name = "test_device_name"
bar_code = "test_bar_code"


class TestSLT:
    """Comprehensive tests for SLT segment."""

    def test_slt_build_and_verify(self):
        seg = SLT()

        seg.device_name = device_name
        seg.bar_code = bar_code

        assert seg.device_name == device_name
        assert seg.bar_code == bar_code

    def test_slt_to_dict(self):
        seg = SLT()

        seg.device_name = device_name
        seg.bar_code = bar_code

        result = seg.to_dict()

        assert result["_segment_id"] == "SLT"
        assert result["device_name"] == device_name
        assert result["bar_code"] == bar_code

    def test_slt_to_json(self):
        seg = SLT()

        seg.device_name = device_name
        seg.bar_code = bar_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "SLT"
        assert result["device_name"] == device_name
        assert result["bar_code"] == bar_code
