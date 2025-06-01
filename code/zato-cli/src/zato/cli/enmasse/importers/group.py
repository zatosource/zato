# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
import logging

# SQLAlchemy
from sqlalchemy import and_, select, delete

# Zato
from zato.common.api import Groups
from zato.common.odb.model import GenericObject
from zato.common.odb.query.generic import GroupsWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class GroupImporter:
    """ A class that knows how to import security groups from YAML.
    """

    def __init__(self, importer):
        self.importer = importer
        self.group_defs = {}

# ################################################################################################################################

    def get_groups_from_db(self, session:'SASession') -> 'anydict':
        """ Returns all security groups from the database, keyed by name.
        """
        out = {}
        cluster_id = self.importer.cluster_id

        # Use a single query to get all groups
        with closing(session) as session:
            # Build a query for all groups - explicitly select columns
            query = select([
                GenericObject.id,
                GenericObject.name
                ]).where(and_(
                    GenericObject.type_ == Groups.Type.Group_Parent,
                    GenericObject.subtype == Groups.Type.API_Clients,
                    GenericObject.cluster_id == cluster_id,
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
                        GenericObject.cluster_id == cluster_id,
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

    def delete_group(self, group_name, group_id, session:'SASession') -> 'None':
        """ Deletes a group and all its members from the database.
        """
        cluster_id = self.importer.cluster_id

        with closing(session) as session:
            # First, delete all members of the group
            member_delete = delete(GenericObject).where(
                and_(
                    GenericObject.type_ == Groups.Type.Group_Member,
                    GenericObject.subtype == Groups.Type.API_Clients,
                    GenericObject.parent_object_id == group_id,
                    GenericObject.cluster_id == cluster_id
                )
            )
            session.execute(member_delete)

            # Then delete the group itself
            group_delete = delete(GenericObject).where(
                and_(
                    GenericObject.id == group_id,
                    GenericObject.type_ == Groups.Type.Group_Parent,
                    GenericObject.subtype == Groups.Type.API_Clients,
                    GenericObject.cluster_id == cluster_id
                )
            )
            session.execute(group_delete)

            # Commit all changes
            session.commit()

            logger.info('Deleted group %s with ID %s', group_name, group_id)

# ################################################################################################################################

    def create_group(self, group:'anydict', session:'SASession') -> 'any_':
        """ Creates a new security group and adds members to it.
        """
        group_name = group['name']
        members = group.get('members', [])
        cluster_id = self.importer.cluster_id

        # Create the group
        with closing(session) as session:
            wrapper = GroupsWrapper(session, cluster_id)

            # Prepare the group data
            group_data = {
                'name': group_name,
                'opaque1': '',  # Equivalent to _generic_attr_name
            }

            # Create the group using create_many
            group_list = [group_data]
            insert = wrapper.create_many(
                group_list,
                Groups.Type.Group_Parent,
                Groups.Type.API_Clients
            )
            session.execute(insert)

            # Get the new group ID - need to query the database since create_many doesn't return it
            query = select([GenericObject.id]).where(
                and_(
                    GenericObject.name == group_name,
                    GenericObject.type_ == Groups.Type.Group_Parent,
                    GenericObject.subtype == Groups.Type.API_Clients,
                    GenericObject.cluster_id == cluster_id
                )
            )
            group_id_result = session.execute(query).fetchone()
            if not group_id_result:
                raise ValueError(f'Could not find newly created group: {group_name}')

            group_id = group_id_result['id']

            # Add members if there are any
            if members:
                logger.info('Adding members to new group %s: %s', group_name, sorted(members))
                member_ids = self._resolve_member_names(members)
                if member_ids:
                    # Add members directly using GroupsWrapper
                    member_list = []
                    for member_id in member_ids:
                        # Create a composite name
                        name = f'{member_id}-{group_id}'
                        member_list.append({
                            'name': name,
                            'opaque1': '',
                        })

                    # Insert members in bulk
                    if member_list:
                        insert = wrapper.create_many(
                            member_list,
                            Groups.Type.Group_Member,
                            Groups.Type.API_Clients,
                            parent_object_id=group_id
                        )
                        session.execute(insert)

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

                # Check if the group already exists
                if group_name in db_groups:
                    existing_group = db_groups[group_name]
                    group_id = existing_group['id']

                    # Delete the existing group and all its members
                    logger.info('Group %s already exists - deleting it first', group_name)
                    self.delete_group(group_name, group_id, session)

                # Create the group with all its members from YAML
                logger.info('Creating group %s with members from YAML', group_name)
                created_group = self.create_group(group, session)
                processed_groups.append(created_group)

                # Store the group definition for later use
                self.group_defs[group_name] = {
                    'id': created_group['id'],
                    'name': group_name
                }

            # Return processed groups and an empty list for updated groups (to match the expected interface)
            return processed_groups, []

        except Exception:
            logger.exception('Error synchronizing groups')
            raise

# ################################################################################################################################
# ################################################################################################################################
