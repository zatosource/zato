from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RSP_E22


class TestRspE22:
    """Comprehensive tests for RspE22 message."""

    def test_rsp_e22_create(self):
        msg = RSP_E22()
        assert msg._structure_id == "RSP_E22"

    def test_rsp_e22_segment_access(self):
        msg = RSP_E22()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"

    def test_rsp_e22_to_dict(self):
        msg = RSP_E22()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_E22"

    def test_rsp_e22_to_json(self):
        msg = RSP_E22()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_E22"
