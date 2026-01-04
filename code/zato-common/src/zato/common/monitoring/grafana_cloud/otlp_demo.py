# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import logging
import socket

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import SpanKind

# ################################################################################################################################
# ################################################################################################################################

class OTLPDemo:

    def __init__(self, traces_endpoint='http://localhost:4318/v1/traces', logs_endpoint='http://localhost:4318/v1/logs', metrics_endpoint='http://localhost:4318/v1/metrics'):
        self.traces_endpoint = traces_endpoint
        self.logs_endpoint = logs_endpoint
        self.metrics_endpoint = metrics_endpoint

# ################################################################################################################################

    def setup(self):
        host_name = socket.gethostname()

        resource = Resource.create({
            'service.name': 'zato-otlp-demo',
            'service.instance.id': 'demo-instance',
            'service.namespace': 'demo',
            'deployment.environment': 'dev',
            'host.id': host_name,
            'host.name': host_name,
        })

        trace_provider = TracerProvider(resource=resource)
        span_exporter = OTLPSpanExporter(endpoint=self.traces_endpoint)
        span_processor = SimpleSpanProcessor(span_exporter)
        trace_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(trace_provider)

        self.tracer = trace.get_tracer('zato.demo')

        log_provider = LoggerProvider(resource=resource)
        log_exporter = OTLPLogExporter(endpoint=self.logs_endpoint)
        log_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
        set_logger_provider(log_provider)

        otlp_handler = LoggingHandler(level=logging.INFO, logger_provider=log_provider)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s - %(message)s')
        stdout_handler.setFormatter(formatter)

        self.logger = logging.getLogger('zato.demo')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(otlp_handler)
        self.logger.addHandler(stdout_handler)

        metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=self.metrics_endpoint))
        metric_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(metric_provider)

        self.meter = metrics.get_meter('zato.demo')
        self.event_counter = self.meter.create_counter('user_events', description='User events counter')

# ################################################################################################################################

    def run(self):
        self.logger.info('Starting OTLP demo')

        with self.tracer.start_as_current_span('demo-process', kind=SpanKind.SERVER) as span:
            span.set_attribute('demo.key', 'demo-value')
            span.set_attribute('demo.step', 'start')

            self.logger.info('Inside demo-process span')

            span.add_event('user_login', {'user.email': 'user@example.com', 'event.type': 'login'})
            self.event_counter.add(1, {'user.email': 'user@example.com', 'event.type': 'login'})
            event_logger = self.logger.getChild('events')
            event_logger.info('user_login', extra={'user.email': 'user@example.com', 'event.type': 'login'})

            span.add_event('session_created', {'user.email': 'user@example.com', 'event.type': 'session', 'session.id': 'abc123'})
            self.event_counter.add(1, {'user.email': 'user@example.com', 'event.type': 'session'})
            event_logger.info('session_created', extra={'user.email': 'user@example.com', 'event.type': 'session', 'session.id': 'abc123'})

            with self.tracer.start_as_current_span('demo-child-operation', kind=SpanKind.INTERNAL) as child_span:
                child_span.set_attribute('operation.type', 'child')
                self.logger.info('Inside child operation')

            span.add_event('user_action', {'user.email': 'user2@example.net', 'event.type': 'action', 'action.name': 'update_profile'})
            self.event_counter.add(1, {'user.email': 'user2@example.net', 'event.type': 'action'})
            event_logger.info('user_action', extra={'user.email': 'user2@example.net', 'event.type': 'action', 'action.name': 'update_profile'})

            span.add_event('user_logout', {'user.email': 'user2@example.net', 'event.type': 'logout'})
            self.event_counter.add(1, {'user.email': 'user2@example.net', 'event.type': 'logout'})
            event_logger.info('user_logout', extra={'user.email': 'user2@example.net', 'event.type': 'logout'})

            self.logger.info('Child operation completed')

        self.logger.info('OTLP demo completed')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    demo = OTLPDemo()
    demo.setup()
    demo.run()

# ################################################################################################################################
# ################################################################################################################################
