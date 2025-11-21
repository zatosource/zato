# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from functools import wraps

# Bunch
from bunch import bunchify

# SQLAlchemy
from sqlalchemy import and_, func, not_, or_
from sqlalchemy.sql.expression import case

# Zato
from zato.common.api import CACHE, DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, GENERIC, HTTP_SOAP_SERIALIZATION_TYPE, \
     PARAMS_PRIORITY, PubSub, URL_PARAMS_PRIORITY
from zato.common.json_internal import loads
from zato.common.odb.model import APIKeySecurity, CacheBuiltin, ChannelAMQP, Cluster, \
    DeployedService, ElasticSearch, HTTPBasicAuth, HTTPSOAP, IMAP, IntervalBasedJob, Job, \
    NTLM, OAuth, OutgoingOdoo, OutgoingAMQP, OutgoingFTP, PubSubPermission, PubSubSubscription, PubSubSubscriptionTopic, \
    PubSubTopic, SecurityBase, Server, Service, SMTP, SQLConnectionPool, OutgoingSAP
from zato.common.util.search import SearchResults as _SearchResults

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

pubsub_publisher = PubSub.API_Client.Publisher
pubsub_subscriber = PubSub.API_Client.Subscriber
pubsub_publisher_subscriber = PubSub.API_Client.Publisher_Subscriber

# ################################################################################################################################
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
        return query_func.__name__ in {
            'http_soap_list',
            'pubsub_permission_list',
        }

# ################################################################################################################################

class _SearchWrapper:
    """ Wraps results in pagination and/or filters out objects by their name or other attributes.
    """
    def __init__(self, q, default_page_size=_no_page_limit, **config):

        # Apply WHERE conditions
        where = config.get('where') or _not_given
        if where is not _not_given:
            q = q.filter(where)
        else:

            filters = []

            if query := config.get('query', []):
                query = query if isinstance(query, (list, tuple)) else [query]

            if filter_by := config.get('filter_by', []):
                filter_by = filter_by if isinstance(filter_by, (list, tuple)) else [filter_by]
                len_filter_by = len(filter_by)
                for column in filter_by:
                    for criterion in query:
                        expression = column.contains(criterion)
                        if criterion.startswith('-'):
                            expression = not_(expression)
                        and_filter = and_(*[expression]) # type: ignore
                        filters.append(and_filter)

                # We need to use "or" if we filter by more then one column
                # to let the filters match all of them independently.
                if filters:
                    if len_filter_by > 1:
                        combine_criteria_using = or_
                    else:
                        combine_criteria_using = and_

                    q = q.filter(combine_criteria_using(*filters))

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
        result = _SearchResults(tool.q, tool.q.all(), tool.q.subquery().columns, tool.total)

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
        ).\
        outerjoin(IntervalBasedJob, Job.id==IntervalBasedJob.job_id).\
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
        first()

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

def sec_base(session, cluster_id, sec_base_id, use_one=True):
    q = _sec_base(session, cluster_id).\
        filter(SecurityBase.id==sec_base_id)

    if use_one:
        result = q.one()
    else:
        result = q.first()

    return result

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
def basic_auth_list(session, cluster_id, cluster_name=None, needs_columns=False):
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
    out = session.query(
        OAuth.id,
        OAuth.name,
        OAuth.is_active,
        OAuth.username,
        OAuth.password,
        OAuth.proto_version,
        OAuth.sig_method,
        OAuth.max_nonce_log,
        OAuth.sec_type,
        OAuth.opaque1,
        ).\
    filter(Cluster.id==cluster_id).\
    filter(Cluster.id==OAuth.cluster_id).\
    filter(SecurityBase.id==OAuth.id).\
    order_by(SecurityBase.name)

    return out

# ################################################################################################################################

def _out_amqp(session, cluster_id):
    return session.query(
        OutgoingAMQP.id,
        OutgoingAMQP.name,
        OutgoingAMQP.is_active,
        OutgoingAMQP.address,
        OutgoingAMQP.username,
        OutgoingAMQP.password,
        OutgoingAMQP.delivery_mode,
        OutgoingAMQP.priority,
        OutgoingAMQP.content_type,
        OutgoingAMQP.content_encoding,
        OutgoingAMQP.expiration,
        OutgoingAMQP.pool_size,
        OutgoingAMQP.user_id,
        OutgoingAMQP.app_id
        ).\
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

