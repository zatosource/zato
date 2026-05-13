from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import SDD


device_name = "test_device_name"
control_code = "test_control_code"
operator_name = "test_operator_name"


class TestSDD:
    """Comprehensive tests for SDD segment."""

    def test_sdd_build_and_verify(self):
        seg = SDD()

        seg.device_name = device_name
        seg.control_code = control_code
        seg.operator_name = operator_name

        assert seg.device_name == device_name
        assert seg.control_code == control_code
        assert seg.operator_name == operator_name

    def test_sdd_to_dict(self):
        seg = SDD()

        seg.device_name = device_name
        seg.control_code = control_code
        seg.operator_name = operator_name

        result = seg.to_dict()

        assert result["_segment_id"] == "SDD"
        assert result["device_name"] == device_name
        assert result["control_code"] == control_code
        assert result["operator_name"] == operator_name

    def test_sdd_to_json(self):
        seg = SDD()

        seg.device_name = device_name
        seg.control_code = control_code
        seg.operator_name = operator_name

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "SDD"
        assert result["device_name"] == device_name
        assert result["control_code"] == control_code
        assert result["operator_name"] == operator_name
