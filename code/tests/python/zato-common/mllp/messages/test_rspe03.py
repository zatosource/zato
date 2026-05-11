from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RspE03
from zato.hl7v2.v2_9.segments import MSA, MSH, QAK, QPD


class TestRspE03:
    """Comprehensive tests for RspE03 message."""

    def test_rsp_e03_create(self):
        msg = RspE03()
        assert msg._structure_id == "RSP_E03"

    def test_rsp_e03_segment_access(self):
        msg = RspE03()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"

    def test_rsp_e03_to_dict(self):
        msg = RspE03()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_E03"

    def test_rsp_e03_to_json(self):
        msg = RspE03()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_E03"
