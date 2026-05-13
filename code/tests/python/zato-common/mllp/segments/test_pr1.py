from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PR1


set_id_pr1 = "test_set_id_pr1"
procedure_date_time = "test_procedure_date_time"
procedure_minutes = "test_procedure_minutes"
anesthesia_minutes = "test_anesthesia_minutes"
procedure_priority = "test_procedure_priority"
procedure_action_code = "test_procedure_action_cod"
respiratory_within_surgery = "test_respiratory_within_s"


class TestPR1:
    """Comprehensive tests for PR1 segment."""

    def test_pr1_build_and_verify(self):
        seg = PR1()

        seg.set_id_pr1 = set_id_pr1
        seg.procedure_date_time = procedure_date_time
        seg.procedure_minutes = procedure_minutes
        seg.anesthesia_minutes = anesthesia_minutes
        seg.procedure_priority = procedure_priority
        seg.procedure_action_code = procedure_action_code
        seg.respiratory_within_surgery = respiratory_within_surgery

        assert seg.set_id_pr1 == set_id_pr1
        assert seg.procedure_date_time == procedure_date_time
        assert seg.procedure_minutes == procedure_minutes
        assert seg.anesthesia_minutes == anesthesia_minutes
        assert seg.procedure_priority == procedure_priority
        assert seg.procedure_action_code == procedure_action_code
        assert seg.respiratory_within_surgery == respiratory_within_surgery

    def test_pr1_to_dict(self):
        seg = PR1()

        seg.set_id_pr1 = set_id_pr1
        seg.procedure_date_time = procedure_date_time
        seg.procedure_minutes = procedure_minutes
        seg.anesthesia_minutes = anesthesia_minutes
        seg.procedure_priority = procedure_priority
        seg.procedure_action_code = procedure_action_code
        seg.respiratory_within_surgery = respiratory_within_surgery

        result = seg.to_dict()

        assert result["_segment_id"] == "PR1"
        assert result["set_id_pr1"] == set_id_pr1
        assert result["procedure_date_time"] == procedure_date_time
        assert result["procedure_minutes"] == procedure_minutes
        assert result["anesthesia_minutes"] == anesthesia_minutes
        assert result["procedure_priority"] == procedure_priority
        assert result["procedure_action_code"] == procedure_action_code
        assert result["respiratory_within_surgery"] == respiratory_within_surgery

    def test_pr1_to_json(self):
        seg = PR1()

        seg.set_id_pr1 = set_id_pr1
        seg.procedure_date_time = procedure_date_time
        seg.procedure_minutes = procedure_minutes
        seg.anesthesia_minutes = anesthesia_minutes
        seg.procedure_priority = procedure_priority
        seg.procedure_action_code = procedure_action_code
        seg.respiratory_within_surgery = respiratory_within_surgery

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PR1"
        assert result["set_id_pr1"] == set_id_pr1
        assert result["procedure_date_time"] == procedure_date_time
        assert result["procedure_minutes"] == procedure_minutes
        assert result["anesthesia_minutes"] == anesthesia_minutes
        assert result["procedure_priority"] == procedure_priority
        assert result["procedure_action_code"] == procedure_action_code
        assert result["respiratory_within_surgery"] == respiratory_within_surgery
