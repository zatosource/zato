# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import subprocess
import sys
import tempfile

# requests
import requests

# PyYAML
from yaml import safe_dump

# Zato
from zato.common.test import rand_string

# Zato - test helpers - the wizard driver lives next to the tests
_this_directory = os.path.dirname(__file__)

if _this_directory not in sys.path:
    sys.path.insert(0, _this_directory)

import _mcp_tool_sources as tool_sources_page
import _mcp_wizard as wizard_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, anynone, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.mcp.tools.' + rand_string() + '.'

# How long the enmasse import subprocess may run
_Enmasse_Import_Timeout = 120

# ################################################################################################################################
# ################################################################################################################################

def _import_connections(server_dir:'str', config:'anydict') -> 'None':
    """ Imports the given enmasse document against the environment the tests run in.
    """

    yaml_text = safe_dump(config, default_flow_style=False, sort_keys=False)

    yaml_file = tempfile.NamedTemporaryFile(mode='w', suffix='-mcp-tools-card.yaml', delete=False)
    _ = yaml_file.write(yaml_text)
    yaml_file.close()

    zato_base_dir = os.environ['ZATO_TEST_BASE_DIR']
    zato_bin = os.path.join(zato_base_dir, 'code', 'bin', 'zato')

    enmasse_environ = os.environ.copy()
    _ = enmasse_environ.pop('COVERAGE_PROCESS_START', None)

    try:
        import_command = [zato_bin, 'enmasse', server_dir, '--verbose', '--import', '--input', yaml_file.name]
        result = subprocess.run(
            import_command, capture_output=True, text=True, timeout=_Enmasse_Import_Timeout, env=enmasse_environ)

        assert result.returncode == 0, \
            f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'

    finally:
        os.remove(yaml_file.name)

# ################################################################################################################################

def _get_gateway_from_odb(zato_dashboard:'anydict', gateway_name:'str') -> 'anydict':
    """ Reads one gateway's stored definition through the admin API.
    """

    server_port = zato_dashboard['server_port']

    api_url = f'http://127.0.0.1:{server_port}/zato/api/invoke/zato.generic.connection.get-list'
    api_auth = ('admin.invoke', zato_dashboard['password'])
    api_headers = {'Content-Type': 'application/json'}
    api_payload = json.dumps({'cluster_id': 1, 'type_': 'gateway-mcp'})

    response = requests.post(api_url, data=api_payload, headers=api_headers, auth=api_auth, timeout=10)
    assert response.status_code == 200, f'API call failed: {response.status_code} {response.text}'

    gateway_data:'anynone' = None

    for item in response.json():
        if item['name'] == gateway_name:
            gateway_data = item
            break

    assert gateway_data is not None, f'Gateway "{gateway_name}" not found in ODB'

    out = gateway_data
    return out

# ################################################################################################################################

def _run_tools_card_scenario(
    page:'Page',
    zato_dashboard:'anydict',
    *,
    scenario:'str',
    source_key:'str',
    config_key:'str',
    connection_names:'strlist',
    enmasse_config:'anydict',
    ) -> 'None':
    """ The one flow every connection source goes through - the connections come in
    through enmasse, a gateway is created with them picked through the Tools card's
    tree, the ODB holds them under the source's key and the edit wizard reopens
    with them assigned.
    """

    base_url = zato_dashboard['dashboard_url']
    server_dir = zato_dashboard['server_dir']

    gateway_name = _Test_Name_Prefix + scenario
    url_path = f'/mcp/test-tools/{scenario}/' + rand_string()

    # The connections must exist before the wizard builds its tree ..
    _import_connections(server_dir, enmasse_config)

    # .. open the create wizard and answer step 1 ..
    wizard_page.open_wizard_create(page, base_url)

    page.fill('#id_name', gateway_name)
    page.fill('#id_url_path', url_path)

    # .. the source's row is in the Tools card's tree and its items are on the picker ..
    wizard_page.open_picker_card(page, source_key)
    wizard_page.wait_for_available_badges(page, source_key, len(connection_names))

    # .. assign every connection by name ..
    for connection_name in connection_names:
        wizard_page.assign_badge(page, source_key, connection_name)

    # .. the source's tree row counts its picks ..
    count_text = tool_sources_page.get_tool_source_count(page, source_key)
    expected_count = str(len(connection_names))
    assert count_text == expected_count, f'Expected count "{expected_count}", got: "{count_text}"'

    # .. save from the review step ..
    wizard_page.save_create(page)

    # .. the ODB holds the allow list under the source's key ..
    gateway_data = _get_gateway_from_odb(zato_dashboard, gateway_name)

    stored_names = set(gateway_data[config_key])
    assert stored_names == set(connection_names), \
        f'Expected {connection_names} under {config_key}, got: {stored_names}'

    # .. and the edit wizard reopens with the picks assigned.
    wizard_page.open_wizard_edit(page, base_url, gateway_name)
    wizard_page.open_picker_card(page, source_key)

    assigned_names = set(wizard_page.get_assigned_badge_names(page, source_key))

    for connection_name in connection_names:
        assert connection_name in assigned_names, \
            f'Expected "{connection_name}" in assigned, got: {assigned_names}'

