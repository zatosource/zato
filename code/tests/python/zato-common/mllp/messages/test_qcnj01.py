from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import QcnJ01
from zato.hl7v2.v2_9.segments import MSH, QID, UAC


class TestQcnJ01:
    """Comprehensive tests for QcnJ01 message."""

    def test_qcn_j01_create(self):
        msg = QcnJ01()
        assert msg._structure_id == "QCN_J01"

    def test_qcn_j01_segment_access(self):
        msg = QcnJ01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.qid._segment_id == "QID"

    def test_qcn_j01_to_dict(self):
        msg = QcnJ01()

        result = msg.to_dict()

        assert result["_structure_id"] == "QCN_J01"

    def test_qcn_j01_to_json(self):
        msg = QcnJ01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QCN_J01"
