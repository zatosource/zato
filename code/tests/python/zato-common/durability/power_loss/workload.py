# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The clients that publish, pull and acknowledge and invoke an audited channel while a server
# runs and loses its power, with what the server acknowledged to each of them.

# stdlib
import json
import threading
import time
from base64 import b64encode
from collections import Counter
from http.client import OK
from typing import NamedTuple
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The topic that the publishers publish to and that the puller pulls from
    Topic_Name = 'durability.power-loss'

    # The users of the clients and the names of their passwords in the placeholders of the enmasse file
    Publisher_Username = 'test.durability.power-loss.publisher'
    Puller_Username = 'test.durability.power-loss.puller'
    Caller_Username = 'test.durability.power-loss.caller'

    Publisher_Password_Key = 'publisher_password'
    Puller_Password_Key = 'puller_password'
    Caller_Password_Key = 'caller_password'

    # The paths of the REST interface of the server
    Publish_Path = f'/pubsub/topic/{Topic_Name}'
    Pull_Path = '/pubsub/messages/get'
    Ack_Path = '/pubsub/messages/ack'
    Audited_Path = '/test/durability/power-loss/audited'

    # The name of the audited channel, under which the audit log records its events
    Audited_Channel_Name = 'test.durability.power-loss.audited'

    # How many clients publish at the same time
    Publisher_Count = 4

    # How many messages one pull asks for
    Pull_Max_Messages = 100

    # How long one request may take, in seconds, which ends the requests that a lost server leaves without a response
    Request_Timeout = 30

    # How long a client waits after a failed request before the next one, in seconds
    Retry_Pause = 0.2

    # How long the queue may take to drain once the server is back, in seconds, which covers the default lease
    # of the messages that were pulled and not acknowledged when the server lost its power
    Drain_Timeout = 300

    # How often the queue is pulled while it drains, in seconds
    Poll_Interval = 1.0

# ################################################################################################################################
# ################################################################################################################################

class HTTPResult(NamedTuple):
    """ The status code and the parsed body of one HTTP response.
    """
    status_code: 'int'
    body: 'anydict'

# ################################################################################################################################
# ################################################################################################################################

def _build_auth(username:'str', password:'str') -> 'str':
    credentials = f'{username}:{password}'
    credentials = credentials.encode()
    credentials = b64encode(credentials)

    out = 'Basic ' + credentials.decode()
    return out

# ################################################################################################################################

def post_json(url:'str', auth:'str', payload:'any_') -> 'HTTPResult':
    """ Sends one request with basic authentication and returns its status code and its parsed body.
    A request that receives no response raises an exception.
    """
    serialized = json.dumps(payload)
    body = serialized.encode()

    request = Request(url, data=body, method='POST')
    request.add_header('Authorization', auth)
    request.add_header('Content-Type', 'application/json')

    # An error status is read in the same way as a success ..
    try:
        with urlopen(request, timeout=ModuleCtx.Request_Timeout) as response:
            response_data = response.read()
            status_code = response.status
    except HTTPError as error:
        response_data = error.read()
        status_code = error.code

    # .. and an empty body parses to an empty dict.
    if response_data:
        response_body = json.loads(response_data)
    else:
        response_body = {}

    out = HTTPResult(status_code, response_body)
    return out

# ################################################################################################################################
# ################################################################################################################################

class Workload:
    """ The clients of one server, with what the server acknowledged to each of them.
    """

    def __init__(self, base_url:'str', passwords:'strstrdict') -> 'None':
        self.base_url = base_url

        self.publisher_auth = _build_auth(ModuleCtx.Publisher_Username, passwords[ModuleCtx.Publisher_Password_Key])
        self.puller_auth = _build_auth(ModuleCtx.Puller_Username, passwords[ModuleCtx.Puller_Password_Key])
        self.caller_auth = _build_auth(ModuleCtx.Caller_Username, passwords[ModuleCtx.Caller_Password_Key])

        # Each publication carries a correlation ID unique to this workload
        self.token = uuid4().hex

        self.lock = threading.Lock()
        self.is_running = threading.Event()
        self._threads:'list[threading.Thread]' = []

        # The msg_id of each acknowledged publication by its correlation ID, the messages whose acknowledgement
        # was acknowledged and the correlation IDs of the acknowledged audited invocations
        self.published:'strstrdict' = {}
        self.acked:'set[str]' = set()
        self.audited_cids:'strlist' = []

        # What the puller received once the server was back, in the order received
        self.drained:'strlist' = []

        # How many requests failed, by the kind of request
        self.failures:'Counter[str]' = Counter()

# ################################################################################################################################

    def _url(self, path:'str') -> 'str':
        out = f'{self.base_url}{path}'
        return out

