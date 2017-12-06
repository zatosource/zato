# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, inspect, os, sys
from datetime import datetime
from errno import ENOENT
from inspect import isclass
from json import loads
from threading import RLock
from time import sleep
from traceback import format_exc
from urlparse import urlparse
from uuid import uuid4

# Bunch
from bunch import bunchify

# dateutil
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, MINUTELY, rrule

# gevent
import gevent

# gunicorn
from gunicorn.workers.ggevent import GeventWorker as GunicornGeventWorker
from gunicorn.workers.sync import SyncWorker as GunicornSyncWorker

# Zato
from zato.broker import BrokerMessageReceiver
from zato.bunch import Bunch
from zato.common import broker_message, CHANNEL, DATA_FORMAT, HTTP_SOAP_SERIALIZATION_TYPE, IPC, KVDB, MSG_PATTERN_TYPE, NOTIF, \
     PUBSUB, SEC_DEF_TYPE, simple_types, TRACE1, ZATO_NONE, ZATO_ODB_POOL_NAME, ZMQ
from zato.common.broker_message import code_to_name, SERVICE
from zato.common.dispatch import dispatcher
from zato.common.match import Matcher
from zato.common.odb.api import PoolStore, SessionWrapper
from zato.common.util import get_tls_ca_cert_full_path, get_tls_key_cert_full_path, get_tls_from_payload, \
     import_module_from_path, new_cid, pairwise, parse_extra_into_dict, parse_tls_channel_security_definition, start_connectors, \
     store_tls, update_apikey_username, update_bind_port, visit_py_source
from zato.server.base.worker.common import WorkerImpl
from zato.server.connection.amqp_ import ConnectorAMQP
from zato.server.connection.cache import CacheAPI
from zato.server.connection.cassandra import CassandraAPI, CassandraConnStore
from zato.server.connection.connector import ConnectorStore, connector_type
from zato.server.connection.cloud.aws.s3 import S3Wrapper
from zato.server.connection.cloud.openstack.swift import SwiftWrapper
from zato.server.connection.email import IMAPAPI, IMAPConnStore, SMTPAPI, SMTPConnStore
from zato.server.connection.ftp import FTPStore
from zato.server.connection.http_soap.channel import RequestDispatcher, RequestHandler
from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper, SudsSOAPWrapper
from zato.server.connection.http_soap.url_data import URLData
from zato.server.connection.odoo import OdooWrapper
from zato.server.connection.search.es import ElasticSearchAPI, ElasticSearchConnStore
from zato.server.connection.search.solr import SolrAPI, SolrConnStore
from zato.server.connection.sms.twilio import TwilioAPI, TwilioConnStore
from zato.server.connection.stomp import ChannelSTOMPConnStore, STOMPAPI, channel_main_loop as stomp_channel_main_loop, \
     OutconnSTOMPConnStore
from zato.server.connection.web_socket import ChannelWebSocket
from zato.server.connection.web_socket.outgoing import OutgoingWebSocket
from zato.server.connection.vault import VaultConnAPI
from zato.server.pubsub import PubSub
from zato.server.query import CassandraQueryAPI, CassandraQueryStore
from zato.server.rbac_ import RBAC
from zato.server.stats import MaintenanceTool
from zato.zmq_.channel import MDPv01 as ChannelZMQMDPv01, Simple as ChannelZMQSimple
from zato.zmq_.outgoing import Simple as OutZMQSimple

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class GeventWorker(GunicornGeventWorker):
    def __init__(self, *args, **kwargs):
        self.deployment_key = '{}.{}'.format(datetime.utcnow().isoformat(), uuid4().hex)
        super(GunicornGeventWorker, self).__init__(*args, **kwargs)

# ################################################################################################################################

class SyncWorker(GunicornSyncWorker):
    def __init__(self, *args, **kwargs):
        self.deployment_key = '{}.{}'.format(datetime.utcnow().isoformat(), uuid4().hex)
        super(GunicornSyncWorker, self).__init__(*args, **kwargs)

# ################################################################################################################################

def _get_base_classes():
    ignore = ('__init__.py', 'common.py')
    out = []

    for py_path in visit_py_source(os.path.dirname(os.path.abspath(__file__))):
        import_path = True
        for item in ignore:
            if py_path.endswith(item):
                import_path = False
                continue

        if import_path:
            mod_info = import_module_from_path(py_path)
            for name in dir(mod_info.module):
                item = getattr(mod_info.module, name)
                if isclass(item) and issubclass(item, WorkerImpl) and item is not WorkerImpl:
                    out.append(item)

    return tuple(out)

# ################################################################################################################################

# Dynamically adds as base classes everything found in current directory that subclasses WorkerImpl
_WorkerStoreBase = type(b'_WorkerStoreBase', _get_base_classes(), {})

class WorkerStore(_WorkerStoreBase, BrokerMessageReceiver):
    """ Dispatches work between different pieces of configuration of an individual gunicorn worker.
    """
    def __init__(self, worker_config=None, server=None):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_ready = False
        self.worker_config = worker_config
        self.server = server
        self.update_lock = RLock()
        self.kvdb = server.kvdb
        self.broker_client = None
        self.pubsub = PubSub(self.server.cluster_id, self.server)
        self.rbac = RBAC()
        self.worker_idx = int(os.environ['ZATO_SERVER_WORKER_IDX'])

        # Which services can be invoked
        self.invoke_matcher = Matcher()

        # Which targets this server supports
        self.target_matcher = Matcher()

        # To speed up look-ups
        self._simple_types = simple_types

# ################################################################################################################################

    def init(self):

        # Statistics maintenance
        self.stats_maint = MaintenanceTool(self.kvdb.conn)

        self.msg_ns_store = self.worker_config.msg_ns_store
        self.json_pointer_store = self.worker_config.json_pointer_store
        self.xpath_store = self.worker_config.xpath_store

        # CassandraOutconnSTOMPConnStore
        self.cassandra_api = CassandraAPI(CassandraConnStore())
        self.cassandra_query_store = CassandraQueryStore()
        self.cassandra_query_api = CassandraQueryAPI(self.cassandra_query_store)

        # STOMP
        self.stomp_outconn_api = STOMPAPI(OutconnSTOMPConnStore())
        self.stomp_channel_api = STOMPAPI(ChannelSTOMPConnStore())

        # Search
        self.search_es_api = ElasticSearchAPI(ElasticSearchConnStore())
        self.search_solr_api = SolrAPI(SolrConnStore())

        # SMS
        self.sms_twilio_api = TwilioAPI(TwilioConnStore())

        # E-mail
        self.email_smtp_api = SMTPAPI(SMTPConnStore())
        self.email_imap_api = IMAPAPI(IMAPConnStore())

        # ZeroMQ
        self.zmq_mdp_v01_api = ConnectorStore(connector_type.duplex.zmq_v01, ChannelZMQMDPv01)
        self.zmq_channel_api = ConnectorStore(connector_type.channel.zmq, ChannelZMQSimple)
        self.zmq_out_api = ConnectorStore(connector_type.out.zmq, OutZMQSimple)

        # WebSocket
        self.web_socket_api = ConnectorStore(connector_type.duplex.web_socket, ChannelWebSocket, self.server)
        self.outgoing_web_sockets = OutgoingWebSocket(self.server.cluster_id, self.server.servers, self.server.odb)

        # AMQP
        self.amqp_api = ConnectorStore(connector_type.duplex.amqp, ConnectorAMQP)
        self.amqp_out_name_to_def = {} # Maps outgoing connection names to definition names, i.e. to connector names

        # Vault connections
        self.vault_conn_api = VaultConnAPI()

        # Caches
        self.cache_api = CacheAPI(self.server)

        # Message-related config - init_msg_ns_store must come before init_xpath_store
        # so the latter has access to the former's namespace map.

        self.init_msg_ns_store()
        self.init_json_pointer_store()
        self.init_xpath_store()

        # After connection is establised, a flag is stored here to let queries consult it
        # before they attempt to prepare statements. In other words, queries wait for connections.
        # They do it in separate greenlets.
        self._cassandra_connections_ready = {}

        # Cassandra
        self.init_cassandra()
        self.init_cassandra_queries()

        # Search
        self.init_search_es()
        self.init_search_solr()

        # SMS
        self.init_sms_twilio()

        # E-mail
        self.init_email_smtp()
        self.init_email_imap()

        # STOMP
        self.init_stomp()

        # ZeroMQ
        self.init_zmq()

        # Odoo
        self.init_odoo()

        # RBAC
        self.init_rbac()

        # Vault connections
        self.init_vault_conn()

        # Caches
        self.init_caches()

        # API keys
        self.update_apikeys()

        # Request dispatcher - matches URLs, checks security and dispatches HTTP
        # requests to services.

        self.request_dispatcher = RequestDispatcher(simple_io_config=self.worker_config.simple_io,
            return_tracebacks=self.server.return_tracebacks, default_error_message=self.server.default_error_message)
        self.request_dispatcher.url_data = URLData(
            self, self.worker_config.http_soap,
            self.server.odb.get_url_security(self.server.cluster_id, 'channel')[0],
            self.worker_config.basic_auth, self.worker_config.jwt, self.worker_config.ntlm, self.worker_config.oauth,
            self.worker_config.tech_acc, self.worker_config.wss, self.worker_config.apikey, self.worker_config.aws,
            self.worker_config.openstack_security, self.worker_config.xpath_sec, self.worker_config.tls_channel_sec,
            self.worker_config.tls_key_cert, self.worker_config.vault_conn_sec, self.kvdb, self.broker_client, self.server.odb,
            self.json_pointer_store, self.xpath_store, self.server.jwt_secret, self.vault_conn_api)

        self.request_dispatcher.request_handler = RequestHandler(self.server)

        # Create all the expected connections and objects
        self.init_sql()
        self.init_ftp()

        self.init_http_soap()

        self.init_cloud()
        self.init_notifiers()

        # WebSocket
        self.init_web_socket()

        # AMQP
        self.init_amqp()

        # All set, whoever is waiting for us, if anyone at all, can now proceed
        self.is_ready = True

