from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PEO


event_onset_date_time = "test_event_onset_date_tim"
event_exacerbation_date_time = "test_event_exacerbation_d"
event_improved_date_time = "test_event_improved_date_"
event_ended_data_time = "test_event_ended_data_tim"
event_serious = "test_event_serious"
event_expected = "test_event_expected"
patient_outcome = "test_patient_outcome"
primary_observers_qualification = "test_primary_observers_qu"
confirmation_provided_by = "test_confirmation_provide"
primary_observer_aware_date_time = "test_primary_observer_awa"
primary_observers_identity_may_be_divulged = "test_primary_observers_id"


class TestPEO:
    """Comprehensive tests for PEO segment."""

    def test_peo_build_and_verify(self):
        seg = PEO()

        seg.event_onset_date_time = event_onset_date_time
        seg.event_exacerbation_date_time = event_exacerbation_date_time
        seg.event_improved_date_time = event_improved_date_time
        seg.event_ended_data_time = event_ended_data_time
        seg.event_serious = event_serious
        seg.event_expected = event_expected
        seg.patient_outcome = patient_outcome
        seg.primary_observers_qualification = primary_observers_qualification
        seg.confirmation_provided_by = confirmation_provided_by
        seg.primary_observer_aware_date_time = primary_observer_aware_date_time
        seg.primary_observers_identity_may_be_divulged = primary_observers_identity_may_be_divulged

        assert seg.event_onset_date_time == event_onset_date_time
        assert seg.event_exacerbation_date_time == event_exacerbation_date_time
        assert seg.event_improved_date_time == event_improved_date_time
        assert seg.event_ended_data_time == event_ended_data_time
        assert seg.event_serious == event_serious
        assert seg.event_expected == event_expected
        assert seg.patient_outcome == patient_outcome
        assert seg.primary_observers_qualification == primary_observers_qualification
        assert seg.confirmation_provided_by == confirmation_provided_by
        assert seg.primary_observer_aware_date_time == primary_observer_aware_date_time
        assert seg.primary_observers_identity_may_be_divulged == primary_observers_identity_may_be_divulged

    def test_peo_to_dict(self):
        seg = PEO()

        seg.event_onset_date_time = event_onset_date_time
        seg.event_exacerbation_date_time = event_exacerbation_date_time
        seg.event_improved_date_time = event_improved_date_time
        seg.event_ended_data_time = event_ended_data_time
        seg.event_serious = event_serious
        seg.event_expected = event_expected
        seg.patient_outcome = patient_outcome
        seg.primary_observers_qualification = primary_observers_qualification
        seg.confirmation_provided_by = confirmation_provided_by
        seg.primary_observer_aware_date_time = primary_observer_aware_date_time
        seg.primary_observers_identity_may_be_divulged = primary_observers_identity_may_be_divulged

        result = seg.to_dict()

        assert result["_segment_id"] == "PEO"
        assert result["event_onset_date_time"] == event_onset_date_time
        assert result["event_exacerbation_date_time"] == event_exacerbation_date_time
        assert result["event_improved_date_time"] == event_improved_date_time
        assert result["event_ended_data_time"] == event_ended_data_time
        assert result["event_serious"] == event_serious
        assert result["event_expected"] == event_expected
        assert result["patient_outcome"] == patient_outcome
        assert result["primary_observers_qualification"] == primary_observers_qualification
        assert result["confirmation_provided_by"] == confirmation_provided_by
        assert result["primary_observer_aware_date_time"] == primary_observer_aware_date_time
        assert result["primary_observers_identity_may_be_divulged"] == primary_observers_identity_may_be_divulged

    def test_peo_to_json(self):
        seg = PEO()

        seg.event_onset_date_time = event_onset_date_time
        seg.event_exacerbation_date_time = event_exacerbation_date_time
        seg.event_improved_date_time = event_improved_date_time
        seg.event_ended_data_time = event_ended_data_time
        seg.event_serious = event_serious
        seg.event_expected = event_expected
        seg.patient_outcome = patient_outcome
        seg.primary_observers_qualification = primary_observers_qualification
        seg.confirmation_provided_by = confirmation_provided_by
        seg.primary_observer_aware_date_time = primary_observer_aware_date_time
        seg.primary_observers_identity_may_be_divulged = primary_observers_identity_may_be_divulged

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PEO"
        assert result["event_onset_date_time"] == event_onset_date_time
        assert result["event_exacerbation_date_time"] == event_exacerbation_date_time
        assert result["event_improved_date_time"] == event_improved_date_time
        assert result["event_ended_data_time"] == event_ended_data_time
        assert result["event_serious"] == event_serious
        assert result["event_expected"] == event_expected
        assert result["patient_outcome"] == patient_outcome
        assert result["primary_observers_qualification"] == primary_observers_qualification
        assert result["confirmation_provided_by"] == confirmation_provided_by
        assert result["primary_observer_aware_date_time"] == primary_observer_aware_date_time
        assert result["primary_observers_identity_may_be_divulged"] == primary_observers_identity_may_be_divulged
