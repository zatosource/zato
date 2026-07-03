from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RSP_K11


class TestRspK11:
    """Comprehensive tests for RspK11 message."""

    def test_rsp_k11_create(self):
        msg = RSP_K11()
        assert msg._structure_id == "RSP_K11"

    def test_rsp_k11_segment_access(self):
        msg = RSP_K11()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_k11_to_dict(self):
        msg = RSP_K11()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_K11"

    def test_rsp_k11_to_json(self):
        msg = RSP_K11()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_K11"
