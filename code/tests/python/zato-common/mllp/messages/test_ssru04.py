from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import SsrU04
from zato.hl7v2.v2_9.segments import EQU, MSH, SAC, UAC


class TestSsrU04:
    """Comprehensive tests for SsrU04 message."""

    def test_ssr_u04_create(self):
        msg = SsrU04()
        assert msg._structure_id == "SSR_U04"

    def test_ssr_u04_segment_access(self):
        msg = SsrU04()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"
        assert msg.sac._segment_id == "SAC"

    def test_ssr_u04_to_dict(self):
        msg = SsrU04()

        result = msg.to_dict()

        assert result["_structure_id"] == "SSR_U04"

    def test_ssr_u04_to_json(self):
        msg = SsrU04()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "SSR_U04"
