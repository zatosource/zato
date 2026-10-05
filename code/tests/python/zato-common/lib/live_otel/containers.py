# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An OpenTelemetry Collector in a container - OTLP over HTTP and over gRPC, both with TLS and a bearer token,
# writing every record it receives as OTLP JSON lines into a directory the tests read back.

# stdlib
import os
import subprocess
from functools import partial
from http.client import OK
from json import loads
from tempfile import mkdtemp
from time import monotonic, sleep
from typing import NamedTuple

# requests
import requests

# Zato
from zato.common.crypto.api import CryptoManager

# Test support
from certificates import generate_certificates
from live_containers.ready import wait_until
from live_environment.quickstart import find_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, dictlist, strlist

    record_list = dictlist
    records_by_id = dict[int, dictlist]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The image the collector runs from, the version the zato-docker Dockerfile names
    Image = 'otel/opentelemetry-collector-contrib:0.143.1'

    # The name of the container so a stale one can be removed
    Container = 'zato-audit-export-test-otel'

    # Where the configuration and the certificates are mounted inside the container, and where the output goes
    Config_Dir = '/etc/otelcol'
    Output_Dir = '/var/lib/otelcol'

    # The names of the files inside those directories
    Config_File = 'config.yaml'
    Output_File = 'logs.jsonl'

    # The ports inside the container
    HTTP_Port   = 4318
    GRPC_Port   = 4317
    Health_Port = 13133

    # The directories of a run are written on the host under these prefixes, so a stale run's can be told apart
    Config_Prefix = 'zato-otel-config-'
    Output_Prefix = 'zato-otel-output-'

    # How long a record has to arrive after the request it records, in seconds, and how often the file is read
    Record_Timeout = 10
    Record_Poll_Interval = 0.2

    # How often the collector writes what it has to the file
    Flush_Interval = '200ms'

    # The attribute every record of the audit log carries
    Event_ID_Attribute = 'zato.audit.event_id'

# ################################################################################################################################
# ################################################################################################################################

# The container runs as the current user so the mounted directories need no special permissions
_directory_mode = 0o755

# The scalar forms OTLP JSON uses and how each is read back - 64-bit integers travel as strings
_json_scalar_keys = ('stringValue', 'boolValue', 'doubleValue', 'bytesValue')

# ################################################################################################################################
# ################################################################################################################################

class OTelCollector(NamedTuple):
    """ A running collector, the addresses it listens on and what it needs to be sent to.
    """
    container_name: 'str'
    http_endpoint: 'str'
    grpc_endpoint: 'str'
    health_url: 'str'
    ca_file: 'str'
    bearer_token: 'str'
    output_path: 'str'
    config_dir: 'str'
    output_dir: 'str'

# ################################################################################################################################
# ################################################################################################################################

def _run(arguments:'strlist') -> 'any_':
    """ Runs one docker command and returns the completed process.
    """
    command = ['docker'] + arguments
    out = subprocess.run(command, capture_output=True, text=True, check=False)
    return out

# ################################################################################################################################

def _run_or_raise(arguments:'strlist', what:'str') -> 'None':
    result = _run(arguments)

    if result.returncode != 0:
        raise Exception(f'Could not {what}, stdout: `{result.stdout}`, stderr: `{result.stderr}`')

# ################################################################################################################################

def remove_container(name:'str'=ModuleCtx.Container) -> 'None':
    """ Removes the container, running or not, along with whatever a previous run left behind under the name.
    """
    _ = _run(['rm', '-f', name])

# ################################################################################################################################

def stop_container(name:'str'=ModuleCtx.Container) -> 'None':
    """ Stops the container without removing it, so it can be started again on the same ports.
    """
    _run_or_raise(['stop', name], f'stop `{name}`')

# ################################################################################################################################

def start_container(name:'str'=ModuleCtx.Container) -> 'None':
    """ Starts a stopped container again.
    """
    _run_or_raise(['start', name], f'start `{name}`')

# ################################################################################################################################

def _new_directory(prefix:'str') -> 'str':
    out = mkdtemp(prefix=prefix)
    os.chmod(out, _directory_mode)
    return out

# ################################################################################################################################

