# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# Paste
from paste.util.converters import asbool

# Zato
from zato.common.api import CONNECTION, DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, \
     HTTP_SOAP_SERIALIZATION_TYPE, MISC, PARAMS_PRIORITY, SEC_DEF_TYPE, URL_PARAMS_PRIORITY, URL_TYPE, \
     ZATO_NONE, ZATO_SEC_USE_RBAC
from zato.common.broker_message import CHANNEL, OUTGOING
from zato.common.exception import ZatoException
from zato.common.json_internal import dumps
from zato.common.odb.model import Cluster, HTTPSOAP, SecurityBase, Service, TLSCACert, to_json
from zato.common.odb.query import cache_by_id, http_soap, http_soap_list
from zato.common.rate_limiting import DefinitionParser
from zato.common.util.sql import elems_with_opaque, get_dict_with_opaque, get_security_by_id, parse_instance_opaque_attr, \
     set_instance_opaque_attrs
from zato.server.service import Boolean, Integer, List
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

class _HTTPSOAPService(object):
    """ A common class for various HTTP/SOAP-related services.
    """
    def notify_worker_threads(self, params, action):
        """ Notify worker threads of new or updated parameters.
        """
        params['action'] = action
        self.broker_client.publish(params)

    def _validate_tls(self, input, sec_info):
        if sec_info['sec_type'] == SEC_DEF_TYPE.TLS_KEY_CERT:
            if not input.get('sec_tls_ca_cert_id'):
                raise ZatoException(self.cid, 'TLS CA certs is a required field if TLS keys/certs are used')

    def _handle_security_info(self, session, security_id, connection, transport):
        """ First checks whether the security type is correct for the given
        connection type. If it is, returns a dictionary of security-related information.
        """
        info = {'security_name':None, 'sec_type':None}

        if security_id:

            sec_def = session.query(SecurityBase.name, SecurityBase.sec_type).\
                filter(SecurityBase.id==security_id).\
                one()

            # Outgoing plain HTTP connections may use HTTP Basic Auth only,
            # outgoing SOAP connections may use either WSS or HTTP Basic Auth.
            if connection == 'outgoing':

                if transport == URL_TYPE.PLAIN_HTTP and \
                   sec_def.sec_type not in(SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.TLS_KEY_CERT, SEC_DEF_TYPE.APIKEY):
                    raise Exception('Unsupported sec_type `{}`'.format(sec_def.sec_type))

                elif transport == URL_TYPE.SOAP and sec_def.sec_type \
                     not in(SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.NTLM, SEC_DEF_TYPE.WSS):

                    raise Exception('Security type must be HTTP Basic Auth, NTLM or WS-Security, not `{}`'.format(
                        sec_def.sec_type))

            info['security_name'] = sec_def.name
            info['sec_type'] = sec_def.sec_type

        return info

# ################################################################################################################################

class _BaseGet(AdminService):
    """ Base class for services returning information about HTTP/SOAP objects.
    """
    class SimpleIO:
        output_required = 'id', 'name', 'is_active', 'is_internal', 'url_path'
        output_optional = 'service_id', 'service_name', 'security_id', 'security_name', 'sec_type', \
            'method', 'soap_action', 'soap_version', 'data_format', 'host', 'ping_method', 'pool_size', 'merge_url_params_req', \
            'url_params_pri', 'params_pri', 'serialization_type', 'timeout', 'sec_tls_ca_cert_id', Boolean('has_rbac'), \
            'content_type', Boolean('sec_use_rbac'), 'cache_id', 'cache_name', Integer('cache_expiry'), 'cache_type', \
            'content_encoding', Boolean('match_slash'), 'http_accept', List('service_whitelist'), 'is_rate_limit_active', \
                'rate_limit_type', 'rate_limit_def', Boolean('rate_limit_check_parent_def'), \
                'hl7_version', 'json_path', 'should_parse_on_input', 'should_validate', 'should_return_errors', \
                'data_encoding'

# ################################################################################################################################

class Get(_BaseGet):
    """ Returns information about an individual HTTP/SOAP object by its ID.
    """
    class SimpleIO(_BaseGet.SimpleIO):
        request_elem = 'zato_http_soap_get_request'
        response_elem = 'zato_http_soap_get_response'
        input_required = 'cluster_id',
        input_optional = 'id', 'name'

    def handle(self):
        with closing(self.odb.session()) as session:
            self.request.input.require_any('id', 'name')
            item = http_soap(session, self.request.input.cluster_id, self.request.input.id, self.request.input.name)
            out = get_dict_with_opaque(item)
            self.response.payload = out

# ################################################################################################################################

