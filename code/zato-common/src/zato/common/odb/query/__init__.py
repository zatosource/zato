# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from functools import wraps

# Bunch
from bunch import bunchify

# SQLAlchemy
from sqlalchemy import and_, func, not_, or_
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import case

# Zato
from zato.common.api import CACHE, DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, GENERIC, HTTP_SOAP_SERIALIZATION_TYPE, \
     PARAMS_PRIORITY, PUBSUB, URL_PARAMS_PRIORITY
from zato.common.json_internal import loads
from zato.common.odb.model import AWSS3, APIKeySecurity, AWSSecurity, Cache, CacheBuiltin, CacheMemcached, CassandraConn, \
     CassandraQuery, ChannelAMQP, ChannelWebSocket, ChannelWMQ, ChannelZMQ, Cluster, ConnDefAMQP, ConnDefWMQ, \
     CronStyleJob, ElasticSearch, HTTPBasicAuth, HTTPSOAP, IMAP, IntervalBasedJob, Job, JSONPointer, JWT, \
     MsgNamespace, NotificationSQL as NotifSQL, NTLM, OAuth, OutgoingOdoo, \
     OutgoingAMQP, OutgoingFTP, OutgoingWMQ, OutgoingZMQ, PubSubEndpoint, \
     PubSubEndpointTopic, PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubSubscription, PubSubTopic, RBACClientRole, \
     RBACPermission, RBACRole, RBACRolePermission, SecurityBase, Server, Service, SMSTwilio, SMTP, Solr, SQLConnectionPool, \
     TLSCACert, TLSChannelSecurity, TLSKeyCertSecurity, WebSocketClient, WebSocketClientPubSubKeys, WebSocketSubscription, \
     WSSDefinition, VaultConnection, XPath, XPathSecurity, OutgoingSAP
from zato.common.util.search import SearchResults as _SearchResults

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

_not_given = object()
_no_page_limit = 2 ** 24 # ~16.7 million results, tops
_gen_attr = GENERIC.ATTR_NAME

# ################################################################################################################################

def count(session, q):
    _q = q.statement.with_only_columns([func.count()]).order_by(None)
    return session.execute(_q).scalar()

# ################################################################################################################################

class _QueryConfig:

    @staticmethod
    def supports_kwargs(query_func):
        """ Returns True if the given query func supports kwargs, False otherwise.
        """
        return query_func in (
            http_soap_list,
        )

# ################################################################################################################################

class _SearchWrapper(object):
    """ Wraps results in pagination and/or filters out objects by their name or other attributes.
    """
    def __init__(self, q, default_page_size=_no_page_limit, **config):

        # Apply WHERE conditions
        where = config.get('where') or _not_given
        if where is not _not_given:
            q = q.filter(where)
        else:

            # If there are multiple filters, they are by default OR-joined
            # to ease in look ups over more than one column.
            filter_op = and_ if config.get('filter_op') == 'and' else or_
            filters = []

            for filter_by in config.get('filter_by', []):
                for criterion in config.get('query', []):
                    filters.append(filter_by.contains(criterion))

            q = q.filter(filter_op(*filters))

        # Total number of results
        total_q = q.statement.with_only_columns([func.count()]).order_by(None)
        self.total = q.session.execute(total_q).scalar()

        # Pagination
        page_size = config.get('page_size', default_page_size)
        cur_page = config.get('cur_page', 0)

        slice_from = cur_page * page_size
        slice_to = slice_from + page_size

        self.q = q.slice(slice_from, slice_to)

# ################################################################################################################################

def query_wrapper(func):
    """ A decorator for queries which works out whether a given query function should return the result only
    or a column list retrieved in addition to the result. This is useful because some callers prefer the former
    and some need the latter. Also, paginates the results if requested to by the caller.
    """
    @wraps(func)
    def inner(*args, **kwargs):

        # Each query function will have the last argument either False or True
        # depending on whether columns are needed or not.
        needs_columns = args[-1]

        if _QueryConfig.supports_kwargs(func):
            result = func(*args, **kwargs)
        else:
            result = func(*args)

        tool = _SearchWrapper(result, **kwargs)
        result = _SearchResults(tool.q, tool.q.all(), tool.q.statement.columns, tool.total)

        if needs_columns:
            return result, result.columns

        return result

    return inner

# ################################################################################################################################

def bunch_maker(func):
    """ Turns SQLAlchemy rows into bunch instances, taking opaque elements into account.
    """
    @wraps(func)
    def inner(*args, **kwargs):

        result = func(*args, **kwargs)
        out = bunchify(result._asdict())

        opaque = out.pop(_gen_attr, None)
        if opaque:
            opaque = loads(opaque)
            out.update(opaque)

        return out

    return inner

# ################################################################################################################################

def internal_channel_list(session, cluster_id):
    """ All the HTTP/SOAP channels that point to internal services.
    """
    return session.query(
        HTTPSOAP.soap_action, Service.name).\
        filter(HTTPSOAP.cluster_id==Cluster.id).\
        filter(HTTPSOAP.service_id==Service.id).\
        filter(Service.is_internal==True).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==HTTPSOAP.cluster_id) # noqa: E712

# ################################################################################################################################

def _job(session, cluster_id):
    return session.query(
        Job.id,
        Job.name,
        Job.is_active,
        Job.job_type,
        Job.start_date,
        Job.extra,
        Service.name.label('service_name'),
        Service.impl_name.label('service_impl_name'),
        Service.id.label('service_id'),
        IntervalBasedJob.weeks,
        IntervalBasedJob.days,
        IntervalBasedJob.hours,
        IntervalBasedJob.minutes,
        IntervalBasedJob.seconds,
        IntervalBasedJob.repeats,
        CronStyleJob.cron_definition
        ).\
        outerjoin(IntervalBasedJob, Job.id==IntervalBasedJob.job_id).\
        outerjoin(CronStyleJob, Job.id==CronStyleJob.job_id).\
        filter(Job.cluster_id==Cluster.id).\
        filter(Job.service_id==Service.id).\
        filter(Cluster.id==cluster_id)

@query_wrapper
def job_list(session, cluster_id, service_name=None, needs_columns=False):
    """ All the scheduler's jobs defined in the ODB.
    """
    q = _job(session, cluster_id)

    if service_name:
        q = q.filter(Service.name==service_name)

    return q.\
        order_by(Job.name)

def job_by_id(session, cluster_id, job_id):
    """ A scheduler's job fetched by its ID.
    """
    return _job(session, cluster_id).\
        filter(Job.id==job_id).\
        one()

def job_by_name(session, cluster_id, name):
    """ A scheduler's job fetched by its name.
    """
    return _job(session, cluster_id).\
        filter(Job.name==name).\
        one()

# ################################################################################################################################

def _sec_base(session, cluster_id):
    return session.query(
        SecurityBase.id,
        SecurityBase.is_active,
        SecurityBase.sec_type,
        SecurityBase.name,
        SecurityBase.username).\
        filter(SecurityBase.cluster_id==Cluster.id).\
        filter(Cluster.id==cluster_id)

def sec_base(session, cluster_id, sec_base_id):
    return _sec_base(session, cluster_id).\
        filter(SecurityBase.id==sec_base_id).\
        one()

