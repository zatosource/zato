from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import RprI03
from zato.hl7v2.v2_9.segments import MSA, MSH, PRD, UAC


class TestRprI03:
    """Comprehensive tests for RprI03 message."""

    def test_rpr_i03_create(self):
        msg = RprI03()
        assert msg._structure_id == "RPR_I03"

    def test_rpr_i03_segment_access(self):
        msg = RprI03()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.prd._segment_id == "PRD"

    def test_rpr_i03_to_dict(self):
        msg = RprI03()

        result = msg.to_dict()

        assert result["_structure_id"] == "RPR_I03"

    def test_rpr_i03_to_json(self):
        msg = RprI03()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "RPR_I03"
