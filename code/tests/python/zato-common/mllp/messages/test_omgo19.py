from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import OMG_O19


class TestOmgO19:
    """Comprehensive tests for OmgO19 message."""

    def test_omg_o19_create(self):
        msg = OMG_O19()
        assert msg._structure_id == "OMG_O19"

    def test_omg_o19_segment_access(self):
        msg = OMG_O19()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"

    def test_omg_o19_to_dict(self):
        msg = OMG_O19()

        result = msg.to_dict()

        assert result["_structure_id"] == "OMG_O19"

    def test_omg_o19_to_json(self):
        msg = OMG_O19()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "OMG_O19"
