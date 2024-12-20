# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger
from tempfile import NamedTemporaryFile
from time import sleep
from random import choice, randint
from unittest import TestCase
from uuid import uuid4

# Bunch
from bunch import Bunch, bunchify

# mock
from mock import MagicMock, Mock

# six
from six import string_types

# SQLAlchemy
from sqlalchemy import create_engine

# Zato
from zato.common.api import CHANNEL, DATA_FORMAT, SIMPLE_IO
from zato.common.ext.configobj_ import ConfigObj
from zato.common.json_internal import loads
from zato.common.log_message import CID_LENGTH
from zato.common.marshal_.api import MarshalAPI
from zato.common.odb import model
from zato.common.odb.model import Cluster, ElasticSearch
from zato.common.odb.api import SessionWrapper, SQLConnectionPool
from zato.common.odb.query import search_es_list
from zato.common.simpleio_ import get_bytes_to_str_encoding, get_sio_server_config, simple_io_conf_contents
from zato.common.py23_ import maxint
from zato.common.typing_ import cast_
from zato.common.util.api import is_port_taken, new_cid
from zato.server.service import Service

# Zato - Cython
from zato.simpleio import CySimpleIO

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import basestring, cmp, unicode, xrange

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.odb.api import ODBManager
    from zato.common.typing_ import any_, anydict, anylist, intnone, strnone
    from zato.common.util.search import SearchResults
    ODBManager = ODBManager
    SearchResults = SearchResults

# ################################################################################################################################
# ################################################################################################################################

test_class_name = '<my-test-class>'

# ################################################################################################################################
# ################################################################################################################################

class test_odb_data:
    cluster_id = 1
    name = 'my.name'
    is_active = True
    es_hosts = 'my.hosts'
    es_timeout = 111
    es_body_as = 'my.body_as'

# ################################################################################################################################
# ################################################################################################################################

class PubSubConfig:
    PathPublish     = '/zato/pubsub/topic/'
    PathReceive     = '/zato/pubsub/topic/'
    PathSubscribe   = '/zato/pubsub/subscribe/topic/'
    PathUnsubscribe = '/zato/pubsub/subscribe/topic/'
    TestTopicPrefix = '/zato/test/internal/'

# ################################################################################################################################
# ################################################################################################################################

def rand_bool():
    return choice((True, False))

# ################################################################################################################################

def rand_csv(count=3):
    return ','.join(str(elem) for elem in rand_int(count=count))

# ################################################################################################################################

def rand_dict():
    out = {}
    funcs = [rand_bool, rand_int, rand_string]

    for _x in range(rand_int(30)):
        out[choice(funcs)()] = choice(funcs)()

    return out

# ################################################################################################################################

def rand_list():
    out = []
    funcs = [rand_bool, rand_int, rand_string]

    for _x in range(rand_int(30)):
        out.append(choice(funcs)())

    return out

# ################################################################################################################################

def rand_list_of_dicts():
    out = []
    for _x in range(rand_int(30)):
        out.append(rand_dict())
    return out

# ################################################################################################################################

def rand_opaque():
    return rand_object()

rand_nested = rand_opaque

# ################################################################################################################################

def rand_datetime(to_string=True):
    value = datetime.utcnow() # Current time is as random any other
    return value.isoformat() if to_string else value

# ################################################################################################################################

def rand_int(start:'int'=1, stop:'int'=100, count:'int'=1) -> 'any_':
    if count == 1:
        return randint(start, stop)
    else:
        return [randint(start, stop) for x in range(count)]

# ################################################################################################################################

def rand_float(start=1.0, stop=100.0):
    return float(rand_int(start, stop))

# ################################################################################################################################

def rand_string(count=1, prefix='') -> 'any_':
    prefix = ('-' + prefix + '-') if prefix else ''

    if count == 1:
        return 'a' + prefix + uuid4().hex
    else:
        return ['a' + prefix + uuid4().hex for x in range(count)]

# ################################################################################################################################

def rand_unicode():
    return 'abc-123-ϠϡϢ-ΩΩΩ-ÞÞÞ'

# ################################################################################################################################

def rand_object():
    return object()

# ################################################################################################################################

