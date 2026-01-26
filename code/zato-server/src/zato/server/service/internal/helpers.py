# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import closing
from dataclasses import dataclass
from http import HTTPStatus
from io import StringIO
from json import loads
from logging import DEBUG, getLogger
from tempfile import gettempdir
from traceback import format_exc
from unittest import TestCase

# Prometheus
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

# Zato
from zato.common.test import rand_csv, rand_string
from zato.common.typing_ import cast_, intnone, list_, optional
from zato.common.util.api import utcnow
from zato.common.util.open_ import open_w
from zato.server.commands import CommandResult, Config
from zato.common.api import CONNECTION, GENERIC, SEC_DEF_TYPE, URL_TYPE
from zato.common.util.auth import check_basic_auth
from zato.server.connection.http_soap import Forbidden, Unauthorized
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

default_services_allowed = (
    'zato.ping',
)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class User(Model):
    user_id:      int
    username:     str
    display_name: optional[str]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class UserAccount(Model):
    user:         User
    account_id:   int
    account_type: intnone

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class GetUserRequest(Model):
    username: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class GetUserAccountListRequest(Model):
    user_id:    optional[int]
    account_id: int

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class GetUserAccountListResponse(Model):
    user_account_list: list_[UserAccount]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class GetUserResponse(Model):
    user:          list_[User]
    parent_user:   list_[optional[User]]
    previous_user: optional[list_[User]]

# ################################################################################################################################
# ################################################################################################################################

class ToggleLogStreaming(Service):
    """ Toggles log streaming on or off.
    """
    name = 'zato.log.streaming.toggle'

    def handle(self) -> 'None':
        self.logger.info('ToggleLogStreaming.handle: called, cid={}'.format(self.cid))
        was_enabled = self.server.log_streaming_manager.is_streaming_enabled()
        self.logger.info('ToggleLogStreaming.handle: was_enabled={}'.format(was_enabled))
        enabled = self.server.log_streaming_manager.toggle_streaming()
        self.logger.info('ToggleLogStreaming.handle: now_enabled={}'.format(enabled))
        self.response.payload = {
            'status': 'success',
            'streaming_enabled': enabled
        }
        self.logger.info('ToggleLogStreaming.handle: response prepared, streaming_enabled={}'.format(enabled))

# ################################################################################################################################
# ################################################################################################################################

class GetLogStreamingStatus(Service):
    """ Returns current log streaming status.
    """
    name = 'zato.log.streaming.status'

    def handle(self) -> 'None':
        self.logger.info('GetLogStreamingStatus.handle: called, cid={}'.format(self.cid))
        enabled = self.server.log_streaming_manager.is_streaming_enabled()
        self.logger.info('GetLogStreamingStatus.handle: streaming_enabled={}'.format(enabled))
        self.response.payload = {
            'streaming_enabled': enabled
        }
        self.logger.info('GetLogStreamingStatus.handle: response prepared')

# ################################################################################################################################
# ################################################################################################################################

class Echo(Service):
    """ Copies request over to response.
    """
    name = 'helpers.echo'

    def handle(self) -> 'None':
        self.response.payload = self.request.raw_request

# ################################################################################################################################
# ################################################################################################################################

class PubInputLogger(Service):

    name = 'demo.input-logger'

    input = '-hello'
    output = 'world'

    def handle(self):
        import logging
        logger = logging.getLogger('zato')
        logger.info(f'Received request: `{self.request.raw_request}`')
        logger.info(f'Channel info: `{self.channel.to_dict()}`')
        self.response.payload.world = f'{self.name} received your request.'

# ################################################################################################################################

class GetMetrics(Service):
    """ Returns metrics in Prometheus format.
    """
    name = 'zato.metrics.get'

    def handle(self):
        self.response.payload = generate_latest().decode('utf-8')
        self.response.content_type = CONTENT_TYPE_LATEST

# ################################################################################################################################
# ################################################################################################################################

