# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC
from zato.common.hl7.mllp.fields import Outconn_Column_Defaults, Outconn_Opaque_Defaults
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

class OutgoingMLLPImporter(GenericConnectionImporter):

    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP

    # What makes a row an outgoing MLLP connection rather than any other generic connection
    connection_defaults = dict(Outconn_Column_Defaults, **{
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
    })

    connection_extra_field_defaults = Outconn_Opaque_Defaults

    connection_secret_keys:'list' = []
    connection_required_attrs = ['name', 'address']

# ################################################################################################################################
# ################################################################################################################################
