from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import FT1


set_id_ft1 = "test_set_id_ft1"
transaction_batch_id = "test_transaction_batch_id"
transaction_posting_date = "test_transaction_posting_"
transaction_quantity = "test_transaction_quantity"
model_number = "test_model_number"
prescription_number = "test_prescription_number"
dme_duration_value = "test_dme_duration_value"
dme_certification_revision_date = "test_dme_certification_re"
dme_initial_certification_date = "test_dme_initial_certific"
dme_last_certification_date = "test_dme_last_certificati"
dme_length_of_medical_necessity_days = "test_dme_length_of_medica"
dme_certification_condition_indicator = "test_dme_certification_co"


class TestFT1:
    """Comprehensive tests for FT1 segment."""

    def test_ft1_build_and_verify(self):
        seg = FT1()

        seg.set_id_ft1 = set_id_ft1
        seg.transaction_batch_id = transaction_batch_id
        seg.transaction_posting_date = transaction_posting_date
        seg.transaction_quantity = transaction_quantity
        seg.model_number = model_number
        seg.prescription_number = prescription_number
        seg.dme_duration_value = dme_duration_value
        seg.dme_certification_revision_date = dme_certification_revision_date
        seg.dme_initial_certification_date = dme_initial_certification_date
        seg.dme_last_certification_date = dme_last_certification_date
        seg.dme_length_of_medical_necessity_days = dme_length_of_medical_necessity_days
        seg.dme_certification_condition_indicator = dme_certification_condition_indicator

        assert seg.set_id_ft1 == set_id_ft1
        assert seg.transaction_batch_id == transaction_batch_id
        assert seg.transaction_posting_date == transaction_posting_date
        assert seg.transaction_quantity == transaction_quantity
        assert seg.model_number == model_number
        assert seg.prescription_number == prescription_number
        assert seg.dme_duration_value == dme_duration_value
        assert seg.dme_certification_revision_date == dme_certification_revision_date
        assert seg.dme_initial_certification_date == dme_initial_certification_date
        assert seg.dme_last_certification_date == dme_last_certification_date
        assert seg.dme_length_of_medical_necessity_days == dme_length_of_medical_necessity_days
        assert seg.dme_certification_condition_indicator == dme_certification_condition_indicator

    def test_ft1_to_dict(self):
        seg = FT1()

        seg.set_id_ft1 = set_id_ft1
        seg.transaction_batch_id = transaction_batch_id
        seg.transaction_posting_date = transaction_posting_date
        seg.transaction_quantity = transaction_quantity
        seg.model_number = model_number
        seg.prescription_number = prescription_number
        seg.dme_duration_value = dme_duration_value
        seg.dme_certification_revision_date = dme_certification_revision_date
        seg.dme_initial_certification_date = dme_initial_certification_date
        seg.dme_last_certification_date = dme_last_certification_date
        seg.dme_length_of_medical_necessity_days = dme_length_of_medical_necessity_days
        seg.dme_certification_condition_indicator = dme_certification_condition_indicator

        result = seg.to_dict()

        assert result["_segment_id"] == "FT1"
        assert result["set_id_ft1"] == set_id_ft1
        assert result["transaction_batch_id"] == transaction_batch_id
        assert result["transaction_posting_date"] == transaction_posting_date
        assert result["transaction_quantity"] == transaction_quantity
        assert result["model_number"] == model_number
        assert result["prescription_number"] == prescription_number
        assert result["dme_duration_value"] == dme_duration_value
        assert result["dme_certification_revision_date"] == dme_certification_revision_date
        assert result["dme_initial_certification_date"] == dme_initial_certification_date
        assert result["dme_last_certification_date"] == dme_last_certification_date
        assert result["dme_length_of_medical_necessity_days"] == dme_length_of_medical_necessity_days
        assert result["dme_certification_condition_indicator"] == dme_certification_condition_indicator

    def test_ft1_to_json(self):
        seg = FT1()

        seg.set_id_ft1 = set_id_ft1
        seg.transaction_batch_id = transaction_batch_id
        seg.transaction_posting_date = transaction_posting_date
        seg.transaction_quantity = transaction_quantity
        seg.model_number = model_number
        seg.prescription_number = prescription_number
        seg.dme_duration_value = dme_duration_value
        seg.dme_certification_revision_date = dme_certification_revision_date
        seg.dme_initial_certification_date = dme_initial_certification_date
        seg.dme_last_certification_date = dme_last_certification_date
        seg.dme_length_of_medical_necessity_days = dme_length_of_medical_necessity_days
        seg.dme_certification_condition_indicator = dme_certification_condition_indicator

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "FT1"
        assert result["set_id_ft1"] == set_id_ft1
        assert result["transaction_batch_id"] == transaction_batch_id
        assert result["transaction_posting_date"] == transaction_posting_date
        assert result["transaction_quantity"] == transaction_quantity
        assert result["model_number"] == model_number
        assert result["prescription_number"] == prescription_number
        assert result["dme_duration_value"] == dme_duration_value
        assert result["dme_certification_revision_date"] == dme_certification_revision_date
        assert result["dme_initial_certification_date"] == dme_initial_certification_date
        assert result["dme_last_certification_date"] == dme_last_certification_date
        assert result["dme_length_of_medical_necessity_days"] == dme_length_of_medical_necessity_days
        assert result["dme_certification_condition_indicator"] == dme_certification_condition_indicator
