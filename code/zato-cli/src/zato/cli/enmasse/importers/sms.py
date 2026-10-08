# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC, SchedulerLink, SMS
from zato.common.odb.query.generic import connection_list
from zato.common.sms.config import apply_outgoing_host_default, validate_channel_definition, validate_outgoing_definition
from zato.common.util.delivery_config import Delivery_Field_Defaults
from zato.cli.enmasse.importers.generic import GenericConnectionImporter
from zato.cli.enmasse.importers.kafka import validate_int_fields
from zato.cli.enmasse.util.delivery import prepare_delivery_fields
from zato.cli.enmasse.util.invocation import Retry_Field_Defaults, sync_sms_poll_job

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import any_, anydict, anylist, listtuple
    EnmasseYAMLImporter = EnmasseYAMLImporter
    any_ = any_
    anydict = anydict
    anylist = anylist
    listtuple = listtuple
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

_scheduler = SMS.Scheduler

# The key under which a channel's YAML definition names its outgoing connection
Channel_Outconn_Key = 'outconn'

# An outgoing connection's fields
Outgoing_Extra_Field_Defaults = {
    SMS.Field_Provider: SMS.Provider.Twilio,
    SMS.Field_Host: '',
    SMS.Field_Username: '',
    SMS.Field_Sender: '',
    SMS.Field_Signature_Secret: '',
    SMS.Field_Channel_Name: '',
    SMS.Field_Pool_Size: SMS.Default_Pool_Size,
    SMS.Field_Timeout: SMS.Default_Timeout,
}
Outgoing_Extra_Field_Defaults.update(Retry_Field_Defaults)
Outgoing_Extra_Field_Defaults.update(Delivery_Field_Defaults)

# A channel's fields
Channel_Extra_Field_Defaults = {
    SMS.Field_Outconn_Name: '',
    SMS.Field_Service: '',
    SMS.Field_Receive_Mode: SMS.Receive_Mode.Webhook,
    _scheduler.Field_Run_Every: _scheduler.Default_Run_Every,
    _scheduler.Field_Run_Unit: _scheduler.Default_Run_Unit,
    _scheduler.Field_Job_ID: 0,
}
Channel_Extra_Field_Defaults.update(Retry_Field_Defaults)
Channel_Extra_Field_Defaults.update(Delivery_Field_Defaults)

# The fields that are whole numbers, by kind of connection
Outgoing_Int_Fields = (SMS.Field_Pool_Size, SMS.Field_Timeout) + tuple(Retry_Field_Defaults)
Channel_Int_Fields = (_scheduler.Field_Run_Every,) + tuple(Retry_Field_Defaults)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingSMSImporter(GenericConnectionImporter):

    label = 'Outgoing SMS connection'
    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_SMS

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_SMS,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'pool_size': SMS.Default_Pool_Size,
        'timeout': SMS.Default_Timeout,
    }

    connection_extra_field_defaults = Outgoing_Extra_Field_Defaults

    # The provider's password is stored in the secret column, the Vonage signature secret in the opaque attributes
    connection_secret_keys = [SMS.Field_Password]
    connection_required_attrs = ['name', 'username']
    opaque_secret_keys = (SMS.Field_Signature_Secret,)

# ################################################################################################################################

    def validate_definition(self, connection_def:'anydict') -> 'None':
        """ The provider has to be a known one, its signature secret and host have to match what the provider takes,
        and the whole-number and delivery fields have to be what each field takes.
        """
        name = connection_def['name']

        try:
            validate_outgoing_definition(connection_def)
        except ValueError as e:
            raise Exception(f'{self.label} `{name}` - {e}')

        apply_outgoing_host_default(connection_def)
        validate_int_fields(connection_def, Outgoing_Int_Fields, self.label)
        prepare_delivery_fields(connection_def, self.label)

# ################################################################################################################################
# ################################################################################################################################

class ChannelSMSImporter(GenericConnectionImporter):

    label = 'SMS channel'
    connection_type = GENERIC.CONNECTION.TYPE.CHANNEL_SMS

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.CHANNEL_SMS,
        'is_internal': False,
        'is_channel': True,
        'is_outconn': False,
        'pool_size': 1,
    }

    connection_extra_field_defaults = Channel_Extra_Field_Defaults

    # A channel has no secret of its own - it reads its provider through the outgoing connection it names
    connection_secret_keys = []
    connection_required_attrs = ['name']
    opaque_secret_keys = ()

    # The polling job links back to the channel the same way a health check job links to its connection
    health_check_conn_type = SchedulerLink.ConnType.SMS_Channel

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        super().__init__(importer)

        # The names of the outgoing SMS connections a channel may refer to, read from the database
        # at the start of each synchronization, after the outgoing connections of the same file were stored
        self.outconn_names:'set[str]' = set()

# ################################################################################################################################

    def sync_definitions(self, conn_list:'anylist', session:'SASession') -> 'listtuple':
        outgoing_defs:'anydict' = {}
        outgoing_rows = connection_list(session, self.importer.cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_SMS, False)
        self._process_defs(outgoing_rows, outgoing_defs)
        self.outconn_names = set(outgoing_defs)

        out = super().sync_definitions(conn_list, session)
        return out

# ################################################################################################################################

    def resolve_references(self, connection_def:'anydict') -> 'None':
        """ The outgoing connection a file names under `outconn` is stored under the channel's own field name.
        """
        if Channel_Outconn_Key in connection_def:
            connection_def[SMS.Field_Outconn_Name] = connection_def.pop(Channel_Outconn_Key)

# ################################################################################################################################

    def validate_definition(self, connection_def:'anydict') -> 'None':
        """ A channel needs a receive mode, a service and an outgoing SMS connection that the same import knows of,
        and the whole-number and delivery fields have to be what each field takes.
        """
        name = connection_def['name']

        # A definition without a receive mode receives its default before the mode is checked
        if not connection_def.get(SMS.Field_Receive_Mode):
            connection_def[SMS.Field_Receive_Mode] = SMS.Receive_Mode.Webhook

        try:
            validate_channel_definition(connection_def)
        except ValueError as e:
            raise Exception(f'{self.label} `{name}` - {e}')

        outconn_name = connection_def[SMS.Field_Outconn_Name]

        if outconn_name not in self.outconn_names:
            raise Exception(f'{self.label} `{name}` names an outgoing SMS connection that does not exist -> `{outconn_name}`')

        validate_int_fields(connection_def, Channel_Int_Fields, self.label)

        prepare_delivery_fields(connection_def, self.label)

# ################################################################################################################################

    def sync_linked_jobs(self, session:'SASession', merged_def:'anydict', connection:'any_') -> 'None':
        """ Creates, updates or deletes the channel's polling job to match its receive mode.
        """
        sync_sms_poll_job(self.importer, session, merged_def, connection)

# ################################################################################################################################
# ################################################################################################################################
