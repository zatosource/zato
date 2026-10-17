# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
import logging

# SQLAlchemy
from sqlalchemy import and_, select, delete, update

# Zato
from zato.common.api import Groups
from zato.common.json_internal import dumps
from zato.common.odb.model import GenericObject
from zato.common.odb.query.generic import GroupsWrapper
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import any_, anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class GroupImporter:
    """ A class that knows how to import security groups from YAML.
    """

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer
        self.group_defs = {}

# ################################################################################################################################

    def get_groups_from_db(self, session:'SASession') -> 'anydict':
        """ Returns all security groups from the database, keyed by name.
        """
        out = {}

        # Use a single query to get all groups
        with closing(session) as session:
            # Build a query for all groups - explicitly select columns
            query = select([
                GenericObject.id,
                GenericObject.name
                ]).where(and_(
                    GenericObject.type_ == Groups.Type.Group_Parent,
                    GenericObject.subtype == Groups.Type.API_Clients,
                ))

            # Execute the query and get results
            groups = session.execute(query).fetchall()

            # Map the results
            for group in groups:
                # SQLAlchemy result row needs to be accessed like a dict
                name = group['name']
                out[name] = {
                    'id': group['id'],
                    'name': name,
                    'members': []
                }

            # If there are groups, get their members in a single query
            if out:
                # Get the group IDs
                group_ids = [group_data['id'] for group_data in out.values()]

                # Build a query for all members of these groups - explicitly select columns
                member_query = select([
                    GenericObject.id,
                    GenericObject.name,
                    GenericObject.parent_object_id
                    ]).where(and_(
                        GenericObject.type_ == Groups.Type.Group_Member,
                        GenericObject.subtype == Groups.Type.API_Clients,
                        GenericObject.parent_object_id.in_(group_ids),
                    ))

                # Execute the query and get results
                members = session.execute(member_query).fetchall()

                # Process members and add them to their respective groups
                for member in members:
                    parent_id = member['parent_object_id']

                    # Find which group this member belongs to
                    for group_data in out.values():
                        if group_data['id'] == parent_id:
                            # Extract member name from composite name (member_id-group_id)
                            composite_name = member['name']
                            parts = composite_name.split('-')

                            # Member names must be in the expected format
                            if len(parts) >= 2:
                                member_type, member_id = parts[0], parts[1]

                                # Find the original member name from security definitions
                                for sec_name, sec_def in self.importer.sec_defs.items():
                                    if str(sec_def.get('id')) == member_id and sec_def.get('type') == member_type:
                                        group_data['members'].append(sec_name)
                                        break

                            break

        return out

# ################################################################################################################################

    def _get_opaque(self, group:'anydict') -> 'str':
        """ Returns the opaque data of a group. A group may reference a quota tier by name,
        which is resolved to the tier's ID because that is what the group's opaque data stores.
        """
        group_name = group['name']

        out = ''

        if tier_name := group.get('quota_tier'):

            tier_def = self.importer.quota_tier_defs.get(tier_name)

            if not tier_def:
                raise ValueError(f'Quota tier `{tier_name}` not found for group `{group_name}`')

            out = dumps({'quota_tier': tier_def['id']})

        return out

# ################################################################################################################################

    def _add_members(
        self,
        wrapper:'GroupsWrapper',
        group_name:'str',
        group_id:'int',
        members:'strlist',
        session:'SASession',
        ) -> 'None':
        """ Inserts the members from YAML into a group.
        """
        if not members:
            return

        logger.info('Adding members to group %s: %s', group_name, sorted(members))
        member_ids = self._resolve_member_names(members)

        # Each member row is named after the member and the group it belongs to
        member_list = []
        for member_id in member_ids:
            name = f'{member_id}-{group_id}'
            member_list.append({
                'name': name,
                'opaque1': '',
            })

        insert = wrapper.create_many(
            member_list,
            Groups.Type.Group_Member,
            Groups.Type.API_Clients,
            parent_object_id=group_id
        )
        _ = session.execute(insert)

