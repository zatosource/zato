from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import BarP10
from zato.hl7v2.v2_9.segments import DG1, EVN, GP1, GP2, MSH, PID, PR1, PV1, UAC


class TestBarP10:
    """Comprehensive tests for BarP10 message."""

    def test_bar_p10_create(self):
        msg = BarP10()
        assert msg._structure_id == "BAR_P10"

    def test_bar_p10_segment_access(self):
        msg = BarP10()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pv1._segment_id == "PV1"
        assert msg.dg1._segment_id == "DG1"
        assert msg.gp1._segment_id == "GP1"
        assert msg.pr1._segment_id == "PR1"
        assert msg.gp2._segment_id == "GP2"

    def test_bar_p10_to_dict(self):
        msg = BarP10()

        result = msg.to_dict()

        assert result["_structure_id"] == "BAR_P10"

    def test_bar_p10_to_json(self):
        msg = BarP10()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "BAR_P10"
