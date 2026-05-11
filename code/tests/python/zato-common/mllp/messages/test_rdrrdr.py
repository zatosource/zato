from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RdrRdr
from zato.hl7v2.v2_9.segments import DSC, MSA, MSH, ORC, PID, RXD, RXE, SFT, TQ1, UAC


class TestRdrRdr:
    """Comprehensive tests for RdrRdr message."""

    def test_rdr_rdr_create(self):
        msg = RdrRdr()
        assert msg._structure_id == "RDR_RDR"

    def test_rdr_rdr_segment_access(self):
        msg = RdrRdr()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.sft._segment_id == "SFT"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxe._segment_id == "RXE"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxd._segment_id == "RXD"
        assert msg.dsc._segment_id == "DSC"

    def test_rdr_rdr_to_dict(self):
        msg = RdrRdr()

        result = msg.to_dict()

        assert result["_structure_id"] == "RDR_RDR"

    def test_rdr_rdr_to_json(self):
        msg = RdrRdr()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RDR_RDR"