def rand_date_utc(as_string=False):
    value = datetime.utcnow() # Now is as random as any other date
    if as_string:
        return cast_(str, value.isoformat())
    return value

# ################################################################################################################################

def is_like_cid(cid):
    """ Raises ValueError if the cid given on input does not look like a genuine CID
    produced by zato.common.util.new_cid
    """
    if not isinstance(cid, string_types):
        raise ValueError('CID `{}` should be string like instead of `{}`'.format(cid, type(cid)))

    len_given = len(cid)

    if len_given != CID_LENGTH:
        raise ValueError('CID `{}` should have length `{}` instead of `{}`'.format(cid, CID_LENGTH, len_given))

    return True

# ################################################################################################################################

def get_free_tcp_port(start=40000, stop=40500):
    """ Iterates between start and stop, returning first free TCP port. Must not be used except for tests because
    it comes with a race condition - another process may want to bind the port we find before our caller does.
    """
    for port in xrange(start, stop):
        if not is_port_taken(port):
            return port
    else:
        raise Exception('Could not find any free TCP port between {} and {}'.format(start, stop))

# ################################################################################################################################

def enrich_with_static_config(object_):
    """ Adds to an object (service instance or class) all attributes that are added by service store.
    Useful during tests since there is no service store around to do it.
    """
    object_.component_enabled_ibm_mq = True
    object_.component_enabled_zeromq = True
    object_.component_enabled_patterns = True
    object_.component_enabled_target_matcher = True
    object_.component_enabled_invoke_matcher = True
    object_.component_enabled_sms = True
    object_.get_name()

    def target_match(*args, **kwargs):
        return True

    is_allowed = target_match

    object_._worker_config = Bunch(out_odoo=None, out_soap=None)
    object_._worker_store = Bunch(
        sql_pool_store=None, outgoing_web_sockets=None, cassandra_api=None,
        cassandra_query_api=None, email_smtp_api=None, email_imap_api=None, search_es_api=None, search_solr_api=None,
        target_matcher=Bunch(target_match=target_match, is_allowed=is_allowed), invoke_matcher=Bunch(is_allowed=is_allowed),
        vault_conn_api=None, sms_twilio_api=None)

# ################################################################################################################################
# ################################################################################################################################

class TestCluster:
    def __init__(self, name:'str') -> 'None':
        self.name = name

# ################################################################################################################################
# ################################################################################################################################

class TestParallelServer:
    def __init__(
        self,
        cluster,    # type: TestCluster
        odb,        # type: ODBManager
        server_name # type: str
    ) -> 'None':
        self.cluster = cluster
        self.cluster_name = self.cluster.name
        self.odb = odb
        self.name = server_name

    def decrypt(self, data:'str') -> 'str':
        return data

    def invoke_all_pids(*args, **kwargs):
        return []

# ################################################################################################################################
# ################################################################################################################################

class Expected:
    """ A container for the data a test expects the service to return.
    """
    def __init__(self):
        self.data = []

    def add(self, item):
        self.data.append(item)

    def get_data(self):
        if not self.data or len(self.data) > 1:
            return self.data
        else:
            return self.data[0]

# ################################################################################################################################
# ################################################################################################################################

class TestBrokerClient:

    def __init__(self):
        self.publish_args = []
        self.publish_kwargs = []
        self.invoke_async_args = []
        self.invoke_async_kwargs = []

    def publish(self, *args, **kwargs):
        raise NotImplementedError()

    def invoke_async(self, *args, **kwargs):
        self.invoke_async_args.append(args)
        self.invoke_async_kwargs.append(kwargs)

# ################################################################################################################################
# ################################################################################################################################

class TestKVDB:

    class TestConn:
        def __init__(self):
            self.setnx_args = None
            self.setnx_return_value = True
            self.expire_args = None
            self.delete_args = None

        def return_none(self, *ignored_args, **ignored_kwargs):
            return None

        get = hget = return_none

        def setnx(self, *args):
            self.setnx_args = args
            return self.setnx_return_value

        def expire(self, *args):
            self.expire_args = args

        def delete(self, args):
            self.delete_args = args

    def __init__(self):
        self.conn = self.TestConn()

    def translate(self, *ignored_args, **ignored_kwargs):
        raise NotImplementedError()

