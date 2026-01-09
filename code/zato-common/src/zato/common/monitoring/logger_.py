# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import Logger

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class DatadogLogger(Logger):

    cid: 'str'
    server: 'ParallelServer'
    service_name: 'str'

    def __init__(self, name:'str', cid:'str', server:'ParallelServer', service_name:'str') -> 'None':
        super().__init__(name)
        self.cid = cid
        self.server = server
        self.service_name = service_name
        self.datadog_tracer = self.server.datadog_tracer

# ################################################################################################################################

    def _zato_emit_log(self, level:'str', msg:'str', step:'strnone') -> 'None':
        trace = self.datadog_tracer.trace(name='', service=self.service_name)
        if step:
            trace.resource = step
        trace.set_tag('cid', self.cid)
        trace.set_tag('message', msg)
        trace.set_tag('message_level', level)
        trace.finish()

# ################################################################################################################################

    def debug(self, msg:'any_', *args:'any_', step:'strnone'=None, **kwargs:'any_') -> 'None':
        super().debug(msg, *args, **kwargs)
        self._zato_emit_log('DEBUG', str(msg), step)

# ################################################################################################################################

    def info(self, msg:'any_', *args:'any_', step:'strnone'=None, **kwargs:'any_') -> 'None':
        super().info(msg, *args, **kwargs)
        self._zato_emit_log('INFO', str(msg), step)

# ################################################################################################################################

    def warning(self, msg:'any_', *args:'any_', step:'strnone'=None, **kwargs:'any_') -> 'None':
        super().warning(msg, *args, **kwargs)
        self._zato_emit_log('WARNING', str(msg), step)

    warn = warning

# ################################################################################################################################

    def error(self, msg:'any_', *args:'any_', step:'strnone'=None, **kwargs:'any_') -> 'None':
        super().error(msg, *args, **kwargs)
        self._zato_emit_log('ERROR', str(msg), step)

# ################################################################################################################################

    def critical(self, msg:'any_', *args:'any_', step:'strnone'=None, **kwargs:'any_') -> 'None':
        super().critical(msg, *args, **kwargs)
        self._zato_emit_log('CRITICAL', str(msg), step)

# ################################################################################################################################
# ################################################################################################################################
