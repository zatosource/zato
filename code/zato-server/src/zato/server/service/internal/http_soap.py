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
from zato.common.api import AS2, AS4, CONNECTION, DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, \
     Groups, HTTP_SOAP, HTTP_SOAP_SERIALIZATION_TYPE, MISC, PARAMS_PRIORITY, query_parameters, SCHEDULER, SEC_DEF_TYPE, \
     SchedulerLink, URL_PARAMS_PRIORITY, URL_TYPE, ZATO_NONE
from zato.common.broker_message import CHANNEL, OUTGOING
from zato.common.const import SECRETS
from zato.common.defaults import default_cluster_id
from zato.common.exception import ServiceMissingException
from zato.common.ext_db.api import ensure_security_copy, ensure_service_copy, get_ext_db_session, is_ext_db_configured, \
     is_ext_object_id, merge_ext_channel_items, needs_ext_db, to_local_id, to_public_id
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import Cluster, HTTPSOAP, Job, SecurityBase, Service
from zato.common.rate_limiting.cidr import SlottedCIDRRule
from zato.common.odb.query import http_soap, http_soap_list
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool, utcnow
from zato.common.util.imap_scheduler import interval_from_unit
from zato.common.util.rest_invocation import parse_param_rows, update_linked_job_fields, validate_jsonata, validate_xpath
from zato.common.util.sql import elems_with_opaque, get_dict_with_opaque, get_security_by_id, parse_instance_opaque_attr, \
     set_instance_opaque_attrs
from zato.server.connection.http_soap import BadRequest
from zato.server.service import AsIs, Boolean
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, anylist, intnone, strdict, strintdict

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

# ################################################################################################################################
# ################################################################################################################################

# All the AS4 fields, each optional on input - the boolean one is declared separately below.
_as4_fields = []

for _as4_field_name in AS4.Common_Fields + AS4.Channel_Fields + ('as4_sml_domain',):
    _as4_fields.append('-' + _as4_field_name)

_as4_fields = tuple(_as4_fields)
_as4_input = _as4_fields + (Boolean('-as4_use_discovery'),)

# All the AS2 fields, each optional on input.
_as2_fields = []

for _as2_field_name in AS2.Common_Fields + AS2.Channel_Fields:
    _as2_fields.append('-' + _as2_field_name)

_as2_input = tuple(_as2_fields)

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

def _has_scheduler_config(service:'AdminService', input:'Bunch') -> 'bool':
    """ Returns True if the scheduler fields were given on input, raising an error if only some of them were.
    """
    run_every = input.scheduler_run_every
    start_date = input.scheduler_start_date

    # Collect the core fields that were actually filled in
    given = []

    for value in (run_every, start_date):
        if value:
            given.append(value)

    given_count = len(given)

    # Nothing was given, which means that no job is expected to exist
    if not given_count:
        return False

    # Only some of the fields were given, which we cannot accept
    if given_count != 2:
        raise BadRequest(service.cid, 'Scheduler options require both run-every and start date to be given')

    return True

# ################################################################################################################################

def _has_health_check_config(service:'AdminService', input:'Bunch') -> 'bool':
    """ Returns True if the health check fields were given on input, raising an error if only some of them were.
    """
    run_every = input.health_check_run_every
    callback_type = input.health_check_callback_type
    callback_name = input.health_check_callback_name

    # Collect the core fields that were actually filled in
    given = []

    for value in (run_every, callback_type, callback_name):
        if value:
            given.append(value)

    given_count = len(given)

    # Nothing was given, which means that no job is expected to exist
    if not given_count:
        return False

    # Only some of the fields were given, which we cannot accept
    if given_count != 3:
        raise BadRequest(service.cid, 'Health check options require run-every, callback type and callback name together')

    return True

# ################################################################################################################################

def _validate_run_every(service:'AdminService', run_every:'any_', run_unit:'str', label:'str') -> 'int':
    """ Makes sure a run-every value and its unit describe a job interval that can be created.
    """
    run_every = int(run_every)

    if run_every < 1:
        raise BadRequest(service.cid, f'{label} run-every must be a positive integer instead of `{run_every}`')

    if run_unit not in _invocation.UnitList:
        raise BadRequest(service.cid, f'{label} unit `{run_unit}` is not one of `{_invocation.UnitList}`')

    return run_every

