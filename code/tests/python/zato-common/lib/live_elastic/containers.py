# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Elasticsearch and Kibana in containers on a network of their own - Elasticsearch with security on and its native
# OTLP logs endpoint, an API key that may only write logs, and a Kibana data view over the audit log's data stream.

# stdlib
import subprocess
from functools import partial
from http.client import NOT_FOUND, OK
from typing import NamedTuple

# requests
import requests

# OpenTelemetry
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest

# Zato
from zato.common.crypto.api import CryptoManager

# Test support
from live_containers.ready import ContainerExited, StartupFailed, wait_until
from live_environment.quickstart import find_free_port, Host

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The images, the newest release of the 9.x line, the first whose Elasticsearch accepts OTLP logs
    ES_Image     = 'docker.elastic.co/elasticsearch/elasticsearch:9.5.4'
    Kibana_Image = 'docker.elastic.co/kibana/kibana:9.5.4'

    # The network the two containers talk over and their names, so a stale run's can be removed
    Network          = 'zato-elastic-demo'
    ES_Container     = 'zato-elastic-demo-elasticsearch'
    Kibana_Container = 'zato-elastic-demo-kibana'

    # The ports inside the containers
    ES_Port     = 9200
    Kibana_Port = 5601

    # The heap is capped so the demo does not take half of the machine's memory
    ES_Java_Opts = '-Xms1g -Xmx1g'

    # The built-in users - the one a person signs in to Kibana as and the one Kibana itself connects as
    Superuser   = 'elastic'
    Kibana_User = 'kibana_system'

    # The containers listen on 127.0.0.1 only, so the person signing in gets a password easy to type
    Superuser_Password = 'elastic'

    # Where Elasticsearch accepts OTLP logs, given in full because it is not the collector's /v1/logs
    OTLP_Logs_Path = '/_otlp/v1/logs'

    # The API key the server exports with and what it may do - write documents into log data streams and create them
    API_Key_Name = 'zato-audit-export'
    API_Key_Role = 'zato_audit_export'
    API_Key_Indices = ['logs-*']
    API_Key_Privileges = ['create_doc', 'auto_configure']

    # The dataset the server's records name as a resource attribute, which decides the data stream they land in
    Dataset = 'zato.audit'

    # The Kibana data view over that data stream
    Data_View_ID      = 'zato-audit-log'
    Data_View_Name    = 'Zato audit log'
    Data_View_Pattern = 'logs-zato.audit.otel-*'
    Data_View_Time    = '@timestamp'

    # The columns Discover opens with
    Discover_Columns = (
        'severity_text',
        'event_name',
        'attributes.zato.audit.object_name',
        'attributes.zato.audit.endpoint',
        'attributes.zato.audit.ext_client_id',
        'attributes.zato.audit.outcome',
        'body.text',
    )

    # How far back Discover looks and how often it refreshes, in milliseconds
    Discover_Time_From = 'now-15m'
    Discover_Refresh   = 5000

    # Kibana's encryption keys need at least 32 characters, 256 bits are 64 hex ones
    Kibana_Key_Bits = 256

    # Kibana needs a header on every call that changes something
    Kibana_XSRF_Header = 'kbn-xsrf'

    # Timeout of each HTTP request, in seconds
    HTTP_Timeout = 10

    # How many lines of a container's log a failure shows
    Log_Tail = '50'

# ################################################################################################################################
# ################################################################################################################################

# The cluster states in which the node accepts writes
_ready_cluster_states = ('green', 'yellow')

# The overall Kibana status once it serves requests
_kibana_available = 'available'

# ################################################################################################################################
# ################################################################################################################################

class ElasticStack(NamedTuple):
    """ A running Elasticsearch and Kibana, where they listen, how to sign in and what the server exports with.
    """
    es_url: 'str'
    kibana_url: 'str'
    discover_url: 'str'
    username: 'str'
    password: 'str'
    otlp_logs_endpoint: 'str'
    api_key: 'str'
    dataset: 'str'

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

