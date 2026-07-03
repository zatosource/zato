from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORL_O55


class TestOrlO55:
    """Comprehensive tests for OrlO55 message."""

    def test_orl_o55_create(self):
        msg = ORL_O55()
        assert msg._structure_id == "ORL_O55"

    def test_orl_o55_segment_access(self):
        msg = ORL_O55()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"

    def test_orl_o55_to_dict(self):
        msg = ORL_O55()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORL_O55"

    def test_orl_o55_to_json(self):
        msg = ORL_O55()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORL_O55"
