from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ACC


accident_date_time = "test_accident_date_time"
accident_location = "test_accident_location"
accident_job_related_indicator = "test_accident_job_related"
accident_death_indicator = "test_accident_death_indic"
accident_description = "test_accident_description"
brought_in_by = "test_brought_in_by"
police_notified_indicator = "test_police_notified_indi"
degree_of_patient_liability = "test_degree_of_patient_li"


class TestACC:
    """Comprehensive tests for ACC segment."""

    def test_acc_build_and_verify(self):
        seg = ACC()

        seg.accident_date_time = accident_date_time
        seg.accident_location = accident_location
        seg.accident_job_related_indicator = accident_job_related_indicator
        seg.accident_death_indicator = accident_death_indicator
        seg.accident_description = accident_description
        seg.brought_in_by = brought_in_by
        seg.police_notified_indicator = police_notified_indicator
        seg.degree_of_patient_liability = degree_of_patient_liability

        assert seg.accident_date_time == accident_date_time
        assert seg.accident_location == accident_location
        assert seg.accident_job_related_indicator == accident_job_related_indicator
        assert seg.accident_death_indicator == accident_death_indicator
        assert seg.accident_description == accident_description
        assert seg.brought_in_by == brought_in_by
        assert seg.police_notified_indicator == police_notified_indicator
        assert seg.degree_of_patient_liability == degree_of_patient_liability

    def test_acc_to_dict(self):
        seg = ACC()

        seg.accident_date_time = accident_date_time
        seg.accident_location = accident_location
        seg.accident_job_related_indicator = accident_job_related_indicator
        seg.accident_death_indicator = accident_death_indicator
        seg.accident_description = accident_description
        seg.brought_in_by = brought_in_by
        seg.police_notified_indicator = police_notified_indicator
        seg.degree_of_patient_liability = degree_of_patient_liability

        result = seg.to_dict()

        assert result["_segment_id"] == "ACC"
        assert result["accident_date_time"] == accident_date_time
        assert result["accident_location"] == accident_location
        assert result["accident_job_related_indicator"] == accident_job_related_indicator
        assert result["accident_death_indicator"] == accident_death_indicator
        assert result["accident_description"] == accident_description
        assert result["brought_in_by"] == brought_in_by
        assert result["police_notified_indicator"] == police_notified_indicator
        assert result["degree_of_patient_liability"] == degree_of_patient_liability

    def test_acc_to_json(self):
        seg = ACC()

        seg.accident_date_time = accident_date_time
        seg.accident_location = accident_location
        seg.accident_job_related_indicator = accident_job_related_indicator
        seg.accident_death_indicator = accident_death_indicator
        seg.accident_description = accident_description
        seg.brought_in_by = brought_in_by
        seg.police_notified_indicator = police_notified_indicator
        seg.degree_of_patient_liability = degree_of_patient_liability

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ACC"
        assert result["accident_date_time"] == accident_date_time
        assert result["accident_location"] == accident_location
        assert result["accident_job_related_indicator"] == accident_job_related_indicator
        assert result["accident_death_indicator"] == accident_death_indicator
        assert result["accident_description"] == accident_description
        assert result["brought_in_by"] == brought_in_by
        assert result["police_notified_indicator"] == police_notified_indicator
        assert result["degree_of_patient_liability"] == degree_of_patient_liability
