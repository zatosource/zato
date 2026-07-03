from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RSP_O33


class TestRspO33:
    """Comprehensive tests for RspO33 message."""

    def test_rsp_o33_create(self):
        msg = RSP_O33()
        assert msg._structure_id == "RSP_O33"

    def test_rsp_o33_segment_access(self):
        msg = RSP_O33()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"

    def test_rsp_o33_to_dict(self):
        msg = RSP_O33()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_O33"

    def test_rsp_o33_to_json(self):
        msg = RSP_O33()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_O33"
