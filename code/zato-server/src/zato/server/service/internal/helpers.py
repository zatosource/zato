# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from json import dumps, loads
from logging import DEBUG, getLogger
from tempfile import gettempdir
from time import sleep
from traceback import format_exc
from unittest import TestCase

# Zato
from zato.common.api import WEB_SOCKET
from zato.common.exception import Forbidden
from zato.common.pubsub import PUBSUB
from zato.common.test import rand_csv, rand_string
from zato.common.typing_ import cast_, intnone, list_, optional
from zato.common.util.open_ import open_rw, open_w
from zato.server.commands import CommandResult, Config
from zato.server.connection.facade import RESTInvoker
from zato.server.service import AsIs, Model, PubSubHook, Service
from zato.server.service.internal.service import Invoke

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.pubsub import PubSubMessage
    from zato.common.typing_ import any_, anydict, anytuple
    anydict = anydict
    PubSubMessage = PubSubMessage

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

default_services_allowed = (
    'zato.pubsub.pubapi.publish-message',
    'zato.pubsub.pubapi.subscribe-wsx',
    'zato.pubsub.pubapi.unsubscribe',
    'zato.pubsub.resume-wsx-subscription',
    'zato.pubsub.subscription.create-wsx-subscription',
    'zato.ping'
)

# This is an indication to the WSX serialization layer
# that a response was produced by our gateway service.
wsx_gateway_response_elem = WEB_SOCKET.GatewayResponseElem

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

class Echo(Service):
    """ Copies request over to response.
    """
    def handle(self) -> 'None':
        self.response.payload = self.request.raw_request

# ################################################################################################################################
# ################################################################################################################################

class InputLogger(Service):
    """ Writes out all input data to server logs.
    """
    def handle(self):
        pass

    def finalize_handle(self) -> 'None': # type: ignore
        _ = self.log_input()

# ################################################################################################################################
# ################################################################################################################################

class PubInputLogger(InputLogger):
    """ Same as InputLogger but has a publicly available name
    """
    name = 'pub.helpers.input-logger'

# ################################################################################################################################
# ################################################################################################################################

