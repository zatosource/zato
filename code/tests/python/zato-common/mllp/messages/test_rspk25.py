from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RspK25
from zato.hl7v2.v2_9.segments import DSC, MSA, MSH, QAK, QPD, RCP, STF, UAC


class TestRspK25:
    """Comprehensive tests for RspK25 message."""

    def test_rsp_k25_create(self):
        msg = RspK25()
        assert msg._structure_id == "RSP_K25"

    def test_rsp_k25_segment_access(self):
        msg = RspK25()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"
        assert msg.stf._segment_id == "STF"
        assert msg.dsc._segment_id == "DSC"

    def test_rsp_k25_to_dict(self):
        msg = RspK25()

        result = msg.to_dict()

        assert result["_structure_id"] == "RSP_K25"

    def test_rsp_k25_to_json(self):
        msg = RspK25()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RSP_K25"