def _channel_amqp(session, cluster_id):
    return session.query(
        ChannelAMQP.id,
        ChannelAMQP.name,
        ChannelAMQP.is_active,
        ChannelAMQP.address,
        ChannelAMQP.username,
        ChannelAMQP.password,
        ChannelAMQP.queue,
        ChannelAMQP.consumer_tag_prefix,
        ChannelAMQP.pool_size,
        ChannelAMQP.ack_mode,
        ChannelAMQP.prefetch_count,
        ChannelAMQP.data_format,
        Service.name.label('service_name'),
        Service.impl_name.label('service_impl_name')).\
        filter(ChannelAMQP.service_id==Service.id).\
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
        HTTPSOAP.cache_id,
        HTTPSOAP.cache_expiry,
        HTTPSOAP.content_encoding,
        HTTPSOAP.opaque1,
        CacheBuiltin.name.label('cache_name'),
        CacheBuiltin.cache_type,
        SecurityBase.sec_type,
        Service.name.label('service_name'),
        Service.id.label('service_id'),
        Service.impl_name.label('service_impl_name'),
        SecurityBase.name.label('security_name'),
        SecurityBase.username.label('username'),
        SecurityBase.password.label('password'),
        SecurityBase.password_type.label('password_type'),).\
        outerjoin(Service, Service.id==HTTPSOAP.service_id).\
        outerjoin(CacheBuiltin, CacheBuiltin.id==HTTPSOAP.cache_id).\
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
        q = q.filter(
            not_(
                HTTPSOAP.name.startswith('zato') |
                HTTPSOAP.name.startswith('pub.zato') |
                HTTPSOAP.name.startswith('admin.invoke') |
                HTTPSOAP.name.startswith('Rule engine API')
            )
        )

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
            q = q.filter(not_(or_(
                Service.name.startswith('zato'),
                Service.name.startswith('helpers'),
                Service.name.startswith('pub.zato'),
            )))

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

def service_deployment_list(session, service_id=None, include_internal=None):
    query = session.query(
        DeployedService.details,
        Server.name.label('server_name'),
        Server.id.label('server_id'),
        Service.id.label('service_id'),
        Service.name.label('service_name'),
        ).\
        filter(DeployedService.service_id==Service.id).\
        filter(DeployedService.server_id==Server.id)

    if service_id:
        query = query.\
        filter(DeployedService.service_id==service_id)

    if not include_internal:
        query = query.\
            filter(Service.is_internal==False) # type: ignore

        query = query.filter(
            not_(
                Service.name.startswith('zato') |
                Service.name.startswith('pub.zato') |
                Service.name.startswith('pub.helpers') |
                Service.name.startswith('helpers')
            )
        )

    return query.all()

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

def cache_by_id(session, cluster_id, cache_id):
    return session.query(CacheBuiltin).\
        filter(CacheBuiltin.id==cluster_id).\
        filter(Cluster.id==CacheBuiltin.cluster_id).\
        filter(CacheBuiltin.id==cache_id).\
        one()

# ################################################################################################################################

def _cache_builtin(session, cluster_id):
    return session.query(CacheBuiltin).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==CacheBuiltin.cluster_id).\
        filter(CacheBuiltin.cache_type==CACHE.TYPE.BUILTIN).\
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

def _pubsub_topic(session, cluster_id):
    return session.query(PubSubTopic).\
        filter(Cluster.id==cluster_id).\
        filter(Cluster.id==PubSubTopic.cluster_id).\
        order_by(PubSubTopic.name)

def pubsub_topic(session, cluster_id, id):
    """ An individual Pub/Sub topic.
    """
    return _pubsub_topic(session, cluster_id).\
        filter(PubSubTopic.id==id).\
        one()

@query_wrapper
def pubsub_topic_list(session, cluster_id, filter_by=None, needs_columns=False):
    """ A list of Pub/Sub topics with publisher and subscriber counts.
    """
    # Subquery to count publishers
    publisher_count = session.query(
        PubSubPermission.pattern,
        func.count(PubSubPermission.id).label('publisher_count')
    ).filter(
        PubSubPermission.cluster_id == cluster_id,
        PubSubPermission.access_type.in_([pubsub_publisher, pubsub_publisher_subscriber])
    ).group_by(PubSubPermission.pattern).subquery()

    # Subquery to count subscribers
    subscriber_count = session.query(
        PubSubPermission.pattern,
        func.count(PubSubPermission.id).label('subscriber_count')
    ).filter(
        PubSubPermission.cluster_id == cluster_id,
        PubSubPermission.access_type.in_([pubsub_subscriber, pubsub_publisher_subscriber])
    ).group_by(PubSubPermission.pattern).subquery()

    # Main query with counts
    query = session.query(
        PubSubTopic,
        func.coalesce(publisher_count.c.publisher_count, 0).label('publisher_count'),
        func.coalesce(subscriber_count.c.subscriber_count, 0).label('subscriber_count')
    ).filter(
        Cluster.id == cluster_id,
        Cluster.id == PubSubTopic.cluster_id
    ).outerjoin(
        publisher_count, PubSubTopic.name == publisher_count.c.pattern
    ).outerjoin(
        subscriber_count, PubSubTopic.name == subscriber_count.c.pattern
    ).order_by(PubSubTopic.name)

    return query

