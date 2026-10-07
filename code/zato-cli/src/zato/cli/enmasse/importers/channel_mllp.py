# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.alerting.object_config import conn_type_to_alert_type
from zato.common.api import GENERIC, HL7
from zato.common.destination.constants import Default_Delivery_Mode, Respond_From_Service
from zato.common.destination.model import count_entries, dump_entries, parse_config
from zato.common.hl7.mllp.fields import Channel_Column_Defaults, Channel_Opaque_Defaults, Channel_Security_Id_Key, \
    Channel_Security_Name_Key, resolve_max_message_size
from zato.common.hl7.mllp.settings import describe_bounds_violations, listener_config_from_bounds
from zato.common.odb.model import GenericConn
from zato.common.util.api import asbool
from zato.common.util.sql import parse_instance_opaque_attr, set_instance_opaque_attrs
from zato.cli.enmasse.client import get_mllp_listener_bounds
from zato.cli.enmasse.importers.generic import GenericConnectionImporter
from zato.cli.enmasse.util.secrets import get_server_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.hl7.mllp.settings import ListenerConfig
    from zato.common.typing_ import any_, anydict, anylist, listtuple

    any_ = any_
    anydict = anydict
    anylist = anylist
    listtuple = listtuple
    ListenerConfig = ListenerConfig
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

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

    # The alerts mapping of a channel follows the MLLP channel type - the channel settings minus everything HTTP,
    # plus the negative acknowledgment codes
    alert_type = conn_type_to_alert_type[GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP]

    def __init__(self, importer:'any_') -> 'None':
        super().__init__(importer)

        # The bounds of the listener the channels will run on, asked of the running server once per import
        self.listener_config:'ListenerConfig | None' = None

# ################################################################################################################################

    def sync_definitions(self, conn_list:'anylist', session:'SASession') -> 'listtuple':
        """ Reads the listener's bounds from the server the session was opened for before any definition is
        judged against them. A server that cannot be reached fails the import - the bounds are the server's own
        and an import must not guess them from its own environment.
        """
        server_dir = get_server_dir(session)
        self.listener_config = listener_config_from_bounds(get_mllp_listener_bounds(server_dir))

        self._ensure_one_default(conn_list)

        out = super().sync_definitions(conn_list, session)
        return out

# ################################################################################################################################

    def _ensure_one_default(self, conn_list:'anylist') -> 'None':
        """ Only one channel is the default at a time, so a file that makes two of them the default is refused
        before anything is written - imported, it would leave the flag with the last of them alone and an export
        would no longer reproduce the file.
        """
        names = []

        for connection_def in conn_list:
            if 'is_default' not in connection_def:
                continue
            if asbool(connection_def['is_default']):
                names.append(connection_def['name'])

        if len(names) > 1:
            raise Exception('Only one HL7 MLLP channel can be the default, the file names {}: {}'.format(
                len(names), ', '.join(names)))

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

        if self.listener_config is None:
            raise Exception('The HL7 MLLP listener bounds have not been read from the server')

        violations = describe_bounds_violations(
            resolve_max_message_size(max_msg_size, max_msg_size_unit),
            idle_timeout,
            self.listener_config,
        )

        if violations:
            name = connection_def['name']
            raise Exception(f'HL7 MLLP channel `{name}` - ' + ', '.join(violations))

# ################################################################################################################################

    def create_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':
        out = super().create_definition(connection_def, session)
        self._clear_other_defaults(connection_def, out, session)
        return out

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':
        out = super().update_definition(connection_def, session)
        self._clear_other_defaults(connection_def, out, session)
        return out

# ################################################################################################################################

    def _clear_other_defaults(self, connection_def:'anydict', connection:'any_', session:'SASession') -> 'None':
        """ Only one channel is the default at a time, so a definition that makes its channel the default
        takes the flag away from every other channel that stores it.
        """
        if 'is_default' not in connection_def:
            return

        if not asbool(connection_def['is_default']):
            return

        others = session.query(GenericConn).\
            filter(GenericConn.cluster_id == self.importer.cluster_id).\
            filter(GenericConn.type_ == self.connection_type).\
            filter(GenericConn.id != connection.id).\
            all()

        for other in others:
            opaque = parse_instance_opaque_attr(other)

            if 'is_default' not in opaque:
                continue

            if not asbool(opaque['is_default']):
                continue

            set_instance_opaque_attrs(other, {'is_default': False})
            session.add(other)
            logger.info('Cleared the default flag from HL7 MLLP channel `%s`', other.name)

# ################################################################################################################################
# ################################################################################################################################
