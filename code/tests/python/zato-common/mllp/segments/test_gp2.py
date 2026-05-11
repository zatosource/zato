from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import GP2


number_of_service_units = "test_number_of_service_un"
pay_rate_per_service_unit = "test_pay_rate_per_service"


class TestGP2:
    """Comprehensive tests for GP2 segment."""

    def test_gp2_build_and_verify(self):
        seg = GP2()

        seg.number_of_service_units = number_of_service_units
        seg.pay_rate_per_service_unit = pay_rate_per_service_unit

        assert seg.number_of_service_units == number_of_service_units
        assert seg.pay_rate_per_service_unit == pay_rate_per_service_unit

    def test_gp2_to_dict(self):
        seg = GP2()

        seg.number_of_service_units = number_of_service_units
        seg.pay_rate_per_service_unit = pay_rate_per_service_unit

        result = seg.to_dict()

        assert result["_segment_id"] == "GP2"
        assert result["number_of_service_units"] == number_of_service_units
        assert result["pay_rate_per_service_unit"] == pay_rate_per_service_unit

    def test_gp2_to_json(self):
        seg = GP2()

        seg.number_of_service_units = number_of_service_units
        seg.pay_rate_per_service_unit = pay_rate_per_service_unit

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "GP2"
        assert result["number_of_service_units"] == number_of_service_units
        assert result["pay_rate_per_service_unit"] == pay_rate_per_service_unit
