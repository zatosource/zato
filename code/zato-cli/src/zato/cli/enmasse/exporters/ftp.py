# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import FileTransfer, FTP, GENERIC
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.util.file_transfer_scheduler import export_schedule_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    ftp_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Fields to extract from opaque attributes, in the order they are exported
Optional_Fields = [
    'port',
]

# Values that are not exported because they match the defaults
_field_defaults = {
    'port': FTP.DEFAULT.PORT,
}

# ################################################################################################################################
# ################################################################################################################################

class FTPExporter:
    """ Exports outgoing FTP connections to their enmasse YAML definitions.
    """

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'ftp_def_list':
        """ Exports FTP connection definitions.
        """
        logger.info('Exporting FTP connection definitions')

        # Our response to produce
        out:'ftp_def_list' = []

        # Get FTP connections from database using the generic connection query.
        db_ftp = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_FTP)

        if not db_ftp:
            logger.info('No FTP connection definitions found in DB')
            return out

        ftp_connections = to_json(db_ftp, return_as_dict=True)

        connection_count = len(ftp_connections)
        connection_suffix = 'definition' if connection_count == 1 else 'definitions'
        logger.debug('Processing %d FTP connection %s', connection_count, connection_suffix)

        for row in ftp_connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # Create base FTP connection entry with fields in import order.
            item = {
                'name': row['name'],
            }

            if host := row['host']:
                item['host'] = host

            if username := row['username']:
                item['username'] = username

            # Only add optional fields that do not match the defaults - the password is never exported.
            for field in Optional_Fields:
                value = row[field]
                default = _field_defaults[field]
                if value != default:
                    item[field] = value

            # The flag is exported only when it differs from the default of off.
            if row['use_ssl'] is True:
                item['use_ssl'] = True

            # The flag is exported only when it differs from the default of off.
            if row['should_store_content'] is True:
                item['should_store_content'] = True

            # File transfer schedules travel in their portable YAML shape.
            if schedules := row.get(FileTransfer.Scheduler.Schedules_Field):
                item['schedules'] = export_schedule_list(schedules)

            out.append(item)

        exported_count = len(out)
        exported_suffix = 'definition' if exported_count == 1 else 'definitions'
        logger.info('Successfully prepared %d FTP connection %s for export', exported_count, exported_suffix)

        return out

# ################################################################################################################################
# ################################################################################################################################
