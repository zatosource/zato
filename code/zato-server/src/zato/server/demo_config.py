# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The registry of the demo config sets - what each one is called, how it is imported,
# how its presence is checked and how its objects are removed. The Demo config screen
# saves through it and the first start of a fresh environment - one with no user
# services to deploy - imports the sets from First_Start_Set_Names through it,
# or the sets named in the Env_First_Start_Set_Names environment variable.

# stdlib
import os
from contextlib import closing
from logging import getLogger
from traceback import format_exc

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.alerting.names import get_notification_conn_name
from zato.common.api import GENERIC
from zato.common.demo.seed import Channel_Clinic, Channel_Lab, Channel_Main, Outconn_FHIR, Outconn_Forward
from zato.common.json_internal import dumps
from zato.common.odb.model import GenericConn, HTTPSOAP, Job, PubSubPermission, PubSubSubscription, PubSubTopic, \
    SecurityBase, SQLConnectionPool
from zato.common.odb.query.generic import GenericObjectWrapper
from zato.common.typing_ import cast_
from zato.common.util.file_system import get_python_files
from zato.server.demo import _archive_intake_channel, _archive_outconn
from zato.server.demo_mcp.common import Gateway_Name as _mcp_gateway_name, Security_Name as _mcp_security_name, \
    SQL_Connections as _mcp_sql_connections
from zato.server.demo_mcp.install import import_demo_mcp, remove_demo_mcp
from zato.server.demo_file_transfer.layout import Feeder_Name as _file_transfer_feeder_name, FTP_Connections, \
    get_connection_names, get_schedule_job_names, SFTP_Connections, SMB_Connections

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strbooldict, stranydict, strlist, strset
    from zato.server.base.parallel import ParallelServer

    any_ = any_
    ParallelServer = ParallelServer
    strbooldict = strbooldict
    stranydict = stranydict
    strlist = strlist
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The names of the demo config sets, in the order the Demo config screen shows them
Set_Scheduler = 'scheduler'
Set_Tutorial  = 'tutorial'
Set_HL7       = 'hl7'
Set_MCP       = 'mcp'
Set_IBM_MQ    = 'ibm_mq'
Set_Kafka     = 'kafka'
Set_PubSub    = 'pubsub'
Set_File_Transfer = 'file_transfer'

# The HL7 set comes before the MCP one, which builds on it
Set_Names = [Set_Scheduler, Set_Tutorial, Set_HL7, Set_MCP, Set_IBM_MQ, Set_Kafka, Set_PubSub, Set_File_Transfer]

# The demo config sets a fresh environment receives on its first start
First_Start_Set_Names = [Set_Tutorial, Set_HL7]

# The environment variable that names, comma-separated, the demo config sets a first start imports instead,
# whatever user services or objects the environment already has
Env_First_Start_Set_Names = 'Zato_Demo_Config_Sets'

# ################################################################################################################################
# ################################################################################################################################

# The scheduler jobs the scheduler demo set consists of - the first one doubles as its presence check
_scheduler_job_names = [
    'crm.sync-contacts',
    'crm.sync-accounts',
    'crm.push-cases',
    'crm.reconcile-invoices',
    'crm.purge-stale-sessions',
    'crm.slow-sftp-export',
]

# The generic connections each broker demo set consists of, as (name, type) pairs
_ibm_mq_connections = [
    ('demo.ibm-mq.channel',   GENERIC.CONNECTION.TYPE.CHANNEL_IBM_MQ),
    ('demo.ibm-mq.publisher', GENERIC.CONNECTION.TYPE.OUTCONN_IBM_MQ),
]

_kafka_connections = [
    ('demo.kafka.channel',   GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA),
    ('demo.kafka.publisher', GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA),
]

# What the pub/sub demo set consists of
_pubsub_topic_name     = 'demo.messages'
_pubsub_security_names = ['demo_pubsub.publisher', 'demo_pubsub.subscriber']
_pubsub_job_name       = 'demo.pubsub'
_pubsub_pickup_file    = 'demo_pubsub_services.py'

# What the tutorial demo set consists of
_tutorial_channel_name  = 'My REST Channel'
_tutorial_outconn_name  = 'CRM'
_tutorial_sql_name      = 'Billing'
_tutorial_security_name = 'My API Key'
_tutorial_job_name      = 'my.report.job'
_tutorial_pickup_file   = 'api.py'

