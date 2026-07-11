# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
from datetime import datetime, timedelta, timezone

# Arrow
from arrow import Arrow

# datetutil
from dateutil.parser import parse as dt_parse
from dateutil.tz.tz import tzutc

# requests
from requests import \
    delete as requests_delete, \
    get    as requests_get,    \
    head   as requests_head,   \
    patch  as requests_patch,  \
    post   as requests_post,   \
    put    as requests_put

# Zato
from zato.common.api import AS4, SCHEDULER
from zato.common.json_internal import dumps
from zato.common.typing_ import cast_
from zato.server.connection.sftp import SFTPConnection
from zato.server.connection.smb import SMBConnection

################################################################################################################################
################################################################################################################################

if 0:
    from elasticsearch import Elasticsearch
    from pymongo import MongoClient
    from requests import Response
    from zato.common.as2.outbound import SendResult as AS2SendResult
    from zato.common.as4.outbound import PullResult, SendResult
    from zato.common.pubsub.redis_backend import PublishResult
    from zato.common.typing_ import any_, anydict, callnone, strbytes, strnone
    from zato.server.base.parallel import ParallelServer
    from zato.server.base.config_manager import ConfigManager
    from zato.server.config import ConfigDict
    from zato.server.connection.as4 import AS4Wrapper
    from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper
    from zato.server.generic.api.outconn_as2 import as2_payload, OutconnAS2Wrapper
    from zato.server.generic.api.outconn_hl7_fhir import _HL7FHIRConnection
    from zato.server.queue_bridge.client import QueueBridgeClient
    from zato.server.service import Service
    _HL7FHIRConnection = _HL7FHIRConnection
    Response = Response
    Service = Service

################################################################################################################################
################################################################################################################################

_utz_utc = timezone.utc

################################################################################################################################
################################################################################################################################

_http_methods = {'delete', 'get', 'head', 'patch', 'post', 'put'}

# How many seconds to wait for a pooled FHIR client, which covers the window
# while the connection queue is still being built at startup.
_fhir_block_timeout = 30

# How many seconds to wait for a pooled OData client, which covers the window
# while the connection queue is still being built at startup.
_odata_block_timeout = 30

################################################################################################################################
################################################################################################################################

class SchedulerFacade:
    """ The API through which jobs can be scheduled.
    """
    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server

################################################################################################################################

    def onetime(
        self,
        invoking_service, # type: Service
        target_service,   # type: any_
        name='',          # type: str
        *,
        prefix='',        # type: str
        start_date='',    # type: any_
        after_seconds=0,  # type: int
        after_minutes=0,  # type: int
        data=''           # type: any_
        ) -> 'int':
        """ Schedules a service to run at a specific date and time or aftern N minutes or seconds.
        """

        # This is reusable
        now = self.server.time_util.utcnow(needs_format=False)

        # We are given a start date on input ..
        if start_date:
            if not isinstance(start_date, datetime):

                # This gives us a datetime object but we need to ensure
                # that it is in UTC because this what the scheduler expects.
                start_date = dt_parse(start_date)

                if not isinstance(start_date.tzinfo, tzutc):
                    _as_arrow = Arrow.fromdatetime(start_date)
                    start_date = _as_arrow.to(_utz_utc)

        # .. or we need to compute one ourselves.
        else:
            start_date = now + timedelta(seconds=after_seconds, minutes=after_minutes)

        # This is the service that is scheduling a job ..
        invoking_name = invoking_service.get_name()

        # .. and this is the service that is being scheduled.
        target_name   = target_service if isinstance(target_service, str) else target_service.get_name()

        # Construct a name for the job
        name = name or '{}{} -> {} {} {}'.format(
            '{} '.format(prefix) if prefix else '',
            invoking_name,
            target_name,
            now.isoformat(),
            invoking_service.cid,
        )

        # This is what the service being invoked will receive on input
        if data:
            data = dumps({
                SCHEDULER.EmbeddedIndicator: True,
                'data': data
            })

        # Now, we are ready to create a new job ..
        response = self.server.invoke(
            'zato.scheduler.job.create', {
                'cluster_id': self.server.cluster_id,
                'name': name,
                'is_active': True,
                'job_type': SCHEDULER.JOB_TYPE.ONE_TIME,
                'service': target_name,
                'start_date': start_date,
                'extra': data
            }
        )

        # .. check if we shouldn't go further to extract the actual response ..
        if 'id' not in response:
            response = response['zato_scheduler_job_create_response']

        # .. and return its ID to the caller.
        return response['id'] # type: ignore