def _pull(image:'str') -> 'None':
    """ Pulls an image with docker's own progress on the terminal, the first pull takes a while.
    """
    print(f'Pulling {image}', flush=True)

    result = subprocess.run(['docker', 'pull', image], check=False)

    if result.returncode != 0:
        raise Exception(f'Could not pull `{image}`')

# ################################################################################################################################

def remove_stack() -> 'None':
    """ Removes both containers and their network, whatever state a previous run left them in.
    """
    _ = _run(['rm', '-f', ModuleCtx.Kibana_Container])
    _ = _run(['rm', '-f', ModuleCtx.ES_Container])
    _ = _run(['network', 'rm', ModuleCtx.Network])

# ################################################################################################################################

def _check_running(container_name:'str') -> 'None':
    """ Ends a wait at once when the container it waits on is gone, with the end of its log as the reason.
    """
    result = _run(['inspect', '-f', '{{.State.Running}}', container_name])

    if result.stdout.strip() != 'true':
        logs = _run(['logs', '--tail', ModuleCtx.Log_Tail, container_name])
        raise ContainerExited(f'Container `{container_name}` is not running, its log:\n{logs.stdout}{logs.stderr}')

# ################################################################################################################################
# ################################################################################################################################

def _start_elasticsearch(port:'int', password:'str') -> 'None':
    """ One node with security on and plain HTTP, so a person signs in and the server sends an API key.
    """
    print(f'Starting Elasticsearch container {ModuleCtx.ES_Container} on port {port}', flush=True)

    command = [
        'run', '-d',
        '--name', ModuleCtx.ES_Container,
        '--network', ModuleCtx.Network,
        '-p', f'{Host}:{port}:{ModuleCtx.ES_Port}',
        '-e', 'discovery.type=single-node',
        '-e', 'xpack.security.enabled=true',
        '-e', 'xpack.security.http.ssl.enabled=false',
        '-e', 'xpack.security.transport.ssl.enabled=false',
        '-e', 'xpack.license.self_generated.type=basic',
        '-e', 'cluster.routing.allocation.disk.threshold_enabled=false',
        '-e', f'ELASTIC_PASSWORD={password}',
        '-e', f'ES_JAVA_OPTS={ModuleCtx.ES_Java_Opts}',
        ModuleCtx.ES_Image,
    ]

    _run_or_raise(command, f'start `{ModuleCtx.ES_Container}`')

# ################################################################################################################################

def _is_es_ready(es_url:'str', auth:'any_') -> 'bool':
    """ One attempt at the cluster health, which answers once the node accepts writes.
    """
    _check_running(ModuleCtx.ES_Container)

    response = requests.get(f'{es_url}/_cluster/health', auth=auth, timeout=ModuleCtx.HTTP_Timeout)

    if response.status_code != OK:
        return False

    out = response.json()['status'] in _ready_cluster_states
    return out

# ################################################################################################################################

def _set_kibana_password(es_url:'str', auth:'any_', password:'str') -> 'None':
    """ Gives the user Kibana connects as the password Kibana is started with.
    """
    url = f'{es_url}/_security/user/{ModuleCtx.Kibana_User}/_password'
    response = requests.post(url, auth=auth, json={'password': password}, timeout=ModuleCtx.HTTP_Timeout)

    if response.status_code != OK:
        raise Exception(f'Could not set the password of `{ModuleCtx.Kibana_User}`, {response.status_code} {response.text}')

# ################################################################################################################################

def _create_api_key(es_url:'str', auth:'any_') -> 'str':
    """ An API key that may write into log data streams and nothing else, in the form an Authorization header carries.
    """
    request:'anydict' = {
        'name': ModuleCtx.API_Key_Name,
        'role_descriptors': {
            ModuleCtx.API_Key_Role: {
                'indices': [{
                    'names': ModuleCtx.API_Key_Indices,
                    'privileges': ModuleCtx.API_Key_Privileges,
                }],
            },
        },
    }

    response = requests.post(f'{es_url}/_security/api_key', auth=auth, json=request, timeout=ModuleCtx.HTTP_Timeout)

    if response.status_code != OK:
        raise Exception(f'Could not create the API key, {response.status_code} {response.text}')

    out = response.json()['encoded']
    return out

