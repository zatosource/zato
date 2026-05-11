from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import QvrQ17
from zato.hl7v2.v2_9.segments import DSC, MSH, QPD, RCP, UAC


class TestQvrQ17:
    """Comprehensive tests for QvrQ17 message."""

    def test_qvr_q17_create(self):
        msg = QvrQ17()
        assert msg._structure_id == "QVR_Q17"

    def test_qvr_q17_segment_access(self):
        msg = QvrQ17()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"
        assert msg.dsc._segment_id == "DSC"

    def test_qvr_q17_to_dict(self):
        msg = QvrQ17()

        result = msg.to_dict()

        assert result["_structure_id"] == "QVR_Q17"

    def test_qvr_q17_to_json(self):
        msg = QvrQ17()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QVR_Q17"