# ################################################################################################################################

    def _record_failure(self, kind:'str') -> 'None':
        with self.lock:
            self.failures[kind] += 1

        time.sleep(ModuleCtx.Retry_Pause)

# ################################################################################################################################

    def _publish_loop(self, publisher_index:'int') -> 'None':

        url = self._url(ModuleCtx.Publish_Path)
        counter = 0

        while self.is_running.is_set():
            counter += 1
            correl_id = f'{self.token}.{publisher_index}.{counter}'

            payload = {
                'data': {'correl_id': correl_id},
                'correl_id': correl_id,
            }

            try:
                result = post_json(url, self.publisher_auth, payload)
            except Exception:
                self._record_failure('publish')
                continue

            if result.status_code == OK:
                with self.lock:
                    self.published[correl_id] = result.body['msg_id']
            else:
                self._record_failure('publish')

# ################################################################################################################################

    def _pull_loop(self) -> 'None':

        pull_url = self._url(ModuleCtx.Pull_Path)
        ack_url = self._url(ModuleCtx.Ack_Path)

        while self.is_running.is_set():

            try:
                result = post_json(pull_url, self.puller_auth, {'max_messages': ModuleCtx.Pull_Max_Messages})
            except Exception:
                self._record_failure('pull')
                continue

            if result.status_code != OK:
                self._record_failure('pull')
                continue

            msg_ids = get_msg_ids(result.body)

            if not msg_ids:
                continue

            try:
                ack_result = post_json(ack_url, self.puller_auth, {'msg_ids': msg_ids})
            except Exception:
                self._record_failure('ack')
                continue

            if ack_result.status_code == OK:
                with self.lock:
                    self.acked.update(msg_ids)
            else:
                self._record_failure('ack')

# ################################################################################################################################

    def _audited_loop(self) -> 'None':

        url = self._url(ModuleCtx.Audited_Path)

        while self.is_running.is_set():

            try:
                result = post_json(url, self.caller_auth, {})
            except Exception:
                self._record_failure('audited')
                continue

            if result.status_code == OK:
                with self.lock:
                    self.audited_cids.append(result.body['cid'])
            else:
                self._record_failure('audited')

# ################################################################################################################################

    def start(self) -> 'None':
        self.is_running.set()

        targets:'list[tuple[any_, tuple]]' = []

        for publisher_index in range(ModuleCtx.Publisher_Count):
            targets.append((self._publish_loop, (publisher_index,)))

        targets.append((self._pull_loop, ()))
        targets.append((self._audited_loop, ()))

        for target, args in targets:
            thread = threading.Thread(target=target, args=args, daemon=True)
            thread.start()
            self._threads.append(thread)

# ################################################################################################################################

    def stop(self) -> 'None':
        self.is_running.clear()

        for thread in self._threads:
            thread.join()

# ################################################################################################################################

    def drain(self) -> 'None':
        """ Pulls and acknowledges what the queue holds once the server is back, until every acknowledged publication
        was delivered, including the messages whose lease the loss of power left behind.
        """
        pull_url = self._url(ModuleCtx.Pull_Path)
        ack_url = self._url(ModuleCtx.Ack_Path)

        expected = set(self.published.values())
        deadline = time.monotonic() + ModuleCtx.Drain_Timeout

        while True:

            delivered = self.acked | set(self.drained)
            missing = expected - delivered

            if not missing:
                break

            assert time.monotonic() < deadline, f'Not delivered after the loss of power: {len(missing)} of {len(expected)}'

            # The server may still be reconnecting to its database ..
            try:
                result = post_json(pull_url, self.puller_auth, {'max_messages': ModuleCtx.Pull_Max_Messages})
            except Exception:
                time.sleep(ModuleCtx.Poll_Interval)
                continue

            if result.status_code != OK:
                time.sleep(ModuleCtx.Poll_Interval)
                continue

            msg_ids = get_msg_ids(result.body)

            # .. and a message pulled before the loss of power returns to the queue only once its lease ends.
            if not msg_ids:
                time.sleep(ModuleCtx.Poll_Interval)
                continue

            self.drained.extend(msg_ids)

            ack_result = post_json(ack_url, self.puller_auth, {'msg_ids': msg_ids})
            assert ack_result.status_code == OK, ack_result

# ################################################################################################################################
# ################################################################################################################################

def get_msg_ids(body:'anydict') -> 'strlist':
    """ Returns the msg_id of each message of a pull response.
    """
    out:'strlist' = []

    for message in body['messages']:
        meta = message['meta']
        out.append(meta['msg_id'])

    return out

# ################################################################################################################################
# ################################################################################################################################