# ################################################################################################################################
# ################################################################################################################################

class RESTFacade:
    """ A facade through which self.rest calls can be made.
    """
    cid: 'str'
    _out_plain_http: 'ConfigDict'

    name_prefix: 'str' = ''
    needs_facade: 'bool' = True
    has_path_in_args: 'bool' = False

    before_call_func: 'callnone' = None
    after_call_func:  'callnone' = None

    def init(self, cid:'str', _out_plain_http:'ConfigDict') -> 'None':
        self.cid = cid
        self._out_plain_http = _out_plain_http

# ################################################################################################################################

    def delete(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return requests_delete(*args, **kwargs)

    def get(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return requests_get(*args, **kwargs)

    def head(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return requests_head(*args, **kwargs)

    def patch(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return requests_patch(*args, **kwargs)

    def post(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return requests_post(*args, **kwargs)

    def put(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return requests_put(*args, **kwargs)

# ################################################################################################################################

    def _get(self, orig_name:'str', needs_prefix:'bool'=True) -> 'RESTInvoker':

        # Check if name may point to an environment variable ..
        if orig_name.startswith('$'):
            env_name = orig_name.replace('$', '', 1)
            name = os.environ[env_name]

        # .. otherwise, use it as is.
        else:
            name = orig_name

        # Use a potential prefix
        if needs_prefix:
            name = self.name_prefix + name

        # This will raise a KeyError if we have no such name ..
        item = self._out_plain_http[name]

        # .. now, we can return our own facade.
        invoker = RESTInvoker(item.conn, self)
        return invoker

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'RESTInvoker':
        result = self._get(name)
        return result

# ################################################################################################################################

    def __getattr__(self, attr_name:'str') -> 'RESTInvoker':

        # Use a potential prefix
        attr_name = self.name_prefix + attr_name

        try:
            # First, try and see if we do not have a connection of that exact name ..
            conn = self._get(attr_name, needs_prefix=False)
        except KeyError:
            # .. this is fine, there was no such connection
            pass
        else:
            # .. if there was, we can return it here ..
            return conn

        # .. otherwise, go through of the connections and check their filesystem-safe names ..
        for config in self._out_plain_http.get_config_list():
            if config['name_fs_safe'] == attr_name:
                name = config['name']
                break
        else:
            raise KeyError(f'No such connection `{attr_name}`')

        # If we are here, it means that we must have found the correct name
        return self._get(name, needs_prefix=False)

# ################################################################################################################################
# ################################################################################################################################

class RESTInvoker:
    conn: 'HTTPSOAPWrapper'
    container: 'RESTFacade'

    def __init__(self, conn:'HTTPSOAPWrapper', container:'RESTFacade') -> 'None':
        self.conn = conn
        self.container = container

    def __repr__(self) -> 'str':
        return f'RESTInvoker({self.conn.config["name"]} at {hex(id(self))})'

# ################################################################################################################################

    def call_rest_func(self, func_name:'str', conn_name:'str', *args:'any_', **kwargs:'str') -> 'any_':

        # .. the actual method to invoke ..
        func = getattr(self.conn, func_name)

        # .. if we have a function to call before the actual method should be invoked, do it now ..
        if self.container.before_call_func:
            self.container.before_call_func(func_name, conn_name, self.conn, *args, **kwargs)

        # .. do invoke the actual function ..
        result = func(self.container.cid, *args, **kwargs)

        # .. if we have a function to call after the actual method was invoked, do it now ..
        if self.container.after_call_func:
            self.container.after_call_func(func_name, conn_name, self.conn, result, *args, **kwargs)

        # .. and return the result to our caller.
        return result

# ################################################################################################################################

    def call_wrapper(self, *args:'any_', **kwargs:'any_') -> 'any_':

        # This will be always the same
        conn_name = self.conn.config['name']
        func_name = args[0]
        args = args[1:]

        # If this is a pre-facade REST call, we do not need the CID in here
        if args:
            if args[0] == self.container.cid:
                args = args[1:]

        # Depending on what kind of an invoker this is, build the path that we actually want to access.
        if self.container.has_path_in_args:
            if args:
                _zato_path = args[0]
                args = args[1:]
            else:
                _zato_path = '/zato-no-path-given'

            # We know we will be always able to populate this key with some value
            kwargs_params = kwargs.setdefault('params', {})
            kwargs_params['_zato_path'] = _zato_path

        return self.call_rest_func(func_name, conn_name, *args, **kwargs)

# ################################################################################################################################

    def invoke(self, *args:'any_', **kwargs:'str') -> 'any_':
        """ Invokes the connection with no arguments needed at all - the HTTP method,
        query string, path params, headers and body come from the connection's
        declarative invocation profile.
        """
        return self.call_wrapper('rest_invoke', *args, **kwargs)

    def get(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('get', *args, **kwargs)

    def delete(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('delete', *args, **kwargs)

    def options(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('options', *args, **kwargs)

    def post(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('post', *args, **kwargs)

    send = post

    def put(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('put', *args, **kwargs)

    def patch(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('patch', *args, **kwargs)

    def ping(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('ping', *args, **kwargs)

    def upload(self, *args:'any_', **kwargs:'str') -> 'any_':
        return self.call_wrapper('upload', *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

class SOAPInvoker:
    """ Wraps a single SOAP outgoing connection for use from services.
    """
    conn: 'HTTPSOAPWrapper'
    cid: 'str'

    def __init__(self, conn:'HTTPSOAPWrapper', cid:'str') -> 'None':
        self.conn = conn
        self.cid = cid

    def __repr__(self) -> 'str':
        return f'SOAPInvoker({self.conn.config["name"]} at {hex(id(self))})'

# ################################################################################################################################

    def invoke(self, operation:'str'='', message:'any_'=None) -> 'any_':
        """ Invokes a SOAP operation - with no arguments, the operation and message both come
        from the connection's declarative invocation profile, explicit arguments always win.
        """
        return self.conn.invoke(self.cid, operation, message)

# ################################################################################################################################

    def invoke_ebxml(self, info:'any_', parts:'any_', sign:'bool'=False, encrypt:'bool'=False) -> 'any_':
        return self.conn.invoke_ebxml(self.cid, info, parts, sign=sign, encrypt=encrypt)

# ################################################################################################################################

    def ping(self) -> 'any_':
        return self.conn.ping(self.cid)

# ################################################################################################################################
# ################################################################################################################################

class SOAPFacade:
    """ Provides dict-like access to SOAP outgoing connections from services via self.soap.
    """
    cid: 'str'
    _out_soap: 'ConfigDict'

    def init(self, cid:'str', _out_soap:'ConfigDict') -> 'None':
        self.cid = cid
        self._out_soap = _out_soap

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'SOAPInvoker':

        # This will raise a KeyError if there is no such connection
        item = self._out_soap[name]

        return SOAPInvoker(item.conn, self.cid)

# ################################################################################################################################
# ################################################################################################################################

class AS4Invoker:
    """ Wraps a single AS4 outgoing connection for use from services.
    """
    conn: 'AS4Wrapper'
    cid: 'str'

    def __init__(self, conn:'AS4Wrapper', cid:'str') -> 'None':
        self.conn = conn
        self.cid = cid

    def __repr__(self) -> 'str':
        return f'AS4Invoker({self.conn.config["name"]} at {hex(id(self))})'

# ################################################################################################################################

    def send(
        self,
        data:'strbytes',
        mime_type:'str'=AS4.Default.Payload_MIME_Type,
        conversation_id:'strnone'=None,
        ) -> 'SendResult':
        """ Sends one AS4 message to the connection's configured endpoint,
        verifying the synchronous receipt.
        """
        out = self.conn.send(self.cid, data, mime_type, conversation_id)
        return out

# ################################################################################################################################

    def send_to(
        self,
        participant_id:'str',
        document_type:'str',
        data:'strbytes',
        from_participant:'strnone'=None,
        conversation_id:'strnone'=None,
        ) -> 'SendResult':
        """ The access-point one-liner - discovers the receiver's endpoint through SML and SMP,
        wraps the business document in an SBDH and delivers it there, verifying the receipt.
        """
        out = self.conn.send_to(self.cid, participant_id, document_type, data, from_participant, conversation_id)
        return out

# ################################################################################################################################

    def pull(self, mpc:'strnone'=None) -> 'PullResult':
        """ Sends one pull request to the connection's configured endpoint -
        the generic One-Way/Pull exchange - and returns whatever came back.
        """
        out = self.conn.pull(self.cid, mpc)
        return out

# ################################################################################################################################

    def ping(self) -> 'str':
        """ Performs a signed ping exchange with the connection's configured endpoint.
        """
        out = self.conn.ping(self.cid)
        return out

# ################################################################################################################################

    def publish(
        self,
        data:'strbytes',
        mime_type:'str'=AS4.Default.Payload_MIME_Type,
        conversation_id:'strnone'=None,
        participant_id:'strnone'=None,
        document_type:'strnone'=None,
        from_participant:'strnone'=None,
        ) -> 'PublishResult':
        """ Publishes the message to the outbound AS4 topic instead of posting it directly -
        the built-in delivery subscriber performs the HTTP delivery, so redelivery on failure
        is pub/sub's built-in behavior. With a participant id the delivery runs send_to,
        without one it runs send.
        """
        if isinstance(data, bytes):
            data = data.decode('utf8')

        # Everything the delivery service needs to replay this call travels in the message.
        message = {
            'connection': self.conn.config['name'],
            'data': data,
            'mime_type': mime_type,
            'conversation_id': conversation_id,
            'participant_id': participant_id,
            'document_type': document_type,
            'from_participant': from_participant,
        }

        server = self.conn.server
        out = server.pubsub_redis.publish(AS4.Default.Outbound_Topic, message, cid=self.cid, correl_id=self.cid)

        return out

# ################################################################################################################################
# ################################################################################################################################

class AS4Facade:
    """ Provides dict-like access to AS4 outgoing connections from services via self.as4.
    """
    cid: 'str'
    _out_as4: 'ConfigDict'

    def init(self, cid:'str', _out_as4:'ConfigDict') -> 'None':
        self.cid = cid
        self._out_as4 = _out_as4

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'AS4Invoker':

        # This will raise a KeyError if there is no such connection
        item = self._out_as4[name]

        return AS4Invoker(item.conn, self.cid)

# ################################################################################################################################
# ################################################################################################################################

class AS2Invoker:
    """ Wraps a single AS2 outgoing connection for use from services.
    """
    conn: 'OutconnAS2Wrapper'
    cid: 'str'

    def __init__(self, conn:'OutconnAS2Wrapper', cid:'str') -> 'None':
        self.conn = conn
        self.cid = cid

    def __repr__(self) -> 'str':
        return f'AS2Invoker({self.conn.config["name"]} at {hex(id(self))})'

# ################################################################################################################################

    def send(self, payload:'as2_payload', filename:'strnone'=None, *, needs_audit:'bool'=True) -> 'AS2SendResult':
        """ Sends one AS2 message to the connection's configured endpoint,
        reconciling the synchronous MDN when one was requested.
        """
        out = self.conn.send(self.cid, payload, filename, needs_audit=needs_audit)
        return out

# ################################################################################################################################

    def ping(self) -> 'None':
        """ Validates the endpoint without posting anything - a TCP connection
        plus, over HTTPS, the TLS handshake against the endpoint's certificate.
        """
        self.conn.ping()

# ################################################################################################################################
# ################################################################################################################################

class AS2Facade:
    """ Provides dict-like access to AS2 outgoing connections from services via self.as2.
    """
    cid: 'str'
    _outconn_as2: 'anydict'

    def init(self, cid:'str', config_manager:'ConfigManager') -> 'None':
        self.cid = cid
        self._outconn_as2 = config_manager.outconn_as2

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'AS2Invoker':

        # This will raise a KeyError if there is no such connection
        item = self._outconn_as2[name]

        # The wrapper holds a queue with the underlying AS2 connections
        wrapper = item['conn']

        out = AS2Invoker(wrapper, self.cid)
        return out

# ################################################################################################################################
# ################################################################################################################################

class KeysightVisionFacade(RESTFacade):
    name_prefix = 'KeysightVision.'
    has_path_in_args = True

# ################################################################################################################################
# ################################################################################################################################

class KeysightHawkeyeFacade(RESTFacade):
    name_prefix = 'KeysightHawkeye.'
    has_path_in_args = True

# ################################################################################################################################

    def before_call_func(
        self,
        func_name, # type: str
        conn_name, # type: str
        conn,      # type: HTTPSOAPWrapper
        *args,     # type: any_
        **kwargs,  # type: str
    ) -> 'any_':
        pass

# ################################################################################################################################

    def after_call_func(
        self,
        func_name, # type: str
        conn_name, # type: str
        conn,      # type: HTTPSOAPWrapper
        result,    # type: Response
        *args,     # type: any_
        **kwargs,  # type: str
    ) -> 'any_':
        pass

# ################################################################################################################################
# ################################################################################################################################

class KeysightContainer:
    vision:  'KeysightVisionFacade'
    hawkeye: 'KeysightHawkeyeFacade'

    def init(self, cid:'str', _out_plain_http:'ConfigDict') -> 'None':

        self.vision = KeysightVisionFacade()
        self.vision.init(cid, _out_plain_http)

        self.hawkeye = KeysightHawkeyeFacade()
        self.hawkeye.init(cid, _out_plain_http)

# ################################################################################################################################
# ################################################################################################################################

class KafkaInvoker:
    _conn_name: 'str'
    _queue_bridge: 'QueueBridgeClient'

    def __init__(self, conn_name:'str', queue_bridge:'QueueBridgeClient') -> 'None':
        self._conn_name = conn_name
        self._queue_bridge = queue_bridge

    def __repr__(self) -> 'str':
        return f'KafkaInvoker({self._conn_name} at {hex(id(self))})'

    def to_dict(self) -> 'anydict':
        return {'conn_name': self._conn_name}

# ################################################################################################################################

    def send(self, data:'any_') -> 'None':
        if isinstance(data, bytes):
            to_send = data
        elif isinstance(data, str):
            to_send = data.encode('utf-8')
        else:
            to_send = json.dumps(data).encode('utf-8')

        reply = self._queue_bridge.send_message(self._conn_name, to_send) # type: anydict

        status = reply['status']
        if status == 'ok':
            return

        if status == 'error':
            raise Exception('Kafka send to `{}` failed: {}'.format(self._conn_name, reply['data']))

        raise Exception('Kafka send to `{}` timed out'.format(self._conn_name))

# ################################################################################################################################
# ################################################################################################################################

class KafkaFacade:
    _outconn_kafka: 'anydict'
    _queue_bridge: 'QueueBridgeClient'

    def init(self, config_manager:'ConfigManager') -> 'None':
        self._outconn_kafka = config_manager.outconn_kafka
        self._queue_bridge = config_manager.server._queue_bridge

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'KafkaInvoker':
        self._outconn_kafka[name]
        return KafkaInvoker(name, self._queue_bridge)

# ################################################################################################################################
# ################################################################################################################################

class IBMMQInvoker:
    _conn_name: 'str'
    _queue_bridge: 'QueueBridgeClient'

    def __init__(self, conn_name:'str', queue_bridge:'QueueBridgeClient') -> 'None':
        self._conn_name = conn_name
        self._queue_bridge = queue_bridge

    def __repr__(self) -> 'str':
        return f'IBMMQInvoker({self._conn_name} at {hex(id(self))})'

    def to_dict(self) -> 'anydict':
        return {'conn_name': self._conn_name}

# ################################################################################################################################

    def send(self, data:'any_') -> 'None':
        if isinstance(data, bytes):
            to_send = data
        elif isinstance(data, str):
            to_send = data.encode('utf-8')
        else:
            to_send = json.dumps(data).encode('utf-8')

        reply = self._queue_bridge.send_message(self._conn_name, to_send) # type: anydict

        status = reply['status']
        if status == 'ok':
            return

        if status == 'error':
            raise Exception('IBM MQ send to `{}` failed: {}'.format(self._conn_name, reply['data']))

        raise Exception('IBM MQ send to `{}` timed out'.format(self._conn_name))

# ################################################################################################################################
# ################################################################################################################################

class IBMMQFacade:
    """ Provides dict-like access to outgoing IBM MQ connections from services via self.ibm_mq.
    """
    _outconn_ibm_mq: 'anydict'
    _queue_bridge: 'QueueBridgeClient'

    def init(self, config_manager:'ConfigManager') -> 'None':
        self._outconn_ibm_mq = config_manager.outconn_ibm_mq
        self._queue_bridge = config_manager.server._queue_bridge

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'IBMMQInvoker':
        self._outconn_ibm_mq[name]
        return IBMMQInvoker(name, self._queue_bridge)

# ################################################################################################################################
# ################################################################################################################################

class HL7MLLPInvoker:
    """ Wraps a single HL7 MLLP outgoing connection for use from services.
    """
    _conn_name: 'str'
    _outconn_hl7_mllp: 'anydict'

    def __init__(self, conn_name:'str', outconn_hl7_mllp:'anydict') -> 'None':
        self._conn_name = conn_name
        self._outconn_hl7_mllp = outconn_hl7_mllp

    def __repr__(self) -> 'str':
        return f'HL7MLLPInvoker({self._conn_name} at {hex(id(self))})'

    def to_dict(self) -> 'anydict':
        return {'conn_name': self._conn_name}

# ################################################################################################################################

    def send(self, data:'str | bytes') -> 'object':
        """ Sends an HL7 message through the named outgoing connection and returns an AckResult.
        """
        wrapper = self._outconn_hl7_mllp[self._conn_name].conn

        # Take a pooled connection for the duration of the send, it goes back to the pool afterwards
        with wrapper.client() as connection:
            out = connection.invoke(data)

        return out

# ################################################################################################################################
# ################################################################################################################################

class MLLPFacade:
    """ Provides dict-like access to HL7 MLLP outgoing connections from services via self.mllp.
    """
    _outconn_hl7_mllp: 'anydict'

    def init(self, config_manager:'ConfigManager') -> 'None':
        self._outconn_hl7_mllp = config_manager.outconn_hl7_mllp

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'HL7MLLPInvoker':
        self._outconn_hl7_mllp[name]
        return HL7MLLPInvoker(name, self._outconn_hl7_mllp)

# ################################################################################################################################
# ################################################################################################################################

class FHIRFacade:
    """ Provides dict-like access to HL7 FHIR outgoing connections from services via self.fhir.
    """
    _outconn_hl7_fhir: 'anydict'

    def init(self, config_manager:'ConfigManager') -> 'None':
        self._outconn_hl7_fhir = config_manager.outconn_hl7_fhir

# ################################################################################################################################

    def __getitem__(self, name:'str') -> '_HL7FHIRConnection':

        # This will raise a KeyError if there is no such connection
        wrapper = self._outconn_hl7_fhir[name].conn

        # Take a pooled client, blocking to cover the window while the queue is still being built,
        # and put it right back - the client is safe for concurrent use so all callers share the one object.
        with wrapper.client(should_block=True, block_timeout=_fhir_block_timeout) as client:
            out = cast_('_HL7FHIRConnection', client)

        return out

# ################################################################################################################################
# ################################################################################################################################

class SFTPFacade:
    """ Provides dict-like access to SFTP outgoing connections from services via self.sftp.
    """
    cid: 'str'
    _outconn_sftp: 'anydict'

    def init(self, cid:'str', config_manager:'ConfigManager') -> 'None':
        self.cid = cid
        self._outconn_sftp = config_manager.outconn_sftp

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'SFTPConnection':

        # This will raise a KeyError if there is no such connection
        item = self._outconn_sftp[name]

        # The wrapper holds a queue with the underlying SFTP client
        wrapper = item['conn']

        out = SFTPConnection(self.cid, wrapper)
        return out

# ################################################################################################################################
# ################################################################################################################################

class SMBFacade:
    """ Provides dict-like access to SMB outgoing connections from services via self.smb.
    """
    cid: 'str'
    _outconn_smb: 'anydict'

    def init(self, cid:'str', config_manager:'ConfigManager') -> 'None':
        self.cid = cid
        self._outconn_smb = config_manager.outconn_smb

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'SMBConnection':

        # This will raise a KeyError if there is no such connection
        item = self._outconn_smb[name]

        # The wrapper holds a queue with the underlying SMB client
        wrapper = item['conn']

        out = SMBConnection(self.cid, wrapper)
        return out

# ################################################################################################################################
# ################################################################################################################################

class MongoDBFacade:
    """ Provides dict-like access to MongoDB outgoing connections from services via self.mongodb.
    """
    cid: 'str'
    _outconn_mongodb: 'anydict'

    def init(self, cid:'str', config_manager:'ConfigManager') -> 'None':
        self.cid = cid
        self._outconn_mongodb = config_manager.outconn_mongodb

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'MongoClient':

        # This will raise a KeyError if there is no such connection
        item = self._outconn_mongodb[name]

        # The wrapper holds the underlying pymongo client
        wrapper = item['conn']

        out = wrapper.client
        return out

# ################################################################################################################################
# ################################################################################################################################

class ESFacade:
    """ Provides dict-like access to Elasticsearch outgoing connections from services via self.es.
    """
    cid: 'str'
    _outconn_es: 'anydict'

    def init(self, cid:'str', config_manager:'ConfigManager') -> 'None':
        self.cid = cid
        self._outconn_es = config_manager.outconn_es

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'Elasticsearch':

        # This will raise a KeyError if there is no such connection
        item = self._outconn_es[name]

        # The wrapper holds the underlying Elasticsearch client
        wrapper = item['conn']

        out = wrapper.client
        return out

# ################################################################################################################################
# ################################################################################################################################

class GraphQLInvoker:
    """ Wraps a single GraphQL outgoing connection for use from services.
    """
    _conn_name: 'str'
    _outconn_graphql: 'anydict'

    def __init__(self, conn_name:'str', outconn_graphql:'anydict') -> 'None':
        self._conn_name = conn_name
        self._outconn_graphql = outconn_graphql

# ################################################################################################################################

    def __repr__(self) -> 'str':
        out = f'GraphQLInvoker({self._conn_name} at {hex(id(self))})'
        return out

# ################################################################################################################################

    @staticmethod
    def _build_transport(config:'anydict', server:'any_'=None) -> 'any_':
        """ Builds a RequestsHTTPTransport from a connection config dict,
        including security headers based on auth_type.
        """
        from gql.transport.requests import RequestsHTTPTransport

        address = config['address']
        timeout = config.get('default_query_timeout')
        if timeout:
            timeout = int(timeout)

        # .. extra headers ..
        if extra := config.get('extra'):
            headers = json.loads(extra) if isinstance(extra, str) else dict(extra)
        else:
            headers = {}

        # .. inject security based on auth_type ..
        auth = None
        auth_type = config.get('auth_type') or ''

        if auth_type in ('basic_auth', 'apikey', 'oauth'):

            # .. resolve the server reference - either from the conn wrapper or passed directly ..
            if not server:
                conn_wrapper = config.get('conn')
                if conn_wrapper:
                    server = conn_wrapper.server

            security_id = config.get('security_id')

            if server and security_id:

                if auth_type == 'basic_auth':
                    from requests.auth import HTTPBasicAuth
                    sec_config = server.config_manager.basic_auth_get_by_id(security_id)
                    auth = HTTPBasicAuth(sec_config['username'], sec_config['password'])

                elif auth_type == 'apikey':
                    sec_config = server.config_manager.apikey_get_by_id(security_id)
                    headers[sec_config['username']] = sec_config['password']

                elif auth_type == 'oauth':
                    auth_header = server.oauth_store.get_auth_header(security_id)
                    if auth_header:
                        headers['Authorization'] = auth_header

        out = RequestsHTTPTransport(url=address, timeout=timeout, headers=headers, auth=auth)
        return out

# ################################################################################################################################

    def execute(self, query:'any_', params:'anydict | None'=None) -> 'anydict':
        """ Executes a GraphQL query or mutation against the configured server.
        """
        # gql
        from gql import Client as GQLClient
        from gql import gql as gql_parse

        # Get the connection's config ..
        config = self._outconn_graphql[self._conn_name]

        # .. build the transport with auth ..
        transport = self._build_transport(config)

        # .. build the client ..
        client = GQLClient(transport=transport)

        # .. if the query is a string, parse it ..
        if isinstance(query, str):
            query = gql_parse(query)

        # .. build the request keyword arguments ..
        execute_kwargs = {}

        if params:
            execute_kwargs['variable_values'] = params

        # .. execute the query ..
        with client as session:
            out = session.execute(query, **execute_kwargs)

        return out

    invoke = execute

# ################################################################################################################################

    def session(self) -> 'any_':
        """ Returns a context manager that yields a (session, DSLSchema) pair for DSL-based queries.
        """
        # stdlib
        from contextlib import contextmanager

        # gql
        from gql import Client as GQLClient
        from gql.dsl import DSLSchema

        # Get the connection's config ..
        config = self._outconn_graphql[self._conn_name]

        @contextmanager
        def _session_ctx():

            # Build the transport with auth and schema fetching enabled ..
            transport = GraphQLInvoker._build_transport(config)
            client = GQLClient(transport=transport, fetch_schema_from_transport=True)

            # .. open the session ..
            with client as gql_session:
                schema = DSLSchema(client.schema)
                yield gql_session, schema

        return _session_ctx()

# ################################################################################################################################

    def ping(self) -> 'bool':
        """ Pings the GraphQL server using a schema introspection query.
        """
        _ping_query = '{ __schema { queryType { name } } }'
        _ = self.execute(_ping_query)

        out = True
        return out

# ################################################################################################################################

    @staticmethod
    def ping_config(config:'anydict') -> 'None':
        """ Pings using a raw config dict (as stored in the config manager).
        """
        from gql import Client as GQLClient
        from gql import gql as gql_parse

        transport = GraphQLInvoker._build_transport(config)
        client = GQLClient(transport=transport)

        try:
            _ = client.execute(gql_parse('{ __schema { queryType { name } } }'))
        except Exception as e:
            raise Exception(str(e)) from None

# ################################################################################################################################
# ################################################################################################################################

class GraphQLFacade:
    """ Provides dict-like access to GraphQL outgoing connections from services via self.out.graphql.
    """
    _outconn_graphql: 'anydict'

    def init(self, config_manager:'ConfigManager') -> 'None':
        self._outconn_graphql = config_manager.outconn_graphql

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'GraphQLInvoker':
        self._outconn_graphql[name]
        return GraphQLInvoker(name, self._outconn_graphql)

# ################################################################################################################################
# ################################################################################################################################

class ODataConnection:
    """ Exposes the OData client API for one outgoing connection - each call borrows
    a pooled client, invokes it and returns it to the pool, so user code never handles
    the pool itself.
    """
    _conn_name: 'str'
    _outconn_odata: 'anydict'

    def __init__(self, conn_name:'str', outconn_odata:'anydict') -> 'None':
        self._conn_name = conn_name
        self._outconn_odata = outconn_odata

# ################################################################################################################################

    def __repr__(self) -> 'str':
        out = f'ODataConnection({self._conn_name} at {hex(id(self))})'
        return out

# ################################################################################################################################

    def _borrow(self) -> 'any_':
        """ Returns a context manager that yields a pooled client, blocking to cover
        the window while the connection queue is still being built at startup.
        """
        wrapper = self._outconn_odata[self._conn_name].conn

        out = wrapper.client(should_block=True, block_timeout=_odata_block_timeout)
        return out

# ################################################################################################################################

    def read(self, *args:'any_', **kwargs:'any_') -> 'any_':
        with self._borrow() as client:
            out = client.read(*args, **kwargs)
        return out

    def iter(self, *args:'any_', **kwargs:'any_') -> 'any_':

        # The client stays borrowed for as long as the caller iterates.
        with self._borrow() as client:
            for item in client.iter(*args, **kwargs):
                yield item

    def get(self, *args:'any_', **kwargs:'any_') -> 'any_':
        with self._borrow() as client:
            out = client.get(*args, **kwargs)
        return out

    def create(self, *args:'any_', **kwargs:'any_') -> 'any_':
        with self._borrow() as client:
            out = client.create(*args, **kwargs)
        return out

    def update(self, *args:'any_', **kwargs:'any_') -> 'any_':
        with self._borrow() as client:
            out = client.update(*args, **kwargs)
        return out

    def delete(self, *args:'any_', **kwargs:'any_') -> 'any_':
        with self._borrow() as client:
            out = client.delete(*args, **kwargs)
        return out

    def call_function(self, *args:'any_', **kwargs:'any_') -> 'any_':
        with self._borrow() as client:
            out = client.call_function(*args, **kwargs)
        return out

    def call_action(self, *args:'any_', **kwargs:'any_') -> 'any_':
        with self._borrow() as client:
            out = client.call_action(*args, **kwargs)
        return out

    def count(self, *args:'any_', **kwargs:'any_') -> 'any_':
        with self._borrow() as client:
            out = client.count(*args, **kwargs)
        return out

    def batch(self, *args:'any_', **kwargs:'any_') -> 'any_':
        with self._borrow() as client:
            out = client.batch(*args, **kwargs)
        return out

    def metadata(self, *args:'any_', **kwargs:'any_') -> 'any_':
        with self._borrow() as client:
            out = client.metadata(*args, **kwargs)
        return out

    def ping(self) -> 'any_':
        with self._borrow() as client:
            out = client.ping()
        return out

# ################################################################################################################################
# ################################################################################################################################

class ODataFacade:
    """ Provides dict-like access to OData outgoing connections from services via self.odata.
    """
    _outconn_odata: 'anydict'

    def init(self, config_manager:'ConfigManager') -> 'None':
        self._outconn_odata = config_manager.outconn_odata

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'ODataConnection':

        # This will raise a KeyError if there is no such connection
        self._outconn_odata[name]

        out = ODataConnection(name, self._outconn_odata)
        return out

# ################################################################################################################################
# ################################################################################################################################
