# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli.enmasse.importers.generic import GenericConnectionImporter
from zato.common.api import GENERIC, SMB

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class SMBImporter(GenericConnectionImporter):

    # Connection-specific constants
    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_SMB

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_SMB,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'is_outgoing': True,
        'pool_size': 1,

        # These two are columns on the ODB model rather than opaque attributes
        'port': SMB.DEFAULT.PORT,
        'username': '',
    }

    connection_extra_field_defaults = {
        'host': '',
    }

    connection_secret_keys = ['password', 'secret']
    connection_required_attrs = ['name', 'host']

    # SMB connections may carry file transfer schedules
    supports_schedules = True

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        # Let the base class update the opaque attributes first ..
        connection = super().update_definition(connection_def, session)

        # .. and then update the two fields that are columns on the ODB model
        # .. rather than opaque attributes, but only if they are actually given on input.
        if 'port' in connection_def:
            connection.port = connection_def['port']

        if 'username' in connection_def:
            connection.username = connection_def['username']

        return connection

# ################################################################################################################################
# ################################################################################################################################
