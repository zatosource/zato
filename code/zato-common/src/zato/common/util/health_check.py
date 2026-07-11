# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.util.rest_invocation import clear_connection_opaque_fields, update_connection_opaque_fields

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import stranydict

    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

_health_check = HTTP_SOAP.HealthCheck

# ################################################################################################################################
# ################################################################################################################################

def update_health_check_fields(session:'SASession', conn_id:'int', values:'stranydict') -> 'None':
    """ Writes the current state of a health check job back to the opaque fields of its linked connection.
    """
    update_connection_opaque_fields(session, conn_id, values)

# ################################################################################################################################

def clear_health_check_fields(session:'SASession', conn_id:'int') -> 'None':
    """ Removes the health check fields from a connection whose linked job was deleted.
    """
    clear_connection_opaque_fields(session, conn_id, list(_health_check.FieldList))

# ################################################################################################################################
# ################################################################################################################################
