from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import QsbQ16
from zato.hl7v2.v2_9.segments import DSC, MSH, QPD, RCP, UAC


class TestQsbQ16:
    """Comprehensive tests for QsbQ16 message."""

    def test_qsb_q16_create(self):
        msg = QsbQ16()
        assert msg._structure_id == "QSB_Q16"

    def test_qsb_q16_segment_access(self):
        msg = QsbQ16()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.qpd._segment_id == "QPD"
        assert msg.rcp._segment_id == "RCP"
        assert msg.dsc._segment_id == "DSC"

    def test_qsb_q16_to_dict(self):
        msg = QsbQ16()

        result = msg.to_dict()

        assert result["_structure_id"] == "QSB_Q16"

    def test_qsb_q16_to_json(self):
        msg = QsbQ16()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "QSB_Q16"
