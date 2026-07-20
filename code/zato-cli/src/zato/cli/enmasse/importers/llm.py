# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import GENERIC, LLM
from zato.cli.enmasse.importers.generic import GenericConnectionImporter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class LLMImporter(GenericConnectionImporter):

    # Connection-specific constants
    connection_type = GENERIC.CONNECTION.TYPE.OUTCONN_LLM

    connection_defaults = {
        'is_active': True,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_LLM,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'is_outgoing': True,
        'pool_size': LLM.DEFAULT.POOL_SIZE,
    }

    # Note that timeout is not here because it is a column on the ODB model
    connection_extra_field_defaults = {
        'provider': LLM.PROVIDER.OPENAI.id,
        'model': LLM.DEFAULT.Model,
        'max_tokens': LLM.DEFAULT.MAX_TOKENS,
        'max_history_turns': LLM.DEFAULT.MAX_HISTORY_TURNS,
        'chat_expiry': LLM.DEFAULT.CHAT_EXPIRY,
    }

    connection_secret_keys = ['secret', 'password', 'api_key']
    connection_required_attrs = ['name', 'address']

# ################################################################################################################################

    def create_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        connection = super().create_definition(connection_def, session)

        # The timeout is a column on the ODB model rather than an opaque attribute
        connection.timeout = connection_def.get('timeout', LLM.DEFAULT.TIMEOUT)

        return connection

# ################################################################################################################################

    def update_definition(self, connection_def:'anydict', session:'SASession') -> 'any_':

        # Let the base class update the opaque attributes first ..
        connection = super().update_definition(connection_def, session)

        # .. and then update the timeout column, but only if it is actually given on input.
        if 'timeout' in connection_def:
            connection.timeout = connection_def['timeout']

        return connection

# ################################################################################################################################
# ################################################################################################################################
