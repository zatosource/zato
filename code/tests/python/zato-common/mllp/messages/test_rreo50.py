from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RRE_O50


class TestRreO50:
    """Comprehensive tests for RreO50 message."""

    def test_rre_o50_create(self):
        msg = RRE_O50()
        assert msg._structure_id == "RRE_O50"

    def test_rre_o50_segment_access(self):
        msg = RRE_O50()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"

    def test_rre_o50_to_dict(self):
        msg = RRE_O50()

        result = msg.to_dict()

        assert result["_structure_id"] == "RRE_O50"

    def test_rre_o50_to_json(self):
        msg = RRE_O50()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RRE_O50"
