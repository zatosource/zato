# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""


# stdlib
from contextlib import closing

# Zato
from zato.common.api import AS2, AS4, CONNECTION, Groups, HTTP_SOAP, SEC_DEF_TYPE, URL_TYPE
from zato.common.const import SECRETS
from zato.common.exception import ServiceMissingException
from zato.common.ext_db.api import ensure_security_copy, ensure_service_copy
from zato.common.json_internal import dumps
from zato.common.odb.model import Cluster, HTTPSOAP, SecurityBase, Service
from zato.common.util.channel import channel_security_key, find_channel_collision, find_channel_conflict, \
     get_channel_collision_items
from zato.common.util.rest_invocation import parse_param_rows, validate_jsonata, validate_xpath
from zato.common.util.sql import parse_instance_opaque_attr
from zato.common.util.url_dispatcher import resolve_match_slash
from zato.server.connection.http_soap import BadRequest
from zato.server.service import AsIs, Boolean, Int
from zato.server.service.internal import AdminService
from zato.server.service.internal.http_soap.health_check import has_health_check_config, \
    has_scheduler_config, validate_run_every

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, anylist, strdict, strintdict
    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

_GetList_Optional = ('include_wrapper', 'cluster_id', 'connection', 'transport', 'data_format', 'needs_security_group_names')

# ################################################################################################################################
# ################################################################################################################################

_invocation = HTTP_SOAP.Invocation
_health_check = HTTP_SOAP.HealthCheck

# All the declarative invocation and health check fields, each optional on input and output.
_invocation_fields = []

for _invocation_field_name in _invocation.FieldList + _health_check.FieldList:
    _invocation_fields.append('-' + _invocation_field_name)

_invocation_input = tuple(_invocation_fields)

_retry = HTTP_SOAP.Retry

# All the retry fields of outgoing connections, each an optional integer on input and output.
_retry_fields = []

for _retry_field_name in _retry.FieldList:
    _retry_fields.append(Int('-' + _retry_field_name))

_retry_input = tuple(_retry_fields)

# The row-based fields whose JSONata-mode values are validated at create/edit time
_row_fields = (
    _invocation.Field_Request_Query_String,
    _invocation.Field_Request_Path_Params,
    _invocation.Field_Request_Headers,
    _invocation.Field_Request_Message,
    _invocation.Field_Request_SOAP_Headers,
)

# Transports that support the declarative invocation profile
_declarative_transports = (URL_TYPE.PLAIN_HTTP, URL_TYPE.SOAP)

# Security types that only outgoing connections use - there is no inbound verification for them,
# so a channel that named one would accept every caller.
_outgoing_only_sec_types = (SEC_DEF_TYPE.NTLM, SEC_DEF_TYPE.SPNEGO)

# ################################################################################################################################
# ################################################################################################################################

# All the AS4 fields, each optional on input - the boolean and the numeric ones
# are declared separately below.
_as4_fields = []

for _as4_field_name in AS4.Common_Fields + AS4.Channel_Fields + ('as4_sml_domain',):
    _as4_fields.append('-' + _as4_field_name)

_as4_fields = tuple(_as4_fields)

# The reception awareness parameters arrive from the Dashboard as text, so they are declared
# as numbers - a form field left empty arrives as an empty value and stays unset.
_as4_numeric_fields = []

for _as4_field_name in AS4.Numeric_Fields:
    _as4_numeric_fields.append(Int('-' + _as4_field_name))

_as4_input = _as4_fields + tuple(_as4_numeric_fields) + (Boolean('-as4_use_discovery'),)

# All the AS2 fields, each optional on input.
_as2_fields = []

for _as2_field_name in AS2.Common_Fields + AS2.Channel_Fields:
    _as2_fields.append('-' + _as2_field_name)

_as2_input = tuple(_as2_fields)

# The secret fields of AS2 and AS4 objects, i.e. their private keys and passwords - they are
# stored encrypted and they are never returned to any caller.
_pem_secret_fields = AS2.Secret_Fields + AS4.Secret_Fields

# ################################################################################################################################
# ################################################################################################################################

def _is_declarative(input:'Bunch') -> 'bool':
    """ Returns True if this connection carries the declarative invocation profile,
    i.e. it is an outgoing REST or SOAP connection.
    """
    if input.connection != CONNECTION.OUTGOING:
        return False

    out = input.transport in _declarative_transports
    return out

# ################################################################################################################################

