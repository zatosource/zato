# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile

# PyYAML
from yaml import safe_load

# Zato
from zato.common.test import rand_string

# local
import _constants
import _enmasse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The object types one export of this test covers
_include_type = 'mcp_gateway,security,groups'

# ################################################################################################################################
# ################################################################################################################################

def _build_config(suffix:'str') -> 'stranydict':
    """ The import document of one round trip - a gateway with every optional field set
    and a minimal one next to it, with the security definition and group the full one uses.
    """

    security_name = f'test.llm.roundtrip.basic.{suffix}'
    group_name = f'llm.test-group-roundtrip.{suffix}'

    full_gateway = {
        'name': f'test.llm.roundtrip.full.{suffix}',
        'is_audit_log_active': True,
        'url_path': f'/mcp/llm/roundtrip-full-{suffix}',
        'services': [_constants.Service_Order_Status],
        'security_groups': [group_name],
        'skills': [_constants.Skill_House_Style],
        'validate_input': True,
        'allow_client_filters': True,
        'max_response_size': 2000,
        'size_cap_mode': 'block',
        'min_size_threshold': 100,
        'characters_per_token': 3.5,
        'safeguards_strip_nulls': True,
        'safeguards_collapse_whitespace': True,
        'safeguards_strip_base64': True,
        'safeguards_pii_enabled': True,
        'safeguards_pii_lands': [_constants.PII_Land_Main],
        'safeguards_pii_detectors': ['intl_ipv4'],
        'safeguards_pii_exclude': ['intl_email'],
        'safeguards_pii_validate': False,
        'safeguards_pii_stable_replacements': True,
        'safeguards_secrets_enabled': True,
        'safeguards_normalize_unicode': True,
        'safeguards_unicode_mode': 'reject',
        'safeguards_sanitize_markup': True,
        'safeguards_markup_mode': 'reject',
        'safeguards_url_policy_enabled': True,
        'safeguards_url_allow_list': [_constants.Safety_Allowed_Host],
        'safeguards_url_mode': 'neutralize',
    }

    minimal_gateway = {
        'name': f'test.llm.roundtrip.minimal.{suffix}',
        'url_path': f'/mcp/llm/roundtrip-minimal-{suffix}',
        'services': [_constants.Service_Order_Status],
    }

    out:'stranydict' = {
        'security': [
            {
                'name': security_name,
                'type': 'basic_auth',
                'username': f'test.llm.roundtrip.user.{suffix}',
                'password': 'test.llm.roundtrip.' + rand_string(),
            },
        ],
        'groups': [
            {'name': group_name, 'members': [security_name]},
        ],
        'mcp_gateway': [full_gateway, minimal_gateway],
    }

    return out

# ################################################################################################################################

def _read_test_gateways(export_path:'str', suffix:'str') -> 'anydict':
    """ Reads one exported file and returns this run's gateways keyed by name.
    """

    with open(export_path) as export_file:
        exported = safe_load(export_file.read())

    assert 'mcp_gateway' in exported, exported

    out:'anydict' = {}

    for gateway in exported['mcp_gateway']:
        if suffix in gateway['name']:
            out[gateway['name']] = gateway

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseRoundTrip:
    """ One full import-export-reimport cycle of MCP gateways - every optional field
    survives the round trip, defaults stay out of the export and a reimport
    of the export changes nothing.
    """

# ################################################################################################################################

    def test_import_export_reimport(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        suffix = rand_string()
        config = _build_config(suffix)

        temp_directory = tempfile.gettempdir()
        export_path = os.path.join(temp_directory, f'zato-mcp-roundtrip-export-{suffix}.yaml')
        second_export_path = os.path.join(temp_directory, f'zato-mcp-roundtrip-export-second-{suffix}.yaml')

        try:
            # One import creates everything the document names ..
            _enmasse.run_import(server_directory, config)

            # .. the export brings the gateways back out ..
            _enmasse.run_export(server_directory, export_path, _include_type)

            gateways_by_name = _read_test_gateways(export_path, suffix)

            gateway_count = len(gateways_by_name)
            assert gateway_count == 2, gateways_by_name

            full = gateways_by_name[f'test.llm.roundtrip.full.{suffix}']
            minimal = gateways_by_name[f'test.llm.roundtrip.minimal.{suffix}']

            # .. every non-default field of the full gateway survived the round trip ..
            assert full['url_path'] == f'/mcp/llm/roundtrip-full-{suffix}', full
            assert full['services'] == [_constants.Service_Order_Status], full
            assert full['is_audit_log_active'] is True, full
            assert full['skills'] == [_constants.Skill_House_Style], full
            assert full['validate_input'] is True, full
            assert full['allow_client_filters'] is True, full

            assert full['max_response_size'] == 2000, full
            assert full['size_cap_mode'] == 'block', full
            assert full['min_size_threshold'] == 100, full
            assert full['characters_per_token'] == 3.5, full

            assert full['safeguards_strip_nulls'] is True, full
            assert full['safeguards_collapse_whitespace'] is True, full
            assert full['safeguards_strip_base64'] is True, full

            assert full['safeguards_pii_enabled'] is True, full
            assert full['safeguards_pii_lands'] == [_constants.PII_Land_Main], full
            assert full['safeguards_pii_detectors'] == ['intl_ipv4'], full
            assert full['safeguards_pii_exclude'] == ['intl_email'], full
            assert full['safeguards_pii_stable_replacements'] is True, full
            assert full['safeguards_secrets_enabled'] is True, full

            # .. the explicit False against a True default survived, so a reimport cannot flip it back ..
            assert full['safeguards_pii_validate'] is False, full

            assert full['safeguards_normalize_unicode'] is True, full
            assert full['safeguards_unicode_mode'] == 'reject', full
            assert full['safeguards_sanitize_markup'] is True, full
            assert full['safeguards_markup_mode'] == 'reject', full
            assert full['safeguards_url_policy_enabled'] is True, full
            assert full['safeguards_url_allow_list'] == [_constants.Safety_Allowed_Host], full
            assert full['safeguards_url_mode'] == 'neutralize', full

            # .. the security group travels by name in both directions ..
            assert full['security_groups'] == [f'llm.test-group-roundtrip.{suffix}'], full

            # .. the minimal gateway keeps its defaults out of the export ..
            assert minimal['url_path'] == f'/mcp/llm/roundtrip-minimal-{suffix}', minimal
            assert minimal['services'] == [_constants.Service_Order_Status], minimal

            assert 'is_audit_log_active' not in minimal, minimal
            assert 'security_groups' not in minimal, minimal
            assert 'skills' not in minimal, minimal
            assert 'validate_input' not in minimal, minimal
            assert 'allow_client_filters' not in minimal, minimal
            assert 'max_response_size' not in minimal, minimal
            assert 'safeguards_pii_enabled' not in minimal, minimal
            assert 'safeguards_secrets_enabled' not in minimal, minimal
            assert 'safeguards_url_policy_enabled' not in minimal, minimal

            # .. the export is a clean input of its own ..
            _enmasse.run_import_file(server_directory, export_path)

            # .. and a second export matches the first, so nothing drifted.
            _enmasse.run_export(server_directory, second_export_path, _include_type)

            second_gateways_by_name = _read_test_gateways(second_export_path, suffix)
            assert second_gateways_by_name == gateways_by_name, second_gateways_by_name

        finally:
            if os.path.isfile(export_path):
                os.remove(export_path)

            if os.path.isfile(second_export_path):
                os.remove(second_export_path)

# ################################################################################################################################
# ################################################################################################################################