def build_config(*, server_cert:'str', server_key:'str', bearer_token:'str') -> 'str':
    """ The collector's configuration - the OTLP receiver over HTTP and gRPC, both with TLS and the bearer
    authenticator, and one file exporter writing OTLP JSON lines.
    """
    config_dir = ModuleCtx.Config_Dir
    cert_name = os.path.basename(server_cert)
    key_name = os.path.basename(server_key)
    output_path = f'{ModuleCtx.Output_Dir}/{ModuleCtx.Output_File}'

    out = f'''\
extensions:
  health_check:
    endpoint: 0.0.0.0:{ModuleCtx.Health_Port}
  bearertokenauth:
    token: "{bearer_token}"

receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:{ModuleCtx.GRPC_Port}
        tls:
          cert_file: {config_dir}/{cert_name}
          key_file: {config_dir}/{key_name}
        auth:
          authenticator: bearertokenauth
      http:
        endpoint: 0.0.0.0:{ModuleCtx.HTTP_Port}
        tls:
          cert_file: {config_dir}/{cert_name}
          key_file: {config_dir}/{key_name}
        auth:
          authenticator: bearertokenauth

exporters:
  file:
    path: {output_path}
    flush_interval: {ModuleCtx.Flush_Interval}

service:
  extensions: [health_check, bearertokenauth]
  pipelines:
    logs:
      receivers: [otlp]
      exporters: [file]
'''
    return out

# ################################################################################################################################

def _is_healthy(health_url:'str') -> 'bool':
    """ One attempt at the health check extension.
    """
    response = requests.get(health_url, timeout=2)
    out = response.status_code == OK
    return out

# ################################################################################################################################

def wait_until_ready(collector:'OTelCollector') -> 'None':
    """ Waits until the collector's health check answers.
    """
    check = partial(_is_healthy, collector.health_url)
    wait_until(check, f'the OpenTelemetry Collector in `{collector.container_name}`')

# ################################################################################################################################

def start_collector(container_name:'str'=ModuleCtx.Container) -> 'OTelCollector':
    """ Starts the collector with TLS and a bearer token on both receivers, on host ports nothing else uses,
    and waits until it is healthy.
    """
    remove_container(container_name)

    config_dir = _new_directory(ModuleCtx.Config_Prefix)
    output_dir = _new_directory(ModuleCtx.Output_Prefix)

    certificates = generate_certificates(config_dir)
    bearer_token = 'otel.' + CryptoManager.generate_hex_string()

    config = build_config(server_cert=certificates.server_cert, server_key=certificates.server_key, bearer_token=bearer_token)
    config_path = os.path.join(config_dir, ModuleCtx.Config_File)

    with open(config_path, 'w') as file_:
        _ = file_.write(config)

    os.chmod(config_path, 0o644)

    # The certificates are read by the process inside the container, which runs as the current user
    for path in (certificates.server_cert, certificates.server_key, certificates.ca_cert):
        os.chmod(path, 0o644)

    http_port = find_free_port()
    grpc_port = find_free_port()
    health_port = find_free_port()

    print(f'Starting OpenTelemetry Collector container {container_name} on ports {http_port}, {grpc_port} and {health_port}', flush=True)

    command = [
        'run', '-d',
        '--name', container_name,
        '--user', str(os.getuid()),
        '-p', f'127.0.0.1:{http_port}:{ModuleCtx.HTTP_Port}',
        '-p', f'127.0.0.1:{grpc_port}:{ModuleCtx.GRPC_Port}',
        '-p', f'127.0.0.1:{health_port}:{ModuleCtx.Health_Port}',
        '-v', f'{config_dir}:{ModuleCtx.Config_Dir}:ro',
        '-v', f'{output_dir}:{ModuleCtx.Output_Dir}',
        ModuleCtx.Image,
        '--config', f'{ModuleCtx.Config_Dir}/{ModuleCtx.Config_File}',
    ]

    _run_or_raise(command, f'start `{container_name}`')

    out = OTelCollector(
        container_name=container_name,
        http_endpoint=f'https://127.0.0.1:{http_port}',
        grpc_endpoint=f'https://127.0.0.1:{grpc_port}',
        health_url=f'http://127.0.0.1:{health_port}/',
        ca_file=certificates.ca_cert,
        bearer_token=bearer_token,
        output_path=os.path.join(output_dir, ModuleCtx.Output_File),
        config_dir=config_dir,
        output_dir=output_dir,
    )

    wait_until_ready(out)
    print(f'OpenTelemetry Collector is ready at {out.http_endpoint} and {out.grpc_endpoint}', flush=True)

    return out

