from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RSP_Z86


class TestRspZ86:
    """Comprehensive tests for RspZ86 message."""

    def test_rsp_z86_create(self):
        msg = RSP_Z86()
        assert msg._structure_id == "RSP_Z86"

    def test_rsp_z86_segment_access(self):
        msg = RSP_Z86()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxo._segment_id == "RXO"
        assert msg.rxe._segment_id == "RXE"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxd._segment_id == "RXD"
        assert msg.rxg._segment_id == "RXG"
        assert msg.rxa._segment_id == "RXA"
        assert msg.obx._segment_id == "OBX"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_z86_to_dict(self):
        msg = RSP_Z86()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_Z86"

    def test_rsp_z86_to_json(self):
        msg = RSP_Z86()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_Z86"
