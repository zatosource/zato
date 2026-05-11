from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OBR


set_id_obr = "test_set_id_obr"
observation_date_time = "test_observation_date_tim"
observation_end_date_time = "test_observation_end_date"
specimen_action_code = "test_specimen_action_code"
placer_field_1 = "test_placer_field_1"
placer_field_2 = "test_placer_field_2"
filler_field_1 = "test_filler_field_1"
filler_field_2 = "test_filler_field_2"
results_rpt_status_chng_date_time = "test_results_rpt_status_c"
diagnostic_serv_sect_id = "test_diagnostic_serv_sect"
result_status = "test_result_status"
transportation_mode = "test_transportation_mode"
scheduled_date_time = "test_scheduled_date_time"
number_of_sample_containers = "test_number_of_sample_con"
transport_arranged = "test_transport_arranged"
escort_required = "test_escort_required"
action_code = "test_action_code"


class TestOBR:
    """Comprehensive tests for OBR segment."""

    def test_obr_build_and_verify(self):
        seg = OBR()

        seg.set_id_obr = set_id_obr
        seg.observation_date_time = observation_date_time
        seg.observation_end_date_time = observation_end_date_time
        seg.specimen_action_code = specimen_action_code
        seg.placer_field_1 = placer_field_1
        seg.placer_field_2 = placer_field_2
        seg.filler_field_1 = filler_field_1
        seg.filler_field_2 = filler_field_2
        seg.results_rpt_status_chng_date_time = results_rpt_status_chng_date_time
        seg.diagnostic_serv_sect_id = diagnostic_serv_sect_id
        seg.result_status = result_status
        seg.transportation_mode = transportation_mode
        seg.scheduled_date_time = scheduled_date_time
        seg.number_of_sample_containers = number_of_sample_containers
        seg.transport_arranged = transport_arranged
        seg.escort_required = escort_required
        seg.action_code = action_code

        assert seg.set_id_obr == set_id_obr
        assert seg.observation_date_time == observation_date_time
        assert seg.observation_end_date_time == observation_end_date_time
        assert seg.specimen_action_code == specimen_action_code
        assert seg.placer_field_1 == placer_field_1
        assert seg.placer_field_2 == placer_field_2
        assert seg.filler_field_1 == filler_field_1
        assert seg.filler_field_2 == filler_field_2
        assert seg.results_rpt_status_chng_date_time == results_rpt_status_chng_date_time
        assert seg.diagnostic_serv_sect_id == diagnostic_serv_sect_id
        assert seg.result_status == result_status
        assert seg.transportation_mode == transportation_mode
        assert seg.scheduled_date_time == scheduled_date_time
        assert seg.number_of_sample_containers == number_of_sample_containers
        assert seg.transport_arranged == transport_arranged
        assert seg.escort_required == escort_required
        assert seg.action_code == action_code

    def test_obr_to_dict(self):
        seg = OBR()

        seg.set_id_obr = set_id_obr
        seg.observation_date_time = observation_date_time
        seg.observation_end_date_time = observation_end_date_time
        seg.specimen_action_code = specimen_action_code
        seg.placer_field_1 = placer_field_1
        seg.placer_field_2 = placer_field_2
        seg.filler_field_1 = filler_field_1
        seg.filler_field_2 = filler_field_2
        seg.results_rpt_status_chng_date_time = results_rpt_status_chng_date_time
        seg.diagnostic_serv_sect_id = diagnostic_serv_sect_id
        seg.result_status = result_status
        seg.transportation_mode = transportation_mode
        seg.scheduled_date_time = scheduled_date_time
        seg.number_of_sample_containers = number_of_sample_containers
        seg.transport_arranged = transport_arranged
        seg.escort_required = escort_required
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "OBR"
        assert result["set_id_obr"] == set_id_obr
        assert result["observation_date_time"] == observation_date_time
        assert result["observation_end_date_time"] == observation_end_date_time
        assert result["specimen_action_code"] == specimen_action_code
        assert result["placer_field_1"] == placer_field_1
        assert result["placer_field_2"] == placer_field_2
        assert result["filler_field_1"] == filler_field_1
        assert result["filler_field_2"] == filler_field_2
        assert result["results_rpt_status_chng_date_time"] == results_rpt_status_chng_date_time
        assert result["diagnostic_serv_sect_id"] == diagnostic_serv_sect_id
        assert result["result_status"] == result_status
        assert result["transportation_mode"] == transportation_mode
        assert result["scheduled_date_time"] == scheduled_date_time
        assert result["number_of_sample_containers"] == number_of_sample_containers
        assert result["transport_arranged"] == transport_arranged
        assert result["escort_required"] == escort_required
        assert result["action_code"] == action_code

    def test_obr_to_json(self):
        seg = OBR()

        seg.set_id_obr = set_id_obr
        seg.observation_date_time = observation_date_time
        seg.observation_end_date_time = observation_end_date_time
        seg.specimen_action_code = specimen_action_code
        seg.placer_field_1 = placer_field_1
        seg.placer_field_2 = placer_field_2
        seg.filler_field_1 = filler_field_1
        seg.filler_field_2 = filler_field_2
        seg.results_rpt_status_chng_date_time = results_rpt_status_chng_date_time
        seg.diagnostic_serv_sect_id = diagnostic_serv_sect_id
        seg.result_status = result_status
        seg.transportation_mode = transportation_mode
        seg.scheduled_date_time = scheduled_date_time
        seg.number_of_sample_containers = number_of_sample_containers
        seg.transport_arranged = transport_arranged
        seg.escort_required = escort_required
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OBR"
        assert result["set_id_obr"] == set_id_obr
        assert result["observation_date_time"] == observation_date_time
        assert result["observation_end_date_time"] == observation_end_date_time
        assert result["specimen_action_code"] == specimen_action_code
        assert result["placer_field_1"] == placer_field_1
        assert result["placer_field_2"] == placer_field_2
        assert result["filler_field_1"] == filler_field_1
        assert result["filler_field_2"] == filler_field_2
        assert result["results_rpt_status_chng_date_time"] == results_rpt_status_chng_date_time
        assert result["diagnostic_serv_sect_id"] == diagnostic_serv_sect_id
        assert result["result_status"] == result_status
        assert result["transportation_mode"] == transportation_mode
        assert result["scheduled_date_time"] == scheduled_date_time
        assert result["number_of_sample_containers"] == number_of_sample_containers
        assert result["transport_arranged"] == transport_arranged
        assert result["escort_required"] == escort_required
        assert result["action_code"] == action_code
