'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Faker
from faker.utils.text import slugify

# Zato
from zato.common.odb.query.generic import GroupsWrapper
from zato.server.service import AsIs, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class GroupsManager:
    sql_wrapper: 'GroupsWrapper'

    def __init__(self, cluster_id:'int')

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):
    """ Returns all groups matching the input criteria.
    """
    name = 'dev.groups.get-list'
    input:'any_' = AsIs('group_type')

    def handle(self):
        self.response.payload = '[]'

# ################################################################################################################################
# ################################################################################################################################

class Create(Service):
    """ Returns all groups matching the input criteria.
    """
    name = 'dev.groups.create'

    input:'any_' = 'group_type', 'name'
    output:'any_' = AsIs('id'), 'name'

    def handle(self):
        self.response.payload.id = slugify(self.request.input.name)
        self.response.payload.name = self.request.input.name

# ################################################################################################################################
# ################################################################################################################################
'''
