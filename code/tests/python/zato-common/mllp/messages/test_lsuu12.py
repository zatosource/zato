from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import LsuU12
from zato.hl7v2.v2_9.segments import EQU, MSH, UAC


class TestLsuU12:
    """Comprehensive tests for LsuU12 message."""

    def test_lsu_u12_create(self):
        msg = LsuU12()
        assert msg._structure_id == "LSU_U12"

    def test_lsu_u12_segment_access(self):
        msg = LsuU12()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"

    def test_lsu_u12_to_dict(self):
        msg = LsuU12()

        result = msg.to_dict()

        assert result["_structure_id"] == "LSU_U12"

    def test_lsu_u12_to_json(self):
        msg = LsuU12()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "LSU_U12"
