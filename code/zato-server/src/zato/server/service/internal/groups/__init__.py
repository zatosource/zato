'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from json import dumps

# Zato
from zato.common.api import Groups, SEC_DEF_TYPE
from zato.common.odb.query.generic import GroupsWrapper
from zato.server.service import AsIs, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, intnone, strlist
    from zato.server.base.parallel import ParallelServer

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

            # .. do delete the group ..
            delete = wrapper.delete(group_id)

            # .. commit the changes now.
            session.execute(delete)
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
                Groups.Type.API_Credentials,
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

    def add_members_to_group(self, group_id:'int', member_id_list:'strlist') -> 'None':

        # Work in a new SQL transaction ..
        with closing(self.server.odb.session()) as session:

            # .. build and object that will wrap access to the SQL database ..
            wrapper = GroupsWrapper(session, self.cluster_id)

            # .. do add the members to the group now ..
            for member_id in member_id_list:

                # This is a composite name because each such name has to be unique in the database
                name = f'{member_id}-{group_id}'

                insert = wrapper.create(
                    name, '',
                    Groups.Type.Group_Member,
                    Groups.Type.API_Credentials,
                    parent_object_id=group_id)

                session.execute(insert)

            # .. and commit the changes.
            session.commit()

# ################################################################################################################################

    def remove_members_from_group(self, group_id:'str', member_id_list:'strlist') -> 'None':
        self
        self

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):
    """ Returns all groups matching the input criteria.
    """
    name = 'dev.groups.get-list'
    input:'any_' = 'group_type'

    def handle(self):
        groups_manager = GroupsManager(self.server)
        group_list = groups_manager.get_group_list(self.request.input.group_type)
        self.response.payload = group_list

# ################################################################################################################################
# ################################################################################################################################

class Create(Service):
    """ Creates a new group.
    """
    name = 'dev.groups.create'

    input:'any_' = 'group_type', 'name'
    output:'any_' = 'id', 'name'

    def handle(self):

        groups_manager = GroupsManager(self.server)
        id = groups_manager.create_group(self.request.input.group_type, self.request.input.name)

        self.response.payload.id = id
        self.response.payload.name = self.request.input.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(Service):
    """ Updates an existing group.
    """
    name = 'dev.groups.edit'

    input:'any_' = 'id', 'group_type', 'name'
    output:'any_' = 'id', 'name'

    def handle(self):

        # Local variables
        input = self.request.input

        groups_manager = GroupsManager(self.server)
        groups_manager.edit_group(input.id, input.group_type, input.name)

        self.response.payload.id = self.request.input.id
        self.response.payload.name = self.request.input.name

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

        groups_manager = GroupsManager(self.server)
        groups_manager.delete_group(input.id)

# ################################################################################################################################
# ################################################################################################################################

class GetMemberList(Service):
    """ Returns current members of a group..
    """
    name = 'dev.groups.get-member-list'
    input:'any_' = 'group_type', 'group_id'

    def handle(self):

        # Local variables
        input = self.request.input

        groups_manager = GroupsManager(self.server)
        member_list = groups_manager.get_member_list(input.group_type, input.group_id)
        self.response.payload = dumps(member_list)

# ################################################################################################################################
# ################################################################################################################################

class EditMemberList(Service):
    """ Adds members to or removes them from a group.
    """
    name = 'dev.groups.edit-member-list'
    input:'any_' = 'action', AsIs('group_id'), AsIs('member_id_list')

    def handle(self):

        # Local variables
        input = self.request.input

        groups_manager = GroupsManager(self.server)
        if input.action == Groups.Membership_Action.Add:
            func = groups_manager.add_members_to_group
        else:
            func = groups_manager.remove_members_from_group

        func(input.group_id, input.member_id_list)

# ################################################################################################################################
# ################################################################################################################################
'''