# What the file transfer demo set consists of - the feeder job doubles as its presence check
_file_transfer_job_names = [_file_transfer_feeder_name] + get_schedule_job_names()

# ################################################################################################################################
# ################################################################################################################################

# Every named object each set consists of, grouped by kind - the screen shows these
# groups as pills and names, and the first name of the first group doubles as the
# set's presence check.
_manifests = {
    Set_Scheduler: [
        {'kind': 'job', 'names': _scheduler_job_names},
    ],
    Set_Tutorial: [
        {'kind': 'channel-rest', 'names': [_tutorial_channel_name]},
        {'kind': 'outconn-rest', 'names': [_tutorial_outconn_name]},
        {'kind': 'sql', 'names': [_tutorial_sql_name]},
        {'kind': 'security-apikey', 'names': [_tutorial_security_name]},
        {'kind': 'job', 'names': [_tutorial_job_name]},
    ],
    Set_MCP: [
        {'kind': 'gateway-mcp', 'names': [_mcp_gateway_name]},
        {'kind': 'sql', 'names': _mcp_sql_connections},
        {'kind': 'security-bearer', 'names': [_mcp_security_name]},
    ],
    Set_HL7: [
        {'kind': 'channel-hl7-mllp', 'names': [Channel_Main, Channel_Lab, Channel_Clinic]},
        {'kind': 'outconn-hl7-mllp', 'names': [Outconn_Forward]},
        {'kind': 'outconn-hl7-fhir', 'names': [Outconn_FHIR]},
        {'kind': 'outconn-rest', 'names': [_archive_outconn]},
        {'kind': 'channel-rest', 'names': [_archive_intake_channel]},
    ],
    Set_IBM_MQ: [
        {'kind': 'channel-ibm-mq', 'names': [_ibm_mq_connections[0][0]]},
        {'kind': 'outconn-ibm-mq', 'names': [_ibm_mq_connections[1][0]]},
    ],
    Set_Kafka: [
        {'kind': 'channel-kafka', 'names': [_kafka_connections[0][0]]},
        {'kind': 'outconn-kafka', 'names': [_kafka_connections[1][0]]},
    ],
    Set_PubSub: [
        {'kind': 'pubsub-topic', 'names': [_pubsub_topic_name]},
        {'kind': 'security-basic-auth', 'names': _pubsub_security_names},
        {'kind': 'job', 'names': [_pubsub_job_name]},
    ],
    Set_File_Transfer: [
        {'kind': 'job', 'names': _file_transfer_job_names},
        {'kind': 'outconn-sftp', 'names': get_connection_names(SFTP_Connections)},
        {'kind': 'outconn-ftp', 'names': get_connection_names(FTP_Connections)},
        {'kind': 'outconn-smb', 'names': get_connection_names(SMB_Connections)},
    ],
}

# The generic-connection type each generic-connection kind stores its rows under
_generic_conn_types = {
    'channel-ibm-mq':   GENERIC.CONNECTION.TYPE.CHANNEL_IBM_MQ,
    'outconn-ibm-mq':   GENERIC.CONNECTION.TYPE.OUTCONN_IBM_MQ,
    'channel-kafka':    GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA,
    'outconn-kafka':    GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA,
    'channel-hl7-mllp': 'channel-hl7-mllp',
    'outconn-hl7-mllp': 'outconn-hl7-mllp',
    'outconn-hl7-fhir': 'outconn-hl7-fhir',
    'outconn-sftp':     GENERIC.CONNECTION.TYPE.OUTCONN_SFTP,
    'outconn-ftp':      GENERIC.CONNECTION.TYPE.OUTCONN_FTP,
    'outconn-smb':      GENERIC.CONNECTION.TYPE.OUTCONN_SMB,
    'gateway-mcp':      GENERIC.CONNECTION.TYPE.GATEWAY_MCP,
}

# Which side of the http-soap table each REST kind lives on
_rest_connections = {
    'channel-rest': 'channel',
    'outconn-rest': 'outgoing',
}

# ################################################################################################################################
# ################################################################################################################################

# The marker that records that the first-start import already ran,
# whether it imported anything or found the environment non-empty.
_marker_type = 'demo.config.auto.import'
_marker_name = 'default'

# The security definitions every new environment is created with - they do not count
# against the emptiness of an environment.
_baseline_security_names = [
    'admin.invoke',
    'ide_publisher',
    'zato.log.streaming',
    'django',
    'metrics',
]

