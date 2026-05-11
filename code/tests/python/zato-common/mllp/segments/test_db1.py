from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import DB1


set_id_db1 = "test_set_id_db1"
disability_indicator = "test_disability_indicator"
disability_start_date = "test_disability_start_dat"
disability_end_date = "test_disability_end_date"
disability_return_to_work_date = "test_disability_return_to"
disability_unable_to_work_date = "test_disability_unable_to"


class TestDB1:
    """Comprehensive tests for DB1 segment."""

    def test_db1_build_and_verify(self):
        seg = DB1()

        seg.set_id_db1 = set_id_db1
        seg.disability_indicator = disability_indicator
        seg.disability_start_date = disability_start_date
        seg.disability_end_date = disability_end_date
        seg.disability_return_to_work_date = disability_return_to_work_date
        seg.disability_unable_to_work_date = disability_unable_to_work_date

        assert seg.set_id_db1 == set_id_db1
        assert seg.disability_indicator == disability_indicator
        assert seg.disability_start_date == disability_start_date
        assert seg.disability_end_date == disability_end_date
        assert seg.disability_return_to_work_date == disability_return_to_work_date
        assert seg.disability_unable_to_work_date == disability_unable_to_work_date

    def test_db1_to_dict(self):
        seg = DB1()

        seg.set_id_db1 = set_id_db1
        seg.disability_indicator = disability_indicator
        seg.disability_start_date = disability_start_date
        seg.disability_end_date = disability_end_date
        seg.disability_return_to_work_date = disability_return_to_work_date
        seg.disability_unable_to_work_date = disability_unable_to_work_date

        result = seg.to_dict()

        assert result["_segment_id"] == "DB1"
        assert result["set_id_db1"] == set_id_db1
        assert result["disability_indicator"] == disability_indicator
        assert result["disability_start_date"] == disability_start_date
        assert result["disability_end_date"] == disability_end_date
        assert result["disability_return_to_work_date"] == disability_return_to_work_date
        assert result["disability_unable_to_work_date"] == disability_unable_to_work_date

    def test_db1_to_json(self):
        seg = DB1()

        seg.set_id_db1 = set_id_db1
        seg.disability_indicator = disability_indicator
        seg.disability_start_date = disability_start_date
        seg.disability_end_date = disability_end_date
        seg.disability_return_to_work_date = disability_return_to_work_date
        seg.disability_unable_to_work_date = disability_unable_to_work_date

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "DB1"
        assert result["set_id_db1"] == set_id_db1
        assert result["disability_indicator"] == disability_indicator
        assert result["disability_start_date"] == disability_start_date
        assert result["disability_end_date"] == disability_end_date
        assert result["disability_return_to_work_date"] == disability_return_to_work_date
        assert result["disability_unable_to_work_date"] == disability_unable_to_work_date
