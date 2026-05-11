from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RqpI04
from zato.hl7v2.v2_9.segments import MSH, PID, PRD, UAC


class TestRqpI04:
    """Comprehensive tests for RqpI04 message."""

    def test_rqp_i04_create(self):
        msg = RqpI04()
        assert msg._structure_id == "RQP_I04"

    def test_rqp_i04_segment_access(self):
        msg = RqpI04()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.prd._segment_id == "PRD"
        assert msg.pid._segment_id == "PID"

    def test_rqp_i04_to_dict(self):
        msg = RqpI04()

        result = msg.to_dict()

        assert result["_structure_id"] == "RQP_I04"

    def test_rqp_i04_to_json(self):
        msg = RqpI04()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RQP_I04"