def _normalize_retry_config(input:'Bunch') -> 'None':
    """ Fills in the retry config of an outgoing connection with the shared defaults
    for any field that was not given on input.
    """
    input.max_retries = input.max_retries or _retry.Default_Max_Retries
    input.retry_sleep_time = input.retry_sleep_time or _retry.Default_Sleep_Time
    input.retry_backoff_threshold = input.retry_backoff_threshold or _retry.Default_Backoff_Threshold
    input.retry_backoff_multiplier = input.retry_backoff_multiplier or _retry.Default_Backoff_Multiplier

# ################################################################################################################################

def _validate_expression(service:'AdminService', expression:'str', mode:'str', field_name:'str') -> 'None':
    """ Compiles a JSONata or XPath expression, reporting the field it came from if it is invalid.
    """
    try:
        if mode == _invocation.ResponseMapMode.XPath:
            validate_xpath(expression)
        else:
            validate_jsonata(expression)
    except Exception as e:
        raise BadRequest(service.cid, f'Invalid {mode} expression in `{field_name}` -> `{expression}` -> {e}')

# ################################################################################################################################

def _validate_callback(service:'AdminService', callback_type:'str', callback_name:'str', type_field:'str') -> 'None':
    """ Makes sure a callback is either fully configured or not given at all.
    """

    # No callback at all is valid
    if not callback_type:
        if not callback_name:
            return

    if not callback_type:
        raise BadRequest(service.cid, f'A callback name requires `{type_field}` to be given too')

    if callback_type not in _invocation.CallbackTypeList:
        raise BadRequest(service.cid, f'Callback type `{callback_type}` is not one of `{_invocation.CallbackTypeList}`')

    if not callback_name:
        raise BadRequest(service.cid, f'Callback type `{callback_type}` requires a callback name')

    # A callback service must exist so typos are caught at config time, not at call time
    if callback_type == _invocation.CallbackType.Service:
        if callback_name not in service.server.service_store.name_to_impl_name:
            raise BadRequest(service.cid, f'Callback service `{callback_name}` does not exist')

# ################################################################################################################################

# ################################################################################################################################

def _validate_invocation_config(service:'AdminService', input:'Bunch') -> 'None':
    """ Validates the declarative invocation profile of an outgoing REST or SOAP connection,
    compiling every expression so syntax errors are rejected at config time instead of at call time.
    """

    # Each JSONata-mode row value must compile ..
    for field_name in _row_fields:
        if rows_json := input.get(field_name):
            rows = parse_param_rows(rows_json)
            kept_rows:'anylist' = []

            for row in rows:
                key = row['key']
                key = key.strip()

                if not key:
                    continue

                mode = row['mode']
                if mode not in _invocation.ValueModeList:
                    raise BadRequest(service.cid, f'Value mode `{mode}` in `{field_name}` is not one of `{_invocation.ValueModeList}`')
                if mode == _invocation.ValueMode.JSONata:
                    _validate_expression(service, row['value'], _invocation.ValueMode.JSONata, field_name)

                # The parsed rows are shared through a cache, so the stripped key goes into a copy
                row = dict(row)
                row['key'] = key
                kept_rows.append(row)

            input[field_name] = dumps(kept_rows)

    # .. so must a JSONata-mode body ..
    if input.request_data:
        if input.request_data_mode == _invocation.ValueMode.JSONata:
            _validate_expression(service, input.request_data, _invocation.ValueMode.JSONata, _invocation.Field_Request_Data)

    # .. and a message map that builds a SOAP message ..
    if input.request_message_map:
        _validate_expression(service, input.request_message_map, _invocation.ValueMode.JSONata,
            _invocation.Field_Request_Message_Map)

    # .. and the response map, in whichever mode it is in ..
    if response_map := input.response_map:
        map_mode = input.response_map_mode
        if not map_mode:
            map_mode = _invocation.ResponseMapMode.JSONata
        if map_mode not in _invocation.ResponseMapModeList:
            raise BadRequest(service.cid, f'Response map mode `{map_mode}` is not one of `{_invocation.ResponseMapModeList}`')
        _validate_expression(service, response_map, map_mode, _invocation.Field_Response_Map)

    # .. callbacks must be fully configured or absent ..
    _validate_callback(service, input.callback_type, input.callback_name, _invocation.Field_Callback_Type)

    # .. the scheduler fields must describe a job that can be created ..
    if has_scheduler_config(service, input):
        input.scheduler_run_every = validate_run_every(
            service, input.scheduler_run_every, input.scheduler_run_unit, 'Scheduler')

    # .. and so must the health check fields.
    if has_health_check_config(input):
        input.health_check_run_every = validate_run_every(
            service, input.health_check_run_every, input.health_check_run_unit, 'Health check')

