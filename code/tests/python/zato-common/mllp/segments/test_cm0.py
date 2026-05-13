from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import CM0


set_id_cm0 = "test_set_id_cm0"
title_of_study = "test_title_of_study"
last_irb_approval_date = "test_last_irb_approval_da"
total_accrual_to_date = "test_total_accrual_to_dat"
last_accrual_date = "test_last_accrual_date"


class TestCM0:
    """Comprehensive tests for CM0 segment."""

    def test_cm0_build_and_verify(self):
        seg = CM0()

        seg.set_id_cm0 = set_id_cm0
        seg.title_of_study = title_of_study
        seg.last_irb_approval_date = last_irb_approval_date
        seg.total_accrual_to_date = total_accrual_to_date
        seg.last_accrual_date = last_accrual_date

        assert seg.set_id_cm0 == set_id_cm0
        assert seg.title_of_study == title_of_study
        assert seg.last_irb_approval_date == last_irb_approval_date
        assert seg.total_accrual_to_date == total_accrual_to_date
        assert seg.last_accrual_date == last_accrual_date

    def test_cm0_to_dict(self):
        seg = CM0()

        seg.set_id_cm0 = set_id_cm0
        seg.title_of_study = title_of_study
        seg.last_irb_approval_date = last_irb_approval_date
        seg.total_accrual_to_date = total_accrual_to_date
        seg.last_accrual_date = last_accrual_date

        result = seg.to_dict()

        assert result["_segment_id"] == "CM0"
        assert result["set_id_cm0"] == set_id_cm0
        assert result["title_of_study"] == title_of_study
        assert result["last_irb_approval_date"] == last_irb_approval_date
        assert result["total_accrual_to_date"] == total_accrual_to_date
        assert result["last_accrual_date"] == last_accrual_date

    def test_cm0_to_json(self):
        seg = CM0()

        seg.set_id_cm0 = set_id_cm0
        seg.title_of_study = title_of_study
        seg.last_irb_approval_date = last_irb_approval_date
        seg.total_accrual_to_date = total_accrual_to_date
        seg.last_accrual_date = last_accrual_date

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CM0"
        assert result["set_id_cm0"] == set_id_cm0
        assert result["title_of_study"] == title_of_study
        assert result["last_irb_approval_date"] == last_irb_approval_date
        assert result["total_accrual_to_date"] == total_accrual_to_date
        assert result["last_accrual_date"] == last_accrual_date
