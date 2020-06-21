# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from importlib import import_module
from logging import getLogger
from traceback import format_exc

# ################################################################################################################################

if 0:
    from bunch import Bunch

    Bunch = Bunch

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

class PhaseCtx(object):
    """ Describes a particular phase of a server startup process.
    """
    def __init__(self, phase, args, kwargs):
        # type: (str, list, dict)
        self.phase = phase
        self.args = args or [] # type: list
        self.kwargs = kwargs or {} # type: dict

# ################################################################################################################################

class StartupCallableTool(object):
    """ Handles logic related to server startup callables.
    """
    def __init__(self, server_config):
        # type: (Bunch)
        self._callable_names = server_config.misc.startup_callable # type: list
        self._callable_names = self._callable_names if isinstance(self._callable_names, list) else \
            [self._callable_names] # type: list
        self.callable_list = []

        self.init()

    def init(self):
        for item in self._callable_names:
            if item:
                if '.' not in item:
                    logger.warn('Invalid startup callable name `%s`, must be a dotted Python name', item)
                    continue

                try:
                    module_name, object_name = item.rsplit('.', 1)
                    mod = import_module(module_name)
                    obj = getattr(mod, object_name)
                    self.callable_list.append(obj)
                except Exception as e:
                    logger.warn('Could not import startup callable `%s`, e:`%s`', item, e)

    def invoke(self, phase, args=None, kwargs=None):
        # type: (PhaseCtx, list, dict)
        ctx = PhaseCtx(phase, args, kwargs)
        for callable_object in self.callable_list:
            try:
                callable_object(ctx)
            except Exception:
                logger.warn('Could not invoke `%s`, e:`%s`', callable_object, format_exc())

# ################################################################################################################################

def default_callable(ctx):
    """ Default startup callable added for demonstration purposes.
    """
    # type: (PhaseCtx)
    logger.info('Default startup callable entering phase `%s`', ctx.phase)

# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

# Bunch
from bunch import bunchify

# Zato
from zato.common import CACHE, SERVER_STARTUP

# Type completion imports
if 0:
    from zato.server.base.parallel import ParallelServer
    from zato.server.startup_callable import PhaseCtx

    ParallelServer = ParallelServer
    PhaseCtx = PhaseCtx

def my_callable(ctx):
    """ This is the callable that is invoked when the server is starting.
    """
    # type: (PhaseCtx)

    if ctx.phase == SERVER_STARTUP.PHASE.AFTER_STARTED:

        server = ctx.kwargs['server'] # type: ParallelServer

        service = 'zato.cache.builtin.create'
        request = {
            'cluster_id': server.cluster_id,
            'name': 'my.cache',
            'is_active': True,
            'is_default': False,
            'max_size': 10000,
            'max_item_size': 10000,
            'extend_expiry_on_get': True,
            'extend_expiry_on_set': True,
            'sync_method': CACHE.SYNC_METHOD.IN_BACKGROUND.id,
            'persistent_storage': CACHE.PERSISTENT_STORAGE.NO_PERSISTENT_STORAGE.id,
            'cache_type': CACHE.TYPE.BUILTIN,
        }

        server.invoke(service, request, as_bunch=True) # type: dict
'''
