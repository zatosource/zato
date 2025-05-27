# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
import logging

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.api import Groups
from zato.common.odb.model import GenericObject
from zato.server.groups.base import GroupsManager

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
        cluster_id = self.importer.server.cluster_id

        # Use a single query to get all groups
        with closing(session) as session:
            # Build a query for all groups
            query = select([GenericObject]).\
                where(and_(
                    GenericObject.type_ == Groups.Type.Group_Parent,
                    GenericObject.subtype == Groups.Type.API_Clients,
                    GenericObject.cluster_id == cluster_id,
                ))

            # Execute the query and get results
            groups = session.execute(query).fetchall()

            # Map the results
            for group in groups:
                name = group.name
                out[name] = {
                    'id': group.id,
                    'name': name,
                    'members': []
                }

            # If there are groups, get their members in a single query
            if out:
                # Get the group IDs
                group_ids = [group_data['id'] for group_data in out.values()]

                # Build a query for all members of these groups
                member_query = select([GenericObject]).\
                    where(and_(
                        GenericObject.type_ == Groups.Type.Group_Member,
                        GenericObject.subtype == Groups.Type.API_Clients,
                        GenericObject.parent_object_id.in_(group_ids),
                        GenericObject.cluster_id == cluster_id,
                    ))

                # Execute the query and get results
                members = session.execute(member_query).fetchall()

                # Process members and add them to their respective groups
                for member in members:
                    parent_id = member.parent_object_id

                    # Find which group this member belongs to
                    for group_data in out.values():
                        if group_data['id'] == parent_id:
                            # Extract the security definition ID from the member name
                            # The format is {sec_def_id}-{group_id}
                            member_name = member.name
                            sec_def_id = member_name.split('-')[0] if '-' in member_name else None

                            if sec_def_id:
                                # Reverse lookup the security definition name
                                for sec_name, sec_data in self.importer.sec_defs.items():
                                    if str(sec_data['id']) == sec_def_id:
                                        group_data['members'].append(sec_name)
                                        break

        return out

# ################################################################################################################################

    def compare_groups(self, yaml_groups:'anylist', db_groups:'anydict') -> 'tuple[anylist, anylist]':
        """ Compares groups from YAML with groups from database and returns lists of groups to create and update.
        """
        to_create = []
        to_update = []

        for group in yaml_groups:
            name = group['name']

            if name not in db_groups:
                logger.info('Group %s not found in DB, will create new', name)
                to_create.append(group)
            else:
                logger.info('Group %s exists in DB with id=%s', name, db_groups[name]['id'])

                # Check if members are different
                needs_update = False
                yaml_members = set(group.get('members', []))
                db_members = set(db_groups[name].get('members', []))

                if yaml_members != db_members:
                    needs_update = True
                    logger.info('Members differ for group %s: YAML=%s DB=%s',
                               name, sorted(yaml_members), sorted(db_members))

                if needs_update:
                    # Add the database ID to the group for later update
                    group['id'] = db_groups[name]['id']
                    to_update.append(group)
                else:
                    logger.info('No update needed for group %s', name)

        return to_create, to_update

# ################################################################################################################################

    def _resolve_member_names(self, member_names:'strlist') -> 'strlist':
        """ Resolves member names to their IDs based on security definitions.
        """
        member_ids = []

        for member_name in member_names:
            if member_name in self.importer.sec_defs:
                sec_type = self.importer.sec_defs[member_name]['sec_type']
                sec_id = self.importer.sec_defs[member_name]['id']
                member_id = f'{sec_type}-{sec_id}'
                member_ids.append(member_id)
            else:
                logger.warning('Security definition %s not found', member_name)

        return member_ids

# ################################################################################################################################

    def create_group(self, group:'anydict', session:'SASession') -> 'any_':
        """ Creates a new security group and adds members to it.
        """
        group_name = group['name']
        members = group.get('members', [])

        # Use a server's groups manager to create the group
        with closing(session) as session:
            groups_manager = GroupsManager(self.importer.server, session)
            group_id = groups_manager.create_group(Groups.Type.API_Clients, group_name)

            # If there are members to add, resolve their names to IDs and add them
            if members:
                member_ids = self._resolve_member_names(members)
                if member_ids:
                    groups_manager.add_members_to_group(group_id, member_ids)

            # Return the created group info
            return {
                'id': group_id,
                'name': group_name,
                'members': members
            }

# ################################################################################################################################

    def update_group(self, group:'anydict', session:'SASession') -> 'any_':
        """ Updates an existing security group with new members.
        """
        group_id = group['id']
        group_name = group['name']
        members = group.get('members', [])

        # Get current group members from database
        db_groups = self.get_groups_from_db(session)
        db_members = set(db_groups[group_name].get('members', []))
        yaml_members = set(members)

        # Use a server's groups manager to update the group
        with closing(session) as session:
            groups_manager = GroupsManager(self.importer.server, session)

            # Members to add: in YAML but not in DB
            members_to_add = yaml_members - db_members
            if members_to_add:
                logger.info('Adding members to group %s: %s', group_name, sorted(members_to_add))
                member_ids = self._resolve_member_names(members_to_add)
                if member_ids:
                    groups_manager.add_members_to_group(group_id, member_ids)

            # Members to remove: in DB but not in YAML
            members_to_remove = db_members - yaml_members
            if members_to_remove:
                logger.info('Removing members from group %s: %s', group_name, sorted(members_to_remove))
                member_ids = self._resolve_member_names(members_to_remove)
                if member_ids:
                    groups_manager.remove_members_from_group(group_id, member_ids)

            # Return the updated group info
            return {
                'id': group_id,
                'name': group_name,
                'members': members
            }

# ################################################################################################################################

    def sync_groups(self, group_list:'anylist', session:'SASession') -> 'tuple[anylist, anylist]':
        """ Synchronizes security groups from YAML with the database.
        """
        # Lists to store created and updated groups
        created_groups = []
        updated_groups = []

        try:
            # Get existing groups from database
            db_groups = self.get_groups_from_db(session)

            # Compare YAML groups with database groups
            to_create, to_update = self.compare_groups(group_list, db_groups)

            # Create new groups
            for group in to_create:
                try:
                    created_group = self.create_group(group, session)
                    created_groups.append(created_group)
                    logger.info('Created group %s', group['name'])
                except Exception as e:
                    logger.error('Error creating group %s: %s', group['name'], e)
                    raise

            # Update existing groups
            for group in to_update:
                try:
                    updated_group = self.update_group(group, session)
                    updated_groups.append(updated_group)
                    logger.info('Updated group %s', group['name'])
                except Exception as e:
                    logger.error('Error updating group %s: %s', group['name'], e)
                    raise

            return created_groups, updated_groups

        except Exception:
            logger.exception('Error synchronizing groups')
            raise

# ################################################################################################################################
# ################################################################################################################################
