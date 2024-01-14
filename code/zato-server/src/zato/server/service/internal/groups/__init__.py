'''# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from json import dumps
from operator import itemgetter

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.api import CONNECTION, GENERIC, Groups, SEC_DEF_TYPE
from zato.common.broker_message import Groups as Broker_Message_Groups
from zato.common.odb.model import GenericObject as ModelGenericObject
from zato.common.odb.query.generic import GroupsWrapper
from zato.server.service import AsIs, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, intnone, strlist
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

_generic_attr_name = GENERIC.ATTR_NAME
ModelGenericObjectTable:'any_' = ModelGenericObject.__table__

# ################################################################################################################################
# ################################################################################################################################

class GroupsManager:

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server
        self.cluster_id = self.server.cluster_id

# ################################################################################################################################

    def create_group(self, group_type:'str', group_name:'str') -> 'str':

        # Work in a new SQL transaction ..
        with closing(self.server.odb.session()) as session:

            # .. build and object that will wrap access to the SQL database ..
            wrapper = GroupsWrapper(session, self.cluster_id)
            wrapper.type_ = Groups.Type.Group_Parent
            wrapper.subtype = group_type

            # .. do create the group now ..
            insert = wrapper.create(group_name, '')

            # .. commit the changes ..
            session.execute(insert)
            session.commit()

            # .. get the newly added group now ..
            group = wrapper.get(group_name)

        # .. and return its ID to our caller.
        return group['id']

# ################################################################################################################################

    def edit_group(self, group_id:'int', group_type:'str', group_name:'str') -> 'None':

        # Work in a new SQL transaction ..
        with closing(self.server.odb.session()) as session:

            # .. build and object that will wrap access to the SQL database ..
            wrapper = GroupsWrapper(session, self.cluster_id)
            wrapper.type_ = Groups.Type.Group_Parent
            wrapper.subtype = group_type

            # .. do edit the group's name (but not its opaque attributes) ..
            update = wrapper.update(group_name, id=group_id)

            # .. and commit the changes now.
            session.execute(update)
            session.commit()

# ################################################################################################################################

    def delete_group(self, group_id:'int') -> 'None':

        # Work in a new SQL transaction ..
        with closing(self.server.odb.session()) as session:

            # .. build and object that will wrap access to the SQL database ..
            wrapper = GroupsWrapper(session, self.cluster_id)

            # .. delete the group ..
            delete_group = wrapper.delete_by_id(group_id)
            session.execute(delete_group)

            # .. remove its members in bulk ..
            remove_members = wrapper.delete_by_parent_object_id(group_id)
            session.execute(remove_members)

            # .. and commit the changes now.
            session.commit()

# ################################################################################################################################

    def get_group_list(self, group_type:'str') -> 'anylist':

        # Our reponse to produce
        out:'anylist' = []

        # Work in a new SQL transaction ..
        with closing(self.server.odb.session()) as session:

            # .. build and object that will wrap access to the SQL database ..
            wrapper = GroupsWrapper(session, self.cluster_id)
            wrapper.type_ = Groups.Type.Group_Parent
            wrapper.subtype = group_type

            # .. get all the results ..
            results = wrapper.get_list()

            # .. populate our response ..
            out[:] = results

        # .. and return the output to our caller.
        return out

# ################################################################################################################################

    def get_member_list(self, group_type:'str', group_id:'intnone'=None) -> 'anylist':

        # Our reponse to produce
        out:'anylist' = []

        # Work in a new SQL transaction ..
        with closing(self.server.odb.session()) as session:

            # .. build and object that will wrap access to the SQL database ..
            wrapper = GroupsWrapper(session, self.cluster_id)

            # .. get all the results ..
            results = wrapper.get_list(
                Groups.Type.Group_Member,
                Groups.Type.API_Clients,
                parent_object_id=group_id
            )

        # .. extract security information for each item ..
        for item in results:

            sec_info = item['name']
            sec_info = sec_info.split('-')

            sec_type, security_id, _ignored_sql_group_id = sec_info
            security_id = int(security_id)

            if sec_type == SEC_DEF_TYPE.BASIC_AUTH:
                get_sec_func = self.server.worker_store.basic_auth_get_by_id
            elif sec_type == SEC_DEF_TYPE.APIKEY:
                get_sec_func = self.server.worker_store.apikey_get_by_id
            else:
                raise Exception(f'Unrecognized sec_type: {sec_type}')

            sec_config = get_sec_func(security_id)

            item['name'] = sec_config['name']
            item['security_id'] = sec_config['id']
            item['sec_type'] = sec_type

        # .. populate our response ..
        out[:] = results

        # .. and return the output to our caller.
        return out

# ################################################################################################################################

    def get_member_count(self, group_type:'str') -> 'anydict':

        # Our response to produce
        out:'anydict' = {}

        # By default, assume that there are no members in any group
        group_list = self.get_group_list(group_type)
        for item in group_list:
            group_id = item['id']
            out[group_id] = 0

        # Work in a new SQL transaction ..
        with closing(self.server.odb.session()) as session:

            q = select([
                ModelGenericObjectTable.c.parent_object_id,
                func.count(ModelGenericObjectTable.c.parent_object_id),
                ]).\
                where(and_(
                    ModelGenericObjectTable.c.type_ == Groups.Type.Group_Member,
                    ModelGenericObjectTable.c.subtype == group_type,
                )).\
                group_by(ModelGenericObjectTable.c.parent_object_id)

            result:'any_' = session.execute(q).fetchall()

            for item in result:
                group_id, member_count = item
                out[group_id] = member_count

        return out

# ################################################################################################################################

    def add_members_to_group(self, group_id:'int', member_id_list:'strlist') -> 'None':

        # Local variables
        member_list = []

        # Process each input member ..
        for member_id in member_id_list:

            # .. each one needs a composite name because each such name has to be unique in the database
            name = f'{member_id}-{group_id}'

            # .. append it for later use
            member_list.append({
                'name': name,
                _generic_attr_name: '',
            })

        # Work in a new SQL transaction ..
        with closing(self.server.odb.session()) as session:

            # .. build and object that will wrap access to the SQL database ..
            wrapper = GroupsWrapper(session, self.cluster_id)

            # .. do add the members to the group now ..
            insert = wrapper.create_many(
                member_list,
                Groups.Type.Group_Member,
                Groups.Type.API_Clients,
                parent_object_id=group_id
            )

            # .. run the query ..
            session.execute(insert)

            # .. and commit the changes.
            session.commit()

# ################################################################################################################################

    def remove_members_from_group(self, group_id:'str', member_id_list:'strlist') -> 'None':

        # Work in a new SQL transaction ..
        with closing(self.server.odb.session()) as session:

            # .. build and object that will wrap access to the SQL database ..
            wrapper = GroupsWrapper(session, self.cluster_id)

            # .. delete members from the group now ..
            for member_id in member_id_list:

                # This is a composite name because each such name has to be unique in the database
                name = f'{member_id}-{group_id}'

                delete = wrapper.delete_by_name(name, parent_object_id=group_id)
                session.execute(delete)

            # .. and commit the changes.
            session.commit()

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):
    """ Returns all groups matching the input criteria.
    """
    name = 'dev.groups.get-list'
    input:'any_' = 'group_type', '-needs_members', '-needs_short_members'

    def handle(self):

        group_type = self.request.input.group_type
        needs_members = self.request.input.needs_members
        needs_short_members = self.request.input.needs_short_members

        groups_manager = GroupsManager(self.server)
        group_list = groups_manager.get_group_list(group_type)
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
    name = 'dev.groups.create'

    input:'any_' = 'group_type', 'name', AsIs('-members')
    output:'any_' = 'id', 'name'

    def handle(self):

        # Local variables
        input = self.request.input

        groups_manager = GroupsManager(self.server)
        id = groups_manager.create_group(input.group_type, input.name)

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
    name = 'dev.groups.edit'

    input:'any_' = 'id', 'group_type', 'name', AsIs('-members')
    output:'any_' = 'id', 'name'

    def handle(self):

        # Local variables
        input = self.request.input

        # All the new members of this group
        to_add:'strlist' = []

        # All the members that have to be removed from the group
        to_remove:'strlist' = []

        groups_manager = GroupsManager(self.server)
        groups_manager.edit_group(input.id, input.group_type, input.name)

        if input.members:

            group_members = groups_manager.get_member_list(input.group_type, input.id)

            input_member_names = set(item['name'] for item in input.members)
            group_member_names = set(item['name'] for item in group_members)

            for group_member_name in group_member_names:
                if not group_member_name in input_member_names:
                    to_remove.append(group_member_name)

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
    name = 'dev.groups.delete'

    input:'any_' = 'id'

    def handle(self):

        # Local variables
        input = self.request.input
        group_id = int(input.id)

        # Delete this group from the database ..
        groups_manager = GroupsManager(self.server)
        groups_manager.delete_group(group_id)

        # .. make sure the database configuration of channels using it is also updated ..
        to_update = []
        data = self.invoke('zato.http-soap.get-list', connection=CONNECTION.CHANNEL, paginate=False, skip_response_elem=True)

        for item in data:
            if security_groups := item.get('security_groups'):
                if group_id in security_groups:
                    security_groups.remove(group_id)
                    item['security_groups'] = security_groups
                    to_update.append(item)

        for item in to_update:
            _= self.invoke('zato.http-soap.edit', item)

        # .. now, let all the threads know about the update.
        input.action = Broker_Message_Groups.Delete.value
        self.broker_client.publish(input)

# ################################################################################################################################
# ################################################################################################################################

class GetMemberList(Service):
    """ Returns current members of a group.
    """
    name = 'dev.groups.get-member-list'
    input:'any_' = 'group_type', 'group_id', '-should_serialize'

    def handle(self):

        # Local variables
        input = self.request.input

        groups_manager = GroupsManager(self.server)
        member_list = groups_manager.get_member_list(input.group_type, input.group_id)
        if input.should_serialize:
            member_list = dumps(member_list)
        self.response.payload = member_list

# ################################################################################################################################
# ################################################################################################################################

class GetMemberCount(Service):
    """ Returns information about how many members are in each group.
    """
    name = 'dev.groups.get-member-count'
    input:'any_' = 'group_type', '-should_serialize'

    def handle(self):

        # Local variables
        input = self.request.input

        groups_manager = GroupsManager(self.server)
        member_count = groups_manager.get_member_count(input.group_type)
        if input.should_serialize:
            member_count = dumps(member_count)
        self.response.payload = member_count

# ################################################################################################################################
# ################################################################################################################################

class EditMemberList(Service):
    """ Adds members to or removes them from a group.
    """
    name = 'dev.groups.edit-member-list'
    input:'any_' = 'group_action', 'group_id', AsIs('-member_id_list'), AsIs('-members')

# ################################################################################################################################

    def _get_member_id_list_from_name_list(self, member_name_list:'any_') -> 'strlist':

        # Our response to produce
        out:'strlist' = []

        # Make sure this is actually a list
        member_name_list = member_name_list if isinstance(member_name_list, list) else [member_name_list] # type: ignore

        # Get a list of all the security definitions possible, out of which we will be building our IDs.
        security_list = self.invoke('zato.security.get-list', skip_response_elem=True)
        for item in member_name_list:
            if isinstance(item, dict):
                item_name = item['name']
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

        groups_manager = GroupsManager(self.server)

        if input.group_action == Groups.Membership_Action.Add:
            func = groups_manager.add_members_to_group
        else:
            func = groups_manager.remove_members_from_group

        func(input.group_id, member_id_list)

        # .. now, let all the threads know about the update.
        input.action = Broker_Message_Groups.Edit_Member_List.value
        self.broker_client.publish(input)

# ################################################################################################################################
# ################################################################################################################################
'''
