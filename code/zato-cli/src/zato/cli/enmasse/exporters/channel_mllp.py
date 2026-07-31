# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.common.destination.model import describe_entries, DestinationException, parse_entries
from zato.common.hl7.mllp.fields import Channel_Destinations_Key, Channel_Fields, Channel_Security_Id_Key, \
    Channel_Security_Name_Key
from zato.common.odb.model import SecurityBase, to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import any_, anydict, list_

    any_ = any_
    channel_mllp_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelMLLPExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def _get_security_name(self, session:'SASession', security_id:'int') -> 'str':
        """ Returns the name of the security definition with the given id, empty when the channel
        refers to one that has been deleted since - such a channel exports without a name rather
        than failing the whole export.
        """
        sec_def = session.query(SecurityBase).filter_by(id=security_id).first()

        if not sec_def:
            logger.info('No security definition with id %s, exporting the channel without one', security_id)
            return ''

        out = sec_def.name
        return out

# ################################################################################################################################

    def _describe_destinations(self, channel_name:'str', destinations:'any_') -> 'any_':
        """ Returns a channel's destination list in the form YAML holds it, which is a list of its
        own. A list that cannot be read is exported as it stands, because an export saying what a
        channel actually holds is better than one quietly leaving its destinations out.
        """
        try:
            entries = parse_entries(destinations)
        except DestinationException as e:
            logger.warning('Exporting the destinations of `%s` as they stand; e:`%s`', channel_name, e)
            return destinations

        out = describe_entries(entries)
        return out

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'channel_mllp_def_list':
        """ Exports HL7 MLLP channel definitions.
        """
        logger.info('Exporting HL7 MLLP channel definitions')

        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP)

        if not db_items:
            logger.info('No HL7 MLLP channel definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)

        connection_count = len(connections)
        noun = 'definition' if connection_count == 1 else 'definitions'
        logger.debug('Processing %d HL7 MLLP channel %s', connection_count, noun)

        exported = []

        for row in connections:

            # Merge opaque attributes into the row so all fields are accessible at the top level ..
            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # .. build the export item with the channel name and whatever the channel
            # .. has been configured away from, so that a re-import reproduces it exactly ..
            item = {
                'name': row['name'],
            }

            for field in Channel_Fields:

                value = row.get(field.name, field.default)

                if value == field.default:
                    continue

                # .. the security definition travels by name rather than by the id that is stored ..
                if field.name == Channel_Security_Id_Key:
                    security_name = self._get_security_name(session, value)
                    if security_name:
                        item[Channel_Security_Name_Key] = security_name
                    continue

                # .. the destination list travels as a list rather than as the JSON text that is
                # stored, so that a file this export produces reads the way one written by hand does ..
                if field.name == Channel_Destinations_Key:
                    item[field.name] = self._describe_destinations(row['name'], value)
                    continue

                item[field.name] = value

            # .. and add it to the output.
            exported.append(item)

        exported_count = len(exported)
        noun = 'definition' if exported_count == 1 else 'definitions'
        logger.info('Successfully prepared %d HL7 MLLP channel %s for export', exported_count, noun)
        return exported

# ################################################################################################################################
# ################################################################################################################################