# ################################################################################################################################

    def _config_to_dict(self, config_list, key='name'):
        """ Converts a list of dictionaries produced by ConfigDict instances to a dictionary keyed with 'key' elements.
        """
        out = {}
        for elem in config_list:
            out[elem[key]] = elem
        return out

# ################################################################################################################################

    def after_broker_client_set(self):
        self.pubsub.broker_client = self.broker_client

        # Pub/sub requires broker client
        self.init_pubsub()

# ################################################################################################################################

    def set_broker_client(self, broker_client):
        self.broker_client = broker_client
        self.after_broker_client_set()

# ################################################################################################################################

    def filter(self, msg):
        # TODO: Fix it, worker doesn't need to accept all the messages
        return True

# ################################################################################################################################

    def _update_queue_build_cap(self, item):
        item.queue_build_cap = float(self.server.fs_server_config.misc.queue_build_cap)

# ################################################################################################################################

    def _update_aws_config(self, msg):
        """ Parses the address to AWS we store into discrete components S3Connection objects expect.
        Also turns metadata string into a dictionary
        """
        url_info = urlparse(msg.address)

        msg.is_secure = True if url_info.scheme == 'https' else False
        msg.port = url_info.port if url_info.port else (443 if msg.is_secure else 80)
        msg.host = url_info.netloc

        msg.metadata = parse_extra_into_dict(msg.metadata_)

# ################################################################################################################################

    def _http_soap_wrapper_from_config(self, config, has_sec_config=True):
        """ Creates a new HTTP/SOAP connection wrapper out of a configuration
        dictionary.
        """
        security_name = config.get('security_name')
        sec_config = {'security_name':security_name, 'sec_type':None, 'username':None, 'password':None, 'password_type':None}
        _sec_config = None

        # This will be set to True only if the method's invoked on a server's starting up
        if has_sec_config:
            # It's possible that there is no security config attached at all
            if security_name:
                _sec_config = config
        else:
            if security_name:
                sec_type = config.sec_type
                func = getattr(self.request_dispatcher.url_data, sec_type + '_get')
                _sec_config = func(security_name).config

        if logger.isEnabledFor(TRACE1):
            logger.log(TRACE1, 'has_sec_config:[{}], security_name:[{}], _sec_config:[{}]'.format(
                has_sec_config, security_name, _sec_config))

        if _sec_config:
            sec_config['sec_type'] = _sec_config['sec_type']
            sec_config['username'] = _sec_config.get('username')
            sec_config['password'] = _sec_config.get('password')
            sec_config['password_type'] = _sec_config.get('password_type')
            sec_config['salt'] = _sec_config.get('salt')

            if sec_config['sec_type'] == SEC_DEF_TYPE.TLS_KEY_CERT:
                tls = self.request_dispatcher.url_data.tls_key_cert_get(security_name)
                sec_config['tls_key_cert_full_path'] = get_tls_key_cert_full_path(
                    self.server.tls_dir, get_tls_from_payload(tls.config.value, True))

        wrapper_config = {'id':config.id,
            'is_active':config.is_active, 'method':config.method,
            'data_format':config.get('data_format'),
            'name':config.name, 'transport':config.transport,
            'address_host':config.host,
            'address_url_path':config.url_path,
            'soap_action':config.soap_action, 'soap_version':config.soap_version, 'ping_method':config.ping_method,
            'pool_size':config.pool_size, 'serialization_type':config.serialization_type,
            'timeout':config.timeout, 'content_type':config.content_type,
            }
        wrapper_config.update(sec_config)

        if config.sec_tls_ca_cert_id and config.sec_tls_ca_cert_id != ZATO_NONE:
            tls_verify = get_tls_ca_cert_full_path(self.server.tls_dir, get_tls_from_payload(
                self.worker_config.tls_ca_cert[config.sec_tls_ca_cert_name].config.value))
        else:
            tls_verify = ZATO_NONE

        wrapper_config['tls_verify'] = tls_verify

        if wrapper_config['serialization_type'] == HTTP_SOAP_SERIALIZATION_TYPE.SUDS.id:
            wrapper_config['queue_build_cap'] = float(self.server.fs_server_config.misc.queue_build_cap)
            wrapper = SudsSOAPWrapper(wrapper_config)
            wrapper.build_client_queue()
            return wrapper

        return HTTPSOAPWrapper(wrapper_config)

# ################################################################################################################################

    def yield_outconn_http_config_dicts(self):
        for transport in('soap', 'plain_http'):
            config_dict = getattr(self.worker_config, 'out_' + transport)
            for name in config_dict.keys(): # Must use .keys() explicitly so that config_dict can be changed during iteration
                yield config_dict, config_dict[name]

# ################################################################################################################################

    def init_sql(self):
        """ Initializes SQL connections, first to ODB and then any user-defined ones.
        """
        # We need a store first
        self.sql_pool_store = PoolStore()

        # Connect to ODB
        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.worker_config.odb_data
        self.odb = SessionWrapper()
        self.odb.init_session(ZATO_ODB_POOL_NAME, self.worker_config.odb_data, self.sql_pool_store[ZATO_ODB_POOL_NAME].pool)

        # Any user-defined SQL connections left?
        for pool_name in self.worker_config.out_sql:
            config = self.worker_config.out_sql[pool_name]['config']
            self.sql_pool_store[pool_name] = config

    def init_ftp(self):
        """ Initializes FTP connetions. The method replaces whatever value self.out_ftp
        previously had (initially this would be a ConfigDict of connection definitions).
        """
        config_list = self.worker_config.out_ftp.get_config_list()
        self.worker_config.out_ftp = FTPStore()
        self.worker_config.out_ftp.add_params(config_list)

    def init_http_soap(self):
        """ Initializes plain HTTP/SOAP connections.
        """
        for config_dict, config_data in self.yield_outconn_http_config_dicts():
            wrapper = self._http_soap_wrapper_from_config(config_data.config)
            config_data.conn = wrapper

            # To make the API consistent with that of SQL connection pools
            config_data.ping = wrapper.ping

            # Store ID -> name mapping
            config_dict.set_key_id_data(config_data.config)

    def init_cloud(self):
        """ Initializes all the cloud connections.
        """
        data = (
            ('cloud_openstack_swift', SwiftWrapper),
            ('cloud_aws_s3', S3Wrapper),
        )

        for config_key, wrapper in data:
            config_attr = getattr(self.worker_config, config_key)
            for name in config_attr:
                config = config_attr[name]['config']
                if isinstance(wrapper, S3Wrapper):
                    self._update_aws_config(config)
                config.queue_build_cap = float(self.server.fs_server_config.misc.queue_build_cap)
                config_attr[name].conn = wrapper(config, self.server)
                config_attr[name].conn.build_queue()

    def _update_cloud_openstack_swift_container(self, config_dict):
        """ Makes sure OpenStack Swift containers always have a path to prefix queries with.
        """
        config_dict.containers = [elem.split(':') for elem in config_dict.containers.splitlines()]
        for item in config_dict.containers:
            # No path specified so we use an empty string to catch everything.
            if len(item) == 1:
                item.append('')

            item.append('{}:{}'.format(item[0], item[1]))

    def init_notifiers(self):
        for config_dict in self.worker_config.notif_cloud_openstack_swift.values():
            self._update_cloud_openstack_swift_container(config_dict.config)

    def get_notif_config(self, notif_type, name):
        config_dict = {
            NOTIF.TYPE.OPENSTACK_SWIFT: self.worker_config.notif_cloud_openstack_swift,
            NOTIF.TYPE.SQL: self.worker_config.notif_sql,
        }[notif_type]

        return config_dict.get(name)

    def create_edit_notifier(self, msg, action, config_dict, update_func=None):

        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg.name

        config_dict.pop(del_name, None) # Delete and ignore if it doesn't exit (it's CREATE then)
        config_dict[msg.name] = Bunch()
        config_dict[msg.name].config = msg

        if update_func:
            update_func(msg)

        # Start a new background notifier either if it's a create action or on rename.
        if msg.source_service_type == 'create' or (old_name and old_name != msg.name):

            self.on_message_invoke_service({
                'service': 'zato.notif.invoke-run-notifier',
                'payload': {'config': msg},
                'cid': new_cid(),
            }, CHANNEL.NOTIFIER_RUN, action)

# ################################################################################################################################

    def _on_cassandra_connection_established(self, config):
        self._cassandra_connections_ready[config.id] = True

    def init_cassandra(self):
        for k, v in self.worker_config.cassandra_conn.items():
            try:
                self._cassandra_connections_ready[v.config.id] = False
                self.update_cassandra_conn(v.config)
                self.cassandra_api.create_def(k, v.config, self._on_cassandra_connection_established)
            except Exception, e:
                logger.warn('Could not create a Cassandra connection `%s`, e:`%s`', k, format_exc(e))