class HTMLService(Service):

    def before_handle(self) -> 'None': # type: ignore

        # Configure Django if this service is used - not that we are not doing it
        # globally for the module because the configuration takes some milliseconds
        # the first time around (but later on it is not significant).

        # Django
        import django
        from django.conf import settings

        # Configure Django settings when the module is picked up
        if not settings.configured:
            settings.configure()
            django.setup()

    def set_html_payload(self, ctx:'any_', template:'str', content_type:'str'='text/html; charset=utf-8') -> 'None':

        # Django
        from django.template import Context, Template

        # Generate HTML and return response
        c = Context(ctx)
        t = Template(template)
        payload = t.render(c).encode('utf-8')

        self.logger.debug('Ctx:[%s]', ctx)
        self.logger.debug('Payload:[%s]', payload)

        if self.logger.isEnabledFor(DEBUG):
            buff = StringIO()
            self.logger.debug(buff.getvalue())
            buff.close()

        self.response.payload = payload
        self.response.content_type = content_type

# ################################################################################################################################
# ################################################################################################################################

class ServiceGateway(Service):
    """ Dispatches incoming requests to target services.
    """
    name = 'helpers.service-gateway'

    def handle(self) -> 'None':
        service = self.request.http.params.get('service')
        request = self.request.raw_request
        channel_id = self.channel.id

        with self.server.gateway_services_allowed_lock:
            allowed_services = self.server.gateway_services_allowed[channel_id]

        if service not in allowed_services:
            raise Unauthorized(self.cid, 'Unauthorized', 'gateway')

        username = self.wsgi_environ.get('HTTP_X_ZATO_USERNAME', '')

        self.wsgi_environ['zato.sec_def'] = {
            'id': None,
            'name': None,
            'type': SEC_DEF_TYPE.BASIC_AUTH,
            'username': username,
            'impl': None,
        }

        self.response.payload = self.invoke(service, request, wsgi_environ=self.wsgi_environ)

# ################################################################################################################################
# ################################################################################################################################

class APISpecHelperUser(Service):
    """ Test support services - User.
    """
    name = 'helpers.api-spec.user'

    class SimpleIO:
        input  = GetUserRequest
        output = GetUserResponse

# ################################################################################################################################

    def handle(self):

        # Our request
        request = self.request.input # type: GetUserRequest

        # Response to produce
        out = GetUserResponse()

        # To be returned in out.user ..
        user1 = User()
        user1.user_id      = 111
        user1.username     = 'username.111'
        user1.display_name = 'display_name.111.' + request.username

        # .. also to be returned in out.user ..
        user2 = User()
        user2.user_id      = 222
        user2.username     = 'username.222'
        user2.display_name = 'display_name.222.' + request.username

        # To be returned as out.parent_user
        # This is an empty list on purpose becaue the field is optional
        parent_user = []

        # To be returned as out.previous_user
        # This is an empty list on purpose becaue the field is optional as well
        previous_user = []

        # Note that user2 is added before user1 - this is on purpose because
        # the test that invokes us will check that this is the specific order, non-ascending,
        # that we are returning the data in, i.e. that nothing attempts to sort it itself
        # before the data is returned to the caller (to the test).
        out.user = [user2, user1]
        out.parent_user = parent_user
        out.previous_user = previous_user

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class MyUser(Model):

    user_name:    str # This is a string

    address_data: dict            # This is a dict
    prefs_dict:   optional[dict]  # This is an optional dict

    phone_list:   list            # This is a list
    email_list:   optional[list]  # This is an optional list

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class MyAccount(Model):

    # This description is above the field
    account_no:      int

    account_type:    str # This is an inline description

    account_segment: str
    """ This is a multiline description,
    it has two lines.
    """

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class MyAccountList(Model):
    account_list: list_[MyAccount]

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class MyRequest(Model):
    request_id: int
    user: MyUser

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MyResponse(Model):
    current_balance: int
    last_account_no: int = 567
    pref_account: MyAccount
    account_list: MyAccountList

