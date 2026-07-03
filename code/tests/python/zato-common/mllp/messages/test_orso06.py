from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import ORS_O06


class TestOrsO06:
    """Comprehensive tests for OrsO06 message."""

    def test_ors_o06_create(self):
        msg = ORS_O06()
        assert msg._structure_id == "ORS_O06"

    def test_ors_o06_segment_access(self):
        msg = ORS_O06()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"

    def test_ors_o06_to_dict(self):
        msg = ORS_O06()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORS_O06"

    def test_ors_o06_to_json(self):
        msg = ORS_O06()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORS_O06"
