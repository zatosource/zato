from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.messages import AdtA60
from zato.hl7v2.v2_9.segments import EVN, IAM, MSH, PID, PV1, PV2, UAC


class TestAdtA60:
    """Comprehensive tests for AdtA60 message."""

    def test_adt_a60_create(self):
        msg = AdtA60()
        assert msg._structure_id == "ADT_A60"

    def test_adt_a60_segment_access(self):
        msg = AdtA60()

        assert msg.msh._segment_id == "MSH"
        assert msg.uac._segment_id == "UAC"
        assert msg.evn._segment_id == "EVN"
        assert msg.pid._segment_id == "PID"
        assert msg.pv1._segment_id == "PV1"
        assert msg.pv2._segment_id == "PV2"
        assert msg.iam._segment_id == "IAM"

    def test_adt_a60_to_dict(self):
        msg = AdtA60()

        result = msg.to_dict()

        assert result["_structure_id"] == "ADT_A60"

    def test_adt_a60_to_json(self):
        msg = AdtA60()

        result = json.loads(msg.to_json())

        assert result["_structure_id"] == "ADT_A60"
