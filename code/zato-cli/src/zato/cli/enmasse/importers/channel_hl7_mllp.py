# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC, HL7
from zato.common.hl7.mllp.fields import Channel_Column_Defaults, Channel_Opaque_Defaults, resolve_max_msg_size
from zato.common.hl7.mllp.settings import describe_bounds_violations
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

class ChannelHL7MLLPImporter(GenericConnectionImporter):

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

    def validate_definition(self, connection_def:'anydict') -> 'None':
        """ A channel hands each message it accepts to a service, to its destinations, or to both,
        so a channel that names neither has nowhere to deliver. Nor may it ask the listener for
        more room or more time than the listener has.
        """
        service = connection_def.get('service')
        destinations = connection_def.get('destinations')

        if not service:
            if not destinations:
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
