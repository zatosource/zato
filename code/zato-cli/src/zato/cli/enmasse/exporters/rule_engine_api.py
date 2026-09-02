# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.api import GENERIC, Groups
from zato.common.odb.model import GenericObject, to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, anylist, list_

    rule_engine_api_def_list = list_[anydict]

    # Add dummy assignments to satisfy type checkers
    SASession = SASession
    EnmasseYAMLExporter = EnmasseYAMLExporter
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Rule_Engine_API_Optional_Fields = [
    'url_path', 'rulesets', 'security_groups',
]

# ################################################################################################################################
# ################################################################################################################################

class RuleEngineAPIExporter:
    """ Exports Rule engine API definitions to their enmasse form.
    """

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter
        self.group_id_to_name:'anydict' = {}

# ################################################################################################################################

    def _load_security_groups(self, session:'SASession', cluster_id:'int') -> 'None':
        """ Loads the security groups of the cluster and builds an id-to-name mapping.
        """

        # The session belongs to the caller, so this method must not close it.
        query = select(
            GenericObject.id,
            GenericObject.name,
        ).where(and_(
            GenericObject.type_ == Groups.Type.Group_Parent,
            GenericObject.subtype == Groups.Type.API_Clients,
            GenericObject.cluster_id == cluster_id,
        ))

        result = session.execute(query)
        groups = result.fetchall()

        for group in groups:
            self.group_id_to_name[group.id] = group.name

# ################################################################################################################################

    def _groups_as_names(self, security_groups:'anylist', definition_name:'str') -> 'anylist':
        """ Returns the given security groups with every id turned into its name.
        """

        # Our response to produce
        out:'anylist' = []

        for group in security_groups:

            # An integer entry is an id to map to its name ..
            if isinstance(group, int):

                if group_name := self.group_id_to_name.get(group):
                    out.append(group_name)
                else:
                    logger.warning('Security group ID %s not found for Rule engine API %s', group, definition_name)

            # .. and everything else already is a name.
            else:
                out.append(group)

        return out

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'rule_engine_api_def_list':
        """ Exports Rule engine API definitions.
        """
        logger.info('Exporting Rule engine API definitions')

        # Our response to produce
        out = []

        self._load_security_groups(session, cluster_id)

        connections = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.GATEWAY_RULE_ENGINE)

        if not connections:
            logger.info('No Rule engine API definitions found in DB')
            return out

        connections = to_json(connections, return_as_dict=True)
        logger.debug('Processing %d Rule engine API definition(s)', len(connections))

        for row in connections:

            # The optional fields live in the opaque attributes, so they are folded into the row first ..
            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            name = row['name']

            item = {
                'name': name,
            }

            # .. each optional field travels only if it has a value ..
            for field in _Rule_Engine_API_Optional_Fields:
                if value := row.get(field):

                    # .. group ids become names, which is what the importer expects back ..
                    if field == 'security_groups':
                        value = self._groups_as_names(value, name)

                    item[field] = value

            # .. and the definition is ready now.
            out.append(item)

        logger.info('Successfully prepared %d Rule engine API definition(s) for export', len(out))

        return out

# ################################################################################################################################
# ################################################################################################################################
