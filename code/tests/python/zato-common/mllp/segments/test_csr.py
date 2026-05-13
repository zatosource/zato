from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import CSR


date_time_of_patient_study_registration = "test_date_time_of_patient"
date_time_patient_study_consent_signed = "test_date_time_patient_st"
study_randomization_datetime = "test_study_randomization_"
date_time_ended_study = "test_date_time_ended_stud"
action_code = "test_action_code"


class TestCSR:
    """Comprehensive tests for CSR segment."""

    def test_csr_build_and_verify(self):
        seg = CSR()

        seg.date_time_of_patient_study_registration = date_time_of_patient_study_registration
        seg.date_time_patient_study_consent_signed = date_time_patient_study_consent_signed
        seg.study_randomization_datetime = study_randomization_datetime
        seg.date_time_ended_study = date_time_ended_study
        seg.action_code = action_code

        assert seg.date_time_of_patient_study_registration == date_time_of_patient_study_registration
        assert seg.date_time_patient_study_consent_signed == date_time_patient_study_consent_signed
        assert seg.study_randomization_datetime == study_randomization_datetime
        assert seg.date_time_ended_study == date_time_ended_study
        assert seg.action_code == action_code

    def test_csr_to_dict(self):
        seg = CSR()

        seg.date_time_of_patient_study_registration = date_time_of_patient_study_registration
        seg.date_time_patient_study_consent_signed = date_time_patient_study_consent_signed
        seg.study_randomization_datetime = study_randomization_datetime
        seg.date_time_ended_study = date_time_ended_study
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "CSR"
        assert result["date_time_of_patient_study_registration"] == date_time_of_patient_study_registration
        assert result["date_time_patient_study_consent_signed"] == date_time_patient_study_consent_signed
        assert result["study_randomization_datetime"] == study_randomization_datetime
        assert result["date_time_ended_study"] == date_time_ended_study
        assert result["action_code"] == action_code

    def test_csr_to_json(self):
        seg = CSR()

        seg.date_time_of_patient_study_registration = date_time_of_patient_study_registration
        seg.date_time_patient_study_consent_signed = date_time_patient_study_consent_signed
        seg.study_randomization_datetime = study_randomization_datetime
        seg.date_time_ended_study = date_time_ended_study
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CSR"
        assert result["date_time_of_patient_study_registration"] == date_time_of_patient_study_registration
        assert result["date_time_patient_study_consent_signed"] == date_time_patient_study_consent_signed
        assert result["study_randomization_datetime"] == study_randomization_datetime
        assert result["date_time_ended_study"] == date_time_ended_study
        assert result["action_code"] == action_code
