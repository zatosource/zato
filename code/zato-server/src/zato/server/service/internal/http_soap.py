# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from json import dumps
from traceback import format_exc

# dateutil
from dateutil.parser import parse

# Paste
from paste.util.converters import asbool

# WebHelpers
from webhelpers.paginate import Page

# Zato
from zato.common import BATCH_DEFAULTS, DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, HTTP_SOAP_SERIALIZATION_TYPE, \
     MISC, MSG_PATTERN_TYPE, PARAMS_PRIORITY, SEC_DEF_TYPE, URL_PARAMS_PRIORITY, URL_TYPE, ZatoException, ZATO_NONE, \
     ZATO_SEC_USE_RBAC
from zato.common.broker_message import CHANNEL, OUTGOING
from zato.common.odb.model import Cluster, JSONPointer, HTTPSOAP, HTTSOAPAudit, HTTSOAPAuditReplacePatternsJSONPointer, \
     HTTSOAPAuditReplacePatternsXPath, SecurityBase, Service, TLSCACert, to_json, XPath
from zato.common.odb.query import cache_by_id, http_soap_audit_item, http_soap_audit_item_list, http_soap, http_soap_list
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
                   sec_def.sec_type not in(SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.TLS_KEY_CERT):
                    raise Exception('Only HTTP Basic Auth and TLS keys/certs are supported, not `{}`'.format(sec_def.sec_type))

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
        output_required = ('id', 'name', 'is_active', 'is_internal', 'url_path')
        output_optional = ('service_id', 'service_name', 'security_id', 'security_name', 'sec_type',
            'method', 'soap_action', 'soap_version', 'data_format', 'host', 'ping_method', 'pool_size', 'merge_url_params_req',
            'url_params_pri', 'params_pri', 'serialization_type', 'timeout', 'sec_tls_ca_cert_id', Boolean('has_rbac'),
            'content_type', Boolean('sec_use_rbac'), 'cache_id', 'cache_name', Integer('cache_expiry'), 'cache_type')

# ################################################################################################################################

class Get(_BaseGet):
    """ Returns information about an individual HTTP/SOAP object by its ID.
    """
    class SimpleIO(_BaseGet.SimpleIO):
        request_elem = 'zato_http_soap_get_request'
        response_elem = 'zato_http_soap_get_response'
        input_required = ('cluster_id', 'id')

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = http_soap(session, self.request.input.cluster_id, self.request.input.id)

# ################################################################################################################################

