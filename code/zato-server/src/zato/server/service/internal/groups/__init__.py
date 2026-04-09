# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps
from operator import itemgetter

# Zato
from zato.common.api import CONNECTION, Groups, SEC_DEF_TYPE
from zato.common.groups import Member
from zato.server.service import AsIs, Service

# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

def _next_group_id(server) -> 'int':
    items = server.config_store.get_list('groups')
    return max((int(x.get('id') or 0) for x in items), default=0) + 1

# ################################################################################################################################

def _find_group_by_id(server, group_id) -> 'dict | None':
    for item in server.config_store.get_list('groups'):
        if str(item.get('id')) == str(group_id):
            return item
    return None

# ################################################################################################################################
# ################################################################################################################################

def _member_string_to_dict(server, group_id, member_str:'str') -> 'dict':
    sec_info = member_str.split('-')
    sec_type, security_id = sec_info[0], sec_info[1]
    security_id = int(security_id)

    if sec_type == SEC_DEF_TYPE.BASIC_AUTH:
        get_sec_func = server.worker_store.basic_auth_get_by_id
    elif sec_type == SEC_DEF_TYPE.APIKEY:
        get_sec_func = server.worker_store.apikey_get_by_id
    else:
        raise Exception(f'Unrecognized sec_type: {sec_type}')

    item = {
        'name': member_str,
        'type': sec_type,
        'group_id': group_id,
        'security_id': security_id,
        'sec_type': sec_type,
    }

    if sec_config := get_sec_func(security_id):
        item['name'] = sec_config['name']
        item['security_id'] = sec_config['id']

    return item

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):
    """ Returns all groups matching the input criteria.
    """
    input:'any_' = 'group_type', '-needs_members', '-needs_short_members'

    def handle(self):

        group_type = self.request.input.group_type
        needs_members = self.request.input.needs_members
        needs_short_members = self.request.input.needs_short_members

        group_list = list(self.server.config_store.get_list('groups'))
        member_count = self.invoke(GetMemberCount, group_type=group_type)

        for item in group_list:
            group_id = item['id']
            group_member_count = member_count[group_id]
            item['member_count'] = group_member_count

            if needs_members:
                members = self.invoke(GetMemberList, group_type=group_type, group_id=group_id)
                if needs_short_members:
                    new_members = []
                    for member in members:
                        new_members.append({
                            'name': member['name'],
                        })
                    members = new_members

                members.sort(key=itemgetter('name')) # type: ignore
                if members:
                    item['members'] = members

            if (group_member_count == 0) or (group_member_count > 1):
                suffix = 's'
            else:
                suffix = ''

            item['description'] = f'{group_member_count} member{suffix}'

        self.response.payload = group_list

# ################################################################################################################################
# ################################################################################################################################

class Create(Service):
    """ Creates a new group.
    """
    input:'any_' = 'group_type', 'name', AsIs('-members')
    output:'any_' = 'id', 'name'

    def handle(self):

        # Local variables
        input = self.request.input

        new_id = _next_group_id(self.server)
        data = {
            'id': new_id,
            'name': input.name,
            'members': [],
        }
        self.server.config_store.set('groups', input.name, data)

        self.invoke(
            EditMemberList,
            group_type=input.group_type,
            group_action=Groups.Membership_Action.Add,
            group_id=new_id,
            members=input.get('members') or [],
        )

        self.response.payload.id = new_id
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(Service):
    """ Updates an existing group.
    """
    input:'any_' = 'id', 'group_type', 'name', AsIs('-members')
    output:'any_' = 'id', 'name'

    def handle(self):

        # Local variables
        input = self.request.input

        # All the new members of this group
        to_add:'strlist' = []

        # All the members that have to be removed from the group
        to_remove:'strlist' = []

        group = _find_group_by_id(self.server, input.id)
        if not group:
            raise Exception('Group not found: id=`{}`'.format(input.id))

        old_name = group['name']
        if old_name != input.name:
            self.server.config_store.delete('groups', old_name)

        data = {
            'id': int(input.id),
            'name': input.name,
            'members': list(group.get('members') or []),
        }
        self.server.config_store.set('groups', input.name, data)

        if input.members:

            group_members = self.invoke(GetMemberList, group_type=input.group_type, group_id=input.id)

            input_member_names = {item['name'] for item in input.members}
            group_member_names = {item['name'] for item in group_members}

            for group_member_name in group_member_names:
                if not group_member_name in input_member_names:
                    to_remove.append(group_member_name) # type: ignore

            for input_member_name in input_member_names:
                if not input_member_name in group_member_names:
                    to_add.append(input_member_name)

        #
        # Add all the new members to the group
        #
        if to_add:
            _ = self.invoke(
                EditMemberList,
                group_action=Groups.Membership_Action.Add,
                group_id=input.id,
                members=to_add,
            )

        #
        # Remove all the members that should not belong to the group
        #
        if to_remove:
            _ = self.invoke(
                EditMemberList,
                group_action=Groups.Membership_Action.Remove,
                group_id=input.id,
                members=to_remove,
            )

        self.response.payload.id = self.request.input.id
        self.response.payload.name = self.request.input.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(Service):
    """ Deletes an existing group.
    """
    input:'any_' = 'id'

    def handle(self):

        # Local variables
        input = self.request.input
        group_id = int(input.id)

        group = _find_group_by_id(self.server, group_id)
        if not group:
            return

        self.server.config_store.delete('groups', group['name'])

        # .. make sure the database configuration of channels using it is also updated ..
        to_update = []
        data = self.invoke('zato.http-soap.get-list', connection=CONNECTION.CHANNEL, paginate=False, skip_response_elem=True)

        for item in data:
            if security_groups := item.get('security_groups'):
                if group_id in security_groups:
                    security_groups.remove(group_id)
                    item['security_groups'] = security_groups
                    to_update.append(item)

        for item in to_update: # type: ignore
            _= self.invoke('zato.http-soap.edit', item)

