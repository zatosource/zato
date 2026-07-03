from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import QBP_Q11


class TestQbpQ11:
    """Comprehensive tests for QbpQ11 message."""

    def test_qbp_q11_create(self):
        msg = QBP_Q11()
        assert msg._structure_id == "QBP_Q11"

    def test_qbp_q11_segment_access(self):
        msg = QBP_Q11()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"
        assert msg.dsc._segment_id == "DSC"

    def test_qbp_q11_to_dict(self):
        msg = QBP_Q11()

        result = msg.to_dict()

        assert result["_structure_id"] == "QBP_Q11"

    def test_qbp_q11_to_json(self):
        msg = QBP_Q11()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QBP_Q11"
