from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import BarP12
from zato.hl7v2.v2_9.segments import DG1, DRG, EVN, MSH, OBX, PID, PR1, PV1, UAC


class TestBarP12:
    """Comprehensive tests for BarP12 message."""

    def test_bar_p12_create(self):
        msg = BarP12()
        assert msg._structure_id == "BAR_P12"

    def test_bar_p12_segment_access(self):
        msg = BarP12()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pv1._segment_id == "PV1"
        assert msg.dg1._segment_id == "DG1"
        assert msg.drg._segment_id == "DRG"
        assert msg.pr1._segment_id == "PR1"
        assert msg.obx._segment_id == "OBX"

    def test_bar_p12_to_dict(self):
        msg = BarP12()

        result = msg.to_dict()

        assert result["_structure_id"] == "BAR_P12"

    def test_bar_p12_to_json(self):
        msg = BarP12()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "BAR_P12"
