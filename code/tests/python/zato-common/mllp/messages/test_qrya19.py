from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import QRY_A19


class TestQryA19:
    """Comprehensive tests for QryA19 message."""

    def test_qry_a19_create(self):
        msg = QRY_A19()
        assert msg._structure_id == "QRY_A19"

    def test_qry_a19_segment_access(self):
        msg = QRY_A19()

        assert msg.msh._segment_id == "MSH"

    def test_qry_a19_to_dict(self):
        msg = QRY_A19()

        result = msg.to_dict()

        assert result["_structure_id"] == "QRY_A19"

    def test_qry_a19_to_json(self):
        msg = QRY_A19()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QRY_A19"