# ################################################################################################################################
# ################################################################################################################################

class TestServices:
    def __getitem__(self, ignored):
        return {'slow_threshold': 1234}

# ################################################################################################################################
# ################################################################################################################################

class TestServiceStore:
    def __init__(self, name_to_impl_name=None, impl_name_to_service=None):
        self.services = TestServices()
        self.name_to_impl_name = name_to_impl_name or {}
        self.impl_name_to_service = impl_name_to_service or {}

    def new_instance(self, impl_name, is_active=True):
        return self.impl_name_to_service[impl_name](), is_active

# ################################################################################################################################
# ################################################################################################################################

class TestODB:
    def session(self, *ignored_args, **ignored_kwargs):
        pass

# ################################################################################################################################
# ################################################################################################################################

class TestServer:

    def __init__(self, service_store_name_to_impl_name=None, service_store_impl_name_to_service=None, worker_store=None):

        self.odb = TestODB()
        self.kvdb = TestKVDB()
        self.service_store = TestServiceStore(service_store_name_to_impl_name, service_store_impl_name_to_service)
        self.marshal_api = MarshalAPI()
        self.worker_store = worker_store

        self.repo_location = rand_string()
        self.delivery_store = None
        self.user_config = Bunch()
        self.static_config = Bunch()
        self.time_util = Bunch()
        self.servers = []
        self.ipc_api = None
        self.component_enabled = Bunch()

        self.cluster_id = 1
        self.name = 'TestServerObject'
        self.pid = 9988

        self.fs_server_config = Bunch()

        self.fs_server_config.misc = Bunch()
        self.fs_server_config.misc.zeromq_connect_sleep = 0.1
        self.fs_server_config.misc.internal_services_may_be_deleted = False

        self.fs_server_config.pubsub = Bunch()
        self.fs_server_config.pubsub_meta_topic = Bunch()
        self.fs_server_config.pubsub_meta_endpoint_pub = Bunch()

        self.fs_server_config.pubsub.data_prefix_len = 9999
        self.fs_server_config.pubsub.data_prefix_short_len = 123
        self.fs_server_config.pubsub.log_if_deliv_server_not_found = True
        self.fs_server_config.pubsub.log_if_wsx_deliv_server_not_found = False

        self.fs_server_config.pubsub_meta_topic.enabled = True
        self.fs_server_config.pubsub_meta_topic.store_frequency = 1

        self.fs_server_config.pubsub_meta_endpoint_pub.enabled = True
        self.fs_server_config.pubsub_meta_endpoint_pub.store_frequency = 1
        self.fs_server_config.pubsub_meta_endpoint_pub.data_len = 1234
        self.fs_server_config.pubsub_meta_endpoint_pub.max_history = 111

        self.ctx = {}

# ################################################################################################################################

    def invoke(self, service:'any_', request:'any_') -> 'None':
        self.ctx['service'] = service
        self.ctx['request'] = request

# ################################################################################################################################

    def on_wsx_outconn_stopped_running(self, conn_id:'str') -> 'None':
        pass

# ################################################################################################################################

    def on_wsx_outconn_connected(self, conn_id:'str') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class SIOElemWrapper:
    """ Makes comparison between two SIOElem elements use their names.
    """
    def __init__(self, value):
        self.value = value

    def __cmp__(self, other):
        # Compare to either other's name or to other directly. In the latter case it means it's a plain string name
        # of a SIO attribute.
        return cmp(self.value.name, getattr(other, 'name', other))

# ################################################################################################################################
# ################################################################################################################################

class ServiceTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        self.maxDiff = None
        super(ServiceTestCase, self).__init__(*args, **kwargs)

    def invoke(self, class_, request_data, expected, mock_data=None, channel=CHANNEL.HTTP_SOAP, job_type=None,
        data_format=DATA_FORMAT.JSON, service_store_name_to_impl_name=None, service_store_impl_name_to_service=None):
        """ Sets up a service's invocation environment, then invokes and returns
        an instance of the service.
        """
        mock_data = mock_data or {}
        class_.component_enabled_email = True
        class_.component_enabled_search = True
        class_.component_enabled_msg_path = True
        class_.has_sio = getattr(class_, 'SimpleIO', False)

        instance = class_()

        server = MagicMock()
        server.component_enabled.stats = False

        worker_store = MagicMock()
        worker_store.worker_config = MagicMock
        worker_store.worker_config.outgoing_connections = MagicMock(return_value=(None, None, None, None))
        worker_store.worker_config.cloud_aws_s3 = MagicMock(return_value=None)
        worker_store.invoke_matcher.is_allowed = MagicMock(return_value=True)

        simple_io_config = {
            'int_parameters': SIMPLE_IO.INT_PARAMETERS.VALUES,
            'int_parameter_suffixes': SIMPLE_IO.INT_PARAMETERS.SUFFIXES,
            'bool_parameter_prefixes': SIMPLE_IO.BOOL_PARAMETERS.SUFFIXES,
        }

        class_.update(
            instance, channel, TestServer(service_store_name_to_impl_name, service_store_impl_name_to_service, worker_store),
            None, worker_store, new_cid(), request_data, request_data, simple_io_config=simple_io_config,
            data_format=data_format, job_type=job_type)

        def get_data(self, *ignored_args, **ignored_kwargs):
            return expected.get_data()

        instance.get_data = get_data

        for attr_name, mock_path_data_list in mock_data.items():
            setattr(instance, attr_name, Mock())
            attr = getattr(instance, attr_name)

            for mock_path_data in mock_path_data_list:
                for path, value in mock_path_data.items():
                    split = path.split('.')
                    new_path = '.return_value.'.join(elem for elem in split) + '.return_value'
                    attr.configure_mock(**{new_path:value})

        broker_client_publish = getattr(self, 'broker_client_publish', None)
        if broker_client_publish:
            instance.broker_client = TestBrokerClient()
            instance.broker_client.publish = broker_client_publish

        def set_response_func(*args, **kwargs):
            pass

        instance.handle()
        instance.update_handle(
            set_response_func, instance, request_data, channel, data_format, None, server, None, worker_store, new_cid(),
            None)
        return instance

    def _check_sio_request_input(self, instance, request_data):
        for k, v in request_data.items():
            self.assertEqual(getattr(instance.request.input, k), v)

        sio_keys = set(getattr(instance.SimpleIO, 'input_required', []))
        sio_keys.update(set(getattr(instance.SimpleIO, 'input_optional', [])))
        given_keys = set(request_data.keys())

        diff = sio_keys ^ given_keys
        self.assertFalse(diff, 'There should be no difference between sio_keys {} and given_keys {}, diff {}'.format(
            sio_keys, given_keys, diff))

    def check_impl(self, service_class, request_data, response_data, response_elem, mock_data=None):
        mock_data = mock_data or {}
        expected_data = sorted(response_data.items())

        instance = self.invoke(service_class, request_data, None, mock_data)
        self._check_sio_request_input(instance, request_data)

        if response_data:
            if not isinstance(instance.response.payload, basestring):
                response = loads(instance.response.payload.getvalue())[response_elem] # Raises KeyError if 'response_elem' doesn't match
            else:
                response = loads(instance.response.payload)[response_elem]

            self.assertEqual(sorted(response.items()), expected_data)

    def check_impl_list(self, service_class, item_class, request_data, # noqa
            response_data, request_elem, response_elem, mock_data={}): # noqa

        expected_keys = response_data.keys()
        expected_data = tuple(response_data for x in range(rand_int(10)))
        expected = Expected()

        for datum in expected_data:
            item = item_class()
            for key in expected_keys:
                value = getattr(datum, key)
                setattr(item, key, value)
            expected.add(item)

        instance = self.invoke(service_class, request_data, expected, mock_data)
        response = loads(instance.response.payload.getvalue())[response_elem]

        for idx, item in enumerate(response):
            expected = expected_data[idx]
            given = Bunch(item)

            for key in expected_keys:
                given_value = getattr(given, key)
                expected_value = getattr(expected, key)
                self.assertEqual(given_value, expected_value)

        self._check_sio_request_input(instance, request_data)

    def wrap_force_type(self, elem):
        return SIOElemWrapper(elem)

