from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RtbKnn
from zato.hl7v2.v2_9.segments import DSC, ERR, MSA, MSH, QAK, QPD, UAC


class TestRtbKnn:
    """Comprehensive tests for RtbKnn message."""

    def test_rtb_knn_create(self):
        msg = RtbKnn()
        assert msg._structure_id == "RTB_Knn"

    def test_rtb_knn_segment_access(self):
        msg = RtbKnn()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.err._segment_id == "ERR"
        assert msg.qak._segment_id == "QAK"
        assert msg.qpd._segment_id == "QPD"
        assert msg.dsc._segment_id == "DSC"

    def test_rtb_knn_to_dict(self):
        msg = RtbKnn()

        result = msg.to_dict()

        assert result["_structure_id"] == "RTB_Knn"

    def test_rtb_knn_to_json(self):
        msg = RtbKnn()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RTB_Knn"
