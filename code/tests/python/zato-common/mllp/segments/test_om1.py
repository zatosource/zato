from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import OM1


sequence_number_test_observation_master_file = "test_sequence_number_test"
specimen_required = "test_specimen_required"
observation_description = "test_observation_descript"
preferred_report_name_for_the_observation = "test_preferred_report_nam"
preferred_short_name_or_mnemonic_for_the_observation = "test_preferred_short_name"
preferred_long_name_for_the_observation = "test_preferred_long_name_"
orderability = "test_orderability"
portable_device_indicator = "test_portable_device_indi"
report_display_order = "test_report_display_order"
date_time_stamp_for_any_change_in_definition_for_the_observation = "test_date_time_stamp_for_"
effective_date_time_of_change = "test_effective_date_time_"
typical_turn_around_time = "test_typical_turn_around_"
processing_time = "test_processing_time"
reporting_priority = "test_reporting_priority"
interpretation_of_observations = "test_interpretation_of_ob"
factors_that_may_affect_the_observation = "test_factors_that_may_aff"
description_of_test_methods = "test_description_of_test_"
challenge_information = "test_challenge_informatio"
exclusive_test = "test_exclusive_test"
diagnostic_serv_sect_id = "test_diagnostic_serv_sect"
special_instructions = "test_special_instructions"


