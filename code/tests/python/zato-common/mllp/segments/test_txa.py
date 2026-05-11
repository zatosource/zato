from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import TXA


set_id_txa = "test_set_id_txa"
document_content_presentation = "test_document_content_pre"
activity_date_time = "test_activity_date_time"
origination_date_time = "test_origination_date_tim"
transcription_date_time = "test_transcription_date_t"
unique_document_file_name = "test_unique_document_file"
document_completion_status = "test_document_completion_"
document_confidentiality_status = "test_document_confidentia"
document_availability_status = "test_document_availabilit"
document_storage_status = "test_document_storage_sta"
document_change_reason = "test_document_change_reas"
agreed_due_date_time = "test_agreed_due_date_time"


class TestTXA:
    """Comprehensive tests for TXA segment."""

    def test_txa_build_and_verify(self):
        seg = TXA()

        seg.set_id_txa = set_id_txa
        seg.document_content_presentation = document_content_presentation
        seg.activity_date_time = activity_date_time
        seg.origination_date_time = origination_date_time
        seg.transcription_date_time = transcription_date_time
        seg.unique_document_file_name = unique_document_file_name
        seg.document_completion_status = document_completion_status
        seg.document_confidentiality_status = document_confidentiality_status
        seg.document_availability_status = document_availability_status
        seg.document_storage_status = document_storage_status
        seg.document_change_reason = document_change_reason
        seg.agreed_due_date_time = agreed_due_date_time

        assert seg.set_id_txa == set_id_txa
        assert seg.document_content_presentation == document_content_presentation
        assert seg.activity_date_time == activity_date_time
        assert seg.origination_date_time == origination_date_time
        assert seg.transcription_date_time == transcription_date_time
        assert seg.unique_document_file_name == unique_document_file_name
        assert seg.document_completion_status == document_completion_status
        assert seg.document_confidentiality_status == document_confidentiality_status
        assert seg.document_availability_status == document_availability_status
        assert seg.document_storage_status == document_storage_status
        assert seg.document_change_reason == document_change_reason
        assert seg.agreed_due_date_time == agreed_due_date_time

    def test_txa_to_dict(self):
        seg = TXA()

        seg.set_id_txa = set_id_txa
        seg.document_content_presentation = document_content_presentation
        seg.activity_date_time = activity_date_time
        seg.origination_date_time = origination_date_time
        seg.transcription_date_time = transcription_date_time
        seg.unique_document_file_name = unique_document_file_name
        seg.document_completion_status = document_completion_status
        seg.document_confidentiality_status = document_confidentiality_status
        seg.document_availability_status = document_availability_status
        seg.document_storage_status = document_storage_status
        seg.document_change_reason = document_change_reason
        seg.agreed_due_date_time = agreed_due_date_time

        result = seg.to_dict()

        assert result["_segment_id"] == "TXA"
        assert result["set_id_txa"] == set_id_txa
        assert result["document_content_presentation"] == document_content_presentation
        assert result["activity_date_time"] == activity_date_time
        assert result["origination_date_time"] == origination_date_time
        assert result["transcription_date_time"] == transcription_date_time
        assert result["unique_document_file_name"] == unique_document_file_name
        assert result["document_completion_status"] == document_completion_status
        assert result["document_confidentiality_status"] == document_confidentiality_status
        assert result["document_availability_status"] == document_availability_status
        assert result["document_storage_status"] == document_storage_status
        assert result["document_change_reason"] == document_change_reason
        assert result["agreed_due_date_time"] == agreed_due_date_time

    def test_txa_to_json(self):
        seg = TXA()

        seg.set_id_txa = set_id_txa
        seg.document_content_presentation = document_content_presentation
        seg.activity_date_time = activity_date_time
        seg.origination_date_time = origination_date_time
        seg.transcription_date_time = transcription_date_time
        seg.unique_document_file_name = unique_document_file_name
        seg.document_completion_status = document_completion_status
        seg.document_confidentiality_status = document_confidentiality_status
        seg.document_availability_status = document_availability_status
        seg.document_storage_status = document_storage_status
        seg.document_change_reason = document_change_reason
        seg.agreed_due_date_time = agreed_due_date_time

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "TXA"
        assert result["set_id_txa"] == set_id_txa
        assert result["document_content_presentation"] == document_content_presentation
        assert result["activity_date_time"] == activity_date_time
        assert result["origination_date_time"] == origination_date_time
        assert result["transcription_date_time"] == transcription_date_time
        assert result["unique_document_file_name"] == unique_document_file_name
        assert result["document_completion_status"] == document_completion_status
        assert result["document_confidentiality_status"] == document_confidentiality_status
        assert result["document_availability_status"] == document_availability_status
        assert result["document_storage_status"] == document_storage_status
        assert result["document_change_reason"] == document_change_reason
        assert result["agreed_due_date_time"] == agreed_due_date_time
