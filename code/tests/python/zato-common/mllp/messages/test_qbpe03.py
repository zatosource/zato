from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import QBP_E03


class TestQbpE03:
    """Comprehensive tests for QbpE03 message."""

    def test_qbp_e03_create(self):
        msg = QBP_E03()
        assert msg._structure_id == "QBP_E03"

    def test_qbp_e03_segment_access(self):
        msg = QBP_E03()

        assert msg.msh._segment_id == "MSH"

    def test_qbp_e03_to_dict(self):
        msg = QBP_E03()

        result = msg.to_dict()

        assert result["_structure_id"] == "QBP_E03"

    def test_qbp_e03_to_json(self):
        msg = QBP_E03()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QBP_E03"
