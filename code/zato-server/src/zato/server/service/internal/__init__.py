# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from copy import deepcopy
from json import loads

# Zato
from zato.common.api import SECRET_SHADOW
from zato.common.util.api import get_response_value, make_cid_public
from zato.server.service import AsIs, Int, Service

# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################

logger = logging.getLogger('zato_admin')

# ################################################################################################################################

class AdminService(Service):
    """ A Zato admin service, part of the Zato public API.
    """
    skip_before_handle = False

    def __init__(self):
        super(AdminService, self).__init__()

# ################################################################################################################################

    def before_handle(self):

        # Do not run if the service explicitly tells us not to
        if self.skip_before_handle:
            return

        # Do not log BASE64-encoded messages
        if self.name == 'zato.service.invoke':
            return

        if self.server.is_admin_enabled_for_info:

            # Prefer that first because it may be a generic connection
            # in which case we want to access its opaque attributes
            # that are not available through self.request.input.
            try:
                data = self.request.raw_request
                if not isinstance(data, dict):
                    data = loads(data)
            except Exception:
                data = self.request.input or {}
            finally:
                to_copy = {}
                if isinstance(data, dict):
                    for k, v in data.items():
                        to_copy[k] = v

                data = deepcopy(to_copy)

            for k in data:
                if 'password' in k:
                    data[k] = SECRET_SHADOW

            logger.info('Request; service:`%s`, data:`%s` cid:`%s`, ', self.name, data, self.cid)

# ################################################################################################################################

    def handle(self, *args, **kwargs):
        raise NotImplementedError('Should be overridden by subclasses (AdminService.handle -> {})'.format(self.name))

# ################################################################################################################################

    def after_handle(self):

        if self.name == 'zato.service.invoke':
            return

        if self.server.is_admin_enabled_for_info:
            logger.info('Response; service:`%s`, data:`%s` cid:`%s`, ',
                self.name, get_response_value(self.response), self.cid)

# ################################################################################################################################

    def _paginate_list(self, items:'anylist') -> 'anydict':
        """ Paginates an in-memory list and returns {"data": [...], "_meta": {...}}.
        """
        from zato.common.util.search import SearchResults

        query = self.request.input.get('query') or ''
        if query:
            items = [item for item in items if query.lower() in str(item.get('name', '')).lower()]

        needs_pagination = self.request.input.get('paginate')
        if needs_pagination:
            cur_page = int(self.request.input.get('cur_page') or 1)
            page_size = int(self.request.input.get('page_size') or 50)
            result = SearchResults.from_list(items, cur_page, page_size, needs_sort=False, needs_reverse=False)
            meta = result.to_dict()
            _ = meta.pop('result', None)
            data = list(result)
        else:
            meta = {}
            data = items

        return {'data': data, '_meta': meta}

# ################################################################################################################################

class Ping(AdminService):
    """ A ping service, useful for API testing.
    """
    name = 'demo.ping'

    def handle(self):
        pub_cid = make_cid_public(self.cid)
        self.response.payload = f'{{"is_ok":true, "cid":"{pub_cid}"}}'

# ################################################################################################################################

class ServerInvoker(AdminService):

    name = 'zato.server.invoker'

    def handle(self):
        func_name = self.request.raw_request['func_name']
        func = getattr(self.server, func_name)

        if func_name == 'import_enmasse':
            file_content = self.request.raw_request.get('file_content', '')
            file_name = self.request.raw_request.get('file_name', 'enmasse.yaml')
            response = func(file_content, file_name)
        else:
            response = func()

        self.response.payload = response

# ################################################################################################################################

class ChangePasswordBase(AdminService):
    """ A base class for changing passwords via the Rust ConfigStore.
    """
    password_required = True
    config_store_entity_type = ''

    input = 'password1', 'password2', Int('-id'), '-name', '-type_'
    output = AsIs('id')

    def _handle(self, _class=None, _auth_func=None, _action=None, **kwargs):

        instance_id = self.request.input.get('id')
        instance_name = self.request.input.get('name', '')
        entity_type = self.config_store_entity_type

        password1 = self.request.input.get('password1', '')
        password2 = self.request.input.get('password2', '')

        password1_decrypted = self.server.decrypt(password1) if password1 else password1
        password2_decrypted = self.server.decrypt(password2) if password2 else password2

        if self.password_required:
            if not password1_decrypted:
                raise Exception('Password must not be empty')
            if not password2_decrypted:
                raise Exception('Password must be repeated')

        if password1_decrypted != password2_decrypted:
            raise Exception('Passwords need to be the same')

        if not instance_name and instance_id:
            for item in self.server.config_store.get_list(entity_type):
                if item.get('id') == instance_id:
                    instance_name = item['name']
                    break

        if not instance_name:
            raise Exception('Either ID or name are required on input')

        existing = self.server.config_store.get(entity_type, instance_name)
        if not existing:
            raise Exception('Could not find `{}` in `{}`'.format(instance_name, entity_type))

        existing['password'] = password1_decrypted
        self.server.config_store.set(entity_type, instance_name, existing)

        self.response.payload.id = existing.get('id') or instance_id

# ################################################################################################################################
