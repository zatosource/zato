# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from unittest import TestCase, main

# Zato
from zato.openapi.generator.io_scanner import TypeMapper
from zato.openapi.generator.naming import get_group_segments, get_summary, get_tags
from zato.openapi.generator.openapi_ import OpenAPIGenerator

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist
    anydict = anydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The services behind the test endpoints, whose names the document never contains
_service_patients     = 'internal.records.patient-lookup'
_service_appointments = 'internal.calendar.appointment-booking'

_docstring_patients     = 'Returns a patient, e.g. by a medical record number. The record includes the address.'
_docstring_appointments = 'Books an appointment.'

_url_path_patients     = '/api/healthcare/v1/patients/{patient_id}'
_url_path_appointments = '/api/healthcare/appointments'

# How many operations are added to a section for it to have more than one group holds
_large_section_padding = 9

# ################################################################################################################################
# ################################################################################################################################

def _make_service_entry(name:'str', url_path:'str', http_method:'str', docstring:'str') -> 'anydict':
    """ Builds one generator service entry.
    """
    out = {
        'name': name,
        'class_name': 'TestService',
        'url_path': url_path,
        'http_method': http_method,
        'docstring': docstring,
        'input': {'type': 'any'},
        'output': {'type': 'any'},
        'is_deprecated': False,
        'deprecation_sunset': '',
        'deprecation_successor': '',
    }

    return out

# ################################################################################################################################

def _make_large_section(paths:'strlist') -> 'strlist':
    """ Returns the paths together with enough other healthcare operations for the section to be divided into groups.
    """
    out = list(paths)

    for index in range(_large_section_padding):
        out.append(f'/api/healthcare/padding/item-{index}')

    return out

# ################################################################################################################################
# ################################################################################################################################

class NamingOpenAPITestCase(TestCase):
    """ Verifies that operations are named and grouped by their URL paths and docstrings, never by their services.
    """

    def setUp(self) -> 'None':

        services = [
            _make_service_entry(_service_patients, _url_path_patients, 'get', _docstring_patients),
            _make_service_entry(_service_appointments, _url_path_appointments, 'post', _docstring_appointments),
        ]

        generator = OpenAPIGenerator(TypeMapper())
        self.document = generator.build_spec({'services': services, 'models': {}})

        self.patients = self.document['paths'][_url_path_patients]['get']
        self.appointments = self.document['paths'][_url_path_appointments]['post']

# ################################################################################################################################

    def test_the_document_never_names_a_service(self) -> 'None':

        text = json.dumps(self.document)

        self.assertNotIn(_service_patients, text)
        self.assertNotIn(_service_appointments, text)

# ################################################################################################################################

    def test_operations_of_a_small_section_are_one_group(self) -> 'None':

        self.assertEqual(self.patients['tags'], ['Healthcare'])
        self.assertEqual(self.appointments['tags'], ['Healthcare'])

# ################################################################################################################################

    def test_a_large_section_is_divided_by_the_segment_that_follows_it(self) -> 'None':

        paths = _make_large_section([
            '/api/healthcare/v1/patients/{patient_id}',
            '/api/healthcare/decision-support',
            '/tutorial/api/get-user',
        ])
        tags = get_tags(paths)

        self.assertEqual(tags['/api/healthcare/v1/patients/{patient_id}'], 'Healthcare / Patients')
        self.assertEqual(tags['/api/healthcare/decision-support'], 'Healthcare / Decision support')
        self.assertEqual(tags['/tutorial/api/get-user'], 'Tutorial')

# ################################################################################################################################

    def test_sections_are_counted_by_operation(self) -> 'None':

        # Nine operations on two paths are more than one group holds
        paths = ['/api/billing/invoices'] * 5 + ['/api/billing/customers/{id}'] * 4
        tags = get_tags(paths)

        self.assertEqual(tags['/api/billing/invoices'], 'Billing / Invoices')
        self.assertEqual(tags['/api/billing/customers/{id}'], 'Billing / Customers')

# ################################################################################################################################

    def test_roles_and_actions_name_no_group(self) -> 'None':

        paths = _make_large_section([
            '/api/healthcare/channel.billing.send-invoice',
            '/api/healthcare/adapters/lab/get-results',
            '/api/healthcare/core.wards.list-beds',
        ])
        tags = get_tags(paths)

        self.assertEqual(tags['/api/healthcare/channel.billing.send-invoice'], 'Healthcare / Billing')
        self.assertEqual(tags['/api/healthcare/adapters/lab/get-results'], 'Healthcare / Lab')
        self.assertEqual(tags['/api/healthcare/core.wards.list-beds'], 'Healthcare / Wards')

# ################################################################################################################################

    def test_a_compound_name_split_across_segments_is_one_group(self) -> 'None':

        paths = _make_large_section(['/api/healthcare/referral/letters', '/api/healthcare/referral-letters/{id}'])
        tags = get_tags(paths)

        self.assertEqual(tags['/api/healthcare/referral/letters'], 'Healthcare / Referral letters')
        self.assertEqual(tags['/api/healthcare/referral-letters/{id}'], 'Healthcare / Referral letters')

# ################################################################################################################################

    def test_a_path_with_only_an_action_joins_the_group_of_its_opaque_identifier(self) -> 'None':

        paths = _make_large_section(['/healthcare/4ed32368/orders', '/healthcare/4ed32368/create', '/healthcare/submit'])
        tags = get_tags(paths)

        self.assertEqual(tags['/healthcare/4ed32368/create'], 'Healthcare / Orders')
        self.assertEqual(tags['/healthcare/submit'], 'Healthcare / General')

# ################################################################################################################################

    def test_operation_ids_are_built_from_the_method_and_the_path(self) -> 'None':

        self.assertEqual(self.patients['operationId'], 'get_api_healthcare_v1_patients_patient_id')
        self.assertEqual(self.appointments['operationId'], 'post_api_healthcare_appointments')

# ################################################################################################################################

    def test_the_summary_is_the_first_sentence_of_the_docstring(self) -> 'None':

        self.assertEqual(self.patients['summary'], 'Returns a patient, e.g. by a medical record number.')
        self.assertEqual(self.patients['description'], _docstring_patients)

# ################################################################################################################################

    def test_an_operation_without_a_docstring_has_no_summary(self) -> 'None':

        result = get_summary('')
        self.assertEqual(result, '')

# ################################################################################################################################

    def test_opaque_identifiers_and_dotted_versions_name_no_resource(self) -> 'None':

        self.assertEqual(get_group_segments('/4ed32368/taxi-queue'), ['taxi-queue'])
        self.assertEqual(get_group_segments('/72203c78-96e1-4e5a-bb8c-a17ff64fd26a/orders'), ['orders'])
        self.assertEqual(get_group_segments('/staff/1.0/info/{user_id}'), ['staff', 'info'])
        self.assertEqual(get_group_segments('/api/v2.0/cafe/menu'), ['cafe', 'menu'])

# ################################################################################################################################

    def test_dotted_names_are_one_segment_per_part(self) -> 'None':

        result = get_group_segments('/api/billing.invoices.reminders')
        self.assertEqual(result, ['billing', 'invoices', 'reminders'])

# ################################################################################################################################

    def test_a_path_without_literal_segments_has_the_default_group(self) -> 'None':

        tags = get_tags(['/{item_id}'])

        self.assertEqual(tags['/{item_id}'], 'General')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
