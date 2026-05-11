from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import OrxO58
from zato.hl7v2.v2_9.segments import MSA, MSH, ORC, PID, TXA, UAC


class TestOrxO58:
    """Comprehensive tests for OrxO58 message."""

    def test_orx_o58_create(self):
        msg = OrxO58()
        assert msg._structure_id == "ORX_O58"

    def test_orx_o58_segment_access(self):
        msg = OrxO58()

        assert msg.msh._segment_id == "MSH"
        assert msg.msa._segment_id == "MSA"
        assert msg.uac._segment_id == "UAC"
        assert msg.pid._segment_id == "PID"
        assert msg.orc._segment_id == "ORC"
        assert msg.txa._segment_id == "TXA"

    def test_orx_o58_to_dict(self):
        msg = OrxO58()

        result = msg.to_dict()

        assert result["_structure_id"] == "ORX_O58"

    def test_orx_o58_to_json(self):
        msg = OrxO58()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ORX_O58"
