from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import DON


phlebotomy_start_date_time = "test_phlebotomy_start_dat"
phlebotomy_end_date_time = "test_phlebotomy_end_date_"
donation_duration = "test_donation_duration"
donor_eligibility_flag = "test_donor_eligibility_fl"
donor_eligibility_date = "test_donor_eligibility_da"
intended_recipient_blood_relative = "test_intended_recipient_b"
intended_recipient_dob = "test_intended_recipient_d"
intended_recipient_procedure_date = "test_intended_recipient_p"
aphaeresis_type_machine = "test_aphaeresis_type_mach"
aphaeresis_machine_serial_number = "test_aphaeresis_machine_s"
donor_reaction = "test_donor_reaction"
final_review_date_time = "test_final_review_date_ti"
number_of_tubes_collected = "test_number_of_tubes_coll"
action_code = "test_action_code"


class TestDON:
    """Comprehensive tests for DON segment."""

    def test_don_build_and_verify(self):
        seg = DON()

        seg.phlebotomy_start_date_time = phlebotomy_start_date_time
        seg.phlebotomy_end_date_time = phlebotomy_end_date_time
        seg.donation_duration = donation_duration
        seg.donor_eligibility_flag = donor_eligibility_flag
        seg.donor_eligibility_date = donor_eligibility_date
        seg.intended_recipient_blood_relative = intended_recipient_blood_relative
        seg.intended_recipient_dob = intended_recipient_dob
        seg.intended_recipient_procedure_date = intended_recipient_procedure_date
        seg.aphaeresis_type_machine = aphaeresis_type_machine
        seg.aphaeresis_machine_serial_number = aphaeresis_machine_serial_number
        seg.donor_reaction = donor_reaction
        seg.final_review_date_time = final_review_date_time
        seg.number_of_tubes_collected = number_of_tubes_collected
        seg.action_code = action_code

        assert seg.phlebotomy_start_date_time == phlebotomy_start_date_time
        assert seg.phlebotomy_end_date_time == phlebotomy_end_date_time
        assert seg.donation_duration == donation_duration
        assert seg.donor_eligibility_flag == donor_eligibility_flag
        assert seg.donor_eligibility_date == donor_eligibility_date
        assert seg.intended_recipient_blood_relative == intended_recipient_blood_relative
        assert seg.intended_recipient_dob == intended_recipient_dob
        assert seg.intended_recipient_procedure_date == intended_recipient_procedure_date
        assert seg.aphaeresis_type_machine == aphaeresis_type_machine
        assert seg.aphaeresis_machine_serial_number == aphaeresis_machine_serial_number
        assert seg.donor_reaction == donor_reaction
        assert seg.final_review_date_time == final_review_date_time
        assert seg.number_of_tubes_collected == number_of_tubes_collected
        assert seg.action_code == action_code

    def test_don_to_dict(self):
        seg = DON()

        seg.phlebotomy_start_date_time = phlebotomy_start_date_time
        seg.phlebotomy_end_date_time = phlebotomy_end_date_time
        seg.donation_duration = donation_duration
        seg.donor_eligibility_flag = donor_eligibility_flag
        seg.donor_eligibility_date = donor_eligibility_date
        seg.intended_recipient_blood_relative = intended_recipient_blood_relative
        seg.intended_recipient_dob = intended_recipient_dob
        seg.intended_recipient_procedure_date = intended_recipient_procedure_date
        seg.aphaeresis_type_machine = aphaeresis_type_machine
        seg.aphaeresis_machine_serial_number = aphaeresis_machine_serial_number
        seg.donor_reaction = donor_reaction
        seg.final_review_date_time = final_review_date_time
        seg.number_of_tubes_collected = number_of_tubes_collected
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "DON"
        assert result["phlebotomy_start_date_time"] == phlebotomy_start_date_time
        assert result["phlebotomy_end_date_time"] == phlebotomy_end_date_time
        assert result["donation_duration"] == donation_duration
        assert result["donor_eligibility_flag"] == donor_eligibility_flag
        assert result["donor_eligibility_date"] == donor_eligibility_date
        assert result["intended_recipient_blood_relative"] == intended_recipient_blood_relative
        assert result["intended_recipient_dob"] == intended_recipient_dob
        assert result["intended_recipient_procedure_date"] == intended_recipient_procedure_date
        assert result["aphaeresis_type_machine"] == aphaeresis_type_machine
        assert result["aphaeresis_machine_serial_number"] == aphaeresis_machine_serial_number
        assert result["donor_reaction"] == donor_reaction
        assert result["final_review_date_time"] == final_review_date_time
        assert result["number_of_tubes_collected"] == number_of_tubes_collected
        assert result["action_code"] == action_code

    def test_don_to_json(self):
        seg = DON()

        seg.phlebotomy_start_date_time = phlebotomy_start_date_time
        seg.phlebotomy_end_date_time = phlebotomy_end_date_time
        seg.donation_duration = donation_duration
        seg.donor_eligibility_flag = donor_eligibility_flag
        seg.donor_eligibility_date = donor_eligibility_date
        seg.intended_recipient_blood_relative = intended_recipient_blood_relative
        seg.intended_recipient_dob = intended_recipient_dob
        seg.intended_recipient_procedure_date = intended_recipient_procedure_date
        seg.aphaeresis_type_machine = aphaeresis_type_machine
        seg.aphaeresis_machine_serial_number = aphaeresis_machine_serial_number
        seg.donor_reaction = donor_reaction
        seg.final_review_date_time = final_review_date_time
        seg.number_of_tubes_collected = number_of_tubes_collected
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "DON"
        assert result["phlebotomy_start_date_time"] == phlebotomy_start_date_time
        assert result["phlebotomy_end_date_time"] == phlebotomy_end_date_time
        assert result["donation_duration"] == donation_duration
        assert result["donor_eligibility_flag"] == donor_eligibility_flag
        assert result["donor_eligibility_date"] == donor_eligibility_date
        assert result["intended_recipient_blood_relative"] == intended_recipient_blood_relative
        assert result["intended_recipient_dob"] == intended_recipient_dob
        assert result["intended_recipient_procedure_date"] == intended_recipient_procedure_date
        assert result["aphaeresis_type_machine"] == aphaeresis_type_machine
        assert result["aphaeresis_machine_serial_number"] == aphaeresis_machine_serial_number
        assert result["donor_reaction"] == donor_reaction
        assert result["final_review_date_time"] == final_review_date_time
        assert result["number_of_tubes_collected"] == number_of_tubes_collected
        assert result["action_code"] == action_code