# ################################################################################################################################

def _is_otlp_ready(endpoint:'str', api_key:'str') -> 'bool':
    """ One empty OTLP logs request with the API key - accepted means the endpoint and the key both work.
    """
    headers = {
        'Authorization': f'ApiKey {api_key}',
        'Content-Type': 'application/x-protobuf',
    }

    body = ExportLogsServiceRequest().SerializeToString()
    response = requests.post(endpoint, data=body, headers=headers, timeout=ModuleCtx.HTTP_Timeout)

    # A node without the endpoint is not going to grow one, so there is nothing to wait for ..
    if response.status_code == NOT_FOUND:
        raise StartupFailed(f'Elasticsearch has no OTLP logs endpoint at {endpoint}, {response.text}')

    # .. while anything else may still be the node settling down.
    out = response.status_code == OK
    return out

# ################################################################################################################################
# ################################################################################################################################

def _new_encryption_key() -> 'str':
    """ A key of the length Kibana's encryption settings take at the least.
    """
    out = CryptoManager.generate_hex_string(ModuleCtx.Kibana_Key_Bits)
    return out

# ################################################################################################################################

def _start_kibana(port:'int', kibana_password:'str') -> 'str':
    """ Kibana connecting to the node over the network by its container name, answering with its address.
    """
    print(f'Starting Kibana container {ModuleCtx.Kibana_Container} on port {port}', flush=True)

    kibana_url = f'http://{Host}:{port}'

    command = [
        'run', '-d',
        '--name', ModuleCtx.Kibana_Container,
        '--network', ModuleCtx.Network,
        '-p', f'{Host}:{port}:{ModuleCtx.Kibana_Port}',
        '-e', f'ELASTICSEARCH_HOSTS=http://{ModuleCtx.ES_Container}:{ModuleCtx.ES_Port}',
        '-e', f'ELASTICSEARCH_USERNAME={ModuleCtx.Kibana_User}',
        '-e', f'ELASTICSEARCH_PASSWORD={kibana_password}',
        '-e', f'SERVER_PUBLICBASEURL={kibana_url}',
        '-e', f'XPACK_ENCRYPTEDSAVEDOBJECTS_ENCRYPTIONKEY={_new_encryption_key()}',
        '-e', f'XPACK_SECURITY_ENCRYPTIONKEY={_new_encryption_key()}',
        '-e', f'XPACK_REPORTING_ENCRYPTIONKEY={_new_encryption_key()}',
        ModuleCtx.Kibana_Image,
    ]

    _run_or_raise(command, f'start `{ModuleCtx.Kibana_Container}`')

    out = kibana_url
    return out

# ################################################################################################################################

def _is_kibana_ready(kibana_url:'str', auth:'any_') -> 'bool':
    """ One attempt at Kibana's status, which is available once it serves its applications.
    """
    _check_running(ModuleCtx.Kibana_Container)

    response = requests.get(f'{kibana_url}/api/status', auth=auth, timeout=ModuleCtx.HTTP_Timeout)

    if response.status_code != OK:
        return False

    out = response.json()['status']['overall']['level'] == _kibana_available
    return out

# ################################################################################################################################