# ################################################################################################################################
# ################################################################################################################################

def _remove_pickup_file(server:'ParallelServer', file_name:'str') -> 'None':
    """ Removes a file an import once wrote into the hot-deployment directory.
    """
    file_path = os.path.join(server.hot_deploy_config.pickup_dir, file_name)

    if os.path.exists(file_path):
        os.remove(file_path)

# ################################################################################################################################
# ################################################################################################################################

def _existing_job_names(server:'ParallelServer', kind:'str', names:'strlist') -> 'strset':

    job_name_column = cast_('any_', Job.name)

    with closing(server.odb.session()) as session:
        rows = session.query(Job.name).\
            filter(job_name_column.in_(names)).\
            all()

    # Our response to produce
    out:'strset' = set()

    for (name,) in rows:
        out.add(name)

    return out

# ################################################################################################################################

def _existing_generic_conn_names(server:'ParallelServer', kind:'str', names:'strlist') -> 'strset':

    type_ = _generic_conn_types[kind]
    conn_name_column = cast_('any_', GenericConn.name)

    with closing(server.odb.session()) as session:
        rows = session.query(GenericConn.name).\
            filter(conn_name_column.in_(names)).\
            filter(GenericConn.type_==type_).\
            all()

    # Our response to produce
    out:'strset' = set()

    for (name,) in rows:
        out.add(name)

    return out

# ################################################################################################################################

def _existing_rest_names(server:'ParallelServer', kind:'str', names:'strlist') -> 'strset':

    connection = _rest_connections[kind]
    rest_name_column = cast_('any_', HTTPSOAP.name)

    with closing(server.odb.session()) as session:
        rows = session.query(HTTPSOAP.name).\
            filter(rest_name_column.in_(names)).\
            filter(HTTPSOAP.connection==connection).\
            all()

    # Our response to produce
    out:'strset' = set()

    for (name,) in rows:
        out.add(name)

    return out

# ################################################################################################################################

def _existing_security_names(server:'ParallelServer', kind:'str', names:'strlist') -> 'strset':

    security_name_column = cast_('any_', SecurityBase.name)

    with closing(server.odb.session()) as session:
        rows = session.query(SecurityBase.name).\
            filter(security_name_column.in_(names)).\
            all()

    # Our response to produce
    out:'strset' = set()

    for (name,) in rows:
        out.add(name)

    return out

# ################################################################################################################################

def _existing_sql_names(server:'ParallelServer', kind:'str', names:'strlist') -> 'strset':

    sql_name_column = cast_('any_', SQLConnectionPool.name)

    with closing(server.odb.session()) as session:
        rows = session.query(SQLConnectionPool.name).\
            filter(sql_name_column.in_(names)).\
            all()

    # Our response to produce
    out:'strset' = set()

    for (name,) in rows:
        out.add(name)

    return out

# ################################################################################################################################

def _existing_topic_names(server:'ParallelServer', kind:'str', names:'strlist') -> 'strset':

    topic_name_column = cast_('any_', PubSubTopic.name)

    with closing(server.odb.session()) as session:
        rows = session.query(PubSubTopic.name).\
            filter(topic_name_column.in_(names)).\
            all()

    # Our response to produce
    out:'strset' = set()

    for (name,) in rows:
        out.add(name)

    return out

# ################################################################################################################################
# ################################################################################################################################

# How each kind's names are looked up in the database
_existing_names_funcs = {
    'job':              _existing_job_names,
    'channel-rest':     _existing_rest_names,
    'outconn-rest':     _existing_rest_names,
    'sql':              _existing_sql_names,
    'security-apikey':  _existing_security_names,
    'security-bearer':  _existing_security_names,
    'security-basic-auth': _existing_security_names,
    'pubsub-topic':     _existing_topic_names,
    'channel-ibm-mq':   _existing_generic_conn_names,
    'outconn-ibm-mq':   _existing_generic_conn_names,
    'channel-kafka':    _existing_generic_conn_names,
    'outconn-kafka':    _existing_generic_conn_names,
    'channel-hl7-mllp': _existing_generic_conn_names,
    'outconn-hl7-mllp': _existing_generic_conn_names,
    'outconn-hl7-fhir': _existing_generic_conn_names,
    'outconn-sftp':     _existing_generic_conn_names,
    'outconn-ftp':      _existing_generic_conn_names,
    'outconn-smb':      _existing_generic_conn_names,
    'gateway-mcp':      _existing_generic_conn_names,
}

