# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import httplib
from ast import literal_eval
from cStringIO import StringIO
from datetime import datetime
from json import loads
from unittest import TestCase

# Bunch
from bunch import Bunch

# nose
from nose.tools import eq_

# pytz
from pytz import UTC

# tzlocal
from tzlocal import get_localzone

# Zato
from zato.common import CHANNEL, DATA_FORMAT, ZATO_NONE
from zato.common.broker_message import CHANNEL as CHANNEL_BROKER_MESSAGE, SERVICE
from zato.common.odb.api import ODBManager
from zato.common.test import rand_int, rand_string
from zato.common.util import new_cid, utcnow
from zato.server.connection.http_soap.channel import RequestDispatcher
from zato.server.connection.http_soap.url_data import URLData
from zato.server.base.parallel import ParallelServer
from zato.server.base.parallel.http import ACCESS_LOG_DT_FORMAT

# ################################################################################################################################

class FakeRequestDispatcher(object):
    def __init__(self, url_data=None, expected_payload=None):
        self.url_data = url_data
        self.expected_payload = expected_payload

    def dispatch(self, *ignored_args, **ignored_kwargs):
        return self.expected_payload

class FakeWorkerStore(object):
    def __init__(self, request_dispatcher=None):
        self.request_dispatcher = request_dispatcher or FakeRequestDispatcher()

class FakeGunicornSocket(object):
    def __init__(self, expected_cert_der, expected_cert_dict):
        self.expected_cert_der = expected_cert_der
        self.expected_cert_dict = expected_cert_dict

    def getpeercert(self, needs_der=False):
        if needs_der:
            return self.expected_cert_der
        return self.expected_cert_dict

    def __repr__(self):
        return self.__class__.__name__

class StartResponse(object):
    def __call__(self, *ignored_args, **ignored_kwargs):
        pass

# ################################################################################################################################

class ParallelServerTestCase(TestCase):
    def test__startup_services(self):

        class FakeBrokerClient(object):
            def __init__(self):
                self.messages = {}

            def invoke_async(self, msg):
                self.messages[msg['service']] = msg

        broker_client = FakeBrokerClient()

        startup_services_any_worker = Bunch()
        for x in range(10):
            name = rand_string()
            payload = rand_string()
            startup_services_any_worker[name] = payload

        ps = ParallelServer()
        ps.broker_client = broker_client
        ps.fs_server_config = Bunch()
        ps.fs_server_config.startup_services_any_worker = startup_services_any_worker

        ps.invoke_startup_services(False)

        for expected_service, expected_payload in startup_services_any_worker.items():
            msg = Bunch(broker_client.messages[expected_service])
            eq_(msg.action, SERVICE.PUBLISH.value)
            eq_(msg.channel, CHANNEL.STARTUP_SERVICE)
            eq_(msg.payload, expected_payload)
            eq_(msg.service, expected_service)
            self.assertEquals(len(msg.cid), 24)

# ################################################################################################################################

