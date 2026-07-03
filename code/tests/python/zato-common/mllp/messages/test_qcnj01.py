from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import QCN_J01


class TestQcnJ01:
    """Comprehensive tests for QcnJ01 message."""

    def test_qcn_j01_create(self):
        msg = QCN_J01()
        assert msg._structure_id == "QCN_J01"

    def test_qcn_j01_segment_access(self):
        msg = QCN_J01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.qid._segment_id == "QID"

    def test_qcn_j01_to_dict(self):
        msg = QCN_J01()

        result = msg.to_dict()

        assert result["_structure_id"] == "QCN_J01"

    def test_qcn_j01_to_json(self):
        msg = QCN_J01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QCN_J01"
