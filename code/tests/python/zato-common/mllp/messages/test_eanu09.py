from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import EAN_U09


class TestEanU09:
    """Comprehensive tests for EanU09 message."""

    def test_ean_u09_create(self):
        msg = EAN_U09()
        assert msg._structure_id == "EAN_U09"

    def test_ean_u09_segment_access(self):
        msg = EAN_U09()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"

    def test_ean_u09_to_dict(self):
        msg = EAN_U09()

        result = msg.to_dict()

        assert result["_structure_id"] == "EAN_U09"

    def test_ean_u09_to_json(self):
        msg = EAN_U09()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EAN_U09"