# ################################################################################################################################
# ################################################################################################################################

def _import_scheduler(server:'ParallelServer') -> 'any_':
    out = server.import_demo_scheduler()
    return out

# ################################################################################################################################

def _import_tutorial(server:'ParallelServer') -> 'any_':
    out = server.import_demo_tutorial()
    return out

# ################################################################################################################################

def _import_hl7(server:'ParallelServer') -> 'any_':
    out = server.import_demo_hl7()
    return out

# ################################################################################################################################

def _import_mcp(server:'ParallelServer') -> 'any_':
    out = import_demo_mcp(server)
    return out

# ################################################################################################################################

def _import_ibm_mq(server:'ParallelServer') -> 'any_':
    out = server.import_demo_ibm_mq()
    return out

# ################################################################################################################################

def _import_kafka(server:'ParallelServer') -> 'any_':
    out = server.import_demo_kafka()
    return out

# ################################################################################################################################

def _import_pubsub(server:'ParallelServer') -> 'any_':
    out = server.import_demo_pubsub()
    return out

# ################################################################################################################################

def _import_file_transfer(server:'ParallelServer') -> 'any_':
    out = server.import_demo_file_transfer()
    return out

# ################################################################################################################################
# ################################################################################################################################

def _delete_jobs(server:'ParallelServer', job_names:'strlist') -> 'strlist':
    """ Deletes the named scheduler jobs and returns the names of what was deleted.
    """

    # One query resolves all the names to their IDs ..
    job_name_column = cast_('any_', Job.name)

    with closing(server.odb.session()) as session:
        rows = session.query(Job.id, Job.name).\
            filter(job_name_column.in_(job_names)).\
            all()

    # Our response to produce
    out:'strlist' = []

    # .. and each job goes through the same delete service the Dashboard uses.
    for job_id, job_name in rows:
        _ = server.invoke('zato.scheduler.job.delete', {'id': job_id})
        out.append(job_name)

    return out

# ################################################################################################################################

def _delete_generic_connections(server:'ParallelServer', connections:'any_') -> 'strlist':
    """ Deletes the given generic connections, each identified by its (name, type) pair.
    Returns the names of what was deleted.
    """
    connection_names = []

    for name, _ignored_type in connections:
        connection_names.append(name)

    # One query resolves all the names to their IDs ..
    with closing(server.odb.session()) as session:
        rows = session.query(GenericConn.id, GenericConn.name).\
            filter(GenericConn.name.in_(connection_names)).\
            all()

    # Our response to produce
    out:'strlist' = []

    # .. and each connection goes through the same delete service the Dashboard uses.
    for connection_id, connection_name in rows:
        _ = server.invoke('zato.generic.connection.delete', {'id': connection_id})
        out.append(connection_name)

    return out

# ################################################################################################################################

def _delete_http_soap(server:'ParallelServer', name:'str', connection:'str') -> 'strlist':
    """ Deletes one REST object - a channel or an outgoing connection - by its name.
    Returns the names of what was deleted.
    """
    with closing(server.odb.session()) as session:
        rows = session.query(HTTPSOAP.id, HTTPSOAP.name).\
            filter(HTTPSOAP.name==name).\
            filter(HTTPSOAP.connection==connection).\
            all()

    # Our response to produce
    out:'strlist' = []

    for object_id, object_name in rows:
        _ = server.invoke('zato.http-soap.delete', {'id': object_id})
        out.append(object_name)

    return out

# ################################################################################################################################

def _remove_scheduler(server:'ParallelServer') -> 'stranydict':

    deleted = _delete_jobs(server, _scheduler_job_names)

    out = {'deleted': deleted}
    return out

# ################################################################################################################################

def _remove_ibm_mq(server:'ParallelServer') -> 'stranydict':

    deleted = _delete_generic_connections(server, _ibm_mq_connections)

    out = {'deleted': deleted}
    return out

# ################################################################################################################################

def _remove_kafka(server:'ParallelServer') -> 'stranydict':

    deleted = _delete_generic_connections(server, _kafka_connections)

    out = {'deleted': deleted}
    return out

# ################################################################################################################################

