from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import SSR_U04


class TestSsrU04:
    """Comprehensive tests for SsrU04 message."""

    def test_ssr_u04_create(self):
        msg = SSR_U04()
        assert msg._structure_id == "SSR_U04"

    def test_ssr_u04_segment_access(self):
        msg = SSR_U04()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.equ._segment_id == "EQU"
        assert msg.sac._segment_id == "SAC"

    def test_ssr_u04_to_dict(self):
        msg = SSR_U04()

        result = msg.to_dict()

        assert result["_structure_id"] == "SSR_U04"

    def test_ssr_u04_to_json(self):
        msg = SSR_U04()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "SSR_U04"
