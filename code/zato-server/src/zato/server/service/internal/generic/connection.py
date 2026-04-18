# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common.api import GENERIC as COMMON_GENERIC, generic_attrs, SEC_DEF_TYPE, SEC_DEF_TYPE_NAME, ZATO_NONE
from zato.common.json_internal import dumps, loads
from zato.common.typing_ import cast_
from zato.common.util.api import parse_simple_type
from zato.common.util.config import replace_query_string_items_in_dict
from zato.common.util.search import SearchResults
from zato.common.util.time_ import utcnow
from zato.server.connection.http_soap import BadRequest
from zato.server.generic.connection import GenericConnection
from zato.server.service import AsIs, Bool, Int
from zato.server.service.internal import AdminService, ChangePasswordBase

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
label = 'a generic connection'
hook = {}

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

_generic_connection_keys = frozenset({
    'id', 'name', 'type_', 'is_active', 'is_internal', 'is_channel', 'is_outconn',
    'address', 'port', 'timeout', 'data_format', 'version', 'extra', 'pool_size',
    'username', 'secret', 'cache_expiry', 'security',
})

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

def _flatten_rust_generic_item(item:'anydict') -> 'anydict':
    """ Merge Rust generic_connection dict (optional nested opaque) into a flat dict for GenericConnection.from_dict.
    """
    flat = dict(item)
    opaque = flat.pop('opaque', None) or {}
    if isinstance(opaque, dict):
        flat.update(opaque)
    return flat

# ################################################################################################################################

def _conn_to_rust_payload(conn:'GenericConnection') -> 'anydict':
    """ Build a PyDict suitable for config_store.set for entity generic_connection.
    """
    flat = conn.to_dict()
    if not isinstance(flat, dict):
        flat = dict(flat)
    payload:'anydict' = {}
    extra:'anydict' = {}
    for k, v in flat.items():
        if v is None:
            continue
        if k in _generic_connection_keys:
            payload[k] = v
        else:
            extra[k] = v
    if extra:
        payload['opaque'] = extra
    return payload

# ################################################################################################################################

def _find_generic_item(server, id=None, name=None, type_=None) -> 'anydict | None':
    for item in server.config_store.get_list('generic_connection'):
        if type_ is not None and item.get('type_') != type_:
            continue
        if id is not None and str(item.get('id')) == str(id):
            return item
        if name is not None and item.get('name') == name:
            return item
    return None

# ################################################################################################################################

def _next_generic_connection_id(server) -> 'str':
    """No longer needed — Rust auto-generates string IDs — but kept for backward compat."""
    return ''

# ################################################################################################################################

class _CreateEdit(AdminService):
    """ Creates a new or updates an existing generic connection in the Rust config store.
    """
    is_create: 'bool'
    is_edit:   'bool'

    input = ('name', 'type_', 'is_active', 'is_internal', 'is_channel', 'is_outconn', Int('pool_size'),
        '-cluster_id', '-id', Int('-cache_expiry'), '-address', Int('-port'), Int('-timeout'), '-data_format', '-version',
        '-extra', '-username', '-username_type', '-secret', '-secret_type', '-conn_def_id', '-cache_id', AsIs('-tenant_id'),
        AsIs('-client_id'), AsIs('-security_id')) + tuple('-' + k for k in extra_secret_keys) + tuple('-' + k for k in generic_attrs)
    output = 'id', 'name'
    force_empty_keys = True
    default_value = None

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

            # .. strip the sec_type prefix, e.g. '2026-...' instead of 'oauth/2026-...'.
            data['security_id'] = security_id

            # .. and store everything else now.
            data['sec_def_type_name'] = sec_def_type_name
            data['security_name'] = security_name

        existing = None
        old_name = None
        if self.is_edit:
            existing = _find_generic_item(self.server, id=data.get('id'), type_=data.get('type_'))
            if not existing:
                raise Exception('Could not find generic connection with id `{}`'.format(data.get('id')))
            old_name = existing['name']
            if not has_input_secret:
                data['secret'] = existing.get('secret')
            if data.get('id') is None:
                data['id'] = existing.get('id')
        else:
            data['id'] = data.get('id') or _next_generic_connection_id(self.server)
            secret = self.crypto.generate_secret().decode('utf8')
            secret = self.server.encrypt('auto.generated.{}'.format(secret))
            secret = cast_('str', secret)
            if not has_input_secret:
                data['secret'] = secret

        if has_input_secret:
            data['secret'] = input_secret

        conn = GenericConnection.from_dict(data)

        hook_func = hook.get(data.type_)
        if hook_func:
            hook_func(self, data, existing, old_name)

        rust_payload = _conn_to_rust_payload(conn)
        if data.get('id'):
            rust_payload['id'] = str(data['id'])
        else:
            rust_payload.pop('id', None)
        rust_payload['name'] = data['name']
        rust_payload.setdefault('type_', data.get('type_') or '')

        new_name = data['name']
        if self.is_edit and old_name and old_name != new_name:
            self.server.config_store.delete('generic_connection', old_name)

        self.logger.info('create/edit: storing type_=%r, rust_payload keys=%r', rust_payload.get('type_'), list(rust_payload.keys()))
        self.server.config_store.set('generic_connection', new_name, rust_payload)

        stored = self.server.config_store.get('generic_connection', new_name)
        self.response.payload.id = stored['id']
        self.response.payload.name = new_name

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

