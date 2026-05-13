from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PID


set_id_pid = "test_set_id_pid"
date_time_of_birth = "test_date_time_of_birth"
birth_place = "test_birth_place"
multiple_birth_indicator = "test_multiple_birth_indic"
birth_order = "test_birth_order"
patient_death_date_and_time = "test_patient_death_date_a"
patient_death_indicator = "test_patient_death_indica"
identity_unknown_indicator = "test_identity_unknown_ind"
last_update_date_time = "test_last_update_date_tim"
strain = "test_strain"


class TestPID:
    """Comprehensive tests for PID segment."""

    def test_pid_build_and_verify(self):
        seg = PID()

        seg.set_id_pid = set_id_pid
        seg.date_time_of_birth = date_time_of_birth
        seg.birth_place = birth_place
        seg.multiple_birth_indicator = multiple_birth_indicator
        seg.birth_order = birth_order
        seg.patient_death_date_and_time = patient_death_date_and_time
        seg.patient_death_indicator = patient_death_indicator
        seg.identity_unknown_indicator = identity_unknown_indicator
        seg.last_update_date_time = last_update_date_time
        seg.strain = strain

        assert seg.set_id_pid == set_id_pid
        assert seg.date_time_of_birth == date_time_of_birth
        assert seg.birth_place == birth_place
        assert seg.multiple_birth_indicator == multiple_birth_indicator
        assert seg.birth_order == birth_order
        assert seg.patient_death_date_and_time == patient_death_date_and_time
        assert seg.patient_death_indicator == patient_death_indicator
        assert seg.identity_unknown_indicator == identity_unknown_indicator
        assert seg.last_update_date_time == last_update_date_time
        assert seg.strain == strain

    def test_pid_to_dict(self):
        seg = PID()

        seg.set_id_pid = set_id_pid
        seg.date_time_of_birth = date_time_of_birth
        seg.birth_place = birth_place
        seg.multiple_birth_indicator = multiple_birth_indicator
        seg.birth_order = birth_order
        seg.patient_death_date_and_time = patient_death_date_and_time
        seg.patient_death_indicator = patient_death_indicator
        seg.identity_unknown_indicator = identity_unknown_indicator
        seg.last_update_date_time = last_update_date_time
        seg.strain = strain

        result = seg.to_dict()

        assert result["_segment_id"] == "PID"
        assert result["set_id_pid"] == set_id_pid
        assert result["date_time_of_birth"] == date_time_of_birth
        assert result["birth_place"] == birth_place
        assert result["multiple_birth_indicator"] == multiple_birth_indicator
        assert result["birth_order"] == birth_order
        assert result["patient_death_date_and_time"] == patient_death_date_and_time
        assert result["patient_death_indicator"] == patient_death_indicator
        assert result["identity_unknown_indicator"] == identity_unknown_indicator
        assert result["last_update_date_time"] == last_update_date_time
        assert result["strain"] == strain

    def test_pid_to_json(self):
        seg = PID()

        seg.set_id_pid = set_id_pid
        seg.date_time_of_birth = date_time_of_birth
        seg.birth_place = birth_place
        seg.multiple_birth_indicator = multiple_birth_indicator
        seg.birth_order = birth_order
        seg.patient_death_date_and_time = patient_death_date_and_time
        seg.patient_death_indicator = patient_death_indicator
        seg.identity_unknown_indicator = identity_unknown_indicator
        seg.last_update_date_time = last_update_date_time
        seg.strain = strain

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PID"
        assert result["set_id_pid"] == set_id_pid
        assert result["date_time_of_birth"] == date_time_of_birth
        assert result["birth_place"] == birth_place
        assert result["multiple_birth_indicator"] == multiple_birth_indicator
        assert result["birth_order"] == birth_order
        assert result["patient_death_date_and_time"] == patient_death_date_and_time
        assert result["patient_death_indicator"] == patient_death_indicator
        assert result["identity_unknown_indicator"] == identity_unknown_indicator
        assert result["last_update_date_time"] == last_update_date_time
        assert result["strain"] == strain
