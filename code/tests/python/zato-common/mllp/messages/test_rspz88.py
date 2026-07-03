from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RSP_Z88


class TestRspZ88:
    """Comprehensive tests for RspZ88 message."""

    def test_rsp_z88_create(self):
        msg = RSP_Z88()
        assert msg._structure_id == "RSP_Z88"

    def test_rsp_z88_segment_access(self):
        msg = RSP_Z88()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_z88_to_dict(self):
        msg = RSP_Z88()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_Z88"

    def test_rsp_z88_to_json(self):
        msg = RSP_Z88()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_Z88"
