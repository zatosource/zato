# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from base64 import b64decode, b64encode
from contextlib import closing
from operator import attrgetter
from traceback import format_exc
from uuid import uuid4

# Python 2/3 compatibility
from builtins import bytes
from zato.common.ext.future.utils import iterkeys

# Zato
from zato.common.api import BROKER, SCHEDULER, StatsKey
from zato.common.broker_message import SERVICE
from zato.common.const import ServiceConst
from zato.common.exception import BadRequest, ZatoException
from zato.common.ext.validate_ import is_boolean
from zato.common.json_ import dumps as json_dumps
from zato.common.json_internal import dumps, loads
from zato.common.json_schema import get_service_config
from zato.common.marshal_.api import Model
from zato.common.odb.model import Cluster, ChannelAMQP, ChannelWMQ, ChannelZMQ, DeployedService, HTTPSOAP, Server, \
    Service as ODBService
from zato.common.odb.query import service_deployment_list, service_list
from zato.common.rate_limiting import DefinitionParser
from zato.common.scheduler import get_startup_job_services
from zato.common.util.api import hot_deploy, parse_extra_into_dict, payload_from_request
from zato.common.util.file_system import get_tmp_path
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service import Boolean, Float, Integer, Service
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import any_, anydict, strnone

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

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_service_get_list_request'
        response_elem = 'zato_service_get_list_response'
        input_required = 'cluster_id'
        input_optional = ('should_include_scheduler',) + GetListAdminSIO.input_optional
        output_required = 'id', 'name', 'is_active', 'impl_name', 'is_internal', Boolean('may_be_deleted')
        output_optional = 'is_json_schema_enabled', 'needs_json_schema_err_details', 'is_rate_limit_active', \
            'rate_limit_type', 'rate_limit_def', Boolean('rate_limit_check_parent_def'), Integer('usage'), \
            Integer('usage'), Integer('slow_threshold')
        output_repeated = True
        default_value = ''

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

            # Attach JSON Schema validation configuration
            json_schema_config = get_service_config(item, self.server)

            item.is_json_schema_enabled = json_schema_config['is_json_schema_enabled']
            item.needs_json_schema_err_details = json_schema_config['needs_json_schema_err_details']

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

class _GetStatsTable(AdminService):

    def handle(self):

        table = None # self.server.stats_client.get_table()
        if table:
            self.response.payload = table

# ################################################################################################################################
# ################################################################################################################################

class GetStatsTable(AdminService):

    class SimpleIO(AdminSIO):
        output_optional = ('name', Float('item_max'), Float('item_min'), Float('item_mean'), Float('item_total_time'), \
            Float('item_usage_share'), Float('item_time_share'), Integer('item_total_usage'),
            'item_total_time_human', 'item_total_usage_human')
        response_elem = None

    def handle(self):

        self.response.payload[:] = []

# ################################################################################################################################
# ################################################################################################################################

class GetServiceStats(AdminService):

    def handle(self):
        usage = self.server.current_usage.get(self.request.raw_request['name'])
        if usage:
            self.response.payload = usage

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

    class SimpleIO(AdminSIO):
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active', 'impl_name', 'is_internal', Boolean('may_be_deleted')
        output_optional = Integer('usage'), Integer('slow_threshold'), 'last_duration', \
            Integer('time_min_all_time'), Integer('time_max_all_time'), 'time_mean_all_time', \
            'is_json_schema_enabled', 'needs_json_schema_err_details', 'is_rate_limit_active', \
            'rate_limit_type', 'rate_limit_def', Boolean('rate_limit_check_parent_def'), 'last_timestamp', \
            'usage_min', 'usage_max', 'usage_mean'

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
    class SimpleIO(_Get.SimpleIO):
        request_elem = 'zato_service_get_by_name_request'
        response_elem = 'zato_service_get_by_name_response'
        input_required = _Get.SimpleIO.input_required + ('name',)

    def add_filter(self, query): # type: ignore
        return query.\
            filter(ODBService.name==self.request.input.name)

# ################################################################################################################################
# ################################################################################################################################

