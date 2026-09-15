# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
from zato.common.api import FileTransfer
from zato.common.alerting.explain.channel_info import describe_channel
from zato.common.alerting.explain.fhir_info import describe_outgoing_fhir
from zato.common.alerting.explain.llm_info import describe_outgoing_llm
from zato.common.alerting.explain.mllp_channel_info import describe_mllp_channel
from zato.common.alerting.explain.mllp_outgoing_info import describe_mllp_outgoing
from zato.common.alerting.explain.outgoing_info import describe_outgoing_http
from zato.common.alerting.object_config import alert_type_file_transfer, channel_sources, transport_by_outgoing_source
from zato.common.alerting.object_settings import load_object_settings
from zato.common.audit_log.api import AuditSource
from zato.common.odb.model import GenericConn
from zato.common.util.file_transfer_scheduler import get_schedule_list
from zato.common.util.sql import get_dict_with_opaque
from zato.server.generic.api.outconn_ftp import Outconn_FTP_Config_Defaults
from zato.server.generic.api.outconn_sftp import outconn_sftp_config_defaults
from zato.server.generic.api.outconn_smb import outconn_smb_config_defaults

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anydict, anylist, dictlist, strlist
    from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

# The sources whose alerts read an outgoing REST or SOAP connection's Object - the connection's own traffic
# and its health check, which calls the same address
_outgoing_http_sources = tuple(transport_by_outgoing_source)

# An outgoing FHIR connection is described the same whether the alert is about its own traffic or its health check
_outgoing_fhir_sources = (AuditSource.FHIR, AuditSource.FHIR_Health)

# What each file transfer connection type is called in the Object section
_file_transfer_type_labels = {
    FileTransfer.ConnType.SFTP: 'SFTP',
    FileTransfer.ConnType.FTP:  'FTP',
    FileTransfer.ConnType.SMB:  'SMB',
}

# The defaults of each file transfer connection type - a connection stored before a key existed reads at its default
_file_transfer_config_defaults = {
    FileTransfer.ConnType.SFTP: outconn_sftp_config_defaults,
    FileTransfer.ConnType.FTP:  Outconn_FTP_Config_Defaults,
    FileTransfer.ConnType.SMB:  outconn_smb_config_defaults,
}

# What a yes-or-no reads as in the Object section
_yes = 'yes'
_no = 'no'

# The per-object toggle saying whether a connection takes part in the test transfers at all
_test_transfers_field = 'test_transfers'

# ################################################################################################################################
# ################################################################################################################################

def get_object_info(service:'AdminService', source:'str', object_name:'str') -> 'tuple[anylist, str, bool]':
    """ The Object section of the evidence - the object's definition as label and value pairs,
    secrets left out - along with the name the baseline is read under and whether test
    transfers are on for the object. An outgoing REST, SOAP, FHIR, LLM or MLLP connection, a channel,
    an MLLP channel, a file transfer connection or one of its schedules are read off the ODB,
    any other source contributes its name alone.
    """
    if source == AuditSource.MLLP_Outgoing:
        with closing(service.odb.session()) as session:
            mllp_outgoing_info = describe_mllp_outgoing(session, service.server.cluster_id, object_name)

        if mllp_outgoing_info is not None:
            return mllp_outgoing_info, object_name, False

    if source in _outgoing_http_sources:
        with closing(service.odb.session()) as session:
            outgoing_info = describe_outgoing_http(session, service.server.cluster_id, source, object_name)

        if outgoing_info is not None:
            return outgoing_info, object_name, False

    if source in _outgoing_fhir_sources:
        with closing(service.odb.session()) as session:
            fhir_info = describe_outgoing_fhir(session, service.server.cluster_id, object_name)

        if fhir_info is not None:
            return fhir_info, object_name, False

    if source == AuditSource.LLM:
        with closing(service.odb.session()) as session:
            llm_info = describe_outgoing_llm(session, service.server.cluster_id, object_name)

        if llm_info is not None:
            return llm_info, object_name, False

    if source in (AuditSource.File_Outgoing, AuditSource.Test_Transfer):
        out = _get_file_transfer_info(service, object_name)
        if out is not None:
            return out

    if source == AuditSource.MLLP_Channel:
        with closing(service.odb.session()) as session:
            mllp_info = describe_mllp_channel(session, service.server.cluster_id, object_name)

        if mllp_info is not None:
            return mllp_info, object_name, False

    if source in channel_sources:
        with closing(service.odb.session()) as session:
            channel_info = describe_channel(session, service.server.cluster_id, source, object_name)

        if channel_info is not None:
            return channel_info, object_name, False

    out = [('Name', object_name)]
    return out, object_name, False

