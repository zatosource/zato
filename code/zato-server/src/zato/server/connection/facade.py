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
from zato.common.api import SCHEDULER
from zato.common.json_internal import dumps

################################################################################################################################
################################################################################################################################

if 0:
    from requests import Response
    from zato.common.typing_ import any_, anydict, callnone
    from zato.server.base.parallel import ParallelServer
    from zato.server.base.config_manager import ConfigManager
    from zato.server.config import ConfigDict
    from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper
    from zato.server.queue_bridge.client import QueueBridgeClient
    from zato.server.service import Service

################################################################################################################################
################################################################################################################################

_utz_utc = timezone.utc

################################################################################################################################
################################################################################################################################

_http_methods = {'delete', 'get', 'head', 'patch', 'post', 'put'}

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
        if not 'id' in response:
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
        conn = self._outconn_hl7_mllp[self._conn_name].conn
        out = conn.invoke(data)
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

    def execute(self, query:'any_', params:'anydict | None'=None) -> 'anydict':
        """ Executes a GraphQL query or mutation against the configured server.
        """

        # gql
        from gql import Client as GQLClient
        from gql import gql as gql_parse
        from gql.transport.requests import RequestsHTTPTransport

        # Get the connection's config ..
        config = self._outconn_graphql[self._conn_name]
        address = config.config['address']
        timeout = config.config.get('default_query_timeout')

        # .. extra headers ..
        if extra_raw := config.config.get('extra'):
            headers = json.loads(extra_raw)
        else:
            headers = {}

        # .. build the transport ..
        transport = RequestsHTTPTransport(url=address, timeout=timeout, headers=headers)

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

# ################################################################################################################################

    def session(self) -> 'any_':
        """ Returns a context manager that yields a (session, DSLSchema) pair for DSL-based queries.
        """

        # stdlib
        from contextlib import contextmanager

        # gql
        from gql import Client as GQLClient
        from gql.dsl import DSLSchema
        from gql.transport.requests import RequestsHTTPTransport

        # Get the connection's config ..
        config = self._outconn_graphql[self._conn_name]
        address = config.config['address']
        timeout = config.config.get('default_query_timeout')

        # .. extra headers ..
        if extra_raw := config.config.get('extra'):
            headers = json.loads(extra_raw)
        else:
            headers = {}

        @contextmanager
        def _session_ctx():

            # Build the transport and client with schema fetching enabled ..
            transport = RequestsHTTPTransport(url=address, timeout=timeout, headers=headers)
            client = GQLClient(transport=transport, fetch_schema_from_transport=True)

            # .. open the session ..
            with client as gql_session:
                ds = DSLSchema(client.schema)
                yield gql_session, ds

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
        from gql.transport.requests import RequestsHTTPTransport

        address = config['address']
        timeout = config.get('default_query_timeout')
        if timeout:
            timeout = int(timeout)

        if extra_raw := config.get('extra'):
            headers = json.loads(extra_raw)
        else:
            headers = {}

        transport = RequestsHTTPTransport(url=address, timeout=timeout, headers=headers)
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
