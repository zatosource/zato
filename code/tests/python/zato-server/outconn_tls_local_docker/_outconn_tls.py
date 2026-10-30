# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import time
from dataclasses import dataclass
from json import dumps

# local
from certs import build_tls_material
from http_test_server import HTTPSTestServer
from local_docker import get_server_log_size, import_enmasse, invoke_service, wait_for_server_log
from soap_test_server import SOAPTestServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from certs import TLSMaterial
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

# Where the container reads outgoing TLS material from - a host directory is mapped to it
Container_Material_Root = '/opt/hot-deploy/ssl/outgoing'

# The service that invokes the connections and the file it is deployed from
Service_Name = 'test.outconn-tls.local-docker.check'
Service_File_Path = os.path.join(os.path.dirname(__file__), 'fixtures', 'services', 'outconn_tls_check.py')

# What the service returns once the connection was invoked
Result_Invoked = 'outconn-tls-invoked'

# The paths that the connection under test and the unrelated connection invoke on the same endpoint
Main_Path = '/main'
Other_Path = '/other'

# The name of the import file, on the host and inside the container
_yaml_file_prefix = 'zato-outconn-tls-local-docker'

# How long to keep retrying an invocation while the service deploys and the connections are configured, in seconds
_invoke_timeout = 120

# How often to retry it, in seconds
_invoke_poll_interval = 1.0

# How long to wait for the server to report a change to TLS material, in seconds
_reload_timeout = 60

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class LocalContainer:
    """ Where the container reaches the host's endpoints and where its outgoing TLS material is mapped from.
    """
    gateway: 'str'
    host_material_root: 'str'

# ################################################################################################################################
# ################################################################################################################################

class MaterialKind:
    """ How a connection names its client certificate.
    """
    MTLS     = 'mtls'     # Through an mTLS security definition
    Combined = 'combined' # Through its own fields, with one file holding the certificate and its key
    Separate = 'separate' # Through its own fields, with the key in a file of its own

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ClientFiles:
    """ The paths of one client's certificate, key and combined file, as the container sees them.
    """
    certificate_path: 'str'
    key_path: 'str'
    combined_path: 'str'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CaseRun:
    """ Everything one case creates - the material on the host, the files as the container sees them,
    the names of the objects it imports and the endpoint the connections invoke.
    """
    case_name: 'str'
    conn_type: 'str'
    transport: 'str'
    material_kind: 'str'

    host_case_directory: 'str'
    material: 'TLSMaterial'

    ca_path: 'str'
    main_files: 'ClientFiles'
    other_files: 'ClientFiles'

    main_security_name: 'str'
    other_security_name: 'str'
    main_conn_name: 'str'
    other_conn_name: 'str'

    endpoint: 'any_'

# ################################################################################################################################
# ################################################################################################################################

def _to_container_path(local_container:'LocalContainer', host_path:'str') -> 'str':
    relative_path = os.path.relpath(host_path, local_container.host_material_root)

    out = os.path.join(Container_Material_Root, relative_path)
    return out

# ################################################################################################################################

def _get_client_files(local_container:'LocalContainer', certificate_path:'str', key_path:'str', combined_path:'str') -> 'ClientFiles':
    out = ClientFiles()
    out.certificate_path = _to_container_path(local_container, certificate_path)
    out.key_path = _to_container_path(local_container, key_path)
    out.combined_path = _to_container_path(local_container, combined_path)
    return out

# ################################################################################################################################

def _write_material(local_container:'LocalContainer', run:'CaseRun') -> 'None':
    """ Generates the CA, the endpoint's and the client's material in the mapped directory,
    and a copy of the client's files for the unrelated connection, then waits until the server
    has been told about each of them, so that no report of these files arrives once the case is under way.
    """
    log_offset = get_server_log_size()

    # A directory that a previous run left behind is replaced ..
    shutil.rmtree(run.host_case_directory, ignore_errors=True)
    os.makedirs(run.host_case_directory)

    run.material = build_tls_material(local_container.gateway, run.host_case_directory)

    # .. the unrelated connection presents the same certificate from files of its own ..
    other_directory = os.path.join(run.host_case_directory, 'other')
    os.makedirs(other_directory)

    other_certificate_path = os.path.join(other_directory, 'client-cert.pem')
    other_key_path = os.path.join(other_directory, 'client-key.pem')
    other_combined_path = os.path.join(other_directory, 'client-combined.pem')

    _ = shutil.copyfile(run.material.client_key_path, other_key_path)
    _ = shutil.copyfile(run.material.client_certificate_path, other_certificate_path)
    _ = shutil.copyfile(run.material.client_combined_path, other_combined_path)

    run.ca_path = _to_container_path(local_container, run.material.ca_path)

    run.main_files = _get_client_files(local_container,
        run.material.client_certificate_path, run.material.client_key_path, run.material.client_combined_path)

    run.other_files = _get_client_files(local_container, other_certificate_path, other_key_path, other_combined_path)

    # .. and the file written last is the one whose report the server logs last.
    _ = wait_for_server_log(f'`{run.other_files.combined_path}`', log_offset, _reload_timeout)

# ################################################################################################################################

def _get_security_yaml(name:'str', files:'ClientFiles', ca_path:'str') -> 'str':
    out = f"""
  - name: {name}
    type: mtls
    use_for: outgoing
    cert_path: {files.certificate_path}
    key_path: {files.key_path}
    ca_certs_path: {ca_path}
"""
    return out

# ################################################################################################################################

