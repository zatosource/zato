# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import FileTransfer, GENERIC, SMB
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

    smb_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Fields to extract from opaque attributes, in the order they are exported
OPTIONAL_FIELDS = [
    'port',
]

# Values that are not exported because they match the defaults
_field_defaults = {
    'port': SMB.DEFAULT.PORT,
}

# ################################################################################################################################
# ################################################################################################################################

class SMBExporter:

    def __init__(self, exporter: 'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session: 'SASession', cluster_id: 'int') -> 'smb_def_list':
        """ Exports SMB connection definitions.
        """
        logger.info('Exporting SMB connection definitions')

        # Get SMB connections from database using the generic connection query
        db_smb = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_SMB)

        if not db_smb:
            logger.info('No SMB connection definitions found in DB')
            return []

        smb_connections = to_json(db_smb, return_as_dict=True)
        logger.debug('Processing %d SMB connection definitions', len(smb_connections))

        exported_smb = []

        for row in smb_connections:

            if GENERIC.ATTR_NAME in row:
                opaque = parse_instance_opaque_attr(row)
                row.update(opaque)
                del row[GENERIC.ATTR_NAME]

            # Create base SMB connection entry with fields in import order
            item = {
                'name': row['name'],
            }

            if host := row.get('host'):
                item['host'] = host

            if username := row.get('username'):
                item['username'] = username

            # Only add optional fields that do not match the defaults - note that the password
            # is never exported because secrets do not leave the database in plain text.
            for field in OPTIONAL_FIELDS:
                value = row.get(field)
                if value is None:
                    continue
                default = _field_defaults[field]
                if value != default:
                    item[field] = value

            # File transfer schedules travel in their portable YAML shape
            if schedules := row.get(FileTransfer.Scheduler.Schedules_Field):
                item['schedules'] = export_schedule_list(schedules)

            exported_smb.append(item)

        logger.info('Successfully prepared %d SMB connection definitions for export', len(exported_smb))
        return exported_smb

# ################################################################################################################################
# ################################################################################################################################
