# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from copy import deepcopy
from uuid import uuid4

# Zato
from zato.common.api import AS2, Audit_Config, FileTransfer, GENERIC as COMMON_GENERIC, HL7, HTTP_SOAP, KAFKA, \
    SchedulerLink, SEC_DEF_TYPE, Sec_Def_Type_Name, SMS, ZATO_NONE
from zato.common.alerting import config_map
from zato.common.alerting.object_config import conn_type_to_alert_type, get_field_kinds as get_alert_field_kinds, \
    storage_name as alert_storage_name
from zato.common.alerting.validate_numbers import Number_Kinds as Alert_Number_Kinds
from zato.common.audit_log.common import AuditEvent, Export_Payload_Flag as _audit_export_payload_field
from zato.common.broker_message import GENERIC
from zato.common.const import SECRETS
from zato.common.exception import BadRequest
from zato.common.hl7.exception import HL7Exception
from zato.common.hl7.fhir.fields import Outgoing_Int_Names as FHIR_Outgoing_Int_Names
from zato.common.hl7.mllp.fields import Channel_Int_Names as MLLP_Channel_Int_Names, \
    Channel_Rest_Channel_Id_Key as MLLP_Rest_Channel_Id_Key, Channel_Text_Names as MLLP_Channel_Text_Names, \
    Outgoing_Int_Names as MLLP_Outgoing_Int_Names
from zato.common.hl7.mllp.tls import validate_client_paths as validate_mllp_client_paths
from zato.common.ext_db.api import is_ext_object_id, needs_ext_db, to_local_id, to_public_id
from zato.common.json_internal import loads
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.sms.config import apply_outgoing_host_default, Channel_Int_Field_Names as SMS_Channel_Int_Names, \
    Outgoing_Int_Field_Names as SMS_Outgoing_Int_Names, validate_channel_definition as validate_sms_channel, \
    validate_outgoing_definition as validate_sms_outgoing
from zato.common.typing_ import cast_
from zato.common.util.api import asbool, parse_simple_type
from zato.common.util.delivery_config import apply_delivery_defaults, Delivery_Int_Fields, validate_delivery_fields
from zato.common.util.sql import parse_instance_opaque_attr
from zato.common.util.gateway import on_mcp_gateway_create_edit, on_mcp_gateway_delete
from zato.common.util.rule_engine_api import on_rule_engine_api_create_edit, on_rule_engine_api_delete
from zato.server.config_audit import get_model_snapshot, record_service_config_change
from zato.server.generic.api.channel_hl7_mllp import clear_other_default_channels as clear_other_mllp_default_channels, \
    delete_rest_channel as delete_mllp_rest_channel
from zato.server.generic.api.outconn_sdk import get_secret_field_names
from zato.server.generic.connection import GenericConnection
from zato.server.service.internal import AdminService, ChangePasswordBase
from zato.server.service.internal.channel.sms_jobs import delete_poll_job as delete_sms_poll_job, \
    sync_poll_job as sync_sms_poll_job, validate_poll_schedule as validate_sms_poll_schedule
from zato.server.service.internal.generic import _BaseService
from zato.server.service.internal.generic.alert_settings import prepare_generic_alert_settings
from zato.server.service.internal.health_check import delete_health_check_job, has_bulk_export_config, has_health_check_config, \
    sync_bulk_export_job, sync_health_check_job, validate_run_every
from zato.server.service.internal.outgoing.file_transfer.schedule import delete_connection_jobs, resync_connection_jobs
from zato.server.service.meta import DeleteMeta

# Python 2/3 compatibility
from six import add_metaclass

# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, anylist, strdict
    from zato.server.service import Service

    anylist = anylist
    Bunch = Bunch
    Service = Service

# ################################################################################################################################

elem = 'generic_connection'
model = ModelGenericConn
label = 'a generic connection'
broker_message = GENERIC
broker_message_prefix = 'CONNECTION_'
list_func = None
extra_delete_attrs = ['type_']

# ################################################################################################################################

_health_check = HTTP_SOAP.HealthCheck
_bulk = HL7.BulkExport

# The generic connection types that carry a health check job, each with the connection type its job links back to
_health_check_link_types = {
    COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: SchedulerLink.ConnType.FHIR_Outgoing,
}

# The generic connection types that carry a bulk export job - FHIR connections alone
_bulk_export_link_types = {
    COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: SchedulerLink.ConnType.FHIR_Outgoing,
}

