# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import dumps
from operator import itemgetter

# Zato
from zato.common.api import CONNECTION, Groups
from zato.common.odb.model import GenericObject as ModelGenericObject
from zato.server.service import AsIs, Service

logger_groups = logging.getLogger('zato.groups.service')

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
    input:'any_' = 'group_type', 'name', AsIs('-member_id_list')
    output:'any_' = 'id', 'name'

    def handle(self):

        # Local variables
        input = self.request.input
        member_id_list = input.get('member_id_list') or []

        logger_groups.info('Create.handle: group_type=%s, name=%s, member_id_list=%s', input.group_type, input.name, member_id_list)

        id = self.server.groups_manager.create_group(input.group_type, input.name)

        if member_id_list:
            self.invoke(
                EditMemberList,
                group_action=Groups.Membership_Action.Add,
                group_id=id,
                member_id_list=member_id_list,
            )

        self.response.payload.id = id
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(Service):
    """ Updates an existing group.
    """
    input:'any_' = 'id', 'group_type', 'name', AsIs('-member_id_list')
    output:'any_' = 'id', 'name'

    def handle(self):

        # Local variables
        input = self.request.input
        member_id_list = input.get('member_id_list') or []

        logger_groups.info('Edit.handle: id=%s, group_type=%s, name=%s, member_id_list=%s',
            input.id, input.group_type, input.name, member_id_list)

        # All the new members of this group
        to_add:'strlist' = []

        # All the members that have to be removed from the group
        to_remove:'strlist' = []

        self.server.groups_manager.edit_group(input.id, input.group_type, input.name)

        if member_id_list:

            group_members = self.server.groups_manager.get_member_list(input.group_type, input.id)

            logger_groups.info('Edit.handle: group_members=%s', group_members)

            input_member_ids = set(member_id_list)
            group_member_ids = {f'{m.sec_type}-{m.security_id}' for m in group_members}

            logger_groups.info('Edit.handle: input_member_ids=%s, group_member_ids=%s',
                input_member_ids, group_member_ids)

            for gm_id in group_member_ids:
                if gm_id not in input_member_ids:
                    to_remove.append(gm_id)

            for im_id in input_member_ids:
                if im_id not in group_member_ids:
                    to_add.append(im_id)

        logger_groups.info('Edit.handle: to_add=%s, to_remove=%s', to_add, to_remove)

        if to_add:
            _ = self.invoke(
                EditMemberList,
                group_action=Groups.Membership_Action.Add,
                group_id=input.id,
                member_id_list=to_add,
            )

        if to_remove:
            _ = self.invoke(
                EditMemberList,
                group_action=Groups.Membership_Action.Remove,
                group_id=input.id,
                member_id_list=to_remove,
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

        logger_groups.info('Delete.handle: group_id=%s', group_id)

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

        logger_groups.info('EditMemberList.handle: group_action=%s, group_id=%s, member_id_list=%s, members=%s',
            input.group_action, input.group_id, input.get('member_id_list'), input.get('members'))

        # We need to have member IDs in further steps so if we have names, they have to be turned into IDs here.
        if not (member_id_list := input.get('member_id_list')):
            member_id_list = self._get_member_id_list_from_name_list(input.members)

        logger_groups.info('EditMemberList.handle: resolved member_id_list=%s', member_id_list)

        if not member_id_list:
            logger_groups.info('EditMemberList.handle: empty member_id_list, returning early')
            return

        if input.group_action == Groups.Membership_Action.Add:
            func = self.server.groups_manager.add_members_to_group
        else:
            func = self.server.groups_manager.remove_members_from_group

        logger_groups.info('EditMemberList.handle: calling %s with group_id=%s, member_id_list=%s',
            func.__name__, input.group_id, member_id_list)

        func(input.group_id, member_id_list)

# ################################################################################################################################
# ################################################################################################################################
