# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from dataclasses import dataclass

# Zato
from zato.common.api import Sec_Def_Type
from zato.common.crypto.api import CryptoManager
from zato.common.typing_ import cast_
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist, strdict

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ObjectContainer(Model):
    basic_auth: 'dictlist | None' = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ItemsInfo(Model):
    to_add: 'dictlist'
    to_update: 'dictlist'

# ################################################################################################################################
# ################################################################################################################################

class ImportObjects(Service):
    """ Imports multiple objects en masse.
    """
    name = 'zato.common.import-objects'

    def handle(self):

        data = self.request.raw_request
        input:'ObjectContainer' = ObjectContainer.from_dict(data)

        has_input:'any_' = input.basic_auth
        if not has_input:
            return

        self.logger.info('*' * 60)

        existing_sec = self._get_existing_security()

        if input.basic_auth:
            sec_info = self._handle_basic_auth_input(input.basic_auth, existing_sec)

            if sec_info.to_add:
                self._create_basic_auth(sec_info.to_add)

            if sec_info.to_update:
                self._update_basic_auth(sec_info.to_update)

            if sec_info.to_add:
                self.logger.info('Basic Auth created: %s', len(sec_info.to_add))

            if sec_info.to_update:
                self.logger.info('Basic Auth updated: %s', len(sec_info.to_update))

# ################################################################################################################################

    def _get_existing_security(self) -> 'dictlist':
        out:'dictlist' = []
        sec_list = self.server.config_store.get_list('security')
        for item in sec_list:
            out.append({
                'id': item.get('id', 0),
                'name': item.get('name', ''),
                'sec_type': item.get('type', ''),
            })
        return out

# ################################################################################################################################

    def _handle_basic_auth_input(self, incoming:'dictlist', existing:'dictlist') -> 'ItemsInfo':

        out = ItemsInfo()
        out.to_add = []
        out.to_update = []

        for new_item in deepcopy(incoming):
            for existing_item in existing:
                if existing_item['sec_type'] == Sec_Def_Type.BASIC_AUTH:
                    if new_item['name'] == existing_item['name']:
                        new_item['id'] = existing_item['id']
                        new_item['sec_type'] = existing_item['sec_type']
                        _ = new_item.pop('realm', None)
                        out.to_update.append(new_item)
                        break
            else:
                if not 'password' in new_item:
                    new_item['password'] = self.name + ' ' + cast_('str', CryptoManager.generate_secret(as_str=True))
                new_item['sec_type'] = Sec_Def_Type.BASIC_AUTH
                out.to_add.append(new_item)

        return out

# ################################################################################################################################

    def _create_basic_auth(self, items:'dictlist') -> 'None':
        for item in items:
            self.invoke('zato.security.basic-auth.create', {
                'name': item['name'],
                'is_active': item.get('is_active', True),
                'username': item.get('username', item['name']),
                'realm': item.get('realm', ''),
            })

# ################################################################################################################################

    def _update_basic_auth(self, items:'dictlist') -> 'None':
        for item in items:
            self.invoke('zato.security.basic-auth.edit', {
                'id': item['id'],
                'name': item['name'],
                'is_active': item.get('is_active', True),
                'username': item.get('username', item['name']),
                'realm': item.get('realm', ''),
            })

# ################################################################################################################################
# ################################################################################################################################
