from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RSP_E03


class TestRspE03:
    """Comprehensive tests for RspE03 message."""

    def test_rsp_e03_create(self):
        msg = RSP_E03()
        assert msg._structure_id == "RSP_E03"

    def test_rsp_e03_segment_access(self):
        msg = RSP_E03()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"

    def test_rsp_e03_to_dict(self):
        msg = RSP_E03()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_E03"

    def test_rsp_e03_to_json(self):
        msg = RSP_E03()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_E03"
