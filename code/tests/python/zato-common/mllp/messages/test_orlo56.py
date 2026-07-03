from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORL_O56


class TestOrlO56:
    """Comprehensive tests for OrlO56 message."""

    def test_orl_o56_create(self):
        msg = ORL_O56()
        assert msg._structure_id == "ORL_O56"

    def test_orl_o56_segment_access(self):
        msg = ORL_O56()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"

    def test_orl_o56_to_dict(self):
        msg = ORL_O56()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORL_O56"

    def test_orl_o56_to_json(self):
        msg = ORL_O56()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORL_O56"
