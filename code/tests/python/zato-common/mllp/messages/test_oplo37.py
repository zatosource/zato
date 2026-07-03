from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OPL_O37


class TestOplO37:
    """Comprehensive tests for OplO37 message."""

    def test_opl_o37_create(self):
        msg = OPL_O37()
        assert msg._structure_id == "OPL_O37"

    def test_opl_o37_segment_access(self):
        msg = OPL_O37()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_opl_o37_to_dict(self):
        msg = OPL_O37()

        result = msg.to_dict()

        assert result["_structure_id"] == "OPL_O37"

    def test_opl_o37_to_json(self):
        msg = OPL_O37()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OPL_O37"
