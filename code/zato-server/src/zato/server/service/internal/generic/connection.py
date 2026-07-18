# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from copy import deepcopy
from datetime import datetime, timezone
from traceback import format_exc
from urllib.parse import parse_qsl
from uuid import uuid4

# Zato
from zato.common.api import AS2, Audit_Config, GENERIC as COMMON_GENERIC, generic_attrs, query_parameters, SEC_DEF_TYPE, \
     SEC_DEF_TYPE_NAME, ZATO_NONE
from zato.common.as2.rotation import complete_rotation, needs_rotation_completion
from zato.common.audit_log.common import AuditEvent
from zato.common.broker_message import GENERIC
from zato.common.const import SECRETS
from zato.common.ext_db.api import get_ext_db_session, is_ext_db_configured, is_ext_object_id, needs_ext_db, \
     to_local_id, to_public_id
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.odb.query.generic import connection_list
from zato.common.typing_ import cast_
from zato.common.util.api import parse_simple_type
from zato.common.util.config import replace_query_string_items_in_dict
from zato.common.util.gateway import on_mcp_gateway_create_edit, on_mcp_gateway_delete
from zato.common.util.time_ import utcnow
from zato.server.config_audit import get_model_snapshot, record_service_config_change
from zato.server.generic.connection import GenericConnection
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService, ChangePasswordBase
from zato.server.service.internal.generic import _BaseService
from zato.server.service.meta import DeleteMeta

# Python 2/3 compatibility
from six import add_metaclass

# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, anydict, anylist, strdict
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

hook = {
    COMMON_GENERIC.CONNECTION.TYPE.GATEWAY_MCP: on_mcp_gateway_create_edit,
}

# ################################################################################################################################

def instance_hook(service, input, instance, attrs):
    """ Called before delete commit. Cleans up the HTTPSOAP channel for MCP connections.
    """
    if instance.type_ == COMMON_GENERIC.CONNECTION.TYPE.GATEWAY_MCP:
        on_mcp_gateway_delete(service, attrs._meta_session, instance.name, instance.cluster_id)

# ################################################################################################################################

def delete_hook(service, input, instance, attrs):
    """ Called after delete commit. The deletion lands in the audit trail
    with what the connection looked like when it was removed.
    """
    before_snapshot = get_model_snapshot(instance)

    record_service_config_change(
        service,
        action=AuditEvent.Config_Deleted,
        object_type=Audit_Config.Object_Type.Generic_Connection,
        object_name=instance.name,
        before=before_snapshot,
    )

# ################################################################################################################################

config_dict_id_name_outconnn = {
    'ftp_source': 'out_ftp',
}

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

)

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
    'as4_peer_signing_cert',
    'as4_peer_encryption_cert',
    'as4_trust_anchors',
}

# ################################################################################################################################

# Values of these generic attributes should be converted to ints
int_attrs = ['pool_size', 'ping_interval', 'pings_missed_threshold', 'socket_read_timeout', 'socket_write_timeout']

# ################################################################################################################################

def ensure_ints(data:'strdict') -> 'None':

    for name in int_attrs:
        value = data.get(name)
        try:
            value = int(value) if value else value
        except ValueError:
            pass # Not an integer
        else:
            data[name] = value

# ################################################################################################################################

class _CreateEditIO:
    input_required = ('name', 'type_', 'is_active', 'is_internal', 'is_channel', 'is_outconn')
    input_optional = ('cluster_id', 'id', Int('pool_size'), Int('cache_expiry'), 'address', Int('port'), Int('timeout'),
        'data_format', 'version',
        'extra', 'username', 'username_type', 'secret', 'secret_type', 'conn_def_id', 'cache_id', AsIs('tenant_id'),
        AsIs('client_id'), AsIs('security_id')) + extra_secret_keys + generic_attrs
    force_empty_keys = True

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

        raw_request = self.request.raw_request
        if isinstance(raw_request, (str, bytes)):
            raw_request = loads(raw_request)

        for key, value in raw_request.items():

            if key not in data:
                if key not in skip_simple_type:
                    value = parse_simple_type(value)
                    value = self._io.eval_(key, value, self.server.encrypt)

            if key in extra_secret_keys:
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

        # The cluster ID may be missing on input, e.g. in API calls that give only the object's ID,
        # or it may have been turned into a bool by the simple-type parser above (1 becomes True),
        # so it is always set to our own server's cluster here.
        data['cluster_id'] = self.server.cluster_id

        self.logger.info('GenericConn _CreateEdit step 2: data after raw_request merge, keys=%s', sorted(data.keys()))
        self.logger.info('GenericConn _CreateEdit step 2b: type_=%s, is_active=%s, security_id=%s',
            data.get('type_'), data.get('is_active'), data.get('security_id'))

        # Break down security definitions into components
        security_id = data.get('security_id') or ''
        if sec_def_sep in security_id:

            # Extract the components ..
            sec_def_type, security_id = security_id.split(sec_def_sep)
            sec_def_type_name = SEC_DEF_TYPE_NAME[sec_def_type]

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
                if has_input_secret:
                    secret = input_secret
                else:
                    secret = self.crypto.generate_secret().decode('utf8')
                    secret = self.server.encrypt('auto.generated.{}'.format(secret))
                    secret = cast_('str', secret)
                conn.secret = secret

            conn_dict = conn.to_sql_dict()

            self.logger.info('GenericConn _CreateEdit step 4: conn_dict keys=%s', sorted(conn_dict.keys()))
            self.logger.info('GenericConn _CreateEdit step 4b: conn_dict type_=%s, name=%s, cluster_id=%s',
                conn_dict.get('type_'), conn_dict.get('name'), conn_dict.get('cluster_id'))

            # This will be needed in case this is a rename
            old_name = model.name

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

        data['old_name'] = old_name
        data['action'] = GENERIC.CONNECTION_EDIT.value if self.is_edit else GENERIC.CONNECTION_CREATE.value
        data['id'] = public_id

        self.logger.info('GenericConn _CreateEdit step 7: publishing config event, action=%s, id=%s, type_=%s',
            data['action'], data['id'], data.get('type_'))

        self.config_dispatcher.publish(data)

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