# ################################################################################################################################

def on_kafka_create_edit(service:'Service', data:'Bunch', model:'any_', old_name:'any_') -> 'None':
    """ Checks that a Kafka connection's SASL mechanism and its security definition go together.
    """
    sasl_mechanism = data.get('sasl_mechanism')
    security_id = data.get('security_id')

    if not sasl_mechanism:
        if security_id:
            raise BadRequest(service.cid, 'A Kafka security definition requires a SASL mechanism')
        return

    if not security_id:
        raise BadRequest(service.cid, f'Kafka SASL mechanism `{sasl_mechanism}` requires a security definition')

    if sasl_mechanism not in KAFKA.Mechanism_Sec_Def_Type:
        raise BadRequest(service.cid, f'Unsupported Kafka SASL mechanism -> `{sasl_mechanism}`')

    expected_auth_type = KAFKA.Mechanism_Sec_Def_Type[sasl_mechanism]
    auth_type = data['auth_type']

    if auth_type != expected_auth_type:
        expected_name = Sec_Def_Type_Name[expected_auth_type]
        actual_name = Sec_Def_Type_Name[auth_type]
        msg = f'Kafka SASL mechanism `{sasl_mechanism}` requires a {expected_name} security definition, ' + \
            f'not {actual_name}'
        raise BadRequest(service.cid, msg)

# ################################################################################################################################

def on_mllp_outgoing_create_edit(service:'Service', data:'Bunch', model:'any_', old_name:'any_') -> 'None':
    """ Checks that an HL7 MLLP outgoing connection's client certificate comes with a CA bundle.
    """
    try:
        validate_mllp_client_paths(data)
    except HL7Exception as e:
        raise BadRequest(service.cid, str(e))

# ################################################################################################################################

def prepare_sms_outgoing(service:'Service', data:'Bunch') -> 'None':
    """ Checks the provider-dependent fields of an outgoing SMS connection and fills in the provider's host,
    before the connection's opaque attributes are built out of the input.
    """
    try:
        validate_sms_outgoing(data)
    except ValueError as e:
        raise BadRequest(service.cid, str(e))

    apply_outgoing_host_default(data)

# ################################################################################################################################

def on_sms_channel_create_edit(service:'Service', data:'Bunch', model:'any_', old_name:'any_') -> 'None':
    """ Checks that an SMS channel names an outgoing SMS connection that exists along with a service and a receive mode.
    """
    try:
        validate_sms_channel(data)
    except ValueError as e:
        raise BadRequest(service.cid, str(e))

    outconn_name = data[SMS.Field_Outconn_Name]

    with closing(service.odb.session()) as session:
        outconn = session.query(ModelGenericConn).\
            filter(ModelGenericConn.type_==COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SMS).\
            filter(ModelGenericConn.name==outconn_name).\
            first()

    if not outconn:
        raise BadRequest(service.cid, f'Outgoing SMS connection `{outconn_name}` does not exist')

# ################################################################################################################################

# The generic connection types that carry the queue switch and the DLQ settings
_delivery_settings_types = (
    COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA,
    COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_SMS,
    COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP,
    COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA,
    COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SMS,
)

# The generic connection types that are channels without a queue in front of them - an SMS channel keeps its queue switch
_channel_delivery_types = (
    COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA,
)

def prepare_delivery_settings(service:'Service', data:'Bunch') -> 'None':
    """ Fills in and validates the delivery settings of a connection being written.
    """
    apply_delivery_defaults(data)

    # A channel has no queue in front of it.
    if data['type_'] in _channel_delivery_types:
        data[HTTP_SOAP.Queue.Field_Use_Queue] = False

    try:
        validate_delivery_fields(data)
    except ValueError as e:
        raise BadRequest(service.cid, str(e))

# ################################################################################################################################

hook = {
    COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA: on_kafka_create_edit,
    COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_SMS: on_sms_channel_create_edit,
    COMMON_GENERIC.CONNECTION.TYPE.GATEWAY_MCP: on_mcp_gateway_create_edit,
    COMMON_GENERIC.CONNECTION.TYPE.GATEWAY_RULE_ENGINE: on_rule_engine_api_create_edit,
    COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP: on_mllp_outgoing_create_edit,
    COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA: on_kafka_create_edit,
}

# ################################################################################################################################