# ################################################################################################################################

def _get_file_transfer_info(service:'AdminService', object_name:'str') -> 'tuple[anylist, str, bool] | None':
    """ The definition of a file transfer connection, or of the connection owning the schedule
    the object name stands for - host, username, how it authenticates, its schedules and
    whether test transfers are on. None when no connection or schedule goes by the name.
    """
    with closing(service.odb.session()) as session:

        rows = session.query(GenericConn).\
            filter(GenericConn.type_.in_(FileTransfer.ConnTypeList)).\
            filter(GenericConn.cluster_id==service.server.cluster_id).\
            all()

        for row in rows:

            schedules = get_schedule_list(session, row.id)
            schedule_names:'strlist' = []

            for schedule in schedules:
                schedule_names.append(schedule['name'])

            is_connection = row.name == object_name
            is_schedule = object_name in schedule_names

            if not (is_connection or is_schedule):
                continue

            # The connection's columns and its opaque attributes together - host, username, key and the like -
            # with every key the connection was stored without at the default of its type
            config = get_dict_with_opaque(row)

            for key, default in _file_transfer_config_defaults[row.type_].items():
                if key not in config or config[key] is None:
                    config[key] = default

            test_transfers_on = _wants_test_transfer(session, service.server.cluster_id, row.name)

            out = _describe_file_transfer(row, config, schedules, object_name, is_schedule, test_transfers_on)

            return out, row.name, test_transfers_on

    return None

# ################################################################################################################################

def _describe_file_transfer(
    row:'GenericConn',
    config:'anydict',
    schedules:'dictlist',
    object_name:'str',
    is_schedule:'bool',
    test_transfers_on:'bool',
    ) -> 'anylist':
    """ The label and value pairs describing one file transfer connection.
    """

    # Our response to produce
    out:'anylist' = []

    type_label = _file_transfer_type_labels[row.type_]

    if is_schedule:
        out.append(('Schedule', f'{object_name}, of the {type_label} connection {row.name}'))

    out.append(('Name', row.name))
    out.append(('Type', type_label))
    out.append(('Active', _yes if row.is_active else _no))

    if row.type_ == FileTransfer.ConnType.SFTP:
        out.append(('Host', config['address']))
        out.append(('Username', config['username']))

        if config['private_key']:
            authentication = f'private key ({config["private_key"]})'
        else:
            authentication = 'password'

        host_key_checking = 'on' if config['strict_host_key_checking'] else 'off'
        out.append(('Authentication', f'{authentication}, host key checking {host_key_checking}'))

    elif row.type_ == FileTransfer.ConnType.FTP:
        out.append(('Host', f'{config["host"]}:{config["port"]}'))
        out.append(('Username', config['username']))

        tls = 'on' if config['use_ssl'] else 'off'
        out.append(('Authentication', f'password, TLS {tls}'))

    else:
        out.append(('Host', f'{config["host"]}:{config["port"]}'))
        out.append(('Username', config['username']))
        out.append(('Authentication', 'password'))

    for schedule in schedules:
        state = 'active' if schedule['is_active'] else 'inactive'
        description = f'{schedule["name"]} - watches {schedule["directory"]}, delivers to {schedule["service"]}, ' + \
            f'every {schedule["run_every"]} {schedule["run_unit"]}, {state}'
        out.append(('Schedule', description))

    if not schedules:
        out.append(('Schedules', 'none'))

    out.append(('Test transfers', 'on' if test_transfers_on else 'off'))

    return out

# ################################################################################################################################

def _wants_test_transfer(session:'SASession', cluster_id:'int', conn_name:'str') -> 'bool':
    """ Whether the connection's own Alerts tab has test transfers on.
    """
    settings_by_object = load_object_settings(session, cluster_id)[alert_type_file_transfer]

    if conn_name not in settings_by_object:
        return False

    out = settings_by_object[conn_name][_test_transfers_field] is True
    return out

# ################################################################################################################################
# ################################################################################################################################
