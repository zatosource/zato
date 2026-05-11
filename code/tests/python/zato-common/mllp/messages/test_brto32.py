from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import BrtO32
from zato.hl7v2.v2_9.segments import BPO, MSA, MSH, ORC, PID, TQ1, UAC


class TestBrtO32:
    """Comprehensive tests for BrtO32 message."""

    def test_brt_o32_create(self):
        msg = BrtO32()
        assert msg._structure_id == "BRT_O32"

    def test_brt_o32_segment_access(self):
        msg = BrtO32()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.bpo._segment_id == "BPO"

    def test_brt_o32_to_dict(self):
        msg = BrtO32()

        result = msg.to_dict()

        assert result["_structure_id"] == "BRT_O32"

    def test_brt_o32_to_json(self):
        msg = BrtO32()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "BRT_O32"