# ################################################################################################################################
# ################################################################################################################################

class TestToolsCardREST:
    """ The Tools card serves outgoing REST connections.
    """

    def test_rest_connections(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        connection_name = _Test_Name_Prefix + 'rest.billing'

        _run_tools_card_scenario(
            logged_in_page, zato_dashboard,
            scenario='rest',
            source_key='rest',
            config_key='rest_connections',
            connection_names=[connection_name],
            enmasse_config={
                'outgoing_rest': [
                    {
                        'name': connection_name,
                        'host': 'http://127.0.0.1:1',
                        'url_path': '/api/billing',
                    },
                ],
            })

# ################################################################################################################################
# ################################################################################################################################

class TestToolsCardSOAP:
    """ The Tools card serves outgoing SOAP connections.
    """

    def test_soap_connections(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        connection_name = _Test_Name_Prefix + 'soap.erp'

        _run_tools_card_scenario(
            logged_in_page, zato_dashboard,
            scenario='soap',
            source_key='soap',
            config_key='soap_connections',
            connection_names=[connection_name],
            enmasse_config={
                'outconn_soap': [
                    {
                        'name': connection_name,
                        'host': 'http://127.0.0.1:1',
                        'url_path': '/soap/erp',
                        'soap_action': 'urn:test:erp',
                        'soap_version': '1.1',
                    },
                ],
            })

# ################################################################################################################################
# ################################################################################################################################

class TestToolsCardSQL:
    """ The Tools card serves outgoing SQL connections.
    """

    def test_sql_connections(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        connection_name = _Test_Name_Prefix + 'sql.reporting'

        _run_tools_card_scenario(
            logged_in_page, zato_dashboard,
            scenario='sql',
            source_key='sql',
            config_key='sql_connections',
            connection_names=[connection_name],
            enmasse_config={
                'sql': [
                    {
                        'name': connection_name,
                        'type': 'mysql',
                        'host': '127.0.0.1',
                        'port': 3306,
                        'db_name': 'reports',
                        'username': 'reports_user',
                        'password': 'reports.' + rand_string(),
                    },
                ],
            })

# ################################################################################################################################
# ################################################################################################################################

class TestToolsCardOdoo:
    """ The Tools card serves outgoing Odoo connections.
    """

    def test_odoo_connections(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        connection_name = _Test_Name_Prefix + 'odoo.erp'

        _run_tools_card_scenario(
            logged_in_page, zato_dashboard,
            scenario='odoo',
            source_key='odoo',
            config_key='odoo_connections',
            connection_names=[connection_name],
            enmasse_config={
                'odoo': [
                    {
                        'name': connection_name,
                        'host': '127.0.0.1',
                        'user': 'odoo_user',
                        'database': 'production',
                        'password': 'odoo.' + rand_string(),
                    },
                ],
            })

# ################################################################################################################################
# ################################################################################################################################

class TestToolsCardSAP:
    """ The Tools card serves SAP connections.
    """

    def test_sap_connections(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        connection_name = _Test_Name_Prefix + 'sap.erp'

        _run_tools_card_scenario(
            logged_in_page, zato_dashboard,
            scenario='sap',
            source_key='sap',
            config_key='sap_connections',
            connection_names=[connection_name],
            enmasse_config={
                'sap': [
                    {
                        'name': connection_name,
                        'address': 'http://127.0.0.1:1/odata',
                        'username': 'sap_user',
                    },
                ],
            })

# ################################################################################################################################
# ################################################################################################################################

class TestToolsCardConfluence:
    """ The Tools card serves Confluence connections.
    """

    def test_confluence_connections(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        connection_name = _Test_Name_Prefix + 'confluence.wiki'

        _run_tools_card_scenario(
            logged_in_page, zato_dashboard,
            scenario='confluence',
            source_key='confluence',
            config_key='confluence_connections',
            connection_names=[connection_name],
            enmasse_config={
                'confluence': [
                    {
                        'name': connection_name,
                        'address': 'https://example.atlassian.net',
                        'username': 'wiki_user@example.com',
                    },
                ],
            })

# ################################################################################################################################
# ################################################################################################################################

class TestToolsCardMicrosoft365:
    """ The Tools card serves Microsoft 365 connections.
    """

    def test_microsoft_365_connections(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        connection_name = _Test_Name_Prefix + 'm365.main'

        _run_tools_card_scenario(
            logged_in_page, zato_dashboard,
            scenario='microsoft-365',
            source_key='microsoft_365',
            config_key='microsoft_365_connections',
            connection_names=[connection_name],
            enmasse_config={
                'microsoft_cloud': [
                    {
                        'name': connection_name,
                        'client_id': 'test-client-id',
                        'tenant_id': 'test-tenant-id',
                        'secret_value': 'm365.' + rand_string(),
                    },
                ],
            })

# ################################################################################################################################
# ################################################################################################################################

class TestToolsCardMicrosoftFabric:
    """ The Tools card serves Microsoft Fabric connections.
    """

    def test_microsoft_fabric_connections(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        connection_name = _Test_Name_Prefix + 'fabric.lake'

        _run_tools_card_scenario(
            logged_in_page, zato_dashboard,
            scenario='microsoft-fabric',
            source_key='microsoft_fabric',
            config_key='microsoft_fabric_connections',
            connection_names=[connection_name],
            enmasse_config={
                'microsoft_fabric': [
                    {
                        'name': connection_name,
                        'client_id': 'test-client-id',
                        'tenant_id': 'test-tenant-id',
                        'secret_value': 'fabric.' + rand_string(),
                    },
                ],
            })

# ################################################################################################################################
# ################################################################################################################################

class TestToolsCardMicrosoftPowerAutomate:
    """ The Tools card serves Microsoft Power Automate connections.
    """

    def test_microsoft_power_automate_connections(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        connection_name = _Test_Name_Prefix + 'pa.flows'

        _run_tools_card_scenario(
            logged_in_page, zato_dashboard,
            scenario='microsoft-power-automate',
            source_key='microsoft_power_automate',
            config_key='microsoft_power_automate_connections',
            connection_names=[connection_name],
            enmasse_config={
                'microsoft_power_automate': [
                    {
                        'name': connection_name,
                        'client_id': 'test-client-id',
                        'tenant_id': 'test-tenant-id',
                        'environment_id': 'test-environment-id',
                        'secret_value': 'pa.' + rand_string(),
                    },
                ],
            })

# ################################################################################################################################
# ################################################################################################################################

class TestToolsCardMicrosoftTeams:
    """ The Tools card serves Microsoft Teams connections.
    """

    def test_microsoft_teams_connections(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        connection_name = _Test_Name_Prefix + 'teams.chat'

        _run_tools_card_scenario(
            logged_in_page, zato_dashboard,
            scenario='microsoft-teams',
            source_key='microsoft_teams',
            config_key='microsoft_teams_connections',
            connection_names=[connection_name],
            enmasse_config={
                'microsoft_teams': [
                    {
                        'name': connection_name,
                        'client_id': 'test-client-id',
                        'tenant_id': 'test-tenant-id',
                        'secret_value': 'teams.' + rand_string(),
                    },
                ],
            })

# ################################################################################################################################
# ################################################################################################################################

class TestToolsCardElasticsearch:
    """ The Tools card serves Elasticsearch connections.
    """

    def test_es_connections(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        connection_name = _Test_Name_Prefix + 'es.search'

        _run_tools_card_scenario(
            logged_in_page, zato_dashboard,
            scenario='es',
            source_key='es',
            config_key='es_connections',
            connection_names=[connection_name],
            enmasse_config={
                'elastic_search': [
                    {
                        'name': connection_name,
                        'address_list': 'http://127.0.0.1:9200',
                    },
                ],
            })

# ################################################################################################################################
# ################################################################################################################################

class TestToolsCardMixedSources:
    """ One gateway holds picks from more than one source at once.
    """

    def test_rest_and_sql_together(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_dir = zato_dashboard['server_dir']

        rest_name = _Test_Name_Prefix + 'mixed.rest'
        sql_name = _Test_Name_Prefix + 'mixed.sql'

        gateway_name = _Test_Name_Prefix + 'mixed'
        url_path = '/mcp/test-tools/mixed/' + rand_string()

        # Both connections come in through one import ..
        _import_connections(server_dir, {
            'outgoing_rest': [
                {
                    'name': rest_name,
                    'host': 'http://127.0.0.1:1',
                    'url_path': '/api/mixed',
                },
            ],
            'sql': [
                {
                    'name': sql_name,
                    'type': 'mysql',
                    'host': '127.0.0.1',
                    'port': 3306,
                    'db_name': 'mixed',
                    'username': 'mixed_user',
                    'password': 'mixed.' + rand_string(),
                },
            ],
        })

        # .. the wizard takes one pick from each source ..
        wizard_page.open_wizard_create(page, base_url)

        page.fill('#id_name', gateway_name)
        page.fill('#id_url_path', url_path)

        wizard_page.assign_badge(page, 'rest', rest_name)
        wizard_page.assign_badge(page, 'sql', sql_name)

        # .. switching between the sources keeps each source's picks ..
        tool_sources_page.select_tool_source(page, 'rest')

        rest_assigned = wizard_page.get_assigned_badge_names(page, 'rest')
        assert rest_name in rest_assigned, rest_assigned

        # .. save from the review step ..
        wizard_page.save_create(page)

        # .. and the ODB holds each allow list under its own key.
        gateway_data = _get_gateway_from_odb(zato_dashboard, gateway_name)

        assert gateway_data['rest_connections'] == [rest_name], gateway_data
        assert gateway_data['sql_connections'] == [sql_name], gateway_data

# ################################################################################################################################
# ################################################################################################################################