# ################################################################################################################################

    def _init_cassandra_query(self, create_func, k, config):
        idx = 0
        while not self._cassandra_connections_ready.get(config.def_id):
            gevent.sleep(1)

            idx += 1
            if not idx % 20:
                logger.warn('Still waiting for `%s` Cassandra connection', config.def_name)

        create_func(k, config, def_=self.cassandra_api[config.def_name])

    def init_cassandra_queries(self):
        for k, v in self.worker_config.cassandra_query.items():
            try:
                gevent.spawn(self._init_cassandra_query, self.cassandra_query_api.create, k, v.config)
            except Exception, e:
                logger.warn('Could not create a Cassandra query `%s`, e:`%s`', k, format_exc(e))

# ################################################################################################################################

    def init_stomp(self):

        for k, v in self.worker_config.out_stomp.items():
            try:
                self.stomp_outconn_api.create_def(k, v.config)
            except Exception, e:
                logger.warn('Could not create a Stomp outgoing connection `%s`, e:`%s`', k, format_exc(e))

        for k, v in self.worker_config.channel_stomp.items():
            try:
                self.stomp_channel_api.create_def(k, v.config, stomp_channel_main_loop, self)
            except Exception, e:
                logger.warn('Could not create a Stomp channel `%s`, e:`%s`', k, format_exc(e))

# ################################################################################################################################

    def init_simple(self, config, api, name):
        for k, v in config.items():
            self._update_queue_build_cap(v.config)
            try:
                api.create(k, v.config)
            except Exception, e:
                logger.warn('Could not create {} connection `%s`, e:`%s`'.format(name), k, format_exc(e))

# ################################################################################################################################

    def init_sms_twilio(self):
        self.init_simple(self.worker_config.sms_twilio, self.sms_twilio_api, 'a Twilio')

# ################################################################################################################################

    def init_search_es(self):
        self.init_simple(self.worker_config.search_es, self.search_es_api, 'an ElasticSearch')

# ################################################################################################################################

    def init_search_solr(self):
        self.init_simple(self.worker_config.search_solr, self.search_solr_api, 'a Solr')

# ################################################################################################################################

    def init_email_smtp(self):
        self.init_simple(self.worker_config.email_smtp, self.email_smtp_api, 'an SMTP')

# ################################################################################################################################

    def init_email_imap(self):
        self.init_simple(self.worker_config.email_imap, self.email_imap_api, 'an IMAP')

# ################################################################################################################################

    def _set_up_zmq_channel(self, name, config, action, start=False):
        """ Actually initializes a ZeroMQ channel, taking into account dissimilarities between MDP ones and PULL/SUB.
        """
        # We need to consult old_socket_type because it may very well be the case that someone
        # not only (say) renamed a channel but also changed its socket type as well.

        if config.get('old_socket_type') and config.socket_type != config.old_socket_type:
            raise ValueError('Cannot change a ZeroMQ channel\'s socket type')

        if config.socket_type.startswith(ZMQ.MDP):
            api = self.zmq_mdp_v01_api

            zeromq_mdp_config = self.server.fs_server_config.zeromq_mdp
            zeromq_mdp_config = {k:int(v) for k, v in zeromq_mdp_config.items()}
            config.update(zeromq_mdp_config)

        else:
            api = self.zmq_channel_api

        getattr(api, action)(name, config, self.on_message_invoke_service)

        if start:
            api.start(name)

# ################################################################################################################################

    def init_zmq_channels(self):
        """ Initializes ZeroMQ channels and MDP connections.
        """

        # Channels
        for name, data in self.worker_config.channel_zmq.items():

            # Each worker uses a unique bind port
            data = bunchify(data)
            update_bind_port(data.config, self.worker_idx)

            self._set_up_zmq_channel(name, bunchify(data.config), 'create')

        self.zmq_mdp_v01_api.start()
        self.zmq_channel_api.start()

    def init_zmq_outconns(self):
        """ Initializes ZeroMQ outgoing connections (but not MDP that are initialized along with channels).
        """
        for name, data in self.worker_config.out_zmq.items():

            # MDP ones were already handled in channels above
            if data.config['socket_type'].startswith(ZMQ.MDP):
                continue

            self.zmq_out_api.create(name, data.config)

        self.zmq_out_api.start()

# ################################################################################################################################

    def init_zmq(self):
        """ Initializes all ZeroMQ connections.
        """
        # Iterate over channels and outgoing connections and populate their respetive connectors.
        # Note that MDP are duplex and we create them in channels while in outgoing connections they are skipped.

        self.init_zmq_channels()
        self.init_zmq_outconns()

# ################################################################################################################################

    def init_web_socket(self):
        """ Initializes all WebSocket connections.
        """
        # Channels
        for name, data in self.worker_config.channel_web_socket.items():

            # Each worker uses a unique bind port
            update_bind_port(data.config, self.worker_idx)

            self.web_socket_api.create(name, bunchify(data.config), self.on_message_invoke_service,
                self.request_dispatcher.url_data.authenticate_web_socket)

        self.web_socket_api.start()

# ################################################################################################################################

    def init_amqp(self):
        """ Initializes all AMQP connections.
        """
        def _name_matches(def_name):
            def _inner(config):
                return config['def_name']==def_name
            return _inner

        for def_name, data in self.worker_config.definition_amqp.items():

            channels = self.worker_config.channel_amqp.get_config_list(_name_matches(def_name))
            outconns = self.worker_config.out_amqp.get_config_list(_name_matches(def_name))
            for outconn in outconns:
                self.amqp_out_name_to_def[outconn['name']] = def_name

            # AMQP definitions as such are always active. It's channels or outconns that can be inactive.
            data.config.is_active = True
            self.amqp_api.create(def_name, bunchify(data.config), self.invoke,
                channels=self._config_to_dict(channels), outconns=self._config_to_dict(outconns))

        self.amqp_api.start()

# ################################################################################################################################

    def init_odoo(self):
        names = self.worker_config.out_odoo.keys()
        for name in names:
            item = config = self.worker_config.out_odoo[name]
            config = item['config']
            config.queue_build_cap = float(self.server.fs_server_config.misc.queue_build_cap)
            item.conn = OdooWrapper(config, self.server)
            item.conn.build_queue()

# ################################################################################################################################

    def init_rbac(self):

        for value in self.worker_config.service.values():
            self.rbac.create_resource(value.config.id)

        for value in self.worker_config.rbac_permission.values():
            self.rbac.create_permission(value.config.id, value.config.name)

        for value in self.worker_config.rbac_role.values():
            self.rbac.create_role(value.config.id, value.config.name, value.config.parent_id)

        for value in self.worker_config.rbac_client_role.values():
            self.rbac.create_client_role(value.config.client_def, value.config.role_id)

        # TODO - handle 'deny' as well
        for value in self.worker_config.rbac_role_permission.values():
            self.rbac.create_role_permission_allow(value.config.role_id, value.config.perm_id, value.config.service_id)

        self.rbac.set_http_permissions()

# ################################################################################################################################

    def init_vault_conn(self):
        for value in self.worker_config.vault_conn_sec.values():
            self.vault_conn_api.create(bunchify(value['config']))

# ################################################################################################################################

    def init_caches(self):

        for name in 'builtin', 'memcached':
            cache = getattr(self.worker_config, 'cache_{}'.format(name))
            for value in cache.values():
                self.cache_api.create(bunchify(value['config']))

# ################################################################################################################################

    def init_pubsub(self):
        """ Sets up all pub/sub endpoints, subscriptions and topics. Also, configures pubsub with getters for each endpoint type.
        """
        for value in self.worker_config.pubsub_endpoint.values():
            self.pubsub.create_endpoint(bunchify(value['config']))

        for value in self.worker_config.pubsub_subscription.values():
            self.pubsub.create_subscription(bunchify(value['config']))

        for value in self.worker_config.pubsub_topic.values():
            self.pubsub.create_topic(bunchify(value['config']))

        self.pubsub.endpoint_getter[PUBSUB.ENDPOINT_TYPE.REST.id] = self.worker_config.out_plain_http.get_by_id
        self.pubsub.endpoint_getter[PUBSUB.ENDPOINT_TYPE.SOAP.id] = self.worker_config.out_soap.get_by_id

# ################################################################################################################################

    def update_apikeys(self):
        """ API keys need to be upper-cased and in the format that WSGI environment will have them in.
        """
        for config_dict in self.worker_config.apikey.values():
            update_apikey_username(config_dict.config)

# ################################################################################################################################

    def init_msg_ns_store(self):
        for k, v in self.worker_config.msg_ns.items():
            self.msg_ns_store.add(k, v.config)

    def init_xpath_store(self):
        for k, v in self.worker_config.xpath.items():
            self.xpath_store.add(k, v.config, self.msg_ns_store.ns_map)

    def init_json_pointer_store(self):
        for k, v in self.worker_config.json_pointer.items():
            self.json_pointer_store.add(k, v.config)