def instance_hook(service:'Service', input:'Bunch', instance:'any_', attrs:'any_') -> 'None':
    """ Called before delete commit. Cleans up the HTTPSOAP channel for MCP and Rule engine API connections.
    """
    if instance.type_ == COMMON_GENERIC.CONNECTION.TYPE.GATEWAY_MCP:
        on_mcp_gateway_delete(service, attrs._meta_session, instance.name, instance.cluster_id)

    elif instance.type_ == COMMON_GENERIC.CONNECTION.TYPE.GATEWAY_RULE_ENGINE:
        on_rule_engine_api_delete(service, instance.name)

# ################################################################################################################################

def delete_hook(service:'Service', input:'Bunch', instance:'any_', attrs:'any_') -> 'None':
    """ Called after delete commit. The deletion lands in the audit trail
    with what the connection looked like when it was removed.
    """

    # File transfer schedules go away with their connection - each one has a linked scheduler job
    # that would otherwise keep firing against a connection that no longer exists ..
    if instance.type_ in FileTransfer.ConnTypeList:
        delete_connection_jobs(service, instance)

    # .. and so does the health check job of a connection that has one.
    if instance.type_ in _health_check_link_types:
        opaque = parse_instance_opaque_attr(instance)
        delete_health_check_job(service, opaque.get(_health_check.Field_Job_ID))

    # .. as does the bulk export job of a FHIR connection ..
    if instance.type_ in _bulk_export_link_types:
        opaque = parse_instance_opaque_attr(instance)
        delete_health_check_job(service, opaque.get(_bulk.Field_Job_ID))

    # .. and the polling job of an SMS channel ..
    if instance.type_ == COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_SMS:
        opaque = parse_instance_opaque_attr(instance)
        delete_sms_poll_job(service, opaque)

    # .. and the REST channel backing an HL7 MLLP one, which is deleted here, once, rather than by each worker's
    # teardown of the channel's wrapper - the same teardown an edit runs, which keeps that channel.
    if instance.type_ == COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP:
        opaque = parse_instance_opaque_attr(instance)
        delete_mllp_rest_channel(service, opaque.get(MLLP_Rest_Channel_Id_Key))

    before_snapshot = get_model_snapshot(instance)

    record_service_config_change(
        service,
        action=AuditEvent.Config_Deleted,
        object_type=Audit_Config.Object_Type.Generic_Connection,
        object_name=instance.name,
        before=before_snapshot,
    )

# ################################################################################################################################

sec_def_sep = '/'

# ################################################################################################################################

extra_secret_keys = (

    #
    # Dropbox
    #
    'oauth2_access_token',

    # Salesforce
    'consumer_key',
    'consumer_secret',

    # OData, Microsoft Fabric and Microsoft Power Automate
    'client_secret',

    # Kafka
    KAFKA.Field_SSL_Key_Password,

    # SMS
    SMS.Field_Signature_Secret,

    # Discord and Slack
    'token',

)

# Keys that hold secrets - they are never returned in listings, no matter whether their values
# are stored in clear text or encrypted, because the browser must never receive them at all.
never_returned_keys = ('secret', 'secret_value', 'password') + extra_secret_keys + AS2.Secret_Fields

# Note that this is a set, unlike extra_secret_keys, because we do not make it part of I/O.
extra_simple_type = {
    'is_active',
}

# This key should be left as they are given on input, without trying to parse them into non-string types.
skip_simple_type = {
    'api_version',
    'group_id',
    'odata_version',

    # Connection names must stay strings even when they look numeric, e.g. a channel named 123.
    'name',

    # Hosts, addresses and usernames must stay strings even when they are all-digit
    'host',
    'address',
    'username',

    # Secrets and API keys must stay strings too - an all-digit key would otherwise
    # arrive as an integer and encryption works only with text.
    'secret',

    # AS2 fields that must stay strings even when their values look numeric -
    # the version travels as the AS2-Version HTTP header and the identifiers
    # and EDI addressing fields are frequently all-digit strings.
    'as2_version',
    'as2_from',
    'as2_to',
    'subject',
    'isa_qualifier',
    'isa_id',
    'gs_id',
    'unb_id',
    'as2_partner_next_cert_from',

    # PEM keys and certificates are always strings - running them through the literal
    # parser would only make the compiler emit SyntaxWarning on key material that
    # happens to contain digits-then-letters tokens.
    'as2_partner_cert',
    'as2_partner_next_cert',
    'as2_signing_key',
    'as2_signing_cert_chain',
    'as2_decryption_key',
    'as2_next_decryption_key',
    'as2_next_decryption_cert',
    'as2_peer_signing_cert',
    'as2_peer_encryption_cert',
    'as2_trust_anchors',
    'as4_signing_key',
    'as4_signing_cert_chain',
    'as4_decryption_key',
    'as4_saml_assertion',
    'as4_peer_signing_cert',
    'as4_peer_encryption_cert',
    'as4_trust_anchors',

    # Kafka fields that are text even when they look like a number, a boolean or JSON - acks of `1` or `0`
    # are what Kafka calls these settings, not a count or a flag
    'topic',
    KAFKA.Producer.Field_Acks,
    KAFKA.Consumer.Field_Topics,
    KAFKA.Consumer.Field_Routing,
    KAFKA.Consumer.Field_Dedup_Header,
    HTTP_SOAP.DLQ.Field_Forward_To,
}

