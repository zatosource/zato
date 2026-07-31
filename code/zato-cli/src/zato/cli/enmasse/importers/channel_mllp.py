# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC, HL7
from zato.common.destination.constants import Default_Delivery_Mode, Respond_From_Service
from zato.common.destination.model import count_entries, dump_entries, parse_config
from zato.common.hl7.mllp.fields import Channel_Column_Defaults, Channel_Opaque_Defaults, Channel_Security_Id_Key, \
    Channel_Security_Name_Key, resolve_max_msg_size
from zato.common.hl7.mllp.settings import describe_bounds_violations
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

class ChannelMLLPImporter(GenericConnectionImporter):

    connection_type = GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP

    # What makes a row an MLLP channel rather than any other generic connection.
    # A channel has no pool of its own, it is one route through the listener every channel shares.
    connection_defaults = dict(Channel_Column_Defaults, **{
        'type_': GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP,
        'is_internal': False,
        'is_channel': True,
        'is_outconn': False,
        'pool_size': 1,
        'data_format': HL7.Const.Version.v2.id,
    })

    connection_extra_field_defaults = Channel_Opaque_Defaults

    connection_secret_keys:'list' = []
    connection_required_attrs = ['name']

# ################################################################################################################################

    def resolve_references(self, connection_def:'anydict') -> 'None':
        """ Turns what a YAML definition names or spells out its own way into what a channel
        stores - the security definition it accepts senders against and its destination list.
        """
        self._resolve_security(connection_def)
        self._resolve_destinations(connection_def)

# ################################################################################################################################

    def _resolve_destinations(self, connection_def:'anydict') -> 'None':
        """ A hand-written file holds a channel's destinations as a list of its own while a channel
        stores the JSON text the Dashboard writes, so what YAML says becomes that text - one stored
        form no matter which of the two wrote it. A list that could not be delivered to is refused
        here rather than after it has been written.
        """
        destinations = connection_def.get('destinations')

        # A channel with no destinations keeps what the field defaults to
        if not destinations:
            return

        name = connection_def['name']
        respond_from = connection_def.get('respond_from', Respond_From_Service)
        delivery_mode = connection_def.get('delivery_mode', Default_Delivery_Mode)

        # Refuses a destination of an unknown type, a reply from a destination the channel does
        # not have and a delivery mode that does not exist ..
        config = parse_config(name, destinations, respond_from, delivery_mode)

        # .. and what is stored is the same text either source of the list produces.
        connection_def['destinations'] = dump_entries(config.entries)

# ################################################################################################################################

    def _resolve_security(self, connection_def:'anydict') -> 'None':
        """ A channel names the security definition it accepts a sender's certificate against, and
        what is stored is that definition's id, so the name is looked up and then dropped - it is
        not a field of the channel and must not reach the opaque attributes.
        """
        security_name = connection_def.pop(Channel_Security_Name_Key, '')

        # A channel without one accepts a connection whatever certificate it was made with
        if not security_name:
            return

        sec_def = self.importer.sec_defs.get(security_name)

        if not sec_def:
            name = connection_def['name']
            raise Exception(f'Security definition `{security_name}` not found for HL7 MLLP channel `{name}`')

        connection_def[Channel_Security_Id_Key] = sec_def['id']

# ################################################################################################################################

    def validate_definition(self, connection_def:'anydict') -> 'None':
        """ A channel hands each message it accepts to a service, to its destinations, or to both,
        so a channel that names neither has nowhere to deliver. Nor may it ask the listener for
        more room or more time than the listener has.
        """
        service = connection_def.get('service')
        destinations = connection_def.get('destinations')

        if not service:
            if not count_entries(destinations):
                name = connection_def['name']
                raise Exception(f'HL7 MLLP channel `{name}` needs a service or at least one destination')

        max_msg_size = connection_def.get('max_msg_size', HL7.Default.max_msg_size_value)
        max_msg_size_unit = connection_def.get('max_msg_size_unit', HL7.Default.max_msg_size_unit)
        idle_timeout = connection_def.get('idle_timeout', HL7.Default.idle_timeout)

        violations = describe_bounds_violations(
            resolve_max_msg_size(max_msg_size, max_msg_size_unit),
            idle_timeout,
        )

        if violations:
            name = connection_def['name']
            raise Exception(f'HL7 MLLP channel `{name}` - ' + ', '.join(violations))

# ################################################################################################################################
# ################################################################################################################################
