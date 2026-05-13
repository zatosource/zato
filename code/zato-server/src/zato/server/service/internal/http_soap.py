# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from time import time
from traceback import format_exc

# Zato
from zato.common.api import CONNECTION, DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, \
     Groups, HTTP_SOAP_SERIALIZATION_TYPE, MISC, PARAMS_PRIORITY, query_parameters, SEC_DEF_TYPE, \
     URL_PARAMS_PRIORITY, URL_TYPE, ZATO_NONE
from zato.common.broker_message import CHANNEL, OUTGOING
from zato.common.exception import ServiceMissingException
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import Cluster, HTTPSOAP, SecurityBase, Service
from zato.common.rate_limiting.cidr import SlottedCIDRRule
from zato.common.odb.query import http_soap, http_soap_list
from zato.common.util.api import as_bool
from zato.common.util.sql import elems_with_opaque, get_dict_with_opaque, get_security_by_id, parse_instance_opaque_attr, \
     set_instance_opaque_attrs
from zato.server.connection.http_soap import BadRequest
from zato.server.service import AsIs, Boolean, Integer
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strdict, strintdict

# ################################################################################################################################
# ################################################################################################################################

_GetList_Optional = ('include_wrapper', 'cluster_id', 'connection', 'transport', 'data_format', 'needs_security_group_names')

# ################################################################################################################################
# ################################################################################################################################

class _HTTPSOAPService:
    """ A common class for various HTTP/SOAP-related services.
    """
    def notify_server(self, params, action):
        """ Notify the server of new or updated parameters.
        """
        params['action'] = action
        self.config_dispatcher.publish(params)

    def _handle_security_info(self, session, security_id, connection, transport):
        """ First checks whether the security type is correct for the given
        connection type. If it is, returns a dictionary of security-related information.
        """
        info = {'security_id': None, 'security_name':None, 'sec_type':None}

        if security_id:

            sec_def = session.query(SecurityBase.name, SecurityBase.sec_type).\
                filter(SecurityBase.id==security_id).\
                one()

            if connection == 'outgoing':

                if transport == URL_TYPE.PLAIN_HTTP and \
                   sec_def.sec_type not in (SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.APIKEY, SEC_DEF_TYPE.OAUTH, SEC_DEF_TYPE.NTLM):
                    raise Exception('Unsupported sec_type `{}`'.format(sec_def.sec_type))

            info['security_id'] = security_id
            info['security_name'] = sec_def.name
            info['sec_type'] = sec_def.sec_type

        return info

# ################################################################################################################################

class _BaseGet(AdminService):
    """ Base class for services returning information about HTTP/SOAP objects.
    """
    output = 'id', 'name', 'is_active', 'is_internal', 'url_path', \
        '-service_id', '-service_name', '-security_id', '-security_name', '-sec_type', \
        '-method', '-soap_action', '-soap_version', '-data_format', '-host', '-ping_method', '-pool_size', \
        '-merge_url_params_req', '-url_params_pri', '-params_pri', '-serialization_type', '-timeout', \
        '-content_type', \
        '-content_encoding', Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', \
        '-data_encoding', '-username', '-is_wrapper', '-wrapper_type', AsIs('-security_groups'), '-security_group_count', \
        '-security_group_member_count', '-needs_security_group_names', Boolean('-validate_tls'), '-gateway_service_list'

# ################################################################################################################################

    def _get_security_groups_info(self, item:'any_', security_groups_member_count:'strintdict') -> 'strdict':

        # Our response to produce
        out:'strdict' = {
            'group_count': 0,
            'member_count': 0,
        }

        if security_groups := item.get('security_groups'):
            for group_id in security_groups:
                member_count = security_groups_member_count.get(group_id) or 0
                out['member_count'] += member_count
                out['group_count'] += 1

        # .. now, return the response to our caller.
        return out

# ################################################################################################################################

