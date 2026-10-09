# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The server of the session and the clients the views and the tests use.

# Live environment
from live_environment.quickstart import Host

# Test support
from request_stub import new_client

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.quickstart import ZatoEnvironment
    from live_sms.suite import SimulatorSuite
    from zato.client import ZatoClient
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

class DashboardSuite:
    """ The simulators and the server of the session, with the clients the views and the tests use.
    """

    def __init__(self, simulators:'SimulatorSuite', zato:'ZatoEnvironment') -> 'None':
        self.simulators = simulators
        self.zato = zato
        self.server_address = f'http://{Host}:{zato.server_port}'

        # The client of the views and the client of the tests
        self.client:'ZatoClient' = new_client(self.server_address, zato.password)
        self.admin:'AdminClient' = zato.client()

# ################################################################################################################################

    def list_connections(self, type_:'str') -> 'anylist':
        """ Every generic connection of a type, as the server lists them.
        """
        out, _ = self.admin.get_list('zato.generic.connection.get-list', cluster_id=1, type_=type_)
        return out

# ################################################################################################################################

    def find_connection(self, type_:'str', name:'str') -> 'dict | None':
        """ One connection by name or None when there is none.
        """
        out = None

        for item in self.list_connections(type_):
            if item['name'] == name:
                out = item
                break

        return out

# ################################################################################################################################

    def delete_connections(self, type_:'str', prefix:'str') -> 'None':
        """ Removes every connection of a type whose name starts with the prefix.
        """
        for item in self.list_connections(type_):
            if item['name'].startswith(prefix):
                _ = self.admin.invoke('zato.generic.connection.delete', {'id': item['id']})

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
