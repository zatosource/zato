from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import BrpO30
from zato.hl7v2.v2_9.segments import BPO, MSA, MSH, ORC, PID, TQ1, UAC


class TestBrpO30:
    """Comprehensive tests for BrpO30 message."""

    def test_brp_o30_create(self):
        msg = BrpO30()
        assert msg._structure_id == "BRP_O30"

    def test_brp_o30_segment_access(self):
        msg = BrpO30()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.bpo._segment_id == "BPO"

    def test_brp_o30_to_dict(self):
        msg = BrpO30()

        result = msg.to_dict()

        assert result["_structure_id"] == "BRP_O30"

    def test_brp_o30_to_json(self):
        msg = BrpO30()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "BRP_O30"
