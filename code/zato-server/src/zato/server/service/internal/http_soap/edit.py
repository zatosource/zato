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
from zato.common.ext_db.api import needs_ext_db, to_local_id, to_public_id
from zato.common.odb.model import HTTPSOAP
from zato.common.typing_ import cast_
from zato.common.util.api import utcnow
from zato.common.util.channel import validate_channel_url_path
from zato.common.util.sql import parse_instance_opaque_attr, set_instance_opaque_attrs
from zato.server.service import AsIs, Boolean
from zato.server.service.internal.http_soap.alert_settings import alert_input, prepare_alert_settings
from zato.server.service.internal.http_soap.common import _as2_input, _as4_input, _CreateEdit, _invocation_input, \
    _is_declarative, _normalize_retry_config, _pem_secret_fields, _retry_input, _validate_invocation_config
from zato.server.service.internal.http_soap.health_check import preserve_job_ids, sync_linked_jobs

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    """ Updates an HTTP/SOAP connection.
    """
    input = 'id', 'name', 'url_path', 'connection', \
        '-service', '-service_id', AsIs('-security_id'), '-method', '-soap_action', '-soap_version', \
        '-data_format', '-host', '-ping_method', '-pool_size', Boolean('-merge_url_params_req'), '-url_params_pri', \
        '-params_pri', '-timeout', '-content_type', \
        Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', '-data_encoding', \
        '-cluster_id', '-is_active', '-transport', \
        '-is_wrapper', '-wrapper_type', '-username', '-password', AsIs('-security_groups'), Boolean('-validate_tls'), \
        '-gateway_service_list', Boolean('-is_audit_log_active'), Boolean('-should_include_in_openapi'), \
        Boolean('-is_deprecated'), '-deprecation_sunset', '-deprecation_successor', \
        Boolean('-use_ws_addressing'), Boolean('-use_mtom'), '-body_credentials', '-tls_client_cert', '-tls_client_key', \
        *_invocation_input, \
        *_retry_input, \
        *_as4_input, \
        *_as2_input, \
        *alert_input
    output = '-id', '-name'

    def handle(self):

        # For later use
        skip_opaque = []

        input = self.request.input
        input.security_id  = input.security_id if input.security_id not in (ZATO_NONE,) else None
        input.soap_action  = input.soap_action if input.soap_action else ''
        input.timeout      = input.get('timeout') or MISC.DEFAULT_HTTP_TIMEOUT
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

        input.transport   = input.get('transport')   or URL_TYPE.PLAIN_HTTP
        input.cluster_id  = input.get('cluster_id')  or self.server.cluster_id
        input.data_format = input.get('data_format') or ''

        input.data_encoding = input.get('data_encoding') or 'utf-8'

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

        # AS2/AS4 objects are stored in the external database when one is configured,
        # under their local ids, without the offset they are known under everywhere else.
        is_ext = needs_ext_db(input.transport)

        # Dashboard forms send the id as a string, whereas the collision check below compares it
        # against database ids, so it is an int from here on
        input_id = int(input.id)

        if is_ext:
            local_id = to_local_id(input_id)
        else:
            local_id = input_id

        with closing(self.server.get_config_session(object_type=input.transport)) as session:

            existing_one = session.query(
                HTTPSOAP.id,
                HTTPSOAP.url_path,
                ).\
                filter(HTTPSOAP.cluster_id==input.cluster_id).\
                filter(HTTPSOAP.id!=local_id).\
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
                service = self._get_channel_service(session, input, is_ext)
            else:
                service = None

            # Will raise exception if the security type doesn't match connection
            # type and transport
            sec_info = self._get_security_info(session, input, is_ext)

            # An edit can move a channel onto another channel's URL path, so it is checked
            # the same way a create is, with this channel itself left out of the comparison
            if input.connection == CONNECTION.CHANNEL:
                validate_channel_url_path(input.url_path)
                self.ensure_channel_is_unique(session,
                    input.url_path, input.http_accept, input.method, input.cluster_id, local_id)
                self.ensure_channel_does_not_conflict(session, input, input.cluster_id, local_id)

            try:
                item = session.query(HTTPSOAP).filter_by(id=local_id).one()

                opaque = parse_instance_opaque_attr(item)

                # A channel that was already deprecated keeps its original deprecation time,
                # one that becomes deprecated now gets the current time, and clearing the flag clears the time.
                if input.is_deprecated:
                    if deprecation_since := opaque.get('deprecation_since'):
                        pass
                    else:
                        now = utcnow()
                        deprecation_since = now.isoformat()
                    input.deprecation_since = deprecation_since
                else:
                    input.deprecation_since = ''

                # The response caching config is edited on its own subpage, so the main form carries it over -
                # otherwise the config event broadcast below would erase it from the runtime channel data.
                if response_cache := opaque.get('response_cache'):
                    input.response_cache = response_cache

                # A REST or SOAP channel edited by a caller that sent no alert settings keeps the ones it has
                prepare_alert_settings(self, input, skip_opaque, opaque)

                # Secrets are never returned to the Dashboard, so an edit form cannot send them back.
                for name in _pem_secret_fields:

                    # A secret given on input is a new one and is stored as given ..
                    if input.get(name):
                        continue

                    # .. the staged next decryption key is cleared along with
                    # .. its certificate once a rotation completes ..
                    if name == 'as2_next_decryption_key':
                        if not input.get('as2_next_decryption_cert'):
                            continue

                    # .. and any other empty secret on input means the stored one is kept.
                    if stored_value := opaque.get(name):
                        input[name] = stored_value

                old_name = item.name
                old_url_path = item.url_path
                old_soap_action = item.soap_action
                old_http_method = item.method
                old_http_accept = opaque.get('http_accept')

                # An empty job ID on input must not overwrite the one stored previously
                if _is_declarative(input):
                    preserve_job_ids(input, opaque)

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
                item.pool_size = input.get('pool_size') or MISC.DEFAULT_HTTP_POOL_SIZE
                item.merge_url_params_req = input.merge_url_params_req
                item.url_params_pri = input.get('url_params_pri') or URL_PARAMS_PRIORITY.DEFAULT
                item.params_pri = input.get('params_pri') or PARAMS_PRIORITY.DEFAULT
                item.timeout = input.get('timeout')
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

                # Opaque attributes
                set_instance_opaque_attrs(item, input, skip=skip_opaque)

                session.add(item)
                session.commit()

                if input.connection == CONNECTION.CHANNEL:
                    if service:
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

                # The connection is committed by now so its linked jobs can be created, updated or deleted
                if _is_declarative(input):
                    sync_linked_jobs(self, input, item.id)

                # Everyone else knows objects from the external database under their offset ids
                item_id = cast_('int', item.id)

                if is_ext:
                    self.response.payload.id = to_public_id(item_id)
                else:
                    self.response.payload.id = item_id
                self.response.payload.name = item.name

            except Exception:
                self.logger.error('Object could not be updated, e:`%s`', format_exc())
                session.rollback()

                raise

# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