@query_wrapper
def apikey_security_list(session, cluster_id, needs_columns=False):
    """ All the API keys.
    """
    return session.query(
        APIKeySecurity.id,
        APIKeySecurity.name,
        APIKeySecurity.is_active,
        APIKeySecurity.username,
        APIKeySecurity.password,
        APIKeySecurity.sec_type,
        APIKeySecurity.opaque1,
        ).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==APIKeySecurity.cluster_id).\
        filter(SecurityBase.id==APIKeySecurity.id).\
        order_by(SecurityBase.name)

@query_wrapper
def aws_security_list(session, cluster_id, needs_columns=False):
    """ All the Amazon security definitions.
    """
    return session.query(
        AWSSecurity.id, AWSSecurity.name,
        AWSSecurity.is_active,
        AWSSecurity.username,
        AWSSecurity.password, AWSSecurity.sec_type).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==AWSSecurity.cluster_id).\
        filter(SecurityBase.id==AWSSecurity.id).\
        order_by(SecurityBase.name)

@query_wrapper
def basic_auth_list(session, cluster_id, cluster_name, needs_columns=False):
    """ All the HTTP Basic Auth definitions.
    """
    q = session.query(
        HTTPBasicAuth.id,
        HTTPBasicAuth.name,
        HTTPBasicAuth.is_active,
        HTTPBasicAuth.username,
        HTTPBasicAuth.realm,
        HTTPBasicAuth.password,
        HTTPBasicAuth.sec_type,
        HTTPBasicAuth.password_type,
        HTTPBasicAuth.opaque1,
        Cluster.id.label('cluster_id'), Cluster.name.label('cluster_name')).\
        filter(Cluster.id==HTTPBasicAuth.cluster_id)

    if cluster_id:
        q = q.filter(Cluster.id==cluster_id)
    else:
        q = q.filter(Cluster.name==cluster_name)

    q = q.filter(SecurityBase.id==HTTPBasicAuth.id).\
        order_by(SecurityBase.name)

    return q

def _jwt(session, cluster_id, cluster_name, needs_columns=False):
    """ All the JWT definitions.
    """
    q = session.query(
        JWT.id,
        JWT.name,
        JWT.is_active,
        JWT.username,
        JWT.password,
        JWT.ttl,
        JWT.sec_type,
        JWT.password_type,
        JWT.opaque1,
        Cluster.id.label('cluster_id'),
        Cluster.name.label('cluster_name')).\
        filter(Cluster.id==JWT.cluster_id)

    if cluster_id:
        q = q.filter(Cluster.id==cluster_id)
    else:
        q = q.filter(Cluster.name==cluster_name)

    q = q.filter(SecurityBase.id==JWT.id).\
        order_by(SecurityBase.name)

    return q

@query_wrapper
def jwt_list(*args, **kwargs):
    return _jwt(*args, **kwargs)

def jwt_by_username(session, cluster_id, username, needs_columns=False):
    """ An individual JWT definition by its username.
    """
    return _jwt(session, cluster_id, None, needs_columns).\
        filter(JWT.username==username).\
        one()

@query_wrapper
def ntlm_list(session, cluster_id, needs_columns=False):
    """ All the NTLM definitions.
    """
    return session.query(
        NTLM.id, NTLM.name,
        NTLM.is_active,
        NTLM.username,
        NTLM.password, NTLM.sec_type,
        NTLM.password_type).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==NTLM.cluster_id).\
        filter(SecurityBase.id==NTLM.id).\
        order_by(SecurityBase.name)

@query_wrapper
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
        order_by(SecurityBase.name)

@query_wrapper
def tls_ca_cert_list(session, cluster_id, needs_columns=False):
    """ TLS CA certs.
    """
    return session.query(TLSCACert).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==TLSCACert.cluster_id).\
        order_by(TLSCACert.name)

@query_wrapper
def tls_channel_sec_list(session, cluster_id, needs_columns=False):
    """ TLS-based channel security.
    """
    return session.query(
        TLSChannelSecurity.id, TLSChannelSecurity.name,
        TLSChannelSecurity.is_active, TLSChannelSecurity.value,
        TLSChannelSecurity.sec_type).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==TLSChannelSecurity.cluster_id).\
        filter(SecurityBase.id==TLSChannelSecurity.id).\
        order_by(SecurityBase.name)

@query_wrapper
def tls_key_cert_list(session, cluster_id, needs_columns=False):
    """ TLS key/cert pairs.
    """
    return session.query(
        TLSKeyCertSecurity.id, TLSKeyCertSecurity.name,
        TLSKeyCertSecurity.is_active, TLSKeyCertSecurity.info,
        TLSKeyCertSecurity.auth_data, TLSKeyCertSecurity.sec_type).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==TLSKeyCertSecurity.cluster_id).\
        filter(SecurityBase.id==TLSKeyCertSecurity.id).\
        order_by(SecurityBase.name)

@query_wrapper
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
        order_by(SecurityBase.name)

@query_wrapper
def xpath_sec_list(session, cluster_id, needs_columns=False):
    """ All the XPath security definitions.
    """
    return session.query(
        XPathSecurity.id, XPathSecurity.name, XPathSecurity.is_active, XPathSecurity.username, XPathSecurity.username_expr,
        XPathSecurity.password_expr, XPathSecurity.password, XPathSecurity.sec_type).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==XPathSecurity.cluster_id).\
        filter(SecurityBase.id==XPathSecurity.id).\
        order_by(SecurityBase.name)

# ################################################################################################################################

