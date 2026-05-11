from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import MfkM01
from zato.hl7v2.v2_9.segments import MFI, MSA, MSH, UAC


class TestMfkM01:
    """Comprehensive tests for MfkM01 message."""

    def test_mfk_m01_create(self):
        msg = MfkM01()
        assert msg._structure_id == "MFK_M01"

    def test_mfk_m01_segment_access(self):
        msg = MfkM01()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.msa._segment_id == "MSA"
        assert msg.mfi._segment_id == "MFI"

    def test_mfk_m01_to_dict(self):
        msg = MfkM01()

        result = msg.to_dict()

        assert result["_structure_id"] == "MFK_M01"

    def test_mfk_m01_to_json(self):
        msg = MfkM01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "MFK_M01"
