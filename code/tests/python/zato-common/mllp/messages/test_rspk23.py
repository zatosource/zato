from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RspK23
from zato.hl7v2.v2_9.segments import DSC, ERR, MSA, MSH, PID, QAK, QPD, UAC


class TestRspK23:
    """Comprehensive tests for RspK23 message."""

    def test_rsp_k23_create(self):
        msg = RspK23()
        assert msg._structure_id == "RSP_K23"

    def test_rsp_k23_segment_access(self):
        msg = RspK23()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.pid._segment_id == "PID"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_k23_to_dict(self):
        msg = RspK23()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_K23"

    def test_rsp_k23_to_json(self):
        msg = RspK23()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_K23"