class RawRequestLogger(Service):
    """ Writes out self.request.raw_request to server logs.
    """
    name = 'pub.helpers.raw-request-logger'

    def handle(self) -> 'None':
        self.logger.info('Received request: `%s`', self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################

class IBMMQLogger(Service):
    """ Writes out self.request.raw_request to server logs.
    """
    name = 'pub.helpers.ibm-mq-logger'

    def handle(self) -> 'None':
        template = """
***********************
IBM MQ message received
***********************
MsgId: `{msg_id}`
CorrelId: `{correlation_id}`
Timestamp: `{timestamp}`
PutDate: `{put_date}`
PutTime: `{put_time}`
ReplyTo: `{reply_to}`
MQMD: `{mqmd!r}`
-----------------------
Data: `{data}`
***********************
"""

        mq = self.request.ibm_mq
        na = 'n/a'

        try:
            msg_id = mq.msg_id.decode('ascii') # type: ignore
        except UnicodeDecodeError:
            msg_id = repr(mq.msg_id)

        if mq.correlation_id:
            try:
                correlation_id = mq.correlation_id.decode('ascii') # type: ignore
            except UnicodeDecodeError:
                correlation_id = repr(mq.correlation_id)
        else:
            correlation_id = na

        info = {
            'msg_id': msg_id,
            'correlation_id': correlation_id,
            'timestamp': mq.timestamp,
            'put_date': mq.put_date,
            'put_time': mq.put_time,
            'reply_to': mq.reply_to or na,
            'mqmd': str(mq.mqmd).splitlines(),
            'data': self.request.raw_request,
        }

        msg = template.format(**info)
        msg_out = msg.encode('utf8')

        self.logger.info(msg_out)

# ################################################################################################################################
# ################################################################################################################################

class JSONRawRequestLogger(RawRequestLogger):
    """ Same as RawRequestLogger but returns a JSON response.
    """
    def handle(self) -> 'None':
        super(JSONRawRequestLogger, self).handle()
        self.response.payload = {'status': 'OK'}

# ################################################################################################################################
# ################################################################################################################################

class SIOInputLogger(Service):
    """ Writes out all SIO input parameters to server logs.
    """
    def handle(self) -> 'None':
        self.logger.info('%r', self.request.input)

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

class TLSLogger(Service):
    """ Logs details of client TLS certificates.
    """
    def handle(self) -> 'None':
        has_tls = False
        for k, v in sorted(self.wsgi_environ.items()):
            if k.startswith('HTTP_X_ZATO_TLS_'):
                has_tls = True
                self.logger.info('%r: %r', k, v)

        if not has_tls:
            self.logger.warning('No HTTP_X_ZATO_TLS_* headers found')

# ################################################################################################################################
# ################################################################################################################################

class WebSocketsGateway(Service):
    """ Dispatches incoming WebSocket requests to target services.
    """
    name = 'helpers.web-sockets-gateway'
    services_allowed = []

    class SimpleIO:
        input_required = 'service'
        input_optional = AsIs('request')
        output_optional = 'sub_key', AsIs(wsx_gateway_response_elem)
        skip_empty_keys = True

    def handle(self, _default_allowed:'anytuple'=default_services_allowed) -> 'None':

        # Local aliases
        input = self.request.input
        service = input.service

        # Make sure that the service can be invoked if we have one on input
        if service:

            # These services can be always invoked
            is_allowed_by_default = service in _default_allowed

            # Our subclasses may add more services that they allow
            is_allowed_by_self_service = service in self.services_allowed

            # Ensure that the input service is allowed
            if not (is_allowed_by_default or is_allowed_by_self_service):
                self.logger.warning('Service `%s` is not among %s', service, self.services_allowed) # noqa: E117
                raise Forbidden(self.cid)

        # We need to special-pub/sub subscriptions
        # because they will require calling self.pubsub on behalf of the current WSX connection.
        if service == 'zato.pubsub.pubapi.subscribe-wsx':
            topic_name = input.request['topic_name']
            unsub_on_wsx_close = input.request.get('unsub_on_wsx_close', True)
            sub_key = self.pubsub.subscribe(
                topic_name,
                use_current_wsx=True,
                unsub_on_wsx_close=unsub_on_wsx_close,
                service=self,
                cid=input.cid,
            )
            self.response.payload.sub_key = sub_key

        else:

            # The service that we are invoking may be interested in what the original, i.e. ours, channel was.
            self.wsgi_environ['zato.orig_channel'] = self.channel

            # Invoke the underlying service and get its response
            response = self.invoke(
                service,
                self.request.input.request,
                wsgi_environ=self.wsgi_environ,
                skip_response_elem=True,
                cid=self.cid,
            )

            # Use setattr to attach the response because we keep the response element's name in a variable
            setattr(self.response.payload, wsx_gateway_response_elem, response)

# ################################################################################################################################
# ################################################################################################################################

class WebSocketsPubSubGateway(Service):
    """ Dispatches incoming WebSocket publish/subscribe requests to target services.
    """
    name = 'helpers.web-sockets-pub-sub-gateway'

    class SimpleIO:
        input_required = ('service',)
        input_optional = (AsIs('request'),)

# ################################################################################################################################

    def handle(self) -> 'None':

        service = self.request.input.service
        request = self.request.input.request
        self.response.payload = self.invoke(service, request, wsgi_environ=self.wsgi_environ)

# ################################################################################################################################
# ################################################################################################################################

class ServiceGateway(Invoke):
    """ Service to invoke other services through.
    """
    name = 'helpers.service-gateway'

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

class APISpecHelperAccountList(Service):
    """ Test support services - AccountList.
    """
    name = 'helpers.api-spec.account-list'

    class SimpleIO:
        input  = GetUserAccountListRequest
        output = GetUserAccountListResponse

# ################################################################################################################################

    def handle(self):

        # Our request
        request = self.request.input # type: GetUserAccountListRequest

        # Response to produce
        out = GetUserAccountListResponse()

        user1 = User()
        user1.user_id      = 111
        user1.username     = 'username.111'
        user1.display_name = 'display_name.111.{}'.format(request.user_id)

        user2 = User()
        user2.user_id      = 222
        user2.username     = 'username.222'
        user2.display_name = 'display_name.222.{}'.format(request.user_id)

        account1 = UserAccount()
        account1.user = user1
        account1.account_id = 1010 + request.account_id
        account1.account_type = 1111

        account2 = UserAccount()
        account2.user = user2
        account2.account_id = 2020 + request.account_id
        account2.account_type = 2222

        out.user_account_list = [account2, account1]
        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class HelperPubSubTarget(Service):
    """ Test support services - PubSubTarget.
    """
    name = 'helpers.pubsub.target'

    def handle(self):

        # Our request
        msg = self.request.raw_request # type: list_[PubSubMessage]

        # Whatever happens next, log what we received
        self.logger.info('************************** 1) I was invoked with %r', msg)

        # .. load the inner dict ..
        data = msg[0].data # type: anydict | str

        # .. confirm what it was ..
        self.logger.info('************************** 2) Data is %r', data)

        # .. this may be a dict or an empty string, the latter is the case
        # .. when a message is published via self.pubsub.publish with no input  ..
        if data:

            # .. rule out string objects ..
            if isinstance(data, dict):

                # .. optionally, save our input data for the external caller to check it ..
                if data['target_needs_file']:

                    # .. this is where we will save our input data ..
                    file_name = data['file_name']

                    # .. we will save the message as a JSON one ..
                    json_msg = msg[0].to_json(needs_utf8_decode=True)

                    # .. confirm what we will be saving and where ..
                    self.logger.info('Saving data to file `%s` -> `%s`', file_name, json_msg)

                    # .. and actually save it now.
                    f = open_rw(file_name)
                    _ = f.write(json_msg)
                    f.close()

# ################################################################################################################################
# ################################################################################################################################

class HelperPubSubHook(PubSubHook):
    """ Test support services - PubSubHook.
    """
    name = 'helpers.pubsub.hook'

    class SimpleIO:
        input_required  = AsIs('ctx')
        output_required = 'hook_action'

    def before_publish(self):

        # Local aliases
        data       = self.request.input.ctx.msg.data
        pub_msg_id = self.request.input.ctx.msg.pub_msg_id

        # Log what we have received ..
        self.logger.info('Helpers before_publish; pub_msg_id:`%s`, data:`%s`', pub_msg_id, data)

        # .. unless this is a test message, load data from JSON ..
        if data != PUBSUB.DEFAULT.Dashboard_Message_Body:

            # .. the data may be still user-provided, in which case it may not be JSON at all ..
            try:
                dict_data = loads(data)
            except Exception:
                # This is fine, it was not JSON
                pass
            else:

                # .. find information where we should save our input to ..
                file_name = dict_data['file_name']

                # .. add a suffix so as not to clash with the main recipient of the message ..
                file_name = file_name + '.hook-before-publish.json'

                # .. store our input in a file for the external caller to check it ..
                f = open_rw(file_name)
                _ = f.write(data)
                f.close()

        # .. and proceed with the publication
        self.response.payload.hook_action = PUBSUB.HOOK_ACTION.DELIVER

# ################################################################################################################################
# ################################################################################################################################

class HelperPubSubSource(Service):
    """ Test support services - PubSubSource.
    """
    name = 'helpers.pubsub.source'

    class SimpleIO:
        input_required = 'random_data', 'file_name'

    def handle(self):

        # Local aliases
        data = self.request.raw_request # type: dict
        topic_name = '/zato/s/to/helpers_pubsub_target'

        # The first time around, we need a file from the target service ..
        data['target_needs_file'] = True

        # Publish the message ..
        self.pubsub.publish(HelperPubSubTarget, data=data)

        # .. the topic for that service has to be potentially created so we wait here until it appears ..
        _ = self.pubsub.wait_for_topic(topic_name)
        sleep(0.1)

        # .. now, once the message has been published, we know that the topic
        # .. for the receiving service exists, so we can assign a hook service to it ..
        response = self.invoke('zato.pubsub.topic.get', {'cluster_id': self.server.cluster_id, 'name': topic_name})
        response = response['response']

        # Request to edit the topic with
        request = {}

        # These can be taken from the previous response as-is
        keys = ('has_gd', 'id','is_active', 'is_internal', 'max_depth_gd', 'max_depth_non_gd', 'name', 'on_no_subs_pub')

        # .. add the default keys ..
        for key in keys:
            request[key] = response[key]

        # .. set the helper hook service and other metadata..
        request['hook_service_name']  = HelperPubSubHook.get_name()
        request['cluster_id']         = self.server.cluster_id
        request['depth_check_freq']   = 500
        request['is_api_sub_allowed'] = True
        request['pub_buffer_size_gd'] = 500
        request['task_sync_interval'] = 500
        request['task_delivery_interval'] = 500

        # .. now, we can edit the topic to set its hooks service
        response = self.invoke('zato.pubsub.topic.edit', request)

        # .. once again, wait until the topic has been recreated ..
        _ = self.pubsub.wait_for_topic(topic_name)
        sleep(0.1)

        # The second time around, the target service should not create a file
        data['target_needs_file'] = False

        # .. and now, we can publish the message once more, this time around expecting
        # .. that the hook service will be invoked ..
        self.pubsub.publish(HelperPubSubTarget, data=data)

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

class PubAPIInvoker(Service):
    """ Tests services that WebSocket clients use.
    """
    name = 'helpers.pubsub.pubapi-invoker'

    def handle(self):

        # stdlib
        from unittest import defaultTestLoader, TestCase, TextTestRunner

        # Zato
        from zato.common.test.pubsub.common import FullPathTester, PubSubTestingClass

        class WSXServicesTestCase(TestCase, PubSubTestingClass):

            def _subscribe(_self, topic_name): # type: ignore
                service = 'zato.pubsub.pubapi.subscribe'
                response = self.invoke(service, {'topic_name': topic_name})
                return response['sub_key']

            def _unsubscribe(_self, topic_name): # type: ignore
                service = 'zato.pubsub.pubapi.unsubscribe'
                response = self.invoke(service, {'topic_name': topic_name})
                return response

            def _publish(_self, topic_name, data): # type: ignore
                service = 'zato.pubsub.pubapi.publish-message'
                response = self.invoke(service, {'topic_name': topic_name, 'data':data})
                return response

            def _receive(_self, topic_name): # type: ignore
                service = 'zato.pubsub.pubapi.get-messages'
                response = self.invoke(service, {'topic_name': topic_name})
                return response

            def test_wsx_services_full_path_subscribe_before_publication(_self):
                tester = FullPathTester(_self, True)
                tester.run()

            def test_wsx_services_full_path_subscribe_after_publication(_self):
                tester = FullPathTester(_self, False)
                tester.run()

        try:
            iters = 10
            for _ in range(iters):
                suite = defaultTestLoader.loadTestsFromTestCase(WSXServicesTestCase)
                result = TextTestRunner().run(suite)

                if result.errors or result.failures:
                    errors   = []
                    failures = []

                    response = {
                        'errors':   errors,
                        'failures': failures,
                    }

                    for error in result.errors:
                        test, reason = error
                        test = str(test)
                        _error = {
                            'error_test': test,
                            'error_reason': reason,
                        }
                        self.logger.warning('Test error in %s\n%s', test, reason)
                        errors.append(_error)

                    for failure in result.failures:
                        test, reason = failure
                        test = str(test)
                        reason = '\n'.join(reason)
                        _failure = {
                            'failure_test': test,
                            'failure_reason': reason,
                        }
                        self.logger.warning('Test failure in %s\n%s', test, reason)
                        failures.append(_failure)

                    # Serialize all the warnings and errors ..
                    self.response.payload = dumps(response)

                    # .. and do resume the test.
                    break

            # If we ar here, it means that there was no error
            else:
                self.response.payload = 'OK'

        except Exception:
            msg = 'Exception in {} -> {}'.format(self.__class__.__name__, format_exc())
            self.logger.warning(msg)
            self.response.payload = msg

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
            now_before_test = datetime.utcnow()

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
            now_after_test = datetime.utcnow()

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
            from zato.server.service.internal.helpers import RawRequestLogger

            self._test_impl(callback=RawRequestLogger)

# ################################################################################################################################

        def test_invoke_with_callback_service_name(self):

            # stdlib
            from zato.server.service.internal.helpers import RawRequestLogger

            self._test_impl(callback=RawRequestLogger.get_name())

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
        test_suite

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

class RESTInternalTester(Service):

    name = 'helpers.rest.internal.tester'

    def _run_assertions(self, result:'str | Response', *, is_ping:'bool'=False) -> 'None':

        # stdlib
        from http.client import OK

        if is_ping:
            if isinstance(result, str):
                if not 'HEAD' in result:
                    raise Exception(f'Invalid ping result (1) -> {result}')
            else:
                if not result.status_code == OK:
                    raise Exception(f'Invalid ping result (2) -> {result}')

        else:
            result = cast_('Response', result)
            headers = result.headers
            server = headers['Server']
            if not server == 'Zato':
                raise Exception(f'Unrecognized Server header in {headers}')

# ################################################################################################################################

    def test_rest_by_getitem_no_cid(self, conn_name:'str') -> 'None':

        conn = self.rest[conn_name]

        result = conn.ping()
        self._run_assertions(result, is_ping=True)

        result = conn.get()
        self._run_assertions(result)

        result = conn.post('abc')
        self._run_assertions(result)

# ################################################################################################################################

    def test_rest_by_getitem_with_cid(self, conn_name:'str') -> 'None':

        conn = self.rest[conn_name]

        result = conn.ping(self.cid)
        self._run_assertions(result, is_ping=True)

        result = conn.get(self.cid)
        self._run_assertions(result)

        result = conn.post(self.cid, 'abc')
        self._run_assertions(result)

# ################################################################################################################################

    def test_rest_by_getattr(self, conn:'RESTInvoker') -> 'None':

        result = conn.ping()
        self._run_assertions(result, is_ping=True)

        result = conn.get()
        self._run_assertions(result)

        result = conn.post('abc')
        self._run_assertions(result)

# ################################################################################################################################

    def handle(self) -> 'None':

        conn_name = 'pubsub.demo.sample.outconn'

        self.test_rest_by_getitem_no_cid(conn_name)
        self.test_rest_by_getitem_with_cid(conn_name)

        conn = self.rest.pubsub_demo_sample_outconn
        self.test_rest_by_getattr(conn) # type: ignore

# ################################################################################################################################
# ################################################################################################################################
