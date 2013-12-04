# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from functools import wraps

# SQLAlchemy
from sqlalchemy import func
from sqlalchemy.sql.expression import case

# Zato
from zato.common import DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, \
     PARAMS_PRIORITY, URL_PARAMS_PRIORITY
from zato.common.odb.model import ChannelAMQP, ChannelWMQ, ChannelZMQ, Cluster, ConnDefAMQP, ConnDefWMQ, CronStyleJob, \
     DeliveryDefinitionBase, DeliveryDefinitionOutconnWMQ, Delivery, DeliveryHistory, DeliveryPayload, ElemPath, HTTPBasicAuth, \
     HTTPSOAP, HTTSOAPAudit, IntervalBasedJob, Job, MsgNamespace, OAuth, OutgoingAMQP, OutgoingFTP, OutgoingWMQ, OutgoingZMQ, \
     SecurityBase, Service, SQLConnectionPool, TechnicalAccount, XPath, WSSDefinition

logger = logging.getLogger(__name__)

def needs_columns(func):
    """ A decorator for queries which works out whether a given query function
    should return the result only or a column list retrieved in addition
    to the result. This is useful because some callers prefer the former and
    some need the latter.
    """
    @wraps(func)
    def inner(*args):
        # needs_columns is always the last argument so we don't have to look
        # it up using the 'inspect' module or anything like that.
        needs_columns = args[-1]

        q = func(*args)

        if needs_columns:
            return q.all(), q.statement.columns
        return q.all()

    return inner

# ##############################################################################

def internal_channel_list(session, cluster_id):
    """ All the HTTP/SOAP channels that point to internal services.
    """
    return session.query(
        HTTPSOAP.soap_action, Service.name).\
        filter(HTTPSOAP.cluster_id==Cluster.id).\
        filter(HTTPSOAP.service_id==Service.id).filter(Service.is_internal==True).filter(Cluster.id==cluster_id).filter(Cluster.id==HTTPSOAP.cluster_id) # noqa

# ##############################################################################

def _job(session, cluster_id):
    return session.query(
        Job.id, Job.name, Job.is_active,
        Job.job_type, Job.start_date, Job.extra,
        Service.name.label('service_name'), Service.impl_name.label('service_impl_name'),
        Service.id.label('service_id'),
        IntervalBasedJob.weeks, IntervalBasedJob.days,
        IntervalBasedJob.hours, IntervalBasedJob.minutes,
        IntervalBasedJob.seconds, IntervalBasedJob.repeats,
        CronStyleJob.cron_definition).\
        outerjoin(IntervalBasedJob, Job.id==IntervalBasedJob.job_id).\
        outerjoin(CronStyleJob, Job.id==CronStyleJob.job_id).\
        filter(Job.cluster_id==Cluster.id).\
        filter(Job.service_id==Service.id).\
        filter(Cluster.id==cluster_id).\
        order_by('job.name')

@needs_columns
def job_list(session, cluster_id, needs_columns=False):
    """ All the scheduler's jobs defined in the ODB.
    """
    return _job(session, cluster_id)

def job_by_name(session, cluster_id, name):
    """ A scheduler's job fetched by its name.
    """
    return _job(session, cluster_id).\
        filter(Job.name==name).\
        one()

# ##############################################################################

@needs_columns
def basic_auth_list(session, cluster_id, needs_columns=False):
    """ All the HTTP Basic Auth definitions.
    """
    return session.query(
        HTTPBasicAuth.id, HTTPBasicAuth.name,
        HTTPBasicAuth.is_active,
        HTTPBasicAuth.username, HTTPBasicAuth.realm,
        HTTPBasicAuth.password, HTTPBasicAuth.sec_type,
        HTTPBasicAuth.password_type).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==HTTPBasicAuth.cluster_id).\
        filter(SecurityBase.id==HTTPBasicAuth.id).\
        order_by('sec_base.name')

@needs_columns
def tech_acc_list(session, cluster_id, needs_columns=False):
    """ All the technical accounts.
    """
    return session.query(
        TechnicalAccount.id, TechnicalAccount.name,
        TechnicalAccount.is_active,
        TechnicalAccount.password, TechnicalAccount.salt,
        TechnicalAccount.sec_type, TechnicalAccount.password_type).\
        order_by(TechnicalAccount.name).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==TechnicalAccount.cluster_id).\
        filter(SecurityBase.id==TechnicalAccount.id).\
        order_by('sec_base.name')