class Get(_BaseGet):
    """ Returns information about an individual HTTP/SOAP object by its ID.
    """
    input = '-cluster_id', '-id', '-name'

    def handle(self):
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id
        with closing(self.odb.session()) as session:
            self.request.input.require_any('id', 'name')
            item = http_soap(session, cluster_id, self.request.input.id, self.request.input.name)
            out = get_dict_with_opaque(item)
            self.response.payload = out

# ################################################################################################################################

class GetList(_BaseGet):
    """ Returns a list of HTTP/SOAP connections.
    """
    _filter_by = HTTPSOAP.name,

    input = '-include_wrapper', '-cluster_id', '-connection', '-transport', '-data_format', '-needs_security_group_names', \
        *query_parameters
    output = 'id', 'name', 'is_active', 'is_internal', 'url_path', \
        '-service_id', '-service_name', '-security_id', '-security_name', '-sec_type', \
        '-method', '-soap_action', '-soap_version', '-data_format', '-host', '-ping_method', '-pool_size', \
        '-merge_url_params_req', '-url_params_pri', '-params_pri', '-serialization_type', '-timeout', \
        '-content_type', \
        '-content_encoding', Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', \
        '-data_encoding', '-username', '-is_wrapper', '-wrapper_type', AsIs('-security_groups'), '-security_group_count', \
        '-security_group_member_count', '-needs_security_group_names', Boolean('-validate_tls'), '-gateway_service_list', \
        '-connection', '-transport'

    def get_data(self, session):

        # Local aliases
        out:'anylist' = []
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id
        needs_security_group_names = self.request.input.get('needs_security_group_names') or False
        include_wrapper = self.request.input.get('include_wrapper') or False
        should_ignore_wrapper = not include_wrapper

        # Get information about security groups which may be used later on
        security_groups_member_count = self.invoke('zato.groups.get-member-count', group_type=Groups.Type.API_Clients)

        if needs_security_group_names:
            all_security_groups = self.invoke('zato.groups.get-list', group_type=Groups.Type.API_Clients)
        else:
            all_security_groups = []

        # Obtain the basic result ..
        result = self._search(http_soap_list, session, cluster_id,
            self.request.input.connection, self.request.input.transport,
            as_bool(self.server.fs_server_config.misc.return_internal_objects),
            self.request.input.get('data_format'),
            False,
            )

        # .. extract all the opaque elements ..
        data:'anylist' = elems_with_opaque(result)

        # .. go through everything we have so far ..
        for item in data:

            # .. build a dictionary of information about groups ..
            security_groups_for_item_info = self._get_security_groups_info(item, security_groups_member_count)

            item['security_group_count'] = security_groups_for_item_info['group_count']
            item['security_group_member_count'] = security_groups_for_item_info['member_count']

            # .. optionally, we may need to turn security group IDs into their names ..
            if needs_security_group_names:
                if security_groups_for_item := item.get('security_groups'):
                    new_security_groups = []
                    for item_group_id in security_groups_for_item:
                        for group in all_security_groups:
                            if item_group_id == group['id']:
                                new_security_groups.append(group['name'])
                                break
                    item['security_groups'] = sorted(new_security_groups)

            # .. ignore wrapper elements if told do ..
            if should_ignore_wrapper and item.get('is_wrapper'):
                continue

            # .. if we are here, it means that this element is to be returned ..
            out.append(item)

        # .. now, return the result to our caller.
        return out

    def handle(self):
        with closing(self.odb.session()) as session:
            data = self.get_data(session)
            self.response.payload[:] = data

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(AdminService, _HTTPSOAPService):

# ################################################################################################################################

    def _raise_error(self, name, url_path, http_accept, http_method, soap_action, source):
        msg = 'Such a channel already exists ({}); url_path:`{}`, http_accept:`{}`, http_method:`{}`, soap_action:`{}` (src:{})'
        raise Exception(msg.format(name, url_path, http_accept, http_method, soap_action, source))