# ################################################################################################################################

def _pubsub_permission(session, cluster_id, id):
    return session.query(PubSubPermission, SecurityBase).\
        join(SecurityBase, PubSubPermission.sec_base_id == SecurityBase.id).\
        filter(PubSubPermission.cluster_id==cluster_id).\
        filter(PubSubPermission.id==id)

def pubsub_permission(session, cluster_id, id):
    return _pubsub_permission(session, cluster_id, id).one()

@query_wrapper
def pubsub_permission_list(session, cluster_id, filter_by=None, needs_columns=False, **config):

    # Subquery to count subscriptions per security definition
    subscription_count = session.query(
        PubSubSubscription.sec_base_id,
        func.count(PubSubSubscription.id).label('subscription_count')
    ).filter(
        PubSubSubscription.cluster_id == cluster_id,
        PubSubSubscription.is_delivery_active == True
    ).group_by(PubSubSubscription.sec_base_id).subquery()

    # Main query with subscription counts
    query = session.query(
        PubSubPermission,
        SecurityBase.name.label('name'),
        func.coalesce(subscription_count.c.subscription_count, 0).label('subscription_count')
    ).join(
        SecurityBase, PubSubPermission.sec_base_id == SecurityBase.id
    ).outerjoin(
        subscription_count, PubSubPermission.sec_base_id == subscription_count.c.sec_base_id
    ).filter(
        PubSubPermission.cluster_id == cluster_id
    )

    # Handle search filtering
    if search_query := config.get('query', []):
        search_query = search_query if isinstance(search_query, (list, tuple)) else [search_query]
        filters = []

        for criterion in search_query:
            # Search in both security definition name and pattern
            name_filter = SecurityBase.name.contains(criterion)
            pattern_filter = PubSubPermission.pattern.contains(criterion)

            if criterion.startswith('-'):
                name_filter = not_(name_filter)
                pattern_filter = not_(pattern_filter)

            # OR between name and pattern for each criterion
            filters.append(or_(name_filter, pattern_filter))

        # AND between different search terms
        if filters:
            query = query.filter(and_(*filters))

    return query.order_by(SecurityBase.name)

# ################################################################################################################################

def _pubsub_subscription(session, cluster_id):

    # Return all subscription-topic pairs without grouping
    return session.query(
        PubSubSubscription.id,
        PubSubSubscription.sub_key,
        PubSubSubscription.is_delivery_active,
        PubSubSubscription.is_pub_active,
        PubSubSubscription.sec_base_id,
        PubSubSubscription.created,
        PubSubSubscription.last_updated,
        PubSubSubscription.delivery_type,
        PubSubSubscription.push_type,
        PubSubSubscription.rest_push_endpoint_id,
        PubSubSubscription.push_service_name,
        PubSubTopic.name.label('topic_name'),
        PubSubSubscriptionTopic.is_pub_enabled,
        PubSubSubscriptionTopic.is_delivery_enabled,
        SecurityBase.name.label('sec_name'),
        SecurityBase.username,
        SecurityBase.password.label('password'),
        HTTPSOAP.name.label('rest_push_endpoint_name') # type: ignore
    ).\
        join(PubSubSubscriptionTopic, PubSubSubscription.id == PubSubSubscriptionTopic.subscription_id).\
        join(PubSubTopic, PubSubSubscriptionTopic.topic_id == PubSubTopic.id).\
        join(SecurityBase, PubSubSubscription.sec_base_id == SecurityBase.id).\
        outerjoin(HTTPSOAP, PubSubSubscription.rest_push_endpoint_id == HTTPSOAP.id).\
        filter(PubSubSubscription.cluster_id == cluster_id).\
        filter(PubSubSubscriptionTopic.cluster_id == cluster_id).\
        order_by(PubSubTopic.name)

def pubsub_subscription(session, cluster_id, id):
    """ An individual Pub/Sub subscription.
    """
    return _pubsub_subscription(session, cluster_id).\
        filter(PubSubSubscription.id == id).\
        one()

@query_wrapper
def pubsub_subscription_list(session, cluster_id, filter_by=None, needs_columns=False):
    """ A list of Pub/Sub subscriptions.
    """
    query = _pubsub_subscription(session, cluster_id)

    # Apply any additional filtering if provided
    if filter_by:
        if isinstance(filter_by, (list, tuple)):
            for filter_criterion in filter_by:
                query = query.filter(filter_criterion)
        else:
            query = query.filter(filter_by)

    # Group by subscription ID to handle subscriptions with multiple topics
    # This ensures we get one row per subscription with the first topic name
    return query

# ################################################################################################################################
