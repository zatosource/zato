# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class SecurityFacade:

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server

    def get_bearer_token_by_name(self, key:'str') -> 'anydict':
        item:'anydictnone' = self.server.worker_store.request_dispatcher.url_data.oauth_config.get(key)
        if item:
            return item['config']
        else:
            raise KeyError(f'Security definition not found by key (1) -> {key}')

    def get_bearer_token_by_id(self, id:'int') -> 'anydict':

        for value in self.server.worker_store.request_dispatcher.url_data.oauth_config.values():
            if value['config']['id'] == id:
                return value['config']
        else:
            raise KeyError(f'Security definition not found ID -> {id}')

# ################################################################################################################################
# ################################################################################################################################
