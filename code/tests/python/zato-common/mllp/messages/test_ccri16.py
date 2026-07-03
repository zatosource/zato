from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import CCR_I16


class TestCcrI16:
    """Comprehensive tests for CcrI16 message."""

    def test_ccr_i16_create(self):
        msg = CCR_I16()
        assert msg._structure_id == "CCR_I16"

    def test_ccr_i16_segment_access(self):
        msg = CCR_I16()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_ccr_i16_to_dict(self):
        msg = CCR_I16()

        result = msg.to_dict()

        assert result["_structure_id"] == "CCR_I16"

    def test_ccr_i16_to_json(self):
        msg = CCR_I16()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "CCR_I16"
