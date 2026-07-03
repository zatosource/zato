from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OMN_O07


class TestOmnO07:
    """Comprehensive tests for OmnO07 message."""

    def test_omn_o07_create(self):
        msg = OMN_O07()
        assert msg._structure_id == "OMN_O07"

    def test_omn_o07_segment_access(self):
        msg = OMN_O07()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_omn_o07_to_dict(self):
        msg = OMN_O07()

        result = msg.to_dict()

        assert result["_structure_id"] == "OMN_O07"

    def test_omn_o07_to_json(self):
        msg = OMN_O07()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OMN_O07"