# ################################################################################################################################

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
                   sec_def.sec_type not in (SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.APIKEY, SEC_DEF_TYPE.OAUTH, SEC_DEF_TYPE.NTLM,
                       SEC_DEF_TYPE.MTLS, SEC_DEF_TYPE.SPNEGO):
                    raise Exception('Unsupported sec_type `{}`'.format(sec_def.sec_type))

            elif connection == CONNECTION.CHANNEL:

                if sec_def.sec_type in _outgoing_only_sec_types:
                    raise Exception('Sec_type `{}` cannot be used with channels'.format(sec_def.sec_type))

            info['security_id'] = security_id
            info['security_name'] = sec_def.name
            info['sec_type'] = sec_def.sec_type

        return info

# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

class _BaseGet(AdminService):
    """ Base class for services returning information about HTTP/SOAP objects.
    """
    output = 'id', 'name', 'is_active', 'is_internal', 'url_path', \
        '-service_id', '-service_name', '-security_id', '-security_name', '-sec_type', \
        '-method', '-soap_action', '-soap_version', '-data_format', '-host', '-ping_method', '-pool_size', \
        '-merge_url_params_req', '-url_params_pri', '-params_pri', '-timeout', \
        '-content_type', \
        Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', \
        '-data_encoding', '-username', '-is_wrapper', '-wrapper_type', AsIs('-security_groups'), '-security_group_count', \
        '-security_group_member_count', '-needs_security_group_names', Boolean('-validate_tls'), '-gateway_service_list', \
        '-transport', Boolean('-is_audit_log_active'), \
        *_invocation_input, \
        *_retry_input, \
        *_as4_input, \
        *_as2_input

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

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(AdminService, _HTTPSOAPService):

# ################################################################################################################################

# ################################################################################################################################

    def _raise_error(self, name, url_path, http_accept, http_method, source):
        msg = 'Such a channel already exists ({}); url_path:`{}`, http_accept:`{}`, http_method:`{}` (src:{})'
        raise Exception(msg.format(name, url_path, http_accept, http_method, source))

# ################################################################################################################################

    def ensure_channel_is_unique(self, session, url_path, http_accept, http_method, cluster_id, skip_id):
        existing_ones = session.query(HTTPSOAP).\
            filter(HTTPSOAP.cluster_id==cluster_id).\
            filter(HTTPSOAP.url_path==url_path).\
            filter(HTTPSOAP.connection==CONNECTION.CHANNEL).\
            all()

        # At least one channel with this kind of basic information already exists
        # but it is possible that it requires different HTTP headers (e.g. Accept, Method)
        # so the shared collision rule needs to look at each one.
        existing_items = []

        for item in existing_ones:
            opaque = parse_instance_opaque_attr(item)
            existing_items.append({
                'id': item.id,
                'name': item.name,
                'url_path': item.url_path,
                'method': item.method,
                'http_accept': opaque.get('http_accept'),
            })

        colliding_name = find_channel_collision(url_path, http_accept, http_method, existing_items, skip_id)

        if colliding_name:
            self._raise_error(colliding_name, url_path, http_accept, http_method, 'chk1')

# ################################################################################################################################

    def _get_security_groups_to_compare(self, input, existing_items, skip_id):
        """ Returns the security groups the channel will have once saved, as a list of their ids.
        """
        # A throwaway list, since what this preprocessing wants to leave out of the opaque
        # attributes is decided by the one call that goes on to write them
        out = self._preprocess_security_groups(input, [])

        # An input that never mentioned groups leaves the ones the channel already has in place,
        # so those are the ones a save would be judged on
        if out is None:
            out = []

            for item in existing_items:
                if item['id'] == skip_id:
                    _, group_ids = item['security']
                    out = list(group_ids)
                    break

        return out

# ################################################################################################################################

    def ensure_channel_does_not_conflict(self, session, input, cluster_id, skip_id):
        """ Refuses a channel that one request could reach in place of one already there, when the
        two secure that request differently and there is nothing but their names to settle which
        of them answers it.
        """
        existing_items = get_channel_collision_items(session, cluster_id)

        security_groups = self._get_security_groups_to_compare(input, existing_items, skip_id)
        security = channel_security_key(input.security_id, security_groups)

        conflicting_name = find_channel_conflict(
            input.url_path,
            input.http_accept,
            input.method,
            resolve_match_slash(input.match_slash),
            security,
            existing_items,
            skip_id,
        )

        if conflicting_name:
            msg = 'Channel `{}` matches the same requests as `{}` and secures them differently; '
            msg += 'url_path:`{}`, http_accept:`{}`, http_method:`{}`'
            raise Exception(msg.format(input.name, conflicting_name, input.url_path, input.http_accept, input.method))

