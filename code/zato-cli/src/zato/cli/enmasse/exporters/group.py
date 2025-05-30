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

                # The member's 'name' field is in the format 'security_reference-group_id'.
                # The 'security_reference' itself is in the format 'type-id' (e.g., 'api-client-123').
                # We need to extract this 'security_reference' to look up the actual security definition name.
                member_full_name = member['name']
                if member_full_name:
                    # The security_reference is everything before the last hyphen (which separates it from group_id)
                    parts = member_full_name.rsplit('-', 1)
                    if len(parts) == 2:
                        security_reference = parts[0] # This is the 'type-id' string e.g. "api-client-123"
                        if security_reference: # Ensure extracted reference is not empty
                            try:
                                sec_name = self._get_security_name_from_reference(session, security_reference, cluster_id)
                                if sec_name:
                                    member_names.append(sec_name)
                            except ValueError as e:
                                logger.warning(f"Could not resolve security reference '{security_reference}' from member name '{member_full_name}' for group '{group_name}': {e}. Skipping member.")
                        else:
                            logger.warning(f"Extracted an empty security reference from member name '{member_full_name}' for group '{group_name}'. Skipping member.")
                    else:
                        logger.warning(f"Could not parse member name '{member_full_name}' to extract security reference for group '{group_name}'. Skipping member.")
                else:
                    logger.warning(f"Member object for group '{group_name}' has an empty name. Skipping member.")

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
            error_msg = "Empty security reference provided."
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            # Parse the security ID from the reference. The reference is 'type-id',
            # where 'type' can itself contain hyphens (e.g., 'api-client').
            # The ID is the numeric part after the last hyphen.
            ref_parts = reference.rsplit('-', 1)
            if len(ref_parts) != 2:
                error_msg = f"Malformed security reference '{reference}'. Expected format like 'type-numeric_id' or 'type-part-numeric_id'."
                logger.error(error_msg)
                raise ValueError(error_msg)

            sec_type_part, sec_id_str = ref_parts
            
            try:
                sec_id = int(sec_id_str) # Convert to int here and catch potential ValueError
            except ValueError:
                error_msg = f"Security ID part '{sec_id_str}' in reference '{reference}' is not a valid integer."
                logger.error(error_msg)
                raise ValueError(error_msg)

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
