# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.alerting.object_config import conn_type_to_alert_type
from zato.common.api import GENERIC
from zato.common.hl7.mllp.fields import Outgoing_Column_Defaults, Outgoing_Opaque_Defaults
from zato.cli.enmasse.importers.generic import GenericConnectionImporter
from zato.cli.enmasse.util.delivery import prepare_delivery_fields

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# How an error message names this kind of connection
_connection_type = 'outgoing MLLP'

# ################################################################################################################################
# ################################################################################################################################

class OutgoingMLLPImporter(GenericConnectionImporter):

    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP

    # What makes a row an outgoing MLLP connection rather than any other generic connection
    connection_defaults = dict(Outgoing_Column_Defaults, **{
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
    })

    connection_extra_field_defaults = Outgoing_Opaque_Defaults

    connection_secret_keys:'list' = []
    connection_required_attrs = ['name', 'address']

    # The alerts mapping of a connection follows the outgoing MLLP type - the failures and the latency,
    # the negative acknowledgment codes the remote system answers and the messages it never acknowledges
    alert_type = conn_type_to_alert_type[GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP]

# ################################################################################################################################

    def validate_definition(self, connection_def:'anydict') -> 'None':
        """ The field list fills in and types the delivery fields on its own, what it does not do is reject a value
        the field does not take - a switch that is not a boolean, a negative count, an action that is not one of the four.
        """
        prepare_delivery_fields(connection_def, _connection_type)

# ################################################################################################################################
# ################################################################################################################################
