from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import IPR


ipr_date_time = "test_ipr_date_time"
expected_payment_date_time = "test_expected_payment_dat"
ipr_checksum = "test_ipr_checksum"


class TestIPR:
    """Comprehensive tests for IPR segment."""

    def test_ipr_build_and_verify(self):
        seg = IPR()

        seg.ipr_date_time = ipr_date_time
        seg.expected_payment_date_time = expected_payment_date_time
        seg.ipr_checksum = ipr_checksum

        assert seg.ipr_date_time == ipr_date_time
        assert seg.expected_payment_date_time == expected_payment_date_time
        assert seg.ipr_checksum == ipr_checksum

    def test_ipr_to_dict(self):
        seg = IPR()

        seg.ipr_date_time = ipr_date_time
        seg.expected_payment_date_time = expected_payment_date_time
        seg.ipr_checksum = ipr_checksum

        result = seg.to_dict()

        assert result["_segment_id"] == "IPR"
        assert result["ipr_date_time"] == ipr_date_time
        assert result["expected_payment_date_time"] == expected_payment_date_time
        assert result["ipr_checksum"] == ipr_checksum

    def test_ipr_to_json(self):
        seg = IPR()

        seg.ipr_date_time = ipr_date_time
        seg.expected_payment_date_time = expected_payment_date_time
        seg.ipr_checksum = ipr_checksum

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "IPR"
        assert result["ipr_date_time"] == ipr_date_time
        assert result["expected_payment_date_time"] == expected_payment_date_time
        assert result["ipr_checksum"] == ipr_checksum