# ################################################################################################################################

def _validate_invocation_config(service:'AdminService', input:'Bunch') -> 'None':
    """ Validates the declarative invocation profile of an outgoing REST or SOAP connection,
    compiling every expression so syntax errors are rejected at config time instead of at call time.
    """

    # Each JSONata-mode row value must compile ..
    for field_name in _row_fields:
        if rows_json := input.get(field_name):
            rows = parse_param_rows(rows_json)
            for row in rows:
                mode = row['mode']
                if mode not in _invocation.ValueModeList:
                    raise BadRequest(service.cid, f'Value mode `{mode}` in `{field_name}` is not one of `{_invocation.ValueModeList}`')
                if mode == _invocation.ValueMode.JSONata:
                    _validate_expression(service, row['value'], _invocation.ValueMode.JSONata, field_name)

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
    _validate_callback(service, input.health_check_callback_type, input.health_check_callback_name,
        _health_check.Field_Callback_Type)

    # .. the scheduler fields must describe a job that can be created ..
    if _has_scheduler_config(service, input):
        input.scheduler_run_every = _validate_run_every(
            service, input.scheduler_run_every, input.scheduler_run_unit, 'Scheduler')

    # .. and so must the health check fields.
    if _has_health_check_config(service, input):
        input.health_check_run_every = _validate_run_every(
            service, input.health_check_run_every, input.health_check_run_unit, 'Health check')

        notify_on = input.health_check_notify_on
        if not notify_on:
            notify_on = _health_check.NotifyOn.Failures
        if notify_on not in _health_check.NotifyOnList:
            raise BadRequest(service.cid, f'Health check notify-on `{notify_on}` is not one of `{_health_check.NotifyOnList}`')

        # Store the normalized value back so a default is saved explicitly
        input.health_check_notify_on = notify_on

# ################################################################################################################################

def _get_linked_job(service:'AdminService', job_id:'int') -> 'any_':
    """ Returns the Job row of the given ID or None if it no longer exists.
    """
    with closing(service.odb.session()) as session:
        out = session.query(Job).filter_by(id=job_id).first()
        if out:
            session.expunge(out)

    return out

# ################################################################################################################################

def _preserve_job_ids(input:'Bunch', opaque:'any_') -> 'None':
    """ An empty job ID on input must not overwrite the one stored previously - the authoritative values
    are written back after the linked jobs are synchronized, once this request is committed.
    """
    for field_name in (_invocation.Field_Job_ID, _health_check.Field_Job_ID):
        if not input.get(field_name):
            if previous_job_id := opaque.get(field_name):
                input[field_name] = previous_job_id

# ################################################################################################################################

def _sync_one_linked_job(
    service,       # type: AdminService
    input,         # type: Bunch
    conn_id,       # type: int
    kind,          # type: str
    has_config,    # type: bool
    job_id,        # type: intnone
    job_name,      # type: str
    job_service,   # type: str
    start_date,    # type: str
    run_every,     # type: any_
    run_unit,      # type: str
    extra,         # type: str
    ) -> 'None':
    """ Creates, updates or deletes one scheduler job linked to a connection, based on the input just committed.
    """

    # The job the connection points to may or may not still exist,
    # e.g. it could have been deleted from the scheduler's own UI.
    job = None
    if job_id:
        job = _get_linked_job(service, job_id)

    # We are to keep a job in sync with what was given on input ..
    if has_config:

        # The connection's transport decides which config store the job's link points back to
        if input.transport == URL_TYPE.SOAP:
            link_conn_type = SchedulerLink.ConnType.SOAP_Outgoing
        else:
            link_conn_type = SchedulerLink.ConnType.REST_Outgoing

        request = {
            'cluster_id': default_cluster_id,
            'is_active': input.is_active,
            'job_type': SCHEDULER.JOB_TYPE.INTERVAL_BASED,
            'service': job_service,
            'start_date': start_date,
            'extra': extra,
            SchedulerLink.Conn_Type: link_conn_type,
            SchedulerLink.Conn_ID: conn_id,
            SchedulerLink.Kind: kind,
        }

        interval = interval_from_unit(run_every, run_unit)
        request.update(interval)

        # .. the job exists so it is updated in place, keeping its current name to honor renames done in the scheduler ..
        if job:
            request['id'] = job.id
            request['name'] = job.name
            _ = service.invoke('zato.scheduler.job.edit', request)
            new_job_id = job.id

        # .. otherwise, a new job is created for this connection ..
        else:
            request['name'] = job_name
            response = service.invoke('zato.scheduler.job.create', request)
            if 'id' not in response:
                response = response['zato_scheduler_job_create_response']
            new_job_id = response['id']

        # .. either way, the connection's opaque attributes now reflect the job's current state.
        with closing(service.odb.session()) as session:
            update_linked_job_fields(session, conn_id, kind, run_every, run_unit, start_date, new_job_id)

    # There is no configuration on input ..
    else:

        # .. so a job that still exists is deleted, which also clears the connection's linked-job fields.
        if job:
            _ = service.invoke('zato.scheduler.job.delete', {'id': job.id})

