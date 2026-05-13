from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OrsO06
from zato.hl7v2.v2_9.segments import MSA, MSH, ORC, PID, RQ1, RQD, TQ1, UAC


class TestOrsO06:
    """Comprehensive tests for OrsO06 message."""

    def test_ors_o06_create(self):
        msg = OrsO06()
        assert msg._structure_id == "ORS_O06"

    def test_ors_o06_segment_access(self):
        msg = OrsO06()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.rqd._segment_id == "RQD"
        assert msg.rq1._segment_id == "RQ1"

    def test_ors_o06_to_dict(self):
        msg = OrsO06()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORS_O06"

    def test_ors_o06_to_json(self):
        msg = OrsO06()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORS_O06"
