from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import SPM


set_id_spm = "test_set_id_spm"
grouped_specimen_count = "test_grouped_specimen_cou"
specimen_received_date_time = "test_specimen_received_da"
specimen_expiration_date_time = "test_specimen_expiration_"
specimen_availability = "test_specimen_availabilit"
number_of_specimen_containers = "test_number_of_specimen_c"
culture_start_date_time = "test_culture_start_date_t"
culture_final_date_time = "test_culture_final_date_t"
action_code = "test_action_code"


class TestSPM:
    """Comprehensive tests for SPM segment."""

    def test_spm_build_and_verify(self):
        seg = SPM()

        seg.set_id_spm = set_id_spm
        seg.grouped_specimen_count = grouped_specimen_count
        seg.specimen_received_date_time = specimen_received_date_time
        seg.specimen_expiration_date_time = specimen_expiration_date_time
        seg.specimen_availability = specimen_availability
        seg.number_of_specimen_containers = number_of_specimen_containers
        seg.culture_start_date_time = culture_start_date_time
        seg.culture_final_date_time = culture_final_date_time
        seg.action_code = action_code

        assert seg.set_id_spm == set_id_spm
        assert seg.grouped_specimen_count == grouped_specimen_count
        assert seg.specimen_received_date_time == specimen_received_date_time
        assert seg.specimen_expiration_date_time == specimen_expiration_date_time
        assert seg.specimen_availability == specimen_availability
        assert seg.number_of_specimen_containers == number_of_specimen_containers
        assert seg.culture_start_date_time == culture_start_date_time
        assert seg.culture_final_date_time == culture_final_date_time
        assert seg.action_code == action_code

    def test_spm_to_dict(self):
        seg = SPM()

        seg.set_id_spm = set_id_spm
        seg.grouped_specimen_count = grouped_specimen_count
        seg.specimen_received_date_time = specimen_received_date_time
        seg.specimen_expiration_date_time = specimen_expiration_date_time
        seg.specimen_availability = specimen_availability
        seg.number_of_specimen_containers = number_of_specimen_containers
        seg.culture_start_date_time = culture_start_date_time
        seg.culture_final_date_time = culture_final_date_time
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "SPM"
        assert result["set_id_spm"] == set_id_spm
        assert result["grouped_specimen_count"] == grouped_specimen_count
        assert result["specimen_received_date_time"] == specimen_received_date_time
        assert result["specimen_expiration_date_time"] == specimen_expiration_date_time
        assert result["specimen_availability"] == specimen_availability
        assert result["number_of_specimen_containers"] == number_of_specimen_containers
        assert result["culture_start_date_time"] == culture_start_date_time
        assert result["culture_final_date_time"] == culture_final_date_time
        assert result["action_code"] == action_code

    def test_spm_to_json(self):
        seg = SPM()

        seg.set_id_spm = set_id_spm
        seg.grouped_specimen_count = grouped_specimen_count
        seg.specimen_received_date_time = specimen_received_date_time
        seg.specimen_expiration_date_time = specimen_expiration_date_time
        seg.specimen_availability = specimen_availability
        seg.number_of_specimen_containers = number_of_specimen_containers
        seg.culture_start_date_time = culture_start_date_time
        seg.culture_final_date_time = culture_final_date_time
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "SPM"
        assert result["set_id_spm"] == set_id_spm
        assert result["grouped_specimen_count"] == grouped_specimen_count
        assert result["specimen_received_date_time"] == specimen_received_date_time
        assert result["specimen_expiration_date_time"] == specimen_expiration_date_time
        assert result["specimen_availability"] == specimen_availability
        assert result["number_of_specimen_containers"] == number_of_specimen_containers
        assert result["culture_start_date_time"] == culture_start_date_time
        assert result["culture_final_date_time"] == culture_final_date_time
        assert result["action_code"] == action_code
