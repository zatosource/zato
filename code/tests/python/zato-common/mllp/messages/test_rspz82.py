from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RSP_Z82


class TestRspZ82:
    """Comprehensive tests for RspZ82 message."""

    def test_rsp_z82_create(self):
        msg = RSP_Z82()
        assert msg._structure_id == "RSP_Z82"

    def test_rsp_z82_segment_access(self):
        msg = RSP_Z82()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_z82_to_dict(self):
        msg = RSP_Z82()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_Z82"

    def test_rsp_z82_to_json(self):
        msg = RSP_Z82()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_Z82"
