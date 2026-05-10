# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
from base64 import b64decode, b64encode
from contextlib import closing
from operator import attrgetter
from traceback import format_exc
from uuid import uuid4

# Python 2/3 compatibility
from builtins import bytes

# Zato
from zato.common.broker_message import SERVICE
from zato.common.const import ServiceConst
from zato.common.exception import BadRequest, ZatoException
from zato.common.ext.validate_ import is_boolean
from zato.common.json_internal import dumps, loads
from zato.common.marshal_.api import Model
from zato.common.odb.model import Cluster, ChannelAMQP, DeployedService, HTTPSOAP, Server, Service as ODBService
from zato.common.odb.query import service_deployment_list, service_list
from zato.common.scheduler import get_startup_job_services
from zato.common.util.api import hot_deploy
from zato.common.util.file_system import get_tmp_path
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service import Boolean, Integer, Service
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# For pyflakes
Service = Service

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of services.
    """
    _filter_by = ODBService.name,

    input = 'cluster_id', '-should_include_scheduler'
    output = 'id', 'name', 'is_active', 'impl_name', 'is_internal', Boolean('may_be_deleted')

# ################################################################################################################################

    def _get_data(self, session, return_internal, include_list, internal_del): # type: ignore

        out = []

        search_result = self._search(service_list, session, self.request.input.cluster_id, return_internal, include_list, False)
        search_result = elems_with_opaque(search_result)

        for item in search_result:

            # First, filter out services that aren't deployed, e.g. they may have existed at one point
            # but right now the server doesn't have them deployed.

            # Extract the name of the module that the service is implemented in ..
            impl_name = item.impl_name

            # .. check if we have any deployment info about this module ..
            deployment_info = self.server.service_store.get_deployment_info(impl_name)

            # .. if there's no file-system path for the module's file, it means it's not deployed ..
            if not deployment_info.get('fs_location'):
                continue

            item.may_be_deleted = internal_del if item.is_internal else True

            out.append(item)

        return out

# ################################################################################################################################

    def get_data(self, session): # type: ignore

        # Reusable
        return_internal = is_boolean(self.server.fs_server_config.misc.return_internal_objects)
        internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)

        # We issue one or two queries to populate this list - the latter case only if we are to return scheduler's jobs.
        out = []

        # Confirm if we are to return services for the scheduler
        if self.request.input.should_include_scheduler:
            scheduler_service_list = get_startup_job_services()
        else:
            scheduler_service_list = []

        # This query runs only if there are scheduler services to return ..
        if scheduler_service_list:
            result = self._get_data(session, return_internal, scheduler_service_list, internal_del)
            out.extend(result)

        # .. while this query runs always (note the empty include_list).
        result = self._get_data(session, return_internal, [], internal_del)
        out.extend(result)

        # .. sort the result before returning ..
        out.sort(key=attrgetter('name'))

        # .. finally, return all that we found.
        return out

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class IsDeployed(Service):

    input = 'name'
    output = 'is_deployed'

    def handle(self):
        is_deployed = self.server.service_store.is_deployed(self.request.input.name)
        self.response.payload.is_deployed = is_deployed

# ################################################################################################################################
# ################################################################################################################################

class _Get(AdminService):

    input = 'cluster_id',
    output = 'id', 'name', 'is_active', 'impl_name', 'is_internal', Boolean('may_be_deleted')

    def get_data(self, session): # type: ignore
        query = session.query(ODBService.id, ODBService.name, ODBService.is_active,
            ODBService.impl_name, ODBService.is_internal, ODBService.slow_threshold).\
            filter(Cluster.id==ODBService.cluster_id).\
            filter(Cluster.id==self.request.input.cluster_id)

        query = self.add_filter(query) # type: ignore
        return query.one()

    def handle(self):
        with closing(self.odb.session()) as session:
            service = self.get_data(session)

            internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)

            self.response.payload.id = service.id
            self.response.payload.name = service.name
            self.response.payload.is_active = service.is_active
            self.response.payload.impl_name = service.impl_name
            self.response.payload.is_internal = service.is_internal
            self.response.payload.slow_threshold = service.slow_threshold
            self.response.payload.may_be_deleted = internal_del if service.is_internal else True

# ################################################################################################################################
# ################################################################################################################################

class GetByName(_Get):
    """ Returns a particular service by its name.
    """
    input = 'cluster_id', 'name'

    def add_filter(self, query): # type: ignore
        return query.\
            filter(ODBService.name==self.request.input.name)

# ################################################################################################################################
# ################################################################################################################################

class GetByID(_Get):
    """ Returns a particular service by its ID.
    """
    input = 'cluster_id', 'id'

    def add_filter(self, query): # type: ignore
        return query.\
            filter(ODBService.id==self.request.input.id)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a service.
    """
    input = 'id', 'is_active', Integer('slow_threshold')
    output = '-id', '-name', '-impl_name', '-is_internal', Boolean('-may_be_deleted')

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:
            try:
                service = session.query(ODBService).filter_by(id=input.id).one() # type: ODBService
                service.is_active = input.is_active
                service.slow_threshold = input.slow_threshold

                set_instance_opaque_attrs(service, input)

                session.add(service)
                session.commit()

                input.action = SERVICE.EDIT.value
                input.impl_name = service.impl_name
                input.name = service.name
                self.config_dispatcher.publish(input)

                self.response.payload = service
                internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)
                self.response.payload.may_be_deleted = internal_del if service.is_internal else True

            except Exception:
                self.logger.error('ODBService could not be updated, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a service.
    """
    input = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                service = session.query(ODBService).\
                    filter(ODBService.id==self.request.input.id).\
                    one() # type: ODBService

                internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)

                if service.is_internal and not internal_del:
                    msg = "Can't delete service:[{}], it's an internal one and internal_services_may_be_deleted is not True".format(
                        service.name)
                    raise ZatoException(self.cid, msg)

                # This will also cascade to delete the related DeployedService objects
                session.delete(service)
                session.commit()

                msg = {
                    'action': SERVICE.DELETE.value,
                    'id': self.request.input.id,
                    'name':service.name,
                    'impl_name':service.impl_name,
                    'is_internal':service.is_internal,
                }
                self.config_dispatcher.publish(msg)

            except Exception:
                session.rollback()
                msg = 'ODBService could not be deleted, e:`{}`'.format(format_exc())
                self.logger.error(msg)

                raise

# ################################################################################################################################
# ################################################################################################################################

class GetChannelList(AdminService):
    """ Returns a list of channels of a given type through which the service is exposed.
    """
    input = 'id', 'channel_type'
    output = 'id', 'name'

    def handle(self):
        channel_type_class = {
            'plain_http': HTTPSOAP,
            'amqp': ChannelAMQP,
        }

        class_ = channel_type_class[self.request.input.channel_type]
        q_attrs = (class_.id, class_.name)

        with closing(self.odb.session()) as session:
            q = session.query(*q_attrs).\
                filter(class_.service_id == self.request.input.id)

            if self.request.input.channel_type == 'soap':
                q = q.filter(class_.soap_version != None) # noqa
            elif self.request.input.channel_type == 'plain_http':
                q = q.filter(class_.soap_version == None) # noqa

            self.response.payload[:] = q.all()

# ################################################################################################################################
# ################################################################################################################################

class GetDeploymentInfoList(AdminService):
    """ Returns detailed information regarding the service's deployment status on each of the servers it's been deployed to.
    """
    input = '-id', '-needs_details', Boolean('-include_internal')
    output = 'server_id', 'server_name', 'service_id', 'service_name', 'fs_location', 'file_name', \
        Integer('line_number'), '-details'

    def get_data(self, session): # type: ignore

        # Response to produce
        out = []

        # This is optional and if it does not exist we assume that it is True
        if not 'include_internal' in self.request.input:
            include_internal = True
        else:
            include_internal = self.request.input.get('include_internal')

        needs_details = self.request.input.needs_details
        items = service_deployment_list(session, self.request.input.id, include_internal)

        for item in items:

            # Convert the item from SQLAlchemy to a dict because we are going to append the file_name to it ..
            _item = item._asdict()

            # .. load it but do not assign it yet because it is optional ..
            details = loads(item.details)

            # .. extract the file name out of the full path to the service ..
            fs_location = details['fs_location']
            _item['file_name'] = os.path.basename(fs_location)

            # .. but append the full path as well ..
            _item['fs_location'] = fs_location

            # .. this is also required ..
            _item['line_number'] = details['line_number']

            # .. this is optional ..
            if needs_details:
                _item['details'] = details
            else:
                del _item['details']

            # .. we can append this item now ..
            out.append(_item)

        # .. and return the whole output once we are done,
        return out

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class GetSourceInfo(AdminService):
    """ Returns information on the service's source code.
    """
    input = 'cluster_id', 'name'
    output = '-service_id', '-server_name', '-source', '-source_path', '-source_hash', '-source_hash_method'

    def get_data(self, session): # type: ignore
        return session.query(ODBService.id.label('service_id'), Server.name.label('server_name'), # type: ignore
            DeployedService.source, DeployedService.source_path,
            DeployedService.source_hash, DeployedService.source_hash_method).\
            filter(Cluster.id==ODBService.cluster_id).\
            filter(Cluster.id==self.request.input.cluster_id).\
            filter(ODBService.name==self.request.input.name).\
            filter(ODBService.id==DeployedService.service_id).\
            filter(Server.id==DeployedService.server_id).\
            filter(Server.id==self.server.id).\
            one()

    def handle(self):
        with closing(self.odb.session()) as session:
            si = self.get_data(session)
            self.response.payload.service_id = si.service_id
            self.response.payload.server_name = si.server_name
            self.response.payload.source = b64encode(si.source) if si.source else None
            self.response.payload.source_path = si.source_path
            self.response.payload.source_hash = si.source_hash
            self.response.payload.source_hash_method = si.source_hash_method

# ################################################################################################################################
# ################################################################################################################################

class UploadPackage(AdminService):
    """ Uploads a package with service(s) to be hot-deployed.
    """
    input = 'cluster_id', 'payload', 'payload_name'

    def handle(self):

        # Local variables
        payload = self.request.input.payload
        payload_name = self.request.input.payload_name
        input_payload = b64decode(payload)

        prefix = 'zato-hd-'
        suffix = payload_name
        body = uuid4().hex

        service_deploy_location = os.environ.get('Zato_Service_Deploy_Location')
        has_abs_path = os.path.isabs(payload_name)

        if service_deploy_location:
            file_name_full = os.path.join(service_deploy_location, suffix)
            needs_default_hot_deploy = False
        elif has_abs_path:
            file_name_full = payload_name
            needs_default_hot_deploy = False
        else:
            prefix = 'zato-hd-'
            body = uuid4().hex
            file_name_full = get_tmp_path(prefix, suffix, body)
            needs_default_hot_deploy = True

        current_user = os.environ.get('USER')
        if current_user == 'zato':
            try:
                _ = subprocess.run(['sudo', 'chmod', '664', file_name_full], check=False, capture_output=True)
            except Exception:
                pass

        with open(file_name_full, 'wb') as tf:
            _ = tf.write(input_payload)
            tf.flush()

        if needs_default_hot_deploy:
            package_id = hot_deploy(self.server, payload_name, tf.name, False)
            self.response.payload = {
                'package_id': package_id
            }

# ################################################################################################################################
# ################################################################################################################################

class ServiceInvoker(Service):
    """ A proxy service to invoke other services through via REST.
    """
    name = ServiceConst.ServiceInvokerName

# ################################################################################################################################

    def _extract_payload_from_request(self):
        payload = self.request.raw_request
        payload = loads(payload) if payload else None
        return payload

# ################################################################################################################################

    def _check_gateway_allowed(self, service_name):
        """ Checks whether the service is allowed for the current channel's gateway allowlist.
        If the allowlist is empty, all services are allowed.
        """
        channel_id = self.channel.id

        with self.server.gateway_services_allowed_lock:
            allowed_services = self.server.gateway_services_allowed.get(channel_id)

        if allowed_services and service_name not in allowed_services:
            raise BadRequest(self.cid, 'No such service `{}`'.format(service_name))

# ################################################################################################################################

    def _set_request_context(self):
        """ Propagates Django and forwarded-for context from HTTP headers into wsgi_environ.
        """
        django_user = self.wsgi_environ.get('HTTP_X_ZATO_USER', '')
        correlation_id = self.wsgi_environ.get('HTTP_X_ZATO_CORRELATION_ID', '')
        forwarded_for = self.wsgi_environ.get('HTTP_X_ZATO_FORWARDED_FOR', '')

        if django_user or correlation_id or forwarded_for:
            self.wsgi_environ['zato.request_ctx'] = {
                'django_user': django_user,
                'correlation_id': correlation_id,
                'forwarded_for': forwarded_for,
            }

# ################################################################################################################################

    def handle(self, _internal=('zato', 'pub.zato')): # type: ignore

        # We track response time for all invocations
        start_time = self.time.utcnow(needs_format=False)

        # ODBService name is given in URL path
        service_name = self.request.http.params.service_name

        # Are we invoking a Zato built-in service or a user-defined one?
        is_internal = service_name.startswith(_internal) # type: bool

        # Before invoking a service that is potentially internal we need to confirm
        # that our channel can be used for such invocations.
        if is_internal:
            if self.channel.name not in self.server.fs_server_config.misc.service_invoker_allow_internal:
                msg = 'ODBService `%s` could not be invoked; channel `%s` not among `%s` (service_invoker_allow_internal)'
                self.logger.warning(
                    msg, service_name, self.channel.name, self.server.fs_server_config.misc.service_invoker_allow_internal)
                self.response.data_format = 'text/plain'
                raise BadRequest(self.cid, 'No such service `{}`'.format(service_name))

        # Per-channel service allowlist enforcement
        self._check_gateway_allowed(service_name)

        # Propagate context headers from callers like the Django plugin
        self._set_request_context()

        # Make sure the service exists
        if self.server.service_store.has_service(service_name):

            # Depending on HTTP verb used, we may need to look up input in different places
            if self.request.http.method == 'GET':
                payload = self.request.http.GET or self._extract_payload_from_request()
            else:
                payload = self._extract_payload_from_request()

            # A dictionary of headers that the target service may want to produce
            zato_response_headers_container = {}

            # Invoke the service now
            response = self.invoke(
                service_name,
                payload,
                wsgi_environ={'HTTP_METHOD':self.request.http.method},
                zato_response_headers_container=zato_response_headers_container
                )

            self.logger.info('ServiceInvoker raw response type=%s for service=%s: %r',
                type(response).__name__, service_name, str(response)[:500])

            # Take dataclass-based models into account
            response = response.to_dict() if isinstance(response, Model) else response

            self.logger.info('ServiceInvoker final response type=%s: %r',
                type(response).__name__, str(response)[:500])

            # Assign response to outgoing payload
            self.response.payload = dumps(response)
            self.response.data_format = 'application/json'
            self.response.headers.update(zato_response_headers_container)

            # Compute and attach response time headers
            elapsed = self.time.utcnow(needs_format=False) - start_time
            total_ms = elapsed.total_seconds() * 1000

            if total_ms < 1:
                response_time_human = 'Below 1 ms'
            elif total_ms < 10_000:
                total_ms = int(total_ms)
                response_time_human = f'{total_ms} ms'
            else:
                total_sec = round(total_ms / 1000.0, 2)
                response_time_human = f'{total_sec} sec.'

            self.response.headers['X-Zato-Response-Time'] = str(total_ms)
            self.response.headers['X-Zato-Response-Time-Human'] = response_time_human

        # No such service as given on input
        else:
            self.response.data_format = 'text/plain'
            raise BadRequest(self.cid, 'No such service `{}`'.format(service_name))

# ################################################################################################################################
# ################################################################################################################################

class RPCServiceInvoker(Service):
    """ An invoker making use of the API that Redis-based communication used to use.
    """
    def handle(self):
        self.server.on_broker_msg(self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################
