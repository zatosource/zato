from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import QBP_Q15


class TestQbpQ15:
    """Comprehensive tests for QbpQ15 message."""

    def test_qbp_q15_create(self):
        msg = QBP_Q15()
        assert msg._structure_id == "QBP_Q15"

    def test_qbp_q15_segment_access(self):
        msg = QBP_Q15()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"
        assert msg.dsc._segment_id == "DSC"

    def test_qbp_q15_to_dict(self):
        msg = QBP_Q15()

        result = msg.to_dict()

        assert result["_structure_id"] == "QBP_Q15"

    def test_qbp_q15_to_json(self):
        msg = QBP_Q15()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QBP_Q15"
