from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RspO34
from zato.hl7v2.v2_9.segments import DON, ERR, MSA, MSH, OBX, PD1, PID, PV1, QAK, QPD, UAC


class TestRspO34:
    """Comprehensive tests for RspO34 message."""

    def test_rsp_o34_create(self):
        msg = RspO34()
        assert msg._structure_id == "RSP_O34"

    def test_rsp_o34_segment_access(self):
        msg = RspO34()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.obx._segment_id == "OBX"
        assert msg.pv1._segment_id == "PV1"
        assert msg.don._segment_id == "DON"
        assert msg.obx._segment_id == "OBX"

    def test_rsp_o34_to_dict(self):
        msg = RspO34()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_O34"

    def test_rsp_o34_to_json(self):
        msg = RspO34()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_O34"