def _create_data_view(kibana_url:'str', auth:'any_') -> 'None':
    """ The data view over the audit log's data stream, made the default one so Discover opens on it.
    """
    headers = {ModuleCtx.Kibana_XSRF_Header: 'true'}

    request:'anydict' = {
        'data_view': {
            'id': ModuleCtx.Data_View_ID,
            'name': ModuleCtx.Data_View_Name,
            'title': ModuleCtx.Data_View_Pattern,
            'timeFieldName': ModuleCtx.Data_View_Time,
        },
        'override': True,
    }

    url = f'{kibana_url}/api/data_views/data_view'
    response = requests.post(url, auth=auth, headers=headers, json=request, timeout=ModuleCtx.HTTP_Timeout)

    if response.status_code != OK:
        raise Exception(f'Could not create the data view, {response.status_code} {response.text}')

    request = {'data_view_id': ModuleCtx.Data_View_ID, 'force': True}

    url = f'{kibana_url}/api/data_views/default'
    response = requests.post(url, auth=auth, headers=headers, json=request, timeout=ModuleCtx.HTTP_Timeout)

    if response.status_code != OK:
        raise Exception(f'Could not make the data view the default one, {response.status_code} {response.text}')

# ################################################################################################################################

def _build_discover_url(kibana_url:'str') -> 'str':
    """ Discover on the data view, over the last minutes, refreshing on its own, with the columns of an audit trail.
    """
    columns = ','.join(ModuleCtx.Discover_Columns)

    app_state = f'(columns:!({columns}),dataSource:(dataViewId:{ModuleCtx.Data_View_ID},type:dataView))'
    global_state = f'(refreshInterval:(pause:!f,value:{ModuleCtx.Discover_Refresh}),time:(from:{ModuleCtx.Discover_Time_From},to:now))'

    out = f'{kibana_url}/app/discover#/?_a={app_state}&_g={global_state}'
    return out

# ################################################################################################################################
# ################################################################################################################################

def start_stack() -> 'ElasticStack':
    """ Starts Elasticsearch and Kibana on host ports nothing else uses, creates the API key and the data view,
    and waits until both answer and the OTLP endpoint accepts the key.
    """
    _pull(ModuleCtx.ES_Image)
    _pull(ModuleCtx.Kibana_Image)

    remove_stack()
    _run_or_raise(['network', 'create', ModuleCtx.Network], f'create network `{ModuleCtx.Network}`')

    password = ModuleCtx.Superuser_Password
    kibana_password = 'kibana.' + CryptoManager.generate_hex_string()
    auth = (ModuleCtx.Superuser, password)

    es_port = find_free_port()
    kibana_port = find_free_port()

    es_url = f'http://{Host}:{es_port}'

    # Elasticsearch comes first, Kibana cannot start without it ..
    _start_elasticsearch(es_port, password)
    wait_until(partial(_is_es_ready, es_url, auth), f'Elasticsearch in `{ModuleCtx.ES_Container}`')
    print(f'Elasticsearch is ready at {es_url}', flush=True)

    # .. the server's key and the endpoint it sends to are checked before anything else depends on them ..
    api_key = _create_api_key(es_url, auth)

    otlp_logs_endpoint = es_url + ModuleCtx.OTLP_Logs_Path
    wait_until(partial(_is_otlp_ready, otlp_logs_endpoint, api_key), f'the OTLP logs endpoint at {otlp_logs_endpoint}')
    print(f'Elasticsearch accepts OTLP logs at {otlp_logs_endpoint}', flush=True)

    # .. and Kibana follows with its own user and the data view people open.
    _set_kibana_password(es_url, auth, kibana_password)
    kibana_url = _start_kibana(kibana_port, kibana_password)

    wait_until(partial(_is_kibana_ready, kibana_url, auth), f'Kibana in `{ModuleCtx.Kibana_Container}`')
    _create_data_view(kibana_url, auth)
    print(f'Kibana is ready at {kibana_url}', flush=True)

    out = ElasticStack(
        es_url=es_url,
        kibana_url=kibana_url,
        discover_url=_build_discover_url(kibana_url),
        username=ModuleCtx.Superuser,
        password=password,
        otlp_logs_endpoint=otlp_logs_endpoint,
        api_key=api_key,
        dataset=ModuleCtx.Dataset,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
