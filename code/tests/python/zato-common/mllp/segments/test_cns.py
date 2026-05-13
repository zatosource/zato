from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import CNS


starting_notification_reference_number = "test_starting_notificatio"
ending_notification_reference_number = "test_ending_notification_"
starting_notification_date_time = "test_starting_notificatio"
ending_notification_date_time = "test_ending_notification_"


class TestCNS:
    """Comprehensive tests for CNS segment."""

    def test_cns_build_and_verify(self):
        seg = CNS()

        seg.starting_notification_reference_number = starting_notification_reference_number
        seg.ending_notification_reference_number = ending_notification_reference_number
        seg.starting_notification_date_time = starting_notification_date_time
        seg.ending_notification_date_time = ending_notification_date_time

        assert seg.starting_notification_reference_number == starting_notification_reference_number
        assert seg.ending_notification_reference_number == ending_notification_reference_number
        assert seg.starting_notification_date_time == starting_notification_date_time
        assert seg.ending_notification_date_time == ending_notification_date_time

    def test_cns_to_dict(self):
        seg = CNS()

        seg.starting_notification_reference_number = starting_notification_reference_number
        seg.ending_notification_reference_number = ending_notification_reference_number
        seg.starting_notification_date_time = starting_notification_date_time
        seg.ending_notification_date_time = ending_notification_date_time

        result = seg.to_dict()

        assert result["_segment_id"] == "CNS"
        assert result["starting_notification_reference_number"] == starting_notification_reference_number
        assert result["ending_notification_reference_number"] == ending_notification_reference_number
        assert result["starting_notification_date_time"] == starting_notification_date_time
        assert result["ending_notification_date_time"] == ending_notification_date_time

    def test_cns_to_json(self):
        seg = CNS()

        seg.starting_notification_reference_number = starting_notification_reference_number
        seg.ending_notification_reference_number = ending_notification_reference_number
        seg.starting_notification_date_time = starting_notification_date_time
        seg.ending_notification_date_time = ending_notification_date_time

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CNS"
        assert result["starting_notification_reference_number"] == starting_notification_reference_number
        assert result["ending_notification_reference_number"] == ending_notification_reference_number
        assert result["starting_notification_date_time"] == starting_notification_date_time
        assert result["ending_notification_date_time"] == ending_notification_date_time
