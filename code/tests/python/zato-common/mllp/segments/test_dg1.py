from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import DG1


set_id_dg1 = "test_set_id_dg1"
diagnosis_date_time = "test_diagnosis_date_time"
diagnosis_priority = "test_diagnosis_priority"
confidential_indicator = "test_confidential_indicat"
attestation_date_time = "test_attestation_date_tim"
diagnosis_action_code = "test_diagnosis_action_cod"
drg_grouping_usage = "test_drg_grouping_usage"


class TestDG1:
    """Comprehensive tests for DG1 segment."""

    def test_dg1_build_and_verify(self):
        seg = DG1()

        seg.set_id_dg1 = set_id_dg1
        seg.diagnosis_date_time = diagnosis_date_time
        seg.diagnosis_priority = diagnosis_priority
        seg.confidential_indicator = confidential_indicator
        seg.attestation_date_time = attestation_date_time
        seg.diagnosis_action_code = diagnosis_action_code
        seg.drg_grouping_usage = drg_grouping_usage

        assert seg.set_id_dg1 == set_id_dg1
        assert seg.diagnosis_date_time == diagnosis_date_time
        assert seg.diagnosis_priority == diagnosis_priority
        assert seg.confidential_indicator == confidential_indicator
        assert seg.attestation_date_time == attestation_date_time
        assert seg.diagnosis_action_code == diagnosis_action_code
        assert seg.drg_grouping_usage == drg_grouping_usage

    def test_dg1_to_dict(self):
        seg = DG1()

        seg.set_id_dg1 = set_id_dg1
        seg.diagnosis_date_time = diagnosis_date_time
        seg.diagnosis_priority = diagnosis_priority
        seg.confidential_indicator = confidential_indicator
        seg.attestation_date_time = attestation_date_time
        seg.diagnosis_action_code = diagnosis_action_code
        seg.drg_grouping_usage = drg_grouping_usage

        result = seg.to_dict()

        assert result["_segment_id"] == "DG1"
        assert result["set_id_dg1"] == set_id_dg1
        assert result["diagnosis_date_time"] == diagnosis_date_time
        assert result["diagnosis_priority"] == diagnosis_priority
        assert result["confidential_indicator"] == confidential_indicator
        assert result["attestation_date_time"] == attestation_date_time
        assert result["diagnosis_action_code"] == diagnosis_action_code
        assert result["drg_grouping_usage"] == drg_grouping_usage

    def test_dg1_to_json(self):
        seg = DG1()

        seg.set_id_dg1 = set_id_dg1
        seg.diagnosis_date_time = diagnosis_date_time
        seg.diagnosis_priority = diagnosis_priority
        seg.confidential_indicator = confidential_indicator
        seg.attestation_date_time = attestation_date_time
        seg.diagnosis_action_code = diagnosis_action_code
        seg.drg_grouping_usage = drg_grouping_usage

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "DG1"
        assert result["set_id_dg1"] == set_id_dg1
        assert result["diagnosis_date_time"] == diagnosis_date_time
        assert result["diagnosis_priority"] == diagnosis_priority
        assert result["confidential_indicator"] == confidential_indicator
        assert result["attestation_date_time"] == attestation_date_time
        assert result["diagnosis_action_code"] == diagnosis_action_code
        assert result["drg_grouping_usage"] == drg_grouping_usage