# ################################################################################################################################

    def ensure_channel_is_unique(self, session, url_path, http_accept, http_method, soap_action, cluster_id):
        existing_ones = session.query(HTTPSOAP).\
            filter(HTTPSOAP.cluster_id==cluster_id).\
            filter(HTTPSOAP.url_path==url_path).\
            filter(HTTPSOAP.soap_action==soap_action).\
            filter(HTTPSOAP.connection==CONNECTION.CHANNEL).\
            all()

        # At least one channel with this kind of basic information already exists
        # but it is possible that it requires different HTTP headers (e.g. Accept, Method)
        # so we need to check each one manually.
        if existing_ones:
            for item in existing_ones:
                opaque = parse_instance_opaque_attr(item)
                item_http_accept = opaque.get('http_accept')

                # Raise an exception if the existing channel's method is equal to ours
                # but only if they use different Accept headers.
                if http_method:
                    if item.method == http_method:
                        if item_http_accept == http_accept:
                            self._raise_error(item.name, url_path, http_accept, http_method, soap_action, 'chk1')

                # Similar, but from the Accept header's perspective
                if item_http_accept == http_accept:
                    if item.method == http_method:
                        self._raise_error(item.name, url_path, http_accept, http_method, soap_action, 'chk2')

# ################################################################################################################################

    def _preprocess_security_groups(self, input):

        # This will contain only IDs
        new_input_security_groups = []

        # Security groups are optional
        if input_security_groups := input.get('security_groups'):

            # Get information about security groups which is need to turn group names into group IDs
            existing_security_groups = self.invoke('zato.groups.get-list', group_type=Groups.Type.API_Clients)

            for input_group in input_security_groups:
                group_id = None
                try:
                    input_group = int(input_group)
                except ValueError:
                    for existing_group in existing_security_groups:
                        if input_group == existing_group['name']:
                            group_id = existing_group['id']
                            break
                    else:
                        raise Exception(f'Could not find ID for group `{input_group}`')
                else:
                    group_id = input_group
                finally:
                    if group_id:
                        new_input_security_groups.append(group_id)

        # Return what we have to our caller
        return new_input_security_groups

