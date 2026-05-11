from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import QbpO34
from zato.hl7v2.v2_9.segments import MSH, QPD, RCP, UAC


class TestQbpO34:
    """Comprehensive tests for QbpO34 message."""

    def test_qbp_o34_create(self):
        msg = QbpO34()
        assert msg._structure_id == "QBP_O34"

    def test_qbp_o34_segment_access(self):
        msg = QbpO34()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"

    def test_qbp_o34_to_dict(self):
        msg = QbpO34()

        result = msg.to_dict()

        assert result["_structure_id"] == "QBP_O34"

    def test_qbp_o34_to_json(self):
        msg = QbpO34()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QBP_O34"
