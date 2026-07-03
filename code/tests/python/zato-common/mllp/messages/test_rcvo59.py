from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RCV_O59


class TestRcvO59:
    """Comprehensive tests for RcvO59 message."""

    def test_rcv_o59_create(self):
        msg = RCV_O59()
        assert msg._structure_id == "RCV_O59"

    def test_rcv_o59_segment_access(self):
        msg = RCV_O59()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_rcv_o59_to_dict(self):
        msg = RCV_O59()

        result = msg.to_dict()

        assert result["_structure_id"] == "RCV_O59"

    def test_rcv_o59_to_json(self):
        msg = RCV_O59()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RCV_O59"
