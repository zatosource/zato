# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The runtime services of generic connections - the ones that reach a live connection through the server's
# config manager to ping it or to invoke it, and never write a row. Their names spell out the module the ODB
# services live in, which is where they used to live and what every caller knows them by.

# stdlib
from contextlib import closing
from traceback import format_exc
from urllib.parse import parse_qsl

# Zato
from zato.common.api import GENERIC as COMMON_GENERIC
from zato.common.ext_db.api import is_ext_object_id, to_local_id
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.util.time_ import utcnow
from zato.server.service import Int
from zato.server.service.internal import AdminService
from zato.server.service.internal.generic import _BaseService

# ################################################################################################################################
# ################################################################################################################################

# The connection types whose clients send messages to a target rather than invoking a request as-is
_chat_conn_types = frozenset({
    COMMON_GENERIC.CONNECTION.TYPE.CHAT_MICROSOFT_TEAMS,
    COMMON_GENERIC.CONNECTION.TYPE.CHAT_SLACK,
})

# ################################################################################################################################
# ################################################################################################################################

class Ping(_BaseService):
    """ Pings a generic connection.
    """
    name = 'zato.generic.connection.ping'
    input = Int('id')
    output = 'info', '-is_success'

    def handle(self) -> 'None':

        # Objects from the external AS2/AS4 database are stored under their local ids there
        input_id = self.request.input.id

        if is_ext_object_id(input_id):
            local_id = to_local_id(input_id)
        else:
            local_id = input_id

        with closing(self.server.get_config_session(object_id=input_id)) as session:

            # To ensure that the input ID is correct
            instance = self._get_instance_by_id(session, ModelGenericConn, local_id)

            # Different code paths will be taken depending on what kind of a generic connection this is
            custom_ping_func_dict = {}

            # Most connections use a generic ping function, unless overridden on a case-by-case basis.
            ping_func = custom_ping_func_dict.get(instance.type_, self.server.config_manager.ping_generic_connection)

            start_time = utcnow()

            try:
                _ = ping_func(self.request.input.id)
            except Exception as e:

                # The full traceback goes to the server log ..
                self.logger.warning(format_exc())

                # .. while the caller gets the actual error message alone.
                error_message = str(e)
                if not error_message:
                    error_message = e.__class__.__name__

                self.response.payload.info = error_message
                self.response.payload.is_success = False
            else:
                response_time = utcnow() - start_time
                info = 'Connection pinged; response time: {}'.format(response_time)
                self.logger.info(info)
                self.response.payload.info = info
                self.response.payload.is_success = True

# ################################################################################################################################
# ################################################################################################################################

class Invoke(AdminService):
    """ Invokes a generic connection by its name.
    """
    name = 'zato.generic.connection.invoke'
    input = 'conn_type', 'conn_name', '-request_data', '-target'
    output = '-response_data'

    def handle(self) -> 'None':

        # Local aliases
        response = None
        conn_type = self.request.input.conn_type
        request_data = self.request.input.request_data

        # Maps all known connection types to their implementation ..
        conn_type_to_container = {
            COMMON_GENERIC.CONNECTION.TYPE.CHAT_MICROSOFT_TEAMS: self.server.config_manager.chat_microsoft_teams,
            COMMON_GENERIC.CONNECTION.TYPE.CHAT_SLACK: self.server.config_manager.chat_slack,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: self.server.config_manager.outconn_hl7_fhir,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP: self.server.config_manager.outconn_hl7_mllp,
        }

        # .. get the actual implementation ..
        container = conn_type_to_container[conn_type]

        # .. chat connections send the request as a message to a target - a channel, a person or a group -
        # .. rather than invoking a client with the request as-is, and their errors are reported to the caller
        # .. instead of being turned into a response, which is why this path returns early ..
        if conn_type in _chat_conn_types:

            target = self.request.input.target
            if not target:
                raise Exception('No target provided')

            if not request_data:
                raise Exception('No message provided')

            # All the chat clients take the target first and the message second.
            client = container[self.request.input.conn_name].conn.shared_client
            response = client.send(target, request_data)

            # The response is JSON and the caller needs text
            self.response.payload.response_data = dumps(response, indent=2)

            return

        # .. and invoke it.
        with container[self.request.input.conn_name].conn.client() as client:

            try:
                # FHIR connections treat the request as a path to GET, e.g. /Patient?_count=1 ..
                if conn_type == COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR:

                    # .. the query string, if any, must go to the client separately from the path ..
                    path, _, query = request_data.partition('?')
                    params = dict(parse_qsl(query))

                    response = client.execute(path=path, method='get', params=params)

                    # The response is JSON and the caller needs text
                    response = dumps(response, indent=2)

                # .. other connections, e.g. MLLP, send the request as a message.
                else:
                    response = client.invoke(request_data)

                    # The result is an AckResult and the caller needs the acknowledgment itself, i.e. the raw ER7 text
                    response = response.ack_text
            except Exception:
                exc = format_exc()
                response = exc
                self.logger.warning(exc)
            finally:
                self.response.payload.response_data = response

