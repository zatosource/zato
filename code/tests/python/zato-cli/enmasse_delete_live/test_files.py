# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NOT_FOUND

# Zato
from zato.cli.enmasse.importer.delete_targets import Section_Alert_Rules, Should_Delete_Key
from zato.common.audit_log.common import AuditEvent

# Live environment
from live_containers.ready import wait_until
from live_environment.audit import events

# Zato - the suite's own parts
from _definitions import basic_auth, deletion_file, group, marked, Ping_Service, Prefix, rest_channel
from _support import is_listed, is_served, ModuleCtx as SupportCtx, Pickup, Runtime, url_status

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.quickstart import ZatoEnvironment
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # What the deletion pipeline logs for an object the file marks that does not exist, and the summary it ends with
    Nothing_To_Delete = 'nothing to delete'
    Zero_Deletions    = "Processed deletions: {'channel_rest': 0}"

    # What the pipeline logs for each object it deleted, and the order the sections of the combined file are deleted in
    Deleted        = 'Deleted `{}`'
    Combined_Order = ('channel_rest', 'channel_soap', 'groups', 'security')

    # The refusal messages of the three files that are never imported
    Refused_Conflict   = 'both marked'
    Refused_Reference  = 'marks `should_delete`'
    Refused_Alert_Rule = f'Section `{Section_Alert_Rules}` does not support `{Should_Delete_Key}`'

# ################################################################################################################################
# ################################################################################################################################

def _names(prefix:'str', *parts:'str') -> 'anydict':
    """ The names of the objects of one test, each under the test's own prefix.
    """
    out = {part: f'{Prefix}{prefix}.{part}' for part in parts}
    return out

# ################################################################################################################################

def _url_path(prefix:'str', part:'str') -> 'str':
    """ The URL path of one channel of a test.
    """
    out = '/' + Prefix.replace('.', '/') + f'{prefix}/{part}'
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_mcp_gateway(
    environment:'ZatoEnvironment',
    client:'AdminClient',
    pickup:'Pickup',
    runtime:'Runtime',
    ) -> 'None':
    """ A deleted MCP gateway answers 404 on its URL and its deletion is in the audit trail.
    """
    names = _names('mcp', 'gateway')
    url_path = _url_path('mcp', 'gateway')

    config = {
        'mcp_gateway': [{
            'name': names['gateway'],
            'is_active': True,
            'url_path': url_path,
            'services': [Ping_Service],
        }],
    }

    # The gateway answers on its URL ..
    log = pickup.place('mcp-create', config)
    assert SupportCtx.Import_OK in log, log
    assert url_status(environment, url_path) != NOT_FOUND

    # .. it is deleted ..
    log = pickup.place('mcp-delete', deletion_file('mcp_gateway', names['gateway']))
    assert SupportCtx.Import_OK in log, log

    # .. its URL is gone ..
    assert url_status(environment, url_path) == NOT_FOUND
    assert not is_listed(client, runtime, 'mcp_gateway', names['gateway'])

    # .. and the audit trail has the deletion.
    def _has_deletion_event() -> 'bool':
        found = events(environment.audit_db_path, event_type=AuditEvent.Config_Deleted, object_name=names['gateway'])
        out = len(found) == 1
        return out

    wait_until(_has_deletion_event, f'the deletion event of {names["gateway"]}')

# ################################################################################################################################

def test_combined_file(client:'AdminClient', pickup:'Pickup', runtime:'Runtime') -> 'None':
    """ One file deletes a security definition, the channels that use it and a group, dependents first.
    """
    names = _names('combined', 'security', 'rest', 'soap', 'group')

    config = {
        'security': [basic_auth(names['security'], 'enmasse.delete.live.combined')],
        'groups': [group(names['group'], [names['security']])],
        'channel_rest': [rest_channel(names['rest'], _url_path('combined', 'rest'), security=names['security'])],
        'channel_soap': [{
            'name': names['soap'],
            'service': Ping_Service,
            'url_path': _url_path('combined', 'soap'),
            'security': names['security'],
            'soap_action': 'urn:enmasse:delete:live:combined',
            'soap_version': '1.1',
        }],
    }

    log = pickup.place('combined-create', config)
    assert SupportCtx.Import_OK in log, log

    # Everything goes in one file ..
    config = {
        'security':     [marked('security', names['security'])],
        'groups':       [marked('groups', names['group'])],
        'channel_rest': [marked('channel_rest', names['rest'])],
        'channel_soap': [marked('channel_soap', names['soap'])],
    }

    log = pickup.place('combined-delete', config)
    assert SupportCtx.Import_OK in log, log

    # .. the channels go before the group and the group before the security definition ..
    positions = [log.index(ModuleCtx.Deleted.format(section)) for section in ModuleCtx.Combined_Order]
    assert positions == sorted(positions), log

    # .. and nothing is left.
    assert not is_listed(client, runtime, 'channel_rest', names['rest'])
    assert not is_listed(client, runtime, 'channel_soap', names['soap'])
    assert not is_listed(client, runtime, 'groups', names['group'])
    assert not is_listed(client, runtime, 'security', names['security'])