def _get_connection_yaml(run:'CaseRun', name:'str', url_path:'str', security_name:'str', files:'ClientFiles') -> 'str':
    """ Returns one outgoing connection, naming its client certificate the way the case requires.
    """
    endpoint = run.endpoint

    out = f"""
  - name: {name}
    host: https://{endpoint.host}:{endpoint.port}
    url_path: {url_path}
    timeout: 20
"""

    # A connection with an mTLS definition reads everything from the definition ..
    if run.material_kind == MaterialKind.MTLS:
        out += f'    security: {security_name}\n'

    # .. while one with its own fields has no CA of its own to validate the endpoint with ..
    else:
        out += '    tls_verify: false\n'

        # .. and it names either a single file ..
        if run.material_kind == MaterialKind.Combined:
            out += f'    tls_client_cert: {files.combined_path}\n'

        # .. or a certificate and its key.
        else:
            out += f'    tls_client_cert: {files.certificate_path}\n'
            out += f'    tls_client_key: {files.key_path}\n'

    if run.conn_type == 'rest':
        out += '    data_format: json\n'
    else:
        out += '    soap_version: "1.1"\n'

    return out

# ################################################################################################################################

def _import_objects(run:'CaseRun') -> 'None':
    """ Imports the case's definitions, if it uses any, and its two connections.
    """
    yaml_text = ''

    if run.material_kind == MaterialKind.MTLS:
        yaml_text += 'security:\n'
        yaml_text += _get_security_yaml(run.main_security_name, run.main_files, run.ca_path)
        yaml_text += _get_security_yaml(run.other_security_name, run.other_files, run.ca_path)

    if run.conn_type == 'rest':
        yaml_text += '\noutgoing_rest:\n'
    else:
        yaml_text += '\noutgoing_soap:\n'

    yaml_text += _get_connection_yaml(run, run.main_conn_name, Main_Path, run.main_security_name, run.main_files)
    yaml_text += _get_connection_yaml(run, run.other_conn_name, Other_Path, run.other_security_name, run.other_files)

    import_enmasse(yaml_text, _yaml_file_prefix)

# ################################################################################################################################

def _start_endpoint(local_container:'LocalContainer', run:'CaseRun') -> 'None':
    """ Starts the endpoint that both connections invoke, on the address the container reaches the host through.
    """
    if run.conn_type == 'rest':
        run.endpoint = HTTPSTestServer(require_client_cert=True, host=local_container.gateway, tls_material=run.material)
    else:
        run.endpoint = SOAPTestServer(tls=True, require_client_cert=True, host=local_container.gateway,
            tls_material=run.material)

    run.endpoint.start()

# ################################################################################################################################

def start_case(
    local_container:'LocalContainer',
    case_name:'str',
    conn_type:'str',
    transport:'str',
    material_kind:'str',
    ) -> 'CaseRun':
    """ Generates the case's material, starts its endpoint and imports its objects.
    """
    run = CaseRun()
    run.case_name = case_name
    run.conn_type = conn_type
    run.transport = transport
    run.material_kind = material_kind
    run.host_case_directory = os.path.join(local_container.host_material_root, f'outconn-tls-{case_name}')

    name_prefix = f'test.outconn-tls.local-docker.{case_name}'

    run.main_security_name = f'{name_prefix}.mtls'
    run.other_security_name = f'{name_prefix}.mtls.other'
    run.main_conn_name = f'{name_prefix}.main'
    run.other_conn_name = f'{name_prefix}.other'

    _write_material(local_container, run)
    _start_endpoint(local_container, run)
    _import_objects(run)

    return run

# ################################################################################################################################

def stop_case(run:'CaseRun') -> 'None':
    """ Stops the case's endpoint and removes its material from the mapped directory.
    """
    run.endpoint.stop()
    shutil.rmtree(run.host_case_directory, ignore_errors=True)

# ################################################################################################################################

def _get_records(run:'CaseRun', path:'str') -> 'anylist':
    out = []

    for record in run.endpoint.recorded_requests:
        if record['path'] == path:
            out.append(record)

    return out

# ################################################################################################################################

def invoke(run:'CaseRun', conn_name:'str', path:'str') -> 'anydict':
    """ Invokes one connection through the service, retrying while the service deploys
    and the connection is configured, and returns what the endpoint recorded of the request.
    """
    payload = dumps({'conn_type': run.conn_type, 'conn_name': conn_name})
    count_before = len(_get_records(run, path))

    deadline = time.monotonic() + _invoke_timeout
    last_output = ''

    while time.monotonic() < deadline:

        last_output = invoke_service(Service_Name, payload)

        # The invocation is complete when the service reports it and the endpoint has recorded it
        if Result_Invoked in last_output:
            records = _get_records(run, path)
            if len(records) > count_before:
                out = records[-1]
                return out

        time.sleep(_invoke_poll_interval)

    raise Exception(f'Connection `{conn_name}` was not invoked within {_invoke_timeout}s, last output: {last_output}')

# ################################################################################################################################

def get_log_offset() -> 'int':
    out = get_server_log_size()
    return out

# ################################################################################################################################

def wait_for_reload(run:'CaseRun', log_offset:'int') -> 'None':
    """ Waits until the server reports that the connection under test discarded its pooled connections
    after the last of its files was replaced.
    """

    # The key is replaced before the certificate and the combined file after both, so the last file
    # that the connection reads is the combined one if it uses that one, and the certificate otherwise.
    if run.material_kind == MaterialKind.Combined:
        path = run.main_files.combined_path
    else:
        path = run.main_files.certificate_path

    text = f'Reloaded TLS material of outgoing connection `{run.main_conn_name}` ({run.transport}) -> `{path}`'
    _ = wait_for_server_log(text, log_offset, _reload_timeout)

# ################################################################################################################################
# ################################################################################################################################