def _remove_pubsub(server:'ParallelServer') -> 'stranydict':

    # Everything that hangs off the demo security definitions is read in one pass -
    # the definitions themselves, their subscriptions and their permissions
    with closing(server.odb.session()) as session:

        security_rows = session.query(SecurityBase.id, SecurityBase.name).\
            filter(SecurityBase.name.in_(_pubsub_security_names)).\
            all()

        security_ids = []

        for security_id, _ignored_name in security_rows:
            security_ids.append(security_id)

        subscription_rows = session.query(PubSubSubscription.id).\
            filter(PubSubSubscription.sec_base_id.in_(security_ids)).\
            all()

        permission_rows = session.query(PubSubPermission.id).\
            filter(PubSubPermission.sec_base_id.in_(security_ids)).\
            all()

        topic_rows = session.query(PubSubTopic.id, PubSubTopic.name).\
            filter(PubSubTopic.name==_pubsub_topic_name).\
            all()

    deleted:'strlist' = []

    # The subscriptions go first, so nothing consumes from the topic meanwhile ..
    for (subscription_id,) in subscription_rows:
        request = {'id': subscription_id}
        _ = server.invoke('zato.pubsub.subscription.delete', request)

    # .. the permissions follow ..
    for (permission_id,) in permission_rows:
        request = {'id': permission_id}
        _ = server.invoke('zato.pubsub.permission.delete', request)

    # .. then the topic itself ..
    for topic_id, topic_name in topic_rows:
        request = {'id': topic_id}
        _ = server.invoke('zato.pubsub.topic.delete', request)
        deleted.append(topic_name)

    # .. the job that publishes to it ..
    deleted_jobs = _delete_jobs(server, [_pubsub_job_name])
    deleted.extend(deleted_jobs)

    # .. the security definitions go last, once nothing references them ..
    for security_id, security_name in security_rows:
        request = {'id': security_id}
        _ = server.invoke('zato.security.basic-auth.delete', request)
        deleted.append(security_name)

    # .. and the services file the import once wrote goes away too.
    _remove_pickup_file(server, _pubsub_pickup_file)

    out = {'deleted': deleted}
    return out

# ################################################################################################################################

def _remove_tutorial(server:'ParallelServer') -> 'stranydict':

    deleted:'strlist' = []

    # The job and the channel name the tutorial service, so they go first ..
    deleted_jobs = _delete_jobs(server, [_tutorial_job_name])
    deleted.extend(deleted_jobs)

    deleted_channels = _delete_http_soap(server, _tutorial_channel_name, 'channel')
    deleted.extend(deleted_channels)

    # .. the outgoing REST connection follows ..
    deleted_outconns = _delete_http_soap(server, _tutorial_outconn_name, 'outgoing')
    deleted.extend(deleted_outconns)

    # .. then the SQL connection ..
    with closing(server.odb.session()) as session:
        sql_rows = session.query(SQLConnectionPool.id, SQLConnectionPool.name).\
            filter(SQLConnectionPool.name==_tutorial_sql_name).\
            all()

    for sql_id, sql_name in sql_rows:
        request = {'id': sql_id}
        _ = server.invoke('zato.outgoing.sql.delete', request)
        deleted.append(sql_name)

    # .. the API key goes once the channel no longer references it ..
    with closing(server.odb.session()) as session:
        security_rows = session.query(SecurityBase.id, SecurityBase.name).\
            filter(SecurityBase.name==_tutorial_security_name).\
            all()

    for security_id, security_name in security_rows:
        request = {'id': security_id}
        _ = server.invoke('zato.security.apikey.delete', request)
        deleted.append(security_name)

    # .. and the service file the import once wrote goes away too.
    _remove_pickup_file(server, _tutorial_pickup_file)

    out = {'deleted': deleted}
    return out

# ################################################################################################################################

def _remove_file_transfer(server:'ParallelServer') -> 'stranydict':

    from zato.server.demo_file_transfer import remove_demo_file_transfer

    out = remove_demo_file_transfer(server)
    return out

# ################################################################################################################################

def _remove_mcp(server:'ParallelServer') -> 'stranydict':
    out = remove_demo_mcp(server)
    return out

# ################################################################################################################################

def _remove_hl7(server:'ParallelServer') -> 'stranydict':

    from zato.server.demo import remove_demo_data

    out = remove_demo_data(server)
    return out

# ################################################################################################################################
# ################################################################################################################################

_import_funcs = {
    Set_Scheduler: _import_scheduler,
    Set_Tutorial:  _import_tutorial,
    Set_HL7:       _import_hl7,
    Set_MCP:       _import_mcp,
    Set_IBM_MQ:    _import_ibm_mq,
    Set_Kafka:     _import_kafka,
    Set_PubSub:    _import_pubsub,
    Set_File_Transfer: _import_file_transfer,
}