# The text fields of an HL7 MLLP channel stay text whatever they are spelled like
skip_simple_type.update(MLLP_Channel_Text_Names)

# The alert settings that are text - a status codes list of `500` alone, an outcome codes list or an ack codes
# list of `AE` must stay what was typed rather than turn into a number or a boolean on the way, and the
# silence slots are a JSON text that is stored as one rather than the list it reads as.
for _alert_text_field_name in (config_map.Status_Codes_Field_Name, config_map.Fault_Codes_Field_Name,
    config_map.Outcome_Codes_Field_Name, config_map.Ack_Codes_Field_Name, config_map.Silence_Slots_Field_Name):
    skip_simple_type.add(alert_storage_name(_alert_text_field_name))

# The alert settings that are numbers - a threshold of 1 is a count, which the simple-type parser
# would otherwise turn into a boolean.
alert_number_keys:'set[str]' = set()

for _alert_type in set(conn_type_to_alert_type.values()):
    for _alert_field_name, _alert_field_kind in get_alert_field_kinds(_alert_type).items():
        if _alert_field_kind in Alert_Number_Kinds:
            alert_number_keys.add(alert_storage_name(_alert_field_name))

# ################################################################################################################################

# Values of these generic attributes should be converted to ints. The HL7 MLLP channel's and
# outgoing connection's counts, sizes, timeouts and ids are among them, as are the FHIR outgoing connection's
# retry and DLQ counts, because they travel as opaque attributes rather than as columns of their own,
# so nothing else says they are numbers.
int_attrs = ['pool_size', 'ping_interval', 'pings_missed_threshold', 'socket_read_timeout', 'socket_write_timeout']
int_attrs = int_attrs + list(MLLP_Channel_Int_Names) + list(MLLP_Outgoing_Int_Names) + list(FHIR_Outgoing_Int_Names)

# The Kafka integer fields
int_attrs = int_attrs + list(KAFKA.Consumer.IntFieldList) + list(KAFKA.Producer.IntFieldList) + list(Delivery_Int_Fields)

# The SMS integer fields
int_attrs = int_attrs + list(SMS_Outgoing_Int_Names) + list(SMS_Channel_Int_Names)
int_attrs = int_attrs + [
    HTTP_SOAP.Retry.Field_Max_Retries,
    HTTP_SOAP.Retry.Field_Sleep_Time,
    HTTP_SOAP.Retry.Field_Backoff_Threshold,
    HTTP_SOAP.Retry.Field_Backoff_Multiplier,
]

# ################################################################################################################################

def ensure_ints(data:'strdict') -> 'None':

    for name in int_attrs:
        value = data.get(name)

        # A one or a zero reaches this point as a bool because that is what the simple-type parser
        # makes of it, and a count of one is a count rather than a yes.
        if isinstance(value, bool):
            data[name] = int(value)
            continue

        try:
            value = int(value) if value else value
        except ValueError:
            pass # Not an integer
        else:
            data[name] = value

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(_BaseService):
    """ Creates a new or updates an existing generic connection in ODB.
    """
    is_create: 'bool'
    is_edit:   'bool'

    output = 'id', 'name'

