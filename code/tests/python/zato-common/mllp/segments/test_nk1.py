from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import NK1


set_id_nk1 = "test_set_id_nk1"
start_date = "test_start_date"
end_date = "test_end_date"
next_of_kin_associated_parties_job_title = "test_next_of_kin_associat"
date_time_of_birth = "test_date_time_of_birth"
protection_indicator = "test_protection_indicator"
contact_person_social_security_number = "test_contact_person_socia"
next_of_kin_birth_place = "test_next_of_kin_birth_pl"


class TestNK1:
    """Comprehensive tests for NK1 segment."""

    def test_nk1_build_and_verify(self):
        seg = NK1()

        seg.set_id_nk1 = set_id_nk1
        seg.start_date = start_date
        seg.end_date = end_date
        seg.next_of_kin_associated_parties_job_title = next_of_kin_associated_parties_job_title
        seg.date_time_of_birth = date_time_of_birth
        seg.protection_indicator = protection_indicator
        seg.contact_person_social_security_number = contact_person_social_security_number
        seg.next_of_kin_birth_place = next_of_kin_birth_place

        assert seg.set_id_nk1 == set_id_nk1
        assert seg.start_date == start_date
        assert seg.end_date == end_date
        assert seg.next_of_kin_associated_parties_job_title == next_of_kin_associated_parties_job_title
        assert seg.date_time_of_birth == date_time_of_birth
        assert seg.protection_indicator == protection_indicator
        assert seg.contact_person_social_security_number == contact_person_social_security_number
        assert seg.next_of_kin_birth_place == next_of_kin_birth_place

    def test_nk1_to_dict(self):
        seg = NK1()

        seg.set_id_nk1 = set_id_nk1
        seg.start_date = start_date
        seg.end_date = end_date
        seg.next_of_kin_associated_parties_job_title = next_of_kin_associated_parties_job_title
        seg.date_time_of_birth = date_time_of_birth
        seg.protection_indicator = protection_indicator
        seg.contact_person_social_security_number = contact_person_social_security_number
        seg.next_of_kin_birth_place = next_of_kin_birth_place

        result = seg.to_dict()

        assert result["_segment_id"] == "NK1"
        assert result["set_id_nk1"] == set_id_nk1
        assert result["start_date"] == start_date
        assert result["end_date"] == end_date
        assert result["next_of_kin_associated_parties_job_title"] == next_of_kin_associated_parties_job_title
        assert result["date_time_of_birth"] == date_time_of_birth
        assert result["protection_indicator"] == protection_indicator
        assert result["contact_person_social_security_number"] == contact_person_social_security_number
        assert result["next_of_kin_birth_place"] == next_of_kin_birth_place

    def test_nk1_to_json(self):
        seg = NK1()

        seg.set_id_nk1 = set_id_nk1
        seg.start_date = start_date
        seg.end_date = end_date
        seg.next_of_kin_associated_parties_job_title = next_of_kin_associated_parties_job_title
        seg.date_time_of_birth = date_time_of_birth
        seg.protection_indicator = protection_indicator
        seg.contact_person_social_security_number = contact_person_social_security_number
        seg.next_of_kin_birth_place = next_of_kin_birth_place

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "NK1"
        assert result["set_id_nk1"] == set_id_nk1
        assert result["start_date"] == start_date
        assert result["end_date"] == end_date
        assert result["next_of_kin_associated_parties_job_title"] == next_of_kin_associated_parties_job_title
        assert result["date_time_of_birth"] == date_time_of_birth
        assert result["protection_indicator"] == protection_indicator
        assert result["contact_person_social_security_number"] == contact_person_social_security_number
        assert result["next_of_kin_birth_place"] == next_of_kin_birth_place
