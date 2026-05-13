from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RdyK15
from zato.hl7v2.v2_9.segments import DSC, ERR, MSA, MSH, QAK, QPD, UAC


class TestRdyK15:
    """Comprehensive tests for RdyK15 message."""

    def test_rdy_k15_create(self):
        msg = RdyK15()
        assert msg._structure_id == "RDY_K15"

    def test_rdy_k15_segment_access(self):
        msg = RdyK15()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.dsc._segment_id == "DSC"

    def test_rdy_k15_to_dict(self):
        msg = RdyK15()

        result = msg.to_dict()

        assert result["_structure_id"] == "RDY_K15"

    def test_rdy_k15_to_json(self):
        msg = RdyK15()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RDY_K15"
