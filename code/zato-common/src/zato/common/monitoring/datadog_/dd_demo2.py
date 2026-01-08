# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import socket

# OpenTelemetry
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

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

        resource = Resource.create({'service.name': 'zato'})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint='localhost:4317', insecure=True)
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(__name__)

# ################################################################################################################################

    def run(self):
        self.logger.info('Starting Datadog demo')

        with self.tracer.start_as_current_span('Step 1', attributes={
            'service': 'channel.1',
            'process': 'My process',
            'cid': '123a',
        }):
            pass

        with self.tracer.start_as_current_span('Step 2', attributes={
            'service': 'core.1',
            'process': 'My process',
            'cid': '123a',
            'user.email': 'user@example.com',
        }):
            pass

        with self.tracer.start_as_current_span('Step 3', attributes={
            'service': 'adapter.1',
            'process': 'My process',
            'cid': '123a',
            'user.email': 'user2@example.net',
        }):
            pass

        self.logger.info('Datadog demo completed')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    demo = DatadogDemo()
    demo.setup()
    demo.run()

# ################################################################################################################################
# ################################################################################################################################
