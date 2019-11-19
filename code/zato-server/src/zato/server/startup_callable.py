# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from importlib import import_module
from logging import getLogger

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

class PhaseCtx(object):
    """ Describes a particular phase of a server startup process.
    """
    def __init__(self, phase, args, kwargs):
        self.phase = phase
        self.args = args or []
        self.kwargs = kwargs or {}

# ################################################################################################################################

class StartupCallableTool(object):
    """ Handles logic related to server startup callables.
    """
    def __init__(self, server_config):
        self._callable_names = server_config.misc.startup_callable
        self._callable_names = self._callable_names if isinstance(self._callable_names, list) else [self._callable_names]
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
        ctx = PhaseCtx(phase, args, kwargs)
        for callable in self.callable_list:
            callable(ctx)

# ################################################################################################################################

def default_callable(ctx):
    """ Default startup callable added for demonstration purposes.
    """
    logger.info('Default startup callable entering phase `%s`', ctx.phase)

# ################################################################################################################################
