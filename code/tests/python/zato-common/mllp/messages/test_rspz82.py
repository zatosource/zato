from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RspZ82
from zato.hl7v2.v2_9.segments import DSC, ERR, MSA, MSH, OBX, ORC, PD1, PID, PV1, PV2, QAK, QPD, RCP, RXD, RXE, RXO, TQ1, UAC


class TestRspZ82:
    """Comprehensive tests for RspZ82 message."""

    def test_rsp_z82_create(self):
        msg = RspZ82()
        assert msg._structure_id == "RSP_Z82"

    def test_rsp_z82_segment_access(self):
        msg = RspZ82()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxo._segment_id == "RXO"
        assert msg.rxe._segment_id == "RXE"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxd._segment_id == "RXD"
        assert msg.obx._segment_id == "OBX"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_z82_to_dict(self):
        msg = RspZ82()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_Z82"

    def test_rsp_z82_to_json(self):
        msg = RspZ82()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_Z82"