def _definition_amqp(session, cluster_id):
    return session.query(
        ConnDefAMQP.name, ConnDefAMQP.id, ConnDefAMQP.host,
        ConnDefAMQP.port, ConnDefAMQP.vhost, ConnDefAMQP.username,
        ConnDefAMQP.frame_max, ConnDefAMQP.heartbeat, ConnDefAMQP.password).\
        filter(Cluster.id==ConnDefAMQP.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(ConnDefAMQP.name)

def definition_amqp(session, cluster_id, id):
    """ A particular AMQP definition
    """
    return _definition_amqp(session, cluster_id).\
        filter(ConnDefAMQP.id==id).\
        one()

@query_wrapper
def definition_amqp_list(session, cluster_id, needs_columns=False):
    """ AMQP connection definitions.
    """
    return _definition_amqp(session, cluster_id)

# ################################################################################################################################

def _def_wmq(session, cluster_id):
    return session.query(
        ConnDefWMQ.id, ConnDefWMQ.name, ConnDefWMQ.host,
        ConnDefWMQ.port, ConnDefWMQ.queue_manager, ConnDefWMQ.channel,
        ConnDefWMQ.cache_open_send_queues, ConnDefWMQ.cache_open_receive_queues,
        ConnDefWMQ.use_shared_connections, ConnDefWMQ.ssl, ConnDefWMQ.ssl_cipher_spec,
        ConnDefWMQ.ssl_key_repository, ConnDefWMQ.needs_mcd, ConnDefWMQ.max_chars_printed,
        ConnDefWMQ.username, ConnDefWMQ.password, ConnDefWMQ.use_jms).\
        filter(Cluster.id==ConnDefWMQ.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(ConnDefWMQ.name)

def definition_wmq(session, cluster_id, id):
    """ A particular IBM MQ definition
    """
    return _def_wmq(session, cluster_id).\
        filter(ConnDefWMQ.id==id).\
        one()

@query_wrapper
def definition_wmq_list(session, cluster_id, needs_columns=False):
    """ IBM MQ connection definitions.
    """
    return _def_wmq(session, cluster_id)

# ################################################################################################################################

def _out_amqp(session, cluster_id):
    return session.query(
        OutgoingAMQP.id, OutgoingAMQP.name, OutgoingAMQP.is_active,
        OutgoingAMQP.delivery_mode, OutgoingAMQP.priority, OutgoingAMQP.content_type,
        OutgoingAMQP.content_encoding, OutgoingAMQP.expiration, OutgoingAMQP.pool_size, OutgoingAMQP.user_id,
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

@query_wrapper
def out_amqp_list(session, cluster_id, needs_columns=False):
    """ Outgoing AMQP connections.
    """
    return _out_amqp(session, cluster_id)

# ################################################################################################################################

def _out_wmq(session, cluster_id):
    return session.query(
        OutgoingWMQ.id, OutgoingWMQ.name, OutgoingWMQ.is_active,
        OutgoingWMQ.delivery_mode, OutgoingWMQ.priority, OutgoingWMQ.expiration,
        ConnDefWMQ.name.label('def_name'), OutgoingWMQ.def_id).\
        filter(OutgoingWMQ.def_id==ConnDefWMQ.id).\
        filter(ConnDefWMQ.id==OutgoingWMQ.def_id).\
        filter(Cluster.id==ConnDefWMQ.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(OutgoingWMQ.name)

def out_wmq(session, cluster_id, id):
    """ An outgoing IBM MQ connection (by ID).
    """
    return _out_wmq(session, cluster_id).\
        filter(OutgoingWMQ.id==id).\
        one()

def out_wmq_by_name(session, cluster_id, name):
    """ An outgoing IBM MQ connection (by name).
    """
    return _out_wmq(session, cluster_id).\
        filter(OutgoingWMQ.name==name).\
        first()

@query_wrapper
def out_wmq_list(session, cluster_id, needs_columns=False):
    """ Outgoing IBM MQ connections.
    """
    return _out_wmq(session, cluster_id)

# ################################################################################################################################

def _channel_amqp(session, cluster_id):
    return session.query(
        ChannelAMQP.id, ChannelAMQP.name, ChannelAMQP.is_active,
        ChannelAMQP.queue, ChannelAMQP.consumer_tag_prefix,
        ConnDefAMQP.name.label('def_name'), ChannelAMQP.def_id,
        ChannelAMQP.pool_size, ChannelAMQP.ack_mode, ChannelAMQP.prefetch_count,
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

@query_wrapper
def channel_amqp_list(session, cluster_id, needs_columns=False):
    """ AMQP channels.
    """
    return _channel_amqp(session, cluster_id)

# ################################################################################################################################

def _channel_wmq(session, cluster_id):
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

def channel_wmq(session, cluster_id, id):
    """ A particular IBM MQ channel.
    """
    return _channel_wmq(session, cluster_id).\
        filter(ChannelWMQ.id==id).\
        one()

@query_wrapper
def channel_wmq_list(session, cluster_id, needs_columns=False):
    """ IBM MQ channels.
    """
    return _channel_wmq(session, cluster_id)

# ################################################################################################################################

def _out_zmq(session, cluster_id):
    return session.query(
        OutgoingZMQ.id, OutgoingZMQ.name, OutgoingZMQ.is_active,
        OutgoingZMQ.address, OutgoingZMQ.socket_type, OutgoingZMQ.socket_method).\
        filter(Cluster.id==OutgoingZMQ.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(OutgoingZMQ.name)

def out_zmq(session, cluster_id, id):
    """ An outgoing ZeroMQ connection.
    """
    return _out_zmq(session, cluster_id).\
        filter(OutgoingZMQ.id==id).\
        one()

@query_wrapper
def out_zmq_list(session, cluster_id, needs_columns=False):
    """ Outgoing ZeroMQ connections.
    """
    return _out_zmq(session, cluster_id)

# ################################################################################################################################

def _channel_zmq(session, cluster_id):
    return session.query(
        ChannelZMQ.id, ChannelZMQ.name, ChannelZMQ.is_active,
        ChannelZMQ.address, ChannelZMQ.socket_type, ChannelZMQ.socket_method, ChannelZMQ.sub_key,
        ChannelZMQ.pool_strategy, ChannelZMQ.service_source, ChannelZMQ.data_format,
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

@query_wrapper
def channel_zmq_list(session, cluster_id, needs_columns=False):
    """ Incoming ZeroMQ connections.
    """
    return _channel_zmq(session, cluster_id)

# ################################################################################################################################

def _http_soap(session, cluster_id):
    return session.query(
        HTTPSOAP.id,
        HTTPSOAP.name,
        HTTPSOAP.is_active,
        HTTPSOAP.is_internal,
        HTTPSOAP.transport,
        HTTPSOAP.host,
        HTTPSOAP.url_path,
        HTTPSOAP.method,
        HTTPSOAP.soap_action,
        HTTPSOAP.soap_version,
        HTTPSOAP.data_format,
        HTTPSOAP.security_id,
        HTTPSOAP.has_rbac,
        HTTPSOAP.connection,
        HTTPSOAP.content_type,
        case([(HTTPSOAP.ping_method != None, HTTPSOAP.ping_method)], else_=DEFAULT_HTTP_PING_METHOD).label('ping_method'), # noqa
        case([(HTTPSOAP.pool_size != None, HTTPSOAP.pool_size)], else_=DEFAULT_HTTP_POOL_SIZE).label('pool_size'),
        case([(HTTPSOAP.merge_url_params_req != None, HTTPSOAP.merge_url_params_req)], else_=True).label('merge_url_params_req'),
        case([(HTTPSOAP.url_params_pri != None, HTTPSOAP.url_params_pri)], else_=URL_PARAMS_PRIORITY.DEFAULT).label('url_params_pri'),
        case([(HTTPSOAP.params_pri != None, HTTPSOAP.params_pri)], else_=PARAMS_PRIORITY.DEFAULT).label('params_pri'),
        case([(
            HTTPSOAP.serialization_type != None, HTTPSOAP.serialization_type)],
             else_=HTTP_SOAP_SERIALIZATION_TYPE.DEFAULT.id).label('serialization_type'),
        HTTPSOAP.timeout,
        HTTPSOAP.sec_tls_ca_cert_id,
        HTTPSOAP.sec_use_rbac,
        HTTPSOAP.cache_id,
        HTTPSOAP.cache_expiry,
        HTTPSOAP.content_encoding,
        HTTPSOAP.opaque1,
        Cache.name.label('cache_name'),
        Cache.cache_type,
        TLSCACert.name.label('sec_tls_ca_cert_name'),
        SecurityBase.sec_type,
        Service.name.label('service_name'),
        Service.id.label('service_id'),
        Service.impl_name.label('service_impl_name'),
        SecurityBase.name.label('security_name'),
        SecurityBase.username.label('username'),
        SecurityBase.password.label('password'),
        SecurityBase.password_type.label('password_type'),).\
        outerjoin(Service, Service.id==HTTPSOAP.service_id).\
        outerjoin(Cache, Cache.id==HTTPSOAP.cache_id).\
        outerjoin(TLSCACert, TLSCACert.id==HTTPSOAP.sec_tls_ca_cert_id).\
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

def http_soap(session, cluster_id, item_id=None, name=None):
    """ An HTTP/SOAP connection.
    """
    q = _http_soap(session, cluster_id)

    if item_id:
        q = q.filter(HTTPSOAP.id==item_id)
    elif name:
        q = q.filter(HTTPSOAP.name==name)
    else:
        raise Exception('Exactly one of \'id\' or \'name\' is required')

    return q.one()

@query_wrapper
def http_soap_list(session, cluster_id, connection=None, transport=None, return_internal=True, data_format=None,
    needs_columns=False, *args, **kwargs):
    """ HTTP/SOAP connections, both channels and outgoing ones.
    """
    q = _http_soap(session, cluster_id)

    if connection:
        q = q.filter(HTTPSOAP.connection==connection)

    if transport:
        q = q.filter(HTTPSOAP.transport==transport)

    if not return_internal:
        q = q.filter(not_(HTTPSOAP.name.startswith('zato')))

    if data_format:
        q = q.filter(HTTPSOAP.data_format.startswith(data_format))

    return q

# ################################################################################################################################

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

@query_wrapper
def out_sql_list(session, cluster_id, needs_columns=False):
    """ Outgoing SQL connections.
    """
    return _out_sql(session, cluster_id)

# ################################################################################################################################

def _out_ftp(session, cluster_id):
    return session.query(
        OutgoingFTP.id,
        OutgoingFTP.name,
        OutgoingFTP.is_active,
        OutgoingFTP.host,
        OutgoingFTP.port,
        OutgoingFTP.user,
        OutgoingFTP.password,
        OutgoingFTP.acct,
        OutgoingFTP.timeout,
        OutgoingFTP.dircache,
        OutgoingFTP.opaque1,
        ).\
        filter(Cluster.id==OutgoingFTP.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(OutgoingFTP.name)

def out_ftp(session, cluster_id, id):
    """ An outgoing FTP connection.
    """
    return _out_ftp(session, cluster_id).\
        filter(OutgoingFTP.id==id).\
        one()

@query_wrapper
def out_ftp_list(session, cluster_id, needs_columns=False):
    """ Outgoing FTP connections.
    """
    return _out_ftp(session, cluster_id)

# ################################################################################################################################

def _service(session, cluster_id):
    return session.query(
        Service.id,
        Service.name,
        Service.is_active,
        Service.impl_name,
        Service.is_internal,
        Service.slow_threshold,
        Service.opaque1,
        ).\
        filter(Cluster.id==Service.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(Service.name)

def service(session, cluster_id, id=None, name=None):
    """ A service.
    """
    q = _service(session, cluster_id)

    if name:
        q = q.filter(Service.name==name)
    elif id:
        q = q.filter(Service.id==id)

    return q.one()

@query_wrapper
def service_list(session, cluster_id, return_internal=True, include_list=None, needs_columns=False):
    """ All services.
    """
    q = _service(session, cluster_id)

    if include_list:
        q = q.filter(or_(Service.name.in_(include_list)))
    else:
        if not return_internal:
            q = q.filter(not_(Service.name.startswith('zato')))

    return q

@query_wrapper
def service_list_with_include(session, cluster_id, include_list, needs_columns=False):
    q = _service(session, cluster_id)
    return q.filter(Service.name.in_(include_list))

def service_id_list(session, cluster_id, name_list=None):
    return session.query(
        Service.id,
        Service.impl_name).\
        filter(Cluster.id==Service.cluster_id).\
        filter(Cluster.id==cluster_id).\
        filter(Service.name.in_(name_list))

# ################################################################################################################################

def _msg_list(class_, order_by, session, cluster_id, needs_columns=False):
    """ All the namespaces.
    """
    return session.query(
        class_.id, class_.name,
        class_.value).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==class_.cluster_id).\
        order_by(order_by)

@query_wrapper
def namespace_list(session, cluster_id, needs_columns=False):
    """ All the namespaces.
    """
    return _msg_list(MsgNamespace, MsgNamespace.name, session, cluster_id, query_wrapper)

@query_wrapper
def xpath_list(session, cluster_id, needs_columns=False):
    """ All the XPaths.
    """
    return _msg_list(XPath, XPath.name, session, cluster_id, query_wrapper)

@query_wrapper
def json_pointer_list(session, cluster_id, needs_columns=False):
    """ All the JSON Pointers.
    """
    return _msg_list(JSONPointer, JSONPointer.name, session, cluster_id, query_wrapper)

# ################################################################################################################################

def _cloud_aws_s3(session, cluster_id):
    return session.query(
        AWSS3.id, AWSS3.name, AWSS3.is_active, AWSS3.pool_size, AWSS3.address, AWSS3.debug_level, AWSS3.suppr_cons_slashes,
        AWSS3.content_type, AWSS3.metadata_, AWSS3.security_id, AWSS3.bucket, AWSS3.encrypt_at_rest, AWSS3.storage_class,
        SecurityBase.username, SecurityBase.password).\
        filter(Cluster.id==cluster_id).\
        filter(AWSS3.security_id==SecurityBase.id).\
        order_by(AWSS3.name)

def cloud_aws_s3(session, cluster_id, id):
    """ An AWS S3 connection.
    """
    return _cloud_aws_s3(session, cluster_id).\
        filter(AWSS3.id==id).\
        one()

@query_wrapper
def cloud_aws_s3_list(session, cluster_id, needs_columns=False):
    """ AWS S3 connections.
    """
    return _cloud_aws_s3(session, cluster_id)

# ################################################################################################################################

def _pubsub_endpoint(session, cluster_id):
    return session.query(
        PubSubEndpoint.id,
        PubSubEndpoint.name,
        PubSubEndpoint.endpoint_type,
        PubSubEndpoint.is_active,
        PubSubEndpoint.is_internal,
        PubSubEndpoint.role,
        PubSubEndpoint.tags,
        PubSubEndpoint.topic_patterns,
        PubSubEndpoint.pub_tag_patterns,
        PubSubEndpoint.message_tag_patterns,
        PubSubEndpoint.security_id,
        PubSubEndpoint.ws_channel_id,
        SecurityBase.sec_type,
        SecurityBase.name.label('sec_name'),
        Service.id.label('service_id'),
        Service.name.label('service_name'),
        ChannelWebSocket.name.label('ws_channel_name'),
        ).\
        outerjoin(SecurityBase, SecurityBase.id==PubSubEndpoint.security_id).\
        outerjoin(Service, PubSubEndpoint.id==PubSubEndpoint.service_id).\
        outerjoin(ChannelWebSocket, ChannelWebSocket.id==PubSubEndpoint.ws_channel_id).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==PubSubEndpoint.cluster_id).\
        order_by(PubSubEndpoint.id)

def pubsub_endpoint(session, cluster_id, id):
    """ An individual pub/sub endpoint.
    """
    return _pubsub_endpoint(session, cluster_id).\
        filter(PubSubEndpoint.id==id).\
        one()

@query_wrapper
def pubsub_endpoint_list(session, cluster_id, needs_columns=False):
    """ A list of pub/sub endpoints.
    """
    return _pubsub_endpoint(session, cluster_id)

# ################################################################################################################################

def _pubsub_topic(session, cluster_id):
    return session.query(
        PubSubTopic.id,
        PubSubTopic.name,
        PubSubTopic.is_active,
        PubSubTopic.is_internal,
        PubSubTopic.max_depth_gd,
        PubSubTopic.max_depth_non_gd,
        PubSubTopic.has_gd,
        PubSubTopic.is_api_sub_allowed,
        PubSubTopic.depth_check_freq,
        PubSubTopic.hook_service_id,
        PubSubTopic.pub_buffer_size_gd,
        PubSubTopic.task_sync_interval,
        PubSubTopic.task_delivery_interval,
        PubSubTopic.opaque1,
        Service.name.label('hook_service_name'),
        ).\
        outerjoin(Service, Service.id==PubSubTopic.hook_service_id).\
        filter(Cluster.id==PubSubTopic.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(PubSubTopic.name)

@bunch_maker
def pubsub_topic(session, cluster_id, id):
    """ A pub/sub topic.
    """
    return _pubsub_topic(session, cluster_id).\
        filter(PubSubTopic.id==id).\
        one()

@query_wrapper
def pubsub_topic_list(session, cluster_id, needs_columns=False):
    """ All pub/sub topics.
    """
    return _pubsub_topic(session, cluster_id)

# ################################################################################################################################

def pubsub_publishers_for_topic(session, cluster_id, topic_id):
    return session.query(
        PubSubEndpoint.service_id, PubSubEndpoint.security_id,
        PubSubEndpoint.ws_channel_id, PubSubEndpoint.name,
        PubSubEndpoint.is_active, PubSubEndpoint.is_internal,
        PubSubEndpoint.last_seen, PubSubEndpoint.last_pub_time,
        PubSubEndpointTopic.last_pub_time,
        PubSubEndpointTopic.pub_msg_id.label('last_msg_id'),
        PubSubEndpointTopic.pub_correl_id.label('last_correl_id'),
        PubSubEndpointTopic.in_reply_to.label('last_in_reply_to'),
        PubSubEndpointTopic.ext_client_id,
        Service.name.label('service_name'),
        SecurityBase.name.label('sec_name'),
        ChannelWebSocket.name.label('ws_channel_name'),
        ).\
        outerjoin(Service, Service.id==PubSubEndpoint.service_id).\
        outerjoin(SecurityBase, SecurityBase.id==PubSubEndpoint.security_id).\
        outerjoin(ChannelWebSocket, ChannelWebSocket.id==PubSubEndpoint.ws_channel_id).\
        filter(PubSubEndpointTopic.topic_id==PubSubTopic.id).\
        filter(PubSubEndpointTopic.topic_id==topic_id).\
        filter(PubSubEndpointTopic.endpoint_id==PubSubEndpoint.id).\
        filter(PubSubEndpointTopic.cluster_id==cluster_id)

# ################################################################################################################################

def _pubsub_topic_message(session, cluster_id, needs_sub_queue_check):
    q = session.query(
        PubSubMessage.pub_msg_id.label('msg_id'),
        PubSubMessage.pub_correl_id.label('correl_id'),
        PubSubMessage.in_reply_to,
        PubSubMessage.pub_time, PubSubMessage.data_prefix_short,
        PubSubMessage.pub_pattern_matched, PubSubMessage.priority,
        PubSubMessage.ext_pub_time, PubSubMessage.size,
        PubSubMessage.data_format, PubSubMessage.mime_type,
        PubSubMessage.data, PubSubMessage.expiration,
        PubSubMessage.expiration_time, PubSubMessage.has_gd,
        PubSubMessage.ext_client_id,
        PubSubEndpoint.id.label('endpoint_id'),
        PubSubEndpoint.name.label('endpoint_name'),
        PubSubEndpoint.service_id,
        PubSubEndpoint.security_id,
        PubSubEndpoint.ws_channel_id,
        PubSubTopic.id.label('topic_id'),
        PubSubTopic.name.label('topic_name'),
        ).\
        filter(PubSubMessage.published_by_id==PubSubEndpoint.id).\
        filter(PubSubMessage.cluster_id==cluster_id).\
        filter(PubSubMessage.topic_id==PubSubTopic.id)

    if needs_sub_queue_check:
        q = q.\
            filter(~PubSubMessage.is_in_sub_queue)

    return q

# ################################################################################################################################

def pubsub_message(session, cluster_id, pub_msg_id, needs_sub_queue_check=True):
    return _pubsub_topic_message(session, cluster_id, needs_sub_queue_check).\
        filter(PubSubMessage.pub_msg_id==pub_msg_id)

# ################################################################################################################################

def _pubsub_endpoint_queue(session, cluster_id):
    return session.query(
        PubSubSubscription.id.label('sub_id'),
        PubSubSubscription.active_status,
        PubSubSubscription.is_internal,
        PubSubSubscription.creation_time,
        PubSubSubscription.sub_key,
        PubSubSubscription.has_gd,
        PubSubSubscription.delivery_method,
        PubSubSubscription.delivery_data_format,
        PubSubSubscription.delivery_endpoint,
        PubSubSubscription.is_staging_enabled,
        PubSubSubscription.ext_client_id,
        PubSubTopic.id.label('topic_id'),
        PubSubTopic.name.label('topic_name'),
        PubSubTopic.name.label('name'), # Currently queue names are the same as their originating topics
        PubSubEndpoint.name.label('endpoint_name'),
        PubSubEndpoint.id.label('endpoint_id'),
        WebSocketSubscription.ext_client_id.label('ws_ext_client_id'),
        ).\
        outerjoin(WebSocketSubscription, WebSocketSubscription.sub_key==PubSubSubscription.sub_key).\
        filter(PubSubSubscription.topic_id==PubSubTopic.id).\
        filter(PubSubSubscription.cluster_id==cluster_id).\
        filter(PubSubSubscription.endpoint_id==PubSubEndpoint.id)

# ################################################################################################################################

@query_wrapper
def pubsub_endpoint_queue_list(session, cluster_id, endpoint_id, needs_columns=False):
    return _pubsub_endpoint_queue(session, cluster_id).\
        filter(PubSubSubscription.endpoint_id==endpoint_id).\
        order_by(PubSubSubscription.creation_time.desc())

# ################################################################################################################################

def pubsub_endpoint_queue_list_by_sub_keys(session, cluster_id, sub_key_list):
    return _pubsub_endpoint_queue(session, cluster_id).\
        filter(PubSubSubscription.sub_key.in_(sub_key_list)).\
        all()

# ################################################################################################################################

def pubsub_endpoint_queue(session, cluster_id, sub_id):
    return _pubsub_endpoint_queue(session, cluster_id).\
        filter(PubSubSubscription.id==sub_id).\
        one()

# ################################################################################################################################

@query_wrapper
def pubsub_messages_for_topic(session, cluster_id, topic_id, needs_columns=False):
    return _pubsub_topic_message(session, cluster_id, True).\
        filter(PubSubMessage.topic_id==topic_id).\
        order_by(PubSubMessage.pub_time.desc())

# ################################################################################################################################

def _pubsub_queue_message(session, cluster_id):
    return session.query(
        PubSubMessage.pub_msg_id.label('msg_id'),
        PubSubMessage.pub_correl_id.label('correl_id'),
        PubSubMessage.in_reply_to,
        PubSubMessage.data_prefix_short,
        PubSubMessage.priority,
        PubSubMessage.ext_pub_time,
        PubSubMessage.size,
        PubSubMessage.data_format,
        PubSubMessage.mime_type,
        PubSubMessage.data,
        PubSubMessage.expiration,
        PubSubMessage.expiration_time,
        PubSubMessage.ext_client_id,
        PubSubMessage.published_by_id,
        PubSubMessage.pub_pattern_matched,
        PubSubTopic.id.label('topic_id'),
        PubSubTopic.name.label('topic_name'),
        PubSubTopic.name.label('queue_name'), # Currently, queue name = name of its underlying topic
        PubSubEndpointEnqueuedMessage.creation_time.label('recv_time'),
        PubSubEndpointEnqueuedMessage.delivery_count,
        PubSubEndpointEnqueuedMessage.last_delivery_time,
        PubSubEndpointEnqueuedMessage.is_in_staging,
        PubSubEndpointEnqueuedMessage.endpoint_id.label('subscriber_id'),
        PubSubEndpointEnqueuedMessage.sub_key,
        PubSubEndpoint.name.label('subscriber_name'),
        PubSubSubscription.sub_pattern_matched,
        ).\
        filter(PubSubEndpointEnqueuedMessage.pub_msg_id==PubSubMessage.pub_msg_id).\
        filter(PubSubEndpointEnqueuedMessage.topic_id==PubSubTopic.id).\
        filter(PubSubEndpointEnqueuedMessage.endpoint_id==PubSubEndpoint.id).\
        filter(PubSubEndpointEnqueuedMessage.sub_key==PubSubSubscription.sub_key).\
        filter(PubSubEndpointEnqueuedMessage.cluster_id==cluster_id)

# ################################################################################################################################

def pubsub_queue_message(session, cluster_id, msg_id):
    return _pubsub_queue_message(session, cluster_id).\
        filter(PubSubMessage.pub_msg_id==msg_id)

# ################################################################################################################################

@query_wrapper
def pubsub_messages_for_queue(session, cluster_id, sub_key, skip_delivered=False, needs_columns=False):
    q = _pubsub_queue_message(session, cluster_id).\
        filter(PubSubEndpointEnqueuedMessage.sub_key==sub_key)

    if skip_delivered:
        q = q.filter(PubSubEndpointEnqueuedMessage.delivery_status != PUBSUB.DELIVERY_STATUS.DELIVERED)

    return q.order_by(PubSubEndpointEnqueuedMessage.creation_time.desc())

# ################################################################################################################################

def pubsub_hook_service(session, cluster_id, endpoint_id, model_class):
    return session.query(
        Service.id,
        Service.name,
        ).\
        filter(Cluster.id==Service.cluster_id).\
        filter(Service.id==model_class.hook_service_id).\
        first()

# ################################################################################################################################

def _notif_sql(session, cluster_id, needs_password):
    """ SQL notifications.
    """

    columns = [NotifSQL.id, NotifSQL.is_active, NotifSQL.name, NotifSQL.query, NotifSQL.notif_type, NotifSQL.interval,
        NotifSQL.def_id, SQLConnectionPool.name.label('def_name'), Service.name.label('service_name')]

    if needs_password:
        columns.append(SQLConnectionPool.password)

    return session.query(*columns).\
        filter(Cluster.id==NotifSQL.cluster_id).\
        filter(SQLConnectionPool.id==NotifSQL.def_id).\
        filter(Service.id==NotifSQL.service_id).\
        filter(Cluster.id==cluster_id)

@query_wrapper
def notif_sql_list(session, cluster_id, needs_password=False, needs_columns=False):
    """ All the SQL notifications.
    """
    return _notif_sql(session, cluster_id, needs_password)

# ################################################################################################################################

def _search_es(session, cluster_id):
    """ ElasticSearch connections.
    """
    return session.query(ElasticSearch).\
        filter(Cluster.id==ElasticSearch.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(ElasticSearch.name)

@query_wrapper
def search_es_list(session, cluster_id, needs_columns=False):
    """ All the ElasticSearch connections.
    """
    return _search_es(session, cluster_id)

# ################################################################################################################################

def _search_solr(session, cluster_id):
    """ Solr sonnections.
    """
    return session.query(Solr).\
        filter(Cluster.id==Solr.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(Solr.name)

@query_wrapper
def search_solr_list(session, cluster_id, needs_columns=False):
    """ All the Solr connections.
    """
    return _search_solr(session, cluster_id)

# ################################################################################################################################

def _server(session, cluster_id, cluster_name):
    q = session.query(
        Server.id, Server.name, Server.bind_host, Server.bind_port, Server.last_join_status, Server.last_join_mod_date,
        Server.last_join_mod_by, Server.up_status, Server.up_mod_date, Server.preferred_address,
        Server.crypto_use_tls,
        Cluster.id.label('cluster_id'), Cluster.name.label('cluster_name')).\
        filter(Cluster.id==Server.cluster_id)

    if cluster_id:
        q = q.filter(Cluster.id==cluster_id)
    else:
        q = q.filter(Cluster.name==cluster_name)

    q = q.order_by(Server.name)

    return q

@query_wrapper
def server_list(session, cluster_id, cluster_name, up_status=None, needs_columns=False):
    """ All the servers defined on a cluster.
    """
    q = _server(session, cluster_id, cluster_name)
    if up_status:
        q = q.filter(Server.up_status==up_status)
    return q

def server_by_name(session, cluster_id, cluster_name, server_name):
    return _server(session, cluster_id, cluster_name).\
        filter(Server.name==server_name).\
        all()

def server_by_id(session, cluster_id, server_id):
    return _server(session, cluster_id, None).\
        filter(Server.id==server_id).\
        one()

# ################################################################################################################################

def _cassandra_conn(session, cluster_id):
    return session.query(CassandraConn).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==CassandraConn.cluster_id).\
        order_by(CassandraConn.name)

def cassandra_conn(session, cluster_id, id):
    """ A Cassandra connection definition.
    """
    return _cassandra_conn(session, cluster_id).\
        filter(CassandraConn.id==id).\
        one()

@query_wrapper
def cassandra_conn_list(session, cluster_id, needs_columns=False):
    """ A list of Cassandra connection definitions.
    """
    return _cassandra_conn(session, cluster_id)

# ################################################################################################################################

def _cassandra_query(session, cluster_id):
    return session.query(
        CassandraQuery.id, CassandraQuery.name, CassandraQuery.value,
        CassandraQuery.is_active, CassandraQuery.cluster_id,
        CassandraConn.name.label('def_name'),
        CassandraConn.id.label('def_id'),
        ).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==CassandraQuery.cluster_id).\
        filter(CassandraConn.id==CassandraQuery.def_id).\
        order_by(CassandraQuery.name)

def cassandra_query(session, cluster_id, id):
    """ A Cassandra prepared statement.
    """
    return _cassandra_query(session, cluster_id).\
        filter(CassandraQuery.id==id).\
        one()

@query_wrapper
def cassandra_query_list(session, cluster_id, needs_columns=False):
    """ A list of Cassandra prepared statements.
    """
    return _cassandra_query(session, cluster_id)

# ################################################################################################################################

def _email_smtp(session, cluster_id):
    return session.query(SMTP).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==SMTP.cluster_id).\
        order_by(SMTP.name)

def email_smtp(session, cluster_id, id):
    """ An SMTP connection.
    """
    return _email_smtp(session, cluster_id).\
        filter(SMTP.id==id).\
        one()

@query_wrapper
def email_smtp_list(session, cluster_id, needs_columns=False):
    """ A list of SMTP connections.
    """
    return _email_smtp(session, cluster_id)

# ################################################################################################################################

def _email_imap(session, cluster_id):
    return session.query(IMAP).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==IMAP.cluster_id).\
        order_by(IMAP.name)

def email_imap(session, cluster_id, id):
    """ An IMAP connection.
    """
    return _email_imap(session, cluster_id).\
        filter(IMAP.id==id).\
        one()

@query_wrapper
def email_imap_list(session, cluster_id, needs_columns=False):
    """ A list of IMAP connections.
    """
    return _email_imap(session, cluster_id)

# ################################################################################################################################

def _rbac_permission(session, cluster_id):
    return session.query(RBACPermission).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==RBACPermission.cluster_id).\
        order_by(RBACPermission.name)

def rbac_permission(session, cluster_id, id=None, name=None):
    """ An RBAC permission.
    """
    q = _rbac_permission(session, cluster_id)

    if name:
        q = q.filter(RBACPermission.name==name)
    elif id:
        q = q.filter(RBACPermission.id==id)

    return q.one()

@query_wrapper
def rbac_permission_list(session, cluster_id, needs_columns=False):
    """ A list of RBAC permissions.
    """
    return _rbac_permission(session, cluster_id)

# ################################################################################################################################

def _rbac_role(session, cluster_id):
    rbac_parent = aliased(RBACRole)
    return session.query(RBACRole.id, RBACRole.name, RBACRole.parent_id, rbac_parent.name.label('parent_name')).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==RBACRole.cluster_id).\
        outerjoin(rbac_parent, rbac_parent.id==RBACRole.parent_id).\
        order_by(RBACRole.name)

def rbac_role(session, cluster_id, id=None, name=None):
    """ An RBAC role.
    """
    q = _rbac_role(session, cluster_id)

    if name:
        q = q.filter(RBACRole.name==name)
    elif id:
        q = q.filter(RBACRole.id==id)

    return q.one()

@query_wrapper
def rbac_role_list(session, cluster_id, needs_columns=False):
    """ A list of RBAC roles.
    """
    return _rbac_role(session, cluster_id)

# ################################################################################################################################

def _rbac_client_role(session, cluster_id):
    return session.query(RBACClientRole).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==RBACClientRole.cluster_id).\
        order_by(RBACClientRole.client_def)

def rbac_client_role(session, cluster_id, id):
    """ An individual mapping between a client and role.
    """
    return _rbac_client_role(session, cluster_id).\
        filter(RBACClientRole.id==id).\
        one()

@query_wrapper
def rbac_client_role_list(session, cluster_id, needs_columns=False):
    """ A list of mappings between clients and roles.
    """
    return _rbac_client_role(session, cluster_id)

# ################################################################################################################################

def _rbac_role_permission(session, cluster_id):
    return session.query(RBACRolePermission).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==RBACRolePermission.cluster_id).\
        order_by(RBACRolePermission.role_id)

def rbac_role_permission(session, cluster_id, id):
    """ An individual permission for a given role against a service.
    """
    return _rbac_role_permission(session, cluster_id).\
        filter(RBACRolePermission.id==id).\
        one()

@query_wrapper
def rbac_role_permission_list(session, cluster_id, needs_columns=False):
    """ A list of permissions for roles against services.
    """
    return _rbac_role_permission(session, cluster_id)

# ################################################################################################################################

def cache_by_id(session, cluster_id, cache_id):
    return session.query(Cache).\
        filter(Cache.id==cluster_id).\
        filter(Cluster.id==Cache.cluster_id).\
        filter(Cache.id==cache_id).\
        one()

# ################################################################################################################################

def _cache_builtin(session, cluster_id):
    return session.query(CacheBuiltin).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==CacheBuiltin.cluster_id).\
        filter(Cache.id==CacheBuiltin.cache_id).\
        filter(Cache.cache_type==CACHE.TYPE.BUILTIN).\
        order_by(CacheBuiltin.name)

def cache_builtin(session, cluster_id, id):
    """ An individual built-in cache definition.
    """
    return _cache_builtin(session, cluster_id).\
        filter(CacheBuiltin.id==id).\
        one()

@query_wrapper
def cache_builtin_list(session, cluster_id, needs_columns=False):
    """ A list of built-in cache definitions.
    """
    return _cache_builtin(session, cluster_id)

# ################################################################################################################################

def _cache_memcached(session, cluster_id):
    return session.query(
        CacheMemcached.cache_id, CacheMemcached.name, CacheMemcached.is_active,
        CacheMemcached.is_default, CacheMemcached.is_debug,
        CacheMemcached.servers, CacheMemcached.extra,
        CacheMemcached.cache_type).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==CacheMemcached.cluster_id).\
        filter(Cache.id==CacheMemcached.cache_id).\
        filter(Cache.cache_type==CACHE.TYPE.MEMCACHED).\
        order_by(CacheMemcached.name)

