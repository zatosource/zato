from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RSP_K31


class TestRspK31:
    """Comprehensive tests for RspK31 message."""

    def test_rsp_k31_create(self):
        msg = RSP_K31()
        assert msg._structure_id == "RSP_K31"

    def test_rsp_k31_segment_access(self):
        msg = RSP_K31()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_k31_to_dict(self):
        msg = RSP_K31()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_K31"

    def test_rsp_k31_to_json(self):
        msg = RSP_K31()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_K31"