# ################################################################################################################################

def _sync_linked_jobs(service:'AdminService', input:'Bunch', conn_id:'int') -> 'None':
    """ Keeps the scheduled-invocation and health check jobs of an outgoing connection in sync
    with the input just committed.
    """

    # The declarative invocation job runs the connection through the shared dispatch service ..
    if input.transport == URL_TYPE.SOAP:
        job_prefix = _invocation.Job_Prefix_SOAP
    else:
        job_prefix = _invocation.Job_Prefix_REST

    scheduler_extra = dumps({
        _invocation.Extra_Conn_ID: conn_id,
        _invocation.Extra_Conn_Name: input.name,
        _invocation.Extra_Transport: input.transport,
    })

    _sync_one_linked_job(
        service,
        input,
        conn_id,
        kind=SchedulerLink.KindType.Scheduler,
        has_config=_has_scheduler_config(service, input),
        job_id=input.get(_invocation.Field_Job_ID),
        job_name=job_prefix + input.name,
        job_service=_invocation.Dispatch_Service,
        start_date=input.scheduler_start_date,
        run_every=input.scheduler_run_every,
        run_unit=input.scheduler_run_unit,
        extra=scheduler_extra,
    )

    # .. and the health check job pings the connection, delivering each outcome to the callback.
    if input.transport == URL_TYPE.SOAP:
        health_check_conn_type = SchedulerLink.ConnType.SOAP_Outgoing
    else:
        health_check_conn_type = SchedulerLink.ConnType.REST_Outgoing

    health_check_extra = dumps({
        _health_check.Extra_Conn_ID: conn_id,
        _health_check.Extra_Conn_Name: input.name,
        _health_check.Extra_Conn_Type: health_check_conn_type,
        _health_check.Field_Callback_Type: input.health_check_callback_type,
        _health_check.Field_Callback_Name: input.health_check_callback_name,
        _health_check.Field_Notify_On: input.health_check_notify_on,
    })

    # Health check jobs have no user-facing start date so they start right away
    health_check_start_date = utcnow().isoformat()

    _sync_one_linked_job(
        service,
        input,
        conn_id,
        kind=SchedulerLink.KindType.HealthCheck,
        has_config=_has_health_check_config(service, input),
        job_id=input.get(_health_check.Field_Job_ID),
        job_name=_health_check.Job_Prefix + input.name,
        job_service=_health_check.Dispatch_Service,
        start_date=health_check_start_date,
        run_every=input.health_check_run_every,
        run_unit=input.health_check_run_unit,
        extra=health_check_extra,
    )

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
        Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', \
        '-data_encoding', '-username', '-is_wrapper', '-wrapper_type', AsIs('-security_groups'), '-security_group_count', \
        '-security_group_member_count', '-needs_security_group_names', Boolean('-validate_tls'), '-gateway_service_list', \
        '-transport', Boolean('-is_audit_log_active'), \
        *_invocation_input, \
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

