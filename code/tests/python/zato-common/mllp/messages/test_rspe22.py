from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RspE22
from zato.hl7v2.v2_9.segments import IVC, MSA, MSH, PSG, PSL, QAK, QPD


class TestRspE22:
    """Comprehensive tests for RspE22 message."""

    def test_rsp_e22_create(self):
        msg = RspE22()
        assert msg._structure_id == "RSP_E22"

    def test_rsp_e22_segment_access(self):
        msg = RspE22()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.ivc._segment_id == "IVC"
        assert msg.psg._segment_id == "PSG"
        assert msg.psl._segment_id == "PSL"

    def test_rsp_e22_to_dict(self):
        msg = RspE22()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_E22"

    def test_rsp_e22_to_json(self):
        msg = RspE22()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_E22"