_remove_funcs = {
    Set_Scheduler: _remove_scheduler,
    Set_Tutorial:  _remove_tutorial,
    Set_HL7:       _remove_hl7,
    Set_MCP:       _remove_mcp,
    Set_IBM_MQ:    _remove_ibm_mq,
    Set_Kafka:     _remove_kafka,
    Set_PubSub:    _remove_pubsub,
    Set_File_Transfer: _remove_file_transfer,
}

# ################################################################################################################################
# ################################################################################################################################

def get_demo_config_details(server:'ParallelServer') -> 'stranydict':
    """ Returns, for each demo config set, whether it is present and which of its
    objects exist, grouped by kind - everything the Demo config screen paints.
    """

    # Our response to produce
    out:'stranydict' = {}

    for set_name in Set_Names:

        groups = []

        for manifest_group in _manifests[set_name]:

            kind = cast_('str', manifest_group['kind'])
            names = cast_('strlist', manifest_group['names'])

            lookup_func = _existing_names_funcs[kind]
            existing = lookup_func(server, kind, names)

            items = []

            for name in names:
                items.append({'name': name, 'exists': name in existing})

            groups.append({'kind': kind, 'items': items})

        # The first name of the first group is the set's presence check
        first_group = groups[0]
        first_item = first_group['items'][0]

        out[set_name] = {
            'is_present': first_item['exists'],
            'groups': groups,
        }

    return {'sets': out}

# ################################################################################################################################

def get_demo_config_states(server:'ParallelServer') -> 'strbooldict':
    """ Returns, for each demo config set, whether its objects currently exist in the environment.
    """
    details = get_demo_config_details(server)

    # Our response to produce
    out:'strbooldict' = {}

    for set_name, set_info in details['sets'].items():
        out[set_name] = set_info['is_present']

    return out

# ################################################################################################################################

