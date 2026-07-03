from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORX_O58


class TestOrxO58:
    """Comprehensive tests for OrxO58 message."""

    def test_orx_o58_create(self):
        msg = ORX_O58()
        assert msg._structure_id == "ORX_O58"

    def test_orx_o58_segment_access(self):
        msg = ORX_O58()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"

    def test_orx_o58_to_dict(self):
        msg = ORX_O58()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORX_O58"

    def test_orx_o58_to_json(self):
        msg = ORX_O58()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORX_O58"