# ################################################################################################################################

    def _update_auth(self, msg, action_name, sec_type, visit_wrapper, keys=None):
        """ A common method for updating auth-related configuration.
        """
        with self.update_lock:
            # Channels
            handler = getattr(self.request_dispatcher.url_data, 'on_broker_msg_' + action_name)
            handler(msg)

            for transport in('soap', 'plain_http'):
                config_dict = getattr(self.worker_config, 'out_' + transport)

                # Wrappers and static configuration for outgoing connections
                for name in config_dict.copy_keys():
                    config = config_dict[name].config
                    wrapper = config_dict[name].conn
                    if config['sec_type'] == sec_type:
                        if keys:
                            visit_wrapper(wrapper, msg, keys)
                        else:
                            visit_wrapper(wrapper, msg)

    def _visit_wrapper_edit(self, wrapper, msg, keys):
        """ Updates a given wrapper's security configuration.
        """
        if wrapper.config['security_name'] == msg['old_name']:
            for key in keys:
                # All's good except for 'name', the msg's 'name' is known
                # as 'security_name' in wrapper's config.
                if key == 'name':
                    key1 = 'security_name'
                    key2 = key
                else:
                    key1, key2 = key, key
                wrapper.config[key1] = msg[key2]
            wrapper.set_auth()

    def _visit_wrapper_delete(self, wrapper, msg):
        """ Deletes a wrapper.
        """
        config_dict = getattr(self.worker_config, 'out_' + wrapper.config['transport'])
        if wrapper.config['security_name'] == msg['name']:
            del config_dict[wrapper.config['name']]

    def _visit_wrapper_change_password(self, wrapper, msg):
        """ Changes a wrapper's password.
        """
        if wrapper.config['security_name'] == msg['name']:
            wrapper.config['password'] = msg['password']
            wrapper.set_auth()

# ################################################################################################################################

    def apikey_get(self, name):
        """ Returns the configuration of the API key of the given name.
        """
        return self.request_dispatcher.url_data.apikey_get(name)

    def on_broker_msg_SECURITY_APIKEY_CREATE(self, msg, *args):
        """ Creates a new API key security definition.
        """
        dispatcher.notify(broker_message.SECURITY.APIKEY_CREATE.value, msg)

    def on_broker_msg_SECURITY_APIKEY_EDIT(self, msg, *args):
        """ Updates an existing API key security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.APIKEY,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name'))

    def on_broker_msg_SECURITY_APIKEY_DELETE(self, msg, *args):
        """ Deletes an API key security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.APIKEY,
                self._visit_wrapper_delete)

    def on_broker_msg_SECURITY_APIKEY_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an API key security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.APIKEY,
                self._visit_wrapper_change_password)

# ################################################################################################################################

    def aws_get(self, name):
        """ Returns the configuration of the AWS security definition
        of the given name.
        """
        return self.request_dispatcher.url_data.aws_get(name)

    def on_broker_msg_SECURITY_AWS_CREATE(self, msg, *args):
        """ Creates a new AWS security definition
        """
        dispatcher.notify(broker_message.SECURITY.AWS_CREATE.value, msg)

    def on_broker_msg_SECURITY_AWS_EDIT(self, msg, *args):
        """ Updates an existing AWS security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.AWS,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name'))

    def on_broker_msg_SECURITY_AWS_DELETE(self, msg, *args):
        """ Deletes an AWS security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.AWS,
                self._visit_wrapper_delete)

    def on_broker_msg_SECURITY_AWS_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an AWS security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.AWS,
                self._visit_wrapper_change_password)

# ################################################################################################################################

    def openstack_get(self, name):
        """ Returns the configuration of the OpenStack security definition
        of the given name.
        """
        self.request_dispatcher.url_data.openstack_get(name)

    def on_broker_msg_SECURITY_OPENSTACK_CREATE(self, msg, *args):
        """ Creates a new OpenStack security definition
        """
        dispatcher.notify(broker_message.SECURITY.OPENSTACK_CREATE.value, msg)

    def on_broker_msg_SECURITY_OPENSTACK_EDIT(self, msg, *args):
        """ Updates an existing OpenStack security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.OPENSTACK,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name'))

    def on_broker_msg_SECURITY_OPENSTACK_DELETE(self, msg, *args):
        """ Deletes an OpenStack security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.OPENSTACK,
                self._visit_wrapper_delete)

    def on_broker_msg_SECURITY_OPENSTACK_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an OpenStack security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.OPENSTACK,
                self._visit_wrapper_change_password)

# ################################################################################################################################

    def ntlm_get(self, name):
        """ Returns the configuration of the NTLM security definition
        of the given name.
        """
        return self.request_dispatcher.url_data.ntlm_get(name)

    def on_broker_msg_SECURITY_NTLM_CREATE(self, msg, *args):
        """ Creates a new NTLM security definition
        """
        dispatcher.notify(broker_message.SECURITY.NTLM_CREATE.value, msg)

    def on_broker_msg_SECURITY_NTLM_EDIT(self, msg, *args):
        """ Updates an existing NTLM security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.NTLM,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name'))

    def on_broker_msg_SECURITY_NTLM_DELETE(self, msg, *args):
        """ Deletes an NTLM security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.NTLM,
                self._visit_wrapper_delete)

    def on_broker_msg_SECURITY_NTLM_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an NTLM security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.NTLM,
                self._visit_wrapper_change_password)

# ################################################################################################################################

    def basic_auth_get(self, name):
        """ Returns the configuration of the HTTP Basic Auth security definition
        of the given name.
        """
        return self.request_dispatcher.url_data.basic_auth_get(name)

    def on_broker_msg_SECURITY_BASIC_AUTH_CREATE(self, msg, *args):
        """ Creates a new HTTP Basic Auth security definition
        """
        dispatcher.notify(broker_message.SECURITY.BASIC_AUTH_CREATE.value, msg)

    def on_broker_msg_SECURITY_BASIC_AUTH_EDIT(self, msg, *args):
        """ Updates an existing HTTP Basic Auth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.BASIC_AUTH,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name'))

    def on_broker_msg_SECURITY_BASIC_AUTH_DELETE(self, msg, *args):
        """ Deletes an HTTP Basic Auth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.BASIC_AUTH,
                self._visit_wrapper_delete)

    def on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an HTTP Basic Auth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.BASIC_AUTH,
                self._visit_wrapper_change_password)

# ################################################################################################################################

    def on_broker_msg_VAULT_CONNECTION_CREATE(self, msg):
        self.vault_conn_api.create(msg)
        dispatcher.notify(broker_message.VAULT.CONNECTION_CREATE.value, msg)

    def on_broker_msg_VAULT_CONNECTION_EDIT(self, msg):
        self.vault_conn_api.edit(msg)
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.VAULT,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name'))

    def on_broker_msg_VAULT_CONNECTION_DELETE(self, msg):
        self.vault_conn_api.delete(msg.name)
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.VAULT,
                self._visit_wrapper_delete)

# ################################################################################################################################

    def jwt_get(self, name):
        """ Returns the configuration of the JWT security definition
        of the given name.
        """
        return self.request_dispatcher.url_data.jwt_get(name)

    def on_broker_msg_SECURITY_JWT_CREATE(self, msg, *args):
        """ Creates a new JWT security definition
        """
        dispatcher.notify(broker_message.SECURITY.JWT_CREATE.value, msg)

    def on_broker_msg_SECURITY_JWT_EDIT(self, msg, *args):
        """ Updates an existing JWT security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.JWT,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name'))

    def on_broker_msg_SECURITY_JWT_DELETE(self, msg, *args):
        """ Deletes a JWT security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.JWT,
                self._visit_wrapper_delete)

    def on_broker_msg_SECURITY_JWT_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of a JWT security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.JWT,
                self._visit_wrapper_change_password)

# ################################################################################################################################

    def oauth_get(self, name):
        """ Returns the configuration of the OAuth security definition
        of the given name.
        """
        return self.request_dispatcher.url_data.oauth_get(name)

    def on_broker_msg_SECURITY_OAUTH_CREATE(self, msg, *args):
        """ Creates a new OAuth security definition
        """
        dispatcher.notify(broker_message.SECURITY.OAUTH_CREATE.value, msg)

    def on_broker_msg_SECURITY_OAUTH_EDIT(self, msg, *args):
        """ Updates an existing OAuth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.OAUTH,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name'))

    def on_broker_msg_SECURITY_OAUTH_DELETE(self, msg, *args):
        """ Deletes an OAuth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.OAUTH,
                self._visit_wrapper_delete)

    def on_broker_msg_SECURITY_OAUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an OAuth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.OAUTH,
                self._visit_wrapper_change_password)

# ################################################################################################################################

    def tech_acc_get(self, name):
        """ Returns the configuration of the technical account of the given name.
        """
        self.request_dispatcher.url_data.tech_acc_get(name)

    def on_broker_msg_SECURITY_TECH_ACC_CREATE(self, msg, *args):
        """ Creates a new technical account.
        """
        dispatcher.notify(broker_message.SECURITY.TECH_ACC_CREATE.value, msg)

    def on_broker_msg_SECURITY_TECH_ACC_EDIT(self, msg, *args):
        """ Updates an existing technical account.
        """
        dispatcher.notify(broker_message.SECURITY.TECH_ACC_EDIT.value, msg)

    def on_broker_msg_SECURITY_TECH_ACC_DELETE(self, msg, *args):
        """ Deletes a technical account.
        """
        dispatcher.notify(broker_message.SECURITY.TECH_ACC_DELETE.value, msg)

    def on_broker_msg_SECURITY_TECH_ACC_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a technical account.
        """
        dispatcher.notify(broker_message.SECURITY.TECH_ACC_CHANGE_PASSWORD.value, msg)

# ################################################################################################################################

    def _update_tls_outconns(self, material_type_id, update_key, msg):
        for config_dict in self.yield_outconn_http_config_dicts():
            if config_dict.config[material_type_id] == msg.id:
                config_dict.conn.config[update_key] = msg.full_path
                config_dict.conn.https_adapter.clear_pool()

# ################################################################################################################################

    def _add_tls_from_msg(self, config_attr, msg):
        config = getattr(self.worker_config, config_attr)
        config[msg.name] = Bunch(config=Bunch(value=msg.value))

    def update_tls_ca_cert(self, msg):
        msg.full_path = get_tls_ca_cert_full_path(self.server.tls_dir, get_tls_from_payload(msg.value))

    def update_tls_key_cert(self, msg):
        msg.full_path = get_tls_key_cert_full_path(self.server.tls_dir, get_tls_from_payload(msg.value, True))

# ################################################################################################################################

    def on_broker_msg_SECURITY_TLS_CHANNEL_SEC_CREATE(self, msg, *args):
        """ Creates a new security definition basing on TLS client certificates.
        """
        # Parse it to be on the safe side
        list(parse_tls_channel_security_definition(msg.value))

        dispatcher.notify(broker_message.SECURITY.TLS_CHANNEL_SEC_CREATE.value, msg)

    def on_broker_msg_SECURITY_TLS_CHANNEL_SEC_EDIT(self, msg, *args):
        """ Updates an existing security definition basing on TLS client certificates.
        """
        # Parse it to be on the safe side
        list(parse_tls_channel_security_definition(msg.value))

        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.TLS_CHANNEL_SEC,
                self._visit_wrapper_edit, keys=('name', 'value'))

    def on_broker_msg_SECURITY_TLS_CHANNEL_SEC_DELETE(self, msg, *args):
        """ Deletes a security definition basing on TLS client certificates.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.TLS_CHANNEL_SEC, self._visit_wrapper_delete)

