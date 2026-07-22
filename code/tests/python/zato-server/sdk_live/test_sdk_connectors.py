# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import subprocess
import tempfile
import time
from base64 import b64encode

# PyYAML
import yaml

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.client import AdminClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.sdk_live')

# ################################################################################################################################
# ################################################################################################################################

_conn_name = 'My CRM'
_conn_type = 'outconn-crm'
_service_name = 'demo.crm.get-customer'
_customer_id = 'CUST-1001'

_api_key = 'api.key.' + CryptoManager.generate_hex_string()
_api_key_after_edit = 'api.key.' + CryptoManager.generate_hex_string()
_api_key_enmasse = 'api.key.' + CryptoManager.generate_hex_string()

_wait_timeout = 60
_poll_interval = 0.5
_enmasse_timeout = 180

_zato_bin = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

# ################################################################################################################################
# ################################################################################################################################

class _TestState:
    """ State shared by the tests, which run in the order they are defined in.
    """
    conn_id = 0

# ################################################################################################################################
# ################################################################################################################################

def _get_client(zato_server:'stranydict') -> 'AdminClient':
    out = AdminClient(zato_server['base_url'], zato_server['invoke_password'])
    return out

# ################################################################################################################################

def _read_server_log(zato_server:'stranydict') -> 'str':
    log_path = os.path.join(zato_server['server_directory'], 'logs', 'server.log')

    with open(log_path, 'r') as log_file:
        out = log_file.read()

    return out

# ################################################################################################################################

def _wait_for(condition:'callable_', description:'str', timeout:'int'=_wait_timeout) -> 'any_':
    """ Polls the condition until it returns a truthy value or the timeout passes.
    """
    deadline = time.monotonic() + timeout
    last_error = ''

    while time.monotonic() < deadline:

        try:
            result = condition()
        except Exception as e:
            last_error = str(e)
        else:
            if result:
                return result

        time.sleep(_poll_interval)

    raise Exception(f'Timed out waiting for {description} after {timeout}s, last error: {last_error}')

# ################################################################################################################################
# ################################################################################################################################

def test_connector_type_registered(zato_server:'stranydict') -> 'None':
    """ The connector module deployed at boot registered its connection type.
    """
    def _is_registered() -> 'bool':
        log_content = _read_server_log(zato_server)
        out = f'Registered connector type `{_conn_type}`' in log_content
        return out

    _ = _wait_for(_is_registered, f'connector type {_conn_type} to register')

# ################################################################################################################################

def test_create_definition(zato_server:'stranydict') -> 'None':
    """ A definition of the new type can be created and pinged.
    """
    client = _get_client(zato_server)

    response = client.create('zato.generic.connection.create',
        cluster_id=1,
        name=_conn_name,
        type_=_conn_type,
        is_active=True,
        is_internal=False,
        is_channel=False,
        is_outconn=True,
        host='127.0.0.1',
        port=zato_server['echo_port'],
        api_key=_api_key,
        pool_size=1,
    )

    _TestState.conn_id = response['id']
    assert _TestState.conn_id

    # The connection builds in the background, so keep pinging until it answers.
    def _ping() -> 'bool':
        ping_response = client.invoke('zato.generic.connection.ping', {'id': _TestState.conn_id})
        out = ping_response['is_success'] is True
        return out

    _ = _wait_for(_ping, f'connection {_conn_name} to answer pings')

# ################################################################################################################################

def test_invoke_from_service(zato_server:'stranydict') -> 'None':
    """ A service reaches the connection through self.out and gets the gateway's response back.
    """
    client = _get_client(zato_server)

    response = client.invoke(_service_name, {'customer_id': _customer_id})
    assert response['response'] == f'{_api_key} get-customer {_customer_id}'

# ################################################################################################################################

def test_secrets_never_returned(zato_server:'stranydict') -> 'None':
    """ Secret fields declared by the connector are not returned in listings.
    """
    client = _get_client(zato_server)

    data, _ = client.get_list('zato.generic.connection.get-list', type_=_conn_type, cluster_id=1)
    assert len(data) == 1

    item = data[0]
    assert item['name'] == _conn_name
    assert 'api_key' not in item

# ################################################################################################################################

def test_edit_definition(zato_server:'stranydict') -> 'None':
    """ Editing the definition stops the old client and the new one uses the new configuration.
    """
    client = _get_client(zato_server)

    _ = client.edit('zato.generic.connection.edit',
        id=_TestState.conn_id,
        cluster_id=1,
        name=_conn_name,
        type_=_conn_type,
        is_active=True,
        is_internal=False,
        is_channel=False,
        is_outconn=True,
        host='127.0.0.1',
        port=zato_server['echo_port'],
        api_key=_api_key_after_edit,
        pool_size=1,
    )

    # The new client sends the new key once the rebuilt connection is in place ..
    def _uses_new_key() -> 'bool':
        response = client.invoke(_service_name, {'customer_id': _customer_id})
        out = response['response'] == f'{_api_key_after_edit} get-customer {_customer_id}'
        return out

    _ = _wait_for(_uses_new_key, 'the edited connection to use the new key')

    # .. and the old client was stopped through the connector's on_stop hook.
    log_content = _read_server_log(zato_server)
    assert f'CRM client for `{_conn_name}` stopped' in log_content

