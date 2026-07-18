# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.common.fhir.display import build_display_tree, parse_and_render, render_display_text

# ################################################################################################################################
# ################################################################################################################################

# A patient with nested complex elements and a repeating name
_patient = {
    'resourceType': 'Patient',
    'id': 'patient-001',
    'active': True,
    'name': [
        {'family': 'Smith', 'given': ['John', 'A'], 'use': 'official'},
        {'family': 'Smith', 'given': ['Johnny'], 'use': 'nickname'},
    ],
    'birthDate': '1985-03-15',
    'managingOrganization': {'reference': 'Organization/general-hospital'},
}

# A failed call's outcome - one issue with diagnostics, one with coded details only
_operation_outcome = {
    'resourceType': 'OperationOutcome',
    'issue': [
        {
            'severity': 'error',
            'code': 'invalid',
            'diagnostics': 'Element Patient.birthDate has an invalid value',
        },
        {
            'severity': 'warning',
            'code': 'code-invalid',
            'details': {'text': 'Unknown code in value set'},
        },
    ],
}

# ################################################################################################################################
# ################################################################################################################################

class TestRenderDisplayText:
    """ The plain-text rendering of a FHIR display tree - what the IDE's parsed view shows.
    """

    def test_the_rendering_covers_the_whole_tree(self) -> 'None':

        tree = build_display_tree(_patient)

        text = render_display_text(tree)
        lines = text.split('\n')

        # The header line names the resource
        assert lines[0] == 'Patient'

        # Scalars render with their labels and values, indented under the header
        assert '  Birth Date: 1985-03-15' in lines
        assert '  Active: True' in lines

        # Repeating elements render as numbered containers with their children indented deeper
        assert '  Name:' in lines
        assert '    Name 1:' in lines
        assert '      Family: Smith' in lines

        # Complex elements render as containers too
        assert '  Managing Organization:' in lines
        assert '    Reference: Organization/general-hospital' in lines

    def test_operation_outcome_issues_come_first(self) -> 'None':

        tree = build_display_tree(_operation_outcome)

        text = render_display_text(tree)
        lines = text.split('\n')

        # The header line names the resource
        assert lines[0] == 'Operation Outcome'

        # The issue summaries follow immediately, before the element tree
        assert lines[2] == '  error (invalid): Element Patient.birthDate has an invalid value'
        assert lines[3] == '  warning (code-invalid): Unknown code in value set'

        # The element tree itself still follows
        assert '  Issue:' in lines

# ################################################################################################################################
# ################################################################################################################################

class TestParseAndRender:
    """ The parse-then-render convenience the IDE's parsed view uses for FHIR payloads.
    """

    def test_a_resource_renders_its_display_tree(self) -> 'None':

        data = json.dumps(_patient)
        text = parse_and_render(data)

        lines = text.split('\n')
        assert lines[0] == 'Patient'
        assert '  Birth Date: 1985-03-15' in lines

    def test_a_payload_that_is_not_json_renders_as_an_empty_string(self) -> 'None':

        text = parse_and_render('This is not a FHIR resource at all')
        assert text == ''

    def test_json_without_a_resource_type_renders_as_an_empty_string(self) -> 'None':

        text = parse_and_render('{"family": "Smith"}')
        assert text == ''

# ################################################################################################################################
# ################################################################################################################################