class Get(_BaseGet):
    """ Returns information about an individual HTTP/SOAP object by its ID.
    """
    input = '-cluster_id', '-id', '-name'

    def handle(self):
        self.request.input.require_any('id', 'name')
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id

        # Ids arrive as strings and the external database check needs an integer
        if input_id := self.request.input.id:
            input_id = int(input_id)
        else:
            input_id = 0

        # Objects from the external AS2/AS4 database are looked up under their local ids there
        is_ext = is_ext_object_id(input_id)

        if is_ext:
            local_id = to_local_id(input_id)
        else:
            local_id = input_id

        with closing(self.server.get_config_session(object_id=input_id)) as session:
            item = http_soap(session, cluster_id, local_id, self.request.input.name)
            out = cast_('anydict', get_dict_with_opaque(item))

        # The object is known everywhere else under its offset id
        if is_ext:
            out['id'] = to_public_id(out['id'])

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
        Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', \
        '-data_encoding', '-username', '-is_wrapper', '-wrapper_type', AsIs('-security_groups'), '-security_group_count', \
        '-security_group_member_count', '-needs_security_group_names', Boolean('-validate_tls'), '-gateway_service_list', \
        '-connection', '-transport', Boolean('-is_audit_log_active'), \
        Boolean('-use_ws_addressing'), Boolean('-use_mtom'), '-body_credentials', '-tls_client_cert', '-tls_client_key', \
        *_invocation_input, \
        *_as4_input, \
        *_as2_input

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
        transport = self.request.input.transport

        # AS2/AS4 objects come from the external database when one is configured ..
        if needs_ext_db(transport):
            with closing(get_ext_db_session()) as session:
                data = self.get_data(session)

            for item in data:
                item['id'] = to_public_id(item['id'])

        else:
            with closing(self.odb.session()) as session:
                data = self.get_data(session)

            # .. lists without a transport filter combine both databases,
            # .. with the external one winning on name conflicts.
            if is_ext_db_configured():
                if not transport:
                    with closing(get_ext_db_session()) as session:
                        ext_data = self.get_data(session)

                    for item in ext_data:
                        item['id'] = to_public_id(item['id'])

                    merge_ext_channel_items(data, ext_data)

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
        """ Encrypts the AS4 private keys unless they are encrypted already.
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

class Create(_CreateEdit):
    """ Creates a new HTTP/SOAP connection.
    """
    input = 'name', 'url_path', 'connection', \
        '-service', '-service_id', AsIs('-security_id'), '-method', '-soap_action', '-soap_version', '-data_format', \
        '-host', '-ping_method', '-pool_size', Boolean('-merge_url_params_req'), '-url_params_pri', '-params_pri', \
        '-serialization_type', '-timeout', '-content_type', \
        Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', '-data_encoding', \
        '-is_active', '-transport', '-is_internal', '-cluster_id', \
        '-is_wrapper', '-wrapper_type', '-username', '-password', AsIs('-security_groups'), Boolean('-validate_tls'), \
        '-gateway_service_list', Boolean('-is_audit_log_active'), Boolean('-should_include_in_openapi'), \
        Boolean('-use_ws_addressing'), Boolean('-use_mtom'), '-body_credentials', '-tls_client_cert', '-tls_client_key', \
        *_invocation_input, \
        *_as4_input, \
        *_as2_input
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

        input.is_audit_log_active = input.get('is_audit_log_active', True)

        # Channels are included in OpenAPI documents unless the flag turns it off
        input.should_include_in_openapi = input.get('should_include_in_openapi', True)

        input.transport   = input.get('transport')   or URL_TYPE.PLAIN_HTTP
        input.cluster_id  = input.get('cluster_id')  or self.server.cluster_id
        input.data_format = input.get('data_format') or ''

        input.data_encoding = input.get('data_encoding') or 'utf-8'

        # AS4 private keys are stored encrypted
        self._encrypt_as4_secrets(input)

        # AS2 private keys are stored encrypted too
        self._encrypt_as2_secrets(input)

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
            input.ping_method = input_ping_method.strip() or DEFAULT_HTTP_PING_METHOD

        if input_content_type:
            input.content_type = input_content_type.strip()

        # The declarative invocation profile of an outgoing connection is validated
        # before anything is committed to the database.
        if _is_declarative(input):
            _validate_invocation_config(self, input)

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
                self.ensure_channel_is_unique(session,
                    input.url_path, input.http_accept, input.method, input.soap_action, input.cluster_id)

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
                item.pool_size = input.get('pool_size') or DEFAULT_HTTP_POOL_SIZE
                item.merge_url_params_req = input.get('merge_url_params_req') or True
                item.url_params_pri = input.get('url_params_pri') or URL_PARAMS_PRIORITY.DEFAULT
                item.params_pri = input.get('params_pri') or PARAMS_PRIORITY.DEFAULT
                item.serialization_type = input.get('serialization_type') or HTTP_SOAP_SERIALIZATION_TYPE.DEFAULT.id
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
                    _sync_linked_jobs(self, input, item_id)

                self.response.payload.id = public_id
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
        Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', '-data_encoding', \
        '-cluster_id', '-is_active', '-transport', \
        '-is_wrapper', '-wrapper_type', '-username', '-password', AsIs('-security_groups'), Boolean('-validate_tls'), \
        '-gateway_service_list', Boolean('-is_audit_log_active'), Boolean('-should_include_in_openapi'), \
        Boolean('-use_ws_addressing'), Boolean('-use_mtom'), '-body_credentials', '-tls_client_cert', '-tls_client_key', \
        *_invocation_input, \
        *_as4_input, \
        *_as2_input
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

        input.is_audit_log_active = input.get('is_audit_log_active', True)

        # Channels are included in OpenAPI documents unless the flag turns it off
        input.should_include_in_openapi = input.get('should_include_in_openapi', True)

        input.transport   = input.get('transport')   or URL_TYPE.PLAIN_HTTP
        input.cluster_id  = input.get('cluster_id')  or self.server.cluster_id
        input.data_format = input.get('data_format') or ''

        input.data_encoding = input.get('data_encoding') or 'utf-8'

        # AS4 private keys are stored encrypted
        self._encrypt_as4_secrets(input)

        # AS2 private keys are stored encrypted too
        self._encrypt_as2_secrets(input)

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
            input.ping_method = input_ping_method.strip() or DEFAULT_HTTP_PING_METHOD

        if input_content_type:
            input.content_type = input_content_type.strip()

        # The declarative invocation profile of an outgoing connection is validated
        # before anything is committed to the database.
        if _is_declarative(input):
            _validate_invocation_config(self, input)

        # AS2/AS4 objects are stored in the external database when one is configured,
        # under their local ids, without the offset they are known under everywhere else.
        is_ext = needs_ext_db(input.transport)

        if is_ext:
            local_id = to_local_id(int(input.id))
        else:
            local_id = input.id

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

            try:
                item = session.query(HTTPSOAP).filter_by(id=local_id).one()

                opaque = parse_instance_opaque_attr(item)

                old_name = item.name
                old_url_path = item.url_path
                old_soap_action = item.soap_action
                old_http_method = item.method
                old_http_accept = opaque.get('http_accept')

                # An empty job ID on input must not overwrite the one stored previously
                if _is_declarative(input):
                    _preserve_job_ids(input, opaque)

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
                    _sync_linked_jobs(self, input, item.id)

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
                        if _get_linked_job(self, job_id):
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

    def handle(self):

        # Objects from the external AS2/AS4 database are stored under their local ids there
        input_id = int(self.request.input.id)

        if is_ext_object_id(input_id):
            local_id = to_local_id(input_id)
        else:
            local_id = input_id

        with closing(self.server.get_config_session(object_id=input_id)) as session:
            item = session.query(HTTPSOAP).filter_by(id=local_id).one()
            config_dict = getattr(self.outgoing, item.transport)
            self.response.payload.id = self.request.input.id

            wrapper = config_dict.get(item.name)

            try:
                result = wrapper.ping(self.cid, ping_path=self.request.input.ping_path)
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

        # API key definitions keep a placeholder username in the ODB while the actual
        # header name is an opaque attribute of the definition, so it is resolved here.
        if sec_def.sec_type == SEC_DEF_TYPE.APIKEY:
            opaque = parse_instance_opaque_attr(sec_def)
            header = opaque.get('header') or self.server.api_key_header
            username = header

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

            # The channel side already records this traffic in its own audit log
            'is_internal': True,
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
