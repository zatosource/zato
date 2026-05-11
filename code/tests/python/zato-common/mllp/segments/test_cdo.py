from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import CDO


set_id_cdo = "test_set_id_cdo"
action_code = "test_action_code"


class TestCDO:
    """Comprehensive tests for CDO segment."""

    def test_cdo_build_and_verify(self):
        seg = CDO()

        seg.set_id_cdo = set_id_cdo
        seg.action_code = action_code

        assert seg.set_id_cdo == set_id_cdo
        assert seg.action_code == action_code

    def test_cdo_to_dict(self):
        seg = CDO()

        seg.set_id_cdo = set_id_cdo
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "CDO"
        assert result["set_id_cdo"] == set_id_cdo
        assert result["action_code"] == action_code

    def test_cdo_to_json(self):
        seg = CDO()

        seg.set_id_cdo = set_id_cdo
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CDO"
        assert result["set_id_cdo"] == set_id_cdo
        assert result["action_code"] == action_code
