from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RTB_K13


class TestRtbK13:
    """Comprehensive tests for RtbK13 message."""

    def test_rtb_k13_create(self):
        msg = RTB_K13()
        assert msg._structure_id == "RTB_K13"

    def test_rtb_k13_segment_access(self):
        msg = RTB_K13()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.dsc._segment_id == "DSC"

    def test_rtb_k13_to_dict(self):
        msg = RTB_K13()

        result = msg.to_dict()

        assert result["_structure_id"] == "RTB_K13"

    def test_rtb_k13_to_json(self):
        msg = RTB_K13()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RTB_K13"
