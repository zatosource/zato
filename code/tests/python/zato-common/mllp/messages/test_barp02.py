from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import BarP02
from zato.hl7v2.v2_9.segments import EVN, MSH, PD1, PID, PV1, UAC


class TestBarP02:
    """Comprehensive tests for BarP02 message."""

    def test_bar_p02_create(self):
        msg = BarP02()
        assert msg._structure_id == "BAR_P02"

    def test_bar_p02_segment_access(self):
        msg = BarP02()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"

    def test_bar_p02_to_dict(self):
        msg = BarP02()

        result = msg.to_dict()

        assert result["_structure_id"] == "BAR_P02"

    def test_bar_p02_to_json(self):
        msg = BarP02()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "BAR_P02"
