# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

template = """extensions:
  health_check:
  pprof:
    endpoint: 0.0.0.0:1777
  zpages:
    endpoint: 0.0.0.0:55679

receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
  prometheus:
    config:
      scrape_configs:
      - job_name: 'otel-collector'
        scrape_interval: 10s
        static_configs:
        - targets: ['0.0.0.0:8888']
  jaeger:
    protocols:
      grpc:
        endpoint: 0.0.0.0:14250
      thrift_binary:
        endpoint: 0.0.0.0:6832
      thrift_compact:
        endpoint: 0.0.0.0:6831
      thrift_http:
        endpoint: 0.0.0.0:14268
  zipkin:
    endpoint: 0.0.0.0:9411

processors:
  batch:
  resource/logs:
    attributes:
    - key: exporter
      value: "OTLP"
      action: upsert
    - key: job
      value: "demo/zato-otlp-demo"
      action: upsert

connectors:
  spanmetrics:
  grafanacloud:
    host_identifiers: ["host.name"]

exporters:
  debug:
    verbosity: detailed
  otlphttp:
    endpoint: {endpoint}
    headers:
      Authorization: Basic {credentials}

service:
  pipelines:
    traces:
      receivers: [otlp, jaeger, zipkin]
      processors: [batch]
      exporters: [debug, otlphttp, spanmetrics, grafanacloud]
    metrics:
      receivers: [otlp, prometheus, spanmetrics]
      processors: [batch]
      exporters: [debug, otlphttp]
    metrics/grafanacloud:
      receivers: [grafanacloud]
      processors: [batch]
      exporters: [otlphttp]
    logs:
      receivers: [otlp]
      processors: [resource/logs, batch]
      exporters: [debug, otlphttp]
  extensions: [health_check, pprof, zpages]
"""
