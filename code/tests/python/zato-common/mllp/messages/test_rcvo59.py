from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RcvO59
from zato.hl7v2.v2_9.segments import MSH, OBX, ORC, PD1, PID, PV1, PV2, RXC, RXD, RXE, RXO, TQ1, UAC


class TestRcvO59:
    """Comprehensive tests for RcvO59 message."""

    def test_rcv_o59_create(self):
        msg = RcvO59()
        assert msg._structure_id == "RCV_O59"

    def test_rcv_o59_segment_access(self):
        msg = RcvO59()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxo._segment_id == "RXO"
        assert msg.rxc._segment_id == "RXC"
        assert msg.rxe._segment_id == "RXE"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxd._segment_id == "RXD"
        assert msg.obx._segment_id == "OBX"

    def test_rcv_o59_to_dict(self):
        msg = RcvO59()

        result = msg.to_dict()

        assert result["_structure_id"] == "RCV_O59"

    def test_rcv_o59_to_json(self):
        msg = RcvO59()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RCV_O59"
