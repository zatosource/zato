# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager
from typing import NamedTuple

# Zato
from live_sql.asserts import assert_mysql_connection_encrypted as assert_mysql_engine_encrypted, \
    assert_postgresql_connection_encrypted as assert_postgresql_engine_encrypted
from live_sql.env import database_env
from zato.common.api import CONNECTION, GENERIC, URL_TYPE
from zato.common.defaults import default_cluster_id
from zato.common.ext.bunch import Bunch
from zato.common.ext_db.api import ModuleCtx as ExtDBCtx, ensure_security_copy, ensure_service_copy, get_ext_db_engine, \
    get_ext_db_session, get_ext_http_soap_list, merge_ext_channel_items, merge_ext_config_entries
from zato.common.json_internal import dumps
from zato.common.odb.model import Cluster, GenericConn, GenericConnSec, HTTPSOAP, SecurityBase, Service
from zato.common.odb.query.generic import connection_list
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anydict, anylist, stranydict

    any_ = any_
    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The prefix all the external database environment variables share
_env_prefix = 'Zato_Ext_DB_'

# The names the test objects are created under
_as2_channel_name = 'as2.orders.inbound'
_as4_channel_name = 'as4.invoices.inbound'
_as4_outconn_name = 'as4.invoices.outbound'
_as2_outconn_name = 'as2.orders.outbound'

# The service the test channels route their messages to
_channel_service_name = 'orders.process-incoming'
_channel_service_impl = 'orders.service.ProcessIncoming'

# The URL path the AS4 channel is edited to point at
_edited_url_path = '/as4/invoices/inbound/v2'

# ################################################################################################################################
# ################################################################################################################################

class _SecurityDefinition(NamedTuple):
    id: int
    name: str
    username: str
    password: str
    password_type: str
    is_active: bool
    sec_type: str

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def ext_db_env(details:'stranydict') -> 'envgen':
    """ Points the Zato_Ext_DB_* variables at one backend for the duration of a test.
    """
    with database_env(_env_prefix, details):
        yield

# ################################################################################################################################

def _clean_up_tables() -> 'None':
    """ Empties all the AS2/AS4 tables so the scenario always starts from scratch -
    containers can be reused between test runs.
    """
    session = get_ext_db_session()

    # Children go first so no foreign key constraint is violated
    try:
        _ = session.query(GenericConnSec).delete()
        _ = session.query(GenericConn).delete()
        _ = session.query(HTTPSOAP).delete()
        _ = session.query(SecurityBase).delete()
        _ = session.query(Service).delete()
        session.commit()
    finally:
        session.close()

# ################################################################################################################################

def _insert_test_objects() -> 'None':
    """ Inserts the AS2/AS4 configuration objects the scenario works with -
    two channels, an AS4 outgoing connection and an AS2 outgoing connection.
    """
    session = get_ext_db_session()

    try:

        # The channels need a service row as their foreign key target ..
        channel_service = ensure_service_copy(session, _channel_service_name, _channel_service_impl, default_cluster_id)

        # .. everything belongs to the seeded cluster row - the relationship object is needed
        # .. because the model's __init__ sets the relationship attributes explicitly,
        # .. which makes SQLAlchemy ignore plain assignments to the foreign key ids ..
        cluster = session.query(Cluster).filter(Cluster.id == default_cluster_id).one()

        # .. an AS2 channel ..
        as2_channel = HTTPSOAP()
        as2_channel.name = _as2_channel_name
        as2_channel.is_active = True
        as2_channel.is_internal = False
        as2_channel.connection = CONNECTION.CHANNEL
        as2_channel.transport = URL_TYPE.AS2
        as2_channel.url_path = '/as2/orders/inbound'
        as2_channel.soap_action = ''
        as2_channel.service = channel_service
        as2_channel.cluster = cluster
        as2_channel.opaque1 = dumps({'as2_local_id': 'zato-station', 'as2_partner_id': 'supplier-station'})

        # .. an AS4 channel ..
        as4_channel = HTTPSOAP()
        as4_channel.name = _as4_channel_name
        as4_channel.is_active = True
        as4_channel.is_internal = False
        as4_channel.connection = CONNECTION.CHANNEL
        as4_channel.transport = URL_TYPE.AS4
        as4_channel.url_path = '/as4/invoices/inbound'
        as4_channel.soap_action = ''
        as4_channel.service = channel_service
        as4_channel.cluster = cluster
        as4_channel.opaque1 = dumps({'as4_from_party_id': 'zato-station', 'as4_to_party_id': 'billing-station'})

        # .. an AS4 outgoing connection ..
        as4_outconn = HTTPSOAP()
        as4_outconn.name = _as4_outconn_name
        as4_outconn.is_active = True
        as4_outconn.is_internal = False
        as4_outconn.connection = CONNECTION.OUTGOING
        as4_outconn.transport = URL_TYPE.AS4
        as4_outconn.host = 'https://as4.billing-station.example.com'
        as4_outconn.url_path = '/as4/invoices/outbound'
        as4_outconn.soap_action = ''
        as4_outconn.cluster = cluster
        as4_outconn.opaque1 = dumps({'as4_from_party_id': 'zato-station', 'as4_to_party_id': 'billing-station'})

        # .. and an AS2 outgoing connection, which is a generic connection -
        # .. the model has no __init__ of its own so its attributes are typed
        # .. as columns and the instance needs a cast before they can be assigned to.
        as2_outconn = cast_('any_', GenericConn())
        as2_outconn.name = _as2_outconn_name
        as2_outconn.type_ = GENERIC.CONNECTION.TYPE.OUTCONN_AS2
        as2_outconn.is_active = True
        as2_outconn.is_internal = False
        as2_outconn.is_channel = False
        as2_outconn.is_outconn = True
        as2_outconn.address = 'https://as2.supplier-station.example.com/orders'
        as2_outconn.cluster_id = default_cluster_id
        as2_outconn.opaque1 = dumps({'as2_local_id': 'zato-station', 'as2_partner_id': 'supplier-station'})

        session.add(as2_channel)
        session.add(as4_channel)
        session.add(as4_outconn)
        session.add(as2_outconn)
        session.commit()

    finally:
        session.close()

