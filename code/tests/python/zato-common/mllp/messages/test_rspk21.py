from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RspK21
from zato.hl7v2.v2_9.segments import DSC, ERR, MSA, MSH, PD1, PID, QAK, QPD, QRI, UAC


class TestRspK21:
    """Comprehensive tests for RspK21 message."""

    def test_rsp_k21_create(self):
        msg = RspK21()
        assert msg._structure_id == "RSP_K21"

    def test_rsp_k21_segment_access(self):
        msg = RspK21()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.pid._segment_id == "PID"
        assert msg.pd1._segment_id == "PD1"
        assert msg.qri._segment_id == "QRI"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_k21_to_dict(self):
        msg = RspK21()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_K21"

    def test_rsp_k21_to_json(self):
        msg = RspK21()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_K21"
