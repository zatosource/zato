from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RraO18
from zato.hl7v2.v2_9.segments import MSA, MSH, ORC, PID, RXA, RXR, TQ1, UAC


class TestRraO18:
    """Comprehensive tests for RraO18 message."""

    def test_rra_o18_create(self):
        msg = RraO18()
        assert msg._structure_id == "RRA_O18"

    def test_rra_o18_segment_access(self):
        msg = RraO18()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxa._segment_id == "RXA"
        assert msg.rxr._segment_id == "RXR"

    def test_rra_o18_to_dict(self):
        msg = RraO18()

        result = msg.to_dict()

        assert result["_structure_id"] == "RRA_O18"

    def test_rra_o18_to_json(self):
        msg = RraO18()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RRA_O18"