# ################################################################################################################################

    def _get_service_from_input(self, session, input):

        service = session.query(Service).\
            filter(Cluster.id==input.cluster_id).\
            filter(Service.cluster_id==Cluster.id)

        if input.service:
            service = service.filter(Service.name==input.service)
        elif input.service_id:
            service = service.filter(Service.id==input.service_id)
        else:
            raise Exception('Either service or service_id is required on input')

        service = service.first()

        if not service:
            msg = 'Service `{}` does not exist in this cluster'.format(input.service)
            self.logger.info(msg)
            raise ServiceMissingException(msg)
        else:
            return service

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    """ Creates a new HTTP/SOAP connection.
    """
    input = 'name', 'url_path', 'connection', \
        '-service', '-service_id', AsIs('-security_id'), '-method', '-soap_action', '-soap_version', '-data_format', \
        '-host', '-ping_method', '-pool_size', Boolean('-merge_url_params_req'), '-url_params_pri', '-params_pri', \
        '-serialization_type', '-timeout', '-content_type', \
        '-content_encoding', Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', '-data_encoding', \
        '-is_active', '-transport', '-is_internal', '-cluster_id', \
        '-is_wrapper', '-wrapper_type', '-username', '-password', AsIs('-security_groups'), Boolean('-validate_tls'), \
        '-gateway_service_list'
    output = 'id', 'name', '-url_path'

    def handle(self):

        # For later use
        skip_opaque = []

        input = self.request.input
        input.security_id = input.security_id if input.security_id not in (ZATO_NONE, ) else None
        input.soap_action = input.soap_action if input.soap_action else ''
        input.timeout = input.get('timeout') or MISC.DEFAULT_HTTP_TIMEOUT
        input.security_groups = self._preprocess_security_groups(input)

        input.is_active   = input.get('is_active',   True)
        input.is_internal = input.get('is_internal', False)

        input.transport   = input.get('transport')   or URL_TYPE.PLAIN_HTTP
        input.cluster_id  = input.get('cluster_id')  or self.server.cluster_id
        input.data_format = input.get('data_format') or ''

        input.data_encoding = input.get('data_encoding') or 'utf-8'

        # Remove extra whitespace
        input_name = input.name
        input_host = input.host
        input_url_path = input.url_path
        input_ping_method = input.get('ping_method')
        input_content_type = input.get('content_type')

        if input_name:
            input.name = input_name.strip()

        if input_host:
            input.host = input_host.strip()

        if input_url_path:
            input.url_path = input_url_path.strip()

        if input_ping_method:
            input.ping_method = input_ping_method.strip() or DEFAULT_HTTP_PING_METHOD

        if input_content_type:
            input.content_type = input_content_type.strip()

        if input.content_encoding and input.content_encoding != 'gzip':
            raise Exception('Content encoding must be empty or equal to `gzip`')

        with closing(self.odb.session()) as session:
            existing_one = session.query(HTTPSOAP.id).\
                filter(HTTPSOAP.cluster_id==input.cluster_id).\
                filter(HTTPSOAP.name==input.name).\
                filter(HTTPSOAP.connection==input.connection).\
                filter(HTTPSOAP.transport==input.transport).\
                first()

            if existing_one:
                raise Exception('An object of that name `{}` already exists in this cluster'.format(input.name))

            if input.connection == CONNECTION.CHANNEL:
                service = self._get_service_from_input(session, input)
            else:
                service = None

            # Will raise exception if the security type doesn't match connection
            # type and transport
            sec_info = self._handle_security_info(session, input.security_id,
                input.connection, input.transport)

            # Make sure this combination of channel parameters does not exist already
            if input.connection == CONNECTION.CHANNEL:
                self.ensure_channel_is_unique(session,
                    input.url_path, input.http_accept, input.method, input.soap_action, input.cluster_id)

            try:

                item = self._new_zato_instance_with_cluster(HTTPSOAP)
                item.connection = input.connection
                item.transport = input.transport
                item.is_internal = input.is_internal
                item.name = input.name
                item.is_active = input.is_active
                item.host = input.host
                item.url_path = input.url_path
                item.method = input.method
                item.soap_action = input.soap_action.strip()
                item.soap_version = input.soap_version or None
                item.data_format = input.data_format
                item.service = service
                item.ping_method = input.ping_method
                item.pool_size = input.get('pool_size') or DEFAULT_HTTP_POOL_SIZE
                item.merge_url_params_req = input.get('merge_url_params_req') or True
                item.url_params_pri = input.get('url_params_pri') or URL_PARAMS_PRIORITY.DEFAULT
                item.params_pri = input.get('params_pri') or PARAMS_PRIORITY.DEFAULT
                item.serialization_type = input.get('serialization_type') or HTTP_SOAP_SERIALIZATION_TYPE.DEFAULT.id
                item.timeout = input.timeout
                item.content_type = input.content_type
                item.content_encoding = input.content_encoding
                item.is_wrapper = bool(input.is_wrapper)
                item.wrapper_type = input.wrapper_type

                if input.username:
                    item.username = input.username
                else:
                    skip_opaque.append('username')

                if input.password:
                    item.password = input.password
                else:
                    skip_opaque.append('password')

                if input.security_id:
                    item.security = get_security_by_id(session, input.security_id)
                else:
                    input.security_id = None # To ensure that SQLite does not reject ''

                # Opaque attributes
                set_instance_opaque_attrs(item, input, skip=skip_opaque)

                session.add(item)
                session.commit()

                if input.connection == CONNECTION.CHANNEL:
                    input.impl_name = service.impl_name
                    input.service_id = service.id
                    input.service_name = service.name

                input.id = item.id
                input.update(sec_info)

                if input.connection == CONNECTION.CHANNEL:
                    action = CHANNEL.HTTP_SOAP_CREATE_EDIT.value
                else:
                    action = OUTGOING.HTTP_SOAP_CREATE_EDIT.value
                self.notify_server(input, action)

                self.response.payload.id = item.id
                self.response.payload.name = item.name
                self.response.payload.url_path = item.url_path

            except Exception:
                self.logger.error('Object could not be created, e:`%s', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Edit(_CreateEdit):
    """ Updates an HTTP/SOAP connection.
    """
    input = 'id', 'name', 'url_path', 'connection', \
        '-service', '-service_id', AsIs('-security_id'), '-method', '-soap_action', '-soap_version', \
        '-data_format', '-host', '-ping_method', '-pool_size', Boolean('-merge_url_params_req'), '-url_params_pri', \
        '-params_pri', '-serialization_type', '-timeout', '-content_type', \
        '-content_encoding', Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', '-data_encoding', \
        '-cluster_id', '-is_active', '-transport', \
        '-is_wrapper', '-wrapper_type', '-username', '-password', AsIs('-security_groups'), Boolean('-validate_tls'), \
        '-gateway_service_list'
    output = '-id', '-name'

    def handle(self):

        # For later use
        skip_opaque = []

        input = self.request.input
        input.security_id  = input.security_id if input.security_id not in (ZATO_NONE,) else None
        input.soap_action  = input.soap_action if input.soap_action else ''
        input.timeout      = input.get('timeout') or MISC.DEFAULT_HTTP_TIMEOUT
        input.security_groups = self._preprocess_security_groups(input)

        input.is_active   = input.get('is_active',   True)
        input.is_internal = input.get('is_internal', False)

        input.transport   = input.get('transport')   or URL_TYPE.PLAIN_HTTP
        input.cluster_id  = input.get('cluster_id')  or self.server.cluster_id
        input.data_format = input.get('data_format') or ''

        input.data_encoding = input.get('data_encoding') or 'utf-8'

        # Remove extra whitespace
        input_name = input.name
        input_host = input.host
        input_url_path = input.url_path
        input_ping_method = input.get('ping_method')
        input_content_type = input.get('content_type')

        if input_name:
            input.name = input_name.strip()

        if input_host:
            input.host = input_host.strip()

        if input_url_path:
            input.url_path = input_url_path.strip()

        if input_ping_method:
            input.ping_method = input_ping_method.strip() or DEFAULT_HTTP_PING_METHOD

        if input_content_type:
            input.content_type = input_content_type.strip()

        if input.content_encoding and input.content_encoding != 'gzip':
            raise Exception('Content encoding must be empty or equal to `gzip`')

        with closing(self.odb.session()) as session:

            existing_one = session.query(
                HTTPSOAP.id,
                HTTPSOAP.url_path,
                ).\
                filter(HTTPSOAP.cluster_id==input.cluster_id).\
                filter(HTTPSOAP.id!=input.id).\
                filter(HTTPSOAP.name==input.name).\
                filter(HTTPSOAP.connection==input.connection).\
                filter(HTTPSOAP.transport==input.transport).\
                first()

            if existing_one:
                if input.connection == CONNECTION.CHANNEL:
                    object_type = 'channel'
                else:
                    object_type = 'connection'
                msg = 'A {} of that name:`{}` already exists in this cluster; path: `{}` (id:{})'
                raise Exception(msg.format(object_type, input.name, existing_one.url_path, existing_one.id))

            if input.connection == CONNECTION.CHANNEL:
                service = self._get_service_from_input(session, input)
            else:
                service = None

            # Will raise exception if the security type doesn't match connection
            # type and transport
            sec_info = self._handle_security_info(session, input.security_id, input.connection, input.transport)

            try:
                item = session.query(HTTPSOAP).filter_by(id=input.id).one()

                opaque = parse_instance_opaque_attr(item)

                old_name = item.name
                old_url_path = item.url_path
                old_soap_action = item.soap_action
                old_http_method = item.method
                old_http_accept = opaque.get('http_accept')

                item.name = input.name
                item.is_active = input.is_active
                item.host = input.host
                item.url_path = input.url_path
                item.security_id = input.security_id or None # So that SQLite does not reject ''
                item.connection = input.connection
                item.transport = input.transport
                item.cluster_id = input.cluster_id
                item.method = input.method
                item.soap_action = input.soap_action
                item.soap_version = input.soap_version or None
                item.data_format = input.data_format
                item.service = service
                item.ping_method = input.ping_method
                item.pool_size = input.get('pool_size') or DEFAULT_HTTP_POOL_SIZE
                item.merge_url_params_req = input.get('merge_url_params_req') or False
                item.url_params_pri = input.get('url_params_pri') or URL_PARAMS_PRIORITY.DEFAULT
                item.params_pri = input.get('params_pri') or PARAMS_PRIORITY.DEFAULT
                item.serialization_type = input.get('serialization_type') or HTTP_SOAP_SERIALIZATION_TYPE.DEFAULT.id
                item.timeout = input.get('timeout')
                item.content_type = input.content_type
                item.content_encoding = input.content_encoding
                item.is_wrapper = bool(input.is_wrapper)
                item.wrapper_type = input.wrapper_type

                if input.username:
                    item.username = input.username
                else:
                    skip_opaque.append('username')

                if input.password:
                    item.password = input.password
                else:
                    skip_opaque.append('password')

                # Opaque attributes
                set_instance_opaque_attrs(item, input, skip=skip_opaque)

                session.add(item)
                session.commit()

                if input.connection == CONNECTION.CHANNEL:
                    input.impl_name = service.impl_name
                    input.service_id = service.id
                    input.service_name = service.name
                    input.merge_url_params_req = item.merge_url_params_req
                    input.url_params_pri = item.url_params_pri
                    input.params_pri = item.params_pri

                else:
                    input.ping_method = item.ping_method
                    input.pool_size = item.pool_size

                input.is_internal = item.is_internal
                input.old_name = old_name
                input.old_url_path = old_url_path
                input.old_soap_action = old_soap_action
                input.old_http_method = old_http_method
                input.old_http_accept = old_http_accept
                input.update(sec_info)

                if input.connection == CONNECTION.CHANNEL:
                    action = CHANNEL.HTTP_SOAP_CREATE_EDIT.value
                else:
                    action = OUTGOING.HTTP_SOAP_CREATE_EDIT.value

                self.notify_server(input, action)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Object could not be updated, e:`%s`', format_exc())
                session.rollback()

                raise

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

        with closing(self.odb.session()) as session:
            try:
                query = session.query(HTTPSOAP)

                if input_id:
                    query = query.\
                        filter(HTTPSOAP.id==input_id)

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

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(HTTPSOAP).filter_by(id=self.request.input.id).one()
            config_dict = getattr(self.outgoing, item.transport)
            self.response.payload.id = self.request.input.id

            try:
                result = config_dict.get(item.name).ping(self.cid, ping_path=self.request.input.ping_path)
                is_success = True
            except Exception as e:
                result = e.args[0]
                is_success = False
            finally:
                self.response.payload.info = result
                self.response.payload.is_success = is_success

# ################################################################################################################################

class GetURLSecurity(AdminService):
    """ Returns a JSON document describing the security configuration of all Zato channels.
    """
    def handle(self):
        response = {}
        response['url_sec'] = sorted(self.server.config_manager.request_handler.security.url_sec.items())
        response['plain_http_handler.http_soap'] = sorted(self.server.config_manager.request_handler.plain_http_handler.http_soap.items())
        response['soap_handler.http_soap'] = sorted(self.server.config_manager.request_handler.soap_handler.http_soap.items())
        self.response.payload = dumps(response, sort_keys=True, indent=4)
        self.response.content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

def _set_invoke_response(service, result):
    service.response.payload.status_code = result['status_code']
    service.response.payload.response_body = result['response_body']
    service.response.payload.response_time = result['response_time']

# ################################################################################################################################

def _parse_key_value_params(text):
    if not text or not text.strip():
        return {}

    result = {}
    for sep in ('&', '\n'):
        if sep in text:
            for pair in text.split(sep):
                pair = pair.strip()
                if '=' in pair:
                    key, _, value = pair.partition('=')
                    result[key.strip()] = value.strip()
            return result

    if '=' in text:
        key, _, value = text.partition('=')
        result[key.strip()] = value.strip()

    return result

# ################################################################################################################################
# ################################################################################################################################

class InvokeChannel(AdminService):

    name = 'zato.http-soap.invoke-channel'
    input = 'id', '-payload', '-request_method', '-query_params', '-path_params'
    output = '-status_code', '-response_body', '-response_time'

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(HTTPSOAP).filter_by(id=self.request.input.id).first()
            if not item:
                raise Exception('REST channel `{}` not found'.format(self.request.input.id))

            channel_config = {
                'url_path': item.url_path,
                'security_id': item.security_id,
            }
            sec_config = self._get_security_config(session, item.security_id)

        url_path = self._resolve_url_path(channel_config)
        wrapper = self._build_temp_wrapper(channel_config, sec_config, url_path)

        try:
            result = self._invoke_wrapper(wrapper)
        finally:
            wrapper.session.close()

        _set_invoke_response(self, result)

    def _get_security_config(self, session, security_id):
        if not security_id:
            return {'sec_type': None, 'username': None, 'password': None, 'orig_username': None}

        sec_def = session.query(SecurityBase).filter_by(id=security_id).first()
        if not sec_def:
            return {'sec_type': None, 'username': None, 'password': None, 'orig_username': None}

        username = getattr(sec_def, 'username', '') or ''
        password = getattr(sec_def, 'password', '') or ''
        if password and hasattr(self.server, 'decrypt'):
            try:
                password = self.server.decrypt(password)
            except Exception:
                pass

        return {
            'sec_type': sec_def.sec_type,
            'username': username,
            'password': password,
            'orig_username': username,
        }

    def _resolve_url_path(self, channel_config):
        url_path = channel_config.get('url_path', '/')
        path_params = _parse_key_value_params(self.request.input.get('path_params', ''))
        if path_params:
            try:
                url_path = url_path.format(**path_params)
            except (KeyError, ValueError):
                pass
        return url_path

    def _build_temp_wrapper(self, channel_config, sec_config, url_path):
        from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper

        port = getattr(self.server, 'port', 17010)
        method = self.request.input.get('request_method', '') or 'POST'

        wrapper_config = {
            'id': 'temp-invoke-{}'.format(self.cid),
            'is_active': True,
            'method': method,
            'data_format': 'json',
            'name': 'temp-invoke-channel-{}'.format(self.cid),
            'transport': 'plain_http',
            'address_host': 'http://127.0.0.1:{}'.format(port),
            'address_url_path': url_path,
            'soap_action': '',
            'soap_version': None,
            'ping_method': 'HEAD',
            'pool_size': 1,
            'serialization_type': 'json',
            'timeout': 90,
            'content_type': None,
            'validate_tls': False,
            'security_name': None,
            'security_id': None,
            'sec_type': sec_config.get('sec_type'),
            'username': sec_config.get('username'),
            'password': sec_config.get('password'),
            'password_type': None,
            'orig_username': sec_config.get('orig_username'),
            'salt': None,
        }

        return HTTPSOAPWrapper(self.server, wrapper_config)

    def _invoke_wrapper(self, wrapper):
        method = self.request.input.get('request_method', '') or 'POST'
        payload = self.request.input.get('payload', '') or ''
        query_params = _parse_key_value_params(self.request.input.get('query_params', ''))

        start = time()
        try:
            response = wrapper.http_request(method, self.cid, data=payload, params=query_params or None)
            elapsed = time() - start
            return {
                'status_code': response.status_code,
                'response_body': response.text,
                'response_time': '{:.1f}ms'.format(elapsed * 1000),
            }
        except Exception as e:
            elapsed = time() - start
            return {
                'status_code': 0,
                'response_body': str(e),
                'response_time': '{:.1f}ms'.format(elapsed * 1000),
            }

# ################################################################################################################################
# ################################################################################################################################

class InvokeOutconn(AdminService):

    name = 'zato.http-soap.invoke-outconn'
    input = 'id', '-payload', '-request_method', '-query_params', '-path_params'
    output = '-status_code', '-response_body', '-response_time'

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(HTTPSOAP).filter_by(id=self.request.input.id).first()
            if not item:
                raise Exception('REST outgoing connection `{}` not found'.format(self.request.input.id))
            outconn_name = item.name

        method = self.request.input.get('request_method', '') or 'POST'
        payload = self.request.input.get('payload', '') or ''
        params = self._build_params()

        result = self._invoke_outconn(outconn_name, method, payload, params)
        _set_invoke_response(self, result)

    def _build_params(self):
        params = {}
        path_params = _parse_key_value_params(self.request.input.get('path_params', ''))
        query_params = _parse_key_value_params(self.request.input.get('query_params', ''))
        params.update(path_params)
        params.update(query_params)
        return params

    def _invoke_outconn(self, outconn_name, method, payload, params):
        config_item = self.outgoing.plain_http.get(outconn_name)
        if not config_item:
            raise Exception('Outgoing REST connection wrapper `{}` not found'.format(outconn_name))

        conn = config_item.conn
        start = time()

        try:
            response = conn.http_request(method, self.cid, data=payload, params=params)
            elapsed = time() - start
            return {
                'status_code': response.status_code,
                'response_body': response.text,
                'response_time': '{:.1f}ms'.format(elapsed * 1000),
            }
        except Exception as e:
            elapsed = time() - start
            return {
                'status_code': 0,
                'response_body': str(e),
                'response_time': '{:.1f}ms'.format(elapsed * 1000),
            }

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingSave(AdminService):

    name = 'zato.http-soap.rate-limiting.save'
    input = 'id', 'rules_json'

    def handle(self) -> 'None':

        input = self.request.input
        channel_id = int(input['id'])
        rules_json = input['rules_json']

        self.logger.info('RateLimitingSave; channel_id:%s, rules_json:%s', channel_id, rules_json)

        # Parse the JSON string into a list of rule dicts ..
        rule_dicts:'anylist' = loads(rules_json)

        self.logger.info('RateLimitingSave; channel_id:%s, parsed %s rule_dicts:%s', channel_id, len(rule_dicts), rule_dicts)

        # .. validate each rule by running it through from_dict ..
        for item in rule_dicts:
            SlottedCIDRRule.from_dict(item)

        with closing(self.odb.session()) as session:

            # Read the current row ..
            row = session.query(HTTPSOAP).filter_by(id=channel_id).one()

            # .. parse the existing opaque1 or start with an empty dict ..
            if row.opaque1:
                opaque = loads(row.opaque1)
            else:
                opaque = {}

            # .. set the rate_limiting key ..
            opaque['rate_limiting'] = rule_dicts

            # .. write it back ..
            row.opaque1 = dumps(opaque)
            session.add(row)
            session.commit()

        self.logger.info('RateLimitingSave; channel_id:%s, ODB committed', channel_id)

        # After ODB commit, notify the config dispatcher so the in-process manager picks up the change
        params = {
            'action': CHANNEL.HTTP_SOAP_RATE_LIMITING_EDIT.value,
            'id': channel_id,
            'rule_dicts': rule_dicts,
        }
        self.config_dispatcher.publish(params)

        self.logger.info('RateLimitingSave; channel_id:%s, config event published', channel_id)

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingGet(AdminService):

    name = 'zato.http-soap.rate-limiting.get'
    input = 'id'

    def handle(self):

        channel_id = int(self.request.input['id'])

        with closing(self.odb.session()) as session:

            # Read the current row ..
            item = session.query(HTTPSOAP).filter_by(id=channel_id).one()

            # .. parse existing opaque1 ..
            opaque = loads(item.opaque1) if item.opaque1 else {}

            # .. extract rate_limiting, defaulting to an empty list ..
            rate_limiting = opaque.get('rate_limiting', [])

        self.response.payload = {'rate_limiting': rate_limiting}

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingClearCounters(AdminService):

    name = 'zato.http-soap.rate-limiting.clear-counters'
    input = 'id', 'rule_index'

    def handle(self):

        channel_id = int(self.request.input['id'])
        rule_index = int(self.request.input['rule_index'])
        key_prefix = f'rest{channel_id}:'

        self.server.rate_limiting_manager.clear_rule_counters(channel_id, rule_index, key_prefix)

# ################################################################################################################################
