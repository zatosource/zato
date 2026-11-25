# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import tempfile

# Zato
from zato.common.crypto.api import CryptoManager

# Test utilities
from _test_util import get_client, read_server_log, wait_for

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

_conn_name = 'My GLPI'
_conn_name_wrong_token = 'My GLPI With a Wrong App Token'
_conn_type = 'outconn-glpi'

_get_ticket_service = 'demo.glpi.get-ticket'
_get_ticket_error_service = 'demo.glpi.get-ticket-error'
_create_ticket_service = 'demo.glpi.create-ticket'

# An ID the GLPI mode never assigns
_missing_ticket_id = 999_999

_enmasse_timeout = 180

_zato_bin = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

# ################################################################################################################################
# ################################################################################################################################

def _import_enmasse(zato_server:'stranydict', yaml_content:'str') -> 'None':
    """ Imports an enmasse file with the given content into the suite's server.
    """
    import_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml', mode='w')
    _ = import_file.write(yaml_content)
    import_file.close()

    command:'strlist' = [
        _zato_bin, 'enmasse', zato_server['server_directory'],
        '--import', '--input', import_file.name, '--missing-wait-time', '15', '--verbose',
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=_enmasse_timeout)
    finally:
        os.unlink(import_file.name)

    if result.returncode != 0:
        raise Exception(f'enmasse failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################

def _get_conn_id(zato_server:'stranydict', name:'str') -> 'int':
    """ Returns the ID of a GLPI definition by its name.
    """
    client = get_client(zato_server)
    data, _ = client.get_list('zato.generic.connection.get-list', type_=_conn_type)

    for item in data:
        if item['name'] == name:
            out = item['id']
            break
    else:
        raise Exception(f'Definition `{name}` not found')

    return out

# ################################################################################################################################

def _ping(zato_server:'stranydict', name:'str') -> 'stranydict':
    """ Pings a GLPI definition by its name and returns the response.
    """
    client = get_client(zato_server)
    conn_id = _get_conn_id(zato_server, name)

    out = client.invoke('zato.generic.connection.ping', {'id': conn_id})
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_glpi_connector_type_registered(zato_server:'stranydict') -> 'None':
    """ The GLPI connector module deployed at boot registered its connection type.
    """
    def _is_registered() -> 'bool':
        log_content = read_server_log(zato_server)
        out = f'Registered connector type `{_conn_type}`' in log_content
        return out

    _ = wait_for(_is_registered, f'connector type {_conn_type} to register')

# ################################################################################################################################

def test_glpi_definition_opens_session(zato_server:'stranydict') -> 'None':
    """ A definition imported with enmasse opens a GLPI session with the configured tokens and answers pings.
    """
    glpi_state = zato_server['glpi_state']
    init_count_before = glpi_state.init_count

    _import_enmasse(zato_server, f"""
custom_glpi:
  - name: {_conn_name}
    address: http://127.0.0.1:{zato_server['glpi_port']}
    app_token: {glpi_state.app_token}
    user_token: {glpi_state.user_token}
""")

    # The connection builds in the background, so keep pinging until it answers ..
    def _is_pinged() -> 'bool':
        response = _ping(zato_server, _conn_name)
        out = response['is_success'] is True
        return out

    _ = wait_for(_is_pinged, f'connection {_conn_name} to answer pings')

    # .. and the session it pings with was opened through initSession.
    assert glpi_state.init_count > init_count_before

# ################################################################################################################################

def test_glpi_wrong_app_token_fails_ping(zato_server:'stranydict') -> 'None':
    """ A definition with an app token GLPI does not accept fails its ping with GLPI's error code.
    """
    glpi_state = zato_server['glpi_state']
    wrong_app_token = 'glpi.app.wrong.' + CryptoManager.generate_hex_string()

    _import_enmasse(zato_server, f"""
custom_glpi:
  - name: {_conn_name_wrong_token}
    address: http://127.0.0.1:{zato_server['glpi_port']}
    app_token: {wrong_app_token}
    user_token: {glpi_state.user_token}
""")

    def _is_rejected() -> 'bool':
        response = _ping(zato_server, _conn_name_wrong_token)
        out = response['is_success'] is False and 'ERROR_WRONG_APP_TOKEN_PARAMETER' in response['info']
        return out

    _ = wait_for(_is_rejected, f'connection {_conn_name_wrong_token} to be rejected')

# ################################################################################################################################

def test_glpi_get_ticket(zato_server:'stranydict') -> 'None':
    """ A service reads a ticket from GLPI, and a ticket GLPI does not have makes the service fail.
    """
    glpi_state = zato_server['glpi_state']
    client = get_client(zato_server)

    ticket_id = glpi_state.add_ticket({'name': 'Printer offline', 'content': 'The printer on floor 3 is offline.'})

    # An existing ticket is returned with its fields ..
    response = client.invoke(_get_ticket_service, {'ticket_id': ticket_id})

    assert response['id'] == ticket_id
    assert response['name'] == 'Printer offline'
    assert response['content'] == 'The printer on floor 3 is offline.'

    # .. while a missing one makes the connector raise an exception with GLPI's error code.
    response = client.invoke(_get_ticket_error_service, {'ticket_id': _missing_ticket_id})

    assert response['error'] is not None, 'The connector was expected to raise for a missing ticket'
    assert 'ERROR_ITEM_NOT_FOUND' in response['error'], response['error']

# ################################################################################################################################

def test_glpi_create_ticket(zato_server:'stranydict') -> 'None':
    """ A service creates a ticket in GLPI and returns the ID GLPI assigned to it.
    """
    glpi_state = zato_server['glpi_state']
    client = get_client(zato_server)

    response = client.invoke(_create_ticket_service, {'name': 'New laptop', 'content': 'A laptop for a new hire.'})
    ticket_id = response['ticket_id']

    ticket = glpi_state.tickets[ticket_id]
    assert ticket['name'] == 'New laptop'
    assert ticket['content'] == 'A laptop for a new hire.'

# ################################################################################################################################

def test_glpi_expired_session_is_renewed(zato_server:'stranydict') -> 'None':
    """ When GLPI rejects an expired session, the connector opens a new one and the call is retried.
    """
    glpi_state = zato_server['glpi_state']
    client = get_client(zato_server)

    ticket_id = glpi_state.add_ticket({'name': 'VPN access', 'content': 'VPN access for a contractor.'})

    # Every open session becomes invalid ..
    init_count_before = glpi_state.init_count
    glpi_state.end_sessions()

    # .. the call still succeeds ..
    response = client.invoke(_get_ticket_service, {'ticket_id': ticket_id})
    assert response['name'] == 'VPN access'

    # .. because a new session was opened through refresh_credentials.
    assert glpi_state.init_count > init_count_before

    log_content = read_server_log(zato_server)
    assert f'GLPI session renewed for `{_conn_name}`' in log_content

# ################################################################################################################################

def test_glpi_delete_definition_kills_session(zato_server:'stranydict') -> 'None':
    """ Deleting the definitions with enmasse closes the open GLPI session through killSession.
    """
    glpi_state = zato_server['glpi_state']
    kill_count_before = glpi_state.kill_count

    _import_enmasse(zato_server, f"""
custom_glpi:
  - name: {_conn_name}
    should_delete: true
  - name: {_conn_name_wrong_token}
    should_delete: true
""")

    def _is_killed() -> 'bool':
        out = glpi_state.kill_count > kill_count_before
        return out

    _ = wait_for(_is_killed, f'the session of {_conn_name} to be closed')

# ################################################################################################################################
# ################################################################################################################################
