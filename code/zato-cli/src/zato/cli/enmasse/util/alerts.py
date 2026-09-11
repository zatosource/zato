# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

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
