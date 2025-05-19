# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from copy import deepcopy
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import insert

# Zato
from zato.common.api import GENERIC, Sec_Def_Type
from zato.common.odb.model import HTTPBasicAuth, SecurityBase
from zato.common.odb.query.common import get_object_list_by_columns, get_object_list_by_name_list
from zato.common.crypto.api import CryptoManager
from zato.common.typing_ import cast_
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, dictlist, strdict

# ################################################################################################################################
# ################################################################################################################################

HTTPBasicAuthTable:'any_' = HTTPBasicAuth.__table__
SecurityBaseTable:'any_' = SecurityBase.__table__


HTTPBasicAuthInsert = HTTPBasicAuthTable.insert

# ################################################################################################################################
# ################################################################################################################################

Generic_Attr_Name = GENERIC.ATTR_NAME

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
    """ Imports multiple pub/sub objects en masse.
    """
    name = 'zato.common.import-objects'

    def handle(self):

        # data = test_data
        data = self.request.raw_request

        # Data that we received on input
        input:'ObjectContainer' = ObjectContainer.from_dict(data)

        has_input:'any_' = input.basic_auth
        if not has_input:
            return

        self.logger.info('*' * 60)

        # Data that already exists
        with closing(self.odb.session()) as session:

            # All security definitions that currently exist
            sec_list = self._get_sec_list(session)

            # If we have security definitions on input,
            # import them first, as they may be needed in subsequent steps.
            if input.basic_auth:

                sec_info = self._handle_basic_auth_input(input.basic_auth, sec_list)

                if sec_info.to_add:
                    self.create_basic_auth(session, sec_info.to_add, input.basic_auth)

                if sec_info.to_update:
                    self.update_objects(session, SecurityBase, sec_info.to_update)

                if sec_info.to_add:
                    self.logger.info('Basic Auth created: %s', len(sec_info.to_add))

                if sec_info.to_update:
                    self.logger.info('Basic Auth updated: %s', len(sec_info.to_update))

                session.commit()

# ################################################################################################################################

    def _get_rest_conn_id_by_name(self, name:'str') -> 'int':

        if conn := self.server.worker_store.get_outconn_rest(name):
            conn_config = conn['config']
            conn_id = conn_config['id']
            return conn_id
        else:
            raise Exception(f'Outgoing REST connection not found -> {name}')

# ################################################################################################################################

    def _get_rest_conn_id_by_item(self, item:'strdict') -> 'int | None':

        if rest_connection := item.get('rest_connection'): # type: ignore
            rest_connection_id = self._get_rest_conn_id_by_name(rest_connection)
            return rest_connection_id

# ################################################################################################################################

    def _handle_basic_auth_input(self, incoming:'dictlist', existing:'dictlist') -> 'ItemsInfo':

        # Our response to produce
        out = ItemsInfo()
        out.to_add = []
        out.to_update = []

        # Go through each item that we potentially need to create and see if there is a match
        for new_item in deepcopy(incoming):
            for existing_item in existing:
                if existing_item['sec_type'] == Sec_Def_Type.BASIC_AUTH:
                    if new_item['name'] == existing_item['name']:
                        new_item['id'] = existing_item['id']
                        new_item['sec_type'] = existing_item['sec_type']
                        new_item['cluster_id'] = self.server.cluster_id
                        _ = new_item.pop('realm', None)
                        out.to_update.append(new_item)
                        break

            # .. if we are here, it means that there was no match, which means that this item truly is new ..
            else:

                # .. passwords are optional on input ..
                if not 'password' in new_item:
                    new_item['password'] = self.name + ' ' + cast_('str', CryptoManager.generate_secret(as_str=True))

                new_item['sec_type'] = Sec_Def_Type.BASIC_AUTH
                new_item['cluster_id'] = self.server.cluster_id
                out.to_add.append(new_item)

        # .. now, we can return the response to our caller.
        return out

# ################################################################################################################################

    def _get_basic_auth_realm_by_sec_name(self, incoming:'dictlist', name:'str') -> 'str':
        for item in incoming:
            if item['name'] == name:
                return item['realm']
        else:
            raise Exception(f'Security definition not found (realm) -> {name}')

# ################################################################################################################################

    def create_basic_auth(self, session:'SASession', values:'dictlist', incoming:'dictlist') -> 'None':

        # We need to create a new list with only these values
        # that the base table can support.
        sec_base_values = []

        for item in values:
            sec_base_item = deepcopy(item)
            _ = sec_base_item.pop('realm', None)
            sec_base_values.append(sec_base_item)

        # First, insert rows in the base table ..
        sec_base_insert = insert(SecurityBase).values(sec_base_values)
        _ = session.execute(sec_base_insert)
        session.commit()

        # .. now, get all of their IDs ..
        name_list:'any_' = [item['name'] for item in values]
        newly_added = get_object_list_by_name_list(session, SecurityBaseTable, name_list)

        to_add_basic_auth = []
        for item in values:
            for newly_added_item in newly_added:
                if item['name'] == newly_added_item['name']:
                    to_add_item = {
                        'id': newly_added_item['id'],
                        'realm': item['realm'],
                    }
                    to_add_basic_auth.append(to_add_item)
                    break

        _ = session.execute(HTTPBasicAuthInsert().values(to_add_basic_auth))
        session.commit()

# ################################################################################################################################

    def create_objects(self, table:'any_', values:'dictlist') -> 'any_':
        result = insert(table).values(values)
        return result

# ################################################################################################################################

    def update_objects(self, session:'SASession', table:'any_', values:'dictlist') -> 'any_':
        session.bulk_update_mappings(table, values)

# ################################################################################################################################

    def _find_items(self, incoming:'dictlist', existing:'dictlist') -> 'ItemsInfo':

        # Our response to produce
        out = ItemsInfo()
        out.to_add = []
        out.to_update = []

        # Go through each item that we potentially need to create and see if there is a match
        for new_item in incoming:

            for existing_item in existing:
                if new_item['name'] == existing_item['name']:
                    new_item['id'] = existing_item['id']
                    new_item['cluster_id'] = self.server.cluster_id
                    out.to_update.append(new_item)
                    break

            # .. if we are here, it means that there was no match, which means that this item truly is new ..
            else:
                new_item['cluster_id'] = self.server.cluster_id
                out.to_add.append(new_item)

        # .. now, we can return the response to our caller.
        return out

# ################################################################################################################################

    def _get_sec_list(self, session:'SASession') -> 'dictlist':

        columns = [SecurityBaseTable.c.id, SecurityBaseTable.c.name, SecurityBaseTable.c.sec_type]
        out = get_object_list_by_columns(session, columns)
        return out

# ################################################################################################################################

    def _get_existing_data(self, session:'SASession', *, needs_subs:'bool') -> 'ObjectContainer':

        # Our response to produce
        out = ObjectContainer()
        return out

# ################################################################################################################################
# ################################################################################################################################