# ################################################################################################################################

def _get_channel_by_name(name:'str') -> 'Bunch':
    """ Returns one channel from the external database by its name.
    """
    channels = get_ext_http_soap_list(default_cluster_id, CONNECTION.CHANNEL)

    for item in channels:
        if item.name == name:
            out = item
            break
    else:
        raise Exception(f'Channel not found in the external database: {name}')

    return out

# ################################################################################################################################

def _check_channels() -> 'None':
    """ Confirms both channels come back from the external database with offset ids and opaque attributes merged in.
    """
    as2_channel = _get_channel_by_name(_as2_channel_name)
    as4_channel = _get_channel_by_name(_as4_channel_name)

    # Ids of external objects are always offset ..
    assert as2_channel.id >= ExtDBCtx.ID_Offset
    assert as4_channel.id >= ExtDBCtx.ID_Offset

    # .. and their opaque attributes are merged into the top level of each row.
    assert as2_channel.as2_local_id == 'zato-station'
    assert as2_channel.as2_partner_id == 'supplier-station'
    assert as4_channel.as4_from_party_id == 'zato-station'
    assert as4_channel.as4_to_party_id == 'billing-station'

# ################################################################################################################################

def _check_outconns() -> 'None':
    """ Confirms the AS4 outgoing connection comes back from the external database with an offset id.
    """
    outconns = get_ext_http_soap_list(default_cluster_id, CONNECTION.OUTGOING, URL_TYPE.AS4)

    outconn_count = len(outconns)
    assert outconn_count == 1

    outconn = outconns[0]
    assert outconn.name == _as4_outconn_name
    assert outconn.id >= ExtDBCtx.ID_Offset
    assert outconn.host == 'https://as4.billing-station.example.com'

# ################################################################################################################################

def _check_channel_merge() -> 'None':
    """ Confirms the merge of channel lists - the external database wins on conflicts
    and unrelated internal rows are kept.
    """

    # An internal row the external database knows nothing about ..
    internal_rest = Bunch()
    internal_rest.id = 57
    internal_rest.name = 'billing.rest.channel'
    internal_rest.connection = CONNECTION.CHANNEL
    internal_rest.transport = 'plain_http'

    # .. and an internal row the external database overrides.
    internal_as2 = Bunch()
    internal_as2.id = 58
    internal_as2.name = _as2_channel_name
    internal_as2.connection = CONNECTION.CHANNEL
    internal_as2.transport = URL_TYPE.AS2

    target:'anylist' = [internal_rest, internal_as2]

    ext_items = get_ext_http_soap_list(default_cluster_id, CONNECTION.CHANNEL)
    merge_ext_channel_items(target, ext_items)

    # The unrelated internal row and both external channels remain
    target_count = len(target)
    assert target_count == 3

    # The REST channel was not touched ..
    names:'anylist' = []

    for item in target:
        names.append(item.name)

    assert 'billing.rest.channel' in names

    # .. while the AS2 channel now comes from the external database, with its offset id.
    for item in target:
        if item.name == _as2_channel_name:
            assert item.id >= ExtDBCtx.ID_Offset

