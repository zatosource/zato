# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.model import SecurityGroup
from zato.common.odb.query import security_group_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class GroupExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_group_definitions(self, session:'SASession') -> 'list':
        """ Export security group definitions from the database.
        """
        logger.info('Exporting security group definitions from cluster_id=%s', self.exporter.cluster_id)
        
        # Get all security groups
        security_groups = security_group_list(session, self.exporter.cluster_id)
        
        group_defs = []
        
        for group in security_groups:
            logger.info('Processing security group: %s', group.name)
            
            # Get all members of this group
            members = []
            for member in group.member_list:
                member_name = member.sec_def.name
                logger.info('Found group member: %s', member_name)
                members.append(member_name)
            
            # Create a dictionary representation of the group
            group_def = {
                'name': group.name,
                'members': members,
                'is_active': group.is_active
            }
            
            # Add to results
            group_defs.append(group_def)
            
        logger.info('Exported %d security groups', len(group_defs))
        return group_defs

# ################################################################################################################################
# ################################################################################################################################
