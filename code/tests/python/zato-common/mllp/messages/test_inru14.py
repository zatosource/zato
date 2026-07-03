from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import INR_U14


class TestInrU14:
    """Comprehensive tests for InrU14 message."""

    def test_inr_u14_create(self):
        msg = INR_U14()
        assert msg._structure_id == "INR_U14"

    def test_inr_u14_segment_access(self):
        msg = INR_U14()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"

    def test_inr_u14_to_dict(self):
        msg = INR_U14()

        result = msg.to_dict()

        assert result["_structure_id"] == "INR_U14"

    def test_inr_u14_to_json(self):
        msg = INR_U14()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "INR_U14"