# ################################################################################################################################

    def _preprocess_security_groups(self, input, skip_opaque):
        """ Turns whatever security groups the input carries into a list of their IDs, or into None
        when the input did not mention them at all.
        """
        # This will contain only IDs
        new_input_security_groups = []

        # Security groups are optional
        input_security_groups = input['security_groups']

        # A request that never mentioned the field arrives with None here, whereas one that sent an
        # empty list means it - the Dashboard sends an empty list once the operator unchecks every
        # group. Only the latter says a channel has no groups, so the former leaves what is stored
        # where it is, the same way username and password are left alone, and travels on to the
        # servers as None so that they keep what they already have too.
        if input_security_groups is None:
            skip_opaque.append('security_groups')
            return None

        if input_security_groups:

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

    def _get_channel_service_from_input(self, session, input):
        """ Returns the service a channel routes to - AS2 and AS4 channels may have none
        because their messages can go to a pub/sub topic instead.
        """
        if input.transport in (URL_TYPE.AS2, URL_TYPE.AS4):
            if not (input.service or input.service_id):
                return None

        out = self._get_service_from_input(session, input)
        return out

# ################################################################################################################################

    def _encrypt_as4_secrets(self, input):
        """ Encrypts the AS4 private keys and password unless they are encrypted already.
        """
        if input.transport != URL_TYPE.AS4:
            return

        for name in AS4.Secret_Fields:
            if value := input.get(name):
                if not value.startswith(SECRETS.PREFIX):
                    input[name] = self.server.encrypt(value)

# ################################################################################################################################

    def _encrypt_as2_secrets(self, input):
        """ Encrypts the AS2 private keys unless they are encrypted already.
        """
        if input.transport != URL_TYPE.AS2:
            return

        for name in AS2.Secret_Fields:
            if value := input.get(name):
                if not value.startswith(SECRETS.PREFIX):
                    input[name] = self.server.encrypt(value)

# ################################################################################################################################

    def _encrypt_own_password(self, input):
        """ Encrypts the object's own password unless it is encrypted already. This is the password
        that a channel or connection carries itself, not the one of a security definition it points to.
        """
        if password := input.get('password'):
            if not password.startswith(SECRETS.PREFIX):
                input['password'] = self.server.encrypt(password)

# ################################################################################################################################

    def _normalize_as2_fields(self, input):
        """ Casts the numeric AS2 fields to integers - a Dashboard form submits them as strings,
        and normalizing here means both the stored value and the published config event carry a number.
        """
        if input.transport != URL_TYPE.AS2:
            return

        if value := input.get('as2_duplicate_window_days'):
            input['as2_duplicate_window_days'] = int(value)

# ################################################################################################################################

    def _get_channel_service(self, session:'any_', input:'any_', is_ext:'bool') -> 'any_':
        """ Returns the service a channel routes to. For external-database objects, the service is validated
        against the main ODB and then mirrored in the external database so the foreign key holds.
        """
        if not is_ext:
            out = self._get_channel_service_from_input(session, input)
            return out

        with closing(self.odb.session()) as odb_session:
            service = self._get_channel_service_from_input(odb_session, input)

        if not service:
            return None

        out = ensure_service_copy(session, service.name, service.impl_name, input.cluster_id)
        return out

# ################################################################################################################################

    def _get_security_info(self, session:'any_', input:'any_', is_ext:'bool') -> 'any_':
        """ Returns security-related information for the input object. Security definitions always live
        in the main ODB - for external-database objects they are validated there and mirrored
        in the external database so AS2/AS4 rows can reference them by id.
        """
        if not is_ext:
            out = self._handle_security_info(session, input.security_id, input.connection, input.transport)
            return out

        with closing(self.odb.session()) as odb_session:
            out = self._handle_security_info(odb_session, input.security_id, input.connection, input.transport)

            if input.security_id:
                sec_def = odb_session.query(SecurityBase).filter(SecurityBase.id == input.security_id).one()
                ensure_security_copy(session, sec_def, input.cluster_id)

        return out

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