class GetList(_BaseGet):

    """ Returns a list of HTTP/SOAP connections.
    """
    _filter_by = HTTPSOAP.name,

    class SimpleIO(GetListAdminSIO, _BaseGet.SimpleIO):
        request_elem = 'zato_http_soap_get_list_request'
        response_elem = 'zato_http_soap_get_list_response'
        input_required = ('cluster_id',)
        input_optional = GetListAdminSIO.input_optional + ('connection', 'transport')
        output_optional = _BaseGet.SimpleIO.output_optional + ('connection', 'transport')
        output_repeated = True

    def get_data(self, session):
        return self._search(http_soap_list, session, self.request.input.cluster_id,
            self.request.input.connection, self.request.input.transport,
            asbool(self.server.fs_server_config.misc.return_internal_objects), False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class _CreateEdit(AdminService, _HTTPSOAPService):
    def add_tls_ca_cert(self, input, sec_tls_ca_cert_id):
        with closing(self.odb.session()) as session:
            input.sec_tls_ca_cert_name = session.query(TLSCACert.name).\
                filter(TLSCACert.id==sec_tls_ca_cert_id).\
                one()[0]

# ################################################################################################################################

class Create(_CreateEdit):
    """ Creates a new HTTP/SOAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_create_request'
        response_elem = 'zato_http_soap_create_response'
        input_required = ('cluster_id', 'name', 'is_active', 'connection', 'transport', 'is_internal', 'url_path')
        input_optional = ('service', 'security_id', 'method', 'soap_action', 'soap_version', 'data_format',
            'host', 'ping_method', 'pool_size', Boolean('merge_url_params_req'), 'url_params_pri', 'params_pri',
            'serialization_type', 'timeout', 'sec_tls_ca_cert_id', Boolean('has_rbac'), 'content_type',
            'cache_id', Integer('cache_expiry'))
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.sec_use_rbac = input.security_id == ZATO_SEC_USE_RBAC
        input.security_id = input.security_id if input.security_id not in (ZATO_NONE, ZATO_SEC_USE_RBAC) else None
        input.soap_action = input.soap_action if input.soap_action else ''
        input.timeout = input.get('timeout') or MISC.DEFAULT_HTTP_TIMEOUT

        with closing(self.odb.session()) as session:
            existing_one = session.query(HTTPSOAP.id).\
                filter(HTTPSOAP.cluster_id==input.cluster_id).\
                filter(HTTPSOAP.name==input.name).\
                filter(HTTPSOAP.connection==input.connection).\
                filter(HTTPSOAP.transport==input.transport).\
                first()

            if existing_one:
                raise Exception('An object of that name `{}` already exists on this cluster'.format(input.name))

            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.cluster_id==Cluster.id).\
                filter(Service.name==input.service).first()

            if input.connection == 'channel' and not service:
                msg = 'Service `{}` does not exist on this cluster'.format(input.service)
                self.logger.error(msg)
                raise Exception(msg)

            # Will raise exception if the security type doesn't match connection
            # type and transport
            sec_info = self._handle_security_info(session, input.security_id,
                input.connection, input.transport)

            try:

                item = HTTPSOAP()
                item.connection = input.connection
                item.transport = input.transport
                item.cluster_id = input.cluster_id
                item.is_internal = input.is_internal
                item.name = input.name
                item.is_active = input.is_active
                item.host = input.host
                item.url_path = input.url_path
                item.security_id = input.security_id or None # So SQLite doesn't reject ''
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
                item.cache_id = input.cache_id
                item.cache_expiry = input.cache_expiry

                sec_tls_ca_cert_id = input.get('sec_tls_ca_cert_id')
                item.sec_tls_ca_cert_id = sec_tls_ca_cert_id if sec_tls_ca_cert_id and sec_tls_ca_cert_id != ZATO_NONE else None

                session.add(item)
                session.commit()

                if input.connection == 'channel':
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

                if input.connection == 'channel':
                    action = CHANNEL.HTTP_SOAP_CREATE_EDIT.value
                else:
                    action = OUTGOING.HTTP_SOAP_CREATE_EDIT.value
                self.notify_worker_threads(input, action)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception, e:
                msg = 'Could not create the object, e:`{}'.format(format_exc())
                self.logger.error(msg)
                session.rollback()

                raise

# ################################################################################################################################

class Edit(_CreateEdit):
    """ Updates an HTTP/SOAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_edit_request'
        response_elem = 'zato_http_soap_edit_response'
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'connection', 'transport', 'url_path')
        input_optional = ('service', 'security_id', 'method', 'soap_action', 'soap_version', 'data_format',
            'host', 'ping_method', 'pool_size', Boolean('merge_url_params_req'), 'url_params_pri', 'params_pri',
            'serialization_type', 'timeout', 'sec_tls_ca_cert_id', Boolean('has_rbac'), 'content_type',
            'cache_id', Integer('cache_expiry'))
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.sec_use_rbac = input.security_id == ZATO_SEC_USE_RBAC
        input.security_id = input.security_id if input.security_id not in (ZATO_NONE, ZATO_SEC_USE_RBAC) else None
        input.soap_action = input.soap_action if input.soap_action else ''

        with closing(self.odb.session()) as session:

            existing_one = session.query(HTTPSOAP.id).\
                filter(HTTPSOAP.cluster_id==input.cluster_id).\
                filter(HTTPSOAP.id!=input.id).\
                filter(HTTPSOAP.name==input.name).\
                filter(HTTPSOAP.connection==input.connection).\
                filter(HTTPSOAP.transport==input.transport).\
                first()

            if existing_one:
                raise Exception('An object of that name `{}` already exists on this cluster'.format(input.name))

            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.cluster_id==Cluster.id).\
                filter(Service.name==input.service).first()

            if input.connection == 'channel' and not service:
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
                old_name = item.name
                old_url_path = item.url_path
                old_soap_action = item.soap_action
                item.name = input.name
                item.is_active = input.is_active
                item.host = input.host
                item.url_path = input.url_path
                item.security_id = input.security_id or None # So SQLite doesn't reject ''
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
                item.cache_id = input.cache_id
                item.cache_expiry = input.cache_expiry

                sec_tls_ca_cert_id = input.get('sec_tls_ca_cert_id')
                item.sec_tls_ca_cert_id = sec_tls_ca_cert_id if sec_tls_ca_cert_id and sec_tls_ca_cert_id != ZATO_NONE else None

                session.add(item)
                session.commit()

                if input.connection == 'channel':
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
                input.update(sec_info)

                if item.sec_tls_ca_cert_id and item.sec_tls_ca_cert_id != ZATO_NONE:
                    self.add_tls_ca_cert(input, item.sec_tls_ca_cert_id)

                if input.connection == 'channel':
                    action = CHANNEL.HTTP_SOAP_CREATE_EDIT.value
                else:
                    action = OUTGOING.HTTP_SOAP_CREATE_EDIT.value
                self.notify_worker_threads(input, action)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception, e:
                msg = 'Could not update the object, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

