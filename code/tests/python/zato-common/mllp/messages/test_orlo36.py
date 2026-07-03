from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORL_O36


class TestOrlO36:
    """Comprehensive tests for OrlO36 message."""

    def test_orl_o36_create(self):
        msg = ORL_O36()
        assert msg._structure_id == "ORL_O36"

    def test_orl_o36_segment_access(self):
        msg = ORL_O36()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"

    def test_orl_o36_to_dict(self):
        msg = ORL_O36()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORL_O36"

    def test_orl_o36_to_json(self):
        msg = ORL_O36()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORL_O36"
