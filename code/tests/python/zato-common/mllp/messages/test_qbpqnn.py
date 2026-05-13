from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import QbpQnn
from zato.hl7v2.v2_9.segments import DSC, MSH, QPD, RCP, RDF, UAC


class TestQbpQnn:
    """Comprehensive tests for QbpQnn message."""

    def test_qbp_qnn_create(self):
        msg = QbpQnn()
        assert msg._structure_id == "QBP_Qnn"

    def test_qbp_qnn_segment_access(self):
        msg = QbpQnn()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rdf._segment_id == "RDF"
        assert msg.rcp._segment_id == "RCP"
        assert msg.dsc._segment_id == "DSC"

    def test_qbp_qnn_to_dict(self):
        msg = QbpQnn()

        result = msg.to_dict()

        assert result["_structure_id"] == "QBP_Qnn"

    def test_qbp_qnn_to_json(self):
        msg = QbpQnn()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QBP_Qnn"