# ################################################################################################################################

class Delete(AdminService, _HTTPSOAPService):
    """ Deletes an HTTP/SOAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_delete_request'
        response_elem = 'zato_http_soap_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(HTTPSOAP).\
                    filter(HTTPSOAP.id==self.request.input.id).\
                    one()

                old_name = item.name
                old_transport = item.transport
                old_url_path = item.url_path
                old_soap_action = item.soap_action

                session.delete(item)
                session.commit()

                if item.connection == 'channel':
                    action = CHANNEL.HTTP_SOAP_DELETE.value
                else:
                    action = OUTGOING.HTTP_SOAP_DELETE.value

                self.notify_worker_threads({'name':old_name, 'transport':old_transport,
                    'old_url_path':old_url_path, 'old_soap_action':old_soap_action}, action)

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the object, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise

# ################################################################################################################################

class Ping(AdminService):
    """ Pings an HTTP/SOAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_ping_request'
        response_elem = 'zato_http_soap_ping_response'
        input_required = ('id',)
        output_required = ('info',)

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(HTTPSOAP).filter_by(id=self.request.input.id).one()
            config_dict = getattr(self.outgoing, item.transport)
            self.response.payload.info = config_dict.get(item.name).ping(self.cid)

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
    """ Returns a JSON document describing the security configuration of all
    Zato channels.
    """
    def handle(self):
        response = {}
        response['url_sec'] = sorted(self.worker_store.request_handler.security.url_sec.items())
        response['plain_http_handler.http_soap'] = sorted(self.worker_store.request_handler.plain_http_handler.http_soap.items())
        response['soap_handler.http_soap'] = sorted(self.worker_store.request_handler.soap_handler.http_soap.items())
        self.response.payload = dumps(response, sort_keys=True, indent=4)
        self.response.content_type = 'application/json'

# ################################################################################################################################

class GetAuditConfig(AdminService):
    """ Returns audit configuration for a given HTTP/SOAP object.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_get_audit_config_request'
        response_elem = 'zato_http_soap_get_audit_config_response'
        input_required = ('id',)
        output_required = (Boolean('audit_enabled'), Integer('audit_back_log'),
            Integer('audit_max_payload'), 'audit_repl_patt_type')

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(HTTPSOAP).\
                filter(HTTPSOAP.id==self.request.input.id).\
                one()

            self.response.payload.audit_enabled = item.audit_enabled
            self.response.payload.audit_back_log = item.audit_back_log
            self.response.payload.audit_max_payload = item.audit_max_payload
            self.response.payload.audit_repl_patt_type = item.audit_repl_patt_type

# ################################################################################################################################

class SetAuditConfig(AdminService):
    """ Sets audit configuration for a given HTTP/SOAP connection. Everything except for replace patterns.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_set_audit_config_request'
        response_elem = 'zato_http_soap_set_audit_config_response'
        input_required = ('id', Integer('audit_max_payload'))

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(HTTPSOAP).\
                filter(HTTPSOAP.id==self.request.input.id).\
                one()

            item.audit_max_payload = self.request.input.audit_max_payload
            session.commit()

            params = {
                'action': CHANNEL.HTTP_SOAP_AUDIT_CONFIG.value,
                'audit_max_payload': item.audit_max_payload,
                'id': item.id
            }
            self.broker_client.publish(params)

