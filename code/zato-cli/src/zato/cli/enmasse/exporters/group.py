# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.api import Groups
from zato.common.odb.model import GenericObject

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    group_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class GroupExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'group_def_list':
        """ Exports security group definitions.
        """

        logger.info('Exporting security group definitions')

        # Get all groups for this cluster
        query = select([
            GenericObject.id,
            GenericObject.name
            ]).where(and_(
                GenericObject.type_ == Groups.Type.Group_Parent,
                GenericObject.subtype == Groups.Type.API_Clients,
                GenericObject.cluster_id == cluster_id,
            ))

        groups = session.execute(query).fetchall()

        if not groups:
            logger.info('No security group definitions found in DB')
            return []

        logger.info('Processing %d security group definitions', len(groups))

        exported_groups = []

        # For each group, get its members
        for group in groups:
            group_id = group['id']
            group_name = group['name']

            # Query to find all members of this group
            member_query = select([
                GenericObject.id,
                GenericObject.name,
                GenericObject.opaque1 # Contains the security definition reference
                ]).where(and_(
                    GenericObject.type_ == Groups.Type.Group_Member,
                    GenericObject.subtype == Groups.Type.API_Clients,
                    GenericObject.parent_object_id == group_id,
                    GenericObject.cluster_id == cluster_id,
                ))

            members = session.execute(member_query).fetchall()

            # Get security definition names from member references
            member_names = []
            for member in members:

                # The member name is stored as a reference in the format 'type-id'
                # We need to look up the security definition name from this
                if member['opaque1']:
                    sec_name = self._get_security_name_from_reference(session, member['opaque1'], cluster_id)
                    if sec_name:
                        member_names.append(sec_name)

            # Create the group export definition
            group_def = {
                'name': group_name,
                'members': member_names
            }

            exported_groups.append(group_def)

        logger.info('Successfully prepared %d security group definitions for export', len(exported_groups))

        return exported_groups

# ################################################################################################################################

    def _get_security_name_from_reference(self, session:'SASession', reference:'str', cluster_id:'int') -> 'str':
        """ Resolves a security reference to a security definition name.
            The reference is typically stored in the format 'type-id'.
        """
        if not reference:
            return ''

        try:
            # Parse the security type and ID from the reference
            parts = reference.split('-')
            if len(parts) != 2:
                return ''

            _, sec_id = parts

            # Query for the security definition
            query = select([
                GenericObject.name
                ]).where(and_(
                    GenericObject.id == int(sec_id),
                    GenericObject.cluster_id == cluster_id,
                ))

            result = session.execute(query).fetchone()
            if result:
                return result['name']

        except Exception as e:
            error_msg = f'Error resolving security reference {reference}: {e}'
            logger.error(error_msg)
            raise ValueError(error_msg)

        error_msg = f'Security definition not found for reference: {reference}'
        logger.error(error_msg)
        raise ValueError(error_msg)

# ################################################################################################################################
# ################################################################################################################################
