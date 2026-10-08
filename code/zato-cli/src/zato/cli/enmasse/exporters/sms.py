# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import re

# Zato
from zato.common.api import GENERIC, SMS
from zato.common.odb.model import to_json
from zato.common.odb.query.generic import connection_list
from zato.common.sms.config import is_polling
from zato.common.util.sql import parse_instance_opaque_attr
from zato.cli.enmasse.exporters.kafka import export_fields
from zato.cli.enmasse.importers.sms import Channel_Outconn_Key
from zato.cli.enmasse.util.delivery import export_delivery_fields
from zato.cli.enmasse.util.invocation import Retry_Field_Defaults

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    sms_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_scheduler = SMS.Scheduler

# Secrets never leave the database in clear text - an exported definition refers to each one through an environment
# variable whose name is built out of the connection's name with this prefix and suffix
Env_Reference_Prefix = 'Zato_Enmasse_Env.'
Env_Name_Prefix = 'SMS_'
Env_Password_Suffix = '_Password'
Env_Signature_Secret_Suffix = '_Signature_Secret'

# The characters of a connection name that an environment variable name may not contain
_env_name_unwanted = re.compile(r'[^A-Za-z0-9_]')

# An outgoing connection's fields beyond its name, active flag and secrets, each with the default it is not exported at
Outgoing_Field_Defaults:'anydict' = {
    SMS.Field_Provider: '',
    SMS.Field_Host: '',
    SMS.Field_Username: '',
    SMS.Field_Sender: '',
    SMS.Field_Channel_Name: '',
    SMS.Field_Pool_Size: SMS.Default_Pool_Size,
    SMS.Field_Timeout: SMS.Default_Timeout,
}
Outgoing_Field_Defaults.update(Retry_Field_Defaults)

# A channel's fields beyond its name, active flag, outgoing connection and schedule
Channel_Field_Defaults:'anydict' = {
    SMS.Field_Service: '',
    SMS.Field_Receive_Mode: SMS.Receive_Mode.Webhook,
}
Channel_Field_Defaults.update(Retry_Field_Defaults)

# The schedule fields of a polling channel
Channel_Schedule_Field_Defaults:'anydict' = {
    _scheduler.Field_Run_Every: _scheduler.Default_Run_Every,
    _scheduler.Field_Run_Unit: _scheduler.Default_Run_Unit,
}

# ################################################################################################################################
# ################################################################################################################################

def get_env_reference(conn_name:'str', suffix:'str') -> 'str':
    """ The environment variable reference an exported definition gives in place of one of its secrets.
    """
    env_name = _env_name_unwanted.sub('_', conn_name)
    out = Env_Reference_Prefix + Env_Name_Prefix + env_name + suffix
    return out

# ################################################################################################################################

def _read_row(row:'anydict') -> 'anydict':
    """ Merges a connection's opaque attributes into its row and returns the attributes alone.
    """
    opaque = {}

    if GENERIC.ATTR_NAME in row:
        opaque = parse_instance_opaque_attr(row)
        row.update(opaque)
        del row[GENERIC.ATTR_NAME]

    return opaque

# ################################################################################################################################
# ################################################################################################################################

class OutgoingSMSExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session:'SASession', cluster_id:'int') -> 'sms_def_list':
        """ Exports outgoing SMS connection definitions.
        """
        logger.info('Exporting SMS outgoing definitions')

        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_SMS)

        if not db_items:
            logger.info('No SMS outgoing definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)
        logger.debug('Processing %d SMS outgoing definitions', len(connections))

        exported = []

        for row in connections:

            opaque = _read_row(row)
            name = row['name']

            item = {
                'name': name,
            }

            if row.get('is_active') is False:
                item['is_active'] = False

            export_fields(item, row, Outgoing_Field_Defaults)

            # The password is always exported as a reference, the signature secret only when the provider uses one
            item[SMS.Field_Password] = get_env_reference(name, Env_Password_Suffix)

            if row.get(SMS.Field_Provider) in SMS.Providers_With_Signature_Secret:
                item[SMS.Field_Signature_Secret] = get_env_reference(name, Env_Signature_Secret_Suffix)

            export_delivery_fields(item, opaque)

            exported.append(item)

        logger.info('Successfully prepared %d SMS outgoing definitions for export', len(exported))
        return exported

# ################################################################################################################################
# ################################################################################################################################

class ChannelSMSExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    def export(self, session:'SASession', cluster_id:'int') -> 'sms_def_list':
        """ Exports SMS channel definitions.
        """
        logger.info('Exporting SMS channel definitions')

        db_items = connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.CHANNEL_SMS)

        if not db_items:
            logger.info('No SMS channel definitions found in DB')
            return []

        connections = to_json(db_items, return_as_dict=True)
        logger.debug('Processing %d SMS channel definitions', len(connections))

        exported = []

        for row in connections:

            opaque = _read_row(row)

            item = {
                'name': row['name'],
            }

            if row.get('is_active') is False:
                item['is_active'] = False

            item[Channel_Outconn_Key] = row[SMS.Field_Outconn_Name]

            export_fields(item, row, Channel_Field_Defaults)

            # The schedule describes a polling channel only - a webhook channel has none
            if is_polling(row):
                export_fields(item, row, Channel_Schedule_Field_Defaults)

            export_delivery_fields(item, opaque)

            exported.append(item)

        logger.info('Successfully prepared %d SMS channel definitions for export', len(exported))
        return exported

# ################################################################################################################################
# ################################################################################################################################