# ################################################################################################################################

def _check_config_entry_merge() -> 'None':
    """ Confirms the merge of config dict entries - the external database wins on name conflicts
    and its entries receive offset ids.
    """
    session = get_ext_db_session()

    # Read the AS2 outgoing connections back from the external database ..
    try:
        result = connection_list(session, default_cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_AS2, False)

        source:'anydict' = {}

        for item in result:
            source[item.name] = {'config': {'id': item.id, 'name': item.name}}
    finally:
        session.close()

    source_count = len(source)
    assert source_count == 1

    # .. build a target that has a conflicting entry with an internal id ..
    target:'anydict' = {
        _as2_outconn_name: {'config': {'id': 61, 'name': _as2_outconn_name}},
    }

    merge_ext_config_entries(target, source)

    # .. and the external entry replaced it, with the offset applied to its id.
    entry = target[_as2_outconn_name]
    entry_id = entry['config']['id']

    assert entry_id >= ExtDBCtx.ID_Offset

# ################################################################################################################################

def _check_edit() -> 'None':
    """ Edits the AS4 channel through the external session and confirms the change is visible.
    """
    session = get_ext_db_session()

    try:
        item = session.query(HTTPSOAP).filter(HTTPSOAP.name == _as4_channel_name).one()
        item.url_path = _edited_url_path
        session.commit()
    finally:
        session.close()

    as4_channel = _get_channel_by_name(_as4_channel_name)
    assert as4_channel.url_path == _edited_url_path

# ################################################################################################################################

def _check_delete() -> 'None':
    """ Deletes the AS4 outgoing connection through the external session and confirms it is gone.
    """
    session = get_ext_db_session()

    try:
        item = session.query(HTTPSOAP).filter(HTTPSOAP.name == _as4_outconn_name).one()
        session.delete(item)
        session.commit()
    finally:
        session.close()

    outconns = get_ext_http_soap_list(default_cluster_id, CONNECTION.OUTGOING, URL_TYPE.AS4)
    assert not outconns

# ################################################################################################################################

def _check_security_copy() -> 'None':
    """ Mirrors a security definition in the external database and confirms mirroring is idempotent.
    """
    # The mirrored copy keeps the id the definition has in the main ODB
    sec_def = _SecurityDefinition(
        id=204,
        name='as2.partner.basic-auth',
        username='as2-partner',
        password='test-sec-password',
        password_type='',
        is_active=True,
        sec_type='basic_auth',
    )

    session = get_ext_db_session()

    # The first call inserts the copy, the second one finds it and does nothing
    try:
        ensure_security_copy(session, sec_def, default_cluster_id)
        session.commit()

        ensure_security_copy(session, sec_def, default_cluster_id)
        session.commit()

        count = session.query(SecurityBase.id).filter(SecurityBase.id == sec_def.id).count()
        assert count == 1
    finally:
        session.close()

# ################################################################################################################################

def run_ext_db_scenario() -> 'None':
    """ The complete external AS2/AS4 database scenario every backend must pass:
    schema creation, inserts of all the AS2/AS4 object kinds, reads with offset ids
    and merged opaque attributes, both merge functions, an edit, a delete
    and idempotent mirroring of a security definition.
    """

    # Connecting creates the schema and seeds the cluster row
    _ = get_ext_db_engine()

    # Start from empty tables because containers can be reused between test runs
    _clean_up_tables()

    # Create all the AS2/AS4 object kinds
    _insert_test_objects()

    # Reads come back with offset ids and merged opaque attributes
    _check_channels()
    _check_outconns()

    # Both merge functions give the external database precedence
    _check_channel_merge()
    _check_config_entry_merge()

    # Changes through the external session are visible right away
    _check_edit()
    _check_delete()

    # Mirroring a security definition is idempotent
    _check_security_copy()

# ################################################################################################################################

def assert_mysql_connection_encrypted() -> 'None':
    """ Confirms the current MySQL session really is encrypted.
    """
    engine = get_ext_db_engine()
    assert_mysql_engine_encrypted(engine)

# ################################################################################################################################

def assert_postgresql_connection_encrypted() -> 'None':
    """ Confirms the current PostgreSQL session really is encrypted.
    """
    engine = get_ext_db_engine()
    assert_postgresql_engine_encrypted(engine)

# ################################################################################################################################
# ################################################################################################################################
