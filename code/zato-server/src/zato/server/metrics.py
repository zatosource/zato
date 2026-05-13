# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# prometheus_client
from prometheus_client import Counter, Gauge, Histogram, Info, REGISTRY

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

Error_Source_None       = 'none'
Error_Source_Gateway     = 'gateway'
Error_Source_Upstream    = 'upstream'
Error_Source_Auth        = 'auth'
Error_Source_Rate_Limit  = 'rate_limit'

# ################################################################################################################################
# ################################################################################################################################

zato_histogram_buckets = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)

zato_size_histogram_buckets = (64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, 4194304, 16777216)

# ################################################################################################################################
# ################################################################################################################################

def get_status_code_class(status_code:'str') -> 'str':
    """ Converts a raw HTTP status code to its class, e.g. '200' -> '2xx', '503' -> '5xx'.
    """

    # Non-numeric codes like 'timeout' or 'connection_error' map to '0xx' ..
    if not status_code.isdigit():
        out = '0xx'

    # .. otherwise, use the first digit to form the class.
    else:
        first_digit = status_code[0]
        out = f'{first_digit}xx'

    return out

# ################################################################################################################################

def get_error_source_from_status_class(status_class:'str') -> 'str':
    """ Derives an error_source label value from an HTTP status code class.
    """

    # 2xx and 3xx are successes ..
    if status_class in ('2xx', '3xx'):
        out = Error_Source_None

    # .. 0xx means connection failure or timeout, which is an upstream issue ..
    elif status_class == '0xx':
        out = Error_Source_Upstream

    # .. anything else is a gateway error by default
    # (auth and rate_limit attribution is done at a higher level).
    else:
        out = Error_Source_Gateway

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_or_create_counter(name:'str', documentation:'str', labelnames:'tuple') -> 'Counter':
    """ Returns an existing counter from the registry or creates a new one.
    """
    if name in REGISTRY._names_to_collectors:
        out = cast_('Counter', REGISTRY._names_to_collectors[name])
    else:
        out = Counter(name, documentation, labelnames)

    return out

# ################################################################################################################################

def _get_or_create_histogram(name:'str', documentation:'str', labelnames:'tuple', buckets:'tuple') -> 'Histogram':
    """ Returns an existing histogram from the registry or creates a new one.
    """
    if name in REGISTRY._names_to_collectors:
        out = cast_('Histogram', REGISTRY._names_to_collectors[name])
    else:
        out = Histogram(name, documentation, labelnames, buckets=buckets)

    return out

# ################################################################################################################################

def _get_or_create_gauge(name:'str', documentation:'str', labelnames:'tuple'=()) -> 'Gauge':
    """ Returns an existing gauge from the registry or creates a new one.
    """
    if name in REGISTRY._names_to_collectors:
        out = cast_('Gauge', REGISTRY._names_to_collectors[name])
    else:
        out = Gauge(name, documentation, labelnames)

    return out

# ################################################################################################################################

def _get_or_create_info(name:'str', documentation:'str') -> 'Info':
    """ Returns an existing info metric from the registry or creates a new one.
    """
    if name in REGISTRY._names_to_collectors:
        out = cast_('Info', REGISTRY._names_to_collectors[name])
    else:
        out = Info(name, documentation)

    return out

# ################################################################################################################################
# ################################################################################################################################

# REST channel metrics

zato_rest_channel_requests_total = _get_or_create_counter(
    'zato_rest_channel_requests_total',
    'Total REST channel requests handled by this server, by channel, HTTP status class, and error attribution',
    ('channel_name', 'status_code', 'error_source'),
)

zato_rest_channel_request_duration_seconds = _get_or_create_histogram(
    'zato_rest_channel_request_duration_seconds',
    'Duration of REST channel requests in seconds, from request accept to response write complete',
    ('channel_name',),
    zato_histogram_buckets,
)

zato_rest_channel_request_size_bytes = _get_or_create_histogram(
    'zato_rest_channel_request_size_bytes',
    'Size of inbound REST request bodies in bytes, by channel name',
    ('channel_name',),
    zato_size_histogram_buckets,
)

zato_rest_channel_response_size_bytes = _get_or_create_histogram(
    'zato_rest_channel_response_size_bytes',
    'Size of outbound REST response bodies in bytes, by channel name',
    ('channel_name',),
    zato_size_histogram_buckets,
)

