from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import INU_U05


class TestInuU05:
    """Comprehensive tests for InuU05 message."""

    def test_inu_u05_create(self):
        msg = INU_U05()
        assert msg._structure_id == "INU_U05"

    def test_inu_u05_segment_access(self):
        msg = INU_U05()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"

    def test_inu_u05_to_dict(self):
        msg = INU_U05()

        result = msg.to_dict()

        assert result["_structure_id"] == "INU_U05"

    def test_inu_u05_to_json(self):
        msg = INU_U05()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "INU_U05"