# ################################################################################################################################
# ################################################################################################################################

class ODBTestCase(TestCase):

    def setUp(self):
        engine_url = 'sqlite:///:memory:'
        pool_name = 'ODBTestCase.pool'

        config = {
            'engine': 'sqlite',
            'sqlite_path': ':memory:',
            'fs_sql_config': {
                'engine': {
                    'ping_query': 'SELECT 1'
                }
            }
        }

        # Create a standalone engine ..
        self.engine = create_engine(engine_url)

        # .. all ODB objects for that engine..
        model.Base.metadata.create_all(self.engine)

        # .. an SQL pool too ..
        self.pool = SQLConnectionPool(pool_name, config, config)

        # .. a session wrapper on top of everything ..
        self.session_wrapper = SessionWrapper()
        self.session_wrapper.init_session(pool_name, config, self.pool)

        # .. and all ODB objects for that wrapper's engine too ..
        model.Base.metadata.create_all(self.session_wrapper.pool.engine)

        # Unrelated to the above, used in individual tests
        self.ODBTestModelClass = ElasticSearch

    def tearDown(self):
        model.Base.metadata.drop_all(self.engine)
        self.ODBTestModelClass = None

    def get_session(self):
        return self.session_wrapper.session()

    def get_sample_odb_orm_result(self, is_list):
        # type: (bool) -> object

        cluster = Cluster()
        cluster.id = test_odb_data.cluster_id
        cluster.name = 'my.cluster'
        cluster.odb_type = 'sqlite'
        cluster.broker_host = 'my.broker.host'
        cluster.broker_port = 1234
        cluster.lb_host = 'my.lb.host'
        cluster.lb_port = 5678
        cluster.lb_agent_port = 9012

        es = self.ODBTestModelClass()
        es.name = test_odb_data.name
        es.is_active = test_odb_data.is_active
        es.hosts = test_odb_data.es_hosts
        es.timeout = test_odb_data.es_timeout
        es.body_as = test_odb_data.es_body_as
        es.cluster_id = test_odb_data.cluster_id

        session = self.session_wrapper._session

        session.add(cluster)
        session.add(es)
        session.commit()

        session = self.session_wrapper._session

        result = search_es_list(session, test_odb_data.cluster_id) # type: tuple
        result = result[0] # type: SearchResults

        # This is a one-element tuple of ElasticSearch ORM objects
        result = result.result # type: tuple

        return result if is_list else result[0]

# ################################################################################################################################
# ################################################################################################################################

class MyODBService(Service):
    class SimpleIO:
        output = 'cluster_id', 'is_active', 'name'

# ################################################################################################################################
# ################################################################################################################################

class MyODBServiceWithResponseElem(MyODBService):
    class SimpleIO(MyODBService.SimpleIO):
        response_elem = 'my_response_elem'

# ################################################################################################################################
# ################################################################################################################################

class MyZatoClass:
    def to_zato(self):
        return {
            'cluster_id': test_odb_data.cluster_id,
            'is_active':  test_odb_data.is_active,
            'name':       test_odb_data.name,
        }

# ################################################################################################################################
# ################################################################################################################################

class BaseSIOTestCase(TestCase):

    def setUp(self):
        self.maxDiff = maxint

    def get_server_config(self, needs_response_elem=False):

        with NamedTemporaryFile(delete=False) as f:
            contents = simple_io_conf_contents.format(bytes_to_str_encoding=get_bytes_to_str_encoding())
            if isinstance(contents, unicode):
                contents = contents.encode('utf8')
            f.write(contents)
            f.flush()
            temporary_file_name=f.name

        sio_fs_config = ConfigObj(temporary_file_name)
        sio_fs_config = bunchify(sio_fs_config)

        import os
        os.remove(temporary_file_name)

        sio_server_config = get_sio_server_config(sio_fs_config)

        if not needs_response_elem:
            sio_server_config.response_elem = None

        return sio_server_config

# ################################################################################################################################

    def get_sio(self, declaration, class_):

        sio = CySimpleIO(None, self.get_server_config(), declaration)
        sio.build(class_)

        return sio

