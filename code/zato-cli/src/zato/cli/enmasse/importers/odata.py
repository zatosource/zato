# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import ODATA, ODATA_Subtype
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class ODataImporter(GenericConnectionImporter):
    """ One importer serves every subtype of the OData implementation - the importer is registered
    once per subtype, e.g. under the odata key and under the sap key.
    """

    connection_secret_keys = ['password', 'secret', 'client_secret']
    connection_required_attrs = ['name', 'address']

    def __init__(self, importer:'EnmasseYAMLImporter', subtype:'str') -> 'None':
        super().__init__(importer)
        self.subtype = ODATA_Subtype[subtype]
        self.connection_type = self.subtype['type_']

        self.connection_defaults = {
            'is_active': True,
            'type_': self.subtype['type_'],
            'is_internal': False,
            'is_channel': False,
            'is_outconn': True,
            'is_outgoing': True,
            'pool_size': ODATA.DEFAULT.POOL_SIZE,
            'timeout': ODATA.DEFAULT.TIMEOUT,

            # This is an actual column, which is why it cannot be an opaque extra field
            'username': '',
        }

        self.connection_extra_field_defaults = {
            'odata_version': self.subtype['odata_version'],
            'auth_type': ODATA.AUTH_TYPE.BASIC.id,
            'token_url': None,
            'tenant_id': None,
            'client_id': None,
            'scopes': None,
            'needs_csrf_token': self.subtype['needs_csrf_token'],
            'page_size': ODATA.DEFAULT.PAGE_SIZE,
        }

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        connection = super().update_definition(connection_def, session)

        # The username is an actual column but it cannot be a required attribute
        # because OAuth2 and no-auth connections do not have one, which is why
        # the base class will not update it and we need to do it ourselves.
        if 'username' in connection_def:
            connection.username = connection_def['username']

        return connection

# ################################################################################################################################
# ################################################################################################################################
