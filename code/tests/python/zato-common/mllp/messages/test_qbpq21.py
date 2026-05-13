from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import QbpQ21
from zato.hl7v2.v2_9.segments import DSC, MSH, QPD, RCP, UAC


class TestQbpQ21:
    """Comprehensive tests for QbpQ21 message."""

    def test_qbp_q21_create(self):
        msg = QbpQ21()
        assert msg._structure_id == "QBP_Q21"

    def test_qbp_q21_segment_access(self):
        msg = QbpQ21()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"
        assert msg.dsc._segment_id == "DSC"

    def test_qbp_q21_to_dict(self):
        msg = QbpQ21()

        result = msg.to_dict()

        assert result["_structure_id"] == "QBP_Q21"

    def test_qbp_q21_to_json(self):
        msg = QbpQ21()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QBP_Q21"