# ################################################################################################################################

    def on_broker_msg_SECURITY_TLS_KEY_CERT_CREATE(self, msg):
        self.update_tls_key_cert(msg)
        self._add_tls_from_msg('tls_key_cert', msg)
        store_tls(self.server.tls_dir, msg.value, True)
        dispatcher.notify(broker_message.SECURITY.TLS_KEY_CERT_CREATE.value, msg)

    def on_broker_msg_SECURITY_TLS_KEY_CERT_EDIT(self, msg):
        self.update_tls_key_cert(msg)
        del self.worker_config.tls_key_cert[msg.old_name]
        self._add_tls_from_msg('tls_key_cert', msg)
        store_tls(self.server.tls_dir, msg.value, True)
        self._update_tls_outconns('security_id', 'tls_key_cert_full_path', msg)
        dispatcher.notify(broker_message.SECURITY.TLS_KEY_CERT_EDIT.value, msg)

    def on_broker_msg_SECURITY_TLS_KEY_CERT_DELETE(self, msg):
        self.update_tls_key_cert(msg)
        dispatcher.notify(broker_message.SECURITY.TLS_KEY_CERT_DELETE.value, msg)

# ################################################################################################################################

    def on_broker_msg_SECURITY_TLS_CA_CERT_CREATE(self, msg):
        self.update_tls_ca_cert(msg)
        self._add_tls_from_msg('tls_ca_cert', msg)
        store_tls(self.server.tls_dir, msg.value)
        dispatcher.notify(broker_message.SECURITY.TLS_CA_CERT_CREATE.value, msg)

    def on_broker_msg_SECURITY_TLS_CA_CERT_EDIT(self, msg):
        self.update_tls_ca_cert(msg)
        del self.worker_config.tls_ca_cert[msg.old_name]
        self._add_tls_from_msg('tls_ca_cert', msg)
        store_tls(self.server.tls_dir, msg.value)
        self._update_tls_outconns('sec_tls_ca_cert_id', 'tls_verify', msg)
        dispatcher.notify(broker_message.SECURITY.TLS_CA_CERT_EDIT.value, msg)

    def on_broker_msg_SECURITY_TLS_CA_CERT_DELETE(self, msg):
        self.update_tls_ca_cert(msg)
        dispatcher.notify(broker_message.SECURITY.TLS_CA_CERT_DELETE.value, msg)

# ################################################################################################################################

    def wss_get(self, name):
        """ Returns the configuration of the WSS definition of the given name.
        """
        self.request_dispatcher.url_data.wss_get(name)

    def on_broker_msg_SECURITY_WSS_CREATE(self, msg, *args):
        """ Creates a new WS-Security definition.
        """
        dispatcher.notify(broker_message.SECURITY.WSS_CREATE.value, msg)

    def on_broker_msg_SECURITY_WSS_EDIT(self, msg, *args):
        """ Updates an existing WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.WSS,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name',
                    'nonce_freshness_time', 'reject_expiry_limit', 'password_type',
                    'reject_empty_nonce_creat', 'reject_stale_tokens'))

    def on_broker_msg_SECURITY_WSS_DELETE(self, msg, *args):
        """ Deletes a WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.WSS,
                self._visit_wrapper_delete)

    def on_broker_msg_SECURITY_WSS_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.WSS,
                self._visit_wrapper_change_password)

# ################################################################################################################################

    def xpath_sec_get(self, name):
        """ Returns the configuration of an XPath security definition of the given name.
        """
        self.request_dispatcher.url_data.xpath_sec_get(name)

    def on_broker_msg_SECURITY_XPATH_SEC_CREATE(self, msg, *args):
        """ Creates a new XPath security definition
        """
        dispatcher.notify(broker_message.SECURITY.XPATH_SEC_CREATE.value, msg)

    def on_broker_msg_SECURITY_XPATH_SEC_EDIT(self, msg, *args):
        """ Updates an existing XPath security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.XPATH_SEC,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name'))

    def on_broker_msg_SECURITY_XPATH_SEC_DELETE(self, msg, *args):
        """ Deletes an XPath security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.XPATH_SEC,
                self._visit_wrapper_delete)

    def on_broker_msg_SECURITY_XPATH_SEC_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an XPath security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.XPATH_SEC,
                self._visit_wrapper_change_password)

# ################################################################################################################################

    def _set_service_response_data(self, serialize=True):

        def inner(service, **ignored):
            if not isinstance(service.response.payload, self._simple_types):
                service.response.payload = service.response.payload.getvalue(serialize)

        return inner

# ################################################################################################################################

    def invoke(self, service, payload, **kwargs):
        """ Invokes a service by its name with request on input.
        """
        channel = kwargs.get('channel', CHANNEL.WORKER)

        return self.on_message_invoke_service({
            'channel': channel,
            'payload': payload,
            'data_format': kwargs.get('data_format'),
            'service': service,
            'cid': new_cid(),
            'is_async': kwargs.get('is_async'),
            'callback': kwargs.get('callback'),
            'zato_ctx': kwargs.get('zato_ctx'),
        }, channel, None, needs_response=True, serialize=kwargs.get('serialize', True))

# ################################################################################################################################

    def on_message_invoke_service(self, msg, channel, action, args=None, **kwargs):
        """ Triggered by external events, such as messages sent through connectots. Creates a new service instance and invokes it.
        """
        zato_ctx = msg.get('zato_ctx') or {}
        target = zato_ctx.get('zato.request_ctx.target', '')
        cid = msg['cid']

        if target:

            if not self.target_matcher.is_allowed(target):
                # It's not an error - we just don't accept this target
                logger.debug('Invocation target `%s` not allowed (%s), CID:%s', target, msg['service'], cid)
                return

            # We can in theory handle this request but there's still some work first. Our server can be composed
            # of more than 1 gunicorn worker and each of them receives the messages directed to concrete targets.
            # Hence we must first check out if another worker from our server didn't beat us to it already.
            # Everything must be done with a distributed server-wide lock so that workers don't
            # interrupt each other.
            else:
                lock = KVDB.LOCK_ASYNC_INVOKE_WITH_TARGET_PATTERN.format(self.server.fs_server_config.main.token, cid)
                processed_key = KVDB.ASYNC_INVOKE_PROCESSED_FLAG_PATTERN.format(self.server.fs_server_config.main.token, cid)

                with self.server.zato_lock_manager(lock):
                    processed = self.server.kvdb.conn.get(processed_key)

                    # Ok, already processed
                    if processed == KVDB.ASYNC_INVOKE_PROCESSED_FLAG_PATTERN:
                        return

                    # We are first, set the processed flag. The flag expires in 5 minutes
                    # which is an arbitrary number huge enough to make sure other workers
                    # within our own server will be able to receive the async message
                    # we are about to process. Note that we don't set the flag after the processing
                    # is finished because even if there is any error along the invocation won't be repeated,
                    # hence we do it here already.
                    else:
                        self.server.kvdb.conn.set(processed_key, KVDB.ASYNC_INVOKE_PROCESSED_FLAG_PATTERN, 300)

        wsgi_environ = {
            'zato.request_ctx.async_msg':msg,
            'zato.request_ctx.in_reply_to':msg.get('in_reply_to'),
            'zato.request_ctx.fanout_cid':zato_ctx.get('fanout_cid'),
            'zato.request_ctx.parallel_exec_cid':zato_ctx.get('parallel_exec_cid'),
        }

        if zato_ctx:
            wsgi_environ['zato.channel_item'] = zato_ctx.get('zato.channel_item')

        data_format = msg.get('data_format')
        transport = msg.get('transport')

        if msg.get('channel') in (CHANNEL.FANOUT_ON_TARGET, CHANNEL.FANOUT_ON_FINAL, CHANNEL.PARALLEL_EXEC_ON_TARGET):
            payload = loads(msg['payload'])
        else:
            payload = msg['payload']

        service, is_active = self.server.service_store.new_instance_by_name(msg['service'])
        if not is_active:
            msg = 'Could not invoke an inactive service:`{}`, cid:`{}`'.format(service.get_name(), cid)
            logger.warn(msg)
            raise Exception(msg)

        service.update_handle(self._set_service_response_data(kwargs.get('serialize', True)), service, payload,
            channel, data_format, transport, self.server, self.broker_client, self, cid,
            self.worker_config.simple_io, job_type=msg.get('job_type'), wsgi_environ=wsgi_environ,
            environ=msg.get('environ'))

        # Invoke the callback, if any.
        if msg.get('is_async') and msg.get('callback'):

            cb_msg = {}
            cb_msg['action'] = SERVICE.PUBLISH.value
            cb_msg['service'] = msg['callback']
            cb_msg['payload'] = service.response.payload
            cb_msg['cid'] = new_cid()
            cb_msg['channel'] = CHANNEL.INVOKE_ASYNC_CALLBACK
            cb_msg['data_format'] = data_format
            cb_msg['transport'] = transport
            cb_msg['is_async'] = True
            cb_msg['in_reply_to'] = cid

            self.broker_client.invoke_async(cb_msg)

        if kwargs.get('needs_response'):
            return service.response.payload

