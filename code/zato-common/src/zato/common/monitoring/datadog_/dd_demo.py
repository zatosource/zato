# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import logging
import socket

from ddtrace import tracer

# ################################################################################################################################
# ################################################################################################################################

class DatadogDemo:

    def __init__(self):
        self.host_name = socket.gethostname()

# ################################################################################################################################

    def setup(self):
        tracer.configure(
            hostname=self.host_name,
        )

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

        with tracer.trace('demo-process', service='zato-dd-demo', resource='demo-process') as span:
            span.set_tag('demo.key', 'demo-value')
            span.set_tag('demo.step', 'start')
            span.set_tag('service.instance.id', 'demo-instance')
            span.set_tag('service.namespace', 'demo')
            span.set_tag('deployment.environment', 'dev')
            span.set_tag('host.id', self.host_name)
            span.set_tag('host.name', self.host_name)

            self.logger.info('Inside demo-process span')

            span.set_tag('user.email', 'user@example.com')
            span.set_tag('event.type', 'login')
            span.set_tag('event.name', 'user_login')
            self.logger.info('user_login event')

            span.set_tag('session.id', 'abc123')
            span.set_tag('event.name', 'session_created')
            self.logger.info('session_created event')

            with tracer.trace('demo-child-operation', service='zato-dd-demo', resource='demo-child-operation') as child_span:
                child_span.set_tag('operation.type', 'child')
                self.logger.info('Inside child operation')

            span.set_tag('user.email', 'user2@example.net')
            span.set_tag('event.type', 'action')
            span.set_tag('action.name', 'update_profile')
            span.set_tag('event.name', 'user_action')
            self.logger.info('user_action event')

            span.set_tag('user.email', 'user2@example.net')
            span.set_tag('event.type', 'logout')
            span.set_tag('event.name', 'user_logout')
            self.logger.info('user_logout event')

            self.logger.info('Child operation completed')

        self.logger.info('Datadog demo completed')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    demo = DatadogDemo()
    demo.setup()
    demo.run()

# ################################################################################################################################
# ################################################################################################################################
