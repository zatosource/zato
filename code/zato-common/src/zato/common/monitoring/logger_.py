# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
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
    process_name: 'str'
    service: 'any_'

    def __init__(
        self,
        cid:'str',
        server:'ParallelServer',
        service_name:'str',
        process_name:'str',
        service:'any_'=None,
    ) -> 'None':
        super().__init__('zato')
        self.cid = cid
        self.server = server
        self.service_name = service_name
        self.process_name = process_name
        self.datadog_tracer = self.server.datadog_tracer
        self.service = service

# ################################################################################################################################

    def _zato_emit_log(self, level:'str', msg:'str', event:'strnone') -> 'None':
        event = event or 'Logger'
        datadog_context = getattr(self.service, 'datadog_context', None)
        trace = self.datadog_tracer.start_span(
            name='',
            service=self.service_name,
            resource=event,
            child_of=datadog_context,
        )
        trace.set_tag('cid', self.cid)
        trace.set_tag('zato_message', msg)
        trace.set_tag('zato_message_level', level)
        trace.set_tag('zato_service', self.service_name)
        trace.set_tag('zato_process', self.process_name)
        trace.finish()

# ################################################################################################################################

    def debug(self, msg:'any_', *args:'any_', event:'strnone'=None, **kwargs:'any_') -> 'None':
        super().debug(msg, *args, **kwargs)
        self._zato_emit_log('DEBUG', str(msg), event)

# ################################################################################################################################

    def info(self, msg:'any_', *args:'any_', event:'strnone'=None, **kwargs:'any_') -> 'None':
        super().info(msg, *args, **kwargs)
        self._zato_emit_log('INFO', str(msg), event)

# ################################################################################################################################

    def warning(self, msg:'any_', *args:'any_', event:'strnone'=None, **kwargs:'any_') -> 'None':
        super().warning(msg, *args, **kwargs)
        self._zato_emit_log('WARNING', str(msg), event)

    warn = warning

# ################################################################################################################################

    def error(self, msg:'any_', *args:'any_', event:'strnone'=None, **kwargs:'any_') -> 'None':
        super().error(msg, *args, **kwargs)
        self._zato_emit_log('ERROR', str(msg), event)

# ################################################################################################################################

    def critical(self, msg:'any_', *args:'any_', event:'strnone'=None, **kwargs:'any_') -> 'None':
        super().critical(msg, *args, **kwargs)
        self._zato_emit_log('CRITICAL', str(msg), event)

# ################################################################################################################################
# ################################################################################################################################