# ################################################################################################################################

    def handle(self) -> 'None':

        data = deepcopy(self.request.input)

        self.logger.info('GenericConn _CreateEdit step 1: is_create=%s, is_edit=%s, data.keys=%s',
            self.is_create, self.is_edit, sorted(data.keys()))
        self.logger.info('GenericConn _CreateEdit step 1b: type_=%s, name=%s',
            data.get('type_'), data.get('name'))

        raw_request = self.request.raw
        if isinstance(raw_request, (str, bytes)):
            raw_request = loads(raw_request)

        # The connection type arrives either through the declared input or in the raw request
        type_ = data.get('type_')
        if not type_:
            type_ = raw_request.get('type_', '')

        # Secret fields declared by hot-deployed connector types are encrypted like the built-in ones
        # and, like the built-in ones, their values always stay strings.
        sdk_secret_keys = get_secret_field_names(self.server.config_manager, type_)
        secret_keys = extra_secret_keys + sdk_secret_keys
        skip_keys = skip_simple_type | set(sdk_secret_keys)

        for key, value in raw_request.items():

            if key not in data:
                if key not in skip_keys:
                    value = parse_simple_type(value, convert_bool=key not in alert_number_keys)
                    value = self._io.eval_(key, value, self.server.encrypt)

            if key in secret_keys:
                if value is None:
                    value = 'auto.generic.{}'.format(uuid4().hex)
                value = self.crypto.encrypt(value)
                value = value.decode('utf8')

            if key in extra_simple_type:
                value = parse_simple_type(value)

            data[key] = value

        # AS2 private keys are pasted as PEM and stored encrypted, unless they arrive encrypted already,
        # e.g. when an edit sends back the values a previous save produced.
        if data.get('type_') == COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_AS2:
            for name in AS2.Secret_Fields:
                if value := data.get(name):
                    if not value.startswith(SECRETS.PREFIX):
                        data[name] = self.server.encrypt(value)

        # Build a reusable flag indicating that a secret was sent on input. This is checked only after the
        # raw_request merge above because the plaintext secret arrives in the raw request, not in self.request.input.
        secret = data.get('secret', ZATO_NONE)
        if (secret is None) or (secret == ZATO_NONE) or (secret == ''):
            has_input_secret  = False
            input_secret = ''
        else:
            has_input_secret = True
            # Encrypt with the well-known prefix included - this is what lets
            # self.server.decrypt recognize the value as encrypted later on.
            input_secret = self.server.encrypt(secret)

        # If the is_active flag does exist but it is None, it should be treated as though it was set to False,
        # which is needed because None would be treated as NULL by the SQL database.
        if 'is_active' in data:
            if data['is_active'] is None:
                data['is_active'] = False

        # Make sure that specific keys are integers
        ensure_ints(data)

        if data.get('type_') in _delivery_settings_types:
            prepare_delivery_settings(self, data)

        if data.get('type_') == COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SMS:
            prepare_sms_outgoing(self, data)

        # The cluster ID may be missing on input, e.g. in API calls that give only the object's ID,
        # or it may have been turned into a bool by the simple-type parser above (1 becomes True),
        # so it is always set to our own server's cluster here.
        data['cluster_id'] = self.server.cluster_id

        self.logger.info('GenericConn _CreateEdit step 2: data after raw_request merge, keys=%s', sorted(data.keys()))
        self.logger.info('GenericConn _CreateEdit step 2b: type_=%s, is_active=%s, security_id=%s',
            data.get('type_'), data.get('is_active'), data.get('security_id'))

        # Break down security definitions into components
        security_id = data.get('security_id') or ''

        # ZATO_NONE means no security definition was selected.
        if security_id == ZATO_NONE:
            security_id = ''
            del data['security_id']

        # Some Dashboard views, e.g. HL7 MLLP channels and FHIR outgoing connections, send the ID
        # as a plain integer with no type prefix, in which case there are no components to break down.
        if isinstance(security_id, int):
            security_id = ''

        if sec_def_sep in security_id:

            # Extract the components ..
            sec_def_type, security_id = security_id.split(sec_def_sep)
            sec_def_type_name = Sec_Def_Type_Name[sec_def_type]

            security_id = int(security_id)

            # .. look up the security name by its ID ..
            if sec_def_type == SEC_DEF_TYPE.BASIC_AUTH:
                func = self.server.config_manager.basic_auth_get_by_id
            elif sec_def_type == SEC_DEF_TYPE.OAUTH:
                func = self.server.config_manager.oauth_get_by_id
            else:
                func = None

            if func:
                sec_def = func(security_id)
                security_name = sec_def.name
            else:
                security_name = 'unset'

            # .. potentially overwrites the security type with what we have here ..
            data['auth_type'] = sec_def_type

            # .. turns the ID into an integer but also remove the sec_type prefix,
            # .. e.g. 17 instead of 'oauth/17'.
            data['security_id'] = int(security_id)

            # .. and store everything else now.
            data['sec_def_type_name'] = sec_def_type_name
            data['security_name'] = security_name

        conn = GenericConnection.from_dict(data)

        self.logger.info('GenericConn _CreateEdit step 3: conn.type_=%s, conn.name=%s', conn.type_, conn.name)

        # A health check asked for must describe a job that can be created
        if data.type_ in _health_check_link_types:
            if has_health_check_config(data):
                run_every = validate_run_every(self, data[_health_check.Field_Run_Every], data[_health_check.Field_Run_Unit],
                    'Health check')
                data[_health_check.Field_Run_Every] = run_every
                conn.opaque[_health_check.Field_Run_Every] = run_every

        # The same goes for a bulk export schedule
        if data.type_ in _bulk_export_link_types:
            if has_bulk_export_config(data):
                run_every = validate_run_every(self, data[_bulk.Field_Run_Every], data[_bulk.Field_Run_Unit], 'Bulk export')
                data[_bulk.Field_Run_Every] = run_every
                conn.opaque[_bulk.Field_Run_Every] = run_every

        # .. and for the polling schedule of an SMS channel.
        if data.type_ == COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_SMS:
            validate_sms_poll_schedule(self, data)
            for name in SMS.Scheduler.FieldList:
                if name in data:
                    conn.opaque[name] = data[name]

        # AS2 outgoing connections are stored in the external database when one is configured,
        # under their local ids, without the offset they are known under everywhere else.
        is_ext = needs_ext_db(data.type_)

        with closing(self.server.get_config_session(object_type=data.type_)) as session:

            # If this is the edit action, we need to find our instance in the database
            # and we need to make sure that we publish its encrypted secret for other layers ..
            if self.is_edit:
                if is_ext:
                    local_id = to_local_id(int(data.id))
                else:
                    local_id = data.id
                model = self._get_instance_by_id(session, ModelGenericConn, local_id)

                # What the connection looked like before this edit - the config-audit
                # event compares it with the state the commit produces.
                before_snapshot = get_model_snapshot(model)

                # Private keys are never returned to the Dashboard, so an edit form cannot send them back.
                if data.get('type_') == COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_AS2:
                    model_opaque = parse_instance_opaque_attr(model)
                    for name in AS2.Secret_Fields:

                        # A key given on input is a new one and is stored as given ..
                        if data.get(name):
                            continue

                        # .. the staged next decryption key is cleared along with
                        # .. its certificate once a rotation completes ..
                        if name == 'as2_next_decryption_key':
                            if not data.get('as2_next_decryption_cert'):
                                continue

                        # .. and any other empty key on input means the stored one is kept.
                        if stored_value := model_opaque.get(name):
                            data[name] = stored_value
                            conn.opaque[name] = stored_value

                # File transfer schedules are managed on their own screen so an edit of the connection
                # itself must not lose them - the connection's edit form does not carry them.
                if data.get('type_') in FileTransfer.ConnTypeList:
                    model_opaque = parse_instance_opaque_attr(model)
                    if stored_schedules := model_opaque.get(FileTransfer.Scheduler.Schedules_Field):
                        data[FileTransfer.Scheduler.Schedules_Field] = stored_schedules
                        conn.opaque[FileTransfer.Scheduler.Schedules_Field] = stored_schedules

                # A connection that alerts keeps the alert settings the edit did not send, and its health check
                # job ID must not be lost to an edit that does not carry it, e.g. one that enmasse runs.
                if data.type_ in conn_type_to_alert_type:
                    model_opaque = parse_instance_opaque_attr(model)
                    self._apply_alert_settings(data, conn, model_opaque)

                if data.type_ in _health_check_link_types:
                    model_opaque = parse_instance_opaque_attr(model)
                    if not data.get(_health_check.Field_Job_ID):
                        if previous_job_id := model_opaque.get(_health_check.Field_Job_ID):
                            data[_health_check.Field_Job_ID] = previous_job_id
                            conn.opaque[_health_check.Field_Job_ID] = previous_job_id

                if data.type_ in _bulk_export_link_types:
                    model_opaque = parse_instance_opaque_attr(model)
                    if not data.get(_bulk.Field_Job_ID):
                        if previous_job_id := model_opaque.get(_bulk.Field_Job_ID):
                            data[_bulk.Field_Job_ID] = previous_job_id
                            conn.opaque[_bulk.Field_Job_ID] = previous_job_id

                # An SMS channel's polling job and poll state are the server's own and an edit never includes them
                if data.type_ == COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_SMS:
                    model_opaque = parse_instance_opaque_attr(model)
                    for name in (SMS.Scheduler.Field_Job_ID, SMS.Field_Poll_State):
                        if not data.get(name):
                            if stored_value := model_opaque.get(name):
                                data[name] = stored_value
                                conn.opaque[name] = stored_value

                # The audit export's payload flag is set through enmasse only and has no field in the Dashboard,
                # so an edit that does not carry it keeps what was stored.
                if _audit_export_payload_field not in data:
                    model_opaque = parse_instance_opaque_attr(model)
                    if stored_payload_flag := model_opaque.get(_audit_export_payload_field):
                        data[_audit_export_payload_field] = stored_payload_flag
                        conn.opaque[_audit_export_payload_field] = stored_payload_flag

                # Use the secret that was given on input because it may be a new one.
                # Otherwise, if no secret is given on input, it means that we are not changing it
                # so we can reuse the same secret that the model already uses.
                if has_input_secret:
                    secret = input_secret
                else:
                    secret = model.secret

                secret = self.server.decrypt(secret)
                conn.secret = secret
                data.secret = secret # We need to set it here because we also publish this message to other servers

            # .. but if it is the create action, we need to create a new instance
            # .. and ensure that its secret is stored - either the one given on input,
            # .. so that later edits without a secret can keep using it, or an auto-generated one.
            else:
                # The external database has its own cluster row that all its objects point to
                if is_ext:
                    model = ModelGenericConn()
                else:
                    model = self._new_zato_instance_with_cluster(ModelGenericConn)

                # A creation has no earlier state to compare with
                before_snapshot = {}

                # A new connection that alerts starts at its type's defaults for whatever the caller did not send
                if data.type_ in conn_type_to_alert_type:
                    self._apply_alert_settings(data, conn, {})

                if has_input_secret:
                    secret = input_secret
                else:
                    secret = self.crypto.generate_secret().decode('utf8')
                    secret = self.server.encrypt(SECRETS.Auto_Generated_Prefix + secret)
                    secret = cast_('str', secret)
                conn.secret = secret

                # The config event published below carries the secret the same way an edit's event does,
                # otherwise the connection wrapper would be built without one until the first edit.
                data['secret'] = secret

            conn_dict = conn.to_sql_dict()

            self.logger.info('GenericConn _CreateEdit step 4: conn_dict keys=%s', sorted(conn_dict.keys()))
            self.logger.info('GenericConn _CreateEdit step 4b: conn_dict type_=%s, name=%s, cluster_id=%s',
                conn_dict.get('type_'), conn_dict.get('name'), conn_dict.get('cluster_id'))

            # This will be needed in case this is a rename
            old_name = cast_('str', model.name)

            for key, value in sorted(conn_dict.items()):

                # If we are merely creating this connection, do not set the field unless a secret was sent on input.
                # If it is an edit, then we will have the secret either from the input or from the model,
                # which is why we do to enter this branch.
                if self.is_create:
                    if key == 'secret' and not (has_input_secret):
                        continue

                setattr(model, key, value)

            self.logger.info('GenericConn _CreateEdit step 5: about to session.add + commit, model.type_=%s, model.name=%s',
                getattr(model, 'type_', None), getattr(model, 'name', None))

            hook_func = hook.get(data.type_)
            if hook_func:
                hook_func(self, data, model, old_name)

            session.add(model)
            session.commit()

            instance = self._get_instance_by_name(session, ModelGenericConn, data.type_, data.name)

            self.logger.info('GenericConn _CreateEdit step 6: committed, instance.id=%s, instance.name=%s, instance.type_=%s',
                instance.id, instance.name, instance.type_)

            # What the connection looks like after the commit - the other side
            # of the config-audit comparison.
            after_snapshot = get_model_snapshot(instance)

            # Everyone else knows objects from the external database under their offset ids
            if is_ext:
                public_id = to_public_id(instance.id)
            else:
                public_id = instance.id

            self.response.payload.id = public_id
            self.response.payload.name = instance.name

            # File transfer schedules follow their connection's name - a rename rebuilds each linked job
            # so its name and extra data point to the connection under its new name.
            if self.is_edit:
                if instance.type_ in FileTransfer.ConnTypeList:
                    if old_name != instance.name:
                        resync_connection_jobs(self, instance)

        # The connection is committed by now so its health check job can be created, updated or deleted -
        # the job pings the connection and each ping lands in the audit log under the connection's health source.
        if data.type_ in _health_check_link_types:
            sync_health_check_job(self, data, public_id, _health_check_link_types[data.type_])

        # .. and so can its bulk export job, which starts an export on the tab's schedule.
        if data.type_ in _bulk_export_link_types:
            sync_bulk_export_job(self, data, public_id, _bulk_export_link_types[data.type_])

        # .. and so can the polling job of an SMS channel.
        if data.type_ == COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_SMS:
            sync_sms_poll_job(self, data, public_id)

        data['old_name'] = old_name
        data['action'] = GENERIC.CONNECTION_EDIT.value if self.is_edit else GENERIC.CONNECTION_CREATE.value
        data['id'] = public_id

        self.logger.info('GenericConn _CreateEdit step 7: publishing config event, action=%s, id=%s, type_=%s',
            data['action'], data['id'], data.get('type_'))

        self.config_dispatcher.publish(data)

        # Only one HL7 MLLP channel is the default, so the one saved with the flag takes it from any other
        if data.type_ == COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP:
            if 'is_default' in data:
                if asbool(data['is_default']):
                    clear_other_mllp_default_channels(self, data['name'])

        # The change lands in the audit trail - who changed what, with a before/after
        # summary of only the fields that differ and secrets masked.
        if self.is_edit:
            audit_action = AuditEvent.Config_Edited
        else:
            audit_action = AuditEvent.Config_Created

        record_service_config_change(
            self,
            action=audit_action,
            object_type=Audit_Config.Object_Type.Generic_Connection,
            object_name=data['name'],
            before=before_snapshot,
            after=after_snapshot,
        )