# ################################################################################################################################

    def on_broker_msg_SCHEDULER_JOB_EXECUTED(self, msg, args=None):
        return self.on_message_invoke_service(msg, CHANNEL.SCHEDULER, 'SCHEDULER_JOB_EXECUTED', args)

    def on_broker_msg_CHANNEL_JMS_WMQ_MESSAGE_RECEIVED(self, msg, args=None):
        return self.on_message_invoke_service(msg, CHANNEL.JMS_WMQ, 'CHANNEL_JMS_WMQ_MESSAGE_RECEIVED', args)

    def on_broker_msg_CHANNEL_ZMQ_MESSAGE_RECEIVED(self, msg, args=None):
        return self.on_message_invoke_service(msg, CHANNEL.ZMQ, 'CHANNEL_ZMQ_MESSAGE_RECEIVED', args)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_SQL_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an SQL connection, including changing its
        password.
        """
        # Is it a rename? If so, delete the connection first
        if msg.get('old_name') and msg.get('old_name') != msg['name']:
            del self.sql_pool_store[msg['old_name']]

        self.sql_pool_store[msg['name']] = msg

    def on_broker_msg_OUTGOING_SQL_CHANGE_PASSWORD(self, msg, *args):
        """ Deletes an outgoing SQL connection pool and recreates it using the
        new password.
        """
        self.sql_pool_store.change_password(msg['name'], msg['password'])

    def on_broker_msg_OUTGOING_SQL_DELETE(self, msg, *args):
        """ Deletes an outgoing SQL connection pool.
        """
        del self.sql_pool_store[msg['name']]

# ################################################################################################################################

    def get_channel_plain_http(self, name):
        with self.update_lock:
            for item in self.request_dispatcher.url_data.channel_data:
                if item.connection == 'channel' and item.name == name:
                    return item

    def on_broker_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an HTTP/SOAP channel.
        """
        self.request_dispatcher.url_data.on_broker_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(msg, *args)

    def on_broker_msg_CHANNEL_HTTP_SOAP_DELETE(self, msg, *args):
        """ Deletes an HTTP/SOAP channel.
        """
        self.request_dispatcher.url_data.on_broker_msg_CHANNEL_HTTP_SOAP_DELETE(msg, *args)

# ################################################################################################################################

    def _delete_config_close_wrapper(self, name, config_dict, conn_type, log_func):
        """ Deletes a wrapper-based connection's config and closes its underlying wrapper.
        """
        # Delete the connection first, if it exists at all ..
        try:
            try:
                wrapper = config_dict[name].conn
            except (KeyError, AttributeError), e:
                log_func('Could not access wrapper, e:[{}]'.format(format_exc(e)))
            else:
                try:
                    wrapper.session.close()
                finally:
                    del config_dict[name]
        except Exception, e:
            log_func('Could not delete `{}`, e:`{}`'.format(conn_type, format_exc(e)))

