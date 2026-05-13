from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RspK32
from zato.hl7v2.v2_9.segments import DSC, ERR, MSA, MSH, PD1, PID, PV1, PV2, QAK, QPD, QRI


class TestRspK32:
    """Comprehensive tests for RspK32 message."""

    def test_rsp_k32_create(self):
        msg = RspK32()
        assert msg._structure_id == "RSP_K32"

    def test_rsp_k32_segment_access(self):
        msg = RspK32()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.qri._segment_id == "QRI"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_k32_to_dict(self):
        msg = RspK32()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_K32"

    def test_rsp_k32_to_json(self):
        msg = RspK32()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_K32"
