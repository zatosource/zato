# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import logging
import os
import socket

os.environ['DD_TRACE_DEBUG'] = 'false'

from ddtrace import patch
from ddtrace.trace import tracer

logging.getLogger('ddtrace').setLevel(logging.WARNING)

patch(gevent=True)

# ################################################################################################################################
# ################################################################################################################################

class DatadogDemo:

    def __init__(self):
        self.host_name = socket.gethostname()

# ################################################################################################################################

    def setup(self):
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s - %(message)s')
        stdout_handler.setFormatter(formatter)

        self.logger = logging.getLogger('zato.demo')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(stdout_handler)

# ################################################################################################################################

    def run(self):
        self.logger.info('Starting Datadog demo')

        step1 = tracer.trace(name='', service='channel.1', resource='Step 1')
        step1.set_tag('process', 'My process')
        step1.set_tag('cid', '123a')
        step1.set_tag('message.info', '---')

        ctx = tracer.current_trace_context()
        step1.finish()

        tracer.context_provider.activate(ctx)

        step2 = tracer.trace(name='', service='core.1', resource='Step 2')
        step2.set_tag('process', 'My process')
        step2.set_tag('cid', '123a')
        step2.set_tag('message.info', 'Here is my info message')
        step2.finish()

        tracer.context_provider.activate(ctx)

        step3 = tracer.trace(name='', service='adapter.1', resource='Step 3')
        step3.set_tag('process', 'My process')
        step3.set_tag('cid', '123a')
        step3.set_tag('message.info', 'System updated OK')
        step3.finish()

        self.logger.info('Datadog demo completed')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    demo = DatadogDemo()
    demo.setup()
    demo.run()

# ################################################################################################################################
# ################################################################################################################################
