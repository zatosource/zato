# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from http.client import OK
from io import StringIO
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
from zato.common import CHANNEL, ZATO_NONE
from zato.common.broker_message import SERVICE
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

            'zato.http.response.status': OK,
            'zato.channel_item': channel_item,
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
                return Bunch(payload=response, content_type='text/plain', headers={}, status_code=OK)

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
