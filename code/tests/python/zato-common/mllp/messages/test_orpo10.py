from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OrpO10
from zato.hl7v2.v2_9.segments import MSA, MSH, ORC, PID, RXC, RXO, TQ1, UAC


class TestOrpO10:
    """Comprehensive tests for OrpO10 message."""

    def test_orp_o10_create(self):
        msg = OrpO10()
        assert msg._structure_id == "ORP_O10"

    def test_orp_o10_segment_access(self):
        msg = OrpO10()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxo._segment_id == "RXO"
        assert msg.rxc._segment_id == "RXC"

    def test_orp_o10_to_dict(self):
        msg = OrpO10()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORP_O10"

    def test_orp_o10_to_json(self):
        msg = OrpO10()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORP_O10"
