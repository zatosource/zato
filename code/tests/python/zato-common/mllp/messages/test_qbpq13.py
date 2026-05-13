from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import QbpQ13
from zato.hl7v2.v2_9.segments import DSC, MSH, PID, QPD, RCP, RDF, UAC


class TestQbpQ13:
    """Comprehensive tests for QbpQ13 message."""

    def test_qbp_q13_create(self):
        msg = QbpQ13()
        assert msg._structure_id == "QBP_Q13"

    def test_qbp_q13_segment_access(self):
        msg = QbpQ13()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.qpd._segment_id == "QPD"
        assert msg.pid._segment_id == "PID"
        assert msg.rdf._segment_id == "RDF"
        assert msg.rcp._segment_id == "RCP"
        assert msg.rdf._segment_id == "RDF"
        assert msg.dsc._segment_id == "DSC"

    def test_qbp_q13_to_dict(self):
        msg = QbpQ13()

        result = msg.to_dict()

        assert result["_structure_id"] == "QBP_Q13"

    def test_qbp_q13_to_json(self):
        msg = QbpQ13()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QBP_Q13"
