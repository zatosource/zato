# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from json import dumps
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep

# Zato
from zato.common.api import HTTP_SOAP, PubSub, URL_TYPE
from zato.common.facade import PubSubFacade
from zato.common.pubsub.util import validate_topic_name
from zato.common.util.api import new_msg_id
from zato.common.util.http_retry import get_next_sleep_time, RetryPolicy
from zato.common.util.time_ import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import PublishResult
    from zato.common.typing_ import any_, anytuple, callable_, strcalldict, stranydict, strset
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

strpagedict = dict[str, 'OutgoingPage']

_topic_prefix   = PubSub.Outgoing.Topic_Prefix
_sub_key_prefix = PubSub.Outgoing.Sub_Key_Prefix
_round_wait     = PubSub.Outgoing.Retry_Round_Wait

# The keys of the envelope a queue stores
Key_Conn_Type  = 'conn_type'
Key_Conn_ID    = 'conn_id'
Key_Conn_Name  = 'conn_name'
Key_CID        = 'cid'
Key_Msg_ID     = 'msg_id'
Key_Pub_Time   = 'pub_time_iso'
Key_Attempts   = 'attempts'
Key_DLQ_Rounds = 'dlq_rounds'
Key_Request    = 'request'

# The keys of the request part - an HTTP type stores a method, a SOAP type an operation
Key_Method    = 'method'
Key_Operation = 'operation'
Key_Data      = 'data'
Key_Headers   = 'headers'
Key_Params    = 'params'

Attempts_None = 0
Attempts_Direct = 1

DLQ_Rounds_None = 0

# Delivery handlers, by connection type
delivery_handlers:'strcalldict' = {}

# Connection locators, by connection type
conn_locators:'strcalldict' = {}

# Retry policy builders, by connection type
retry_policy_builders:'strcalldict' = {}

# DLQ settings readers, by connection type
dlq_settings_readers:'strcalldict' = {}

# What the delivery page shows of each connection type
page_descriptions:'strpagedict' = {}

# Connection types whose queue topics write no pub/sub audit events
audit_disabled_conn_types:'strset' = set()

# The Ace modes a message's body is shown in
Body_Mode_JSON = 'json'
Body_Mode_XML  = 'xml'
Body_Mode_HL7  = 'hl7'
Body_Mode_Text = 'text'

_json_openers = ('{', '[')
_xml_opener   = '<'
_hl7_opener   = 'MSH|'

# ################################################################################################################################
# ################################################################################################################################

class OutgoingType:
    """ The kinds of outgoing connection that can be published to.
    """
    REST = 'rest'
    SOAP = 'soap'
    FHIR = 'fhir'
    SFTP = 'sftp'
    SMB = 'smb'
    FTP = 'ftp'