# ################################################################################################################################

def test_idempotency(client:'AdminClient', pickup:'Pickup', runtime:'Runtime') -> 'None':
    """ A deletion file placed a second time is imported without error and reports zero deletions.
    """
    names = _names('idempotency', 'channel')
    config = {'channel_rest': [rest_channel(names['channel'], _url_path('idempotency', 'channel'))]}

    log = pickup.place('idempotency-create', config)
    assert SupportCtx.Import_OK in log, log

    # The first deletion removes the channel ..
    log = pickup.place('idempotency-delete', deletion_file('channel_rest', names['channel']))
    assert SupportCtx.Import_OK in log, log
    assert not is_listed(client, runtime, 'channel_rest', names['channel'])

    # .. and the second one has nothing to remove.
    log = pickup.place('idempotency-delete-again', deletion_file('channel_rest', names['channel']))
    assert SupportCtx.Import_OK in log, log
    assert ModuleCtx.Nothing_To_Delete in log, log
    assert ModuleCtx.Zero_Deletions in log, log

# ################################################################################################################################

def test_refused_files(client:'AdminClient', pickup:'Pickup', runtime:'Runtime') -> 'None':
    """ A conflict, a reference to a deleted object and a marker in alert rules are each refused with nothing written,
    the plain object each file also defines included.
    """
    names = _names('refused', 'conflict', 'security', 'referrer', 'witness')

    # The same channel both defined and marked ..
    config = {
        'channel_rest': [
            rest_channel(names['conflict'], _url_path('refused', 'conflict')),
            marked('channel_rest', names['conflict']),
            rest_channel(names['witness'], _url_path('refused', 'witness')),
        ],
    }

    log = pickup.place('refused-conflict', config)
    assert SupportCtx.Import_Error in log, log
    assert ModuleCtx.Refused_Conflict in log, log
    assert not is_listed(client, runtime, 'channel_rest', names['conflict'])
    assert not is_listed(client, runtime, 'channel_rest', names['witness'])

    # .. a channel referring to a security definition the file deletes ..
    config = {
        'security': [marked('security', names['security'])],
        'channel_rest': [
            rest_channel(names['referrer'], _url_path('refused', 'referrer'), security=names['security']),
            rest_channel(names['witness'], _url_path('refused', 'witness')),
        ],
    }

    log = pickup.place('refused-reference', config)
    assert SupportCtx.Import_Error in log, log
    assert ModuleCtx.Refused_Reference in log, log
    assert not is_listed(client, runtime, 'channel_rest', names['referrer'])
    assert not is_listed(client, runtime, 'channel_rest', names['witness'])

    # .. and the marker in a section whose items are not objects.
    config = {
        Section_Alert_Rules: [{'type': 'rest', 'is_active': True, Should_Delete_Key: True}],
        'channel_rest': [rest_channel(names['witness'], _url_path('refused', 'witness'))],
    }

    log = pickup.place('refused-alert-rules', config)
    assert SupportCtx.Import_Error in log, log
    assert ModuleCtx.Refused_Alert_Rule in log, log
    assert not is_listed(client, runtime, 'channel_rest', names['witness'])

# ################################################################################################################################

def test_replacement_under_a_new_name(
    environment:'ZatoEnvironment',
    client:'AdminClient',
    pickup:'Pickup',
    runtime:'Runtime',
    ) -> 'None':
    """ One file deletes a REST channel and creates another under a new name on the same URL path, which serves.
    """
    names = _names('replacement', 'old', 'new')
    url_path = _url_path('replacement', 'channel')

    log = pickup.place('replacement-create', {'channel_rest': [rest_channel(names['old'], url_path)]})
    assert SupportCtx.Import_OK in log, log
    assert is_served(environment, url_path)

    # The old channel goes and the new one takes its URL path ..
    config = {
        'channel_rest': [
            marked('channel_rest', names['old']),
            rest_channel(names['new'], url_path),
        ],
    }

    log = pickup.place('replacement-delete-and-create', config)
    assert SupportCtx.Import_OK in log, log

    # .. and the new one serves.
    assert not is_listed(client, runtime, 'channel_rest', names['old'])
    assert is_listed(client, runtime, 'channel_rest', names['new'])
    assert is_served(environment, url_path)

# ################################################################################################################################
# ################################################################################################################################
