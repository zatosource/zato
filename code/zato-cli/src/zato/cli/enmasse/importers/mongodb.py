# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli.enmasse.importers.generic import GenericConnectionImporter
from zato.common.api import GENERIC, MongoDB

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class MongoDBImporter(GenericConnectionImporter):

    # Connection-specific constants
    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'is_outgoing': True,
        'pool_size': 1,

        # This one is a column on the ODB model rather than an opaque attribute
        'username': '',
    }

    connection_extra_field_defaults = {
        'server_list': MongoDB.Default.Server_List,
        'auth_source': MongoDB.Default.Auth_Source,
        'app_name': MongoDB.Default.App_Name,
        'pool_size_max': MongoDB.Default.Pool_Size_Max,
        'connect_timeout': MongoDB.Default.Connect_Timeout,
        'server_select_timeout': MongoDB.Default.Server_Select_Timeout,
    }

    connection_secret_keys = ['password', 'secret']
    connection_required_attrs = ['name', 'server_list']

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        # Let the base class update the opaque attributes first ..
        connection = super().update_definition(connection_def, session)

        # .. and then update the field that is a column on the ODB model
        # .. rather than an opaque attribute, but only if it is actually given on input.
        if 'username' in connection_def:
            connection.username = connection_def['username']

        return connection

# ################################################################################################################################
# ################################################################################################################################
