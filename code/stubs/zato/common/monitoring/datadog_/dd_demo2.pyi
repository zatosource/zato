from typing import Any

import logging
import socket
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

class DatadogDemo:
    def __init__(self: Any) -> None: ...
    def setup(self: Any) -> None: ...
    def run(self: Any) -> None: ...
