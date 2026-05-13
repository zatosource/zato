from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import InuU05
from zato.hl7v2.v2_9.segments import EQU, MSH, UAC


class TestInuU05:
    """Comprehensive tests for InuU05 message."""

    def test_inu_u05_create(self):
        msg = InuU05()
        assert msg._structure_id == "INU_U05"

    def test_inu_u05_segment_access(self):
        msg = InuU05()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"

    def test_inu_u05_to_dict(self):
        msg = InuU05()

        result = msg.to_dict()

        assert result["_structure_id"] == "INU_U05"

    def test_inu_u05_to_json(self):
        msg = InuU05()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "INU_U05"
