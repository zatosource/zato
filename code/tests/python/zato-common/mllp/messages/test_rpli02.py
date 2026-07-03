from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import RPL_I02


class TestRplI02:
    """Comprehensive tests for RplI02 message."""

    def test_rpl_i02_create(self):
        msg = RPL_I02()
        assert msg._structure_id == "RPL_I02"

    def test_rpl_i02_segment_access(self):
        msg = RPL_I02()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.prd._segment_id == "PRD"
        assert msg.dsc._segment_id == "DSC"

    def test_rpl_i02_to_dict(self):
        msg = RPL_I02()

        result = msg.to_dict()

        assert result["_structure_id"] == "RPL_I02"

    def test_rpl_i02_to_json(self):
        msg = RPL_I02()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RPL_I02"