def cache_memcached(session, cluster_id, id):
    """ An individual Memcached cache definition.
    """
    return _cache_builtin(session, cluster_id).\
        filter(CacheMemcached.id==id).\
        one()

@query_wrapper
def cache_memcached_list(session, cluster_id, needs_columns=False):
    """ A list of Memcached cache definitions.
    """
    return _cache_memcached(session, cluster_id)

# ################################################################################################################################

def _out_odoo(session, cluster_id):
    return session.query(OutgoingOdoo).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==OutgoingOdoo.cluster_id).\
        order_by(OutgoingOdoo.name)

def out_odoo(session, cluster_id, id):
    """ An individual Odoo connection.
    """
    return _out_odoo(session, cluster_id).\
        filter(OutgoingOdoo.id==id).\
        one()

@query_wrapper
def out_odoo_list(session, cluster_id, needs_columns=False):
    """ A list of Odoo connections.
    """
    return _out_odoo(session, cluster_id)

# ################################################################################################################################

def _out_sap(session, cluster_id):
    return session.query(OutgoingSAP).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==OutgoingSAP.cluster_id).\
        order_by(OutgoingSAP.name)

def out_sap(session, cluster_id, id):
    """ An individual SAP RFC connection.
    """
    return _out_sap(session, cluster_id).\
        filter(OutgoingSAP.id==id).\
        one()

