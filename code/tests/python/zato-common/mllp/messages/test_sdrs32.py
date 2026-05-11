from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import SdrS32
from zato.hl7v2.v2_9.segments import MSH, SDD, UAC


class TestSdrS32:
    """Comprehensive tests for SdrS32 message."""

    def test_sdr_s32_create(self):
        msg = SdrS32()
        assert msg._structure_id == "SDR_S32"

    def test_sdr_s32_segment_access(self):
        msg = SdrS32()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.sdd._segment_id == "SDD"

    def test_sdr_s32_to_dict(self):
        msg = SdrS32()

        result = msg.to_dict()

        assert result["_structure_id"] == "SDR_S32"

    def test_sdr_s32_to_json(self):
        msg = SdrS32()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "SDR_S32"