# ################################################################################################################################
# ################################################################################################################################

class MyDataclassService(Service):
    """ This is my service.

    It has a docstring.
    """
    name = 'helpers.dataclass-service'

    class SimpleIO:
        input  = MyRequest
        output = MyResponse

    def handle(self):
        pass

# ################################################################################################################################
# ################################################################################################################################

class CommandsService(Service):

    name = 'helpers.commands-service'

    class SimpleIO:
        output = CommandResult

    class _CommandsServiceTestCase(TestCase):

        def __init__(self, service:'Service') -> 'None':
            super().__init__()
            self.service = service

# ################################################################################################################################

        def _test_impl(
            self,
            *,
            cid:'str'         = '',
            data:'str'        = '',
            stdin:'str'       = '',
            command:'str'     = '',
            timeout:'float'   = Config.Timeout,
            is_async:'bool'   = False,
            encoding:'str'    = Config.Encoding,
            callback:'any_'   = None,
            use_pubsub:'bool' = False,
            replace_char:'str'  = Config.ReplaceChar,
            is_multiline:'bool' = False,
            ) -> 'None':

            # Local aliases
            tmp_dir = gettempdir()

            # Test data that we will expect to read back from a test file
            data = data or rand_csv()
            len_data = len(data)

            # If we use the default timeout, it actually means that we do not want to have any
            if timeout == Config.Timeout:
                timeout = cast_('float', None)

            # Where our test data is
            test_file_name = rand_string(prefix='commands-test_invoke_core') + '.txt'
            full_path = os.path.join(tmp_dir, test_file_name)

            # Log useful details
            logger.info('Saving test data `%s` to file `%s`', data, full_path)

            # Populate the file with test data
            with open_w(full_path) as f:
                _ = f.write(data)

            # Read the file back
            command = f'cat {full_path}'

            # Prepend new lines if the command is multiline
            if is_multiline:

                # Let's add two lines in front of the actual command
                line1 = 'cd {} \\ \n'.format(tmp_dir)
                line2 = 'cd {} \\ \n'.format(tmp_dir)
                command = line1 + line2 + command

            # If we have a timeout on input, let's sleep for more than that
            # before running the command. We use an integer instead of a smaller number like 1.1
            # because whether the sleep time is considered a float or integer is up to the underlying shell.
            # To stay on the safe side, it is an integer in our test.
            if timeout:
                sleep_time = timeout * 2
                prefix = f'sleep {sleep_time}'
                command = prefix + ' && ' + command

            # To check that results contain correct timestamps
            now_before_test = utcnow()

            func = self.service.commands.invoke_async if is_async else self.service.commands.invoke

            # Invoke the commands to get the result
            result = func(
                command,
                cid=cid,
                timeout=timeout,
                callback=callback,
                stdin=stdin,
                replace_char=replace_char,
                encoding=encoding,
                use_pubsub=use_pubsub,
            )

            logger.info('Result received -> %s', result)

            # To check that results contain correct timestamps
            now_after_test = utcnow()

            # .. and run the actual tests now ..

            self.assertEqual(result.timeout, timeout)

            if timeout:
                self.assertEqual(result.exit_code, -1)
                self.assertFalse(result.is_ok)
                self.assertFalse(result.is_async)
                self.assertTrue(result.is_timeout)

                expected_timeout_msg = f'Command \'{command}\' timed out after {timeout} sec.'
                self.assertEqual(result.timeout_msg, expected_timeout_msg)

                self.assertEqual(result.stdin,  '')
                self.assertEqual(result.stderr, '')
                self.assertEqual(result.stdout, '')

                self.assertEqual(result.len_stderr_bytes, 0)
                self.assertEqual(result.len_stderr_human, '')

                self.assertEqual(result.len_stdout_bytes, 0)
                self.assertEqual(result.len_stdout_human, '')

            else:
                if is_async:
                    self.assertEqual(result.exit_code, -1)
                    self.assertTrue(result.is_ok)
                    self.assertTrue(result.is_async)

                    return

                else:

                    self.assertEqual(result.exit_code, 0)
                    self.assertTrue(result.is_ok)
                    self.assertFalse(result.is_async)
                    self.assertFalse(result.is_timeout)
                    self.assertEqual(result.timeout_msg, '')

                    self.assertEqual(result.stdin,  stdin)
                    self.assertEqual(result.stderr, '')
                    self.assertEqual(result.stdout, data)

                    self.assertEqual(result.len_stderr_bytes, 0)
                    self.assertEqual(result.len_stderr_human, '0 Bytes')

                    self.assertEqual(result.len_stdout_bytes, len_data)
                    self.assertEqual(result.len_stdout_human, '{} Bytes'.format(len_data))

            if cid:
                self.assertEqual(result.cid, cid)
            else:
                self.assertTrue(result.cid.startswith('zcmd'))

            self.assertEqual(result.encoding,     encoding)
            self.assertEqual(result.replace_char, replace_char)

            self.assertIsInstance(result.total_time_sec, float)

            start_time_as_iso = result.start_time.isoformat()
            end_time_as_iso   = result.end_time.isoformat()

            self.assertEqual(result.start_time_iso, start_time_as_iso)
            self.assertEqual(result.end_time_iso,   end_time_as_iso)

            self.assertLess(result.start_time, result.end_time)

            self.assertLess(now_before_test, result.start_time)
            self.assertLess(now_before_test, result.end_time)

            self.assertGreater(now_after_test, result.start_time)
            self.assertGreater(now_after_test, result.end_time)

