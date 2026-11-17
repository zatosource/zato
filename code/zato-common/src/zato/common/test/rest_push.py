# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The configuration store of a stand-in server, holding the outgoing REST connections that push subscriptions
# deliver to, which push delivery looks up by the ID that a subscription refers to.

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.server.config import ConfigDict, ConfigStore

# ################################################################################################################################
# ################################################################################################################################

class RESTPushStore:
    """ A configuration store with the outgoing REST connections of push subscriptions.
    """
    def __init__(self) -> 'None':
        self.config_store = ConfigStore()
        self.config_store.out_plain_http = ConfigDict('out_plain_http', Bunch())
        self._last_id = 0

# ################################################################################################################################

    def add_endpoint(self, name:'str', host:'str', url_path:'str') -> 'int':
        """ Adds an outgoing REST connection to the host and the path and returns its ID.
        """
        self._last_id += 1

        config = Bunch()
        config.id = self._last_id
        config.name = name
        config.host = host
        config.url_path = url_path

        outconn = Bunch()
        outconn.config = config

        self.config_store.out_plain_http[name] = outconn
        self.config_store.out_plain_http.set_key_id_data(config)

        out = self._last_id
        return out

# ################################################################################################################################
# ################################################################################################################################
