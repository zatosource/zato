from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import PV1


set_id_pv1 = "test_set_id_pv1"
transfer_to_bad_debt_date = "test_transfer_to_bad_debt"
bad_debt_transfer_amount = "test_bad_debt_transfer_am"
bad_debt_recovery_amount = "test_bad_debt_recovery_am"
delete_account_date = "test_delete_account_date"
admit_date_time = "test_admit_date_time"
discharge_date_time = "test_discharge_date_time"
current_patient_balance = "test_current_patient_bala"
total_charges = "test_total_charges"
total_adjustments = "test_total_adjustments"
total_payments = "test_total_payments"
service_episode_description = "test_service_episode_desc"


class TestPV1:
    """Comprehensive tests for PV1 segment."""

    def test_pv1_build_and_verify(self):
        seg = PV1()

        seg.set_id_pv1 = set_id_pv1
        seg.transfer_to_bad_debt_date = transfer_to_bad_debt_date
        seg.bad_debt_transfer_amount = bad_debt_transfer_amount
        seg.bad_debt_recovery_amount = bad_debt_recovery_amount
        seg.delete_account_date = delete_account_date
        seg.admit_date_time = admit_date_time
        seg.discharge_date_time = discharge_date_time
        seg.current_patient_balance = current_patient_balance
        seg.total_charges = total_charges
        seg.total_adjustments = total_adjustments
        seg.total_payments = total_payments
        seg.service_episode_description = service_episode_description

        assert seg.set_id_pv1 == set_id_pv1
        assert seg.transfer_to_bad_debt_date == transfer_to_bad_debt_date
        assert seg.bad_debt_transfer_amount == bad_debt_transfer_amount
        assert seg.bad_debt_recovery_amount == bad_debt_recovery_amount
        assert seg.delete_account_date == delete_account_date
        assert seg.admit_date_time == admit_date_time
        assert seg.discharge_date_time == discharge_date_time
        assert seg.current_patient_balance == current_patient_balance
        assert seg.total_charges == total_charges
        assert seg.total_adjustments == total_adjustments
        assert seg.total_payments == total_payments
        assert seg.service_episode_description == service_episode_description

    def test_pv1_to_dict(self):
        seg = PV1()

        seg.set_id_pv1 = set_id_pv1
        seg.transfer_to_bad_debt_date = transfer_to_bad_debt_date
        seg.bad_debt_transfer_amount = bad_debt_transfer_amount
        seg.bad_debt_recovery_amount = bad_debt_recovery_amount
        seg.delete_account_date = delete_account_date
        seg.admit_date_time = admit_date_time
        seg.discharge_date_time = discharge_date_time
        seg.current_patient_balance = current_patient_balance
        seg.total_charges = total_charges
        seg.total_adjustments = total_adjustments
        seg.total_payments = total_payments
        seg.service_episode_description = service_episode_description

        result = seg.to_dict()

        assert result["_segment_id"] == "PV1"
        assert result["set_id_pv1"] == set_id_pv1
        assert result["transfer_to_bad_debt_date"] == transfer_to_bad_debt_date
        assert result["bad_debt_transfer_amount"] == bad_debt_transfer_amount
        assert result["bad_debt_recovery_amount"] == bad_debt_recovery_amount
        assert result["delete_account_date"] == delete_account_date
        assert result["admit_date_time"] == admit_date_time
        assert result["discharge_date_time"] == discharge_date_time
        assert result["current_patient_balance"] == current_patient_balance
        assert result["total_charges"] == total_charges
        assert result["total_adjustments"] == total_adjustments
        assert result["total_payments"] == total_payments
        assert result["service_episode_description"] == service_episode_description

    def test_pv1_to_json(self):
        seg = PV1()

        seg.set_id_pv1 = set_id_pv1
        seg.transfer_to_bad_debt_date = transfer_to_bad_debt_date
        seg.bad_debt_transfer_amount = bad_debt_transfer_amount
        seg.bad_debt_recovery_amount = bad_debt_recovery_amount
        seg.delete_account_date = delete_account_date
        seg.admit_date_time = admit_date_time
        seg.discharge_date_time = discharge_date_time
        seg.current_patient_balance = current_patient_balance
        seg.total_charges = total_charges
        seg.total_adjustments = total_adjustments
        seg.total_payments = total_payments
        seg.service_episode_description = service_episode_description

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "PV1"
        assert result["set_id_pv1"] == set_id_pv1
        assert result["transfer_to_bad_debt_date"] == transfer_to_bad_debt_date
        assert result["bad_debt_transfer_amount"] == bad_debt_transfer_amount
        assert result["bad_debt_recovery_amount"] == bad_debt_recovery_amount
        assert result["delete_account_date"] == delete_account_date
        assert result["admit_date_time"] == admit_date_time
        assert result["discharge_date_time"] == discharge_date_time
        assert result["current_patient_balance"] == current_patient_balance
        assert result["total_charges"] == total_charges
        assert result["total_adjustments"] == total_adjustments
        assert result["total_payments"] == total_payments
        assert result["service_episode_description"] == service_episode_description