class AuditTestCase(TestCase):
    def test_audit(self):
        for expected_audit_enabled in(True, False):
            for expected_status_code in(httplib.OK, httplib.FORBIDDEN):
                for use_x_remote_addr in(True, False):

                    expected_auth_ok = True if expected_status_code == httplib.OK else False
                    expected_invoke_ok = True if expected_auth_ok is True else False

                    expected_cid = new_cid()
                    expected_url_scheme = rand_string()
                    expected_payload = rand_string()

                    expected_audit_repl_patt_type = rand_string()
                    expected_replace_patterns_json_pointer = []
                    expected_replace_patterns_xpath = []
                    expected_cluster_id = rand_int()
                    expected_id = rand_int()
                    expected_name = rand_string()
                    expected_password = '******'
                    expected_username = rand_string()
                    expected_transport = rand_string()
                    expected_connection = rand_string()
                    expected_data_format = DATA_FORMAT.JSON
                    expected_is_active = True
                    expected_request = rand_string()
                    expected_audit_max_payload = len(expected_request) - 7 # Substracting any value would do

                    expected_channel_item_key1 = rand_string()
                    expected_channel_item_value1 = rand_string()

                    expected_match_target = rand_string()

                    channel_item = {
                        'id': expected_id,
                        'name': expected_name,
                        'transport': expected_transport,
                        'connection': expected_connection,
                        'audit_enabled': expected_audit_enabled,
                        expected_channel_item_key1:expected_channel_item_value1,
                        'audit_repl_patt_type': expected_audit_repl_patt_type,
                        'replace_patterns_json_pointer': expected_replace_patterns_json_pointer,
                        'replace_patterns_xpath': expected_replace_patterns_xpath,
                        'audit_max_payload': expected_audit_max_payload,
                        'is_active': expected_is_active,
                        'data_format': DATA_FORMAT.JSON,
                        'match_target': expected_match_target,
                        'username': expected_username,
                        'method': '',
                    }

                    wsgi_environ = {
                        'wsgi.url_scheme': expected_url_scheme,
                        'gunicorn.socket': FakeGunicornSocket(None, None),
                        'zato.http.response.status': expected_status_code,
                        'zato.http.channel_item': channel_item,
                        'PATH_INFO': rand_string(),
                        'wsgi.input': StringIO(expected_request),
                        'REQUEST_METHOD': rand_string(),
                        'SERVER_PROTOCOL': rand_string(),
                        'HTTP_USER_AGENT': rand_string(),
                    }

                    expected_remote_addr = rand_string()

                    if use_x_remote_addr:
                        expected_remote_addr_header = 'HTTP_X_FORWARDED_FOR'
                        wsgi_environ[expected_remote_addr_header] = expected_remote_addr
                    else:
                        expected_remote_addr_header = 'REMOTE_ADDR'
                        wsgi_environ[expected_remote_addr_header] = expected_remote_addr

                    class FakeSession:
                        def __init__(self, audit=None):
                            self.audit = audit
                            self.commit_called = False

                        def close(self):
                            pass

                        def commit(self):
                            self.commit_called = True

                        def add(self, audit):
                            self.audit = audit

                    fake_session = FakeSession()

                    class FakeBrokerClient(object):
                        def __init__(self):
                            self.msg = None

                        def publish(self, msg):
                            self.msg = msg

                    class FakeODB(ODBManager):
                        def __init__(self):
                            self.msg = None
                            self.cluster = Bunch(id=expected_cluster_id)

                        def session(self):
                            return fake_session

                    class FakeURLData(URLData):
                        def __init__(self):
                            self.url_sec = {expected_match_target: Bunch(sec_def=ZATO_NONE, sec_use_rbac=False)}

                        def match(self, *ignored_args, **ignored_kwargs):
                            return True, channel_item

                    class FakeRequestHandler(object):
                        def handle(self, *ignored_args, **ignored_kwargs):
                            return Bunch(payload=expected_payload, content_type='text/plain', headers={}, status_code=expected_status_code)

                    bc = FakeBrokerClient()
                    ws = FakeWorkerStore()
                    ws.request_dispatcher = RequestDispatcher()
                    ws.request_dispatcher.request_handler = FakeRequestHandler()
                    ws.request_dispatcher.url_data = FakeURLData()
                    ws.request_dispatcher.url_data.broker_client = bc
                    ws.request_dispatcher.url_data.odb = FakeODB()

                    ps = ParallelServer()
                    ps.worker_store = ws
                    ps.request_dispatcher_dispatch = ws.request_dispatcher.dispatch
                    ps.on_wsgi_request(wsgi_environ, StartResponse(), cid=expected_cid)

                    if expected_audit_enabled:

                        #
                        # Audit 1/2 - Request
                        #

                        # Parsing will confirm the proper value was used
                        datetime.strptime(fake_session.audit.req_time.isoformat(), '%Y-%m-%dT%H:%M:%S.%f')

                        self.assertEquals(fake_session.audit.name, expected_name)
                        self.assertEquals(fake_session.audit.cid, expected_cid)
                        self.assertEquals(fake_session.audit.transport, expected_transport)
                        self.assertEquals(fake_session.audit.connection, expected_connection)
                        self.assertEquals(fake_session.audit.resp_time, None)
                        self.assertEquals(fake_session.audit.user_token, expected_username)
                        self.assertEquals(fake_session.audit.auth_ok, None)
                        self.assertEquals(fake_session.audit.invoke_ok, None)
                        self.assertEquals(fake_session.audit.remote_addr, expected_remote_addr)
                        self.assertEquals(fake_session.audit.req_payload, expected_request[:expected_audit_max_payload])
                        self.assertEquals(fake_session.audit.resp_headers, None)
                        self.assertEquals(fake_session.audit.resp_payload, None)

                        req_headers = literal_eval(fake_session.audit.req_headers)

                        self.assertEquals(req_headers[expected_remote_addr_header], repr(expected_remote_addr))
                        self.assertEquals(req_headers['wsgi.url_scheme'], repr(expected_url_scheme))
                        self.assertEquals(req_headers['gunicorn.socket'], repr(FakeGunicornSocket(None, None)))

                        channel_item = literal_eval(req_headers['zato.http.channel_item'])

                        self.assertEquals(channel_item['audit_max_payload'], expected_audit_max_payload)
                        self.assertEquals(channel_item['name'], expected_name)
                        self.assertEquals(channel_item['username'], expected_username)
                        self.assertEquals(channel_item[expected_channel_item_key1], expected_channel_item_value1)
                        self.assertEquals(channel_item['audit_repl_patt_type'], expected_audit_repl_patt_type)
                        self.assertEquals(channel_item['replace_patterns_json_pointer'], expected_replace_patterns_json_pointer)
                        self.assertEquals(channel_item['is_active'], expected_is_active)
                        self.assertEquals(channel_item['data_format'], expected_data_format)
                        self.assertEquals(channel_item['audit_enabled'], expected_audit_enabled)
                        self.assertEquals(channel_item['password'], expected_password)
                        self.assertEquals(channel_item['transport'], expected_transport)
                        self.assertEquals(channel_item['match_target'], expected_match_target)

                        #
                        # Audit 2/2 - Response
                        #

                        self.assertEquals(bc.msg['action'], CHANNEL_BROKER_MESSAGE.HTTP_SOAP_AUDIT_RESPONSE.value)
                        self.assertEquals(bc.msg['cid'], expected_cid)
                        self.assertEquals(bc.msg['data_format'], DATA_FORMAT.JSON)
                        self.assertEquals(bc.msg['service'], 'zato.http-soap.set-audit-response-data')

                        payload = loads(bc.msg['payload'])

                        self.assertEquals(payload['auth_ok'], expected_auth_ok)
                        self.assertEquals(payload['invoke_ok'], expected_invoke_ok)
                        self.assertEquals(payload['resp_payload'], expected_payload)

                        # Parsing alone will check its format is valid
                        datetime.strptime(payload['resp_time'], '%Y-%m-%dT%H:%M:%S.%f')

                        wsgi_environ = loads(payload['resp_headers'])

                        self.assertEquals(wsgi_environ['wsgi.url_scheme'], repr(expected_url_scheme))
                        self.assertEquals(wsgi_environ['gunicorn.socket'], repr(FakeGunicornSocket(None, None)))
                        self.assertEquals(wsgi_environ['zato.http.response.status'],
                            "'{} {}'".format(
                                expected_status_code,
                                httplib.responses[expected_status_code],
                            ))

                        channel_item = literal_eval(wsgi_environ['zato.http.channel_item'])

                        self.assertEquals(channel_item[expected_channel_item_key1], expected_channel_item_value1)
                        self.assertEquals(channel_item['audit_enabled'], expected_audit_enabled)
                        self.assertEquals(channel_item['audit_repl_patt_type'], expected_audit_repl_patt_type)
                        self.assertEquals(channel_item['replace_patterns_json_pointer'], expected_replace_patterns_json_pointer)
                        self.assertEquals(channel_item['replace_patterns_xpath'], expected_replace_patterns_xpath)
                        self.assertEquals(channel_item['name'], expected_name)
                        self.assertEquals(channel_item['id'], expected_id)
                        self.assertEquals(channel_item['password'], expected_password)
                        self.assertEquals(channel_item['data_format'], expected_data_format)
                        self.assertEquals(channel_item['transport'], expected_transport)
                        self.assertEquals(channel_item['connection'], expected_connection)
                        self.assertEquals(channel_item['audit_max_payload'], expected_audit_max_payload)
                        self.assertEquals(channel_item['is_active'], expected_is_active)
                    else:
                        # Audit not enabled so no response audit message was published on the broker
                        self.assertTrue(bc.msg is None)