class GetList(AdminService):
    """ Returns a list of generic connections by their type; includes pagination.
    """
    _filter_by = ModelGenericConn.name,

    input = 'cluster_id', '-type_', *query_parameters

# ################################################################################################################################

    def get_data(self, session:'any_') -> 'any_':
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id
        self.logger.info('GenericConn GetList.get_data: cluster_id=%s, type_=%s', cluster_id, self.request.input.type_)
        data = self._search(connection_list, session, cluster_id, self.request.input.type_, False)
        self.logger.info('GenericConn GetList.get_data: result count=%s', data.count() if hasattr(data, 'count') else 'N/A')
        return data

# ################################################################################################################################

    def _add_custom_conn_dict_fields(self, conn_dict:'anydict') -> 'None':
        pass

# ################################################################################################################################

    def _enrich_conn_dict(self, conn_dict:'anydict') -> 'None':

        # Local aliases
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id

        # New items that will be potentially added to conn_dict
        to_add = {}

        # Mask out all the relevant attributes
        replace_query_string_items_in_dict(self.server, conn_dict)

        # Process all the items found in the database.
        for key, value in conn_dict.items():

            if value:

                if key.endswith('_service_id'):
                    prefix = key.split('_service_id')[0]
                    service_attr = prefix + '_service_name'
                    try:
                        service_name = self.invoke('zato.service.get-by-id', {
                            'cluster_id': cluster_id,
                            'id': value,
                        })['zato_service_get_by_name_response']['name']
                    except Exception:
                        pass
                    else:
                        conn_dict[service_attr] = service_name

                else:
                    for id_name_base, out_name in config_dict_id_name_outconnn.items():
                        item_id = '{}_id'.format(id_name_base)
                        if key == item_id:
                            config_dict = self.server.config.get_config_by_item_id(out_name, value)
                            item_name = '{}_name'.format(id_name_base)
                            to_add[item_name] = config_dict['name']

        # .. add custom fields that do not exist in the database ..
        self._add_custom_conn_dict_fields(conn_dict)

        # .. and hand the final result back to our caller.
        if to_add:
            conn_dict.update(to_add)

# ################################################################################################################################
# ################################################################################################################################

    def _append_conn_dicts(self, session:'any_', out:'anylist', needs_id_offset:'bool') -> 'None':

        search_result = self.get_data(session)

        for item in search_result:
            conn = GenericConnection.from_model(item)
            conn_dict = cast_('anydict', conn.to_dict())

            # Everyone else knows objects from the external database under their offset ids
            if needs_id_offset:
                conn_dict['id'] = to_public_id(conn_dict['id'])

            self._enrich_conn_dict(conn_dict)
            out.append(conn_dict)