# ################################################################################################################################

    def update_group(self, group:'anydict', group_id:'int', session:'SASession') -> 'anydict':
        """ Replaces the members and the opaque data of an existing group. The group keeps its row and its ID,
        which MCP gateways and channels store as their reference to it.
        """
        group_name = group['name']
        members = group.get('members', [])
        opaque = self._get_opaque(group)

        with closing(session) as session:

            # The members the group has are replaced by the ones from YAML ..
            member_delete = delete(GenericObject).where(
                and_(
                    GenericObject.type_ == Groups.Type.Group_Member,
                    GenericObject.subtype == Groups.Type.API_Clients,
                    GenericObject.parent_object_id == group_id,
                )
            )
            _ = session.execute(member_delete)

            # .. the group's own row receives its opaque data anew ..
            group_update = update(GenericObject).where(
                and_(
                    GenericObject.id == group_id,
                    GenericObject.type_ == Groups.Type.Group_Parent,
                    GenericObject.subtype == Groups.Type.API_Clients,
                )
            ).values(opaque1=opaque, last_modified=utcnow())
            _ = session.execute(group_update)

            # .. and the members from YAML are added.
            wrapper = GroupsWrapper(session)
            self._add_members(wrapper, group_name, group_id, members, session)

            session.commit()

        logger.info('Updated group %s with ID %s', group_name, group_id)

        out = {
            'id': group_id,
            'name': group_name,
            'members': members
        }
        return out

# ################################################################################################################################

    def create_group(self, group:'anydict', session:'SASession') -> 'any_':
        """ Creates a new security group and adds members to it.
        """
        group_name = group['name']
        members = group.get('members', [])
        opaque = self._get_opaque(group)

        # Create the group
        with closing(session) as session:
            wrapper = GroupsWrapper(session)

            # Prepare the group data
            group_data = {
                'name': group_name,
                'opaque1': opaque,
            }

            # Create the group using create_many
            group_list = [group_data]
            insert = wrapper.create_many(
                group_list,
                Groups.Type.Group_Parent,
                Groups.Type.API_Clients
            )
            _ = session.execute(insert)

            # Get the new group ID - need to query the database since create_many doesn't return it
            query = select([GenericObject.id]).where(
                and_(
                    GenericObject.name == group_name,
                    GenericObject.type_ == Groups.Type.Group_Parent,
                    GenericObject.subtype == Groups.Type.API_Clients,
                )
            )
            group_id_result = session.execute(query).fetchone()
            if not group_id_result:
                raise ValueError(f'Could not find newly created group: {group_name}')

            group_id = group_id_result['id']

            # Add members if there are any
            self._add_members(wrapper, group_name, group_id, members, session)

            # Commit all changes
            session.commit()
        return {
            'id': group_id,
            'name': group_name,
            'members': members
        }

# ################################################################################################################################

    def _resolve_member_names(self, member_names:'strlist') -> 'strlist':
        """ Resolves member names to their IDs based on security definitions.
        """
        member_ids = []

        for member_name in member_names:

            # Look up the security definition by name
            sec_def = self.importer.sec_defs.get(member_name)

            # Log available definitions for troubleshooting
            logger.info('Security definitions available: %s', list(self.importer.sec_defs.keys()))

            if not sec_def:
                msg = f'Security definition "{member_name}" not found among "{self.importer.sec_defs}"'
                logger.error(msg)
                raise Exception(msg)

            # Get the ID and type from the security definition
            sec_id = sec_def['id']
            sec_type = sec_def['type']

            # Create a member ID in the format type-id
            member_id = f'{sec_type}-{sec_id}'
            member_ids.append(member_id)

        return member_ids

# ################################################################################################################################

    def sync_groups(self, group_list:'anylist', session:'SASession') -> 'tuple[anylist, anylist]':
        """ Synchronizes security groups from YAML with the database.
        """
        # Lists to store processed groups
        processed_groups = []
        self.group_defs = {}

        try:
            # Get existing groups from database
            db_groups = self.get_groups_from_db(session)

            # Process each group from YAML
            for group in group_list:
                group_name = group['name']

                # An existing group keeps its ID and receives the members from YAML ..
                if group_name in db_groups:
                    group_id = db_groups[group_name]['id']
                    logger.info('Updating group %s with members from YAML', group_name)
                    processed_group = self.update_group(group, group_id, session)

                # .. while a new one is created with them.
                else:
                    logger.info('Creating group %s with members from YAML', group_name)
                    processed_group = self.create_group(group, session)

                processed_groups.append(processed_group)

                # Store the group definition for later use
                self.group_defs[group_name] = {
                    'id': processed_group['id'],
                    'name': group_name
                }

            # Return processed groups and an empty list for updated groups (to match the expected interface)
            return processed_groups, []

        except Exception:
            logger.exception('Error synchronizing groups')
            raise

# ################################################################################################################################
# ################################################################################################################################
