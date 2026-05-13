from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import EarU08
from zato.hl7v2.v2_9.segments import ECD, ECR, EQU, MSH, SAC, UAC


class TestEarU08:
    """Comprehensive tests for EarU08 message."""

    def test_ear_u08_create(self):
        msg = EarU08()
        assert msg._structure_id == "EAR_U08"

    def test_ear_u08_segment_access(self):
        msg = EarU08()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"
        assert msg.ecd._segment_id == "ECD"
        assert msg.sac._segment_id == "SAC"
        assert msg.ecr._segment_id == "ECR"

    def test_ear_u08_to_dict(self):
        msg = EarU08()

        result = msg.to_dict()

        assert result["_structure_id"] == "EAR_U08"

    def test_ear_u08_to_json(self):
        msg = EarU08()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "EAR_U08"