# ################################################################################################################################

    def handle(self) -> 'None':
        out:'anylist' = []
        type_ = self.request.input.type_

        self.logger.info('GenericConn GetList.handle: type_=%s', type_)

        # AS2 outgoing connections come from the external database when one is configured ..
        is_ext = needs_ext_db(type_)

        with closing(self.server.get_config_session(object_type=type_)) as session:
            self._append_conn_dicts(session, out, is_ext)

        # .. lists without a type filter combine both databases.
        if is_ext_db_configured():
            if not type_:
                with closing(get_ext_db_session()) as session:
                    self._append_conn_dicts(session, out, True)

        self.logger.info('GenericConn GetList.handle: returning %s items for type_=%s', len(out), type_)

        self.response.payload = dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class GetByID(AdminService):
    """ Returns a single generic connection by its ID.
    """
    input = Int('id')

    def handle(self) -> 'None':

        input_id = self.request.input.id

        # Objects from the external AS2/AS4 database are stored under their local ids there ..
        if is_ext_object_id(input_id):
            local_id = to_local_id(input_id)
        else:
            local_id = input_id

        # .. look the connection up in the correct database ..
        with closing(self.server.get_config_session(object_id=input_id)) as session:
            query = session.query(ModelGenericConn)
            query = query.filter(ModelGenericConn.id==local_id)
            item = query.one()

            # .. turn the model into a dict ..
            conn = GenericConnection.from_model(item)
            conn_dict = cast_('anydict', conn.to_dict())

        # .. everyone else knows objects from the external database under their offset ids ..
        conn_dict['id'] = input_id

        # .. mask out all the relevant secret attributes ..
        replace_query_string_items_in_dict(self.server, conn_dict)

        # .. and return the connection to our caller.
        self.response.payload = dumps(conn_dict)

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the secret (password) of a generic connection.
    """
    password_required = False


# ################################################################################################################################

    def _run_pre_handle_tasks_CLOUD_MICROSOFT_365(self, session:'any_', instance:'any_') -> 'None':

        # Disabled, no longer in use
        return

        # stdlib
        from json import dumps, loads
        from urllib.parse import parse_qs, urlsplit

        # office-365
        from O365 import Account

        auth_url = self.request.input.password
        auth_url = self.server.decrypt(auth_url)

        query = urlsplit(auth_url).query
        parsed = parse_qs(query)

        state = parsed['state']
        state = state[0]

        opaque1 = instance.opaque1
        opaque1 = loads(opaque1)

        client_id = opaque1['client_id']
        secret_value = opaque1.get('secret_value') or opaque1.get('secret') or opaque1['password']

        credentials = (client_id, secret_value)

        account = Account(credentials)
        _ = account.con.request_token(authorization_url=auth_url, state=state)

        opaque1['token'] = account.con.token_backend.token
        opaque1 = dumps(opaque1)
        instance.opaque1 = opaque1

        session.add(instance)
        session.commit()

# ################################################################################################################################

    def _run_pre_handle_tasks(self, session:'any_', instance:'any_') -> 'None':
        conn_type = self.request.input.get('type_')

        if conn_type == COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365:
            self._run_pre_handle_tasks_CLOUD_MICROSOFT_365(session, instance)

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

        with closing(self.server.get_config_session(object_id=instance_id)) as session:
            query = session.query(ModelGenericConn)
            query = query.filter(ModelGenericConn.id==local_id)
            instance = query.one()

            # This steps runs optional post-handle tasks that some types of connections may require.
            self._run_pre_handle_tasks(session, instance)

        # This step updates the secret.
        self._handle(ModelGenericConn, _auth, GENERIC.CONNECTION_CHANGE_PASSWORD.value, instance_id=instance_id,
            publish_instance_attrs=['type_'])

# ################################################################################################################################
# ################################################################################################################################

class Ping(_BaseService):
    """ Pings a generic connection.
    """
    input = Int('id')
    output = 'info', '-is_success'

    def handle(self) -> 'None':

        # Objects from the external AS2/AS4 database are stored under their local ids there
        input_id = self.request.input.id

        if is_ext_object_id(input_id):
            local_id = to_local_id(input_id)
        else:
            local_id = input_id

        with closing(self.server.get_config_session(object_id=input_id)) as session:

            # To ensure that the input ID is correct
            instance = self._get_instance_by_id(session, ModelGenericConn, local_id)

            # Different code paths will be taken depending on what kind of a generic connection this is
            custom_ping_func_dict = {}

            # Most connections use a generic ping function, unless overridden on a case-by-case basis.
            ping_func = custom_ping_func_dict.get(instance.type_, self.server.config_manager.ping_generic_connection)

            start_time = utcnow()

            try:
                _ = ping_func(self.request.input.id)
            except Exception:
                exc = format_exc()
                self.logger.warning(exc)
                self.response.payload.info = exc
                self.response.payload.is_success = False
            else:
                response_time = utcnow() - start_time
                info = 'Connection pinged; response time: {}'.format(response_time)
                self.logger.info(info)
                self.response.payload.info = info
                self.response.payload.is_success = True

# ################################################################################################################################
# ################################################################################################################################

class Invoke(AdminService):
    """ Invokes a generic connection by its name.
    """
    input = 'conn_type', 'conn_name', '-request_data'
    output = '-response_data'

    def handle(self) -> 'None':

        # Local aliases
        response = None
        conn_type = self.request.input.conn_type
        request_data = self.request.input.request_data

        # Maps all known connection types to their implementation ..
        conn_type_to_container = {
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: self.server.config_manager.outconn_hl7_fhir,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP: self.server.config_manager.outconn_hl7_mllp,
        }

        # .. get the actual implementation ..
        container = conn_type_to_container[conn_type]

        # .. and invoke it.
        with container[self.request.input.conn_name].conn.client() as client:

            try:
                # FHIR connections treat the request as a path to GET, e.g. /Patient?_count=1 ..
                if conn_type == COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR:

                    # .. the query string, if any, must go to the client separately from the path ..
                    path, _, query = request_data.partition('?')
                    params = dict(parse_qsl(query))

                    response = client.execute(path=path, method='get', params=params)

                    # The response is JSON and the caller needs text
                    response = dumps(response, indent=2)

                # .. other connections, e.g. MLLP, send the request as a message.
                else:
                    response = client.invoke(request_data)

                    # Results are objects, e.g. an AckResult for MLLP, and the caller needs text
                    response = str(response)
            except Exception:
                exc = format_exc()
                response = exc
                self.logger.warning(exc)
            finally:
                self.response.payload.response_data = response

# ################################################################################################################################
# ################################################################################################################################

class InvokeGraphQL(_BaseService):
    """ Invokes a GraphQL outgoing connection with a query and optional variables.
    """
    name = 'zato.generic.connection.invoke-graphql'
    input = Int('id'), '-query', '-variables'
    output = '-response_data', '-response_time'

    def handle(self) -> 'None':

        import json
        import time

        from gql import Client as GQLClient
        from gql import gql as gql_parse
        from zato.server.connection.facade import GraphQLInvoker

        with closing(self.odb.session()) as session:
            instance = self._get_instance_by_id(session, ModelGenericConn, self.request.input.id)
            config = loads(instance.opaque1) if instance.opaque1 else {}
            config['address'] = instance.address
            config['extra'] = instance.extra

        query_text = self.request.input.get('query', '')
        variables_text = self.request.input.get('variables', '')

        if not query_text or not query_text.strip():
            raise Exception('No query provided')

        if variables_text and variables_text.strip():
            variables = json.loads(variables_text)
        else:
            variables = None

        transport = GraphQLInvoker._build_transport(config, self.server)
        client = GQLClient(transport=transport)

        parsed_query = gql_parse(query_text)

        execute_kwargs = {}
        if variables:
            execute_kwargs['variable_values'] = variables

        start = time.monotonic()

        try:
            with client as gql_session:
                result = gql_session.execute(parsed_query, **execute_kwargs)
        except Exception as e:
            elapsed = time.monotonic() - start
            self.response.payload.response_data = str(e)
            self.response.payload.response_time = f'{elapsed:.3f}s'
            raise Exception(str(e)) from None

        elapsed = time.monotonic() - start
        self.response.payload.response_data = json.dumps(result, indent=2)
        self.response.payload.response_time = f'{elapsed:.3f}s'

# ################################################################################################################################
# ################################################################################################################################

# The entries of a live connection's config dict that must not travel to the edit service -
# the live wrapper objects plus the values the config manager adds at runtime,
# with the secret left out so the edit keeps the one already stored.
_rotation_runtime_only_keys = ('conn', 'parent', 'secret', 'queue_build_cap', 'auth_url')

# ################################################################################################################################
# ################################################################################################################################

class CompleteAS2Rotation(AdminService):
    """ Completes the scheduled certificate rotation of every outgoing AS2 connection
    whose next-certificate activation date plus the grace window has passed -
    the next certificate becomes the current one and the next-certificate fields are cleared.
    """
    name = AS2.Default.Rotation_Service

    def handle(self) -> 'None':

        # One reference moment for the whole sweep
        now = datetime.now(timezone.utc)

        # Take a snapshot of the current connections because completing a rotation modifies the container ..
        conn_dicts = list(self.server.config_manager.outconn_as2.values())

        for conn_dict in conn_dicts:

            # .. skip the connections with no rotation to complete ..
            if not needs_rotation_completion(conn_dict, now):
                continue

            # .. copy the config without its runtime-only entries ..
            request = {}
            for key, value in conn_dict.items():
                if key in _rotation_runtime_only_keys:
                    continue
                request[key] = value

            # .. promote the next certificate to the current one ..
            complete_rotation(request)

            # .. and persist the change through the edit service, which keeps the ext-db id mapping,
            # .. secret re-encryption and the cluster-wide propagation correct.
            _ = self.invoke('zato.generic.connection.edit', request)

            self.logger.info('Completed AS2 certificate rotation for connection `%s`', request['name'])

# ################################################################################################################################
# ################################################################################################################################

