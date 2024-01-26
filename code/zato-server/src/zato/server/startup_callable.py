# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
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

class PhaseCtx:
    """ Describes a particular phase of a server startup process.
    """
    def __init__(self, phase, args, kwargs):
        # type: (str, list, dict)
        self.phase = phase
        self.args = args or [] # type: list
        self.kwargs = kwargs or {} # type: dict

# ################################################################################################################################

class StartupCallableTool:
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
                    logger.warning('Invalid startup callable name `%s`, must be a dotted Python name', item)
                    continue

                try:
                    module_name, object_name = item.rsplit('.', 1)
                    mod = import_module(module_name)
                    obj = getattr(mod, object_name)
                    self.callable_list.append(obj)
                except Exception as e:
                    logger.warning('Could not import startup callable `%s`, e:`%s`', item, e)

    def invoke(self, phase, args=None, kwargs=None):
        # type: (PhaseCtx, list, dict)
        ctx = PhaseCtx(phase, args, kwargs)
        for callable_object in self.callable_list:
            try:
                callable_object(ctx)
            except Exception:
                logger.warning('Could not invoke `%s`, e:`%s`', callable_object, format_exc())

# ################################################################################################################################

def default_callable(ctx):
    """ Default startup callable added for demonstration purposes.
    """
    # type: (PhaseCtx)
    logger.info('Default startup callable entering phase `%s`', ctx.phase)

# ################################################################################################################################
