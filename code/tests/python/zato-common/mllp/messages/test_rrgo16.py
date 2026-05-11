from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RrgO16
from zato.hl7v2.v2_9.segments import MSA, MSH, ORC, PID, RXG, TQ1, UAC


class TestRrgO16:
    """Comprehensive tests for RrgO16 message."""

    def test_rrg_o16_create(self):
        msg = RrgO16()
        assert msg._structure_id == "RRG_O16"

    def test_rrg_o16_segment_access(self):
        msg = RrgO16()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxg._segment_id == "RXG"
        assert msg.tq1._segment_id == "TQ1"

    def test_rrg_o16_to_dict(self):
        msg = RrgO16()

        result = msg.to_dict()

        assert result["_structure_id"] == "RRG_O16"

    def test_rrg_o16_to_json(self):
        msg = RrgO16()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RRG_O16"
