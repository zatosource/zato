# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.fhir.display import build_display_tree

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict
    anylist = anylist
    stranydict = stranydict

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
# and one with no text at all
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
        {
            'severity': 'information',
            'code': 'informational',
        },
    ],
}

# ################################################################################################################################
# ################################################################################################################################

def _get_node(nodes:'anylist', name:'str') -> 'stranydict':
    for node in nodes:
        if node['name'] == name:
            return node
    raise Exception(f'Node `{name}` not found in `{nodes}`')

# ################################################################################################################################
# ################################################################################################################################

class TestResourceTree:

    def test_header_identifies_the_resource(self) -> 'None':

        tree = build_display_tree(_patient)

        assert tree['resource_type'] == 'Patient'
        assert tree['label'] == 'Patient'

    def test_nodes_keep_document_order_and_skip_the_resource_type(self) -> 'None':

        tree = build_display_tree(_patient)

        names = [node['name'] for node in tree['nodes']]
        assert names == ['id', 'active', 'name', 'birthDate', 'managingOrganization']

    def test_scalar_element_carries_its_native_value(self) -> 'None':

        tree = build_display_tree(_patient)

        birth_date = _get_node(tree['nodes'], 'birthDate')
        assert birth_date['label'] == 'Birth Date'
        assert birth_date['value'] == '1985-03-15'
        assert birth_date['children'] == []

        active = _get_node(tree['nodes'], 'active')
        assert active['value'] is True

    def test_repeating_element_fans_out_into_numbered_children(self) -> 'None':

        tree = build_display_tree(_patient)

        name = _get_node(tree['nodes'], 'name')
        assert name['value'] is None

        children = name['children']
        assert len(children) == 2
        assert children[0]['name'] == 'name[0]'
        assert children[0]['label'] == 'Name 1'
        assert children[1]['name'] == 'name[1]'
        assert children[1]['label'] == 'Name 2'

    def test_complex_element_fans_out_into_labeled_children(self) -> 'None':

        tree = build_display_tree(_patient)

        name = _get_node(tree['nodes'], 'name')
        official = name['children'][0]

        family = _get_node(official['children'], 'family')
        assert family['label'] == 'Family'
        assert family['value'] == 'Smith'

        organization = _get_node(tree['nodes'], 'managingOrganization')
        assert organization['label'] == 'Managing Organization'

        reference = _get_node(organization['children'], 'reference')
        assert reference['value'] == 'Organization/general-hospital'

# ################################################################################################################################
# ################################################################################################################################

class TestOperationOutcome:

    def test_plain_resource_has_no_issue_summary(self) -> 'None':

        tree = build_display_tree(_patient)
        assert 'issues' not in tree

    def test_issues_are_summarized(self) -> 'None':

        tree = build_display_tree(_operation_outcome)

        assert tree['resource_type'] == 'OperationOutcome'
        assert tree['label'] == 'Operation Outcome'

        issues = tree['issues']
        assert len(issues) == 3

    def test_diagnostics_is_the_preferred_text(self) -> 'None':

        tree = build_display_tree(_operation_outcome)
        issue = tree['issues'][0]

        assert issue['severity'] == 'error'
        assert issue['code'] == 'invalid'
        assert issue['text'] == 'Element Patient.birthDate has an invalid value'

    def test_details_text_is_the_fallback(self) -> 'None':

        tree = build_display_tree(_operation_outcome)
        issue = tree['issues'][1]

        assert issue['severity'] == 'warning'
        assert issue['text'] == 'Unknown code in value set'

    def test_an_issue_with_no_text_stays_empty(self) -> 'None':

        tree = build_display_tree(_operation_outcome)
        issue = tree['issues'][2]

        assert issue['severity'] == 'information'
        assert issue['text'] == ''

    def test_issues_also_appear_in_the_tree_itself(self) -> 'None':

        tree = build_display_tree(_operation_outcome)

        issue_node = _get_node(tree['nodes'], 'issue')
        assert issue_node['label'] == 'Issue'
        assert len(issue_node['children']) == 3

        first_issue = issue_node['children'][0]
        severity = _get_node(first_issue['children'], 'severity')
        assert severity['value'] == 'error'

# ################################################################################################################################
# ################################################################################################################################