# ################################################################################################################################

class GetAuditReplacePatterns(AdminService):
    """ Returns audit replace patterns for a given connection, both JSONPointer and XPath.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_get_audit_replace_patterns_request'
        response_elem = 'zato_http_soap_get_audit_replace_patterns_response'
        input_required = ('id',)
        output_required = (List('patterns_json_pointer'), List('patterns_xpath'))

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(HTTPSOAP).\
                filter(HTTPSOAP.id==self.request.input.id).\
                one()

            self.response.payload.patterns_json_pointer = [elem.pattern.name for elem in item.replace_patterns_json_pointer]
            self.response.payload.patterns_xpath = [elem.pattern.name for elem in item.replace_patterns_xpath]

# ################################################################################################################################

class SetAuditReplacePatterns(AdminService):
    """ Set audit replace patterns for a given HTTP/SOAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_set_replace_patterns_request'
        response_elem = 'zato_http_soap_set_replace_patterns_response'
        input_required = ('id', 'audit_repl_patt_type')
        input_optional = (List('pattern_list'),)

    def _clear_patterns(self, conn):
        conn.replace_patterns_json_pointer[:] = []
        conn.replace_patterns_xpath[:] = []

    def handle(self, JSON_POINTER=MSG_PATTERN_TYPE.JSON_POINTER):
        conn_id = self.request.input.id
        patt_type = self.request.input.audit_repl_patt_type

        with closing(self.odb.session()) as session:
            conn = session.query(HTTPSOAP).\
                filter(HTTPSOAP.id==conn_id).\
                one()

            if not self.request.input.pattern_list:
                # OK, no patterns at all so we indiscriminately delete existing ones, if any, for the connection.
                self._clear_patterns(conn)
                session.commit()

            else:
                pattern_class = JSONPointer if patt_type == JSON_POINTER.id else XPath
                conn_pattern_list_class = HTTSOAPAuditReplacePatternsJSONPointer if patt_type == JSON_POINTER.id else \
                    HTTSOAPAuditReplacePatternsXPath

                all_patterns = session.query(pattern_class).\
                    filter(pattern_class.cluster_id==self.server.cluster_id).\
                    all()

                missing = set(self.request.input.pattern_list) - set([elem.name for elem in all_patterns])
                if missing:
                    msg = 'Could not find one or more pattern(s) {}'.format(sorted(missing))
                    self.logger.warn(msg)
                    raise ZatoException(self.cid, msg)

                # Clears but doesn't commit yet
                self._clear_patterns(conn)

                for name in self.request.input.pattern_list:
                    for pattern in all_patterns:
                        if name == pattern.name:
                            item = conn_pattern_list_class()
                            item.conn_id = conn.id
                            item.pattern_id = pattern.id
                            item.cluster_id = self.server.cluster_id
                            session.add(item)

                session.commit()

                params = {
                    'action': CHANNEL.HTTP_SOAP_AUDIT_PATTERNS.value,
                    'id': conn_id,
                    'audit_repl_patt_type': self.request.input.audit_repl_patt_type,
                    'pattern_list': self.request.input.pattern_list,
                }
                self.broker_client.publish(params)

# ################################################################################################################################

