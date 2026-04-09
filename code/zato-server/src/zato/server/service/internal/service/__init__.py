# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
from base64 import b64decode, b64encode
from hashlib import sha256
from traceback import format_exc
from uuid import uuid4

# Python 2/3 compatibility
from builtins import bytes
from zato.common.ext.future.utils import iterkeys

# Bunch
from bunch import Bunch

# Zato
from zato.common.api import BROKER, CONNECTION, SCHEDULER
from zato.common.broker_message import SERVICE
from zato.common.const import ServiceConst
from zato.common.exception import BadRequest, ZatoException
from zato.common.ext.validate_ import is_boolean
from zato.common.json_ import dumps as json_dumps
from zato.common.json_internal import dumps, loads
from zato.common.marshal_.api import Model
from zato.common.scheduler import get_startup_job_services
from zato.common.util.api import hot_deploy, parse_extra_into_dict, payload_from_request
from zato.common.util.file_system import get_tmp_path
from zato.server.service import Boolean, Integer, Service
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

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_service_get_list_request'
        response_elem = 'zato_service_get_list_response'
        input_required = 'cluster_id'
        input_optional = ('should_include_scheduler',) + GetListAdminSIO.input_optional
        output_required = 'id', 'name', 'is_active', 'impl_name', 'is_internal', Boolean('may_be_deleted')
        output_repeated = True
        default_value = ''

# ################################################################################################################################

    def get_data(self):

        return_internal = is_boolean(self.server.fs_server_config.misc.return_internal_objects)
        internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)

        scheduler_service_set = set()
        if self.request.input.should_include_scheduler:
            scheduler_service_set = set(get_startup_job_services())

        store = self.server.service_store
        out = []
        seen_names = set()

        for impl_name, svc_data in store.services.items():
            name = svc_data['name']

            if name in seen_names:
                continue

            service_class = svc_data['service_class']
            is_internal = getattr(service_class, 'is_internal', name.startswith('zato.') or name.startswith('pub.zato.'))

            if not return_internal and is_internal:
                if name not in scheduler_service_set:
                    continue

            deployment_info = store.get_deployment_info(impl_name)
            if not deployment_info.get('fs_location'):
                continue

            service_id = store.impl_name_to_id.get(impl_name, 0)

            item = Bunch(
                id=service_id,
                name=name,
                is_active=svc_data.get('is_active', True),
                impl_name=impl_name,
                is_internal=is_internal,
                slow_threshold=svc_data.get('slow_threshold', 99999),
                may_be_deleted=internal_del if is_internal else True,
            )
            out.append(item)
            seen_names.add(name)

        out.sort(key=lambda x: x.name)
        return out

    def handle(self):
        self.response.payload[:] = self.get_data()

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

    def _lookup_service(self):
        raise NotImplementedError

    def handle(self):
        store = self.server.service_store
        service_id, impl_name = self._lookup_service()
        svc_data = store.services[impl_name]
        service_class = svc_data['service_class']
        is_internal = getattr(service_class, 'is_internal', svc_data['name'].startswith('zato.'))

        internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)

        self.response.payload.id = service_id
        self.response.payload.name = svc_data['name']
        self.response.payload.is_active = svc_data.get('is_active', True)
        self.response.payload.impl_name = impl_name
        self.response.payload.is_internal = is_internal
        self.response.payload.slow_threshold = svc_data.get('slow_threshold', 99999)
        self.response.payload.may_be_deleted = internal_del if is_internal else True

# ################################################################################################################################
# ################################################################################################################################

class GetByName(_Get):
    """ Returns a particular service by its name.
    """
    class SimpleIO(_Get.SimpleIO):
        request_elem = 'zato_service_get_by_name_request'
        response_elem = 'zato_service_get_by_name_response'
        input_required = _Get.SimpleIO.input_required + ('name',)

    def _lookup_service(self):
        store = self.server.service_store
        name = self.request.input.name
        impl_name = store.name_to_impl_name[name]
        service_id = store.impl_name_to_id[impl_name]
        return service_id, impl_name

# ################################################################################################################################
# ################################################################################################################################

