# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""


# stdlib
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common.api import CONNECTION, MISC, PARAMS_PRIORITY, URL_PARAMS_PRIORITY, URL_TYPE, ZATO_NONE
from zato.common.broker_message import CHANNEL, OUTGOING
from zato.common.ext_db.api import needs_ext_db, to_public_id
from zato.common.odb.model import HTTPSOAP
from zato.common.typing_ import cast_
from zato.common.util.api import utcnow
from zato.common.util.channel import validate_channel_url_path
from zato.common.util.sql import get_security_by_id, set_instance_opaque_attrs
from zato.server.service import AsIs, Boolean
from zato.server.service.internal.http_soap.alert_settings import alert_input, prepare_alert_settings
from zato.server.service.internal.http_soap.common import _as2_input, _as4_input, _CreateEdit, _invocation_input, \
    _is_declarative, _normalize_retry_config, _retry_input, _validate_invocation_config
from zato.server.service.internal.http_soap.delivery_settings import delivery_input, prepare_delivery_settings
from zato.server.service.internal.http_soap.health_check import sync_linked_jobs

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    """ Creates a new HTTP/SOAP connection.
    """
    name = 'zato.http-soap.create'

    input = 'name', 'url_path', 'connection', \
        '-service', '-service_id', AsIs('-security_id'), '-method', '-soap_action', '-soap_version', '-data_format', \
        '-host', '-ping_method', '-pool_size', Boolean('-merge_url_params_req'), '-url_params_pri', '-params_pri', \
        '-timeout', '-content_type', \
        Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', '-data_encoding', \
        '-is_active', '-transport', '-is_internal', '-cluster_id', \
        '-is_wrapper', '-wrapper_type', '-username', '-password', AsIs('-security_groups'), Boolean('-validate_tls'), \
        '-gateway_service_list', Boolean('-is_audit_log_active'), Boolean('-should_include_in_openapi'), \
        Boolean('-is_deprecated'), '-deprecation_sunset', '-deprecation_successor', \
        Boolean('-use_ws_addressing'), Boolean('-use_mtom'), '-body_credentials', '-tls_client_cert', '-tls_client_key', \
        *_invocation_input, \
        *_retry_input, \
        *_as4_input, \
        *_as2_input, \
        *alert_input, \
        *delivery_input
    output = 'id', 'name', '-url_path'

    def handle(self):

        # For later use
        skip_opaque = []

        input = self.request.input
        input.security_id = input.security_id if input.security_id not in (ZATO_NONE, ) else None
        input.soap_action = input.soap_action if input.soap_action else ''
        input.timeout = input.get('timeout') or MISC.DEFAULT_HTTP_TIMEOUT
        input.security_groups = self._preprocess_security_groups(input, skip_opaque)

        input.is_active   = input.get('is_active',   True)
        input.is_internal = input.get('is_internal', False)

        input.is_audit_log_active = input.get('is_audit_log_active', True)

        # Channels are included in OpenAPI documents unless the flag turns it off
        input.should_include_in_openapi = input.get('should_include_in_openapi', True)

        # Channels are not deprecated unless the flag turns it on
        input.is_deprecated = input.get('is_deprecated', False)
        input.deprecation_sunset = input.get('deprecation_sunset') or ''
        input.deprecation_successor = input.get('deprecation_successor') or ''

        # The moment the channel becomes deprecated is recorded for the Deprecation response header
        if input.is_deprecated:
            now = utcnow()
            input.deprecation_since = now.isoformat()
        else:
            input.deprecation_since = ''

        input.transport   = input.get('transport')   or URL_TYPE.PLAIN_HTTP
        input.cluster_id  = input.get('cluster_id')  or self.server.cluster_id
        input.data_format = input.get('data_format') or ''

        input.data_encoding = input.get('data_encoding') or 'utf-8'

        # A new REST or SOAP channel starts with every alert setting the caller did not send at its default
        prepare_alert_settings(self, input, skip_opaque, {})

        # A new outgoing REST connection starts with every delivery setting the caller did not send at its default
        prepare_delivery_settings(self, input, skip_opaque, {})

        # AS4 private keys are stored encrypted
        self._encrypt_as4_secrets(input)

        # AS2 private keys are stored encrypted too
        self._encrypt_as2_secrets(input)

        # .. and so is the object's own password
        self._encrypt_own_password(input)

        # The numeric AS2 fields arrive as strings from Dashboard forms
        self._normalize_as2_fields(input)

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
            input.ping_method = input_ping_method.strip() or MISC.DEFAULT_HTTP_PING_METHOD

        if input_content_type:
            input.content_type = input_content_type.strip()

        # The declarative invocation profile of an outgoing connection is validated
        # before anything is committed to the database, and the connection's retry config
        # receives the shared defaults for any field that was not given on input.
        if _is_declarative(input):
            _validate_invocation_config(self, input)
            _normalize_retry_config(input)

        # AS2/AS4 objects are stored in the external database when one is configured
        is_ext = needs_ext_db(input.transport)

        with closing(self.server.get_config_session(object_type=input.transport)) as session:
            existing_one = session.query(HTTPSOAP.id).\
                filter(HTTPSOAP.cluster_id==input.cluster_id).\
                filter(HTTPSOAP.name==input.name).\
                filter(HTTPSOAP.connection==input.connection).\
                filter(HTTPSOAP.transport==input.transport).\
                first()

            if existing_one:
                raise Exception('An object of that name `{}` already exists in this cluster'.format(input.name))

            if input.connection == CONNECTION.CHANNEL:
                service = self._get_channel_service(session, input, is_ext)
            else:
                service = None

            # Will raise exception if the security type doesn't match connection
            # type and transport
            sec_info = self._get_security_info(session, input, is_ext)

            # Make sure this combination of channel parameters does not exist already
            if input.connection == CONNECTION.CHANNEL:
                validate_channel_url_path(input.url_path)
                self.ensure_channel_is_unique(session,
                    input.url_path, input.http_accept, input.method, input.cluster_id, None)
                self.ensure_channel_does_not_conflict(session, input, input.cluster_id, None)

            try:

                # The external database has its own cluster row that all its objects point to
                if is_ext:
                    item = HTTPSOAP()
                    item.cluster_id = input.cluster_id
                else:
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
                item.pool_size = input.get('pool_size') or MISC.DEFAULT_HTTP_POOL_SIZE
                item.merge_url_params_req = input.merge_url_params_req
                item.url_params_pri = input.get('url_params_pri') or URL_PARAMS_PRIORITY.DEFAULT
                item.params_pri = input.get('params_pri') or PARAMS_PRIORITY.DEFAULT
                item.timeout = input.timeout
                item.content_type = input.content_type
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
                    # The external database holds a mirror of the definition under the same id
                    if is_ext:
                        item.security_id = input.security_id
                    else:
                        item.security = get_security_by_id(session, input.security_id)
                else:
                    input.security_id = None # To ensure that SQLite does not reject ''

                # Opaque attributes
                set_instance_opaque_attrs(item, input, skip=skip_opaque)

                session.add(item)
                session.commit()

                if input.connection == CONNECTION.CHANNEL:
                    if service:
                        input.impl_name = service.impl_name
                        input.service_id = service.id
                        input.service_name = service.name

                # Everyone else knows objects from the external database under their offset ids
                item_id = cast_('int', item.id)

                if is_ext:
                    public_id = to_public_id(item_id)
                else:
                    public_id = item_id

                input.id = public_id
                input.update(sec_info)

                if input.connection == CONNECTION.CHANNEL:
                    action = CHANNEL.HTTP_SOAP_CREATE_EDIT.value
                else:
                    action = OUTGOING.HTTP_SOAP_CREATE_EDIT.value
                self.notify_server(input, action)

                # The connection is committed by now so its linked jobs can be created
                if _is_declarative(input):
                    sync_linked_jobs(self, input, item_id)

                self.response.payload.id = public_id
                self.response.payload.name = item.name
                self.response.payload.url_path = item.url_path

            except Exception:
                self.logger.error('Object could not be created, e:`%s', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
