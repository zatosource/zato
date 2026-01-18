# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.DEBUG)

# OpenTelemetry
from opentelemetry import trace, context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Zato
from zato.server.service import Service

resource = Resource.create({'service.name': 'zato'})
provider = TracerProvider(resource=resource)
exporter = OTLPSpanExporter(endpoint='localhost:4317', insecure=True)
provider.add_span_processor(SimpleSpanProcessor(exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

class TracedService(Service):
    def handle(self):
        ctx = context.Context()
        with tracer.start_as_current_span(self.name, context=ctx) as span:
            span.set_attribute('process', self.process_name)
            span.set_attribute('cid', self.cid)
            self._handle()

    def _handle(self):
        raise NotImplementedError

class MyService3(TracedService):
    name = 'service3'
    process_name = 'My process'

    def _handle(self):
        _ = self.invoke(MyService4)
        self.response.payload = {
            'cid1': self.cid,
            'cid2': self.cid,
        }

class MyService4(TracedService):
    name = 'service4'
    process_name = 'My process'

    def _handle(self):
        self.response.payload = self.cid
