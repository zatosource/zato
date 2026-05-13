from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import RXV


set_id_rxv = "test_set_id_rxv"
bolus_type = "test_bolus_type"
bolus_dose_amount = "test_bolus_dose_amount"
bolus_dose_volume = "test_bolus_dose_volume"
pca_type = "test_pca_type"
pca_dose_amount = "test_pca_dose_amount"
pca_dose_amount_volume = "test_pca_dose_amount_volu"
max_dose_amount = "test_max_dose_amount"
max_dose_amount_volume = "test_max_dose_amount_volu"
syringe_size = "test_syringe_size"
action_code = "test_action_code"


class TestRXV:
    """Comprehensive tests for RXV segment."""

    def test_rxv_build_and_verify(self):
        seg = RXV()

        seg.set_id_rxv = set_id_rxv
        seg.bolus_type = bolus_type
        seg.bolus_dose_amount = bolus_dose_amount
        seg.bolus_dose_volume = bolus_dose_volume
        seg.pca_type = pca_type
        seg.pca_dose_amount = pca_dose_amount
        seg.pca_dose_amount_volume = pca_dose_amount_volume
        seg.max_dose_amount = max_dose_amount
        seg.max_dose_amount_volume = max_dose_amount_volume
        seg.syringe_size = syringe_size
        seg.action_code = action_code

        assert seg.set_id_rxv == set_id_rxv
        assert seg.bolus_type == bolus_type
        assert seg.bolus_dose_amount == bolus_dose_amount
        assert seg.bolus_dose_volume == bolus_dose_volume
        assert seg.pca_type == pca_type
        assert seg.pca_dose_amount == pca_dose_amount
        assert seg.pca_dose_amount_volume == pca_dose_amount_volume
        assert seg.max_dose_amount == max_dose_amount
        assert seg.max_dose_amount_volume == max_dose_amount_volume
        assert seg.syringe_size == syringe_size
        assert seg.action_code == action_code

    def test_rxv_to_dict(self):
        seg = RXV()

        seg.set_id_rxv = set_id_rxv
        seg.bolus_type = bolus_type
        seg.bolus_dose_amount = bolus_dose_amount
        seg.bolus_dose_volume = bolus_dose_volume
        seg.pca_type = pca_type
        seg.pca_dose_amount = pca_dose_amount
        seg.pca_dose_amount_volume = pca_dose_amount_volume
        seg.max_dose_amount = max_dose_amount
        seg.max_dose_amount_volume = max_dose_amount_volume
        seg.syringe_size = syringe_size
        seg.action_code = action_code

        result = seg.to_dict()

        assert result["_segment_id"] == "RXV"
        assert result["set_id_rxv"] == set_id_rxv
        assert result["bolus_type"] == bolus_type
        assert result["bolus_dose_amount"] == bolus_dose_amount
        assert result["bolus_dose_volume"] == bolus_dose_volume
        assert result["pca_type"] == pca_type
        assert result["pca_dose_amount"] == pca_dose_amount
        assert result["pca_dose_amount_volume"] == pca_dose_amount_volume
        assert result["max_dose_amount"] == max_dose_amount
        assert result["max_dose_amount_volume"] == max_dose_amount_volume
        assert result["syringe_size"] == syringe_size
        assert result["action_code"] == action_code

    def test_rxv_to_json(self):
        seg = RXV()

        seg.set_id_rxv = set_id_rxv
        seg.bolus_type = bolus_type
        seg.bolus_dose_amount = bolus_dose_amount
        seg.bolus_dose_volume = bolus_dose_volume
        seg.pca_type = pca_type
        seg.pca_dose_amount = pca_dose_amount
        seg.pca_dose_amount_volume = pca_dose_amount_volume
        seg.max_dose_amount = max_dose_amount
        seg.max_dose_amount_volume = max_dose_amount_volume
        seg.syringe_size = syringe_size
        seg.action_code = action_code

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "RXV"
        assert result["set_id_rxv"] == set_id_rxv
        assert result["bolus_type"] == bolus_type
        assert result["bolus_dose_amount"] == bolus_dose_amount
        assert result["bolus_dose_volume"] == bolus_dose_volume
        assert result["pca_type"] == pca_type
        assert result["pca_dose_amount"] == pca_dose_amount
        assert result["pca_dose_amount_volume"] == pca_dose_amount_volume
        assert result["max_dose_amount"] == max_dose_amount
        assert result["max_dose_amount_volume"] == max_dose_amount_volume
        assert result["syringe_size"] == syringe_size
        assert result["action_code"] == action_code
