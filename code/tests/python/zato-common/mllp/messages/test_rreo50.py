from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RreO50
from zato.hl7v2.v2_9.segments import MSA, MSH, ORC, PID, RXE, TQ1, UAC


class TestRreO50:
    """Comprehensive tests for RreO50 message."""

    def test_rre_o50_create(self):
        msg = RreO50()
        assert msg._structure_id == "RRE_O50"

    def test_rre_o50_segment_access(self):
        msg = RreO50()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rxe._segment_id == "RXE"
        assert msg.tq1._segment_id == "TQ1"

    def test_rre_o50_to_dict(self):
        msg = RreO50()

        result = msg.to_dict()

        assert result["_structure_id"] == "RRE_O50"

    def test_rre_o50_to_json(self):
        msg = RreO50()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RRE_O50"
