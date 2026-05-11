from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import QbpO33
from zato.hl7v2.v2_9.segments import MSH, QPD, RCP, UAC


class TestQbpO33:
    """Comprehensive tests for QbpO33 message."""

    def test_qbp_o33_create(self):
        msg = QbpO33()
        assert msg._structure_id == "QBP_O33"

    def test_qbp_o33_segment_access(self):
        msg = QbpO33()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"

    def test_qbp_o33_to_dict(self):
        msg = QbpO33()

        result = msg.to_dict()

        assert result["_structure_id"] == "QBP_O33"

    def test_qbp_o33_to_json(self):
        msg = QbpO33()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QBP_O33"
