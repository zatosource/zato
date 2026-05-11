from __future__ import annotations

import json
import pytest

from zato.hl7v2.v2_9.segments import ERR


severity = "test_severity"
application_error_parameter = "test_application_error_pa"
diagnostic_information = "test_diagnostic_informati"
user_message = "test_user_message"


class TestERR:
    """Comprehensive tests for ERR segment."""

    def test_err_build_and_verify(self):
        seg = ERR()

        seg.severity = severity
        seg.application_error_parameter = application_error_parameter
        seg.diagnostic_information = diagnostic_information
        seg.user_message = user_message

        assert seg.severity == severity
        assert seg.application_error_parameter == application_error_parameter
        assert seg.diagnostic_information == diagnostic_information
        assert seg.user_message == user_message

    def test_err_to_dict(self):
        seg = ERR()

        seg.severity = severity
        seg.application_error_parameter = application_error_parameter
        seg.diagnostic_information = diagnostic_information
        seg.user_message = user_message

        result = seg.to_dict()

        assert result["_segment_id"] == "ERR"
        assert result["severity"] == severity
        assert result["application_error_parameter"] == application_error_parameter
        assert result["diagnostic_information"] == diagnostic_information
        assert result["user_message"] == user_message

    def test_err_to_json(self):
        seg = ERR()

        seg.severity = severity
        seg.application_error_parameter = application_error_parameter
        seg.diagnostic_information = diagnostic_information
        seg.user_message = user_message

        result = json.loads(seg.to_json())

        assert result["_segment_id"] == "ERR"
        assert result["severity"] == severity
        assert result["application_error_parameter"] == application_error_parameter
        assert result["diagnostic_information"] == diagnostic_information
        assert result["user_message"] == user_message
