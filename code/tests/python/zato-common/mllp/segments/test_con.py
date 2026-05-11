from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import CON


set_id_con = "test_set_id_con"
consent_form_id_and_version = "test_consent_form_id_and_"
consent_discussion_date_time = "test_consent_discussion_d"
consent_decision_date_time = "test_consent_decision_dat"
consent_effective_date_time = "test_consent_effective_da"
consent_end_date_time = "test_consent_end_date_tim"
subject_competence_indicator = "test_subject_competence_i"
translator_assistance_indicator = "test_translator_assistanc"
informational_material_supplied_indicator = "test_informational_materi"
consent_disclosure_level = "test_consent_disclosure_l"


class TestCON:
    """Comprehensive tests for CON segment."""

    def test_con_build_and_verify(self):
        seg = CON()

        seg.set_id_con = set_id_con
        seg.consent_form_id_and_version = consent_form_id_and_version
        seg.consent_discussion_date_time = consent_discussion_date_time
        seg.consent_decision_date_time = consent_decision_date_time
        seg.consent_effective_date_time = consent_effective_date_time
        seg.consent_end_date_time = consent_end_date_time
        seg.subject_competence_indicator = subject_competence_indicator
        seg.translator_assistance_indicator = translator_assistance_indicator
        seg.informational_material_supplied_indicator = informational_material_supplied_indicator
        seg.consent_disclosure_level = consent_disclosure_level

        assert seg.set_id_con == set_id_con
        assert seg.consent_form_id_and_version == consent_form_id_and_version
        assert seg.consent_discussion_date_time == consent_discussion_date_time
        assert seg.consent_decision_date_time == consent_decision_date_time
        assert seg.consent_effective_date_time == consent_effective_date_time
        assert seg.consent_end_date_time == consent_end_date_time
        assert seg.subject_competence_indicator == subject_competence_indicator
        assert seg.translator_assistance_indicator == translator_assistance_indicator
        assert seg.informational_material_supplied_indicator == informational_material_supplied_indicator
        assert seg.consent_disclosure_level == consent_disclosure_level

    def test_con_to_dict(self):
        seg = CON()

        seg.set_id_con = set_id_con
        seg.consent_form_id_and_version = consent_form_id_and_version
        seg.consent_discussion_date_time = consent_discussion_date_time
        seg.consent_decision_date_time = consent_decision_date_time
        seg.consent_effective_date_time = consent_effective_date_time
        seg.consent_end_date_time = consent_end_date_time
        seg.subject_competence_indicator = subject_competence_indicator
        seg.translator_assistance_indicator = translator_assistance_indicator
        seg.informational_material_supplied_indicator = informational_material_supplied_indicator
        seg.consent_disclosure_level = consent_disclosure_level

        result = seg.to_dict()

        assert result["_segment_id"] == "CON"
        assert result["set_id_con"] == set_id_con
        assert result["consent_form_id_and_version"] == consent_form_id_and_version
        assert result["consent_discussion_date_time"] == consent_discussion_date_time
        assert result["consent_decision_date_time"] == consent_decision_date_time
        assert result["consent_effective_date_time"] == consent_effective_date_time
        assert result["consent_end_date_time"] == consent_end_date_time
        assert result["subject_competence_indicator"] == subject_competence_indicator
        assert result["translator_assistance_indicator"] == translator_assistance_indicator
        assert result["informational_material_supplied_indicator"] == informational_material_supplied_indicator
        assert result["consent_disclosure_level"] == consent_disclosure_level

    def test_con_to_json(self):
        seg = CON()

        seg.set_id_con = set_id_con
        seg.consent_form_id_and_version = consent_form_id_and_version
        seg.consent_discussion_date_time = consent_discussion_date_time
        seg.consent_decision_date_time = consent_decision_date_time
        seg.consent_effective_date_time = consent_effective_date_time
        seg.consent_end_date_time = consent_end_date_time
        seg.subject_competence_indicator = subject_competence_indicator
        seg.translator_assistance_indicator = translator_assistance_indicator
        seg.informational_material_supplied_indicator = informational_material_supplied_indicator
        seg.consent_disclosure_level = consent_disclosure_level

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CON"
        assert result["set_id_con"] == set_id_con
        assert result["consent_form_id_and_version"] == consent_form_id_and_version
        assert result["consent_discussion_date_time"] == consent_discussion_date_time
        assert result["consent_decision_date_time"] == consent_decision_date_time
        assert result["consent_effective_date_time"] == consent_effective_date_time
        assert result["consent_end_date_time"] == consent_end_date_time
        assert result["subject_competence_indicator"] == subject_competence_indicator
        assert result["translator_assistance_indicator"] == translator_assistance_indicator
        assert result["informational_material_supplied_indicator"] == informational_material_supplied_indicator
        assert result["consent_disclosure_level"] == consent_disclosure_level
