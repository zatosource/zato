from typing import Any

import logging
from opentelemetry import trace, context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from zato.server.service import Service

class TracedService(Service):
    def handle(self: Any) -> None: ...
    def _handle(self: Any) -> None: ...

class MyService3(TracedService):
    name: Any
    process_name: Any
    def _handle(self: Any) -> None: ...

class MyService4(TracedService):
    name: Any
    process_name: Any
    def _handle(self: Any) -> None: ...
