from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import QbpZ73
from zato.hl7v2.v2_9.segments import MSH, QPD, RCP, UAC


class TestQbpZ73:
    """Comprehensive tests for QbpZ73 message."""

    def test_qbp_z73_create(self):
        msg = QbpZ73()
        assert msg._structure_id == "QBP_Z73"

    def test_qbp_z73_segment_access(self):
        msg = QbpZ73()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"

    def test_qbp_z73_to_dict(self):
        msg = QbpZ73()

        result = msg.to_dict()

        assert result["_structure_id"] == "QBP_Z73"

    def test_qbp_z73_to_json(self):
        msg = QbpZ73()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QBP_Z73"
