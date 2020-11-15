# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from copy import deepcopy
from datetime import datetime
from traceback import format_exc

# Zato
from zato.common.api import GENERIC as COMMON_GENERIC
from zato.common.broker_message import GENERIC
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.odb.query.generic import connection_list
from zato.common.util.api import parse_simple_type
from zato.server.generic.connection import GenericConnection
from zato.server.service import Bool, Int
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO
from zato.server.service.internal.generic import _BaseService
from zato.server.service.meta import DeleteMeta

# Python 2/3 compatibility
from past.builtins import basestring
from six import add_metaclass

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.service import Service

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

# ################################################################################################################################

extra_secret_keys = (

    #
    # Dropbox
    #
    'oauth2_access_token',
)

# ################################################################################################################################

class _CreateEditSIO(AdminSIO):
    input_required = ('name', 'type_', 'is_active', 'is_internal', 'is_channel', 'is_outconn', Int('pool_size'),
        Bool('sec_use_rbac'), 'cluster_id')
    input_optional = ('id', Int('cache_expiry'), 'address', Int('port'), Int('timeout'), 'data_format', 'version',
        'extra', 'username', 'username_type', 'secret', 'secret_type', 'conn_def_id', 'cache_id')
    force_empty_keys = True

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(_BaseService):
    """ Creates a new or updates an existing generic connection in ODB.
    """
    is_edit = None

    class SimpleIO(_CreateEditSIO):
        output_required = ('id', 'name')
        default_value = None
        response_elem = None

# ################################################################################################################################

    def handle(self):
        data = deepcopy(self.request.input)

        raw_request = self.request.raw_request
        if isinstance(raw_request, basestring):
            raw_request = loads(raw_request)

        for key, value in raw_request.items():
            if key not in data:

                value = parse_simple_type(value)
                value = self._sio.eval_(key, value, self.server.encrypt)

                data[key] = value

        conn = GenericConnection.from_dict(data)

        # Make sure not to overwrite the seceret in Edit
        if not self.is_edit:
            conn.secret = self.server.encrypt('auto.generated.{}'.format(self.crypto.generate_secret()))
        conn_dict = conn.to_sql_dict()

        with closing(self.server.odb.session()) as session:

            if self.is_edit:
                model = self._get_instance_by_id(session, ModelGenericConn, data.id)
            else:
                model = self._new_zato_instance_with_cluster(ModelGenericConn)

            # This will be needed in case this is a rename
            old_name = model.name

            for key, value in sorted(conn_dict.items()):
                if key == 'secret':
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
    is_edit = False

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    """ Updates an existing generic connection.
    """
    is_edit = True

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

    def get_data(self, session):
        return self._search(connection_list, session, self.request.input.cluster_id, self.request.input.type_, False)

# ################################################################################################################################

    def _enrich_conn_dict(self, conn_dict):
        # type: (dict)

        # New items that will be potentially added to conn_dict
        to_add = {}

        for key, value in conn_dict.items():

            if value:

                if key.endswith('_service_id'):
                    prefix = key.split('_service_id')[0]
                    service_attr = prefix + '_service_name'
                    try:
                        service_name = self.invoke('zato.service.get-by-id', {
                            'cluster_id': self.request.input.cluster_id,
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

        if to_add:
            conn_dict.update(to_add)

# ################################################################################################################################
# ################################################################################################################################

    def handle(self):
        out = {'_meta':{}, 'response':[]}

        with closing(self.odb.session()) as session:

            search_result = self.get_data(session)
            out['_meta'].update(search_result.to_dict())

            for item in search_result:
                conn = GenericConnection.from_model(item)
                conn_dict = conn.to_dict()
                self._enrich_conn_dict(conn_dict)
                out['response'].append(conn_dict)

        self.response.payload = dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the secret (password) of a generic connection.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        response_elem = None

    def handle(self):

        def _auth(instance, secret):
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

        return self._handle(ModelGenericConn, _auth, GENERIC.CONNECTION_CHANGE_PASSWORD.value, instance_id=instance_id,
            publish_instance_attrs=['type_'])

# ################################################################################################################################
# ################################################################################################################################

class Ping(_BaseService):
    """ Pings a generic connection.
    """
    class SimpleIO(AdminSIO):
        input_required = 'id',
        output_required = 'info',
        response_elem = None

    def handle(self):
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
                ping_func(self.request.input.id)
            except Exception:
                self.response.payload.info = format_exc()
            else:
                response_time = datetime.utcnow() - start_time
                self.response.payload.info = 'Connection pinged; response time: {}'.format(response_time)

# ################################################################################################################################
# ################################################################################################################################