class SetAuditState(AdminService):
    """ Enables or disables audit for a given HTTP/SOAP object.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_set_audit_state_request'
        response_elem = 'zato_http_soap_set_audit_state_response'
        input_required = ('id', Boolean('audit_enabled'))

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(HTTPSOAP).\
                filter(HTTPSOAP.id==self.request.input.id).\
                one()

            item.audit_enabled = self.request.input.audit_enabled

            session.add(item)
            session.commit()

            params = {
                'action': CHANNEL.HTTP_SOAP_AUDIT_STATE.value,
                'id': item.id,
                'audit_enabled': item.audit_enabled,
            }
            self.broker_client.publish(params)

# ################################################################################################################################

class SetAuditResponseData(AdminService):
    """ Updates information regarding a response of a channel/outconn invocation.
    """
    def handle(self):
        with closing(self.odb.session()) as session:

            payload_req = self.request.payload
            item = session.query(HTTSOAPAudit).filter_by(cid=payload_req['cid']).one()

            item.invoke_ok = asbool(payload_req['invoke_ok'])
            item.auth_ok = asbool(payload_req['auth_ok'])
            item.resp_time = parse(payload_req['resp_time'])
            item.resp_headers = payload_req['resp_headers'].encode('utf-8')
            item.resp_payload = payload_req['resp_payload'].encode('utf-8')

            session.add(item)
            session.commit()

# ################################################################################################################################

class _BaseAuditService(AdminService):
    def get_page(self, session):
        current_batch = self.request.input.get('current_batch', BATCH_DEFAULTS.PAGE_NO)
        batch_size = self.request.input.get('batch_size', BATCH_DEFAULTS.SIZE)
        batch_size = min(batch_size, BATCH_DEFAULTS.MAX_SIZE)

        q = http_soap_audit_item_list(session, self.server.cluster_id, self.request.input.conn_id,
            self.request.input.get('start'), self.request.input.get('stop'), self.request.input.get('query'), False)

        return Page(q, page=current_batch, items_per_page=batch_size)

# ################################################################################################################################

class GetAuditItemList(_BaseAuditService):
    """ Returns a list of audit items for a particular HTTP/SOAP object.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_get_audit_item_list_request'
        response_elem = 'zato_http_soap_get_audit_item_list_response'
        input_required = ('conn_id', )
        input_optional = ('start', 'stop', Integer('current_batch'), Integer('batch_size'), 'query')
        output_required = ('id', 'cid', 'req_time_utc', 'remote_addr',)
        output_optional = ('resp_time_utc', 'user_token', 'invoke_ok', 'auth_ok', )

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_page(session)

        for item in self.response.payload.zato_output:
            item.req_time_utc = item.req_time_utc.isoformat()
            if item.resp_time_utc:
                item.resp_time_utc = item.resp_time_utc.isoformat()

# ################################################################################################################################

class GetAuditBatchInfo(_BaseAuditService):
    """ Returns pagination information for audit log for a specified object and from/to dates.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_get_batch_info_request'
        response_elem = 'zato_http_soap_get_batch_info_response'
        input_required = ('conn_id',)
        input_optional = ('start', 'stop', Integer('current_batch'), Integer('batch_size'), 'query')
        output_required = ('total_results', 'num_batches', 'has_previous', 'has_next', 'next_batch_number',
            'previous_batch_number')

    def handle(self):
        with closing(self.odb.session()) as session:
            page = self.get_page(session)
            self.response.payload = {
                'total_results': page.item_count,
                'num_batches': page.page_count,
                'has_previous': page.previous_page is not None,
                'has_next': page.next_page is not None,
                'next_batch_number': page.next_page,
                'previous_batch_number': page.previous_page,
            }

# ################################################################################################################################

class GetAuditItem(_BaseAuditService):
    """ Returns a particular audit item by its ID.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_get_audit_item_request'
        response_elem = 'zato_http_soap_get_audit_item_response'
        input_required = ('id',)
        output_required = ('id', 'cid', 'req_time_utc', 'remote_addr',)
        output_optional = ('resp_time_utc', 'user_token', 'invoke_ok', 'auth_ok', 'req_headers', 'req_payload',
            'resp_headers', 'resp_payload')

    def handle(self):
        with closing(self.odb.session()) as session:
            item = http_soap_audit_item(session, self.server.cluster_id, self.request.input.id).one()
            item.req_time_utc = item.req_time_utc.isoformat()
            if item.resp_time_utc:
                item.resp_time_utc = item.resp_time_utc.isoformat()

            self.response.payload = item

# ################################################################################################################################
