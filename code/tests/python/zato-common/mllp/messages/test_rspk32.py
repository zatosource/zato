from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RSP_K32


class TestRspK32:
    """Comprehensive tests for RspK32 message."""

    def test_rsp_k32_create(self):
        msg = RSP_K32()
        assert msg._structure_id == "RSP_K32"

    def test_rsp_k32_segment_access(self):
        msg = RSP_K32()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_k32_to_dict(self):
        msg = RSP_K32()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_K32"

    def test_rsp_k32_to_json(self):
        msg = RSP_K32()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_K32"
