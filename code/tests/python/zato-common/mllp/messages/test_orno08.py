from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORN_O08


class TestOrnO08:
    """Comprehensive tests for OrnO08 message."""

    def test_orn_o08_create(self):
        msg = ORN_O08()
        assert msg._structure_id == "ORN_O08"

    def test_orn_o08_segment_access(self):
        msg = ORN_O08()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"

    def test_orn_o08_to_dict(self):
        msg = ORN_O08()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORN_O08"

    def test_orn_o08_to_json(self):
        msg = ORN_O08()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORN_O08"