class TestOM1:
    """Comprehensive tests for OM1 segment."""

    def test_om1_build_and_verify(self):
        seg = OM1()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.specimen_required = specimen_required
        seg.observation_description = observation_description
        seg.preferred_report_name_for_the_observation = preferred_report_name_for_the_observation
        seg.preferred_short_name_or_mnemonic_for_the_observation = preferred_short_name_or_mnemonic_for_the_observation
        seg.preferred_long_name_for_the_observation = preferred_long_name_for_the_observation
        seg.orderability = orderability
        seg.portable_device_indicator = portable_device_indicator
        seg.report_display_order = report_display_order
        seg.date_time_stamp_for_any_change_in_definition_for_the_observation = date_time_stamp_for_any_change_in_definition_for_the_observation
        seg.effective_date_time_of_change = effective_date_time_of_change
        seg.typical_turn_around_time = typical_turn_around_time
        seg.processing_time = processing_time
        seg.reporting_priority = reporting_priority
        seg.interpretation_of_observations = interpretation_of_observations
        seg.factors_that_may_affect_the_observation = factors_that_may_affect_the_observation
        seg.description_of_test_methods = description_of_test_methods
        seg.challenge_information = challenge_information
        seg.exclusive_test = exclusive_test
        seg.diagnostic_serv_sect_id = diagnostic_serv_sect_id
        seg.special_instructions = special_instructions

        assert seg.sequence_number_test_observation_master_file == sequence_number_test_observation_master_file
        assert seg.specimen_required == specimen_required
        assert seg.observation_description == observation_description
        assert seg.preferred_report_name_for_the_observation == preferred_report_name_for_the_observation
        assert seg.preferred_short_name_or_mnemonic_for_the_observation == preferred_short_name_or_mnemonic_for_the_observation
        assert seg.preferred_long_name_for_the_observation == preferred_long_name_for_the_observation
        assert seg.orderability == orderability
        assert seg.portable_device_indicator == portable_device_indicator
        assert seg.report_display_order == report_display_order
        assert seg.date_time_stamp_for_any_change_in_definition_for_the_observation == date_time_stamp_for_any_change_in_definition_for_the_observation
        assert seg.effective_date_time_of_change == effective_date_time_of_change
        assert seg.typical_turn_around_time == typical_turn_around_time
        assert seg.processing_time == processing_time
        assert seg.reporting_priority == reporting_priority
        assert seg.interpretation_of_observations == interpretation_of_observations
        assert seg.factors_that_may_affect_the_observation == factors_that_may_affect_the_observation
        assert seg.description_of_test_methods == description_of_test_methods
        assert seg.challenge_information == challenge_information
        assert seg.exclusive_test == exclusive_test
        assert seg.diagnostic_serv_sect_id == diagnostic_serv_sect_id
        assert seg.special_instructions == special_instructions

    def test_om1_to_dict(self):
        seg = OM1()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.specimen_required = specimen_required
        seg.observation_description = observation_description
        seg.preferred_report_name_for_the_observation = preferred_report_name_for_the_observation
        seg.preferred_short_name_or_mnemonic_for_the_observation = preferred_short_name_or_mnemonic_for_the_observation
        seg.preferred_long_name_for_the_observation = preferred_long_name_for_the_observation
        seg.orderability = orderability
        seg.portable_device_indicator = portable_device_indicator
        seg.report_display_order = report_display_order
        seg.date_time_stamp_for_any_change_in_definition_for_the_observation = date_time_stamp_for_any_change_in_definition_for_the_observation
        seg.effective_date_time_of_change = effective_date_time_of_change
        seg.typical_turn_around_time = typical_turn_around_time
        seg.processing_time = processing_time
        seg.reporting_priority = reporting_priority
        seg.interpretation_of_observations = interpretation_of_observations
        seg.factors_that_may_affect_the_observation = factors_that_may_affect_the_observation
        seg.description_of_test_methods = description_of_test_methods
        seg.challenge_information = challenge_information
        seg.exclusive_test = exclusive_test
        seg.diagnostic_serv_sect_id = diagnostic_serv_sect_id
        seg.special_instructions = special_instructions

        result = seg.to_dict()

        assert result["_segment_id"] == "OM1"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["specimen_required"] == specimen_required
        assert result["observation_description"] == observation_description
        assert result["preferred_report_name_for_the_observation"] == preferred_report_name_for_the_observation
        assert result["preferred_short_name_or_mnemonic_for_the_observation"] == preferred_short_name_or_mnemonic_for_the_observation
        assert result["preferred_long_name_for_the_observation"] == preferred_long_name_for_the_observation
        assert result["orderability"] == orderability
        assert result["portable_device_indicator"] == portable_device_indicator
        assert result["report_display_order"] == report_display_order
        assert result["date_time_stamp_for_any_change_in_definition_for_the_observation"] == date_time_stamp_for_any_change_in_definition_for_the_observation
        assert result["effective_date_time_of_change"] == effective_date_time_of_change
        assert result["typical_turn_around_time"] == typical_turn_around_time
        assert result["processing_time"] == processing_time
        assert result["reporting_priority"] == reporting_priority
        assert result["interpretation_of_observations"] == interpretation_of_observations
        assert result["factors_that_may_affect_the_observation"] == factors_that_may_affect_the_observation
        assert result["description_of_test_methods"] == description_of_test_methods
        assert result["challenge_information"] == challenge_information
        assert result["exclusive_test"] == exclusive_test
        assert result["diagnostic_serv_sect_id"] == diagnostic_serv_sect_id
        assert result["special_instructions"] == special_instructions

    def test_om1_to_json(self):
        seg = OM1()

        seg.sequence_number_test_observation_master_file = sequence_number_test_observation_master_file
        seg.specimen_required = specimen_required
        seg.observation_description = observation_description
        seg.preferred_report_name_for_the_observation = preferred_report_name_for_the_observation
        seg.preferred_short_name_or_mnemonic_for_the_observation = preferred_short_name_or_mnemonic_for_the_observation
        seg.preferred_long_name_for_the_observation = preferred_long_name_for_the_observation
        seg.orderability = orderability
        seg.portable_device_indicator = portable_device_indicator
        seg.report_display_order = report_display_order
        seg.date_time_stamp_for_any_change_in_definition_for_the_observation = date_time_stamp_for_any_change_in_definition_for_the_observation
        seg.effective_date_time_of_change = effective_date_time_of_change
        seg.typical_turn_around_time = typical_turn_around_time
        seg.processing_time = processing_time
        seg.reporting_priority = reporting_priority
        seg.interpretation_of_observations = interpretation_of_observations
        seg.factors_that_may_affect_the_observation = factors_that_may_affect_the_observation
        seg.description_of_test_methods = description_of_test_methods
        seg.challenge_information = challenge_information
        seg.exclusive_test = exclusive_test
        seg.diagnostic_serv_sect_id = diagnostic_serv_sect_id
        seg.special_instructions = special_instructions

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "OM1"
        assert result["sequence_number_test_observation_master_file"] == sequence_number_test_observation_master_file
        assert result["specimen_required"] == specimen_required
        assert result["observation_description"] == observation_description
        assert result["preferred_report_name_for_the_observation"] == preferred_report_name_for_the_observation
        assert result["preferred_short_name_or_mnemonic_for_the_observation"] == preferred_short_name_or_mnemonic_for_the_observation
        assert result["preferred_long_name_for_the_observation"] == preferred_long_name_for_the_observation
        assert result["orderability"] == orderability
        assert result["portable_device_indicator"] == portable_device_indicator
        assert result["report_display_order"] == report_display_order
        assert result["date_time_stamp_for_any_change_in_definition_for_the_observation"] == date_time_stamp_for_any_change_in_definition_for_the_observation
        assert result["effective_date_time_of_change"] == effective_date_time_of_change
        assert result["typical_turn_around_time"] == typical_turn_around_time
        assert result["processing_time"] == processing_time
        assert result["reporting_priority"] == reporting_priority
        assert result["interpretation_of_observations"] == interpretation_of_observations
        assert result["factors_that_may_affect_the_observation"] == factors_that_may_affect_the_observation
        assert result["description_of_test_methods"] == description_of_test_methods
        assert result["challenge_information"] == challenge_information
        assert result["exclusive_test"] == exclusive_test
        assert result["diagnostic_serv_sect_id"] == diagnostic_serv_sect_id
        assert result["special_instructions"] == special_instructions
