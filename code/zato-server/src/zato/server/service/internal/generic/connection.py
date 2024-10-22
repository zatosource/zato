# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from copy import deepcopy
from datetime import datetime
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common.api import GENERIC as COMMON_GENERIC, generic_attrs, SEC_DEF_TYPE, SEC_DEF_TYPE_NAME, ZATO_NONE
from zato.common.broker_message import GENERIC
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.odb.query.generic import connection_list
from zato.common.typing_ import cast_
from zato.common.util.api import parse_simple_type
from zato.common.util.config import replace_query_string_items_in_dict
from zato.server.generic.connection import GenericConnection
from zato.server.service import AsIs, Bool, Int
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO
from zato.server.service.internal.generic import _BaseService
from zato.server.service.meta import DeleteMeta

# Python 2/3 compatibility
from six import add_metaclass

# ################################################################################################################################

if 0:
    from bunch import Bunch
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

hook = {}

# ################################################################################################################################

config_dict_id_name_outconnn = {
    'ftp_source': 'out_ftp',
    'sftp_source': 'out_sftp',
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

)

# Note that this is a set, unlike extra_secret_keys, because we do not make it part of SIO.
extra_simple_type = {
    'is_active',
}

# This key should be left as they are given on input, without trying to parse them into non-string types.
skip_simple_type = {
    'api_version',
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

class _CreateEditSIO(AdminSIO):
    input_required = ('name', 'type_', 'is_active', 'is_internal', 'is_channel', 'is_outconn', Int('pool_size'),
        Bool('sec_use_rbac'))
    input_optional = ('cluster_id', 'id', Int('cache_expiry'), 'address', Int('port'), Int('timeout'), 'data_format', 'version',
        'extra', 'username', 'username_type', 'secret', 'secret_type', 'conn_def_id', 'cache_id', AsIs('tenant_id'),
        AsIs('client_id'), AsIs('security_id'), AsIs('sec_tls_ca_cert_id')) + extra_secret_keys + generic_attrs
    force_empty_keys = True

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(_BaseService):
    """ Creates a new or updates an existing generic connection in ODB.
    """
    is_create: 'bool'
    is_edit:   'bool'

    class SimpleIO(_CreateEditSIO):
        output_required = ('id', 'name')
        default_value = None
        response_elem = None

# ################################################################################################################################

    def handle(self) -> 'None':

        data = deepcopy(self.request.input)

        # Build a reusable flag indicating that a secret was sent on input.
        secret = data.get('secret', ZATO_NONE)
        if (secret is None) or (secret == ZATO_NONE):
            has_input_secret  = False
            input_secret = ''
        else:
            has_input_secret = True
            input_secret = secret
            if input_secret:
                input_secret = self.crypto.encrypt(input_secret)
                input_secret = input_secret.decode('utf8')

        raw_request = self.request.raw_request
        if isinstance(raw_request, (str, bytes)):
            raw_request = loads(raw_request)

        for key, value in raw_request.items():

            if key not in data:
                if key not in skip_simple_type:
                    value = parse_simple_type(value)
                value = self._sio.eval_(key, value, self.server.encrypt)

            if key in extra_secret_keys:
                if value is None:
                    value = 'auto.generic.{}'.format(uuid4().hex)
                value = self.crypto.encrypt(value)
                value = value.decode('utf8')

            if key in extra_simple_type:
                value = parse_simple_type(value)

            data[key] = value

        # If the is_active flag does exist but it is None, it should be treated as though it was set to False,
        # which is needed because None would be treated as NULL by the SQL database.
        if 'is_active' in data:
            if data['is_active'] is None:
                data['is_active'] = False

        # Make sure that specific keys are integers
        ensure_ints(data)

        # Break down security definitions into components
        security_id = data.get('security_id') or ''
        if sec_def_sep in security_id:

            # Extract the components ..
            sec_def_type, security_id = security_id.split(sec_def_sep)
            sec_def_type_name = SEC_DEF_TYPE_NAME[sec_def_type]

            security_id = int(security_id)

            # .. look up the security name by its ID ..
            if sec_def_type == SEC_DEF_TYPE.BASIC_AUTH:
                func = self.server.worker_store.basic_auth_get_by_id
            elif sec_def_type == SEC_DEF_TYPE.OAUTH:
                func = self.server.worker_store.oauth_get_by_id
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

        with closing(self.server.odb.session()) as session:

            # If this is the edit action, we need to find our instance in the database
            # and we need to make sure that we publish its encrypted secret for other layers ..
            if self.is_edit:
                model = self._get_instance_by_id(session, ModelGenericConn, data.id)

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
            # .. and ensure that its secret is auto-generated.
            else:
                model = self._new_zato_instance_with_cluster(ModelGenericConn)
                secret = self.crypto.generate_secret().decode('utf8')
                secret = self.server.encrypt('auto.generated.{}'.format(secret))
                secret = cast_('str', secret)
                conn.secret = secret

            conn_dict = conn.to_sql_dict()

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

            hook_func = hook.get(data.type_)
            if hook_func:
                hook_func(self, data, model, old_name)

            session.add(model)
            session.commit()

            instance = self._get_instance_by_name(session, ModelGenericConn, data.type_, data.name)

            self.response.payload.id = instance.id
            self.response.payload.name = instance.name

        data['old_name'] = old_name
        data['action'] = GENERIC.CONNECTION_EDIT.value if self.is_edit else GENERIC.CONNECTION_CREATE.value
        data['id'] = instance.id
        self.broker_client.publish(data)

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

    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id',)
        input_optional = GetListAdminSIO.input_optional + ('type_',)

# ################################################################################################################################

    def get_data(self, session:'any_') -> 'any_':
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id
        data = self._search(connection_list, session, cluster_id, self.request.input.type_, False)
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

    def handle(self) -> 'None':
        out = {'_meta':{}, 'response':[]}
        _meta = cast_('anydict', out['_meta'])

        with closing(self.odb.session()) as session:

            search_result = self.get_data(session)
            _meta.update(search_result.to_dict())

            for item in search_result:
                conn = GenericConnection.from_model(item)
                conn_dict = conn.to_dict()
                self._enrich_conn_dict(conn_dict)
                cast_('anylist', out['response']).append(conn_dict)

        # Results are already included in the list of out['response'] elements
        _ = _meta.pop('result', None)

        self.response.payload = dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the secret (password) of a generic connection.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        response_elem = None

# ################################################################################################################################

    def _run_pre_handle_tasks_CLOUD_MICROSOFT_365(self, session:'any_', instance:'any_') -> 'None':

        # Disabled, no longer in use
        return

        # stdlib
        from json import dumps, loads
        from urllib.parse import parse_qs, urlsplit

        # office-365
        from O365 import Account

        auth_url = self.request.input.password1
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
            instance_id = self.request.input.id
        else:
            with closing(self.odb.session()) as session:
                instance_id = session.query(ModelGenericConn).\
                    filter(ModelGenericConn.name==self.request.input.name).\
                    filter(ModelGenericConn.type_==self.request.input.type_).\
                    one().id

        with closing(self.odb.session()) as session:
            query = session.query(ModelGenericConn)
            query = query.filter(ModelGenericConn.id==instance_id)
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
    class SimpleIO(AdminSIO):
        input_required = 'id'
        output_required = 'info'
        output_optional = 'is_success'
        response_elem = None

    def handle(self) -> 'None':
        with closing(self.odb.session()) as session:

            # To ensure that the input ID is correct
            instance = self._get_instance_by_id(session, ModelGenericConn, self.request.input.id)

            # Different code paths will be taken depending on what kind of a generic connection this is
            custom_ping_func_dict = {
                COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SFTP: self.server.connector_sftp.ping_sftp
            }

            # Most connections use a generic ping function, unless overridden on a case-by-case basis, like with SFTP
            ping_func = custom_ping_func_dict.get(instance.type_, self.server.worker_store.ping_generic_connection)

            start_time = datetime.utcnow()

            try:
                _ = ping_func(self.request.input.id)
            except Exception:
                exc = format_exc()
                self.logger.warning(exc)
                self.response.payload.info = exc
                self.response.payload.is_success = False
            else:
                response_time = datetime.utcnow() - start_time
                info = 'Connection pinged; response time: {}'.format(response_time)
                self.logger.info(info)
                self.response.payload.info = info
                self.response.payload.is_success = True

# ################################################################################################################################
# ################################################################################################################################

class Invoke(AdminService):
    """ Invokes a generic connection by its name.
    """
    class SimpleIO:
        input_required = 'conn_type', 'conn_name'
        input_optional = 'request_data'
        output_optional = 'response_data'
        response_elem = None

    def handle(self) -> 'None':

        # Local aliases
        response = None

        # Maps all known connection types to their implementation ..
        conn_type_to_container = {
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: self.out.hl7.fhir,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP: self.out.hl7.mllp
        }

        # .. get the actual implementation ..
        container = conn_type_to_container[self.request.input.conn_type]

        # .. and invoke it.
        with container[self.request.input.conn_name].conn.client() as client:

            try:
                response = client.invoke(self.request.input.request_data)
            except Exception:
                exc = format_exc()
                response = exc
                self.logger.warning(exc)
            finally:
                self.response.payload.response_data = response

# ################################################################################################################################
# ################################################################################################################################
