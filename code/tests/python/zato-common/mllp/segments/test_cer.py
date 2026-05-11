from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import CER


set_id_cer = "test_set_id_cer"
serial_number = "test_serial_number"
version = "test_version"
granting_country = "test_granting_country"
subject_name = "test_subject_name"
basic_constraint = "test_basic_constraint"
jurisdiction_country = "test_jurisdiction_country"
granting_date = "test_granting_date"
issuing_date = "test_issuing_date"
activation_date = "test_activation_date"
inactivation_date = "test_inactivation_date"
expiration_date = "test_expiration_date"
renewal_date = "test_renewal_date"
revocation_date = "test_revocation_date"


class TestCER:
    """Comprehensive tests for CER segment."""

    def test_cer_build_and_verify(self):
        seg = CER()

        seg.set_id_cer = set_id_cer
        seg.serial_number = serial_number
        seg.version = version
        seg.granting_country = granting_country
        seg.subject_name = subject_name
        seg.basic_constraint = basic_constraint
        seg.jurisdiction_country = jurisdiction_country
        seg.granting_date = granting_date
        seg.issuing_date = issuing_date
        seg.activation_date = activation_date
        seg.inactivation_date = inactivation_date
        seg.expiration_date = expiration_date
        seg.renewal_date = renewal_date
        seg.revocation_date = revocation_date

        assert seg.set_id_cer == set_id_cer
        assert seg.serial_number == serial_number
        assert seg.version == version
        assert seg.granting_country == granting_country
        assert seg.subject_name == subject_name
        assert seg.basic_constraint == basic_constraint
        assert seg.jurisdiction_country == jurisdiction_country
        assert seg.granting_date == granting_date
        assert seg.issuing_date == issuing_date
        assert seg.activation_date == activation_date
        assert seg.inactivation_date == inactivation_date
        assert seg.expiration_date == expiration_date
        assert seg.renewal_date == renewal_date
        assert seg.revocation_date == revocation_date

    def test_cer_to_dict(self):
        seg = CER()

        seg.set_id_cer = set_id_cer
        seg.serial_number = serial_number
        seg.version = version
        seg.granting_country = granting_country
        seg.subject_name = subject_name
        seg.basic_constraint = basic_constraint
        seg.jurisdiction_country = jurisdiction_country
        seg.granting_date = granting_date
        seg.issuing_date = issuing_date
        seg.activation_date = activation_date
        seg.inactivation_date = inactivation_date
        seg.expiration_date = expiration_date
        seg.renewal_date = renewal_date
        seg.revocation_date = revocation_date

        result = seg.to_dict()

        assert result["_segment_id"] == "CER"
        assert result["set_id_cer"] == set_id_cer
        assert result["serial_number"] == serial_number
        assert result["version"] == version
        assert result["granting_country"] == granting_country
        assert result["subject_name"] == subject_name
        assert result["basic_constraint"] == basic_constraint
        assert result["jurisdiction_country"] == jurisdiction_country
        assert result["granting_date"] == granting_date
        assert result["issuing_date"] == issuing_date
        assert result["activation_date"] == activation_date
        assert result["inactivation_date"] == inactivation_date
        assert result["expiration_date"] == expiration_date
        assert result["renewal_date"] == renewal_date
        assert result["revocation_date"] == revocation_date

    def test_cer_to_json(self):
        seg = CER()

        seg.set_id_cer = set_id_cer
        seg.serial_number = serial_number
        seg.version = version
        seg.granting_country = granting_country
        seg.subject_name = subject_name
        seg.basic_constraint = basic_constraint
        seg.jurisdiction_country = jurisdiction_country
        seg.granting_date = granting_date
        seg.issuing_date = issuing_date
        seg.activation_date = activation_date
        seg.inactivation_date = inactivation_date
        seg.expiration_date = expiration_date
        seg.renewal_date = renewal_date
        seg.revocation_date = revocation_date

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "CER"
        assert result["set_id_cer"] == set_id_cer
        assert result["serial_number"] == serial_number
        assert result["version"] == version
        assert result["granting_country"] == granting_country
        assert result["subject_name"] == subject_name
        assert result["basic_constraint"] == basic_constraint
        assert result["jurisdiction_country"] == jurisdiction_country
        assert result["granting_date"] == granting_date
        assert result["issuing_date"] == issuing_date
        assert result["activation_date"] == activation_date
        assert result["inactivation_date"] == inactivation_date
        assert result["expiration_date"] == expiration_date
        assert result["renewal_date"] == renewal_date
        assert result["revocation_date"] == revocation_date
