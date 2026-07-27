# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.common.hl7.mllp.fields import Channel_Fields, Channel_Security_Id_Key, Channel_Security_Name_Key
from zato.common.odb.model import SecurityBase, to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    channel_hl7_mllp_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelHL7MLLPExporter:

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

    def export(self, session:'SASession', cluster_id:'int') -> 'channel_hl7_mllp_def_list':
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

                item[field.name] = value

            # .. and add it to the output.
            exported.append(item)

        exported_count = len(exported)
        noun = 'definition' if exported_count == 1 else 'definitions'
        logger.info('Successfully prepared %d HL7 MLLP channel %s for export', exported_count, noun)
        return exported

# ################################################################################################################################
# ################################################################################################################################
