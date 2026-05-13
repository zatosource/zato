from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OrlO53
from zato.hl7v2.v2_9.segments import MSA, MSH, OBR, ORC, PID, SPM, TQ1, UAC


class TestOrlO53:
    """Comprehensive tests for OrlO53 message."""

    def test_orl_o53_create(self):
        msg = OrlO53()
        assert msg._structure_id == "ORL_O53"

    def test_orl_o53_segment_access(self):
        msg = OrlO53()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.tq1._segment_id == "TQ1"
        assert msg.obr._segment_id == "OBR"
        assert msg.spm._segment_id == "SPM"

    def test_orl_o53_to_dict(self):
        msg = OrlO53()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORL_O53"

    def test_orl_o53_to_json(self):
        msg = OrlO53()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORL_O53"