# ################################################################################################################################
# ################################################################################################################################

# REST outgoing metrics

zato_rest_outgoing_requests_total = _get_or_create_counter(
    'zato_rest_outgoing_requests_total',
    'Total outgoing REST requests sent to external systems, by connection, HTTP status class, and error attribution',
    ('connection_name', 'status_code', 'error_source'),
)

zato_rest_outgoing_request_duration_seconds = _get_or_create_histogram(
    'zato_rest_outgoing_request_duration_seconds',
    'Duration of outgoing REST requests in seconds, from send to response received',
    ('connection_name',),
    zato_histogram_buckets,
)

zato_rest_outgoing_request_size_bytes = _get_or_create_histogram(
    'zato_rest_outgoing_request_size_bytes',
    'Size of outgoing REST request bodies in bytes, by connection name',
    ('connection_name',),
    zato_size_histogram_buckets,
)

zato_rest_outgoing_response_size_bytes = _get_or_create_histogram(
    'zato_rest_outgoing_response_size_bytes',
    'Size of inbound REST response bodies from external systems in bytes, by connection name',
    ('connection_name',),
    zato_size_histogram_buckets,
)

# ################################################################################################################################
# ################################################################################################################################

# Service invocation metrics

zato_service_invocations_total = _get_or_create_counter(
    'zato_service_invocations_total',
    'Total invocations of Zato services, by service name and outcome',
    ('service_name', 'outcome'),
)

zato_service_duration_seconds = _get_or_create_histogram(
    'zato_service_duration_seconds',
    'Duration of service handle() execution in seconds, by service name',
    ('service_name',),
    zato_histogram_buckets,
)

# ################################################################################################################################
# ################################################################################################################################

# Pub/sub metrics

zato_pubsub_messages_published_total = _get_or_create_counter(
    'zato_pubsub_messages_published_total',
    'Total messages published to pub/sub topics',
    ('topic_name',),
)

zato_pubsub_messages_delivered_total = _get_or_create_counter(
    'zato_pubsub_messages_delivered_total',
    'Total messages delivered from pub/sub topics to subscribers',
    ('topic_name',),
)

# ################################################################################################################################
# ################################################################################################################################

# Server info and operational metrics

zato_server_info = _get_or_create_info(
    'zato_server',
    'Static information about this Zato server instance',
)

def set_server_info(server_name:'str', version:'str'='4.1') -> 'None':
    """ Called once at startup to populate the server info metric.
    """
    _ = zato_server_info.info({'server_name': server_name, 'version': version})

# ################################################################################################################################

_server_start_time = time.time()

def get_uptime_seconds() -> 'float':
    """ Returns the number of seconds since the server process started.
    """
    return time.time() - _server_start_time

zato_server_uptime_seconds = _get_or_create_gauge(
    'zato_server_uptime_seconds',
    'Time in seconds since the server process started',
)

def refresh_uptime() -> 'None':
    """ Updates the uptime gauge to the current elapsed time. Called before each scrape.
    """
    _ = zato_server_uptime_seconds.set(get_uptime_seconds())

# ################################################################################################################################

zato_server_requests_in_flight = _get_or_create_gauge(
    'zato_server_requests_in_flight',
    'Number of HTTP requests currently being processed',
)

# ################################################################################################################################

zato_server_config_reloads_total = _get_or_create_counter(
    'zato_server_config_reloads_total',
    'Total configuration reload operations, by result',
    ('result',),
)

# ################################################################################################################################

zato_server_config_last_reload_timestamp_seconds = _get_or_create_gauge(
    'zato_server_config_last_reload_timestamp_seconds',
    'Unix timestamp of the last successful configuration reload',
)

# ################################################################################################################################

zato_outgoing_health = _get_or_create_gauge(
    'zato_outgoing_health',
    'Health status of outgoing connections, 1 = healthy, 0 = unhealthy',
    ('connection_name', 'address'),
)

# ################################################################################################################################

zato_tls_certificate_expiry_timestamp_seconds = _get_or_create_gauge(
    'zato_tls_certificate_expiry_timestamp_seconds',
    'Unix timestamp when a TLS certificate expires',
    ('cert_name', 'listener'),
)

# ################################################################################################################################
# ################################################################################################################################