# ################################################################################################################################
# ################################################################################################################################

def from_json_value(value:'anydict') -> 'any_':
    """ Turns the OTLP JSON form of an attribute value into a Python one.
    """
    if 'intValue' in value:
        out = int(value['intValue'])
        return out

    if 'arrayValue' in value:
        out = []
        for item in value['arrayValue'].get('values', []):
            out.append(from_json_value(item))
        return out

    if 'kvlistValue' in value:
        out = {}
        for item in value['kvlistValue'].get('values', []):
            out[item['key']] = from_json_value(item['value'])
        return out

    for key in _json_scalar_keys:
        if key in value:
            out = value[key]
            return out

    return None

# ################################################################################################################################

def attributes_of(items:'anylist') -> 'anydict':
    """ A list of OTLP JSON key-value pairs as a dict.
    """
    out:'anydict' = {}

    for item in items:
        out[item['key']] = from_json_value(item['value'])

    return out

# ################################################################################################################################

def _parse_line(line:'str') -> 'record_list':
    """ The records of one exported request, each with its resource and scope attributes attached.
    """
    out:'record_list' = []

    document = loads(line)

    for resource_logs in document.get('resourceLogs', []):

        resource = attributes_of(resource_logs.get('resource', {}).get('attributes', []))

        for scope_logs in resource_logs.get('scopeLogs', []):

            scope = scope_logs.get('scope', {})

            for log_record in scope_logs.get('logRecords', []):

                record:'anydict' = {
                    'time_unix_nano': int(log_record.get('timeUnixNano', '0')),
                    'observed_time_unix_nano': int(log_record.get('observedTimeUnixNano', '0')),
                    'severity_number': log_record.get('severityNumber', 0),
                    'severity_text': log_record.get('severityText', ''),
                    'event_name': log_record.get('eventName', ''),
                    'body': from_json_value(log_record.get('body', {})),
                    'attributes': attributes_of(log_record.get('attributes', [])),
                    'resource': resource,
                    'scope_name': scope.get('name', ''),
                    'scope_version': scope.get('version', ''),
                }

                out.append(record)

    return out

# ################################################################################################################################

def read_records(output_path:'str') -> 'records_by_id':
    """ Every record the collector wrote so far, keyed by the audit event id, each id holding its records
    in the order they arrived - an event updated in place arrives more than once.
    """
    out:'records_by_id' = {}

    if not os.path.isfile(output_path):
        return out

    with open(output_path) as file_:
        lines = file_.readlines()

    for line in lines:

        line = line.strip()

        # The last line may still be half-written
        if not line:
            continue

        try:
            records = _parse_line(line)
        except ValueError:
            continue

        for record in records:
            event_id = record['attributes'].get(ModuleCtx.Event_ID_Attribute)

            if event_id is None:
                continue

            out.setdefault(event_id, []).append(record)

    return out

# ################################################################################################################################

def wait_for_record(output_path:'str', event_id:'int', *, timeout:'float'=ModuleCtx.Record_Timeout, min_count:'int'=1) -> 'record_list':
    """ Waits until at least this many records of the event have arrived and returns all of them.
    """
    deadline = monotonic() + timeout

    while monotonic() < deadline:

        records = read_records(output_path).get(event_id, [])
        record_count = len(records)

        if record_count >= min_count:
            return records

        sleep(ModuleCtx.Record_Poll_Interval)

    records = read_records(output_path)
    raise Exception(f'No record of event {event_id} within {timeout}s, got ids: {sorted(records)}')

# ################################################################################################################################

def has_record(output_path:'str', event_id:'int') -> 'bool':
    """ Whether any record of the event has arrived.
    """
    out = event_id in read_records(output_path)
    return out

# ################################################################################################################################
# ################################################################################################################################
