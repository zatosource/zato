# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class ConnectionContext:
    """ Who is on one connection and what has come down it so far.
    """
    def __init__(self, client_ip:'str', client_port:'int', client_common_name:'str') -> 'None':

        # The sender's own address, as reported by the load balancer that accepted the connection
        self.client_ip = client_ip
        self.client_port = client_port

        # The common name of the client certificate that was verified, empty when there was none
        self.client_common_name = client_common_name

        self.total_messages_received = 0

    @property
    def endpoint(self) -> 'str':
        out = f'{self.client_ip}:{self.client_port}'
        return out

# ################################################################################################################################
# ################################################################################################################################
