from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import Ack
from zato.hl7v2.v2_9.segments import MSA, MSH, UAC


class TestAck:
    """Comprehensive tests for Ack message."""

    def test_ack_create(self):
        msg = Ack()
        assert msg._structure_id == "ACK"

    def test_ack_segment_access(self):
        msg = Ack()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"

    def test_ack_to_dict(self):
        msg = Ack()

        result = msg.to_dict()

        assert result["_structure_id"] == "ACK"

    def test_ack_to_json(self):
        msg = Ack()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ACK"
