# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An object's alert settings sit under one alerts mapping, its names the unprefixed ones of the Alerts tab,
# durations in seconds, and only what differs from the defaults needs writing:
#
#     channel_rest:
#       - name: orders.api
#         service: orders.create
#         url_path: /api/orders
#         alerts:
#           max_latency: 2000
#           traffic_expected: true
#           silence_window: 1800
#           email_connection: smtp:ops.smtp
#           llm_connection: ops.llm
#
#       - name: orders.status
#         service: orders.status
#         url_path: /api/orders/status
#         alerts:
#           is_active: false
#
#     channel_soap:
#       - name: orders.soap
#         service: orders.create
#         url_path: /soap/orders
#         soap_action: urn:orders
#         soap_version: '1.1'
#         alerts:
#           max_latency: 2500
#           auth_failures: 3

# stdlib
import logging
from json import loads

# Zato
from zato.common.alerting import object_config
from zato.common.api import EMAIL, GENERIC
from zato.common.defaults import default_cluster_id
from zato.common.odb.model import GenericConn, IMAP, SMTP
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anydict, anydictnone
    SASession = SASession
    anydict = anydict
    anydictnone = anydictnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def _find_email_connection(kind:'str', name:'str', session:'SASession') -> 'bool':
    """ Whether an email connection of the given kind and name exists and may send alerts - any SMTP
    connection may, whereas among IMAP ones only Microsoft 365 has the Graph API to send with.
    """
    if kind == object_config.Email_Conn_Type_SMTP:
        connection = session.query(SMTP).filter_by(cluster_id=default_cluster_id, name=name).first()
        out = connection is not None
        return out

    connection = session.query(IMAP).filter_by(cluster_id=default_cluster_id, name=name).first()

    # No such IMAP connection at all
    if connection is None:
        return False

    # The server type of an IMAP connection is an opaque attribute of its own
    opaque = parse_instance_opaque_attr(connection)

    if 'server_type' not in opaque:
        return False

    out = opaque['server_type'] == EMAIL.IMAP.ServerType.Microsoft365
    return out

# ################################################################################################################################

def _ensure_email_connection_exists(
    value:'str',
    connection_type:'str',
    connection_name:'str',
    session:'SASession',
) -> 'None':
    """ Rejects an email connection an object names for its alerts unless it exists,
    so that alerts are never configured to go out through a connection that is not there.
    """

    # No connection named means the alerts go out through the ruleset-wide notifications only
    if value == object_config.Email_Connection_Default:
        return

    kind, name = object_config.decode_email_connection(value)

    if kind not in object_config.email_conn_types:
        raise Exception(f'Email connection `{value}` of unknown kind `{kind}` for {connection_type} connection `{connection_name}`')

    if not _find_email_connection(kind, name, session):
        raise Exception(f'Email connection `{name}` of kind `{kind}` not found for {connection_type} connection `{connection_name}`')

# ################################################################################################################################

def _ensure_llm_connection_exists(
    name:'str',
    connection_type:'str',
    connection_name:'str',
    session:'SASession',
) -> 'None':
    """ Rejects an LLM connection an object names for its alerts unless it exists,
    so that explanations are never configured to go through a connection that is not there.
    """

    # No connection named means the deployment's default explains the object's alerts
    if name == object_config.LLM_Connection_Default:
        return

    connection = session.query(GenericConn).\
        filter_by(cluster_id=default_cluster_id, name=name, type_=GENERIC.CONNECTION.TYPE.OUTCONN_LLM).\
        first()

    if connection is None:
        raise Exception(f'LLM connection `{name}` not found for {connection_type} connection `{connection_name}`')

# ################################################################################################################################
# ################################################################################################################################

def flatten_alerts(connection_def:'anydict', alert_type:'str', connection_type:'str', session:'SASession') -> 'None':
    """ Takes the alerts mapping out of a YAML connection definition and puts its values, over the defaults,
    into the definition under their storage names, in place - which is where the opaque attributes come from.
    A definition without the mapping gets the defaults, so that every stored connection carries every field.
    """
    connection_name = connection_def['name']

    alerts = connection_def.pop(object_config.Alerts_Key, None)
    if alerts is None:
        alerts = {}

    field_names = object_config.get_field_names(alert_type)

    for name in alerts:
        if name not in field_names:
            raise Exception(f'Unknown alert field `{name}` for {connection_type} connection `{connection_name}`')

    if object_config.Email_Connection_Field in alerts:
        email_connection = alerts[object_config.Email_Connection_Field]
        _ensure_email_connection_exists(email_connection, connection_type, connection_name, session)

    if object_config.LLM_Connection_Field in alerts:
        llm_connection = alerts[object_config.LLM_Connection_Field]
        _ensure_llm_connection_exists(llm_connection, connection_type, connection_name, session)

    values = object_config.get_defaults(alert_type)
    values.update(alerts)

    connection_def.update(object_config.to_storage(alert_type, values))

# ################################################################################################################################

def alerts_need_update(item:'anydict', db_def:'anydict', alert_type:'str') -> 'bool':
    """ Whether the alert settings a YAML definition gives, over the defaults, differ from the ones the database row stores.
    """
    values = object_config.get_defaults(alert_type)

    if object_config.Alerts_Key in item:
        values.update(item[object_config.Alerts_Key])

    expected = object_config.to_storage(alert_type, values)

    stored = {}
    opaque1 = db_def['opaque1']
    if opaque1:
        stored = loads(opaque1)

    for key, value in expected.items():
        if key not in stored:
            logger.info('Alert setting %s missing for %s', key, item['name'])
            return True
        if stored[key] != value:
            logger.info('Alert setting %s changed for %s: yaml=%s db=%s', key, item['name'], value, stored[key])
            return True

    return False

# ################################################################################################################################

def take_alert_attrs(connection_def:'anydict', alert_type:'str', connection_type:'str', session:'SASession') -> 'anydict':
    """ The alert settings of a YAML definition under their storage names, over the defaults, ready for the opaque
    attributes. The alerts mapping leaves the definition, so that it never reaches the object's own attributes.
    """
    out = {'name': connection_def['name']}

    if object_config.Alerts_Key in connection_def:
        out[object_config.Alerts_Key] = connection_def.pop(object_config.Alerts_Key)

    flatten_alerts(out, alert_type, connection_type, session)
    del out['name']

    return out

# ################################################################################################################################

def group_alerts(row:'anydict', alert_type:'str') -> 'anydictnone':
    """ The alerts mapping an exported connection carries - only the settings moved away from their defaults,
    in field order, or None when there is nothing to write, so that a file the export produces reads
    the way one written by hand does.
    """
    defaults = object_config.get_defaults(alert_type)
    values = object_config.from_storage(alert_type, row)

    out:'anydict' = {}

    for name, value in values.items():
        if value != defaults[name]:
            out[name] = value

    if not out:
        return None

    return out

# ################################################################################################################################
# ################################################################################################################################