# ################################################################################################################################
# ################################################################################################################################

class InvokeGraphQL(_BaseService):
    """ Invokes a GraphQL outgoing connection with a query and optional variables.
    """
    name = 'zato.generic.connection.invoke-graphql'
    input = Int('id'), '-query', '-variables'
    output = '-response_data', '-response_time'

    def handle(self) -> 'None':

        import json
        import time

        from gql import Client as GQLClient
        from gql import gql as gql_parse
        from zato.server.connection.facade import GraphQLInvoker

        with closing(self.odb.session()) as session:
            instance = self._get_instance_by_id(session, ModelGenericConn, self.request.input.id)
            config = loads(instance.opaque1) if instance.opaque1 else {}
            config['address'] = instance.address
            config['extra'] = instance.extra

        query_text = self.request.input.get('query', '')
        variables_text = self.request.input.get('variables', '')

        if not query_text or not query_text.strip():
            raise Exception('No query provided')

        if variables_text and variables_text.strip():
            variables = json.loads(variables_text)
        else:
            variables = None

        transport = GraphQLInvoker._build_transport(config, self.server)
        client = GQLClient(transport=transport)

        parsed_query = gql_parse(query_text)

        execute_kwargs = {}
        if variables:
            execute_kwargs['variable_values'] = variables

        start = time.monotonic()

        try:
            with client as gql_session:
                result = gql_session.execute(parsed_query, **execute_kwargs)
        except Exception as e:
            elapsed = time.monotonic() - start
            self.response.payload.response_data = str(e)
            self.response.payload.response_time = f'{elapsed:.3f}s'
            raise Exception(str(e)) from None

        elapsed = time.monotonic() - start
        self.response.payload.response_data = json.dumps(result, indent=2)
        self.response.payload.response_time = f'{elapsed:.3f}s'

# ################################################################################################################################
# ################################################################################################################################

class InvokeGRPC(_BaseService):
    """ Invokes a unary method of a gRPC outgoing connection with a JSON request.
    """
    name = 'zato.generic.connection.invoke-grpc'
    input = Int('id'), '-method', '-request_data'
    output = '-response_data', '-response_time'

    def handle(self) -> 'None':

        import time

        from zato.server.connection.grpc_ import invoke_unary_from_json

        # Look up the connection's name by its ID ..
        with closing(self.odb.session()) as session:
            instance = self._get_instance_by_id(session, ModelGenericConn, self.request.input.id)
            name = instance.name

        method = self.request.input.method
        if not method:
            raise Exception('No method provided')

        request_data = self.request.input.request_data or '{}'

        # .. the connection's wrapper holds the underlying channel and stub ..
        config = self.server.config_manager.outconn_grpc[name]
        wrapper = config['conn']

        start = time.monotonic()

        # .. and now the method can be invoked.
        try:
            response_data = invoke_unary_from_json(wrapper, method, request_data, self.cid)
        except Exception as e:
            elapsed = time.monotonic() - start
            self.response.payload.response_data = str(e)
            self.response.payload.response_time = f'{elapsed:.3f}s'
            raise Exception(str(e)) from None

        elapsed = time.monotonic() - start
        self.response.payload.response_data = response_data
        self.response.payload.response_time = f'{elapsed:.3f}s'

# ################################################################################################################################
# ################################################################################################################################
