# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from io import StringIO
from logging import DEBUG, getLogger
from tempfile import gettempdir
from unittest import TestCase

# Prometheus
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

# Zato
from zato.common.test import rand_csv, rand_string
from zato.common.typing_ import cast_, intnone, list_, optional
from zato.common.util.api import utcnow
from zato.common.util.open_ import open_w
from zato.server.commands import CommandResult, Config
from zato.common.api import SEC_DEF_TYPE
from zato.server.connection.http_soap import Unauthorized
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
    def handle(self) -> 'None':
        self.response.payload = self.request.raw_request

# ################################################################################################################################
# ################################################################################################################################

class PubInputLogger(Service):

    name = 'demo.input-logger'

    def handle(self):
        self.logger.info(f'Received request: `{self.request.raw_request}`')

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

        self.logger.info('[DEBUG] Checking service `%s` for channel `%s` (%s), cid:%s, allowed: %s',
            service, self.channel.name, self.request.http.path, self.cid, allowed_services)

        if service not in allowed_services:
            self.logger.warning('[DEBUG] Service `%s` not in allowed list for channel `%s` (%s), cid:%s',
                service, self.channel.name, self.request.http.path, self.cid)
            raise Unauthorized(self.cid, 'Service not allowed', 'gateway')

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
