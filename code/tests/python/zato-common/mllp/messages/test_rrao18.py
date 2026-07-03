from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RRA_O18


class TestRraO18:
    """Comprehensive tests for RraO18 message."""

    def test_rra_o18_create(self):
        msg = RRA_O18()
        assert msg._structure_id == "RRA_O18"

    def test_rra_o18_segment_access(self):
        msg = RRA_O18()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"

    def test_rra_o18_to_dict(self):
        msg = RRA_O18()

        result = msg.to_dict()

        assert result["_structure_id"] == "RRA_O18"

    def test_rra_o18_to_json(self):
        msg = RRA_O18()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RRA_O18"
