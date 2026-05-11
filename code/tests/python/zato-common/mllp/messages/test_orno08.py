from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OrnO08
from zato.hl7v2.v2_9.segments import MSA, MSH, ORC, PID, RQ1, RQD, TQ1, UAC


class TestOrnO08:
    """Comprehensive tests for OrnO08 message."""

    def test_orn_o08_create(self):
        msg = OrnO08()
        assert msg._structure_id == "ORN_O08"

    def test_orn_o08_segment_access(self):
        msg = OrnO08()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rqd._segment_id == "RQD"
        assert msg.rq1._segment_id == "RQ1"

    def test_orn_o08_to_dict(self):
        msg = OrnO08()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORN_O08"

    def test_orn_o08_to_json(self):
        msg = OrnO08()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORN_O08"
