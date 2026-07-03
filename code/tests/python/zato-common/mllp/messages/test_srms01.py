from __future__ import annotations

import json

from zato.hl7v2.v2_9.messages import SRM_S01


class TestSrmS01:
    """Comprehensive tests for SrmS01 message."""

    def test_srm_s01_create(self):
        msg = SRM_S01()
        assert msg._structure_id == "SRM_S01"

    def test_srm_s01_segment_access(self):
        msg = SRM_S01()

        assert msg.msh._segment_id == "MSH"
        assert msg.arq._segment_id == "ARQ"
        assert msg.apr._segment_id == "APR"

    def test_srm_s01_to_dict(self):
        msg = SRM_S01()

        result = msg.to_dict()

        assert result["_structure_id"] == "SRM_S01"

    def test_srm_s01_to_json(self):
        msg = SRM_S01()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "SRM_S01"
