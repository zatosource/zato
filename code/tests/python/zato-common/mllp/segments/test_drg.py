from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import DRG


drg_assigned_date_time = "test_drg_assigned_date_ti"
drg_approval_indicator = "test_drg_approval_indicat"
outlier_days = "test_outlier_days"
confidential_indicator = "test_confidential_indicat"
effective_weight = "test_effective_weight"
grouper_software_name = "test_grouper_software_nam"
grouper_software_version = "test_grouper_software_ver"
calculated_days = "test_calculated_days"


class TestDRG:
    """Comprehensive tests for DRG segment."""

    def test_drg_build_and_verify(self):
        seg = DRG()

        seg.drg_assigned_date_time = drg_assigned_date_time
        seg.drg_approval_indicator = drg_approval_indicator
        seg.outlier_days = outlier_days
        seg.confidential_indicator = confidential_indicator
        seg.effective_weight = effective_weight
        seg.grouper_software_name = grouper_software_name
        seg.grouper_software_version = grouper_software_version
        seg.calculated_days = calculated_days

        assert seg.drg_assigned_date_time == drg_assigned_date_time
        assert seg.drg_approval_indicator == drg_approval_indicator
        assert seg.outlier_days == outlier_days
        assert seg.confidential_indicator == confidential_indicator
        assert seg.effective_weight == effective_weight
        assert seg.grouper_software_name == grouper_software_name
        assert seg.grouper_software_version == grouper_software_version
        assert seg.calculated_days == calculated_days

    def test_drg_to_dict(self):
        seg = DRG()

        seg.drg_assigned_date_time = drg_assigned_date_time
        seg.drg_approval_indicator = drg_approval_indicator
        seg.outlier_days = outlier_days
        seg.confidential_indicator = confidential_indicator
        seg.effective_weight = effective_weight
        seg.grouper_software_name = grouper_software_name
        seg.grouper_software_version = grouper_software_version
        seg.calculated_days = calculated_days

        result = seg.to_dict()

        assert result["_segment_id"] == "DRG"
        assert result["drg_assigned_date_time"] == drg_assigned_date_time
        assert result["drg_approval_indicator"] == drg_approval_indicator
        assert result["outlier_days"] == outlier_days
        assert result["confidential_indicator"] == confidential_indicator
        assert result["effective_weight"] == effective_weight
        assert result["grouper_software_name"] == grouper_software_name
        assert result["grouper_software_version"] == grouper_software_version
        assert result["calculated_days"] == calculated_days

    def test_drg_to_json(self):
        seg = DRG()

        seg.drg_assigned_date_time = drg_assigned_date_time
        seg.drg_approval_indicator = drg_approval_indicator
        seg.outlier_days = outlier_days
        seg.confidential_indicator = confidential_indicator
        seg.effective_weight = effective_weight
        seg.grouper_software_name = grouper_software_name
        seg.grouper_software_version = grouper_software_version
        seg.calculated_days = calculated_days

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "DRG"
        assert result["drg_assigned_date_time"] == drg_assigned_date_time
        assert result["drg_approval_indicator"] == drg_approval_indicator
        assert result["outlier_days"] == outlier_days
        assert result["confidential_indicator"] == confidential_indicator
        assert result["effective_weight"] == effective_weight
        assert result["grouper_software_name"] == grouper_software_name
        assert result["grouper_software_version"] == grouper_software_version
        assert result["calculated_days"] == calculated_days