# ################################################################################################################################

        def test_invoke_core(self):

            # This is the same as the base test
            self._test_impl()

# ################################################################################################################################

        def test_invoke_multiline(self):
            self._test_impl(is_multiline=True)

# ################################################################################################################################

        def test_invoke_with_timeout(self):
            self._test_impl(timeout=1)

# ################################################################################################################################

        def test_invoke_with_own_cid(self):
            self._test_impl(cid='abcdef')

# ################################################################################################################################

        def test_invoke_with_encoding(self):
            self._test_impl(encoding='ascii')

# ################################################################################################################################

        def test_invoke_with_replace_char(self):
            self._test_impl(replace_char='?')

# ################################################################################################################################

        def test_invoke_with_stdin(self):
            self._test_impl(stdin='hello')

# ################################################################################################################################

        def test_invoke_with_callback_function(self):
            self._test_impl(callback=self._on_command_completed)

# ################################################################################################################################

        def test_invoke_with_callback_service_class(self):

            # stdlib
            from zato.server.service.internal.helpers import PubInputLogger

            self._test_impl(callback=PubInputLogger)

# ################################################################################################################################

        def test_invoke_with_callback_service_name(self):

            # stdlib
            from zato.server.service.internal.helpers import PubInputLogger

            self._test_impl(callback=PubInputLogger.get_name())

# ################################################################################################################################

        def test_invoke_with_callback_topic_name(self):
            self._test_impl(callback='zato.ping', use_pubsub=True)

# ################################################################################################################################

        def test_invoke_async_core(self):
            self._test_impl(is_async=True)

# ################################################################################################################################

        def _on_command_completed(self, result:'CommandResult') -> 'None':
            pass

# ################################################################################################################################

    def handle(self):

        # Build and run the test suite
        test_suite = self._CommandsServiceTestCase(self)

        #
        # Sync invoke
        #
        test_suite.test_invoke_core()
        test_suite.test_invoke_multiline()
        test_suite.test_invoke_with_timeout()
        test_suite.test_invoke_with_own_cid()
        test_suite.test_invoke_with_encoding()
        test_suite.test_invoke_with_replace_char()
        test_suite.test_invoke_with_stdin()
        test_suite.test_invoke_with_callback_function()
        test_suite.test_invoke_with_callback_service_class()
        test_suite.test_invoke_with_callback_service_name()
        test_suite.test_invoke_with_callback_topic_name()

        #
        # Async invoke
        #
        test_suite.test_invoke_async_core()

        self.response.payload = 'OK'