class GetList(_BaseGet):
    """ Returns a list of HTTP/SOAP connections.
    """
    _filter_by = HTTPSOAP.name,

    class SimpleIO(GetListAdminSIO, _BaseGet.SimpleIO):
        request_elem = 'zato_http_soap_get_list_request'
        response_elem = 'zato_http_soap_get_list_response'
        input_required = 'cluster_id'
        input_optional = GetListAdminSIO.input_optional + ('connection', 'transport', 'data_format')
        output_optional = _BaseGet.SimpleIO.output_optional + ('connection', 'transport')
        output_repeated = True

    def get_data(self, session):
        result = self._search(http_soap_list, session, self.request.input.cluster_id,
            self.request.input.connection, self.request.input.transport,
            asbool(self.server.fs_server_config.misc.return_internal_objects),
            self.request.input.get('data_format'),
            False,
            )
        return elems_with_opaque(result)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(AdminService, _HTTPSOAPService):
    def add_tls_ca_cert(self, input, sec_tls_ca_cert_id):
        with closing(self.odb.session()) as session:
            input.sec_tls_ca_cert_name = session.query(TLSCACert.name).\
                filter(TLSCACert.id==sec_tls_ca_cert_id).\
                one()[0]

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
# ################################################################################################################################

class Create(_CreateEdit):
    """ Creates a new HTTP/SOAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_create_request'
        response_elem = 'zato_http_soap_create_response'
        input_required = 'cluster_id', 'name', 'is_active', 'connection', 'transport', 'is_internal', 'url_path'
        input_optional = 'service', 'security_id', 'method', 'soap_action', 'soap_version', 'data_format', \
            'host', 'ping_method', 'pool_size', Boolean('merge_url_params_req'), 'url_params_pri', 'params_pri', \
            'serialization_type', 'timeout', 'sec_tls_ca_cert_id', Boolean('has_rbac'), 'content_type', \
            'cache_id', Integer('cache_expiry'), 'content_encoding', Boolean('match_slash'), 'http_accept', \
            List('service_whitelist'), 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', \
            Boolean('rate_limit_check_parent_def'), Boolean('sec_use_rbac'), 'hl7_version', 'json_path', \
            'should_parse_on_input', 'should_validate', 'should_return_errors', 'data_encoding'
        output_required = ('id', 'name')

    def handle(self):

        # If we have a rate limiting definition, let's check it upfront
        DefinitionParser.check_definition_from_input(self.request.input)

        input = self.request.input
        input.sec_use_rbac = input.get('sec_use_rbac') or (input.security_id == ZATO_SEC_USE_RBAC)
        input.security_id = input.security_id if input.security_id not in (ZATO_NONE, ZATO_SEC_USE_RBAC) else None
        input.soap_action = input.soap_action if input.soap_action else ''
        input.timeout = input.get('timeout') or MISC.DEFAULT_HTTP_TIMEOUT

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

            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.cluster_id==Cluster.id).\
                filter(Service.name==input.service).first()

            if input.connection == CONNECTION.CHANNEL and not service:
                msg = 'Service `{}` does not exist on this cluster'.format(input.service)
                self.logger.error(msg)
                raise Exception(msg)

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
                item.soap_action = input.soap_action
                item.soap_version = input.soap_version or None
                item.data_format = input.data_format
                item.service = service
                item.ping_method = input.get('ping_method') or DEFAULT_HTTP_PING_METHOD
                item.pool_size = input.get('pool_size') or DEFAULT_HTTP_POOL_SIZE
                item.merge_url_params_req = input.get('merge_url_params_req') or True
                item.url_params_pri = input.get('url_params_pri') or URL_PARAMS_PRIORITY.DEFAULT
                item.params_pri = input.get('params_pri') or PARAMS_PRIORITY.DEFAULT
                item.serialization_type = input.get('serialization_type') or HTTP_SOAP_SERIALIZATION_TYPE.DEFAULT.id
                item.timeout = input.timeout
                item.has_rbac = input.get('has_rbac') or input.sec_use_rbac or False
                item.content_type = input.get('content_type')
                item.sec_use_rbac = input.sec_use_rbac
                item.cache_id = input.get('cache_id') or None
                item.cache_expiry = input.get('cache_expiry') or 0
                item.content_encoding = input.content_encoding

                if input.security_id:
                    item.security = get_security_by_id(session, input.security_id)
                else:
                    input.security_id = None # To ensure that SQLite doesn't reject ''

                sec_tls_ca_cert_id = input.get('sec_tls_ca_cert_id')
                item.sec_tls_ca_cert_id = sec_tls_ca_cert_id if sec_tls_ca_cert_id and sec_tls_ca_cert_id != ZATO_NONE else None

                # Opaque attributes
                set_instance_opaque_attrs(item, input)

                session.add(item)
                session.commit()

                if input.connection == CONNECTION.CHANNEL:
                    input.impl_name = service.impl_name
                    input.service_id = service.id
                    input.service_name = service.name

                    cache = cache_by_id(session, input.cluster_id, item.cache_id) if item.cache_id else None
                    if cache:
                        input.cache_type = cache.cache_type
                        input.cache_name = cache.name
                    else:
                        input.cache_type = None
                        input.cache_name = None

                if item.sec_tls_ca_cert_id and item.sec_tls_ca_cert_id != ZATO_NONE:
                    self.add_tls_ca_cert(input, item.sec_tls_ca_cert_id)

                input.id = item.id
                input.update(sec_info)

                if input.connection == CONNECTION.CHANNEL:
                    action = CHANNEL.HTTP_SOAP_CREATE_EDIT.value
                else:
                    action = OUTGOING.HTTP_SOAP_CREATE_EDIT.value
                self.notify_worker_threads(input, action)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Object could not be created, e:`%s', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

class Edit(_CreateEdit):
    """ Updates an HTTP/SOAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_edit_request'
        response_elem = 'zato_http_soap_edit_response'
        input_required = 'id', 'cluster_id', 'name', 'is_active', 'connection', 'transport', 'url_path'
        input_optional = 'service', 'security_id', 'method', 'soap_action', 'soap_version', 'data_format', \
            'host', 'ping_method', 'pool_size', Boolean('merge_url_params_req'), 'url_params_pri', 'params_pri', \
            'serialization_type', 'timeout', 'sec_tls_ca_cert_id', Boolean('has_rbac'), 'content_type', \
            'cache_id', Integer('cache_expiry'), 'content_encoding', Boolean('match_slash'), 'http_accept', \
            List('service_whitelist'), 'is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', \
            Boolean('rate_limit_check_parent_def'), Boolean('sec_use_rbac'), 'hl7_version', 'json_path', \
            'should_parse_on_input', 'should_validate', 'should_return_errors', 'data_encoding'
        output_required = 'id', 'name'

    def handle(self):

        # If we have a rate limiting definition, let's check it upfront
        DefinitionParser.check_definition_from_input(self.request.input)

        input = self.request.input
        input.sec_use_rbac = input.get('sec_use_rbac') or (input.security_id == ZATO_SEC_USE_RBAC)
        input.security_id = input.security_id if input.security_id not in (ZATO_NONE, ZATO_SEC_USE_RBAC) else None
        input.soap_action = input.soap_action if input.soap_action else ''

        if input.content_encoding and input.content_encoding != 'gzip':
            raise Exception('Content encoding must be empty or equal to `gzip`')

        with closing(self.odb.session()) as session:

            existing_one = session.query(HTTPSOAP.id).\
                filter(HTTPSOAP.cluster_id==input.cluster_id).\
                filter(HTTPSOAP.id!=input.id).\
                filter(HTTPSOAP.name==input.name).\
                filter(HTTPSOAP.connection==input.connection).\
                filter(HTTPSOAP.transport==input.transport).\
                first()

            if existing_one:
                raise Exception('An object of that input.name:`{}` already exists in this cluster ' \
                '(input.connection:`{}` input.transport:`{}` input.id:`{}` existing_one.id:`{}`)'.format(
                    input.name, input.connection, input.transport, input.id, existing_one.id))

            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.cluster_id==Cluster.id).\
                filter(Service.name==input.service).first()

            if input.connection == CONNECTION.CHANNEL and not service:
                msg = 'Service `{}` does not exist on this cluster'.format(input.service)
                self.logger.error(msg)
                raise Exception(msg)

            # Will raise exception if the security type doesn't match connection
            # type and transport
            sec_info = self._handle_security_info(session, input.security_id, input.connection, input.transport)

            # TLS data comes in combinations, i.e. certain elements are required only if TLS keys/certs are used
            self._validate_tls(input, sec_info)

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
                item.ping_method = input.get('ping_method') or DEFAULT_HTTP_PING_METHOD
                item.pool_size = input.get('pool_size') or DEFAULT_HTTP_POOL_SIZE
                item.merge_url_params_req = input.get('merge_url_params_req') or False
                item.url_params_pri = input.get('url_params_pri') or URL_PARAMS_PRIORITY.DEFAULT
                item.params_pri = input.get('params_pri') or PARAMS_PRIORITY.DEFAULT
                item.serialization_type = input.get('serialization_type') or HTTP_SOAP_SERIALIZATION_TYPE.DEFAULT.id
                item.timeout = input.get('timeout') or MISC.DEFAULT_HTTP_TIMEOUT
                item.has_rbac = input.get('has_rbac') or input.sec_use_rbac or False
                item.content_type = input.get('content_type')
                item.sec_use_rbac = input.sec_use_rbac
                item.cache_id = input.get('cache_id') or None
                item.cache_expiry = input.get('cache_expiry') or 0
                item.content_encoding = input.content_encoding

                sec_tls_ca_cert_id = input.get('sec_tls_ca_cert_id')
                item.sec_tls_ca_cert_id = sec_tls_ca_cert_id if sec_tls_ca_cert_id and sec_tls_ca_cert_id != ZATO_NONE else None

                # Opaque attributes
                set_instance_opaque_attrs(item, input)

                session.add(item)
                session.commit()

                if input.connection == CONNECTION.CHANNEL:
                    input.impl_name = service.impl_name
                    input.service_id = service.id
                    input.service_name = service.name
                    input.merge_url_params_req = item.merge_url_params_req
                    input.url_params_pri = item.url_params_pri
                    input.params_pri = item.params_pri

                    cache = cache_by_id(session, input.cluster_id, item.cache_id) if item.cache_id else None
                    if cache:
                        input.cache_type = cache.cache_type
                        input.cache_name = cache.name
                    else:
                        input.cache_type = None
                        input.cache_name = None

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

                if item.sec_tls_ca_cert_id and item.sec_tls_ca_cert_id != ZATO_NONE:
                    self.add_tls_ca_cert(input, item.sec_tls_ca_cert_id)

                if input.connection == CONNECTION.CHANNEL:
                    action = CHANNEL.HTTP_SOAP_CREATE_EDIT.value
                else:
                    action = OUTGOING.HTTP_SOAP_CREATE_EDIT.value
                self.notify_worker_threads(input, action)

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
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_delete_request'
        response_elem = 'zato_http_soap_delete_response'
        input_required = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(HTTPSOAP).\
                    filter(HTTPSOAP.id==self.request.input.id).\
                    one()

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

                self.notify_worker_threads({
                    'name':old_name,
                    'transport':old_transport,
                    'old_url_path':old_url_path,
                    'old_soap_action':old_soap_action,
                    'old_http_method': old_http_method,
                    'old_http_accept': old_http_accept,
                }, action)

            except Exception:
                session.rollback()
                self.logger.error('Object could not be deleted, e:`%s`', format_exc())

                raise

