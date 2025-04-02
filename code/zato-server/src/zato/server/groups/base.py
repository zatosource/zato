# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.common.api import GENERIC, Groups, SEC_DEF_TYPE
from zato.common.groups import Member
from zato.common.odb.model import GenericObject as ModelGenericObject
from zato.common.odb.query.generic import GroupsWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, intnone, list_, strlist
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

_generic_attr_name = GENERIC.ATTR_NAME
ModelGenericObjectTable:'any_' = ModelGenericObject.__table__

# ################################################################################################################################
# ################################################################################################################################

class GroupsManager:

    def __init__(self, server:'ParallelServer', session:'any_'=None) -> 'None':
        self.server = server
        self.session = session or self.server.odb.session
        self.cluster_id = self.server.cluster_id

# ################################################################################################################################

    def create_group(self, group_type:'str', group_name:'str') -> 'str':

        # Work in a new SQL transaction ..
        with closing(self.session()) as session:

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
        with closing(self.session()) as session:

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
        with closing(self.session()) as session:

            # .. build and object that will wrap access to the SQL database ..
            wrapper = GroupsWrapper(session, self.cluster_id)

            # .. delete the group ..
            delete_group = wrapper.delete_by_id(group_id)
            session.execute(delete_group)

            # .. remove its members in bulk ..
            remove_members = wrapper.delete_by_parent_object_id(group_id)
            session.execute(remove_members)

            # .. and commit the changes now.
            # session.commit()

# ################################################################################################################################

    def get_group_list(self, group_type:'str') -> 'anylist':

        # Our reponse to produce
        out:'anylist' = []

        # Work in a new SQL transaction ..
        with closing(self.session()) as session:

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

    def get_member_list(self, group_type:'str', group_id:'intnone'=None) -> 'list_[Member]':

        # Our reponse to produce
        out:'list_[Member]' = []

        # Work in a new SQL transaction ..
        with closing(self.session()) as session:

            # .. build and object that will wrap access to the SQL database ..
            wrapper = GroupsWrapper(session, self.cluster_id)

            # .. get all the results ..
            results = wrapper.get_list(Groups.Type.Group_Member, group_type, parent_object_id=group_id)

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

            # .. build a new business object for the member ..
            member = Member.from_dict(item)

            # .. populate our response list ..
            out.append(member)

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
        with closing(self.session()) as session:

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
        with closing(self.session()) as session:

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
        with closing(self.session()) as session:

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
