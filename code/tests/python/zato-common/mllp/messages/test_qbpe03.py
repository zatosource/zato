from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import QbpE03
from zato.hl7v2.v2_9.segments import MSH, QPD, RCP


class TestQbpE03:
    """Comprehensive tests for QbpE03 message."""

    def test_qbp_e03_create(self):
        msg = QbpE03()
        assert msg._structure_id == "QBP_E03"

    def test_qbp_e03_segment_access(self):
        msg = QbpE03()

        assert msg.msh._segment_id == "MSH"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"

    def test_qbp_e03_to_dict(self):
        msg = QbpE03()

        result = msg.to_dict()

        assert result["_structure_id"] == "QBP_E03"

    def test_qbp_e03_to_json(self):
        msg = QbpE03()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QBP_E03"
