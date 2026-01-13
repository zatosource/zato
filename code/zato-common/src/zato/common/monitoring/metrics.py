# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from threading import RLock

# ddtrace
from ddtrace.vendor.dogstatsd.base import statsd

# Zato
from zato.common.typing_ import anydict, floatnone
from zato.common.util.time_ import utcnow_as_ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class MetricsStore:
    """ Thread-safe storage for process metrics with Prometheus text format export.
    """

    def __init__(self) -> 'None':
        self._metrics: 'anydict' = {}
        self._timers: 'anydict' = {}
        self._lock = RLock()

    def set_value(self, process_name:'str', ctx_id:'str', key:'str', value:'float') -> 'None':
        """ Set metric value for given process, context, and key.
        """
        with self._lock:
            metric_key = (process_name, ctx_id, key)
            self._metrics[metric_key] = value

    def get_value(self, process_name:'str', ctx_id:'str', key:'str') -> 'floatnone':
        """ Get current metric value.
        """
        with self._lock:
            metric_key = (process_name, ctx_id, key)
            return self._metrics.get(metric_key)

    def increment_value(self, process_name:'str', ctx_id:'str', key:'str', amount:'float' = 1.0) -> 'None':
        """ Increment metric value by amount.
        """
        with self._lock:
            metric_key = (process_name, ctx_id, key)
            current = self._metrics.get(metric_key, 0.0)
            new_value = current + amount
            self._metrics[metric_key] = new_value

    def decrement_value(self, process_name:'str', ctx_id:'str', key:'str', amount:'float' = 1.0) -> 'None':
        """ Decrement metric value by amount.
        """
        with self._lock:
            metric_key = (process_name, ctx_id, key)
            current = self._metrics.get(metric_key, 0.0)
            new_value = current - amount
            self._metrics[metric_key] = new_value

    def set_max_value(self, process_name:'str', ctx_id:'str', key:'str', value:'float') -> 'None':
        """ Set value only if it exceeds current value.
        """
        with self._lock:
            metric_key = (process_name, ctx_id, key)
            current = self._metrics.get(metric_key, float('-inf'))
            if value > current:
                self._metrics[metric_key] = value

    def set_min_value(self, process_name:'str', ctx_id:'str', key:'str', value:'float') -> 'None':
        """ Set value only if it is below current value.
        """
        with self._lock:
            metric_key = (process_name, ctx_id, key)
            current = self._metrics.get(metric_key, float('inf'))
            if value < current:
                self._metrics[metric_key] = value

    def timer_start(self, process_name:'str', ctx_id:'str', key:'str') -> 'None':
        """ Start timer for given key.
        """
        with self._lock:
            timer_key = (process_name, ctx_id, key)
            current_time = utcnow_as_ms()
            self._timers[timer_key] = current_time

    def timer_stop(self, process_name:'str', ctx_id:'str', key:'str') -> 'floatnone':
        """ Stop timer and record elapsed milliseconds as metric.
        """
        with self._lock:
            timer_key = (process_name, ctx_id, key)
            start_time = self._timers.pop(timer_key, None)
            if start_time is not None:
                current_time = utcnow_as_ms()
                elapsed_seconds = current_time - start_time
                elapsed_ms = elapsed_seconds * 1000.0
                metric_key = (process_name, ctx_id, key)
                self._metrics[metric_key] = elapsed_ms
                return elapsed_ms
            return None

    def get_prometheus_format(self) -> 'str':
        """ Export all metrics in Prometheus text format.
        """
        with self._lock:
            if not self._metrics:
                return '# No metrics available\n'

            lines = ['# HELP process_value Process metric values']
            lines.append('# TYPE process_value gauge')

            for (process_name, ctx_id, key), value in sorted(self._metrics.items()):
                if ctx_id:
                    line = f'process_value{{process_name="{process_name}",ctx_id="{ctx_id}",key="{key}"}} {value}'
                else:
                    line = f'process_value{{process_name="{process_name}",key="{key}"}} {value}'
                lines.append(line)

            return '\n'.join(lines) + '\n'

# ################################################################################################################################
# ################################################################################################################################

class ServiceMetrics:
    """ Metrics interface for services.
    """

    def __init__(self, service:'Service') -> 'None':
        self.service = service

    def push(self, event_name:'str', value:'float') -> 'None':
        """ Push a metric with a numeric value.
        """
        import logging
        logger = logging.getLogger('zato.metrics.push')

        service_name = self.service.name
        server = self.service.server

        logger.info('[trace] event_name=%s value=%s service_name=%s', event_name, value, service_name)
        logger.info('[trace] is_datadog_enabled=%s is_grafana_cloud_enabled=%s',
            server.is_datadog_enabled, server.is_grafana_cloud_enabled)

        if server.is_datadog_enabled:
            logger.info('[trace] pushing to datadog')
            tags = [f'service:{service_name}']
            statsd.gauge(event_name, value, tags=tags)
            logger.info('[trace] datadog push done')

        if server.is_grafana_cloud_enabled:
            logger.info('[trace] pushing to grafana cloud')
            logger.info('[trace] otlp_meter=%s', server.otlp_meter)
            logger.info('[trace] otlp_gauges=%s', server.otlp_gauges)
            logger.info('[trace] otlp_gauges_lock=%s', server.otlp_gauges_lock)
            with server.otlp_gauges_lock:
                logger.info('[trace] acquired lock')
                gauge = server.otlp_gauges.get(event_name)
                logger.info('[trace] existing gauge=%s', gauge)
                if not gauge:
                    logger.info('[trace] creating new gauge for %s', event_name)
                    gauge = server.otlp_meter.create_gauge(event_name)
                    server.otlp_gauges[event_name] = gauge
                    logger.info('[trace] gauge created=%s', gauge)
            logger.info('[trace] setting gauge value=%s attrs=%s', value, {'service': service_name})
            gauge.set(value, {'service': service_name})
            logger.info('[trace] gauge.set done')

# ################################################################################################################################
# ################################################################################################################################

# Global metrics store instance
_global_metrics_store = MetricsStore()

# ################################################################################################################################
# ################################################################################################################################

def get_global_metrics_store() -> 'MetricsStore':
    """ Get the global metrics store instance.
    """
    return _global_metrics_store

# ################################################################################################################################
# ################################################################################################################################