# ################################################################################################################################

    def _apply_alert_settings(self, data:'Bunch', conn:'GenericConnection', stored:'strdict') -> 'None':
        """ The alert settings of the connection being written - the ones sent as sent, the rest from the stored
        row or the type's defaults - land both in the data that is published and in the opaque attributes that are stored.
        """
        alert_settings = prepare_generic_alert_settings(self, data.type_, data, stored)

        for key, value in alert_settings.items():
            data[key] = value
            conn.opaque[key] = value

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    """ Creates a new generic connection.
    """
    is_create = True
    is_edit   = False

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    """ Updates an existing generic connection.
    """
    is_create = False
    is_edit   = True

# ################################################################################################################################
# ################################################################################################################################

@add_metaclass(DeleteMeta)
class Delete(AdminService):
    """ Deletes a generic connection.
    """

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the secret (password) of a generic connection.
    """
    password_required = False

# ################################################################################################################################

    def handle(self) -> 'None':

        def _auth(instance:'any_', secret:'str | bytes') -> 'None':
            if secret:

                # Always encrypt the secret given on input
                instance.secret = self.server.encrypt(secret)

        if self.request.input.id:
            instance_id = int(self.request.input.id)
        else:
            with closing(self.server.get_config_session(object_type=self.request.input.type_)) as session:
                instance_id = session.query(ModelGenericConn).\
                    filter(ModelGenericConn.name==self.request.input.name).\
                    filter(ModelGenericConn.type_==self.request.input.type_).\
                    one().id

            # Everyone else knows objects from the external database under their offset ids
            if needs_ext_db(self.request.input.type_):
                instance_id = to_public_id(instance_id)

        # Objects from the external AS2/AS4 database are stored under their local ids there
        if is_ext_object_id(instance_id):
            local_id = to_local_id(instance_id)
        else:
            local_id = instance_id

        # To ensure that the input ID is correct
        with closing(self.server.get_config_session(object_id=instance_id)) as session:
            query = session.query(ModelGenericConn)
            query = query.filter(ModelGenericConn.id==local_id)
            _ = query.one()

        # This step updates the secret.
        self._handle(ModelGenericConn, _auth, GENERIC.CONNECTION_CHANGE_PASSWORD.value, instance_id=instance_id,
            publish_instance_attrs=['type_'])

# ################################################################################################################################
# ################################################################################################################################