class Delete(AdminService):
    """ Deletes a generic connection.
    """
    input = '-id', '-name', '-should_raise_if_missing', '-cluster_id', '-type_'

# ################################################################################################################################

    def handle(self) -> 'None':

        input = self.request.input
        input_id = input.get('id')
        input_name = input.get('name')
        type_ = input.get('type_')

        if not (input_id or input_name):
            raise BadRequest(self.cid, 'Either id or name is required on input')

        found = _find_generic_item(self.server, id=input_id, name=input_name, type_=type_)
        if not found:
            if input.get('should_raise_if_missing', True):
                attr_name = 'id' if input_id else 'name'
                attr_value = input_id or input_name
                raise BadRequest(self.cid, 'Could not find a generic connection instance with {} `{}`'.format(
                    attr_name, attr_value))
            return

        self.server.config_store.delete('generic_connection', found['name'])

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of generic connections by their type; includes pagination.
    """
    _filter_by = 'name',

    input = 'cluster_id', Int('-cur_page'), Bool('-paginate'), '-query', '-type_', Int('-page_size')

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

    def _filter_items_by_query(self, items:'anylist', query_tokens:'anylist') -> 'anylist':
        if not query_tokens:
            return items
        out = []
        for item in items:
            name = (item.get('name') or '')
            ok = True
            for criterion in query_tokens:
                neg = criterion.startswith('-')
                crit = criterion[1:] if neg else criterion
                contained = crit in name
                if neg and contained:
                    ok = False
                    break
                if not neg and not contained:
                    ok = False
                    break
            if ok:
                out.append(item)
        return out

# ################################################################################################################################

    def handle(self) -> 'None':
        out = {'_meta':{}, 'data':[]}
        _meta = cast_('anydict', out['_meta'])

        type_ = self.request.input.type_

        all_items = self.server.config_store.get_list('generic_connection')
        self.logger.info('get-list: type_=%r, store has %d items, types=%r', type_, len(all_items), [x.get('type_') for x in all_items])

        items = all_items
        if type_:
            items = [x for x in items if x.get('type_') == type_]
        self.logger.info('get-list: after filter %d items', len(items))
        items.sort(key=lambda x: (x.get('name') or ''))

        query = self.request.input.get('query')
        if query:
            query = query.strip().split()
            items = self._filter_items_by_query(items, query)

        needs_pagination = self.request.input.get('paginate')
        if needs_pagination:
            try:
                cur_page = int(self.request.input.get('cur_page', 1))
            except (ValueError, TypeError):
                cur_page = 1
            try:
                page_size = int(self.request.input.get('page_size', 50))
            except (ValueError, TypeError):
                page_size = 50
            search_result = SearchResults.from_list(list(items), cur_page, page_size, needs_sort=False)
            iter_items = list(search_result)
        else:
            search_result = SearchResults(None, items, None, len(items))
            iter_items = items

        _meta.update(search_result.to_dict())

        for item in iter_items:
            flat = _flatten_rust_generic_item(item)
            conn = GenericConnection.from_dict(flat)
            conn_dict = conn.to_dict()
            self._enrich_conn_dict(conn_dict)
            cast_('anylist', out['data']).append(conn_dict)

        _ = _meta.pop('result', None)

        self.response.payload = out

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

        inp = self.request.input
        password1 = inp.get('password1', '')
        password2 = inp.get('password2', '')
        password1_decrypted = self.server.decrypt(password1) if password1 else password1
        password2_decrypted = self.server.decrypt(password2) if password2 else password2

        if password1_decrypted != password2_decrypted:
            raise Exception('Passwords need to be the same')

        instance_id = inp.get('id')
        type_ = inp.get('type_')
        if not instance_id:
            if not (inp.get('name') and type_):
                raise Exception('Either ID or name and type_ are required on input')
            found = _find_generic_item(self.server, name=inp.get('name'), type_=type_)
            if not found:
                raise Exception('Could not find generic connection')
            instance_id = found['id']

        item = _find_generic_item(self.server, id=instance_id, type_=type_)
        if not item:
            raise Exception('Could not find generic connection with id `{}`'.format(instance_id))

        self._run_pre_handle_tasks(None, item)

        if password1_decrypted:
            enc = self.server.encrypt(password1_decrypted)
            if isinstance(enc, bytes):
                enc = enc.decode('utf8')
            item = dict(item)
            flat = _flatten_rust_generic_item(item)
            conn = GenericConnection.from_dict(flat)
            conn.secret = enc
            rust_payload = _conn_to_rust_payload(conn)
            rust_payload['id'] = str(item.get('id') or instance_id)
            rust_payload['name'] = item['name']
            self.server.config_store.set('generic_connection', item['name'], rust_payload)

        self.response.payload.id = instance_id

# ################################################################################################################################
# ################################################################################################################################

class Ping(AdminService):
    """ Pings a generic connection.
    """
    input = 'id'
    output = 'info', '-is_success'

    def handle(self) -> 'None':

        found = _find_generic_item(self.server, id=self.request.input.id)
        if not found:
            raise BadRequest(self.cid, 'Could not find generic connection with id `{}`'.format(self.request.input.id))

        custom_ping_func_dict = {}
        ping_func = custom_ping_func_dict.get(found.get('type_'), self.server.worker_store.ping_generic_connection)

        start_time = utcnow()

        try:
            _ = ping_func(self.request.input.id, conn_name=found.get('name', ''))
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

        # Maps all known connection types to their implementation ..
        conn_type_to_container = {}

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
