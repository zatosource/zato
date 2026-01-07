# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import logging
import socket

from ddtrace.trace import tracer

# ################################################################################################################################
# ################################################################################################################################

class DatadogDemo:

    def __init__(self):
        self.host_name = socket.gethostname()

# ################################################################################################################################

    def setup(self):
        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s - %(message)s')
        stdout_handler.setFormatter(formatter)

        self.logger = logging.getLogger('zato.demo')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(stdout_handler)

# ################################################################################################################################

    def run(self):
        self.logger.info('Starting Datadog demo')

        parent_span = tracer.trace('My Process', service='My Process', resource='My Process')
        parent_span.set_tag('Process name', 'My process')
        ctx = tracer.current_trace_context()
        parent_span.finish()

        self.logger.info('Parent span finished, ctx=%s', ctx)

        tracer.context_provider.activate(ctx)

        step1 = tracer.trace('Step 1', service='zato-dd-demo', resource='Step 1')
        step1.set_tag('user.email', 'user@example.com')
        self.logger.info('Step 1')
        step1.finish()

        tracer.context_provider.activate(ctx)

        step2 = tracer.trace('Step 2', service='zato-dd-demo', resource='Step 2')
        step2.set_tag('user.email', 'user2@example.net')
        self.logger.info('Step 2')
        step2.finish()

        self.logger.info('Datadog demo completed')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    demo = DatadogDemo()
    demo.setup()
    demo.run()

# ################################################################################################################################
# ################################################################################################################################