@query_wrapper
def out_sap_list(session, cluster_id, needs_columns=False):
    """ A list of SAP RFC connections.
    """
    return _out_sap(session, cluster_id)

# ################################################################################################################################

def _channel_web_socket(session, cluster_id):
    """ WebSocket channels
    """
    return session.query(
        ChannelWebSocket.id,
        ChannelWebSocket.name,
        ChannelWebSocket.is_active,
        ChannelWebSocket.is_internal,
        ChannelWebSocket.address,
        ChannelWebSocket.data_format,
        ChannelWebSocket.service_id,
        ChannelWebSocket.security_id,
        ChannelWebSocket.new_token_wait_time,
        ChannelWebSocket.token_ttl,
        ChannelWebSocket.is_out,
        ChannelWebSocket.opaque1,
        SecurityBase.sec_type,
        VaultConnection.default_auth_method.label('vault_conn_default_auth_method'),
        SecurityBase.name.label('sec_name'),
        Service.name.label('service_name'),
        ).\
        outerjoin(Service, Service.id==ChannelWebSocket.service_id).\
        outerjoin(SecurityBase, SecurityBase.id==ChannelWebSocket.security_id).\
        outerjoin(VaultConnection, SecurityBase.id==VaultConnection.id).\
        filter(Cluster.id==ChannelWebSocket.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(ChannelWebSocket.name)

def channel_web_socket(session, cluster_id, id):
    """ An incoming WebSocket connection.
    """
    return _channel_web_socket(session, cluster_id).\
        filter(ChannelWebSocket.id==id).\
        one()

@query_wrapper
def channel_web_socket_list(session, cluster_id, needs_columns=False):
    """ All the WebSocket channel connections.
    """
    return _channel_web_socket(session, cluster_id)

# ################################################################################################################################

def web_socket_client_by_pub_id(session, pub_client_id):
    """ An individual WebSocket connection by its public ID.
    """
    return session.query(
        WebSocketClient.id,
        ChannelWebSocket.id.label('channel_id'),
        ChannelWebSocket.name.label('channel_name')
        ).\
        filter(WebSocketClient.pub_client_id==pub_client_id).\
        outerjoin(ChannelWebSocket, ChannelWebSocket.id==WebSocketClient.channel_id).\
        one()

# ################################################################################################################################

def web_socket_client_by_ext_id(session, ext_client_id, needs_one_or_none=False):
    """ An individual WebSocket connection by its external client ID.
    """
    query = session.query(
        WebSocketClient,
        ChannelWebSocket.id.label('channel_id'),
        ChannelWebSocket.name.label('channel_name')
        ).\
        filter(WebSocketClient.ext_client_id==ext_client_id).\
        outerjoin(ChannelWebSocket, ChannelWebSocket.id==WebSocketClient.channel_id)

    return query.one_or_none() if needs_one_or_none else query.all()

# ################################################################################################################################

def web_socket_clients_by_server_id(session, server_id, server_pid):
    """ A list of WebSocket clients attached to a particular server by the latter's ID.
    """
    query = session.query(WebSocketClient).\
        filter(WebSocketClient.server_id==server_id)

    if server_pid:
        query = query.\
            filter(WebSocketClient.server_proc_pid==server_pid)

    return query

# ################################################################################################################################

def _web_socket_client(session, cluster_id, channel_id):
    return session.query(WebSocketClient).\
        filter(WebSocketClient.cluster_id==cluster_id).\
        filter(WebSocketClient.channel_id==channel_id).\
        order_by(WebSocketClient.connection_time.desc())

# ################################################################################################################################

def web_socket_client(session, cluster_id, channel_id, pub_client_id=None, ext_client_id=None, use_first=True):
    query = _web_socket_client(session, cluster_id, channel_id)

    if pub_client_id:
        query = query.filter(WebSocketClient.pub_client_id==pub_client_id)

    elif ext_client_id:
        query = query.filter(WebSocketClient.ext_client_id==ext_client_id)

    else:
        raise ValueError('Either pub_client_id or ext_client_id is required on input')

    return query.first() if use_first else query.all()

# ################################################################################################################################

@query_wrapper
def web_socket_client_list(session, cluster_id, channel_id, needs_columns=False):
    """ A list of subscriptions to a particular pattern.
    """
    return _web_socket_client(session, cluster_id, channel_id)

# ################################################################################################################################

def _web_socket_sub_key_data(session, cluster_id, pub_client_id):
    return session.query(
        WebSocketClientPubSubKeys.sub_key,
        PubSubSubscription.topic_id,
        PubSubSubscription.id.label('sub_id'),
        PubSubSubscription.creation_time,
        PubSubSubscription.endpoint_id,
        PubSubSubscription.sub_pattern_matched,
        PubSubSubscription.ext_client_id,
        PubSubEndpoint.name.label('endpoint_name'),
        PubSubTopic.name.label('topic_name')
        ).\
        filter(WebSocketClient.pub_client_id==pub_client_id).\
        filter(WebSocketClient.id==WebSocketClientPubSubKeys.client_id).\
        filter(WebSocketClientPubSubKeys.sub_key==WebSocketSubscription.sub_key).\
        filter(WebSocketClientPubSubKeys.sub_key==PubSubSubscription.sub_key).\
        filter(PubSubSubscription.topic_id==PubSubTopic.id).\
        filter(PubSubSubscription.endpoint_id==PubSubEndpoint.id)

@query_wrapper
def web_socket_sub_key_data_list(session, cluster_id, pub_client_id, needs_columns=False):
    return _web_socket_sub_key_data(session, cluster_id, pub_client_id)

# ################################################################################################################################

def _vault_connection(session, cluster_id):
    return session.query(VaultConnection.id, VaultConnection.is_active, VaultConnection.name,
            VaultConnection.url, VaultConnection.token, VaultConnection.default_auth_method,
            VaultConnection.timeout, VaultConnection.allow_redirects, VaultConnection.tls_verify,
            VaultConnection.tls_ca_cert_id, VaultConnection.tls_key_cert_id, VaultConnection.sec_type,
            Service.name.label('service_name'), Service.id.label('service_id')).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==VaultConnection.cluster_id).\
        outerjoin(Service, Service.id==VaultConnection.service_id).\
        order_by(VaultConnection.name)

def vault_connection(session, cluster_id, id):
    """ An individual Vault connection.
    """
    return _vault_connection(session, cluster_id).\
        filter(VaultConnection.id==id).\
        one()

@query_wrapper
def vault_connection_list(session, cluster_id, needs_columns=False):
    """ A list of Vault connections.
    """
    return _vault_connection(session, cluster_id)

# ################################################################################################################################

def _sms_twilio(session, cluster_id):
    """ SMS Twilio connections.
    """
    return session.query(SMSTwilio).\
        filter(Cluster.id==SMSTwilio.cluster_id).\
        filter(Cluster.id==cluster_id).\
        order_by(SMSTwilio.name)

def sms_twilio(session, cluster_id, id):
    """ An individual SMS Twilio connection.
    """
    return _sms_twilio(session, cluster_id).\
        filter(SMSTwilio.id==id).\
        one()

@query_wrapper
def sms_twilio_list(session, cluster_id, needs_columns=False):
    """ All the SMS Twilio connections.
    """
    return _sms_twilio(session, cluster_id)

# ################################################################################################################################
