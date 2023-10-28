# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone
    from zato.server.base.parallel import ParallelServer
    from zato.server.config import ConfigDict

# ################################################################################################################################
# ################################################################################################################################

class _SecurityFacade_Impl:

    config_dict:'ConfigDict'
    __slots__ = ('config_dict',)

    def __init__(self, config_dict:'ConfigDict') -> 'None':
        self.config_dict = config_dict

    def get(self, key:'str', default:'any_'=None) -> 'anydict':
        item:'anydictnone' = self.config_dict.get(key)
        if item:
            return item['config']
        else:
            raise KeyError(f'Security definition not found by key (1) -> {key}')

    def get_by_id(self, id:'int') -> 'anydict':

        for value in self.config_dict.values():
            if value['config']['id'] == id:
                return value['config']
        else:
            raise KeyError(f'Security definition not found ID -> {id}')

    def __getitem__(self, key:'str') -> 'anydict':
        item:'anydictnone' = self.config_dict.__getitem__(key)
        if item:
            return item['config']
        else:
            raise KeyError(f'Security definition not found by key (2) -> {key}')

# ################################################################################################################################
# ################################################################################################################################

class SecurityFacade:
    """ The API through which security definitions can be accessed.
    """
    __slots__ = ('basic_auth', 'bearer_token')

    def __init__(self, server:'ParallelServer') -> 'None':
        self.basic_auth = _SecurityFacade_Impl(server.worker_store.worker_config.basic_auth)
        self.bearer_token = _SecurityFacade_Impl(server.worker_store.worker_config.oauth)

# ################################################################################################################################
# ################################################################################################################################
