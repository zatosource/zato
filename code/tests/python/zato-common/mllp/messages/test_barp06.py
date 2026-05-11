from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import BarP06
from zato.hl7v2.v2_9.segments import EVN, MSH, PID, PV1, UAC


class TestBarP06:
    """Comprehensive tests for BarP06 message."""

    def test_bar_p06_create(self):
        msg = BarP06()
        assert msg._structure_id == "BAR_P06"

    def test_bar_p06_segment_access(self):
        msg = BarP06()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pv1._segment_id == "PV1"

    def test_bar_p06_to_dict(self):
        msg = BarP06()

        result = msg.to_dict()

        assert result["_structure_id"] == "BAR_P06"

    def test_bar_p06_to_json(self):
        msg = BarP06()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "BAR_P06"