class GetByID(_Get):
    """ Returns a particular service by its ID.
    """
    class SimpleIO(_Get.SimpleIO):
        request_elem = 'zato_service_get_by_name_request'
        response_elem = 'zato_service_get_by_name_response'
        input_required = _Get.SimpleIO.input_required + ('id',)

    def add_filter(self, query): # type: ignore
        return query.\
            filter(ODBService.id==self.request.input.id)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a service.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_edit_request'
        response_elem = 'zato_service_edit_response'
        input_required = 'id', 'is_active', Integer('slow_threshold')
        input_optional = 'is_json_schema_enabled', 'needs_json_schema_err_details', 'is_rate_limit_active', \
            'rate_limit_type', 'rate_limit_def', 'rate_limit_check_parent_def'
        output_optional = 'id', 'name', 'impl_name', 'is_internal', Boolean('may_be_deleted')

    def handle(self):
        input = self.request.input

        # If we have a rate limiting definition, let's check it upfront
        DefinitionParser.check_definition_from_input(input)

        with closing(self.odb.session()) as session:
            try:
                service = session.query(ODBService).filter_by(id=input.id).one() # type: ODBService
                service.is_active = input.is_active
                service.slow_threshold = input.slow_threshold

                set_instance_opaque_attrs(service, input)

                # Configure JSON Schema validation if service has a schema assigned by user.
                class_info = self.server.service_store.get_service_info_by_id(input.id) # type: anydict
                class_ = class_info['service_class'] # type: ODBService
                if class_.schema:
                    self.server.service_store.set_up_class_json_schema(class_, input) # type: ignore

                # Set up rate-limiting each time an object was edited
                self.server.service_store.set_up_rate_limiting(service.name)

                session.add(service)
                session.commit()

                input.action = SERVICE.EDIT.value
                input.impl_name = service.impl_name
                input.name = service.name
                self.broker_client.publish(input)

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
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_delete_request'
        response_elem = 'zato_service_delete_response'
        input_required = ('id',)

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
                self.broker_client.publish(msg)

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
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_get_channel_list_request'
        response_elem = 'zato_service_get_channel_list_response'
        input_required = ('id', 'channel_type')
        output_required = ('id', 'name')

    def handle(self):
        channel_type_class = {
            'plain_http': HTTPSOAP,
            'amqp': ChannelAMQP,
            'jms-wmq': ChannelWMQ,
            'zmq': ChannelZMQ,
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

class Invoke(AdminService):
    """ Invokes the service directly, as though it was exposed through a channel defined in web-admin.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_invoke_request'
        response_elem = 'zato_service_invoke_response'
        input_optional = 'id', 'name', 'payload', 'channel', 'data_format', 'transport', Boolean('is_async'), \
            Integer('expiration'), Integer('pid'), Boolean('all_pids'), Integer('timeout'), Boolean('skip_response_elem'), \
            'needs_response_time'
        output_optional = ('response',)

# ################################################################################################################################

    def _get_payload_from_extra(self, payload:'any_') -> 'strnone':

        if not payload:
            return

        if payload in (b'""', b"''", b'null', 'null'):
            return

        if isinstance(payload, bytes):
            payload = payload.decode('utf8')

        # .. ignore payload that seems to be JSON ..
        if '{' in payload or '}' in payload:
            return

        payload = payload[1:-1]
        payload = payload.replace('\\n', '\n')
        payload = parse_extra_into_dict(payload)

        return payload

# ################################################################################################################################

    def _invoke_other_server_pid(
        self,
        name:'str',
        payload:'any_',
        pid:'int',
        data_format:'str',
        skip_response_elem:'bool',
    ) -> 'any_':

        response = self.server.invoke(
            name,
            payload, # type: ignore
            pid=pid,
            data_format=data_format,
            skip_response_elem=skip_response_elem)

        response = {
            pid: {
                'is_ok': True,
                'pid': pid,
                'pid_data': response or None,
                'error_info': '',
        }}

        return response

# ################################################################################################################################

    def _invoke_current_server_pid(
        self,
        id:'any_',
        name:'str',
        all_pids:'bool',
        payload:'any_',
        channel:'str',
        data_format:'str',
        transport:'str',
        zato_response_headers_container:'anydict',
        skip_response_elem:'bool',
    ) -> 'any_':

        func, id_ = (self.invoke, name) if name else (self.invoke_by_id, id)

        response = func(
            id_,
            payload, # type: ignore
            channel,
            data_format,
            transport,
            zato_response_headers_container=zato_response_headers_container,
            skip_response_elem=skip_response_elem,
            serialize=True)

        if all_pids:

            response = {
                self.server.pid: {
                    'is_ok': True,
                    'pid': self.server.pid,
                    'pid_data': response,
                    'error_info': '',
            }}

        return response

# ################################################################################################################################

    def _build_response(self, response:'any_') -> 'any_':

        if not isinstance(response, str):
            if not isinstance(response, bytes):
                if hasattr(response, 'to_dict'):
                    response = response.to_dict() # type: ignore
                response = json_dumps(response)

        # Make sure what we return is a string ..
        response = response if isinstance(response, bytes) else response.encode('utf8')

        # .. which we base64-encode ..
        response = b64encode(response).decode('utf8') if response else ''

        # .. and return to our caller.
        return response

# ################################################################################################################################

    def _run_async_invoke(
        self,
        pid:'int',
        id:'any_',
        name:'str',
        payload:'any_',
        channel:'str',
        data_format:'str',
        transport:'str',
        expiration:'int',
    ) -> 'any_':

        if id:
            impl_name = self.server.service_store.id_to_impl_name[id]
            name = self.server.service_store.service_data(impl_name)['name']

        # If PID is given on input it means we must invoke this particular server process by it ID
        if pid and pid != self.server.pid:
            response = self.server.invoke_by_pid(name, payload, pid)
        else:
            response = self.invoke_async(name, payload, channel, data_format, transport, expiration)

        return response

# ################################################################################################################################

    def _run_sync_invoke(
        self,
        pid:'int',
        timeout:'int',
        id:'any_',
        name:'str',
        all_pids:'bool',
        payload:'any_',
        channel:'str',
        data_format:'str',
        transport:'str',
        zato_response_headers_container:'anydict',
        skip_response_elem:'bool',
    ) -> 'any_':

        # This method is the same as the one for async, except that in async there was no all_pids

        # It is possible that we were given the all_pids flag on input but we know
        # ourselves that there is only one process, the current one, so we can just
        # invoke it directly instead of going through IPC.
        if all_pids and self.server.fs_server_config.main.gunicorn_workers > 1:
            use_all_pids = True
        else:
            use_all_pids = False

        if use_all_pids:
            args = (name, payload, timeout) if timeout else (name, payload)
            response = dumps(self.server.invoke_all_pids(*args, skip_response_elem=skip_response_elem))

        else:

            # We are invoking another server by its PID ..
            if pid and pid != self.server.pid:
                response = self._invoke_other_server_pid(name, payload, pid, data_format, skip_response_elem)

            # .. we are invoking our own process ..
            else:
                response = self._invoke_current_server_pid(
                    id, name, all_pids, payload, channel, data_format, transport,
                    zato_response_headers_container, skip_response_elem)

        return response

# ################################################################################################################################

    def _build_response_time(self, start_time:'datetime') -> 'any_':

        response_time = self.time.utcnow(needs_format=False) - start_time # type: ignore
        response_time = response_time.total_seconds()
        response_time = response_time * 1000 # Turn seconds into milliseconds

        # If we have less than a millisecond, don't show exactly how much it was ..
        if response_time < 1:
            response_time_human = 'Below 1 ms'
        else:
            # .. if it's below 10 seconds, keep using milliseconds ..
            if response_time < 10_000:
                response_time = int(response_time) # Round it up
                response_time_human = f'{response_time} ms'

            # .. otherwise, turn it into seconds ..
            else:
                _response_time = float(response_time)
                _response_time = _response_time / 1000.0 # Convert it back to seconds
                _response_time = round(_response_time, 2) # Keep it limited to two digits
                response_time_human = f'{_response_time} sec.'

        return response_time, response_time_human

# ################################################################################################################################

    def handle(self):

        # Local aliases
        payload:'any_' = None
        needs_response_time = self.request.input.get('needs_response_time', True)

        # A dictionary of headers that the target service may want to produce
        zato_response_headers_container = {}

        # Optionally, we are return the total execution time of this service
        if needs_response_time:
            start_time = self.time.utcnow(needs_format=False)

        # This is our input ..
        orig_payload:'any_' = self.request.input.get('payload')

        # .. which is optional ..
        if orig_payload:

            # .. if it exists, it will be BASE64-encoded ..
            orig_payload = b64decode(orig_payload) # type: ignore

            # .. try and see if it a dict of extra keys and value ..
            payload = self._get_payload_from_extra(orig_payload)

            # .. if it is not, run the regular parser ..
            if not payload:
                payload = payload_from_request(self.server.json_parser, self.cid, orig_payload,
                    self.request.input.data_format, self.request.input.transport)

                if payload:

                    if isinstance(payload, str):
                        scheduler_indicator = SCHEDULER.EmbeddedIndicator
                    else:
                        scheduler_indicator = SCHEDULER.EmbeddedIndicatorBytes

                    if scheduler_indicator in payload: # type: ignore
                        payload = loads(payload) # type: ignore
                        payload = payload['data'] # type: ignore

        id = self.request.input.get('id')
        name = self.request.input.get('name')
        pid = self.request.input.get('pid') or 0
        all_pids = self.request.input.get('all_pids')
        timeout = self.request.input.get('timeout') or None
        skip_response_elem = self.request.input.get('skip_response_elem') or False

        channel = self.request.input.get('channel')
        data_format = self.request.input.get('data_format')
        transport = self.request.input.get('transport')
        expiration = self.request.input.get('expiration') or BROKER.DEFAULT_EXPIRATION

        if name and id:
            raise ZatoException('Cannot accept both id:`{}` and name:`{}`'.format(id, name))

        try:

            # Is this an async invocation ..
            if self.request.input.get('is_async'):
                response = self._run_async_invoke(
                    pid, id, name, payload, channel, data_format, transport, expiration)

            # .. or a sync one ..
            else:
                response = self._run_sync_invoke(
                    pid, timeout, id, name, all_pids, payload, channel,
                    data_format, transport, zato_response_headers_container, skip_response_elem
                )

            # .. we still may not have any response here ..
            if response is not None:
                response = self._build_response(response)
                self.response.payload.response = response

        finally:

            # If we are here, it means that we can optionally compute the total execution time ..
            if needs_response_time:

                # .. build the values we are to return ..
                response_time, response_time_human = self._build_response_time(start_time) # type: ignore

                # .. which we attach to our response.
                self.response.headers['X-Zato-Response-Time'] = response_time
                self.response.headers['X-Zato-Response-Time-Human'] = response_time_human

# ################################################################################################################################
# ################################################################################################################################

class GetDeploymentInfoList(AdminService):
    """ Returns detailed information regarding the service's deployment status on each of the servers it's been deployed to.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_get_deployment_info_list_request'
        response_elem = 'zato_service_get_deployment_info_list_response'
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
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_get_source_info_request'
        response_elem = 'zato_service_get_source_info_response'
        input_required = ('cluster_id', 'name')
        output_optional = ('service_id', 'server_name', 'source', 'source_path', 'source_hash', 'source_hash_method')

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
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_upload_package_request'
        response_elem = 'zato_service_upload_package_response'
        input_required = ('cluster_id', 'payload', 'payload_name')

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

class ServiceInvoker(AdminService):
    """ A proxy service to invoke other services through via REST.
    """
    name = ServiceConst.ServiceInvokerName

# ################################################################################################################################

    def _extract_payload_from_request(self):
        payload = self.request.raw_request
        payload = loads(payload) if payload else None
        return payload

# ################################################################################################################################

    def handle(self, _internal=('zato', 'pub.zato')): # type: ignore

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

            # All internal services wrap their responses in top-level elements that we need to shed here ..
            if is_internal and response:
                top_level = list(iterkeys(response))[0]
                response = response[top_level]

            # Take dataclass-based models into account
            response = response.to_dict() if isinstance(response, Model) else response

            # Assign response to outgoing payload
            self.response.payload = dumps(response)
            self.response.data_format = 'application/json'
            self.response.headers.update(zato_response_headers_container)

        # No such service as given on input
        else:
            self.response.data_format = 'text/plain'
            raise BadRequest(self.cid, 'No such service `{}`'.format(service_name))

# ################################################################################################################################
# ################################################################################################################################

class RPCServiceInvoker(AdminService):
    """ An invoker making use of the API that Redis-based communication used to use.
    """
    def handle(self):
        self.server.on_broker_msg(self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################
