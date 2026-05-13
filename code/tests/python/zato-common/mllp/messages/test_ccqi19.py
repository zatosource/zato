from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import CcqI19
from zato.hl7v2.v2_9.segments import MSH, PRD, RF1, UAC


class TestCcqI19:
    """Comprehensive tests for CcqI19 message."""

    def test_ccq_i19_create(self):
        msg = CcqI19()
        assert msg._structure_id == "CCQ_I19"

    def test_ccq_i19_segment_access(self):
        msg = CcqI19()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.rf1._segment_id == "RF1"
        assert msg.prd._segment_id == "PRD"

    def test_ccq_i19_to_dict(self):
        msg = CcqI19()

        result = msg.to_dict()

        assert result["_structure_id"] == "CCQ_I19"

    def test_ccq_i19_to_json(self):
        msg = CcqI19()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "CCQ_I19"