# ################################################################################################################################
# ################################################################################################################################

class OpenAPIHandler(Service):
    """ Returns OpenAPI specification for a given OpenAPI channel.
    Requires basic auth credentials matching one of the REST channels in the OpenAPI channel.
    """
    name = 'zato.channel.openapi.get'

    def _get_active_rest_channel_ids(self, channel):
        rest_channel_list = []
        if channel.opaque1:
            opaque = loads(channel.opaque1) if isinstance(channel.opaque1, str) else channel.opaque1
            raw = opaque.get('rest_channel_list')
            if raw:
                rest_channel_list = loads(raw) if isinstance(raw, str) else raw

        out = []
        for item in rest_channel_list:
            if item['state'] == 'on':
                out.append(int(item['id']))
        return out

    def _get_basic_auth_security_ids(self, session, rest_channels):
        from zato.common.odb.model import SecurityBase

        out = set()
        for rest_channel in rest_channels:
            if rest_channel.security_id:
                sec_base = session.query(SecurityBase).filter(
                    SecurityBase.id == rest_channel.security_id,
                    SecurityBase.sec_type == SEC_DEF_TYPE.BASIC_AUTH,
                ).first()
                if sec_base:
                    out.add(rest_channel.security_id)
        return out

    def _check_credentials(self, auth_header, basic_auth_security_ids):
        for security_id in basic_auth_security_ids:
            sec_def = self.server.worker_store.basic_auth_get_by_id(security_id)
            if sec_def:
                password = sec_def['password']
                if password.startswith('gAAAAA'):
                    password = self.crypto.decrypt(password)
                result = check_basic_auth(self.cid, auth_header, sec_def['username'], password)
                if result is True:
                    return True
        return False

    def _collect_services_info(self, rest_channels):
        out = []
        for rest_channel in rest_channels:
            source_path = None
            if rest_channel.service:
                try:
                    source_info = self.invoke('zato.service.get-source-info', {
                        'cluster_id': self.server.cluster_id,
                        'name': rest_channel.service.name,
                    })
                    if source_info:
                        source_path = source_info.get('source_path')
                except Exception:
                    logger.warning('Could not get source info for %s: %s', rest_channel.service.name, format_exc())

            security_name = None
            if rest_channel.security:
                security_name = rest_channel.security.name

            out.append({
                'name': rest_channel.service.name if rest_channel.service else rest_channel.name,
                'url_path': rest_channel.url_path,
                'http_method': rest_channel.method or 'POST',
                'source_path': source_path,
                'security_name': security_name,
            })
        return out

    def _enrich_with_schemas(self, services_info, scan_results):
        schema_by_service = {}
        for service in scan_results['services']:
            service_name = service.get('name')
            if service_name:
                schema_by_service[service_name] = {
                    'input': service.get('input'),
                    'output': service.get('output'),
                    'class_name': service.get('class_name')
                }

        for service in services_info:
            schema = schema_by_service.get(service['name'])
            if schema:
                service.update(schema)

    def _build_openapi_spec(self, channel_name, services_info, scan_results):
        from zato.openapi.generator.openapi_ import OpenAPIGenerator

        security_schemes = {}
        for service in services_info:
            security_name = service.get('security_name')
            if security_name and security_name not in security_schemes:
                security_schemes[security_name] = {'type': 'http', 'scheme': 'basic'}

        openapi_spec = {
            'openapi': '3.1.0',
            'info': {'title': channel_name, 'version': '1.0.0'},
            'paths': {},
            'components': {'schemas': {}, 'securitySchemes': security_schemes}
        }

        openapi_generator = OpenAPIGenerator(type_mapper=scan_results['type_mapper'])

        for service in services_info:
            path = service.get('url_path', f'/{service["name"].replace(".", "/")}')
            method = service.get('http_method', 'post').lower()

            operation = {
                'summary': f'Invoke {service["name"]}',
                'operationId': service['name'].replace('.', '_').replace('-', '_'),
                'responses': {
                    '200': {'description': 'Successful response'},
                    '400': {'description': 'Bad Request'},
                    '500': {'description': 'Internal Server Error'}
                }
            }

            security_name = service.get('security_name')
            if security_name:
                operation['security'] = [{security_name: []}]

            if service.get('input'):
                try:
                    request_schema = openapi_generator._create_request_schema(service['input'], scan_results['models'])
                    if request_schema:
                        input_def = service['input']
                        is_required = True
                        if input_def.get('type') == 'string':
                            is_required = input_def.get('required', True)
                        elif input_def.get('type') == 'tuple':
                            is_required = any(el.get('required', True) for el in input_def.get('elements', []))
                        operation['requestBody'] = {
                            'required': is_required,
                            'content': {'application/json': {'schema': request_schema}}
                        }
                except Exception:
                    logger.warning('Could not create request schema for %s: %s', service['name'], format_exc())

            if service.get('output'):
                try:
                    response_schema = openapi_generator._create_response_schema(service['output'], scan_results['models'])
                    if response_schema:
                        operation['responses']['200']['content'] = {'application/json': {'schema': response_schema}}
                except Exception:
                    logger.warning('Could not create response schema for %s: %s', service['name'], format_exc())

            if path not in openapi_spec['paths']:
                openapi_spec['paths'][path] = {}
            openapi_spec['paths'][path][method] = operation

        schema_components = openapi_generator.type_mapper.get_schema_components()
        if schema_components:
            openapi_spec['components']['schemas'].update(schema_components)

        return openapi_spec

    def handle(self):
        from zato.common.odb.model import GenericConn, HTTPSOAP
        from zato.openapi.generator.io_scanner import IOScanner
        import yaml

        channel_name = self.request.http.params.get('name')
        if not channel_name:
            raise Forbidden(self.cid, 'Channel name is required')

        auth_header = self.wsgi_environ.get('HTTP_AUTHORIZATION', '')

        with closing(self.odb.session()) as session:

            channel = session.query(GenericConn).filter(
                GenericConn.type_ == GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI,
                GenericConn.name == channel_name,
                GenericConn.cluster_id == self.server.cluster_id,
            ).first()

            if not channel:
                raise Forbidden(self.cid, 'Channel not found')

            active_rest_channel_ids = self._get_active_rest_channel_ids(channel)

            rest_channels = []
            if active_rest_channel_ids:
                rest_channels = list(session.query(HTTPSOAP).filter(
                    HTTPSOAP.id.in_(active_rest_channel_ids),
                    HTTPSOAP.cluster_id == self.server.cluster_id,
                    HTTPSOAP.connection == CONNECTION.CHANNEL,
                    HTTPSOAP.transport == URL_TYPE.PLAIN_HTTP,
                ))

            basic_auth_security_ids = self._get_basic_auth_security_ids(session, rest_channels)

            if not self._check_credentials(auth_header, basic_auth_security_ids):
                self.response.status_code = HTTPStatus.FORBIDDEN
                self.response.payload = {'error': 'Invalid credentials'}
                return

            services_info = self._collect_services_info(rest_channels)

            file_paths = [item['source_path'] for item in services_info if item['source_path']]

            scanner = IOScanner()
            scan_results = scanner.scan_files(file_paths) if file_paths else {'services': [], 'models': {}}
            scan_results['type_mapper'] = scanner.type_mapper

            self._enrich_with_schemas(services_info, scan_results)

            openapi_spec = self._build_openapi_spec(channel_name, services_info, scan_results)
            yaml_output = yaml.dump(openapi_spec, sort_keys=False, allow_unicode=True)

            logger.info('Generated OpenAPI for channel %s', channel_name)

            self.response.payload = yaml_output
            self.response.content_type = 'application/x-yaml'

# ################################################################################################################################
# ################################################################################################################################