# ################################################################################################################################
# ################################################################################################################################

class BaseZatoTestCase(TestCase):

    maxDiff = 1234567890

    def __init__(self, *args, **kwargs) -> 'None':
        self.logger = getLogger('zato.test')
        super().__init__(*args, **kwargs)

    def create_pubsub_topic(
        self,
        *,
        topic_name:  'strnone' = None,
        topic_prefix:'strnone' = PubSubConfig.TestTopicPrefix,
        limit_retention:'intnone' = None,
        limit_message_expiry:'intnone' = None,
        limit_sub_inactivity:'intnone' = None
        ) -> 'anydict':

        if not (topic_name or topic_prefix):
            raise Exception('Either topic_name or topic_prefix is required')

        if topic_name and topic_prefix:
            raise Exception('Cannot provide both topic_name and topic_prefix')

        if not topic_name:
            topic_name = topic_prefix + datetime.utcnow().isoformat()

        # These parameters for the Command to invoke will always exist ..
        cli_params = ['pubsub', 'create-topic', '--name', topic_name]

        self.logger.info(f'Creating topic {topic_name} ({self.__class__.__name__})')

        # .. whereas these ones are optional ..
        if limit_retention:
            cli_params.append('--limit-retention')
            cli_params.append(limit_retention)

        if limit_message_expiry:
            cli_params.append('--limit-message-expiry')
            cli_params.append(limit_message_expiry)

        if limit_sub_inactivity:
            cli_params.append('--limit-sub-inactivity')
            cli_params.append(limit_sub_inactivity)

        # Create the test topic here ..
        return self.run_zato_cli_json_command(cli_params) # type: anydict

# ################################################################################################################################

    def _handle_cli_out(
        self,
        out:'str',
        assert_ok:'bool',
        load_json:'bool' = False
        ) -> 'str':

        # We do not need any extra new lines
        out = out.strip()

        # If told do, make sure that the response indicates a success ..
        if assert_ok:
            self.assertEqual(out, 'OK')

        # .. load a JSON response if configured to do so ..
        if load_json:
            out = loads(out)

        # .. and return our output.
        return out

# ################################################################################################################################

    def run_zato_cli_command(
        self,
        cli_params:'anylist',
        command_name:'str'='zato',
        assert_ok:'bool'=False,
        load_json:'bool'=False,
        ) -> 'any_':

        # Zato
        from zato.common.util.cli import CommandLineInvoker

        # Prepare the invoker ..
        invoker = CommandLineInvoker(check_stdout=False)

        # .. append the path to our test server ..
        cli_params.append('--path')
        cli_params.append(invoker.server_location)

        # .. invoke the service and obtain its response ..
        out = invoker.invoke_cli(cli_params, command_name) # type: str

        # .. let the changes propagate across servers ..
        sleep(1)

        # .. and let the parent class handle the result
        return self._handle_cli_out(out, assert_ok, load_json)

# ################################################################################################################################

    def run_zato_cli_json_command(self, *args, **kwargs) -> 'any_':
        return self.run_zato_cli_command(*args, **kwargs, load_json=True)

# ################################################################################################################################

    def delete_pubsub_topics_by_pattern(self, pattern:'str') -> 'any_':
        cli_params = ['pubsub', 'delete-topics', '--pattern', pattern]
        return self.run_zato_cli_json_command(cli_params)

# ################################################################################################################################
# ################################################################################################################################

class CommandLineTestCase(BaseZatoTestCase):
    pass

# ################################################################################################################################
# ################################################################################################################################

class CommandLineServiceTestCase(BaseZatoTestCase):

    def run_zato_service_test(self, service_name:'str', assert_ok:'bool'=True) -> 'str':

        # Zato
        from zato.common.util.cli import CommandLineServiceInvoker

        # Prepare the invoker
        invoker = CommandLineServiceInvoker(check_stdout=False)

        # .. invoke the service and obtain its response ..
        out = invoker.invoke_and_test(service_name) # type: str

        # .. and let the parent class handle the result
        return self._handle_cli_out(out, assert_ok)

# ################################################################################################################################
# ################################################################################################################################
