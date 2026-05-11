from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RplI02
from zato.hl7v2.v2_9.segments import DSC, MSA, MSH, PRD, UAC


class TestRplI02:
    """Comprehensive tests for RplI02 message."""

    def test_rpl_i02_create(self):
        msg = RplI02()
        assert msg._structure_id == "RPL_I02"

    def test_rpl_i02_segment_access(self):
        msg = RplI02()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.prd._segment_id == "PRD"
        assert msg.dsc._segment_id == "DSC"

    def test_rpl_i02_to_dict(self):
        msg = RplI02()

        result = msg.to_dict()

        assert result["_structure_id"] == "RPL_I02"

    def test_rpl_i02_to_json(self):
        msg = RplI02()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RPL_I02"
