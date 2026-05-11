from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import NDS


notification_reference_number = "test_notification_referen"
notification_date_time = "test_notification_date_ti"


class TestNDS:
    """Comprehensive tests for NDS segment."""

    def test_nds_build_and_verify(self):
        seg = NDS()

        seg.notification_reference_number = notification_reference_number
        seg.notification_date_time = notification_date_time

        assert seg.notification_reference_number == notification_reference_number
        assert seg.notification_date_time == notification_date_time

    def test_nds_to_dict(self):
        seg = NDS()

        seg.notification_reference_number = notification_reference_number
        seg.notification_date_time = notification_date_time

        result = seg.to_dict()

        assert result["_segment_id"] == "NDS"
        assert result["notification_reference_number"] == notification_reference_number
        assert result["notification_date_time"] == notification_date_time

    def test_nds_to_json(self):
        seg = NDS()

        seg.notification_reference_number = notification_reference_number
        seg.notification_date_time = notification_date_time

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "NDS"
        assert result["notification_reference_number"] == notification_reference_number
        assert result["notification_date_time"] == notification_date_time
