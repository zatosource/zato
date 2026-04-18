# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.groups import Member

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, intnone, list_, strlist
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class GroupsManager:

    def __init__(self, server:'ParallelServer', session:'any_'=None) -> 'None':
        self.server = server
        self.cluster_id = self.server.cluster_id

# ################################################################################################################################

    def create_group(self, group_type:'str', group_name:'str') -> 'str':
        self.server.config_manager.set('groups', group_name, {
            'name': group_name,
            'group_type': group_type,
            'members': [],
        })
        item = self.server.config_manager.get('groups', group_name)
        return item['id']

# ################################################################################################################################

    def edit_group(self, group_id:'int', group_type:'str', group_name:'str') -> 'None':
        for item in self.server.config_manager.get_list('groups'):
            if item.get('id') == group_id:
                old_name = item['name']
                item['name'] = group_name
                item['group_type'] = group_type
                if old_name != group_name:
                    self.server.config_manager.delete('groups', old_name)
                self.server.config_manager.set('groups', group_name, item)
                return
        raise Exception('Group with id `{}` not found'.format(group_id))

# ################################################################################################################################

    def delete_group(self, group_id:'int') -> 'None':
        for item in self.server.config_manager.get_list('groups'):
            if item.get('id') == group_id:
                self.server.config_manager.delete('groups', item['name'])
                return

# ################################################################################################################################

    def get_group_list(self, group_type:'str') -> 'anylist':
        out:'anylist' = []
        for item in self.server.config_manager.get_list('groups'):
            if not group_type or item.get('group_type', '') == group_type:
                out.append(item)
        return out

# ################################################################################################################################

    def get_member_list(self, group_type:'str', group_id:'intnone'=None) -> 'list_[Member]':

        out:'list_[Member]' = []

        groups = self.server.config_manager.get_list('groups')
        for group in groups:
            if group_type and group.get('group_type', '') != group_type:
                continue
            if group_id is not None and group.get('id') != group_id:
                continue

            members = group.get('members', [])
            for member_key in members:

                parts = member_key.split('-')
                if len(parts) < 2:
                    continue

                sec_type = parts[0]
                security_id = int(parts[1])

                if sec_type == SEC_DEF_TYPE.BASIC_AUTH:
                    get_sec_func = self.server.worker_store.basic_auth_get_by_id
                elif sec_type == SEC_DEF_TYPE.APIKEY:
                    get_sec_func = self.server.worker_store.apikey_get_by_id
                else:
                    continue

                if sec_config := get_sec_func(security_id):
                    item = {
                        'name': sec_config['name'],
                        'security_id': sec_config['id'],
                        'sec_type': sec_type,
                    }
                    member = Member.from_dict(item)
                    out.append(member)

        return out

# ################################################################################################################################

    def get_member_count(self, group_type:'str') -> 'anydict':

        out:'anydict' = {}

        group_list = self.get_group_list(group_type)
        for item in group_list:
            group_id = item['id']
            members = item.get('members', [])
            out[group_id] = len(members)

        return out

# ################################################################################################################################

    def add_members_to_group(self, group_id:'int', member_id_list:'strlist') -> 'None':

        for group in self.server.config_manager.get_list('groups'):
            if group.get('id') == group_id:
                members = list(group.get('members', []))
                for member_id in member_id_list:
                    composite = f'{member_id}-{group_id}'
                    if composite not in members:
                        members.append(composite)
                group['members'] = members
                self.server.config_manager.set('groups', group['name'], group)
                return

# ################################################################################################################################

    def remove_members_from_group(self, group_id:'str', member_id_list:'strlist') -> 'None':

        for group in self.server.config_manager.get_list('groups'):
            if group.get('id') == int(group_id):
                members = list(group.get('members', []))
                for member_id in member_id_list:
                    composite = f'{member_id}-{group_id}'
                    if composite in members:
                        members.remove(composite)
                group['members'] = members
                self.server.config_manager.set('groups', group['name'], group)
                return

# ################################################################################################################################
# ################################################################################################################################
