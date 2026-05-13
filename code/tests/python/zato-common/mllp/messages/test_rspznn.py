from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RspZnn
from zato.hl7v2.v2_9.segments import DSC, ERR, MSA, MSH, QAK, QPD, UAC


class TestRspZnn:
    """Comprehensive tests for RspZnn message."""

    def test_rsp_znn_create(self):
        msg = RspZnn()
        assert msg._structure_id == "RSP_Znn"

    def test_rsp_znn_segment_access(self):
        msg = RspZnn()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_znn_to_dict(self):
        msg = RspZnn()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_Znn"

    def test_rsp_znn_to_json(self):
        msg = RspZnn()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_Znn"
