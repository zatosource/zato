'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from json import dumps

# Faker
from faker.utils.text import slugify

# Zato
from zato.common.api import Groups
from zato.common.odb.query.generic import GroupsWrapper
from zato.server.service import AsIs, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class GroupsManager:

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server
        self.cluster_id = self.server.cluster_id

# ################################################################################################################################

    def create(self, group_type:'str', group_name:'str') -> 'str':

        # A slag of the name becomes the group's ID ..
        group_id = slugify(group_name)

        # .. work in a new SQL transaction ..
        with closing(self.server.odb.session()) as session:

            # .. build and object that will wrap access to the SQL database ..
            wrapper = GroupsWrapper(session, self.cluster_id)
            wrapper.type_ = Groups.Type.Group_Parent
            wrapper.subtype = group_type

            # .. build a request that represents the group ..
            data = {
                'group_id': group_id,
            }
            data = dumps(data)

            # .. do create the group now ..
            insert = wrapper.create(group_name, data)

            # .. commit the changes ..
            session.execute(insert)
            session.commit()

        # .. and return its ID to our caller.
        return group_id

# ################################################################################################################################

    def delete(self, group_type:'str', group_id:'str') -> 'None':
        raise NotImplementedError()

# ################################################################################################################################

    def get_list(self, group_type:'str') -> 'anylist':

        # Our reponse to produce
        out = []

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
# ################################################################################################################################

class GetList(Service):
    """ Returns all groups matching the input criteria.
    """
    name = 'dev.groups.get-list'
    input:'any_' = AsIs('group_type')

    def handle(self):
        groups_manager = GroupsManager(self.server)
        group_list = groups_manager.get_list(self.request.input.group_type)
        self.response.payload = group_list

# ################################################################################################################################
# ################################################################################################################################

class Create(Service):
    """ Creates a new group.
    """
    name = 'dev.groups.create'

    input:'any_' = 'group_type', 'name'
    output:'any_' = AsIs('id'), 'name'

    def handle(self):
        groups_manager = GroupsManager(self.server)
        group_id = groups_manager.create(self.request.input.group_type, self.request.input.name)
        self.response.payload.id = group_id
        self.response.payload.name = self.request.input.name

# ################################################################################################################################
# ################################################################################################################################
'''
