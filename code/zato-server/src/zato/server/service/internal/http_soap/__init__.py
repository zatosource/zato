# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""


# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.broker_message import CHANNEL, OUTGOING
from zato.common.exception import ZatoException
from zato.common.ext_db.api import is_ext_object_id, to_local_id
from zato.common.odb.model import HTTPSOAP
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.connection.http_soap import BadRequest
from zato.server.service.internal import AdminService
from zato.server.service.internal.http_soap.common import _health_check, _HTTPSOAPService, _invocation
from zato.server.service.internal.http_soap.health_check import get_linked_job

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService, _HTTPSOAPService):
    """ Deletes an HTTP/SOAP connection.
    """
    input = '-id', '-name', '-connection', '-should_raise_if_missing'
    output = '-details'

    def handle(self):

        input = self.request.input
        input_id = input.get('id')
        name = input.get('name')
        connection = input.get('connection')

        has_expected_input = input_id or (name and connection)

        if not has_expected_input:
            raise Exception('Either ID or name/connection are required on input')

        # Ids arrive as strings and the external database check needs an integer
        if input_id:
            input_id = int(input_id)
        else:
            input_id = 0

        # Objects from the external AS2/AS4 database are stored under their local ids there
        is_ext = is_ext_object_id(input_id)

        if is_ext:
            local_id = to_local_id(input_id)
        else:
            local_id = input_id

        with closing(self.server.get_config_session(object_id=input_id)) as session:
            try:
                query = session.query(HTTPSOAP)

                if input_id:
                    query = query.\
                        filter(HTTPSOAP.id==local_id)

                else:
                    query = query.\
                        filter(HTTPSOAP.name==name).\
                        filter(HTTPSOAP.connection==connection)

                item = query.first()

                # Optionally, raise an exception if such an object is missing
                if not item:
                    if input.get('should_raise_if_missing', True):
                        raise BadRequest(self.cid, 'Could not find an object based on input -> `{}`'.format(input))
                    else:
                        self.response.payload.details = 'No such object'
                        return

                opaque = parse_instance_opaque_attr(item)

                old_name = item.name
                old_transport = item.transport
                old_url_path = item.url_path
                old_soap_action = item.soap_action
                old_http_method = item.method
                old_http_accept = opaque.get('http_accept')

                # .. clean up all pub/sub state before the CASCADE delete -
                # .. the state lives in the main ODB only, so external-database objects have none ..
                if not is_ext:
                    self.server.config_manager.cleanup_rest_endpoint_pubsub(session, item.id)

                session.delete(item)
                session.commit()

                if item.connection == CONNECTION.CHANNEL:
                    action = CHANNEL.HTTP_SOAP_DELETE.value
                else:
                    action = OUTGOING.HTTP_SOAP_DELETE.value

                self.notify_server({
                    'id': self.request.input.id,
                    'name':old_name,
                    'transport':old_transport,
                    'old_url_path':old_url_path,
                    'old_soap_action':old_soap_action,
                    'old_http_method': old_http_method,
                    'old_http_accept': old_http_accept,
                }, action)

                # Scheduler jobs auto-created for this connection are deleted along with it,
                # but only if they still exist - they could have been deleted from the scheduler's own UI.
                for job_id_field in (_invocation.Field_Job_ID, _health_check.Field_Job_ID):
                    if job_id := opaque.get(job_id_field):
                        if get_linked_job(self, job_id):
                            _ = self.invoke('zato.scheduler.job.delete', {'id': job_id})

                self.response.payload.details = 'OK, deleted'

            except Exception:
                session.rollback()
                self.logger.error('Object could not be deleted, e:`%s`', format_exc())

                raise

# ################################################################################################################################

class Ping(AdminService):
    """ Pings an HTTP/SOAP connection.
    """
    input = 'id', '-ping_path'
    output = 'id', 'is_success', '-info'

    def handle(self) -> 'None':

        # Objects from the external AS2/AS4 database are stored under their local ids there
        input_id = int(self.request.input.id)

        if is_ext_object_id(input_id):
            local_id = to_local_id(input_id)
        else:
            local_id = input_id

        # The name and the transport are read while the session is still open
        # because the object is detached from it once it closes.
        with closing(self.server.get_config_session(object_id=input_id)) as session:
            item = session.query(HTTPSOAP).filter_by(id=local_id).one()
            name = item.name
            transport = item.transport

        config_dict = getattr(self.outgoing, transport)
        self.response.payload.id = self.request.input.id

        # A connection that the database has may not have reached this server's RAM yet,
        # which is a different answer than a ping that was sent and came back with an error.
        config_item = config_dict.get(name)

        if config_item is None:
            self.response.payload.is_success = False
            self.response.payload.info = f'No such outgoing connection on this server -> `{name}`'
            return

        try:
            info = config_item.ping(self.cid, ping_path=self.request.input.ping_path)

        # .. a Zato exception carries the message on its own attribute ..
        except ZatoException as e:
            is_success = False
            info = e.msg

        # .. and anything else describes itself.
        except Exception as e:
            is_success = False
            info = str(e)

        else:
            is_success = True

        self.response.payload.info = info
        self.response.payload.is_success = is_success

# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

class ProcessScheduledRequest(AdminService):
    """ Invoked by the scheduler on behalf of an outgoing REST or SOAP connection - runs the connection
    through its declarative invocation profile, which also delivers the response to the configured callback.
    """
    name = _invocation.Dispatch_Service

    def handle(self) -> 'None':

        # The scheduler job carries the connection's identity in its extra data,
        # which arrives here as a dict no matter if the invocation came from the scheduler or over HTTP.
        context = self.request.payload

        conn_name = context[_invocation.Extra_Conn_Name]
        transport = context[_invocation.Extra_Transport]

        # The connection's declarative profile fills in everything else - the HTTP method, query string,
        # path params, headers and body for REST, or the operation and message for SOAP.
        if transport == URL_TYPE.SOAP:
            _ = self.soap[conn_name].invoke()
        else:
            _ = self.rest[conn_name].invoke()

# ################################################################################################################################
# ################################################################################################################################
