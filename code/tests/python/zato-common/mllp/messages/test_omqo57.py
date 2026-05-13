from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OmqO57
from zato.hl7v2.v2_9.segments import BLG, CTD, GT1, IN1, IN2, IN3, MSH, OBR, OBX, ORC, PD1, PID, PRT, PV1, PV2, TQ1, TXA, UAC


class TestOmqO57:
    """Comprehensive tests for OmqO57 message."""

    def test_omq_o57_create(self):
        msg = OmqO57()
        assert msg._structure_id == "OMQ_O57"

    def test_omq_o57_segment_access(self):
        msg = OmqO57()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.in1._segment_id == "IN1"
        assert msg.in2._segment_id == "IN2"
        assert msg.in3._segment_id == "IN3"
        assert msg.gt1._segment_id == "GT1"
        assert msg.orc._segment_id == "ORC"
        assert msg.obx._segment_id == "OBX"
        assert msg.txa._segment_id == "TXA"
        assert msg.ctd._segment_id == "CTD"
        assert msg.obx._segment_id == "OBX"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.orc._segment_id == "ORC"
        assert msg.obr._segment_id == "OBR"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.prt._segment_id == "PRT"
        assert msg.ctd._segment_id == "CTD"
        assert msg.obx._segment_id == "OBX"
        assert msg.blg._segment_id == "BLG"

    def test_omq_o57_to_dict(self):
        msg = OmqO57()

        result = msg.to_dict()

        assert result["_structure_id"] == "OMQ_O57"

    def test_omq_o57_to_json(self):
        msg = OmqO57()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OMQ_O57"