# ################################################################################################################################
# ################################################################################################################################

class GetMemberList(Service):
    """ Returns current members of a group.
    """
    input:'any_' = 'group_type', 'group_id', '-should_serialize'

    def handle(self):

        # Local variables
        input = self.request.input

        group = _find_group_by_id(self.server, input.group_id)
        if not group:
            member_list = []
        else:
            member_list = []
            for member_str in group.get('members') or []:
                item = _member_string_to_dict(self.server, input.group_id, member_str)
                member_list.append(Member.from_dict(item))

        member_list = [elem.to_dict() for elem in member_list]

        if input.should_serialize:
            member_list = dumps(member_list)

        self.response.payload = member_list

# ################################################################################################################################
# ################################################################################################################################

class GetMemberCount(Service):
    """ Returns information about how many members are in each group.
    """
    input:'any_' = 'group_type', '-should_serialize'

    def handle(self):

        # Local variables
        input = self.request.input

        member_count = {}
        for grp in self.server.config_store.get_list('groups'):
            gid = grp.get('id')
            members = grp.get('members') or []
            member_count[gid] = len(members)

        if input.should_serialize:
            member_count = dumps(member_count)
        self.response.payload = member_count

# ################################################################################################################################
# ################################################################################################################################

class EditMemberList(Service):
    """ Adds members to or removes them from a group.
    """
    input:'any_' = 'group_action', 'group_id', AsIs('-member_id_list'), AsIs('-members')

    def _get_member_id_list_from_name_list(self, member_name_list:'any_') -> 'strlist':

        # Our response to produce
        out:'strlist' = []

        # Make sure this is actually a list
        member_name_list = member_name_list if isinstance(member_name_list, list) else [member_name_list] # type: ignore

        # Get a list of all the security definitions possible, out of which we will be building our IDs.
        security_list = self.invoke('zato.security.get-list', skip_response_elem=True)
        for item in member_name_list:
            if isinstance(item, dict):
                item_name:'str' = item['name']
            else:
                item_name = item
            for security in security_list:
                if item_name == security['name']:
                    sec_type = security['sec_type']
                    sec_def_id = security['id']
                    member_name = f'{sec_type}-{sec_def_id}'
                    out.append(member_name)

        return out

# ################################################################################################################################

    def handle(self):

        # Local variables
        input = self.request.input

        group = _find_group_by_id(self.server, input.group_id)
        if not group:
            return

        # We need to have member IDs in further steps so if we have names, they have to be turned into IDs here.
        if not (member_id_list := input.get('member_id_list')):
            member_id_list = self._get_member_id_list_from_name_list(input.members)

        if not member_id_list:
            return

        members = list(group.get('members') or [])
        name = group['name']

        if input.group_action == Groups.Membership_Action.Add:
            for mid in member_id_list:
                if mid not in members:
                    members.append(mid)
        else:
            for mid in member_id_list:
                if mid in members:
                    members.remove(mid)

        data = {
            'id': int(group['id']),
            'name': name,
            'members': members,
        }
        self.server.config_store.set('groups', name, data)

# ################################################################################################################################
# ################################################################################################################################