# ################################################################################################################################

class Ping(AdminService):
    """ Pings an HTTP/SOAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_ping_request'
        response_elem = 'zato_http_soap_ping_response'
        input_required = 'id'
        output_required = 'id', 'is_success'
        output_optional = 'info'

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(HTTPSOAP).filter_by(id=self.request.input.id).one()
            config_dict = getattr(self.outgoing, item.transport)
            self.response.payload.id = self.request.input.id

            try:
                result = config_dict.get(item.name).ping(self.cid)
                is_success = True
            except Exception as e:
                result = e.args[0]
                is_success = False
            finally:
                self.response.payload.info = result
                self.response.payload.is_success = is_success

# ################################################################################################################################

class ReloadWSDL(AdminService, _HTTPSOAPService):
    """ Reloads WSDL by recreating the whole underlying queue of SOAP clients.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_reload_wsdl_request'
        response_elem = 'zato_http_soap_reload_wsdl_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(HTTPSOAP).filter_by(id=self.request.input.id).one()
            sec_info = self._handle_security_info(session, item.security_id, item.connection, item.transport)

        fields = to_json(item, True)['fields']
        fields['sec_type'] = sec_info['sec_type']
        fields['security_name'] = sec_info['security_name']

        action = OUTGOING.HTTP_SOAP_CREATE_EDIT.value
        self.notify_worker_threads(fields, action)

# ################################################################################################################################

class GetURLSecurity(AdminService):
    """ Returns a JSON document describing the security configuration of all Zato channels.
    """
    def handle(self):
        response = {}
        response['url_sec'] = sorted(self.worker_store.request_handler.security.url_sec.items())
        response['plain_http_handler.http_soap'] = sorted(self.worker_store.request_handler.plain_http_handler.http_soap.items())
        response['soap_handler.http_soap'] = sorted(self.worker_store.request_handler.soap_handler.http_soap.items())
        self.response.payload = dumps(response, sort_keys=True, indent=4)
        self.response.content_type = 'application/json'

# ################################################################################################################################
