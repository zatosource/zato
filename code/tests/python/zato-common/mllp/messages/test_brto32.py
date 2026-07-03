from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import BRT_O32


class TestBrtO32:
    """Comprehensive tests for BrtO32 message."""

    def test_brt_o32_create(self):
        msg = BRT_O32()
        assert msg._structure_id == "BRT_O32"

    def test_brt_o32_segment_access(self):
        msg = BRT_O32()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"

    def test_brt_o32_to_dict(self):
        msg = BRT_O32()

        result = msg.to_dict()

        assert result["_structure_id"] == "BRT_O32"

    def test_brt_o32_to_json(self):
        msg = BRT_O32()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "BRT_O32"