@needs_columns
def oauth_list(session, cluster_id, needs_columns=False):
    """ All the OAuth definitions.
    """
    return session.query(
        OAuth.id, OAuth.name,
        OAuth.is_active,
        OAuth.username, OAuth.password,
        OAuth.proto_version, OAuth.sig_method,
        OAuth.max_nonce_log, OAuth.sec_type).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==OAuth.cluster_id).\
        filter(SecurityBase.id==OAuth.id).\
        order_by('sec_base.name')

@needs_columns
def wss_list(session, cluster_id, needs_columns=False):
    """ All the WS-Security definitions.
    """
    return session.query(
        WSSDefinition.id, WSSDefinition.name, WSSDefinition.is_active,
        WSSDefinition.username, WSSDefinition.password, WSSDefinition.password_type,
        WSSDefinition.reject_empty_nonce_creat, WSSDefinition.reject_stale_tokens,
        WSSDefinition.reject_expiry_limit, WSSDefinition.nonce_freshness_time,
        WSSDefinition.sec_type).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==WSSDefinition.cluster_id).\
        filter(SecurityBase.id==WSSDefinition.id).\
        order_by('sec_base.name')

# ##############################################################################

def _def_amqp(session, cluster_id):
    return session.query(
        ConnDefAMQP.name, ConnDefAMQP.id, ConnDefAMQP.host,
        ConnDefAMQP.port, ConnDefAMQP.vhost, ConnDefAMQP.username,
        ConnDefAMQP.frame_max, ConnDefAMQP.heartbeat, ConnDefAMQP.password).\
        filter(ConnDefAMQP.def_type=='amqp').\
        filter(Cluster.id==ConnDefAMQP.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(ConnDefAMQP.name)

def def_amqp(session, cluster_id, id):
    """ A particular AMQP definition
    """
    return _def_amqp(session, cluster_id).\
        filter(ConnDefAMQP.id==id).\
        one()

@needs_columns
def def_amqp_list(session, cluster_id, needs_columns=False):
    """ AMQP connection definitions.
    """
    return _def_amqp(session, cluster_id)

# ##############################################################################

def _def_jms_wmq(session, cluster_id):
    return session.query(
        ConnDefWMQ.id, ConnDefWMQ.name, ConnDefWMQ.host,
        ConnDefWMQ.port, ConnDefWMQ.queue_manager, ConnDefWMQ.channel,
        ConnDefWMQ.cache_open_send_queues, ConnDefWMQ.cache_open_receive_queues,
        ConnDefWMQ.use_shared_connections, ConnDefWMQ.ssl, ConnDefWMQ.ssl_cipher_spec,
        ConnDefWMQ.ssl_key_repository, ConnDefWMQ.needs_mcd, ConnDefWMQ.max_chars_printed).\
        filter(Cluster.id==ConnDefWMQ.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(ConnDefWMQ.name)

def def_jms_wmq(session, cluster_id, id):
    """ A particular JMS WebSphere MQ definition
    """
    return _def_jms_wmq(session, cluster_id).\
        filter(ConnDefWMQ.id==id).\
        one()

@needs_columns
def def_jms_wmq_list(session, cluster_id, needs_columns=False):
    """ JMS WebSphere MQ connection definitions.
    """
    return _def_jms_wmq(session, cluster_id)

# ##############################################################################

def _out_amqp(session, cluster_id):
    return session.query(
        OutgoingAMQP.id, OutgoingAMQP.name, OutgoingAMQP.is_active,
        OutgoingAMQP.delivery_mode, OutgoingAMQP.priority, OutgoingAMQP.content_type,
        OutgoingAMQP.content_encoding, OutgoingAMQP.expiration, OutgoingAMQP.user_id,
        OutgoingAMQP.app_id, ConnDefAMQP.name.label('def_name'), OutgoingAMQP.def_id).\
        filter(OutgoingAMQP.def_id==ConnDefAMQP.id).\
        filter(ConnDefAMQP.id==OutgoingAMQP.def_id).\
        filter(Cluster.id==ConnDefAMQP.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(OutgoingAMQP.name)

def out_amqp(session, cluster_id, id):
    """ An outgoing AMQP connection.
    """
    return _out_amqp(session, cluster_id).\
        filter(OutgoingAMQP.id==id).\
        one()

@needs_columns
def out_amqp_list(session, cluster_id, needs_columns=False):
    """ Outgoing AMQP connections.
    """
    return _out_amqp(session, cluster_id)

# ##############################################################################

def _out_jms_wmq(session, cluster_id):
    return session.query(
        OutgoingWMQ.id, OutgoingWMQ.name, OutgoingWMQ.is_active,
        OutgoingWMQ.delivery_mode, OutgoingWMQ.priority, OutgoingWMQ.expiration,
        ConnDefWMQ.name.label('def_name'), OutgoingWMQ.def_id).\
        filter(OutgoingWMQ.def_id==ConnDefWMQ.id).\
        filter(ConnDefWMQ.id==OutgoingWMQ.def_id).\
        filter(Cluster.id==ConnDefWMQ.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(OutgoingWMQ.name)

def out_jms_wmq(session, cluster_id, id):
    """ An outgoing JMS WebSphere MQ connection (by ID).
    """
    return _out_jms_wmq(session, cluster_id).\
        filter(OutgoingWMQ.id==id).\
        one()

def out_jms_wmq_by_name(session, cluster_id, name):
    """ An outgoing JMS WebSphere MQ connection (by name).
    """
    return _out_jms_wmq(session, cluster_id).\
        filter(OutgoingWMQ.name==name).\
        first()

@needs_columns
def out_jms_wmq_list(session, cluster_id, needs_columns=False):
    """ Outgoing JMS WebSphere MQ connections.
    """
    return _out_jms_wmq(session, cluster_id)

# ##############################################################################

def _channel_amqp(session, cluster_id):
    return session.query(
        ChannelAMQP.id, ChannelAMQP.name, ChannelAMQP.is_active,
        ChannelAMQP.queue, ChannelAMQP.consumer_tag_prefix,
        ConnDefAMQP.name.label('def_name'), ChannelAMQP.def_id,
        ChannelAMQP.data_format,
        Service.name.label('service_name'),
        Service.impl_name.label('service_impl_name')).\
        filter(ChannelAMQP.def_id==ConnDefAMQP.id).\
        filter(ChannelAMQP.service_id==Service.id).\
        filter(Cluster.id==ConnDefAMQP.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(ChannelAMQP.name)

def channel_amqp(session, cluster_id, id):
    """ A particular AMQP channel.
    """
    return _channel_amqp(session, cluster_id).\
        filter(ChannelAMQP.id==id).\
        one()

@needs_columns
def channel_amqp_list(session, cluster_id, needs_columns=False):
    """ AMQP channels.
    """
    return _channel_amqp(session, cluster_id)

# ##############################################################################

def _channel_jms_wmq(session, cluster_id):
    return session.query(
        ChannelWMQ.id, ChannelWMQ.name, ChannelWMQ.is_active,
        ChannelWMQ.queue, ConnDefWMQ.name.label('def_name'), ChannelWMQ.def_id,
        ChannelWMQ.data_format, Service.name.label('service_name'),
        Service.impl_name.label('service_impl_name')).\
        filter(ChannelWMQ.def_id==ConnDefWMQ.id).\
        filter(ChannelWMQ.service_id==Service.id).\
        filter(Cluster.id==ConnDefWMQ.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(ChannelWMQ.name)

def channel_jms_wmq(session, cluster_id, id):
    """ A particular JMS WebSphere MQ channel.
    """
    return _channel_jms_wmq(session, cluster_id).\
        filter(ChannelWMQ.id==id).\
        one()

@needs_columns
def channel_jms_wmq_list(session, cluster_id, needs_columns=False):
    """ JMS WebSphere MQ channels.
    """
    return _channel_jms_wmq(session, cluster_id)

# ##############################################################################

def _out_zmq(session, cluster_id):
    return session.query(
        OutgoingZMQ.id, OutgoingZMQ.name, OutgoingZMQ.is_active,
        OutgoingZMQ.address, OutgoingZMQ.socket_type).\
        filter(Cluster.id==OutgoingZMQ.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(OutgoingZMQ.name)

def out_zmq(session, cluster_id, id):
    """ An outgoing ZeroMQ connection.
    """
    return _out_zmq(session, cluster_id).\
        filter(OutgoingZMQ.id==id).\
        one()

@needs_columns
def out_zmq_list(session, cluster_id, needs_columns=False):
    """ Outgoing ZeroMQ connections.
    """
    return _out_zmq(session, cluster_id)

# ##############################################################################

def _channel_zmq(session, cluster_id):
    return session.query(
        ChannelZMQ.id, ChannelZMQ.name, ChannelZMQ.is_active,
        ChannelZMQ.address, ChannelZMQ.socket_type, ChannelZMQ.sub_key, ChannelZMQ.data_format,
        Service.name.label('service_name'), Service.impl_name.label('service_impl_name')).\
        filter(Service.id==ChannelZMQ.service_id).\
        filter(Cluster.id==ChannelZMQ.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(ChannelZMQ.name)

def channel_zmq(session, cluster_id, id):
    """ An incoming ZeroMQ connection.
    """
    return _channel_zmq(session, cluster_id).\
        filter(ChannelZMQ.id==id).\
        one()

@needs_columns
def channel_zmq_list(session, cluster_id, needs_columns=False):
    """ Incoming ZeroMQ connections.
    """
    return _channel_zmq(session, cluster_id)

# ##############################################################################

def _http_soap(session, cluster_id):
    return session.query(
        HTTPSOAP.id, HTTPSOAP.name, HTTPSOAP.is_active,
        HTTPSOAP.is_internal, HTTPSOAP.transport, HTTPSOAP.host,
        HTTPSOAP.url_path, HTTPSOAP.method, HTTPSOAP.soap_action,
        HTTPSOAP.soap_version, HTTPSOAP.data_format, HTTPSOAP.security_id,
        HTTPSOAP.connection,
        case([(HTTPSOAP.ping_method != None, HTTPSOAP.ping_method)], else_=DEFAULT_HTTP_PING_METHOD).label('ping_method'), # noqa
        case([(HTTPSOAP.pool_size != None, HTTPSOAP.pool_size)], else_=DEFAULT_HTTP_POOL_SIZE).label('pool_size'),
        case([(HTTPSOAP.merge_url_params_req != None, HTTPSOAP.merge_url_params_req)], else_=True).label('merge_url_params_req'),
        case([(HTTPSOAP.url_params_pri != None, HTTPSOAP.url_params_pri)], else_=URL_PARAMS_PRIORITY.DEFAULT).label('url_params_pri'),
        case([(HTTPSOAP.params_pri != None, HTTPSOAP.params_pri)], else_=PARAMS_PRIORITY.DEFAULT).label('params_pri'),
        HTTPSOAP.audit_enabled,
        HTTPSOAP.audit_back_log,
        HTTPSOAP.audit_max_payload,
        HTTPSOAP.audit_repl_patt_type,
        SecurityBase.sec_type,
        Service.name.label('service_name'),
        Service.id.label('service_id'),
        Service.impl_name.label('service_impl_name'),
        SecurityBase.name.label('security_name'),
        SecurityBase.username.label('username'),
        SecurityBase.password.label('password'),
        SecurityBase.password_type.label('password_type'),).\
        outerjoin(Service, Service.id==HTTPSOAP.service_id).\
        outerjoin(SecurityBase, HTTPSOAP.security_id==SecurityBase.id).\
        filter(Cluster.id==HTTPSOAP.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(HTTPSOAP.name)

def http_soap_security_list(session, cluster_id, connection=None):
    """ HTTP/SOAP security definitions.
    """
    q = _http_soap(session, cluster_id)

    if connection:
        q = q.filter(HTTPSOAP.connection==connection)

    return q

def http_soap(session, cluster_id, id):
    """ An HTTP/SOAP connection.
    """
    return _http_soap(session, cluster_id).\
        filter(HTTPSOAP.id==id).\
        one()

@needs_columns
def http_soap_list(session, cluster_id, connection=None, transport=None, needs_columns=False):
    """ HTTP/SOAP connections, both channels and outgoing ones.
    """
    q = _http_soap(session, cluster_id)

    if connection:
        q = q.filter(HTTPSOAP.connection==connection)

    if transport:
        q = q.filter(HTTPSOAP.transport==transport)

    return q

# ##############################################################################

def _out_sql(session, cluster_id):
    return session.query(SQLConnectionPool).\
        filter(Cluster.id==SQLConnectionPool.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(SQLConnectionPool.name)

def out_sql(session, cluster_id, id):
    """ An outgoing SQL connection.
    """
    return _out_sql(session, cluster_id).\
        filter(SQLConnectionPool.id==id).\
        one()

@needs_columns
def out_sql_list(session, cluster_id, needs_columns=False):
    """ Outgoing SQL connections.
    """
    return _out_sql(session, cluster_id)

# ##############################################################################

def _out_ftp(session, cluster_id):
    return session.query(
        OutgoingFTP.id, OutgoingFTP.name, OutgoingFTP.is_active,
        OutgoingFTP.host, OutgoingFTP.port, OutgoingFTP.user, OutgoingFTP.password,
        OutgoingFTP.acct, OutgoingFTP.timeout, OutgoingFTP.dircache).\
        filter(Cluster.id==OutgoingFTP.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(OutgoingFTP.name)

def out_ftp(session, cluster_id, id):
    """ An outgoing FTP connection.
    """
    return _out_ftp(session, cluster_id).\
        filter(OutgoingFTP.id==id).\
        one()

@needs_columns
def out_ftp_list(session, cluster_id, needs_columns=False):
    """ Outgoing FTP connections.
    """
    return _out_ftp(session, cluster_id)

# ##############################################################################

def _service(session, cluster_id):
    return session.query(
        Service.id, Service.name, Service.is_active,
        Service.impl_name, Service.is_internal, Service.slow_threshold).\
        filter(Cluster.id==Service.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(Service.name)

def service(session, cluster_id, id):
    """ A service.
    """
    return _service(session, cluster_id).\
        filter(Service.id==id).\
        one()

@needs_columns
def service_list(session, cluster_id, needs_columns=False):
    """ All services.
    """
    return _service(session, cluster_id)

# ##############################################################################

def _delivery_definition(session, cluster_id):
    return session.query(DeliveryDefinitionBase).\
        filter(Cluster.id==DeliveryDefinitionBase.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(DeliveryDefinitionBase.name)

def delivery_definition_list(session, cluster_id, target_type=None):
    """ Returns a list of delivery definitions for a given target type.
    """
    def_list = _delivery_definition(session, cluster_id)

    if target_type:
        def_list = def_list.\
            filter(DeliveryDefinitionBase.target_type==target_type)

    return def_list

# ##############################################################################

def delivery_count_by_state(session, def_id):
    return session.query(Delivery.state, func.count(Delivery.state)).\
        filter(Delivery.definition_id==def_id).\
        group_by(Delivery.state)

def delivery_list(session, cluster_id, def_name, state, start=None, stop=None, needs_payload=False):
    columns = [
        DeliveryDefinitionBase.name.label('def_name'),
        DeliveryDefinitionBase.target_type,
        Delivery.task_id,
        Delivery.creation_time.label('creation_time_utc'),
        Delivery.last_used.label('last_used_utc'),
        Delivery.source_count,
        Delivery.target_count,
        Delivery.resubmit_count,
        Delivery.state,
        DeliveryDefinitionBase.retry_repeats,
        DeliveryDefinitionBase.check_after,
        DeliveryDefinitionBase.retry_seconds
    ]

    if needs_payload:
        columns.extend([DeliveryPayload.payload, Delivery.args, Delivery.kwargs])

    q = session.query(*columns).\
        filter(DeliveryDefinitionBase.id==Delivery.definition_id).\
        filter(DeliveryDefinitionBase.cluster_id==cluster_id).\
        filter(DeliveryDefinitionBase.name==def_name).\
        filter(Delivery.state.in_(state))

    if needs_payload:
        q = q.filter(DeliveryPayload.task_id==Delivery.task_id)

    if start:
        q = q.filter(Delivery.last_used >= start)

    if stop:
        q = q.filter(Delivery.last_used <= stop)

    q = q.order_by(Delivery.last_used.desc())

    return q

def delivery(session, task_id, target_def_class):
    return session.query(
        target_def_class.name.label('def_name'),
        target_def_class.target_type,
        Delivery.task_id,
        Delivery.creation_time.label('creation_time_utc'),
        Delivery.last_used.label('last_used_utc'),
        Delivery.source_count,
        Delivery.target_count,
        Delivery.resubmit_count,
        Delivery.state,
        target_def_class.retry_repeats,
        target_def_class.check_after,
        target_def_class.retry_seconds,
        DeliveryPayload.payload,
        Delivery.args,
        Delivery.kwargs,
        target_def_class.target,
        ).\
        filter(target_def_class.id==Delivery.definition_id).\
        filter(Delivery.task_id==task_id).\
        filter(DeliveryPayload.task_id==Delivery.task_id)

@needs_columns
def delivery_history_list(session, task_id, needs_columns=True):
    return session.query(
        DeliveryHistory.entry_type,
        DeliveryHistory.entry_time,
        DeliveryHistory.entry_ctx,
        DeliveryHistory.resubmit_count).\
        filter(DeliveryHistory.task_id==task_id).\
        order_by(DeliveryHistory.entry_time.desc())

# ##############################################################################

def _msg_list(class_, order_by, session, cluster_id, needs_columns=False):
    """ All the namespaces.
    """
    return session.query(
        class_.id, class_.name,
        class_.value).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==class_.cluster_id).\
        order_by(order_by)

@needs_columns
def namespace_list(session, cluster_id, needs_columns=False):
    """ All the namespaces.
    """
    return _msg_list(MsgNamespace, 'msg_ns.name', session, cluster_id, needs_columns)

@needs_columns
def xpath_list(session, cluster_id, needs_columns=False):
    """ All the XPaths.
    """
    return _msg_list(XPath, 'msg_xpath.name', session, cluster_id, needs_columns)

@needs_columns
def elem_path_list(session, cluster_id, needs_columns=False):
    """ All the ElemPaths.
    """
    return _msg_list(ElemPath, 'msg_elem_path.name', session, cluster_id, needs_columns)

# ################################################################################################################################

def _http_soap_audit(session, cluster_id, conn_id=None, start=None, stop=None, query=None, id=None, needs_req_payload=False):
    columns = [
        HTTSOAPAudit.id,
        HTTSOAPAudit.name.label('conn_name'),
        HTTSOAPAudit.cid,
        HTTSOAPAudit.transport,
        HTTSOAPAudit.connection,
        HTTSOAPAudit.req_time.label('req_time_utc'),
        HTTSOAPAudit.resp_time.label('resp_time_utc'),
        HTTSOAPAudit.user_token,
        HTTSOAPAudit.invoke_ok,
        HTTSOAPAudit.auth_ok,
        HTTSOAPAudit.remote_addr,
    ]

    if needs_req_payload:
        columns.extend([
            HTTSOAPAudit.req_headers, HTTSOAPAudit.req_payload, HTTSOAPAudit.resp_headers, HTTSOAPAudit.resp_payload
        ])

    q = session.query(*columns)
    
    if query:
        query = '%{}%'.format(query)
        q = q.filter(
            HTTSOAPAudit.cid.ilike(query) | \
            HTTSOAPAudit.req_headers.ilike(query) | HTTSOAPAudit.req_payload.ilike(query) | \
            HTTSOAPAudit.resp_headers.ilike(query) | HTTSOAPAudit.resp_payload.ilike(query)
        )

    if id:
        q = q.filter(HTTSOAPAudit.id == id)

    if conn_id:
        q = q.filter(HTTSOAPAudit.conn_id == conn_id)

    if start:
        q = q.filter(HTTSOAPAudit.req_time >= start)

    if stop:
        q = q.filter(HTTSOAPAudit.req_time <= start)

    q = q.order_by(HTTSOAPAudit.req_time.desc())

    return q

def http_soap_audit_item_list(session, cluster_id, conn_id, start, stop, query, needs_req_payload):
    return _http_soap_audit(session, cluster_id, conn_id, start, stop, query)

def http_soap_audit_item(session, cluster_id, id):
    return _http_soap_audit(session, cluster_id, id=id, needs_req_payload=True)

# ################################################################################################################################