class GetByID(_Get):
    """ Returns a particular service by its ID.
    """
    class SimpleIO(_Get.SimpleIO):
        request_elem = 'zato_service_get_by_name_request'
        response_elem = 'zato_service_get_by_name_response'
        input_required = _Get.SimpleIO.input_required + ('id',)

    def _lookup_service(self):
        store = self.server.service_store
        service_id = int(self.request.input.id)
        impl_name = store.id_to_impl_name[service_id]
        return service_id, impl_name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a service.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_service_edit_request'
        response_elem = 'zato_service_edit_response'
        input_required = 'id', 'is_active', Integer('slow_threshold')
        output_optional = 'id', 'name', 'impl_name', 'is_internal', Boolean('may_be_deleted')

    def handle(self):
        input = self.request.input
        store = self.server.service_store

        service_id = int(input.id)
        impl_name = store.id_to_impl_name[service_id]
        svc_data = store.services[impl_name]

        svc_data['is_active'] = input.is_active
        svc_data['slow_threshold'] = input.slow_threshold

        service_class = svc_data['service_class']
        is_internal = getattr(service_class, 'is_internal', svc_data['name'].startswith('zato.'))

        input.action = SERVICE.EDIT.value
        input.impl_name = impl_name
        input.name = svc_data['name']
        self.broker_client.publish(input)

        internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)

        self.response.payload.id = service_id
        self.response.payload.name = svc_data['name']
        self.response.payload.impl_name = impl_name
        self.response.payload.is_internal = is_internal
        self.response.payload.may_be_deleted = internal_del if is_internal else True

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
        store = self.server.service_store
        service_id = int(self.request.input.id)
        impl_name = store.id_to_impl_name[service_id]
        svc_data = store.services[impl_name]
        name = svc_data['name']
        service_class = svc_data['service_class']
        is_internal = getattr(service_class, 'is_internal', name.startswith('zato.'))

        internal_del = is_boolean(self.server.fs_server_config.misc.internal_services_may_be_deleted)

        if is_internal and not internal_del:
            msg = "Can't delete service:[{}], it's an internal one and internal_services_may_be_deleted is not True".format(name)
            raise ZatoException(self.cid, msg)

        store._delete_service_data(name)

        msg = {
            'action': SERVICE.DELETE.value,
            'id': self.request.input.id,
            'name': name,
            'impl_name': impl_name,
            'is_internal': is_internal,
        }
        self.broker_client.publish(msg)

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
        service_id = int(self.request.input.id)
        channel_type = self.request.input.channel_type

        out = []

        if channel_type in ('plain_http', 'soap'):
            channel_data = self.server.worker_store.request_dispatcher.url_data.channel_data
            for item in channel_data:
                if item.get('connection') != CONNECTION.CHANNEL:
                    continue

                item_service_id = item.get('service_id')
                if item_service_id and int(item_service_id) == service_id:
                    if channel_type == 'soap' and not item.get('soap_version'):
                        continue
                    if channel_type == 'plain_http' and item.get('soap_version'):
                        continue
                    out.append(Bunch(id=item['id'], name=item['name']))

        self.response.payload[:] = out

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
        name = self.request.input.get('name') or ''
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

    def get_data(self):

        out = []

        if not 'include_internal' in self.request.input:
            include_internal = True
        else:
            include_internal = self.request.input.get('include_internal')

        needs_details = self.request.input.needs_details
        store = self.server.service_store

        service_id = self.request.input.get('id')
        if service_id:
            service_id = int(service_id)
            impl_name = store.id_to_impl_name.get(service_id)
            if impl_name:
                items_to_check = [(service_id, impl_name)]
            else:
                items_to_check = []
        else:
            items_to_check = list(store.id_to_impl_name.items())

        for svc_id, impl_name in items_to_check:
            svc_data = store.services.get(impl_name)
            if not svc_data:
                continue

            name = svc_data['name']
            service_class = svc_data['service_class']
            is_internal = getattr(service_class, 'is_internal', name.startswith('zato.'))

            if not include_internal and is_internal:
                continue

            deployment = store.get_deployment_info(impl_name)
            fs_location = deployment.get('fs_location') or svc_data.get('path', '')

            _item = {
                'server_id': self.server.id,
                'server_name': self.server.name,
                'service_id': svc_id,
                'service_name': name,
                'fs_location': fs_location,
                'file_name': os.path.basename(fs_location) if fs_location else '',
                'line_number': deployment.get('line_number', 0),
            }

            if needs_details:
                _item['details'] = deployment
            out.append(_item)

        return out

    def handle(self):
        self.response.payload[:] = self.get_data()

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

    def handle(self):
        store = self.server.service_store
        name = self.request.input.name

        impl_name = store.name_to_impl_name.get(name)
        if not impl_name:
            return

        svc_data = store.services[impl_name]
        service_id = store.impl_name_to_id.get(impl_name, 0)
        source_code = svc_data.get('source_code', '')

        if isinstance(source_code, str):
            source_bytes = source_code.encode('utf-8')
        else:
            source_bytes = source_code

        self.response.payload.service_id = service_id
        self.response.payload.server_name = self.server.name
        self.response.payload.source = b64encode(source_bytes) if source_bytes else None
        self.response.payload.source_path = svc_data.get('path', '')
        self.response.payload.source_hash = sha256(source_bytes).hexdigest() if source_bytes else ''
        self.response.payload.source_hash_method = 'SHA-256'

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

        # Service name is given in URL path
        service_name = self.request.http.params.service_name

        # Are we invoking a Zato built-in service or a user-defined one?
        is_internal = service_name.startswith(_internal) # type: bool

        # Before invoking a service that is potentially internal we need to confirm
        # that our channel can be used for such invocations.
        if is_internal:
            if self.channel.name not in self.server.fs_server_config.misc.service_invoker_allow_internal:
                msg = 'Service `%s` could not be invoked; channel `%s` not among `%s` (service_invoker_allow_internal)'
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
                http_environ={'HTTP_METHOD':self.request.http.method},
                zato_response_headers_container=zato_response_headers_container
                )

            # All internal services wrap their responses in top-level elements that we need to shed here ..
            if is_internal and response:
                meta = response.pop('_meta', None)
                top_level = list(iterkeys(response))[0]
                response = response[top_level]
                if meta:
                    response = {'response': response, '_meta': meta}

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