# ################################################################################################################################

class HTTPAccessLogTestCase(TestCase):
    def test_access_log(self):

        def _utcnow():
            return datetime(year=2014, month=1, day=12, hour=16, minute=22, second=12, tzinfo=UTC)

        local_tz = get_localzone()
        _now = _utcnow()

        local_dt = _now.replace(tzinfo=UTC).astimezone(local_tz)
        local_dt = local_tz.normalize(local_dt)

        request_timestamp = local_dt.strftime(ACCESS_LOG_DT_FORMAT)

        response = rand_string() * rand_int()
        cid = new_cid()
        cluster_id = 1

        channel_name = rand_string()
        url_path = '/{}'.format(rand_string())
        user_agent = rand_string()
        http_version = rand_string()
        request_method = rand_string()
        remote_ip = '10.{}.{}.{}'.format(rand_int(), rand_int(), rand_int())
        req_timestamp_utc = utcnow()

        channel_item = {
            'name': channel_name,
            'audit_enabled': False,
            'is_active': True,
            'transport': 'plain_http',
            'data_format': None,
            'match_target': url_path,
            'method': '',
        }

        wsgi_environ = {
            'gunicorn.socket': FakeGunicornSocket(None, None),
            'wsgi.url_scheme': 'http',
            'wsgi.input': StringIO(response),

            'zato.http.response.status': httplib.OK,
            'zato.http.channel_item': channel_item,
            'zato.request_timestamp_utc': req_timestamp_utc,

            'HTTP_X_FORWARDED_FOR': remote_ip,
            'PATH_INFO': url_path,
            'REQUEST_METHOD': request_method,
            'SERVER_PROTOCOL': http_version,
            'HTTP_USER_AGENT': user_agent,
        }

        class FakeBrokerClient(object):
            def __init__(self):
                self.msg = None

            def publish(self, msg):
                self.msg = msg

        class FakeODB(ODBManager):
            def __init__(self):
                self.msg = None
                self.cluster = Bunch(id=cluster_id)

        class FakeURLData(URLData):
            def __init__(self):
                self.url_sec = {url_path: Bunch(sec_def=ZATO_NONE, sec_use_rbac=False)}

            def match(self, *ignored_args, **ignored_kwargs):
                return True, channel_item

        class FakeRequestHandler(object):
            def handle(self, *ignored_args, **ignored_kwargs):
                return Bunch(payload=response, content_type='text/plain', headers={}, status_code=httplib.OK)

        class FakeAccessLogger(object):
            def __init__(self):
                self.level = object()
                self.msg = object()
                self.args = object()
                self.exc_info = object()
                self.extra = object()

            def _log(self, level, msg, args, exc_info, extra):
                self.level = level
                self.msg = msg
                self.args
                self.exc_info = exc_info
                self.extra = extra

            def isEnabledFor(self, ignored):
                return True

        bc = FakeBrokerClient()
        ws = FakeWorkerStore()
        ws.request_dispatcher = RequestDispatcher()
        ws.request_dispatcher.request_handler = FakeRequestHandler()
        ws.request_dispatcher.url_data = FakeURLData()
        ws.request_dispatcher.url_data.broker_client = bc
        ws.request_dispatcher.url_data.odb = FakeODB()

        ps = ParallelServer()
        ps.worker_store = ws
        ps.request_dispatcher_dispatch = ws.request_dispatcher.dispatch
        ps.access_logger = FakeAccessLogger()
        ps.access_logger_log = ps.access_logger._log
        ps.on_wsgi_request(wsgi_environ, StartResponse(), cid=cid, _utcnow=_utcnow)

        extra = Bunch(ps.access_logger.extra)

        eq_(extra.channel_name, channel_name)
        eq_(extra.user_agent, user_agent)
        eq_(extra.status_code, '200')
        eq_(extra.http_version, http_version)
        eq_(extra.response_size, len(response))
        eq_(extra.path, url_path)
        eq_(extra.cid_resp_time, '{}/0.0'.format(cid)) # It's 0.0 because we mock utcnow to be a constant value
        eq_(extra.method, request_method)
        eq_(extra.remote_ip, remote_ip)
        eq_(extra.req_timestamp_utc, '12/Jan/2014:16:22:12 +0000')
        eq_(extra.req_timestamp, request_timestamp)

# ################################################################################################################################
