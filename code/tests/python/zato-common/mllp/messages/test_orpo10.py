from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORP_O10


class TestOrpO10:
    """Comprehensive tests for OrpO10 message."""

    def test_orp_o10_create(self):
        msg = ORP_O10()
        assert msg._structure_id == "ORP_O10"

    def test_orp_o10_segment_access(self):
        msg = ORP_O10()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"

    def test_orp_o10_to_dict(self):
        msg = ORP_O10()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORP_O10"

    def test_orp_o10_to_json(self):
        msg = ORP_O10()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORP_O10"
