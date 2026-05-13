from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import SsuU03
from zato.hl7v2.v2_9.segments import EQU, MSH, SAC, SPM, UAC


class TestSsuU03:
    """Comprehensive tests for SsuU03 message."""

    def test_ssu_u03_create(self):
        msg = SsuU03()
        assert msg._structure_id == "SSU_U03"

    def test_ssu_u03_segment_access(self):
        msg = SsuU03()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"
        assert msg.sac._segment_id == "SAC"
        assert msg.spm._segment_id == "SPM"

    def test_ssu_u03_to_dict(self):
        msg = SsuU03()

        result = msg.to_dict()

        assert result["_structure_id"] == "SSU_U03"

    def test_ssu_u03_to_json(self):
        msg = SsuU03()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "SSU_U03"
