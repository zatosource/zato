from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RspZ90
from zato.hl7v2.v2_9.segments import CTD, DSC, ERR, MSA, MSH, OBR, OBX, ORC, PD1, PID, PV1, PV2, QAK, QPD, RCP, SPM, TQ1, UAC


class TestRspZ90:
    """Comprehensive tests for RspZ90 message."""

    def test_rsp_z90_create(self):
        msg = RspZ90()
        assert msg._structure_id == "RSP_Z90"

    def test_rsp_z90_segment_access(self):
        msg = RspZ90()

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
        assert msg.obr._segment_id == "OBR"
        assert msg.ctd._segment_id == "CTD"
        assert msg.obx._segment_id == "OBX"
        assert msg.spm._segment_id == "SPM"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_z90_to_dict(self):
        msg = RspZ90()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_Z90"

    def test_rsp_z90_to_json(self):
        msg = RspZ90()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_Z90"