def save_demo_config(server:'ParallelServer', states:'strbooldict') -> 'stranydict':
    """ Applies the desired states - a set slid on is imported, a set slid off has its objects
    removed and a set whose slider matches what exists is left alone.
    """
    current = get_demo_config_states(server)

    results:'stranydict' = {}
    imported:'strlist' = []
    removed:'strlist' = []
    failed:'strlist' = []

    for set_name in Set_Names:

        # A request may carry only some of the sets - the rest is left alone,
        # which is what lets sliders move independently at the same time
        if set_name not in states:
            continue

        desired = states[set_name]

        # What exists already matches the slider, so there is nothing to do ..
        if desired == current[set_name]:
            results[set_name] = {'action': 'unchanged', 'is_ok': True}
            continue

        # .. otherwise the slider says which way to go.
        if desired:
            action = 'imported'
            action_func = _import_funcs[set_name]
        else:
            action = 'removed'
            action_func = _remove_funcs[set_name]

        try:
            _ = action_func(server)
        except Exception:
            logger.warning('Demo config: could not apply `%s` -> %s', set_name, format_exc())
            results[set_name] = {'action': action, 'is_ok': False}
            failed.append(set_name)
        else:
            results[set_name] = {'action': action, 'is_ok': True}
            if desired:
                imported.append(set_name)
            else:
                removed.append(set_name)

    # The message names what was done, in the same words the actions use
    message_parts = []

    if imported:
        message_parts.append('Imported: {}'.format(', '.join(imported)))

    if removed:
        message_parts.append('Removed: {}'.format(', '.join(removed)))

    if failed:
        message_parts.append('Failed: {}'.format(', '.join(failed)))

    if not message_parts:
        message_parts.append('No changes to apply')

    # The details are read anew, so the cards show what actually exists now
    details_after = get_demo_config_details(server)

    out = {
        'success': not failed,
        'message': '. '.join(message_parts),
        'results': results,
        'sets': details_after['sets'],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def is_environment_empty(server:'ParallelServer') -> 'bool':
    """ Whether the environment holds no user-defined objects - nothing beyond what a new
    environment is created with.
    """
    with closing(server.odb.session()) as session:

        # Scheduler jobs - a new environment has none
        job_count = session.query(Job).\
            count()

        # REST objects - a new environment only has internal ones
        is_internal_column = cast_('any_', HTTPSOAP.is_internal)

        rest_count = session.query(HTTPSOAP).\
            filter(is_internal_column.is_(False)).\
            count()

        # Security definitions beyond the ones every new environment is created with
        security_count = session.query(SecurityBase).\
            filter(SecurityBase.name.notin_(_baseline_security_names)).\
            count()

        # Generic connections - a new environment only has the inactive alert
        # notification placeholders
        connection_count = session.query(GenericConn).\
            filter(GenericConn.is_internal.is_(False)).\
            filter(GenericConn.name != get_notification_conn_name()).\
            count()

        # Pub/sub topics - a new environment has none
        topic_count = session.query(PubSubTopic).\
            count()

        # SQL connections - a new environment has none
        sql_count = session.query(SQLConnectionPool).\
            count()

    total = job_count + rest_count + security_count + connection_count + topic_count + sql_count

    out = total == 0
    return out

# ################################################################################################################################

def has_user_services(server:'ParallelServer') -> 'bool':
    """ Whether the server has any user services to deploy - a hot-deployment source
    configured, an auto-deployment directory given on startup or files already waiting
    in the pickup directory.
    """

    # Project roots, hot-deployment directories and pickup stanzas all end up here
    if server.service_sources:
        return True

    # The zato start --deploy option points to user code as well
    if server.deploy_auto_from:
        return True

    # Anything already waiting in the pickup directory counts too
    pickup_files = get_python_files(server.hot_deploy_config.pickup_dir)
    pickup_file_count = len(pickup_files)

    out = pickup_file_count > 0
    return out

# ################################################################################################################################

def _claim_startup_marker(server:'ParallelServer') -> 'bool':
    """ Records that the first-start pass ran. Returns whether this call made the record,
    the unique index permits only one such record.
    """
    with closing(server.odb.session()) as session:

        wrapper = GenericObjectWrapper(session)
        wrapper.type_ = _marker_type

        # A marker from an earlier start means the pass already ran
        if wrapper.exists(_marker_name):
            return False

        opaque = dumps({'server': server.name})
        query = wrapper.create(_marker_name, opaque)

        try:
            _ = session.execute(query)
            session.commit()
        except IntegrityError:

            # The record already exists, so the pass is not run again
            session.rollback()
            return False

    return True

# ################################################################################################################################

def _get_requested_set_names(requested_set_names:'str') -> 'strlist':
    """ Turns the comma-separated set names from the environment into a list, in the order of Set_Names,
    so that a set is imported after the sets it builds on.
    """
    requested:'strlist' = []

    for name in requested_set_names.split(','):
        name = name.strip()

        if name not in Set_Names:
            raise Exception(f'Unknown demo config set `{name}` in {Env_First_Start_Set_Names}, expected one of {Set_Names}')

        requested.append(name)

    out:'strlist' = []

    for set_name in Set_Names:
        if set_name in requested:
            out.append(set_name)

    return out

# ################################################################################################################################

def import_demo_config_on_first_start(server:'ParallelServer') -> 'None':
    """ Imports the demo config sets from First_Start_Set_Names when a fresh environment starts
    for the first time - one with no user services to deploy and no user-defined objects yet.
    The sets named in the Env_First_Start_Set_Names variable are imported instead, whatever the environment has.
    The pass runs once per environment - a marker records that it ran, so removed demo config never
    comes back on a restart.
    """

    # Only the server that makes the record runs the pass ..
    if not _claim_startup_marker(server):
        return

    # .. sets named in the environment are imported in any case ..
    if requested_set_names := os.environ.get(Env_First_Start_Set_Names):
        set_names = _get_requested_set_names(requested_set_names)

    # .. otherwise, an environment that deploys its own user services is never touched ..
    elif has_user_services(server):
        logger.debug('Demo config: user services found, skipping the first-start import')
        return

    # .. neither is one that already holds anything user-defined ..
    elif not is_environment_empty(server):
        logger.debug('Demo config: skipping the first-start import')
        return

    # .. and a fresh one receives the default demo config sets.
    else:
        set_names = First_Start_Set_Names

    for set_name in set_names:

        import_func = _import_funcs[set_name]

        try:
            _ = import_func(server)
        except Exception:
            logger.warning('Demo config: could not import `%s` at first start -> %s', set_name, format_exc())
        else:
            logger.info('Demo config: imported `%s` at first start', set_name)

# ################################################################################################################################
# ################################################################################################################################
