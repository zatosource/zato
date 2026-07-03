"""Tests for 9a - validate_to_outcome returning typed OperationOutcome."""

from __future__ import annotations

import json


from zato.fhir.validation import validate_to_outcome
from zato.fhir.r4_0_1.resources import (
    Observation,
    OperationOutcome,
    OperationOutcomeIssue,
    Patient,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _valid_patient() -> Patient:
    p = Patient()
    p.id = 'p1'
    p.active = True
    return p


def _invalid_observation() -> Observation:
    return Observation()


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------

class TestReturnType:

    def test_returns_operation_outcome(self):
        oo = validate_to_outcome(_valid_patient())
        assert isinstance(oo, OperationOutcome)

    def test_issues_are_typed(self):
        oo = validate_to_outcome(_valid_patient())
        assert isinstance(oo.issue[0], OperationOutcomeIssue)

    def test_resource_type(self):
        oo = validate_to_outcome(_valid_patient())
        assert oo._resource_type == 'OperationOutcome'


# ---------------------------------------------------------------------------
# Valid resource
# ---------------------------------------------------------------------------

class TestValidResource:

    def test_single_informational_issue(self):
        oo = validate_to_outcome(_valid_patient())
        assert len(oo.issue) == 1

    def test_severity_information(self):
        oo = validate_to_outcome(_valid_patient())
        assert oo.issue[0].severity == 'information'

    def test_code_informational(self):
        oo = validate_to_outcome(_valid_patient())
        assert oo.issue[0].code == 'informational'

    def test_diagnostics_successful(self):
        oo = validate_to_outcome(_valid_patient())
        assert oo.issue[0].diagnostics == 'Validation successful'


# ---------------------------------------------------------------------------
# Invalid resource - missing required fields
# ---------------------------------------------------------------------------

class TestInvalidRequired:

    def test_has_error_issues(self):
        oo = validate_to_outcome(_invalid_observation())
        error_issues = [i for i in oo.issue if i.severity == 'error']
        assert len(error_issues) >= 2

    def test_missing_status(self):
        oo = validate_to_outcome(_invalid_observation())
        msgs = [i.diagnostics for i in oo.issue]
        assert any('status' in m for m in msgs)

    def test_missing_code(self):
        oo = validate_to_outcome(_invalid_observation())
        msgs = [i.diagnostics for i in oo.issue]
        assert any('code' in m for m in msgs)

    def test_issue_code_is_required(self):
        oo = validate_to_outcome(_invalid_observation())
        for issue in oo.issue:
            if issue.severity == 'error':
                assert issue.code == 'required'

    def test_expression_set(self):
        oo = validate_to_outcome(_invalid_observation())
        for issue in oo.issue:
            if issue.severity == 'error':
                assert len(issue.expression) >= 1


# ---------------------------------------------------------------------------
# Dot access convenience
# ---------------------------------------------------------------------------

class TestDotAccess:

    def test_issue_dot_severity(self):
        oo = validate_to_outcome(_valid_patient())
        assert oo.issue.severity == 'information'

    def test_issue_dot_diagnostics(self):
        oo = validate_to_outcome(_valid_patient())
        assert oo.issue.diagnostics == 'Validation successful'


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

class TestSerialization:

    def test_to_dict(self):
        oo = validate_to_outcome(_valid_patient())
        d = oo.to_dict()
        assert d['resourceType'] == 'OperationOutcome'
        assert len(d['issue']) == 1
        assert d['issue'][0]['severity'] == 'information'

    def test_to_json(self):
        oo = validate_to_outcome(_valid_patient())
        j = oo.to_json()
        data = json.loads(j)
        assert data['resourceType'] == 'OperationOutcome'
        assert data['issue'][0]['code'] == 'informational'

    def test_roundtrip(self):
        oo1 = validate_to_outcome(_invalid_observation())
        j = oo1.to_json()
        oo2 = OperationOutcome.from_json(j)
        assert isinstance(oo2, OperationOutcome)
        assert len(oo2.issue) == len(oo1.issue)
        for i1, i2 in zip(oo1.issue, oo2.issue):
            assert i1.severity == i2.severity
            assert i1.code == i2.code
            assert i1.diagnostics == i2.diagnostics

    def test_invalid_to_dict_has_errors(self):
        oo = validate_to_outcome(_invalid_observation())
        d = oo.to_dict()
        assert len(d['issue']) >= 2
        severities = {i['severity'] for i in d['issue']}
        assert 'error' in severities


# ---------------------------------------------------------------------------
# include_valueset flag
# ---------------------------------------------------------------------------

class TestIncludeValueset:

    def test_without_valueset(self):
        oo = validate_to_outcome(_valid_patient(), include_valueset=False)
        assert isinstance(oo, OperationOutcome)
        assert oo.issue.severity == 'information'
