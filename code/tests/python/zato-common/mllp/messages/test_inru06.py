from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import InrU06
from zato.hl7v2.v2_9.segments import EQU, MSH, UAC


class TestInrU06:
    """Comprehensive tests for InrU06 message."""

    def test_inr_u06_create(self):
        msg = InrU06()
        assert msg._structure_id == "INR_U06"

    def test_inr_u06_segment_access(self):
        msg = InrU06()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"

    def test_inr_u06_to_dict(self):
        msg = InrU06()

        result = msg.to_dict()

        assert result["_structure_id"] == "INR_U06"

    def test_inr_u06_to_json(self):
        msg = InrU06()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "INR_U06"
