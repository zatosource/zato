from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import QbpE22
from zato.hl7v2.v2_9.segments import MSH, QPD, RCP


class TestQbpE22:
    """Comprehensive tests for QbpE22 message."""

    def test_qbp_e22_create(self):
        msg = QbpE22()
        assert msg._structure_id == "QBP_E22"

    def test_qbp_e22_segment_access(self):
        msg = QbpE22()

        assert msg.msh._segment_id == "MSH"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"

    def test_qbp_e22_to_dict(self):
        msg = QbpE22()

        result = msg.to_dict()

        assert result["_structure_id"] == "QBP_E22"

    def test_qbp_e22_to_json(self):
        msg = QbpE22()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QBP_E22"