# Which kind of outgoing connection an HTTP/SOAP connection is, by its transport
http_soap_outgoing_types = {
    URL_TYPE.PLAIN_HTTP: OutgoingType.REST,
    URL_TYPE.SOAP: OutgoingType.SOAP,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OutgoingInvoker:
    """ The invoke dialog of one connection type's list page, which the delivery page opens on a message's destination.
    """

    # Where the dialog posts to, the connection's id and a slash follow
    url_prefix: 'str'

    # What the dialog knows the connection as
    connection: 'str'

    # What the history of one connection's invocations is stored under, the connection's id follows
    history_key_prefix: 'str'

    # (request) -> the dialog's options that are the message's own, e.g. its method and query string
    options: 'callable_'

# ################################################################################################################################

@dataclass(init=False)
class OutgoingPage:
    """ What the delivery page shows of one connection type's messages.
    """

    # (wrapper, request) -> the text of the Destination column
    destination: 'callable_'

    # (request) -> the request facts of the details window, each a label and a value, the value a string or a dict
    details_facts: 'callable_'

    # (request) -> the mode the body is shown in
    body_mode: 'callable_'

    # None for a type whose list page has no invoke dialog
    invoker: 'OutgoingInvoker | None' = None

# ################################################################################################################################

def detect_body_mode(data:'str') -> 'str':
    """ The mode a body is shown in, by what it opens with.
    """
    text = data.lstrip()

    if text.startswith(_json_openers):
        out = Body_Mode_JSON

    elif text.startswith(_xml_opener):
        out = Body_Mode_XML

    elif text.startswith(_hl7_opener):
        out = Body_Mode_HL7

    else:
        out = Body_Mode_Text

    return out

# ################################################################################################################################

def invoker_to_dict(invoker:'OutgoingInvoker | None', request:'stranydict | None'=None) -> 'stranydict | None':
    """ An invoker as the page's script receives it, with the options of one message when there is a message.
    """
    if invoker:
        out = {
            'url_prefix': invoker.url_prefix,
            'connection': invoker.connection,
            'history_key_prefix': invoker.history_key_prefix,
        }

        if request:
            out['options'] = invoker.options(request)
    else:
        out = None

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_outgoing_topic_name(conn_type:'str', conn_name:'str') -> 'str':
    """ The name of the topic in front of one outgoing connection.
    """
    out = f'{_topic_prefix}{conn_type}.{conn_name}'
    out = out.lower()

    validate_topic_name(out)

    return out

# ################################################################################################################################

def get_outgoing_sub_key(conn_type:'str', conn_id:'int') -> 'str':
    """ The sub key of the queue in front of one outgoing connection.
    """
    out = f'{_sub_key_prefix}{conn_type}.{conn_id}'
    return out

# ################################################################################################################################

def parse_outgoing_sub_key(sub_key:'str') -> 'anytuple':
    """ Turns a sub key back into the connection type and connection id it was built from.
    """
    remainder = sub_key[len(_sub_key_prefix):]
    conn_type, _, conn_id = remainder.rpartition('.')

    out = (conn_type, int(conn_id))
    return out

# ################################################################################################################################

def get_outgoing_sub_config(sub_key:'str', topic_name:'str') -> 'stranydict':
    """ The push subscription that puts one outgoing connection's queue in front of the delivery service.
    """
    out = {
        'sub_key': sub_key,
        'topic_name': topic_name,
        'push_type': PubSub.Push_Type.Service,
        'push_service_name': PubSub.Outgoing.Delivery_Service,
        'rest_push_endpoint_id': None,
    }

    return out

# ################################################################################################################################

def register_outgoing_conn_type(
    conn_type:'str',
    locator:'callable_',
    handler:'callable_',
    *,
    is_audit_log_active:'bool'=True,
    retry_policy:'callable_ | None'=None,
    dlq_settings:'callable_ | None'=None,
    page:'OutgoingPage | None'=None,
    ) -> 'None':
    """ Registers one type of outgoing connection with its locator, handler, retry policy, DLQ settings and what
    the delivery page shows of its messages.
    """
    conn_locators[conn_type] = locator
    delivery_handlers[conn_type] = handler

    if retry_policy:
        retry_policy_builders[conn_type] = retry_policy

    if dlq_settings:
        dlq_settings_readers[conn_type] = dlq_settings

    if page:
        page_descriptions[conn_type] = page

    if not is_audit_log_active:
        audit_disabled_conn_types.add(conn_type)

# ################################################################################################################################

def get_page_description(conn_type:'str') -> 'OutgoingPage':
    """ What the delivery page shows of one connection type's messages, raising for a type that has no page.
    """
    page = page_descriptions.get(conn_type)

    if not page:
        raise Exception(f'No delivery page for outgoing connection type `{conn_type}`')

    out = page
    return out

# ################################################################################################################################

def get_dlq_settings(conn_type:'str', wrapper:'any_') -> 'stranydict | None':
    """ The DLQ settings of one connection, or None for a type that has no DLQ.
    """
    reader = dlq_settings_readers.get(conn_type)

    if reader:
        out = reader(wrapper)
    else:
        out = None

    return out

# ################################################################################################################################

def is_dlq_active(conn_type:'str', wrapper:'any_') -> 'bool':
    """ Whether one connection's DLQ switch is on.
    """
    settings = get_dlq_settings(conn_type, wrapper)

    if settings:
        out = settings[HTTP_SOAP.DLQ.Field_Use_DLQ]
    else:
        out = False

    return out

# ################################################################################################################################

def get_retry_policy(conn_type:'str', wrapper:'any_') -> 'RetryPolicy':
    """ The retry policy of one connection, or the default one for a type that has none.
    """
    builder = retry_policy_builders.get(conn_type)

    if builder:
        out = builder(wrapper)
    else:
        out = RetryPolicy.from_config({})

    return out

# ################################################################################################################################

def find_outgoing_conn(server:'ParallelServer', conn_type:'str', conn_id:'int') -> 'anytuple':
    """ One outgoing connection by its id, as its current name and its wrapper, or None if there is no such connection.
    """
    locator = conn_locators.get(conn_type)

    if not locator:
        raise Exception(f'No locator for outgoing connection type `{conn_type}`')

    out = locator(server, conn_id)
    return out

# ################################################################################################################################

def locate_outgoing_conn(server:'ParallelServer', conn_type:'str', conn_id:'int', conn_name:'str'='') -> 'anytuple':
    """ One outgoing connection by its id, as its current name and its wrapper, raising if there is no such connection.
    """
    out = find_outgoing_conn(server, conn_type, conn_id)

    if not out:
        raise Exception(f'No outgoing {conn_type} connection with id `{conn_id}` (`{conn_name}`)')

    return out

# ################################################################################################################################

class DeliveryExhausted(Exception):
    """ Raised when a round of delivery ran out of attempts.
    """

    def __init__(self, error:'str', attempts:'int') -> 'None':
        super().__init__(error)
        self.error = error
        self.attempts = attempts

# ################################################################################################################################
# ################################################################################################################################

def deliver_envelope(server:'ParallelServer', cid:'str', envelope:'stranydict') -> 'None':
    """ Delivers one envelope to its outgoing connection under the connection's retry policy, raising DeliveryExhausted
    when the round ran out of attempts.
    """
    conn_type = envelope[Key_Conn_Type]
    conn_id = envelope[Key_Conn_ID]
    conn_name = envelope[Key_Conn_Name]
    request = envelope[Key_Request]

    # The message travels under the correlation id of the service that sent it
    if envelope[Key_CID]:
        cid = envelope[Key_CID]

    _, wrapper = locate_outgoing_conn(server, conn_type, conn_id, conn_name)
    handler = delivery_handlers[conn_type]
    policy = get_retry_policy(conn_type, wrapper)

    def attempt() -> 'None':
        handler(server, cid, wrapper, request)

    deliver_with_policy(policy, envelope[Key_Attempts], cid, conn_name, attempt)

# ################################################################################################################################

def deliver_with_policy(
    policy:'RetryPolicy',
    attempts_made:'int',
    cid:'str',
    conn_name:'str',
    attempt:'callable_',
    ) -> 'None':
    """ Runs attempts until one is accepted or the policy allows no more, counting from the attempts already made.
    """
    attempts_allowed = 1 + policy.max_retries

    total_sleep_time = 0
    current_sleep_time = policy.sleep_time

    while True:

        # Every attempt after a failed one is preceded by a wait
        if attempts_made:
            sleep(current_sleep_time)
            total_sleep_time += current_sleep_time
            current_sleep_time = get_next_sleep_time(policy, current_sleep_time, total_sleep_time)

        try:
            attempt()
            return

        except Exception as e:
            attempts_made += 1

            # Both the attempt count and the total wait are caps
            has_attempts_left = attempts_made < attempts_allowed
            has_time_left = total_sleep_time < policy.backoff_threshold

            if has_attempts_left and has_time_left:
                logger.info('Queue delivery retry cid=%s, conn=%s, attempt=%s of %s, reason=%s',
                    cid, conn_name, attempts_made, attempts_allowed, e)
                continue

            logger.info('Queue delivery round over cid=%s, conn=%s, attempts=%s, reason=%s', cid, conn_name, attempts_made, e)
            raise DeliveryExhausted(str(e), attempts_made) from e

# ################################################################################################################################

def wait_between_rounds() -> 'None':
    """ The wait between two rounds of one message.
    """
    sleep(_round_wait)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SendResult:
    """ What a send with the queue switch on comes back with.
    """

    # The direct attempt was accepted
    is_ok: 'bool' = False

    # The message is in the queue
    is_in_queue: 'bool' = False

    # The message's id in the queue
    msg_id: 'str' = ''

    # The endpoint's response, if there was one
    response: 'any_' = None

    # Why the message is not delivered
    error: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

class SendRejected(Exception):
    """ Raised by a direct attempt when the endpoint turned the message down.
    """

    def __init__(self, error:'str', response:'any_'=None) -> 'None':
        super().__init__(error)
        self.error = error
        self.response = response

# ################################################################################################################################
# ################################################################################################################################

def build_envelope(
    conn_type:'str',
    conn_id:'int',
    conn_name:'str',
    cid:'str',
    attempts:'int',
    request:'stranydict',
    *,
    dlq_rounds:'int'=DLQ_Rounds_None,
) -> 'stranydict':
    """ The envelope the queue stores for one message.
    """
    out = {
        Key_Conn_Type: conn_type,
        Key_Conn_ID: conn_id,
        Key_Conn_Name: conn_name,
        Key_CID: cid,
        Key_Msg_ID: new_msg_id(),
        Key_Pub_Time: utcnow().isoformat(),
        Key_Attempts: attempts,
        Key_DLQ_Rounds: dlq_rounds,
        Key_Request: request,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class OutgoingPublisher:
    """ Publishes messages to the topic in front of one outgoing connection.
    """

    def __init__(self, server:'ParallelServer', conn_type:'str', conn_id:'int') -> 'None':
        self.server = server
        self.conn_type = conn_type
        self.conn_id = conn_id
        self.sub_key = get_outgoing_sub_key(conn_type, conn_id)

        # Publications are recorded under the delivery service
        self.pubsub = PubSubFacade(server, PubSub.Outgoing.Delivery_Service)

# ################################################################################################################################

    def __repr__(self) -> 'str':
        return f'OutgoingPublisher({self.conn_type}/{self.conn_id} at {hex(id(self))})'

# ################################################################################################################################

    def publish(self, data:'any_'='', **kwargs:'any_') -> 'PublishResult':
        """ Queues one message for delivery to the connection.
        """

        # Handlers are given the payload as a string
        if not isinstance(data, str):
            data = dumps(data)

        request = {
            Key_Data: data,
        }

        out = self.publish_request('', Attempts_None, request, **kwargs)
        return out

# ################################################################################################################################

    def publish_request(
        self,
        cid:'str',
        attempts:'int',
        request:'stranydict',
        *,
        dlq_rounds:'int'=DLQ_Rounds_None,
        **kwargs:'any_',
        ) -> 'PublishResult':
        """ Queues one request for delivery to the connection.
        """
        config_manager = self.server.config_manager

        # Under the connection's publish lock, a rename happens entirely before or entirely after this publication
        with config_manager.get_outgoing_publish_lock(self.conn_type, self.conn_id):

            topic_name, conn_name = config_manager.ensure_outgoing_subscription(self.conn_type, self.conn_id)
            envelope = build_envelope(self.conn_type, self.conn_id, conn_name, cid, attempts, request, dlq_rounds=dlq_rounds)

            # The queue stores the message under the id and the time the envelope carries
            msg_id = envelope[Key_Msg_ID]
            kwargs['msg_id'] = msg_id
            kwargs['pub_time'] = envelope[Key_Pub_Time]

            envelope = dumps(envelope)

            # The depth is raised before the write, or a concurrent send overtakes this message
            depth = config_manager.outgoing_queue_depth
            depth.raise_(self.sub_key)

            if cid:
                kwargs['cid'] = cid

            try:
                pubsub = self.pubsub
                out = pubsub.publish(topic_name, envelope, **kwargs)

            except Exception:
                depth.lower(self.sub_key, 1)
                raise

        # The envelope's id, whichever backend the queue has
        out.msg_id = msg_id

        return out

# ################################################################################################################################

    def send_or_queue(self, cid:'str', request:'stranydict', attempt:'callable_') -> 'SendResult':
        """ Makes the direct attempt if the queue is empty, otherwise or on a rejection queues the message. Never raises.
        """
        out = SendResult()

        depth = self.server.config_manager.outgoing_queue_depth

        # The queue is empty, so the direct attempt is made ..
        if depth.get(self.sub_key) == 0:

            try:
                response = attempt()

            except SendRejected as e:
                out.error = e.error
                out.response = e.response

            except Exception as e:
                out.error = str(e)

            else:
                out.is_ok = True
                out.response = response

                return out

            attempts = Attempts_Direct

        # .. otherwise the message goes to the queue.
        else:
            attempts = Attempts_None

        try:
            result = self.publish_request(cid, attempts, request)

        except Exception as e:
            logger.warning('Could not queue a message for `%s`, cid `%s`, e:`%s`', self.sub_key, cid, format_exc())
            out.error = str(e)

            return out

        out.is_in_queue = True
        out.msg_id = result.msg_id

        return out

# ################################################################################################################################
# ################################################################################################################################