# ################################################################################################################################

    def _delete_config_close_wrapper_http_soap(self, name, transport, log_func):
        """ Deletes/closes an HTTP/SOAP outconn.
        """
        # Are we dealing with plain HTTP or SOAP?
        config_dict = getattr(self.worker_config, 'out_' + transport)

        return self._delete_config_close_wrapper(name, config_dict, 'an outgoing HTTP/SOAP connection', log_func)

    def on_broker_msg_OUTGOING_HTTP_SOAP_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an outgoing HTTP/SOAP connection.
        """
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']

        # .. delete the connection if it exists ..
        self._delete_config_close_wrapper_http_soap(del_name, msg['transport'], logger.debug)

        # .. and create a new one
        wrapper = self._http_soap_wrapper_from_config(msg, False)
        config_dict = getattr(self.worker_config, 'out_' + msg['transport'])
        config_dict[msg['name']] = Bunch()
        config_dict[msg['name']].config = msg
        config_dict[msg['name']].conn = wrapper
        config_dict[msg['name']].ping = wrapper.ping # (just like in self.init_http)

        # Store mapping of ID -> name
        config_dict.set_key_id_data(msg)

    def on_broker_msg_OUTGOING_HTTP_SOAP_DELETE(self, msg, *args):
        """ Deletes an outgoing HTTP/SOAP connection (actually delegates the
        task to self._delete_config_close_wrapper_http_soap.
        """
        self._delete_config_close_wrapper_http_soap(msg['name'], msg['transport'], logger.error)

# ################################################################################################################################

    def on_broker_msg_SERVICE_DELETE(self, msg, *args):
        """ Deletes the service from the service store and removes it from the filesystem
        if it's not an internal one.
        """
        # Delete the service from RBAC resources
        self.rbac.delete_resource(msg.id)

        # Module this service is in so it can be removed from sys.modules
        mod = inspect.getmodule(self.server.service_store.services[msg.impl_name]['service_class'])

        # Where to delete it from in the second step
        deployment_info = loads(self.server.service_store.services[msg.impl_name]['deployment_info'])
        fs_location = deployment_info['fs_location']

        # Delete it from the service store
        del self.server.service_store.services[msg.impl_name]

        # Delete it from the filesystem, including any bytecode left over. Note that
        # other parallel servers may wish to do exactly the same so we just ignore
        # the error if any files are missing. Also note that internal services won't
        # be ever deleted from the FS.
        if not msg.is_internal:
            all_ext = ('py', 'pyc', 'pyo')
            no_ext = '.'.join(fs_location.split('.')[:-1])
            for ext in all_ext:
                path = '{}.{}'.format(no_ext, ext)
                try:
                    os.remove(path)
                except OSError, e:
                    if e.errno != ENOENT:
                        raise

        # Makes it actually gets reimported next time it's redeployed
        del sys.modules[mod.__name__]

    def on_broker_msg_SERVICE_EDIT(self, msg, *args):
        for name in('is_active', 'slow_threshold'):
            self.server.service_store.services[msg.impl_name][name] = msg[name]

# ################################################################################################################################

    def on_broker_msg_OUTGOING_FTP_CREATE_EDIT(self, msg, *args):
        self.worker_config.out_ftp.create_edit(msg, msg.get('old_name'))

    def on_broker_msg_OUTGOING_FTP_DELETE(self, msg, *args):
        self.worker_config.out_ftp.delete(msg.name)

    def on_broker_msg_OUTGOING_FTP_CHANGE_PASSWORD(self, msg, *args):
        self.worker_config.out_ftp.change_password(msg.name, msg.password)

# ################################################################################################################################

    def on_broker_msg_hot_deploy(self, msg, service, payload, action, *args):
        msg.cid = new_cid()
        msg.service = service
        msg.payload = payload
        return self.on_message_invoke_service(msg, 'hot-deploy', 'HOT_DEPLOY_{}'.format(action), args)

# ################################################################################################################################

    def on_broker_msg_HOT_DEPLOY_CREATE_SERVICE(self, msg, *args):
        return self.on_broker_msg_hot_deploy(msg, 'zato.hot-deploy.create', {'package_id': msg.package_id}, 'CREATE_SERVICE',
            *args)

# ################################################################################################################################

    def on_broker_msg_HOT_DEPLOY_CREATE_STATIC(self, msg, *args):
        return self.on_broker_msg_hot_deploy(msg, 'zato.pickup.on-update-static', {'data': msg.data, 'file_name': msg.file_name},
            'CREATE_STATIC', *args)

# ################################################################################################################################

    def on_broker_msg_HOT_DEPLOY_CREATE_USER_CONF(self, msg, *args):
        return self.on_broker_msg_hot_deploy(msg, 'zato.pickup.on-update-user-conf',
            {'data': msg.data, 'file_name': msg.file_name}, 'CREATE_USER_CONF', *args)

# ################################################################################################################################

    def on_broker_msg_HOT_DEPLOY_AFTER_DEPLOY(self, msg, *args):
        self.rbac.create_resource(msg.id)

# ################################################################################################################################

    def on_broker_msg_STATS_DELETE(self, msg, *args):
        start = parse(msg.start)
        stop = parse(msg.stop)

        # Looks weird but this is so we don't have to create a list instead of a generator
        # (and Python 3 won't leak the last element anymore)
        last_elem = None

        # Are the dates are at least a day apart? If so, we'll split the interval
        # into smaller one day-long batches.
        if(stop-start).days:
            for elem1, elem2 in pairwise(elem for elem in rrule(DAILY, dtstart=start, until=stop)):
                self.broker_client.invoke_async(
                    {'action':broker_message.STATS.DELETE_DAY.value, 'start':elem1.isoformat(), 'stop':elem2.isoformat()})

                # So as not to drown the broker with a sudden surge of messages
                sleep(0.02)

                last_elem = elem2

            # It's possible we still have something left over. Let's say
            #
            # start = '2012-07-24T02:02:53'
            # stop = '2012-07-25T02:04:53'
            #
            # The call to rrule(DAILY, ...) will nicely slice the time between
            # start and stop into one day intervals yet the last element of the slice
            # will have the time portion equal to that of start - so in this
            # particular case it would be that last_elem was 2012-07-25T02:02:53
            # which would be still be 2 minutes short of stop. Hence the need for
            # a relativedelta, to tease out the remaining time information.
            delta = relativedelta(stop, last_elem)
            if delta.minutes:
                self.stats_maint.delete(last_elem, stop, MINUTELY)

        # Not a full day apart so we can delete everything ourselves
        else:
            self.stats_maint.delete(start, stop, MINUTELY)

    def on_broker_msg_STATS_DELETE_DAY(self, msg, *args):
        self.stats_maint.delete(parse(msg.start), parse(msg.stop), MINUTELY)

# ################################################################################################################################

    def on_broker_msg_SERVICE_PUBLISH(self, msg, args=None):
        return self.on_message_invoke_service(msg, msg.get('channel') or CHANNEL.INVOKE_ASYNC, 'SERVICE_PUBLISH', args)

# ################################################################################################################################

    def on_broker_msg_MSG_NS_CREATE(self, msg, *args):
        """ Creates a new namespace.
        """
        self.msg_ns_store.on_broker_msg_MSG_NS_CREATE(msg, *args)

    def on_broker_msg_MSG_NS_EDIT(self, msg, *args):
        """ Updates an existing namespace.
        """
        self.msg_ns_store.on_broker_msg_MSG_NS_EDIT(msg, *args)

    def on_broker_msg_MSG_NS_DELETE(self, msg, *args):
        """ Deletes a namespace.
        """
        self.msg_ns_store.on_broker_msg_MSG_NS_DELETE(msg, *args)

# ################################################################################################################################

    def on_broker_msg_MSG_XPATH_CREATE(self, msg, *args):
        """ Creates a new XPath.
        """
        self.xpath_store.on_broker_msg_create(msg, self.msg_ns_store.ns_map)

    def on_broker_msg_MSG_XPATH_EDIT(self, msg, *args):
        """ Updates an existing XPath.
        """
        self.xpath_store.on_broker_msg_edit(msg, self.msg_ns_store.ns_map)

    def on_broker_msg_MSG_XPATH_DELETE(self, msg, *args):
        """ Deletes an XPath.
        """
        self.xpath_store.on_broker_msg_delete(msg, *args)

# ################################################################################################################################

    def on_broker_msg_MSG_JSON_POINTER_CREATE(self, msg, *args):
        """ Creates a new JSON Pointer.
        """
        self.json_pointer_store.on_broker_msg_create(msg)

    def on_broker_msg_MSG_JSON_POINTER_EDIT(self, msg, *args):
        """ Updates an existing JSON Pointer.
        """
        self.request_dispatcher.url_data.on_broker_msg_MSG_JSON_POINTER_EDIT(msg)
        self.json_pointer_store.on_broker_msg_edit(msg)

    def on_broker_msg_MSG_JSON_POINTER_DELETE(self, msg, *args):
        """ Deletes an JSON Pointer.
        """
        # Delete the pattern from its store
        self.json_pointer_store.on_broker_msg_delete(msg, *args)

        # Delete the pattern from url_data's cache and let know servers that it should be deleted from the ODB as well
        for item_id, pattern_list in self.request_dispatcher.url_data.on_broker_msg_MSG_JSON_POINTER_DELETE(msg):

            # This is a bit inefficient, if harmless, because each worker in a cluster will publish it
            # so the list of patterns will be updated that many times.

            msg = {}
            msg['action'] = broker_message.SERVICE.PUBLISH.value
            msg['service'] = 'zato.http-soap.set-audit-replace-patterns'
            msg['payload'] = {'id':item_id, 'audit_repl_patt_type':MSG_PATTERN_TYPE.JSON_POINTER.id, 'pattern_list':pattern_list}
            msg['cid'] = new_cid()
            msg['channel'] = CHANNEL.WORKER
            msg['data_format'] = DATA_FORMAT.JSON

            self.broker_client.invoke_async(msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_HTTP_SOAP_AUDIT_RESPONSE(self, msg, *args):
        return self.on_message_invoke_service(msg, CHANNEL.AUDIT, 'SCHEDULER_JOB_EXECUTED', args)

    def on_broker_msg_CHANNEL_HTTP_SOAP_AUDIT_CONFIG(self, msg, *args):
        return self.request_dispatcher.url_data.on_broker_msg_CHANNEL_HTTP_SOAP_AUDIT_CONFIG(msg)

    def on_broker_msg_CHANNEL_HTTP_SOAP_AUDIT_STATE(self, msg, *args):
        return self.request_dispatcher.url_data.on_broker_msg_CHANNEL_HTTP_SOAP_AUDIT_STATE(msg)

    def on_broker_msg_CHANNEL_HTTP_SOAP_AUDIT_PATTERNS(self, msg, *args):
        return self.request_dispatcher.url_data.on_broker_msg_CHANNEL_HTTP_SOAP_AUDIT_PATTERNS(msg)

# ################################################################################################################################

    def _on_broker_msg_cloud_create_edit(self, msg, conn_type, config_dict, wrapper_class):

        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']

        # .. delete the connection if it exists ..
        self._delete_config_close_wrapper(del_name, config_dict, conn_type, logger.debug)

        # .. and create a new one
        msg['queue_build_cap'] = float(self.server.fs_server_config.misc.queue_build_cap)
        wrapper = wrapper_class(msg, self.server)
        wrapper.build_queue()

        item = Bunch()

        config_dict[msg['name']] = item
        config_dict[msg['name']].config = msg
        config_dict[msg['name']].conn = wrapper

        return item

# ################################################################################################################################

    def on_broker_msg_CLOUD_OPENSTACK_SWIFT_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an OpenStack Swift connection.
        """
        self._on_broker_msg_cloud_create_edit(msg, 'OpenStack Swift', self.worker_config.cloud_openstack_swift, SwiftWrapper)

    def on_broker_msg_CLOUD_OPENSTACK_SWIFT_DELETE(self, msg, *args):
        """ Closes and deletes an OpenStack Swift connection.
        """
        self._delete_config_close_wrapper(msg['name'], self.worker_config.cloud_openstack_swift, 'OpenStack Swift', logger.debug)

# ################################################################################################################################

    def on_broker_msg_CLOUD_AWS_S3_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an AWS S3 connection.
        """
        self._update_aws_config(msg)
        self._on_broker_msg_cloud_create_edit(msg, 'AWS S3', self.worker_config.cloud_aws_s3, S3Wrapper)

    def on_broker_msg_CLOUD_AWS_S3_DELETE(self, msg, *args):
        """ Closes and deletes an AWS S3 connection.
        """
        self._delete_config_close_wrapper(msg['name'], self.worker_config.cloud_aws_s3, 'AWS S3', logger.debug)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_ODOO_CREATE(self, msg, *args):
        """ Creates or updates an Odoo connection.
        """
        self._on_broker_msg_cloud_create_edit(msg, 'Odoo', self.worker_config.out_odoo, OdooWrapper)

    on_broker_msg_OUTGOING_ODOO_CHANGE_PASSWORD = on_broker_msg_OUTGOING_ODOO_EDIT = on_broker_msg_OUTGOING_ODOO_CREATE

    def on_broker_msg_OUTGOING_ODOO_DELETE(self, msg, *args):
        """ Closes and deletes an Odoo connection.
        """
        self._delete_config_close_wrapper(msg['name'], self.worker_config.out_odoo, 'Odoo', logger.debug)

# ################################################################################################################################

    def on_broker_msg_NOTIF_RUN_NOTIFIER(self, msg):
        self.on_message_invoke_service(loads(msg.request), CHANNEL.NOTIFIER_RUN, 'NOTIF_RUN_NOTIFIER')

# ################################################################################################################################

    def on_broker_msg_NOTIF_CLOUD_OPENSTACK_SWIFT_CREATE_EDIT(self, msg):
        self.create_edit_notifier(msg, 'NOTIF_CLOUD_OPENSTACK_SWIFT_CREATE_EDIT',
            self.server.worker_store.worker_config.notif_cloud_openstack_swift,
            self._update_cloud_openstack_swift_container)

    def on_broker_msg_NOTIF_CLOUD_OPENSTACK_SWIFT_DELETE(self, msg):
        del self.server.worker_store.worker_config.notif_cloud_openstack_swift[msg.name]

# ################################################################################################################################

    def _on_broker_msg_NOTIF_SQL_CREATE_EDIT(self, msg, source_service_type):
        msg.source_service_type = source_service_type
        self.create_edit_notifier(msg, 'NOTIF_SQL', self.server.worker_store.worker_config.notif_sql)

    def on_broker_msg_NOTIF_SQL_CREATE(self, msg):
        self._on_broker_msg_NOTIF_SQL_CREATE_EDIT(msg, 'create')

    def on_broker_msg_NOTIF_SQL_EDIT(self, msg):
        self._on_broker_msg_NOTIF_SQL_CREATE_EDIT(msg, 'edit')

    def on_broker_msg_NOTIF_SQL_DELETE(self, msg):
        del self.server.worker_store.worker_config.notif_sql[msg.name]

# ################################################################################################################################

    def update_cassandra_conn(self, msg):
        for name in 'tls_ca_certs', 'tls_client_cert', 'tls_client_priv_key':
            value = msg.get(name)
            if value:
                value = os.path.join(self.server.repo_location, 'tls', value)
                msg[name] = value

    def on_broker_msg_DEFINITION_CASSANDRA_CREATE(self, msg):
        self.cassandra_api.create_def(msg.name, msg)
        self.update_cassandra_conn(msg)

    def on_broker_msg_DEFINITION_CASSANDRA_EDIT(self, msg):
        # It might be a rename
        dispatcher.notify(broker_message.DEFINITION.CASSANDRA_EDIT.value, msg)
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.update_cassandra_conn(msg)
        new_def = self.cassandra_api.edit_def(del_name, msg)
        self.cassandra_query_store.update_by_def(del_name, new_def)

    def on_broker_msg_DEFINITION_CASSANDRA_DELETE(self, msg):
        dispatcher.notify(broker_message.DEFINITION.CASSANDRA_DELETE.value, msg)
        self.cassandra_api.delete_def(msg.name)

    def on_broker_msg_DEFINITION_CASSANDRA_CHANGE_PASSWORD(self, msg):
        dispatcher.notify(broker_message.DEFINITION.CASSANDRA_CHANGE_PASSWORD.value, msg)
        self.cassandra_api.change_password_def(msg)

# ################################################################################################################################

    def on_broker_msg_QUERY_CASSANDRA_CREATE(self, msg):
        self.cassandra_query_api.create(msg.name, msg, def_=self.cassandra_api[msg.def_name])

    def on_broker_msg_QUERY_CASSANDRA_EDIT(self, msg):
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.cassandra_query_api.edit(del_name, msg, def_=self.cassandra_api[msg.def_name])

    def on_broker_msg_QUERY_CASSANDRA_DELETE(self, msg):
        self.cassandra_query_api.delete(msg.name)

# ################################################################################################################################

    def on_broker_msg_SEARCH_ES_CREATE(self, msg):
        self.search_es_api.create(msg.name, msg)

    def on_broker_msg_SEARCH_ES_EDIT(self, msg):
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.search_es_api.edit(del_name, msg)

    def on_broker_msg_SEARCH_ES_DELETE(self, msg):
        self.search_es_api.delete(msg.name)

# ################################################################################################################################

    def on_broker_msg_SEARCH_SOLR_CREATE(self, msg):
        self._update_queue_build_cap(msg)
        self.search_solr_api.create(msg.name, msg)

    def on_broker_msg_SEARCH_SOLR_EDIT(self, msg):
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self._update_queue_build_cap(msg)
        self.search_solr_api.edit(del_name, msg)

    def on_broker_msg_SEARCH_SOLR_DELETE(self, msg):
        self.search_solr_api.delete(msg.name)

# ################################################################################################################################

    def on_broker_msg_EMAIL_SMTP_CREATE(self, msg):
        self.email_smtp_api.create(msg.name, msg)

    def on_broker_msg_EMAIL_SMTP_EDIT(self, msg):
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        msg.password = self.email_smtp_api.get(del_name, True).config.password
        self.email_smtp_api.edit(del_name, msg)

    def on_broker_msg_EMAIL_SMTP_DELETE(self, msg):
        self.email_smtp_api.delete(msg.name)

    def on_broker_msg_EMAIL_SMTP_CHANGE_PASSWORD(self, msg):
        self.email_smtp_api.change_password(msg)

# ################################################################################################################################

    def on_broker_msg_EMAIL_IMAP_CREATE(self, msg):
        self.email_imap_api.create(msg.name, msg)

    def on_broker_msg_EMAIL_IMAP_EDIT(self, msg):
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        msg.password = self.email_imap_api.get(del_name, True).config.password
        self.email_imap_api.edit(del_name, msg)

    def on_broker_msg_EMAIL_IMAP_DELETE(self, msg):
        self.email_imap_api.delete(msg.name)

    def on_broker_msg_EMAIL_IMAP_CHANGE_PASSWORD(self, msg):
        self.email_imap_api.change_password(msg)

# ################################################################################################################################

    def on_broker_msg_RBAC_PERMISSION_CREATE(self, msg):
        self.rbac.create_permission(msg.id, msg.name)

    def on_broker_msg_RBAC_PERMISSION_EDIT(self, msg):
        self.rbac.edit_permission(msg.id, msg.name)

    def on_broker_msg_RBAC_PERMISSION_DELETE(self, msg):
        self.rbac.delete_permission(msg.id)

# ################################################################################################################################

    def on_broker_msg_RBAC_ROLE_CREATE(self, msg):
        self.rbac.create_role(msg.id, msg.name, msg.parent_id)

    def on_broker_msg_RBAC_ROLE_EDIT(self, msg):
        self.rbac.edit_role(msg.id, msg.old_name, msg.name, msg.parent_id)

    def on_broker_msg_RBAC_ROLE_DELETE(self, msg):
        self.rbac.delete_role(msg.id, msg.name)

# ################################################################################################################################

    def on_broker_msg_RBAC_CLIENT_ROLE_CREATE(self, msg):
        self.rbac.create_client_role(msg.client_def, msg.role_id)

    def on_broker_msg_RBAC_CLIENT_ROLE_DELETE(self, msg):
        self.rbac.delete_client_role(msg.client_def, msg.role_id)

# ################################################################################################################################

    def on_broker_msg_RBAC_ROLE_PERMISSION_CREATE(self, msg):
        self.rbac.create_role_permission_allow(msg.role_id, msg.perm_id, msg.service_id)

    def on_broker_msg_RBAC_ROLE_PERMISSION_DELETE(self, msg):
        self.rbac.delete_role_permission_allow(msg.role_id, msg.perm_id, msg.service_id)

# ################################################################################################################################

    def zmq_channel_create_edit(self, name, msg, action, lock_timeout, start):
        with self.server.zato_lock_manager(msg.config_cid, ttl=10, block=lock_timeout):
            self._set_up_zmq_channel(name, msg, action, start)

# ################################################################################################################################

    def zmq_channel_create(self, msg):
        self.zmq_channel_create_edit(msg.name, msg, 'create', 0, True)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_ZMQ_CREATE(self, msg):
        if self.server.zato_lock_manager.acquire(msg.config_cid, ttl=10, block=False):
            start_connectors(self, 'zato.channel.zmq.start', msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_ZMQ_EDIT(self, msg):

        # Each worker uses a unique bind port
        msg = bunchify(msg)
        update_bind_port(msg, self.worker_idx)

        self.zmq_channel_create_edit(msg.old_name, msg, 'edit', 5, False)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_ZMQ_DELETE(self, msg):
        with self.server.zato_lock_manager(msg.config_cid, ttl=10, block=5):
            api = self.zmq_mdp_v01_api if msg.socket_type.startswith(ZMQ.MDP) else self.zmq_channel_api
            if msg.name in api.connectors:
                api.delete(msg.name)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_ZMQ_CREATE(self, msg):
        print(333, msg)
        self.zmq_out_api.create(msg.name, msg)

    def on_broker_msg_OUTGOING_ZMQ_EDIT(self, msg):
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.zmq_out_api.edit(del_name, msg)

    def on_broker_msg_OUTGOING_ZMQ_DELETE(self, msg):
        self.zmq_out_api.delete(msg.name)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_STOMP_CREATE(self, msg):
        self.stomp_outconn_api.create_def(msg.name, msg)

    def on_broker_msg_OUTGOING_STOMP_EDIT(self, msg):
        dispatcher.notify(broker_message.OUTGOING.STOMP_EDIT.value, msg)
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.stomp_outconn_api.edit_def(del_name, msg)

    def on_broker_msg_OUTGOING_STOMP_DELETE(self, msg):
        dispatcher.notify(broker_message.OUTGOING.STOMP_DELETE.value, msg)
        self.stomp_outconn_api.delete_def(msg.name)

    def on_broker_msg_OUTGOING_STOMP_CHANGE_PASSWORD(self, msg):
        dispatcher.notify(broker_message.OUTGOING.STOMP_CHANGE_PASSWORD.value, msg)
        self.stomp_outconn_api.change_password_def(msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_STOMP_CREATE(self, msg):
        self.stomp_channel_api.create_def(msg.name, msg, stomp_channel_main_loop, self)

    def on_broker_msg_CHANNEL_STOMP_EDIT(self, msg):
        dispatcher.notify(broker_message.CHANNEL.STOMP_EDIT.value, msg)
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.stomp_channel_api.edit_def(del_name, msg, stomp_channel_main_loop, self)

    def on_broker_msg_CHANNEL_STOMP_DELETE(self, msg):
        dispatcher.notify(broker_message.CHANNEL.STOMP_DELETE.value, msg)
        self.stomp_channel_api.delete_def(msg.name)

    def on_broker_msg_CHANNEL_STOMP_CHANGE_PASSWORD(self, msg):
        dispatcher.notify(broker_message.CHANNEL.STOMP_CHANGE_PASSWORD.value, msg)
        self.stomp_channel_api.change_password_def(msg)

# ################################################################################################################################

    def on_ipc_message(self, msg, success=IPC.STATUS.SUCCESS, failure=IPC.STATUS.FAILURE):

        # If there is target_pid we cannot continue if we are not the recipient.
        if msg.target_pid and msg.target_pid != self.server.pid:
            return

        # We get here if there is no target_pid or if there is one and it matched that of ours.

        try:
            response = self.invoke(msg.service, msg.payload, channel=CHANNEL.IPC, data_format=msg.data_format)
            status = success
        except Exception, e:
            response = format_exc(e)
            status = failure
        finally:
            data = '{};{}'.format(status, response)

        with open(msg.reply_to_fifo, 'wb') as fifo:
            fifo.write(data)

# ################################################################################################################################