# ################################################################################################################################

def test_redeploy_module_keeps_definitions(zato_server:'stranydict') -> 'None':
    """ Redeploying the connector module updates the registered type and live definitions survive.
    """
    client = _get_client(zato_server)

    # Read the module as it was deployed ..
    deployed_path = zato_server['connector_deployed_path']

    with open(deployed_path, 'rb') as module_file:
        module_content = module_file.read()

    # .. and deploy it once again through the same service that handles hot-deployment.
    payload = b64encode(module_content).decode('utf8')

    _ = client.invoke('zato.hot-deploy.create', {
        'payload': payload,
        'payload_name': deployed_path,
    })

    # The type was updated rather than registered anew ..
    def _is_updated() -> 'bool':
        log_content = _read_server_log(zato_server)
        out = f'Updated connector type `{_conn_type}`' in log_content
        return out

    _ = _wait_for(_is_updated, f'connector type {_conn_type} to be updated')

    # .. and the definition kept working across the redeployment.
    response = client.invoke(_service_name, {'customer_id': _customer_id})
    assert response['response'] == f'{_api_key_after_edit} get-customer {_customer_id}'

# ################################################################################################################################

def test_server_restart_restores_connections(zato_server:'stranydict') -> 'None':
    """ After a restart, registering the connector type starts the definitions stored in the database.
    """
    # The helper comes through the fixture - importing it from conftest would create
    # a second module instance with its own, disconnected session state.
    zato_server['restart_zato_server'](zato_server)

    client = _get_client(zato_server)

    # The definition could not start during the boot scan of stored connections because the type
    # was not registered yet - it started when the connector module deployed and registered the type.
    def _answers() -> 'bool':
        response = client.invoke(_service_name, {'customer_id': _customer_id})
        out = response['response'] == f'{_api_key_after_edit} get-customer {_customer_id}'
        return out

    _ = _wait_for(_answers, 'the restored connection to answer')

# ################################################################################################################################

def test_delete_definition(zato_server:'stranydict') -> 'None':
    """ Deleting the definition makes it unavailable to services.
    """
    client = _get_client(zato_server)

    _ = client.delete('zato.generic.connection.delete', id=_TestState.conn_id)

    # The definition disappears from the container, so invoking the service starts to fail.
    def _is_gone() -> 'bool':
        try:
            _ = client.invoke(_service_name, {'customer_id': _customer_id})
        except Exception:
            return True
        else:
            return False

    _ = _wait_for(_is_gone, f'connection {_conn_name} to be deleted')

# ################################################################################################################################

def _run_enmasse(arguments:'list', zato_server:'stranydict') -> 'None':
    """ Runs the enmasse command against the suite's server, raising an exception if it fails.
    """
    command = [_zato_bin, 'enmasse', zato_server['server_directory']] + arguments + ['--verbose']

    result = subprocess.run(command, capture_output=True, text=True, timeout=_enmasse_timeout)
    if result.returncode != 0:
        raise Exception(f'enmasse failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################

def test_enmasse_import_starts_connection(zato_server:'stranydict') -> 'None':
    """ Importing a custom_crm definition with enmasse creates the connection on the live server
    and services can use it right away, with no restarts.
    """
    yaml_content = f"""
custom_crm:
  - name: {_conn_name}
    host: 127.0.0.1
    port: {zato_server['echo_port']}
    api_key: {_api_key_enmasse}
"""

    import_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml', mode='w')
    _ = import_file.write(yaml_content)
    import_file.close()

    try:
        # The import writes the definition to the database and reloads the server's configuration.
        _run_enmasse(['--import', '--input', import_file.name], zato_server)
    finally:
        os.unlink(import_file.name)

    # The service reaches the connection the import created, proving the whole chain works -
    # the YAML key became the connection type and the declared fields reached the connector.
    client = _get_client(zato_server)

    def _uses_enmasse_key() -> 'bool':
        response = client.invoke(_service_name, {'customer_id': _customer_id})
        out = response['response'] == f'{_api_key_enmasse} get-customer {_customer_id}'
        return out

    _ = _wait_for(_uses_enmasse_key, 'the enmasse-imported connection to answer')

# ################################################################################################################################

def test_enmasse_export_round_trip(zato_server:'stranydict') -> 'None':
    """ Exporting with enmasse returns the definition under its custom_crm key with the fields intact.
    """
    export_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
    export_file.close()

    try:
        _run_enmasse(['--export', '--output', export_file.name, '--include-type', 'custom_crm'], zato_server)

        with open(export_file.name, 'r') as f:
            exported = yaml.safe_load(f.read())
    finally:
        os.unlink(export_file.name)

    # The definition is under its own top-level key ..
    items = exported['custom_crm']
    assert len(items) == 1

    # .. and the fields the YAML carried on import survived the round trip.
    item = items[0]
    assert item['name'] == _conn_name
    assert item['host'] == '127.0.0.1'
    assert item['port'] == zato_server['echo_port']
    assert item['api_key'] == _api_key_enmasse

# ################################################################################################################################
# ################################################################################################################################
