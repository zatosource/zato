# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps
from operator import itemgetter

# Zato
from zato.common.api import CONNECTION, Groups
from zato.common.broker_message import Groups as Broker_Message_Groups
from zato.common.odb.model import GenericObject as ModelGenericObject
from zato.server.service import AsIs, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

ModelGenericObjectTable:'any_' = ModelGenericObject.__table__

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

        group_list = self.server.groups_manager.get_group_list(group_type)
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

        id = self.server.groups_manager.create_group(input.group_type, input.name)

        self.invoke(
            EditMemberList,
            group_type=input.group_type,
            group_action=Groups.Membership_Action.Add,
            group_id=id,
            members=input.members,
        )

        self.response.payload.id = id
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

        self.server.groups_manager.edit_group(input.id, input.group_type, input.name)

        if input.members:

            group_members = self.server.groups_manager.get_member_list(input.group_type, input.id)

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

        # .. enrich the message that is to be published ..
        input.to_add = to_add
        input.to_remove = to_remove

        # .. now, let all the threads know about the update.
        input.action = Broker_Message_Groups.Edit.value
        self.broker_client.publish(input)

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

        # Delete this group from the database ..
        self.server.groups_manager.delete_group(group_id)

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

        # .. now, let all the threads know about the update.
        input.action = Broker_Message_Groups.Delete.value
        self.broker_client.publish(input)

# ################################################################################################################################
# ################################################################################################################################

class GetMemberList(Service):
    """ Returns current members of a group.
    """
    input:'any_' = 'group_type', 'group_id', '-should_serialize'

    def handle(self):

        # Local variables
        input = self.request.input

        member_list = self.server.groups_manager.get_member_list(input.group_type, input.group_id)
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

        member_count = self.server.groups_manager.get_member_count(input.group_type)
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

        # We need to have member IDs in further steps so if we have names, they have to be turned into IDs here.
        if not (member_id_list := input.get('member_id_list')):
            member_id_list = self._get_member_id_list_from_name_list(input.members)

        if not member_id_list:
            return

        if input.group_action == Groups.Membership_Action.Add:
            func = self.server.groups_manager.add_members_to_group
        else:
            func = self.server.groups_manager.remove_members_from_group

        func(input.group_id, member_id_list)

        # .. now, let all the threads know about the update.
        input.action = Broker_Message_Groups.Edit_Member_List.value
        self.broker_client.publish(input)

# ################################################################################################################################
# ################################################################################################################################
