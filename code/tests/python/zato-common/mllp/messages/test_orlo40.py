from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORL_O40


class TestOrlO40:
    """Comprehensive tests for OrlO40 message."""

    def test_orl_o40_create(self):
        msg = ORL_O40()
        assert msg._structure_id == "ORL_O40"

    def test_orl_o40_segment_access(self):
        msg = ORL_O40()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"

    def test_orl_o40_to_dict(self):
        msg = ORL_O40()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORL_O40"

    def test_orl_o40_to_json(self):
        msg = ORL_O40()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORL_O40"
